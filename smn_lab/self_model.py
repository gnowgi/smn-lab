# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The self-model: a body's own connectivity graph, recovered from *exploratory*
movement (independent per-zone drive / "babbling"). NB: under coordinated locomotion
(one oscillator driving all zones) the read-out tracks command phase, not body
topology, and collapses toward chance -- see experiments/self_model_babble_behave.
Chance neighbour-accuracy for an n-zone chain is 2/n (so n=2 bodies are uninformative).

This module is **the model** — the computation the SMN framework says the *agent*
performs to build its self-model. It is deliberately kept separate from
``smn_lab.metrics`` (the experimenter's scoring, which reads against ground truth
the agent cannot access). Keeping cognition and measurement in different modules is
what lets a reviewer see the ``simulated / computed / assumed`` boundary at a glance.

C3 (the shared state-space has no central reader — "the graph *is* the computer").
The atomic operation is :func:`local_read`: **one zone** correlates its *own*
efference with every channel it hears on the broadcast. That is purely local — a
zone uses only its own efference copy and what neighbours broadcast; it never reads
the whole body. :func:`read_all` stacks those independent per-zone reads into a
matrix, but the stacking is a *vectorization convenience*, not a shared computation:
row ``i`` depends only on zone ``i``'s efference and the broadcast, so the matrix is
exactly the union of independent local reads. The body graph is then the union of
each zone's *own* strongest-co-mover edge (:func:`local_edge`) — assembled by no
one. Any operation that needs the whole matrix at once (e.g. spectral seriation for
a chain-order *score*) is the experimenter's summary and lives in
:mod:`smn_lab.metrics`, not here.

Inputs are two time-by-index arrays gathered while the body moves:
  A[t, i] -- zone i's own signal (efference: commanded torque, or joint velocity);
  B[t, s] -- every channel heard on the broadcast (segment yaw-rate / joint motion).
"""
from __future__ import annotations
import numpy as np


def _z(X, eps=1e-9):
    """Per-channel z-score (standardize each column over time)."""
    return (X - X.mean(0)) / (X.std(0) + eps)


# --8<-- [start:local_read]
def local_read(a_i, B):
    """One zone's self-model read-out: zone i's normalized cross-correlation of its
    OWN signal ``a_i`` (efference copy) against every broadcast channel ``B``.

    Purely local (C3): uses only zone i's own channel and what it hears broadcast —
    no zone ever reads the whole body. Returns a length-``B.shape[1]`` vector."""
    return (_z(a_i[:, None])[:, 0] @ _z(B)) / len(B)
# --8<-- [end:local_read]


# --8<-- [start:read_all]
def read_all(A, B):
    """The batch of every zone's :func:`local_read`, stacked into a matrix
    ``C[i, s] = local_read(A[:, i], B)[s]``. The stacking is a vectorization
    convenience, NOT a central reader: row i depends only on zone i's own signal
    ``A[:, i]`` and the broadcast ``B``, so ``C`` is exactly the union of
    independent local reads."""
    return (_z(A).T @ _z(B)) / len(A)
# --8<-- [end:read_all]


# --8<-- [start:coupling]
def coupling(JV, OMEGA):
    """Signed self-model read-out C[joint, segment] = read_all(JV, OMEGA).
    Each joint's top positive column is its child, top negative its parent."""
    return read_all(JV, OMEGA)
# --8<-- [end:coupling]


# --8<-- [start:transfer]
def transfer(TAU, VEL):
    """Undirected transmission gain G[i,j] = |read_all(TAU, VEL)|, symmetrized,
    self-terms zeroed. The magnitude-and-symmetric specialization of the same
    local read-out: each edge is agreed by both endpoints from the shared
    broadcast (i's read of j and j's read of i). Independent drives make G[i,j]
    isolate 'how much j moves because i moved'; elastic attenuation makes it fall
    off with hop-distance."""
    G = np.abs(read_all(TAU, VEL))
    G = 0.5 * (G + G.T)
    np.fill_diagonal(G, 0.0)
    return G
# --8<-- [end:transfer]


# --8<-- [start:local_edge]
def local_edge(c_i):
    """One zone's own edge, decided locally from its coupling vector ``c_i``: the
    (co-rotating, counter-rotating) pair = (argmax, argmin), order-normalized.
    A signed read (:func:`coupling`) gives child/parent; for an unsigned gain
    (:func:`transfer`) argmax is the strongest co-mover."""
    lo, hi = int(np.argmax(c_i)), int(np.argmin(c_i))
    return (min(lo, hi), max(lo, hi))
# --8<-- [end:local_edge]


def recover_edges(C):
    """The body graph = union of every zone's own :func:`local_edge` (no central
    fit; each zone decides its edge from its own row)."""
    return [local_edge(C[j]) for j in range(C.shape[0])]


def edge_strength(C):
    """Per-joint coupling magnitude, normalized to [0, 1] -- for edge width."""
    s = np.array([abs(C[j].max()) + abs(C[j].min()) for j in range(C.shape[0])])
    return (s - s.min()) / (np.ptp(s) + 1e-9)


def degrees(edges):
    d = {}
    for a, b in edges:
        d[a] = d.get(a, 0) + 1; d[b] = d.get(b, 0) + 1
    return d


def branch_node(edges):
    """The highest-degree node if it is an actual branch point (degree >= 3),
    else None (a chain has no branch point)."""
    d = degrees(edges)
    if not d:
        return None
    n = max(d, key=d.get)
    return n if d[n] >= 3 else None
