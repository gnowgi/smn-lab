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
| **Sensor** | an **unfilled circle** with a modality-colored ring | a single-interface transducer, drawn **inside** the segment it is mounted on; bilateral sensors give an L node (upper inside) and an R node (lower inside) |
| **CAZ** | **one circle split in half** — one half filled (flexor), one half unfilled (extensor) | the opponent pair actuating **one degree of freedom**. *Every CAZ is dual-interface (it both senses and acts); that is defined here, not drawn.* |
| **Localizer (eye / ear)** | a literal paired icon at the anterior face | a distal sensor; its placement is what marks the front |
| **Coupling / network** | **light-blue lines** | sensor → CAZ and CAZ ↔ CAZ — one color for "these nodes talk" |

## CAZ and degrees of freedom

The CAZ is the one glyph of our own. A **Coordinated Action Zone is one
flexor/extensor opponent pair = one degree of freedom**, drawn as a single circle
split into a filled half (flexor pull) and an unfilled half (extensor pull). The
**orientation of the split encodes the DOF axis**:

- **vertical split** (left ∣ right) → **lateral bend** (turn left/right);
- **horizontal split** (top ∣ bottom) → **dorsoventral bend** (pitch up/down).

So a joint's degrees of freedom are read directly off its CAZ glyphs:

- a **single split circle** → a single-DOF joint;
- **two circles of different orientation** → a two-DOF joint (e.g. L/R + up/down);
- **two circles of the same orientation** → a redundant pair adding force on the
  one DOF.

This is why segments that share a single DOF show only one CAZ: the CAZ is always
a pair (the two halves), and adding another CAZ adds either a new DOF or
additive force — never a lone actuator.

## Fixed conventions

- **Anterior = +x (right)** — matching the crawler code (head = `seg0` at +x). A
  small compass appears in every figure.
- **Top view**, with **L = +y (warm)** and **R = −y (cool)**, matching the body's
  left/right sites.
- One **fixed modality → color table**, shown as a shared legend:

| modality | color | role |
|---|---|---|
| touch | orange | contact / force (ventral skin) |
| chem | green | chemical gradient (field) |
| thermal | red | thermal gradient (field) |
| pressure | purple | pressure (field) |
| vision | blue | distal — eye (localizer) |
| audio | teal | distal — ear (localizer) |
| proprio | grey | proprioception (internal) |
| *coupling* | *light blue* | *the network (sensor→CAZ, CAZ↔CAZ messaging beam)* |

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
cd experiments && ../.venv/bin/python morphology_figs.py
```
