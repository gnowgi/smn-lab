# SMN-Lab: a synthetic instrument for minimal embodied cognition

*Working draft — target: Artificial Life (MIT Press); cross-post arXiv (cs.AI; cross-list nlin.AO, q-bio.NC).*

**Authors.** G. Nagarjuna; Durgaprasad Karnam.

**Keywords.** synthetic method; embodied cognition; enactivism; minimal cognition;
morphological computation; reafference; model organism; reproducibility; artificial life.

---

## Abstract

We present **SMN-Lab**, an open-source, embodied simulation bench for the synthetic
study of minimal embodied cognition, built on MuJoCo. Designed for rigor and reuse,
the bench is organized around a single synthetic model organism — a minimal axial
crawler whose form is *derived*, not assumed, as the smallest body able to initiate
non-inertial movement and so to actively sample a world. The agent is placed in a
gravitational field **treated as a structural prior**, and its elementary unit — a
Coordinated Action Zone, an antagonistic pull-only opponent pair that both senses
and acts — is organized to **oppose that field and the forces of the medium**,
holding a dynamic equilibrium from which action departs. A network of such zones,
coupled through a *messaging beam*, realizes the body's control as morphological
computation, and the agent **constructs its world model in its own body geometry**
— a body-relative frame rather than a god's-eye coordinate system. Five design
commitments support falsifiable, reproducible experiments: a fixed model organism
varied one parameter at a time; a diagram grammar that renders any agent's
morphology, sensors, and coupling in one notation; a strict boundary between the
physics engine and the architecture; pre-registered hypotheses with matched
non-modulatory foils; and seeded, self-describing datasets. We validate the
instrument by exercising it on the Sensation Modulating Network architecture across
nine pre-registered studies; the architecture is confirmed about as often as it is
corrected — demonstrating that the bench can put a theory *at risk*. All code,
documentation, and data are openly available. SMN-Lab is offered to the
artificial-life and enactive-cognition communities as a reusable, falsifiable
testbed; we also confront the irony it embodies — an *embodied* agent inside a
*simulation* — and ask, explicitly, whether a simulation can capture embodiment and
object-directed phenomenology.

## Specifications table

| | |
|---|---|
| **Name** | SMN-Lab |
| **Subject area** | Artificial life; embodied & enactive cognitive science; minimal cognition; morphological computation |
| **Instrument type** | Open-source embodied simulation bench (MuJoCo); a model-organism testbed |
| **Closest analog** | Bespoke agent-based embodied-cognition simulations (e.g. evolved CTRNN agents); no shared, pre-registered, reproducible bench of this kind. Hardware sibling: the Enactive Torch (Estelle et al.) |
| **License** | GNU GPL-3.0-or-later |
| **Cost** | Free (open source) |
| **Languages / dependencies** | Python · MuJoCo · NumPy · matplotlib (Streamlit optional) |
| **Source repository** | github.com/gnowgi/smn-lab |
| **Documentation** | smn-lab.readthedocs.io |
| **Architecture reference** | Nagarjuna & Karnam, *The Sensation Modulating Network*, arXiv:2605.26856 |

---

## 1. The instrument in context  *(outline)*

- The synthetic method (understanding by building) and its **rigor gap**: embodied
  architectures are usually *illustrated* by a bespoke simulation, rarely *risked*.
- One-paragraph statement of the SMN architecture (cite arXiv:2605.26856).
- What SMN-Lab provides: a shared, falsifiable, reproducible instrument — itself the
  contribution, independent of any single theoretical result.
- Kinship: the **Enactive Torch** (a hardware sensory-substitution device for
  enactive research) — SMN-Lab is its computational counterpart: a *synthetic* body
  rather than an *augmented* one.

---

## 2. Design principles  *(drafted)*

SMN-Lab is built from a small number of commitments, each chosen so that an
architectural claim about embodied cognition can be stated as a measurement and put
at risk. They are design choices, not results; the results (Section 4) are what the
choices make possible.

### 2.1 A *derived* model organism

Comparative biology earns its power by returning to a few well-characterized model
organisms rather than a new animal per study. SMN-Lab adopts the same discipline
with one synthetic organism, and insists that its form be *derived* rather than
chosen for convenience. The derivation runs from movement. In an overdamped world —
the regime of small bodies, where drag dominates and nothing coasts — Purcell's
scallop theorem forbids net displacement to any body with a single reciprocating
degree of freedom. The smallest body that can therefore *initiate non-inertial
movement* is a three-segment axial chain: two joints, whose phased motion traces a
non-reciprocal cycle and yields net travel. Below this it cannot go anywhere; at
this size it can carry its sensors *through* the world and ask directional
questions of it. We take this as the minimal body that can *have* a world, and make
it the organism. Scaling is then a parameter (segment count), not a redesign, and
the same data structure describes a three-block crawler and a many-block one;
appendages are branches of the same segmental graph.

