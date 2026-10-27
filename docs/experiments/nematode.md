# The nematode — a tube that bends

!!! abstract "The tubular rung"
    The nematode is the **tubular** rung of the [worm ladder](../ladder/overview.md). Two things
    happen here that the cnidarian did not have. First, the muscle **detaches** from the body: where
    the cnidarian was one epitheliomuscular mesh, the nematode separates into **three tissues** — a
    passive **skin** (carrying the sensors), a passive **gut** (no muscle at all), and a detached
    **muscle** riding on the skin. Second, that muscle is **longitudinal only** — there is **no
    circular muscle** — so the animal's degree of freedom is a **dorsoventral bend**, opposed by the
    elastic cuticle. Model: `experiments/nematode.py`.

## The body as modelled

![Nematode body plan — a cross-section at one station (eight-node skin ring, four detached muscle quadrants, four-node gut ring) beside the unrolled side view of all twelve stations, with the transducers marked; the gut tube is joined to nothing](../figures/nematode_body_plan.png)

How to read it. On the left, one station in true cross-section: the eight-node **skin** ring,
the four detached **muscle** quadrants just inside it (two subdorsal, two subventral), and the
four-node **gut** ring at the centre. On the right, the whole body unrolled: each tube cut
along one line and laid flat, twelve stations from head (left) to tail, each tissue in its own
band. Heavy lines are the actuated muscle `f`s (longitudinal chains, the pharyngeal fan at the
mouth, the anal pair at the tail); light lines are passive. Every skin node carries a touch
transducer; the orange rings and yellow triangles mark the added temperature transducers and
photoreceptors (photoreceptors denser toward the head).

!!! warning "The gut, as modelled, is not attached to the animal"
    The body graph has **two connected components**: a 147-node animal (skin, muscle, mouth,
    anus) and the 48-node gut tube, which no link joins to the skin, the mouth or the anus. In
    the worm the gut opens at the pharynx and the anus. Here it is a separate passive tube
    floating inside the body, which is why its band in the figure has no line reaching it. The
    undulation demo below is unaffected (the gut carries no muscle and takes no part in the
    bend), but any experiment that reads the gut, or counts on it as part of the body, would
    not be. Attaching it is left to its own change, because it alters the committed demo.

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

## 4 · The self-model — measured, and it mostly fails

The demo above never asks whether the nematode can recover its own body from its own
movement. Here that is measured with the disk's procedure, unchanged: random pull-only drive on
every actuated `f`, then the `endpoint` read-out, which takes each `f`'s two most strongly
co-moving segments as its endpoints.

![The nematode's self-model on its unrolled body: six of the 44 longitudinal muscle f's and both anal f's are recovered (green); the rest are misread, most often as a pair of skin nodes (red)](../figures/nematode_self_model.png)

!!! failure "Endpoint recovery 0.15 (8 of 54 actuated `f`s)"
    Longitudinal muscle 6/44, pharyngeal radial 0/8, anal 2/2. In 32 of the 46 misses the
    read-out names two **skin** nodes; in the other 14, one muscle node and one skin node.
    For comparison, the same procedure gives 0.86 on the [medusa](medusa.md) and 0.93 on the
    [earthworm](earthworm.md).

Why it fails is **not established**. It is suggestive that the failure falls on the nematode's
defining feature: its muscle is detached from the skin and rides on it through stiff attachment
links, so a muscle's pull shows up most strongly in the skin it drags rather than in its own
two endpoints. That reading is a hypothesis, not a result.

Two limits hold for any worm with this read-out. It has one row per **actuated** `f`, so it can
recover the muscle network only: the 324 passive links (skin rings, cuticle, attachments, gut)
are outside its reach by construction. And the babble runs with no medium, so it says nothing
yet about the self-model of a worm moving through a world.

## No world-model yet

!!! info "No world-model on this rung yet"
    This experiment has no world in it: no source, no object, no field, and the skin transducers are
    never read. So there is nothing to visualize as a world-model, and none is drawn. A
    world-model here would be a new experiment with its own pre-registration (the medusa's
    razor carried to the tube), not a picture of this one.

## Run it

```bash
python experiments/nematode.py
python experiments/worm_self_model.py   # body plans and self-models, both worms
```

Prints the three-tissue structure and the opponent pairs, and writes `figures/nematode.png`. The
file is self-contained.

## Sources

Body-wall muscle is longitudinal-only in four quadrants, producing a dorsoventral bend with the
cuticle/hydrostat as the passive antagonist:
[WormAtlas — somatic muscle](https://www.wormatlas.org/hermaphrodite/musclesomatic/MusSomaticframeset.html);
[Neurobiology of *C. elegans* locomotion, *BioScience* 64(6):476](https://academic.oup.com/bioscience/article/64/6/476/289633).
