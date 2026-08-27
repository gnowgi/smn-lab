# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Consolidation audit — what a CAZ is in each model system, and the coordination kinds.

Two corrections before finalizing nematode + annelid:

(A) The CAZ is an OPPONENT PAIR (one DOF) — but WHICH pair differs by animal, and the opponent
    is sometimes another muscle, sometimes a PASSIVE elastic/hydrostat. The lattice nodes are
    muscle-side regions, never CAZ.
      * Cnidarian: epitheliomuscular contraction  ⊕  mesoglea + hydrostatic cavity (PASSIVE elastic)
                   — the most primitive opponent pair (muscle vs passive). [radial]
      * Nematode : dorsal-longitudinal  ⊕  ventral-longitudinal  (muscle vs MUSCLE, DV bend);
                   cuticle + hydrostatic pressure + resting tone = the passive restoring side.
                   NO circular muscle. Mouth = radial fibres ⊕ elastic recoil. [sourced]
      * Earthworm: circular ⊕ longitudinal (telescoping) + left-long ⊕ right-long (lateral bend);
                   coelomic hydrostat. NO dorsoventral muscle. [sourced]
      * Leech/slug: adds a dorsoventral MUSCLE opponent pair (+ oblique).
    So the nematode's "4 detached longitudinal chains" are 4 muscle-SIDE groups, not 4 CAZ; the
    CAZ is the dorsal⊕ventral opponent pair. Reading nodes as CAZ mis-states the DOF.

(B) The cnidarian has TWO lattice layers coupled ONLY at the rim. Is that inter-layer messaging
    net a DFN or an IN? NEITHER, cleanly. DFN = intra-net differentiated opposing-zone coupling
    (damped, geometry-bearing, local); IN = integration board (non-decremental global snapshot;
    needs ganglia, which cnidarians lack). The rim coupling BETWEEN two epithelial sheets is a
    different, more primitive kind of coordination — an inter-tissue GATEWAY. Best labelled
    "neither / uncertain", not forced into the dichotomy.

Run:  ../.venv/bin/python caz_coordination_audit.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle, Circle, FancyArrowPatch

C_MUS, C_MUS2, C_PASV = "#c0392b", "#2c7fb8", "#cdbf9a"
C_DFN, C_IN, C_NEITHER = "#2c7fb8", "#c0392b", "#7f8c8d"


def split(ax, x, y, r, fa, fb, vertical=True, z=6):
    (a0, a1), (b0, b1) = ((90, 270), (-90, 90)) if vertical else ((0, 180), (180, 360))
    ax.add_patch(Wedge((x, y), r, a0, a1, facecolor=fa, edgecolor="k", lw=1.2, zorder=z))
    ax.add_patch(Wedge((x, y), r, b0, b1, facecolor=fb, edgecolor="k", lw=1.2, zorder=z))


