# Mathematical Toolkit for the SMN Bench

## Purpose

This note maps the major architectural questions in the SMN bench to the mathematical tools most likely to be useful. It is written both as an internal design aid and as a collaborator-facing document.

The point is not to force the bench into a single formalism. Different parts of the architecture call for different mathematics. The bench is likely to need:

- geometry
- dynamical systems
- graph theory
- network science
- control theory
- statistical mechanics and threshold methods
- learning theory
- information-theoretic tools

The aim is to know **what mathematics belongs where**, and what kinds of collaborators would be useful.

## Main Architectural Domains

The bench now has at least six distinct mathematical domains:

1. body geometry and kinematics
2. local zone dynamics
3. messaging board / coupling topology
4. world-model construction
5. action-pattern dynamics and recruitment
6. learning, invention, and adaptation

Each of these should be formalized differently.

## 1. Body Geometry and Frame of Reference

### Architectural question

How does body geometry define the frame of reference in relation to which the world model is constructed?

### Mathematical tools

- rigid-body kinematics
- articulated body geometry
- differential geometry where needed
- coordinate transforms
- reachability and workspace analysis
- contact geometry
- graph-embedded spatial models

### Why this matters

The SMN bench should not treat geometry as a rendering detail. Geometry is part of the architecture:

- where the CAZs are matters
- where the transducers are matters
- what appendages can reach matters
- what counts as left/right/front/back/up/down is body-defined

The world model is therefore not a free-floating representation. It is a structured relation between body geometry and sensed modulation.

### Concrete uses

- define the canonical organism's body schema
- define limb workspaces and support polygons
- define transducer mounting maps
- compute object location relative to body geometry
- formalize affordances such as reachable, climbable, graspable, enclosed

### Useful collaborator types

- roboticists
- geometers
- kinematics and mechanism designers

## 2. Local Zone Dynamics

### Architectural question

What is the right mathematical description of a CAZ as a local sensing-acting-modulating unit?

### Mathematical tools

- nonlinear dynamical systems
- coupled oscillators
- phase models
- hybrid systems
- local control theory
- stability analysis

### Why this matters

A CAZ is not just a node in a graph. It is a local dynamical unit:

- it senses
- it acts
- it modulates
- it may oscillate, recruit, halt, or negotiate

The zone may need to be formalized as a local dynamical system with state, not just a stateless input-output mapping.

### Concrete uses

- BAP rhythm generation
- HAP interruption dynamics
- local appendage coordination
- modulation thresholds and local attractors
- stability of postural and exploratory patterns

### Useful collaborator types

- dynamical systems theorists
- motor control researchers
- nonlinear control people

## 3. Messaging Board / Balance Beam

### Architectural question

How should zones be networked, and what kinds of network architecture support the emergence of objecthood, world-model coherence, and stable action-pattern coordination?

### Mathematical tools

- graph theory
- network science
- spectral graph theory
- random graph models
- percolation theory
- random matrix methods
- reservoir dynamics
- neural network theory

### Why this matters

This is likely the most important mathematical domain for the bench.

The board is where one can vary:

- decentralized ganglionic organization
- centralized boards
- hybrid multi-scale boards
- small-world boards
- hub-rich or approximately scale-free boards
- direct coupling vs relay-mediated coupling
- trainable vs non-trainable coupling

### Concrete uses

- define adjacency rules between CAZs
- compare board families on the same body
- compute connectivity statistics
- examine spectral signatures of different boards
- study emergence thresholds for largest bound components
- test whether objecthood onset behaves like a percolation transition

### Important open questions

- Is there a critical coupling density below which the world model remains fragmented?
- Does objecthood depend on the largest connected or effectively coupled component?
- Can HAPs and NAPs define network context by changing effective coupling structure?
- Can the board be a reservoir?
- What changes if the board is a neural network?
- What changes if learning is allowed on the board?

### Useful collaborator types

- network scientists
- graph theorists
- statistical physicists
- reservoir computing researchers
- neural network theorists

## 4. World-Model Construction

### Architectural question

What is the right mathematical description of the world model built from action and modulated sensation?

### Mathematical tools

- spatial statistics
- occupancy and evidence accumulation
- metric geometry
- topological data analysis
- manifold learning
- relational geometry
- Bayesian filtering where appropriate

