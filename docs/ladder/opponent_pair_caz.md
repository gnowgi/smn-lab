# The opponent-pair CAZ across the complexity ladder

_Direction: G. Nagarjuna. This note fixes the CAZ ontology for the ladder model systems and
records the two reconstructed morphologies (nematode, earthworm)._

## What a CAZ is (canonical)

A **CAZ = one Coordinated Action Zone = one opponent pair = one degree of freedom** (see
`smn_lab/morphology.py`: "one circle split in half … the opponent pair actuating ONE degree of
freedom"; v2 evaluation C1: "opponency is the primitive"). Therefore:

- a lattice **node** is a multicellular **muscle-side region** — *not* a CAZ;
- a **muscle** (a circular ring, a longitudinal strand) is **one side** of a CAZ;
- a **CAZ** is the **opponent pair** (two sides) across a shared zone; **opponency is intrinsic**,
  not an edge between two CAZ.

A single node — or a single muscle — has no opponent, so it is not a CAZ.

## Which opponent pair — it differs by animal

| model system | opponent pair(s) = CAZ | opponent kind | locomotor DOF |
|---|---|---|---|
| **cnidarian** | epitheliomuscular ⊕ mesoglea/hydrostat | muscle vs **passive** elastic | radial contraction |
| **nematode** | dorsal-long ⊕ ventral-long (+ mouth radial ⊕ elastic) | muscle vs muscle (+ passive cuticle) | **dorsoventral bend** (no circular) |
| **earthworm** | circular ⊕ longitudinal (telescoping) + left-long ⊕ right-long | muscle vs muscle via hydrostat | **peristalsis** + turn (no DV) |
| **leech / slug** | + dorsoventral muscle (+ oblique) | more muscle pairs | + flattening |

Opponent axes **elaborate up the ladder** alongside tissue differentiation. Sourced in
`claude/SMN_annelid_muscle_biology.md` (Britannica; Fox/Lander *Lumbricus*; *Hirudinaria*; WormAtlas;
BioScience 64(6):476).

## The two reconstructed models

- `experiments/nematode.py` — three tissues (passive skin + transducers, passive gut with no
  muscle, detached longitudinal muscle in four quadrants). CAZ = **dorsal ⊕ ventral longitudinal**
  (DV bend), cuticle/hydrostat as the passive restoring side; **no circular**, so no telescoping.
  Mouth = radial ⊕ elastic recoil; anus = DV pair. Demo: an anti-phase DV contraction wave → a
  travelling dorsoventral undulation.
- `experiments/earthworm.py` — two **disjoint** muscle tissues (circular segmental ⊕ longitudinal
  continuous), coupled only through the coelomic hydrostat `B_i` and the ganglia. CAZ =
  **telescoping** (circular ⊕ longitudinal, per segment → peristalsis) + **lateral-bend**
  (left ⊕ right longitudinal → turn); **no dorsoventral** pair (that is a leech/slug rung). Demos:
  a peristaltic wave and a turn.

Both are self-contained (no cross-experiment imports) and print their structure (tissues, opponent
pairs, addressing) on run.

## A coordination caveat (cnidarian)

The cnidarian disk has **two epithelial layers coupled only at the rim**. That inter-layer messaging
is **neither a DFN nor an IN** — the DFN/IN split was derived for differentiation-vs-integration
*within one net*; coupling *between two tissue layers* is a distinct, more primitive kind of
coordination (an inter-tissue gateway). Left labelled uncertain, not forced into the dichotomy.
