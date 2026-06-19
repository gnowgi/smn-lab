# Diagram grammar

Every C-series figure that describes an agent's geometry uses one consistent
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
- **Network view** — *who couples to whom*: the same layout with light-blue
  coupling lines — each sensor to its CAZ, and CAZ to CAZ along the body (the
  messaging beam). The body is drawn faintly underneath, because the network is
  grounded in body geometry, not abstracted away from it.

![The SMN diagram grammar — morphology view, network view, and the CAZ/DOF key](figures/diagram_grammar.png)

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
- **Nesting** — a single *flexible* part is a chain of small rigid sub-segments in
  series. This is the answer to the natural objection "your segments are rigid, so
  how can a part bend?": a finger or a tail is flexible **because** it is many rigid
  links jointed together. Flexibility is nested segmentation, not a new primitive.
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

The grammar makes the [Lesson 1](lesson1.md) ladder legible at a glance — each
new block (and its CAZ) unlocks the next epistemic transition:

![The 1/2/3-block morphological ladder: object → self/world → aboutness](figures/morphology_ladder.png)

## Regenerating the figures

```bash
cd experiments && ../.venv/bin/python morphology_figs.py   # grammar + ladder
cd experiments && ../.venv/bin/python menagerie_figs.py     # the menagerie
```
