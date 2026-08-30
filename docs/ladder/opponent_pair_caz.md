# The CAZ across the complexity ladder

_Direction: G. Nagarjuna. This note fixes the CAZ ontology for the ladder model systems and
records the two reconstructed morphologies (nematode, earthworm)._

## What a CAZ is (canonical)

A **CAZ = a Coordinated Action Zone = a zone of coordinated action over `f`s** — the coordination of
*which contractile units act together, and when* — realized by the **whole SMN** (sensing + pulling +
messaging) and **read out**, never imposed by a controller. The tidy **opponent pair actuating one
degree of freedom** — the split-circle in `smn_lab/morphology.py` — is the CAZ's **differentiated
(appendicular) limit**, not its definition. (This corrects the earlier "opponency is the primitive"
reading: opponency is the *differentiated form* the opposition eventually takes, not the ground of a
CAZ.) Therefore:

- a lattice **node** is an `s`, a multicellular **region** — *not* a CAZ;
- a lattice **link** — a muscle-tendon unit (a circular ring, a longitudinal strand) — is one **`f`**:
  a pull-only Sensation Modulator, **one side** of an opponent relation, *not* a CAZ;
- a **CAZ** is a *coordination* over many `f`s; **antagonism is a relation between `f`s** (an edge in
  the coordination), and at the appendicular limit two `f`s across one shared joint form the opponent
  pair. Saying "a CAZ *is* a pair" collapses this limit case into the definition and breeds confusion.

A single `f` has no coordination partner drawn yet, and a bare pair is only the differentiated tip; a
CAZ is the coordinated zone that the whole SMN reads out over its `f`s.

## Which differentiated opponent axis — it differs by animal

The **appendicular limit** of a CAZ is a discrete opponent pair; up the ladder that axis
**differentiates**, and which axis actuates a rung differs by animal:

| model system | differentiated opponent axis (appendicular limit) | opponent kind | locomotor DOF |
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
  muscle, detached longitudinal muscle in four quadrants). Differentiated axis = **dorsal ⊕ ventral
  longitudinal** (DV bend), cuticle/hydrostat as the passive restoring side; **no circular**, so no telescoping.
  Mouth = radial ⊕ elastic recoil; anus = DV pair. Demo: an anti-phase DV contraction wave → a
  travelling dorsoventral undulation.
- `experiments/earthworm.py` — two **disjoint** muscle tissues (circular segmental ⊕ longitudinal
  continuous), coupled only through the coelomic hydrostat `B_i` and the ganglia. Differentiated axes =
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
