# Status ledger — what to trust, and how far

!!! abstract "Read this first"
    Every experiment here is a **simulation that tests whether the SMN mathematics is
    internally consistent and buildable** — that the equations do what the framework
    says they do. **None is a claim about how biological agents actually work.** These
    labels track the epistemic status of each *consistency check*, not biological
    validity. Like any live research project, some parts are solid and some are
    work-in-progress; this page says which is which.

## The labels

| icon | label | means |
|---|---|---|
| ✅ | **Consistency-checked** | The computation does what the framework says, with controls/nulls that behave and results that reproduce. A statement about the *internal consistency of the model*, not about biology. |
| 🟡 | **Provisional** | The result stands but has **not yet been independently audited** under the scrutiny campaign, or is an exploratory proof-of-concept. Read with appropriate caution. |
| 🟠 | **Open problem** | A real confound or limitation has been identified; the mechanism or claim is under **active revision**. |
| ⛔ | **Withdrawn** | A claim **retracted after review**. Kept on its page, with the reasons, as provenance. |

A ✅ means "we checked the instrument, not just the page." Of the experiments put
through that check so far, **three did not survive it as stated** — entrainment (a
servo-lag brake, not entrainment), the field-scale control (a decoder-dimensionality
artifact), and the self-model (recoverable only under exploratory drive, and used by
nothing). The self-model had even been marked ✅ on an earlier, shallower read; the
audit reversed it. That is the point of the process, and the reason most pages stay
🟡 until they earn the ✅ rather than being assumed correct.

## The ledger

### §1 · The modular unit
| status | experiment | note |
|---|---|---|
| ✅ | [C0 — it moves](experiments/c0_crawler.md) | Non-inertial locomotion; reproduces (net displacement PASS), re-run repeatedly as a backward-compat anchor. |
| 🟡 | [S0 — locomotion is a network effect](experiments/sweep_c0_coupling.md) | Coupling sweep; not yet audited. |
| 🟠 | [S0b — proprioceptive entrainment](experiments/entrainment.md) | Three review rounds: two withdrawn claims; topology now correct + CI-guarded, but the payoff (body shapes the rhythm) needs an articulation-load model. Fix plan pre-committed on the page. |
| 🟡 | [Antagonistic benefits](experiments/sweep_pred3_antagonistic.md) | Not yet audited. |
| 🟡 | [R1 — tonic-load coupling](experiments/sweep_r1_tonic_load.md) | Reclassified as an **analytic** consistency check (a consequence of the alert-energy ODE), not empirical evidence. |
| 🟡 | [R2 — resumption latency](experiments/sweep_r2_resumption.md) | Semi-analytic (direction built in); not fully audited. |

### §3 · The self-model
!!! warning "Audited — the earlier ✅ was premature (see [babble vs behave](experiments/self_model_babble_behave.md))"
    A review pass found the self-model read-out recovers the body only under
    **exploratory (babbling)** drive; under coordinated locomotion it collapses toward
    chance (reads command phase, not body topology). It is also never stored or used,
    and its metric has a **2/n chance floor** (uninformative for 3-segment bodies).
    Recovery in the babble regime is a genuine consistency check, so these are 🟠 (real
    limitation, under revision), not ⛔ — and a testable prediction follows: complex
    multi-subsystem bodies should keep G recoverable *while* behaving.

| status | experiment | note |
|---|---|---|
| 🟠 | [Chain — the read-out](experiments/self_model_topology.md) | Recovers topology from **exploratory** drive (neighbour-acc 1.00, clean hop-decay, working rigid/frozen foils); collapses to chance under the beam. Existence proof in the babble regime; behave-recovery, storage, and use are open. |
| 🟠 | [Babble vs behave](experiments/self_model_babble_behave.md) | The audit itself: babble neighbour-acc 1.00 vs behave 0.286 (chance 0.25), hop-profile inverts. Records the limitation, the interpretation (babbling as a wake-up state; simple-body artifact), and the complex-body prediction. |
| 🟡 | [Complex body — subsystems restore it](experiments/self_model_complex_body.md) | **Prediction confirmed:** a few independently-*tuned* subsystems (peak K≈3) restore neighbour-acc to ~0.86 while behaving (inverted-U from the 0.23 collapse); a same-rhythm control stays low/erratic, so the cause is drive *incoherence*, not partition. Shows the collapse is a simple-single-chain artifact. Fresh; drive-on-fixed-chain (not real morphology); awaiting independent check. |
| 🟡 | [Branched body (tree)](experiments/branched_self_model.md) | Recovers the tree + branch point under babble; arm-swap residual 0.10 vs 0.32. Inherits the babble-only / storage / use / metric-floor open questions. |
| 🟡 | [Sheet & tube (2-D)](experiments/lattice_self_model.md) | Endpoint-recovery 1.00 / 0.99 / 0.97 under babble; same open questions. *Recommended: wiring-shuffle / rigid null.* |
| 🟡 | [Nested lattice (scale-invariance)](experiments/nested_lattice_self_model.md) | Coarse/mid 1.00; fine 0.88; same open questions. |

