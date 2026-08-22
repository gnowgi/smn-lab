# Q1 — modulation and the resolution principle

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-mechanical-and-messaging) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_q1_modulation.png)

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
and the local field gradient (`dr_k = ∇m·v_k`). This is the preprint's Sensation Modulator
(arXiv:2605.26856): by both measuring and moving through one substrate, modulators
implement the reafference principle in the body itself. The per-zone
implementation is ours. **Foil:** the same body, same sensors, no cancellation
(modulation off). Conditions vary only modulation on/off and segment count; world,
exafference, and exploration are matched.

## Formalism — per-zone (distributed) reafference

Q1 is the **distributed** form of the [reafference cut](q2_reafference.md): instead
of one head-velocity prediction, **each zone** cancels its **own** self-motion — the
dual-port modulator, each zone both sensing and moving:

\[
\text{basis}_k = \nabla m \cdot \Delta\mathrm{pos}_k,
\qquad
r^{\text{mod}}_k = \Delta r_k - s_k\,\text{basis}_k,
\qquad
r^{\text{foil}}_k = \Delta r_k.
\]

Each zone accumulates its **own** sensed displacement (dual-port):

```python
--8<-- "experiments/sweep_q1_modulation.py:dualport"
```

and cancels its own self-caused change; the foil does not:

```python
--8<-- "experiments/sweep_q1_modulation.py:modulate"
```

Because each zone cancels its *own* term, extra zones add resolution **only when
modulated** — the resolution principle: resolution scales with CAZ density × internal
capacity, not raw transducer count. The parameters varied are **segment count ×
mode** (modulated / foil).

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
The core claim — *modulation is what lets a distributed body resolve the world* —
is **supported**: an unmodulated distributed body loses self/world resolution as it
grows; the per-zone dual-port modulator holds it at the noise floor. The narrower
"absolute resolution scales up with density" claim is **not** established
(confounded) here and is taken up in [Q1b](sweep_q1b_resolution.md) — where the
[audit](sweep_q1b_resolution.md#audit-the-density-claim-does-not-separate-from-noise-averaging-2026-07-24)
finds it does not separate from noise averaging. *Nothing on this page depends on
that narrower claim.*

## Audit — null + a sharper foil for the dual-port claim (2026-07-24)

The scrutiny pass. Two questions a skeptic asks here.

**1. Is the separation world-caused?** Re-run with the moving source removed
(`EXAF_AMP = 0`), so the "exafference" window contains no world event. Both ratios
must collapse to ~1 at **every** body size.

**2. Is it the *dual-port* part that does the work?** The committed foil is *no
cancellation at all*, which confounds "cancels with the right zone's motion" with
"cancels at all". The preprint's claim is specifically that each zone senses **its
own** motion, so the audit adds two sharper foils that keep all the machinery and
re-calibrate their own per-zone gains, changing only *whose* motion each zone
cancels:

- **distant zone** — each zone cancels a zone half a body away (right magnitude,
  wrong identity);
- **head-only** — every zone cancels the head zone's displacement: exactly
  [Q2](q2_reafference.md)'s single-point proprioceptive model, run on this body.

![Q1 audit — with the wrong zone's motion the advantage largely disappears; in the
no-event null both ratios sit at 1 at every body size](../figures/sweep_q1_modulation_audit.png)

| world/self ratio (6 seeds) | n=3 | n=5 | n=7 | n=9 |
|---|---|---|---|---|
| **own motion (dual-port)** | **115.8** | **51.4** | **33.2** | **26.3** |
| distant zone (wrong identity) | 32.2 | 5.0 | 3.2 | 4.2 |
| head-only (Q2 single-point) | 17.6 | 3.9 | 2.1 | 2.1 |
| no cancellation (committed foil) | 13.7 | 2.7 | 1.3 | 1.2 |
| *no-event null, modulated* | *1.06* | *0.89* | *1.10* | *0.96* |
| *no-event null, foil* | *1.06* | *1.07* | *0.81* | *0.99* |

**Survives — and the sharper foils strengthen it.** With the source removed every
ratio collapses to ~1 at every body size, so the separation is world-caused. And
own-motion cancellation beats the *head-only* model by **6.6× – 15.9×** and the
*wrong-zone* model by **3.6× – 10.4×**, with the gap widening as the body grows.
That is the dual-port claim tested directly: it is not enough to subtract something
of the right size, or to subtract the head's motion — each zone has to cancel **its
own**, and this matters more the longer the body. It also re-derives
[Q2](q2_reafference.md)'s limitation from inside Q1: the head-only column *is* Q2's
forward model, and it degrades from 17.6 to 2.1 as sensors spread over a bending
body.

Two honest refinements the audit adds:

- **The core claim does not need the world event at all.** What actually carries it
  is the *self-test residual floor*: with modulation it stays flat
  (0.00088 → 0.00055 from n=3 to n=9), without it grows **3.8×**
  (0.0075 → 0.0289). Both numbers are identical in the null, so this is a
  world-independent property of the cancellation — the strongest form of the
  claim, and the one to state.
- **The foil's ratio collapse is not purely a resolution collapse.** Its ratio
  falls 11× (13.7 → 1.2) while its self floor grows only 3.8×; the rest is that
  the foil's *exafference* residual also falls 3× (0.101 → 0.033) — the same
  localized-source dilution the [Correction](#correction-against-the-pre-registration)
  above records for the modulated curve. Both curves are diluted; the
  dilution-free statement is the self-floor comparison above.

Reproduction:
[`audit_q1_modulation.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/audit_q1_modulation.py).
`run_one` now takes an optional `basis_mode` (`own` / `shuffle` / `single`); the
default reproduces the committed sweep exactly (all four baseline numbers above are
unchanged). Row moves 🟡 → ✅ for the *modulation-is-necessary* claim, with the
absolute-resolution question left where the page already left it.


## What's measured and plotted
**Raw data (per run = segment count × mode {modulated, foil} × seed):** each zone
accumulates its **own** sensed displacement (the dual-port modulator). Every 0.25 s
window: each zone's mean reading `r_k`, the aggregate residual, and a phase tag.
**Computed:** the per-zone `basis`, the modulated/foil residuals, and the
exafference/self-test `ratio` — defined as running code in
[Formalism](#formalism-per-zone-distributed-reafference) above.

**Plotted:** **A** ratio vs segment count, modulated vs foil; **B** the self-test residual (the noise floor) vs segment count, modulated vs foil.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_q1_modulation.py
```
