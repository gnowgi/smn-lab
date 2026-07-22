# W2 — world-geometry, computed in the self-frame

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_world_geometry_self_frame.png)

## Why this experiment

[W1](world_in_self_graph.md) placed a single world feature as a position on the
self-graph. W2 takes the next step the framework requires: with *two* features
present, the world model is their **geometric relation, expressed in the
self-frame**. We measure the separation between two sources not in metres but in
**self-graph hops** — the body's own topology is the ruler.

## The design

The same elastic chain bends naturally beside two sources on two modality channels
(a "chem" source and a "thermal" source), each read on its own channel and each
localized to a self-graph node by the [W1](world_in_self_graph.md) read-out. The
world-geometry is the signed node separation `d = node_B − node_A`. We sweep the
true separation of the two sources and read back `d`.

## Formalism — world-geometry in self-graph units

Each feature is localized to a self-graph node by the
[W1](world_in_self_graph.md#formalism-locating-a-where-on-the-self-graph) read-out;
the world-geometry is their **signed node separation** — a relation, expressed in the
body's own units, against an allocentric foil in world units:

\[
d_{\text{self}} = \hat n_B - \hat n_A = \sum_k w^B_k\,k - \sum_k w^A_k\,k,
\qquad
d_{\text{allo}} = \frac{x_B - x_A}{\ell_{\text{seg}}}.
\]

```python
--8<-- "experiments/world_geometry_self_frame.py:separation"
```

A *relation* cancels the body's common-mode self-motion, so world-geometry in the
self-frame is even more stable than a single location — the body is the ruler. The
parameter varied is the **true separation** of the two sources.

## Pre-registered prediction

1. **World-metric in self-units** — as the true separation of the two sources
   grows, the recovered self-graph separation `d` tracks it (a body-anchored,
   metric-free measure of "how far apart" that still scales with the world).
2. **Self-anchored, posture-invariant** — while the body bends (sources static),
   the recovered separation holds, because both features are referred to the same
   self-frame.

## Result — prediction confirmed

![Left: recovered self-graph separation vs true separation lands on the ideal slope-1 line (slope 0.98, r 1.00). Right: the A→B separation holds at the true value while the body deforms throughout](../figures/world_geometry_self_frame.png)

8-segment chain, 3 seeds; feature A parked near node 2, feature B swept away:

| true separation (hops) | recovered self-graph `d` (hops) |
|---|---|
| 1 | 1.06 ± 0.19 |
| 2 | 2.03 ± 0.26 |
| 3 | 3.02 ± 0.26 |
| 4 | 3.98 ± 0.26 |

Recovered vs true separation: **slope 0.98, r = 1.000** — the world-metric is
recovered in self-graph units, with the body as the ruler. And it holds within
**±0.24 hops** as the body bends throughout (right panel).

A nice corollary: a **relation** is even more robust to self-motion than a single
location, because the body's common-mode motion shifts both features' readings
together and **cancels in the difference**. World-geometry expressed in the
self-frame inherits this robustness for free.

## What this establishes

- The world's geometry is the same *kind* of object as the self-model — a
  relation on a graph, in the body's own units, not a metric in an external frame.
- It **scales with the world** (slope ≈ 1) yet is **invariant to the body's
  posture** — world-geometry computed in relation to the self-model's geometry,
  exactly as the framework states.

Next: [W3](reafference_cut_self_graph.md) makes the self/world cut in this frame.

## What's measured and plotted

**Raw data:** two per-zone readings `sA_k`, `sB_k` (two modality channels), zone
world positions, nominal positions from calibration. **Computed:** each feature's
self-graph location and the signed separation — defined as running code in
[Formalism](#formalism-world-geometry-in-self-graph-units) above — plus a linear fit
of recovered `d` vs true separation. **Plotted:** recovered vs true separation with
the ideal slope-1 line; the separation time series for one configuration while the
body deforms.

## Run

```bash
cd experiments && ../.venv/bin/python world_geometry_self_frame.py
```
