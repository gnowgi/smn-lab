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

## Reading the bench alongside the preprint

The navigation follows the preprint's section order, so each experiment sits
under the paper section it realizes:

| Preprint § | Bench pages |
|---|---|
| **§1 The modular unit** | the moving opponent body — C0, S0, antagonistic benefits; **R1** tonic-load coupling, **R2** resumption latency |
| **§2 Generative morphology** | the diagram grammar, the construction of experience |
| **§3 The self-model** | topology / branched / sheet–tube / nested self-model |
| **§4 World-model & self/world/other** | Q2, the reafference cut, W1/W2, Q1, the resolution principle (S1, Q1b), **R5** dual-signal residual |
| **§5 Haltability & object-directedness** | C1, the manipulator (E1), the haltable pattern (E3), haltability signatures |
| **§6 From resistance to object** | self/field/object (E2), cross-modal (deferred) |
| **§7 Taxonomy of action patterns** | the layering pivot, network scaling, zonal dissociations |

The **framework (reference)** pages are background for the whole arc; the
**provenance** section keeps the earlier exploratory studies. (§8, the paper's
positioning against competing accounts, is argued in the preprint and has no
bench experiment.)

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

- **New to the bench?** Read [The Construction of Experience](construction-of-experience.md)
  (why the minimal organism is a three-segment axial crawler), then the
  [diagram grammar](diagram-grammar.md) (how every figure of an agent is read).
- **Want the model organism?** [C0](experiments/c0_crawler.md) (it moves) and
  [C1](experiments/c1_touch.md) (it touches and halts).
- **Want the science?** The [test plan](test-plan.md) (what each experiment claims
  and how it could be falsified) and the [datasets](datasets.md) page.

## The experiments — a two-phase research programme

The path is organized as an *argument*, not a catalogue.

- **The organism** — the minimal moving body everything runs on
  ([C0](experiments/c0_crawler.md), [S0](experiments/sweep_c0_coupling.md)).
- **[Phase I](phase1.md) — grounding self, world & object in physics** (the current
  focus): a body whose zones modulate their own single-interface transducers
  constructs, in order, a **self-model** (one function, any body —
  [chain](experiments/self_model_topology.md),
  [tree](experiments/branched_self_model.md), tube), a **world-model** in its own
  frame from *modulated* transducers ([reafference](experiments/q2_reafference.md),
  [W1](experiments/world_in_self_graph.md), [W2](experiments/world_geometry_self_frame.md),
  [Q1](experiments/sweep_q1_modulation.md)), and **aboutness** as resistance
  ([C1](experiments/c1_touch.md), [E1](experiments/p4_manipulator_objecthood.md)).
  The case for CS+physics collaboration: cognitive tokens get specific meaning only
  when a physical construction fixes them.
- **[Phase I → II](phase2.md) — the pivot**: Phase I's own null result — adding
  transducers in a line does *not* enrich the world-model
  ([S1](experiments/sweep_geometry_worldmodel.md),
  [Q1b](experiments/sweep_q1b_resolution.md)).
- **[Phase II](phase2.md) — the evo-devo path** (pointed to): richer world-models
  need *architecture* — polarized → tubular → segmented → bilateral → appendicular —
  for **nested CAZ modulation**, not more identical zones.
- **Provenance / exploratory studies** — the bench's first exploratory studies (the
  P-series), kept as proofs-of-concept (see the
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
