# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The two networks of an SMN agent, in the diagram grammar (generated from the
schema by morphology.render_two_network, so the figure cannot drift from code).

Left: an agent's two networks -- the MECHANICAL body above, the ONE broadcasting
CANVAS below. Single-interface transducers reach the canvas through their OWN
colour-coded channels, bundled through a modulation gate (alpha; only modulated
data enters). The EYE is drawn as an ORBIT unit (several extraocular CAZ pairs)
with its own bundle -- vision is the paradigm sensorimotor contingency, not a
passive sensor.

Right: the canvas's regional structure is CONSTRUCTED, not given -- an emergent
dependency digraph whose LAYERS emerge from the graph (strata derived, never
stipulated). A simple agent has one undivided canvas; a complex body's canvas
self-stratifies.

Run:  ../.venv/bin/python fig_two_network_grammar.py
"""
from __future__ import annotations
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import (crawler_schema, render_two_network,
                                render_emergent_canvas)

# a small dependency digraph -- only the edges are declared; strata emerge.
CORE = ["v0", "v1", "v2"]                                # visceral core (few hubs)
AX = ["a0", "a1", "a2", "a3"]
AP = ["p0", "p1", "p2", "p3", "p4"]
NODES = CORE + AX + AP
EDGES = [("v0", "a0"), ("v0", "a1"), ("v1", "a1"), ("v1", "a2"), ("v2", "a2"),
         ("v2", "a3"), ("a0", "a2"), ("a1", "a3"),
         ("a0", "p0"), ("a1", "p1"), ("a2", "p2"), ("a2", "p3"), ("a3", "p4")]


def main():
    fig = plt.figure(figsize=(16, 6.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.12)

    axL = fig.add_subplot(gs[0, 0])
    schema = crawler_schema(n_seg=5, touch=True, field_modalities=("chem", "thermal"),
                            localizers=("vision",))
    render_two_network(axL, schema)
    axL.set_title("An agent's two networks — mechanical body (with an EYE on its orbit) "
                  "+ one broadcasting canvas\n"
                  "single-interface transducers bundle through the α gate; the eye is a "
                  "sensorimotor-contingency unit (extraocular CAZs + its own bundle)",
                  fontsize=9.3)

    axR = fig.add_subplot(gs[0, 1])
    render_emergent_canvas(axR, NODES, EDGES, 0.0, 6.0, 0.0, 6.0, core=CORE)
    axR.set_xlim(-0.4, 8.4); axR.set_ylim(-0.6, 6.9); axR.set_aspect("equal")
    axR.axis("off")
    axR.set_title("The canvas's regions are CONSTRUCTED, not given\n"
                  "layers EMERGE as a dependency digraph (core = a few coupled hubs; "
                  "size = degree)", fontsize=9.3)

    fig.suptitle("The two networks of an SMN agent — mechanical body + the single "
                 "broadcasting canvas (regions constructed, not given)", fontsize=12,
                 y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "two_network_grammar.png")
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
