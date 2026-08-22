# Hydra — the "hello world" of SMN

!!! tip "New here? Start on this page."
    Hydra is the smallest creature that shows the **whole** SMN argument at once —
    a body that builds a model of itself, senses the world in its own frame, and
    acts on an object — with **no brain, no ganglia, no central controller** to hide
    the work. If you read one experiment first, read this one.

## Why Hydra earns the title

Hydra removes every excuse for a central controller. It has no brain and no ganglia,
it is radially symmetric, and its nervous system is a **diffuse nerve net** spread
through the wall of a two-layer sac. Yet a water-flea brushing a single tentacle
becomes a **whole-animal, object-directed act**: the tentacles converge, the body
wall contracts, and the prey is carried to the mouth. Because there is nowhere for a
controller to sit, *any* coordination Hydra shows is, by construction, a **network
effect** — which is exactly the claim the SMN architecture wants to be load-bearing.

So Hydra is the natural minimal test. If the SMN account is right, we should be able
to build this creature on the bench and watch a coordinated capture **emerge** from
local parts reading a shared picture — with no line of code that plays the role of a
boss.

## The body — a two-layer sac

Hydra is a **diploblast**: two stitched shells (an outer **ectoderm** and an inner
**endoderm**) with a jelly **mesoglea** between them, joined at the oral **rim** that
forms the mouth. The nerve net lives in the mesoglea — radial links that run *through
the wall* connecting the two layers. On the bench this is built by stitching two
nested capped tubes; the rim links close them into one sac.

The distinction matters and is worth stating once:

| body | topology | closure |
|---|---|---|
| **tube** | a single open cylinder | both ends open (no sac) |
| **single-layer sac** | one shell with a foot-apex cap | one closed end (a cup) |
| **diploblast (Hydra)** | **two** shells + mesoglea, joined at the rim | the rim becomes the **mouth** |

