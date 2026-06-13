# Engine Boundary for the SMN Bench

## Purpose

This document defines the boundary between the **physics engine** and the **SMN bench architecture**.

The goal is to prevent accidental collapse of the project into:

- MuJoCo-specific experiment code
- sensor implementation details masquerading as theory
- backend assumptions leaking into architectural claims

The physics engine is a substrate for physical realization. It is **not** the architecture. The bench must remain conceptually portable even if MuJoCo remains the default backend for a long time.

## Main Principle

The engine should provide:

- physical state evolution
- collisions and contacts
- actuator application
- low-level sensing primitives
- optional rendering support

The bench should provide:

- CAZ definitions
- body schema abstraction
- modality definitions
- messaging board / balance beam logic
- action-pattern logic
- world-model construction
- interpretation of self/world/object
- experiment logic and metrics

The bench should depend on a backend interface, not on MuJoCo internals spread throughout the codebase.

## What Belongs to the Engine

The following belong to the physics backend.

### Physical realization

- articulated body dynamics
- rigid-body integration
- joints and constraints
- contacts and collision response
- gravity and surface interaction

### Actuation substrate

- application of forces, torques, controls, tendon forces, or actuator commands

### Native sensor primitives

- range or ray-based primitives if provided
- contact or touch primitives
- body pose and velocity
- joint states
- rendered image buffers if used as raw visual input

### Rendering and visualization support

- scene rendering used as raw visual data
- debug visualization of bodies, contacts, and geometry

## What Does Not Belong to the Engine

The following must remain bench-level concerns.

### Architecture

- what a CAZ is
- what the body schema means
- what counts as a modality package
- what the messaging board does
- how action patterns are organized

### Interpretation

- self/world distinction
- objecthood and binding
- affordance interpretation
- world-model updates
- conceptual or relational structure

### Experiment logic

- tasks
- ablations
- lesions
- metrics
- scoring
- comparisons across architectural variants

This is the most important section of the boundary. If these responsibilities drift into backend code, the bench stops being an architecture bench and becomes a simulator demo.

## Raw Signals vs Interpreted Signals

The engine should expose **raw signals**.

Examples:

- contact forces
- ray distances
- rendered frames
- joint angles
- body-frame velocities
- body orientation

The bench should derive **interpreted signals**.

Examples:

- modality tokens
- residuals for reafference
- object codes
- affordance states
- world-model updates
- pattern recruitment conditions

This separation is essential. The backend should not directly output:

- bound objects
- self/world labels
- world-model cells
- pattern identities

Those belong to the architecture.

## What Must Be Backend-Independent

The following layers should be portable across backends:

- body schema abstraction
- config schema
- modality package definitions
- board definitions
- action-pattern layer
- world-model layer
- experiment specifications
- metrics and scoring

Only the backend adapter and model-building layer should need replacement if a different engine is used.

## Boundary Interfaces

The boundary should be enforced through explicit interfaces.

## 1. Body-to-engine interface

Responsibilities:

- compile a body schema into a backend-specific model
- attach joints, constraints, actuators, and mount points
- create any backend-specific sensor or render hooks

The bench provides:

- body geometry and CAZ placement

The backend adapter provides:

- compiled physical model

## 2. Engine-to-modality interface

Responsibilities:

- expose raw sensor readings
- expose raw rendered buffers if needed
- expose body and joint state

The modality layer then converts these into modality-specific interpreted signals.

## 3. Engine-to-board interface

There should be no direct semantic coupling between the engine and the board.

The board should consume:

- interpreted signals
- body-state abstractions
- context from action-pattern layers

It should not depend on MuJoCo names, IDs, or rendering assumptions.

## 4. Engine-to-world-model interface

The engine should not build the world model.

It should provide:

- raw readings
- body state
- contact geometry if needed

The world-model layer should decide how to use those inputs.

## 5. Pattern-to-engine interface

Action-patterns should generate:

- action requests
- modulation outputs
- recruitment or halt signals

The backend should only receive the low-level actuation form needed to realize them.

## Physics Backend Interface

The project should define a `PhysicsBackend` interface or equivalent protocol.

Suggested responsibilities:

- `load_body_schema(...)`
- `load_environment(...)`
- `reset(...)`
- `step(...)`
- `apply_actions(...)`
- `read_raw_sensors(...)`
- `read_body_state(...)`
- `render_sensor_view(...)`
- `query_contacts(...)`

Then:

- `MuJoCoBackend` is one implementation
- additional backends can be added later if justified

## MuJoCo as the Default Backend

