# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""PROTOTYPE — the canvas as an EMERGENT dependency digraph.

GN's suggestion: rather than draw the canvas's regions as stipulated bands (or even
nested rectangles), draw the canvas as ONE directed graph of hubs whose LAYERS
EMERGE from the dependency structure -- we never stipulate how many layers exist.
A digraph with dependency edges, laid out by dependency depth (a proxy for a
force-directed / weighted layout), self-stratifies: the visceral core is a small
cluster of a FEW interconnected hubs (not one), axial hubs depend on it,
appendicular hubs depend on those. Node size = degree (weight); colour = the
EMERGENT depth-stratum.

Run:  ../.venv/bin/python fig_emergent_canvas.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

# a small dependency digraph -- the layers are NOT declared, only the edges are.
CORE = ["C0", "C1", "C2"]                       # visceral: a few interconnected hubs
AX = ["A0", "A1", "A2", "A3"]
AP = ["P0", "P1", "P2", "P3", "P4"]
NODES = CORE + AX + AP

CORE_INTERNAL = [("C0", "C1"), ("C1", "C2"), ("C0", "C2")]        # bidirectional
FORWARD = [                                                       # X -> Y : Y depends on X
    ("C0", "A0"), ("C0", "A1"), ("C1", "A1"), ("C1", "A2"), ("C2", "A2"), ("C2", "A3"),
    ("A0", "A2"), ("A1", "A3"),                                   # axial cross-dependencies
    ("A0", "P0"), ("A1", "P1"), ("A2", "P2"), ("A2", "P3"), ("A3", "P4"),
]


def _depths():
    """Emergent stratum of each node = longest dependency path from the core."""
    d = {n: 0 for n in CORE}
    for _ in range(len(NODES)):                 # relax longest paths
        for (u, v) in FORWARD:
            d[v] = max(d.get(v, 0), d.get(u, 0) + 1)
    for n in NODES:
        d.setdefault(n, 0)
    return d


def main():
    depth = _depths()
    levels = sorted(set(depth.values()))
    deg = {n: 0 for n in NODES}
    for (u, v) in FORWARD + CORE_INTERNAL:
        deg[u] += 1; deg[v] += 1

    # layout: y = -stratum (emergent), x spread within a stratum
    pos = {}
    for lv in levels:
        row = [n for n in NODES if depth[n] == lv]
        xs = np.linspace(-1.6 * (len(row) - 1) / 2, 1.6 * (len(row) - 1) / 2, len(row))
        for n, x in zip(row, xs):
            pos[n] = (x, -1.7 * lv)

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(levels)))
    lvl_color = {lv: cmap[i] for i, lv in enumerate(levels)}

    for (u, v) in FORWARD:                       # directed dependency edges
        ax.add_patch(FancyArrowPatch(pos[u], pos[v], arrowstyle="-|>", mutation_scale=10,
                     color="#9fb0bd", lw=1.1, shrinkA=11, shrinkB=11,
                     connectionstyle="arc3,rad=0.08", zorder=1))
    for (u, v) in CORE_INTERNAL:                 # within-core (bidirectional)
        ax.add_patch(FancyArrowPatch(pos[u], pos[v], arrowstyle="<|-|>", mutation_scale=8,
                     color="#c0392b", lw=1.4, shrinkA=11, shrinkB=11, zorder=1))
    for n in NODES:
        x, y = pos[n]
        r = 0.16 + 0.045 * deg[n]                # size = degree (weight)
        ax.add_patch(Circle((x, y), r, facecolor=lvl_color[depth[n]], edgecolor="#33414f",
                     lw=1.3, zorder=3))
        ax.text(x, y, n, ha="center", va="center", fontsize=7, color="white", zorder=4)

    for lv in levels:                            # label the EMERGENT strata
        ys = -1.7 * lv
        name = {0: "core (a few interconnected hubs)"}.get(lv, f"stratum {lv}")
        ax.text(2.6, ys, name, ha="left", va="center", fontsize=8.5, color="#33414f")

    ax.text(0, 1.1, f"{len(levels)} strata EMERGED (not stipulated) from the dependency "
            "digraph", ha="center", fontsize=10, style="italic", color="#2a3742")
    ax.set_xlim(-3.2, 6.0); ax.set_ylim(-1.7 * (max(levels) + 0.7), 1.6)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("The canvas as an emergent dependency digraph\n"
                 "(node size = degree/weight · colour = emergent stratum · "
                 "red = within-core mutual coupling)", fontsize=10)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "emergent_canvas.png")
    fig.savefig(out, dpi=130, bbox_inches="tight"); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
