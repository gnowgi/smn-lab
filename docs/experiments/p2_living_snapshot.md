# The living snapshot — map decay

## What it shows
The world model as a **dynamic equilibrium** between mapping and forgetting,
rather than a monotonic record. With a positive decay rate the held map fades
where it is not revisited; **how much of the world the agent can hold at once
depends on the balance between decay and revisit**.

## Setup
The P2 self-localized mapper, with `OccupancyMap(decay=d)`: each cell's evidence
decays each timestep (`grid *= exp(-d·dt)`); a whisker hit reinforces (+1,
saturated at `cap`); the **live map** is the cells whose evidence exceeds
`thresh = 0.5`. Two runs:

- a **time-lapse** at `decay = 0.4/s`, recording the live map at four moments
  during a 120 s exploration;
- a **decay-rate sweep** over `decay ∈ {0, 0.05, 0.1, 0.2, 0.4, 0.8}/s`,
  measuring the live coverage of the full arena at the end of each run.

## Assumptions specific to this experiment
(in addition to the [common](../assumptions.md) and [P2](p2_world_model.md) sets)

- The occupancy map is **no longer monotonic**: cells lose evidence as
  `exp(-d·dt)` between hits.
- A live-cell threshold (`0.5`) with reinforcement cap (`5.0`) defines the
  "held" map. These knobs are configurable.

## Run
```bash
cd experiments && ../.venv/bin/python p2_living_snapshot.py
```

## Outputs
- `figures/p2_living_snapshot.png` — time-lapse (top) and decay-vs-coverage
  curve (bottom).
- printed summary.

## Result & interpretation

![Living snapshot — time-lapse of the live map at decay 0.4/s and the decay-vs-coverage curve](../figures/p2_living_snapshot.png)

*Top: a time-lapse of the live map at decay 0.4 / s — a moving local snapshot
that trails the agent and fades behind it. Bottom: live coverage of the full
arena as a function of decay rate, falling from 99 % (accumulator) to 37 % at
0.8 / s.*

At `decay = 0` the map holds the full arena (~99 %). At `0.05/s` it still does
(half-life ≫ revisit period). From `0.1/s` onwards coverage falls; by `0.8/s`
only ~37 % is held at a time — the map becomes a **moving local snapshot** that
trails the agent and fades behind it. "The snapshot is always already becoming a
different snapshot" turned into a measurable quantity.

| decay (1/s) | half-life | live coverage |
|---:|---:|---:|
| 0.00 | ∞ | 99 % |
| 0.05 | 13.9 s | 99 % |
| 0.10 | 6.9 s | 91 % |
| 0.20 | 3.5 s | 73 % |
| 0.40 | 1.7 s | 52 % |
| 0.80 | 0.9 s | 37 % |
