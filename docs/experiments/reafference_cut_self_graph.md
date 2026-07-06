# W3 — the reafference cut, made in the self-graph frame

## Why this experiment

This closes the self/world arc. The [self-model](self_model_topology.md) was built
from movement; [W1](world_in_self_graph.md) placed a world feature on the
self-graph; [W2](world_geometry_self_frame.md) read the relation between two
features in self-units. W3 asks the question the whole framework is about: when a
zone's reading changes, was it the **body** that moved or the **world** that
changed? — and it answers *per node, on the self-graph*.

## The design

Reafference against the self-model. Each zone knows how its own reading changes
when it moves (a local field gradient `g_k` learned during calibration). The
**self-referred reading** removes that self-caused part:

```
s_self_k = s_k − g_k · (pos_k − nominal_k)
```

Its deviation from the calibrated baseline is the *world-caused* change, and its
profile over the self-graph nodes says *where* on the body the world changed.

Two challenges follow one another, with the body sweeping (a systematic bend +
jitter) **throughout**:

- **self-motion** — source static: the body sweeps toward and away from the
  source, so raw readings swing a lot.
- **exafference** — a second source fades in at a node: a genuine world change.

## Pre-registered prediction

- A **naive** detector (raw deviation from baseline) fires in *both* windows — it
  mistakes the body's own motion for a world change (false alarm under
  self-motion).
- The **reafferent** detector (self-referred deviation) stays silent under
  self-motion and fires only for the real world change — and localizes it to the
  correct self-graph node.

## Result — prediction confirmed

![Left: the reafferent detector (blue) is near-zero under self-motion and jumps for the world change; the naive detector (orange) rises during self-motion too. Right: the reafferent deviation over self-graph nodes is blank during self-motion, then a sharp band at node 6 during exafference](../figures/reafference_cut_self_graph.png)

8-segment chain; standing source at node 3, exafference source fading in at node 6:

| detector | self-motion | exafference | discriminability |
|---|---|---|---|
| **reafferent** | 0.009 | 0.192 | **21.5×** |
| naive | 0.021 | 0.186 | 8.7× |

The reafferent detector separates self from world **21.5×** — nearly silent while
only the body moves (0.009) and fully lit for a genuine world change (0.192). The
naive detector manages only 8.7× and false-alarms 2.3× more under self-motion. And
the reafferent deviation **localizes** the world change to self-graph node **5.3**
(true 6). The right panel makes it visible: blank during self-motion, then a sharp
band at the correct node once the world changes — while the body is moving the
whole time.

## What this establishes

- The self/world distinction the architecture claims as **structural** is, on the
  bench, **operational**: the agent tells its own motion from the world's, and
  says **where** on its own body the world changed.
- The cut is made **in the self-graph frame** — the payoff of building the
  self-model first ([self-model](self_model_topology.md)) and the world in its
  frame ([W1](world_in_self_graph.md), [W2](world_geometry_self_frame.md)).

Together, the four studies **construct** the self/world distinction from the body
up — self first, world in its frame, with the graph as the only computer.

## What's measured, computed, and plotted

**Raw data:** per-zone reading `s_k` and world position while the body sweeps;
`g_k`, nominal positions, and a baseline learned in calibration. **Computed:**
self-referred reading `s_self_k = s_k − g_k·(pos_k − nominal_k)`; reafferent
deviation = `s_self_k − baseline_k`; naive deviation = `s_k − baseline_k`;
detector = mean |deviation| over zones per step; discriminability = detector during
steady exafference ÷ during self-motion; localization = positive-deviation centroid
over self-graph nodes. **Plotted:** the two detectors over time; a node × time
heatmap of the reafferent deviation.

## Run

```bash
cd experiments && ../.venv/bin/python reafference_cut_self_graph.py
```
