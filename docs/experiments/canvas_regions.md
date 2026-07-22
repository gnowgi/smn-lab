# Canvas regions — the canvas constructs its own structure

!!! success "Status: wired — verdict PASS (emergent dependency digraph)"
    This experiment is on branch `exp/canvas-regions`. The hypothesis, order
    parameters, and matched foils were fixed *before* the run (preregistration
    below). The construction model was **reworked** from a self-organizing map to the
    **emergent dependency digraph** the diagram grammar draws, so the bench and the
    diagram are one object; the [results](#results) are below, verdict **PASS**. The
    full build history — including the rework rationale — is in
    `experiments/canvas_regions_DEVLOG.md`.

The broadcasting substrate — the **canvas** — is **one undivided field**. A small,
unbranched agent has one canvas and **no regions**. The framework's claim is that
functional structure (regions, the L0/L1/L2 layers, maps) is **not pre-given** but
**constructed**: it self-organizes from the functional relations of the modules
that keep broadcasting to the canvas, as anatomy grows.

This is the distinction that matters. The structure is **not a description** (we do
not impose regions) and **not** built into the substrate; it is a **prediction of a
construction** — the framework predicts that structure *emerges* — and it is
therefore falsifiable. Building the exact condition and asking whether the
construction happens is the framework's **best test**.

## The canvas as an emergent dependency digraph

We model the canvas as the very object the [diagram grammar](../diagram-grammar.md)
draws (`render_emergent_canvas`): an **emergent dependency digraph**. Modules
broadcast to one undivided canvas; the canvas keeps *no map* — it accumulates
**couplings** from broadcast co-activity:

- modules that fire **together** (same tick) build a **symmetric** coupling →
  **regions** (communities of mutually-coupled modules — the functional
  territories; the *breadth* of the canvas);
- modules that fire **in order** (one leads, the next lags) build a **directed**
  coupling → **layers** (the dependency ladder; strata = the longest dependency
  path, *derived not stipulated* — the *depth* of the canvas).

Both come from the **same** broadcast stream (only co-active / modulated data shapes
the canvas). A smoothing map on a stipulated 2-D sheet can only ever see breadth; a
dependency digraph sees **both**, and they come apart once a body branches.

## Preregistration

- **Hypothesis.** Modules of *distinct functionalities* broadcasting to **one
  undivided canvas** cause functional structure to **self-organize**: emergent
  communities **recover the functional classes**, the number of **regions** tracks
  morphological **breadth**, and the number of **layers** (dependency strata) tracks
  morphological **depth**. A single-class (simple) agent yields **one undivided
  canvas** (one region, one stratum).
- **Order parameters** (in `canvas_regions.py`, the single source of truth):
    - `community_class_match` ∈ [0, 1] — **primary**: NMI of emergent communities
      against the functional classes (1 = communities *are* the functional
      territories; ~0 = independent of class);
    - `n_regions` — the number of emergent communities (breadth);
    - `emergent_strata` — the number of dependency layers (depth), the *same*
      longest-path rule the grammar's emergent canvas uses.
- **Matched foils.**
    1. **No plasticity** (couplings frozen at random) — nothing is constructed.
    2. **Scrambled functionality** (co-activity decoupled from class) — even *with*
       plasticity the canvas builds a graph, but its communities do **not** match the
       functional classes.
- **Pass.** With plasticity **and** structured functionality: `community_class_match
  > 0.7`; simple agent = **one** region and **one** stratum; `n_regions` and
  `emergent_strata` **increase monotonically** as the body grows; **depth < breadth
  once the body branches** (left/right appendages share a stratum); and **both foils
  fail the primary order parameter** (`community_class_match` low).
- **Falsify.** Structured functionality + plasticity, yet communities do not match
  the classes (match stays low) → the framework's constructive claim about the
  canvas fails; the regions would then have to be *imposed*, not constructed.

## Why this is the keystone

It is the **constructive-grounding** claim in miniature: the SMN **builds** the
structure — regions *and* the dependency ladder — that other frameworks assume as
given. Modelling it as the emergent digraph (not a stipulated sheet) matters twice:
it matches the diagram grammar exactly, and its primary order parameter —
"do the emergent communities *match the functional classes*" — cannot be faked by
generic self-organization (a class-free graph scores 0), so the test is
discriminating **by construction**.

## Results {#results}

The construction model (`sweep_canvas_regions.py`) — modules broadcasting to one
undivided canvas, couplings accumulated from co-activity, structure read off the
emergent digraph — runs the morphology sweep and the two foils. Verdict **PASS**
(stable across seeds):

![The canvas constructs an emergent dependency digraph — regions and layers both track morphology; the foils do not](../figures/canvas_regions.png)

- **Structured (the claim).** Communities **recover the functional classes**
  (`community_class_match` = 1.00). As the body grows, `n_regions` = 1, 2, 3, 4, 5
  (breadth) and `emergent_strata` = 1, 2, 3, 3, 4 (depth). A **simple agent stays
  one undivided canvas** (one region, one stratum). Regions and layers **diverge**
  exactly where the body branches — the LEFT and RIGHT appendages join at **one**
  stratum (breadth without depth) — then the dexterous layer adds depth.
- **No-plasticity foil.** Frozen canvas → `community_class_match` 0.00 — it builds
  nothing.
- **Scrambled foil.** Co-activity decoupled from class → the canvas still forms
  communities, but `community_class_match` = 0.25 — the communities do **not** match
  the functional classes.

!!! note "Reworked from a self-organizing map — and why that gained rigour"
    An earlier version modelled the canvas as a self-organizing map on a stipulated
    2-D sheet. It passed, but it needed a **post-hoc criterion correction**
    (segregation → `n_regions`), because a SOM smooths *any* input, so its natural
    order parameter was confounded and could not fail the scrambled foil. The
    emergent-digraph rework matches the diagram grammar **and** dissolves that
    confound: the primary order parameter (`community_class_match`) cannot be faked
    by generic self-organization, so no post-hoc fix is needed. The full account is
    in `experiments/canvas_regions_DEVLOG.md`.

## Order parameters, in code

The estimators are the single source of truth, read from the script at build time:

```python
--8<-- "experiments/canvas_regions.py:match"
```

```python
--8<-- "experiments/canvas_regions.py:communities"
```

```python
--8<-- "experiments/canvas_regions.py:strata"
```

## Run

```bash
cd experiments
../.venv/bin/python canvas_regions.py        # self-test of the order parameters
../.venv/bin/python sweep_canvas_regions.py  # the construction model + morphology sweep
```

The estimator self-test reads a known dependency chain, a branch, a single blob, and
a class-structured vs class-free graph correctly. The sweep runs the broadcast-
coupling construction over the morphology series and the two foils, and writes
`figures/canvas_regions.png`. The canvas constructs its regions **and** its layers
and the foils do not; the page graduates to `main` on review.
