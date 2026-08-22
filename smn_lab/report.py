# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The one results module -- invoked at the end of EVERY run.

Rationale (modularity). An experiment should decide *what happens in the world* and
*how the body moves*; it should NOT each re-invent *how a result is computed or
drawn*. That re-invention is what let one experiment localize on head-pose while
another used the recovered self-graph -- silent divergence. This module removes the
possibility: an experiment hands over a canonical :class:`RunRecord` and this module
generates the metrics, the SMN-native graph figures, and the emergent-structure
diagnostics -- identically, every time. Change an experiment freely; you cannot
change how a result is generated, because the experiment no longer owns that code.

It is an ORCHESTRATOR, not a re-implementation: recovery is
:mod:`smn_lab.self_model` (graph-first: coupling -> ``recover_edges``; a chain is the
special case that also admits a linear order), scoring is :mod:`smn_lab.metrics`,
network figures are :mod:`smn_lab.morphology` (the diagram grammar), controllability
is :mod:`smn_lab.controllability`, and emergent regions/strata are
:mod:`smn_lab.canvas`. Because SMN *is* a network, the default representation is a
graph/topology and world geometry is reported in ordinal/relational units -- never
metric.

Because the bench is a complex system, the emergent-structure diagnostics run on
EVERY record (whether or not the experiment asked), so that if organization emerges
we notice it instead of missing it.

