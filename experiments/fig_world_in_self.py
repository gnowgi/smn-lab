# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""F3 -- the world model as the second shadow: affordances, in the self-frame.

Panel 3 of the card, on its own and with its source. The world offers a field of
affordances (left, in metric space, around the moving body). The agent does not
represent it in absolute coordinates -- it registers it in the frame of its own
recovered self-model (right), where the source lands on a specific node/limb. The
world model is the world's geometry expressed in the self-model's frame.

Run:  ../.venv/bin/python fig_world_in_self.py
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab import morphology as gram
from smn_lab import self_model as sm
from smn_lab.fields import ScalarField
from branched_self_model import run, CONFIGS


def main():
    JV, OMEGA, positions, true_edges, jo, arm_struct = run(CONFIGS["asymmetric"])
    C = sm.coupling(JV, OMEGA)
    rec = sm.recover_edges(C)
    layout = gram.graph_layout(list(positions), rec, seed=3)

    long_arm = arm_struct[2]
    tip = long_arm["segs"][-1]
    ang = math.radians(long_arm["angle"]); tx, ty = positions[tip]
    src = (tx + 0.10 * math.cos(ang), ty + 0.10 * math.sin(ang))
    field = ScalarField([(src[0], src[1], 1.0, 0.26)])
    node_field = {n: field.sample(*positions[n]) for n in positions}
    source_node = max(node_field, key=node_field.get)

    fig, ax = plt.subplots(1, 2, figsize=(11.2, 5.4))

    # -- left: the world in metric space (a field of affordances around the body) --
    xs = [p[0] for p in positions.values()]; ys = [p[1] for p in positions.values()]
    pad = 0.35
    X, Y, Z = field.grid((min(xs + [src[0]]) - pad, max(xs + [src[0]]) + pad),
                         (min(ys + [src[1]]) - pad, max(ys + [src[1]]) + pad), n=200)
    ax[0].contourf(X, Y, Z, levels=18, cmap="Greens", alpha=0.9)
    for a, b in true_edges:                                # the body, faint
        ax[0].plot([positions[a][0], positions[b][0]], [positions[a][1], positions[b][1]],
                   color="#33414f", lw=2.0, alpha=0.7, zorder=3)
    ax[0].scatter(xs, ys, s=90, color="#dfe6ef", edgecolor="#33414f", lw=1.2, zorder=4)
    ax[0].scatter([src[0]], [src[1]], marker="*", s=320, color="#146b3a",
                  edgecolor="white", lw=1.2, zorder=5)
    ax[0].annotate("source", src, textcoords="offset points", xytext=(10, 8),
                   fontsize=9, color="#0f4023")
    ax[0].set_aspect("equal"); ax[0].axis("off")
    ax[0].set_title("The world — a field of affordances\n(metric space, around the body)",
                    fontsize=10)

    # -- right: the world in the self-frame --
    gram.render_world_in_self(ax[1], layout, rec, node_field, source_node=source_node,
                              modality="chem")
    h = None
    adj = {}
    for a, b in rec:
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    seen = {0}; q = [(0, 0)]
    while q:
        nn, d = q.pop(0)
        if nn == source_node:
            h = d; break
        for m in adj.get(nn, []):
            if m not in seen:
                seen.add(m); q.append((m, d + 1))
    ax[1].set_title(f"The world in the self-frame\n(source on seg {source_node}"
                    + (f", {h} hops from head)" if h is not None else ")"), fontsize=10)

    fig.suptitle("The world model is the second shadow — the world's affordances "
                 "expressed in the self-model's frame", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "world_in_self_frame.png")
    fig.savefig(out, dpi=130)
    print(f"world source on seg {source_node} · figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