### §4 · The world-model & self / world / other
| status | experiment | note |
|---|---|---|
| 🟡 | [Q2 — the reafference cut](experiments/q2_reafference.md) | Not yet audited. |
| 🟡 | [W3 — the cut in the self-graph](experiments/reafference_cut_self_graph.md) | Not yet audited. |
| 🟡 | [W1 — a world feature in the self-graph](experiments/world_in_self_graph.md) | Not yet audited. |
| 🟡 | [W2 — world-geometry in the self-frame](experiments/world_geometry_self_frame.md) | Not yet audited. |
| 🟡 | [Q1 — modulation builds the world model](experiments/sweep_q1_modulation.md) | Not yet audited; carries the resolution claim (with Q1b). |
| 🟡 | [S1 — more body ≠ more world](experiments/sweep_geometry_worldmodel.md) | The flat null stands as data, but its **interpretation is hedged**: it no longer supports the resolution principle (see the withdrawn control below). Decodability ≠ world-model. |
| ⛔ | [S1 field-scale control](experiments/sweep_geometry_worldmodel_fieldscale.md) | **Withdrawn.** kNN-skill slope vs `n_seg` is confounded (decoder dimensionality; broad-masking flips a ridge slope positive on an unmasked field; trajectory noise). Cannot separate resolution principle from field-geometry artifact. |
| 🟡 | [Q1b — resolution = CAZ density](experiments/sweep_q1b_resolution.md) | Not yet audited; where the resolution claim actually rests. |
| 🟡 | [Resolution exponent](experiments/sweep_resolution_exponents.md) | Not yet audited. |
| 🟡 | [R5 — dual-signal residual](experiments/sweep_r5_dual_signal.md) | Not yet audited. |
| 🟡 | [R4 — adaptation dynamics](experiments/sweep_r4_adaptation.md) | Preregistered; not yet audited. |

### §5–§7 · Object-directedness, multimodal, taxonomy
| status | experiment | note |
|---|---|---|
| 🟡 | [C1 — halt-on-contact](experiments/c1_touch.md) | Not yet audited. |
| 🟡 | [E1 — manipulator objecthood](experiments/p4_manipulator_objecthood.md) | Not yet audited. |
| 🟡 | [E3 — haltability → aboutness](experiments/p6_haltability_aboutness.md) | Not yet audited. |
| 🟡 | [Haltability signatures](experiments/sweep_pred1_haltability.md) | Prediction; not yet audited. |
| 🟡 | [E2 — self / field / object](experiments/p5_self_field_object.md) | Not yet audited. |
| 🟡 | [P3 — cross-modal discrimination](experiments/p3_crossmodal_discrimination.md) | Exploratory; touch-only class count is calibration-sensitive (flagged on the page). |
| 🟡 | [Canvas regions](experiments/canvas_regions.md) | Not yet audited. |
| 🟡 | [Integrator & snapshot](experiments/integrator_snapshot.md) | Not yet audited. |
| 🟡 | [Haltability (the pivot)](experiments/haltability.md) | Not yet audited. |
| 🟡 | [E4 — world model scales with the network](experiments/p7_scaling_network.md) | Not yet audited. |
| 🟡 | [E4b — objecthood transition](experiments/p8_objecthood_transition.md) | Not yet audited. |
| 🟡 | [Zonal dissociations](experiments/sweep_pred2_zonal.md) | Prediction; not yet audited. |

### Provenance / exploratory studies
| status | experiment | note |
|---|---|---|
| 🟡 | [All P0–P2 studies](reproducibility.md) | The bench's **first exploratory series**, kept as provenance and explicitly read as proofs-of-concept (several single-seed, some metrics saturate). Not to be read as clean ablations. |

## How an experiment earns a ✅

It goes through the same pass the review campaign applied to entrainment and the
field-scale control: read the term/metric in code (not the page), find the artifact a
skeptic would look for, and confirm the result survives a working null. When one does,
its row moves from 🟡 to ✅ (or to 🟠/⛔ if it doesn't). This ledger is the honest
running score of that process.
