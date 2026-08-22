# Two networks are forced — a double dissociation

!!! abstract "The claim"
    An SMN agent needs **two** networks, not one, and they cannot be the same medium.
    A **damped, differentiating** net can build the body's geometry but keeps
    information local. A **non-decremental, integrating** net can make a fact available
    to the whole body but cannot build geometry. Neither can do the other's job — so
    both are required. This page shows that as a clean 2×2.

## Why this experiment exists

[Hydra](hydra.md) hands us the puzzle directly. Its passive mechanical tissue recovers
the whole body at 0.99 and localizes a touch at 1.00 — but the *location* of that touch
fades as it travels across the body (0.28 → 0.16 → 0.11). Localization is excellent;
global availability is weak. That gap is the question: is one network enough, with the
attenuation just a nuisance — or is the attenuation itself telling us a **second**
network is needed?

The answer is the second one, and the attenuation is not a nuisance — it is the
**signature** of the network that builds geometry.

## The two properties, and the two media

The experiment puts the *same* body under two ways of moving a local touch around, and
scores each on two order parameters:

- **geometry** — can you recover the body's connectivity graph from how it moves?
  (self-model recovery, higher is better; chance ≈ 0.04 for this body)
- **global snapshot** — does a far zone receive as much of a local touch as a near one?
  (far/near ratio; 1.00 = uniformly available, → 0 = decremental)

| network | geometry (differentiation) | global snapshot (integration) |
|---|---|---|
| **damped mechanical** (the DFN) | **0.99** | far/near = **0.02** (decremental) |
| **integrating** (the IN board) | **0.04** (≈ chance) | far/near = **1.00** (uniform) |

![The two-network double dissociation — damped net builds geometry but stays local; integrating net broadcasts but cannot build geometry](../figures/two_networks_dissociation.png)

Read the diagonal against the off-diagonal and the dissociation is complete:

- The **damped** net **builds geometry (0.99)** but **stays local (0.02)**: what a far
  zone feels of a local touch is almost nothing, because attenuation is exactly what
  encodes *how far apart* two zones are. **Attenuation is the self-model's signal.**
- The **integrating** net makes the snapshot **available to all (1.00)** but **cannot
  build geometry (0.04, ≈ chance)**: because it does *not* attenuate, it carries no
  information about distance. **Non-decrement is the snapshot's signal.**

A single medium cannot be both decremental (to encode geometry) and non-decremental (to
broadcast uniformly) at the same time. So **two networks are forced.**

To make the contrast concrete: what a far zone actually receives of a local touch is
**0.02** through its own mechanics versus **0.05** through the IN board — about **3×**
more via the broadcasting net, and flat with distance rather than fading.

![The self/world card for the damped net — clean geometry recovered](../figures/dissoc_damped_self_world_card.png)
*The damped/differentiating net recovers the body cleanly (0.99).*

![The self/world card for the integrating net — geometry collapses to chance](../figures/dissoc_integrated_self_world_card.png)
*The integrating net cannot recover geometry — every zone looks equidistant, so the graph collapses to chance (0.04).*

## The architectural reading (and a correction)

The two networks map onto the SMN's two kinds of "oneness": the **unity of the picture**
(the IN's globally-available snapshot) and the **unity of action** (the DFN's body acting
as one).

!!! warning "Coordination is the DFN's job, not the IN's"
    A natural misreading is that the broadcasting net *coordinates* the body. It does
    not. **Coordination happens in the differentiated net**, through opposing zones
    acting **locally** with **no central control**. The **IN only integrates a
    globally-available snapshot — it cannot command or control.** This experiment is
    careful about that line: it measures *differentiation* (geometry) versus
    *integration* (snapshot), and does **not** measure coordination, which lives in the
    DFN's opposing zones. The [Hydra capture reflex](hydra.md#stage-2-the-whole-net-capture-reflex-with-no-controller)
    is where coordination is demonstrated — local links reading one shared snapshot,
    nobody commanding.

## Run it

```bash
cd experiments && ../.venv/bin/python two_networks_dissociation.py
```

Source:
[`two_networks_dissociation.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/two_networks_dissociation.py).
The architectural constraints are written up alongside the [Hydra](hydra.md) programme;
both self/world cards are generated through the one [results module](../results-module.md).
