# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Morphology of the integrator-snapshot configurations, in the diagram grammar.

So a reader can see WHICH body each result ran on, in the same visual vocabulary
as the rest of the bench (split-circle CAZ = one opponent pair = one DOF;
light-blue lines = the coupling / messaging beam):

  (top)    the Phase-A / capacity / capacity->performance NETWORK configuration --
           the coarse-graining hierarchy 36 motor CAZ -> 9 -> 3 beam integrators
           (the lattice also uses 27->9->3->1 and 144->36->12);
  (middle) the Phase-B EMBODIED instance -- the same motor-CAZ layer realized as a
           physical axial opponent chain (rendered by smn_lab.morphology, which
           shares parameters with the MuJoCo builder, so it cannot drift);
  (bottom) the CAZ key.

Run:  ../.venv/bin/python fig_integrator_snapshot_morphology.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import (crawler_schema, render_network, caz_glyph, caz_key,
                                 NETWORK_COLOR)

BEAM_FC = "#eaf2f8"        # beam-integrator node fill (nervous-system layer)


def render_hierarchy(ax, layers=(36, 9, 3), row_gap=3.4):
    """The coarse-graining beam hierarchy in the grammar: the bottom layer is the
    motor CAZ (split-circle glyphs), each upper layer a row of beam-integrator
    nodes pooling a contiguous block below, joined by the light-blue beam."""
    # x-position of node i in a layer = center of the span it covers at the base.
    base_n = layers[0]
    xs = []                                    # xs[l] = list of x-centers in layer l
    for l, n in enumerate(layers):
        edges = np.linspace(0, base_n, n + 1)
        xs.append([(edges[k] + edges[k + 1]) / 2 for k in range(n)])
    ys = [l * row_gap for l in range(len(layers))]

    # coupling: each node to its parent (the pool it feeds)
    for l in range(len(layers) - 1):
        child_n, par_n = layers[l], layers[l + 1]
        for i in range(child_n):
            p = int(i * par_n / child_n)
            ax.plot([xs[l][i], xs[l + 1][p]], [ys[l], ys[l + 1]],
                    color=NETWORK_COLOR, lw=1.0, alpha=0.7, zorder=1)

    # nodes: motor CAZ (bottom) as split-circle glyphs; beam integrators as circles
    r_caz = 0.42
    for i, x in enumerate(xs[0]):
        caz_glyph(ax, x, ys[0], r_caz, dof="lateral", z=5)
    for l in range(1, len(layers)):
        for x in xs[l]:
            ax.add_patch(Circle((x, ys[l]), 0.7, facecolor=BEAM_FC,
                                edgecolor=NETWORK_COLOR, lw=1.6, zorder=5))

    labels = ["motor CAZ — slow, serial strokes (< 10 Hz)",
              "beam integrators — fast refresh (γ), θ hold",
              "snapshot — the held low-D manifold"]
    for l, lab in enumerate(labels[:len(layers)]):
        ax.text(-1.5, ys[l], f"{layers[l]}", ha="right", va="center",
                fontsize=11, fontweight="bold", color="#33414f")
        ax.text(base_n + 1.5, ys[l], lab, ha="left", va="center", fontsize=9,
                color="#33414f")
    ax.set_xlim(-6, base_n + 22)
    ax.set_ylim(-1.4, ys[-1] + 1.4)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Phase A / capacity / capacity→performance — the network configuration: "
                 "36 motor CAZ → 9 → 3 beam integrators\n"
                 "(the lattice also runs 27→9→3→1 · deep-tree, and 144→36→12 · big-brain)",
                 fontsize=10)


def main():
    fig = plt.figure(figsize=(13.5, 10.5))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.15, 0.9, 0.7], hspace=0.28)

    render_hierarchy(fig.add_subplot(gs[0]))

    axB = fig.add_subplot(gs[1])
    schema = crawler_schema(n_seg=6, touch=False, field_modalities=(), localizers=())
    render_network(axB, schema, compass=False)
    axB.set_title("Phase B — the embodied instance: the same motor-CAZ layer as a "
                  "physical axial opponent chain\n"
                  "(drawn A6; the ceiling runs A6, the manifold A10 — one CAZ = one "
                  "hinge = one opponent pair)", fontsize=10)

    caz_key(fig.add_subplot(gs[2]))

    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "integrator_snapshot_morphology.png")
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
