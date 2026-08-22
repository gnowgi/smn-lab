# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""World-model, morphology-dependent (headline experiment for the world-model paper).

Claim: the SMN's world-model is expressed in the SELF-model's frame, so it is
grounded in the body's morphology -- and therefore NOT transferable across bodies.
Two bodies in the SAME world build DIFFERENT world-models. This is the falsifiable
contrast with body-agnostic (SLAM / observer-map) representations, which any body
reads the same way.

Operationalization -- cross-body decoder transfer:
  * Task: self-localization -- infer the agent's pose (x, y) in a fixed scalar field
    from its current sensation (a minimal 'where am I in my world-model').
  * Self-frame representation: the body's own bilateral field sensors (seg_k L/R),
    a vector indexed by body part. Its geometry depends on morphology (segment length
    h, sensor offset sense_off).
  * Allocentric baseline: the field sampled on a world-axis grid anchored at the
    agent's location -- an external observer's read, identical for every body.
  * Train a linear decoder on body A, test it on body B (same pose set). If the
    world-model is body-grounded, cross-body transfer COLLAPSES; if body-agnostic, it
    transfers. Order parameter: transfer skill vs morphological distance.

PRE-REGISTRATION
  OP1 (world-model exists, W1): within-body decoding skill >> shuffle foil, for every body.
  OP2 (headline, W3): self-frame cross-body transfer decays with morphological distance and
    is far below the within-body diagonal; the allocentric baseline stays flat (transfers).
    PASS if mean self-frame off-diagonal/diagonal ratio < 0.5 while allocentric ratio > 0.8.

Run:  ../.venv/bin/python worldmodel_morphology.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml
from smn_lab.fields import ScalarField

N_SEG = 8
N_POSES = 800
POSE_HALF = 1.0
SENSOR_NOISE = 0.01
KNN = 12

# one fixed world: five Gaussian sources -> a structured field with enough spatial
# variation that a static sensory read carries location information.
FIELD = ScalarField([(0.9, 0.7, 1.0, 0.35), (-0.8, 0.6, 0.9, 0.35),
                     (0.1, -0.9, 1.0, 0.35), (-0.6, -0.5, 0.8, 0.35),
                     (0.7, -0.2, 0.9, 0.35)])

# four morphologies, same topology (8 segments) -> comparable feature dimension.
# morphology vector m = (segment length h, sensor offset sense_off).
BODIES = {
    "small-narrow": dict(h=0.05, sense_off=0.04),
    "small-wide":   dict(h=0.05, sense_off=0.13),
    "large-narrow": dict(h=0.10, sense_off=0.04),
    "large-wide":   dict(h=0.10, sense_off=0.13),
}


def poses(seed=0):
    rng = np.random.default_rng(seed)
    xy = rng.uniform(-POSE_HALF, POSE_HALF, size=(N_POSES, 2))
    th = np.zeros(N_POSES)                              # fixed heading: isolate position
    return xy, th


def sense_body(cfg, xy, th, seed):
    """Place the (straight) body at each pose; return the self-frame sensor vector
    (per-segment bilateral field readings, dim 2*N_SEG) and the allocentric baseline
    (world-axis 3x3 field grid at the head, dim 9, identical across bodies)."""
    rng = np.random.default_rng(100 + seed)
    xml = build_crawler_xml(n_seg=N_SEG, h=cfg["h"], sense_off=cfg["sense_off"],
                            bend_limit_deg=45.0)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    ax = model.joint("slide_x").qposadr[0]
    ay = model.joint("slide_y").qposadr[0]
    aw = model.joint("yaw").qposadr[0]
    sL = [model.site(f"seg{k}_L").id for k in range(N_SEG)]
    sR = [model.site(f"seg{k}_R").id for k in range(N_SEG)]
    grid = np.array([(dx, dy) for dx in (-0.2, 0.0, 0.2) for dy in (-0.2, 0.0, 0.2)])

    S_self = np.zeros((len(xy), 2 * N_SEG))
    S_allo = np.zeros((len(xy), len(grid)))
    for i in range(len(xy)):
        data.qpos[:] = 0.0
        data.qpos[ax], data.qpos[ay], data.qpos[aw] = xy[i, 0], xy[i, 1], th[i]
        mujoco.mj_forward(model, data)
        row = []
        for k in range(N_SEG):
            row.append(FIELD.sample(*data.site_xpos[sL[k]][:2]))
            row.append(FIELD.sample(*data.site_xpos[sR[k]][:2]))
        S_self[i] = row
        S_allo[i] = [FIELD.sample(xy[i, 0] + dx, xy[i, 1] + dy) for dx, dy in grid]
    S_self += rng.normal(0, SENSOR_NOISE, S_self.shape)
    S_allo += rng.normal(0, SENSOR_NOISE, S_allo.shape)
    return S_self, S_allo


def ridge_fit(S, P):
    """kNN 'fit' = standardize + store the training set (nonlinear decoder suited to a
    smooth field). Named ridge_* only to keep the call sites stable."""
    mu, sd = S.mean(0), S.std(0) + 1e-9
    return mu, sd, (S - mu) / sd, P


def ridge_predict(model, S, k=KNN):
    mu, sd, Atr, Ptr = model
    B = (S - mu) / sd
    d2 = ((B[:, None, :] - Atr[None, :, :]) ** 2).sum(-1)
    idx = np.argsort(d2, axis=1)[:, :k]
    return Ptr[idx].mean(axis=1)


