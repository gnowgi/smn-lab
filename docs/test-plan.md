# Test plan — pre-registration & status

This page is the progression's **pre-registration ledger**. Each test's hypothesis,
order parameter, foil, and pass/fail is fixed **before** it is run — here or on the
experiment's own page — so a result cannot be manufactured by tuning until the
framework looks good. It is organized by the **self → world → object** spine, and
records outcomes against the predictions, including nulls. We test the SMN
architecture *as scientists, not as its advocates*; where an honest test needs a
mechanism the bench does not yet have, we say so rather than quietly adding one.

Two honesty caveats on the word *pre-registration*: (1) it is **self-administered**
— a commitment recorded in this repository before running, not a third-party
registration; for Phase-II we intend genuine OSF Registrations. (2) A few listed
"predictions" are **analytic consequences of the model's own equations** (e.g. R1's
tonic-load slope) — a consistency check of the implementation, not a contingent
finding — and are marked as such so they are not read as independent evidence for
the mechanism.

## Ground rules

1. **Pre-register.** Hypothesis, order parameter, foil, and pass/fail are stated
   before running. Results are reported against them, including nulls.
2. **A matched foil.** Every claim is tested against a control identical except for
   the one thing SMN says matters (elasticity / coupling / modulation). A result the
   foil also produces is not evidence for SMN.
