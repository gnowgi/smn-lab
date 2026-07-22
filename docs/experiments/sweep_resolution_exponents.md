# Resolution exponent — R ∼ ρ^a (the resolution principle, measured)

!!! success "Result: a = 0.49 ± 0.14 (N=6), matching the predicted √ρ (a = ½)"

**Operational definition.** Resolution is the *world-detection ratio*

$$R = \frac{\langle|\text{world-caused residual}|\rangle}{\langle|\text{self-caused residual}|\rangle}$$

(dimensionless): $R=1$ means the world is lost in the self-noise floor, $R>1$ means
it is resolved above it. This is the order parameter of [Q1b](sweep_q1b_resolution.md).

**Mechanism → prediction.** Under per-zone modulation each zone cancels its own
self-motion, so the self-noise floor averages down as $\rho^{-1/2}$ while the
*distributed* world signal survives. Hence resolution scales as a **power** of CAZ
density, $R \sim \rho_{\text{CAZ}}^{\,a}$, with predicted exponent $a = \tfrac12$.
Modulation is the multiplicative **gate** (gain $\mu\in[0,1]$): $\mu=0 \to R\approx1$
(foil), $\mu=1 \to R \sim \sqrt{\rho}$ — a gate, not a second power law.

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_resolution_exponents.png)

## Pre-registration
- **Order parameter:** $R$ (world/self ratio).
- **Density fit:** $\log R = a\log\rho + c$, fitted per seed at full modulation.
- **Pass:** $a>0$ and consistent with $\tfrac12$; foil exponent $\le 0$.
- **Gate:** at fixed $\rho$, $R$ rises monotonically with $\mu$ from $\approx1$ toward $\sqrt{\rho}$.

## Result

| condition | exponent $a$ in $R\sim\rho^{a}$ |
|---|---|
| full modulation ($\mu=1$) | **0.49 ± 0.14** (95% CI ±0.12, N=6) — predicted 0.5 |
| foil ($\mu=0$) | **−0.52 ± 0.21** — resolution *declines* with density |

Mean $R(\rho)$ at $\mu=1$: 14.0 → 16.0 → 21.4 → 22.6 → 23.7 → 29.5 for $\rho = 3,5,7,9,11,13$.

**Modulation gate** at $\rho=9$: $R(\mu)$ = 1.43 → 1.57 → 1.86 → 2.74 → **22.6** for
$\mu = 0, 0.25, 0.5, 0.75, 1.0$ — a steep, saturating gate.

## The order parameter and the fit, in code

```python
--8<-- "experiments/sweep_resolution_exponents.py:resolution"
```

## Run

```bash
cd experiments && ../.venv/bin/python sweep_resolution_exponents.py
```

## Why a predicted exponent matters

A single predicted-and-confirmed exponent turns "resolution × density" from a slogan
into a **falsifiable, scale-free law**. The *value* is a fingerprint of the mechanism:
$a=\tfrac12$ is *independent per-zone averaging* (the √N of signal-to-noise everywhere
in physics); $a=1$ would mean coherent gain, $a=0$ no benefit. The measured 0.49 stakes
the mechanism on a number reality could have refused — and links the body's
world-resolution to the same √N that limits any instrument.
