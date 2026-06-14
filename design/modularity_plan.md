# Modularity Plan for the SMN Bench

## Purpose

If the bench is to become tweakable by other researchers, it must be modular by design rather than by convention. The goal is not merely cleaner code. The goal is to make it possible for a user to:

- switch one architectural concern on or off
- compare variants while holding all other concerns constant
- compose experiments without rewriting core code
- expose the major experimental levers through parameters and UI

This note describes a modular architecture for the bench that separates concerns cleanly enough for experimentation, reuse, and collaboration.

## Main Design Principle

The bench should be organized around:

- fixed interfaces
- swappable modules
- parameterized composition
- config-driven assembly
- UI-visible controls

The experiment should compose modules rather than define them internally.

## Main Separation of Concerns

The bench should be split into six main layers.

## 1. Body Layer

Defines:

- skeleton
- CAZ locations
- joint topology
- appendage layout
- body geometry
- bilateral and asymmetric structure
- transducer mounting points

Examples of switchable choices:

- body family
- limb count
- segment count
- CAZ count
- body symmetry/asymmetry preset
- gravity and surface assumptions

This layer should not know about specific experiments.

## 2. Modality Layer

Defines:

- vision
- echo-location
- tactile-range
- force/contact
- chemical/gradient
- internal state channels

Examples of switchable choices:

- modality on/off
- density
- field of view or sensing range
- noise
- delay/latency
- asymmetry

This layer should attach transducers to pre-declared mount sites on the body.

## 3. Board Layer

Defines:

- messaging board / balance beam topology
- coupling distribution
- direct vs intermediated coupling
- fixed vs trainable board
- graph structure and relay structure

Examples of switchable choices:

- ganglionic / decentralized
- centralized
- hybrid hierarchical
- small-world
- hub-rich
- reservoir-like
- neural
- with or without backpropagation

This should be treated as one of the most important experimental axes.

## 4. Action-Pattern Layer

Defines:

- BAPs
- HAPs
- SMAPs
- RAPs
- TAPs
- NAPs

Examples of switchable choices:

- pattern family enabled/disabled
- recruitment rules
- interruption scope
- local vs global action control
- adaptation enabled/disabled
- invention of new NAPs enabled/disabled

This layer should depend on body and board interfaces, but not on any one experiment.

## 5. World-Model Layer

Defines:

- map or snapshot type
- update rules
- body-relative spatial model
- object-binding representation
- relational or affordance model

Examples of switchable choices:

- occupancy model
- decaying snapshot
- affordance field
- object-centric model
- relational geometry model
- body-relative versus alternative frame assumptions

This layer should expose scoring hooks rather than bundle them inseparably with the representation.

## 6. Experiment Layer

Defines:

- tasks
- environments
- ablations
- perturbations
- metrics
- logging
- analysis

Experiments should assemble the other layers rather than re-implement them.

## Target Package Structure

A more modular project structure could look like this:

```text
smn_lab/
  bodies/
  modalities/
  boards/
  patterns/
  worldmodels/
  environments/
  experiments/
  metrics/
  configs/
  ui/
  core/
```

Where:

- `core/` holds shared interfaces and composition logic
- the other packages implement interchangeable modules

This can coexist with the current structure at first, then gradually absorb it.

## Required Stable Interfaces

The key to modularity is not folders, but interfaces.

## Body interface

Should answer:

- what CAZs exist?
- where are they?
- what joints and segments exist?
- what mount points exist for transducers?
- what geometric transforms are available?

Example shape:

```python
body = BodyFactory.create(body_config)
body.cazs()
body.mount_points()
body.geometry()
body.transforms()
```

## Modality interface

Should answer:

- what signals are available?
- where are they mounted?
- what noise/latency/range assumptions hold?
- how are they updated each step?

Example shape:

```python
modalities = ModalitySuite.from_config(modality_config, body)
readings = modalities.read(state)
```

## Board interface

Should answer:

- which CAZs are coupled?
- how does modulation propagate?
- what hidden or relay units exist?
- is the board fixed or adaptive?

Example shape:

```python
board = BoardFactory.create(board_config, body)
board_state = board.step(zone_state, modality_state, context)
```

## Pattern interface

Should answer:

- which action patterns are enabled?
- how are they recruited, halted, negotiated, or adapted?
- what control outputs do they generate?

Example shape:

```python
patterns = PatternSuite.from_config(pattern_config, body, board)
actions = patterns.step(context, board_state, world_model_state)
```

## World-model interface

Should answer:

- how is the world state updated?
- what body-relative model is being built?
- what object or affordance structure is represented?

Example shape:

```python
world_model = WorldModelFactory.create(world_model_config, body)
world_model.update(readings, body_state, board_state)
```

## Experiment interface

Should answer:

- which environment and task are being run?
- which modules are assembled?
- what metrics are recorded?

Example shape:

```python
system = System(body, modalities, board, patterns, world_model, environment)
result = experiment.run(system, config)
```

## Parameter Design

Parameters should be grouped by concern and exposed through a stable schema.

They should not be embedded as ad hoc globals inside experiment scripts.

## Body parameters

Examples:

- `body.type`
- `body.caz_count`
- `body.limb_count`
- `body.segment_count`
- `body.symmetry`
- `body.appendage_layout`
- `body.gravity_mode`

## Modality parameters

Examples:

- `modalities.vision.enabled`
- `modalities.echo.enabled`
- `modalities.tactile.enabled`
- `modalities.chemical.enabled`
- `modalities.force.enabled`
- `modalities.noise`
- `modalities.latency`
- `modalities.density`
- `modalities.asymmetry`

