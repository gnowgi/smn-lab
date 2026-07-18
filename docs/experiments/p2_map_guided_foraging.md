# P2 — Map-guided foraging (the map's decay as survival pressure)

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **progression** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [The Construction of Experience](../construction-of-experience.md).


`experiments/p2_map_guided_foraging.py`

In [Basal coupling](p2_basal_coupling.md) the agent's HAP read whisker
affordances only; food was found by the chance that wall-following crossed
it. The map of the world existed, but the agent did not *act on it* — it was
a picture for the modeller, not yet a tool for the agent.

This experiment closes that gap. The HAP now reads a second living-snapshot
layer — a **food memory** — in which each consumption deposits a fading marker
at the agent's dead-reckoned position. When the forward path is clear of walls
and the food memory holds a live point in recall range, the HAP biases the
turn toward the closest one. The map becomes *for something the agent needs*.

That turns the map's decay rate into a direct survival pressure: forget too
fast → can't return to known food → starve under the same world.

## Setup

Same body, balance beam, dead-reckoner, and living-snapshot wall map as
[Basal coupling](p2_basal_coupling.md). Added:

| component | role |
|---|---|
| `food_map` | a second `OccupancyMap` (its own decay rate, cap 3.0); consumption events deposit 2 hits at the **dead-reckoned position**, not the food's true coordinates |
| recall steering | when `gate == 1` (path clear) and any live food-memory cell lies within `[0.20, 2.0] m`, turn := `clip(2.0 · angular_error)` toward the closest one |

Steering yields to wall avoidance whenever the HAP's standard `(turn, gate)`
asks for in-place rotation. The food memory does not override survival reflex.

The arena is **harsher than basal coupling** to make memory matter:

- **4 food items, mixed**: 2 perimeter (`(0.8, 0.9)`, `(-0.9, 0.7)` — a wall-follower will find them) and 2 interior (`(0.3, 0.2)`, `(-0.4, -0.3)` — only a remembering agent comes back).
- **Slow regrowth**: `T_regrow = 90 s`.
- **Long horizon**: `T_end = 300 s` (≈ 1.7× basal coupling).
- **Slightly richer food**: `E_food = 32` (the basal coupling used 25; the foraging
  task is harder, so each meal is worth more).

## Conditions

| | map use | food-memory decay | half-life |
|---|---|---|---|
| **C1 random** | none | — | — (baseline) |
| **C2 map-guided, slow** | yes | 0.02 / s | ≈ 35 s |
| **C3 map-guided, fast** | yes | 1.00 / s | ≈ 0.7 s |

Everything else is identical (seed, body, biology, walls, food positions).

## Result

```
C1 random (no map guidance)        : died at t = 271.7 s,  events = 5,  mean E = 45,  guided =  0.0%
C2 map-guided, slow decay (0.02/s) : alive at t = 300.0 s, events = 8,  mean E = 60,  guided = 21.3%
C3 map-guided, fast decay (1.0/s)  : died at t = 175.1 s,  events = 3,  mean E = 28,  guided =  0.3%
```

Three-way ordering, with the slow-memory agent the only survivor.

- **C1 random** dies at 272 s. The wall-following HAP visits the two
  perimeter foods reliably but never finds the interior ones — and two
  perimeter foods on a 90 s regrowth do not yield enough energy to cover the
  300 s horizon.
- **C2 map-guided, slow** is alive at the end with 60% more consumption events
  than C1 (8 vs 5) and a mean energy 30% higher. The 21% of timesteps where
  the food memory steered the turn are concentrated near the interior
  locations the random forager never reaches.
- **C3 map-guided, fast** dies *earlier* than C1 (175 s vs 272 s). Fast decay
  is not merely useless — it is **misleading**: in the ~1 s window after a
  consumption the memory still pulls the agent back toward the just-eaten
  spot, where food will not regrow for another 90 s. The agent oscillates
  near recently-emptied spots, wastes energy, and dies sooner than the
  unguided baseline.

![Map-guided foraging — three-way contrast: random dies at 272 s, slow-decay alive at 300 s, fast-decay dies earlier than random at 175 s](../figures/p2_map_guided_foraging.png)

*Top row per condition: trajectory + wall live map (red) + **food memory live
points (orange squares)** + food (green = available, gray × = eaten). Bottom
row: energy time-series with consumption (green) and death (red) markers. Only
the slow-decay agent reaches the horizon alive; fast decay dies earlier than
the no-map baseline.*

## What this experiment shows

It demonstrates the central claim from [Basal coupling](p2_basal_coupling.md)
made *quantitative*:

- The **same parameter** that controls the cognitive substrate's perceptual
  fidelity (the living snapshot's decay rate) also controls **survival**. Slow
  decay → alive; fast decay → dead-sooner-than-no-map.
- Cognition does not sit on top of biology as a separable competence. The map
  is *for* finding food, food is *for* keeping the BAP alive, the BAP is *for*
  movement, and movement is *for* keeping the map. Sever any link — including
  by making the map fade too fast — and the loop opens.
- "Forgetting" is not neutral. *Some* decay is needed (otherwise the map
  hallucinates food at spots that have been emptied), but *too much* turns a
  reliable cognitive substrate into a misleading one. The optimum is set by
  the world's regrowth period — a property of the habitat, not of the agent.

It does **not** yet show:

- Quantitative robustness across seeds and parameter ranges (this is a single
  illustrative seed; the next refinement is a viability landscape sweep).
- Adaptive decay: the agent does not learn the world's regrowth period from
  experience. The decay rate is set, not discovered.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus the
[Basal coupling](p2_basal_coupling.md) biological state (energy reserve,
energy-gated BAP, food as Python-tracked point items with regrowth). New:

- A **food memory** living-snapshot layer (its own `OccupancyMap`), with its
  own decay rate, populated by consumption events (not by distance sensing).
- The deposit is at the agent's **dead-reckoned position**, not the food's
  true coordinates — the memory lives in the agent's self-localized frame, so
  drift in dead-reckoning shifts the memory the same way it shifts the wall
  map. (See [P2 self-localized](p2_world_model.md) for the drift budget.)
- A **layered HAP**: wall affordance > food memory > wander. Food-seeking is
  only invoked when the wall reflex is satisfied.

What is **not** added: distance sensing of food (the agent does not see food,
it only feels it on contact); adaptive decay; multi-step planning. Each is a
natural follow-up.

## Why this experiment is in the bench

This is the first experiment in which **the cognitive substrate is a survival
organ**, not just a representation. Basal coupling showed that movement
sustains life through food; this one shows that *remembering where food was*
is what makes that sustainability work — and that the *quality* of that
memory (its decay rate) is a measurable survival pressure.

The same setup invites the obvious next sweeps:

1. **Decay × regrowth landscape** — vary `(food_decay, T_regrow)` and trace
   the viability boundary. The optimal decay should track the regrowth
   period (forget exactly when food becomes worth checking again).
2. **HAP ablation under metabolism** — does removing wall affordance, or the
   food-memory steering alone, collapse viability the way removing BAP did
   in the topology sweep?
3. **Adaptive decay** — let the agent infer the regrowth period from
   inter-consumption intervals and adjust its own forgetting rate. A first
   primitive form of learning the habitat's dynamics.

## Run it

```bash
cd experiments && ../.venv/bin/python p2_map_guided_foraging.py
```

Outputs: `figures/p2_map_guided_foraging.png`. Runtime: ~40 s on a laptop CPU.
