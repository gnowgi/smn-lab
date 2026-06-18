# Prediction 3 — antagonistic benefits

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_pred3_antagonistic.png)

Pre-registered in the experiment file. This is the first of the SMN preprint's
six *Predictions and Testable Claims* (§Predictions) reproduced in the bench —
part of turning the preprint's qualitative claims into the quantitative ones it
explicitly calls for. Prediction #3: *"Perturbation studies should reveal faster
error correction when antagonistic tension is preserved vs pharmacologically
reduced."* It is also the mechanism Friston connected to (the equilibrium-point
hypothesis): co-contraction stiffens the joint, steepening the basin around the
equilibrium point.

## Declared mechanism + adjustment (read this first)
The bench's existing `OpponentBoard.cocontraction` adds tonic activation to two
pull-only **force** motors (gears +1/−1); these sum to **zero net torque and add no
stiffness**, so co-contraction as previously implemented is *inert for impedance*.
Testing #3 with it would give a false null — an artifact of the actuator model.

We therefore add a **muscle-impedance model**, faithful to the preprint
(`hm-new-plan`: the modulator's "efferent modulation signal adjusts the
**impedance** … of the antagonistic bundles") and to textbook biomechanics:

- co-contraction `coc` produces **intrinsic, zero-delay** stiffness & damping
  proportional to `coc` (active muscle is stiffer);
- neural feedback (`kp,kd`) acts with a realistic **delay** (a reflex loop);
- tonic co-contraction **costs energy** (both pullers active) with no net torque.

So the genuine, non-trivial claim is: *intrinsic (zero-delay) co-contraction
stiffness rejects a perturbation faster than delayed feedback can — at an energy
cost.* A tradeoff, not a free lunch.

## Setup
A single hinge limb (gravity off) holds a set-point; an external torque pulse
perturbs it. IV: co-contraction `coc ∈ {0, 0.15, 0.3, 0.6, 1.2}` (0 = the
preprint's "pharmacologically reduced" tension) × perturbation size {small, large}
× 6 seeds. Order parameters: peak deviation, integrated error (IAE), settling
time, energy (∫ activation² dt).

## Result — confirmed

![Prediction 3 — peak deviation and integrated error fall with co-contraction (more for the large perturbation), while energy rises; panel C shows the error–energy tradeoff with diminishing returns](../figures/sweep_pred3_antagonistic.png)

Large-perturbation summary (mean over seeds):

| coc | peak dev (rad) | integrated error | energy |
|---|---|---|---|
| 0.0 | 0.109 | 0.060 | 0.00 |
| 0.15 | 0.074 | 0.018 | 0.07 |
| 0.3 | 0.057 | 0.009 | 0.28 |
| 0.6 | 0.040 | 0.0045 | 1.09 |
| 1.2 | 0.025 | 0.0021 | 4.33 |

**The prediction holds.** Co-contraction reduces peak deviation **4.4×** (0.109 →
0.025) and integrated error **~28×**, i.e. markedly faster error correction — and
the benefit is **larger for the large perturbation** (panel A), exactly as
predicted. Energy rises from 0 to 4.33 (≈ quadratic in `coc`), so it is a genuine
**tradeoff** with **diminishing returns** — the error–energy curve (panel C) has a
knee near `coc ≈ 0.3–0.6`, beyond which more tension buys little.

## Honest framing
The *direction* (stiffness rejects perturbation faster than delayed feedback)
follows from the modeled muscle impedance plus the feedback delay — both textbook.
So this experiment is a **demonstration that the SMN antagonistic architecture,
given realistic muscle impedance, exhibits the preprint-predicted benefit** — not a
discovery that stiffness helps. The genuinely informative, falsifiable content is
**quantitative**: the size of the benefit, that it **scales with perturbation
magnitude**, and that it is **priced** (a steep, ~quadratic energy cost with a
clear knee) — which is why real bodies co-contract *selectively* rather than
always. A flat error-vs-`coc` curve would have falsified it.

This is the second pre-registered claim **confirmed** rather than corrected
(after the Q1b resolution-vs-density result).

## Run
```bash
cd experiments && ../.venv/bin/python sweep_pred3_antagonistic.py
```
