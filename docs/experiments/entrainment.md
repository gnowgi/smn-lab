# Proprioceptive entrainment — closing the body → rhythm loop

!!! info "Status: response to a scientific-accuracy review; strengthens S0"
    Raised by an external review: in the base bench the messaging beam is causally
    sealed off from the body. This experiment closes the loop and tests whether the
    body can now perturb the rhythm. **A second review round caught two bugs in the
    first term — both are fixed here; see "A correction that corrected itself" below.**
    See the [release notes](../release-notes.md).

## The gap this closes

Proprioception is *present* in the base bench — the [servo board](../concepts.md)
reads its own joint angle every step, the [self-model read-out](self_model_topology.md)
is built from joint velocities, and [dead reckoning](q2_reafference.md) integrates
sensed body-frame velocity. What was missing is proprioception reaching the **rhythm**.
`MessagingBeam.command()` advanced `self.phase` from `omega` and neighbour coupling
alone; no body state entered. So the beam could not slow under load and could not
re-phase to an obstruction — it was a **controller commanding a body**, not a
**body-and-controller in mutual entrainment**.

Real undulators do not work this way. Lamprey **edge cells** and *C. elegans*
**stretch-receptor coupling** feed the mechanics back into the oscillators — so much
so that the "oscillator" is largely mechanosensory (Wen et al. 2012, *Neuron* 76:750).
That is exactly the layer where the SMN thesis — *the body is the computer* — should
be strongest.

## What was added (opt-in, nothing else changes)

`MessagingBeam` gained an `entrain` gain (default `0.0`) and `command()` accepts the
sensed `theta`, `theta_dot`. When `entrain > 0`, each oscillator is pulled toward the
**phase its own segment is really bent to**:

```python
psi = np.arctan2(th, thd / self.w)      # realized gait phase (th is the sine arg)
r   = np.hypot(th, thd / self.w)        # bend magnitude — the receptor drive
self.ent = (r / (r + 1e-3)) * np.sin(psi - self.phase)
dphi += self.entrain * self.ent
```

Two properties make this a *stretch* term rather than an arbitrary drive: (i) under
perfect tracking `th = amp·sin(phase)`, `thd/ω = amp·cos(phase)`, so `psi = phase` and
the pull is **identically zero** — no error, no pull; (ii) the `r/(r+ε)` gate makes a
**still body exert no pull** (a silent stretch receptor), so the phase estimate and
the pull both fade as the body stops. With `entrain = 0` or no `theta`, the beam is
bit-for-bit the sealed open-loop generator, so **every existing experiment reproduces
exactly**.

## Result

![Proprioceptive entrainment (corrected): (A) the pull vanishes under perfect tracking, unlike the first buggy term; (B) closing the loop drags the realized frequency down to arrest as coupling rises; (C) frequency does not adapt to the medium](../figures/entrainment.png)

**A — mechanism check (no error → no pull).** The corrected pull is **identically
zero** under perfect tracking (blue). The first version (red) was a full-amplitude
`cos(2φ)` — a spurious `2ω` drive that fired even when the body did exactly what it
was told. A stretch term that pulls under zero error is not modelling stretch.

**B — the body enters the rhythm.** With the loop closed, the realized undulation
frequency falls below the commanded `0.9 Hz` and, as the gain rises, is **dragged all
the way to arrest** (`0.89 → 0.75 → 0.53 → 0.27 → 0.04 Hz`). The reason is physical
and correct: the PD-driven body **lags** its command, so `psi` trails `phase`, the
pull is negative, and the oscillator locks to the body it is actually moving. The
rhythm is no longer the intrinsic `ω` — the body shapes it. (This bites *more* than a
first-order toy body predicts, because the real servo carries a real, consistent lag.)

**C — an honest negative (unchanged by the fix).** Realized frequency vs medium drag
stays **flat**. In this bench the anisotropic drag resists body **translation**, not
joint **articulation**, and the servo imposes the bend timing, so there is no
articulation load for the medium to modulate. Reproducing the *C. elegans* water↔agar
frequency law needs a **joint-loading model** (drag torque on the bend, or a
load-limited muscle) — a declared next step, not something the feedback path delivers.

!!! note "A correction that corrected itself"
    The **first** version of this experiment reported an "arrest during a gated halt"
    and a baseline-frequency offset. A second review round showed both rested on two
    bugs in the entrainment term:

    1. **Swapped `arctan2` arguments.** `arctan2(thd/ω, th)` makes `psi = π/2 − φ`, so
       the pull was `cos(2φ)` — a `2ω` drive that does **not** vanish under perfect
       tracking (verified: the pull was exactly `cos 2φ` to machine precision). Fixed
       by using `arctan2(th, thd/ω)`.
    2. **No magnitude gate.** The pull was applied at full strength even when the body
       was still, where `arctan2(0,0)=0` yanks the phase to a fixed `0`. The old
       "halt arrest" was that edge case — the phase was pulled toward zero, not toward
       the body's phase — not the mechanism. Fixed by the `r/(r+ε)` gate.

    With both fixed, the gated-halt arrest **disappears** (a slack body correctly
    exerts no pull), and a pinned-at-a-bend obstruction does **not** cleanly arrest
    either (a fixed bend gives `ψ=±π/2`, which speeds the oscillator as much as it
    slows it). So those framings are **withdrawn**; the corrected, robust result is
    panel B. Logged in the [release notes](../release-notes.md) as the same honesty
    the review asked for — the term is now right, and the result is smaller and true.

## What it shows, and does not

- **Shows:** the body now shapes the rhythm — closing the loop couples the oscillator
  to the actually-lagging body and drags the realized frequency down to arrest. S0's
  "locomotion is a network effect" now includes the body, not just the software layer.
- **Does not show:** medium-dependent frequency adaptation (panel C), arrest by a
  discrete obstruction (withdrawn above), and it is not wired into the default
  experiments (they stay open-loop for reproducibility). The term is a minimal
  edge-cell surrogate, not a validated stretch-receptor model.

## Run

```bash
cd experiments && ../.venv/bin/python entrainment.py
```

Writes `figures/entrainment.png`. Runtime ~1 min on a laptop CPU.
