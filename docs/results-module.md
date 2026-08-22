# The results module: one place generates every result

Every experiment on this bench ends the same way — it hands its run to
**`smn_lab.report`**, and that module generates the metrics, the SMN-native graph
figures, and the emergent-structure diagnostics. Nothing else draws a self/world
card or scores a self-model. This page is the answer to *"I have a run — how do I
turn it into results the way the bench does?"*

## Why it exists

An experiment should decide **what happens in the world** and **how the body
moves**. It should *not* re-invent **how a result is computed or drawn** — because
the moment two experiments each roll their own plotting and scoring, they drift:
one localizes a world feature on the recovered self-graph, another quietly uses raw
body pose, and the figures no longer mean the same thing. `smn_lab.report` removes
the possibility. Change an experiment freely; you cannot change how a result is
generated, because the experiment no longer owns that code.

It is an **orchestrator, not a re-implementation**. Recovery is
[`smn_lab.self_model`](self-model-and-measurement.md); scoring is `smn_lab.metrics`;
the network figures are the [diagram grammar](diagram-grammar.md)
(`smn_lab.morphology`); controllability is `smn_lab.controllability`; the emergent
regions and strata are `smn_lab.canvas`. The same model/measurement firewall the
rest of the bench keeps (see [model vs. measurement](self-model-and-measurement.md))
holds here: the module only *reports*; it never adds cognition.

Because SMN **is** a network, the default representation is a graph/topology and
world geometry is reported in **ordinal / relational** units — never metric
coordinates. And because the bench is a complex system, the emergent-structure
diagnostics run on **every** record whether or not the experiment asked, so that if
organization emerges we notice it rather than miss it.

## The contract: a `RunRecord`

Fill a `RunRecord` and call `render(record, spec)`. The only thing strictly
required is *something to recover a self-model from* — a movement trace. Everything
else is optional and unlocks another panel or diagnostic.

| field | meaning | unlocks |
|---|---|---|
| `omega` | `T×N` broadcast trace (segment co-motion) | self-model recovery (undirected) |
| `jv` | `T×N` efference; if given → **signed** coupling | branched-body edges (directed) |
| `coupling_matrix` | a precomputed `C` (skips the read-out) | recovery without raw traces |
| `positions` | node → `(x, y)` designed layout (default: a chain) | panel 1 (the designed body) |
| `true_edges` | designed topology (default: a chain) | edge-correctness colouring in panel 2 |
| `node_field` | node → world reading (agent-side) | panel 3 (world in the self-frame) |
| `world_signal` | `T×N` per-zone **world-caused** signal over time (ideally the DFN residual) | builds the **canvas** (the IN) on every modulating run; also supplies the proximal snapshot if `node_field` is absent |
| `source_node` | localized source (default: `argmax(node_field)`) | the ringed source on panel 3 |
| `metrics` | the experiment's declared order parameters | the order-parameter plot + record |
| `canvas_nodes` / `canvas_edges` / `canvas_core` | the IN's dependency digraph | emergent strata (+ region/class NMI with `canvas_classes`) |
| `meta` | free-form provenance | stored in the results JSON |

## What `render` does on every run

1. **Graph-first self-model recovery** — with `jv` (or a signed `coupling_matrix`)
   it recovers the coupling graph and reads each zone's own edge (works for
   *branched* bodies); with only `omega` it falls back to the **chain special
   case** (seriate into a linear order, join consecutive nodes). The self-model is
   a *graph*, not merely an ordering.
2. **Ordinal world localization** on the recovered graph — label-based and
   frame-relative (a reflection of the recovered order does not move the source).
3. **The SMN-native figures** — the [self/world card](diagram-grammar.md) (designed
   body → recovered self-graph with edge width = coupling and the branch point
   ringed → the world painted onto that graph), plus an order-parameter plot and,
   if a canvas is supplied, the emergent canvas.
4. **Always-on emergent diagnostics** on the recovered graph: degree sequence and
   `max_degree`, `is_chain` / `branch_node`, `algebraic_connectivity` (the Fiedler
   value), `N_D` (exact-controllability driver count — arm **symmetry** shows up
   here as `N_D > 1`), a provable `driver_nodes` set (for small bodies), and
   `n_regions` (one coupled blob = one undivided body); plus `canvas_strata` and
   `canvas_region_class_NMI` when a canvas is given.
5. **A machine-readable record** → `results/<prefix>_results.json` (metrics +
   diagnostics + recovered structure), and a consistent one-block console summary.

`render` returns all of the above as a dict, so a sweep can collect it too.

## The canvas — always built from modulation (not displacement)

SMN has **two** graphs, and they are not the same thing. The **self-model** is the
body's own connectivity graph (fixed topology, recovered above). The **world-model**
lives on the **canvas** — the IN's shared state-space, whose regions are *constructed,
not given*. The canvas is built whenever the agent **modulates** — any zone moving —
**not** only when the whole body displaces. A sessile hydra parked on a plant, with no
vision, still builds a world-model: prey drifts onto a tentacle, reafference tells it
*the flea pushed me* (not *I reached*), and the tentacle zones fire in sequence to
convey the prey to the mouth. Zero displacement, a complete world-model. Movement is
modulation in SMN; with no modulation the agent is cognitively dead — so the module
constructs the canvas on **every** modulating run.

