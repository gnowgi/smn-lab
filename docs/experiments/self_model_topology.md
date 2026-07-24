# Self-model — the body's topology, recovered from movement

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_self_model_topology.png)

!!! warning "Scope of this result (audit, 2026-07)"
    Everything below holds under the **exploratory (babbling)** drive this experiment
    uses — an independent OU torque per zone. It does **not** hold under coordinated
    locomotion: driven by the beam wave, the read-out tracks command phase, not body
    topology, and neighbour-accuracy collapses toward chance
    ([babble vs behave](self_model_babble_behave.md)). Also: chance neighbour-accuracy
    is **2/n** for an *n*-zone chain, so the metric is uninformative on 3-segment
    bodies (n = 2 → chance 1.0). Read this page as *the self-model is recoverable from
    exploratory movement*, and see the audit page for the interpretation and the
    complex-body prediction.

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

## Formalism — the transmission gain \(G\)

While the body moves, each zone \(i\) logs two channels: its **own efference**
\(\tau_{t,i}\) (the torque it commands, `TAU`) and, on the broadcast, every zone
\(j\)'s **afferent motion** \(v_{t,j}\) (joint angular velocity, `VEL`). Before
reading, the whole-body common mode is stripped — the reafference move — so only
motion *relative to the body* survives:

\[
v_{t,j} \;\leftarrow\; v_{t,j} - \frac{1}{n_J}\sum_{j'} v_{t,j'}.
\]

```python
--8<-- "experiments/self_model_topology.py:commonmode"
```

The self-model read-out is the magnitude of the normalized correlation between
zone \(i\)'s efference and zone \(j\)'s afferent motion, symmetrized, self-terms
zeroed:

\[
G_{ij} \;=\; \Bigl|\, \tfrac{1}{n}\sum_{t} \hat{z}(\tau)_{t,i}\,\hat{z}(v)_{t,j} \,\Bigr|,
\qquad G \leftarrow \tfrac{1}{2}\bigl(G + G^{\top}\bigr), \quad G_{ii}=0,
\]

with \(\hat{z}\) the per-channel z-score (same operator as on the
[template page](../formalism-and-code.md)). Because the zones' drives are
independent, \(G_{ij}\) isolates *how much \(j\) moves because \(i\) moved* — the
transmission gain, which elastic attenuation makes fall off with hop-distance.

This read-out is **the model** — it lives in the framework
([`smn_lab/self_model.py`](../self-model-and-measurement.md)), not in this script,
because it is what the theory says the *agent* computes:

```python
--8<-- "smn_lab/self_model.py:transfer"
```

Each row is one zone's own [`local_read`](../self-model-and-measurement.md) — its
efference correlated against the broadcast — so no zone ever holds the whole matrix
(**C3**). The body graph is then the union of each zone's own strongest-co-mover
edge, decided locally.

Recovering the whole **chain order** is different: it needs the entire matrix at
once (the Fiedler vector \(\nu_2\) of the Laplacian \(L = D - G\)), so it is *not*
something a zone can do — it is the **experimenter's** summary, and it lives in
[`smn_lab/metrics.py`](../self-model-and-measurement.md), not in the agent:

\[
L = D - G, \qquad \text{order} = \operatorname{argsort}\,\nu_2(L).
\]

```python
--8<-- "smn_lab/metrics.py:seriation_order"
```

### The parameter the live demo varies

The read-out is only informative because the substrate is **elastic**. Joint
stiffness \(k\) (`joint_stiffness` in `crawler.py`) is the single varied parameter;
the three conditions are exactly:

```python
--8<-- "experiments/self_model_topology.py:conditions"
```

| condition | \(k\) | drive | what happens to \(G\) |
|---|---|---|---|
| **elastic** | `0.6` | on | co-movement **decays with hops** → chain order recovered |
| **rigid** | `80.0` | on | body moves as one common mode → no differential signal to read |
| **frozen** | `0.6` | off | no movement → \(G\) carries nothing |

In the seminar the slider is \(k\): the audience watches the transfer matrix's
super/sub-diagonal band (the recovered adjacency) wash out as \(k\) rises — the
[result below](#result-prediction-confirmed) at \(k=0.6\), and the rigid foil at
\(k=80\).

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

## What's measured and plotted

**Raw data (per run = one condition × one seed):** per-zone commanded torque `TAU`
(efference) and joint angular velocity `VEL` (afference), common-mode removed.
**Computed:** the transmission gain \(G\), the hop-distance curve, and the recovered
chain order — all defined and shown as running code in
[Formalism](#formalism-the-transmission-gain-g) above. **Plotted:** the
transfer-vs-hops curve for all three conditions and the elastic transfer matrix
(the bright super/sub-diagonal band = recovered chain adjacency).

## Run

```bash
cd experiments && ../.venv/bin/python self_model_topology.py
```
