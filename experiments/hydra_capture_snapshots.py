# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Stage 2, seen as SNAPSHOTS in time -- the prey's trajectory to the mouth.

Runs the whole-net capture reflex (prey condition) and records the WHOLE body's
configuration at several instants, then renders them as a filmstrip: the sac deforming
as the caught prey is conveyed, step by step, to the mouth. Each panel is a snapshot of
the world-in-action at that time; together they are the trajectory.

Run:  ../.venv/bin/python hydra_capture_snapshots.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab.lattice import lattice_edges
from hydra_capture_reflex import (build, bfs_to_mouth, idx, anchor_foot, node_pos,
                                  DT, N_COL, N_ROW, NSEG, CONTRACT, THETA,
                                  SENSE_STEPS, REFLEX_STEPS)

PROJ = (0, 2)          # project world (x, z) -- oral-aboral axis vs a cross-section axis


def draw(ax, P, edges, mouth, foot, k, trail, t, dist):
    px, pz = P[:, PROJ[0]], P[:, PROJ[1]]
    for a, b in edges:
        ax.plot([px[a], px[b]], [pz[a], pz[b]], color="#c9d3dc", lw=0.8, zorder=1)
    ax.scatter(px, pz, s=22, color="#5b7089", zorder=2)
    ax.scatter(px[mouth], pz[mouth], s=40, color="#27ae60", zorder=3, label="mouth")
    ax.scatter(px[foot], pz[foot], s=34, color="#7f8c8d", marker="s", zorder=3, label="foot (anchored)")
    if len(trail) > 1:
        tr = np.array(trail)
        ax.plot(tr[:, 0], tr[:, 1], color="#c0392b", lw=1.6, alpha=0.7, zorder=4)
    ax.scatter([px[k]], [pz[k]], s=110, color="#c0392b", edgecolor="k", zorder=5, label="prey")
    ax.set_title(f"t = {t:.2f}s   ·   prey→mouth = {dist:.2f}", fontsize=9)
    ax.set_aspect("equal"); ax.axis("off")


def main():
    edges = lattice_edges(N_COL, N_ROW, closed=True)
    mouth = [idx(r, 0) for r in range(N_ROW)]
    foot = [idx(r, N_COL - 1) for r in range(N_ROW)]
    V = bfs_to_mouth(edges, mouth)
    k = idx(3, N_COL // 2)

    m, d, bid = build()
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    mouth_c = np.mean([node_pos(d, bid, i) for i in mouth], axis=0)

    # PHASE 1: the moving prey touch -> sense the world-caused energy -> gate
    energy = 0.0
    for i in range(SENSE_STEPS):
        d.xfrc_applied[:] = 0
        d.xfrc_applied[bid[k], 2] = 14.0 * np.sin(2 * np.pi * 6.0 * i * DT)
        anchor_foot(d, bid, foot); mujoco.mj_step(m, d)
        energy += abs(d.qvel[3 * k + 2]) * DT
    gate = energy > THETA
    Vk = V[k]
    active = [L for L, (a, b) in enumerate(edges) if V[a] <= Vk and V[b] <= Vk] if gate else []

    # PHASE 2: the reflex; capture the whole configuration at 6 instants
    snap_at = list(np.linspace(0, REFLEX_STEPS - 1, 6).astype(int))
    snaps, trail = [], []
    for i in range(REFLEX_STEPS):
        d.xfrc_applied[:] = 0; d.ctrl[:] = 0
        for L in active:
            d.ctrl[L] = CONTRACT
        anchor_foot(d, bid, foot); mujoco.mj_step(m, d)
        pk = node_pos(d, bid, k)
        trail.append([pk[PROJ[0]], pk[PROJ[1]]])
        if i in snap_at:
            P = np.array([node_pos(d, bid, j) for j in range(NSEG)])
            mc = np.mean(P[mouth], axis=0)
            snaps.append((i * DT, P.copy(), float(np.linalg.norm(pk - mc)), list(trail)))

    print(f"prey moving-energy {energy:.3f} -> gate={gate}; captured "
          f"{len(active)}/{m.nu} links; {len(snaps)} snapshots")

    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(outdir, exist_ok=True)
    # each captured snapshot as its OWN image
    for fi, (t, P, dist, tr) in enumerate(snaps):
        f1, a1 = plt.subplots(figsize=(5.2, 3.4))
        draw(a1, P, edges, mouth, foot, k, tr, t, dist)
        if fi == 0:
            a1.legend(loc="upper left", fontsize=7, frameon=False)
        f1.tight_layout()
        f1.savefig(os.path.join(outdir, f"hydra_snap_{fi}.png"), dpi=130)
        plt.close(f1)

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 6.6))
    for ax, (t, P, dist, tr) in zip(axes.ravel(), snaps):
        draw(ax, P, edges, mouth, foot, k, tr, t, dist)
    axes.ravel()[0].legend(loc="upper left", fontsize=7, frameon=False)
    fig.suptitle("The capture reflex as snapshots in time — the prey's trajectory to the mouth\n"
                 "(whole-net contraction emerging from local rules on one shared snapshot; no controller)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "hydra_capture_snapshots.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