3. **Seeds and intervals.** Replicated seeds with reported spread, not single runs.
4. **Declare every adjustment**, especially anything not specified in the SMN preprint
   ([arXiv:2605.26856](https://arxiv.org/abs/2605.26856)) — marked on the experiment page.
5. **Be willing to be wrong.** If a result falsifies a claim or shows our earlier
   understanding was incorrect, we update the framework and say so.

---

## Phase I·① — Self: the self-model
*Pre-registered on the experiment pages; recorded here.*

- **Topology-invariance.** *Hypothesis:* the framework read-out `coupling` recovers
  the body graph from movement for **any topology**, but only on an **elastic**
  substrate. *Order parameter:* endpoint / neighbour recovery vs a **rigid / frozen**
  foil. *Pass:* high recovery for the elastic body, ≈ chance for the foils.
  **✅ Confirmed** — [chain](experiments/self_model_topology.md) order recovery
  0.89 / neighbour 1.00 (rigid 0.40, frozen 0.14); [branched](experiments/branched_self_model.md)
  9/9 & 8/8; [sheet/tube](experiments/lattice_self_model.md) 0.99 / 0.97. Elasticity is
  load-bearing (Commitment C6).
- **Scale-invariance.** *Hypothesis:* the *same* `coupling`, coarse-grained,
  recovers the graph at **every level** of a nested lattice (a renormalization step).
  *Pass:* high recovery at each level. **✅ Confirmed** —
  [nested lattice](experiments/nested_lattice_self_model.md) 36→9→3: fine 0.88, mid
  1.00, coarse 1.00. The deep layer is a faint **canvas** (a feature, not a bug).

## Phase I·② — World: a world-model in the self-frame

- **Flagship — geometry → world model.** *Hypothesis:* with the world fixed, the world
  an agent can differentiate scales with its body's sensory geometry. *Order
  parameter:* held-out position-decoding **skill** = `1 − MAE_dec/MAE_naive` (kNN
  decoder, train/test split). *IV:* `n_seg ∈ {3,5,7,9}`. *Foil:* a **shuffle control**
  (must give skill ≈ 0). *Pass:* skill above shuffle **and** rising with `n_seg`.
  **🟡 Partly supported — prediction corrected** ([S1](experiments/sweep_geometry_worldmodel.md)):
  a real, body-relative world model exists at every size (skill ≈ 0.4 ≫ shuffle), but
  it did **not** rise with segment count (flat in `n_seg`). Our "rises with `n_seg`"
  was wrong; the null is consistent with the resolution principle and redirects the
  question to modulation (Q1).
- **Q1 — world model from *modulation*.** *Hypothesis:* modulation contributes beyond
  geometry — the coupled-vs-uncoupled gap widens with sensor count (resolution
  principle). *Foil:* modulation off. **✅ Core supported** — per-zone dual-port
  modulation cancels self-caused change at every size; without it, self/world
  resolution collapses as the body grows (foil ratio 13.7 → 1.2). Closed by
  **[Q1b](experiments/sweep_q1b_resolution.md)**: with a distributed stimulus the
  modulated ratio **rises** with CAZ density (14 → 22.6), the foil falls toward 1 —
  resolution scales with density, but only with modulation.
- **Q2 — self / world distinction (reafference).** *Hypothesis:* a forward model keyed
  on self-motion cancels self-caused but not world-caused change. *Order parameter:*
  residual ratio |exafference| / |self-test|. *Foil:* no forward model. *Pass:*
  ratio ≫ 1. **🟡 Partially supported** ([Q2](experiments/q2_reafference.md)): 2.2 vs
  foil 1.58 — real but modest, limited by single-point (head) proprioception on a
  bending body, which is exactly what Q1's per-zone modulation fixes.

## Phase I·③ — Object: object-directedness

- **Q3 — haltability → object-directedness.** *Hypothesis:* haltability yields action
  organized around an individuated object. *Foils:* no-haltability; a CPG rhythm.
  **🟡 Directedness confirmed, selection deferred** ([E3](experiments/p6_haltability_aboutness.md)):
  computed in the self-frame recovered first, the haltable action *pattern* is
  **persistent** (1.5 s vs CPG 0.3 s), **returnable** (5×), and **side-specific** — that
  triad *is* object-directedness. Object-*class selection* among several objects needs
  a multi-object scene and presupposes discovering **particulars** + a ratchet
  (Phase II / M2) — deferred.

## Phase I → II — the pivot (why more body ≠ more world)

The flagship's null and Q1b together are the hinge: **linear scaling of identical
zones does not enrich the world-model**; resolution scales with **CAZ density ×
internal capacity × depth of nesting**, not raw transducer count. This motivates the
evo-devo path of [Phase II](phase2.md).

## Phase II — what the layering enables

- **Haltability needs a pivot layer.** *Hypothesis:* a stable, addressable **hold**
  needs a stable reference (the canvas). *Order parameter:* held-node position spread
  + addressing, **canvas ON vs OFF**. *Pass:* a tight, addressed hold only with the
  canvas. **✅ Confirmed** ([haltability](experiments/haltability.md)): hold-spread
  0.0055 vs 0.046 (8×), addressed 6/6 vs 4.5/6 — while the rest of the body keeps
  moving. (This is the *capacity*; the object-directed *pattern* is E3.)

## Preprint predictions (reproducing the paper's testable claims)

- **Prediction 1 — [haltability signatures](experiments/sweep_pred1_haltability.md):
  confirmed.** Deceptive reach: the haltable controller imposes a distinct stop
  (velocity → 0, dwell ~0.17 s) absent in a smooth controller; the *dwell* (not the
  zero-crossing) is the diagnostic, and it carries no speed benefit — as predicted.
- **Prediction 2 — [zonal dissociations](experiments/sweep_pred2_zonal.md): partially
  confirmed.** Same task through a rigid vs viscoelastic tool: the optimal gain *moves*
  with substrate and the compliant substrate is far less forgiving (60× vs 11× spread);
  but the strong "substrate-specific priors are *needed*" reading is not supported (a
  conservative generic prior ≈ matches both).
- **Prediction 3 — [antagonistic benefits](experiments/sweep_pred3_antagonistic.md):
  confirmed.** Co-contraction cuts peak deviation 4.4× and integrated error ~28× after
  a perturbation, at a steep ~quadratic energy cost (a knee near coc ≈ 0.3–0.6).
  Declared adjustment: a muscle-impedance model (ideal motors were inert for stiffness).

## Still open / deferred

- **Q4 — cross-modal object construction.** [P3](experiments/p3_crossmodal_discrimination.md)
  did a version with hand-defined features (the review's main critique); a clean test on
  the minimal organism needs genuine multi-modal binding in the messaging beam. Deferred.
- **Object-class selection** (Q3's second half) — needs discovering particulars + a
  ratchet (bodily emancipation + external/social scaffolding). Phase II / M2.

## Honest status

The **self-model** (topology- and scale-invariance) and **haltability** are confirmed;
the **flagship** and **Q1/Q1b/Q2** world-model tests are done (two corrected, honestly);
**Q3**'s object-directedness is shown, its selection deferred; **Q4** awaits a mechanism.
Three preprint predictions reproduced. We would rather report rigorous results and honest
"not yet testable" verdicts than manufactured passes.
