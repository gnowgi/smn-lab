# Proprioceptive entrainment — closing the body → rhythm loop

!!! info "Status: response to a scientific-accuracy review; strengthens S0"
    Raised by an external review: in the base bench the messaging beam is causally
    sealed off from the body. This experiment closes the loop and tests whether the
    body can now perturb the rhythm. See the [release notes](../release-notes.md).

## The gap this closes

Proprioception is *present* in the base bench — the [servo board](../concepts.md)
reads its own joint angle every step, the [self-model read-out](self_model_topology.md)
is built from joint velocities, and [dead reckoning](q2_reafference.md) integrates
sensed body-frame velocity. What was missing is proprioception reaching the **rhythm**.
`MessagingBeam.command()` advanced `self.phase` from `omega` and neighbour coupling
alone; no body state entered. So the beam could not slow under load, could not
re-phase after an obstruction, and — the sharp case — during a gated halt it wound
through cycles the body never executed. It was a **controller commanding a body**,
not a **body-and-controller in mutual entrainment**.

Real undulators do not work this way. Lamprey **edge cells** and *C. elegans*
**stretch-receptor coupling** between adjacent regions feed the mechanics back into
the oscillators — so much so that the "oscillator" is largely mechanosensory rather
than neural (Wen et al. 2012, *Neuron* 76:750; Cohen & Sanders on lamprey edge cells).
That is exactly the layer where
the SMN thesis — *the body is the computer* — should be strongest, so leaving it open
understated the theory's own claim.

## What was added (opt-in, nothing else changes)

`MessagingBeam` gained an `entrain` gain (default `0.0`) and `command()` now accepts
the actually-sensed joint state `theta`, `theta_dot`. When `entrain > 0`, each
oscillator is pulled toward the **phase its own segment is really bent to** — the
`(theta, theta_dot/omega)` pair traces a circle whose angle is the segment's realized
gait phase, and `dphi += entrain · sin(psi_body − phase)`. With `entrain = 0` (or no
`theta` passed) the beam is bit-for-bit the sealed open-loop generator, so **every
existing experiment reproduces exactly**; only this page turns the loop on.

## The test

A three-block crawler, commanded frequency fixed at `0.9 Hz`. The HAP gates the wave
off for a 2 s window (the same halt mechanism as [C1](c1_touch.md)), and we log the
head oscillator's phase. Then a medium-resistance sweep for the frequency question.
Both outcomes are pre-committed as informative.

## Result

![Proprioceptive entrainment: (A) the closed loop arrests during a halt while the open loop winds straight through; (B) cycles wound during the halt fall as the gain rises; (C) undulation frequency does not adapt to the medium in either loop](../figures/entrainment.png)

**A — the arrest (the loop is closed).** Open loop (`entrain=0`), the phase climbs
straight through the 2 s halt, winding **1.80 cycles = ωT** the body never executed.
Closed loop (`entrain=6`), the oscillator is pulled toward the body's arrested state:
it **plateaus inside the halt band** and, overall, winds at a lower rate. The body now
reaches the rhythm.

**B — progressive arrest.** Cycles wound during the 2 s halt fall monotonically with
the entrainment gain — from the full free winding (**1.80**, `ε=0`) to **0.75** at
`ε=6`. The order parameter is unambiguous: mechanics feed the phase.

**C — an honest negative.** Steady-state undulation frequency vs medium drag stays
**flat in both loops** (`≈0.89 Hz` open; a lower `≈0.6 Hz` offset closed — entrainment
lowers the baseline but does **not** make it drag-dependent). So closing the loop does
**not**, by itself, reproduce the *C. elegans* water↔agar frequency law here: in this
bench the anisotropic drag resists body **translation**, not joint **articulation**,
and the stiff PD servo imposes the bend timing, so there is no articulation load for
the medium to modulate. Reproducing frequency-adaptation needs a **joint-loading
model** (drag torque on the bend itself, or a load-limited muscle) — a declared next
step, not something the feedback path alone delivers. Reporting this rather than
tuning a demonstrator into existence is the same discipline the review asked for.

## What it shows, and does not

- **Shows:** the body can now perturb the rhythm — arrest is felt, the wave is held
  to the mechanics, and S0's "locomotion is a network effect" now includes the body,
  not just the software layer. This is the property the base beam lacked.
- **Does not show:** medium-dependent frequency adaptation (panel C), and it is not
  wired into the default experiments (they stay open-loop for reproducibility). The
  entrainment term is a minimal edge-cell surrogate, not a validated stretch-receptor
  model.

## Run

```bash
cd experiments && ../.venv/bin/python entrainment.py
```

Writes `figures/entrainment.png`. Runtime ~1 min on a laptop CPU.
