# S1 — geometry → world model (flagship)

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_geometry_worldmodel.png)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_geometry_worldmodel.png)

Pre-registered in the [test plan](../test-plan.md). The question: with the world
held fixed, does the world an agent can *differentiate* scale with its body's
sensory geometry?

## What it tests
A fixed three-source scalar field is held constant; only the body's **segment
count** varies (3, 5, 7, 9). As the crawler explores, we log its internal sensory
state (per-segment bilateral field readings) and its true position. A **model-free
kNN decoder**, trained on the first 60% of the trajectory and tested on the
held-out 40%, asks whether the agent's position can be read out of its internal
state. The order parameter is **decoding skill** = `1 − MAE_decoder / MAE_naive`
(0 = no better than guessing the mean position; 1 = perfect).

**Integrity control.** A **shuffle control** decodes from state↔position pairs that
have been shuffled; it must sit at skill ≈ 0. Held-out testing plus the shuffle
control mean the result cannot be tuned into existence.

## Declared adjustments

The first run was **confounded and is not reported as a result**: the larger
bodies were numerically unstable (the exploration bias, applied uniformly to every
joint, over-drove them) and barely explored, so their decoding was meaningless.
That is a simulation artifact, not a finding. The following adjustments were made
— each declared, none touching the skill metric or steering toward an outcome:

1. **Stability + exploration** — the exploration bias now steers the **anterior
   joint only** (head steering), not every joint uniformly. Larger bodies are now
   stable (zero solver warnings) and, in fact, explore **more** area than small
   ones (panel B), removing the exploration confound.
2. **Decoder data** — a longer run (90 s) logged ~1800 samples per run, enough for
   kNN at up to 18 state dimensions, so the higher-dimensional state of larger
   bodies is not penalized by sparse sampling.

None of these is specified in the SMN preprint; they are simulation-hygiene
choices for a fair test, recorded here.

## Result

![S1 — held-out world-model skill is well above the shuffle control at every body size, but does not rise with segment count; larger bodies explore more area](../figures/sweep_geometry_worldmodel.png)

| n_seg | skill (mean ± sd) | shuffle |
|---|---|---|
| 3 | 0.39 ± 0.24 | +0.05 |
| 5 | 0.43 ± 0.31 | +0.01 |
| 7 | 0.36 ± 0.42 | +0.03 |
| 9 | 0.49 ± 0.28 | +0.05 |

**Two findings, reported against the pre-registration:**

- **World-information is decodable in the self-frame — confirmed.** A held-out kNN
  decoder recovers position from the agent's field readings at skill ~0.4 at every
  body size, far above the shuffle control (~0). **What this shows and does not
  show:** the agent's sensory state carries enough information to *locate* it in the
  world (decodability); it is **not** yet a persistent, composable world-*model*.
  Information present in a signal is not the agent holding a model of it — the
  representational, map-like construct is deferred to Phase-II / M2. We keep to the
  weaker, warranted claim (the decoding-vs-representation distinction).
- **It does NOT scale with segment count — the pre-committed prediction was wrong.**
  Skill is flat across `n_seg` (within seed noise), even though larger bodies have
  more sensors and explored more area (panel B). *More body does not, by itself, mean
  more decodable world.*

## Interpretation — and a correction

We pre-committed that world-information would scale with the body's sensory
geometry. It did not — correcting a naive expectation of our own. But the null has
**two candidate explanations, and we have not yet separated them**:

1. **The SMN resolution principle** — resolution is CAZ density × internal capacity,
   **not** raw transducer count, so ungated extra sensors should not add resolution.
2. **A mundane field-geometry confound** — the differentiation field's spatial scale
   (`sigma ~ 0.8-0.9 m`) is far larger than the body (~0.2 m), so every segment reads
   a nearly identical value and extra segments add almost no *independent*
   information, whatever the theory says.

Both make the *same* flat prediction here, so this experiment does not distinguish
them. The clean test is a **body-scale field** (`sigma ~ body length`), where
segments genuinely see different values: if skill still does not rise with `n_seg`,
(1) is supported; if it does, the earlier null was the (2) artifact.

!!! danger "That control turned out to be confounded — we do NOT read this null as evidence for (1)"
    The [field-scale control](sweep_geometry_worldmodel_fieldscale.md) was run and, on
    a later review, **withdrawn**. Its order parameter — the slope of *kNN* decoding
    skill vs `n_seg` — is confounded three ways: (i) kNN degrades with state dimension,
    so it manufactures a negative slope even for a field with **no** independent
    per-segment information; (ii) the "body-scale" field kept the broad sources, which
    dominate and mask the body-scale signal — a properly body-scale field makes a
    *dimension-robust* decoder's slope go **positive** (more body → more decodable);
    (iii) the skill metric is trajectory-noisy (the curves are non-monotone with wide
    variance). So the control does **not** separate (1) from (2). **This S1 null is
    therefore consistent with either explanation, and must not be cited as evidence
    for the resolution principle.** The resolution claim is carried instead by the
    *modulation* experiments ([Q1](sweep_q1_modulation.md), [Q1b](sweep_q1b_resolution.md)),
    where CAZ density is varied with modulation on vs off.

The resolution question is separately pursued through *modulation* — does modulation
add what geometry alone does not? That is [Q1](sweep_q1_modulation.md) (per-zone
modulation) and [Q1b](sweep_q1b_resolution.md): resolution scales with CAZ density,
but only *with* modulation.

**Caveat.** Eight seeds with wide spread: "flat" means no trend detectable at this
power, not a proven exact-zero. A larger ensemble could reveal a weak effect.


## What's measured, computed, and plotted
**Raw data (per run = one segment count x one seed; ~1800 logged times):** the
internal sensory state `S` (the `2*n_seg` vector of per-segment bilateral field
readings) and the true head position `P = (x, y)`.

**Computed (the order parameter — held-out decoding skill):**
- split the run by time into train (first 60%) and test (last 40%); standardize each state channel;
- for each test state, find its `k = 8` nearest train states (Euclidean distance) and predict the mean of their positions;
- `MAE = mean Euclidean error` of those predictions; `MAE_naive = error of always predicting the train-mean position`;
- `skill = 1 - MAE / MAE_naive` (0 = no better than guessing the mean; 1 = perfect);
- **shuffle control** = the same with train state↔position pairs shuffled (must give skill ≈ 0);
- `coverage` = explored bounding-box area.

**Plotted:** **A** skill vs segment count (mean ± 95% CI) with the shuffle control; **B** coverage vs segment count.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_geometry_worldmodel.py
```
Outputs `data/s1_geometry/` (+ curated `samples/s1_geometry/summary.csv`) and
`figures/sweep_geometry_worldmodel.png`.
