# SMN-A48 Architecture Brainstorm

> **Note — read [Lesson 1](lesson1_construction_of_experience.md) first.** The
> spider-like canonical body described below is a *scaling target*, not a starting
> point. The minimal organism is a three-block **axial** segmented crawler (the
> worm precedes the spider); the canonical body is reached by *scaling and
> branching* that axial chain — appendages are branches of a segmental graph — never
> by starting from the spider. Lesson 1 gives the constructive baseline this note
> builds on.

## Purpose

This note consolidates the current design brainstorming for a more serious SMN bench organism than the present low-CAZ prototypes. The goal is to define a stable artificial model system on which many experiments can be run while varying selected architectural parameters cleanly.

The central design judgment is:

- a handful of CAZs is enough for demonstrations
- a handful of CAZs is not enough for the stronger SMN thesis
- the world model, objecthood, and higher action-pattern effects are likely to require crossing a critical number of coupled zones

The current working target is a `48-CAZ` organism, with a reduced `24-CAZ` version as a possible stepping stone.

## Why Few CAZs Are Not Enough

The small-CAZ agents used so far are useful for showing:

- reafference in a single zone
- simple body-relative mapping
- small cross-modal demonstrations

But they are too sparse to test the stronger claims of SMN. If the architecture is fundamentally a distributed, geometric, body-wide modulation network, then:

- too few CAZs means too few distinct local differentiae
- too few CAZs means too little coupling structure
- too few CAZs means too little room for redundancy, asymmetry, compensation, and graceful degradation
- too few CAZs means the world model may remain fragmented rather than emerging as a coherent object/world structure

The working hypothesis is that there is a **critical scale** or **critical coupling regime** below which the characteristic SMN effects do not emerge in a convincing way. In that sense, failure at low CAZ counts may not count strongly against SMN. The more relevant question is whether the architecture begins to show threshold behavior once network size and coupling density become sufficiently large.

This suggests:

- `4-8 CAZs`: toy demonstrations only
- `24 CAZs`: minimal serious networked organism
- `48-64 CAZs`: better region for threshold, scaling, and topology experiments

## Core Commitments for the Organism

The organism should embody the following structural commitments.

### Polarization

The body should have a front-back axis, allowing asymmetries in exploration, approach, manipulation, and retreat.

### Asymmetry

The organism should not be perfectly uniform. Some asymmetries in sensor placement, limb role, or coupling are desirable because asymmetry is often functionally important.

### Bilateral symmetry

At the large scale, the body should remain bilaterally organized. This supports opposition, coordinated locomotion, and stable gravitational relation.

### Opposition to gravity

The body should not be designed as if posture were trivial. Opponency and action patterns should be able to support stance, bracing, lifting, climbing, and traversal across different surfaces.

### Body geometry as frame of reference

The world model should be built relative to:

- where the CAZs are
- where the transducers are
- what appendages can reach
- how the body is oriented

The geometry of the body is the reference frame. The world model, and later perhaps the conceptual space, should be grounded in that geometry.

### Affordance-dependence

The structure of the organism partly determines what affordances the world offers. A world is not just sensed; it is enacted through the body's reachable, supportable, graspable, climbable, avoidable, and negotiable relations.

## Recommended Body Form

The best current candidate is a spider-like segmented body with jointed appendages.

Why this is attractive:

- the body is already a network of zones
- multiple appendages support distributed contact and exploration
- locomotion and posture are inherently opponent and gravity-sensitive
- appendages provide natural sites for distal and contact transducers
- the same body can support locomotion, probing, climbing, bracing, object contact, and dexterous local adaptation

This should not be a biological replica of a spider. It should be an artificial segmented crawler/climber built to suit the SMN architecture.

## Proposed Canonical Organism: SMN-A48

### High-level shape

- segmented trunk
- eight appendages, four per side
- moderate front-back polarization
- bilateral overall organization
- local asymmetries in sensing and role

### CAZ allocation

A plausible `48-CAZ` distribution:

