# P2 — a body-relative, self-localized world model

## What it shows
The world model built **in relation to the body geometry** and from the agent's
**own proprioception** — no god's-eye pose anywhere. This is the honest substrate
the [balance-beam sweep](p2_topology_sweep.md) needs.

## Setup
The agent is built from an explicit **body schema** (`MouseSchema`): the single
source of truth for every zone's body-frame location, used both to build the
MuJoCo body and as the agent's self-knowledge.

- **Locomotion from two located drive zones** (`drive_L`, `drive_R`), each an
  **opponent pair** (signed net activation). `DifferentialDrive` turns
  (forward, turn) into their activations and computes the net force **and torque
  from their positions** — forward = both, turn = differential, and in-place
  rotation is possible because the zones are antagonistic.
- **Self-localization** (`DeadReckoner`): the agent integrates the body-frame
  linear velocity (`velocimeter`) and yaw rate (`gyro`) it senses into a pose
  estimate. It never reads its absolute pose.
- Each whisker hit is placed from the **estimated** pose ⊕ the whisker's known
  body-frame position/angle ⊕ the measured distance.

## Assumptions specific to P2
(in addition to the [common assumptions](../assumptions.md))
- Locomotion is a **computed wrench** from the located zones (no simulated limbs).
- Proprioception is idealized (true velocity); add noise to study drift.
- The map is a monotonic accumulator (no decay).

## Run
```bash
cd experiments && ../.venv/bin/python p2_world_model.py
```

## Outputs
- `figures/p2_world_model.png` — true vs self-estimated path, the self-localized
  map, and coverage / precision / dead-reckoning drift.
- `data/p2_world_model.npz` — hit cloud + trajectories (gitignored; see
  [Assumptions §data](../assumptions.md)).

## Result & interpretation

![P2 self-localized world model — true vs self-estimated path, the constructed map, and the coverage / precision / drift summary](../figures/p2_world_model.png)

*True vs self-estimated trajectory, the world model built from the agent's
proprioceptive self-localization (no god's-eye pose), and the coverage /
precision / dead-reckoning drift summary.*

~97% coverage, ~100% precision, ~0.2 cm drift — the self-estimated path overlies
the true path and the map is faithful, built entirely from the agent's body
geometry + self-motion sense. With clean proprioception the result approaches P1;
the value is that it is now the agent's *own* construction.
