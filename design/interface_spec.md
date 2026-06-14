# Interface Specification for the SMN Bench

## Purpose

This document specifies a researcher-facing interface for the SMN bench.

The guiding requirement is that the interface should be:

- functional rather than fancy
- understandable by researchers
- suitable for parameter exploration
- suitable for repeated experiments
- suitable for modular architecture comparison

The target interaction style is closer to a **NetLogo-like research console** than to a glossy dashboard or a custom simulation game.

## Interface Design Decision

The interface should borrow:

- the direct widget model of NetLogo
- the step/run/reset parameter interaction pattern of simulation consoles
- the parameter form model of Mesa/Solara-style browser interfaces
- the current honesty of the existing `smn-lab` app, which runs the real code

The interface should avoid:

- heavy custom front-end engineering
- decorative animation
- visually dense dashboarding
- hiding experimental structure behind polished presentation

## Why NetLogo-Like Is the Right Direction

A NetLogo-like interface is suitable because it gives researchers:

- simple visible controls
- sliders, switches, choosers, and buttons
- clear `setup` / `go` / `step` style interaction
- a strong relationship between parameters and observable behavior
- a natural path to batch experimentation

This makes it easier to inspect the system as a scientific object rather than as a product demo.

## Main Interface Modes

The bench should expose four main modes.

## 1. Compose

Purpose:

- choose the architecture
- assemble an organism and experiment before running

Controls should include:

- body family
- CAZ count
- modality packages
- board family
- pattern-family toggles
- world-model type
- environment preset
- experiment preset

This mode makes the modular design visible.

## 2. Run

Purpose:

- execute a single live simulation or trial

Controls should include:

- `Setup`
- `Step`
- `Run`
- `Pause`
- `Reset`
- random seed
- simulation speed

This mode is the equivalent of the main NetLogo-style bench operation.

## 3. Inspect

Purpose:

- inspect the internal state of the organism and architecture while it runs

Panels should include:

- CAZ activity
- modality readings
- board state
- action-pattern state
- world-model state
- event log

This mode is essential for architecture work.

## 4. Sweep

Purpose:

- perform structured parameter experiments

This is the equivalent of a built-in BehaviorSpace-like tool.

Controls should include:

- choose parameters to vary
- choose ranges or discrete sets
- choose repetitions
- choose metrics
- run batch
- export results

This should become a first-class part of the bench, not an afterthought.

## Recommended Screen Layout

The interface should have a stable, legible layout.

## Left Sidebar: Composition and Controls

This should contain the major input controls, grouped by concern.

Sections:

- Preset
- Body
- Modalities
- Board
- Patterns
- World model
- Experiment
- Run controls

This is the main place where researchers alter the system.

## Center Panel: World

This is the main live simulation panel.

It should show:

- the physical world
- the organism moving in it
- optionally sensor overlays or contact overlays

The center panel should remain visually dominant.

## Right Sidebar: Inspectors

This should show the currently selected or most relevant internal state.

Possible sections:

- selected CAZ
- selected modality
- board summary
- active pattern family
- current metric summary

This should be compact and interpretable.

## Bottom Tabs

The bottom region should provide structured detail without crowding the live world.

Recommended tabs:

- `Plots`
- `Logs`
- `Documentation`
- `Batch Results`
- `Config`

This lets the interface remain shallow while still exposing detail.

## Core Controls

At minimum, the interface should always provide these controls.

## Run controls

- `Setup`
- `Step`
- `Run`
- `Pause`
- `Reset`
- `Randomize Seed`

## Experiment controls

- run duration
- repetitions
- perturbations
- lesions or ablations
- metric selection

## World-view controls

- camera view
- overlay toggles
- render speed or frame rate choice

## Save/export controls

- export config
- export run data
- export plots
- export batch results

## UI Panels by Architecture Layer

The UI should map directly to the modular architecture.

## Body panel

Should expose:

