# The canonical SM block — pre-registration

!!! warning "Pre-registered, unrun"
    Written and committed on 25 Nov 2026 **before any self-model or locomotion run on this block**.
    The block's mechanical statics are fixed by `tests/test_sm_block.py`; nothing below has been
    measured. When results exist they are added beneath this page, and the predictions here are
    not edited.

## Why this block

Preprint v3 builds every body from one modular unit. Its Sensation Modulator is pull-only,
depends on both activation and configuration, and senses through the same tissue that pulls
(Eqs. 1–2). Its elastic substrate is "the physics keystone of the whole construction" (§3.5, C7).
The bench has so far used two different units:

- the crawler: ideal torque motors at each hinge, with a parallel joint spring only where an
  experiment sets one (`self_model_topology.py` uses 0.6; the locomotion experiments use 0);
- the lattice bodies: a motor on a tendon that carries a parallel spring.

Neither is the muscle–tendon unit v3 describes. This page fixes one canonical block, used from
here on by both the bench and the playground, and pre-registers the tests it must pass.

## The block

`smn_lab/sm_block.py`, built from MuJoCo constructors. It is the three-element (Hill-type)
muscle:

| element | v3 | MuJoCo realization |
|---|---|---|
| contractile element (CE) | the active pole of Z±, F = Φ(a, …) ≥ 0 | motor on an internal slide DOF; `ctrlrange 0 F_max`; viscosity `b_ce` |
| series elastic element (SEE) | the tendon, "in series with a passive elastic one" (§3.5) | fixed tendon L = ∓r·q + x, stiffness `k_see`, dead band `springlength="-10 0"`: pulls when stretched, slack otherwise |
| parallel elastic element (PEE) | k (q − q0) of Eq. 3 | the joint's stiffness `k_pee` |
| afferent s = Ψ(q, q̇, F) | Eq. 2, same tissue | SEE length (tension; tendon-organ), CE force, joint angle and velocity (muscle–tendon length and rate; spindle-like) |

**Fixed parameters.** r = 0.025 m. F_max = 5 N, so r·F_max equals the bench torque motors' peak
of 0.125 N·m. k_see = 1800 N/m, a 2.8 mm stretch (0.11 rad joint-equivalent) at F_max.
b_ce = 2.0. m_ce = 10⁻³ kg (numerical). The board's activations map onto force as
F = (a / c_max)·F_max.

**A point the construction settles before any experiment.** A force-producing CE in series with
a spring supplies *no* restoring stiffness. The spring transmits whatever force the CE makes,
wherever the joint is. With co-contraction at 2 + 2 N and no parallel element, a 0.02 N·m push
moves the joint 0.79 rad and it never returns. With k_pee = 0.6 it moves 0.033 rad and returns to
0.0000 (`test_series_spring_alone_does_not_restore`, `test_parallel_element_restores`). §3.5's
sentence therefore does not by itself yield Eq. 3's k(q − q0); the block carries both elements.
*Suggested for v3:* say that the SM is a contractile element with a series and a parallel elastic
element, and that the restoring term of Eq. 3 is the parallel one, or else a CE force–length
relation.

**Declared idealizations.** No force–length or nonlinear force–velocity curve; constant moment
arm; the CE slide carries a small numerical mass.

## H1 — the self-model on the canonical block (C7)

**Design.** Replicates `self_model_topology.py` exactly, with the torque motors replaced by the
block:

- an 8-segment chain, drag 0.6 / 4.0, 4 s warm-up and 60 s recorded, proprioceptive noise 0.02;
- 5 seeds;
- an independent OU drive per joint, its positive part sent to the flexor CE and its negative
  part to the extensor CE (same OU parameters, mapped by F = (a/2.5)·F_max);
- read-out `smn_lab.self_model.transfer`, after common-mode removal;
- scores `neighbour_accuracy` and `order_accuracy` (`smn_lab.metrics`).

**Conditions (control parameters).**

| condition | k_see | k_pee | drive |
|---|---|---|---|
| **block** | 1800 | 0.6 | OU |
| PEE-only (stiff tendon) | 10⁶ | 0.6 | OU |
| SEE-only | 1800 | 0 | OU |
| rigid foil (bench precedent) | 1800 | 80 | OU |
| frozen foil | 1800 | 0.6 | none |

**Order parameter, and a classification note.** v3 is inconsistent here. Table 2 classes
self-model graph recovery as a *diagnostic*; §5.2 calls recovery quality the section's *order
parameter*. This pre-registration follows Table 2 and §12: recovery is a diagnostic, and the test
is the **separation from matched foils**. *Suggested for v3:* reconcile §5.2 with Table 2.

**Predictions.**

- **P1.** The block recovers the chain: mean neighbour accuracy ≥ 0.90 and order accuracy ≥ 0.80.
  (The torque-motor bench, as published, reaches 1.00 and 0.89.)