Contract
--------
Fill a :class:`RunRecord` and call :func:`render`. Minimal record: a movement trace
(``omega``) is enough to recover a self-model; add ``jv`` for signed (directed)
edges; add ``node_field`` for the world-in-self panel; add ``metrics`` for the
order-parameter plot; add ``canvas_*`` for the emergent-canvas strata/regions.
"""
from __future__ import annotations
import os, json
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from smn_lab import self_model as sm
from smn_lab import metrics as mx
from smn_lab import controllability as ctl
from smn_lab import canvas as cvs
from smn_lab import morphology as gram

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FIGDIR = os.path.join(_ROOT, "figures")
DEFAULT_RESULTDIR = os.path.join(_ROOT, "results")


@dataclass
class RunRecord:
    """The canonical hand-off from an experiment to the results module.

    Everything the module reports is relational/ordinal; nothing metric about the
    world leaks in. Provide at least ``omega`` (or a precomputed ``coupling_matrix``).
    """
    name: str
    # --- self-model source (movement) ---
    omega: Optional[np.ndarray] = None          # T x N broadcast channels (segment co-motion)
    jv: Optional[np.ndarray] = None             # T x N efference; if given -> signed coupling
    coupling_matrix: Optional[np.ndarray] = None  # precomputed C (skips the read-out)
    # --- designed body (experimenter-side truth; panel 1) ---
    positions: Optional[dict] = None            # node -> (x, y); default: chain along x
    true_edges: Optional[list] = None           # designed topology; default: chain
    # --- world in the self-frame (panel 3) ---
    node_field: Optional[dict] = None           # node -> world reading (agent-side)
    source_node: Optional[int] = None           # default: argmax(node_field)
    modality: str = "chem"
    # --- the world signal that BUILDS the canvas (the IN), on every modulating run ---
    # T x N per-zone WORLD-caused reading over time (ideally the DFN residual). The
    # canvas is constructed from this whenever the agent modulates -- displacement is
    # NOT required (a sessile body whose zones move still builds a world-model). If
    # given and node_field is not, the proximal snapshot is its time-mean.
    world_signal: Optional[np.ndarray] = None
    # --- experiment-declared order parameters ---
    metrics: dict = field(default_factory=dict)
    # --- optional emergent canvas (the IN's dependency digraph) ---
    canvas_nodes: Optional[list] = None
    canvas_edges: Optional[list] = None         # directed (u, v)
    canvas_core: Optional[list] = None
    canvas_classes: Optional[list] = None       # functional class per node (for NMI)
    # --- recovery mode: "auto" (signed->tree, else chain), "signed", "chain",
    #     or "endpoint" (each row's two strongest-magnitude co-movers = its edge --
    #     the lattice/sheet/tube read-out, C[link, seg] non-negative) ---
    recovery: Optional[str] = None
    # --- provenance ---
    meta: dict = field(default_factory=dict)


# --------------------------------------------------------------- recovery ------
def recover(rec: RunRecord) -> dict:
    """Graph-first self-model recovery (chain is the special case).

    With ``jv`` (or a signed ``coupling_matrix``) we recover the coupling graph and
    read each zone's own edge (``recover_edges``) -- works for branched bodies. With
    only ``omega`` we get an undirected transmission gain and fall back to the chain
    special case: seriate into a linear order and join consecutive nodes.
    """
    signed = False
    if rec.coupling_matrix is not None:
        C = np.asarray(rec.coupling_matrix, float)
        signed = bool(C.min() < -1e-9)
    elif rec.jv is not None and rec.omega is not None:
        C = sm.coupling(np.asarray(rec.jv, float), np.asarray(rec.omega, float))
        signed = True
    elif rec.omega is not None:
        C = sm.transfer(np.asarray(rec.omega, float), np.asarray(rec.omega, float))
    else:
        raise ValueError(f"[{rec.name}] RunRecord needs omega, jv+omega, or coupling_matrix")

    n = C.shape[1]
    mode = rec.recovery or ("signed" if signed else "chain")

    if mode == "endpoint":
        # each row's two strongest-magnitude co-movers are its endpoints -- the
        # lattice/sheet/tube read-out (C[link, seg] non-negative). Works for any body.
        A = np.abs(C)
        rec_edges = [tuple(sorted(int(s) for s in np.argsort(A[L])[::-1][:2]))
                     for L in range(A.shape[0])]
        ew = np.array([A[L, np.argsort(A[L])[::-1][:2]].sum() for L in range(A.shape[0])])
        edge_w = (ew - ew.min()) / (np.ptp(ew) + 1e-9) if len(ew) else ew
        branch = sm.branch_node(rec_edges)
        order = list(range(n))
        chain_assumed = False
    elif mode == "signed":
        rec_edges = sm.recover_edges(C)
        edge_w = sm.edge_strength(C)
        branch = sm.branch_node(rec_edges)
        # a linear order only makes sense for a chain; still provide the seriation of
        # the symmetric coupling of the columns as a best-effort ordinal axis
        Wsym = np.abs(0.5 * (C[:n, :n] + C[:n, :n].T)) if C.shape[0] >= n else None
        order = list(mx.seriation_order(Wsym)) if Wsym is not None else list(range(n))
        chain_assumed = False
    else:
        Wsym = np.abs(0.5 * (C + C.T)); np.fill_diagonal(Wsym, 0.0)
        order = list(mx.seriation_order(Wsym))
        rec_edges = [(int(order[i]), int(order[i + 1])) for i in range(n - 1)]
        ew = np.array([Wsym[order[i], order[i + 1]] for i in range(n - 1)])
        edge_w = (ew - ew.min()) / (np.ptp(ew) + 1e-9) if n > 1 else ew
        branch = sm.branch_node(rec_edges)                    # None for a clean chain
        chain_assumed = True

    # node adjacency of the RECOVERED graph (topology) -- unit weights so the
    # emergent diagnostics (N_D, regions, algebraic connectivity) read the body's
    # structure/symmetry, not the coupling magnitudes. This is square (n x n) even
    # when the coupling read-out C is joint x segment (non-square).
    W = np.zeros((n, n))
    for (a, b) in rec_edges:
        if 0 <= a < n and 0 <= b < n:
            W[a, b] = W[b, a] = 1.0

    positions = rec.positions or {k: (float(k), 0.0) for k in range(n)}
    true_edges = rec.true_edges or [(k, k + 1) for k in range(n - 1)]
    return dict(C=C, W=W, rec_edges=rec_edges, edge_w=edge_w, branch=branch,
                order=order, chain_assumed=chain_assumed,
                positions=positions, true_edges=true_edges, n=n, signed=signed)


# --------------------------------------------------- emergent diagnostics ------
def diagnostics(recov: dict, rec: RunRecord) -> dict:
    """Always-on complex-system readouts of the recovered graph (and the canvas, if
    provided). Cheap, global, and computed for every run so emergence can't slip by."""
    W, rec_edges, n = recov["W"], recov["rec_edges"], recov["n"]
    deg = {}
    for a, b in rec_edges:
        deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
    degseq = [deg.get(k, 0) for k in range(n)]

    L = ctl.graph_laplacian(W)
    evals = np.sort(np.linalg.eigvalsh(L))
    alg_conn = float(evals[1]) if n > 1 else 0.0              # Fiedler value

    d = dict(
        n_nodes=n,
        n_edges=len(rec_edges),
        degree_sequence=degseq,
        max_degree=int(max(degseq) if degseq else 0),
        is_chain=(recov["branch"] is None),
        branch_node=(None if recov["branch"] is None else int(recov["branch"])),
        chain_assumed=recov["chain_assumed"],
        algebraic_connectivity=alg_conn,
        N_D=int(ctl.exact_controllability_nd(W)),             # min driver zones (symmetry)
    )
    # a minimal provable driver set -- only when the combinatorial search is cheap
    if n <= 12:
        try:
            d["driver_nodes"] = [int(x) for x in ctl.min_driver_set(W)]
        except Exception:
            d["driver_nodes"] = None
    # regions of the recovered coupling graph (one blob = one undivided body)
    thresh = 0.15 * float(W.max()) if W.size and W.max() > 0 else 0.0
    _, n_regions = cvs.graph_communities(W, thresh)
    d["n_regions"] = int(n_regions)

    # emergent CANVAS (the IN's dependency digraph), if the experiment supplied one
    if rec.canvas_nodes is not None and rec.canvas_edges is not None:
        d["canvas_strata"] = int(cvs.emergent_strata(
            rec.canvas_nodes, rec.canvas_edges, core=rec.canvas_core))
        if rec.canvas_classes is not None:
            # communities on the canvas coupling if it is a matrix, else by dependency
            comm = _canvas_communities(rec)
            if comm is not None:
                d["canvas_region_class_NMI"] = float(
                    cvs.community_class_match(comm, rec.canvas_classes))
    return d