For the present bench, MuJoCo is a sensible default backend because it is strong at:

- articulated body simulation
- contact-rich locomotion and manipulation
- tendon and actuator modeling
- efficient stepping
- model-based robotics workflows
- procedural model generation
- low-level sensor integration

Official documentation emphasizes:

- generalized-coordinate articulated dynamics
- contact handling
- tendon geometry
- broad actuator abstractions
- reconfigurable computation
- plugins for custom sensors/actuators

Sources:

- https://mujoco.readthedocs.io/en/stable/overview.html
- https://mujoco.readthedocs.io/en/stable/computation/index.html
- https://mujoco.readthedocs.io/en/stable/XMLreference.html

## MuJoCo-Specific Assumptions That Must Be Isolated

Even if MuJoCo remains the default backend, the following should be isolated behind the adapter boundary.

### 1. MJCF construction

No long-term experiment script should directly build MJCF strings or rely on MJCF structure internally.

### 2. Sensor naming conventions

No architectural layer should depend on MuJoCo sensor names like:

- `whisker_0`
- `gyro`
- `vel`

Those should be mapped into backend-independent modality channels.

### 3. Rendering pipeline assumptions

Visual modality code should not directly assume MuJoCo renderer semantics at the experiment level.

### 4. Contact and body-ID conventions

Body IDs, geom IDs, and raw contact indexing should stay inside the backend adapter.

### 5. Pose conventions

If the backend provides specific coordinate conventions, those should be normalized into bench-level geometry interfaces.

## Known Limits of MuJoCo for This Bench

MuJoCo is good for the current direction of the project, but there are limits.

It is less naturally suited to being the sole backend if the bench moves toward:

- truly flexible whiskers as first-class mechanics
- highly deformable bodies
- richly deformable terrain or substrate mechanics
- soft robotics as the primary body model
- specialized wave or field simulation beyond ordinary sensor approximations

These are not immediate reasons to abandon MuJoCo. They are reasons to keep the backend boundary clean.

## When Engine Substitution or Supplementation Is Justified

The project should consider adding or comparing another backend if:

- flexible appendage physics becomes central to the claim
- soft-body or deformable terrain dynamics become central
- very large-scale GPU-batched learning becomes a core workload
- sensor-generation needs exceed what the MuJoCo-based pipeline can support cleanly

Until then, MuJoCo should remain the default backend, but not the architecture.

## Practical Refactor Consequences

This boundary implies several concrete code decisions.

### 1. No direct backend construction in experiment scripts

Experiments should request:

- body
- modalities
- board
- patterns
- world model
- environment

from the bench assembly system, not build engine models themselves.

### 2. Backend-specific code moves into adapter/builders

MuJoCo-specific concerns should gradually move into:

- backend adapters
- backend body builders
- backend environment builders

### 3. Configs target bench abstractions

Config files should say:

- `board.type: hybrid`
- `modalities.vision.enabled: false`

not:

- MuJoCo geom names
- sensor IDs
- MJCF implementation details

### 4. Metrics remain backend-independent

The scoring and analysis layers should compare architectural variants, not backend internals.

## Example Flow Through the Boundary

One conceptual run should look like this:

1. `SMN-A48` body schema is selected.
2. The chosen backend compiles the body and environment into a physical model.
3. The backend advances physical state and returns raw readings.
4. The modality layer converts raw readings into interpreted modality signals.
5. The board updates coupling and modulation state.
6. The action-pattern layer updates BAP/HAP/SMAP/RAP/TAP/NAP state and emits action requests.
7. The backend applies low-level actions to the body.
8. The world-model layer updates from body-relative interpreted signals.
9. Metrics and experiment logic evaluate outcomes.

In that flow:

- the engine handles physical realization
- the bench handles cognition, architecture, and interpretation

## Why This Boundary Matters

Without an explicit engine boundary, the project risks:

- treating MuJoCo implementation details as theory
- baking backend assumptions into experiments
- making later engine comparison or substitution prohibitively expensive
- weakening the scientific claim that the bench tests SMN rather than one simulator setup

This document is therefore not just a software note. It is part of the methodological discipline of the project.

## Summary

The physics engine should remain:

- the substrate of embodiment
- the provider of raw physical and sensory primitives
- the mechanism for realizing action in a world

The SMN bench should remain:

- the definition of the body schema
- the organization of zones
- the board and pattern architecture
- the world-model logic
- the experiment logic
- the metrics and interpretation

MuJoCo is an appropriate default backend for now, but only if the project keeps this boundary clean.
