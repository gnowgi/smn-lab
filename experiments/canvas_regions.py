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
import numpy as np


# --8<-- [start:strata]
def emergent_strata(nodes, edges, core=None):
    """LAYERS that emerge from a directed dependency graph -- the number of strata,
    derived, never stipulated. This is the SAME rule the grammar's
    `render_emergent_canvas` uses: each node's depth is its longest dependency path
    from the source set (nodes with no incoming edge, or the given `core`); the
    number of strata is 1 + max depth. Relaxation is capped at len(nodes) passes
    (cycle-safe). A single coupled blob with no dependency ordering => 1 stratum
    (one undivided canvas); a viscera->axial->appendicular->dexterous ladder => its
    depth."""
    nodes = list(nodes)
    incoming = {n: 0 for n in nodes}
    for (u, v) in edges:
        incoming[v] = incoming.get(v, 0) + 1
    src = core or [n for n in nodes if incoming.get(n, 0) == 0]
    depth = {n: 0 for n in nodes}
    for n in src:
        depth[n] = 0
    for _ in range(max(1, len(nodes))):                  # relax longest paths
        for (u, v) in edges:
            depth[v] = max(depth.get(v, 0), depth.get(u, 0) + 1)
    return 1 + (max(depth.values()) if depth else 0)
# --8<-- [end:strata]


# --8<-- [start:communities]
def graph_communities(W, thresh):
    """REGIONS -- the connected components (4-connected in the graph sense: reachable
    through kept couplings) of the canvas graph after keeping only couplings above
    `thresh`. Undirected for the purpose of a region: a territory is a set of
    mutually-coupled modules. Returns (labels, count). One coupled blob => 1 region
    (one undivided canvas)."""
    W = np.asarray(W, float)
    n = W.shape[0]
    A = (0.5 * (W + W.T)) > thresh
    lab = -np.ones(n, int)
    c = 0
    for s in range(n):
        if lab[s] >= 0:
            continue
        stack = [s]
        lab[s] = c
        while stack:
            u = stack.pop()
            for v in np.nonzero(A[u])[0]:
                if lab[v] < 0:
                    lab[v] = c
                    stack.append(int(v))
        c += 1
    return lab, c
# --8<-- [end:communities]


# --8<-- [start:match]
def community_class_match(comm, cls):
    """PRIMARY order parameter: normalized mutual information (NMI) between the
    emergent communities and the modules' functional classes, in [0, 1]. 1 =
    communities recover the functional classes exactly (regions ARE the functional
    territories); ~0 = communities independent of class (the foils). Crucially,
    unlike a segregation/smoothness score this is NOT inflated by generic graph
    structure -- a canvas that self-organizes on class-free couplings scores ~0, so
    the discriminator is built into the order parameter itself."""
    comm = np.asarray(comm)
    cls = np.asarray(cls)
    n = len(cls)

    def _entropy(x):
        _, cnt = np.unique(x, return_counts=True)
        p = cnt / n
        return float(-np.sum(p * np.log(p + 1e-12)))

    if _entropy(cls) <= 1e-9:            # a single functional class -- trivially matched
        return 1.0                       # (the "one undivided canvas" is checked by n_regions)

    mi = 0.0
    for a in np.unique(comm):
        pa = np.mean(comm == a)
        for b in np.unique(cls):
            pab = np.mean((comm == a) & (cls == b))
            if pab > 0:
                pb = np.mean(cls == b)
                mi += pab * np.log(pab / (pa * pb) + 1e-12)
    denom = 0.5 * (_entropy(comm) + _entropy(cls))
    return 0.0 if denom <= 0 else float(max(0.0, min(1.0, mi / denom)))
# --8<-- [end:match]


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