## Board parameters

Examples:

- `board.type`
- `board.topology`
- `board.direct_coupling`
- `board.intermediary_units`
- `board.coupling_density`
- `board.trainable`
- `board.learning_rule`
- `board.context_gating`

## Pattern parameters

Examples:

- `patterns.bap.enabled`
- `patterns.hap.enabled`
- `patterns.smap.enabled`
- `patterns.rap.enabled`
- `patterns.tap.enabled`
- `patterns.nap.enabled`
- `patterns.hap_scope`
- `patterns.nap_adaptation`
- `patterns.nap_invention`

## World-model parameters

Examples:

- `world_model.type`
- `world_model.decay`
- `world_model.reference_frame`
- `world_model.binding_rule`
- `world_model.metric_family`

## Experiment parameters

Examples:

- `experiment.task`
- `experiment.environment`
- `experiment.duration`
- `experiment.seed`
- `experiment.repetitions`
- `experiment.ablations`
- `experiment.metrics`

## Configuration Design

The bench should move toward config-driven composition.

Each run should be definable by a configuration file rather than by editing code.

Recommended:

- YAML or TOML config files
- one base organism config
- one or more overlay configs for experiments

Example idea:

```text
configs/
  organisms/
    smn_a24.yaml
    smn_a48.yaml
  boards/
    ganglionic.yaml
    hybrid.yaml
    reservoir.yaml
  modalities/
    no_vision.yaml
    echo_only.yaml
    full_multimodal.yaml
  experiments/
    reafference.yaml
    world_model.yaml
    objecthood.yaml
```

Then runs can be assembled from multiple config fragments.

## UI Design

The UI should expose modular composition directly.

The current bench UI is experiment-oriented. The future bench UI should also be architecture-oriented.

## Core control panels

### Body panel

Should allow:

- select body family
- set CAZ count
- set limb/segment count
- choose symmetry or asymmetry preset

### Modalities panel

Should allow:

- modality on/off
- set density
- set range and field of view
- set noise and latency
- choose modality presets

### Board panel

Should allow:

- choose board family
- choose decentralized / centralized / hybrid
- set coupling density
- enable or disable intermediary units
- fixed vs trainable board
- choose learning rule if trainable

### Patterns panel

Should allow:

- enable or disable BAP/HAP/SMAP/RAP/TAP/NAP
- set local/global scope
- enable NAP adaptation or invention
- define recruitment presets

### World-model panel

Should allow:

- select world-model type
- set decay
- choose body-relative frame assumptions
- choose metric suite

### Experiment panel

Should allow:

- select task
- select environment
- select perturbations and lesions
- set duration, seeds, repetitions

### Metrics panel

Should allow:

- choose what to log
- choose plots and summaries
- compare multiple module variants

## Presets

To keep the system usable, the UI and config system should support presets.

Examples:

- `Minimal Reafference`
- `24-CAZ Mapper`
- `48-CAZ Canonical`
- `No Vision`
- `Echo Substitution`
- `Ganglionic Board`
- `Central Board`
- `Hybrid Board`
- `Reservoir Board`
- `NAP Learning On`

Presets lower the entry barrier for other researchers while still allowing expert tweaking.

## Logging and Observability

Modularity is not enough if users cannot inspect what the modules are doing.

The bench should log:

- body state
- modality readings
- board state
- action-pattern state
- world-model state
- experiment metrics

The UI should show:

- trajectory and posture
- active modalities
- board topology and active couplings
- zone activations
- world-model updates
- order parameters and objecthood metrics

This is essential if collaborators are to understand what changes when they switch modules.

## Migration Strategy

The bench does not need to be rewritten all at once.

A staged migration is better.

## Stage 1: interface extraction

- identify existing body, control, world-model, and experiment responsibilities
- define stable interfaces in `core/`
- wrap current implementations rather than replacing them immediately

## Stage 2: config introduction

- move hard-coded experiment parameters into configs
- allow experiments to instantiate modules from config

## Stage 3: board modularization

- extract board types as interchangeable modules
- make coupling topology a first-class parameter

## Stage 4: modality modularization

- separate modality definitions from body definitions
- support true on/off and substitution experiments

## Stage 5: pattern-family modularization

- expose BAP/HAP/SMAP/RAP/TAP/NAP families as swappable components

## Stage 6: UI refactor

- reorganize controls by concern rather than by script
- add presets, comparisons, and architecture panels

## What Should Stay Constant in Comparisons

A major reason for modularity is experimental clarity.

Users should be able to vary one thing while keeping others constant:

- same body, different board
- same board, different modalities
- same body and board, different action-pattern sets
- same organism, different world-model formalizations

This is the real scientific value of modular design.

## Immediate Recommendation

The most important first step is to define:

- the canonical system composition interface
- the config schema
- the board module interface

The board is likely to be the most interesting experimental lever, and config-driven assembly is the prerequisite for exposing it properly.

## Summary

The bench should become a modular laboratory in which users can switch on and off:

- body variants
- modality packages
- board families
- action-pattern families
- world-model variants
- experiment tasks

without editing core code.

That requires:

- clean separation of concerns
- stable interfaces
- config-driven assembly
- UI panels grouped by architecture layer
- presets for accessibility
- strong logging and observability

If implemented well, this will make the bench scientifically stronger, easier to collaborate on, and much more useful to outside users.
