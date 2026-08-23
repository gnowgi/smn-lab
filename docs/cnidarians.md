# Cnidarians — a synthetic model system

!!! abstract "The proposal"
    Use the cnidarian body plan as a **synthetic model system** for embodied cognition.
    Cnidarians are the first animals with **neurons** — a nerve net — yet they have no
    brain, no ganglia, and a small vocabulary of body plans. That makes them the sweet
    spot: complex enough to build a self-model, sense a world, and act on an object, but
    simple enough that every competence can be traced to a specific piece of morphology.
    One dial — the body plan — sweeps the whole class, and each setting generates a
    creature whose **self-model, world-model, object-directedness, and Umwelt** we can
    measure on the bench.

## Why cnidarians, and not a worm or a fly

An embodied theory of cognition needs a model organism the way genetics needed the fly
and neuroscience needed the squid axon. The choice is a trade-off. Too simple (a single
sheet, a sponge) and there is no nervous system to speak of, nothing that integrates.
Too complex (an insect, a tetrapod) and the appendages, ganglia, and brains pile so many
mechanisms on top of each other that no single competence can be cleanly attributed.

Cnidarians sit exactly between. They are the **first group with neurons** — the
messaging network the SMN architecture is about — organized as a **diffuse nerve net**
rather than a brain. They are radially (not bilaterally) symmetric, they have two tissue
layers, and their body plans form a short, well-understood list. So they are complex
enough to be genuinely cognitive in the bench's operational sense, and simple enough that
**there is nowhere for a hidden controller to hide** — every coordinated act must be a
network effect. That is the property that makes them a clean instrument.

## One dial spans the class

The bench builds a cnidarian from a **two-layer sac** — an outer face (ectoderm) and an
inner face (endoderm) with mesoglea between, joined at a **rim**. From that one plan,
small morphological moves generate the recognizable forms:

| move on the dial | creature | on the bench |
|---|---|---|
| the sac as a column, mouth up | **polyp** (e.g. *Hydra*) | [Hydra — the sac, localization, capture](experiments/hydra.md) |
| **add tentacles** at the rim | **medusa / hydroid** forms | tentacle experiments below |
| **remove tentacles**, keep the ciliated sac | **ciliary / filter feeders** | the bare two-layer disk |
| flatten the sac to a **disk**, vary the rim | the rim as a special place | [the disk experiments](experiments/cnidarian_disk.md) |
| **close the sac** into a sphere (no rim) | a blastula-like closed body | the no-rim sphere below |

Because the SMN world-model is built in the **body's own frame**, each of these bodies —
in the *same* pond — builds a **different Umwelt** (see [Umwelt](experiments/umwelt.md)):
the tentacled form reaches out and localizes prey on its arms; the bare ciliary feeder
knows only what drifts onto its surface. Same world, different animals, different worlds.

## The architecture cnidarians actually realize — DFN, not yet IN

!!! note "A working position (under active revision)"
    The two-network reading below is being **reconsidered** for cnidarians specifically.
    What follows is the current best account, not a settled claim.

The SMN architecture distinguishes two networks: a **DFN** (a Differentiating net — it
differentiates the body into zones, drives action, and passes messages locally) and an
**IN** (an Integrating net — it binds the whole body's state into a single, globally
available snapshot). The clean way to see that these are *different jobs* is the
[two-network dissociation](experiments/two_networks.md): a damped, differentiating medium
can build a body's geometry but keeps information local; a non-decremental integrating
medium can broadcast globally but cannot build geometry. One medium cannot do both.

The key point for cnidarians is that they appear to realize **only the DFN**. The
fundamental module — the **CAZ** — is *both* an **action zone** (it contracts, it
differentiates) *and* a set of **messaging edges** (it conducts to its neighbours). Action
and messaging are the same module, not two nets; and those messaging edges *are* the
diffuse nerve net, living in the **mesoglea** between the two layers. There is no separate
broadcasting board.

And crucially, **cnidarians have no ganglia**. A ganglion is a local condensation of the
net — a place where signals are gathered and integrated — and that is the anatomical
signature of an **IN**. A diffuse net with no condensations has differentiation and local
messaging but no integrating centre. So the cnidarian nervous system looks like a **DFN
without an IN**: it can differentiate the body and pass news from neighbour to neighbour,
but it has no organ that makes the whole body's state available *as one picture*.

This is not a deficiency to explain away — it is the **most useful thing about the model
system**. It lets us ask a sharp evolutionary question the bench can actually answer:

> **What competence does an agent gain when the IN appears?**

Start from the cnidarian DFN, then add an integrating channel (the first ganglion), and
measure what the animal can suddenly do that it could not before — bind a snapshot, hold
it against decay, attend to one thing while another waits, coordinate across the whole
body at once. The DFN-only cnidarian is the **baseline**; the IN is the **independent
variable**; the new competence is the **read-out**.

## What we generate for each body

Every cnidarian the dial produces is run through the one [results module](results-module.md),
so the same quantities come out for each, comparably:

- a **self-model** — the body's own connectivity graph, recovered from movement alone;
- a **world-model** (the canvas) — built in the self-model's frame from modulated sensing;
- **object-directedness** — an object is what *halts* a pattern; in the polyp a moving
  prey above threshold triggers a whole-net capture with no controller;
- an **Umwelt** — the slice of the world that *this* morphology can construct.

## Where to read next

- **[The polyp (Hydra)](experiments/hydra.md)** — the sac recovers its own two-layer body,
  localizes a prey touch, and performs a whole-net capture reflex with no central control.
- **[The disk experiments](experiments/cnidarian_disk.md)** — flatten the sac to a disk and
  ask what the *rim* is: a betweenness bottleneck in the self-model, the sole door for a
  perturbation to cross between the layers, and — remove it — the difference between a body
  with a special place and one without.
- **[Two networks are forced](experiments/two_networks.md)** — why differentiation and
  integration need different media, and hence why the IN is a genuine next step, not a
  relabelling of the DFN.
- **[Umwelt](experiments/umwelt.md)** — same world, different anatomy, different world.