- body family
- CAZ count
- limb and segment structure
- symmetry/asymmetry presets
- gravity or surface assumptions if relevant

## Modalities panel

Should expose:

- modality on/off
- density
- noise
- latency
- range and field of view
- substitution presets such as `No Vision` or `Echo`

## Board panel

Should expose:

- board family
- topology
- decentralized / centralized / hybrid selection
- coupling density
- direct vs intermediated coupling
- fixed vs trainable
- learning rule if trainable

This is one of the most important panels in the whole interface.

## Patterns panel

Should expose:

- enable/disable BAPs
- enable/disable HAPs
- enable/disable SMAPs
- enable/disable RAPs
- enable/disable TAPs
- enable/disable NAPs
- local/global scope settings
- NAP adaptation and invention toggles

## World-model panel

Should expose:

- world-model type
- decay
- reference frame
- binding rule
- metric family

## Experiment panel

Should expose:

- task
- environment
- perturbations
- ablations
- repetitions
- runtime mode

## Metrics panel

Should expose:

- which metrics to compute
- which summaries to display
- which plots to render live

## Presets

Presets are essential for usability.

The interface should support named presets that bundle architecture choices into meaningful starting points.

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

Presets lower the threshold for use by researchers who did not build the codebase.

## Inspect Mode Details

Inspect mode should not be an afterthought. The bench is about architecture, so internal observability matters.

Recommended inspectables:

- live CAZ activation table
- active coupling graph or summary
- selected appendage or CAZ details
- modality channel values
- action-pattern state
- world-model update stream
- current order parameters or binding state

Not every panel must always be visible, but they should be available.

## Sweep Mode Details

Sweep mode should be a built-in experiment runner inspired by NetLogo’s BehaviorSpace.

It should support:

- one-factor sweeps
- multi-factor sweeps
- repetitions
- seed control
- conditional metric recording if needed
- export to CSV/NPZ
- experiment bundles saved as config

This is important for architectural science. A single-run UI is not enough.

## Documentation Integration

The interface should preserve one current strength of the bench: inline documentation.

Each preset or experiment should link directly to:

- what the module does
- what parameters mean
- what metrics are reported
- what assumptions are in force

This keeps the interface scientifically legible.

## Relationship to the Config System

The interface should sit on top of the config schema rather than invent a separate UI-only model.

Meaning:

- every UI state should correspond to a config
- presets should be config bundles
- exports should produce valid config files

This keeps the UI and the bench aligned.

## Relationship to the Backend Boundary

The interface should expose bench-level concepts, not backend-specific ones.

Good UI terms:

- `board type`
- `echo enabled`
- `NAP adaptation`

Bad UI terms:

- MuJoCo geom names
- sensor IDs
- MJCF internal details

This keeps the interface useful even if the backend later changes.

## Recommended Implementation Path

## Short term

Use the current Streamlit stack.

Reason:

- already present
- enough for forms, tabs, plots, and batch launch controls
- low implementation burden

## Medium term

If the bench grows more stateful and inspection-heavy, consider a more reactive Python UI stack such as Solara.

But the immediate goal is not a migration. The immediate goal is to redesign the current interface around the modular architecture.

## Development Priority

The best implementation order is:

1. config-driven system assembly
2. architecture-layer controls
3. improved inspect panels
4. sweep panel
5. presets
6. richer visualizations if still needed

The sweep panel is especially important because it turns the interface into a real experimental console.

## Summary

The recommended interface is:

- NetLogo-like in interaction model
- modular in architecture exposure
- parameterized through the config schema
- researcher-facing rather than decorative
- implemented first in Streamlit

It should provide:

- a `Compose` mode
- a `Run` mode
- an `Inspect` mode
- a `Sweep` mode

with:

- a left control sidebar
- a central world view
- a right inspection sidebar
- bottom tabs for plots, logs, docs, batch results, and config

This is the most practical and scientifically appropriate interface direction for the SMN bench.
