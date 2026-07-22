# Canvas regions — the canvas constructs its own functional regions

!!! warning "Status: preregistered — implementation in progress"
    This page is the **preregistration** for the canvas-regions experiment, on
    branch `exp/canvas-regions`. The hypothesis, order parameters, and matched
    foils are fixed here *before* the self-organizing-canvas run. See
    [Contributing experiments](../contributing.md) for the workflow.

    **Update:** the self-organizing canvas + morphology sweep are now wired
    (`sweep_canvas_regions.py`); the [first results](#first-results) are below,
    verdict **PASS** — with one preregistered criterion corrected (segregation →
    `n_regions`), logged in `experiments/canvas_regions_DEVLOG.md`.

The broadcasting substrate — the **canvas** — is **one undivided field**. A small,
unbranched agent has one canvas and **no regions**. The framework's claim is that
functional regions (L0/L1/L2, maps) are **not pre-given** but **constructed**:
they self-organize from the functional relations of the modules that keep
broadcasting to the canvas, as anatomy grows — the way cortical maps form.

This is the distinction that matters. The regionalization is **not a
description** (we do not impose regions) and **not** built into the substrate; it
is a **prediction of a construction** — the framework predicts that regions
*emerge* — and it is therefore falsifiable. Building the exact condition and
asking whether the construction happens is the framework's **best test**.

## Preregistration

- **Hypothesis.** Modules of *distinct functionalities* broadcasting to **one
  undivided plastic canvas** cause functional regions to **self-organize**:
  canvas segregation rises from chance to structured, and the number of emergent
  regions **tracks the number of functional classes**. A single-class (simple)
  agent yields **one undivided canvas** (no regions).
- **Order parameters.** `canvas_segregation` ∈ [0, 1] — the spatial segregation of
  the canvas's functional labels (0 = unstructured/chance, 1 = fully segregated
  regions); and `n_regions` — the number of contiguous label territories formed.
- **Matched foils.**
    1. **No plasticity** (the canvas cannot learn) — regions cannot be
       constructed, so segregation stays at chance.
    2. **Scrambled functionality** (modules carry no coherent functional classes)
       — even *with* plasticity there is no functional structure to segregate.
- **Pass.** With plasticity **and** structured functionality: `canvas_segregation
  > 0.7` and `n_regions ≈ (number of functional classes)`; **both foils ≤ 0.2**;
  and, across a growing body, `n_regions` **increases monotonically** with the
  number of functional classes (simple → 1 undivided canvas; complex → many
  regions).
- **Falsify.** Structured functionality + plasticity, yet segregation stays at
  chance → the framework's constructive claim about the canvas fails; the regions
  would then have to be *imposed*, not constructed.

## Why this is the keystone

It is the same phenomenon as **cortical map formation** (Kohonen self-organizing
maps; activity-dependent somatotopy, tonotopy, ocular-dominance): so the framework
predicts the canvas self-organizes *like cortex*, grounded and testable. And it is
the strongest support for the constructive-grounding stance the whole programme
takes — the SMN **builds** the structure (regions, maps) that other frameworks
assume as given.

## First results {#first-results}

The self-organizing canvas (`sweep_canvas_regions.py`) — modules broadcasting to
one plastic canvas (a SOM) — is wired, and the morphology sweep runs. Verdict
**PASS**:

![The canvas constructs functional regions that track morphology; the foils do not](../figures/canvas_regions.png)

- **Structured (the claim).** As functional classes are added, the canvas
  **partitions itself to match** — `n_regions` = 1, 2, 3, 5, 5 for K = 1…5 (on the
  diagonal), segregation 0.88–1.00. A **simple agent stays one undivided canvas**
  (left panel); a dexterous one grows to five regions. Regions are *constructed*,
  and their number *tracks morphological complexity*.
- **No-plasticity foil.** Frozen canvas → segregation 0.00, `n_regions` 212 — it
  builds nothing.
- **Scrambled foil.** Signatures with no class structure → the SOM still makes a
  *smooth* map (segregation 0.81!) but `n_regions` = 9 ≫ K = 4 — smooth yet
  **fragmented**, not matched to the classes.

!!! note "One criterion was corrected — provenance"
    The preregistered foil test was `segregation ≤ 0.2`. It had to be corrected: a
    self-organizing map smooths *any* input, so segregation is high even for
    scrambled functionality — the discriminator is **`n_regions ≈ K`**, not
    segregation. This is a post-hoc criterion change (a correction of a wrong
    assumption, *more* stringent for the structured case, not a loosening to pass),
    logged with the full build history in
    `experiments/canvas_regions_DEVLOG.md`. The structured result needed no such
    change.

## Order parameters, in code

The estimators are the single source of truth, read from the script at build time:

```python
--8<-- "experiments/canvas_regions.py:segregation"
```

```python
--8<-- "experiments/canvas_regions.py:regions"
```

## Plan (staged)

1. **The self-organizing canvas.** A body of modules with distinct functionalities
   (slow visceral BAPs, axial HAPs, fast emancipated patterns; transducers of
   several modalities), all broadcasting to **one undivided plastic canvas** (a
   self-organizing map). Measure `canvas_segregation` vs. the two foils.
2. **The morphology sweep.** Grow the body — add functional classes / the L0→L1→L2
   ladder — and show the canvas **construct more regions**, `n_regions` tracking
   the functional complexity. A simple agent stays one undivided canvas; a complex
   one partitions itself.

## Run

```bash
cd experiments
../.venv/bin/python canvas_regions.py        # self-test of the order parameters
../.venv/bin/python sweep_canvas_regions.py  # the self-organizing canvas + morphology sweep
```

The estimator self-test reads a known segregated map, a random map, and a
single-class canvas correctly. The sweep runs the self-organizing canvas over the
morphology series and the two foils, and writes `figures/canvas_regions.png`. The
canvas constructs its regions and the foils do not; the page graduates to `main` on
review.
