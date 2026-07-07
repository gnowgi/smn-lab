# W1 — a world feature located in the self-graph

## Why this experiment

With the [self-model](self_model_topology.md) in hand — the body's own hop-graph,
built from movement — the world model can begin. The framework takes the order
literally: the world model is world-geometry expressed **in the self-model's
frame**. W1 is the first step: give a world feature a **location on the
self-graph**.

## The design

The same elastic chain, base pinned so it deforms in place, bends naturally beside
a single Gaussian field source (a "where" in the world). Each zone reads the field
at its bilateral sites. We ask where the source is, two ways, and the contrast is
the point:

- **self-referred** — report the location as a position on the *self-graph*: the
  reading-weighted centroid of the zone **node indices**. The answer is a node, a
  place in the body's own topology. It needs no external frame.
- **allocentric** (foil) — report the location in absolute **world** coordinates:
  the reading-weighted centroid of the zones' world positions. This needs an
  external frame, and it moves whenever the body moves, because the zones carry
  their readings to new places as they bend.

Two phases: **self-motion** (source static, body bending) and **world-motion**
(source sweeping along the body).

## Pre-registered prediction

The self-referred location holds still while the body moves (source static) and
tracks the source when the source moves; the allocentric location is corrupted by
the body's own movement. The world is knowable as geometry-in-the-self-frame
*without* a God's-eye external frame.

## Result — prediction confirmed

![The world feature's location on the self-graph over time: the self-referred estimate (blue) is stable under self-motion and tracks the sweeping source; the allocentric estimate (orange) jitters under self-motion](../figures/world_in_self_graph.png)

| phase | frame | node err | jitter | tracks source |
|---|---|---|---|---|
| self-motion (source static) | **self-referred** | 0.54 | **0.13** | — |
| | allocentric | 0.70 | 0.46 | — |
| world-motion (source sweeps) | **self-referred** | 0.28 | 0.33 | **0.97** |
| | allocentric | 0.15 | 0.37 | 0.96 |

The decisive number is the **3.5× lower jitter (0.13 vs 0.46) under self-motion**:
when the body moves but the world does not, the body-anchored self-graph location
holds still while the world-coordinate estimate drifts. Both track the source when
it actually moves (r ≈ 0.97). In the figure, during the static-source window the
self-referred estimate (blue) sits smoothly near the source while the allocentric
one (orange) spikes; during the sweep both climb the staircase, the self-referred
one cleanly.

## What this establishes

- A world feature has a **location on the self-graph** — world-in-self-frame.
- That location is **body-anchored**: stable under the agent's own motion, and it
  needs no external/allocentric frame to be expressed or to be robust.

Next: [W2](world_geometry_self_frame.md) reads the *relation* between two features
in self-graph units; [W3](reafference_cut_self_graph.md) makes the self/world cut
in the same frame.

## What's measured, computed, and plotted

**Raw data:** per-zone field reading `s_k` (mean of the two bilateral sites) and
world position; nominal zone positions learned in a short calibration.
**Computed:** sharpened, above-baseline reading weights `w_k`; self-referred
location = `Σ k·w_k` (node-index centroid); allocentric location = `Σ x_k·w_k`
mapped to the nearest nominal node; ground truth = the node whose nominal position
is nearest the source. **Plotted:** all three (true, self-referred, allocentric)
over time, across the self-motion and world-motion windows.

## Run

```bash
cd experiments && ../.venv/bin/python world_in_self_graph.py
```
