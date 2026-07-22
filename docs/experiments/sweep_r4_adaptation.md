# R4 — world-model adaptation dynamics (κ > 0)

!!! warning "Status: preregistered — implementation in progress"
    This page is the **preregistration** for R4, on branch `exp/r4-adaptation`.
    The hypothesis, order parameter, and matched foil are fixed here *before* the
    modulated-vs-foil sweep is run. See [Contributing experiments](../contributing.md)
    for the workflow.

Mastery of the world is not only a *static* decoding skill (cf.
[S1](sweep_geometry_worldmodel.md), [Q1](sweep_q1_modulation.md)) but an
adaptation **process**: after the world changes, the world-model re-fits and the
rolling-RMS reafference residual decays back toward the noise floor. R4 measures
that decay.

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_r4_adaptation.png)

## Preregistration

- **Hypothesis.** After a step change in the world (a field remap or an object
  move), the rolling-RMS reafference residual decays toward the noise floor at a
  rate $\kappa > 0$ under modulation; a non-modulatory foil does not adapt
  ($\kappa \approx 0$; the residual stays elevated).
- **Order parameter.** $\kappa$, the exponential decay rate of the post-change
  rolling-RMS residual, fitting $r(t) = r_\infty + (r_0 - r_\infty)\,e^{-\kappa t}$.
- **Matched foil.** The unmodulated control — same body, same world change,
  modulation off.
- **Pass.** $\kappa_\text{SMN} > 0$ and the residual returns to within 10 % of the
  noise floor; foil $\kappa \approx 0$.
- **Falsify.** $\kappa \approx 0$ under modulation → mastery is not a dynamic
  process in the bench.

## Order parameter, in code

The estimator is the single source of truth, read from the script at build time:

```python
--8<-- "experiments/sweep_r4_adaptation.py:kappa"
```

## Run

```bash
cd experiments && ../.venv/bin/python sweep_r4_adaptation.py
```

Running it now executes a synthetic **self-test** of the estimator (a decay with
a known $\kappa$, recovered) — not yet a bench measurement. The
modulated-vs-foil sweep on the two-CAZ body is the next step; when it passes,
this page graduates to `main` with its result and plot.
