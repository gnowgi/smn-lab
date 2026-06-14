# Config Schema Specification for the SMN Bench

## Purpose

This document specifies the configuration model needed to make the bench modular and tweakable by others. The aim is to let users compose runs by configuration rather than by editing experiment code.

The config system should support:

- stable organism definitions
- swappable modality packages
- alternative board architectures
- pattern-family toggles
- world-model variants
- experiment tasks and perturbations
- UI-driven parameter exposure

## Design Principles

The schema should be:

- layered by concern
- explicit rather than magical
- composable from multiple files
- stable enough for UI generation
- expressive enough for architectural variation

Recommended format:

- YAML or TOML

Recommended assembly model:

- base organism file
- zero or more overlay files
- experiment file

## Top-Level Schema

Suggested top-level sections:

```yaml
system:
body:
modalities:
board:
patterns:
world_model:
environment:
experiment:
metrics:
ui:
```

## 1. `system`

General run-level settings.

Example fields:

```yaml
system:
  name: smn_a48_hybrid_full
  organism: SMN-A48
  seed: 7
  duration_s: 180
  dt: 0.005
  repetitions: 8
```

## 2. `body`

Defines geometry and CAZ structure.

Example fields:

```yaml
body:
  type: smn_a48
  caz_count: 48
  limb_count: 8
  segment_count: 5
  symmetry: bilateral
  asymmetry_preset: exploratory_front_bias
  gravity_mode: earth
  surface_mode: planar
```

Additional fields may include:

- appendage layout
- trunk segmentation
- mount-map preset
- reduced or expanded variant tags

## 3. `modalities`

Defines which transducer packages are present.

Example structure:

```yaml
modalities:
  proprioception:
    enabled: true
    noise: low
  force_contact:
    enabled: true
    density: default
  tactile_range:
    enabled: true
    range_m: 0.8
    density: medium
  vision:
    enabled: false
  echo:
    enabled: true
    angular_resolution: coarse
    range_m: 2.5
  chemical:
    enabled: false
```

Common fields:

- `enabled`
- `density`
- `noise`
- `latency_ms`
- `range_m`
- `fov_deg`
- `asymmetry`

## 4. `board`

Defines messaging-board architecture and coupling.

Example:

```yaml
board:
  type: hybrid
  topology: small_world
  direct_coupling: false
  intermediary_units: relay
  coupling_density: 0.11
  trainable: false
  learning_rule: none
  context_gating:
    hap: true
    nap: true
```

Expected fields:

- `type`
  - decentralized
  - centralized
  - hybrid
  - reservoir
  - neural
- `topology`
  - local
  - hierarchical
  - small_world
  - hub_rich
- `direct_coupling`
- `intermediary_units`
- `coupling_density`
- `trainable`
- `learning_rule`
- `context_gating`

## 5. `patterns`

Defines pattern families and their settings.

Example:

```yaml
patterns:
  bap:
    enabled: true
    mode: gait_default
  hap:
    enabled: true
    scope: regional
    interrupt_strength: medium
  smap:
    enabled: true
  rap:
    enabled: true
    library: default
  tap:
    enabled: false
  nap:
    enabled: true
    adaptation: false
    invention: false
```

This section should support:

- family enable/disable
- scope
- recruitment rules
- adaptation or invention toggles

## 6. `world_model`

Defines representation and update rules.

Example:

```yaml
world_model:
  type: living_snapshot
  reference_frame: body_relative
  decay: 0.1
  binding_rule: coupled_differentiae
  affordance_layers:
    support: true
    obstacle: true
    object: true
```

Expected fields:

- `type`
- `reference_frame`
- `decay`
- `binding_rule`
- `affordance_layers`
- `metric_family`

## 7. `environment`

Defines the physical and task environment.

Example:

```yaml
environment:
  arena: uneven_testbed
  gravity: normal
  surfaces:
    floor: rough
    walls: enabled
  objects:
    count: 4
    distribution: mixed
  fields:
    chemical: false
    thermal: false
```

This keeps environment assumptions out of the body and experiment sections.

## 8. `experiment`

Defines the experimental task and intervention.

Example:

```yaml
experiment:
  task: cross_modal_objecthood
  perturbations:
    self_motion_mix: true
    external_motion: true
  ablations:
    no_vision: true
  logging_level: full
```

Typical fields:

- task
- perturbations
- ablations
- lesions
- repetition schedule
- runtime mode

## 9. `metrics`

Defines what is measured and stored.

Example:

```yaml
metrics:
  world_model:
    coverage: true
    precision: true
    free_space: true
  objecthood:
    category_count: true
    persistence: true
  reafference:
    residual_separation: true
  board:
    largest_component: true
    coupling_entropy: false
```

This section should be explicit so the UI can render the available outputs.

## 10. `ui`

Optional UI hints and preset behavior.

Example:

```yaml
ui:
  preset_label: Echo Without Vision
  expose_advanced_board_controls: true
  default_panels:
    - body
    - modalities
    - board
```

## Config Composition

The system should support composition from multiple files.

Example directory layout:

```text
configs/
  organisms/
    smn_a24.yaml
    smn_a48.yaml
  modalities/
    no_vision.yaml
    echo_substitution.yaml
  boards/
    ganglionic.yaml
    hybrid_small_world.yaml
    reservoir.yaml
  experiments/
    p0_reafference.yaml
    world_model_threshold.yaml
```

A run might be assembled from:

- one organism config
- one or more modality overlays
- one board config
- one experiment config

## Validation Requirements

The schema should be machine-validated.

At minimum:

- required sections must exist
- enumerated fields must be checked
- numeric ranges must be validated
- incompatible combinations must fail early

Examples of invalid combinations:

- `vision.enabled: false` with vision-only task requirement
- `board.trainable: true` with no learning rule
- `caz_count: 48` on a body type that only supports 24

## UI Implications

Because the schema is organized by concern, it can drive the UI directly.

Sections map naturally to panels:

- body panel
- modalities panel
- board panel
- patterns panel
- world-model panel
- experiment panel
- metrics panel

Presets can simply be config bundles.

## Immediate Implementation Recommendation

First implement:

- `body`
- `modalities`
- `board`
- `patterns`
- `world_model`
- `experiment`

Then add:

- validation
- UI bindings
- preset composition

## Summary

The config system should become the bench's public composition language. If done well, it will let others vary:

- organism
- modalities
- board
- pattern families
- world-model type
- experiment task

without editing code.
