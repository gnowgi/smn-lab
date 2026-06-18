# C0 — minimal axial crawler (non-inertial movement + the messaging beam)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_c0_crawler.png)

## What it shows
The disciplined model organism of [Lesson 1](../lesson1.md): a three-block axial
crawler that *initiates* non-inertial movement. With two inter-segment joints the
joint-angle cycle is **non-reciprocal**, so it clears Purcell's scallop theorem
and a traveling wave nets a displacement. A bilateral chemical field biases the
wave, so the crawler climbs the gradient to the source — the minimal
aboutness-precursor: directed movement toward a "where".

## The agent
In the [diagram grammar](../diagram-grammar.md): a three-block axial chain, one
CAZ (a yaw opponent pair) at each joint, and bilateral chemical sensors mounted
inside each block. No contact skin and no localizer — chemotaxis from a field
gradient is all this experiment needs.

![C0 agent — the A3 crawler with bilateral chemical sensing, in the diagram grammar](../figures/c0_agent.png)

## Setup
- **Body** — `build_crawler_xml(n_seg=3)`: an axial chain of massed blocks, each
  inter-segment hinge driven by a **pull-only opponent pair**.
- **Medium** — overdamped, **anisotropic drag** (transverse ≫ tangential) applied
  as an explicit, inspectable force law (`apply_anisotropic_drag`): the
  *C. elegans* recipe by which a traveling wave becomes net thrust.
- **Messaging beam** — `MessagingBeam`: nearest-neighbor coupled phase oscillators;
  the traveling wave emerges from local coupling alone (no center), biased by the
  head's bilateral field sense.
- **Field** — `ScalarField`: a virtual chemical/thermal Gaussian source sampled
  bench-side at the sensor sites (per the [engine boundary](../assumptions.md)).

## Assumptions specific to C0
(in addition to the [common assumptions](../assumptions.md))
- v0 is the **overdamped-swimmer idealization**: gravity off, the drag *is* the
  medium. Gravity, a ventral touch skin, and objects are added in
  [C1](c1_touch.md).
- The anisotropic drag is an explicit Python force law, not MuJoCo's fluid solver.
- Steering is klinotaxis: a turn bias from the bilateral field difference at the head.


## What's measured, computed, and plotted
**Raw data (logged at 50 Hz):** head position `(x, y)`; the two inter-segment joint
angles `(theta_j1, theta_j2)`; the beam oscillator phases and coupling-message
magnitudes; each segment's field reading (mean of its left/right chemical samples);
segment centre-of-mass positions; distance to the source.

**Computed (the math):**
- `net_disp = hypot(x_end - x_start, y_end - y_start)` — straight-line distance moved.
- `path_len = sum of hypot(dx, dy)` over steps — total path length.
- `closed_gap = dist_start - dist_end` — how much of the gap to the source was closed (chemotaxis).
- `swept_area = |shoelace area of the (theta_j1, theta_j2) curve|` — cumulative gait non-reciprocity; a non-zero loop area is what Purcell's theorem requires for net motion.
- steering bias `= field(left head sensor) - field(right head sensor)` (klinotaxis).

**Plotted:** **A** the field (filled contours) + the head path + a few body postures + the source (★); **B** the messaging beam as a graph on the body — nodes = segments coloured by the field each senses, edges = coupling; **C** the gait in state-space `(theta_j1 vs theta_j2)`, coloured by time — the enclosed loop area is the non-reciprocity.

## Run
```bash
cd experiments && ../.venv/bin/python c0_crawler.py
```

## Outputs
- `figures/c0_crawler.png` — (A) field + path + body postures; (B) the messaging
  beam as a graph drawn on the body; (C) the gait loop in state-space.
- printed stats: net displacement, gap-to-source closed, swept area; verdict.

## Result & interpretation

![C0 — the three-block crawler climbs a chemical field; the messaging beam graph; the gait loop in state-space](../figures/c0_crawler.png)

*A: the crawler curves up the gradient to the source. B: the messaging beam drawn
on the body — nodes are segments coloured by the field each senses (the head
hottest), edges are the inter-segment coupling. C: the beam's shared actuation
state-space (θ_j1, θ_j2) — the gait loop whose enclosed area is the
non-reciprocity that yields net motion.*

Net displacement ~1.37 m, with the gap to the source closing from 1.84 m to
0.56 m: non-inertial locomotion and chemotaxis from the same coupled-oscillator
beam. The non-zero loop area in (C) is Purcell's scallop theorem being broken —
two joints suffice.
