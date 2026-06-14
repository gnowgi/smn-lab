# SMN-A48 Specification

> **Note — read [Lesson 1](lesson1_construction_of_experience.md) first.**
> `SMN-A48` is a *scaling target*. The constructive baseline is the minimal
> three-block **axial** crawler of Lesson 1; A48 is reached by scaling segments and
> adding branches (appendages) to that axial chain — the spider is a worm that grew
> legs — not by taking the spider as the primitive.

## Purpose

`SMN-A48` is the proposed canonical organism for the next phase of the SMN bench. It is intended to be:

- large enough to test network-scale SMN claims
- geometrically explicit
- modular in modalities
- reconfigurable in board topology
- reusable across many experiments

It is not intended to be biologically faithful to any one species. It is an artificial model organism designed to make the architecture testable.

## Design Rationale

The present bench has shown that a few zones are enough for demonstrations, but likely too few for the stronger thesis. The design hypothesis behind `SMN-A48` is:

- self/world distinction can appear in small systems
- objecthood and world-model coherence likely require many coupled differentiae
- a meaningful distributed benchmark needs enough CAZs for threshold, topology, redundancy, and degradation experiments

The chosen scale is:

- `24 CAZs` as a reduced stepping-stone
- `48 CAZs` as the canonical benchmark organism
- `64 CAZs` as a future expansion

## Core Structural Principles

The organism should satisfy the following architectural commitments.

### Polarization

There should be a front-back axis supporting exploratory, orienting, and manipulative differences.

### Bilateral symmetry

The large-scale body should be bilaterally organized to support opposition, stance, and gravity-related stabilization.

### Local asymmetry

Perfect symmetry is not required. Local asymmetries in transducer density, appendage role, or board coupling are allowed and may be useful.

### Opposition to gravity

The organism should support:

- stance
- bracing
- climbing
- turning on varied surfaces
- load-bearing appendage coordination

### Body geometry as frame of reference

The body schema must explicitly define:

- CAZ locations
- joint axes
- appendage roots
- transducer mount sites
- reachable workspace

The world model is built in relation to this geometry.

## Body Family

`SMN-A48` is a segmented spider-like crawler/climber with multiple articulated appendages.

### High-level morphology

- segmented trunk
- 8 appendages, 4 per side
- anterior region with orienting structures
- multiple distal exploratory/contact structures
- support for multimodal transducer mounting

This form is chosen because it supports:

- distributed sensing
- distributed contact
- postural coordination
- local and global action patterns
- multi-limb object contact
- terrain-sensitive movement

## CAZ Allocation

The following is the base allocation.

## 1. Appendage locomotor CAZs: 24

8 appendages x 3 principal CAZs each:

- proximal swing
- lift/lower
- distal extension/flexion

These provide the basic locomotor and exploratory structure.

## 2. Trunk/postural CAZs: 8

Used for:

- axial stabilization
- bilateral trunk bends
- pitch/roll compensation equivalents
- body bracing under stance and contact

## 3. Distal exploratory CAZs: 8

One per appendage cluster, used for:

- probing
- near-range tactile exploration
- appendage-local exploratory routines

## 4. Orienting CAZs: 4

Used for:

- anterior orienting structures
- head or sensor-turret equivalents
- active modulation of distal sensory orientation

## 5. Internal/basal CAZs: 4

Used for:

- energy-like state
- strain/tension
- equilibrium
- basal modulation support

## Total

`24 + 8 + 8 + 4 + 4 = 48 CAZs`

This is the base version. The exact internal partition can evolve while preserving the total scale and modular layout.

## Geometric Schema

The body schema should explicitly encode:

- trunk segments
- appendage base coordinates
- appendage joint chain geometry
- bilateral correspondences
- mount point coordinates for each transducer family
- support polygon and stance geometry
- reachable and graspable zones

At runtime, the organism should always be able to answer:

- where is this CAZ?
- what can this CAZ reach?
- what transducers are mounted here?
- what is the relation of this local geometry to the whole body?

## Modalities

Modalities should be swappable packages attached to a fixed body.

## Baseline modality roles