Pass `world_signal` (a `T×N` per-zone world-caused stream — ideally the DFN residual)
and the module builds the canvas from it: the **regions** are zones that co-respond to
the world (one prey → one territory), and the **strata** are the recruitment order the
world imposes on the zones (the trajectory across the body), derived — never stipulated
— via `smn_lab.canvas.emergent_strata`. It emits a canvas figure (the emergent
dependency digraph) and records `canvas_live_regions` / `canvas_live_strata`. When
`world_signal` is present but `node_field` is not, the proximal snapshot for panel 3 is
its time-mean, so one input feeds both the self-graph card and the canvas.

```python
render(RunRecord(name="hydra", omega=tentacle_comotion, world_signal=world_caused_per_zone))
# -> [report:hydra] canvas (built from modulation): regions=1 · strata=6 (constructed even with no displacement)
```

## Minimal use

```python
from smn_lab.report import RunRecord, render

# ... run your experiment; collect the body's own movement trace OMEGA (T×N)
# and, if you sensed a world feature, its per-node reading ...

render(
    RunRecord(
        name="my_experiment",
        omega=OMEGA,                       # the trace the self-model is recovered from
        node_field={k: reading[k] for k in range(N)},   # optional: the world in the self-frame
        metrics={"order_acc": 0.99, "tracking": 1.00},  # your declared order parameters
    ),
    spec=dict(suptitle="My experiment — self/world card"),
)
```

That single call writes `figures/my_experiment_self_world_card.png`,
`figures/my_experiment_order_params.png`, and
`results/my_experiment_results.json`, and prints:

```
[report:my_experiment] self-model: chain · nodes=8 edges=7 · N_D=1 · regions=1 · alg.conn=0.152
[report:my_experiment] order params: order_acc=0.99  tracking=1
[report:my_experiment] figures: my_experiment_self_world_card.png, my_experiment_order_params.png · json: my_experiment_results.json
```

A branched body needs directed edges — pass `jv` (the joint efference) alongside
`omega`, or a signed `coupling_matrix`; the module then recovers the tree, rings
the hub, and reports `N_D` from the arm symmetry.

The `spec` dict is how an experiment says *exactly what to render*: `card`,
`op_plot`, `emergent_fig` (booleans), `suptitle`, `prefix`, `outdir`,
`results_dir`, `dpi`. Omitted keys take sensible defaults (card on; order-parameter
plot on when `metrics` is non-empty).

## Tested before use

`experiments/test_report.py` checks the module against **known** synthetic
structures — a chain, a branched **Y**, a localized source, and a sessile **hydra**
(a world signal with no displacement) — and two properties the bench cares about:
*relabeling invariance* of the topology diagnostics and *frame (reflection) relativity*
of the ordinal localization. The Y body returns `branch_node = hub`, the exact tree
edges, and `N_D = 2` from its arm symmetry; the hydra builds a canvas with the prey's
recruitment ladder as emergent strata, with the body never displacing. Run it:

```bash
cd experiments && MPLBACKEND=Agg ../.venv/bin/python test_report.py
```

## The one-page experiment figure (paper-ready)

`experiment_page(record, spec)` assembles a single **page-length** figure in the diagram
grammar, the same layout for every experiment, so a reader learns to read one and can read
them all:

```
[ title · one-line description · key metrics ]
[ 1 · Body plan (morphology) ]   [ 2 · World ]
[ 3 · Self-model (recovered) ]   [ 4 · World-model (canvas / IN snapshot) ]
[ 5 · Data (order parameters) ................ full width ]
```

The module draws the panels it can from the `RunRecord` — body plan (positions/edges),
self-model (recovered graph), world-model (the canvas from `world_signal`, else the world
on the self-graph from `node_field`). The two experiment-specific panels are passed as draw
callbacks in `spec`: `world_draw(ax)` paints the external world (objects/fields/prey), and
`plots_draw(fig, cell)` draws the result plots into the given GridSpec cell (it may subdivide
the cell for several sub-plots). Both are optional. `spec` also takes `description`,
`page_size` (default portrait A4-ish), `dpi`, and `prefix`. Saves `<prefix>_page.png` and
returns the path. A worked example is `experiments/experiment_page_demo.py` (the diploblast
sac). These pages are meant to drop straight into the paper as page-length figures.

## Adding it to a new experiment

Two lines: build a `RunRecord` from what your experiment already has (a movement
trace is enough), and `render` it at the end. Keep your experiment's own analysis
if you like — the module does not replace your science, it standardizes how the
result is generated and drawn. `experiments/worldmodel_from_selfmodel.py` is the
worked example: it keeps its three-condition test unchanged and additionally emits
its self/world card, diagnostics, and JSON through the one module.
