# Release notes / change notebook

A running record of substantive changes to the bench and its claims, so we can
issue release notes and keep the paper and bench in step. Newest first. Paper
changes are logged here as **[PAPER v3 — pending]** and applied only to a future
paper v3 (the arXiv/PsyArXiv v2 is frozen).

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
  **not** adapt to medium drag in either loop (flat in panel C; the closed loop only
  lowers the baseline). In this bench the drag resists translation, not joint
  articulation, and the stiff servo imposes the bend timing — so the *C. elegans*
  water↔agar frequency law needs a **joint-loading model** (declared next step), not
  just the feedback path.

### [PAPER v3 — pending]
- S0 ("locomotion is a network effect") can be stated more strongly once entrainment
  is on: with the loop closed the *body* is part of the network, not only the coupled
  software oscillators. Add the arrest result as the concrete demonstration; keep the
  frequency-adaptation limitation explicit (it needs joint loading).

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