![The Hydra sac as a one-page experiment figure — body plan, world, recovered self-model, world-model canvas, and data](../figures/hydra_sac_page.png)
*The whole experiment on one page (the standard [experiment-page template](../results-module.md#the-one-page-experiment-figure-paper-ready)): the two-layer body plan, the world (a moving prey on one ectoderm zone), the self-model recovered from movement, the world-model canvas, and the data.*

## Stage 1 — it recovers its own body, and localizes the touch

Give the sac (62 zones, 151 links, 30 of them radial mesoglea links) nothing but its
own movement to learn from, then touch one ectoderm zone with a prey.

| order parameter | value | meaning |
|---|---|---|
| self-model recovery | **0.99** | the two-layer body graph is recovered from movement alone |
| localization | **1.00** | the touched zone is the peak of the response — the animal knows *where* |

![The Hydra self/world card — the recovered two-layer body graph with the touch localized on it](../figures/hydra_sac_self_world_card.png)

So far, so good: the passive mechanical net (the **DFN** — the differentiating,
damped tissue) both **builds the geometry** and **localizes** the touch. The question
is whether that same passive tissue can also make the touch's location available to
the *whole* animal, so a distant tentacle can act on it.

## The finding that forces a second network

It can — but only **weakly, and with attenuation**. Decoding where the touch landed
from progressively more distant parts of the body:

| decode the touch location from… | skill | vs. shuffle |
|---|---|---|
| the far **outer oral ring** (within the ectoderm) | 0.28 | −0.11 |
| the **gut mouth** (the inner oral ring) | 0.16 | −0.11 |
| the whole **endoderm** (across the mesoglea) | 0.11 | −0.11 |

The location is present everywhere above chance — but the signal **fades with
distance** (0.28 → 0.16 → 0.11). Perfect *localization* does **not** buy strong
*global availability*. Passive mechanics can hold a body's shape and say where it was
touched, but it cannot make that fact equally and immediately knowable across the
whole animal. That is precisely the job of an **active** broadcasting network — the
**IN** (the integrating net) — and this finding is what motivates it.

!!! note "One creature, two networks"
    This is the empirical doorway to the [two-network dissociation](two_networks.md):
    a **damped, differentiating** net builds geometry but stays local; a
    **non-decremental integrating** net makes a snapshot available to all but cannot
    build geometry. One medium cannot be both — so Hydra needs both. Coordination is
    the DFN's job (opposing zones acting locally, no central control); the IN only
    supplies the shared **snapshot** — it cannot command.

## Stage 2 — the whole-net capture reflex, with no controller

Now the pay-off. The IN broadcasts the prey **snapshot** — which zone was touched, and
therefore its graph distance to the mouth `V[k]`, made globally available. Every DFN
link then reads that shared snapshot **plus its own** distance-to-mouth `V`, and acts
**locally**: a link on the mouth-ward side of the prey (`V[a], V[b] ≤ V[k]`) contracts.
There is **no controller** — just a per-link local rule applied to one shared picture.

Object-directedness comes from a **reafference threshold**: the reflex fires only for a
**moving mass above threshold** — a struggling prey produces persistent, world-caused
motion at the contact — and stays silent for a static, weak touch (inert debris).

| stimulus | moving-energy | reflex gate | net recruited | conveyed to mouth |
|---|---|---|---|---|
| **prey** (moving, strong) | 0.498 | **fires** | **54 %** | **81 %** |
| **debris** (static, weak) | 0.047 | silent | 0 % | — |

The supra-threshold prey (caught at a zone three graph-steps from the mouth) fires the
reflex; the whole mouth-ward net recruits and carries the prey **81 %** of the way in
(graph distance 0.51 → 0.10). Inert debris is below threshold and nothing happens.

![The Hydra capture reflex — the mouth-ward net recruits and conveys the prey; inert debris does nothing](../figures/hydra_capture_reflex.png)

The conveyance is a coordinated, object-directed act, and every part of it is produced
by **local links each reading one shared snapshot**. Nobody commands. That is the SMN
claim — demonstrated, not asserted.

![The capture as a sequence of snapshots in time — the prey carried toward the mouth](../figures/hydra_capture_snapshots.png)

## Honest scope

The idealizations are all reasonable for a "hello world", and all declared. The reflex
reads the mouth-ward geometry `V` (a breadth-first distance to the mouth) as the *true*
graph — the same geometry the stage-1 self-model recovers at 0.99, but here taken as
given rather than re-recovered inside the reflex. The gate is a first-cut energy/motion
threshold. Capture reaches 81 %, not 100 %, because the structural springs resist full
collapse. The foot is hard-anchored (Hydra is sessile). None of these change the
result: a coordinated capture with no central control.

## Where it goes next

- Make the reflex read the **recovered** `V` (from the stage-1 self-model) rather than
  the true graph, and add the explicit **IN board** channel (non-decremental) for the
  snapshot.
- Turn the conveyance across zones into the **canvas** recruitment ladder — the
  world-model trajectory on the real sac (see [the canvas](../results-module.md#the-canvas-always-built-from-modulation-not-displacement)).
- A full discrimination curve over (moving vs static) × magnitude.

## Run it

```bash
cd experiments
../.venv/bin/python hydra_sac.py             # stage 1b — the two-layer sac, recovery + localization
../.venv/bin/python hydra_touch_broadcast.py # stage 1 — single-tube broadcast baseline
../.venv/bin/python hydra_capture_reflex.py  # stage 2 — the whole-net capture reflex
../.venv/bin/python hydra_capture_snapshots.py  # the capture as a filmstrip
```

Sources on GitHub:
[`hydra_sac.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/hydra_sac.py) ·
[`hydra_touch_broadcast.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/hydra_touch_broadcast.py) ·
[`hydra_capture_reflex.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/hydra_capture_reflex.py) ·
[`hydra_capture_snapshots.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/hydra_capture_snapshots.py).
Every result is generated through the one [results module](../results-module.md).
