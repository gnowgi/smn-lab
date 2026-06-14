# Refactor Plan for `smn-lab`

## Purpose

This note translates the modularity discussion into a concrete refactor plan against the current `smn-lab` codebase.

The current repository already has useful separations:

- `smn_lab/body.py`
- `smn_lab/control.py`
- `smn_lab/model.py`
- `smn_lab/worldmodel.py`
- `smn_lab/vision.py`
- `experiments/*.py`

But most experiments still assemble systems ad hoc inside the scripts. The main refactor goal is to move from:

- experiment-specific construction

to:

- config-driven system composition

## Current Codebase Strengths

The current code already has a solid starting point:

- explicit body schema work has begun
- world-model logic is at least partly isolated
- vision-specific logic is separated
- experiments are relatively readable
- docs are strong enough to guide a reorganization

The refactor should preserve those strengths.

## Current Pain Points

The biggest limitations of the current structure are:

- experiment scripts hard-code system assembly
- modality toggles are not first-class modules
- board variants are not isolated enough
- pattern families are not explicitly separated
- configs are not the public composition layer
- UI is experiment-oriented rather than architecture-oriented

## Refactor Target

The target is a modular system with:

- stable interfaces
- factories or builders
- config-driven composition
- swappable organism, modality, board, pattern, and world-model modules

## Proposed Package Evolution

The current package can evolve toward:

```text
smn_lab/
  core/
  bodies/
  modalities/
  boards/
  patterns/
  worldmodels/
  environments/
  metrics/
  systems/
  configs/
  ui/
```

This does not have to be done in one step.

## Recommended Module Mapping from Current Code

### Current `smn_lab/body.py`

Should evolve into:

- `bodies/schema.py`
- `bodies/smn_a24.py`
- `bodies/smn_a48.py`

### Current `smn_lab/model.py`

Should be split into:

- geometry/model builders
- environment builders
- body-to-MJCF assembly utilities

Likely destinations:

- `bodies/mjcf_builders.py`
- `environments/mjcf_envs.py`

### Current `smn_lab/control.py`

This is currently too broad. It should be decomposed into:

- board logic
- pattern logic
- drive and low-level actuation logic
- reafference and estimation logic

Suggested targets:

- `boards/`
- `patterns/`
- `core/actuation.py`
- `core/estimation.py`

### Current `smn_lab/worldmodel.py`

Should evolve into:

- `worldmodels/occupancy.py`
- `worldmodels/living_snapshot.py`
- `worldmodels/object_binding.py`
- `metrics/worldmodel_metrics.py`

### Current `smn_lab/vision.py`

Should evolve into:

- `modalities/vision.py`
- and eventually peer modules such as:
  - `modalities/echo.py`
  - `modalities/tactile_range.py`
  - `modalities/chemical.py`

## New Core Interfaces

Before moving files aggressively, define interfaces first.

## 1. Body interface

Needs methods for:

- CAZ inventory
- mount-point inventory
- geometric transforms
- MJCF attachment hooks

## 2. Modality interface

Needs methods for:

- initialization on a body
- per-step readings
- metadata about channels and mount points

## 3. Board interface

Needs methods for:

- initialization from body and config
- per-step coupling/modulation update
- optional training or adaptation step

## 4. Pattern interface

Needs methods for:

- per-step action-pattern update
- recruitment
- interruption
- negotiation

## 5. World-model interface

Needs methods for:

- update
- query
- reset
- score hooks

## 6. System assembler

A new `systems/assembler.py` or similar should take a config and assemble:

- body
- modalities
- board
- patterns
- world model
- environment

This becomes the common entry point for experiments and UI.

## Refactor Phases

## Phase 1: introduce `core` interfaces

Goal:

- define abstract interfaces and data contracts

No major logic changes yet.

Deliverables:

- base classes or protocols
- minimal config loader
- system assembly scaffolding

## Phase 2: wrap current implementations

Goal:

- adapt current code to the new interfaces without rewriting core behavior

Examples:

- wrap current `MouseSchema`
- wrap current occupancy map
- wrap current reafference predictor

This keeps behavior stable while the architecture becomes cleaner.

## Phase 3: split `control.py`

Goal:

- separate board, pattern, drive, and estimation responsibilities

This is likely the most important internal cleanup.

Suggested resulting modules:

- `boards/basic.py`
- `patterns/bap.py`
- `patterns/hap.py`
- `patterns/nap.py`
- `core/drive.py`
- `core/reafference.py`
- `core/dead_reckoning.py`

## Phase 4: move modality logic into `modalities/`

Goal:

- make sensor packages swappable

Current `vision.py` becomes the model for the modality interface.

New packages can then be added cleanly.

## Phase 5: introduce config-driven experiments

Goal:

- convert selected experiments from hard-coded assembly to config-based assembly

Start with:

- P0 reafference
- P2 world model
- P2 topology sweep

These are good first targets because they already reflect major architectural questions.

## Phase 6: UI reorganization

Goal:

- expose body, modalities, board, patterns, and world-model choices directly

The current UI can then move from:

- experiment picker

toward:

- architecture composer + experiment runner

## Minimal First Refactor Deliverables

The smallest meaningful first pass would produce:

1. `core/interfaces.py`
2. `core/config.py`
3. `systems/assembler.py`
4. one config-driven body module
5. one config-driven board module
6. one config-driven experiment runner

This would prove the modular architecture before the rest of the migration.

## Suggested Initial File Additions

Short-term additions:

- `smn_lab/core/interfaces.py`
- `smn_lab/core/config.py`
- `smn_lab/systems/assembler.py`
- `smn_lab/bodies/__init__.py`
- `smn_lab/modalities/__init__.py`
- `smn_lab/boards/__init__.py`
- `smn_lab/patterns/__init__.py`

## What Not to Do

The refactor should avoid:

- breaking all experiments at once
- introducing one huge generic class that hides all structure
- treating the board as just another controller detail
- burying architectural choices back inside scripts

The board and the body schema are too important for that.

## Recommended First Experiment After Refactor

Once the first modular slice exists, the best validation experiment is:

- same body
- same modalities
- same task
- different boards

That is the clearest proof that the modular refactor is scientifically useful rather than just cleaner code.

## Recommendation on Scope

This should be done incrementally. The right order is:

1. interfaces
2. wrappers
3. config assembly
4. board extraction
5. modality extraction
6. UI and richer organisms

That gives the project a stable path from the current `smn_lab` to a true configurable bench.

## Summary

The current codebase is already structured enough to refactor successfully, but the main shift is conceptual:

- from scripts that build systems
- to a system that runs scripts

That requires:

- interfaces
- config-driven assembly
- board modularization
- modality modularization
- UI reorganization

If these are done carefully, `smn_lab` can become a real modular laboratory for SMN experiments.