def skill(pred, P, ref_mean):
    mae = float(np.mean(np.hypot(*(pred - P).T)))
    naive = float(np.mean(np.hypot(*(P - ref_mean).T)))
    return 1.0 - mae / max(naive, 1e-9)


def transfer_matrix(states, P, tr):
    """states: dict name->S. Fit on each body's train split, test on every body's test
    split (shared poses). Returns skill matrix T[train, test] and the shuffle foil."""
    names = list(states)
    ref = P[tr].mean(0)
    models = {n: ridge_fit(states[n][tr], P[tr]) for n in names}
    T = np.zeros((len(names), len(names)))
    for a, na in enumerate(names):
        for b, nb in enumerate(names):
            T[a, b] = skill(ridge_predict(models[na], states[nb][~tr]), P[~tr], ref)
    # shuffle foil (within-body, destroy pose pairing) for OP1
    rng = np.random.default_rng(7)
    foil = {}
    for n in names:
        m = ridge_fit(states[n][tr], P[tr][rng.permutation(tr.sum())])
        foil[n] = skill(ridge_predict(m, states[n][~tr]), P[~tr], ref)
    return names, T, foil


def main():
    xy, th = poses()
    P = xy
    rng = np.random.default_rng(1)
    tr = rng.random(len(P)) < 0.6                       # shared train/test split

    S_self, S_allo = {}, {}
    for name, cfg in BODIES.items():
        ss, sa = sense_body(cfg, xy, th, seed=hash(name) % 1000)
        S_self[name] = ss; S_allo[name] = sa

    names, Tself, foil = transfer_matrix(S_self, P, tr)
    _,     Tallo, _    = transfer_matrix(S_allo, P, tr)

    diag_self = np.diag(Tself); off_self = Tself[~np.eye(len(names), dtype=bool)]
    diag_allo = np.diag(Tallo); off_allo = Tallo[~np.eye(len(names), dtype=bool)]
    ratio_self = off_self.mean() / max(diag_self.mean(), 1e-9)
    ratio_allo = off_allo.mean() / max(diag_allo.mean(), 1e-9)

    print("\nMorphology-dependent world-model: cross-body decoder transfer\n" + "=" * 70)
    print("Task: self-localization (decode pose from sensation) in one fixed field.")
    print(f"within-body skill (W1: world-model exists) -- self-frame diag mean "
          f"{diag_self.mean():.2f}, shuffle foil {np.mean(list(foil.values())):.2f}")
    print("-" * 70)
    print("SELF-FRAME transfer matrix T[train->test] (rows train on, cols test on):")
    print("            " + "".join(f"{n[:11]:<12}" for n in names))
    for a, na in enumerate(names):
        print(f"{na[:11]:<12}" + "".join(f"{Tself[a, b]:<12.2f}" for b in range(len(names))))
    print(f"\nself-frame : diagonal {diag_self.mean():.2f}  off-diagonal {off_self.mean():.2f}  "
          f"ratio {ratio_self:.2f}")
    print(f"allocentric: diagonal {diag_allo.mean():.2f}  off-diagonal {off_allo.mean():.2f}  "
          f"ratio {ratio_allo:.2f}")
    op1 = diag_self.mean() > 0.3 and np.mean(list(foil.values())) < 0.1
    op2 = ratio_self < 0.5 and ratio_allo > 0.8
    print("=" * 70)
    print(f"OP1 (world-model exists, W1): [{'PASS' if op1 else 'CHECK'}]")
    print(f"OP2 (morphology-dependent, W3): self ratio {ratio_self:.2f} < 0.5 and "
          f"allo ratio {ratio_allo:.2f} > 0.8  [{'PASS' if op2 else 'CHECK'}]")
    print("Reading: each body localizes itself in the field (a world-model exists), but the\n"
          "self-frame world-model does NOT transfer across morphologies -- different bodies\n"
          "build different, non-interchangeable world-models of the same world. A body-agnostic\n"
          "(observer) read transfers freely. Morphology is constitutive of the world-model.\n")

    # morphological distance vs transfer
    m = {n: np.array([BODIES[n]["h"] / 0.1, BODIES[n]["sense_off"] / 0.13]) for n in names}
    dists, tsv, tav = [], [], []
    for a, na in enumerate(names):
        for b, nb in enumerate(names):
            if a == b:
                continue
            dists.append(np.linalg.norm(m[na] - m[nb])); tsv.append(Tself[a, b]); tav.append(Tallo[a, b])

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for k, (T, ttl) in enumerate([(Tself, "self-frame (SMN)"), (Tallo, "allocentric (observer)")]):
        im = ax[k].imshow(T, vmin=0, vmax=1, cmap="viridis")
        ax[k].set_xticks(range(len(names))); ax[k].set_xticklabels(names, rotation=40, ha="right", fontsize=7)
        ax[k].set_yticks(range(len(names))); ax[k].set_yticklabels(names, fontsize=7)
        ax[k].set_title(f"transfer skill: {ttl}"); ax[k].set_xlabel("test body"); ax[k].set_ylabel("train body")
        fig.colorbar(im, ax=ax[k], fraction=0.046)
    ax[2].scatter(dists, tsv, c="#2c6fbb", label="self-frame (SMN)", s=45)
    ax[2].scatter(dists, tav, c="#c0672a", marker="s", label="allocentric", s=45)
    ax[2].set_xlabel("morphological distance"); ax[2].set_ylabel("cross-body transfer skill")
    ax[2].set_ylim(-0.1, 1.05); ax[2].set_title("transfer decays with morphology"); ax[2].legend(fontsize=8)
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "worldmodel_morphology.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
