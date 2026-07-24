# Proprioceptive entrainment — the mechanism, and an open problem

!!! info "Status: closed the loop; the payoff is deferred (three review rounds)"
    An external scientific-accuracy review pushed this from a claimed *result* to an
    honest *mechanism + open problem* over three rounds — two headline claims were
    **withdrawn** along the way. The endpoint: the loop is closed with the
    biologically correct topology and a CI-guarded invariant, but a positive
    demonstration that the body shapes the rhythm needs a further step. See the
    [release notes](../release-notes.md).

## The gap this closes

Proprioception is *present* in the base bench — the [servo board](../concepts.md)
reads its own joint angle, the [self-model](self_model_topology.md) is built from
joint velocities, [dead reckoning](q2_reafference.md) integrates sensed velocity. What
was missing is proprioception reaching the **rhythm**. `MessagingBeam.command()`
advanced `self.phase` from `omega` + neighbour coupling alone — a **controller
commanding a body**, not a **body-and-controller in mutual entrainment**. Lamprey
edge cells and *C. elegans* stretch-receptor coupling feed mechanics back into the
oscillators (Wen et al. 2012, *Neuron* 76:750) — the layer where the SMN thesis *the
body is the computer* is strongest.

## How it took three rounds (each correction kept)

| round | added / claimed | what review found | outcome |
|---|---|---|---|
| 1 | opt-in `entrain` term; "arrest during a gated halt" | (a) `arctan2` args swapped → pull was `cos(2φ)`, nonzero under perfect tracking; (b) ungated pull → the halt "arrest" was the `arctan2(0,0)=0` edge case | both **withdrawn** |
| 2 | fixed arg order + magnitude gate; "coupling drags freq to arrest" | the term entrained each oscillator to its **own** servo-delayed joint → `sin(ψ−φ)=sin(−δ)`, a constant brake; the curve was pure frequency **detuning** | **withdrawn** |
| 3 | **inter-segmental** topology (this page) | — | current |

The round-3 term is the biologically faithful one: each oscillator is entrained to its
**anterior neighbour's** realized phase, offset by the intended head→tail lag, so the
wave propagates *through the body*; the head is the free pacemaker (no anterior
neighbour → no pull). `entrain_mode="inter"` is the default; `"self"` is kept only as
the ablation that shows why. Both vanish under perfect tracking; `entrain=0` is still
bit-for-bit the open loop (**all prior experiments reproduce exactly**).

## Result

![Entrainment (round 3): (A) the corrected pull vanishes under perfect tracking, unlike the round-1 cos 2φ; (B) on a 5-segment body the self ablation is a runaway brake while inter-segmental is stable; (C) frequency is flat vs drag under both — the open problem](../figures/entrainment.png)

**A — the invariant (no error → no pull).** Under perfect tracking the corrected pull
is `≡ 0` (blue); the round-1 term was a full-amplitude `cos(2φ)` (red). This is now a
**regression test** (`tests/test_entrainment.py`, pure-numpy) — the check that would
have caught the original bug before it reached a page. A CI workflow is provided at
`.github/workflows/tests.yml` (activate with a workflow-scoped push).

**B — why topology matters** (5-segment body). The `"self"` ablation is a **runaway
self-brake**: entraining an oscillator to a delayed copy of its own output can only
retard, so gain drags the frequency toward arrest — that is detuning, not the body
speaking. The correct **inter-segmental** form is far more stable: the free pacemaker
keeps the rhythm alive and the interior joints wait on their anterior neighbours.

**C — the open problem (honest negative).** Free-run frequency vs medium drag is
**flat under both topologies**. Closing the loop does **not**, by itself, make the
rhythm track the medium. In this bench the anisotropic drag loads body **translation**,
not joint **articulation**, so the entrainment sees a spatially-uniform servo lag with
no medium gradient to read. (An apparent drag-dependence on a 3-segment body was a
2-joint edge artifact; it vanishes here.) A positive result — medium-dependent
frequency, the *C. elegans* water↔agar law — needs a **joint-loading model**: a drag
torque on the bend itself, or a load-limited actuator. That is the **declared next
step**; a first crude attempt was numerically unstable and is not shipped.

## What it shows, and does not

- **Shows:** the loop is now closed with the **correct mechanism** — inter-segmental
  proprioceptive coupling, faithful to Wen et al., zero under perfect tracking, and
  CI-guarded. The `"self"` ablation makes explicit why naive self-entrainment (the
  withdrawn round-2 claim) is only detuning.
