# Integrator & snapshot — the beam holds the canvas

!!! warning "Status: preregistered — implementation in progress"
    This page is the **preregistration** for the integrator–snapshot experiment,
    on branch `exp/integrator-snapshot`. The hypotheses, order parameters, and
    matched foils are fixed here *before* the configuration-lattice sweep is run.
    See [Contributing experiments](../contributing.md) for the workflow.

Phase I's resolution principle is *spatial*: resolution scales with CAZ density ×
internal capacity, not raw transducer count ([Q1b](sweep_q1b_resolution.md),
[exponent](sweep_resolution_exponents.md)). This experiment adds the *temporal*
and *capacity* axes — and it does so by taking the **broadcasting beam** (the
integrating network; the nervous system, in the SMN reading) as an object of
study in its own right.

The claim in one line: **the beam is a fast, two-timescale integrator that
*holds* a low-dimensional snapshot of a body whose motor zones can only stroke it
slowly and serially — and the working-memory capacity of that snapshot is a
function of morphology, not a universal number.**

## The architecture under test

- **Motor CAZ — the strokes.** Peripheral opponent zones perturb the network.
  They are *slow* (a structural ceiling on how fast an appendage can be used) and
  *serial* — attention writes one coordinated stroke at a time.
- **The beam — the canvas.** An integrating network coupled by a concrete
  broadcast operator $\Pi$ (linear diffusive coupling, the simplest realization
  that can yield a stable consensus). It carries **two timescales**: a *fast
  refresh* (it re-reads the whole body — gamma-like) and a *slow hold* (the
  snapshot persists — theta-like).
- **The snapshot.** The low-dimensional manifold the beam settles onto and holds.
  It is maintained by the **beam**, not by the CAZ: a stroke is a transient
  perturbation; the held configuration is the representation-substrate — the
  *plot, not the point*.
- **Layers.** A coarse-graining hierarchy, e.g. `[36, 9, 3]` (or `[27, 9, 3, 1]`)
  — each level pools the one below. The lattice **is** the experimental variable
  ([Phase II](../phase2.md): morphology sets what the mechanism can construct);
  showing the manifold survives up the layers is also the *renormalization*
  result.

## Preregistration

Three order parameters, each with a matched foil. **None is a target number** —
each is a quantity read off the configuration.

### A — the snapshot is a held low-dimensional manifold

- **Hypothesis.** The beam's state settles onto a low-dimensional manifold and
  *holds* it after the driving stroke is removed; an elastic substrate is what
  lets the held continuum exist.
- **Order parameter.** The effective dimensionality (participation ratio) of the
  top-layer trajectory, plus the along-manifold drift rate after release.
- **Matched foils.** *Rigid* substrate ($k\to\infty$: the held continuum
  collapses, cf. the [self-model foil](self_model_topology.md)); *decoupled*
  ($\Pi$ off / closure broken: no consensus).
- **Pass.** PR $\ll D$ under coupling and small drift after release; foils give
  PR $\approx D$ (scatter) or no held state.
- **Falsify.** No low-dimensional held manifold under any admissible $\Pi$ → the
  beam does not integrate into a snapshot substrate.

### B — the canvas out-refreshes the stroke (a Nyquist condition)

- **Hypothesis.** Faithful intrinsic image formation *requires* the beam refresh
  to exceed the fastest stroke; below that the held snapshot aliases and the
  agent mis-reads its own activity.
- **Order parameter.** Snapshot fidelity (stroke ↔ held-snapshot correlation) as
  a function of stroke frequency; the **aliasing threshold** — the stroke
  frequency at which fidelity falls below criterion, predicted $\approx$ beam
  refresh$/2$.
- **Matched foil.** The beam slowed below the stroke rate (refresh $<$ stroke).
- **Pass.** Fidelity high while stroke $<$ refresh$/2$ and collapses past it; the
  threshold tracks refresh$/2$ across configs.
- **Falsify.** Fidelity independent of the refresh-to-stroke ratio → no temporal
  resolution constraint; the "canvas higher-resolution than stroke" claim fails.

