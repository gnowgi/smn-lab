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

## Run

```bash
cd experiments && ../.venv/bin/python entrainment.py     # ~2 min, writes figures/entrainment.png
python ../tests/test_entrainment.py                       # the invariants (no MuJoCo)
```
