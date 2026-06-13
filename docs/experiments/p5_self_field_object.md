# E2 — Self / field / object factoring (force-reafference)

`experiments/p5_self_field_object.py`

[E1](p4_manipulator_objecthood.md) read a thing by how it resists the pull. But a
limb lifting in a gravitational field already meets a *second* thing it must press
against — the field itself. This experiment generalizes the bench's self/world
register (P0) into a **three-way** factoring — **self / field / object** — now in
the force domain and in real gravity.

The claim under test is that the field can be **factored out architecturally**, by
a forward model, so that an object and an external cause each surface *by
construction* — no trained classifier. The field is the always-present third term
that, once predicted, never masquerades as an object.

## Setup

A single sagittal limb (hinge axis y, so gravity loads it) lifts against the field.
The agent carries a **force-reafference forward model** (`ReafferencePredictor`,
keyed on `|angle|`): by self-motion alone — no object present — it learns the
effort its own pull needs to lift the limb *against gravity*. That calibration is
the **field model**. Thereafter, the same upward motion is attributed three ways:

| condition | what happens | the signature |
|---|---|---|
| **self+field** | the agent lifts in empty field | residual ≈ 0 (effort matches the field prediction) |
| **object** | the lift arc meets a fixed block | effort/contact rises *beyond* the field baseline (residual > 0) |
| **external** | the world lifts the limb; agent passive | motion with *no* efference — exafference |

The independent variable is which of these three is in play; the dependent
variables are the **residual effort** (effort − field prediction) and the board's
**attribution** of each instant to self+field / object / external.

## What it measures

| panel | claim | shows |
|---|---|---|
| **A — effort vs angle** | the field is a predictable baseline | each condition's effort against the calibrated field curve |
| **B — residual over time** | the object rises above the field | residual ≈ 0 for self+field, elevated for the object |
| **C — attribution** | same motion → three causes, by construction | the board's per-condition attribution fractions |

## Result

```
condition      mean residual   peak contact          attribution (fraction)
self+field          ~0.001          0.00     self+field≈1.00  object≈0.00  external≈0.00
object              ~0.34           >0        self+field≈0.32  object≈0.68  external≈0.00
external            ~0              0.00       self+field≈0.00  object≈0.00  external≈1.00
```

- **Self+field** is attributed self+field with probability ≈ 1.00 — its residual is
  essentially zero, because the field model predicts the agent's own effort.
- **Object** is attributed *object* ≈ 0.68 on a residual of ≈ 0.34 plus contact;
  its pre-contact phase honestly reads self+field (the limb is still only fighting
  gravity), and it flips to object exactly when resistance exceeds the field.
- **External** is attributed external ≈ 1.00 — motion with no efference is read as
  world-caused, the exafference signature.

[![Self / field / object: effort vs angle against the calibrated field baseline, the residual beyond the field (≈0 for self+field, elevated for the object), and the board's attribution of the same motion to three causes](../figures/p5_self_field_object.png)](../figures/p5_self_field_object.png)

## What this experiment shows

- **The field is a free prior, factored by reafference.** Gravity is a strong,
  always-present structure; the agent reads it only through the work it does
  against it, and once that work is predicted, the field stops being mistaken for an
  object.
- **Self / world generalizes to self / field / object.** The same reafference
  machinery that splits self-caused from world-caused change at a distance (P0)
  does the three-way force-domain split here, with the field as the third term.
- **No classifier.** The attribution falls out of the forward model + the dual
  interface (efference, residual, contact, motion), not from labeled training.

It does **not** yet show:

- **Composition.** This is still one zone reading one field; objecthood as a
  composition of differentiae across a network is [E4](p7_scaling_network.md).
- **A free-space stiffness equilibrium.** Co-contraction with tunable stiffness in
  free space needs muscle/tendon actuators; here the object (and gravity) supply the
  equilibrium.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus:

- A **gravity-loaded** sagittal limb (hinge axis y) whose pivot sits above the arm
  length, so the limb never reaches the floor — the field is the only baseline load.
- A **force-reafference forward model** calibrated on self-motion in empty field,
  using the *same* press profile as the test runs, so the prediction is honest.
- An **external** condition driven by an applied torque (`qfrc_applied`) with zero
  efference — the world moves the limb while the agent does nothing.

## Why this experiment is in the bench

It is the force-domain home of the self/world distinction that runs through the
whole bench. Without factoring the field, every lift would read as resistance and
the agent could never tell its own effort-against-gravity from an object. It also
supplies the third term — *field* — that the cognitive vocabulary usually omits.

## Run it

```bash
cd experiments && ../.venv/bin/python p5_self_field_object.py
```

Outputs: `figures/p5_self_field_object.png`. Runtime: a few seconds on a laptop
CPU (force/contact read, no rendering).
