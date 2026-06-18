# Prediction 1 — haltability signatures (deceptive reach)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_pred1_haltability.png)

Pre-registered in the experiment file. SMN preprint, Predictions & Testable Claims
#1: *"Tasks requiring mid-course reversals (e.g., deceptive reach) should show
distinct stoppage–resume patterns and re-pairing among effectors."* This is the HAP
(Haltable Action Pattern) signature — extending [C1](c1_touch.md)'s halt-on-contact
to a halt triggered by an internal goal change.

## Setup
A single hinge limb (an opponent pair = two effectors) reaches its tip to a target.
**Mid-reach, while the limb is still moving, the target jumps** — for the headline
case it *reverses* sign (a deceptive reach). Two controllers solve the identical
task: **halt** (HAP — brakes to a stop, a short dwell, then resumes to the new
target) vs **smooth** (a continuous PD that just re-targets, no halt). Conditions:
controller × jump {reversal, same-direction adjustment} × 6 seeds.

## Declared adjustment
The first runs were confounded: the limb was so light/strong it reached the target
in ~30 ms, so it had always *arrived and settled* before any jump — low velocity
then meant "finished," not "halted." Fixed by using a slow, heavy limb with a low
actuator ceiling so the reach has a real ~0.5 s cruising phase, and the jump lands
while the limb is genuinely moving. A physical-regime fix, declared.

## Result — confirmed (signature), with an honest nuance

![Prediction 1 — at the reversal the halt controller's velocity dips to zero and dwells before resuming while the smooth controller corrects continuously; the opponent pair re-pairs; the dwell cleanly separates halt from smooth](../figures/sweep_pred1_haltability.png)

| controller | jump | velocity min (rad/s) | dwell (s) |
|---|---|---|---|
| **halt** | reversal | 0.00 | **0.17** |
| **halt** | same-direction | 0.00 | **0.17** |
| smooth | reversal | 0.01 | 0.05 |
| smooth | same-direction | **0.98** | **0.00** |

**The stoppage–resume signature is confirmed, and is diagnostic of haltability.**
The halt controller imposes a full stop (velocity → 0, dwell ~0.17 s) before
resuming, in *both* jump types, and the opponent pair **re-pairs** discretely (the
dominant puller flips through the dwell; panel B).

The clean discriminator is the **dwell**, and the *same-direction adjustment* shows
it most starkly: the smooth controller **never even slows** (velocity 0.98, dwell
0), while the halt controller stops. **Honest nuance:** on a *reversal*, any
controller must cross zero velocity (you cannot reverse without it) — so a momentary
stop is not unique to haltability there; what distinguishes the halt is that it
*dwells* at zero (0.17 s vs 0.05 s). So velocity-passes-through-zero is not the
signature; the **dwell** is.

## Functional note (exploratory)
The halt is **not** a speed advantage — it reacquires the new target *later* than
the smooth controller by roughly the dwell duration (it pays for the stop), and
overshoot is essentially identical. So haltability here is a **diagnostic kinematic
signature**, not a performance gain — consistent with the preprint, which predicts
the *signature*, not superiority.

## Verdict
Prediction #1 **confirmed**: the haltable architecture produces the predicted
distinct stoppage (a dwell) and discrete effector re-pairing, absent in a smooth
continuous controller — most cleanly on same-direction adjustments. As with the
other preprint-prediction reproductions, that a halt controller halts is partly by
construction; the informative content is that the signature is **categorically
distinct and cleanly quantifiable** (the dwell), exactly the diagnostic the preprint
proposes — while carrying no functional speed benefit.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_pred1_haltability.py
```
