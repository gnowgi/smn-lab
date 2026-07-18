# Sheet & tube — one function, any body

## Why this experiment

The [self-model read-out](self_model_topology.md) recovered a *line* from a chain;
the [branched body](branched_self_model.md) recovered a *tree*. This closes the
argument: the **same** function recovers a **2-D** body too — a **sheet** (two
linked chains) and a **tube** (three or more chains closed into a ring). The
Phase I·① claim in full: *irrespective of the body's complexity, one mechanism
constructs the self-model.*

The biology is the point. A **muscle** is a chain of CAZ; a **sheet / sheath** is
two such chains linked laterally; a **tube** — a worm, a digestive tract, a vessel —
is chains linked **longitudinally and laterally**. None of them has a central
regulator. If one read-out recovers all of them, the self-model is a property of
*any* linked-CAZ tissue, not of a special body.

## The idea

The **segments are scaffolding** — point masses that hold sensors. Every **link is
one CAZ**: a spring-tendon muscle with its own linear actuator (longitudinal links
= longitudinal muscle; lateral links = circular muscle). Each link is driven
independently, and the tissue is **overdamped** — the regime of real soft tissue
(low Reynolds, like the crawler's medium). In that regime a driven link's force
shows up **only at its two endpoint segments**, so each link can discover the two
segments it couples by a purely local correlation — no zone ever reads the whole
body (**C3**).

## Formalism — the same read-out, on a lattice

The true body graph is the set of longitudinal and lateral links (wrapped into a
ring for a tube):

```python
--8<-- "smn_lab/lattice.py:edges"
```

Driving each link and correlating its drive with every segment's motion is the
**same** `coupling` from [`smn_lab.self_model`](../self-model-and-measurement.md) —
the identical function that recovers the chain and the tree, unchanged; we only
combine the planar axes:

```python
--8<-- "experiments/lattice_self_model.py:readout"
```

```python
--8<-- "smn_lab/self_model.py:coupling"
```

Each link's **two strongest co-movers are its endpoints**; the union of those edges
is the recovered body graph. Scoring that against the known wiring is the
experimenter's metric (it uses the answer key, so it lives in
[`smn_lab.metrics`](../self-model-and-measurement.md)):

```python
--8<-- "smn_lab/metrics.py:endpoint_recovery"
```

### The parameter this experiment varies

Not stiffness, not modulation — **the topology itself** (`n_row`, `closed`): chain
(`n_row=1`) → sheet (`n_row=2`) → tube (`n_row≥3, closed`). Nothing else changes,
least of all the read-out.

## Result — one function, any body

![The same read-out recovers a chain (a path), a sheet (a ladder), and a tube (an unrolled cylinder with the wrap edges dashed); endpoint-recovery 1.00 / 0.99 / 0.97](../figures/lattice_self_model.png)

| body | segments | links | endpoint-recovery (3 seeds) |
|---|---|---|---|
| **chain** (a muscle) | 8 | 7 | **1.00 ± 0.00** |
| **sheet** (two linked chains) | 12 | 16 | **0.99 ± 0.01** |
| **tube** (closed ring) | 24 | 44 | **0.97 ± 0.01** |

The `coupling` read-out recovers every topology at ~0.97–1.00, with the injected
code byte-identical to the [chain](self_model_topology.md) and
[tree](branched_self_model.md) pages. The control that proves the mechanism: driving
the *segments* (cells) instead of the *links* (muscles) collapses to chance — **a
tissue knows its shape through the muscles that move it, not through an external
agent poking its cells.**

## What this establishes

- **Topology-invariance of the self-model.** Chain, tree, sheet, tube — one
  function, any body. The mechanism (elastic, overdamped, link-driven, local) does
  not care about the body plan.
- **The construction is decentralized.** No zone reads the whole lattice; the graph
  assembles from each link's own local read (C3, in two dimensions).
- **The bridge to [Phase II](../phase2.md).** The tube is the evo-devo *tubular*
  rung. That the *same* mechanism scales to it means richer bodies come from
  **architecture** — nested longitudinal × circular modulation — not from more
  identical zones. The muscle behaviors (C. elegans bending, earthworm peristalsis)
  that this anatomy affords are the next step.

## Run

```bash
cd experiments && ../.venv/bin/python lattice_self_model.py
```
