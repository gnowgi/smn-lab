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
- **Done** — the balance-beam sweep: the constructed world model measured across information-routing topology (flat vs hierarchical), body morphology (whisker count, drive track width), the ±BAP/±HAP toggles, and proprioceptive noise. **Findings:** removing the basal drive (−BAP) or the haltable affordance-action (−HAP) collapses coverage (20% / 44% vs 97%) — both are necessary to build a world model; proprioceptive noise smears the map (precision 100% → 74%, drift 6.7 cm); routing and morphology are robust at this task difficulty. See `figures/p2_topology_sweep.png`.
- **Done** — map decay / **living snapshot**: the world model fades where it is not revisited; live coverage of the full arena falls from 99% (accumulator) to 37% at decay 0.8/s — a moving local snapshot that trails the agent. See `figures/p2_living_snapshot.png`.
- **Done** — **basal coupling** (the first telling simulation): the agent carries an energy reserve, the BAP is energy-gated, and food in the world replenishes. Without food: dies at t ≈ 120 s. With food + regrowth: alive at t = 180 s with 19 consumption events. Same agent — the closed loop (movement ↔ energy ↔ food ↔ map) is what keeps it alive. See `figures/p2_basal_coupling.png`.
- **Done** — **map-guided foraging**: the HAP now reads a food-memory living-snapshot layer and steers toward remembered food when the path is clear of walls. The map's *decay rate* becomes a direct survival pressure — in a harsher world (4 foods, 90 s regrowth, 300 s horizon), slow decay (0.02 / s) keeps the agent **alive** at the end (8 consumption events); the no-map baseline **dies at 272 s** (5 events); fast decay (1.0 / s) dies *earlier* (175 s, 3 events) — the brief, misleading memory drags the agent back to just-eaten spots before food regrows. See `figures/p2_map_guided_foraging.png`.
- **Next** — multi-agent (shared intentionality / self-world-other).
- Configuration-driven scenarios and rendering for reuse and presentation.

## See the setup
`experiments/scene_geometry.py` draws the **body schema** (every zone's
body-frame location, the opponent drive pair, the whisker fan) and the **agent
placed in the scene** → `figures/agent_geometry.png`, plus a top-down MuJoCo
render `figures/scene_render.png` when a GL backend is available.

## Documentation
Live docs: **<https://smn-lab.readthedocs.io>**. The Markdown source lives in
[`docs/`](docs/index.md); build it locally with `pip install -r docs/requirements.txt && mkdocs serve`.

## What the simulation assumes
[`docs/assumptions.md`](docs/assumptions.md) is a living record separating what
the physics engine **simulates**, what the control code **computes**, and what is
an **idealization**. Assumptions are *layered* — a common core plus per-experiment
specifics that can add or override — and stated plainly (e.g. the whiskers are
distal rays, not tactile bristles; the map does not yet decay; co-activation data
at rest is not modelled).

## Data & reproducibility
All randomness is seeded, so runs are byte-reproducible.
- **Generated data → `data/`** (gitignored by directory name): each experiment writes its **point clouds + true/estimated trajectories** (`.npz`) and a `sweep_results.csv`. The data coverage/precision are computed from these. Regenerable, so kept out of git.
- **Curated demo data → `samples/`** (tracked): small example files with a [README](samples/README.md) explaining the format, so you can inspect the data without running anything.
- For a paper, a versioned snapshot (and a Zenodo DOI) will provide a frozen, citable dataset.

## Layout
- `smn_lab/body.py` — `MouseSchema`: the explicit body geometry (every zone's body-frame location), shared by the model builder and the agent.
- `smn_lab/model.py` — MJCF body/world builders (`build_p0/p1/p2_xml`).
- `smn_lab/control.py` — `OpponentBoard`, `ReafferencePredictor`, `CPG` (BAP drive), `HAPExplorer`, `DifferentialDrive` (located drive zones), `DeadReckoner` (proprioceptive self-localization); the balance beam lives here.
- `smn_lab/worldmodel.py` — `OccupancyMap` and the point-based map score (the constructed "picture").
- `experiments/p0_reafference.py` — single-CAZ reafference.
- `experiments/p1_world_model.py` — multi-CAZ agent builds a world model (uses true pose).
- `experiments/p2_world_model.py` — body-geometry-relative, self-localized world model (proprioception only).
- `experiments/p2_topology_sweep.py` — the balance-beam sweep (routing × morphology × ±BAP/±HAP × proprioceptive noise).
- `experiments/p2_living_snapshot.py` — the world model decays where unrevisited (the living snapshot).
- `experiments/p2_basal_coupling.py` — why the agent moves: energy + food + map + motion as one closed loop.
- `experiments/p2_map_guided_foraging.py` — the HAP reads a food-memory layer; the map's decay rate is a direct survival pressure.
- `experiments/scene_geometry.py` — draws the body schema + the agent in the scene (and a MuJoCo render).

## Citation
If you use this bench in published work, please cite the SMN paper:

> Nagarjuna, G. & D. Karnam. *The Sensation Modulating Network.* arXiv:2605.26856. https://arxiv.org/abs/2605.26856

## License
**GNU GPL v3 (or later).** See [`LICENSE`](LICENSE).
