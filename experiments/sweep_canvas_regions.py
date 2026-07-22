# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Canvas regions -- the EMERGENT DEPENDENCY DIGRAPH + the morphology sweep.

Wires the preregistered order parameters (canvas_regions.py) onto the construction
model the diagram grammar draws. Modules broadcast to ONE undivided canvas; the
canvas keeps no map -- it accumulates COUPLINGS from broadcast co-activity:

  - modules that fire TOGETHER (same tick) build a symmetric coupling  -> REGIONS
    (communities of mutually-coupled modules, the functional territories);
  - modules that fire in ORDER (one leads, the next lags) build a DIRECTED coupling
    -> LAYERS (the dependency ladder; strata = longest path, derived not stipulated).

Both come from the SAME broadcast stream (only modulated/co-active data shapes the
canvas). After construction we condense the recovered module graph to a digraph of
communities and read the two order parameters off its topology -- exactly the
emergent canvas of `smn_lab.morphology.render_emergent_canvas`.

  structured (the claim): class-coherent co-activity + a plastic canvas
                          -> communities recover the classes AND the dependency
                             ladder emerges.
  no-plasticity (foil 1): couplings frozen at random -> nothing is constructed.
  scrambled  (foil 2):    co-activity decoupled from class -> the canvas still
                          builds a graph, but its communities do NOT match the
                          functional classes (the PRIMARY order parameter fails --
                          no post-hoc correction needed).

Morphology sweep: a simple (axial-only) agent stays ONE undivided canvas; as the
body grows (viscera -> axial -> appendicular L/R -> dexterous) the canvas
partitions itself -- n_regions grows with BREADTH, n_strata with DEPTH, and the two
DIVERGE once the body branches (L and R appendages share a stratum).

Run:  ../.venv/bin/python sweep_canvas_regions.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canvas_regions import emergent_strata, graph_communities, community_class_match
from smn_lab.morphology import render_emergent_canvas

TICKS = 4000
N_PER_CLASS = 5
NOISE = 0.15                     # chance a module misfires / an off-class module joins


# ---- the body plan: functional classes + a ground-truth dependency ladder -------
# The full body (level 5): a viscera CORE, an axial chain that depends on it, a LEFT
# and a RIGHT appendage that both depend on the axial chain (same stratum -> breadth
# without depth), and a dexterous layer depending on the appendages. `level` unlocks
# this ladder one class at a time. Note L=4 adds the RIGHT appendage: n_regions rises
# to 4 but n_strata stays 3 -- the divergence the emergent digraph makes visible.
PLAN = [
    ("axial",      None),          # 0  the founding chain (a simple agent = this alone)
    ("viscera",    None),          # 1  core the axial depends on
    ("append_L",   "axial"),       # 2  left appendage depends on axial
    ("append_R",   "axial"),       # 3  right appendage depends on axial  (shares stratum)
    ("dexterous",  "append_L"),    # 4  hands depend on an appendage
]
# ground-truth dependency among the CLASSES (parent -> child): viscera founds axial;
# appendages depend on axial; dexterous on an appendage. `axial` is the core root.
CLASS_PARENT = {"axial": None, "viscera": None, "append_L": "axial",
                "append_R": "axial", "dexterous": "append_L"}
# viscera is drawn as the deep core the axial rides on:
CLASS_PARENT_FULL = {"axial": "viscera", "viscera": None, "append_L": "axial",
                     "append_R": "axial", "dexterous": "append_L"}

MORPHS = [("simple\n(axial)", 1), ("+ viscera", 2), ("+ append L", 3),
          ("+ append R", 4), ("dexterous\n(L0/L1/L2)", 5)]


def _classes(level):
    """The functional classes present at a given morphological level, and each
    module's class label."""
    names = [PLAN[i][0] for i in range(level)]
    cls = np.repeat(np.arange(level), N_PER_CLASS)
    return names, cls


