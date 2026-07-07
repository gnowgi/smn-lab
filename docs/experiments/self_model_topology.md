# Self-model — the body's topology, recovered from movement

## Why this experiment

Before an agent can have a world model it must have a **self-model**: a model of
its own body. The SMN framework makes this order strict — the world model is
world-geometry expressed *in the self-model's frame* — so the self-model is the
load-bearing construction for the [self/world distinction](q2_reafference.md).

It also settles a question the framework insists on (Commitment **C3**): the
shared state-space must be computed *without a central reader* — "the graph **is**
the computer," or else a homunculus is smuggled in to read it. Here the body's
own connectivity graph is recovered from movement **locally**, with no zone ever
reading the whole body.

## The idea

The zones move (that is what zones do). The segments joining them are **elastic**,
so when one zone moves, a farther zone displaces *less* — the transmitted motion
attenuates with the number of intervening segments (hops). Each zone therefore
asks one purely local question — *whose movement follows from mine?* — by
correlating its **own efference** (the torque it commands) with the **afferent
motion** it hears from every other zone. Because the drives are independent, this
isolates the transmission gain `G[i,j]` ("how much j moves because i moved"),
which falls off with hop-distance. Nearest-neighbours are the strongest co-movers;
the body's connectivity graph assembles itself.

We recover a **topology, not a metric** — a *graph, not a ruler*. No absolute
distance is ever measured; only who-is-near-whom, in hops.

## Pre-registered prediction

For an **elastic** chain, `G[i,j]` decays monotonically with hop-distance, so each
zone's strongest co-mover is a true chain-neighbour and the chain order is
recoverable. Falsifiers, run as foils:

- **rigid** chain — stiff joints move the body near-rigidly, so after the
  whole-body common mode is removed (reafference) there is *no differential
  displacement* left to read; the self-model should not form.
- **frozen** — an elastic body with no drive: no movement, no self-model (the
  resolution principle — modulation, not transduction, builds it).

## Result — prediction confirmed

![Transfer gain decays with hops for the elastic chain only (left); the transfer matrix's bright super/sub-diagonal band is the recovered chain adjacency (right)](../figures/self_model_topology.png)

8-segment chain, 5 seeds:

| condition | chain-order recovery | 1-hop neighbour accuracy | transfer 1-hop → 2-hop |
|---|---|---|---|
| **elastic** | **0.89 ± 0.08** | **1.00 ± 0.00** | 0.19 → 0.09 (decays) |
| rigid | 0.47 ± 0.10 | 0.40 ± 0.17 | 0.00 → 0.00 |
| frozen | 0.43 ± 0.00 | 0.14 ± 0.00 | 0.00 → 0.00 |

Every zone's single strongest co-mover is its true chain neighbour (100%), and the
whole chain order falls out by spectral seriation (0.89). The transfer matrix shows
a bright super/sub-diagonal band — **that band is the recovered chain adjacency**.
The rigid and frozen foils carry no usable signal.

## What this establishes

- **The self-model is a graph, built from movement**, scale-free (hops, not
  metres) — the body as its own relational frame.
- **C3 realized as an emergent broadcast.** The estimate is built by each zone
  from its own efference copy and what it hears of its neighbours — a local
  reafference computation on the body graph, with no central fit and no separate
  reader.
- **C6 in action.** Elasticity is load-bearing: differential displacement is what
  encodes the graph, so a body with none (rigid) recovers nothing.

It is the foundation the world-model series builds on:
[W1](world_in_self_graph.md) places a world feature on this graph,
[W2](world_geometry_self_frame.md) reads relations in its units, and
[W3](reafference_cut_self_graph.md) makes the reafference cut in its frame.

## The self/world card

Assembled into a [self/world card](../diagram-grammar.md#the-selfworld-card) — the
designed chain, the recovered self-model as an abstract graph (a path; edge width =
measured coupling), and a world source localized along the *recovered* graph:

![Self/world card for the chain body: designed agent, recovered self-model path, world localized along the chain](../figures/self_world_card_chain.png)

## What's measured, computed, and plotted

**Raw data:** per-zone commanded torque `TAU` (efference) and joint angular
velocity `VEL` (afference), common-mode removed. **Computed:** `G[i,j] =
|corr(TAU_i, VEL_j)|`, symmetrized; the hop-distance curve `mean G vs |i-j|`;
chain order by the Fiedler vector of the `G`-graph Laplacian (spectral seriation);
1-hop neighbour accuracy = fraction of zones whose argmax co-mover is a true
neighbour. **Plotted:** transfer-vs-hops curve for all three conditions; the
elastic transfer matrix.

## Run

```bash
cd experiments && ../.venv/bin/python self_model_topology.py
```
