# P2 — Basal coupling: why a cognizing agent moves

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **C-series** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [Lesson 1](../lesson1.md).


`experiments/p2_basal_coupling.py`

The first telling simulation of the bench. The previous P2 experiments asked
*can the agent build a faithful picture of its world?*; this one asks the prior
question: **why does it move at all?**

The answer is constructive, not designed. Movement is encoded as a biological
necessity, and the cognitive substrate (the living-snapshot map) is what closes
the loop:

> The BAP needs energy. Energy depletes with movement. Energy is replenished
> only by food, which is in the world. The map of the world fades where it is
> not revisited. So — no movement, no live map; no food, no energy; no energy,
> no BAP; no BAP, no movement.

The same closed loop, taken through the body, is **why** an organism moves and
**why** the cognitive substrate is inseparable from biology. The simulation lets
the loop run and watches what happens.

## Setup

Same body, balance beam, locomotion, dead-reckoning, and living-snapshot map as
[P2 — living snapshot](p2_living_snapshot.md). New is a **biological state** the
agent carries:

| variable | role |
|---|---|
| `energy ∈ [0, 100]` | a single scalar reserve |
| `E_basal = 0.5/s` | drain at rest (a baseline metabolism) |
| `E_move = 1.5/s · |drive|` | additional drain proportional to BAP output |
| `E_food = 25` | gain on body contact with a food item |
| `E_crit_low = 5`, `E_crit_hi = 20` | BAP weakens linearly between these; fails at or below 5 |

The BAP drive itself is gated by the reserve — `forward = bap·gate·energy_gate(E)`
— so as energy falls toward the floor, the drive smoothly weakens and the agent
stops. At `E = 0` the gate is zero and the agent halts permanently: **death**.

Food is eight point items scattered through the arena, **not in the MJCF model**.
They are tracked in Python and consumed on body contact (distance < `R_eat = 0.13`
m). A consumed item regrows at its source after `T_regrow = 30 s` — the world is
an *ecosystem*, not a larder. The map decays at `0.1/s` (a moderate living snapshot).

## Conditions

| condition | what differs |
|---|---|
| **A — no food** | the world has no food items |
| **B — with food** | eight food items, regrowing 30 s after consumption |

Everything else is held fixed (same seed, same body, same arena, same map decay).
The only thing that changes is whether the world offers nourishment.

## Result

```
no food  : died at t = 119.5 s   (final energy = 0)
with food: alive,  consumption events = 19,  final energy = 98.7
```

The contrast is the experiment's whole point:

- **A — no food.** Energy decays monotonically; the BAP gate falls below 1 around
  E ≤ 20 and the agent slows; it dies at **t ≈ 120 s**. The map it built is
  sparse — it never circulated long enough to develop one.
- **B — with food + regrowth.** Energy traces a characteristic sawtooth — drain,
  contact, refill near `E_max`, drain — and the agent is alive at `t = 180 s`
  with 19 consumption events. The same body, kept alive long enough, produces a
  visibly richer live map of the arena.

![Basal coupling — no food (dies at ~120 s) vs with food + regrowth (alive at 180 s); trajectory + live map on top, energy time-series with consumption and death markers on the bottom](../figures/p2_basal_coupling.png)

*Top row per condition: trajectory + arena + food (green = available, gray × =
eaten) + live map. Bottom row: energy time-series with consumption (green) and
death (red) markers. Same agent in both columns — only the world differs.*

The map quality in the **with-food** panel is not a separate finding — it is
the *same* finding seen from the cognitive side. The agent has a more developed
picture of its world because it stayed alive long enough to keep moving.
Cognition is sustained by biology; biology is sustained by what cognition makes
findable. This is what "basal coupling" names.

## What this experiment says (and does not)

It **does** say:

- A minimal cognizing agent built from the SMN primitives stays alive only
  because the loop closes through the body and through the world. Remove any
  link (BAP, energy, food, movement) and the loop opens — and the agent dies.
- The cognitive substrate (the living-snapshot map) is not optional decoration
  on top of biology. In B, it is built precisely because the agent could afford
  to keep moving; in A, it cannot be built because the agent runs out before
  it can map.

It **does not** say:

- That the agent is *navigating* to remembered food. In this experiment, food
  acquisition is by random body contact during the exploration the HAP drives
  (it follows open whiskers and avoids walls). The next refinement is to let
  the HAP read the live map and steer toward remembered food — at which point
  map decay becomes a direct survival pressure, not only a perceptual one.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold (planar rigid-body world; rangefinder
"whiskers"; etc.). This experiment **adds** these idealizations:

- The agent carries a single scalar **energy reserve**, depleted by drive and a
  basal cost and replenished only by food contact.
- The **BAP is energy-gated** by a piecewise-linear ramp `[5, 20]`; at zero the
  drive is zero ("death") and is irreversible within a run.
- **Food** is a list of point items in Python state (not MJCF geoms); consumption
  is a body-frame proximity check. Each item **regrows** at its source after
  a fixed delay (`T_regrow = 30 s`) — the simplest model of a renewable resource.
- The map is a **living snapshot** (decay 0.1/s) as in
  [P2 — living snapshot](p2_living_snapshot.md).

What is **not** modelled: an explicit metabolism for cognition (the map decay
plays the role of biological "forgetting" but is not energetically costed); food
appearance/odour cues at distance; HAP-level food-seeking.

## Why this is in the bench

This is the experiment a phenomenologist or a biologist would ask for first.
The previous P2 experiments asked the modeller's question — *what does the
constructed picture look like?* This one asks the agent's question — *why are
you moving in the first place?* — and answers it by letting the bench run the
coupled loop. Subsequent experiments can then perturb pieces of the loop
(starve the world; raise the map's decay rate; ablate the HAP) and ask which
breakage kills the agent first — turning the coupling into a quantitative
landscape of viability.

## Run it

```bash
cd experiments && ../.venv/bin/python p2_basal_coupling.py
```

Outputs: `figures/p2_basal_coupling.png`. Runtime: ~25 s on a laptop CPU.
