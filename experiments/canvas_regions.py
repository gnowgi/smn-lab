# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Canvas regions -- does the broadcasting canvas CONSTRUCT its own functional
structure? ORDER PARAMETERS (the single source of truth).

The broadcasting substrate (the canvas) is ONE undivided field. The framework's
claim is that its functional structure is NOT pre-given (not a description) but
CONSTRUCTED from the functional relations of the modules that keep broadcasting.
This experiment realizes that as an EMERGENT DEPENDENCY DIGRAPH -- the same object
the diagram grammar draws (`smn_lab.morphology.render_emergent_canvas`): modules
broadcast, co-activity builds couplings, and structure emerges from the graph's
topology. Two things emerge that a smoothing map cannot tell apart:

  - REGIONS (breadth): communities of mutually-coupled modules -- the functional
    territories. A simple agent = ONE undivided community (one undivided canvas);
    a complex body partitions itself. Read by `graph_communities` + counted.
  - LAYERS / STRATA (depth): the dependency levels (the L0/L1/L2 ladder), derived
    as the longest dependency path over the graph -- NOT stipulated. Read by
    `emergent_strata`, using the SAME rule as the grammar's emergent canvas.

The PRIMARY order parameter is `community_class_match` (NMI of emergent
communities against the functional classes). Unlike a smoothness/segregation
score it is NOT inflated by generic self-organization: a graph that organizes on
class-FREE couplings scores ~0. That is why the graph formulation needs no
post-hoc criterion correction where the earlier self-organizing-map did (see the
dev-log).

Run:  ../.venv/bin/python canvas_regions.py
"""
from __future__ import annotations
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# The canonical emergent-structure order parameters now live in the library
# (smn_lab.canvas) so this experiment and the always-invoked results module
# (smn_lab.report) call the SAME rule -- one place generates results, never forked.
from smn_lab.canvas import (                       # noqa: E402  (re-exported here)
    emergent_strata, graph_communities, community_class_match,
)


def _self_test():
    """Synthetic self-test of the order parameters (NOT a canvas run): confirm each
    reads a known structure correctly."""
    # strata: a viscera->axial->appendicular chain of communities => 3 strata;
    # a branch (two appendages sharing a parent) does NOT deepen it.
    chain_nodes = ["V", "A", "P"]
    chain_edges = [("V", "A"), ("A", "P")]
    print(f"[chain V->A->P]        emergent_strata="
          f"{emergent_strata(chain_nodes, chain_edges)} (expect 3)")
    branch_nodes = ["V", "A", "PL", "PR"]
    branch_edges = [("V", "A"), ("A", "PL"), ("A", "PR")]
    print(f"[branch (PL,PR share)] emergent_strata="
          f"{emergent_strata(branch_nodes, branch_edges)} (expect 3 -- breadth, not depth)")
    print(f"[single blob]          emergent_strata="
          f"{emergent_strata(['x'], [])} (expect 1 -- one undivided canvas)")

    # communities + match: three clean class-blocks vs a random coupling.
    rng = np.random.default_rng(0)
    cls = np.array([0] * 6 + [1] * 6 + [2] * 6)
    W = np.zeros((18, 18))
    for i in range(18):
        for j in range(18):
            W[i, j] = (0.9 if cls[i] == cls[j] else 0.05) + 0.02 * rng.standard_normal()
    lab, k = graph_communities(W, thresh=0.4)
    print(f"[3 class-blocks]  n_regions={k} (expect 3)  "
          f"community_class_match={community_class_match(lab, cls):.2f} (expect ~1)")

    Wr = 0.3 + 0.05 * rng.standard_normal((18, 18))      # class-free couplings
    labr, kr = graph_communities(Wr, thresh=0.32)
    print(f"[class-free graph] community_class_match="
          f"{community_class_match(labr, cls):.2f} (expect ~0 -- NOT inflated)")

    print("[canvas-regions] order parameters ready. The construction model, the two "
          "foils, and the morphology sweep are wired in sweep_canvas_regions.py.")


if __name__ == "__main__":
    _self_test()
