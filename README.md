# smn-lab — an experimental bench for cognitive science based on the SMN architecture

An embodied, configurable simulation bench for studying the **Sensation
Modulating Network (SMN)** architecture, built on **MuJoCo**. The control
architecture the SMN specifies drives a physical body in a physics world, so the
architecture's predicted empirical contrasts (its *registers*) can be reproduced
from real sensorimotor engagement — and so the **modulatory coupling topology
(the "balance beam") can be varied as an experimental independent variable**.

Based on the architecture described in:

> Nagarjuna, G. & D. Karnam. *The Sensation Modulating Network.* arXiv:2605.26856.
> https://arxiv.org/abs/2605.26856

## Why a bench (the experiment)
- **Control (fixed):** the body (zones, transducers, modulators), the world, the task ("explore and build a model").
- **Independent variable:** the balance-beam topology — {layered, non-layered} × {hierarchical, distributed} × {±BAP} × {±HAP}.
- **Dependent variable:** the state-space (world model) the agent constructs — forward-model accuracy, reafference self/world separation, dimensionality, stability, and *which registers emerge under which topology*.

It is intended as a reusable testbed for SMN hypotheses, including multi-agent
ones (shared intentionality; self/world/other).

## Architecture → simulation mapping
| SMN component | In the bench |
|---|---|
| Zone / CAZ | a body segment + actuated joint that senses and acts (dual-port) |
| S — transducer | rangefinder "whiskers", contact, gradient sensors |
| M — modulator | MuJoCo pull-only antagonist actuators (a zone's two Sensation Modulators) |
| N — communication board = **balance beam** | the coupling topology routing modulation among zones — **the IV** |
| BAP | coupled CPG oscillators (baseline rhythm; ±BAP toggle) |
| HAP | haltable controller recruited by sensed affordances (±HAP toggle) |
| snapshot / world model | the state-space built from (action, modulated-sensation) — **the DV** |
| world / habitat | arena with objects/affordances |
| multi-agent | 2+ agents → shared intentionality / self-world-other |

## Install & run
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd experiments && ../.venv/bin/python p0_reafference.py
```

## Current capability — the reafference register in the body
A single Coordinated Action Zone (a yaw "head" driven by a pull-only antagonist
pair) carries one rangefinder "whisker" and sweeps a static walled arena. A
forward model keyed on the agent's own heading learns the whisker reading during
a self-motion phase, then:

- **self-motion** (world static): residual ≈ sensor noise floor — **mean |res| ≈ 9.6 mm**
- **exafference** (an object the agent did *not* move slides in): residual jumps —
  **mean |res| ≈ 90 mm (×9.4), peak ≈ 723 mm**

The self/world distinction emerges structurally, from the wiring and real
physics. Output: `figures/p0_reafference.png`.

## Also available — a multi-CAZ agent that builds a world model
A planar "mouse" with a steering Coordinated Action Zone (pull-only antagonist
pair) and a five-whisker rangefinder fan explores a walled arena with two
objects. A Basal Action Pattern (CPG) provides the locomotor drive; a Haltable
Action Pattern, recruited by the whisker affordances, steers toward open space
and rotates in place when blocked. From its own pose plus each whisker's known
angle and measured distance, the agent accumulates hits into an occupancy map —
**the picture it constructs of its world from action and modulated sensation**.
It reconstructs the walls and both objects at **~97% surface coverage, ~99%
precision**. Output: `figures/p1_world_model.png`.

```bash
cd experiments && ../.venv/bin/python p1_world_model.py
```

## Roadmap
- **Done** — single-CAZ reafference (the self/world register) in the body.
- **Done** — multi-CAZ agent explores an arena and builds a faithful world model.
- **Done** — body-geometry-relative, self-localized world model: an explicit body schema (located drive zones + whiskers), locomotion from located opponent drive zones, and a map built from proprioceptive dead-reckoning rather than any absolute pose (~97% coverage, ~0.2 cm drift).
- **Next** — swappable balance-beam topology; sweeps over {layered/non-layered, hierarchical/distributed, ±BAP, ±HAP}; measure how the constructed state-space changes.
- Multi-agent (shared intentionality / self-world-other).
- Configuration-driven scenarios and rendering for reuse and presentation.

## Layout
- `smn_lab/body.py` — `MouseSchema`: the explicit body geometry (every zone's body-frame location), shared by the model builder and the agent.
- `smn_lab/model.py` — MJCF body/world builders (`build_p0/p1/p2_xml`).
- `smn_lab/control.py` — `OpponentBoard`, `ReafferencePredictor`, `CPG` (BAP drive), `HAPExplorer`, `DifferentialDrive` (located drive zones), `DeadReckoner` (proprioceptive self-localization); the balance beam lives here.
- `smn_lab/worldmodel.py` — `OccupancyMap` and the point-based map score (the constructed "picture").
- `experiments/p0_reafference.py` — single-CAZ reafference.
- `experiments/p1_world_model.py` — multi-CAZ agent builds a world model (uses true pose).
- `experiments/p2_world_model.py` — body-geometry-relative, self-localized world model (proprioception only).

## Citation
If you use this bench in published work, please cite the SMN paper:

> Nagarjuna, G. & D. Karnam. *The Sensation Modulating Network.* arXiv:2605.26856. https://arxiv.org/abs/2605.26856

## License
**GNU GPL v3 (or later).** See [`LICENSE`](LICENSE). Copyleft is deliberate: it
keeps derivatives free, so the bench and anything built on it stay open while
remaining usable commercially.
