# smn-playground — record of steps

A dated record of what was built, why, and what was found along the way. Each entry says what the step
was for, what was decided and why, and what it established. Times are IST. "GN" is G. Nagarjuna; the
building and checking were done with Claude (Anthropic) in review sessions on this repository.

---

## 2026-11-24 · Origin

**Brief (GN).** For investors, graphs and mathematics do not carry the idea. What does is that one
module, like a Lego block, builds many morphologies, and that those bodies live in a habitat: an
aquarium or a terrarium. The model was `playground.mujoco.org`, which showcases MuJoCo.

**First decision: the playground must not say more than the bench.** This project exists to keep the
presentation true to the paper. So every exhibit carries the ledger status of the experiment it
shows, and anything that is not a bench experiment is labelled as such. The morphology–habitat note
had already shown that several "blocks" are diagram-only: DOF variety, more than one CAZ per joint,
and a branched body with sensors and a floor. Those appear on the page as locked tiles, not as
renders.

**Second decision: live simulation rather than recorded video** (GN: "a live in-browser simulation is
good for a non-technical audience"). This required MuJoCo WASM, and it raised the question of fidelity.

## 2026-11-24 · v1: live bench in the browser

- **Engine.** `@mujoco/mujoco` 4.0.1, the official WASM build. The Python side was pinned to the same
  `mujoco==4.0.1`, so that any difference would come from the port, not the engine.
- **Port.** `OpponentBoard`, `MessagingBeam` (open loop, `entrain = 0`, as in every experiment shown),
  `ScalarField`, `apply_anisotropic_drag`, `apply_ground_friction` and the medusa's `apply_medium`
  were ported line for line.
- **Bodies.** A chain of 3–12 blocks, in water (C0 settings) or on ground (gravity_locomotion
  settings), and the medusa (medusa_swim settings), in water only. The medusa on ground shows a
  "Not on the bench" card.
- **Parity against Python.** Crawlers without contact are bit-level (≤ 1.3e-15 m). The medusa is
  chaotic: perturbing the Python bench by 1e-15 already moves its trajectory by 1.4e-3. Its 24 s rise
  is 0.065 in the browser, against 0.058–0.064 across the perturbed Python ensemble.
- **A WASM pitfall caught by the parity test.** Out-parameters must live on the WASM heap
  (`DoubleBuffer`). Passing a JS `Float64Array` silently left the velocities at zero, and the crawlers
  did not move.
- **CSP.** Embind generates its invokers with `new Function`. A page hosted under a CSP without
  `unsafe-eval` would therefore fail to start. `patches/mujoco-js-noeval.patch` falls back to a
  closure invoker (Emscripten's DYNAMIC_EXECUTION=0 semantics). It was tested under such a CSP.

## 2026-11-24 · v2: GN's three points

1. **Firefox did not start WebGL.** It could not be tested here. The page now catches the failure,
   shows the browser's own reason, and falls back to a flat 2-D renderer (top view for chains, side
   view for the bell).
2. **The world-model from the agent's perspective, by mounting transducers.**
   - Chemical (both sides) and touch skin can be mounted or unmounted. An unmounted modality gives a
     structural zero, as in the umwelt experiment's "sensory access".
   - A panel shows the body in its own frame (head on top) and kymographs over the last 40 s: felt
     change, change attributed to the world, and touch.
   - The attribution is a port of **Q1's per-zone dual-port reafference** (`sweep_q1_modulation.py`,
     ✅ on the ledger). Two departures are declared on the page: it runs noise-free, and the food's
     field is a Gaussian rather than Q1's linear slope, so the cancellation is only approximate.
     Residuals match a Q1-faithful Python reference to 9.6e-15.
3. **Objects did not resist.**
   - Tank walls (`with_walls`) and static cylinders (`objects`) now come from `build_crawler_xml`.
     C1's object is placed by default, and users can add rocks while the body moves. The builder was
     ported to JS (byte-identical on 73 configurations), so that adding a rock recompiles the model
     and carries the state over.
   - Decorative scenery was moved outside the arena, so that nothing within reach looks solid without
     being solid.
   - There is no halt: the body keeps pushing. Halting is the next block.
   - Contact runs agree to within the bench's own floor: perturbing the Python run by 1e-15 moves it
     7.7e-4 to 1.1e-3 m, and the browser stays within that.
   - ✅ is shown only for C0 in an empty world.

