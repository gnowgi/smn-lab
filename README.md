# smn-lab — an experimental bench for cognitive science based on the SMN architecture

An embodied, configurable simulation bench for the **Sensation Modulating Network
(SMN)** architecture, built on **MuJoCo**. The control architecture the SMN
specifies drives a physical body in a physics world, so the architecture's
predicted contrasts can be reproduced from real sensorimotor engagement — and the
things the theory says matter (coupling topology, modulation, body geometry) can be
varied as experimental variables and measured.

Every experiment is **pre-registered** — hypothesis, order parameter, matched
foil, and pass/fail fixed *before* running — and exports tidy, self-describing
data. The bench is meant as a *generative model* others can verify and mine, not a
fixed set of results.

Based on the architecture described in:

> Nagarjuna, G. & D. Karnam. *The Sensation Modulating Network.* arXiv:2605.26856.
> https://arxiv.org/abs/2605.26856

**Live docs (start here): <https://smn-lab.readthedocs.io>**

## The model organism

The bench is built on one disciplined model organism — a **minimal axial crawler**
(an annelid-like chain of segments), derived in [Lesson 1](docs/lesson1.md) as the
smallest body that can *initiate non-inertial movement* and so the first body that
can have a world. Each inter-segment joint is a **CAZ** — a pull-only **opponent
pair** — and the joints are coupled by a **messaging beam** into a traveling wave.
Every agent is drawn in a consistent [diagram grammar](docs/diagram-grammar.md), so
its morphology, sensors, and coupling can be read at a glance, and the same body
schema generates both the simulation and the figures.