### C — working-memory capacity is a function of morphology

This is the headline, and it is **explicitly not tuned to 7.** Seven may be the
*human body's* point on the curve; another configuration may sit at 70 (and, if
so, greater capacity is a candidate advantage — see the secondary hypothesis).
The result is the **mapping** capacity(morphology) and its *shape*, not any
single value.

- **Hypothesis.** The snapshot holds a bounded number of serially-loaded items,
  and that bound is set by morphology. Two mechanisms are run as *distinct points
  in the configuration space* — not rival guesses to be adjudicated by fit:
    - **A · theta/gamma slots** (beam locus): capacity $=$ hold-window $\div$
      refresh-slot (theta/gamma ratio).
    - **B · serial-stroke decay** (motor locus): capacity $=$ decay-time $\times$
      stroke-rate.
- **Order parameter.** Capacity $=$ the largest serial load retrieved above
  criterion; and, across the lattice, the **functional law** capacity(config).
- **Discriminating design (preregistered).** Each mechanism predicts capacity to
  depend on a *different* knob, so we perturb each and check which moves:

    | manipulation | A (theta/gamma) predicts | B (serial-decay) predicts |
    |---|---|---|
    | change beam bands (refresh, hold) | capacity shifts | ≈ unchanged |
    | change motor rate / decay | ≈ unchanged | capacity shifts |

- **Matched foils.** Decoupled beam (capacity $\to 1$); below-Nyquist beam
  (capacity degraded via aliasing — links B ↔ C).
- **Pass.** Capacity varies **lawfully and monotonically** with the predicted
  knob, in the predicted functional form; the two mechanisms separate by locus.
- **Falsify.** Capacity is **flat across the whole lattice** (morphology does not
  set capacity — the SMN thesis fails here); *or* it responds to neither knob (no
  mechanism); *or* every configuration lands at the same number regardless of
  morphology (an over-flexible free knob — the unfalsifiability we are guarding
  against).

!!! note "Report the failures"
    The rigor is in publishing the *whole* map — including configurations that
    give capacity 1, unbounded, or unstable — not the one config that lands near
    a familiar number. A curve with a predicted slope and named breakpoints is
    the result; a single lucky value is not.

## Secondary — does more capacity buy performance?

A further, separable hypothesis: greater working memory performs *more
efficiently*. Operationalized as a delayed-response / multi-site task whose
demand exceeds one item; measure performance (success, latency, or energy per
success) against capacity across the lattice. Prediction: performance rises with
capacity up to task demand, then saturates. Flagged as a **planned extension**,
not part of the core three.

## Order parameters, in code

The estimators are the single source of truth, read from the script at build
time:

```python
--8<-- "experiments/integrator_snapshot.py:dimensionality"
```

```python
--8<-- "experiments/integrator_snapshot.py:nyquist"
```

```python
--8<-- "experiments/integrator_snapshot.py:capacity"
```

The two preregistered capacity **laws** (mechanism A vs B) — each responds to a
different morphological knob:

```python
--8<-- "experiments/integrator_snapshot.py:laws"
```

## Plan (staged)

1. **Phase A — reduced dynamical network** (this branch, first): the layered
   opponent hierarchy with a concrete diffusive $\Pi$, no MuJoCo. Delivers all
   three order parameters and the capacity map fast and analyzably. This is where
   the "closure $\neq$ stability; show the beam *integrates*" and the
   renormalization-across-nested-scales points are settled.
2. **Phase B — embodied instance**: a smaller layered body in MuJoCo, so the
   strokes are real opponent-pair perturbations and the grounding is physical.

## Run

```bash
cd experiments && ../.venv/bin/python integrator_snapshot.py
```

Running it now executes a synthetic **self-test** of the three estimators (a
known dimensionality, aliasing threshold, and capacity recovered) — not yet a
bench measurement. Wiring the layered-network model and the lattice sweep is the
next step; when the map passes, this page graduates to `main` with its result and
plots.
