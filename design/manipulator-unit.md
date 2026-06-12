# Design spec — the bilateral two-limb manipulator unit

*A design document, written before code. It fixes the architecture's commitments
so they are inspectable, derives the finite state-space ("field") from the
structure, and defines the experiments as "which subset of that field is
occupied." Nothing here is learned; the field is given by construction.*

## 0. Purpose and scope

The first agent of the contact phase of `smn-lab`. A **bilaterally symmetric,
two-limb manipulator** that contacts objects resting in a real gravitational
field. It is deliberately **one body segment**: a series of these units, coupled
by an activation wave, becomes the crawler of the next iteration (turning by
bilateral halt-differentiation). For the manipulator experiments the segment is
**pinned to the world** (no locomotion, no balance) so the claims are isolated.

It must support three claims, each only an opponent-modulated contact body in a
field can make:

1. **Objecthood is resistance-to-modulation.** A thing is what resists the
   agent's attempted pulls — separable by mass, friction, fixation, compliance.
2. **Self / field / object are factored architecturally**, through the
   dual-interface effort signal, not by a learned classifier.
3. **Haltability generates aboutness.** A halt-in-contact (co-activated
   equilibrium) is a persistent, returnable, side-specific state *about* the
   object.

### Theoretical anchoring — an enacted two-vector model

The unit is, concretely, an embodied realisation of Gärdenfors's **two-vector
model of events**: an event is an **action force vector** mapped to a **result
vector** (the patient's change). Here the antagonist **pull is the force
vector**; the object's **response — yield, resist, comply — is the result
vector**; gravity and friction are the Talmy/Wolff **counterforces**. So
*objecthood is the force→result causal mapping*, read as resistance to the
agent's own modulation. Two commitments distinguish our version: the mapping is
**enacted by construction** — neither *learned* (the open problem in that
literature) nor *inferred* probabilistically (Bayesian models, which are
ill-suited here) — and the state-space it lives in is a **geometric conceptual
space**, so the register lattice (§4) carries the monotonicity, continuity, and
convexity such mappings obey. The three claims above are the three faces of this
one model: its mapping (1), its decomposition into action-force / counterforce /
patient-response (2), and its equilibrium-as-halt (3).

## 1. Non-negotiable commitments

| Commitment | Consequence for the design |
|---|---|
| **Pull-only antagonist actuators; no steppers** | Every DOF is driven by *two* opposing pull-only linear actuators. You never command an angle — you modulate two pulls. The opponent pair is the atomic dynamical system; its co-activated equilibrium is the *balance*. |
| **Dual-interface zone** | A CAZ senses and acts through *one* coupling. In code, one zone object owns both the pull commands (act) and the effort/contact/proprioceptive read (sense) — not separate actuator/sensor modules. |
| **Field as prior** | Gravity is ON, the floor has real friction, objects have mass and a fixation mode. The agent never gets the field for free as background; it *reads the field through the work it does against it.* Field parameters $(g, \mu, m, \text{fixation})$ are explicit independent variables. |
| **Haltability is an equilibrium, not a stop** | A halt = the antagonist pair (plus gravity/contact) settling into co-activation. It is a *state*, and it can be *held* and *returned to*. |
| **Bilateral** | Left and right limbs are mirror zones. Left/right differentiation (one halts, the other acts) is the seed of both turning and object-directedness. |

## 2. Body structure (concrete)

```
world: gravity (0,0,-9.81); floor plane with friction mu (IV)
  segment_base  (box) — welded to world for the unit; the chaining face for the crawler
    ├─ limb_L : hinge (axis = body +y), link length L, tip geom + touch site
    │            actuators: pull_L_down (gear +), pull_L_up (gear -)   [ctrlrange 0..cmax]
    └─ limb_R : hinge (axis = body +y), link length L, tip geom + touch site
                 actuators: pull_R_down (gear +), pull_R_up (gear -)   [ctrlrange 0..cmax]
  object (box/cylinder) on the floor ahead of a limb:
     mass m (IV), friction (IV), fixation ∈ {free, welded, compliant-spring} (IV)
```

Each limb swings in its **sagittal (x–z) plane**, so gravity genuinely matters:
lowering is gravity-assisted, lifting is work against the field. A limb reaches
down-and-forward to press the floor or an object. Minimal version: **one joint
per limb**; a second joint (a "wrist") is the first option if reach/press needs
it (§9).

**Per-limb sensing (the dual interface read):**
- joint position, joint velocity (proprioception),
- **actuator/joint force** — the *effort / tension* signal = work against
  (field + object); this is the channel that makes resistance legible,
- **tip touch/contact** sensor.

This is the SMN dual-interface: the same zone that pulls also reports the effort
and contact those pulls meet.

## 3. The field (independent variables)

The world is structured, and its structure is varied on purpose:

| IV | values | what it probes |
|---|---|---|
| gravity $g$ | {full, reduced} | is "field-resistance" really gravity-grounded? |
| floor friction $\mu$ | {low, mid, high} | friction $=\mu N$ — field-dependent object resistance |
| object presence | {absent, present} | field-only vs field+object |
| object mass $m$ | {light, heavy} | resistance-to-push from inertia/weight |
| object fixation | {free, welded, compliant} | movable vs fixed vs springy — the objecthood axis |

"Field" here = gravity and its surface (the ground that always pushes back).
"Object" = the variable figure resting in/on the field. The agent must tell the
constant ground from the variable figure — that is claim 2.

## 4. The derived finite field (register lattice)

The structure (fixed DOF + antagonist pairs + contact possibilities) **defines a
finite register space a priori**, before any run. Per limb:

| register | values |
|---|---|
| **Contact** $C$ | free · ground · object |
| **Effort** $E$ | slack · working · straining  (binned from \|actuator force\|, gated against a calibrated floor) |
| **Motion** $M$ | with-field (descending, gravity-aided) · against-field (ascending, effort) · halted (\|vel\|≈0 under co-activation) |

Per-limb cells $= 3\times3\times3 = 27$. The **bilateral coordination register**
adds: `both-free · L-halt/R-act · R-halt/L-act · both-halt` $(4)$. The whole
**field** is this finite lattice; it is computable from the body alone.

In two-vector terms, **Effort $E$ is the agent's read of the action force** (the
compensation it performs) and **Contact$\times$Motion $(C,M)$ is its read of the
result**; each object condition is therefore a *different force→result mapping*,
hence a different trajectory through the lattice.

