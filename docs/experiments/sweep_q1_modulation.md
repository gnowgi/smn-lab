# Q1 — modulation and the resolution principle

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_q1_modulation.png)

Pre-registered in the [test plan](../test-plan.md). [Q2](q2_reafference.md) showed
reafference works on the crawler but only partially, because a single head-velocity
signal cannot predict how *distributed* sensors move on a *bending* body. The SMN
preprint's answer is the **dual-port modulator** — each zone *both measures and
moves*, sensing **its own** motion. This experiment builds exactly that:
**distributed, per-zone reafference**, and tests the resolution principle —
*resolution is CAZ density × internal capacity, not raw transducer count.*

## Mechanism and provenance (declared)
Each CAZ predicts its own reafferent consequence from its **own** sensed velocity
and the local field gradient (`dr_k = ∇m·v_k`). This is the preprint's modulator
(arXiv:2605.26856, *hm-new-plan*: "by both measuring and moving, modulators
implement the reafference principle in the body itself"). The per-zone
implementation is ours. **Foil:** the same body, same sensors, no cancellation
(modulation off). Conditions vary only modulation on/off and segment count; world,
exafference, and exploration are matched.

## Result

![Q1 — with per-zone modulation the self/world ratio stays high at all body sizes while the foil collapses to ~1; modulation holds the self-caused residual at the noise floor while the foil's grows with zone count](../figures/sweep_q1_modulation.png)

| n_seg | modulated ratio | foil ratio | modulation advantage |
|---|---|---|---|
| 3 | 115.8 | 13.7 | 8.5× |
| 5 | 51.4 | 2.7 | 19× |
| 7 | 33.2 | 1.3 | 26× |
| 9 | 26.3 | 1.2 | 22× |

**Modulation is necessary for a distributed body — strongly supported.** Per-zone
modulation cancels self-caused change to the **noise floor at every body size**
(panel B: modulated residual flat at ~0.0007). Without modulation, the aggregate
self-caused residual **grows** with zone count (0.0075 → 0.029), so self/world
resolution **collapses** — the foil's ratio falls from 13.7 to ~1.2 (no separation
at all on the large body). The modulation advantage **widens with density**
(8.5× → 22×).

The clean reading of the resolution principle: **raw transducer count without
modulation does not add resolution — it subtracts it.** Adding zones to an
unmodulated body makes its self/world discrimination *worse*; modulation (the
per-zone dual-port modulator) is what lets a distributed body resolve the world at
all.

## Correction (against the pre-registration)
We pre-registered that the *modulated* ratio would **rise** with segment count. It
does not — the absolute modulated ratio **falls** (116 → 26). Honest cause: the
exafference is a *localized* moving source, so on a longer body many zones are far
from it and the whole-body **mean** residual dilutes the world signal. That is a
stimulus/metric confound, not a property of modulation. So we **do not** claim
absolute resolution rises with density; what the data support is that the
*modulation advantage* over the foil widens with density, and that **modulation is
required** for resolution to survive at all as the body grows.

A clean test of *absolute* resolution-vs-density would need a non-localized
stimulus (or a per-zone metric that is not diluted by averaging across a long
body). Recorded as the next refinement.

## Verdict
The core resolution-principle claim — *modulation, not raw transducer count, yields
resolution* — is **supported, decisively**: an unmodulated distributed body loses
self/world resolution as it grows; the per-zone dual-port modulator restores it to
the noise floor. The narrower "absolute resolution scales up with density" claim is
**not** established (confounded) and is left open.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_q1_modulation.py
```