### 2.2 The Coordinated Action Zone: opposition, dual interface, morphological computation

The elementary unit is the **Coordinated Action Zone (CAZ)**: an antagonistic,
*pull-only* opponent pair spanning a joint, which both moves the joint and senses
its state — a single dual-interface element, not separate sensor and motor. Two
commitments make the CAZ more than a controller.

First, the agent is placed in a **gravitational field treated as a structural
prior** — an ambient, directional ordering constraint the body does not choose and
cannot leave. The CAZ's antagonism is organized to *oppose* this field (and the
forces of the medium): the opponent pair holds a **dynamic equilibrium** — a
balance of physical forces — and action is a departure from that balance, not a
command issued into a void. Posture, before anything else, is the work of opposing
gravity; movement is a modulation of the balance. This makes the unit of control a
*balance to be shifted* rather than a torque to be applied, and it locates the
agent's elementary cognitive act in mechanics, not in a model.

Second, control is **morphological computation**: a network of CAZs coupled along
the body performs the work that a central controller would otherwise do. Locomotion
is not commanded trajectory-by-trajectory; it is a traveling wave that the coupling
*and the body's mechanics in its medium* together produce. The body is not a plant
driven by a brain; it is the computer.

### 2.3 The messaging beam

CAZs are coupled by a **messaging beam** — nearest-neighbor phase coupling
(a Kuramoto-type chain, the formal model the SMN preprint specifies). From local
coupling alone a coherent traveling wave emerges, with no centre; a bilateral
sensory gradient biases it into directed movement. The beam is also where the
network's shared state lives: the world model is not stored in any one segment but
*between* the segments, in the coupled state the beam maintains — and, by the same
token, the **world model is constructed in the agent's own body geometry**, a
body-relative frame rather than a god's-eye coordinate system. What an agent can
differentiate about its world is a property of how its zones are placed and coupled,
not of a transducer count.

### 2.4 The diagram grammar

Every agent is drawn in one **diagram grammar**, so that morphology, sensors, and
coupling can be read at a glance and compared across experiments. Segments are
blocks; a CAZ is a split circle (the opponent pair; its split orientation encodes
the degree of freedom); sensors are unfilled circles mounted inside the body;
localizers are literal anterior icons; the coupling network is drawn in one colour.
Crucially the same **body schema is the single source of truth** for both the
simulated body and its figures — a published diagram cannot drift from the code that
ran. The grammar borrows the field's recognizable conventions (kinematic chains,
Braitenberg-style front sensors, color-coded channels) and adds one glyph of its
own for the concept that lacked a standard.

### 2.5 The engine boundary

A strict boundary separates the **physics engine** from the **architecture**. The
engine supplies rigid-body dynamics, contact, actuation, and raw sensor primitives;
the architecture supplies the CAZs, the messaging beam, the action patterns, and the
constructed world model. Modalities the engine does not simulate — chemical and
thermal fields — are computed bench-side as virtual scalar fields sampled at the
body's sensor sites. The boundary keeps backend assumptions out of the theory and
keeps the bench portable: MuJoCo is a good default, not the architecture.

### 2.6 Pre-registration and matched foils

Every experiment is **pre-registered**: hypothesis, order parameter, a matched
control, and pass/fail are fixed *before* running, in a public test plan. Two
disciplines make the test real. The **matched non-modulatory foil** is identical to
the experimental agent except for the one thing the SMN theory says matters
(coupling, or per-zone modulation); a result the foil also produces is not evidence
for the architecture. And **replicated seeds** with reported spread replace the
single illustrative run. Adjustments forced during an experiment — and especially
anything beyond the published architecture — are declared explicitly; confounded
runs are discarded, not reported.

### 2.7 The bench as a generative model

The bench is not a fixed set of results but a **generator**. A sweep harness runs an
experiment across a parameter grid and a seed ensemble and writes self-describing
data: a tidy table (one row per run: parameters, seed, metrics), a long-format
time-series file, and a manifest stamping the grid, the seeds, and the exact code
commit. Every run is reproducible and the data are openly available — so the
"small-data" objection dissolves: a collaborator can sweep the grid as wide as they
like and re-analyze with their own tools.

---

## 3. Instrument description  *(outline)*

- Architecture → simulation mapping (table).
- The modules: `crawler` (the body + the anisotropic medium), `morphology` (the
  schema + the diagram grammar), `control` (`MessagingBeam`, `OpponentBoard`,
  reafference, the action-pattern layers), `fields` (virtual scalar fields),
  `sweep` (the harness), `viz` (the beam + its dynamic state).
- Building an agent from a schema; the Streamlit lab interface.

