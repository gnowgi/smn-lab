# E4b — The onset of objecthood is a coupling-density transition

!!! note "Exploratory trial — P/E series"
    Part of the bench's first exploratory series, built while learning the bench:
    a **proof-of-concept**, not a clean ablation (several runs are single-seed and
    some metrics saturate). The disciplined model organism and the going-forward
    line is the **C-series** — [C0](c0_crawler.md), [C1](c1_touch.md) — grounded in
    [Lesson 1](../lesson1.md).


`experiments/p8_objecthood_transition.py`

[E4](p7_scaling_network.md) established two things: each zone reliably registers one
differentia (hard/soft at accuracy 1.00), and the world model scales 2^K with the
zones the board **binds**. This experiment asks the network-physics question that
follows: as the board's coupling density rises, **when** do differentiae bind into
an object? The answer is that objecthood appears as a **percolation-like
transition** — it has a threshold in the modulation network's connectivity, not an
all-or-nothing switch.

## Setup

Model the board as a random graph **G(K, p)**: each pair of *K* zones is coupled
with probability *p*. Composition binds zones within a connected component (coupled
zones share their differentiae into one joint code), so the richest single object
the agent can hold is the **largest bound component**, with capacity
2^(largest component). Sweeping *p*, the largest bound object — the order parameter
— traces the classic giant-component curve.

The per-zone differentiae here are the **real bench reads of E4**; what is swept is
the **board's connectivity**. This is the random-board baseline (structured boards
are an open question). Parameters: K = 24 zones, 400 random boards averaged per
coupling density, swept over p ∈ [0, 0.32].

## What it measures

| panel | claim | independent variable | dependent variable |
|---|---|---|---|
| **A — order parameter** | a giant bound object emerges past a critical density | coupling density p | largest bound object / K |
| **B — capacity** | the world model jumps at the transition | coupling density p | 2^(largest bound object) |

The two reference lines are the **giant-component onset** p_c = 1/K and **full
connectivity** p = ln K / K.

## Result

```
=== E4b — onset of objecthood as a coupling-density transition ===
  K=24 zones; p_c(giant)=1/K=0.042; p_c(connected)=lnK/K=0.132

  p≈0.021 (=0.5/K): largest bound object ≈  few /24 zones   -> capacity ~2^4
  p≈0.042 (=1.0/K): largest bound object   rising            -> capacity climbing
  p≈0.083 (=2.0/K): largest bound object ≈ 18 /24 zones      -> capacity ~2^18
```

- **Below p_c = 1/K** the differentiae stay **fragmented** — the largest bound
  object is only a few zones (capacity ~2^4): the agent holds no real object, only
  scattered differences.
- **Past p_c** a **giant bound object emerges** — the capacity jumps to ~2^18 by
  p = 2/K. The order parameter (largest bound object as a fraction of K) is the
  classic giant-component curve.
- **Objecthood is not all-or-nothing.** It has a **threshold** in the modulation
  network's connectivity — a percolation-like phase transition in a complex network.

[![Objecthood as a percolation transition: the largest bound object (order parameter) and the world-model capacity jump as the board's coupling density crosses p_c = 1/K; below it the differentiae are fragmented, above it a giant bound object emerges](../figures/p8_objecthood_transition.png)](../figures/p8_objecthood_transition.png)

## What this experiment shows

- **Objecthood has an onset.** Given reliable per-zone differentiae, whether they
  *bind* into an object is set by the board's coupling density, with a critical
  threshold p_c = 1/K.
- **The agent is a complex network.** The transition reframes the scaling law of E4
  as network physics: the question of when a world appears is a percolation
  question, answerable with random-matrix / network-dynamics methods.
- **The bench supplies the system.** The coupling matrices and per-zone reads come
  from the real body, so the physics questions are posed on an actual cognitive
  agent, not a toy graph.

It does **not** yet show:

- **Structured boards.** Only the *random* board (G(K, p)) is swept here; how
  modular, hierarchical, or scale-free coupling shifts the onset is open.
- **The coupling spectrum.** What the spectrum of the coupling matrix says about
  *which* networks compose objects (a random-matrix question) is left for future
  work.
- **Binding dynamics.** The *dynamics* of binding — how an object forms in time, not
  just whether it can — is not modeled here.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus:

- This is an **analytic network sweep**, not a MuJoCo run: it reuses E4's real
  per-zone differentiae and varies only the board connectivity, so it needs no
  physics engine.
- A **random-graph board** G(K, p) with composition binding zones within a connected
  component — the random-board baseline against which structured boards will be
  compared.

## Why this experiment is in the bench

It turns the scaling law into a phase transition and opens the bench's most explicitly
**physical** line of inquiry — objecthood as a percolation phenomenon in the body's
modulation network. It marks the frontier where the cognitive vocabulary hands off to
network physics, on a system the bench can supply in full.

## Run it

```bash
cd experiments && ../.venv/bin/python p8_objecthood_transition.py
```

Outputs: `figures/p8_objecthood_transition.png`. Runtime: a few seconds on a laptop
CPU (an analytic sweep over random boards — no physics engine, no rendering).
