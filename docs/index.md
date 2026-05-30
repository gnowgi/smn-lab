# smn-lab

An embodied, configurable experimental bench for the **Sensation Modulating
Network (SMN)** architecture, built on [MuJoCo](https://mujoco.readthedocs.io).
The control architecture the SMN specifies drives a physical body in a physics
world, so the architecture's predicted contrasts (its *registers*) can be
reproduced from real sensorimotor engagement — and the **modulatory coupling
topology (the "balance beam") can be varied as an experimental variable**.

Architecture reference: Nagarjuna, G. & D. Karnam. *The Sensation Modulating
Network.* [arXiv:2605.26856](https://arxiv.org/abs/2605.26856).

## What's in the lab

### Library (`smn_lab/`)
| module | what it provides |
|---|---|
| `body.py` | `MouseSchema` — the explicit body geometry (every zone's body-frame location), shared by the model builder and the agent. |
| `model.py` | `build_p0/p1/p2_xml` — MJCF body + world builders. |
| `control.py` | `OpponentBoard`, `ReafferencePredictor`, `CPG` (BAP drive), `HAPExplorer` (affordance-recruited, swappable routing), `DifferentialDrive` (located drive zones), `DeadReckoner` (proprioceptive self-localization). |
| `worldmodel.py` | `OccupancyMap`, surface sampling, the point-based coverage/precision score, data dump. |

### Experiments (`experiments/`)
| experiment | shows | page |
|---|---|---|
| `p0_reafference.py` | reafference (self vs world) in a single CAZ | [P0](experiments/p0_reafference.md) |
| `p1_world_model.py` | a multi-CAZ agent builds a world model (true pose) | [P1](experiments/p1_world_model.md) |
| `p2_world_model.py` | the same, body-relative + self-localized (no god's-eye pose) | [P2](experiments/p2_world_model.md) |
| `p2_topology_sweep.py` | the balance-beam sweep: routing × morphology × ±BAP/±HAP × noise | [Sweep](experiments/p2_topology_sweep.md) |
| `p2_living_snapshot.py` | the world model decays where unrevisited (a living snapshot) | [Living snapshot](experiments/p2_living_snapshot.md) |
| `p2_basal_coupling.py` | why the agent moves — energy · food · map · motion as one closed loop | [Basal coupling](experiments/p2_basal_coupling.md) |
| `scene_geometry.py` | the body schema + agent-in-scene figures (and a MuJoCo render) | — |

## Quickstart
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd experiments && ../.venv/bin/python p2_world_model.py
```

## How the pieces fit
`MouseSchema` (body geometry) builds the MuJoCo body and is also what the agent
knows about itself. Each step: the whisker **transducers** sense; the **HAP**
layer turns affordances into a steering command (its *routing* is the balance
beam); the **BAP** provides the locomotor drive; the **DifferentialDrive** board
turns (forward, turn) into the located opponent drive-zone activations; the agent
**self-localizes** from proprioception and places hits into its **world model**.
The experiment holds the body/world/task fixed and varies the balance beam,
measuring the constructed world model (coverage, precision, drift).

## See also
- [Concepts](concepts.md) — the SMN → simulation mapping and vocabulary.
- [Assumptions](assumptions.md) — what is simulated vs computed vs idealized (common + per-experiment).
- Building these docs: `pip install mkdocs && mkdocs serve` (or publish via Read the Docs).
