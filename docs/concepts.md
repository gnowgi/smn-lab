# Concepts: the SMN → simulation mapping

The bench implements the SMN architecture as controllers driving a MuJoCo body —
now a family of bodies: the segmented **crawler** (C0/C1), spring-tendon
**lattices** (self-model, sheet/tube, nested), and the bilateral **manipulator**
(E3). The vocabulary below is used throughout the experiment pages.

## Architecture → simulation
| SMN component | In the bench |
|---|---|
| **Zone / CAZ** (Coordinated Action Zone) | a body element that both senses and acts (**dual-interface**); an opponent pair actuating one DOF. In the lattice bodies each link *is* a CAZ (a spring-tendon muscle). |
| **S — transducer** | a **single-interface** sensor: a bilateral field/chemical/thermal reader, a ventral touch skin, a contact/effort sensor, or a rangefinder. Not tied to any one modality. |
| **M — modulator** | a pull-only actuator; zones are **opponent pairs** (agonist/antagonist), giving a signed net activation. |
| **N — messaging beam** | nearest-neighbour (Kuramoto-style) phase coupling between zones — a traveling wave from local coupling alone, no centre (`smn_lab.control.MessagingBeam`). |
| **BAP** — basal action pattern | a central pattern generator (`CPG` / `MessagingBeam`) — the baseline drive. |
| **HAP** — haltable action pattern | an action recruited or **halted** by a sensed affordance (contact halt in C1; the manipulator's directed halt in E3). |
| **self-model** | the body's own graph, **recovered from movement** by the framework read-out `smn_lab.self_model.coupling` — one function, any topology, any scale. |
| **world-model** | world-geometry expressed **in the self-model's frame** (a feature localised on the self-graph), not an absolute map. |
| **reafference** | a forward model keyed on the agent's own state; its residual separates self-caused from world-caused change. |

## Key ideas

- **Opponency.** Each zone is an antagonist pair. A body with only forward-pulling
  drives cannot rotate in place — opponent zones can (one forward, one back = pure
  torque). Steering, turning, and *halting* require it.
- **The substrate is elastic and overdamped.** The self-model is recoverable only
  because links transmit motion elastically with attenuation (rigid → whole-body
  common mode → nothing to read), in the overdamped soft-tissue / low-Reynolds
  regime. Elasticity is a load-bearing commitment, not decoration.
- **Model vs. measurement.** What the *agent* computes (the self-model read-out,
  local, no central reader — Commitment C3) is kept in `smn_lab.self_model`; what
  the *experimenter* computes to score it against ground truth is kept in
  `smn_lab.metrics`. The boundary is visible in the module layout — see
  [model vs. measurement](self-model-and-measurement.md).
- **Self, then world, then object.** The progression grounds three cognitive tokens
  in order: the **self-model** (from CAZ modulation), the **world-model** (from
  *modulated* transducers, in the self-frame), and **object-directedness** (a
  haltable action pattern). See [Phase I](phase1.md).
- **One function, any body, any level.** The same `coupling` recovers the body graph
  for a chain, a tree, a sheet, a tube, and across scales of a nested lattice —
  topology- and scale-invariant.

## The experimental logic

- **Control (fixed):** body, world, task.
- **Independent variable:** the single commitment each rung isolates — joint
  **elasticity** (self-model), body **topology / scale** (sheet, tube, nested),
  **modulation** (Q1), or the presence of a stable layer (haltability).
- **Dependent variable:** the appropriate order parameter — self-model
  **endpoint/neighbour recovery**, world-model **decoding skill** (held-out, with a
  shuffle control), the reafference **residual ratio**, or the halt signature — each
  an experimenter-side [metric](self-model-and-measurement.md).

For exactly what is simulated vs computed vs idealized, see
[Assumptions](assumptions.md).
