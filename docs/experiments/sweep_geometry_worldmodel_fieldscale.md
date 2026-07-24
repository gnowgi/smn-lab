# S1 field-scale control — WITHDRAWN (the order parameter was confounded)

!!! danger "Verdict withdrawn on review"
    This control once claimed the S1 flat-null "is not a field-geometry artifact →
    resolution principle survives." A scientific-accuracy review checked the harness in
    code and simulation; the verdict does **not** hold and is **withdrawn**. The
    decoder is clean, but its *order parameter* — the slope of kNN decoding skill vs
    `n_seg` — is confounded three ways. The control is **inconclusive**. See the
    [release notes](../release-notes.md).

## What it was supposed to do

[S1](sweep_geometry_worldmodel.md) found decoding skill flat in segment count under a
large-`sigma` field and read it as consistent with the resolution principle. The
competing explanation is **field geometry**: under a large-`sigma` field every segment
reads nearly the same value, so extra segments add no independent information whatever
the theory says. This control was meant to separate the two with a **body-scale**
field where segments genuinely read different values.

## Why it fails — three confounds, all reproduced

The experiment now runs three fields through **two** decoders. `broad_only` is the
original large-`sigma` S1 field (a **dimensionality control**: by construction it
carries *no* independent per-segment information). `broad+fine` was the first control
field. `weakbroad+fine` scales the broad sources down to 0.35 so they only anchor
global position without masking the body-scale texture.

Full budget (8 seeds, 75 s). Skill (mean); slope = skill per segment:

| field | decoder | n=3 | n=5 | n=9 | slope |
|---|---|---|---|---|---|
| `broad_only` (=S1 large-σ, **no** independent info) | kNN | 0.486 | 0.516 | 0.364 | **−0.023** |
| | ridge | 0.383 | 0.456 | 0.331 | −0.012 |
| `broad+fine` (first control field) | kNN | 0.506 | 0.275 | 0.300 | **−0.029** |
| | ridge | 0.402 | 0.194 | 0.183 | −0.032 |
| `weakbroad+fine` (decodable, **unmasked**) | kNN | 0.503 | −0.098 | 0.328 | −0.010 |
| | ridge | 0.161 | −0.027 | 0.367 | **+0.044** |

![Field-scale control confounded: kNN slopes are dimensionality artifacts; under a dimension-robust ridge decoder, unmasking the body-scale field flips the slope positive](../figures/sweep_geometry_worldmodel_fieldscale.png)

**1 — Decoder dimensionality.** The order parameter was the slope of **kNN** skill vs
`n_seg`. kNN degrades with state dimension (`2·n_seg` channels), so it manufactures a
**negative slope even for `broad_only`** (−0.023) — a field that carries no independent
per-segment information at all. The negative slope came from the decoder, not the
world. A dimension-robust **ridge** readout nearly flattens it (−0.012). The original
verdict test (`kNN slope ≤ 0.01 → "survives"`) is thus satisfiable by any field.
(Note `broad_only` here reproduces the *published* large-σ row exactly — 0.486/0.516/0.364,
kNN −0.023 — so this is the same harness, not a different one.)

**2 — Field masking.** `broad+fine` kept the three broad S1 sources "for decodability."
But they dominate the signal and are `n_seg`-flat, so they **swamp** the fine
body-scale component whose `n_seg`-dependence is the whole point. Scale the broad
sources down (`weakbroad+fine`) and the **ridge slope flips positive** (−0.032 →
**+0.044**): a genuinely body-scale, unmasked field shows *more body → more decodable
world* — exactly the effect the control was built to detect, hidden by the broad
sources it retained.

**3 — Trajectory noise.** Skill is strongly trajectory-dependent. Every field dips at
`n_seg=5` (see the published `broad+fine` row: 0.506 → 0.275 → 0.300, non-monotone) and
seed variance is ±0.2–0.6. A slope at this budget cannot resolve the question anyway.

## Consequence

The control does **not** separate the resolution principle from a field-geometry
artifact — if anything, the unmasked field leans toward the artifact. So the **S1
flat-null is consistent with either explanation** and [S1](sweep_geometry_worldmodel.md)
no longer cites it as evidence for the resolution principle. That claim rests instead
on the *modulation* experiments — [Q1](sweep_q1_modulation.md), [Q1b](sweep_q1b_resolution.md)
— where CAZ density is varied with modulation on vs off, which is the actual content of
the principle (resolution = CAZ density × modulation, not raw transducer count).

!!! note "The honest ledger for this page"
    Round 1 of this control used a periodic checkerboard field (aliased → undecodable);
    fixed to broad+fine. Round 2 (here) found broad+fine itself confounded and withdrew
    the verdict. A clean redesign — dimension-robust decoder, a decodable **and**
    unmasked body-scale field, an explicit trajectory/coverage control, and many more
    seeds — is future work. Until then this is logged as an **inconclusive** control,
    not a result.

## Run

```bash
cd experiments && ../.venv/bin/python sweep_geometry_worldmodel_fieldscale.py   # ~8-10 min
```

Runs all three fields through `metrics.decoding_skill` (kNN) and `metrics.ridge_skill`
(dimension-robust), and writes `figures/sweep_geometry_worldmodel_fieldscale.png`.
