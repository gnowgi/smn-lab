# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The two networks of the C0 agent, in the diagram grammar.

The first rollout of ``morphology.render_two_network`` onto an experiment page:
the 3-block axial crawler (C0) shown as both networks -- the mechanical body and
the one broadcasting canvas. C0 is simple and unbranched, so it has ONE undivided
canvas (no regions yet).

Run:  ../.venv/bin/python fig_two_network_c0.py
"""
from __future__ import annotations
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import crawler_schema, render_two_network


def main():
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    schema = crawler_schema(n_seg=3, touch=False, field_modalities=("chem",),
                            localizers=())
    render_two_network(ax, schema)
    ax.set_title("The two networks of C0 — the 3-block crawler\n"
                 "mechanical body above · one undivided canvas below "
                 "(simple agent, no regions yet)", fontsize=10)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "two_network_c0.png")
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
