# Test plan — pre-registered C-series

This page is written **before** the experiments are run. Its purpose is integrity:
to fix each test's hypothesis, order parameter, foil, and pass/fail criteria in
advance, so a result cannot be manufactured by tuning until the framework looks
good. We test the SMN architecture *as scientists, not as its advocates*. Where an
honest test needs a mechanism the bench does not yet have, we say so here rather
than quietly adding one to get a pass.

## Ground rules

1. **Pre-register.** Hypothesis, order parameter, foil, and pass/fail are stated
   before running. Results are reported against them, including nulls.
2. **A matched foil.** Every claim is tested against a control that is identical
   except for the one thing SMN says matters (coupling / modulation). A result
   that the foil also produces is not evidence for SMN.
3. **Seeds and intervals.** Replicated seeds with reported spread, not single
   illustrative runs.
4. **Declare every adjustment.** If a test requires changing a parameter,
   controller, or body beyond what an experiment started with — and especially
   anything **not specified in the SMN preprint** ([arXiv:2605.26856](https://arxiv.org/abs/2605.26856))
   — it is stated explicitly in the experiment page, marked as an adjustment.
5. **Be willing to be wrong.** If a result falsifies a claim, or shows our earlier
   understanding was incorrect, we update the framework and say so.

## Flagship — geometry → world model

- **Hypothesis.** With the world held fixed, the world an agent can *differentiate*
  scales with its body's sensory geometry: more segments (distributed sensing over
  a wider baseline) yield a richer, body-relative world model.
- **Order parameter.** Held-out position-decoding **skill** = `1 − MAE_decoder /
  MAE_naive`, where a model-free kNN decoder maps the agent's internal sensory
  state → its position in a fixed structured field, trained on the first part of
  the trajectory and tested on the held-out remainder. Skill 0 = no better than
  guessing the mean position; 1 = perfect. The naive normalization controls for
  differences in explored area across body sizes.
- **IV.** Segment count `n_seg ∈ {3, 5, 7, 9}`. World (a fixed multi-source field)
  identical across all runs.
- **Foil / control.** A **shuffle control**: the same decoder on state↔position
  pairs that have been shuffled, which must give skill ≈ 0. This proves the signal
  is a real body↔world relation, not an artifact of the decoder.
- **Pass.** Skill is clearly above the shuffle control **and** increases with
  `n_seg`.
- **Falsify.** Skill flat across `n_seg`, or not above shuffle — the internal
  state would not constitute a body-relative world model.

## Q1 — world model from sensation *modulation*

- **Hypothesis.** Modulation/coupling contributes *beyond* geometry and
  exploration: the **gap** between a coupled and an uncoupled controller in
  world-model skill widens with sensor count (the resolution principle —
  resolution is CAZ density × internal capacity, not raw transducer count).
- **Order parameter.** Skill gap = skill(coupled) − skill(foil), vs `n_seg`.
- **Foil.** Modulation off: sensory state not integrated across zones.
- **⚠ Mechanism gap (declared).** C0/C1 do **not** implement sensory modulation /
  gating — the messaging beam currently produces *locomotion*, not sensory
  integration. An honest test of this claim requires adding a sensory-modulation
  mechanism. Whether such a mechanism is specified in the SMN preprint must be
  checked first; if we add one, it is an explicit, declared adjustment. **Deferred
  until that mechanism is designed and its provenance stated.**

## Q2 — self / world distinction (reafference)

- **Hypothesis.** A forward model keyed on self-motion cancels self-caused sensory
  change but not world-caused change (Register 3).
- **Status.** Established in [P0](experiments/p0_reafference.md). Plan: port to the
  crawler as a multi-seed sweep.
- **Order parameter.** Residual ratio = |exafference residual| / |self-test
  residual|. **Foil.** No forward model (raw reading). **Pass.** Ratio ≫ 1 across
  seeds. This is the bench's strongest claim; the C-series adds the seed ensemble.

## Q3 — haltability → object-directedness

- **Hypothesis.** Haltability yields action organized around an *individuated
  object* (selective approach, persistence, reacquisition after occlusion), beyond
  reactive avoidance plus memory.
- **Order parameter.** Selective-approach success to a target object class, and
  reacquisition rate after occlusion. **Foils.** No-haltability; reactive-only
  (obstacle avoidance without object selection).
- **⚠ Mechanism gap (declared).** C1 demonstrates *halt-on-contact* (objecthood as
  resistance) but not object *selection*. A clean test needs a multi-object scene
  and a target-class mechanism not yet built. **Deferred — substantial new task.**

## Q4 — cross-modal object construction

- **Hypothesis.** Cross-modal modulation constructs an object identity stable
  across viewpoint change, sensory dropout, and single-modality conflict — beyond
  what uncoupled streams or a single modality achieve.
- **Order parameter.** Object-identity consistency over time and perturbation.
  **Foils.** Uncoupled modality streams; single modality.
- **⚠ Mechanism gap (declared).** [P3](experiments/p3_crossmodal_discrimination.md)
  did a version, but with hand-defined features (the review's main critique). A
  clean test on the minimal organism needs genuine multi-modal binding built into
  the messaging beam. **Deferred — substantial new mechanism.**

## Honest status

Of the five, the flagship and **Q2** are testable with the bench as it stands. The
modulation gap in **Q1**, and **Q3** and **Q4**, require mechanisms the bench does
not yet have; building them is legitimate, but each addition will be declared and
its relation to the preprint stated. We would rather report two rigorous results
and three honest "not yet testable" verdicts than five manufactured passes.

## Results so far (outcomes vs the predictions above)

The predictions above are left as written; outcomes are recorded here.

- **Flagship — [S1](experiments/sweep_geometry_worldmodel.md): partly supported,
  prediction corrected.** A real, body-relative world model exists at every body
  size (decoding skill ≈ 0.4 ≫ shuffle ≈ 0; held-out, shuffle-controlled). But it
  did **not** scale with segment count — flat in `n_seg`, even though larger
  bodies had more sensors *and* explored more. Our pre-registered "rises with
  `n_seg`" was wrong; we record the correction. The null is consistent with the
  resolution principle (raw transducer count alone adds no resolution) and
  redirects the live question to Q1 (modulation), which is deferred for lack of a
  declared mechanism. First run was confounded (instability + collapsed
  exploration) and discarded; the clean re-run used declared adjustments.
- **Q1 — [modulation](experiments/sweep_q1_modulation.md): core claim supported,
  narrow claim left open.** We built the declared mechanism (distributed per-zone
  dual-port modulators). Modulation cancels self-caused change to the noise floor
  at every body size; *without* it, self/world resolution collapses as the body
  grows (foil ratio 13.7 → 1.2) — so raw transducer count without modulation
  subtracts resolution rather than adding it. The pre-registered "modulated ratio
  rises with `n_seg`" was wrong (absolute ratio falls, confounded by a localized
  stimulus diluting the whole-body mean); the *modulation advantage* widens with
  density (8.5× → 22×). The narrow "absolute resolution scales with density" is
  left open. → **Now closed by [Q1b](experiments/sweep_q1b_resolution.md):** with a
  *distributed* stimulus (removing the localized-source dilution), the modulated
  world-detection ratio **rises** with CAZ density (14 → 22.6, ≈ 1/√N) while the
  foil falls toward 1 — resolution scales with density, but only with modulation.
  The first C-series prediction confirmed rather than corrected.
- **Q2 — [reafference](experiments/q2_reafference.md): partially supported.**
  Reafference cancels ~37% of self-caused change and lifts the self/world ratio
  (2.2 vs foil 1.58), but not to P0's clean level — limited by single-point
  (head) proprioception on a bending body, which is exactly what Q1's per-zone
  modulation fixes. P0 remains the clean canonical demonstration.
- **Q3 / Q4** — not yet run (mechanism gaps declared above).
