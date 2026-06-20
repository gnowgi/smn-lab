# Related-work survey — what researchers do with MuJoCo & similar benches

*Working note for the instrument paper (§1.1 / §1.2). Compiled from a verified
literature survey (deep-research run, 2026-06; 20 sources fetched, 24/25 claims
confirmed by 3-vote adversarial verification). Citations are primary peer-reviewed
unless noted.*

## Headline

The dominant use of physics simulators (MuJoCo, PyBullet, Brax, Isaac, Webots,
Gazebo) in ALife and cognitive robotics is **performance optimization, not
hypothesis testing**. The genuine hypothesis-testing lineage is the minimal/enactive
tradition — but it runs on **bespoke, often non-reproducible** code, *not* a shared
physics bench. That gap is SMN-Lab's niche.

## Findings (verified)

1. **MuJoCo leads — *for RL*.** A multi-engine review (arXiv:2407.08590) finds
   MuJoCo "the leading framework due to its performance and flexibility, despite
   usability challenges." *Scope caveat:* the stronger claim that these engines are
   used *predominantly* for RL was **refuted (0-3)** — say "leading for RL", not
   "only for RL".

2. **Canonical MuJoCo benches = reward/imitation task-performance.** DeepMind
   Control Suite (Tassa et al. 2018, arXiv:1801.00690): "continuous control tasks …
   with interpretable rewards … performance benchmarks for RL agents." LocoMuJoCo
   (Al-Hafez et al. 2023, arXiv:2311.02496): an imitation-learning locomotion
   benchmark with "handcrafted metrics" and "state-of-the-art baseline algorithms."
   No hypothesis-testing scaffolding.

3. **Evo-robotics/embodied-AI = brain-body-morphology co-optimization for
   performance.** DERL (Gupta et al., Nature Comms 2021): evolve morphologies + PPO
   to solve locomotion/manipulation. Evolution Gym (Bhatia et al., NeurIPS 2021):
   co-optimize design+control of soft robots, "outperforming hand-designed robots."

4. **The ALife/minimal-cognition lineage uses evolved agents as *scientific
   instruments*.** Harvey, Di Paolo, Wood, Quinn & Tuci (Artificial Life 2005):
   evolutionary robotics "as a scientific tool for studying minimal models of
   cognition." Beer: evolve CTRNN "nervous systems" and analyze brain-body-
   environment dynamical systems ("frictionless brains") for *conceptual
   understanding*, not benchmarking. **← SMN-Lab's methodological lineage.**

5. **Precedent for hypothesis falsification.** Froese & Di Paolo (Connection
   Science 2010): a perceptual-crossing model where the task "cannot be solved by
   either participant independently" — and a proposed internal-circuit hypothesis was
   **falsified** by analyzing the evolved agents' actual dynamics; predicted patterns
   later seen in humans. *Caveat:* CTRNN simulations, **not** a physics-engine bench.

6. **What a raw engine lacks: the closed reafferent loop.** Pfeifer, Iida & Gomez
   (2006): morphological computation "only works if the agent is actually behaving …
   generating sensory stimulation" — correlated optic-flow/proprioceptive/tactile
   patterns via "tight interaction between the motor system and the various sensory
   systems." The engine gives dynamics; the experimenter must build the loop.
   *Caveat:* the "computation" label is contested (Müller & Hoffmann 2017); rely on
   the scoped "morphology offloads control / needs an active reafferent loop" reading.

7. **The decisive gap = reproducibility + shared model-organism methodology.**
   Sangati & Fukushima (Frontiers Neurorobotics 2023): prior enactive/PCE models are
   "hard to replicate … no source code … made available"; their PCE Simulation
   Toolkit is a purpose-built **open** bench whose contribution is *reproducibility
   and extensibility of cognitive-mechanism simulation*. **Direct template for
   SMN-Lab** — which brings the same discipline to *continuous MuJoCo physics*.

8. **Active inference (pymdp) is complementary, not a substitute.** Heins et al.
   (2022, JOSS, arXiv:2201.03904): the first open active-inference library, but
   discrete-state POMDPs with no embodied physics.

## How to use this in the paper
- §1.1: cite 1–4 for the "performance optimization" cluster; 4–5 for the lineage;
  7 for the reproducibility precedent.
- §1.2 "Why not just use MuJoCo directly?": three lacks — (a) the reafferent loop
  (6, Pfeifer); (b) a cognitive-architecture abstraction; (c) experimental
  scaffolding (matched foils, seeds, pre-registration, model organism). 8 (pymdp) as
  the complementary cognition-tool.

## Honesty caveats (carry into the paper)
- Scope MuJoCo-leadership to **"for RL"** (the "only for RL" claim was refuted).
- **Do not claim "first."** Isaac Lab, Brax, ManiSkill, Habitat/AI2-THOR/iGibson
  were *not* verified with primary claims here; phrase as "we are not aware of a
  physics-engine bench that …" and flag as an open check.
- Strongest hypothesis-testing exemplars are **pre-MuJoCo CTRNN** sims — itself the
  argument for building SMN-Lab, but state it as such.

## Sources (primary unless noted)
- arXiv:2407.08590 — multi-engine RL review (secondary/2024).
- Tassa et al. 2018, DeepMind Control Suite — arXiv:1801.00690.
- Al-Hafez et al. 2023, LocoMuJoCo — arXiv:2311.02496.
- Gupta et al. 2021, DERL — Nature Communications (s41467-021-25874-z).
- Bhatia et al. 2021, Evolution Gym — arXiv:2201.09863.
- Harvey, Di Paolo et al. 2005, "Evolutionary Robotics: A New Scientific Tool" — Artificial Life 11(1-2).
- Beer, minimally cognitive agents — casci.binghamton.edu/publications/embrob.
- Froese & Di Paolo 2010, perceptual crossing — Connection Science 22(1).
- Pfeifer, Iida & Gomez 2006, morphological computation — Springer (10.1007/11613022_2).
- Sangati & Fukushima 2023, PCE Simulation Toolkit — Frontiers in Neurorobotics (PMC10229854).
- Heins et al. 2022, pymdp — JOSS / arXiv:2201.03904.
