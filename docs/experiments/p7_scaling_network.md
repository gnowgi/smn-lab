# E4 — Objecthood as composition; the world model scales with the network

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **C-series** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [Lesson 1](../lesson1.md).


`experiments/p7_scaling_network.py`

This is the clinching result of the manipulator series. [E1](p4_manipulator_objecthood.md)
showed a single zone registering one **difference** (a differentia). But a
difference is not an object. An **object is a composition of differentiae**, and
composition requires the zones to be **coupled** — a *network*. This experiment
makes that thesis precise and falsifiable: **scaling the modulation network is
scaling the world model.**

It also answers the obvious objection — *where is the network?* The body **is** the
network of zones, and the world it can construct grows with it.

## Setup

A row of *K* pull-only antagonist **press pads** (zones) presses on *K* facets of
an object. Each facet is **hard** (welded) or **soft** (spring-backed), and each
pad reads that facet's resistance differentia exactly as in E1 (contact impulse,
hard vs soft). The **board** composes the *bound* zones' differentiae into a single
object code.

The independent variable is **how many zones the network binds** (K = 1…5); the
dependent variable is the agent's **world-model capacity** — the number of objects
it can individuate — read off real multi-zone presses. The contrast is **bound**
(the board couples all K zones) vs **unbound** (zones present but not coupled — only
a single difference survives).

## What it measures

| panel | claim | independent variable | dependent variable |
|---|---|---|---|
| **A — scaling** | the world model grows 2^K with the bound network, not the sensor count | zones bound (K), bound vs unbound | individuable objects (log₂) |
| **B — fidelity** | every composed object is read correctly from real presses | network size K | per-object read accuracy |

## Result

```
=== E4 — the world model scales with the network of zones ===
  per-zone differentia: hard impulse=3.83  soft impulse=2.08  threshold=2.96

  K=1: networked capacity=  2 (2^K=2)   unbound=2  per-object read acc=1.00
  K=2: networked capacity=  4 (2^K=4)   unbound=2  per-object read acc=1.00
  K=3: networked capacity=  8 (2^K=8)   unbound=2  per-object read acc=1.00
  K=4: networked capacity= 16 (2^K=16)  unbound=2  per-object read acc=1.00
  K=5: networked capacity= 32 (2^K=32)  unbound=2  per-object read acc=1.00
```

- **Capacity scales as 2^K with the bound network:** 2, 4, 8, 16, 32 individuable
  objects for K = 1…5 — a clean scaling law, log₂(capacity) = (bound zones).
- **Every composed object is read correctly** from real multi-zone presses
  (per-object accuracy 1.00 across all 62 objects; per-zone hard impulse 3.83 vs
  soft 2.08, cleanly separated by the threshold).
- **Unbound zones add nothing.** Zones present but not coupled give only a single
  difference — capacity 2, flat — no matter how many there are. **The world model is
  built by the network, not by the sensor count.**

[![The world model scales with the network of zones: capacity grows 2^K with the coupled network while unbound zones give only a single difference (capacity 2, flat); each composed object is read correctly from real per-zone presses](../figures/p7_scaling_network.png)](../figures/p7_scaling_network.png)

## What this experiment shows

- **An object is a composition of differentiae.** What a single zone cannot do —
  individuate more than two things — a *coupled* network of zones does, and exactly
  to the degree it is coupled.
- **Scaling modulation is scaling the world.** The agent's grip on its world grows
  with the network that binds its zones, not with raw transducer count — the
  series' central, contestable prediction, here measured against real presses.
- **The continuum is not pixelated.** The BAPG floor fills the spaces *between* the
  discrete differentiae, so the constructed world is a smooth dynamical manifold,
  not a pixel grid.

It does **not** yet show:

- **When the binding happens.** The *onset* of objecthood as the coupling density
  rises — a percolation-like transition — is [E4b](p8_objecthood_transition.md).
- **Structured boards.** This uses a fully-bound board; how modular, hierarchical,
  or scale-free coupling shifts the picture is an open question.
- **Naming.** A shared symbol for the composed object is conventional and social,
  and lies beyond a single agent (M2 territory).

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus:

- A **row of K press pads** — pull-only antagonist prismatic zones — over K facets,
  each facet hard (welded) or soft (spring-backed); the per-zone read is the same
  resistance differentia as E1.
- A **board** that composes the *bound* zones into one object code; the
  bound-vs-unbound contrast is the experiment's whole lever.
- The note that the `2^K` law, once each facet is one clean bit, is true *by
  construction*; the non-trivial content is the **dissociation** — capacity tracks
  the bound network, not the sensor count — and a real multi-zone body reading 62
  objects without error.

## Why this experiment is in the bench

It is where the bench states its strongest claim as a measured scaling law: the
world an agent can have is set by the network its body binds. It reframes the agent
as a **complex network** and opens the physics questions E4b begins to ask.

## Run it

```bash
cd experiments && ../.venv/bin/python p7_scaling_network.py
```

Outputs: `figures/p7_scaling_network.png`. Runtime: ~1 min on a laptop CPU (it
runs real multi-pad presses for every object up to K = 5; no rendering).
