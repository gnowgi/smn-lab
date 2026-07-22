# R2 — resumption latency (post-halt reversal is faster)

**Register 2.** During active engagement the alert energy `E_R` builds. After a
brief **halt**, a small **reversed** target flips the active zone; the newly-active
(previously-alert) zone's drive is amplified by `(1 + gamma*E_R)` — a head start
that shortens the resumption latency, `Δt ≈ gamma*E_R / K_p`. Classical inhibition
has no alert energy and no amplification, so it is slower.

**Reconciliation with [Prediction 1](sweep_pred1_haltability.md).** Prediction 1
found the *halt itself* carries no speed benefit — the dwell is a genuine stop. R2
is a different claim: it is the **resumption** after the halt, in a new direction,
that the primed partner accelerates. Halting costs; resuming from a primed state
pays. The two are consistent.

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_r2_resumption.png)

## Pre-registration
- **Hypothesis:** post-halt reversal latency is shorter under SMN than classical inhibition, and the advantage grows with the alert energy at release.
- **Order parameter:** resumption latency (time to displace into the reversal); SMN advantage `Δt = latency_classical − latency_SMN`.
- **Matched foil:** classical inhibition.
- **Pass:** `latency_SMN < latency_classical`, rising with load.

## Result
![R2 — SMN resumption latency falls with alert energy while classical inhibition is flat; the advantage grows with E_R](../figures/sweep_r2_resumption.png)

Engage against a load (E_R builds) → halt → flip the target. **SMN latency
121–172 ms** (falling as E_R rises) against the **classical foil's flat 312 ms**;
the **advantage grows with the alert energy at release** (140 → 191 ms) — exactly
`Δt ≈ gamma*E_R/K_p`. Because the partner tone (R1) opposes the reversal near the
target, the order parameter is the *initiation* speed the amplification governs,
not settling at a static offset.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_r2_resumption.py
```
