# P0 — reafference (self vs world) in a single CAZ

## What it shows
The **reafference** register: an agent distinguishes self-caused from
world-caused sensory change, structurally, from its own wiring. The self/world
distinction emerges — it is not a category applied on top.

## Setup
A single Coordinated Action Zone: a yaw "head" driven by a **pull-only
antagonist pair** (two MuJoCo `motor` actuators on the yaw joint), carrying one
rangefinder **whisker**, inside a walled arena. A movable object delivers
*exafference* — a world-caused change the agent did not produce.

A forward model (`ReafferencePredictor`) learns the whisker reading as a function
of the head's own heading during a self-motion phase, then predicts it from
efference/proprioception alone; the **residual** (actual − predicted) is the
reafference signal.

## Assumptions specific to P0
(in addition to the [common assumptions](../assumptions.md))
- The head only rotates; there is **no locomotion**.
- The **world is static** except for a **scheduled** exafference object that
  slides in during the test window.
- The forward model is a **binned running mean** of range vs heading.
- A 5 mm rangefinder **noise floor** is added; the predictor learns from noisy
  readings (the bin mean averages noise out).

## Run
```bash
cd experiments && ../.venv/bin/python p0_reafference.py
```

## Outputs
- `figures/p0_reafference.png` — whisker reading vs forward-model prediction (top)
  and residual over time with phase shading (bottom).
- printed stats: self-test vs exafference mean residual, ratio, verdict.

## Result & interpretation

![P0 reafference — whisker reading vs forward-model prediction; residual over time with phase shading](../figures/p0_reafference.png)

*Top: whisker reading vs forward-model prediction along the agent's heading.
Bottom: residual over time, with the self-motion and exafference phases shaded.
The residual sits at the sensor noise floor under self-motion and jumps roughly
nine-fold when the object the agent did not move slides in.*

Under self-motion (static world) the residual sits at the noise floor
(~9.6 mm); when the object the agent did not move slides in, the residual jumps
(~90 mm mean, ×9.4, peak ~723 mm). Self-caused change is predicted away;
world-caused change is not — the structural basis of the self/world distinction.