- `24 appendage CAZs`
  - 8 appendages x 3 main joint CAZs
- `8 trunk/postural CAZs`
  - axial stabilization, body bends, stance regulation
- `8 distal exploratory CAZs`
  - one exploratory or probing CAZ cluster per appendage
- `4 orienting CAZs`
  - head or anterior orienting structures
- `4 internal/basal CAZs`
  - energy, tension, equilibrium, or other internal modulatory state

This should be treated as a first design point, not as a final law.

### Reduced stepping-stone organism

A smaller `SMN-A24` could be built first while preserving the same design logic:

- fewer appendages or fewer joints per appendage
- fewer orienting and internal CAZs
- same geometric principles

The reduced version should be explicitly designed as a scaled-down member of the same organism family, not a different kind of body.

## Modalities as Swappable Packages

The body should stay fixed while modalities are added, removed, or substituted depending on the experiment. Otherwise too many variables change at once.

### Fixed

- body geometry
- CAZ locations
- joint opponency
- support structure
- board infrastructure

### Variable

- vision present or absent
- echo-location present or absent
- chemical sensing present or absent
- distal tactile density
- force/contact density
- modality asymmetry
- cross-modal coupling pattern

### Modality roles

It is more useful to classify modalities by architectural role than by biological name:

- `internal/self-state`
  - proprioception, body orientation, joint load, energy, strain
- `contact-near`
  - force, resistance, slip, direct touch
- `distal spatial`
  - vision, echo-location, tactile-range, airflow-like spatial sensing
- `field/environmental`
  - chemical, thermal, substrate vibration, gradients

### Recommended baseline package

For a serious SMN bench, a good default suite is:

- proprioception
- contact/force
- distal tactile-range
- coarse active vision or echo-location
- one field modality such as chemical or substrate gradient

This gives the organism enough sensory richness to support mapping, reafference, cross-modal binding, affordance recruitment, and modality substitution experiments.

## Action-Pattern Taxonomy

The body should be able to host multiple classes of action patterns without redesign.

### BAPs

Basal Action Patterns:

- gait cycles
- stance maintenance
- scanning oscillations
- baseline exploratory rhythms

### HAPs

Haltable Action Patterns:

- stop, brace, orient, freeze, partial halt, global halt
- affordance-sensitive interruptions and redirections

### SMAPs

Self-Modulating Action Patterns:

- loops in which ongoing activity modulates its own further recruitment
- gait-body sway-proprioception couplings
- repeated exploratory loops that reshape subsequent sensing

### RAPs

Recruited Action Patterns:

- context-sensitive local routines such as step-over, probe-gap, climb-edge, grasp-surface, withdraw

### TAPs

Transactive or socially recruitable patterns:

- signaling, shared indication, later conventional or cooperative actions

### NAPs

Negotiable Action Patterns:

- dexterous, demand-sensitive local adaptations
- locally improvised adjustments
- context-shaped multi-step fine control
- likely place for learning, local innovation, and invention of new patterns

NAPs are especially important because they provide a place in the architecture where:

- local variability is not treated as error
- dexterity can emerge
- novel task-specific routines can be constructed
- learning may attach most naturally

NAPs may become one of the most important sites for adaptive mechanisms in the bench.

## The Messaging Board / Balance Beam

This is a major experimental variable and should be treated as such while keeping all other aspects constant.

The board is not just a plumbing detail. It may determine:

- whether local differentiae remain isolated
- whether they bind into objects
- whether local routines scale into global world-structure
- whether the body behaves as a fragmented collection or as an integrated cognitive organism

## Board Design as a First-Class Axis

Three dimensions should be separated:

- `topology`: who can couple to whom
- `depth`: direct zone-to-zone vs intermediated coupling
- `control distribution`: local, regional, central, hybrid

## Candidate Board Families

### 1. Segmented decentralized board

Like ganglia or a spinal system:

- strong local coupling within appendage or segment
- moderate coupling between neighboring segments
- sparse long-range coupling

