# Release notes / change notebook

A running record of substantive changes to the bench and its claims, so we can
issue release notes and keep the paper and bench in step. Newest first. Paper
changes are logged here as **[PAPER v3 — pending]** and applied only to a future
paper v3 (the arXiv/PsyArXiv v2 is frozen).

---

## 2026-07 — Self-model audited: recoverable from *exploratory* movement, not behaviour

A review pass checked the §3 self-model the same way (in code + simulation). The
read-out (`transfer`/`coupling`) is scored under an **independent OU torque per zone**
— exploratory/"babbling" drive. Under the **beam wave** (coordinated locomotion) it
collapses: on an 8-segment chain neighbour-accuracy falls from 1.00 to **0.286**
(chance = 2/8 = 0.25) and the hop-profile inverts — one oscillator driving all zones
makes `|corr(efference, motion)|` track command *phase*, not mechanical distance.
Independently reproduced.

- **New experiment `self_model_babble_behave`** records the contrast (both hop
  profiles + both transfer matrices) rather than burying it — a real finding.
- **Wording corrected:** "recovered from movement" → "recovered from **exploratory**
  movement" (`self_model.py` docstring, topology page).
- **Metric floor flagged:** chance neighbour-accuracy is **2/n**; for the 3-segment
  crawler (n = 2) chance is **1.00** — the metric cannot fail, so 3-segment self-model
  numbers are uninformative.
- **Ledger:** §3 self-model ✅ → 🟠/🟡 (the earlier ✅ was a shallower read; the audit
  reversed it — that is the process working). Three audited claims have now not
  survived as stated (entrainment, field-scale, self-model).
- **Interpretation recorded (GN), kept distinct from the result:** babbling may be
  continuous (a wake-up / calibration state) so G stays available while behaving; the
  dissociation is a *simple-body* artifact — complex multi-subsystem bodies can babble
  in one part while behaving in another, giving the **testable prediction** that
  G-recovery-under-behaviour scales with independent-subsystem count; and *G is for
  action* (Glenberg) — the model must be stored and used. Self/world/object are taken
  as co-evolving; the document's ordering is expository, not ontological.

### Complex-body test — GN's prediction confirmed

`self_model_complex_body.py`: hold morphology fixed (8-seg chain), partition the zones
into `K` independent subsystems each with its own beam, sweep `K`. Distinct-frequency
subsystems trace an **inverted-U** — neighbour-accuracy climbs from the single-beam
collapse (0.23) to a peak of **0.86 at K=3**, then falls back toward chance as
subsystems shrink to single low-SNR oscillators. A **same-frequency control stays
low/erratic** (mean ≈ 0.28, no systematic recovery), so the cause is drive
**incoherence** (distinct rhythms), not partition per se. Confirms the collapse is a *simple-single-chain
artifact*, as predicted: complex, multi-rhythm bodies keep the self-model legible during
behaviour, with an optimal intermediate number of subsystems. (Drive-on-fixed-chain, to
isolate the mechanism; a real branched-morphology version is the follow-up.)

### Next build (proposed)
- **babble → behave → perturb** cycle: babble to learn G and freeze it; behave using
  the stored G to address zones; perturb a joint; measure whether behaviour degrades
  and a re-babble restores it. Closes model → use and tests "the graph is the computer."
- **Real branched-morphology** version of the complex-body test (independent limbs /
  layered subsystems supplying the incoherence, rather than a partitioned chain).

---

## 2026-07 — S1 field-scale control WITHDRAWN (decoder + field-design confounds)

The same review turned to the S1 field-scale control (`sweep_geometry_worldmodel_fieldscale`),
which had claimed the S1 flat-null "is not a field-geometry artifact → resolution
principle survives." Checking the harness in code + simulation, that verdict does not
hold. **Withdrawn.** The decoder itself is clean (train-only standardization, temporal
60/40 split, sound shuffle control), but the *order parameter* — the slope of kNN
decoding skill vs `n_seg` — is confounded three ways:

