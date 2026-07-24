# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Experimenter-side scoring — NOT part of the agent's cognition.

Every function here reads against **ground truth the agent cannot access** (the
true body order, the true hop-distance, the true world position) or performs a
**global** operation over a whole matrix (spectral seriation) that no single zone
could do. They exist to *falsify* the model from the outside — to ask "did the
self/world model that :mod:`smn_lab.self_model` builds actually match reality?" —
and they are kept out of :mod:`smn_lab.self_model` on purpose so the
cognition/measurement boundary (see ``docs/assumptions.md``) is visible in the
module layout itself.

Rule of thumb: if a function needs the answer key, it is a metric and lives here;
if a zone could compute it from its own efference and the broadcast, it is the
model and lives in :mod:`smn_lab.self_model`.
"""
from __future__ import annotations
import numpy as np


# --8<-- [start:seriation_order]
def seriation_order(G):
    """EXPERIMENTER-SIDE. Global spectral seriation: order zones by the Fiedler
    vector (2nd-smallest eigenvector) of the graph Laplacian L = D - G. This reads
    the WHOLE matrix at once, so it is the experimenter's summary of the
    distributed graph, not a per-zone computation. Returns the recovered ordering."""
    W = G.copy()
    L = np.diag(W.sum(1)) - W                      # graph Laplacian
    w, v = np.linalg.eigh(L)
    fiedler = v[:, 1]                              # 2nd-smallest eigenvector
    return np.argsort(fiedler)
# --8<-- [end:seriation_order]


def order_accuracy(order):
    """EXPERIMENTER-SIDE. How well a recovered order matches the TRUE chain order
    0..nj-1, up to reflection: |corr| of recovered rank vs true rank."""
    nj = len(order)
    rank = np.empty(nj, dtype=float)
    rank[order] = np.arange(nj)
    true = np.arange(nj, dtype=float)
    return abs(np.corrcoef(rank, true)[0, 1])


def neighbour_accuracy(C):
    """EXPERIMENTER-SIDE. Fraction of zones whose single strongest co-mover is a
    TRUE chain neighbour (|i-j| == 1). Scores the purely-local 1-hop read against
    the answer key."""
    nj = C.shape[0]
    ok = 0
    for i in range(nj):
        j = int(np.argmax(C[i]))
        if abs(j - i) == 1:
            ok += 1
    return ok / nj


def curve_vs_hops(C):
    """EXPERIMENTER-SIDE. Mean co-movement binned by TRUE hop-distance |i-j| along
    the chain (uses the known body order). Returns (hops, mean_C_at_each_hop)."""
    nj = C.shape[0]
    hops = {}
    for i in range(nj):
        for j in range(i + 1, nj):
            hops.setdefault(j - i, []).append(C[i, j])
    hs = sorted(hops)
    return np.array(hs), np.array([np.mean(hops[h]) for h in hs])


# --8<-- [start:arm_swap_residual]
def arm_swap_residual(C, joint_order, armA, armB):
    """EXPERIMENTER-SIDE. ||C - swap(C)|| / ||C|| for exchanging armA and armB
    (aligned from the hub). Near 0 => the two arms are interchangeable in the data
    (the self-model cannot tell them apart). Uses the known arm assignment."""
    jidx = {jn: i for i, jn in enumerate(joint_order)}
    seg_perm = np.arange(C.shape[1]); jnt_perm = np.arange(C.shape[0])
    k = min(len(armA["segs"]), len(armB["segs"]))
    for i in range(k):                              # swap aligned segments and joints
        sa, sb = armA["segs"][i], armB["segs"][i]
        seg_perm[sa], seg_perm[sb] = sb, sa
        ja, jb = jidx[armA["joints"][i]], jidx[armB["joints"][i]]
        jnt_perm[ja], jnt_perm[jb] = jb, ja
    Cp = C[jnt_perm][:, seg_perm]
    return float(np.linalg.norm(C - Cp) / (np.linalg.norm(C) + 1e-12))
# --8<-- [end:arm_swap_residual]


# --8<-- [start:endpoint_recovery]
def endpoint_recovery(C, edges):
    """EXPERIMENTER-SIDE. For a link-driven read-out C[link, seg] (each link's
    co-movement with every segment), score whether each link's two strongest
    co-movers are its TRUE endpoints. Returns the fraction recovered (partial
    credit 0/0.5/1 per link). Uses the known wiring — the answer key."""
    hits = 0.0
    for L, (a, b) in enumerate(edges):
        top2 = set(np.argsort(C[L])[::-1][:2])
        hits += len({a, b} & top2) / 2.0
    return hits / len(edges)
# --8<-- [end:endpoint_recovery]


# --8<-- [start:decoding_skill]
def decoding_skill(S, P, rng, k=8, shuffle=False):
    """EXPERIMENTER-SIDE. Held-out kNN decoding skill of TRUE position P from the
    agent's internal state S. Split 60/40 by time; predict each test point from its
    k nearest train states. skill = 1 - MAE_decoder / MAE_naive (naive = predict the
    train-mean position). With shuffle=True the state<->position pairing is destroyed
    (integrity control; must sit at skill ~ 0). Uses the true position — the agent
    never sees it; this only asks whether S *encodes* it."""
    n = len(S)
    cut = int(0.6 * n)
    Str, Ptr, Ste, Pte = S[:cut], P[:cut], S[cut:], P[cut:]
    if shuffle:                               # destroy the state<->position relation
        Ptr = Ptr[rng.permutation(len(Ptr))]
    # standardize state dims so kNN distance is not dominated by one channel
    mu, sd = Str.mean(0), Str.std(0) + 1e-9
    A, B = (Str - mu) / sd, (Ste - mu) / sd
    d2 = ((B[:, None, :] - A[None, :, :]) ** 2).sum(-1)      # (n_te, n_tr)
    idx = np.argsort(d2, axis=1)[:, :k]
    pred = Ptr[idx].mean(axis=1)
    mae = float(np.mean(np.hypot(*(pred - Pte).T)))
    naive = float(np.mean(np.hypot(*(Pte - Ptr.mean(0)).T)))
    return 1.0 - mae / max(naive, 1e-9)
# --8<-- [end:decoding_skill]


# --8<-- [start:correction_dc_ratio]
def correction_dc_ratio(ent):
    """Diagnostic: |mean| / std of a feedback/correction signal over time.

    A well-formed *correction* term is zero-mean with ripple — it nudges toward and
    away from the reference. The moment its DC component dominates its variance it has
    stopped correcting and started **biasing** (e.g. a constant brake). This ratio
    catches that: `~0` = a genuine corrector; `>> 1` = a disguised bias.

    It would have flagged both entrainment bugs by inspection: the argument-order bug
    (cos 2φ, still ripple-like) less so, but the self-feedback topology gave
    mean=-0.75, std=0.17 -> ratio 4.4, a pure brake wearing a correction's clothes.
    Pre-committed success criterion for the entrainment fix: ratio < 0.05 in steady
    free swimming (see docs/experiments/entrainment.md)."""
    ent = np.asarray(ent, dtype=float)
    return float(abs(ent.mean()) / (ent.std() + 1e-12))
# --8<-- [end:correction_dc_ratio]


# --8<-- [start:ridge_skill]
def ridge_skill(S, P, rng, lam=1.0, shuffle=False):
    """EXPERIMENTER-SIDE, dimension-robust companion to decoding_skill.

    Same 60/40 temporal split, same standardize-on-train, same skill definition
    (1 - MAE/MAE_naive) and shuffle control -- but a ridge-regularized LINEAR readout
    S -> P instead of kNN. kNN degrades with state dimension (curse of
    dimensionality): adding sensor channels can lower kNN skill even when they add
    information, so a kNN skill *slope* vs channel count is confounded by the number
    of channels. A regularized linear map does not have that pathology -- extra
    channels can only help or be shrunk toward zero -- so comparing this against
    decoding_skill separates 'the world got less decodable' from 'kNN ran out of
    samples per dimension'. Use BOTH when the claim is about a skill slope."""
    n = len(S)
    cut = int(0.6 * n)
    Str, Ptr, Ste, Pte = S[:cut], P[:cut], S[cut:], P[cut:]
    if shuffle:
        Ptr = Ptr[rng.permutation(len(Ptr))]
    mu, sd = Str.mean(0), Str.std(0) + 1e-9
    A = np.column_stack([(Str - mu) / sd, np.ones(len(Str))])   # + bias column
    B = np.column_stack([(Ste - mu) / sd, np.ones(len(Ste))])
    reg = lam * np.eye(A.shape[1]); reg[-1, -1] = 0.0           # don't penalize bias
    W = np.linalg.solve(A.T @ A + reg, A.T @ Ptr)
    pred = B @ W
    mae = float(np.mean(np.hypot(*(pred - Pte).T)))
    naive = float(np.mean(np.hypot(*(Pte - Ptr.mean(0)).T)))
    return 1.0 - mae / max(naive, 1e-9)
# --8<-- [end:ridge_skill]
