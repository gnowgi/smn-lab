# Prediction 2 — zonal dissociations

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_pred2_zonal.png)

Pre-registered in the experiment file. SMN preprint, Predictions & Testable Claims
#2: *"The same abstract task should produce different performance across
materials/couplings (viscoelastic vs rigid tools) due to zone priors —
dissociations by substrate even with identical task-level specifications."* The
second preprint prediction reproduced in the bench.

## Setup
The same reach-and-hold task is performed through a **tool**: a motor-driven limb
carries a passive tool link whose joint has stiffness (elastic) + damping
(viscous) — the *material*. **Rigid** = stiff, lightly resonant (tip ≈ limb);
**viscoelastic** = compliant + lightly damped (a resonant 2-DOF load). The agent's
PD controller gains `(kp, kd)` are its **zone prior**. We sweep the gain grid on
both substrates (4 seeds); the dissociation is whether the *optimal* gain differs
by substrate and whether cross-applying one substrate's optimum to the other hurts.

The clean, falsifiable form is a **crossover**, not a difficulty main effect.

## Declared adjustment
The first run was a **setup bug, not a result**: the actuator ceiling was so low
(`CMAX=0.6`) that every gain saturated, so the gain — the independent variable —
had no effect, and the "viscoelastic" tool's resonance was far out of band. We
raised the ceiling so gains operate, and gave the tool real inertia so a compliant
joint yields an in-band resonance. Both are physical-regime fixes (chosen by
reasoning, not by hunting for a crossover), declared here.

## Result — partially confirmed, with an honest nuance

![Prediction 2 — task-error landscapes over gains differ by substrate (optimum moves); the rigid-tuned high-gain prior is catastrophic on the compliant substrate, but a conservative generic prior does about as well as the matched prior on both](../figures/sweep_pred2_zonal.png)

| | rigid substrate | viscoelastic substrate |
|---|---|---|
| optimal gain | kp 30, kd 1.0 | kp 15, kd 0.4 |
| best IAE | 0.018 | 0.028 |
| worst IAE (in grid) | 0.20 (11×) | **1.71 (60×)** |
| rigid-optimal prior applied here | 0.018 (matched) | **0.111 (4× worse)** |
| generic prior (kp 15, kd 0.4) | 0.020 | 0.028 |

**Confirmed — the substrate reshapes the task, strongly and asymmetrically.** The
optimal gain *moves* between substrates, and the same task yields very different
gain landscapes. The compliant substrate is **far less forgiving**: its best→worst
spread is 60× (vs 11× on rigid), and the aggressive prior that is *optimal* on the
rigid tool is **catastrophic** on the compliant one (0.111 vs 0.028 matched; the
worst aggressive corner reaches 1.71) — high gain excites the compliant resonance.
So "same task, very different performance by material" holds decisively.

**Not supported — the strong "needs substrate-specific priors" reading.** A single
**conservative generic** prior (kp 15, kd 0.4) does about as well as the
substrate-*matched* prior on **both** substrates (rigid 0.020 vs 0.018 matched;
viscoelastic 0.028 = matched). So in this task, pre-tuned per-substrate priors are
**not required**: priors matter mainly to *avoid* the catastrophic aggressive
regime on compliant substrates — which a cautious default also avoids.

## Verdict
Prediction #2 is **partially confirmed**. The dissociation in performance by
substrate is real and strong (and asymmetric: compliant materials severely punish
aggressive control). But the part attributing it to a *need* for substrate-specific
zone priors is **weak here** — a conservative generic controller captures most of
the performance, because the dissociation lives almost entirely in one
catastrophic corner rather than in a genuine two-way crossover of optima. We record
this as a qualification of the strong reading: substrate constrains *which control
is viable*, more than it *requires distinct priors* for this task. A task with a
true two-sided crossover (where each substrate punishes the other's optimum) would
test the stronger claim.


## What's measured, computed, and plotted
**Raw data (per run = kp x kd x substrate {rigid, viscoelastic} x seed):** time and
the tool-**tip** angle (`= limb-joint angle + tool-joint angle`) during a
reach-and-hold.

**Computed (the math):**
- `IAE = integral of |target - tip| dt` — integrated absolute tracking error (the task error); also overshoot and final error.
- per substrate: the mean IAE over seeds on each `(kp, kd)` gain → a 2-D landscape; its optimum = `argmin IAE`; the optima are compared across substrates (matched vs mismatched vs a generic compromise gain).

**Plotted:** **A, B** the IAE landscape over `(kp x kd)` for each substrate, optimum ★; **C** bars of matched / mismatched / generic IAE on each substrate.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_pred2_zonal.py
```