---

## 4. Validation — the instrument in use  *(outline)*

The C-series demonstrations, each with its raw-data → math → figure chain:

- locomotion as a network effect (coupling sweep);
- a body-relative world model — and the *corrected* prediction that it does not
  scale with raw geometry;
- modulation and the **resolution principle** (resolution scales with CAZ density
  only with modulation);
- self/world discrimination by reafference;
- the three reproduced architectural predictions (haltability signatures, zonal
  dissociations, antagonistic benefits).

**The ledger.** Across the nine pre-registered studies the architecture was
confirmed about as often as it was corrected, and three confounded runs were caught
and discarded before reporting. This is the instrument doing its job — *risking* the
theory — and the central evidence that the bench is a test, not an illustration.

---

## 5. Discussion & positioning  *(drafted in part)*

- **Instrument that tests vs principle that absorbs.** Position against active
  inference / the free-energy principle (often held to be unfalsifiable, which is
  why it absorbs every mechanism) and the equilibrium-point hypothesis / hybrid
  generative models (genuine points of contact). The bench's contribution is that
  it makes architectural claims *falsifiable*.
- **Lineage.** Braitenberg's vehicles; Beer's minimally cognitive agents; Pfeifer &
  Bongard on morphological computation; Di Paolo, Buhrmann & Barandiaran on
  enactive sensorimotor life; Froese on enactive cognition and minimal perception.

### 5.x Can a simulation be embodied? (the irony, stated)

SMN-Lab embodies an obvious irony: it offers an *embodied* agent inside a
*simulation*. We state it plainly rather than finesse it. A simulation is not a
body and has no phenomenology; nothing here is claimed to feel anything. What MuJoCo
does provide is **real physics** — gravity, contact, drag, opponent forces — and
what the bench instantiates is the *structural and relational* conditions that the
SMN architecture holds to constitute object-directedness: a body-relative frame,
the reafferent separation of self from world, the dual interface that measures
while it moves, and the halt at resistance through which an object announces itself
as *other*. These conditions are exactly what a physics simulation *can* carry, and
they are what our experiments measure. The felt, first-person character of
experience is neither captured nor claimed. The bench therefore tests the
*signatures* of embodiment and object-directedness, not their phenomenology — and we
take the value of stating that boundary precisely to outweigh the discomfort of the
irony. Whether the structural signatures we can reproduce are *sufficient for*
phenomenology, or merely *necessary*, is the open question the instrument is built
to sharpen, not to settle.

---

## 6. Availability, reproducibility, limitations, roadmap  *(outline + drafted item)*

- Open source (GPL-3.0); docs; seeded, commit-stamped datasets; a DOI for a frozen
  snapshot.
- Limitations: planar idealizations in the current studies; a single organism
  family; phenomenology not addressed (Section 5.x).

### 6.x Perceptual crossing and the Enactive Torch in simulation  *(drafted)*

The **Enactive Torch** (Estelle et al.; Froese et al.) is a hardware
sensory-substitution device that converts distance into vibration so that a user
perceives by active exploration. SMN-Lab is its computational sibling — a
*synthetic* body rather than an *augmented* one — and the same sensory-substitution
"feel" can be staged in an agent whose coupling we fully control. A natural first
social experiment is **perceptual crossing** (Auvray, Lenay & Stewart, 2009): two
agents move sensors along a shared line, each receiving a contact signal when it
crosses the other; the question is whether an agent can distinguish another
*responsive* agent from a non-responsive lure by the **dynamics of mutual
interaction** alone. Reproducing perceptual crossing in SMN-Lab would extend the
instrument from object-directedness to *other*-directedness — and it probes exactly
the boundary named in Section 5.x, since "detecting another perceiver" is here a
dynamical signature of interaction, not a phenomenal report.

---

## 7. Conclusion  *(outline)*

A minimal synthetic organism, a small set of design commitments, and a discipline of
pre-registration turn an embodied-cognition architecture into something testable. The
instrument's value is that it can be wrong — and sometimes is.

---

## Appendices  *(outline)*
- **A.** Architecture → simulation mapping.
- **B.** Metric definitions (the data → math → plot tables, per experiment).
- **C.** Diagram-grammar reference.

## References to add
SMN preprint (Nagarjuna & Karnam, arXiv:2605.26856); Enactive Torch (Estelle,
Dayantri, Meng, Morrissey & Froese, SSRN 5749009); Purcell (1977), *Life at low
Reynolds number*; Braitenberg (1984); Beer (e.g. 2003); Pfeifer & Bongard (2006);
Di Paolo, Buhrmann & Barandiaran (2017); Auvray, Lenay & Stewart (2009); Froese &
Di Paolo on perceptual crossing; Friston (FEP) and Latash (EPH) for positioning.