- **Decoder dimensionality.** kNN degrades with state dimension (`2·n_seg` channels),
  so it produces a **negative slope even for `broad_only`** — a field that carries *no*
  independent per-segment information by construction. The negative slope was
  manufactured by the decoder, not the world. A dimension-robust **ridge** readout puts
  `broad_only` flat. (New `ridge_skill` in `metrics.py`.)
- **Field masking.** The "body-scale" field kept the three broad S1 sources "for
  decodability," but they dominate the signal and are `n_seg`-flat, **swamping** the
  fine body-scale component whose `n_seg`-dependence was the whole test. Weaken/remove
  them (`weakbroad+fine`, `fine_only`) and the ridge slope goes **positive** — a
  genuinely body-scale field shows *more body → more decodable world*.
- **Trajectory noise.** Skill is strongly trajectory-dependent: the published curves
  are non-monotone (a dip at `n_seg=5` across all fields) with ±0.2–0.6 seed variance,
  so a slope at this budget cannot resolve the question anyway.

Net: the control is **inconclusive**, not confirmatory. The experiment and figure are
rewritten to run both decoders + a dimensionality control + an unmasked field, and to
report the withdrawal. The **S1 page no longer cites its null as evidence for the
resolution principle** — that claim is carried only by the *modulation* experiments
(Q1/Q1b). A clean redesign (dimension-robust decoder, decodable-and-unmasked
body-scale field, trajectory control, many seeds) is future work.

### [PAPER v3 — pending]
- Remove any v3 use of the field-scale control as clearing the S1 field-geometry
  confound. S1's flat-null is consistent with *either* the resolution principle or a
  field-geometry artifact; do not adjudicate with this control. (See item 4/2.)

---

## 2026-07 — Proprioceptive entrainment: closing the body → rhythm loop

Second point from the same scientific-accuracy review: in the base bench the
messaging beam is causally **sealed off** from the body — `MessagingBeam.command()`
advanced its phase from `ω` + neighbour coupling only, so a wall, a load, or a gated
halt never reached the rhythm. It was a controller commanding a body, not a
body-and-controller in mutual entrainment — and that gap sits exactly where the SMN
thesis ("the body is the computer") is strongest.

- **Mechanism (opt-in, backward-compatible).** `MessagingBeam` gained an `entrain`
  gain (default `0.0`); `command()` now accepts the sensed `theta`, `theta_dot` and,
  when `entrain > 0`, pulls each oscillator toward the phase its own segment is
  actually bent to (`dphi += entrain·sin(ψ_body − φ)`, the edge-cell / stretch-receptor
  loop). With `entrain = 0` or no `theta`, the beam is bit-for-bit the old open-loop
  generator, so **all existing experiments reproduce exactly**.
- **New experiment `entrainment.py` / `entrainment.md`** (nav §1, after S0). During a
  2 s gated halt the open-loop beam winds the full `ωT = 1.80` cycles the body never
  executed; the closed loop (`ε=6`) is arrested to **0.75** cycles and plateaus inside
  the halt — the body now perturbs the rhythm. Strengthens S0: the network includes
  the body.
- **Honest negative reported, not hidden.** Steady-state undulation frequency does
  **not** adapt to medium drag in either loop. In this bench the drag resists
  translation, not joint articulation, and the stiff servo imposes the bend timing —
  so the *C. elegans* water↔agar frequency law needs a **joint-loading model**
  (declared next step), not just the feedback path.

### Correction (third review round) — the term was self-entrainment, not entrainment

A third review checked the *corrected* term's dynamics and found it still wasn't
entrainment. Each oscillator was entrained to its **own** joint — which is just the
beam's own servo-delayed output — so `sin(ψ−φ) = sin(−δ)` (δ = servo lag) was a
**constant brake**. The round-2 headline, "closing the loop drags the frequency to
arrest," was therefore pure frequency **detuning**, carrying no information about the
body's load or the medium. **Withdrawn.**

- **Fix — inter-segmental topology.** `MessagingBeam` gained `entrain_mode`
  (`"inter"` default, `"self"` ablation). The correct form entrains each oscillator to
  its **anterior neighbour's** realized phase (offset by the head→tail lag), so the
  wave propagates *through the body* — faithful to Wen et al. 2012. The head is the
  free pacemaker. Both forms vanish under perfect tracking.
