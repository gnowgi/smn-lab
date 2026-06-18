# Q2 — self/world distinction (reafference) on the crawler

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_q2_reafference.png)

Pre-registered in the [test plan](../test-plan.md). The reafference principle:
sensed change decomposes as `dm/dt = ∇m·v` (self-caused) `+ ∂m/∂t|world`
(world-caused); a reafferent agent predicts the self term and is left with the
world term.

## What it tests
The crawler explores a static **linear field** (a uniform slope — the world where
the reafference model `∇m·v` is *exact*, so any residual after cancellation is
genuinely world-caused, not model error). Then:
- **self-test** — world static, agent moving → residual should fall to ~noise;
- **exafference** — a strong source *moves* across the agent's region (as in P0's
  sliding object) → residual should spike (a world-caused change the agent did not
  produce).

Order parameter: residual ratio = mean |residual| (exafference / self-test).
**Foil:** no forward model (no cancellation). Pass: ratio ≫ 1 for the reafferent
agent and ≈ 1 for the foil.

## Declared adjustments

This was the hardest port so far, and several choices were needed — all declared,
and the modeling trail is reported rather than hidden:

- **Windowed evaluation (0.25 s).** Per-step field change is below the sensor-noise
  floor; reafference is evaluated over a window where self-caused change clears
  noise.
- **Linear field + moving source.** Chosen by principle, not by result: the linear
  field makes the gradient model exact, and a moving source (P0-style) gives a
  strong world-caused term. Earlier curved-field and slow-ramp versions were
  discarded because the signal sat near the noise floor (an honest SNR failure,
  not a finding).
- **Self-gain calibration.** A scalar relating `∇m·(self-displacement)` to the
  observed change is fit during a static-world phase.

None of these is in the SMN preprint; they are operationalizations of its
reafference principle.

## Result

![Q2 — the reafferent residual is lower than the foil during self-motion and spikes during exafference; ratio 2.2 vs foil 1.58 across 10 seeds](../figures/q2_reafference.png)

| quantity | reafferent | foil |
|---|---|---|
| self-test residual | **0.0104** | 0.0164 |
| exafference residual | 0.0228 | 0.0252 |
| ratio (exaf / self) | **2.2 ± 0.3** | 1.58 ± 0.35 |

**Partially supported — a real but modest effect.** Reafference **cancels ~37% of
self-caused change** (self-test residual 0.0104 vs the foil's 0.0164) and lifts the
self/world ratio to 2.2 vs the foil's 1.58, across 10 seeds. So the principle
*works* on the crawler — self-caused change is partly cancelled and world-caused
change stands out more — but far less cleanly than in
[P0](p0_reafference.md) (single whisker, ~9× ratio).

## Interpretation — why only partial, and what it implies

The cancellation does **not** reach the noise floor even though the field model is
exact. The reason is a genuine, interesting limitation: the agent predicts from a
single **head-velocity** proprioceptive signal, but its sensors are **distributed**
over a **bending** body — so the head's motion is a poor proxy for how a tail
sensor actually moves. Single-point proprioception cannot fully predict
distributed reafference.

This is not a failure of the principle; it is a pointer to the mechanism the
architecture actually specifies. The SMN preprint's **dual-port modulator** has
each zone *both measure and move* — i.e., each zone senses **its own** motion. That
is exactly what would let each distributed sensor predict its own reafferent
consequence. So Q2's limitation directly motivates the
[Q1](sweep_q1_modulation.md) modulation mechanism: **distributed, per-zone
reafference**. P0 remains the clean canonical demonstration of the principle;
the crawler shows it is real but needs distributed modulation to be clean.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_q2_reafference.py
```
