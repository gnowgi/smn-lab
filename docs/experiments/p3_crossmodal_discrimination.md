# P3 — Cross-modal discrimination (recognition as a basal SMN result)

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **C-series** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [Lesson 1](../lesson1.md).


`experiments/p3_crossmodal_discrimination.py`

The P2 experiments showed the agent *building a world* — mapping, foraging,
self-localizing. This one asks whether **recognition** — telling one object
from another — needs any new machinery, or whether the same opponent-modulated,
located zones that forage are already enough.

The claim under test is that recognition needs **no new mechanism**. The set of
world-states that recruit the same action is the recognized category; the
invariant is in the coupling, not in a stored template. So the controller that
forages is the controller that discriminates — and it does so **actively, with
no labeled corpus and no backprop**. What individuates an object is the
*coupling of distinct modalities through modulation*, not transducer richness
within one — and what *locates* it is the same self/world split (reafference)
the agent already uses to map.

This is the bench's first **mediated-cognition–facing** experiment: the basal
architecture, asked to recognize and to name a where.

## Setup

The same planar mouse (slide-x, slide-y, yaw, a whisker fan, an IMU), facing
one cylindrical object. Each object carries **one feature bit per modality**:

| modality | transducer | the bit |
|---|---|---|
| **touch** | whisker fan (rangefinders) | object **angular extent** — a big object subtends more whiskers (`big` vs `small` radius) |
| **vision** | `vision.EyeCamera` (rendered) | object **luminance** — `light` vs `dark` rgba, read as patch tokens |
| **taste** | analytic chemical field | the **sign** of a Gaussian source at the object — `sweet` vs `bitter` |

Three bits → **8 object types**, placed at distinct bearings so localization
also exercises body geometry (left / right / front).

The independent variable is the **cross-modal board** (`control.CrossModalBoard`)
— the balance beam for this experiment. It (a) **modulates**: gates each
reading against a per-modality floor, so only a reading that breaks the floor
flows; and (b) **couples**: concatenates the resolved bits into a single object
code. Its two knobs are `coupled` (which modalities are wired in) and
`modulate` (whether the gate is active).

The visual channel is genuinely rendered and pooled into `VPATCH × VPATCH`
luminance tokens (resolution = token/CAZ density, **not** pixel count). It is
surfaced by **reafference**: at closest approach the agent makes a small forward
probe; its rotation-only forward model (`AnalyticalFramePredictor`) predicts no
image shift from pure translation, so the residual between the actual and
predicted view is the object's unpredicted *looming*, which the
`PatchResidualModulator` gates against its floor (`reafferent_luminance`). The
gated patches locate the object (figure-ground from the agent's own motion); its
albedo is then read at the object body. If the probe surfaces nothing the
channel falls back to a static contrast read (`luminance_from_tokens`), and with
no GL backend to analytic luminance — so the experiment always runs.

The approach itself reuses the bench's locomotion machinery — a `CPG` (basal
action pattern) for thrust and a `DifferentialDrive` that turns (forward, turn)
into a body wrench from the two **located** drive zones — recruited by the
object affordance and halted at contact: **the controller that forages in P2 is
the controller that approaches here.**

Localization places the object in the agent's **dead-reckoned** frame from the
whisker bearing + range. With **reafference on**, self-motion is discounted (the
object holds its true place as the agent approaches); with it **off**, the agent
attributes its own approach to the object and mislocalizes it.

## What it measures

| figure | claim | independent variable | dependent variable |
|---|---|---|---|
| **A — binding** | the object is the cross-modal invariant | modalities *coupled* (and whisker count) | individuable categories |
| **(A) — localization** | locating needs the self/world split | reafference on / off | mean localization error |
| **B — resolution** | resolution is modulation, not sensor count | sensor channels, modulation on / off | discrimination accuracy |
| **C — the foil** | the architecture replaces the corpus | labeled training examples | deep-net vs SMN accuracy |

## Result

```
binding:  coupled=touch              : 2 classes,  bit-acc=1.00
          coupled=touch+vision       : 4 classes,  bit-acc=1.00
          coupled=touch+vision+taste : 8 classes,  bit-acc=1.00
          touch only, 9 whiskers     : 2 classes   (density ≠ modality)
          subsumption, 3 sensors     : 2 classes   (suppression, no binding)

localization:  reafference ON  : mean loc error = 0.10 m
               reafference OFF : mean loc error = 0.40 m

resolution:    N=1  channels : modulation ON 0.65   OFF 0.65
               N=15 channels : modulation ON 0.94   OFF 0.65

foil (same test set):
         deep net, untrained (0 ex) : 0.12   (≈ chance, 1/8)
         deep net,  128 labeled ex  : 0.94
         deep net,  512 labeled ex  : 1.00
         SMN,         0 labeled ex  : 0.96   (net needs ~128 ex to match)
```

- **Binding.** Individuable categories = `2^(modalities coupled)`: 2 → 4 → 8.
  Adding whiskers (touch density) keeps it at 2 — a touch-only agent cannot read
  colour no matter how many whiskers it grows. **Sensors are not modalities.**
- **The subsumption foil (measured).** Give the same body, the same three
  sensors, and the same reactive approach to a `SubsumptionArbiter` — fixed
  priority *suppression* instead of modulation — and it individuates only **2**
  categories. Suppression yields one surviving channel; it never *binds*. The
  ceiling is architectural: **binding requires modulation, not suppression.**
