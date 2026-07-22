# E1 — Objecthood as resistance-to-modulation (the manipulator unit)

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **progression** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [The Construction of Experience](../construction-of-experience.md).


`experiments/p4_manipulator_objecthood.py`

The P0–P3 experiments built and recognized a world at a distance — mapping,
foraging, discriminating. This one starts the **manipulator** series: a bilateral
two-limb contact unit (see `design/manipulator-unit.md`) that meets the world by
*pressing on it*. The first question is the most basic one in the series — what is
an object, before any naming or composition?

The claim under test is that **objecthood is the force→result mapping**: a thing
*is* how it answers the agent's own pull. A single opponent zone, pressing,
already tells things apart by the resistance they return — and it does so **by
construction, with no learning and no stored template**. This is honestly a
*difference register*, not yet full objecthood (one zone composes nothing) — but
it is the atom the rest of the series builds on.

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_p4_manipulator_objecthood.png)

## Setup

One pull-only antagonist limb (the **dual interface**: intended effort,
proprioceptive result, contact resistance) presses, on a ramp, against five things
that differ *only* in how they resist:

| condition | what it is |
|---|---|
| **free** | nothing there |
| **movable-light** | a light free box — yields easily, small field-friction |
| **movable-heavy** | a heavy free box — yields, but more friction = field cost |
| **compliant** | a spring-backed box — gives, then resists |
| **fixed** | a welded box — cannot be pushed through |

Each step is classified, by construction, into the **register lattice**
(Contact × Effort × Motion). The independent variable is the thing being pressed;
the dependent variables are the contact **impulse** it returns (resistance) and
the **final angle** the limb reaches (yielding).

The **foil** is the same body driven by a **position ("stepper") controller** that
commands an angle instead of modulating a force — the contrast that shows why the
opponent-pull architecture matters.

## What it measures

| panel | claim | independent variable | dependent variable |
|---|---|---|---|
| **A — force→result map** | objecthood = how the thing answers the pull | commanded press | achieved angle |
| **B — objecthood map** | each thing is a distinct (resistance, yielding) | thing pressed | (impulse, final angle) |
| **C — register occupancy** | the things occupy separable lattice cells | thing pressed | occupancy over Contact×Effort×Motion |
| **D — the foil** | force-modulation is bounded; the stepper is not | actuation (SMN vs position) | contact impulse |

## Result

```
condition        final angle   impulse(N·s)   peak(N)            dom. register   disp(m)
free                   1.20          0.000      ...      free·working·moving        —
movable-light          1.06          3.1        ...    object·straining·moving    0.0xx
movable-heavy          0.71          9.3        ...    object·straining·halted    0.0xx
compliant              0.37         13.2        ...    object·straining·halted     —
fixed                  0.13         18.9        ...    object·straining·halted     —

occupancy vectors over 5 conditions: min pairwise L1 > 0   (all distinct)
foil overpress (contact impulse, SMN vs position):
    fixed           SMN 18.9   position 57.x       (the stepper overpresses what it cannot reach)
```

- **The five things fall on a single monotone arc** of resistance vs yielding —
  one differentia, resistance-to-modulation, cleanly separating free → movable →
  compliant → fixed.
- **Register occupancy is distinct per thing** (min pairwise L1 distance > 0): the
  conditions occupy separable subsets of the Contact×Effort×Motion lattice,
  recovered with zero learning.
- **The stepper foil overpresses.** On the fixed thing the position controller's
  contact impulse is ~57 N·s against the SMN pull's ~19 — the unbounded failure of
  commanding an *angle* rather than modulating a *force*. The opponent pair stays
  force-bounded and resistance-reading; the stepper does not.

[![The single-zone difference register: the force→result map, the (resistance, yielding) map, register occupancy per thing, and the stepper foil overpressing the unreachable thing](../figures/p4_manipulator_objecthood.png)](../figures/p4_manipulator_objecthood.png)

## What this experiment shows

- **A thing is how it answers the pull.** Objecthood, at this floor, is a
  force→result mapping read off the dual interface — not a label, not a template.
- **The register lattice is occupied, not learned.** The body's structure fixes,
  *a priori*, the finite space of distinctions (Contact × Effort × Motion); an
  experiment records which subset each thing drives the agent into.
- **Opponent-pull modulation is force-bounded.** The foil shows the architectural
  payoff: a force you modulate cannot overpress what it cannot reach, where a
  commanded angle will drive without limit.

It does **not** yet show:

- **Objecthood as composition.** One zone registers one differentia; it composes
  nothing. Binding several differentiae into an object needs a *network* — that is
  [E4](p7_scaling_network.md).
- **Self / field / object factoring.** Here the field is incidental; separating
  the agent's own effort against gravity from the object is [E2](p5_self_field_object.md).
- **Directedness.** That a halt-in-contact is *about* the thing is [E3](p6_haltability_aboutness.md).

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus:

- A **contact bench**: gravity on, a frictional floor, things carrying mass,
  fixation, and compliance, read **only through the work the agent does against
  them** (effort + contact), not by inspection.
- A **pull-only antagonist zone** with a baseline co-contraction tone (the opponent
  pair); there are no position commands in the SMN condition — the position
  controller appears only as the foil.

## Why this experiment is in the bench

It is the atom of the manipulator series — the move from perceiving a world at a
distance (P0–P3) to *handling* it. Every later result (self/field/object, halt-as-
aboutness, the 2^K scaling law) is built on this single-zone difference register,
so it must be made concrete and falsifiable first.

## Run it

```bash
cd experiments && ../.venv/bin/python p4_manipulator_objecthood.py
```

Outputs: `figures/p4_manipulator_objecthood.png`. Runtime: a few seconds on a
laptop CPU (no rendering — the read is force/contact, not visual).
