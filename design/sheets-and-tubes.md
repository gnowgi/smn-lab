# Design — sheets and tubes: muscle tissue as linked CAZ chains

*Phase I·① extension (topology-invariant self-model) that also seeds the Phase II
tubular rung. Status: design; build staged below.*

## The claim

One mechanism, any anatomy. A **muscle** is nothing but a long chain of CAZ
(coordinated action zones); a **sheet/sheath** is two such chains linked laterally;
a **tube** — a worm, a digestive tract, a blood vessel — is three or more chains
linked both **longitudinally** and **laterally**. Nothing central regulates them.
The anatomy (which chains, how linked, what DOF each link has, which nodes are
active) *is* the specification of the behavior. So an experimenter can compose an
agent **at will** and read off what behavior its body plan affords — the bench
becomes truly generative, and predicting "what this architecture is up to" is the
bonus that makes the case to physics **and** artificial-life colleagues.

Two payoffs, one construction:

1. **Self-model (Phase I·①).** The *same* framework read-out
   (`smn_lab.self_model.transfer` / `coupling`) recovers the body graph whatever
   the topology — a line, a grid (sheet), a cylinder (tube). Topology-invariance,
   shown with byte-identical injected code.
2. **Behavior (bridge to Phase II).** The same links, driven as *muscles*, produce
   crawling, peristalsis, and rolling — anatomy → behavior, with no central clock.

## From chain to sheet to tube

We already have the **chain**: `build_crawler_xml(n_seg=N)` — `N` segments joined
head-to-tail by elastic hinges (the **longitudinal** links). Extend to a lattice of
`R` rows (parallel chains) × `N` columns (segments per chain):

| Body | Rows `R` | Lateral closure | Recovered self-graph |
|---|---|---|---|
| **chain** (muscle) | 1 | — | a path (line) |
| **sheet / sheath** | 2 | open | a 2×N ladder |
| **tube** | ≥ 3 | closed (row `R−1` ↔ row `0`) | an `R×N` cylinder |

- **Longitudinal links** — the within-row elastic hinges (already in the chain).
  Contract them in a wave and the tube shortens/bends along its length →
  **longitudinal muscle**.
- **Lateral links** — elastic couplings between laterally-adjacent segments
  `(r,c)–(r+1,c)`. Contract them around the ring and the tube constricts its radius
  → **circular muscle**.

Two rows give a *sheet* (a flat sheath); closing three or more rows into a ring
gives a *tube* — because only a closed lateral loop has an inside and an outside.

## MuJoCo realization (loop-free, elastic, stable)

A MuJoCo kinematic tree cannot contain loops, and a grid/cylinder is full of them.
So the lattice is built as **`R` independent elastic chains** (each a normal
kinematic tree, as today) plus **lateral spring-tendons** between laterally-adjacent
segments. A spatial tendon *is* a muscle — spring-backed (`stiffness`, `damping`),
optionally actuated — so the physics and the SMN reading coincide:

- **Longitudinal muscle** = the existing hinge + its pull-only opponent pair
  (`m_j{k}_p/_n`), elasticity via `joint_stiffness` (as in the
  [self-model](../docs/experiments/self_model_topology.md)).
- **Circular muscle** = a lateral spatial tendon between `seg{r}_{c}` and
  `seg{r+1}_{c}`, with spring stiffness (elastic transmission) and, when driven, a
  tendon actuator that shortens it.
- **Tube closure** = the same lateral tendon wrapping row `R−1` back to row `0`.

Elastic lateral links are not a convenience — they are *required*: the self-model
read-out works because a driven node displaces a far node **less** (attenuation with
hops). Lateral elasticity is what lets co-movement travel across rows, so the grid
is readable. This reuses the rung-3 mechanism exactly, in a second dimension.

### Proposed builder API

```
build_lattice_xml(n_col=8, n_row=1, closed=False,
                  long_stiffness=0.6, lat_stiffness=0.6,
                  lat_dof="tendon",          # "tendon" | "hinge" | "slide"
                  drive="independent", ...) -> str
```