def build_canvas(world_signal, thresh_frac=0.35):
    """Construct the CANVAS (the IN's world-model) from the per-zone world-caused
    signal -- ALWAYS, whenever the agent modulates (displacement not required).

    The canvas is not the body's mechanical self-graph; its structure is CONSTRUCTED
    from the world stream: which zones co-respond to the world (regions), and in what
    dependency order they are recruited (strata). A sessile hydra whose tentacle zones
    fire in sequence as prey is conveyed to the mouth builds exactly this -- a world
    trajectory across zones, zero displacement.
    """
    X = np.asarray(world_signal, float)
    T, n = X.shape
    Wc = np.abs(sm.read_all(X, X)); Wc = 0.5 * (Wc + Wc.T); np.fill_diagonal(Wc, 0.0)
    thresh = thresh_frac * float(Wc.max()) if Wc.max() > 0 else 0.0
    # REGIONS -- zones that co-respond to the world (one flea -> one territory)
    labels, n_regions = cvs.graph_communities(Wc, thresh)
    # DEPENDENCY DIGRAPH -- within each region, order zones by RECRUITMENT TIME (each
    # zone's peak) and chain consecutive ones. Acyclic by construction; the emergent
    # strata = the depth of the world's recruitment ladder (prey conveyed tentacle->mouth).
    peak = np.argmax(X, axis=0)
    nodes = list(range(n))
    edges = []
    for r in sorted(set(labels)):
        members = sorted([k for k in nodes if labels[k] == r], key=lambda k: peak[k])
        for a, b in zip(members, members[1:]):
            if peak[a] != peak[b]:
                edges.append((a, b))
    strata = cvs.emergent_strata(nodes, edges)
    incoming = {k: 0 for k in nodes}
    for (u, v) in edges:
        incoming[v] += 1
    core = [k for k in nodes if incoming[k] == 0]
    return dict(Wc=Wc, labels=[int(x) for x in labels], n_regions=int(n_regions),
                edges=edges, strata=int(strata), core=core, nodes=nodes)