### Internal/self-state

- proprioception
- appendage load
- body orientation
- internal energy or strain state

### Contact-near

- foot/pad contact
- force/resistance
- slip or substrate response

### Distal spatial

- tactile-range
- vision
- echo-location

### Field/environmental

- chemical gradient
- thermal gradient
- substrate vibration or other field signal

## Baseline package

The default serious multimodal package should include:

- proprioception
- contact/force
- tactile-range
- vision or echo-location
- one field modality

## Modality substitution principle

The same body should support experiments such as:

- no vision
- vision replaced by echo-location
- tactile-range only
- asymmetric sensory loss
- multimodal redundancy
- multimodal conflict

This is necessary if the bench is to test the modality-generality of the architecture.

## Action-Pattern Taxonomy

The organism must support the full pattern family.

### BAPs

Basal Action Patterns:

- gait
- stance
- baseline scanning
- exploratory rhythmic structure

### HAPs

Haltable Action Patterns:

- stop
- brace
- partial halt
- orient
- interrupt and redirect

### SMAPs

Self-Modulating Action Patterns:

- loops where ongoing activity alters its own further recruitment
- cross-limb stabilization loops

### RAPs

Recruited Action Patterns:

- local routines such as step-over, climb-edge, probe-gap, grasp-surface

### TAPs

Transactive or externally recruitable patterns:

- later signaling or cooperative routines

### NAPs

Negotiable Action Patterns:

- dexterous local adaptation
- demand-sensitive adjustments
- likely locus for learning and invention of new routines

`SMN-A48` should be designed so that these pattern families can be enabled, disabled, or compared without changing the body itself.

## Board Architecture

The body is fixed; the messaging board is variable.

`SMN-A48` should support at least these board families:

- segmented decentralized ganglionic board
- centralized board
- hybrid hierarchical board
- small-world board
- hub-rich / approximate scale-free board
- reservoir-like board
- neural board

And at least these coupling modes:

- direct CAZ coupling
- relay/intermediary-unit coupling
- fixed board
- trainable board

This is a major experimental axis.

## Recommended Default Board

The default `SMN-A48` board should be hybrid:

- local ganglia per appendage
- bilateral/regional coordination boards
- axial/postural board
- sparse central binding board

This gives:

- strong embodiment
- local robustness
- support for global object/world binding

## World Model

The organism should not be limited to one world-model formalism.

It should support:

- occupancy-like spatial map
- living snapshot with decay
- affordance field
- object-binding representation
- body-relative relational model

The key invariant is that the model is grounded in body geometry and modulation, not in a god’s-eye frame.

## Benchmark Questions SMN-A48 Should Support

The canonical organism should support all of the following without redesign:

- single-zone and multi-zone reafference
- body-relative mapping
- self/world distinction under rich self-motion
- world-model degradation under noise and lesion
- objecthood from multi-zone contact
- cross-modal binding
- haltability and object-directedness
- NAP learning and invention
- board topology sweeps
- scaling and threshold experiments

## Reduced Variant: SMN-A24

`SMN-A24` should be a reduced member of the same family, not a separate organism concept.

Suggested reduction:

- fewer appendages or fewer active joints
- fewer orienting and internal CAZs
- same geometric and modular logic

Its main role is:

- faster iteration
- low-cost pilot experiments
- interface and config development

Its main limitation is:

- likely underpowered for stronger emergence claims

## Expansion Variant: SMN-A64

`SMN-A64` should be treated as a future scaling target.

Likely gains:

- richer redundancy
- better degradation studies
- stronger board-topology comparisons
- better test of threshold and approximate scale-free hypotheses

## Implementation Constraints

The organism should be implemented so that:

- geometry is explicit and queryable
- modalities are mountable packages
- boards are swappable
- action patterns are modular
- experiments compose modules rather than define them

This makes `SMN-A48` a bench organism rather than a one-off script.

## Immediate Next Step

The next formal artifact after this spec should be:

- a zone table
- a transducer mount table
- a board-layer adjacency spec
- a config schema binding these together

Those will translate the present specification into software architecture.
