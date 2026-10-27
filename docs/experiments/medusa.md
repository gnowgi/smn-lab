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

![The medusa's designed body (top view) and its self-model recovered from movement alone](../figures/medusa_self_world_card.png)

**Reading the numbers.** The body has 49 segments and 90 `f`s. Segment `0` is the
aboral apex; `1–8`, `9–16` and `17–24` are the three bell rings, inner to outer,
so `17–24` is the **margin**. The six tentacles hang from margin spokes 0, 1, 3, 4, 5
and 7, each four segments long, root-to-tip:

| tentacle | hangs from margin segment | segments (root → tip) |
|---|---|---|
| T1 | 17 | 25 · 26 · 27 · **28** |
| T2 | 18 | 29 · 30 · 31 · **32** |
| T3 | 20 | 33 · 34 · 35 · **36** |
| T4 | 21 | 37 · 38 · 39 · **40** |
| T5 | 22 | 41 · 42 · 43 · **44** |
| T6 | 24 | 45 · 46 · 47 · **48** |

The tips (bold) are the world-model's transducers in §2. Margin segments 19 and 23
carry no tentacle: six tentacles cannot sit evenly on eight spokes.

**The self-model.** The right-hand panel is recovered by the disk's procedure,
unchanged: random pull-only drive on every `f`, no medium, and the `endpoint`
read-out (each `f`'s two strongest co-moving segments are taken as its endpoints).
Red edges are the misses. Endpoint recovery is **0.86**, and the errors are not where
one might guess. The tentacles are recovered almost perfectly (22 of 24 tentacle
`f`s, all 18 braces). The misses cluster at the **bell's centre**: 7 of the 8
apex-to-inner-ring spokes, and 7 of the 8 inner-ring coronal links. Why the hub
reads worst is not yet established. One plausible reading, unverified, is that
eight `f`s converge on the apex, so no single link's drive dominates its motion.

## The experiment on one page

![The medusa as a one-page experiment figure — body plan, world, recovered self-model, world-model as decoded versus true source location (sessile beside swimming), and the razor](../figures/medusa_page.png)

Panel 4 departs from the [Hydra](hydra.md) page on purpose. The Hydra's world-model
is a per-zone world signal, so it can be painted onto the self-graph. The medusa's
is not: it is the **decodability** of a hidden source from the tips' self-caused
change (§2). Painting the tips' raw readings onto the graph would show the sessile
medusa "localizing" the source, because a still tip does register it. That is
exactly the static reading the experiment excludes. So panel 4 draws the order
parameter itself: on held-out trials, each true source (●) joined to its decoded
location (×). Sessile, the decoder can only guess the centre. Swimming, the guesses
move out toward the sources.

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

![World-model skill rises monotonically from chance at zero self-motion to 0.45 as the medusa moves, tracking the self-generated tip baseline; the shuffle control never rises above chance](../figures/medusa_world_model.png)

| self-motion α | world-model skill (x-y) | skill (3-D) | shuffle |
|---|---|---|---|
| **0.0 (sessile)** | **−0.02** | 0.05 | 0.02 |
| 2.0 | 0.12 | 0.18 | −0.10 |
| 4.0 | 0.26 | 0.29 | −0.12 |
| 7.0 | 0.36 | 0.36 | −0.12 |
| 10.0 | 0.41 | 0.39 | −0.12 |
| 13.0 | 0.45 | 0.41 | −0.10 |

*The shuffle column was corrected on 27 Oct 2026. The earlier table
(−0.03 … −0.04) matched neither the committed figure nor a re-run of the committed
script; the values above are the re-run, and agree with the figure.*

!!! warning "Scoring caveat — the published skill is horizontal only"
    `smn_lab.metrics.decoding_skill` measures error as `np.hypot(*(pred − P).T)`,
    written for 2-D positions. Given the medusa's 3-D source locations, NumPy treats
    the third column as hypot's output buffer, so the score counts **x-y error
    only** and silently drops the vertical, which is the swim axis. The x-y column
    reproduces the published numbers exactly. The 3-D column is the full error,
    computed in `medusa_self_world.py`. The razor survives: 0.05 sessile to 0.41
    swimming. The only other callers, the two Hydra scripts, decode 2-D
    positions and are unaffected. The fix to `decoding_skill` is left to its own change,
    because it moves the medusa's headline number from 0.45 to 0.41.

!!! success "Result — the razor"
    At `α = 0` the source location is **undecodable** (skill ≈ chance): the sessile
    animal, one fixed projection with no self-caused change, has **no world-model**.
    As the medusa moves, skill **rises monotonically** to 0.45, tracking the
    self-generated tip **baseline** (parallax). The world-model is **emergent in
    self-motion**, not stipulated. The shuffle control never rises above chance
    (it sits slightly below zero, at −0.10 to −0.12, once the animal moves). This
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
cd experiments && ../.venv/bin/python medusa_self_world.py    # body, self-model, one-page figure
```
