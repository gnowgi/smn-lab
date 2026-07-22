# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Paper figures for the SMN preprint (pp1-arxiv-v2), drawn in the FINALIZED
diagram grammar so the paper cannot drift from the bench.

Two figures, saved as both PDF (for the paper) and PNG (for reference) into
smn-lab/figures/; copy the PDFs into pp1-arxiv-v2/figures/:

  diagram_grammar   -- the grammar reference, UPGRADED: the modular-unit morphology
                       view PLUS the finalized TWO-NETWORK view (mechanical body <->
                       DFN(alpha) <-> one broadcasting canvas; double-headed exchange;
                       no canvas->actuator command, C3), plus the CAZ key + legend.
  canvas_emergent   -- the canvas as an EMERGENT dependency digraph, and the bench
                       result that BOTH its regions (breadth) and its layers (depth)
                       self-organize and track morphology, diverging where the body
                       branches. Supports sec:kit-network.

Run:  ../.venv/bin/python paper_figs.py
"""
from __future__ import annotations
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import (crawler_schema, render_morphology, render_two_network,
                                render_emergent_canvas, caz_key, modality_legend)
import sweep_canvas_regions as S


def _save(fig, stem, figdir):
    for ext in ("pdf", "png"):
        out = os.path.join(figdir, f"{stem}.{ext}")
        fig.savefig(out, dpi=130, bbox_inches="tight")
        print(f"[saved] {out}")
    plt.close(fig)


def fig_grammar(figdir):
    """The grammar reference, upgraded with the finalized two-network view."""
    schema = crawler_schema(n_seg=3, touch=True,
                            field_modalities=("chem", "thermal"),
                            localizers=("vision",))
    fig = plt.figure(figsize=(11, 11.6))
    gs = fig.add_gridspec(3, 2, height_ratios=[4.4, 5.4, 1.3],
                          width_ratios=[3.1, 1.0], hspace=0.26, wspace=0.06)

    ax0 = fig.add_subplot(gs[0, :])
    render_morphology(ax0, schema)
    ax0.set_title("Morphology view — where things are mounted\n"
                  "segment blocks · sensors inside (shape = modality, L upper / R "
                  "lower) · CAZ glyph at each joint · anterior eye", fontsize=9.0)

    ax1 = fig.add_subplot(gs[1, :])
    render_two_network(ax1, schema)
    ax1.set_title("Two-network view — the finalized grammar\n"
                  "mechanical body ⇕ DFN (differentiate + filter, α) ⇕ one broadcasting "
                  "canvas (IN); the exchange is double-headed and no arrow runs "
                  "canvas→actuator (C3)", fontsize=9.0)

    ax2 = fig.add_subplot(gs[2, 0]); caz_key(ax2)
    ax3 = fig.add_subplot(gs[2, 1])
    modality_legend(ax3, ["touch", "chem", "thermal", "vision"])
    _save(fig, "diagram_grammar", figdir)


def fig_canvas_emergent(figdir):
    """The canvas as an emergent dependency digraph + the regions/layers result."""
    levels = [k for _, k in S.MORPHS]
    reg = [int(S._median_run(k, "structured", "n_regions")) for k in levels]
    strata = [int(S._median_run(k, "structured", "n_strata")) for k in levels]
    m_struct = float(S._median_run(5, "structured", "match"))
    m_np = float(S._median_run(5, "no_plasticity", "match"))
    m_sc = float(S._median_run(5, "scrambled", "match"))
    ex = S.run_one(5, "structured", seed=0)

    fig = plt.figure(figsize=(13, 4.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.3, 0.8], wspace=0.3)

    axA = fig.add_subplot(gs[0, 0])
    render_emergent_canvas(axA, ex["nodes"], ex["edges"], 0.0, 6.0, 0.0, 5.2,
                           label=False)
    axA.set_xlim(-0.5, 6.5); axA.set_ylim(-0.5, 6.2); axA.set_aspect("equal")
    axA.axis("off")
    axA.set_title("The canvas is an emergent dependency digraph\n"
                  "(regions = communities; layers = strata, derived)", fontsize=9)

    axB = fig.add_subplot(gs[0, 1])
    axB.plot(levels, reg, "-o", color="#1538a0", lw=2, label="regions (breadth)")
    axB.plot(levels, strata, "-s", color="#1b8a5a", lw=2, label="layers (depth)")
    axB.set_xlabel("morphological complexity (body grows →)")
    axB.set_ylabel("emergent structure")
    axB.set_xticks(levels)
    axB.set_xticklabels([m.replace("\n", " ") for m, _ in S.MORPHS], fontsize=7.5,
                        rotation=12, ha="right")
    axB.set_ylim(0, max(reg) + 1.0)
    axB.annotate("diverge where\nthe body branches", xy=(4, strata[3]),
                 xytext=(2.9, max(reg) + 0.1), fontsize=8, color="#555", ha="center",
                 arrowprops=dict(arrowstyle="->", color="#999"))
    axB.set_title("Both regions and layers are constructed\nand track morphology",
                  fontsize=9)
    axB.legend(fontsize=8, loc="upper left")

    axC = fig.add_subplot(gs[0, 2])
    axC.bar(["structured", "no-plast.", "scrambled"], [m_struct, m_np, m_sc],
            color=["#1538a0", "#b00000", "#e8902a"])
    axC.axhline(0.7, ls="--", color="0.5", lw=1)
    axC.set_ylim(0, 1.02)
    axC.set_ylabel("community–class match (NMI)")
    axC.set_title("The primary order parameter\nseparates the foils directly",
                  fontsize=9)
    for i, v in enumerate([m_struct, m_np, m_sc]):
        axC.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    axC.tick_params(axis="x", labelsize=7.5)
    _save(fig, "canvas_emergent", figdir)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    fig_grammar(figdir)
    fig_canvas_emergent(figdir)
