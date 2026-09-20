# The medusa — a moving cnidarian builds a world worth having

The disk experiments held the cnidarian **sessile**. That is one turn of the
body-plan dial (see the [cnidarian model system](../cnidarians.md)); this is the
next — **add movement**. A polyp anchored to the substrate senses only what the
world does *to* it. A **medusa** swims, and moves its tentacles, so for the first
time the animal produces **self-caused** sensory change. The claim under test
(G. Nagarjuna): *a sessile cnidarian is unlikely to construct a valuable
world-model* — and self-motion is what changes that.

Everything keeps the settled vocabulary ([vocabulary](../vocabulary.md)): a
**segment** is an `s`, every **link is one `f`** (a pull-only contractile unit),
and a **CAZ** is a *zone of coordinated action* over `f`s — here the swim itself,
a pulsation pattern coordinated across the bell, read out and never imposed by a
controller.

## The body — a dome bell with curling tentacles

The medusa is a shallow **dome** (a paraboloid umbrella, apex aboral/up), built
from the same `f` scaffold as every other body (`smn_lab/medusa.py`). Three link
kinds do three jobs:

| link kind | role | driven? |
|---|---|---|
| **coronal** (circumferential rings) | the **subumbrellar swimming muscle** — contract to squeeze the bell (the power stroke) | yes — the swim |
| **radial** (spokes: apex→ring, ring→ring) | structural **mesoglea** that bears the dome and elastically restores it (the recovery stroke) | no |
| **tentacle** (chains hanging from the margin) | contract to **curl/retract** the tentacle | yes — the probe |

A single hanging chain of point-mass links is a floppy string: contract it and it
curls, but nothing straightens it again. So each tentacle also carries passive
**brace** `f`s (2-hop links) — the **mesoglea antagonist** of a muscular hydrostat,
the elastic side that re-extends the tentacle. It is opponency in its most
primitive form (muscle vs passive elastic), not a discrete opponent pair.

## 1 · The medusa swims — coordinated pulsation nets locomotion

The disk cannot move; the medusa can. Its coronal `f`s **pulsate** — a fast power
stroke, then a spring-limited recovery — in a pond modelled as an explicit
**quadratic-drag** medium (`smn_lab.medusa.apply_medium`, the same
inspectable-medium philosophy as the [crawler](c0_crawler.md), but nonlinear).
Nobody pushes the body: the swim is the whole-SMN consequence of a pulsation
*pattern* meeting the medium.

The load-bearing physics is the **scallop theorem** and its escape. A reciprocal
shape change (contract, then relax) nets **zero** displacement in a *linear*-drag
world, however vigorous. The medusa escapes it by a **rate asymmetry** — a sharp
power stroke, a slow recovery — biting against the **nonlinear** law: the fast
stroke meets far more resistance than the slow one, so their drag impulses do not
cancel. Two controls prove that this, and only this, is the mechanism:

![The medusa swims: net aboral displacement climbs monotonically under pulsation; the linear-drag and symmetric-drive controls both collapse to zero](../figures/medusa_swim.png)

- **Linear-drag control** (`c_quad = 0`): the same pulsation in a purely linear
  medium → net translation collapses. The *nonlinearity* is necessary.
- **Symmetric-drive control**: the same time-averaged coronal force applied
  *steadily* (no power/recovery asymmetry) → net translation collapses. The *rate
  asymmetry* is necessary.

!!! success "Result"
    The medusa translates **aboral** (`+0.06` over 24 s, monotonic), **~20×**
    either control. Order parameter: **net aboral displacement per unit time** — a
    collective, emergent locomotor rate that is exactly zero for the disk and turns
    positive only when an asymmetric pattern meets a nonlinear medium.

## 2 · A sessile cnidarian builds no world-model; a moving one does

Now put a **world source** in the pond — a Gaussian field peak (chemical/thermal)
at a fixed 3-D location, of randomised strength. It is a **distal** modality
(evaluated bench-side at each sensor's position — `smn_lab.fields`), so it does
**not** push the body: the animal's self-motion is *independent* of where the
source is. One swim, many possible worlds. The **tentacle tips** are the
transducers.

The world-model is the **decodability of the source's location** from the
tip-sensor stream (held-out kNN skill, `smn_lab.metrics.decoding_skill`, with a
shuffle control). Crucially, the features are built from **self-caused change
only** — how much each tip's reading *swept* and *drifted* over the trajectory —
never the raw static reading. This is the SMN commitment that the world-model is
grounded in **modulated** sensation (cf. [Q1](sweep_q1_modulation.md)): with no
self-motion there is no modulation, hence no world-model. A fixed sensor array
reading a static field would hand a sessile animal a free bearing; that is exactly
the shortcut the SMN position rejects.

The test is the **order-parameter razor** ([order parameters](../order-parameters.md)):
sweep **self-motion amplitude `α`** (the control parameter — coronal + tentacle
drive; `α = 0` is the sessile disk) and read **world-model skill** (the order
parameter).

![World-model skill rises monotonically from chance at zero self-motion to 0.45 as the medusa moves, tracking the self-generated tip baseline; the shuffle control stays at zero throughout](../figures/medusa_world_model.png)

| self-motion α | world-model skill | shuffle |
|---|---|---|
| **0.0 (sessile)** | **−0.02** | −0.03 |
| 2.0 | 0.12 | −0.07 |
| 4.0 | 0.26 | −0.09 |
| 7.0 | 0.36 | −0.09 |
| 10.0 | 0.41 | −0.07 |
| 13.0 | 0.45 | −0.04 |

!!! success "Result — the razor"
    At `α = 0` the source location is **undecodable** (skill ≈ chance): the sessile
    animal, one fixed projection with no self-caused change, has **no world-model**.
    As the medusa moves, skill **rises monotonically** to 0.45, tracking the
    self-generated tip **baseline** (parallax). The world-model is **emergent in
    self-motion**, not stipulated — the shuffle control sits at zero throughout. This
    is *a sessile cnidarian is unlikely to construct a valuable world-model* turned
    from an assertion into a measured transition.

## Why this is the payoff of Phase B

The disk gave a self-model (the rim announces itself) but only a passive, world-caused
world-model. The medusa closes the loop the SMN architecture is really about: **the
animal moves, the world changes as a consequence, and that self-caused change is the
material the world-model is built from.** The same one shared pond will, in
[Phase C](../cnidarians.md), be handed to every body on the ladder, and the
decodable richness of the Umwelt each constructs — a direct function of how, and how
finely, it moves — becomes the cross-morphology order parameter.

## Reproduce

```bash
cd experiments && ../.venv/bin/python medusa_swim.py          # the swim + scallop controls
cd experiments && ../.venv/bin/python medusa_world_model.py   # the world-model razor
```