`n_row=1` reproduces `build_crawler_xml` (a muscle). `n_row=2, closed=False` → sheet;
`n_row>=3, closed=True` → tube. `lat_dof` sets what the circular link can do — a
constricting tendon, a bending hinge, or a sliding shear — which is the DOF knob
below.

## The DOF knob → behavior (the generative table)

Behavior is selected by *which links are active* and *what DOF they have* — not by a
controller. Target demonstrations:

| Active muscle | DOF | Wave pattern | Behavior | Biology |
|---|---|---|---|---|
| longitudinal | hinge (bend) | traveling head→tail | **crawl / swim** | worm locomotion |
| longitudinal | slide (contract) | traveling | **inch / peristalsis-along** | earthworm |
| circular | tendon (constrict) | traveling ring wave | **peristalsis** | gut / digestive tract |
| circular + longitudinal | phase-offset | coupled waves | **squeeze-and-push** | swallowing, blood vessel |
| longitudinal (one side) | hinge | standing asymmetry | **roll / curl** | torsion |

Each row is one experiment: fix the anatomy, choose the active muscle + DOF, and the
behavior falls out of the decentralized dynamics. This is the "anatomy → behavior at
the developer's will" claim, made runnable.

## The self-model demonstration (the Phase I·① close)

For each body (chain, sheet, tube), drive every node independently (OU forcing, as
in the self-model experiment), log per-node drive and motion, and apply the **same**
`transfer` read-out. Prediction, pre-registered:

- **chain** → recovered graph is a path;
- **sheet** → a 2×N ladder (each node's strongest co-movers are its longitudinal
  *and* lateral neighbours);
- **tube** → an `R×N` cylinder (the lateral neighbours wrap).

The order parameter is neighbour-recovery accuracy against the true lattice
adjacency (an [experimenter metric](../docs/self-model-and-measurement.md), keyed on
the known wiring). Passing on all three = **one function, any body**, with the
injected code byte-identical across the three pages.

## Why this clinches the audience

- **Physics/biophysics.** A tissue-level structure (muscle, gut) is reduced to a
  local coupling rule with no central regulator; the self-model is recovered by a
  correlation the tissue itself computes. Decentralized regulation, made measurable.
- **Artificial life.** The body plan is a *generative program*: specify the lattice
  and the DOFs, and the morphology predicts the behavior. This is exactly the
  "morphology computes" thesis, now with a knob and a prediction.
- **The bridge.** It makes the [Phase II](../docs/phase2.md) tubular rung concrete —
  the second step of polarized → **tubular** → segmented → bilateral → appendicular —
  and shows how nested (longitudinal × circular) modulation is the route to richer
  behavior and richer world-models, not more identical zones.

## Prototype finding (2026-07-16) — the read-out must go through the muscles

A first prototype (`scratchpad/lattice_proto.py`) confirmed the **buildability**: an
`R×N` lattice of elastic chains + lateral spring-tendons loads and runs stably in
MuJoCo (contacts disabled — it is one tissue, not colliding parts), and the tube
(closed lateral ring, `R≥3`) constructs cleanly.

But it also surfaced the crux. Driving each **segment** with an external force and
reading its velocity recovers the lattice only weakly (chain ≈ 0.31 ≈ chance;
sheet/tube ≈ 0.44). The reason is exactly why the [chain self-model](../docs/experiments/self_model_topology.md)
works at 1.00: there the read-out drives the **links** (joint torques) and reads the
*differential* motion that elastic links transmit with hop-attenuation. An external
push on a whole cell propagates as a global mode with no clean attenuation.

**Design consequence:** the self-model of a tissue must be read **through its own
muscles** — drive each link (longitudinal hinge + lateral tendon actuator)
independently and correlate each link's efference with the afferent motion it hears,
per `transfer`. This is not a tuning detail; it is the point — a tissue knows its own
shape through the muscles that move it, not through an external agent poking its
cells. T2 below implements this link-driven read-out.

## Settled design (2026-07-16, with GN)

- **CAZ = one muscle-tendon unit** (active actuator + series elastic + embedded
  transducer), variable DOF. We do *not* split muscle vs tendon. This is the
  standard biomechanical MTU idealization — valid.