Expected strengths:

- local adaptability
- robust locomotion
- graceful degradation

Expected weakness:

- weaker global binding unless long-range links are sufficient

### 2. Centralized board

Like a central brain-board:

- most information routed upward
- central binding or arbitration
- modulatory bias sent back downward

Expected strengths:

- easier global integration
- easier modality binding

Expected weakness:

- bottlenecks
- fragility
- possible loss of strong embodiment

### 3. Hybrid board

Likely best default:

- local ganglia
- regional boards
- sparse central binding board

This preserves local embodiment while still allowing global object/world integration.

### 4. Small-world board

- dense local coupling plus sparse long-range shortcuts

Useful for testing whether efficient global coherence can emerge without a dominant center.

### 5. Hub-rich or approximate scale-free board

- a few highly connected hubs
- many sparsely connected peripheral nodes

Useful for testing the hypothesis that after some threshold the effects may become scale free or approximately scale-invariant.

## Direct Coupling vs Intermediary Units

Another important parameter is whether CAZs couple directly or through intermediary units.

### Direct board

- CAZ to CAZ coupling
- easier to interpret
- good for minimal tests and baseline sweeps

### Intermediated board

- relay or hidden units between CAZs
- can gate, delay, amplify, inhibit, synchronize, normalize, bind

This is where one can experiment with:

- relay layers
- reservoir-like boards
- neural-network boards
- trainable vs non-trainable boards

The key question is whether the essential SMN effects still appear:

- with no intermediary units
- with relay units but no backpropagation
- with trainable neural boards
- with reservoir-like dynamics

## Questions for Board Experiments

Holding the body fixed, one should be able to ask:

- can the board be a reservoir?
- can the board be a neural network?
- does backpropagation help, distort, or trivialize the architecture?
- are intermediary units necessary for binding?
- does global objecthood require a center?
- does a small-world topology outperform flat or hierarchical topologies?
- do HAPs and NAPs function as context-defining modulatory states for the network?

The last question is especially important. HAPs and NAPs may not merely be action outputs; they may define the active context within which the network couples and interprets signals.

## Working Hypothesis About Emergence

The current working hypothesis is:

- the world model may not emerge below a critical number of CAZs
- objecthood may depend on crossing a critical coupling density
- once a sufficiently large and richly coupled network is reached, some effects may become robust to local details
- that robustness may look approximately scale-free, though this should be tested rather than assumed

This gives two major scaling axes:

- number of zones
- board connectivity structure

## Canonical Experimental Strategy

The main strategy should be:

- keep the body geometry fixed
- keep the CAZ placements fixed
- keep the available action-pattern classes fixed
- vary modalities cleanly
- vary the board cleanly

This makes the board one of the strongest experimental variables in the bench.

## Suggested Next Step: Mathematical Toolkit

Once the organism and board families are defined, the next design question is what mathematical tools are needed, and where.

Likely domains include:

- geometry and body kinematics
- graph theory and network topology
- percolation or threshold analysis
- dynamical systems for action patterns and recruitment
- information flow measures across boards
- learning theory for NAP formation and trainable boards
- statistical mechanics style tools for emergence and phase transitions

That should be addressed in a separate follow-up note once the organism and board design are fixed enough.

## Summary

The main conclusions of this brainstorming are:

- a serious SMN bench needs more than a few CAZs
- `48 CAZs` is a reasonable target for a canonical organism
- a spider-like segmented body is a strong candidate
- body geometry should ground the world model
- modalities should be swappable while the body remains fixed
- the action-pattern taxonomy should include `BAPs`, `HAPs`, `SMAPs`, `RAPs`, `TAPs`, and `NAPs`
- the messaging board is a central experimental parameter
- board topology, depth, and distribution should all be varied
- reservoir-like, neural, trainable, and non-trainable boards should all be testable on the same body
- HAPs and NAPs may define context for network coupling, not just output actions
- the next stage is to define the mathematical toolkit appropriate to each part of the architecture