- **P2 (C7 falsifier).** The rigid foil fails: neighbour accuracy ≤ 0.60, and below the block's by
  ≥ 0.30. The frozen foil is at chance.
- **P3 (X: no stake).** PEE-only matches the block within 0.10 on both scores. If it does, series
  compliance is not what the read-out needs; parallel compliance is.
- **P4 (X: two competing outcomes, both informative for §3.5).**
  - (a) SEE-only fails or degrades, because nothing restores the joints: the body wanders to its
    joint limits and the co-movement gradient is lost.
  - (b) SEE-only recovers, because under continual OU drive the series springs still transmit
    differential motion with attenuation.

  The outcome is reported as it falls, together with the fraction of time any joint sits at its
  bend limit.

**Falsified if.** The block fails P1 while the torque-motor bench passes on the same run.
Diagnosis would then precede any retuning, and retuning is a new pre-registration.

## H2 — no regression in behaviour

**Design.** C0 (3 segments, water, chemotaxis, 60 s) and gravity_locomotion (8 segments, ground,
ratio 20, 15 s), run on the block (k_see = 1800, k_pee = 0, as in those experiments) with board
gains unchanged. The same script runs the torque-motor bench alongside, as the baseline.

**Prediction.** Net displacement on the block is ≥ 50% of the torque-motor baseline in both, and
C0 still closes distance to the source.

**If not.** The result is reported, and the gains are not retuned within this pre-registration.

## H3 — exploratory (X): does the tendon tell the body about the ground?

On ground at friction ×0.3, ×1 and ×3 (block, k_pee = 0), report how the following vary with
friction while the command does not:

- the SEE tension afferent;
- the phase lag of joint angle behind the command;
- the realized bend.

With torque motors the force "afferent" *is* the command, so it can carry no ground information.
No pass threshold is set: this is the measurement that would ground step 3 of the S0b fix plan
(the load-limited actuator).

## Addendum — fixed before the first run (26 Nov 2026)

GN approved the hypotheses and thresholds above on 26 Nov 2026 ("start a series of experiments
with the canonical block"). Committed before `experiments/sm_block.py` was run. Details the page
left open are fixed here, so none can be chosen after seeing a result:

- **Engine.** MuJoCo **3.9.0**, the version in the bench's own `.venv`, so the block is compared
  with the torque-motor bench under the same engine. A cross-check on 4.0.1 is reported, but it
  does not decide any verdict. The statics tests pass on both.
- **H1 drive.** The bench's OU process unchanged (`tau_tc = 0.15`, `tau_sig = 8.0`): flexor force
  `clip(τ, 0, 2.5)·(F_max/2.5)`, extensor force `clip(−τ, 0, 2.5)·(F_max/2.5)`. The efference
  passed to `transfer` is τ, as in the bench. Joint damping 0.05 and bend limit 45° are as in
  `self_model_topology.py`. Seeds 0–4; mean and s.d. reported.
- **H1 torque-motor reference.** `self_model_topology.py`'s own "elastic" condition is rerun in
  the same script, on the same engine and seeds, so that P1's comparison is like with like.
- **H2.** C0: 3 segments, water, source (1.6, 0.9), amplitude 1, σ 0.9, 60 s; board kp 4, kd 0.4,
  c_max 2.5, turn gain 4. gravity_locomotion: 8 segments, μ = 0.15 / 3.0, joint damping 0.03,
  bend limit 50°, 15 s. Block k_pee = 0 in both, as those experiments have no joint spring.
  Metrics: net head displacement, and for C0 also the distance closed to the source. Both runs
  are deterministic, so one run each.
- **H3.** 8 segments on ground, friction (μ_long and μ_trans together) scaled ×0.3, ×1 and ×3,
  20 s, first 5 s discarded. Reported per condition, averaged over joints:
  - mean SEE tension (flexor + extensor);
  - the lag of joint angle behind command (peak of their cross-correlation);
  - realized bend amplitude.

  The same quantities are reported for the torque-motor bench, whose "force afferent" is the
  command itself.

## Protocol deviation (26 Nov 2026, before any PEE-only data)

On the first run, the PEE-only condition, implemented as k_see = 10⁶ on the CE's 1 g numerical
mass, was numerically unstable at dt = 2 ms: the solver diverged at t = 12 ms, with no data
recorded. The limit this condition stands for, an infinitely stiff tendon, transmits the CE force
directly to the joint. That is exactly the bench's torque-motor chain with the same parallel spring
(k_pee = 0.6), and `self_model_topology.py`'s "elastic" condition, which this script already runs
as its torque-motor reference. **PEE-only is therefore scored on that reference row.** P3's
threshold is unchanged. Before the deviation was committed, the only outputs seen were the
torque-reference and block rows of H1.

## Run

```bash
python tests/test_sm_block.py                 # statics of the block (already passing)
cd experiments && python sm_block.py          # H1–H3 (to be written after this page is approved)
```
