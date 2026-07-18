# C0 — minimal axial crawler (non-inertial movement + the messaging beam)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_c0_crawler.png)

## What it shows
The disciplined model organism of [The Construction of Experience](../construction-of-experience.md): a three-block axial
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


## Formalism — locomotion from local coupling

Three model pieces (all in the framework) turn local coupling into directed motion;
a fourth quantity is the experimenter's check that motion is even possible.

**1 · The messaging beam — a traveling wave with no center.** Each inter-segment
joint hosts a phase oscillator \(\varphi_i\) advancing at \(\omega = 2\pi f\), pulled
by nearest-neighbour (Kuramoto-style) messages toward a fixed phase lag \(\delta\):

\[
\dot\varphi_i = \omega + K\!\left[\sin\!\big((\varphi_{i-1}-\varphi_i)-\delta\big)
                               + \sin\!\big((\varphi_{i+1}-\varphi_i)+\delta\big)\right],
\qquad
\theta^{\text{cmd}}_i = A\sin\varphi_i + g\,b,
\]

with \(b\) the head's bilateral field bias (chemotactic turn). The wave emerges from
the coupling \(K\) alone — no central clock:

```python
--8<-- "smn_lab/control.py:beam_command"
```

**2 · The opponent board — a signed torque from two pull-only muscles.** A PD law on
the commanded angle gives a desired torque, split into antagonist activations (the
opponent pair is the atomic actuator):

\[
\tau = k_p(\theta^{\text{cmd}}-\theta) + k_d(\dot\theta^{\text{cmd}}-\dot\theta),
\qquad a_R=\max(\tau,0)\wedge c_{\max},\quad a_L=\max(-\tau,0)\wedge c_{\max}.
\]

```python
--8<-- "smn_lab/control.py:opponent_commands"
```

**3 · The medium — anisotropy is what rectifies the wave.** Overdamped drag in each
segment's local frame, transverse \(\gg\) longitudinal; that anisotropy
(\(c_\perp \gg c_\parallel\)) is the *C. elegans* recipe by which a transverse wave
becomes net forward thrust:

\[
f^{\text{local}} = (-c_\parallel v_\parallel,\; -c_\perp v_\perp),\qquad c_\perp \gg c_\parallel,
\]

```python
--8<-- "smn_lab/crawler.py:drag"
```

**4 · Is motion even possible? (the experimenter's check).** Purcell's scallop
theorem: in an overdamped world a *reciprocal* gait nets zero. Non-reciprocity is
the signed area enclosed by the \((\theta_{j1},\theta_{j2})\) loop (shoelace) — a
measurement of the gait, so it lives in `smn_lab.viz`, not the agent:

\[
\text{swept area} = \tfrac12\sum_i\big(\theta_{1,i}\,\theta_{2,i+1} - \theta_{1,i+1}\,\theta_{2,i}\big).
\]

```python
--8<-- "smn_lab/viz.py:loop_area"
```

Two joints give a non-zero loop area — enough to clear the theorem. (S0 then makes
the coupling \(K\) the [independent variable](sweep_c0_coupling.md).)

## What's measured and plotted
**Raw data (logged at 50 Hz):** head position `(x, y)`; the two inter-segment joint
angles `(theta_j1, theta_j2)`; the beam oscillator phases and coupling-message
magnitudes; each segment's field reading; segment centre-of-mass positions; distance
to the source. **Computed:** `net_disp`, `path_len`, `closed_gap` (chemotaxis), and
the gait `swept_area` — the last defined as running code in
[Formalism](#formalism-locomotion-from-local-coupling) above.

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
