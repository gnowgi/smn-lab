# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Generate the diagram-grammar reference figures from the body schema.

Single source of truth: these figures are drawn by ``smn_lab.morphology`` from
the same schema that parameterizes the simulated body, so the published diagram
cannot drift from the code that ran.

Outputs:
  figures/diagram_grammar.png   -- the annotated A3 crawler + modality legend.
  figures/morphology_ladder.png -- the 1/2/3-block ladder of Lesson 1.

Run:  ../.venv/bin/python morphology_figs.py        (from this directory)
"""
from __future__ import annotations
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import (crawler_schema, render_morphology, render_network,
                                modality_legend, BodySchema, Segment)


def fig_grammar(out):
    schema = crawler_schema(n_seg=3, touch=True,
                            field_modalities=("chem", "thermal"),
                            localizers=("vision",))
    fig = plt.figure(figsize=(11, 8.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[5, 5, 1], hspace=0.18)

    ax0 = fig.add_subplot(gs[0])
    render_morphology(ax0, schema)
    ax0.set_title("Morphology view — where things are mounted\n"
                  "segments (blocks) · CAZ = opposed zone-pair Z+/Z− (half-filled "
                  "circles) · ventral touch skin (hatch) · bilateral field strips "
                  "(ticks) · anterior eye (icon)", fontsize=9.0)

    ax1 = fig.add_subplot(gs[1])
    render_network(ax1, schema)
    ax1.set_title("Network view — who couples to whom\n"
                  "zones (Z+/Z−) and sensors (unfilled circles) as nodes · "
                  "light-blue coupling lines: messaging beam, opponency, "
                  "sensor→CAZ", fontsize=9.0)

    axl = fig.add_subplot(gs[2])
    modality_legend(axl, ["touch", "chem", "thermal", "vision"])
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"[saved] {out}")


def fig_ladder(out):
    """The 1/2/3-block ladder: the morphologies of the epistemic transitions."""
    rows = [
        ("1 block — a pure object (can only be moved)", 1),
        ("2 blocks / 1 CAZ — self/world (reafference), but scallop-stuck", 2),
        ("3 blocks / 2 CAZ — locomotion → aboutness", 3),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 6.6))
    for ax, (title, n) in zip(axes, rows):
        # plain skeleton: blocks + CAZ only (no sensors), to show the ladder
        schema = BodySchema(name=f"A{n}",
                            segments=[Segment(name=("head" if k == 0 else f"s{k}"),
                                              is_head=(k == 0)) for k in range(n)])
        render_morphology(ax, schema, show_labels=True, compass=False)
        ax.set_title(title, fontsize=9.5, loc="left")
    fig.suptitle("The morphological ladder (Lesson 1): each new block unlocks a transition",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    fig_grammar(os.path.join(figdir, "diagram_grammar.png"))
    fig_ladder(os.path.join(figdir, "morphology_ladder.png"))