def _canvas_communities(rec: RunRecord):
    """Undirected components of the canvas dependency graph (labels aligned to
    ``canvas_nodes`` order), for the class-match NMI. Returns None if not derivable."""
    nodes = list(rec.canvas_nodes)
    idx = {nd: i for i, nd in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n))
    for (u, v) in rec.canvas_edges:
        if u in idx and v in idx:
            A[idx[u], idx[v]] = 1.0
    _, _ = None, None
    lab, _ = cvs.graph_communities(A, 0.5)
    return lab


# --------------------------------------------------------------- rendering -----
def _op_plot(ax, metrics: dict):
    """Standard order-parameter bar chart from the experiment's declared metrics."""
    items = [(k, float(v)) for k, v in metrics.items()
             if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not items:
        ax.axis("off"); ax.set_title("order parameters (none numeric)", fontsize=10); return
    names = [k for k, _ in items]; vals = [v for _, v in items]
    ax.bar(range(len(vals)), vals, color="#2c6fbb")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_title("order parameters", fontsize=10); ax.grid(alpha=0.3, axis="y")


def render(rec: RunRecord, spec: Optional[dict] = None) -> dict:
    """The always-invoked entry point. Recovers the self-model, renders the requested
    SMN-native figures, computes emergent diagnostics, writes a machine-readable
    results record, and returns everything as a dict.
    """
    spec = dict(spec or {})
    prefix = spec.get("prefix", rec.name)
    figdir = spec.get("outdir", DEFAULT_FIGDIR)
    resdir = spec.get("results_dir", DEFAULT_RESULTDIR)
    dpi = spec.get("dpi", 130)
    want_card = spec.get("card", True)
    want_op = spec.get("op_plot", bool(rec.metrics))
    os.makedirs(figdir, exist_ok=True); os.makedirs(resdir, exist_ok=True)

    recov = recover(rec)

    # the world signal BUILDS the canvas (always, on any modulating run); it also
    # supplies the proximal snapshot (its time-mean) for the self-graph's world panel.
    node_field = rec.node_field
    if node_field is None and rec.world_signal is not None:
        ws = np.abs(np.asarray(rec.world_signal, float)).mean(0)
        node_field = {k: float(ws[k]) for k in range(len(ws))}
    source_node = rec.source_node
    if source_node is None and node_field:
        source_node = max(node_field, key=node_field.get)

    diag = diagnostics(recov, rec)
    canvas = None
    if rec.world_signal is not None:
        canvas = build_canvas(rec.world_signal)
        diag["canvas_live_regions"] = canvas["n_regions"]
        diag["canvas_live_strata"] = canvas["strata"]

    figures = []
    if want_card:
        ys = [p[1] for p in recov["positions"].values()]
        xs = [p[0] for p in recov["positions"].values()]
        ar = (max(ys) - min(ys)) / (max(xs) - min(xs) + 1e-9)
        fig_h = float(np.clip(3.3 + 3.4 * ar, 3.4, 5.4))
        fig = gram.self_world_card(
            recov["positions"], recov["true_edges"], recov["rec_edges"],
            head=0, branch=recov["branch"], edge_w=recov["edge_w"],
            node_field=node_field, source_node=source_node,
            modality=rec.modality, suptitle=spec.get("suptitle", rec.name),
            fig_h=fig_h)
        p = os.path.join(figdir, f"{prefix}_self_world_card.png")
        fig.savefig(p, dpi=dpi); plt.close(fig); figures.append(p)

    if canvas is not None and spec.get("canvas_fig", True):
        yspan = 0.55 * max(1, canvas["strata"])          # spread strata so nodes don't overlap
        fig, ax = plt.subplots(figsize=(5.4, 2.2 + 0.75 * canvas["strata"]))
        gram.render_emergent_canvas(ax, canvas["nodes"], canvas["edges"],
                                    0.0, 1.0, 0.0, yspan, core=canvas["core"], label=False)
        ax.set_xlim(-0.15, 1.15); ax.set_ylim(-0.25, yspan + 0.3); ax.axis("off")
        ax.set_title(f"The canvas (IN) — world-model built from modulation\n"
                     f"{canvas['n_regions']} region(s), {canvas['strata']} strata emerged",
                     fontsize=10)
        p = os.path.join(figdir, f"{prefix}_canvas.png")
        fig.savefig(p, dpi=dpi); plt.close(fig); figures.append(p)

    if want_op:
        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        _op_plot(ax, rec.metrics); fig.tight_layout()
        p = os.path.join(figdir, f"{prefix}_order_params.png")
        fig.savefig(p, dpi=dpi); plt.close(fig); figures.append(p)

    if spec.get("emergent_fig") and rec.canvas_nodes is not None:
        fig, ax = plt.subplots(figsize=(5.4, 5.0))
        gram.render_emergent_canvas(ax, rec.canvas_nodes, rec.canvas_edges,
                                    0, 1, 0, 1, core=rec.canvas_core)
        p = os.path.join(figdir, f"{prefix}_emergent_canvas.png")
        fig.savefig(p, dpi=dpi); plt.close(fig); figures.append(p)

    out = dict(name=rec.name, metrics=rec.metrics, diagnostics=diag,
               recovered=dict(rec_edges=[list(e) for e in recov["rec_edges"]],
                              order=recov["order"], chain_assumed=recov["chain_assumed"],
                              source_node=(None if source_node is None else int(source_node))),
               figures=figures, meta=rec.meta)
    jpath = os.path.join(resdir, f"{prefix}_results.json")
    with open(jpath, "w") as fh:
        json.dump(out, fh, indent=2, default=_json_default)
    out["results_json"] = jpath
    _print_summary(out)
    return out


def experiment_page(rec: RunRecord, spec: Optional[dict] = None) -> str:
    """A ONE-PAGE, standardized figure for an experiment, in the diagram grammar:

        [ title + one-line description + key metrics ]
        [ 1 · Body plan (morphology) ]   [ 2 · World ]
        [ 3 · Self-model (recovered) ]   [ 4 · World-model (canvas / IN snapshot) ]
        [ 5 · Data (order parameters) .......... full width ]

    The module draws the panels it can from the record (body plan, self-model, canvas)
    with the grammar renderers, so every experiment page reads the same. The two
    experiment-specific panels are supplied as draw callbacks in ``spec``:
      * ``world_draw(ax)``            -- paint the external world (objects/fields/prey);
      * ``plots_draw(fig, cell)``     -- the data/result plots into the GridSpec ``cell``.
    Both optional; omit and the panel shows the world-in-self / the order-parameter bars.
    Meant to double as a page-length paper figure. Returns the saved path.
    """
    import matplotlib.gridspec as _gs
    spec = dict(spec or {})
    prefix = spec.get("prefix", rec.name)
    figdir = spec.get("outdir", DEFAULT_FIGDIR); os.makedirs(figdir, exist_ok=True)
    dpi = spec.get("dpi", 150)

    recov = recover(rec)
    node_field = rec.node_field
    if node_field is None and rec.world_signal is not None:
        ws = np.abs(np.asarray(rec.world_signal, float)).mean(0)
        node_field = {k: float(ws[k]) for k in range(len(ws))}
    source_node = rec.source_node
    if source_node is None and node_field:
        source_node = max(node_field, key=node_field.get)
    canvas = build_canvas(rec.world_signal) if rec.world_signal is not None else None
    lay = gram.graph_layout(list(recov["positions"].keys()), recov["rec_edges"],
                            seed=spec.get("layout_seed", 3))

    fig = plt.figure(figsize=spec.get("page_size", (8.3, 11.0)))
    g = fig.add_gridspec(4, 2, height_ratios=[0.95, 2.0, 2.0, 2.0], hspace=0.36, wspace=0.14)

    # --- title band ---
    axt = fig.add_subplot(g[0, :]); axt.axis("off")
    axt.text(0.0, 0.98, rec.name, fontsize=13.5, fontweight="bold", va="top")
    if spec.get("description"):
        axt.text(0.0, 0.60, spec["description"], fontsize=9.0, va="top", wrap=True)
    d = diagnostics(recov, rec)
    kv = []
    for k, v in (rec.metrics or {}).items():
        kv.append(f"{k}={v:.2g}" if isinstance(v, (int, float)) and not isinstance(v, bool) else f"{k}={v}")
    topo = "chain" if d["is_chain"] else f"branched@{d['branch_node']}"
    line = f"self-model: {topo} · {d['n_nodes']} zones · N_D={d['N_D']} · regions={d['n_regions']}"
    if canvas is not None:
        line += f" · canvas {canvas['n_regions']} region/{canvas['strata']} strata"
    if kv:
        line += "      " + "   ".join(kv)
    axt.text(0.0, 0.02, line, fontsize=8.2, va="bottom", ha="left", color="#33414f")

    # --- 1 · body plan (morphology) ---
    axb = fig.add_subplot(g[1, 0])
    gram.render_body_graph(axb, recov["positions"], recov["true_edges"], head=0,
                           title="1 · Body plan (morphology)")

    # --- 2 · world ---
    axw = fig.add_subplot(g[1, 1])
    if spec.get("world_draw"):
        spec["world_draw"](axw)
    else:
        axw.axis("off")
        axw.text(0.5, 0.5, "(world)", ha="center", va="center", color="#9fb0bd", fontsize=11)
    axw.set_title("2 · World", fontsize=10)

    # --- 3 · self-model (recovered from movement) ---
    axs = fig.add_subplot(g[2, 0])
    gram.render_self_model(axs, lay, recov["rec_edges"], true_edges=recov["true_edges"],
                           branch=recov["branch"], edge_w=recov["edge_w"],
                           title="3 · Self-model (recovered from movement)")

    # --- 4 · world-model (canvas / IN snapshot) ---
    axc = fig.add_subplot(g[2, 1])
    if canvas is not None:
        gram.render_emergent_canvas(axc, canvas["nodes"], canvas["edges"], 0.0, 1.0, 0.0, 1.0,
                                    core=canvas["core"], label=False)
        axc.set_xlim(-0.12, 1.12); axc.set_ylim(-0.15, 1.15); axc.axis("off")
        axc.set_title(f"4 · World-model (canvas): {canvas['n_regions']} region, "
                      f"{canvas['strata']} strata", fontsize=10)
    elif node_field is not None:
        gram.render_world_in_self(axc, lay, recov["rec_edges"], node_field,
                                  source_node=source_node, modality=rec.modality,
                                  title="4 · World-model (world on the self-graph)")
    else:
        axc.axis("off"); axc.set_title("4 · World-model", fontsize=10)

    # --- 5 · data (order parameters) ---
    if spec.get("plots_draw"):
        spec["plots_draw"](fig, g[3, :])
    else:
        axd = fig.add_subplot(g[3, :]); _op_plot(axd, rec.metrics or {})
        axd.set_title("5 · Data (order parameters)", fontsize=10)

    if spec.get("suptitle"):
        fig.suptitle(spec["suptitle"], fontsize=12, y=0.995)
    out = os.path.join(figdir, f"{prefix}_page.png")
    fig.savefig(out, dpi=dpi, bbox_inches="tight"); plt.close(fig)
    print(f"[page:{rec.name}] -> {os.path.basename(out)}")
    return out


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def _print_summary(out: dict):
    d = out["diagnostics"]
    top = "chain" if d["is_chain"] else f"branched@{d['branch_node']}"
    print(f"\n[report:{out['name']}] self-model: {top} · nodes={d['n_nodes']} "
          f"edges={d['n_edges']} · N_D={d['N_D']} · regions={d['n_regions']} "
          f"· alg.conn={d['algebraic_connectivity']:.3f}")
    if "canvas_live_regions" in d:
        print(f"[report:{out['name']}] canvas (built from modulation): "
              f"regions={d['canvas_live_regions']} · strata={d['canvas_live_strata']} "
              f"(constructed even with no displacement)")
    if "canvas_strata" in d:
        extra = ""
        if "canvas_region_class_NMI" in d:
            extra = f" · region/class NMI={d['canvas_region_class_NMI']:.2f}"
        print(f"[report:{out['name']}] supplied canvas: strata={d['canvas_strata']}{extra}")
    if out["metrics"]:
        ms = "  ".join(f"{k}={v:.3g}" if isinstance(v, (int, float)) and not isinstance(v, bool)
                       else f"{k}={v}" for k, v in out["metrics"].items())
        print(f"[report:{out['name']}] order params: {ms}")
    print(f"[report:{out['name']}] figures: {', '.join(os.path.basename(f) for f in out['figures'])} "
          f"· json: {os.path.basename(out['results_json'])}")