### Why this matters

At present the bench uses relatively simple surface-hit accumulation. That is fine for early experiments, but the stronger SMN claims call for richer formalization.

The world model may need to be described not just as occupancy, but as:

- geometric relation
- affordance field
- support structure
- object-boundary organization
- conceptual or relational manifold

### Concrete uses

- improve scoring beyond coverage/precision
- formalize free-space and support-space correctness
- define object persistence and object identity consistency
- model the world as a graph or manifold relative to body geometry
- compare map-like, topological, and affordance-based world models

### Useful collaborator types

- SLAM and mapping researchers
- computational geometers
- topological data analysis people
- spatial cognition researchers

## 5. Reafference and Self/World Distinction

### Architectural question

What mathematical form should the self/world distinction take when the agent predicts the sensory consequences of its own action?

### Mathematical tools

- forward models
- prediction-error formalisms
- filtering and estimation
- state-space models
- observer theory
- signal detection and statistical discrimination

### Why this matters

The simplest current form is a learned sensorimotor contingency with residual analysis. More realistic forms may need:

- multi-modal forward models
- joint state estimation
- self-motion under translation and rotation
- moving world and moving conspecifics
- uncertainty-aware residual comparison

### Concrete uses

- compare self-caused and world-caused change statistically
- define threshold criteria for discrimination
- extend from one zone to whole-body reafference
- compare visual, tactile, and echoic reafference

### Useful collaborator types

- state-estimation researchers
- control theorists
- signal-processing researchers

## 6. Action-Pattern Taxonomy

### Architectural question

How should the action patterns of the organism be mathematically described, especially when multiple classes interact?

### Pattern families

- `BAPs`
- `HAPs`
- `SMAPs`
- `RAPs`
- `TAPs`
- `NAPs`

### Mathematical tools

- hybrid dynamical systems
- switching systems
- hierarchical control
- dynamical grammars
- automata where useful
- attractor-based pattern selection
- phase-transition ideas for recruitment and coordination

### Why this matters

The bench should not collapse all action into one controller. Different pattern classes have different mathematical needs:

- BAPs: oscillatory and baseline dynamics
- HAPs: interruptive and gating dynamics
- SMAPs: self-modifying loops
- RAPs: context-triggered routine recruitment
- TAPs: interactional and later social coordination
- NAPs: demand-sensitive, dexterous, negotiable local adaptation

### NAPs are especially important

NAPs are the most likely place for:

- local learning
- improvisation
- invention of new routines
- dexterity under demand

This suggests that NAPs may need mathematical treatment distinct from fixed-pattern controllers.

### Useful collaborator types

- hybrid systems researchers
- control theorists
- motor learning researchers
- computational neuroscientists

## 7. Learning and Adaptation

### Architectural question

Where can learning occur in the architecture without erasing its core claims?

### Candidate locations

- local CAZ adaptation
- NAP formation
- relay-unit or board adaptation
- modulation threshold adaptation
- action-pattern invention
- modality substitution and compensation

### Mathematical tools

- online learning
- adaptive control
- reinforcement learning in constrained roles
- self-organization
- meta-stability analysis
- reservoir adaptation
- representation learning without assuming backprop everywhere

### Key design issue

The bench should distinguish clearly between:

- fixed architectural structure
- learned local refinements
- learned new patterns
- trainable boards

This is especially important if collaborators from machine learning join the project. Otherwise the architecture could be trivially replaced by a generic learned controller, and the core SMN question would be lost.

### Useful collaborator types

- learning theorists
- adaptive control researchers
- reinforcement learning researchers with an embodied focus

## 8. Thresholds, Emergence, and Scaling

### Architectural question

Do key SMN effects emerge only after crossing a critical number of zones or a critical coupling regime?

### Mathematical tools

- percolation theory
- phase transitions
- finite-size scaling
- critical phenomena methods
- bifurcation analysis
- order parameters

### Why this matters

This is central to the current design hypothesis:

- too few CAZs may fail not because SMN is false, but because the system is below critical scale
- objecthood and world-model coherence may depend on connectedness or effective coupling
- after some threshold, the system may become robust to local detail

### Concrete uses

