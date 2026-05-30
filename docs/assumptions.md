# Assumptions, and what is derived

Assumptions in this lab are **layered and not fixed**. There is a **common core**
(this page) that holds across experiments, plus **per-experiment specifics** that
add to or override it — because the right assumptions depend on the experimental
setup. Each [experiment page](experiments/p0_reafference.md) states its own
deltas; this page is the shared reference.

Every result traces to one of three things: **(A)** physics the engine
integrates, **(B)** a calculation our control code performs, or **(C)** a
modelling idealization.

## Common assumptions (unless an experiment says otherwise)
- **Planar rigid-body world.** The agent is one rigid body with three DOF
  (`slide_x`, `slide_y`, `yaw`) and viscous damping; MuJoCo integrates the
  dynamics (RK4, dt = 5 ms). No out-of-plane motion (z, roll, pitch); no ground
  friction (frictionless glide, resisted only by joint damping).
- **Whiskers are range sensors, not bristles.** Each is a zero-thickness, rigid,
  **straight rangefinder ray** — unbounded but capped at `MAX_RAY` (4 m). It
  reports **distance to the nearest surface**, not contact or bending along a
  length. No flex, no tactile surface.
- **The world** is a walled arena (plus objects) at body height; rays hit walls
  and objects.
- **Reproducible.** All RNGs are seeded; runs are byte-reproducible.
- **Data is logged every timestep**, whether the agent is moving or not.

## A. Simulated by MuJoCo (derived)
Rigid-body planar dynamics (pose/velocity from integrated forces+damping);
rangefinder distances (raycasts against geoms); proprioception (a `velocimeter`
+ `gyro` giving true body-frame linear velocity and yaw rate).

## B. Computed by our control code (not physics)
The drive **wrench** (net force+torque from the located drive zones' positions);
the **dead-reckoned pose** (integrating proprioception); the **world model** (hit
points placed from estimated pose ⊕ body-schema whisker pose ⊕ measured
distance); the **scores** (coverage/precision as point-based nearest-neighbour
fractions, ε = 6 cm, against ground-truth surface samples).

## C. Idealizations (common)
- Movement is a **computed wrench on a rigid body** — no simulated limbs,
  muscle–tendon units, or ground-contact thrust.
- Whiskers are distal **rays**, not tactile bristles (no flex, no contact).
- Proprioception is idealized (true velocity, optionally + noise); **the SMN
  "balance/co-activation generates data at rest" (Register 1) is not modelled**.
- The occupancy map is a **monotonic accumulator by default**; an optional decay
  rate turns it into a *living snapshot* — see
  [Living snapshot](experiments/p2_living_snapshot.md).

## Per-experiment assumptions (these vary)
| aspect | P0 reafference | P1 world model | P2 self-localized | sweep |
|---|---|---|---|---|
| body | single CAZ "head" | mobile, 5 whiskers | mobile, body schema | varies (3/5/9 whiskers; track width) |
| locomotion | none (head only) | central `xfrc` thrust | **located** opponent drive zones | + `±BAP` toggle |
| steering | opponent yaw (motors) | opponent yaw (motors) | differential located drive | + routing: flat / hierarchical |
| pose for mapping | n/a (heading-keyed) | **true pose (god's-eye)** | **dead-reckoned (proprioception)** | + proprioceptive noise |
| world dynamics | static + scheduled exafference object | static arena | static arena | static arena |
| internal model | binned forward model (range vs heading) | occupancy accumulator | occupancy accumulator | + `±HAP` toggle |

> The P1 → P2 shift is the clearest example that assumptions track the setup: P1
> builds the map from the simulator's true pose; P2 uses only the agent's own
> proprioceptive self-localization. Same task, different assumption — and it
> changes what the experiment can claim.

## D. How the figures are computed
- The result maps (`p0/p1/p2/sweep`) are **matplotlib plots of computed arrays**
  (hit cloud, trajectories, ground-truth outlines, metric text). No physics render.
- `agent_geometry.png` is a **matplotlib schematic** from `MouseSchema`.
- `scene_render.png` is a **real MuJoCo (EGL) rasterization** with the rangefinder
  rays drawn by the visualizer.

## E. Known divergences / refinement backlog
1. Tonic / co-activation data at rest (Register 1).
2. ~~World-model **decay** rate (a living snapshot in dynamic equilibrium).~~ — ✅
   available now via `OccupancyMap(decay=…)`; see
   [Living snapshot](experiments/p2_living_snapshot.md).
3. Physical, **flexible whiskers** that bend and sense contact along their length.
4. **Actuated locomotion** (real muscle/tendon + ground contact).
5. Out-of-plane DOFs (z, roll, pitch); friction; uneven terrain.
6. Sensor models: rangefinder noise/dropout; proprioceptive bias/drift.

## F. What *is* faithful to SMN
Opponency at the zones (in-place rotation needs antagonists); reafference
self/world from an efference-keyed forward model (P0); located zones + explicit
body schema; a world model built **in relation to body geometry** from the
agent's own self-localization; BAP and HAP both **necessary** to build a world
model (ablations collapse coverage).
