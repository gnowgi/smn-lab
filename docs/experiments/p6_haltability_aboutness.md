# E3 — the haltable action pattern generates object-directedness

[E1](p4_manipulator_objecthood.md) read a thing by its resistance;
[E2](p5_self_field_object.md) separated self, field, and object. This experiment
asks the directedness question — in what sense is the agent's press *about* the thing
it presses? — and answers it **in the progression's order: self-model first, then the
object in that self-frame.** The claim: object-directedness is generated not by a
one-time halt but by a haltable action **pattern** — a *recurrent, recognisable* halt
— and the [capacity to halt](haltability.md) it builds on needs the layered canvas.

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_p6_haltability_aboutness.png)

## Formalism — self-model first, then the pattern in its frame

**① The self-model, first.** In free space the agent drives its two limbs with
independent probes and applies the **same framework read-out** — each zone responds
to its *own* efference and not the other's (off-diagonal ≈ 0): two independently
modulable zones, *my-left* and *my-right*, each fixed by its efference→motion
contingency. Being bilateral, the two are mirror-alike — as in the
[branched body](branched_self_model.md), *a symmetric self cannot yet tell its
mirror-zones apart.*

```python
--8<-- "smn_lab/self_model.py:coupling"
```

```python
--8<-- "experiments/p6_haltability_aboutness.py:selfmodel"
```

**② The haltable action pattern, in the self-frame.** With a thing on the left, a
haltable *pattern* (not a one-time halt) produces a halt-in-contact tested for three
properties — the marks of a *recurrent, recognisable* pattern:

| property | = the pattern is… | test |
|---|---|---|
| **persistent** | recoverable | a perturbation torque shoves the left limb off mid-hold; the halt is restored |
| **returnable** | recurrent / recognisable-as-same | withdraw → re-press re-acquires the *same* thing across cycles |
| **side-specific** | differentiated in the self-frame | the RIGHT self-zone, same command, has nothing to press and never holds |

```python
--8<-- "experiments/p6_haltability_aboutness.py:pattern"
```

The object **breaks the bilateral symmetry** — it individuates the self's left zone
*and* the object together. The **foil** is a **CPG** rhythm: it touches every cycle
but is forced to release. The order parameter is the **longest sustained directed
halt** (plus episodes = returnability). *Rhythm is not aboutness; the haltable pattern
is.*

## Result

```
[1] self-model (framework coupling, free space):
    zone-coupling  L: [1.00 0.09]  R: [0.08 0.88]   off-diagonal = 0.09
    -> two independently-modulable zones (my-left, my-right)

[2] object-directedness, in the self-frame:
    agent/limb          longest halt (s)   episodes   held fraction
    SMN left (object)               1.51          5          0.91
    SMN right (none)                0.00          0          0.00
    CPG left (object)               0.26         17          0.73
```

- **Self-model first.** Off-diagonal coupling ≈ 0.09: the agent recovers *two
  decoupled zones* before any object — the self-referred frame the aboutness is then
  expressed in.
- **Persistent (recoverable).** The left self-zone sustains a directed halt for
  ~1.51 s and restores it after the perturbation — the object plus the continued
  press are a halt equilibrium.
- **Returnable (recurrent).** Across withdraw/re-press cycles the agent re-acquires
  the *same* thing five times — the recurrence that earns the "pattern" label.
- **Side-specific (differentiated).** The right self-zone, identical command, nothing
  to press, never holds (0.00 s). The left-halt / right-free asymmetry *is*
  directedness — the object individuates the self's left zone.
- **The CPG foil only flickers.** Longest sustained halt ~0.26 s (17 brief touches):
  a rhythm is forced to release. *Rhythm is not aboutness; the haltable pattern is.*

[![Haltability generates aboutness: SMN left holds the object across cycles and restores after a perturbation while the right never holds; the CPG foil only flickers; the sustained directed halt appears only with haltability, only on the object side](../figures/p6_haltability_aboutness.png)](../figures/p6_haltability_aboutness.png)

## What this experiment shows

- **Self-model, then object — in order.** The self-referred frame (two decoupled
  zones) is recovered *first*, with the same framework `coupling` used everywhere;
  the object-directedness is expressed *in that frame*. This is the progression's
  discipline applied to the manipulator.
- **Object-directedness is a haltable action *pattern*, not a one-time halt.** Being
  *about* a thing is a *recurrent, recognisable* held halt-in-contact — persistent
  (recoverable), returnable (recurrent), side-specific (differentiated). Haltability
  (the [capacity](haltability.md)) is necessary; the **pattern** is what is
  sufficient for aboutness. The two — the haltable pattern and object-directedness —
  **co-occur**.
- **The object breaks the bilateral symmetry.** A symmetric self cannot tell its
  mirror-zones apart ([branched](branched_self_model.md)); the object individuates
  the self's left zone *and* itself together — self-differentiation and
  object-directedness arrive as one event.
- **It is the pattern, not rhythm.** A basal rhythm can touch but cannot hold; only
  the haltable pattern commits the body to the thing.

It does **not** show (deliberately, per the progression): counting, naming, or
registers — those need the discovery of **particulars**, a **ratchet** (emancipated
appendages + external/social scaffolding), and are [Phase II](../phase2.md)/M2. It
also does not yet show a **free-space stiffness equilibrium** (a co-contracted hold
in free space needs muscle/tendon actuators; here the object supplies the equilibrium)
— a later refinement.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus:

- A **bilateral** two-limb unit with both limbs commanded identically, so the
  object-side / empty-side asymmetry is the only difference between them.
- A **perturbation probe**: an applied torque during the hold that shoves the limb
  off the object, to test whether the directed halt is restored.
- A **CPG foil** (basal rhythmic drive) on the same body, as the no-haltability
  comparison.

## Why this experiment is in the bench

It supplies the third leg of the single-zone account — directedness — without which
the difference register of E1 would be a sensor reading, not a stance toward a
thing. Aboutness grounded in haltability is the bench's bridge from the unmediated
agent (M1) toward the *about*-ness that mediated cognition (M2) will trade in.

## Run it

```bash
cd experiments && ../.venv/bin/python p6_haltability_aboutness.py
```

Outputs: `figures/p6_haltability_aboutness.png`. Runtime: a few seconds on a laptop
CPU (force/contact read, no rendering).
