# The worm ladder — nematode → earthworm

!!! abstract "The proposal"
    After the cnidarian (the [polarized rung](../cnidarians.md)) the ladder climbs through the
    **worms**. Each rung elaborates the **body plan**, and each elaboration adds two things at once:
    a new **tissue differentiation** and a new **opponent axis** (a new kind of degree of freedom).
    The two rungs built here are the **nematode** (a tube that bends dorsoventrally) and the
    **earthworm** (a segmented hydrostat that crawls by peristalsis). The point of the ladder is to
    watch the model's **tokens layer** as morphology climbs — see [Phase II](../phase2.md).

## The ladder

Following Fig. 5 of the monograph, the model systems are:

| rung | creature | new differentiation | new opponent axis (the CAZ) |
|---|---|---|---|
| polarized | [**cnidarian**](../cnidarians.md) | one epitheliomuscular mesh | muscle ⊕ **passive** mesoglea/hydrostat (radial) |
| **tubular** | [**nematode**](../experiments/nematode.md) | skin · gut · muscle **detach** | **dorsal ⊕ ventral** longitudinal (DV bend) |
| **segmented** | [**earthworm**](../experiments/earthworm.md) | circular & longitudinal **two disjoint tissues** | **telescoping** + **lateral bend** (peristalsis + turn) |
| bilateral | *(next)* | paired zones | left/right steering |
| appendicular | *(next)* | limbs / manipulators | flexor ⊕ extensor at joints |

## What a CAZ is (read this before the rungs)

A **CAZ = one opponent pair = one degree of freedom** — a circle split in half, the two halves the
two opposing muscle-sides (see the [opponent-pair reference](opponent_pair_caz.md) and
`smn_lab/morphology.py`). This matters because it is easy to get wrong:

- a lattice **node** is a multicellular **muscle-side region** — *not* a CAZ;
- a **muscle** (a circular ring, a longitudinal strand) is **one side** of a CAZ;
- **opponency is intrinsic** to a CAZ, not a relation *between* CAZs.

And crucially, **which** opponent pair actuates a rung differs by animal — the nematode has a
dorsal⊕ventral pair and **no circular muscle**; the earthworm has a circular⊕longitudinal
(telescoping) pair and **no dorsoventral muscle**. Reading a node, or a lone muscle, as a whole CAZ
mis-states the animal's degree of freedom.

![Across the ladder a CAZ is always an opponent pair, but which pair differs by animal; and the cnidarian's inter-layer rim coupling is neither DFN nor IN](../figures/caz_coordination_audit.png)

## A coordination caveat carried up from the cnidarian

The cnidarian disk has **two epithelial layers coupled only at the rim**. That inter-layer messaging
is **neither a DFN nor an IN**: the DFN/IN split was derived for differentiation-vs-integration
*within one net*, whereas the rim couples *two separate tissue layers* — a distinct, more primitive
kind of coordination (an inter-tissue gateway). We keep it labelled **uncertain** rather than force
it into the dichotomy.

## Where to read next

- **[The nematode](../experiments/nematode.md)** — the muscle detaches from the epithelium; a tube
  that bends dorsoventrally, with no circular muscle and the cuticle as its passive antagonist.
- **[The earthworm](../experiments/earthworm.md)** — two disjoint muscle tissues woven around a
  segmented hydrostat; peristalsis and turning as two distinct opponent pairs.
- **[Opponent-pair CAZ (reference)](opponent_pair_caz.md)** — the ontology and the per-animal table,
  with sources.
