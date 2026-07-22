# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The two networks of an SMN agent, in the diagram grammar.

Generated from the body schema by ``morphology.render_two_network`` (which shares
its parameters with the MuJoCo builder), so the figure cannot drift from the code.
It draws BOTH networks of an agent:

  - the MECHANICAL network -- segments (nodes), muscles/hinge (edges), the
    dual-interface CAZ (split circle), and the single-interface transducers
    (sensors, the major source of data);
  - the MESSAGING network -- ONE broadcasting CANVAS (a high-frequency substrate).
    Every CAZ writes to AND reads from it (network closure); a single-interface
    transducer reaches it only through a CAZ's modulation (only modulated data
    enters). Canvas regions are CONSTRUCTED, not given: an agent with simple
    anatomy has one undivided canvas; regions self-organize as functionality grows
    (cf. the canvas-regions study).

Run:  ../.venv/bin/python fig_two_network_grammar.py
"""
from __future__ import annotations
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import crawler_schema, render_two_network


def main():
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(15, 5.6))

    # A -- a simple agent: one undivided canvas (no regions to partition)
    sA = crawler_schema(n_seg=4, touch=False, field_modalities=("chem",),
                        localizers=())
    render_two_network(axA, sA)
    axA.set_title("A simple, unbranched agent\none undivided canvas — no regions yet",
                  fontsize=10)

    # B -- a richer agent: regions CONSTRUCTED on the canvas as functionality grows
    sB = crawler_schema(n_seg=7, touch=True, field_modalities=("chem", "thermal"),
                        localizers=("vision",))
    render_two_network(axB, sB,
                       regions=["visceral (L0)", "axial (L1)", "appendicular (L2)"])
    axB.set_title("A richer agent — regions CONSTRUCTED on the canvas\n"
                  "(self-organized as functionality grows; cf. canvas-regions)",
                  fontsize=10)

    fig.suptitle("The two networks of an SMN agent — mechanical body + the single "
                 "broadcasting canvas", fontsize=12, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "two_network_grammar.png")
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
