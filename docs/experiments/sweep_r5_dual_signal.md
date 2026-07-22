# R5 — intra-body dual-signal residual (a structural signature)

**Register 5.** Two CAZs of one SMN whose mechanical states co-determine a shared
sensory substrate are in *self-contact*: what CAZ_y's transducer reads depends on
where the partner CAZ_x is. Because the partner's configuration is on the broadcast,
the reafference residual is fully explained by the **partner-as-stimulus** form —
regressed against

$$\Delta\hat s = I\!\left[\exp\!\frac{-(\theta_y-\theta_x)^2}{\sigma^2}
   - \exp\!\frac{-(\theta_y-\phi_0)^2}{\sigma^2}\right],$$

$R^2 \to 1$. For a **decoupled** control (the same transducer reading an exogenous
stimulus), $R^2 \to 0$. The signature is **structural** (a fit quality), not a
magnitude difference — diagnostic, and not confounded by noise level.

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_sweep_r5_dual_signal.png)

## Pre-registration
- **Hypothesis:** in self-contact the residual is fully explained by the partner-as-stimulus form (R² → 1); decoupled, it is not (R² → 0).
- **Order parameter:** R² of the residual against the partner-as-stimulus regressor.
- **Matched foil:** decoupled (exogenous stimulus, same magnitude & noise).
- **Pass:** R²_self ≈ 1 and R²_decoupled ≈ 0.

## Result
![R5 — the residual is structurally explained by the partner-as-stimulus form in self-contact (R²≈1) but not when decoupled (R²≈0)](../figures/sweep_r5_dual_signal.png)

A two-CAZ body (two MuJoCo hinges under independent drive) supplies the
trajectories; the self/world distinction is read off the residual's **structure**:
**R² self-contact 0.998**, **R² decoupled 0.056**. Self, world, and other are told
apart by a structural contrast, not a magnitude — the dual-signal property made
operational.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_r5_dual_signal.py
```
