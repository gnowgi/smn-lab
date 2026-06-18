# smn-lab

An embodied, configurable experimental bench for the **Sensation Modulating
Network (SMN)** architecture, built on [MuJoCo](https://mujoco.readthedocs.io). The
control architecture the SMN specifies drives a physical body in a physics world,
so the architecture's predicted contrasts can be reproduced from real sensorimotor
engagement — and the things the theory says matter (coupling topology, modulation,
body geometry) can be varied as experimental variables and measured.

Every experiment is **pre-registered** (hypothesis, order parameter, matched foil,
pass/fail fixed before running; see the [test plan](test-plan.md)) and exports tidy,
self-describing [datasets](datasets.md). The bench is meant as a *generative model*
others can verify and mine, not a fixed set of results.

Architecture reference: Nagarjuna, G. & D. Karnam. *The Sensation Modulating
Network.* [arXiv:2605.26856](https://arxiv.org/abs/2605.26856).

## What the lab looks like

The agent's body (its morphology and sensors), the physics world it moves in, and
the kind of data the bench produces:

![The 3D world — a segmented crawler and an object in a walled MuJoCo arena](figures/hero_world_3d.png)
*The 3D physics world (MuJoCo): the segmented crawler — coloured dots are its
bilateral sensors — and an object in a walled arena.*

![An agent and its world — morphology in the diagram grammar (left) and the experimental conditions (right)](figures/setup_c1_touch.png)
*Every experiment is specified by an **agent** (built in the
[diagram grammar](diagram-grammar.md)) and a **world**. Here: a three-block crawler
with a ventral touch skin and bilateral chemical sensing, a chemical field, and an
object on its path to the source.*

![A sample result — the crawler climbs a chemical gradient; the messaging beam on its body; the gait loop in state-space](figures/c0_crawler.png)
*A sample result ([C0](experiments/c0_crawler.md)): the crawler climbs a chemical
field (left), the messaging beam drawn on its body (middle), and its gait cycle in
state-space (right).*

## Start here

- **New to the bench?** Read [Lesson 1 — the construction of experience](lesson1.md)
  (why the minimal organism is a three-segment axial crawler), then the
  [diagram grammar](diagram-grammar.md) (how every figure of an agent is read).
- **Want the model organism?** [C0](experiments/c0_crawler.md) (it moves) and
  [C1](experiments/c1_touch.md) (it touches and halts).
- **Want the science?** The [test plan](test-plan.md) (what each experiment claims
  and how it could be falsified) and the [datasets](datasets.md) page.

## The experiments

Two lines, kept separate in the navigation:

- **Experiments** — the disciplined model organism and the going-forward science,
  all on one well-characterized body that varies a single parameter at a time:
  the crawler ([C0](experiments/c0_crawler.md), [C1](experiments/c1_touch.md)),
  the sweeps and core questions (locomotion as a network effect; geometry →
  world model; self/world; the resolution principle), and the **preprint
  predictions** (haltability signatures, zonal dissociations, antagonistic
  benefits) reproduced quantitatively.
- **Trial experiments** — the bench's first exploratory studies (the P/E series),
  kept as provenance and read as proofs-of-concept, not clean ablations (see the
  [reproducibility note](reproducibility.md)).

## What's in the lab (`smn_lab/`)

| module | what it provides |
|---|---|
| `crawler.py` | `build_crawler_xml` — the minimal axial crawler (segments, pull-only opponent pairs); `apply_anisotropic_drag` — the overdamped medium that turns a traveling wave into thrust. |
| `morphology.py` | `BodySchema` / `CAZ` / `Segment` + `render_morphology`, `render_network` — the [diagram grammar](diagram-grammar.md): one schema is the source of truth for both the body and its figures. |
| `control.py` | `MessagingBeam` (coupled-oscillator traveling wave + chemotaxis), `OpponentBoard` (pull-only antagonist board), `ReafferencePredictor`, `DeadReckoner`, and the action-pattern layers (`BAPG`, `HAPExplorer`, `DifferentialDrive`). |
| `fields.py` | `ScalarField` — virtual chemical/thermal fields sampled bench-side (per the [engine boundary](assumptions.md)). |
| `sweep.py` | `run_sweep` / `export_curated` — the parametric-sweep + dataset-export harness (summary.csv + timeseries.parquet + manifest). |
| `viz.py` | `draw_beam_graph`, `plot_state_space` — the messaging beam and its dynamic state. |
| `body.py`, `model.py`, `vision.py`, `worldmodel.py` | the earlier trial line (the planar "mouse" builders, camera, occupancy map). |

## Quickstart
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd experiments && ../.venv/bin/python c0_crawler.py   # the minimal crawler
```

## How the pieces fit
The body is an **axial chain of segments**; each inter-segment joint is a **CAZ** —
a pull-only **opponent pair**. The **messaging beam** couples the joints
(nearest-neighbor phase coupling) into a **traveling wave** (locomotion), which the
**anisotropic medium** turns into net thrust; a bilateral field gradient biases the
wave (**chemotaxis**). Sensors — a ventral touch skin, bilateral field strips,
distal localizers — are read against the body geometry; the agent **dead-reckons**
its own motion (reafference), separating self-caused from world-caused change. Each
experiment holds the world fixed and varies one architectural quantity — coupling
strength, segment count, modulation, co-contraction — measuring the result and
exporting the data.

## See also
- [Concepts](concepts.md) — the SMN → simulation mapping and vocabulary.
- [Assumptions](assumptions.md) — what is simulated vs computed vs idealized.
- [Datasets](datasets.md) — the bench as a generative model; the export format.
- [NetLogo integration (feasibility report)](integrations/netlogo.md).
- Building these docs: `pip install mkdocs && mkdocs serve` (or publish via Read the Docs).