- **Two CAZ archetypes** (the second is new to the visual grammar and must be added):
  - **skeletal** — a flexor/extensor *pair* across a rigid lever (hinge). Needs a
    skeleton (internal or external). The current grammar.
  - **hydrostatic** — *linked linear actuators*, no skeleton; the antagonist is the
    structure itself (constant volume / turgor). Shapes tubes, worms, tongue, gut.
- **Segments = scaffolding** — rigid mounts for sensors "when and where we need"; the
  CAZ links are what move and what the self-model is read through.
- **C. elegans vs earthworm** — longitudinal-only (cuticle as antagonist → bending
  waves) vs longitudinal+circular (→ peristalsis). Only the earthworm needs true
  volume coupling.
- **Toolbox (MuJoCo 3.9.0, probed):** linear actuators (slide+spring), tendon
  actuators (circular), and FLEX deformables are all available.
- **Chosen route:** spring-lattice of rigid segments + linked linear-actuator CAZ,
  passive springs as antagonist; **FLEX kept as a labelled realism upgrade** (true
  volume-preserving hydrostat) for a later rung.
- **Order:** the topology-invariant **self-model recovery** first (Phase I·① claim);
  the C. elegans / earthworm **behaviors** after (Phase II tubular rung).

### The read-out (settled): link-driven, and it is the *same framework function*

Each CAZ link is driven independently; we read each **segment's** motion and ask,
per link, which two segments it couples — its strongest positive and negative
co-movers. That is exactly `coupling` + `recover_edges` from
[`smn_lab.self_model`](../docs/self-model-and-measurement.md) — the identical
functions that recover the [branched tree](../docs/experiments/branched_self_model.md):

- `C = coupling(LINK_VEL, SEG_MOTION)`  (rectangular, n_link × n_seg)
- `edges = recover_edges(C)`  → each link's (argmax, argmin) = its two endpoints
- union of edges = the recovered body graph: a **path** (chain), a **ladder**
  (sheet), a **cylinder** (tube).

So "one function, any body" is not a slogan — the injected code is byte-identical
across chain, tree, sheet and tube. The prototype's failure (driving *cells*, chance
recovery) is the control that proves the point: a tissue knows its shape through the
muscles that move it.

## Validation (2026-07-16) — topology-invariance shown

The link-driven read-out works, cleanly, across all three topologies
(`scratchpad/lattice_v2.py`; mass-spring lattice, each link a spring-tendon CAZ with
its own actuator, driven independently; segments **overdamped**):

| body | segments | links | endpoint-recovery (3 seeds) |
|---|---|---|---|
| chain (muscle) | 8 | 7 | **1.00 ± 0.00** |
| sheet (sheath) | 12 | 16 | **0.99 ± 0.01** |
| tube (closed ring) | 24 | 44 | **0.97 ± 0.01** |

The recovery uses the framework `coupling` unchanged: `C = |coupling(LINK_DRIVE,
VX)| + |coupling(LINK_DRIVE, VY)|`, and each link's top-2 segments are its
endpoints. **The mechanism is the physics, not a tuning trick:** soft tissue is
overdamped (the same low-Reynolds regime as the crawler's medium), and in the
overdamped limit a driven link's force shows up *only* at its two endpoints — so the
correlation is local however dense the lattice. This is why one function recovers
any body.

## Build plan

- **T1 — the lattice builder.** `build_lattice_xml` in `smn_lab/crawler.py` (or a new
  `smn_lab/lattice.py`): R elastic chains + lateral spring-tendons; `closed` ring
  option. Verify it loads and is stable (zero solver warnings) for chain/sheet/tube.
- **T2 — self-model recovery.** One experiment `experiments/lattice_self_model.py`:
  drive independently, apply `transfer`, score neighbour recovery vs the true lattice
  for chain/sheet/tube. Doc page under **Phase I·① Self** ("one function, any body"),
  injecting the canonical read-out.
- **T3 — muscle behaviors.** `experiments/tube_behaviors.py`: peristalsis (circular
  wave), crawl (longitudinal wave), roll (asymmetric) — the generative table, driven
  with the messaging beam. Doc page under **Phase II** (tubular rung).
- **T4 — the ① Self overview.** A short landing page presenting chain/tree/sheet/tube
  together as the topology-invariance result, with the neighbour-recovery summary.
