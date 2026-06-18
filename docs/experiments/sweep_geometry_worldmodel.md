# S1 — geometry → world model (flagship)

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

- **A real, body-relative world model exists — confirmed.** Decoding skill is ~0.4
  at every body size, far above the shuffle control (~0). The agent's internal
  state genuinely differentiates its position in the world; held-out and
  shuffle-controlled, this is not an artifact. This is an affirmative answer to
  *"can the agent construct a world model from embodied sensing?"*
- **It does NOT scale with segment count — the pre-registered prediction was
  wrong.** Skill is flat across `n_seg` (within seed noise), even though larger
  bodies have **more** sensors **and** explored **more** area (panel B). We update
  our understanding: *more body does not, by itself, mean more world.*

## Interpretation — and a correction

We pre-registered that the world model would scale with the body's sensory
geometry. It did not. Honestly, this **corrects a naive expectation of our own**:
adding transducers (segments) alone did not enrich the world model.

Notably, this null is *consistent with the SMN resolution principle* — that
resolution is CAZ density × internal capacity, **not** raw transducer count, so
ungated extra sensors should not add resolution. The geometry experiment therefore
does not settle the world-model question by itself; it **redirects** it to the
real test: does *modulation* add what geometry alone does not? That is
[Q1](../test-plan.md#q1-world-model-from-sensation-modulation), which requires a
sensory-modulation mechanism the bench does not yet have (declared, deferred).

We resist the temptation to read the resolution-principle consistency as a win:
this experiment shows a world model exists and that segment count alone does not
scale it. Whether modulation does is still untested.

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