**Bench finding: the touch skin is ambiguous at the box corners.** In `build_crawler_xml` the touch
site is exactly the size of the segment's box (`size="{h} {w} {w}"`). Contacts at the box corners
therefore lie on the site boundary, and whether they are counted is decided by round-off. At
t = 27.5 s, with an 8-block crawler against a wall, native Python read touch0 = 0.8539 N, while the
contact normals summed to 0.8731 N; two 0.0096 N corner contacts were dropped. This affects C1's
touch readings. *Proposed fix:* make the site slightly larger than the geom (×1.05).

## 2026-11-24 · Probe: a non-uniform wobble (`tools/probes/wobble.py`)

8-block crawler in water, 30 s per condition.

| condition | net displacement (m) | forward fraction of path | joints' frequencies locked? | heading change |
|---|---|---|---|---|
| uniform (bench) | 2.34 | 0.94 | yes | 0° |
| amplitude tapers head→tail (1→0.3) | 1.08 | 0.82 | yes | 1° |
| amplitude grows head→tail (0.3→1) | 1.13 | 0.96 | yes | 0° |
| one dead joint (j4) | 1.56 | 0.88 | yes | 1° |
| one-sided bias (+0.15 rad) | 2.02 | 0.88 | yes | −45°, turns steadily |
| ±10% frequency spread, coupling 4 | 1.67 | 0.90 | yes | 1° |
| ±40% frequency spread, coupling 4 | 0.64 | 0.65 | no (0.22 Hz spread) | 3° |
| ±10% frequency spread, coupling 0 | 0.33 | 0.25 | no (0.18 Hz spread) | −8° |

- Uneven amplitude costs distance but not coherence.
- A one-sided bias produces a steady turn, by the same mechanism as food steering.
- Uneven rhythm is where the network matters: neighbour coupling locks a ±10% spread into a single
  wave, while without coupling the body thrashes rather than travels.

This is a quick probe, not a ledger result: one deterministic run per condition, water only.

## 2026-11-25 · Floor height in the terrarium; uneven ground

**The shadow below the crawler (GN).** The bench's ground crawler has no floor geometry. Gravity is
off in its MJCF (`gravity_on=False`), and weight enters only as μ·m·g inside `apply_ground_friction`.
The body is held in its plane by the head's slide joints at z0 = 0.1, so its belly sits at 0.075. The
page had drawn the floor at 0. It now draws it at 0.075, where the friction law treats the body as
resting. Real contact under gravity (`free_root=True`) exists on the bench, but its own docstring says
it still needs contact-dynamics tuning.

**Uneven ground (GN: let the wobble depend on the resistance of uneven territory).**
- *Extension, not on the bench.* The friction scale is a field,
  s(x, y) = exp(Σ aᵢ·exp(−rᵢ²/2σ²)), with σ = 0.35 and aᵢ = ±ln 3, so the coefficient ranges from
  1/3 to 3 times the bench value and the anisotropy is unchanged. The bench's `apply_ground_friction`
  is applied per segment with its local coefficient. The page labels it as an extension.
- *Parity.* Bit-level (1.8e-15 m).
- *Display.* A "bend it achieves" band in the agent's-frame panel shows each joint's achieved bend
  against its 0.8 rad command.

**Probe: does terrain resistance change the wobble? (`tools/probes/terrain_probe.py`)** 8 blocks, on
ground.

| friction × | entrainment | bend achieved (rad, of 0.8 commanded) | f_beam (Hz) | speed (m/s) | muscle saturated |
|---|---|---|---|---|---|
| 0.3 | 0 | 0.367 | 0.900 | 0.312 | 0% |
| 1 | 0 | 0.234 | 0.900 | 0.147 | 12% |
| 3 | 0 | 0.187 | 0.900 | 0.018 | 23% |
| 0.3 | 2 (inter) | 0.470 | 0.736 | 0.231 | 0% |
| 1 | 2 (inter) | 0.391 | 0.742 | 0.202 | 0% |
| 3 | 2 (inter) | 0.340 | 0.733 | 0.047 | 3% |

