# Diagram grammar

Every C-series figure that describes an agent's geometry uses one consistent
visual grammar, so a reader who learns it once can read all of them. There is no
single community standard for *morphology + sensors + coupling* as one notation,
so the grammar borrows the recognizable conventions of the field where they exist
(kinematic trees, Braitenberg-style front sensors, color-coded channels) and uses
one glyph of our own — the **dual-interface zone** — where the SMN concept has no
standard.

The diagrams are **generated from the body schema** (`smn_lab/morphology.py`),
which shares its parameters with the MuJoCo body builder
(`smn_lab/crawler.py`). A published figure therefore cannot drift from the code
that ran.

![The SMN diagram grammar — the A3 axial crawler, with every glyph labeled](figures/diagram_grammar.png)

## The glyphs

| Element | Glyph | Notes |
|---|---|---|
| **Segment (block)** | rounded rectangle | the head is shaded distinctly; the chain runs head → tail |
| **Zone** | a circle, **half filled / half unfilled** | *our notation*: the dual-interface unit — the filled half is the **acting** interface, the unfilled half the **sensing** interface |
| **CAZ** | an **opposed pair of zones** | the two sensation modulators, facing each other across the inter-segment joint (the opponent pair) |
| **Messaging beam** | dashed line linking the CAZs | the coupling that maintains the shared state-space |
| **Ventral touch skin** | hatched outline (orange) | contact-force skin on the segment's ventral face |
| **Field / gradient strip** | a row of color-coded ticks on each lateral edge | distributed, bilateral; color = modality (see legend) |
| **Localizer (eye / ear)** | a literal paired icon at the anterior | distal modality; its placement is what marks the front |

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

## The description language

Each body has a compact textual spec that maps one-to-one onto the diagram and
onto the builder parameters:

```
organism A3 {
  axis: anterior=+x
  seg head { mass; skin:ventral; strip:[chem,thermal]@bilateral; eye:pair@anterior }
  caz  j1  { pair_of_zones }
  seg s1   { mass; skin:ventral; strip:[chem,thermal]@bilateral }
  caz  j2  { pair_of_zones }
  seg s2   { mass; skin:ventral; strip:[chem,thermal]@bilateral }
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
