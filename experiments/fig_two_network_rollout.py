# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Batch-generate the two-network view for every §1-§7 experiment page.

One figure per page (figures/two_network_<stem>.png), drawn from the page's body
by morphology.render_two_network (axial) or render_two_network_graph (branched /
sheet / appendicular). The body archetype matches the experiment; the point on
every page is the same -- two networks, mechanical body + one broadcasting canvas.

Run:  ../.venv/bin/python fig_two_network_rollout.py
"""
from __future__ import annotations
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import (crawler_schema, render_two_network,
                                render_two_network_graph)


def _crawler(n, touch=False, fields=("chem",), eye=False):
    return crawler_schema(n_seg=n, touch=touch, field_modalities=fields,
                          localizers=(("vision",) if eye else ()))


def _tree():
    pos = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0), 4: (2, 1), 5: (2, -1)}
    return pos, [(0, 1), (1, 2), (2, 3), (2, 4), (2, 5)]


def _sheet(n=3):
    pos, edges = {}, []
    ix = lambda i, j: i * n + j
    for i in range(n):
        for j in range(n):
            pos[ix(i, j)] = (j, -i)
            if j < n - 1: edges.append((ix(i, j), ix(i, j + 1)))
            if i < n - 1: edges.append((ix(i, j), ix(i + 1, j)))
    return pos, edges


def _appendicular():
    pos = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0),
           4: (1, 1), 5: (1, -1), 6: (3, 1), 7: (3, -1)}
    return pos, [(0, 1), (1, 2), (2, 3), (1, 4), (1, 5), (3, 6), (3, 7)]


# stem -> ("axial", schema)  or  ("graph", (positions, edges))
AGENTS = {
    "sweep_c0_coupling": ("axial", _crawler(3, fields=())),
    "sweep_pred3_antagonistic": ("axial", _crawler(2)),
    "sweep_r1_tonic_load": ("axial", _crawler(2)),
    "sweep_r2_resumption": ("axial", _crawler(2)),
    "self_model_topology": ("axial", _crawler(5)),
    "branched_self_model": ("graph", _tree()),
    "lattice_self_model": ("graph", _sheet(3)),
    "nested_lattice_self_model": ("graph", _sheet(4)),
    "q2_reafference": ("axial", _crawler(5)),
    "reafference_cut_self_graph": ("axial", _crawler(5)),
    "world_in_self_graph": ("axial", _crawler(5)),
    "world_geometry_self_frame": ("axial", _crawler(5)),
    "sweep_q1_modulation": ("axial", _crawler(7)),
    "sweep_geometry_worldmodel": ("axial", _crawler(7)),
    "sweep_q1b_resolution": ("axial", _crawler(7)),
    "sweep_resolution_exponents": ("axial", _crawler(7)),
    "sweep_r5_dual_signal": ("axial", _crawler(2)),
    "sweep_r4_adaptation": ("axial", _crawler(5)),
    "c1_touch": ("axial", _crawler(3, touch=True)),
    "p4_manipulator_objecthood": ("axial", _crawler(2)),
    "p6_haltability_aboutness": ("axial", _crawler(2)),
    "sweep_pred1_haltability": ("axial", _crawler(2)),
    "p5_self_field_object": ("axial", _crawler(2)),
    "p3_crossmodal_discrimination": ("axial", _crawler(5, fields=("chem", "thermal"))),
    "haltability": ("axial", _crawler(5)),
    "p7_scaling_network": ("graph", _appendicular()),
    "p8_objecthood_transition": ("graph", _appendicular()),
    "sweep_pred2_zonal": ("axial", _crawler(2)),
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    for stem, (kind, body) in AGENTS.items():
        fig, ax = plt.subplots(figsize=(8.5, 4.8) if kind == "axial" else (7.5, 5.6))
        if kind == "axial":
            render_two_network(ax, body)
        else:
            render_two_network_graph(ax, body[0], body[1])
        ax.set_title("The two networks of this agent — mechanical body + one "
                     "broadcasting canvas", fontsize=9.5)
        out = os.path.join(figdir, f"two_network_{stem}.png")
        fig.savefig(out, dpi=125, bbox_inches="tight"); plt.close(fig)
    print(f"[generated] {len(AGENTS)} two-network figures in {figdir}")


if __name__ == "__main__":
    main()