- **Regression test.** `tests/test_entrainment.py` (pure-numpy, no MuJoCo) asserts the
  invariant a docs page once violated: *under perfect tracking the pull is identically
  zero.* This would have caught the round-1 `cos(2φ)` bug. A CI workflow is provided at
  `.github/workflows/tests.yml` (to be activated with a workflow-scoped push).
- **The experiment is downgraded to "mechanism + open problem."** On a 5-segment body:
  the `"self"` ablation runs away toward arrest (detuning); inter-segmental is stable.
  But free-run frequency is **flat vs medium drag under both topologies** — closing the
  loop does not make the rhythm track the medium. That needs a **joint-loading model**
  (drag torque on the bend / load-limited actuator); the drag here loads translation,
  not articulation. A first crude attempt was numerically unstable and is not shipped.
- **Net honesty ledger:** two withdrawn claims (halt-arrest; freq-to-arrest), one
  correct mechanism, one CI invariant, and a clearly scoped open problem. **S0 is
  NOT strengthened by a bench result yet** — only the mechanism is in place.

### Correction (second review round) — two bugs in the first entrainment term

A follow-up scientific-accuracy review checked the term itself, not just the page,
and found two defects. Both are now fixed; the experiment and figure are rebuilt.

- **Swapped `arctan2` arguments.** `arctan2(thd/ω, th)` yields `psi = π/2 − φ`, so the
  pull was `cos(2φ)` — a spurious `2ω` drive that does **not** vanish under perfect
  tracking (independently verified: the pull equalled `cos 2φ` to ~1e-16). A
  well-formed stretch term must be zero when the body does exactly what it was told.
  Fixed to `arctan2(th, thd/ω)`.
- **No magnitude gate.** The pull fired at full strength even when the body was still,
  where `arctan2(0,0)=0` drags the phase to a fixed `0`. The first version's headline
  **"arrest during a gated halt" was that edge case**, not the mechanism. Fixed with an
  `r/(r+ε)` gate (a still body carries no phase — a silent stretch receptor).
- **What changed in the result.** With both fixed, the gated-halt arrest **disappears**
  (a slack body correctly exerts no pull) and a pinned obstruction does not cleanly
  arrest either — so those framings are **withdrawn**. The corrected, robust result:
  closing the loop couples the oscillator to the actually-lagging PD body, which
  **drags the free-run frequency from 0.89 Hz down to arrest** as the gain rises
  (panel B). Smaller than first claimed, and true. The panel-C frequency-vs-drag
  negative is unchanged.

### [PAPER v3 — pending]
- S0 ("locomotion is a network effect") can be stated more strongly once entrainment
  is on: with the loop closed the *body* is part of the network, not only the coupled
  software oscillators. Use the **corrected** demonstration — closing the loop drags
  the rhythm toward the body's actual (lagging) motion — **not** the withdrawn arrest
  figure; keep the frequency-adaptation limitation explicit (it needs joint loading).

---

## 2026-07 — Honesty pass in response to an external scientific-accuracy review

An independent reviewer read the docs and the source and raised well-founded
points about where the bench's language outran its quantities. We agree, and the
changes below tighten the bench's claims to match what the code actually
establishes. None change a result; they reclassify and relabel.

### Framing
- **Landing page now states the bench's epistemic status up front:** it is an
  *existence proof that the architecture is buildable and coherent*, not evidence
  that this is how biology works. The cognitive vocabulary (self-model, aboutness,
  objecthood) names operational quantities (a correlation-recovered graph, a dwell
  time, a decoding score), and the gap to the full concept is flagged.

### Tier 2 — the resistive medium (accuracy of the "aquatic" label)
- The anisotropic drag ratio is `c_trans/c_long = 14`. Slender-body resistive-force
  theory caps the perpendicular/parallel ratio near **2** in Stokes flow, so 14 is
  **not** a low-Reynolds fluid — it is a **resistive/frictional substrate** (snake
  on ground). Relabelled "aquatic / low-Reynolds / swimmer" → **anisotropic
  resistive drag**; added a note that the ratio is a strong-anisotropy modelling
  choice exceeding ideal Stokes RFT. The locomotion mechanism is unchanged and
  correct; only the label overreached.

