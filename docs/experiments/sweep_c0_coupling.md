# S0 — coupling sweep (locomotion is a network effect)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_sweep_c0_coupling.png)

## What it shows
The first [harness](../datasets.md) demonstration, and a clean network-effect
result with the methodology the [formal review](../reproducibility.md) asked for:
**multiple seeds, a matched foil, and confidence intervals.**

The three-block crawler's locomotion is a traveling wave on the messaging beam.
We sweep the beam's **coupling strength** and, for each value, run many seeds whose
**initial joint phases are randomized** — so the coupling has to re-establish a
coherent wave from a random start.

- **coupling = 0** is the **matched foil**: identical body, actuators, and drag —
  only the inter-zone coupling removed. The joints keep their random starting
  offset, so net displacement is a lottery.
- **coupling > 0** pulls the joints to the productive phase lag regardless of
  where they started, so every seed locks into the same forward wave.

The claim under test, in its smallest form: **locomotion lives in the coupling,
not in the parts.**

## Setup
- **Body / medium** — the [C0](c0_crawler.md) three-block crawler in the
  overdamped anisotropic medium.
- **IV** — `MessagingBeam(coupling=…)` swept over `[0, 0.25, 0.5, 1, 2, 4, 8]`.
- **Foil** — `coupling = 0` with randomized initial joint phases.
- **Ensemble** — 10 seeds per coupling (70 runs); no chemotactic bias (pure
  locomotion).
- **Order parameter** — net displacement; we also report across-seed spread and
  phase-lag coherence.


## What's measured, computed, and plotted
**Raw data (per run = one coupling value x one seed; 70 runs):** head `(x, y)` over
time; `dphi` = the phase difference between the two joint oscillators.

**Computed (the math):**
- `net_disp` per run (as C0).
- `phase_coherence = |mean over time of exp(i*dphi)|` — 1 if the joints hold a fixed phase relation, → 0 if they drift apart.
- across seeds, per coupling value: mean net_disp, its **95% CI** (= `1.96 x sem`), and its standard deviation.

**Plotted:** **A** mean net_disp vs coupling with the 95% CI band, the foil (coupling = 0) circled; **B** the across-seed standard deviation of net_disp vs coupling (the variance collapse).

## Run
```bash
cd experiments && ../.venv/bin/python sweep_c0_coupling.py
```

## Outputs
- `data/s0_coupling/{summary.csv, timeseries.parquet, manifest.json}` (full,
  gitignored); curated `samples/s0_coupling/summary.csv` (committed).
- `figures/sweep_c0_coupling.png`.

## Result & interpretation

![Coupling sweep — net displacement rises and seed-to-seed variance collapses as the messaging-beam coupling increases](../figures/sweep_c0_coupling.png)

*A: mean net displacement vs coupling, with the 95% CI over seeds; the foil
(coupling = 0) is circled. B: the across-seed standard deviation of net
displacement.*

The foil (coupling = 0) travels **0.56 ± 0.28 m** — a wide spread, because each
random start yields a different fixed phase offset and so a different gait. Adding
coupling raises the mean to **0.75 ± 0.002 m** and **collapses the seed-to-seed
spread by ~100×**: every random start now locks to the same productive traveling
wave. Locomotion is reproducible only when the zones are coupled — a network
effect, demonstrated with a matched foil and a seed ensemble rather than a single
illustrative run.

This is the template for the C-series: an explicit order parameter, a matched
non-modulatory foil, replicated seeds, and exported data for re-analysis.
