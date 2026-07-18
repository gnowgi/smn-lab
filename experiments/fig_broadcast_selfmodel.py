# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""F2 -- the self-model as the force-directed shadow of the architecture.

The broadcast is a shared space, so the self-model is *potentially a complete
graph*: any zone could couple to any other. In a working agent the weights of
*differentiated action* -- set by the morphology, ontogenetic inheritance, and
developmental history -- collapse that potential K_n into a **force-directed
graph** whose shape the body predicts.

One consistent visual encoding across both panels:
  * node diameter = a zone's TOTAL coupling (its summed weights) -> hubs are the
    largest nodes;
  * edge width    = the PAIRWISE coupling weight between two zones.

  left  -- the POTENTIAL: a complete graph, undifferentiated (uniform faint edges,
           equal nodes);
  right -- the ACTUAL: force-directed by the measured weights. Differentiation
           shows as variation -- the hub swells and its strong edges thicken; the
           morphology (hub + limbs) emerges, the weak potential edges fade.

Run:  ../.venv/bin/python fig_broadcast_selfmodel.py
"""
from __future__ import annotations
import os, sys, itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab import morphology as gram
from smn_lab import self_model as sm
from branched_self_model import run, CONFIGS

SLATE = "#3f5566"
BLUE = "#7aa7cf"
AMBER = "#e8902a"


def draw(ax, layout, W, *, node_r=None, hub=None, potential=False, emph=1.5):
    """Two consistent encodings: node diameter = number of couplings (``node_r``
    per node), edge width = pairwise coupling weight. ``potential`` draws the
    undifferentiated complete graph (uniform faint, equal nodes)."""
    P = gram._norm_positions(layout, [])
    n = W.shape[0]
    Wn = W / (W.max() + 1e-9)
    for i, j in itertools.combinations(range(n), 2):
        if potential:
            ax.plot([P[i][0], P[j][0]], [P[i][1], P[j][1]], color=SLATE,
                    lw=0.7, alpha=0.20, zorder=2)
            continue
        w = Wn[i, j]
        if w < 0.02:
            continue
        we = w ** emph
        ax.plot([P[i][0], P[j][0]], [P[i][1], P[j][1]], color=SLATE,
                lw=0.4 + 6.0 * we, alpha=min(0.92, 0.05 + 0.95 * we),
                solid_capstyle="round", zorder=2)
    for m in range(n):
        r = 0.15 if potential else node_r[m]
        ax.add_patch(plt.Circle(P[m], r, facecolor=(AMBER if m == hub else BLUE),
                     edgecolor="#33414f", lw=1.4, zorder=5))
        ax.text(P[m][0], P[m][1], str(m), ha="center", va="center", fontsize=8,
                color="#132029", zorder=6)
    ax.set_aspect("equal"); ax.axis("off")


def main():
    JV, OMEGA, positions, true_edges, jo, arm = run(CONFIGS["asymmetric"])
    C = sm.coupling(JV, OMEGA)
    n = len(positions)
    A = np.abs(C)
    W = A.T @ A                                     # segment-by-segment coupling
    np.fill_diagonal(W, 0.0)
    # node size = number of couplings (recovered degree): leaf < internal < hub
    rec = sm.recover_edges(C)
    deg = sm.degrees(rec)
    node_r = {m: 0.13 + 0.065 * deg.get(m, 0) for m in range(n)}
    hub = int(max(deg, key=deg.get))

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 5.9))

    th = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    circ = {i: (float(np.cos(t)), float(np.sin(t))) for i, t in zip(range(n), th)}
    Wuni = np.ones((n, n)); np.fill_diagonal(Wuni, 0.0)
    draw(ax[0], circ, Wuni, potential=True)
    ax[0].set_title("Potential — the shared broadcast\n"
                    "a complete graph, undifferentiated", fontsize=10)

    lay = gram.graph_layout_weighted(list(range(n)), W, seed=2)
    draw(ax[1], lay, W, node_r=node_r, hub=hub)
    ax[1].set_title("Actual — sculpted by differentiated action\n"
                    "force-directed by the weights: the morphology emerges", fontsize=10)

    fig.suptitle("The self-model is the force-directed shadow of the architecture — "
                 "a potentially complete broadcast, weighted by differentiated action",
                 fontsize=12)
    fig.text(0.5, 0.045,
             "encoding:  node diameter = number of couplings, degree "
             "(leaf < internal < hub)     ·     edge width = pairwise coupling weight",
             ha="center", fontsize=9.5, color="#3a4a5a")
    fig.tight_layout(rect=[0, 0.06, 1, 0.93])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "broadcast_to_selfmodel.png")
    fig.savefig(out, dpi=130)
    print(f"hub (largest total coupling) = seg {hub}")
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
