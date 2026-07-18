# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""F4 -- the layered body: an axial pivot with emancipated appendages.

The self-graph is not uniformly plastic. Its evolutionarily older **axial** core
is the most stable part -- the pivot the rest of the body swings against, home of
the Basal Action Patterns. The **appendicular** periphery is emancipated from the
axial job: freed of load-bearing, it gains degrees of freedom, and with them the
Haltable and Negotiable Action Patterns where generativity lives -- despite
remaining constrained by the morphology. So the graph is a stable axial hub with a
plastic emancipated rim.

The axial core is taken as the graph's longest path (its main axis); the
appendages are what branches off it.

Run:  ../.venv/bin/python fig_layered_body.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab import morphology as gram
from branched_self_model import build_branched_xml

AXIAL = "#2c3e50"
APPEND = "#e8902a"


def _adj(edges):
    a = {}
    for x, y in edges:
        a.setdefault(x, []).append(y); a.setdefault(y, []).append(x)
    return a


def _farthest(adj, s):
    seen = {s}; par = {s: None}; q = [s]; last = s
    while q:
        n = q.pop(0); last = n
        for m in adj.get(n, []):
            if m not in seen:
                seen.add(m); par[m] = n; q.append(m)
    return last, par


def longest_path(edges):
    """The diameter path of the tree = its main axis."""
    adj = _adj(edges)
    u, _ = _farthest(adj, next(iter(adj)))
    v, par = _farthest(adj, u)
    path = []; n = v
    while n is not None:
        path.append(n); n = par[n]
    return set(path)


def main():
    # a body with a clear axis and one emancipated limb
    arms = [(0.0, 3), (130.0, 2), (230.0, 4)]
    xml, positions, true_edges, jo, jp = build_branched_xml(arms)
    axial = longest_path(true_edges)
    P = gram._norm_positions(positions, true_edges)

    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    for a, b in true_edges:
        on = (a in axial and b in axial)
        ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]],
                color=AXIAL if on else APPEND, lw=5.0 if on else 3.2,
                alpha=0.95 if on else 0.9, solid_capstyle="round", zorder=2)
    for n, (x, y) in P.items():
        on = n in axial
        ax.add_patch(plt.Circle((x, y), 0.20, facecolor=(AXIAL if on else APPEND),
                     edgecolor="#1b2733", lw=1.4, zorder=4))
        ax.text(x, y, str(n), ha="center", va="center", fontsize=8.5,
                color="white", zorder=5)

    # layer labels near the two regions
    ax_xy = np.mean([P[n] for n in axial], axis=0)
    app = [n for n in positions if n not in axial]
    if app:
        ap_xy = np.mean([P[n] for n in app], axis=0)
        ax.annotate("emancipated appendage\nhigher DOF · generativity\nHAP → NAP",
                    ap_xy, textcoords="offset points", xytext=(18, 0), fontsize=9.5,
                    color="#8a5200", va="center",
                    bbox=dict(boxstyle="round,pad=0.4", fc="#fff4e3", ec=APPEND, lw=1.2))
    ax.annotate("axial core\nevolutionarily older · most stable\nthe pivot · BAP",
                (ax_xy[0], ax_xy[1] - 0.1), textcoords="offset points", xytext=(-4, -70),
                fontsize=9.5, color="#e8eef4", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.4", fc=AXIAL, ec="#1b2733", lw=1.0))

    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("The layered body — an axial pivot with an emancipated appendage\n"
                 "stability in the old axial core (BAP); generativity in the freed rim (HAP → NAP)",
                 fontsize=11)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "layered_body.png")
    fig.savefig(out, dpi=130)
    print(f"axial core = segs {sorted(axial)} · appendage = segs {sorted(app)}")
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
