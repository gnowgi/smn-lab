# The earthworm — a segmented hydrostat

!!! abstract "The segmented rung"
    The earthworm is the **segmented** rung of the [worm ladder](../ladder/overview.md). Its body
    wall is **two disjoint muscle tissues** — a thin **circular** layer (segmental, interrupted by
    the septa) and a thick **longitudinal** layer (continuous along the body, in bundles) — woven
    around a **segmented hydrostatic skeleton**. The two tissues share no muscle, yet they are
    **opponents** through the coelomic fluid: this is the earthworm's primary CAZ, the **telescoping**
    pair that drives **peristalsis**. It is also the first rung to face **gravity** directly. Model:
    `experiments/earthworm.py`.

## The body as modelled

![Earthworm body plan — a cross-section of one segment (outer circular square, inner longitudinal square, ventral ganglion) beside the unrolled side view of all six segments with every link kind](../figures/earthworm_body_plan.png)

How to read it. On the left, one segment in true cross-section: four **circular** nodes on the
outside, four **longitudinal** nodes inside, and the segmental **ganglion** below, joined by
radial hydrostat struts and ganglion spokes. (The diagonal struts join neighbouring segments,
so they appear only in the side view.) On the right, all six segments
unrolled, head left, each tissue in its own band. The **circular** muscle `f`s run *round* each
segment, so in the unrolled view they are the heavy red verticals (with dotted stubs where a
ring closes round the body). The **longitudinal** muscle `f`s run *along* the body: the heavy
blue horizontals. Everything light is passive. The model has 54 nodes and 205 links, of which 44
are actuated, all in one connected body.

## 1 · Two disjoint muscle tissues, woven

Sourced anatomy: the circular layer is *divided into rings by the intersegmental grooves* — it is
**segmental**; the longitudinal layer *runs without interruption across segment boundaries* — it is
**continuous**, in several bundles. The two tissues **share no muscle cell** (`V_circ ∩ V_long = ∅`);
unwrapped, they cross like a **cross-woven fabric**. There is **no oblique and no dorsoventral
muscle** (that is a leech/slug elaboration, below).

## 2 · Two opponent pairs — telescoping and lateral bend

- **Telescoping CAZ** (per segment) = **circular ⊕ longitudinal**, opposed through the coelomic
  **hydrostat** at fixed volume: circular contraction narrows-and-elongates a segment, longitudinal
  contraction shortens-and-widens it. Sequenced along the body, this is the **peristaltic wave** —
  the earthworm's propulsion. (Circular's antagonist is the *longitudinal*, not the adjacent circular
  ring: rings are **sequenced** in the wave, not opposed.)
- **Lateral-bend CAZ** (per segment) = **left-longitudinal ⊕ right-longitudinal** → **turning**.
- **No dorsoventral pair** — the earthworm has no dorsoventral muscle.

## 3 · The demos — a peristaltic wave and a turn

Sequencing the telescoping pairs (a longitudinal shortening wave) produces a travelling peristaltic
wave down the body; driving the lateral-bend pair (left longitudinal contracted, right relaxed) bends
the body into a turn.

![Earthworm — a peristaltic wave from the telescoping pairs sequenced head to tail, and a turn from the lateral-bend pair](../figures/earthworm.png)

## 4 · Why the segmented rung matters — gravity adds an opponent axis

The earthworm is the **first rung to face gravity directly**. Earlier animals were aquatic, with
water buffering gravity; the terrestrial annelids work a **segmented hydrostatic skeleton against
gravity and a substrate**. The septa isolate each segment's coelom at fixed volume, which is what
lets a local circular⊕longitudinal contraction do useful work. The three body relations are now built
in as **axes**: antero-posterior (a head→tail identity gradient), **dorsoventral polarity** (dorsal ≠
ventral in identity — though not yet a muscle antagonist), and left-right **reflection** symmetry.

Up the next rung, the dorsoventrally flattened forms — **leeches and slugs** — add a **dorsoventral
muscle** opponent pair (and oblique muscle). So **gravity adds the dorsoventral opponent axis** one
rung later: a clean instance of the ladder's rule that each grade adds an opponent axis.

## 5 · The self-model — measured, and it largely recovers the muscle network

The demos never ask whether the earthworm can recover its own body from its own movement. Here
that is measured with the disk's procedure, unchanged: random pull-only drive on every actuated
`f`, then the `endpoint` read-out, which takes each `f`'s two most strongly co-moving segments as
its endpoints.

![The earthworm's self-model on its unrolled body: all 20 longitudinal f's and 21 of 24 circular f's are recovered (green); the three misses are circular f's misattributed to a ganglion (red)](../figures/earthworm_self_model.png)

!!! success "Endpoint recovery 0.93 (41 of 44 actuated `f`s)"
    Longitudinal 20/20, circular 21/24. All three misses are circular `f`s that the read-out
    attributes partly to a ganglion, the segmental node that spokes join to both tissues.

What it recovers is worth stating precisely. The read-out has one row per **actuated** `f`, so
the self-model is the muscle network only: six circular rings and four longitudinal bundles.
The 161 passive links, including the hydrostat struts through which the two tissues oppose each
other, are outside its reach by construction. So the earthworm recovers *both halves* of its
telescoping CAZ but not, by this read-out, the coupling that makes them opponents. The babble
runs with no medium and no gravity.

## No world-model yet

!!! info "No world-model on this rung yet"
    This experiment has no world in it: no source, no object, no field, and the body's transducers (none are defined in this model) are
    never read. So there is nothing to visualize as a world-model, and none is drawn. A
    world-model here would be a new experiment with its own pre-registration (the medusa's
    razor carried to the segmented hydrostat), not a picture of this one.

## Run it

```bash
python experiments/earthworm.py
python experiments/worm_self_model.py   # body plans and self-models, both worms
```

Prints the two-tissue structure and the opponent-pair CAZ, runs the peristalsis and turn demos, and
writes `figures/earthworm.png`. The file is self-contained.

## Sources

Circular (segmental) and longitudinal (continuous) muscle acting antagonistically through the
coelomic hydrostat, peristaltic locomotion; no dorsoventral muscle (leeches add six muscle layers):
[Britannica — skeletomusculature of an earthworm](https://www.britannica.com/science/skeleton/Skeletomusculature-of-an-earthworm);
[Britannica — annelid locomotion](https://www.britannica.com/animal/annelid/Locomotion);
[Fox / Lander — *Lumbricus terrestris*](https://lanwebs.lander.edu/faculty/rsfox/invertebrates/lumbricus.html);
[Anatomy of *Hirudinaria* (leech)](https://www.bioscience.com.pk/en/topics/zoology/anatomy-of-hirudinaria).