## Architecture → simulation mapping
| SMN component | In the bench |
|---|---|
| Zone / CAZ | an inter-segment joint driven by a pull-only opponent pair — sensing and acting in one (dual-interface) |
| S — transducer | ventral touch skin, bilateral field strips (chemical/thermal), rangefinder whiskers, camera |
| M — modulator | MuJoCo pull-only antagonist actuators (a zone's two Sensation Modulators) |
| N — communication board = **messaging beam** | the coupling among zones (`MessagingBeam`: nearest-neighbor phase coupling) — a key independent variable |
| FAP/BAP | the coupled-oscillator traveling wave (baseline locomotion) |
| HAP | a haltable action recruited by contact / goal change (halt-on-contact, halt-on-reversal) |
| world model | the shared state-space *insofar as it differentiates the world* — the dependent variable |
| world / habitat | a walled arena + virtual scalar fields + objects |

## Install & run

**Prerequisites:** Python 3.10+ (tested on 3.12) and `git`; Linux, macOS, or
Windows. MuJoCo, NumPy, and Matplotlib are the only dependencies — `pip` installs
them below (no separate MuJoCo binary or license needed).

```bash
# 1. get the code
git clone https://github.com/gnowgi/smn-lab.git
cd smn-lab

# 2. environment + dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. run the minimal crawler
cd experiments && ../.venv/bin/python c0_crawler.py
```

## The experiments

Two lines, kept separate (full list + per-experiment pages in the
[docs](https://smn-lab.readthedocs.io)):

**Experiments — the model organism and the going-forward science.** One
well-characterized body; one parameter varied at a time; a matched non-modulatory
foil; replicated seeds. Results so far (the framework is confirmed and corrected
about equally — that is the falsifiability working):

| experiment | what it tests | result |
|---|---|---|
| **C0 / C1** | the crawler moves (non-inertial); touches and halts | locomotion + chemotaxis; halt-on-contact = objecthood as resistance |
| **S0** coupling sweep | is locomotion a network effect? | **yes** — coupling locks the wave: foil 0.56 ± 0.28 m → coupled 0.75 ± 0.002 m |
| **S1** geometry → world model | does the world model scale with body geometry? | a real body-relative world model exists (decoding skill ≈ 0.4 ≫ shuffle 0); it does **not** scale with segment count — *prediction corrected* |
| **Q2** self / world (reafference) | does a self-motion forward model separate self from world? | partial — cancels ~37% of self-caused change (ratio 2.2 vs foil 1.58); cleanest in [P0](docs/experiments/p0_reafference.md) |
| **Q1 / Q1b** modulation & resolution | does modulation, not raw transduction, give resolution? | **yes** — without modulation, self/world resolution collapses as the body grows; with it, resolution rises with CAZ density (the resolution principle) |
| **Preprint pred. 1** haltability signatures | deceptive reach → distinct stop-resume + re-pairing | **confirmed** — a halt dwell (~0.17 s) + discrete effector re-pairing, absent in a smooth controller |
| **Preprint pred. 2** zonal dissociations | same task, different performance by material | partial — the optimal control moves with substrate (aggressive prior is catastrophic on a compliant tool); a conservative generic ≈ matched |
| **Preprint pred. 3** antagonistic benefits | co-contraction → faster perturbation correction | **confirmed** — peak deviation −4.4×, integrated error −28×, at a steep energy cost (a tradeoff) |

Each experiment's page makes the **raw data → math → plot** chain explicit, and
opens with a setup figure (agent morphology + world). Methodology and pass/fail are
pre-registered in the [test plan](docs/test-plan.md).

**Trial experiments — the bench's first exploratory studies** (the P/E series: a
planar "mouse" with whiskers; single- and multi-CAZ reafference; world-model
mapping, foraging, cross-modal discrimination). Kept as provenance and read as
proofs-of-concept, not clean ablations — see the
[reproducibility note](docs/reproducibility.md).

## Datasets & reproducibility
All randomness is seeded; runs are reproducible and stamped with the git commit.
The sweep harness (`smn_lab/sweep.py`) writes, per study, a tidy `summary.csv`
(one row per run: parameters + seed + metrics), a long-format `timeseries.parquet`,
and a `manifest.json` (grid, seeds, commit). Full data lands in `data/`
(gitignored, regenerable); a curated `summary.csv` per study ships in `samples/`.
The bench is a *generator* — sweep the grid as wide as you like.
See [Datasets](docs/datasets.md).

## The lab interface
A simple Streamlit window so you — or a reviewer — can see the bench as **the math
in action**: pick an experiment, watch its actual MuJoCo world, and inspect the
graphs, computed results, and documentation side by side.
```bash
.venv/bin/pip install -r requirements-ui.txt    # one extra dependency: streamlit
.venv/bin/streamlit run app.py
```
A GL backend renders the world; the core bench does not need streamlit. More
detail: [the lab interface docs](docs/lab-interface.md).

## Layout (`smn_lab/`)
- `crawler.py` — `build_crawler_xml` (the minimal axial crawler) + `apply_anisotropic_drag` (the overdamped medium).
- `morphology.py` — `BodySchema`/`CAZ`/`Segment` + `render_morphology`/`render_network`: the diagram grammar (one source of truth for body and figures).
- `control.py` — `MessagingBeam` (traveling wave + chemotaxis), `OpponentBoard`, `ReafferencePredictor`, `DeadReckoner`, and the action-pattern layers (`BAPG`, `HAPExplorer`, `DifferentialDrive`); plus the trial-line `CrossModalBoard` / `SubsumptionArbiter`.
- `fields.py` — `ScalarField`: virtual chemical/thermal fields sampled bench-side.
- `sweep.py` — `run_sweep` / `export_curated`: the parametric-sweep + dataset-export harness.
- `viz.py` — `draw_beam_graph`, `plot_state_space`: the messaging beam and its dynamic state.
- `body.py`, `model.py`, `vision.py`, `worldmodel.py` — the earlier trial line (planar "mouse" builders, camera, occupancy map).
- `experiments/` — one script per experiment (C/S/Q/predictions + the P/E trials); `doc_figs.py` generates the docs' setup figures and 3D render.

## Documentation
Live docs: **<https://smn-lab.readthedocs.io>**. Source in [`docs/`](docs/index.md);
build locally with `pip install -r docs/requirements.txt && mkdocs serve`.
[`docs/assumptions.md`](docs/assumptions.md) separates what the engine **simulates**,
what the code **computes**, and what is an **idealization**.

## Contributing experiments
New experiments live on their own `exp/<topic>` branch and are published as a
separate Read the Docs *version* (browsable alongside the stable `main` docs via
the version flyout); each starts with a preregistration page. Conventions and a
checklist: [`docs/contributing.md`](docs/contributing.md).

## Citation
If you use this bench in published work, please cite the SMN paper:

> Nagarjuna, G. & D. Karnam. *The Sensation Modulating Network.* arXiv:2605.26856. https://arxiv.org/abs/2605.26856

## License
**GNU GPL v3 (or later).** See [`LICENSE`](LICENSE).