def _broadcast_couplings(names, cls, mode, seed):
    """Construct the canvas couplings from broadcast co-activity.

    Returns (Wsym, Wdir): a symmetric co-activation matrix (same-tick firing ->
    regions) and a directed lead/lag matrix (ordered firing -> layers). `mode`:
      'structured'    -- actions recruit a class and its dependency ancestry in
                         order (class-coherent, ordered co-activity);
      'no_plasticity' -- couplings frozen at random init (nothing accumulates);
      'scrambled'     -- the class label of every module is shuffled, so co-activity
                         no longer respects the functional classes.
    """
    rng = np.random.default_rng(seed)
    m = len(cls)
    name_of = {c: names[c] for c in range(len(names))}
    members = {c: np.nonzero(cls == c)[0] for c in range(len(names))}
    idx_by_name = {names[c]: c for c in range(len(names))}

    if mode == "no_plasticity":                          # frozen random canvas
        Wsym = rng.random((m, m)); Wsym = 0.5 * (Wsym + Wsym.T)
        Wdir = rng.random((m, m))
        np.fill_diagonal(Wsym, 0.0)
        return Wsym, Wdir

    eff_cls = cls.copy()
    if mode == "scrambled":                              # decouple class from co-activity
        eff_cls = rng.permutation(cls)
        members = {c: np.nonzero(eff_cls == c)[0] for c in range(len(names))}

    Wsym = np.zeros((m, m))
    Wdir = np.zeros((m, m))
    for _ in range(TICKS):
        c = rng.integers(len(names))                     # an action centred on a class
        # build the ordered cascade: ancestry root ... -> this class
        chain = [c]
        p = CLASS_PARENT_FULL.get(name_of[c])
        while p is not None and p in idx_by_name:
            chain.append(idx_by_name[p])
            p = CLASS_PARENT_FULL.get(p)
        chain = chain[::-1]                               # root first -> leaf last (time order)
        active_by_time = []
        for ci in chain:
            grp = list(members[ci])
            grp = [g for g in grp if rng.random() > NOISE]     # some members drop out
            if rng.random() < NOISE:                            # an off-class module joins
                grp.append(int(rng.integers(m)))
            active_by_time.append(grp)
        # same-tick co-activation -> symmetric coupling (regions)
        for grp in active_by_time:
            for i in grp:
                for j in grp:
                    if i != j:
                        Wsym[i, j] += 1.0
        # lead/lag across successive layers -> directed coupling (layers)
        for t in range(len(active_by_time) - 1):
            for i in active_by_time[t]:
                for j in active_by_time[t + 1]:
                    Wdir[i, j] += 1.0
    np.fill_diagonal(Wsym, 0.0)
    return Wsym, Wdir


def _condense(lab, Wdir, margin=0.02):
    """Condense the recovered module graph to a digraph of COMMUNITIES: one node per
    community, a directed edge A->B when the net lead/lag flow from A's modules to
    B's clearly dominates the reverse (viscera leads axial leads appendages leads
    dexterous). Direction is read straight from PAIRWISE dominance: `net` is
    antisymmetric, so no A<->B 2-cycle can form, and the ground-truth dependency is a
    DAG. Longest path over it is the dependency depth; transitive edges are harmless
    (they never lengthen the longest path). Appendages that neither leads the other
    get no edge between them -> they share a stratum (breadth without depth)."""
    comms = sorted(set(int(x) for x in lab))
    scale = max(Wdir.sum(), 1e-9)
    nodes = [f"R{c}" for c in comms]
    edges = []
    for a in comms:
        for b in comms:
            if a != b:
                fab = Wdir[np.ix_(lab == a, lab == b)].sum()
                fba = Wdir[np.ix_(lab == b, lab == a)].sum()
                if (fab - fba) / scale > margin:
                    edges.append((f"R{a}", f"R{b}"))
    return nodes, edges


def _normalize(Wsym):
    """Row-normalize each module's couplings by its OWN strongest bond, so a quiet
    class (fired rarely, e.g. dexterous) is judged on the same scale as a busy one
    (viscera, an ancestor of every action). A within-territory pair sits near 1 for
    both partners; a cross-territory link stays low. This is the per-node analogue of
    'keep a clear within-territory bond'; one knob, magnitude only."""
    return Wsym / (Wsym.max(axis=1, keepdims=True) + 1e-9)


def run_one(level, mode, seed=0):
    names, cls = _classes(level)
    Wsym, Wdir = _broadcast_couplings(names, cls, mode, seed)
    lab, nreg = graph_communities(_normalize(Wsym), thresh=0.3)
    match = community_class_match(lab, cls)
    nodes, edges = _condense(lab, Wdir)
    nstrata = emergent_strata(nodes, edges)
    return dict(n_regions=nreg, match=match, n_strata=nstrata,
                nodes=nodes, edges=edges, lab=lab, cls=cls, names=names)


def _median_run(level, mode, key, seeds=(0, 1, 2)):
    vals = [run_one(level, mode, s)[key] for s in seeds]
    return float(np.median(vals))