- **The shape of the wobble follows the ground.** Ground friction, unlike water drag applied at each
  segment's centre, loads the joints, so the bend shrinks on rough ground as the muscles saturate.
- **The rhythm does not.** f_beam stays flat, even with the bench's inter-segmental entrainment
  switched on. This is the S0b open problem, now seen on ground as well.
- *Side finding.* At the bench's own friction, the ground crawler achieves only about 0.23 rad of its
  0.8 rad command. It is already largely held back by load, which bears on step 3 of the S0b fix plan
  (the load-limited actuator).

## 2026-11-25 · Is the pulling element elastic? (GN)

| body | pulling element | elasticity |
|---|---|---|
| crawler (C0, C1, the playground chain) | ideal torque-motor opponent pair at each hinge | **none**: `joint_stiffness=0.0`; only the controller's gain (`kp=4`) acts like a spring |
| lattice bodies (sheet, tube, nested, Hydra, medusa, worms) | motor on a spatial tendon | spring on the tendon (`stiffness` 18–20), **in parallel** with the motor |
| manipulator | ideal torque motors | spring on the joint, not in the muscle |

**Bench finding: the lattice spring is labelled "series", but it is parallel.** The comments in
`lattice.py` and `medusa.py` speak of "the series spring". In MuJoCo, the motor force and the tendon
spring act along the same length, so the spring is in parallel. Either the wording or the model should
change. `docs/assumptions.md` already lists muscle–tendon impedance in its refinement backlog, and
Prediction 3 adds impedance inside the controller rather than in the muscle.

## 2026-11-25 · Alignment with preprint v3 (`smn-v3.pdf`, §§3–6)

**GN's statement of the goal.** The playground should present what is to be built on v3's modular
approach, and become an experimental bench for embodied cognition and artificial life, as NetLogo is
for complex systems. Gravity and the elastic substrate are the physical variables, the CAZ block is
kept constant while morphology varies, and the self-model and world-model are computed by reading the
DFN and the IN.

**Agreed:** one block, four moves (§4.1), one invariant mechanism (§4.5), and the self-model and
world-model read from the messaging network (DFN: own-action contrast with the α gate, C4; IN: the
broadcast Π under network closure, §4.4).

**Amendments recorded.**
1. **The physical parameters** (§3.10) also include the medium and damping (b), the opponency type
   (skeletal, hydrostatic or distributed), transducer physics (A, σ, η) and messaging physics
   (τ_b, C_b, λ_b, ε_b). Elasticity k is the load-bearing one (C7).
2. **The block is not yet one block, and in the chain neither variable is simulated.**
   - In the chain, k = 0 (torque motors) and gravity is off.
   - The bell has a parallel spring, with gravity and contact disabled.
   - Neither is the muscle–tendon unit of Eqs. 1–3: pull-only, contractile element in series with an
     elastic one, with the afferent s = Ψ(q, q̇, F) read from the same tissue.
3. **What the agent computes must stay separate from what we score** (§5.2).
   - Under coordinated locomotion G_ij collapses; the bench audit records this.
   - A live self-model panel should therefore show the collapse, as an experiment, not hide it.

**The current playground against v3**

| v3 element | current playground |
|---|---|
| SM = muscle + series-elastic tendon, k finite (Eq. 3, C7) | chain: k = 0, torque motors; bell: parallel spring |
| gravity as a load the balance holds | off in the chain, entering only through friction; off in the bell |
| medium / damping (b) | present: water drag, ground friction, uneven ground |
| board: drive, a₀, E_R, halt gate (Eqs. 4–8) | drive (PD) only |
| DFN: own-action contrast + α (C4) | contrast only (Q1 residual) |
| IN: broadcast Π with network closure | absent; beam messages go between neighbours only |
| self-model G_ij (Eq. 10) | not computed live |
| world-model: residual (Eqs. 11–12) and φ̂ update (Eq. 13) | residual only |
| four moves | scale only in the playground (sheet, tube, worms and medusa exist on the bench) |
| messaging physics | messages are instantaneous |

