# Branched body — the body computes its own morphology (a morphological computer)

## Why this experiment

The [self-model](self_model_topology.md) recovered a *line* because the body was a
line. But the mathematics is topology-general: the coupling between zones is fixed
by the body's mechanical graph, whatever its shape. So a **branched** body should
recover a **tree**, with its branch points as higher-degree nodes — and if it
does, the body is literally computing its own structure from its own movement. It
also lets us make a sharper point about **asymmetry**.

## The local rule

Each joint (a CAZ) is the hinge between exactly two segments, and its own angular
velocity *is* their yaw-rate difference:

```
JV_j = omega_child - omega_parent
```

So a joint finds the two segments it couples as the one it **co-rotates** with
(its strongest positive correlate) and the one it **counter-rotates** with (its
strongest negative correlate) — one edge of the body tree, read from local
signals. The union of every joint's edge is the recovered morphology. The hub,
being the parent of three arm-joints, is the negative correlate of three of them —
so it surfaces as a **degree-3 node**, the branch point, with no zone ever seeing
the whole body.

## Two bodies

- **asymmetric** — a hub with three arms of *different* lengths (3, 2, 4 segments).
- **symmetric** — a stem with two *equal*, mirror-image arms.

## Pre-registered prediction

Both recover the tree topology and the degree-3 branch point (the topology is
always readable from movement). But the two bodies differ in whether the body can
tell its own arms apart, measured by the **arm-swap residual**
`||C − swap(C)|| / ||C||` (near 0 ⇒ the two arms are interchangeable in the data):

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

## What's measured, computed, and plotted

**Raw data:** each joint's own angular velocity `JV` (from its velocity sensor)
and each segment's world yaw-rate `omega` (from `mj_objectVelocity`), while the
body moves under independent per-joint OU drive. **Computed:** the signed coupling
`C[j, s] = corr(JV_j, omega_s)`; each joint's edge = (argmax, argmin) over
segments; node degrees from the recovered edges; the arm-swap residual per arm
pair. **Plotted:** the recovered tree over the true morphology for both bodies
(branch point highlighted), and the min arm-swap residual per body.

## Run

```bash
cd experiments && ../.venv/bin/python branched_self_model.py
```
