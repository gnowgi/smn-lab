# The self/world boundary is earned

!!! question "The question this answers"
    If a force is applied at a body zone at time \(t_0\) and is *still there* from
    \(t_1\) to \(t_n\), it is just a **weight** resting on that zone. How does the agent
    know it is **not part of the body** — since it is constantly there?

The honest answer is: it does not, and it should not. The self/world cut is **not**
about where a force comes from. It is about whether the force produces **ongoing,
unpredicted change**. A constant load makes one transient and then settles; a moving
prey keeps changing. The boundary between self and world is therefore not given in
advance — it is **earned**, moment by moment, by adaptation.

## The mechanism — a reafference residual against a slow baseline

The agent carries a slowly-adapting **baseline**: the self-model's expectation of how
its own body sits (a forward model). The quantity that matters is the **reafference
residual** = actual displacement − baseline.

- A **constant** load makes one transient and then holds steady. The baseline tracks
  it, the residual decays to ≈ 0, and the load is **absorbed into the self** —
  recalibrated as body. (You stop feeling your clothes; a barnacle becomes part of the
  whale.)
- A **moving** prey keeps changing faster than the baseline can follow. The residual
  stays elevated, so it stays **world** — an *other*.

This is just habituation, stated precisely. Nothing needs to know the "true" origin of
a force; the residual against a slow baseline earns the boundary on its own.

## The experiment

On the two-layer [Hydra](hydra.md) sac (foot anchored, so a constant force reaches a
static equilibrium instead of drifting the animal away), apply the **same-magnitude**
force at one ectoderm zone — once **constant**, once **moving** (a struggling prey).
The order parameter is the reafference residual at that zone over time.

| condition | reafference residual (world-signal) | reading |
|---|---|---|
| **constant load** — onset transient | 0.2226 | a real event *arrives*… |
| **constant load** — settled | **0.0093** | …then is **absorbed into the self** |
| **moving prey** — settled | **0.0950** | stays **world** |
| ratio (moving / constant, settled) | **10×** | only *ongoing change* stays world |
| **control** — removing the absorbed load | 0.1599 | its removal is itself a **world-event** |

![The self/world boundary — the constant load's residual decays to near zero while the moving prey's stays elevated; removing the absorbed load spikes the residual](../figures/self_world_boundary.png)

The constant load starts as a clear event (residual 0.22) and then **decays to ≈ 0.009**
as the baseline absorbs it — it has become body. The moving prey settles **10× higher**
(0.095) and stays world. The two forces are the *same magnitude*; what separates them is
only whether the change is ongoing and unpredicted.

## The control that proves absorption

The cleanest evidence that the constant load truly *became self* is what happens when
you take it away. After the load has been absorbed, **removing** it spikes the residual
back up (to 0.16) — because the baseline had come to *expect* it. Its removal is now a
**world-event**. You only get startled by the absence of something your body had folded
into its own expectation.

## Why this matters for the architecture

This closes a gap that any embodied self/world account has to answer. It shows the cut
is not a labeling rule ("forces from outside are world") but a **dynamical** one
("unpredicted ongoing change is world"), computed by the same reafference machinery the
bench uses everywhere else — see [Q2 reafference](q2_reafference.md) and
[the cut in the self-graph (W3)](reafference_cut_self_graph.md). Object-directedness in
the [Hydra capture reflex](hydra.md#stage-2-the-whole-net-capture-reflex-with-no-controller)
uses exactly this threshold: the reflex fires for a *moving mass above threshold* and
ignores an inert, constant touch.

## Run it

```bash
cd experiments && ../.venv/bin/python self_world_boundary.py
```

Source:
[`self_world_boundary.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/self_world_boundary.py).
