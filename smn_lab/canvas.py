# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Emergent-structure analysis of the broadcasting canvas / any coupling graph.

These are the canonical library home for the order parameters that read the
*emergent* organization of a graph -- the ones the diagram grammar draws as the
emergent canvas and the self/world card leans on:

  * :func:`emergent_strata`   -- LAYERS (depth) of a directed dependency graph;
  * :func:`graph_communities` -- REGIONS (connected components above a coupling
                                 threshold) -- one blob = one undivided canvas;
  * :func:`community_class_match` -- NMI of emergent communities vs functional
                                 classes (the primary canvas-regions order parameter).

They were first written inside ``experiments/canvas_regions.py``; they are moved
here so BOTH that experiment and the always-invoked results module
(:mod:`smn_lab.report`) call the *same* rule -- results are generated in one place,
never forked per experiment. They are experimenter-side summaries (global reads of a
whole graph), so they live in the library's analysis layer, not in the agent's local
per-zone operators (:mod:`smn_lab.network` / :mod:`smn_lab.self_model`).
"""
from __future__ import annotations
import numpy as np


# --8<-- [start:strata]
def emergent_strata(nodes, edges, core=None):
    """LAYERS that emerge from a directed dependency graph -- the number of strata,
    derived, never stipulated. This is the SAME rule the grammar's
    ``render_emergent_canvas`` uses: each node's depth is its longest dependency path
    from the source set (nodes with no incoming edge, or the given ``core``); the
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
    """REGIONS -- the connected components (reachable through kept couplings) of the
    canvas graph after keeping only couplings above ``thresh``. Undirected for the
    purpose of a region: a territory is a set of mutually-coupled modules. Returns
    (labels, count). One coupled blob => 1 region (one undivided canvas)."""
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
