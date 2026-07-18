# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Lattice self-model: one function, any body (chain / sheet / tube).

The self-model read-out that recovers a chain's order and a branched body's tree is
topology-general. Here we show it recovers a **2-D** body too: a sheet (two linked
chains) and a tube (>=3 chains closed into a ring). The claim (Phase I.1): the SAME
framework read-out -- ``smn_lab.self_model.coupling`` -- recovers the body graph
whatever the shape, with no change to the function.

Mechanism. Each CAZ link (a spring-tendon muscle) is driven independently while the
body is overdamped (soft tissue / low Reynolds). In that regime a driven link's
force appears only at its two endpoint segments, so correlating each link's drive
with every segment's motion (``coupling``) makes each link discover the two segments
it couples -- purely locally, no central reader (C3). The union of those edges is
the recovered body graph.

Run:  ../.venv/bin/python lattice_self_model.py
"""
from __future__ import annotations
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.lattice import build_lattice_xml, lattice_edges, lattice_positions
from smn_lab.self_model import coupling            # the model read-out (unchanged)
from smn_lab.metrics import endpoint_recovery      # experimenter-side scoring

DT = 0.002
T_WARM, T_REC = 2.0, 30.0
U_TC, U_SIG = 0.15, 5.0                              # OU drive per link

BODIES = [
    dict(name="chain",  n_col=8, n_row=1, closed=False, label="chain (a muscle)"),
    dict(name="sheet",  n_col=6, n_row=2, closed=False, label="sheet (two linked chains)"),
    dict(name="tube",   n_col=6, n_row=4, closed=True,  label="tube (closed ring)"),
]


def run_one(spec, seed):
    """Drive each CAZ link independently; return C[link, seg] via the framework
    read-out, plus the true edges."""
    xml = build_lattice_xml(n_col=spec["n_col"], n_row=spec["n_row"],
                            closed=spec["closed"])
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    rng = np.random.default_rng(seed)
    edges = lattice_edges(spec["n_col"], spec["n_row"], spec["closed"])
    nseg = spec["n_col"] * spec["n_row"]
    nlink = len(edges)
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)

    u = np.zeros(nlink)
    DRV = np.zeros((n_rec, nlink))
    VX = np.zeros((n_rec, nseg)); VY = np.zeros((n_rec, nseg)); VZ = np.zeros((n_rec, nseg))
    for i in range(n_warm + n_rec):
        u += (-u / U_TC) * DT + U_SIG * np.sqrt(DT) * rng.standard_normal(nlink)
        data.ctrl[:] = u                              # drive each LINK (muscle)
        mujoco.mj_step(model, data)
        if i >= n_warm:
            j = i - n_warm
            DRV[j] = u
            VX[j] = data.qvel[0::3]                    # per-segment slide velocities
            VY[j] = data.qvel[1::3]
            VZ[j] = data.qvel[2::3]
    # common-mode removal (the reafference move), then the SAME read-out per axis
    VX -= VX.mean(1, keepdims=True); VY -= VY.mean(1, keepdims=True); VZ -= VZ.mean(1, keepdims=True)
    # --8<-- [start:readout]
    # C[link, seg] = how much each segment moves when each CAZ link is driven,
    # combining the planar axes -- the SAME framework read-out, unchanged.
    C = np.abs(coupling(DRV, VX)) + np.abs(coupling(DRV, VY)) + np.abs(coupling(DRV, VZ))
    # --8<-- [end:readout]
    return C, edges


def recovered_edges(C, edges):
    """Each link's two strongest co-movers = its recovered endpoints."""
    return [tuple(sorted(int(s) for s in np.argsort(C[L])[::-1][:2]))
            for L in range(len(edges))]


def plot(results, out):
    from matplotlib.patches import FancyArrowPatch
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
    for ax, r in zip(axes, results):
        nc, nr = r["n_col"], r["n_row"]
        def xy(i):                                     # unrolled schematic grid
            row, col = divmod(i, nc)
            return (-col, row)
        true = {frozenset(e) for e in r["edges"]}
        for (a, b) in r["rec"]:
            ok = frozenset((a, b)) in true
            col = "#1538a0" if ok else "#c0392b"
            lw = 2.4 if ok else 1.5
            (xa, ya), (xb, yb) = xy(a), xy(b)
            ra, rb = a // nc, b // nc
            if nr > 2 and abs(ra - rb) == nr - 1:      # wrap edge -> arc (the ring)
                ax.add_patch(FancyArrowPatch((xa, ya), (xb, yb), arrowstyle="-",
                             connectionstyle="arc3,rad=-0.55", color=col, lw=lw,
                             linestyle=(0, (4, 2)), alpha=0.85))
            else:
                ax.plot([xa, xb], [ya, yb], "-", lw=lw, color=col, alpha=0.9)
        pts = np.array([xy(i) for i in range(nr * nc)])
        ax.scatter(pts[:, 0], pts[:, 1], s=70, color="#2c3e50", zorder=3)
        sub = "  (dashed = the wrap that closes the ring)" if r["closed"] else ""
        ax.set_title(f"{r['label']}\nendpoint-recovery = {r['acc']:.2f}{sub}", fontsize=9.5)
        ax.set_aspect("equal"); ax.axis("off"); ax.margins(0.15)
    fig.suptitle("One function, any body — the SAME read-out recovers "
                 "chain, sheet and tube", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


def main():
    seeds = list(range(3))
    print("\nLattice self-model — one function, any body\n" + "=" * 52)
    print(f"{'body':<26}{'seg':>4}{'links':>7}{'recovery':>12}")
    results = []
    for spec in BODIES:
        accs, C_last, edges = [], None, None
        for s in seeds:
            C, edges = run_one(spec, s)
            accs.append(endpoint_recovery(C, edges))
            C_last = C
        acc = float(np.mean(accs))
        nseg = spec["n_col"] * spec["n_row"]
        print(f"{spec['label']:<26}{nseg:>4}{len(edges):>7}"
              f"{acc:>8.2f} ± {np.std(accs):.2f}")
        results.append(dict(**spec, edges=edges, rec=recovered_edges(C_last, edges),
                            acc=acc))
    print("=" * 52)
    print("The same smn_lab.self_model.coupling recovers every topology.\n")
    figdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    plot(results, os.path.join(figdir, "lattice_self_model.png"))


if __name__ == "__main__":
    main()