### Tier 3.1 — analytic vs contingent results (the R1 register)
- **R1 (tonic-load coupling) is analytically guaranteed by the alert-energy ODE**
  (`a_partner = a0 + β·E_R`, `E_R* = ρ·τ_E·F` ⇒ slope `βρτ_E`), so its "confirmation"
  is a **consistency check of the integrator**, not evidence about opponent
  physiology. Reclassified in the ledger with an explicit epistemic-category tag
  (*analytic/verification* vs *contingent-empirical*); "the coupling *emerges*" →
  "the integrator reproduces the predicted closed-form steady state."
- **R2 (resumption latency)** is only *partly* built in: the monotone direction
  (advantage grows with `E_R`) follows from boosting the drive, but the latency
  magnitude is measured through the physics. Marked accordingly (semi-contingent).

### Tier 3.2 — decoding is not a model (the world-model / S1 experiment)
- The "world-model" result is a **kNN decoder recovering position from instantaneous
  field readings** — decodability, not a persistent, composable model. Reframed as
  *world-information decodable in the self-frame*, with the explicit caveat that
  information present in a signal is not the agent holding a model; a genuine
  world-*model* is deferred to Phase-II / M2.
- **New confound flagged and tested (batch 2):** the flat-in-`n_seg` null ("more
  body ≠ more world") may be **field geometry**, not a resolution principle — with
  `σ ≈ 0.8–0.9 m ≫ 0.2 m` body, every segment reads nearly the same value, so extra
  segments add ~no independent information regardless of the theory. See the
  body-scale-field control experiment below.

### Tier 3.3 — self-administered pre-registration
- "Pre-registered" softened to **"pre-committed / pre-specified in the repo
  (self-administered, not a third-party registry)"** across the docs. Genuine OSF
  Registrations flagged as the right move for Phase-II.

### Reproducibility
- **P3 docs↔code discrepancy** (`formal_review.md`: docs claim 2 touch-only classes,
  code yields 3) — a **re-run of the current code reproduces 2** (matching the docs);
  the earlier 3 was not reproduced, so the exact count is **calibration-sensitive**
  (touch noise/thresholds), now flagged on the P3 page. The qualitative claim (more
  whiskers ≠ a new individuable modality) is robust to the count.

### [PAPER v3 — pending]
- R1 presented as a bench-confirmed *register* should be marked an
  analytic/consistency result, not empirical evidence for the mechanism.
- The paper's world-model framing should carry the decoding-vs-model caveat the
  bench now states (the v2 text already scopes "world-model in the self-frame";
  tighten the bench-result language to match).

---

## Batch 2 — field-geometry control for the resolution null (new experiment)

`sweep_geometry_worldmodel_fieldscale.py` + `sweep_geometry_worldmodel_fieldscale.md`
(nav under §4). Repeats the S1 world-model sweep under a **body-scale field** to test
whether the flat-in-`n_seg` null is the SMN resolution principle or a field-geometry
artifact.

- **The control corrected itself first.** A naive body-scale field (a *periodic*
  checkerboard) aliased position and read at ~shuffle regardless of `n_seg` — a
  degenerate field, not a result. Fixed to a **multi-scale field**: the three broad
  S1 sources (global decodability) + an aperiodic scatter of narrow Gaussians
  (body-scale texture). The fixed field is decodable (skill ≈ 0.5 at `n_seg=3`).
- **Outcome (8 seeds, 75 s):** under the decodable body-scale field, skill still does
  **not** rise with segment count (slope −0.029, indistinguishable from the
  large-`sigma` −0.023). So the S1 flat-null is **not** the field-geometry artifact
  — it survives when extra segments carry independent information. S1 may now be
  cited as *consistent with* the resolution principle rather than merely undecided.
- **Caveat:** wide variance (±0.12–0.36); a higher-seed run would tighten the slope.
  The qualitative result held across the 4-seed and 8-seed runs.

Net: the reviewer's confound was a legitimate worry; we built the control; the
confound does **not** explain the null. A good outcome — reached by testing, not by
assertion.
