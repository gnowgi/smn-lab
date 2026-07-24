# S1 field-scale control — is the resolution null real, or field geometry?

!!! info "Status: control experiment for the S1 world-model null"
    This page tests whether the flat-in-`n_seg` result of
    [S1](sweep_geometry_worldmodel.md) is evidence for the SMN resolution principle
    or a mundane **field-geometry artifact**. Raised by an external scientific-accuracy
    review; see the [release notes](../release-notes.md).

## Why this control exists

S1 found held-out decoding skill **flat** across segment count and read it as
consistent with the resolution principle (resolution = CAZ density × internal
capacity, *not* raw transducer count). But there is a competing explanation the S1
design cannot rule out: the S1 field's spatial scale is `sigma ≈ 0.8–0.9 m`, far
larger than the body (`≈ 0.2 m`), so **every segment reads a nearly identical
value** and extra segments add almost no *independent* information — whatever the
theory says. Under a large-`sigma` field the two explanations make the *same* flat
prediction, so S1 does not separate them.

## Pre-committed test

- **Hypothesis (discriminating).** Repeat the sweep under a **body-scale field**
  (`sigma ≈ body length`, tiled so the body always spans a gradient), where
  different segments genuinely read different values.
    - If skill **still does not rise** with `n_seg` → the resolution-principle
      reading survives (extra ungated transducers add no resolution even when the
      information is there to be had).
    - If skill **rises** with `n_seg` under the body-scale field → the S1 flat-null
      was the **field-geometry artifact**, and S1 must not be cited as evidence for
      the resolution principle.
- **Order parameter.** The slope of decoding skill vs `n_seg`, under each field
  scale (large-`sigma` control vs body-scale). Threshold: a rise > 0.01 skill per
  segment counts as "rises."
- **Matched control.** The original large-`sigma` field, run in the same harness, as
  the reference that reproduces the S1 flat null.
- **Both outcomes are informative** — this is a genuine discriminator, not a
  confirmation run.

## Result

![Field-scale control: held-out decoding skill does not rise with segment count under either the large-sigma field or a decodable body-scale field](../figures/sweep_geometry_worldmodel_fieldscale.png)

Full budget (8 seeds, 75 s):

| field | n_seg=3 | n_seg=5 | n_seg=9 | slope vs n_seg |
|---|---|---|---|---|
| large-`sigma` (~0.85 m, original S1) | 0.486 | 0.516 | 0.364 | **−0.023** |
| body-scale (broad + fine texture, ~0.22 m) | 0.506 | 0.275 | 0.300 | **−0.029** |

Two things matter. First, the **body-scale field is decodable** — skill ≈ 0.5 at
`n_seg=3`, comparable to the large-`sigma` field — so this is a *fair* test:
segments now read genuinely different values, yet absolute position stays globally
recoverable. Second, and decisively for the confound: **skill does not rise with
segment count under the body-scale field either** (slope −0.029, indistinguishable
from the large-`sigma` −0.023). So the S1 flat-null is **not** the field-geometry
artifact — it survives even when extra segments carry independent information. That
leaves the [resolution-principle](sweep_q1b_resolution.md) reading standing
(resolution = CAZ density × modulation, not raw transducer count), so S1 may now be
cited as *consistent with* that principle rather than merely undecided.

!!! note "A control that corrected itself"
    The first version of this control used a *periodic* checkerboard body-scale
    field, which made absolute position ambiguous (aliased) and collapsed decoding
    to ~shuffle regardless of `n_seg` — a degenerate field, not evidence. Fixed to a
    multi-scale field (broad sources for global decodability + aperiodic fine
    texture). Logged in the [release notes](../release-notes.md) as an instance of
    the same honesty the review asked for.

!!! warning "Caveat"
    Variance is wide (±0.12–0.36, largest at `n_seg=9`); "flat" means no rise
    detectable at this budget. The qualitative outcome — no rise with `n_seg` under
    either field — is consistent across the 4-seed and 8-seed runs, but a
    higher-seed run would tighten the slope estimate.

## Run

```bash
cd experiments
../.venv/bin/python sweep_geometry_worldmodel_fieldscale.py
```

Sweeps `n_seg ∈ {3, 5, 9}` × 4 seeds × {large-`sigma`, body-scale} fields, computes
held-out kNN decoding skill (with shuffle control) for each, fits the skill-vs-`n_seg`
slope per field, and writes `figures/sweep_geometry_worldmodel_fieldscale.png`.
