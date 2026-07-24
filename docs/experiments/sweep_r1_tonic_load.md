# R1 — tonic-load coupling (partner tone rises with load)

**Register 1.** During a sustained isometric hold, the SMN's haltability operator
makes the *inactive* (partner) zone tonically engaged in proportion to the *active*
zone's load, through the alert energy `E_R`:

$$a_{\text{partner}} = a_0 + \beta\,E_R,\qquad E_R^{*}=\rho\,\tau_E\,F_{\text{active}}
\;\Rightarrow\; a_{\text{partner}} = a_0 + (\beta\rho\tau_E)\,F_{\text{active}}.$$

Classical reciprocal inhibition predicts the opposite: the partner is held at
baseline, **independent of load** (slope 0).

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_r1_tonic_load.png)

## Pre-registration
- **Hypothesis:** partner tone rises linearly with the active zone's steady-state force; slope = `beta*rho*tau_E > 0`.
- **Order parameter:** the fitted slope of `a_partner` vs `F_active`.
- **Matched foil:** classical inhibition (the same board with no alert energy).
- **Pass:** SMN slope > 0 and ≈ `beta*rho*tau_E`; foil slope ≈ 0.

## The board (single source of truth)
The alert energy and its routing are read from `smn_lab/control.py`:
```python
--8<-- "smn_lab/control.py:alert_energy"
```

## Result
![R1 — partner tone rises linearly with active load under the SMN, flat under classical inhibition](../figures/sweep_r1_tonic_load.png)

!!! note "Epistemic status: analytic / consistency check, not a contingent finding"
    R1 is **guaranteed by construction**: `AlertEnergyBoard` *sets* the resting
    partner to `a0 + beta*E_R`, whose steady state is `E_R* = rho*tau_E*F`, so the
    slope `beta*rho*tau_E` follows algebraically. This experiment therefore
    **verifies that the integrator reproduces the closed-form steady state** — a unit
    test of the ODE, and of the SMN's *departure from classical inhibition* (whose
    foil has no such state and is flat). It is **not** evidence about opponent
    physiology; that would need a biological measurement. We keep it in a different
    epistemic category from results that could have come out otherwise (the S1 null,
    the Q2 downgrade).

An opponent CAZ (one MuJoCo hinge, two pull-only motors) holds a configuration
against a swept external load. **SMN slope 0.744**, matching the closed-form
`beta*rho*tau_E = 0.750` — the integrator reproduces the predicted tonic-load
coupling. The **classical-inhibition foil is flat (−0.00)**, as it must be: it has
no alert-energy state to carry load into resting tone.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_r1_tonic_load.py
```