- define order parameters for objecthood
- compare emergence across `24`, `48`, and `64` CAZ organisms
- test coupling-density transitions
- compare decentralized vs centralized thresholds

### Useful collaborator types

- statistical physicists
- complex systems researchers
- applied mathematicians working on emergence

## 9. Information Flow and Functional Coupling

### Architectural question

How can one quantify what information is actually moving through the board and between modalities?

### Mathematical tools

- information theory
- mutual information
- transfer entropy
- causal influence measures
- synergy and redundancy analysis

### Why this matters

A structural graph is not the same as a functional graph. Two boards may have the same nominal topology and very different effective information flow.

These tools can help ask:

- which couplings matter?
- where does binding actually occur?
- how much redundancy exists across modalities?
- when do HAPs or NAPs reconfigure functional coupling?

### Useful collaborator types

- information theorists
- computational neuroscientists
- complex systems analysts

## 10. Reservoirs and Neural Boards

### Architectural question

Can the messaging board be modeled as a reservoir, a neural network, or a trainable dynamical substrate, and if so under what constraints?

### Mathematical tools

- reservoir computing
- recurrent neural network analysis
- echo-state property analysis
- controllability and observability
- learning dynamics with and without backpropagation

### Why this matters

This is one of the most interesting experimental branches:

- board as fixed dynamical reservoir
- board as trainable recurrent network
- board with no backpropagation
- board with backpropagation

This must be handled carefully, because overly powerful learned boards may erase the architecture's intended explanatory structure. But the comparison is scientifically important.

### Key comparison questions

- Does a fixed reservoir already support useful binding and context sensitivity?
- What additional capability appears with training?
- Does backpropagation produce qualitatively different solutions from local or architectural adaptation?
- Can HAPs and NAPs act as context-setting control signals over the reservoir state?

### Useful collaborator types

- reservoir computing researchers
- recurrent neural network researchers
- machine learning theorists

## 11. Candidate Mathematical Roadmap

The following sequencing is likely sensible.

### Phase 1: geometry and organism formalization

Needed first:

- articulated geometry
- body schema formalization
- CAZ placement specification
- modality mounting maps

### Phase 2: local dynamics and board topology

Needed next:

- local CAZ models
- graph definitions for board families
- direct vs intermediated board formalization

### Phase 3: threshold and scaling analysis

Needed once larger organisms are built:

- order parameters
- connectivity and component analysis
- percolation-style sweeps
- finite-size comparisons

### Phase 4: richer world-model and objecthood metrics

Needed once the body and board are stable:

- manifold or topological measures
- object persistence metrics
- affordance-structure metrics

### Phase 5: learning and NAPs

Needed once the non-learning architecture is clear:

- adaptive mechanisms
- invention of local patterns
- trainable boards and controlled ML comparisons

## 12. Suggested Collaboration Roles

This project could realistically support collaborators from several mathematical and technical communities.

### Geometry and embodied robotics

Questions:

- body schema
- transducer placement
- locomotor and manipulator geometry

### Dynamical systems and control

Questions:

- local zone dynamics
- stability of action patterns
- switching and recruitment

### Network science and statistical physics

Questions:

- board topology
- coupling thresholds
- emergence of objecthood
- scaling with CAZ count

### Mapping and spatial representation

Questions:

- world-model formalization
- affordance geometry
- object and scene persistence

### Machine learning and adaptive systems

Questions:

- NAP learning
- trainable boards
- reservoir comparisons
- non-backprop alternatives

### Information theory and functional analysis

Questions:

- where binding occurs
- how modalities interact
- what functional couplings matter

## 13. Immediate Recommendation

The next concrete step should be to turn the `SMN-A48` organism note into a more formal architecture specification, and then define:

- the body geometry formally
- the board families formally
- the order parameters for emergence formally
- the first benchmark comparisons formally

Only then should more advanced learning machinery be layered in.

## Summary

The bench does not need one mathematics. It needs a **stack** of mathematical tools, each suited to a different architectural layer:

- geometry for the body
- dynamics for the zones and patterns
- graph and network theory for the board
- threshold methods for emergence
- mapping and topology for the world model
- information theory for functional coupling
- learning theory for NAPs and trainable boards

That stack also defines a clear collaboration map. This can be useful both scientifically and practically when seeking collaborators.
