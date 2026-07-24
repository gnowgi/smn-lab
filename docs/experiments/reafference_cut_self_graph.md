# W3 — the reafference cut, made in the self-graph frame

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_reafference_cut_self_graph.png)

## Why this experiment

This closes the self/world arc. The [self-model](self_model_topology.md) was built
from movement; [W1](world_in_self_graph.md) placed a world feature on the
self-graph; [W2](world_geometry_self_frame.md) read the relation between two
features in self-units. W3 asks the question the whole framework is about: when a
zone's reading changes, was it the **body** that moved or the **world** that
changed? — and it answers *per node, on the self-graph*.

## Formalism — the cut, in the self-graph frame

The same reafference cut as [Q2](q2_reafference.md#formalism-the-reafference-cut),
now expressed in the **self-model's own coordinates**. Each zone \(k\) learns,
during calibration, how its reading changes with its own displacement — a local gain
\(g_k\) (least-squares of \(\Delta s_k\) on \(\Delta\text{pos}_k\)). The
**self-referred reading** subtracts that self-term; its deviation from a calibrated
baseline is the world-caused change, per node:

\[
s^{\text{self}}_k = s_k - g_k\cdot(\text{pos}_k - \text{nominal}_k),
\qquad
\text{reaf\_dev}_k = s^{\text{self}}_k - \text{base}_k.
\]

```python
--8<-- "experiments/reafference_cut_self_graph.py:reaff"
```

A **naive** detector uses the raw deviation \(s_k - \text{base}_k\) and cannot tell
self from world. The reafferent deviation's profile over the self-graph nodes also
says *where* the world changed (the positive-deviation centroid). This is the cut
made in the frame the [self-model](self_model_topology.md) built — the payoff of
building self first, and the same read-out family (a per-zone `zone_xy` localization
from `smn_lab.worldmodel`).

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

## Audit — replicate + null + localization specificity (2026-07-24)

The scrutiny pass. As first committed this experiment was **single-seed**
(`default_rng(0)`) — against the repo's own ground rule (*replicated seeds with
reported spread, not single runs*). The audit replicates across 10 seeds and adds
the two nulls a skeptic asks for. `run()` now takes `(seed, exaf_on, b_node)`; the
default reproduces the committed single-seed numbers byte-identically.

1. **Working null (no-event):** run with `exaf_on=False`, so source B never fades
   in and the "exafference" window is pure self-motion. If the reafferent
   discriminability is world-caused it must collapse toward 1, and the localizer
   must stop pointing at node 6.
2. **Localization specificity:** move the world change to node 2 (`b_node=2`) and
   check the reafferent centroid follows — i.e. it reads *where* the world changed
   rather than a fixed bias toward high node indices.

![W3 audit — discriminability collapses to ~1 in the no-event null; the localizer
tracks the world change from node 6 to node 2](../figures/reafference_cut_self_graph_audit.png)

| metric (10 seeds) | baseline (B at node 6) | no-event null (no B) | localization swap (B at node 2) |
|---|---|---|---|
| reafferent discriminability | **20.5 ± 2.5** | **1.1 ± 0.1** | 23.7 ± 2.4 |
| naive discriminability | 8.3 ± 1.6 | 0.9 ± 0.2 | 9.5 ± 1.9 |
| reafferent > naive | 10 / 10 seeds | — | 10 / 10 seeds |
| localized node (true) | 5.4 (6) | 3.4 (—) | **2.2 (2)** |

**Survives.** The single-seed headline replicates (reafferent discriminability
20.5 ± 2.5 across 10 seeds, reafferent > naive in every seed). In the no-event null
the reafferent discriminability collapses from 20.5 to **1.1** and the localizer
drifts off node 6 — so the separation is genuinely world-caused, not a
self-motion/windowing artifact. And the localizer **tracks the world**: moving the
source to node 2 moves the read-out to 2.2. Two honest caveats the audit records:
(i) the naive detector reaches 8.3× here (the exafference is a *strong* source, so
the reafferent's real advantage is its **silence under self-motion** — 0.010 vs the
naive's 0.021 false-alarm floor — plus ~2.5× better discriminability, not naive
sitting at 1, as the code docstring loosely said); (ii) localization slightly
**undershoots for the near-tail node 6** (reads 5.4 — an edge effect as the source's
Gaussian is clipped by the body end) while it is accurate mid-body (2.2 for node 2).
Reproduction: [`audit_w3_self_graph.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/audit_w3_self_graph.py).

Row moves 🟡 (not yet audited) → ✅ (consistency-checked) for the operational
self/world cut, with the two caveats above on the record.

## What this establishes

- The self/world distinction the architecture claims as **structural** is, on the
  bench, **operational**: the agent tells its own motion from the world's, and
  says **where** on its own body the world changed.
- The cut is made **in the self-graph frame** — the payoff of building the
  self-model first ([self-model](self_model_topology.md)) and the world in its
  frame ([W1](world_in_self_graph.md), [W2](world_geometry_self_frame.md)).

Together, the four studies **construct** the self/world distinction from the body
up — self first, world in its frame, with the graph as the only computer.

## What's measured and plotted

**Raw data:** per-zone reading `s_k` and world position while the body sweeps;
`g_k`, nominal positions, and a baseline learned in calibration. **Computed:** the
self-referred reading and reafferent/naive deviations (as running code in
[Formalism](#formalism-the-cut-in-the-self-graph-frame) above); detector = mean
|deviation| over zones per step; discriminability = detector during steady
exafference ÷ during self-motion; localization = positive-deviation centroid over
self-graph nodes. **Plotted:** the two detectors over time; a node × time heatmap of
the reafferent deviation.

## Run

```bash
cd experiments && ../.venv/bin/python reafference_cut_self_graph.py
```
