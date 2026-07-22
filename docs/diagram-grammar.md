# Diagram grammar

Every agent figure that describes its geometry uses one consistent
visual grammar, so a reader who learns it once can read all of them. There is no
single community standard for *morphology + sensors + coupling* as one notation,
so the grammar borrows the recognizable conventions of the field where they exist
(kinematic trees, Braitenberg-style front sensors, color-coded channels) and uses
one glyph of our own — the **split-circle CAZ** — where the SMN concept has no
standard.

The diagrams are **generated from the body schema** (`smn_lab/morphology.py`),
which shares its parameters with the MuJoCo body builder (`smn_lab/crawler.py`). A
published figure therefore cannot drift from the code that ran.

## Two views of one body

The grammar gives the same body **two views**, sharing one vocabulary:

- **Morphology view** — *where things are mounted*: the head-to-tail chain of
  segment blocks, with **sensors mounted inside each block** and a CAZ glyph at
  each inter-segment joint.
- **Two-network view** — *the mechanical body and the messaging canvas*: the same
  body drawn as two coupled networks — the mechanical network above, the one
  broadcasting canvas (IN) below, joined through the DFN. This is the paper's
  Figure 2; it is expanded in [The two networks](#the-two-networks--body-and-canvas)
  below.

![The SMN diagram grammar — morphology view, the two-network view, and the CAZ/DOF key](figures/diagram_grammar.png)

## The two networks — mechanical and messaging

Beyond the two *views* above, a fuller figure shows the two *networks* an SMN
agent is made of, generated from the schema by `render_two_network(ax, schema)`:

![The two networks — the mechanical body and the single broadcasting canvas](figures/two_network_grammar.png)

### Which nodes, which edges?

The agent is one SMN, but "network" is answered at three levels — spell out the
nodes and edges of each and the ambiguity dissolves:

| level (criterion) | nodes | edges | count |
| --- | --- | --- | --- |
| **substrate** (what the tissue is) | actuators (motor tissue), sensors, integrators (neurons/boards) | couplings (synapses) | **one** signal graph, 3 node-kinds |
| **state** (what has its own dynamics) | *mechanical:* segments · *messaging:* CAZ boards (+ sensors as sources) | *mechanical:* actuators (a joint's opponent pair) · *messaging:* afferents + broadcast (Π) | **two** networks |
| **function** (what the messaging net computes) | — | — | **two** operators: DFN, IN |

The **CAZ** is the shared vertex: it is an actuator **edge** of the mechanical
network *and* a board **node** of the messaging network. That double role is the
point, not a slip — a muscle is at once a *thing* (an actuator node of the signal
graph) and a *connection between two segments* (an edge of the mechanical network),
so the mechanical network is the **dual**, on its actuator sub-part, of the signal
graph. Whether you say **two** networks or **three** graphs is only where you put
the sensors: fold them into the messaging network as afferent sources → two;
separate them → a *graph of three graphs* (kinematic, sensory, messaging). We lead
with **two**, because each of the two has its own state and the sensory graph has
none of its own.

### The figure: the mechanical network above, the messaging network (DFN + IN) below

- The **mechanical network** (top) — segments (nodes), actuators (edges, a joint's
  opponent pair = one CAZ = one DOF), the dual-interface CAZ, and the
  single-interface transducers (the major source of data).
- The **messaging network** (below) is drawn as its **two functional
  sub-networks**, distinguished by function not location:
    - the **DFN — differentiating + filtering** (middle band): where the **sensory
      bundle and the motor efference MEET**, and where the modulation filter **α
      (C4)** acts — *only modulated data enters* (a stream is admitted only if it is
      a predicted consequence of the board's own action, which is why α needs the
      efference and lives here, not on the raw sensory bundle);
    - the **IN — integrating** (bottom): the one broadcasting **canvas**. The DFN's
      *filtered output enters the canvas*; the canvas integrates it into the held
      snapshot, which every board reads back (network closure). It does **not**
      drive the actuators: the CAZs regulate one another through the DFN —
      coordination is peer-to-peer, not central command (C3).

Two glyph notes:

- **Colour-coded channels, no riding the actuator.** Single-interface transducers
  reach the DFN through their own colour-coded channels (bundled), not through the
  CAZ half-circle — sensors are their own graph.
- **The eye is an orbit unit, not a bare sensor.** A visual transducer is drawn on
  an **orbit** (a small segment) carrying several **extraocular CAZ pairs**, with
  its own bundle to the DFN — because vision is the paradigm **sensorimotor
  contingency**: its data is constituted by the eye's own movement, not passively
  received.

**Regions on the canvas are constructed, not given — and they are drawn as an
emergent digraph, not stipulated bands.** A small, unbranched agent has **one
undivided canvas**. As the body grows, the canvas's **layers emerge** from the
dependency structure of the messaging graph: a directed digraph whose strata are
*derived* (longest dependency path from a small, interconnected visceral core),
node size = degree/weight, colour = emergent stratum. The **number of layers is
never stipulated** — it emerges (right panel; `render_emergent_canvas`). This is
the constructive commitment made literal, and the phenomenon tested in the
canvas-regions study.

## The glyphs

| Element | Glyph | Notes |
|---|---|---|
| **Segment (block)** | rounded rectangle | a body block with mass; the head is shaded; the chain runs head → tail |
| **Sensor** | an **unfilled marker whose shape encodes the modality** (colour is a redundant cue) | a single-interface transducer, drawn **inside** the segment it is mounted on; bilateral sensors give an L node (upper inside) and an R node (lower inside). Shapes keep modalities distinguishable on a black-and-white display or for colour-blind readers |
| **CAZ** | **one circle split in half** — one half filled (flexor), one half unfilled (extensor) | the opponent pair actuating **one degree of freedom**. *Every CAZ is dual-interface (it both senses and acts); that is defined here, not drawn.* |
| **Localizer (eye / ear)** | a literal paired icon at the anterior face | a distal sensor; its placement is what marks the front |
| **Coupling / network** | **light-blue lines** | sensor → CAZ and CAZ ↔ CAZ — one color for "these nodes talk" |

## CAZ and degrees of freedom

The CAZ is the one glyph of our own. A **Coordinated Action Zone is one
flexor/extensor opponent pair = one degree of freedom**. A joint between two
bodies admits at most six DOF (three rotational, three translational); the four
that matter for creatures, and their glyphs:

| DOF | motion | axis | glyph |
|---|---|---|---|
| **yaw** | lateral bend (turn L/R) | dorsoventral | circle, **vertical split** |
| **pitch** | dorsoventral bend (up/down) | lateral | circle, **horizontal split** |
| **roll** | axial twist | anteroposterior | circle, **curved double-arrow** |
| **telescoping** | axial extend/contract (peristalsis) | anteroposterior | circle, **straight double-arrow** |

The two **bending** DOFs read as a split circle (split orientation = the bend
axis; filled half = flexor, unfilled = extensor). The **twist** and **axial**
DOFs read as a double-headed arrow showing the two opposing pulls (curved for
twist, straight along the body for length).

A joint's degrees of freedom are read directly off its CAZ glyphs:

- a **single CAZ** → a single-DOF joint;
- **two CAZs of different kind** → a multi-DOF joint (e.g. yaw + pitch);
- **two CAZs of the same kind** → a redundant pair adding force on one DOF.

This is why segments that share a single DOF show only one CAZ: the CAZ is always
a pair (the two opposing pulls), and adding another CAZ adds either a new DOF or
additive force — never a lone actuator.

!!! note "One archetype drawn; a second deferred"
    The split-circle glyph draws the **skeletal** CAZ — a flexor/extensor opponent
    pair across a rigid lever. There is a second archetype the grammar does **not**
    yet draw: the **hydrostatic** CAZ — *linked linear actuators* with no skeleton,
    whose antagonist is the structure itself (constant volume / turgor), as in a
    worm, tongue, or gut. It is a known, deliberately deferred extension (not needed
    for the current results); see the *physics at every layer* design note.

## Building complex agents — and extending the grammar

The grammar is meant to compose *complex* creatures from these few components.
What the current components already support:

| locomotion | recipe | status |
|---|---|---|
| **swimming** (undulatory) | yaw wave + anisotropic medium | ✓ (see [C0](experiments/c0_crawler.md)) |
| **crawling** (undulatory) | yaw wave + ground contact | ✓ (see [C1](experiments/c1_touch.md)) |
| **crawling** (peristaltic) | telescoping DOF + anchoring | DOF ✓ · anchor → roadmap |
| **walking** | branching legs (multi-DOF) + load contact | branching → roadmap |
| **flying** | branching wings + roll + a lift medium | branching/medium → roadmap |

The remaining needs are **extensions within the same abstractions**, not changes
to them — which is why the grammar can be treated as final and grown as
experiments demand:

- **Branching** — appendages (legs, wings, fins, antennae) are sub-chains that
  branch off the axial chain. *A body is a graph of segments; a branch is a segment
  attached to a segment.* The schema is a tree rather than a list; the node types
  are unchanged.
- **Nesting (two senses).** *(i) Flexibility-nesting* — a single *flexible* part is a
  chain of small rigid sub-segments in series (a finger or a tail bends **because** it
  is many rigid links jointed together; flexibility is nested segmentation, not a new
  primitive). *(ii) Scale-recursion nesting* — a different, later idea: a lattice whose
  nodes are themselves lattices, so the **same self-model read-out recovers the body at
  every level** (segments → blocks → super-blocks). See the
  [nested lattice](experiments/nested_lattice_self_model.md). The grammar here draws the
  *flexibility* sense; the *scale* sense is a property of the read-out, not a new glyph.
- **Anchor / gripper** — an *actuated* contact (a foot that grips and releases, a
  sucker, setae) for peristalsis, inchworming, and climbing. One more node type,
  alongside the sensor.
- **Medium models** — swimming uses anisotropic drag and walking uses ground
  reaction (both present); flying additionally needs a lift model. This is a
  physics layer, orthogonal to the diagram grammar.

### A menagerie from one grammar

The same primitives — rigid **segments**, **CAZ** opponent-pair joints (whose split
orientation sets the degree of freedom), and shape-coded **sensors** — compose into
very different bodies by four moves: **scale** (add segments), **branch** (a chain
on a segment), **nest** (small segments in series → a flexible part), and
**configure DOF** (choose each joint's CAZ). A worm, a fish, a quadruped, a bird,
and a biped are the *same kit*, assembled differently.

![A menagerie from one grammar — worm, fish, lizard/quadruped, bird, biped, all built by scaling, branching, nesting, and configuring DOF](figures/menagerie.png)

## Fixed conventions

- **Anterior = +x (right)** — matching the crawler code (head = `seg0` at +x). A
  small compass appears in every figure.
- **Top view**, with **L = +y (warm)** and **R = −y (cool)**, matching the body's
  left/right sites.
- One **fixed modality → shape + colour table**, shown as a shared legend. Each
  modality has a distinct **shape** (so it reads on a B/W screen or for colour-blind
  viewers) with colour as a redundant cue:

| modality | shape | color | role |
|---|---|---|---|
| touch | triangle | orange | contact / force (ventral skin) |
| chem | square | green | chemical gradient (field) |
| thermal | pentagon | red | thermal gradient (field) |
| pressure | hexagon | purple | pressure (field) |
| vision | circle | blue | distal — eye (localizer) |
| audio | octagon | teal | distal — ear (localizer) |
| proprio | (circle) | grey | proprioception (internal) |
| *coupling* | *line* | *light blue* | *the network (sensor→CAZ, CAZ↔CAZ messaging beam)* |

## The description language

Each body has a compact textual spec that maps one-to-one onto the diagram and
onto the builder parameters:

```
organism A3 {
  axis: anterior=+x
  seg head { mass; skin:ventral; sensors:[chem,thermal]@bilateral; eye:pair@anterior }
  caz  j1  { dof: lateral }          # one flexor/extensor pair, one DOF
  seg s1   { mass; skin:ventral; sensors:[chem,thermal]@bilateral }
  caz  j2  { dof: lateral }
  seg s2   { mass; skin:ventral; sensors:[chem,thermal]@bilateral }
  beam: nearest_neighbor
}
```

In code this is the `BodySchema` returned by `crawler_schema(...)`; `render_morphology(ax, schema)` draws it.

## The morphological ladder

The grammar makes the [construction-of-experience](construction-of-experience.md) ladder legible at a glance — each
new block (and its CAZ) unlocks the next epistemic transition:

![The 1/2/3-block morphological ladder: object → self/world → aboutness](figures/morphology_ladder.png)

## The self/world card

Any experiment can emit a **self/world card** — three views of the agent in one
visual language, from `morphology.self_world_card(...)`:

1. **The designed agent** (metric) — what we built: segment blocks, a CAZ glyph per
   joint, the messaging beam.
2. **The recovered self-model** (topology) — the *abstract graph* the agent
   reconstructs from its own movement, laid out force-directed from its **own
   recovered adjacency** (never the body's coordinates), with **edge width set by
   the measured coupling** and the branch point ringed. Drawn as plain nodes and
   edges, not a body, so it never looks like a redrawn agent — and it doubles as a
   design-vs-recovered check.
3. **The world in the self-frame** — a field source painted onto the *recovered*
   self-graph, landing on a specific node or limb: the world in the body's own
   frame, never in absolute space.

The three renderers take only positions + edges, so the card works for any
morphology. A branched body and a chain:

![Self/world card for a branched body: designed agent, recovered self-model as an abstract graph, and the world source localized on one limb](figures/self_world_card_branched.png)

![Self/world card for a chain body: designed agent, recovered self-model, and the world localized along the chain](figures/self_world_card_chain.png)

The recovery is `self_model.coupling` / `recover_edges` — each joint (a CAZ) finds
the two segments it hinges because its own angular velocity **is** their yaw-rate
difference; the layout is `morphology.graph_layout`, a small force-directed routine
(no new dependency). See the [self-model](experiments/self_model_topology.md) and
[branched-body](experiments/branched_self_model.md) experiments for the mechanism.

## Regenerating the figures

```bash
cd experiments && ../.venv/bin/python morphology_figs.py   # grammar + ladder
cd experiments && ../.venv/bin/python menagerie_figs.py     # the menagerie
cd experiments && ../.venv/bin/python self_world_card.py    # self/world cards
```
