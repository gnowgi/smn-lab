# The balance-beam sweep

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **C-series** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [Lesson 1](../lesson1.md).


## Question
Does the structure of the modulatory coupling and the body geometry determine the
structure of the world the agent can build?

## Setup
Each condition runs the [self-localized mapper](p2_world_model.md) under a
different "balance beam", varying **both**:

- **(a) information-routing topology** — how whisker affordances are routed into
  the steering command: `flat`/distributed (all whiskers pooled at once) vs
  `hierarchical`/layered (whisker groups summarized, then combined),
  via `HAPExplorer(routing=...)`;
- **(b) physical body geometry** — whisker count (3 / 5 / 9) and drive-zone track
  width (narrow / wide), via `MouseSchema`;

plus the architectural toggles **±BAP** (the locomotor drive) and **±HAP** (the
affordance-recruited haltable action), and **proprioceptive noise**.

## Conditions (9)
full · hierarchical routing · sparse (3w) · dense (9w) · narrow track · wide
track · −BAP · −HAP · noisy proprioception.

## Run
```bash
cd experiments && ../.venv/bin/python p2_topology_sweep.py
```

## Outputs
- `figures/p2_topology_sweep.png` — a 3×3 grid of the constructed maps.
- `data/sweep_results.csv` — coverage, precision, drift, and parameters per
  condition; per-condition `data/sweep_*.npz` (hit clouds + trajectories). The
  full data is gitignored; a curated copy is in [`samples/`](../assumptions.md).

## Findings

![Balance-beam sweep — a 3×3 grid of constructed maps across routing × morphology × ±BAP/±HAP × proprioceptive noise](../figures/p2_topology_sweep.png)

*A 3×3 grid of constructed maps across the swept conditions. The columns and
rows that build a faithful map are immediately visible; the ones that collapse
it (no BAP, no HAP, heavy proprioceptive noise) are equally visible.*

- **±BAP / ±HAP are decisive.** Removing the basal drive (−BAP) collapses
  coverage to ~20% (no locomotion → it maps only a sliver); removing the haltable
  affordance-action (−HAP) drops it to ~44% (drives into a wall and stalls).
  **Both modulatory layers are necessary to build a world model** — "no
  modulation → no learning."
- **Self-localization quality gates fidelity.** Noisy proprioception keeps
  coverage but drops precision (100% → 74%) with ~6.7 cm drift: the snapshot
  smears.
- **Routing and morphology are robust here** (~96–97% across flat/hierarchical,
  3/5/9 whiskers, narrow/wide track) — the arena is easy enough that the
  architecture is forgiving. Harder tasks (sparser sensing, a maze, faster
  motion) would separate these axes; that knob is built in.

!!! warning "Mixed-ablation panel, not topology isolation"
    These conditions vary routing, morphology, ±BAP/±HAP, and noise *together*, so
    this is an ablation **panel**, not a clean test of coupling topology with body,
    world, and task held fixed. Treat the topology contrast as suggestive.
    Isolating coupling topology as a single independent variable is a C-series
    target.
