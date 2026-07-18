# Branched body — the body computes its own morphology (a morphological computer)

## Why this experiment

The [self-model](self_model_topology.md) recovered a *line* because the body was a
line. But the mathematics is topology-general: the coupling between zones is fixed
by the body's mechanical graph, whatever its shape. So a **branched** body should
recover a **tree**, with its branch points as higher-degree nodes — and if it
does, the body is literally computing its own structure from its own movement. It
also lets us make a sharper point about **asymmetry**.

## Formalism — the same read-out, on a tree

This experiment runs the **same** self-model read-out as the
[chain](self_model_topology.md), unchanged — the point is that it is
topology-general. Each joint (a CAZ) is the hinge between two segments, and its own
angular velocity *is* their yaw-rate difference, \(\dot\theta_j = \omega_{\text{child}} - \omega_{\text{parent}}\).
So the **signed** read-out \(C_{j,s} = \mathrm{Xcorr}(\dot\theta_j, \omega_s)\)
gives each joint a positive correlate (its child) and a negative correlate (its
parent). It is the framework's `coupling` — no per-experiment copy:

```python
--8<-- "smn_lab/self_model.py:coupling"
```

Each joint then decides **its own** edge locally — (co-rotating, counter-rotating)
= (argmax, argmin) of its row — and the body graph is the union of those local
edges. The hub, being the parent of three arm-joints, is the negative correlate of
three of them, so it surfaces as a **degree-3 node** (the branch point) with no zone
ever reading the whole body (**C3**):

```python
--8<-- "smn_lab/self_model.py:local_edge"
```

### The parameter this experiment varies

Here the varied parameter is not stiffness but **body morphology** — the arm
structure itself (angle and segment-count per arm):

```python
--8<-- "experiments/branched_self_model.py:configs"
```

- **asymmetric** — a hub with three arms of *different* lengths (3, 2, 4 segments).
- **symmetric** — a stem with two *equal*, mirror-image arms.

### The measurement — can the body tell its arms apart?

Both bodies recover the tree and the degree-3 branch point (topology is always
readable). They differ in whether the self-model can *individuate* mirror-parts —
an **experimenter's** probe (it uses the known arm assignment, so it lives in
`smn_lab.metrics`, not the agent): the arm-swap residual
\(\lVert C - \mathrm{swap}(C)\rVert / \lVert C\rVert\), near 0 ⇔ the two arms are
interchangeable in the data.

```python
--8<-- "smn_lab/metrics.py:arm_swap_residual"
```

- symmetric → small residual: the two equal arms are indistinguishable; the body
  cannot tell left from right.
- asymmetric → large residual: every part is unique; the self-model is rigid.

## Result — prediction confirmed

![Left: the asymmetric body recovers its tree with the degree-3 branch point (orange). Middle: the symmetric body recovers the same topology but its two mirror-arms are indistinguishable. Right: the arm-swap residual is small for the symmetric body and large for the asymmetric one](../figures/branched_self_model.png)

| body | edges recovered | branch node | arm-swap residual |
|---|---|---|---|
| **asymmetric** | 9/9 | seg 0 (degree 3) | **0.318** (arms distinct) |
| **symmetric** | 8/8 | seg 0 (degree 3) | **0.096** (arms interchangeable) |

Both recover the tree topology and the branch point exactly. The asymmetric body's
every part is unique (residual 0.32); the symmetric body's two equal arms are
**data-indistinguishable** (residual 0.10) — it knows it has two arms but nothing
in its own movement tells it which is left and which is right.

## What this establishes

- **The SMN body is a morphological computer.** It reconstructs its own morphology
  — chain or tree, branch points and all — from its own movement, through the same
  opponent modulation that drives behaviour. Model-building is not a faculty bolted
  above the body; it is what a moving opponent body does. (Contrast the usual sense
  of "morphological computation," where the body offloads work from a controller;
  here the body computes a *model of the body*.)
- **Asymmetry is a cognitive-architectural feature, not a bug.** A symmetric body
  cannot individuate its mirror-parts: a determinate self *requires* an asymmetry
  (a mark, a lateralized stiffness, an unequal limb). This reframes the
  developmental asymmetries of Commitment C6 as the very condition of an
  unambiguous self-model — and suggests why evolved body plans are polarized and
  lateralized rather than symmetric.

Topology-generality also strengthens the [chain result](self_model_topology.md):
the same local, no-central-reader rule (C3) reads *any* morphology.

## The self/world card

The same result reads at a glance as a [self/world card](../diagram-grammar.md#the-selfworld-card)
— the designed agent, the recovered self-model as an abstract graph (branch point
ringed), and a world source localized on one limb of the *recovered* graph:

![Self/world card for the branched body: designed agent, recovered self-model graph, world on one limb](../figures/self_world_card_branched.png)

## What's measured and plotted

**Raw data:** each joint's own angular velocity `JV` (velocity sensor) and each
segment's world yaw-rate `omega` (`mj_objectVelocity`), while the body moves under
independent per-joint OU drive. **Computed:** the signed coupling, each joint's
local edge, node degrees, and the arm-swap residual — all defined as running code in
[Formalism](#formalism-the-same-read-out-on-a-tree) above (the read-out and edges
from `smn_lab.self_model`, the residual from `smn_lab.metrics`). **Plotted:** the
recovered tree over the true morphology for both bodies (branch point highlighted),
and the min arm-swap residual per body.

## Run

```bash
cd experiments && ../.venv/bin/python branched_self_model.py
```
