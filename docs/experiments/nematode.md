# The nematode — a tube that bends

!!! abstract "The tubular rung"
    The nematode is the **tubular** rung of the [worm ladder](../ladder/overview.md). Two things
    happen here that the cnidarian did not have. First, the muscle **detaches** from the body: where
    the cnidarian was one epitheliomuscular mesh, the nematode separates into **three tissues** — a
    passive **skin** (carrying the sensors), a passive **gut** (no muscle at all), and a detached
    **muscle** riding on the skin. Second, that muscle is **longitudinal only** — there is **no
    circular muscle** — so the animal's degree of freedom is a **dorsoventral bend**, opposed by the
    elastic cuticle. Model: `experiments/nematode.py`.

## 1 · The differentiation event — one mesh becomes three tissues

In the cnidarian, every cell is muscular and the single mesh does action, structure, and (with
transducers) sensing all at once. In the nematode that unity breaks:

- the **skin** is a passive epithelial tube carrying the transducers — **touch** all over,
  **temperature** interspersed, diffuse **photoreceptors** denser toward the head (no eyes);
- the **gut** is a passive tube of cells with **no muscle**;
- the **muscle** has detached into discrete longitudinal pieces that ride on the skin.

This is the **layering** the ladder predicts at this step: one functional network becomes several.

## 2 · The opponent pair — dorsoventral, and no circular muscle

The body-wall muscle is **longitudinal only**, arranged in **four quadrants** (two subdorsal, two
subventral). There is **no circular muscle**. So the CAZ — the opponent pair that actuates a degree
of freedom — is **dorsal-longitudinal ⊕ ventral-longitudinal**, and the animal bends in the
**dorsoventral** plane (it lies on its side, so the bend reads as a sinusoid). The **passive
antagonist** — the side that restores the bend — is the elastic **cuticle** plus hydrostatic
pressure and resting muscle tone; puncturing the cuticle drops body stiffness ~18%.

!!! note "Contrast with the earthworm (don't get this backwards)"
    The nematode **has** a dorsoventral opponent pair and **no circular** muscle. The
    [earthworm](earthworm.md) is the opposite: it **has** circular muscle (a circular⊕longitudinal
    *telescoping* pair) and **no dorsoventral** muscle. Reading the nematode's four longitudinal
    strands as four independent "CAZ" would miss that its real degree of freedom is the DV opponent
    pair — the kind of interpretation error the [CAZ ontology](../ladder/opponent_pair_caz.md) exists
    to prevent.

Two further opponent pairs complete the animal: the **mouth** is radial pharyngeal fibres ⊕ elastic
recoil (the pump), and the **anus** is a dorsoventral muscle-cell pair.

## 3 · The bend travels — a dorsoventral undulation

Driving the dorsal and ventral sides **anti-phase** (the opponent pair) with a wave that travels
head→tail produces a travelling **dorsoventral bend** — the nematode's locomotor gait. The centreline
deflection shows the wave marching down the body; the body midline is a travelling sinusoid.

![Nematode DV undulation — the dorsal/ventral opponent pair driven anti-phase makes a dorsoventral bend that travels head to tail; the body midline is a sinusoid](../figures/nematode.png)

!!! warning "Amplitude is modest"
    The free tube is stiff in bending, so the modelled undulation is small (~0.5× body radius). The
    **mechanism and structure are correct** — a DV opponent pair with no circular muscle — but a
    softer cuticle and ground anchoring are needed to render a large, clean sinusoid.

## Run it

```bash
python experiments/nematode.py
```

Prints the three-tissue structure and the opponent pairs, and writes `figures/nematode.png`. The
file is self-contained.

## Sources

Body-wall muscle is longitudinal-only in four quadrants, producing a dorsoventral bend with the
cuticle/hydrostat as the passive antagonist:
[WormAtlas — somatic muscle](https://www.wormatlas.org/hermaphrodite/musclesomatic/MusSomaticframeset.html);
[Neurobiology of *C. elegans* locomotion, *BioScience* 64(6):476](https://academic.oup.com/bioscience/article/64/6/476/289633).
