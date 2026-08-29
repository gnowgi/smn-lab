# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Earthworm (oligochaete) — the segmented model system, opponent-pair CAZ (canonical).

Reconstructed with the CAZ ontology corrected (G. Nagarjuna): a lattice NODE is a multicellular
muscle-side REGION; a MUSCLE is one SIDE of a CAZ; a CAZ = one OPPONENT PAIR = one DOF.

Anatomy (sourced — see SMN_annelid_muscle_biology.md):
  * Two DISJOINT muscle tissues, no shared node (V_circ ∩ V_long = ∅):
      - CIRCULAR: thin, OUTER, SEGMENTAL (interrupted by the septa) — actuated circumferentially;
      - LONGITUDINAL: thick, INNER, CONTINUOUS across the body, in several BUNDLES — actuated along AP.
  * NO dorsoventral muscle, NO oblique (that is a leech/slug rung).
Opponent-pair CAZ (what actually actuates a DOF):
  * TELESCOPING CAZ (per segment) = circular ⊕ longitudinal, opposed through the coelomic
    hydrostat B_i (fixed volume): circular↑ → narrow+elongate; longitudinal↑ → shorten+widen.
    Sequenced along the body → the PERISTALTIC WAVE (the earthworm's propulsion).
  * LATERAL-BEND CAZ (per segment) = LEFT-longitudinal ⊕ RIGHT-longitudinal → turning.
Body relations built in as positional identity: AP a_i=(i-1)/5, DV polarity (θ_D≠θ_V), LR mirror.
The two tissues couple ONLY through the passive body wall (radial + diagonal hydrostat struts) and
the segmental ganglia G_i (ventral cord; an integrating channel, role kept tentative).

Two demos: (1) a peristaltic wave from the telescoping pairs; (2) a turn from the lateral pair.
Self-contained. Run:  ../.venv/bin/python earthworm.py
"""
from __future__ import annotations
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.fbody import build_body   # shared pull-only f primitive (A2)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

N_SEG, NR = 6, 4                       # 6 segments, 4 quadrants (DL,DR,VL,VR)
SEGX, R_C, R_L = 0.30, 0.16, 0.09      # segment length; outer circular / inner longitudinal radius
QUAD = {"DL": (-1, +1), "DR": (+1, +1), "VL": (-1, -1), "VR": (+1, -1)}   # (y=left−, z=dorsal+)
UDIR = {q: np.array(v, float) / np.linalg.norm(v) for q, v in QUAD.items()}
QUADS = ["DL", "DR", "VL", "VR"]; RING = ["DL", "DR", "VR", "VL"]
DT = 0.002
K_CM, K_LM = 14.0, 26.0                # circular muscle (thin), longitudinal (thick, stronger pull)
K_CS, K_LS, K_RAD, K_DIAG = 2.5, 2.5, 5.0, 3.5     # passive: circ/long continuity, radial, diagonal
K_CORD, K_SPOKE = 3.0, 1.5


def spec():
    """Two disjoint muscle tissues + ganglia. Returns positions, typed edges, metadata."""
    pos, tissue, seg, quad = [], [], [], []
    C, L, G = {}, {}, {}
    def add(p, t, s, q):
        i = len(pos); pos.append(p); tissue.append(t); seg.append(s); quad.append(q); return i
    for i in range(N_SEG):                                       # circular tissue (outer)
        for q in QUADS:
            C[(i, q)] = add((i * SEGX, *(R_C * UDIR[q])), "circ", i, q)
    for i in range(N_SEG):                                       # longitudinal tissue (inner)
        for q in QUADS:
            L[(i, q)] = add((i * SEGX, *(R_L * UDIR[q])), "long", i, q)
    for i in range(N_SEG):                                       # ganglia (ventral cord / IN)
        G[i] = add((i * SEGX, 0.0, -0.05), "gang", i, "-")

    edges, etype, is_musc, stiff = [], [], [], []
    def E(a, b, t, m, k): edges.append((a, b)); etype.append(t); is_musc.append(m); stiff.append(k)
    for i in range(N_SEG):                                       # circular MUSCLE ring (segmental)
        for a, b in zip(RING, RING[1:] + RING[:1]):
            E(C[(i, a)], C[(i, b)], "circ_m", True, K_CM)
    for q in QUADS:                                              # circular structural AP (passive)
        for i in range(N_SEG - 1):
            E(C[(i, q)], C[(i + 1, q)], "circ_s", False, K_CS)
    for q in QUADS:                                              # longitudinal MUSCLE (continuous)
        for i in range(N_SEG - 1):
            E(L[(i, q)], L[(i + 1, q)], "long_m", True, K_LM)
    for i in range(N_SEG):                                       # longitudinal structural ring (passive)
        for a, b in zip(RING, RING[1:] + RING[:1]):
            E(L[(i, a)], L[(i, b)], "long_s", False, K_LS)
    for i in range(N_SEG):                                       # hydrostat B_i: radial outer<->inner
        for q in QUADS:
            E(C[(i, q)], L[(i, q)], "b_rad", False, K_RAD)
    for q in QUADS:                                              # hydrostat: diagonal cross-brace
        for i in range(N_SEG - 1):
            E(C[(i, q)], L[(i + 1, q)], "b_diag", False, K_DIAG)
            E(L[(i, q)], C[(i + 1, q)], "b_diag", False, K_DIAG)
    for i in range(N_SEG - 1):                                   # ventral cord (IN)
        E(G[i], G[i + 1], "cord", False, K_CORD)
    for i in range(N_SEG):                                       # ganglion spokes to BOTH tissues
        for q in QUADS:
            E(G[i], C[(i, q)], "spoke", False, K_SPOKE)
            E(G[i], L[(i, q)], "spoke", False, K_SPOKE)
    return dict(pos=np.array(pos), tissue=np.array(tissue), seg=np.array(seg), quad=np.array(quad),
                edges=edges, etype=np.array(etype), is_musc=np.array(is_musc, bool),
                stiff=np.array(stiff, float), C=C, L=L, G=G)


def build(S):
    # One shared, PULL-ONLY f primitive (a muscle only contracts; non-negative ctrl = contraction
    # amount; the series spring restores). Was gear=1/ctrlrange=-4 4 (bidirectional = could push).
    return build_body(S["pos"], S["edges"], S["stiff"], S["is_musc"],
                      cmax=4.0, gear=1.0, pull_only=True, seg_damp=3.0, name="earthworm")


def run(S, ctrl, T):
    m, d, aoe = build(S); n = int(T / DT); traj = np.zeros((n, len(S["pos"]), 3))
    d.qpos[:] = 0; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    for t in range(n):
        u = np.zeros(m.nu); ctrl(t * DT, S, aoe, u); d.ctrl[:] = u; mujoco.mj_step(m, d)
        traj[t] = d.qpos.reshape(-1, 3) + S["pos"]
    return traj


def seg_len(S, P):
    cen = np.array([P[[S["L"][(i, q)] for q in QUADS]].mean(0) for i in range(N_SEG)])
    return np.diff(cen[:, 0]), cen


def main():
    S = spec()
    nC = int((S["tissue"] == "circ").sum()); nL = int((S["tissue"] == "long").sum())
    print("\nEarthworm — segmented model system (opponent-pair CAZ)")
    print("=" * 70)
    print(f"  DISJOINT muscle tissues: circular {nC} + longitudinal {nL} muscle-side regions "
          f"(V_c ∩ V_l = ∅)")
    print(f"  ganglia G_i: {int((S['tissue']=='gang').sum())}   (ventral cord / integrating channel)")
    print(f"  circular muscle edges: {(S['etype']=='circ_m').sum()} (segmental rings)   "
          f"longitudinal: {(S['etype']=='long_m').sum()} (continuous bundles)")
    print("  OPPONENT-PAIR CAZ (one DOF each):")
    print(f"    · telescoping  x{N_SEG}: circular(seg) ⊕ longitudinal(seg)  via hydrostat B_i  → peristalsis")
    print(f"    · lateral-bend x{N_SEG}: LEFT-long(DL,VL) ⊕ RIGHT-long(DR,VR)               → turning")
    print(f"    · dorsoventral:  NONE (earthworm has no DV muscle)")
    print("=" * 70)

    long_m = np.where(S["etype"] == "long_m")[0]
    gap_of = {}; e = 0
    for q in QUADS:
        for g in range(N_SEG - 1):
            gap_of[long_m[e]] = (q, g); e += 1

    # Demo 1 — peristaltic wave: telescoping pairs sequenced (longitudinal shortening wave)
    T_W = 6.0
    def ctrl_wave(tt, S, aoe, u):
        for e, (q, g) in gap_of.items():
            u[aoe[e]] = 2.0 * max(0.0, np.sin(2 * np.pi * (tt / 2.0 - g / N_SEG)))
    trW = run(S, ctrl_wave, T_W)
    gaps = np.array([seg_len(S, trW[t])[0] for t in range(trW.shape[0])])
    gaps_rel = gaps / gaps[0] - 1.0

    # Demo 2 — turn: lateral-bend pair (contract LEFT longitudinal, relax RIGHT)
    def ctrl_turn(tt, S, aoe, u):
        r = min(1.0, tt / 1.5)
        for e, (q, g) in gap_of.items():
            u[aoe[e]] = r * (4.0 if q in ("DL", "VL") else 0.0)
    trT = run(S, ctrl_turn, 6.0)
    cen0 = seg_len(S, trT[0])[1]; cen1 = seg_len(S, trT[-1])[1]
    chord = cen1[-1, :2] - cen1[0, :2]; nrm = np.array([-chord[1], chord[0]]) / (np.linalg.norm(chord)+1e-9)
    bend = ((cen1[:, :2] - cen1[0, :2]) @ nrm)
    bend = bend[np.argmax(np.abs(bend))]

    print(f"Demo 1 · peristaltic wave: max segment shortening {100*np.abs(gaps_rel).max():.1f}%, "
          f"phase travels head→tail (the telescoping pairs sequenced)")
    print(f"Demo 2 · turn: max body bend {bend/R_L:+.2f}×R_L off the chord "
          f"(lateral-bend pair: left longitudinal contracted)")
    print("=" * 70)

    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.2))
    im = ax[0].imshow(gaps_rel.T, aspect="auto", origin="lower", cmap="RdBu",
                      extent=[0, T_W, 0.5, N_SEG - 0.5],
                      vmin=-np.abs(gaps_rel).max(), vmax=np.abs(gaps_rel).max())
    ax[0].set_title("Demo 1 · peristaltic wave (telescoping CAZ sequenced)\n"
                    "segment shortening; diagonal band = travelling wave", fontsize=9.5)
    ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("segment gap"); ax[0].set_yticks(range(1, N_SEG))
    fig.colorbar(im, ax=ax[0], fraction=0.046, label="Δlength/rest")
    ax[1].plot(cen0[:, 0], cen0[:, 1], "o-", color="#bbb", label="rest")
    ax[1].plot(cen1[:, 0], cen1[:, 1], "o-", color="#c0392b", label="left-long contracted → turn")
    for i, (x, y) in enumerate(cen1[:, :2]): ax[1].text(x, y + 0.01, f"S{i+1}", fontsize=7, ha="center")
    ax[1].set_title(f"Demo 2 · turn (lateral-bend CAZ)\nmax bend {bend/R_L:+.2f}×R_L", fontsize=9.5)
    ax[1].set_aspect("equal"); ax[1].legend(fontsize=8); ax[1].axis("off")
    fig.suptitle("Earthworm — telescoping CAZ (peristalsis) + lateral-bend CAZ (turn), two disjoint "
                 "muscle tissues, no DV", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "earthworm.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print("figure ->", os.path.normpath(out))


if __name__ == "__main__":
    main()
