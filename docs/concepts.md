# Concepts: the SMN → simulation mapping

The bench implements components of the SMN architecture as controllers driving a
MuJoCo body. The vocabulary below is used throughout the experiment pages.

## Architecture → simulation
| SMN component | In the bench |
|---|---|
| **Zone / CAZ** (Coordinated Action Zone) | a body segment + actuated DOF that senses and acts (dual-port). |
| **S — transducer** | a rangefinder "whisker" (distance sensor); contact/gradient sensors are possible. |
| **M — modulator** | a pull-only actuator; zones are **opponent pairs** (agonist/antagonist), giving a signed net activation. |
| **N — communication board = the "balance beam"** | the coupling that routes sensed affordances into the drive/steering command — the experimental **independent variable** (`HAPExplorer.routing`, drive mapping). |
| **BAP** — basal action pattern | a central pattern generator (`CPG`) providing the baseline locomotor drive. |
| **HAP** — haltable action pattern | `HAPExplorer`: action recruited/halted by sensed affordances. |
| **snapshot / world model** | the state the agent builds from (action, modulated sensation) — here an occupancy map. |
| **reafference** | a forward model keyed on the agent's own state; its residual separates self-caused from world-caused sensory change. |

## Key ideas
- **Opponency.** Each zone is an antagonist pair. This is not decoration: a body
  with only forward-pulling drives cannot rotate in place — opponent drive zones
  can (one forward, one back = pure torque). Steering and turning *require* it.
- **Body-relative world model.** The agent knows where its zones are (the body
  schema) and localizes from its own proprioception; the world model is built in
  the agent's own frame, never from an absolute "god's-eye" pose. (See the
  [P1 → P2](experiments/p2_world_model.md) shift.)
- **The balance beam as the variable.** The experiment fixes the body, world, and
  task, and varies the modulatory coupling + body geometry, asking: *does the
  structure of the balance beam determine the structure of the world the agent
  can build?*

## The experimental logic
- **Control (fixed):** body, world, task ("explore and build a model").
- **Independent variable:** the balance beam — routing topology (flat vs
  hierarchical), body morphology (zone count/placement), the ±BAP/±HAP toggles,
  proprioceptive noise.
- **Dependent variable:** the constructed world model — coverage, precision, and
  dead-reckoning drift.

For exactly what is simulated vs computed vs assumed, see
[Assumptions](assumptions.md).
