# Q1b — does resolution scale with CAZ density? (closing the Q1 thread)

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-mechanical-and-messaging) of this
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

!!! warning "Audited — the density reading did not survive (see the [audit](#audit-the-density-claim-does-not-separate-from-noise-averaging-2026-07-24) below)"
    The measurement below stands and its null is clean, but the audit shows the
    order parameter cannot tell **CAZ density** from **any** source of independent
    samples: sub-sampling zones on a *fixed* body reproduces the whole trend, and
    adding **raw transducers** to a fixed 3-zone body buys *more* resolution than
    adding zones does — contradicting the very clause ("not raw transducer count")
    this experiment was meant to support. The row is 🟠, with a pre-registered fix.

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
*(written before the audit; the first bullet is what the audit overturns)*

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


## Audit — the density claim does not separate from noise averaging (2026-07-24)

The scrutiny pass, and the one this page most needed: it is where the resolution
claim rests, and the result section above *already names the mechanism* — a
1/√N averaging law. That is exactly what makes the audit necessary, because the
claim being supported is the preprint's: resolution is **CAZ density × internal
capacity, *not* raw transducer count**. If the gain is generic sample-averaging it
is not about CAZs at all — the same failure mode that withdrew the
[S1 field-scale control](sweep_geometry_worldmodel_fieldscale.md) (a
decoder-dimensionality artifact dressed as a resolution principle). Three checks:

1. **Working null (no tide).** `EXAF_RATE = 0`: with no world change the ratio must
   be ~1 *and flat* in segment count.
2. **Density vs zones-averaged.** Hold the body **fixed at 9 segments** and
   aggregate the residual over only *k* = 3, 5, 7, 9 evenly spaced zones. If the
   ratio-vs-*k* curve reproduces the ratio-vs-`n_seg` curve, "resolution scales
   with CAZ density" is a property of the **read-out's aggregation**, not of the
   body.
3. **Not raw transducer count.** Hold the CAZ count **fixed at 3** and multiply the
   **raw transducers per sensor site** (`n_rep` = 1, 3, 9 independent reads,
   averaged). The preprint's clause says this should *not* buy resolution.

![Q1b audit — the null is flat at 1; and growing the body, sub-sampling zones on a
fixed body, and adding raw transducers to a fixed body all land on the same √N
curve](../figures/sweep_q1b_resolution_audit.png)

| route to more samples (6 seeds) | 3 | 5 | 7 | 9 | 27 | rise |
|---|---|---|---|---|---|---|
| grow the **body** (CAZ density), all zones | 14.0 | 16.0 | 21.4 | 22.6 | — | 1.62× |
| **fixed 9-segment body**, average *k* zones | 12.5 | 17.0 | 18.5 | 22.6 | — | 1.81× |
| **fixed 3-segment body**, ×1 / ×3 / ×9 raw transducers | 14.0 | — | — | 24.2 | 41.7 | 2.99× |
| no-tide null (modulated) | 1.06 | 0.89 | 1.10 | 0.96 | — | flat |

**The null passes; the density reading does not.** With no tide the ratio sits at
~1 at every body size and does not rise, so the measured trend *is* world-caused —
the data stand. But:

- **Growing the body adds nothing beyond averaging more zones.** Sub-sampling a
  *fixed* 9-segment body reproduces the entire trend (1.81×, if anything steeper
  than the 1.62× from actually growing the body), and *k*=3 zones of a 9-body
  (12.5) matches a real 3-segment body (14.0). Whatever the extra segments
  contribute mechanically, the order parameter does not see it.
- **Raw transducers buy *more* resolution than CAZs do.** Nine reads per site on a
  3-zone body reaches **41.7** — nearly double what a 9-zone body reaches. At
  **matched raw-transducer count** (18 reads either way) the two routes are
  indistinguishable: 3 CAZs × 3 transducers **24.2 ± 2.6** vs 9 CAZs × 1
  transducer **22.6 ± 3.4**. The clause "*not* raw transducer count" is
  contradicted on this observable.
- **Why.** Once modulation is working, the modulated self-test residual is *pure
  sensor noise*: it falls as exactly 1/√(reads) — 0.00088 → 0.00051 → 0.00030 for
  ×1 / ×3 / ×9, i.e. 1 : 1/√3 : 1/3 to two digits. The world term is untouched
  (0.01220 at every condition). So the order parameter is a **detection-SNR
  statistic**, and *any* independent samples improve it. It cannot distinguish a
  denser body from a noisier sensor sampled more often.

**What stands, and what does not.**

- **Stands:** the null; the measurement; the 1/√N mechanism (which this page
  already stated correctly); and — from [Q1](sweep_q1_modulation.md), separately
  audited — that **modulation is necessary**, since without it the self floor grows
  with body size and no amount of averaging helps.
- **Does not stand:** the reading that *resolution scales with CAZ density*, and
  the preprint clause *not raw transducer count*, **as tested by this order
  parameter**. Neither is refuted about the architecture; both are shown to be
  **untestable with a detection-SNR observable**. Row 🟡 → 🟠.

**Fix, pre-registered before running (Q1c — two-source discrimination).** The
resolution principle needs a **discrimination** observable, not a detection one.
Adding transducers at a fixed site can make one read cleaner but cannot make two
nearby world events *distinguishable*; that requires spatially distinct modulated
zones. So: two sources changing simultaneously at different body locations,
separation `d` swept; order parameter = whether the read-out resolves **two** peaks
and localizes both (per-zone deviation profile, as in
[W3](reafference_cut_self_graph.md)). *Hypothesis:* modulated discrimination
improves with CAZ density and fails once zone spacing exceeds `d`; adding raw
transducers at fixed CAZ count does **not** improve it; the unmodulated foil fails
at all densities. *Falsifier:* raw transducers recover discrimination too — then
the CAZ-density clause is wrong on this bench, not just untested.

Reproduction:
[`audit_q1b_resolution.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/audit_q1b_resolution.py).
`run_one` gained optional `n_rep` and `k_zones`; defaults reproduce the committed
sweep exactly (the baseline row above is unchanged to two decimals).

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