- **Localization.** Reafference off is ~5× worse, and the error is ≈ the
  distance the agent travelled — the signature of attributing self-motion to the
  world.
- **Resolution.** With modulation, accuracy rises as the sensor channels are
  integrated (`σ/√N`); without it, the ungated extras are dropped and more
  sensors do nothing — flat. The rise is bought by the modulatory architecture,
  not by raw transducer count.
- **The foil (same test set).** On the identical generative test set, an
  untrained net on the raw stream sits at chance and SMN's fixed architecture
  scores 0.96 with **zero** labeled examples; a trained net needs ~128 examples
  just to match it. At the same zero corpus the deep net is at chance and SMN is
  near-perfect — the architecture is the entire difference. (With more data the
  net edges slightly past SMN's un-tuned thresholds — fair, and beside the
  point: SMN paid no corpus.)

[![Binding (categories = 2^modalities coupled; neither more whiskers nor suppression adds categories), localization needs the self/world split, and the 8-object scene](../figures/p3_crossmodal_discrimination.png)](../figures/p3_crossmodal_discrimination.png)

[![Resolution scales with modulation, not sensor count: with modulation accuracy rises with channel count, without it stays flat](../figures/p3_resolution_principle.png)](../figures/p3_resolution_principle.png)

[![The foil: a deep net needs ~128 labeled examples to reach what the SMN architecture achieves with none; untrained, it sits at chance](../figures/p3_deepnet_foil.png)](../figures/p3_deepnet_foil.png)

## What this experiment shows

- **Recognition is not a separate competence.** The same located, opponent
  zones — same module types as the foraging experiments, zero new primitives —
  discriminate an object. The recognized category *is* the equivalence class of
  scenes that drive the same coupled code.
- **The object is a cross-modal invariant.** It becomes determinate where
  distinct modalities, coupled through modulation, agree. One modality collapses
  the set 4-fold; coupling individuates.
- **Resolution is architectural.** More of the same transducer buys nothing
  without modulation to integrate it — the prediction an ML reviewer would bet
  against, and the one this bench was built to make.
- **The architecture stands in for the corpus.** What a deep net must learn from
  a labeled dataset, the SMN structure supplies as a prior — embodied,
  unsupervised, in a single lifetime.

It does **not** yet show:

- **Naming.** Mapping the object code to an utterance is another modulatory
  coupling, but naming is conventional and social — it needs at least a dyad
  (M2 territory), so it is deliberately out of scope here.
- **Free-foraging discrimination.** The approach is affordance-driven and uses
  the bench's locomotion (CPG + differential drive), but the *encounter* is
  staged one object at a time for a controlled read, not discovered during open
  exploration.
- **A full reafference forward model.** The looming gate uses the rotation-only
  predictor, so it surfaces the object from self-caused translation it cannot
  predict — figure-ground from motion, not yet a model that predicts looming too.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus:

- A **taste** modality: an analytic Gaussian chemical field sampled at the
  agent's position (it must approach to taste), not a contact sense.
- A **rendered visual bit**: object luminance read from `EyeCamera` patch tokens,
  surfaced by the reafference/looming gate (`reafferent_luminance`) under flat
  lighting + gray skybox (added to `build_p3_xml`); the whisker channel is
  colour-blind and unaffected by these scene changes.
- An **affordance-recruited approach**: the agent is drawn to the object and
  reads at closest approach, driven by the bench's own `CPG` + `DifferentialDrive`
  — active perception with the foraging locomotion, the encounter staged per
  object for a controlled read.

## Why this experiment is in the bench

It is where the bench turns from *building a world* to *recognizing things in
it* — the hinge from the unmediated agent (M1) toward mediated cognition (M2) —
and it makes the framework's most contestable prediction concrete and
falsifiable: **recognition scales with modulatory architecture, not with sensor
richness or with a labeled corpus.** It also stakes out the comparison ground:
SMN keeps the no-dataset, embodied commitment of Brooks' subsumption — measured
here by a `SubsumptionArbiter` that, with the same body, the same three sensors,
and the same reactive approach, individuates only 2 categories — while adding
the modulation that *binds* them and the constructed, body-relative snapshot
that *locates* them. That is the bridge subsumption lacked: it can approach an
object it can neither individuate nor place.

Natural next steps:

1. **Free-foraging discrimination** — let the agent discover and recognize
   objects during open exploration, rather than one staged encounter at a time.
2. **A predictive forward model** — extend reafference to predict looming from
   known forward motion, separating self-caused looming from world motion.
3. **Toward naming** — a second agent and a shared coupling (M2).

## Run it

```bash
cd experiments && ../.venv/bin/python p3_crossmodal_discrimination.py
```

Outputs: `figures/p3_crossmodal_discrimination.png`,
`figures/p3_resolution_principle.png`, `figures/p3_deepnet_foil.png`.
The visual channel renders when a GL backend is present (the console prints
`[vision] rendered path active`) and falls back to analytic luminance otherwise.
Runtime: ~1–2 min on a laptop CPU.

To **watch** the agent approach and read objects in a live MuJoCo window (on a
machine with a display):

```bash
cd experiments && ../.venv/bin/python p3_crossmodal_discrimination.py --watch
```

This opens the interactive viewer for a few objects in turn (close the window to
advance). It does not write figures; it is for seeing the embodied approach. The
batch run above is offscreen — it needs a GL backend but no on-screen window.
