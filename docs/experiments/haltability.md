# Haltability — the pivot that layering enables

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_haltability.png)

## Why this experiment

The [nested lattice](nested_lattice_self_model.md) established the **layering**: a
body has a stable deep **canvas** beneath its active top layers. This shows the first
thing the layering is *for*: **haltability** — the capacity to bring an ongoing
action to a stable stop against the canvas.

The claim (GN): *a halt needs a pivot, and a pivot needs a stable layer to bear
against.* This experiment shows exactly that **capacity**, and no more. Haltability
is **necessary but not sufficient** for what lies above it. What is sufficient is a
haltable action **pattern** — not a one-time hold, but a *recoverable, recognisable,
recurrent* halt (a differentiation of difference mapped to a stable recurring
phenomenology). The pattern is what makes a halt **object-directed** — and
object-directedness, not counting, is the capstone this leads toward (see
[below](#what-this-establishes-and-what-it-does-not)).

!!! warning "What this is *not*"
    A single stable hold is **not** counting, naming, or a "register". Nameable,
    countable registers need much more than haltability: *more layers*, *emancipated
    appendages* (a ratchet), and the discovery of **particulars** (the 2nd epistemic
    transition — else the same object is counted again and again). Those are
    [Phase II](../phase2.md) and M2, not here. Building a **world model** for habitat
    adaptation is also not the same thing as naming stable registers.

## The idea

An active chain (the writing) is coarse-coupled and driven. To **halt** node \(k\), a
haltable action pattern clamps it to a **home** position. A halt is a *stable,
addressable* hold only if there is a stable reference to clamp to — the canvas:

- **canvas ON** (a stable deep layer): node \(k\) is clamped to its fixed home and is
  held at a discrete **address** \(k\) — while the rest of the body keeps moving. A
  *selective* hold: hold one part, write with the rest. The \(N\) homes are \(N\)
  addressable positions — the enumeration / counting substrate.
- **canvas OFF** (no stable layer): there is no fixed home to clamp to; the best a
  halt can do is freeze velocity, and the node still **drifts** with the flow — no
  stable, addressable hold.

## Formalism — the halt is a clamp to the canvas

The haltable action pattern, per node, is a PD clamp — but *to what* depends on
whether a stable layer exists. With the canvas it clamps to the fixed address
\(x_k\); without, it can only damp velocity:

\[
f^{\text{halt}}_k =
\begin{cases}
-K\,(x_k^{\text{now}} - x_k^{\text{home}}) - D\,\dot x_k & \text{canvas ON (a fixed home)}\\[2pt]
-D\,\dot x_k & \text{canvas OFF (no reference)}
\end{cases}
\]

```python
--8<-- "experiments/haltability.py:halt"
```

The parameter varied is exactly the **presence of the stable layer** (`canvas_on`) —
nothing else changes.

## Result — a stable, addressable hold needs the pivot layer

![Left: the held node's position over time — with the canvas it stays pinned at its address; without, it drifts. Right: across all six halt targets, the canvas holds each node exactly at its commanded address (on the diagonal, 100%), while without it the holds scatter (75%).](../figures/haltability.png)

| | held-node spread (the hold) | active-node spread (the writing) | addressed (of 6) |
|---|---|---|---|
| **canvas ON** (stable deep layer) | **0.0055** | 0.131 | **1.00** |
| canvas OFF (no stable layer) | 0.046 (8×) | 0.137 | 0.75 |

With the canvas, the halt is a clean hold — the node is pinned at its address (spread
0.0055) *while the rest of the body keeps moving* (0.131): a **selective** hold, and
every one of the six positions is addressed correctly. Remove the stable layer and
the same halt drifts (8× the spread) and the address becomes unreliable. **Halting is
not a property of the node — it is a relation to the stable layer beneath it.**

## What this establishes — and what it does not

- **Haltability needs a pivot layer.** A stable stop is possible only against a
  stable reference. This is why *layering is the precondition of halting* — and why
  the [canvas](nested_lattice_self_model.md) had to come first.
- **A hold is the capacity, not yet the pattern.** What this experiment shows is the
  *capacity* to halt stably. That becomes cognitively load-bearing only as a haltable
  action **pattern** — a *recurrent, recognisable* halt. That the recurrent pattern
  **is** object-directedness (the two co-occur) is shown in
  [E3 — haltability generates aboutness](p6_haltability_aboutness.md): a halt-in-contact
  that is **persistent** (restored after perturbation), **returnable** (re-press
  re-acquires the *same* object), and **side-specific** — the triad *is* being directed
  at the object; its CPG foil (rhythmic touch that never holds) shows rhythm is not
  aboutness, haltability is. This page is the *capacity*; E3 is the *pattern*.
- **The action-pattern hierarchy.** Emancipation (a neck, then appendages) lets an
  agent climb **BAP → HAP (haltable) → NAP (negotiable) → … → TAP**. Haltability is
  the HAP rung; each rung is enabled because an emancipated part can **write on the
  lower layers without perturbing them** (the [canvas](nested_lattice_self_model.md)
  principle, now with its mechanism).

What this **does not** establish (deliberately):

- **Not counting or naming.** Enumerating discrete registers needs the discovery of
  **particulars** (individuating *this* object from similar tokens — else the same one
  is recounted) and a **ratchet** to hold each discrete state. The ratchet is not the
  hold shown here: it is *emancipated, branched, digitised appendages* (cheap movement
  that does not displace the network), **and** external traces and other agents that
  hold the memory. That is [Phase II](../phase2.md) and M2.
- **Not dexterity by itself.** The selective hold is a *precursor* to dexterity;
  dexterity proper needs the emancipated appendages the ratchet requires.

## Run

```bash
cd experiments && ../.venv/bin/python haltability.py
```