An experiment **records which cells are occupied** under a condition. Examples of
the *predicted* occupied subset:

- **Free swing (no object):** $C=$free; $M$ cycles with-field/against-field;
  $E=$slack→working; halted only at the gravity-set apex/nadir.
- **Press ground:** $C=$ground; $E=$working→straining; $M=$halted (equilibrium
  against the field's surface).
- **Press *fixed* object:** $C=$object; $E=$straining; $M=$halted — can't push
  through.
- **Press *movable* object:** $C=$object; $E=$working then $M=$against-field
  *while the object yields* — resistance falls as it slides. A **different
  lattice trajectory** from the fixed case.
- **Press *compliant* object:** $C=$object; $E$ rises smoothly with displacement;
  $M$ creeps to a springy equilibrium.

The four object conditions trace **distinct, separable trajectories** in
$(C,E,M)$ — *objecthood as resistance-to-modulation, by construction, no
learning.* That separation is the headline figure.

## 5. Experiments (each = "which subset of the field")

### E1 — Objecthood as resistance-to-modulation
*Manipulation:* object $\in$ {absent, free-light, free-heavy, welded, compliant};
limb presses. *Claim:* the conditions occupy distinct, separable regions/
trajectories of the $(C,E,M)$ lattice — i.e. each object is a distinct
**force→result mapping** (the two-vector causal map), recovered by construction. *Metric:* separability of the occupied
subsets (e.g., cluster purity over $(C,E,M)$ trajectories); resistance estimate
vs ground truth. *Foils:* torque/position controller and a CPG — show they
separate objects less cleanly and cannot hold stable contact without overpress.

### E2 — Self / field / object factoring
*Manipulation:* matched limb **kinematics**, different **cause** — (a) free swing
(self+field), (b) press ground (self+field-surface), (c) press object
(self+field+object), (d) externally perturbed limb (world acts on agent).
*Claim:* the SMN agent assigns these to distinct cells via the effort-vs-achieved
(dual-interface) mismatch; a position-only/torque agent confounds them.
*Metric:* three/four-way separability from internal variables alone; robustness
under motor noise and reduced $g$. *This is the three-way generalization of the
self/world register* — in force-dynamics terms, **action-force vs counterforce
(field) vs patient-response (object)**.

### E3 — Haltability → returnable aboutness
*Manipulation:* object on the **left** vs **right**; press, withdraw, re-press.
*Claim:* the halt-in-contact is a **persistent, side-specific, returnable**
state — the agent re-finds the same resistance; the bilateral asymmetry
(L-halt/R-act) *is* directedness toward the object. *Metric:* persistence of the
object cell across withdrawal; re-acquisition success/precision; bilateral
register correctly tracks object side. *Foils:* CPG (keeps oscillating, cannot
hold an object-directed halt); torque (can hold, but without self/field/object
factoring its hold is not *about* the object as resistance).

## 6. Foils and comparison protocol

Same body, same sensors, same field, swap only the controller:

- **SMN** — opponent pull-only pairs + dual-interface modulation + halt.
- **Torque/position controller** — one signed command per DOF, no opponency, no
  halt register.
- **CPG** — rhythmic antagonist drive, no haltable equilibrium.

Core claims are judged **by construction** (no learning), via **lattice
occupancy / separability**, not reward. A matched-budget *learned* baseline
(forward-model or small RL) can be added later for an "architecture-biases-
learning" framing; it is not needed for the by-construction result and is
deferred.

**A concern, addressed.** One might object that a by-construction agent with
fixed couplings simply *engineers the answer*. The reply is methodological: the
field/lattice is **fixed by the body's structure before any run, identically for
every controller** — what differs is only *which subset each controller can
occupy*. The claim is not that SMN scores higher, but that opponent modulation +
halt + the dual-interface make a **larger, more separable, field/object-factored
region of the same lattice reachable** than torque or CPG control do — a
structural fact about the architecture, not a tuned threshold. (The deferred
learned baseline closes the matched-budget form of the same question.)

## 7. MuJoCo faithfulness — validate first

Before building experiments, a tiny probe: drive a single pull-only antagonist
joint into a fixed vs free vs compliant contact and confirm the **effort signal
(actuator/joint force) reads a clean, monotone resistance** that distinguishes
the three. The whole program rests on this signal; if MuJoCo's actuator/contact
model muddies it (the muscle-tendon mapping is only approximate), we adjust the
actuator model (e.g., `tendon`+`muscle`) before going further.

## 8. Build ladder

1. **This unit** (pinned): E1–E3 above.
2. **Crawler** = a series of units; release the pin; forward by activation wave,
   turn by bilateral halt-differentiation. Adds the *habitat* snapshot
   (locomotion as continuous work against the field) on the **same primitive**.
3. Later stages: active touch, tool incorporation, whole-body halt-as-balance.

## 9. Open decisions (for review before coding)

1. **One joint per limb, or two** (add a "wrist" for press geometry)? Start with
   one; add the second only if the limb can't make clean contact.
2. **Effort binning** — fixed thresholds vs a calibrated per-zone floor (the
   reafference-style gate we already use). Leaning calibrated floor (consistent
   with the modulator).
3. **Object set** — the five conditions in §3, or a finer fixation/compliance
   sweep?
4. **Lead claim for the first paper** — E2 (self/field/object) as headline with
   E1/E3 supporting, or E1 (objecthood) as headline? (Earlier lean: E2.)
5. **Learned baseline now or later** — deferred by default (§6).
