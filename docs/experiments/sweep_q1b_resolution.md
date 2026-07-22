# Q1b — does resolution scale with CAZ density? (closing the Q1 thread)

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_q1b_resolution.png)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_q1b_resolution.png)

Pre-registered in the experiment file. [Q1](sweep_q1_modulation.md) left one
question open: it showed the modulation *advantage* widens with density, but the
*absolute* modulated ratio **fell** with segment count — because the exafference
was a **localized** moving source, so on a longer body most zones sat far from it
and the whole-body mean diluted the world signal. We could not say whether
resolution scales *up* with density.

## The one change
A **distributed** world-caused change: a spatially uniform "tide" that rises
everywhere, so every zone sees it equally and the per-zone aggregate no longer
dilutes it. Everything else is the Q1 setup — per-zone dual-port modulation vs
foil, static linear field, noisy sensors, segment count swept.

## Pre-registered prediction
With a distributed signal and per-zone modulation, the world-detection ratio
should **rise** with CAZ density: each zone cancels its own self-motion, so
averaging N zones drives the self-noise floor down ~1/√N while the shared world
signal survives. The foil should **fall** (its uncancelled self-motion floor grows
with density). Falsifier: modulated ratio also flat/declining → resolution does not
scale with density even with modulation.

## Result — prediction confirmed

![Q1b — with a distributed world signal the modulated world-detection ratio rises with segment count (14 → 22.6) while the foil falls toward 1; the modulated self-noise floor stays near zero while the foil's grows fourfold](../figures/sweep_q1b_resolution.png)

| n_seg | modulated ratio | foil ratio |
|---|---|---|
| 3 | 14.0 ± 1.6 | 2.5 ± 0.4 |
| 5 | 16.0 ± 2.3 | 1.8 ± 0.3 |
| 7 | 21.4 ± 2.9 | 1.4 ± 0.1 |
| 9 | 22.6 ± 3.7 | 1.4 ± 0.2 |

**Resolution scales with CAZ density — but only with modulation.** Removing the
dilution confound flips the absolute trend: the modulated world-detection ratio now
**rises** with segment count (14 → 22.6), while the foil **falls** toward 1
(2.5 → 1.4). Panel B shows the mechanism directly: per-zone modulation holds the
self-noise floor near zero at every body size, while without modulation it **grows
fourfold** (0.0075 → 0.029) as zones multiply.

The magnitude is mechanistically consistent: 22.6/14 ≈ **1.6×** from n_seg 3 → 9,
close to the **√(9/3) ≈ 1.73×** expected if the gain comes from averaging
independent per-zone noise (∝ 1/√N). So this is not just a direction but a
quantitatively sensible one.

## What this closes, and what it does not

- **Closed:** the open Q1 question. With a non-diluting (distributed) stimulus,
  *resolution rises with CAZ density* — and *only when modulated*. Without
  modulation, adding zones lowers resolution (the foil's noise floor grows). This
  is the resolution principle in full: density helps, but only modulation lets the
  body cash it in.
- **Honest scope:** the effect is real but modest (~1.6× over a 3× density range,
  as the 1/√N mechanism predicts — not a dramatic threshold). And it is shown for
  *world-change detection*; the related claim for a *static* world model (the
  [flagship S1](sweep_geometry_worldmodel.md), which was flat in `n_seg`) is a
  different observable and remains as found — smooth static fields give redundant
  per-zone reads, so density does not help there.

This is also the first progression prediction to be **confirmed** rather than
corrected (after [S1](sweep_geometry_worldmodel.md), [Q1](sweep_q1_modulation.md),
and [Q2](q2_reafference.md) each corrected one) — a small reassurance that the
framework is being tested, not bent: predictions sometimes hold and sometimes do
not.


## What's measured, computed, and plotted
**Raw data & math:** identical to [Q1](sweep_q1_modulation.md) — per-zone
reafference with each zone cancelling its **own** sensed displacement; aggregate
residual = mean over zones; `ratio = mean|aggregate| in exafference / in self-test`.
The only change is the world-caused signal: a spatially **uniform "tide"** (a
distributed change every zone sees equally) instead of a localized source.

**Plotted:** **A** the world-detection ratio vs segment count, modulated vs foil (modulated rises, foil falls); **B** the self-test residual (noise floor) vs segment count.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_q1b_resolution.py
```