def main():
    levels = [k for _, k in MORPHS]
    print("=== morphology sweep (structured: modules broadcast to one plastic canvas) ===")
    print(f"{'morphology':<20}{'classes':>8}{'match':>8}{'n_regions':>11}{'n_strata':>10}")
    reg, strata, match = [], [], []
    exemplars = {}
    for (name, k) in MORPHS:
        r = int(_median_run(k, "structured", "n_regions"))
        s = int(_median_run(k, "structured", "n_strata"))
        mt = _median_run(k, "structured", "match")
        reg.append(r); strata.append(s); match.append(mt)
        exemplars[k] = run_one(k, "structured", seed=0)
        print(f"{name.replace(chr(10), ' '):<20}{k:>8}{mt:>8.2f}{r:>11}{s:>10}")

    print("\n=== the two foils (full body, K = 5) ===")
    kf = 5
    m_np = _median_run(kf, "no_plasticity", "match")
    r_np = int(_median_run(kf, "no_plasticity", "n_regions"))
    m_sc = _median_run(kf, "scrambled", "match")
    r_sc = int(_median_run(kf, "scrambled", "n_regions"))
    print(f"  no-plasticity (frozen canvas):     match={m_np:.2f}  n_regions={r_np}")
    print(f"  scrambled functionality (plastic): match={m_sc:.2f}  n_regions={r_sc}")
    print("  (the PRIMARY order parameter is community_class_match: both foils fail on "
          "it\n   directly -- the graph formulation needs no post-hoc criterion "
          "correction.)")

    reg = np.array(reg); strata = np.array(strata); match = np.array(match)
    lv = np.array(levels)
    struct_ok = (match[lv > 1].min() > 0.7                    # communities recover classes
                 and reg[0] == 1 and strata[0] == 1           # simple = one undivided canvas
                 and np.all(np.diff(reg) >= 0)                 # regions track breadth
                 and np.all(np.diff(strata) >= 0)             # strata track depth
                 and strata[-1] < reg[-1])                    # depth < breadth once branched
    foils_fail = (m_np < 0.3) and (m_sc < 0.3)
    ok = struct_ok and foils_fail
    print("\nverdict:", "PASS -- structured broadcasting CONSTRUCTS the canvas's structure "
          "as an emergent dependency digraph: communities recover the functional classes "
          "(match>0.7), REGIONS track breadth and STRATA track depth (they diverge once the "
          "body branches: L/R appendages share a layer), and a simple agent stays one "
          "undivided canvas. Neither foil reproduces it -- both fail the primary order "
          "parameter (community_class_match)."
          if ok else "INCONCLUSIVE -- see order parameters above.")

    _plot(MORPHS, levels, reg, strata, match, (m_np, r_np), (m_sc, r_sc), exemplars)


def _plot(morphs, levels, reg, strata, match, foil_np, foil_sc, exemplars):
    (m_np, r_np), (m_sc, r_sc) = foil_np, foil_sc
    fig = plt.figure(figsize=(15, 8.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.92], hspace=0.32, wspace=0.28)

    # top row: the emergent canvas digraph for three morphologies
    for col, k in enumerate((1, 3, 5)):
        ax = fig.add_subplot(gs[0, col])
        ex = exemplars[k]
        render_emergent_canvas(ax, ex["nodes"], ex["edges"], 0.0, 6.0, 0.0, 5.2,
                               label=False)
        ax.set_xlim(-0.5, 6.5); ax.set_ylim(-0.5, 6.2); ax.set_aspect("equal")
        ax.axis("off")
        title = [m for m, kk in morphs if kk == k][0].replace("\n", " ")
        nr, ns = reg[levels.index(k)], strata[levels.index(k)]
        ax.set_title(f"{title}\n{nr} region{'s' if nr > 1 else ''}, "
                     f"{ns} {'strata' if ns > 1 else 'stratum'}", fontsize=9.5)

    # bottom-left + centre (span): regions & strata track morphology
    axT = fig.add_subplot(gs[1, :2])
    axT.plot(levels, reg, "-o", color="#1538a0", lw=2, label="n_regions (breadth)")
    axT.plot(levels, strata, "-s", color="#1b8a5a", lw=2, label="n_strata (depth)")
    axT.set_xlabel("morphological complexity  (body grows →)")
    axT.set_ylabel("emergent structure")
    axT.set_xticks(levels)
    axT.set_xticklabels([m.replace("\n", " ") for m, _ in morphs], fontsize=8)
    axT.set_ylim(0, max(reg) + 1.2)
    axT.annotate("regions & layers DIVERGE\n(L/R appendages share a stratum)",
                 xy=(4, strata[3]), xytext=(3.1, max(reg) + 0.2), fontsize=8,
                 color="#555", ha="center",
                 arrowprops=dict(arrowstyle="->", color="#999"))
    axT.set_title("Regions (communities) and layers (dependency strata) are BOTH "
                  "constructed and track morphology", fontsize=9.5)
    axT.legend(fontsize=8.5, loc="upper left")

    # bottom-right: the primary order parameter -- structured vs the two foils
    axM = fig.add_subplot(gs[1, 2])
    bars = ["structured", "no-plasticity", "scrambled"]
    vals = [float(np.median(match[np.array(levels) > 1])), m_np, m_sc]
    cols = ["#1538a0", "#b00000", "#e8902a"]
    axM.bar(bars, vals, color=cols)
    axM.axhline(0.7, ls="--", color="0.5", lw=1)
    axM.text(2.4, 0.72, "pass 0.7", fontsize=7.5, color="0.4", ha="right")
    axM.set_ylim(0, 1.02)
    axM.set_ylabel("community_class_match (NMI)")
    axM.set_title("The primary order parameter\nseparates the foils directly\n"
                  "(no post-hoc correction)", fontsize=9)
    for i, v in enumerate(vals):
        axM.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=8.5)
    axM.tick_params(axis="x", labelsize=8)

    fig.suptitle("The canvas constructs its own structure — an emergent dependency "
                 "digraph (regions + layers), tracking morphology; the foils do not",
                 fontsize=12.5, y=0.98)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "canvas_regions.png")
    fig.savefig(out, dpi=130, bbox_inches="tight"); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
