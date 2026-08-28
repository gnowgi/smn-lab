# The earthworm — a segmented hydrostat

!!! abstract "The segmented rung"
    The earthworm is the **segmented** rung of the [worm ladder](../ladder/overview.md). Its body
    wall is **two disjoint muscle tissues** — a thin **circular** layer (segmental, interrupted by
    the septa) and a thick **longitudinal** layer (continuous along the body, in bundles) — woven
    around a **segmented hydrostatic skeleton**. The two tissues share no muscle, yet they are
    **opponents** through the coelomic fluid: this is the earthworm's primary CAZ, the **telescoping**
    pair that drives **peristalsis**. It is also the first rung to face **gravity** directly. Model:
    `experiments/earthworm.py`.

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

## Run it

```bash
python experiments/earthworm.py
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
