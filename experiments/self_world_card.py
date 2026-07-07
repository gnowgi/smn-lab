# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The self/world card -- one figure that tells the whole framework story for an
agent, in the SMN diagram grammar.

Three views, one visual language:
  1. the DESIGNED agent       -- what we built, at metric coordinates (a body:
                                 blocks, a CAZ glyph per joint, the messaging beam);
  2. the RECOVERED self-model -- the abstract graph the agent reconstructs from its
                                 own movement (force-directed from its OWN adjacency,
                                 edge width = measured coupling, branch point ringed);
  3. the WORLD in the self-frame -- a source painted onto the recovered self-graph,
                                 landing on a specific limb -- never in absolute space.

The rendering is a reusable helper (``morphology.self_world_card``) and the recovery
is body-agnostic (``self_model.coupling`` / ``recover_edges``), so ANY experiment
that moves the body can emit its own card. Here we emit two: a branched body and a
chain, to show the same card works for either morphology.

Run:  ../.venv/bin/python self_world_card.py
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab import morphology as gram
from smn_lab import self_model as sm
from smn_lab.fields import ScalarField
from branched_self_model import run, CONFIGS

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")


def make_card(name, arms, world_arm, suptitle):
    """Run a body, recover its self-model, localize a world source on one limb, and
    save its self/world card."""
    JV, OMEGA, positions, true_edges, joint_order, arm_struct = run(arms)
    C = sm.coupling(JV, OMEGA)
    rec = sm.recover_edges(C)
    branch = sm.branch_node(rec)
    edge_w = sm.edge_strength(C)

    # a chemical source just past the tip of the chosen limb
    arm = arm_struct[world_arm]
    tip = arm["segs"][-1]
    ang = math.radians(arm["angle"]); tx, ty = positions[tip]
    src = (tx + 0.10 * math.cos(ang), ty + 0.10 * math.sin(ang))
    field = ScalarField([(src[0], src[1], 1.0, 0.26)])
    node_field = {n: field.sample(*positions[n]) for n in positions}
    source_node = max(node_field, key=node_field.get)

    # shrink the figure height for flat (chain-like) bodies so panels aren't mostly blank
    xs = [p[0] for p in positions.values()]; ys = [p[1] for p in positions.values()]
    ar = (max(ys) - min(ys)) / (max(xs) - min(xs) + 1e-9)
    fig_h = float(np.clip(3.3 + 3.4 * ar, 3.4, 5.4))

    fig = gram.self_world_card(positions, true_edges, rec, head=0, branch=branch,
                               edge_w=edge_w, node_field=node_field,
                               source_node=source_node, modality="chem",
                               suptitle=suptitle, fig_h=fig_h)
    out = os.path.join(FIGDIR, f"self_world_card_{name}.png")
    fig.savefig(out, dpi=130)
    bp = f"seg {branch}" if branch is not None else "none (chain)"
    print(f"[{name}] branch point: {bp} · world on seg {source_node} "
          f"-> {os.path.normpath(out)}")


def main():
    make_card("branched", CONFIGS["asymmetric"], world_arm=2,
              suptitle="The self/world card — branched body")
    make_card("chain", [(0.0, 7)], world_arm=0,
              suptitle="The self/world card — chain body")


if __name__ == "__main__":
    main()
