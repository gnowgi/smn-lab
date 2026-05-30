# P1 — a multi-CAZ agent builds a world model

## What it shows
A mobile "mouse" with a steering CAZ and a whisker fan explores an arena and
**constructs a map** of it ("the picture") from its pose and whisker readings.

## Setup
A planar agent (`slide_x`, `slide_y`, `yaw`) with a five-whisker rangefinder fan.
Steering is an **opponent yaw pair** (two MuJoCo motors); forward locomotion is a
**central body-frame thrust** applied via `xfrc`. A `CPG` (BAP) provides the
drive; a `HAPExplorer` (HAP) steers toward open space and rotates when blocked.
Each whisker hit is placed in world coordinates and accumulated in an
`OccupancyMap`.

## Assumptions specific to P1
(in addition to the [common assumptions](../assumptions.md))
- **The map is built from the simulator's *true* pose (god's-eye).** This is the
  first cut; it is *not* the agent's own self-knowledge. See [P2](p2_world_model.md),
  which removes this assumption.
- Locomotion is a **central thrust** (not located drive zones).
- The occupancy map is a monotonic accumulator (no decay).

## Run
```bash
cd experiments && ../.venv/bin/python p1_world_model.py
```

## Outputs
- `figures/p1_world_model.png` — true arena outline, exploration path, constructed
  point cloud, and coverage/precision.

## Result & interpretation

![P1 world model — exploration path, constructed hit cloud, and the coverage/precision summary](../figures/p1_world_model.png)

*Arena outline, exploration trajectory, the constructed hit cloud against the
true surfaces, and the coverage/precision numbers. The walls and both objects
are recovered at ~97% coverage and ~99% precision.*

The agent reconstructs the walls and both objects at ~97% coverage, ~99%
precision. Because the map uses the true pose, the reconstruction is essentially
the upper bound — which is exactly why P2 rebuilds it from the agent's own
self-localization, so the constructed world model is genuinely the agent's
*construction* (and so the [sweep](p2_topology_sweep.md) is meaningful).
