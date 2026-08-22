# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Hydra stage 2 -- the whole-net capture reflex, emerging with NO central control.

Architecture (corrected): the IN cannot command. It broadcasts the prey-SNAPSHOT -- the
prey's location relative to the mouth, made globally available (non-decremental). Each DFN
CAZ link reads that shared snapshot PLUS its own recovered geometry (its graph-distance to
the mouth) and acts LOCALLY through its opposing pair: a link on the mouth-ward side of the
prey contracts, drawing the caught region toward the mouth. The coordinated whole-net
conveyance EMERGES from these local rules all reading one shared snapshot -- nobody
commands.

Object-directedness via a reafference threshold: the reflex fires only for a **moving mass
above threshold** (a struggling prey -> world-caused, persistent motion at the contact),
not for a static or weak touch (inert debris). *The flea pushed me* vs *a static speck*.

Body: a closed tube sac; the oral ring (col 0) = the MOUTH; the foot ring (last col) is
anchored (sessile). Prey caught at a body node k is conveyed to the mouth iff the reflex
fires.

Order parameters:
  * CAPTURE: fractional reduction of the prey->mouth graph-distance in space (did it arrive);
  * RECRUITMENT: fraction of the body's links that act (whole-net, not local);
  * DISCRIMINATION: capture(prey, moving supra-threshold) vs capture(debris, static/weak).

Run:  ../.venv/bin/python hydra_capture_reflex.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.lattice import build_lattice_xml, lattice_edges

DT = 0.002
N_COL, N_ROW = 7, 6
NSEG = N_COL * N_ROW
SENSE_STEPS, REFLEX_STEPS = 150, 900
CONTRACT = -3.0                       # actuator command that SHORTENS the tendon (pulls in)
THETA = 0.15                          # reafference threshold on moving-contact energy
SEED = 0


def idx(r, c):
    return r * N_COL + c


def bfs_to_mouth(edges, mouth):
    adj = {i: [] for i in range(NSEG)}
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    V = {i: 1e9 for i in range(NSEG)}
    q = list(mouth)
    for m0 in mouth:
        V[m0] = 0
    while q:
        u = q.pop(0)
        for w in adj[u]:
            if V[w] > V[u] + 1:
                V[w] = V[u] + 1; q.append(w)
    return V


def build():
    xml = build_lattice_xml(n_col=N_COL, n_row=N_ROW, closed=True)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(NSEG)]
    return m, d, bid


def node_pos(d, bid, i):
    return d.xpos[bid[i]].copy()


def anchor_foot(d, bid, foot):
    for i in foot:
        adr = 3 * i
        d.qpos[adr:adr + 3] = 0.0
        d.qvel[adr:adr + 3] = 0.0


def run(stim, k, edges, V, mouth, foot, rng):
    m, d, bid = build()
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    mouth_c0 = np.mean([node_pos(d, bid, i) for i in mouth], axis=0)
    dist0 = np.linalg.norm(node_pos(d, bid, k) - mouth_c0)

    # --- PHASE 1: the touch. prey = moving (oscillating) supra-threshold force;
    #     debris = a weak static poke. Sense the moving-contact energy at k. ---
    energy = 0.0
    for i in range(SENSE_STEPS):
        d.xfrc_applied[:] = 0
        t = i * DT
        if stim == "prey":
            f = 14.0 * np.sin(2 * np.pi * 6.0 * t)        # struggling: strong, moving
        else:
            f = 1.2                                        # debris: weak, static
        d.xfrc_applied[bid[k], 2] = f
        anchor_foot(d, bid, foot)
        mujoco.mj_step(m, d)
        energy += abs(d.qvel[3 * k + 2]) * DT              # world-caused motion at the contact
    prey_signal = energy                                   # the IN broadcasts this (a scalar)
    gate = prey_signal > THETA                             # reafference: moving mass beyond threshold?

    # --- PHASE 2: the reflex. Each link reads the shared snapshot (prey at node k -> V[k])
    #     and its OWN V; a link on the mouth-ward side of the prey contracts. No controller. ---
    Vk = V[k]
    active = [L for L, (a, b) in enumerate(edges)
              if gate and V[a] <= Vk and V[b] <= Vk] if gate else []
    dist_t = []
    for i in range(REFLEX_STEPS):
        d.xfrc_applied[:] = 0
        d.ctrl[:] = 0
        for L in active:
            d.ctrl[L] = CONTRACT
        anchor_foot(d, bid, foot)
        mujoco.mj_step(m, d)
        if i % 15 == 0:
            mc = np.mean([node_pos(d, bid, j) for j in mouth], axis=0)
            dist_t.append(np.linalg.norm(node_pos(d, bid, k) - mc))
    distf = dist_t[-1] if dist_t else dist0
    capture = float((dist0 - distf) / (dist0 + 1e-9))
    recruit = len(active) / m.nu
    return dict(gate=gate, prey_signal=prey_signal, capture=capture,
                recruit=recruit, dist_t=np.array(dist_t), dist0=dist0)