**Planned order of work** (before anything is added to the page):
1. One canonical SM/CAZ block in MuJoCo, shared by bench and playground: a pull-only tendon actuator,
   a series elastic element, and length, velocity and force sensors on the same tendon as the
   afferent. Pre-register that self-model recovery separates from the rigid (k → ∞) and floppy
   (k → 0) foils.
2. Real gravity and contact in the terrarium.
3. An explicit messaging network: Π with network closure, the α gate, and the board's a₀, E_R and halt
   gate, with live G_ij and φ̂ read from them.
4. One body-and-habitat specification that both the browser and the Python bench load, so that
   every playground finding is auditable on the bench (the parity discipline above, generalized).

## 2026-11-25 · Uneven ground recorded; a correction; the canonical SM block pre-registered

**Uneven ground.** The code and its log entry are in commit `82aa3ff`. Republishing the public page
awaits GN's explicit go-ahead.

**Correction to the elasticity entry above.** The statement that "the crawler has k = 0" holds for
the *locomotion* experiments (C0, gravity_locomotion) and for the playground's chain. It does not
hold for the bench's chain self-model test: `self_model_topology.py` sets a parallel joint spring
(`joint_stiffness=0.6`, with 80 for the rigid foil). That test already implements Eq. 3's
k(q − q0). The v3 alignment table should be read with this in mind: k = 0 applies to the playground
chain, not to every bench chain.

**The canonical SM block** (`smn_lab/sm_block.py`, from MuJoCo constructors). It is the
three-element Hill-type muscle:

- a pull-only contractile element: a motor on an internal slide DOF, with viscosity;
- a series elastic element: a fixed tendon L = ∓r·q + x with a dead band, so it pulls only when
  stretched;
- a parallel elastic element: the joint stiffness, i.e. Eq. 3's k(q − q0);
- afferents read from the same tissue: tendon length/tension, CE force, joint angle and velocity.

r·F_max equals the bench torque motors' peak torque. Its statics are fixed by
`tests/test_sm_block.py`, all passing: series equilibrium (tension = CE force to 10⁻³ N),
pull-only slack, q = rF/k_pee, and co-contraction holding the joint with both tendons taut.

**Finding for v3, from the construction itself.** A force-producing contractile element in series
with a spring gives no restoring stiffness. At co-contraction 2 + 2 N with no parallel element, a
0.02 N·m push moves the joint 0.79 rad and it never returns; with k_pee = 0.6 it moves 0.033 rad
and returns to zero. So §3.5's "a contractile element in series with a passive elastic one" does
not by itself supply Eq. 3's k(q − q0). *Suggested wording for v3:* the SM has a series and a
parallel elastic element, and the restoring term of Eq. 3 is the parallel one (or a CE
force–length relation).

**A second v3 note.** Table 2 classes self-model graph recovery as a *diagnostic*, while §5.2 calls
recovery quality the *order parameter*. The pre-registration follows Table 2 and §12: the test is
the separation from matched foils.

**Pre-registration** (`docs/experiments/sm_block.md`, written before any run, linked from the nav
and the status ledger as "pre-registered, unrun"):

- **H1.** The self-model on the block, replicating `self_model_topology.py`. Conditions: block,
  PEE-only, SEE-only, rigid foil, frozen foil.
  - P1: block neighbour accuracy ≥ 0.90 and order accuracy ≥ 0.80.
  - P2: rigid foil ≤ 0.60, and ≥ 0.30 below the block.
  - P3 (X): PEE-only within 0.10 of the block.
  - P4 (X): SEE-only — two competing outcomes, both reported.
- **H2.** No regression: C0 and gravity_locomotion on the block reach ≥ 50% of the torque-motor
  displacement, with gains unchanged and no retuning within this pre-registration.
- **H3 (X).** Whether the tendon afferent and the joint lag carry ground friction while the command
  does not.

Status: awaiting GN's approval of the hypotheses and thresholds before `experiments/sm_block.py` is
written and run.

## Publication

- Live page: <https://claude.ai/artifact/PepmNmqmfnP6vyWuaAi3eD> (public).
- v1 and v2 are live. The 25 Nov changes (terrarium floor height, uneven ground, the bend band) are
  built and tested, and await GN's go-ahead to republish the public page.
