# Assumptions, and what is derived

Assumptions in this lab are **layered and not fixed**. There is a **common core**
(this page) that holds across experiments, plus **per-experiment specifics** that
add to or override it. Each experiment page states its own deltas; this page is the
shared reference.

Every result traces to one of three things: **(A)** physics the engine integrates,
**(B)** a computation our code performs, or **(C)** a modelling idealization.

## The bodies

The bench is no longer one body. The current progression uses three families, each
page stating which it uses:

- **the segmented crawler** — an axial chain of massed segments with opponent hinge
  pairs, moved by a messaging-beam wave through an anisotropic drag medium
  ([C0](experiments/c0_crawler.md), [C1](experiments/c1_touch.md); `smn_lab.crawler`);
- **spring-tendon lattices** — point-mass segments joined by spring-tendon CAZ links,
  in the overdamped soft-tissue regime, for the self-model / sheet / tube / nested
  experiments (`smn_lab.lattice`);
- **the bilateral manipulator** — a two-limb contact unit for object-directedness
  ([E3](experiments/p6_haltability_aboutness.md); `smn_lab.manipulator`).

## Common assumptions (unless an experiment says otherwise)

- **MuJoCo integrates the dynamics** at **dt = 2 ms** with the `implicitfast`
  integrator (not the older RK4 / 5 ms trial default).
- **Overdamped, non-inertial regime.** Nothing coasts: motion is resisted by an
  explicit **anisotropic drag** medium (crawler) or by high **joint damping**
  (lattices). This is the low-Reynolds / soft-tissue regime.
- **Tissue lattices disable contact.** A lattice is *one tissue*, not colliding
  parts, so segment–segment contact is switched off and gravity is off. The crawler
  and manipulator keep the contacts they need (touch skin, object press).
- **Links are elastic (compliant).** Elastic transmission with attenuation is what
  makes the self-model recoverable at all (a rigid body moves as one common mode and
  reveals nothing). Elasticity is a load-bearing commitment.
- **Reproducible.** All RNGs are seeded; runs are byte-reproducible.

## A. Simulated by MuJoCo (derived)
Rigid-body dynamics of the segments; joint and spatial-tendon spring/damper forces;
contact forces where enabled (the C1 ventral skin, the manipulator's press);
proprioception (joint velocities, body linear/angular velocity via
`mj_objectVelocity`).

## B. Computed by our code
- **The model (the agent's own computation).** The messaging-beam wave
  (`MessagingBeam`); the pull-only opponent activations (`OpponentBoard`); the
  **self-model read-out** `self_model.coupling` — recovered *locally*, no central
  reader (Commitment C3); reafference residuals; localization in the self-frame.
- **The measurement (the experimenter's).** The scores that read against ground truth
  the agent cannot access — endpoint/neighbour recovery, decoding skill + shuffle
  control, the reafference ratio — all in `smn_lab.metrics`, kept separate on
  purpose (see [model vs. measurement](self-model-and-measurement.md)).

## C. Idealizations (common)
- The overdamped medium is an **explicit force law** (anisotropic drag) or joint
  damping, not MuJoCo's fluid solver.
- Lattice **segments are point-mass scaffolding** — a place to mount sensors; the
  links (CAZ muscles) are what move and what the self-model is read through.
- The manipulator uses **ideal torque motors**, so co-contraction is inert for
  stiffness in free space; there, the object supplies the equilibrium (a
  muscle–tendon impedance model is a declared later refinement).
- Some bodies are **planar** or have out-of-plane DOFs suppressed; friction is off
  except where an experiment needs it.

## Per-experiment assumptions

### The spine (the current progression)

| aspect | Organism (C0/C1) | Self (self-model · lattice) | World (Q2 · W1/W2 · Q1) | Object (E3) |
|---|---|---|---|---|
| **body** | axial crawler segments | point-mass segments + spring-tendon CAZ links | crawler / elastic chain | bilateral two-limb manipulator |
| **medium** | anisotropic drag (C0 gravity off; C1 gravity on + touch skin + object) | overdamped, contacts off, gravity off | anisotropic drag | ideal torque motors + object contact |
| **the agent computes** | messaging-beam wave | `coupling` (self-model) | `coupling` + self-frame localization + reafference | `coupling` (2 zones) + the halt pattern |
| **the experimenter scores** | net displacement, gait loop-area | endpoint / neighbour recovery | decoding skill (+ shuffle), residual ratio | longest sustained directed halt |
| **the one variable** | coupling (S0) | elasticity; topology / scale | modulation; segment count | canvas present / halt |

### Provenance (the P-series — exploratory, superseded)

The bench's first exploratory line ran on a *different* body — a **planar single
"mouse"** (one rigid body, `slide_x`/`slide_y`/`yaw`), **rangefinder whiskers**, and a
**camera + 8×8 modulator** — and built an **occupancy-map** world model scored by
coverage/precision. It is kept as [provenance](reproducibility.md), *not* the current
bench; its assumptions live on its own pages (P0–P3). Read it as proofs-of-concept.

| aspect | P0 / P0-visual | P1 / P2 (world model) |
|---|---|---|
| body | single planar "head" (± eye CAZ) | mobile planar body, whiskers |
| transducer | rangefinder whisker / camera + 8×8 patch | 5-whisker fan |
| world model | forward-model residual | occupancy accumulator (coverage / precision) |

## D. What *is* faithful to SMN
Opponency at the zones (in-place rotation needs antagonists); an **elastic** substrate
that transmits differential motion; a self-model **recovered locally** from movement
with no central reader (C3); a world model built **in the self's own frame**;
reafference separating self from world; and a **haltable action pattern** that makes an
action *about* an object.

## E. Refinement backlog
1. **FLEX volume-conserving hydrostat** (the aquatic/soft-tissue regime; true
   "contract-circular → elongate" coupling) — the labelled realism upgrade.
2. **Hydrostatic CAZ in the visual grammar** (linked linear actuators; deferred).
3. **Muscle–tendon impedance** for a free-space stiffness equilibrium (E3's deferral).
4. **Muscle behaviours** on the tube (C. elegans bending, earthworm peristalsis).
5. Out-of-plane DOFs, friction, uneven terrain; sensor noise / dropout models.