def main():
    rng = np.random.default_rng(SEED)
    m0, d0, _ = build()
    edges = lattice_edges(N_COL, N_ROW, closed=True)
    mouth = [idx(r, 0) for r in range(N_ROW)]
    foot = [idx(r, N_COL - 1) for r in range(N_ROW)]
    V = bfs_to_mouth(edges, mouth)
    k = idx(3, N_COL // 2)                                  # a body node mid-way to the mouth

    res = {s: run(s, k, edges, V, mouth, foot, rng) for s in ("prey", "debris")}

    print("\nHydra capture reflex -- whole-net conveyance, no central control\n" + "=" * 68)
    print(f"body: closed tube {N_ROW}x{N_COL}={NSEG} zones; mouth=oral ring, foot anchored")
    print(f"prey caught at node {k} (graph-distance {V[k]} from the mouth)\n")
    print(f"{'stimulus':<10}{'moving-energy':>14}{'gate':>7}{'recruited':>11}{'capture':>10}")
    for s in ("prey", "debris"):
        r = res[s]
        print(f"{s:<10}{r['prey_signal']:>14.3f}{str(r['gate']):>7}"
              f"{r['recruit']:>10.0%}{r['capture']:>9.0%}")
    print("=" * 68)
    ok = (res["prey"]["gate"] and not res["debris"]["gate"]
          and res["prey"]["capture"] > 0.3 and res["prey"]["capture"] > res["debris"]["capture"] + 0.2)
    print(f"Object-directed capture [{'PASS' if ok else 'CHECK'}]: the moving supra-threshold prey")
    print(f"fires the reflex -- the whole mouth-ward net recruits and conveys it "
          f"{res['prey']['capture']:.0%} to the mouth;")
    print(f"the static/weak debris is below threshold, no reflex ({res['debris']['capture']:.0%}). The")
    print(f"conveyance EMERGES from local links reading one shared snapshot -- nobody commands.\n")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    for s, col in (("prey", "#2c6fbb"), ("debris", "#c0392b")):
        r = res[s]
        tt = np.arange(len(r["dist_t"])) * 15 * DT
        ax[0].plot(tt, r["dist_t"], color=col, lw=2.2, label=f"{s} (gate={r['gate']})")
    ax[0].set_xlabel("reflex time (s)"); ax[0].set_ylabel("prey → mouth distance")
    ax[0].set_title("Conveyance to the mouth"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    ax[1].bar([0, 1, 2, 3],
              [res["prey"]["recruit"], res["prey"]["capture"], res["debris"]["recruit"], res["debris"]["capture"]],
              color=["#2c6fbb", "#2c6fbb", "#c0392b", "#c0392b"])
    ax[1].set_xticks([0, 1, 2, 3]); ax[1].set_xticklabels(["prey\nrecruit", "prey\ncapture",
                                                           "debris\nrecruit", "debris\ncapture"], fontsize=8)
    ax[1].set_ylim(0, 1.05); ax[1].set_title("Whole-net recruitment & object-directed capture")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "hydra_capture_reflex.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