- **Does not show:** that the body shapes the rhythm. There is **no positive
  demonstration** yet — free-run frequency is dominated by a uniform servo lag and is
  flat vs the medium under both topologies. The payoff awaits the articulation-load
  step. The S0 "locomotion is a network effect" claim is therefore **not** yet
  strengthened by a bench result here; only the mechanism is in place.

!!! note "Why this is logged as a result at all"
    A correct-but-not-yet-decisive mechanism, with two withdrawn claims and a CI test,
    is a more useful artifact than a tidy figure that turned out to measure an
    `arctan2` edge case or a servo lag. The page maps exactly what remains: land the
    articulation load, then ask panel C again.

## The fix plan — pre-committed (before the physics run)

Written down **before** running, so the criteria can't drift to fit the outcome. Four
changes in dependency order (each useless without the ones before), then the criteria
that decide success, then the failure reading we commit to in advance.

**The four changes.**

1. **Topology (done).** Anterior-neighbour coupling — the only change that turns
   self-feedback into something that can both retard *and* advance the wave. In place
   (`entrain_mode="inter"`), CI-guarded.
2. **Make the drag produce articulation load — don't bolt one on.** *Not* joint damping
   scaled by viscosity (a fudge factor that hands us the answer). The principled fix:
   `apply_anisotropic_drag` applies one force at each segment's **centre of mass**, so a
   rod rotating about its end misses the resistance its distal half sweeps through the
   fluid. Integrate resistive force theory **along the link** (3–5 sample points), so
   bending resistance emerges from the *same* `c_trans` that already produces thrust —
   one parameter, two consequences, no new knob.
3. **Load-limited actuator.** With `kp=4.0` the servo imposes bend timing regardless of
   load (δ ≈ 50°, drag-independent). Drop `kp` / lean on `cmax` (or the muscle-impedance
   model from Prediction 3). Test before proceeding: **δ must now vary with drag** — log
   it and confirm.
4. **The control that decides it worked — two frequencies logged separately.** A loaded
   body slows *whether or not the loop is closed* (mechanics), and that looks like
   success on a freq-vs-drag plot. So log **`f_beam`** (the oscillator's own phase-advance
   rate) and **`f_body`** (the realized bend frequency) separately. The claim is
   specifically that **`f_beam` acquires a drag dependence** and stays phase-locked to
   `f_body`. If `f_body` falls while `f_beam` stays flat, that's a body dragged behind an
   indifferent controller — the original problem in disguise.

    | | ε = 0 | ε > 0 |
    |---|---|---|
    | `f_beam` | flat in drag *by construction* | **must bend down** ← the claim |
    | `f_body` | may fall (mechanics alone) | falls, stays locked to `f_beam` |

**Success criteria (pre-committed).**

1. **Null preserved.** Perfect-tracking pull stays `~1e-16` and `ε=0` reproduces prior
   results bit-for-bit. (Panel A + CI.)
2. **No free-running brake.** At the lowest drag, `f_beam` at `ε>0` is close to the
   commanded 0.9 Hz. Operationalized by the standing diagnostic: `correction_dc_ratio(ent)
   < 0.05` in steady free swimming (a corrector is zero-mean ripple; a brake is
   DC-dominated). **The current term fails this**, which is exactly the open problem.
3. **Wavelength holds while frequency falls.** The strong one. Fang-Yen et al. (PNAS
   2010) varied external viscosity ~4 orders of magnitude in *C. elegans*: undulation
   frequency fell continuously while **wavelength stayed roughly constant** — gait shape
   preserved, not just slowed. Nothing in the architecture builds this in, so if it falls
   out it is a real result. Read the target off that paper's figures, not from memory.

**Failure reading (committed in advance).** If `f_beam` stays flat after all four
changes, the honest conclusion is that **mechanical entrainment does not emerge from
this body plan — the "body is the computer" thesis is unsupported at this layer in this
bench.** Stating that in advance costs nothing, given the arrest figure is already
withdrawn.

**Sequencing.** Do **1 + 4 first** (topology + two-frequency logging) with the existing
drag: expect the brake to mostly persist and panel C flat — a clean intermediate showing
*the term is correct but the body has no load to report*. Then add **2 + 3** and see
whether `f_beam` moves. Splitting it this way means if C never moves, we know exactly
which claim failed.

**Standing diagnostic (now in CI).** `metrics.correction_dc_ratio` +
`tests/test_entrainment.py` guard the general signature of this whole class of bug: a
correction term whose DC component dominates its ripple has stopped correcting and
started biasing.

## Run

```bash
cd experiments && ../.venv/bin/python entrainment.py     # ~2 min, writes figures/entrainment.png
python ../tests/test_entrainment.py                       # the invariants (no MuJoCo)
```
