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

A ✅ means "we checked the instrument, not just the page." Two of the first three
experiments put through that check (entrainment, the field-scale control) did **not**
survive it — which is why most pages are honestly marked 🟡 until they get the same
pass, rather than assumed correct.

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
| status | experiment | note |
|---|---|---|
| ✅ | [Chain — the read-out](experiments/self_model_topology.md) | Local (C3) neighbour-accuracy 1.00 ± 0.00 with working rigid/frozen foils that fail as predicted; the cross-correlation read-out is not subject to the decoder confounds that felled others. Read as an *existence proof* (buildable, homunculus-free), not a biological discovery. |
| ✅ | [Branched body (tree)](experiments/branched_self_model.md) | Same function recovers the tree + branch point; arm-swap residual discriminates symmetric (0.10) vs asymmetric (0.32). *Recommended strengthening: a wiring-shuffle null.* |
| ✅ | [Sheet & tube (2-D)](experiments/lattice_self_model.md) | Endpoint-recovery 1.00 / 0.99 / 0.97, tight variance. *Recommended: a wiring-shuffle / rigid null of its own.* |
| ✅ | [Nested lattice (scale-invariance)](experiments/nested_lattice_self_model.md) | Coarse/mid 1.00; fine 0.88 with the inter-block limitation honestly reported. *Recommended: the same null.* |

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