def main():
    fig = plt.figure(figsize=(19, 10))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.05, 1])

    # ================= A: the CAZ opponent pair per model system =================
    axA = fig.add_subplot(gs[0]); axA.axis("off"); axA.set_xlim(0, 20); axA.set_ylim(0, 10)
    axA.set_title("A · a CAZ = one opponent pair = one DOF — but WHICH pair (and whether the "
                  "opponent is muscle or passive elastic) differs by animal", fontsize=12, loc="left")
    cols = [
        (2.4, "CNIDARIAN", "epitheliomuscular\n⊕\nmesoglea + hydrostat", "muscle vs PASSIVE elastic",
         C_MUS, C_PASV, "radial contraction", "the most primitive pair"),
        (7.0, "NEMATODE", "dorsal-long\n⊕\nventral-long", "muscle vs MUSCLE (DV bend)",
         C_MUS, C_MUS, "NO circular · cuticle/hydrostat = restoring", "mouth = radial ⊕ elastic recoil"),
        (11.8, "EARTHWORM", "circular\n⊕\nlongitudinal", "telescoping (peristalsis)",
         C_MUS2, C_MUS, "+ left-long ⊕ right-long (lateral bend)", "NO dorsoventral muscle"),
        (16.7, "LEECH / SLUG", "dorsal\n⊕\nventral (added)", "+ DV muscle & oblique",
         C_MUS, C_MUS2, "gravity → DV differentiation", "most muscle layers"),
    ]
    for x, name, pair, kind, fa, fb, note1, note2 in cols:
        axA.text(x, 9.2, name, ha="center", fontsize=10.5, fontweight="bold")
        split(axA, x, 7.3, 0.95, fa, fb, vertical=(name != "CNIDARIAN"))
        axA.text(x, 5.65, pair, ha="center", va="center", fontsize=8.5)
        axA.text(x, 4.5, kind, ha="center", va="center", fontsize=8.5, color="#8a6d00",
                 fontweight="bold")
        axA.text(x, 3.5, note1, ha="center", va="center", fontsize=7.8, color="#555")
        axA.text(x, 2.7, note2, ha="center", va="center", fontsize=7.8, color="#555")
    for xsep in (4.7, 9.4, 14.25):
        axA.plot([xsep, xsep], [2.2, 8.9], color="#e0e0e0", lw=1)
    axA.text(10, 1.3, "lattice NODES are muscle-side REGIONS, never CAZ. The nematode's "
             "\"4 detached longitudinal chains\" are 4 muscle-SIDE groups;", ha="center", fontsize=9)
    axA.text(10, 0.6, "its CAZ is the dorsal⊕ventral opponent pair. Reading a node (or a lone "
             "chain) as a CAZ mis-states the degree of freedom.", ha="center", fontsize=9,
             color="#c0392b")

    # ================= B: three kinds of coordination (the cnidarian question) =================
    axB = fig.add_subplot(gs[1]); axB.axis("off"); axB.set_xlim(0, 20); axB.set_ylim(0, 10)
    axB.set_title("B · the cnidarian's two layers couple only at the rim — is that messaging net "
                  "a DFN, an IN, or neither?", fontsize=12, loc="left")

    # the disk: two layers + rim door
    axB.text(3.2, 9.0, "cnidarian disk — two epithelial lattice layers", ha="center", fontsize=9.5)
    th = np.linspace(np.pi * 0.15, np.pi * 0.85, 40)
    for r, c, lab in ((2.6, C_MUS2, "outer (ectoderm)"), (1.7, C_MUS, "inner (endoderm/gut)")):
        axB.plot(3.2 + r * np.cos(th), 3.6 + r * np.sin(th), color=c, lw=4)
    # rim connection (the only door)
    for sgn in (-1, 1):
        xr = 3.2 + sgn * 2.6 * np.cos(np.pi * 0.15)
        axB.plot([xr, 3.2 + sgn * 1.7 * np.cos(np.pi * 0.15)], [3.6 + 2.6 * np.sin(np.pi * 0.15),
                 3.6 + 1.7 * np.sin(np.pi * 0.15)], color="#8e44ad", lw=3)
    axB.text(3.2, 5.05, "?", ha="center", fontsize=20, color=C_NEITHER, fontweight="bold")
    axB.text(3.2, 1.9, "connected ONLY at the rim\n(the only mechanical door: ~0.6% through)",
             ha="center", fontsize=8, color="#555")
    axB.annotate("inter-layer\nmessaging net", (3.2, 4.4), (0.2, 6.6), fontsize=8,
                 color=C_NEITHER, arrowprops=dict(arrowstyle="-", color=C_NEITHER))

    def box(x, c, title, lines):
        axB.add_patch(Rectangle((x, 1.4), 4.3, 6.6, facecolor="none", edgecolor=c, lw=2))
        axB.text(x + 2.15, 7.4, title, ha="center", fontsize=10, fontweight="bold", color=c)
        for k, ln in enumerate(lines):
            axB.text(x + 0.2, 6.5 - k * 0.72, ln, fontsize=8.2, va="top", color="#333")

    box(7.0, C_DFN, "DFN (differentiate)", [
        "intra-net, differentiated coupling;", "opposing zones, damped/decremental;",
        "geometry-bearing, LOCAL;", "controls leakage within ONE net.",
        "", "→ not this: the rim couples", "   TWO separate sheets, not zones", "   inside one net."])
    box(11.6, C_IN, "IN (integrate)", [
        "non-decremental broadcast board;", "one global SNAPSHOT → body as one;",
        "needs ganglia/condensations —", "cnidarians have NONE.",
        "", "→ not this: no broadcast,", "   no snapshot, no ganglion;", "   a local rim bridge only."])
    box(16.2, C_NEITHER, "NEITHER (our read)", [
        "an inter-tissue GATEWAY:", "couples two epithelial layers", "at one place (the rim);",
        "a different, more primitive", "kind of coordination.",
        "", "→ best labelled uncertain;", "   don't force the dichotomy."])
    axB.annotate("", xy=(16.1, 4.7), xytext=(6.0, 4.7),
                 arrowprops=dict(arrowstyle="-|>", color=C_NEITHER, lw=2))
    axB.text(10.8, 0.5, "The DFN/IN split was derived for differentiation-vs-integration WITHIN one "
             "net. Coupling BETWEEN two tissue layers is a third axis — not yet DFN or IN.",
             ha="center", fontsize=8.6, color="#333")

    fig.suptitle("Consolidation audit — CAZ = opponent pair (which pair varies by animal); the "
                 "cnidarian inter-layer rim coupling is neither DFN nor IN", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "caz_coordination_audit.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=130); print("figure ->", os.path.normpath(out))


if __name__ == "__main__":
    main()
