# SMN presentation plan — Bengaluru (ICTS / NCBS / TIFR) seminars

*Working plan for the systematic presentation of the SMN framework + smn-lab to a
complex-systems / physics–biology / computational-neuroscience audience. Not part
of the published docs nav.*

**Audience.** Professional scientists comfortable with mathematical formalisms and
graphs as their native representational modality. They will attack rigor, not
narrative. The pitch must be: *one formal spine, rendered three ways that cannot
disagree.*

**Channel plan (user's).** Open with the **revised preprint** (formalisms in the
main body, not an appendix), then hand off to the **readthedocs** site as the
living lab where research is documented going forward; short focused papers then
report sets of experiments.

---

## ⭐ The research-programme reframe (2026-07, governs everything below)

The site is a **two-phase argument**, not a catalogue of every experiment we ran.
*(NB: "Phase I/II" here = the research programme; the "Phase 0–4" further down =
my doc-build execution phases. Different things.)*

- **The organism** — the minimal moving body (C0, S0, antagonistic-benefits).
- **Phase I — grounding self, world & object in physics** (current focus; the pitch
  to biophysicists = cognitive tokens get specific meaning only when a physical
  construction fixes them):
  - **① Self** — the self-model by CAZ modulation. Key claim = **topology-invariance**:
    the *same* framework function (`transfer`/`coupling`) builds the self-model for a
    chain, a tree, and **linked chains forming a tube**, byte-identical injected code.
    → **new experiment to build: the tube self-model** (chain + branched exist).
  - **② World** — world-model in the self-frame from *modulated* transducers
    (reafference Q2/W3, W1, W2, Q1).
  - **③ Object/aboutness** — resistance to modulation (C1 + promoted E1, E3;
    haltability-prediction folded in).
- **Phase I → II pivot** — Phase I's own null result: adding transducers in a line
  does NOT enrich the world-model (S1, Q1b/resolution principle).
- **Phase II — evo-devo path** (pointed to): polarized → tubular → segmented →
  bilateral → appendicular = **nested CAZ modulation**; richer world-models need
  architecture, not more identical zones (E4, E4b, zonal-dissociation prediction).
- **Provenance** — the P-series + E2, kept as proofs-of-concept.

Predictions folded into the phase each tests (haltability→I·③, antagonistic→organism,
zonal→II). **Landing pages `phase1.md` + `phase2.md` carry the argument.** The
preprint revision must be scoped to Phase I, pointing to Phase II.

Status: nav + landing pages + index reframed and building clean.
**Sheets & tubes** (Phase I·① + Phase II tubular): design written
(`design/sheets-and-tubes.md`) — muscle=chain, sheet=2 chains, tube=≥3 chains closed
laterally; longitudinal links=longitudinal muscle, lateral tendons=circular muscle;
DOF/activation → crawl/peristalsis/roll (anatomy→behavior, no central controller).
Settled with GN: CAZ = one muscle-tendon unit (variable DOF); two archetypes
(skeletal flexor/extensor pair vs **hydrostatic linked-linear-actuators** — the
latter new to the grammar); segments = sensor scaffolding; C. elegans (long-only) vs
earthworm (long+circular); route = **spring-lattice now, FLEX as labelled upgrade**;
**self-model recovery first, behaviors after**.

**T1+T2 DONE (productionized):** `smn_lab/lattice.py` (`build_lattice_xml` +
`lattice_edges` + `lattice_positions`; segments overdamped point masses, links =
spring-tendon CAZ, real ring cross-section for the tube); `smn_lab/metrics.py`
`endpoint_recovery`; `experiments/lattice_self_model.py` (drive links, `coupling`
read-out, figure); Phase I·① doc page `lattice_self_model.md` injecting the canonical
`coupling`, wired into nav + phase1.md. Result reproduced: **chain 1.00 / sheet 0.99
/ tube 0.97**; unrolled-cylinder figure with dashed wrap edges. Strict build clean.
The hydrostatic-CAZ grammar update is **deferred by GN** (not needed to validate the
preprint argument).

**SCALE-INVARIANCE DONE (2026-07-17):** two-level nested lattice — `smn_lab/lattice.py`
`nested_lattice_spec` + `build_nested_lattice_xml`; `experiments/nested_lattice_self_model.py`
recovers FINE (16 segments, 0.91) + COARSE (4 blocks, 1.00) from one run with the SAME
`coupling` (coarse via block-averaging = renormalization). Page under Phase I·① with the
**n-level recursive formalization** (Φ commutes with the coarse-graining operator; self-model
= fixed point of the RG flow in form). Finding: fine misses = the inter-block links → layering
is *necessary*. Framing: morphological computing + haltability-needs-a-pivot-layer. See
[[project_smn_scale_recursive_caz]] and `design/physics-at-every-layer.md`.

**HALTABILITY DONE (2026-07-17):** `experiments/haltability.py` + doc `haltability.md`
(under Phase II). A halt = clamp an active node to a canvas home; a stable, addressable
hold needs a stable reference. **canvas ON: hold-spread 0.0055, all 6 addresses correct
(the counting substrate), rest keeps moving (selective/dexterity); canvas OFF: drifts 8×,
75% addressed.** Establishes: haltability needs a pivot layer (why layering came first);
addressable holds = counting substrate; selective hold = dexterity primitive; same topology
≠ same haltability (chimp vs human); engineerable for cognitive robotics.

**E3 CLEANED + REFRAMED (2026-07-17):** `p6_haltability_aboutness` promoted to spine
standard. Now **self-model FIRST** (framework `coupling` on the 2 limbs in free space →
off-diagonal 0.09 = two decoupled zones = self-referred frame), **then object-directedness
in that frame** via the haltable action *pattern* (smn_press: recurrent/recognisable, not
a one-time halt): persistent 1.51s (recoverable), returnable 5× (recurrent), side-specific
0.00s (differentiated); CPG foil 0.26s. Reframed per GN's corrections: haltability=capacity
(necessary), the *pattern*=sufficient; the object breaks bilateral symmetry (individuates
self's L zone + object together, ties to branched asymmetry); counting/naming explicitly
deferred (particulars + ratchet + emancipation → Phase II/M2). Formalism block injects
`self_model.py:coupling` + the `selfmodel`/`pattern` blocks. Also corrected the overclaim in
`haltability.md` + captured emancipation/ratchet/action-pattern-hierarchy theory in
`design/physics-at-every-layer.md` §7.

**FRAMEWORK DE-RELICED (2026-07-17):** full line-by-line audit of the "The framework"
nav section before the preprint. Rewrote `concepts.md` (dropped the "balance beam"
framing; now CAZ/opponency/elastic-substrate/model-vs-measurement/self→world→object)
and `assumptions.md` (old planar-mouse/whisker/RK4-5ms/P-series content → current
crawler/lattice/manipulator bodies, dt=2ms, overdamped, contacts-off, spine table +
clearly-labeled P-series *provenance* sub-table). Fixed `diagram-grammar.md` (the
"nesting" wording now distinguishes flexibility-nesting vs scale-recursion; added a
deferred-hydrostatic-CAZ note), `test-plan.md` (Q3 now reflects E3: directedness shown,
selection deferred), `lab-interface.md` (honest note: app exercises P3; self/world-card
is current). `datasets.md`, `formalism-and-code.md`, `self-model-and-measurement.md` audited clean.
Then: **"Lesson 1" → "The Construction of Experience"** (only one lesson; dropped the
numbering/"lesson" framing; file `lesson1.md`→`construction-of-experience.md`, ~18 refs
updated). **Test-plan reframed** from "pre-registered C-series" → "Pre-registration &
status": reorganized around self→world→object, **added the self-model / scale-invariance /
haltability pre-reg entries** (topology- & scale-invariance ✅, haltability ✅), kept the 5
questions + 3 predictions re-labeled by phase with outcomes. **"C-series" reframed →
"progression" repo-wide** (the C/P-series track split predates the two-phase spine).
Strict build clean; relic-term sweep clean.

**NEXT (per GN):** revise the preprint scoped to Phase I, with smn-lab providing detailed
support to the narration. Remaining bench: T3 behaviors, FLEX rung, clean E1.

## The reframe: one spine, three renderings

| Rendering | Audience touchpoint | Source of truth |
|---|---|---|
| Revised preprint (formalism in main body) | first contact / citable | the formal spine |
| readthedocs (equation + injected code + result, per condition) | the living lab they evaluate & revisit | spine + `smn_lab/*.py` (injected) |
| live MuJoCo demo (sliders on parameters named in the spine) | the seminar room | `smn_lab/*.py` (same code) |

If the three cannot disagree, that guarantee **is** the pitch. Do the math **once**
as a single canonical source; the paper and the docs both derive from it.

---

## Critical findings (state as of 2026-07)

1. **No mathematics renders on the pages.** No `arithmatex`/MathJax; the "What's
   computed" sections are prose. For this audience prose-algorithm is a downgrade
   and contradicts the stated goal. → Phase 1.
2. **The "same functions we use" commitment is a manual promise, not a mechanism.**
   Page math and `smn_lab/*.py` can silently drift; the first discovered mismatch
   destroys trust in all of it. → mechanize with code-from-source injection. Phase 1.
3. **Elasticity is already load-bearing in the code but absent from the preprint.**
   `self_model_topology.py` varies `joint_stiffness` as the `elastic / rigid /
   frozen` foil; the elastic chain's transmission gain `G[i,j]` decaying with
   hop-distance is what makes the self-model recoverable. The ablation already
   exists. The preprint formalism lags. → Phase 0 = extract + formalize, not invent.
4. **The two-track nav is a liability.** A clean spine (C0/C1/S0/S1/Q1/Q2/preds +
   self/world W1–W3) sits co-equal with a 20+ page P0–E4b "trial" series. Sprawl
   lowers perceived signal. → Phase 2 demotes provenance to a labeled archive.
5. **The progressive series isn't explicit.** The nav is a catalog, not a path.
   The minimal-organism ladder (1 seg = object, 2 = self/world, 3 = aboutness; then
   +gravity/contact, +elasticity, +modulation) should be the site backbone. → Phase 2.
6. **Live-demo ↔ page binding under-specified.** The demo lands only if each page
   names the exact parameter, its symbol, and its function argument (symbol ↔
   code-arg ↔ live-control). `lab-interface.md` is 44 lines. → Phase 3.
7. **Paper/docs math will diverge if written twice.** Single canonical source. → Phase 0/4.

---

## Phased execution plan

### Phase 0 — Formalism spine + elastic substrate *(theory, do first)*
- [ ] Write the substrate / self-model / world-model formalism as one canonical
      source, with the exact symbols reused everywhere. Include the **elastic term**:
      the transmission gain `G[i,j]` (co-movement attenuating with hop-distance),
      parameterized by joint stiffness `k` (`joint_stiffness` in `crawler.py`).
- [ ] Confirm the code path: `self_model_topology.py` conditions
      `elastic (k=0.6) / rigid (k=80) / frozen (k=0.6, no drive)`.
- [ ] Promote the existing elasticity foil to a **flagship** result: off (rigid) →
      self-model fails to form; on (elastic) → chain order recovered.

### Phase 1 — Rendering infrastructure — ✅ DONE
- [x] `mkdocs.yml`: `pymdownx.arithmatex` (generic) + MathJax loader (`docs/javascripts/mathjax.js`).
- [x] `mkdocs.yml`: `pymdownx.snippets` (`check_paths: true`) — function bodies **read
      from `smn_lab/*.py` at build time** via named sections, not pasted.
- [x] Drift-safety **verified**: renaming a source anchor fails the strict build
      (`SnippetMissingError`); restoring passes.
- [x] Reference page `docs/formalism-and-code.md` (equation → injected `coupling()`
      → the `k` elasticity parameter). Approved as the template.

### Phase 2 — Restructure nav into the progressive spine — ✅ DONE
- [x] Merged the old "Experiments" + "Self / world construction" tracks into one
      ordered **7-rung progression** (minimal organism → gravity/contact →
      self-model+elasticity → reafference cut → world-model → modulation/resolution
      → preprint predictions).
- [x] Added a **Frontier — aboutness & objecthood** tier (E-series manipulator work):
      honors the ladder's final rung without promoting trial-grade pages into the
      clean spine. *[judgment call — moveable in seconds if you'd rather it sit in
      Provenance.]*
- [x] Demoted the P-series to **Provenance / exploratory studies**; renamed
      "About the bench" → "The framework"; fixed the stale `#the-two-experiment-series`
      anchor; `index.md` + `reproducibility.md` prose now match the 3-tier nav.
### Phase 2a — Consolidate read-out/metrics into the framework — ✅ DONE
Triggered by the "why are these functions in experiment scripts, not the model?"
audit. Decisions: **C3-honest** (the read-out is the agent's local cognition) +
**full consolidation**.
- [x] `smn_lab/self_model.py` (rewritten): canonical **local** read-out —
      `local_read` (one zone, purely local) → `read_all` (stacked, not a central
      reader) → `coupling`/`transfer` (signed / |·|-symmetrized specializations of
      one Xcorr primitive) → `local_edge`/`recover_edges` (graph = union of local
      edges). Docstrings state the C3 locality argument.
- [x] `smn_lab/metrics.py` (new): **experimenter-side** scoring, labeled — needs the
      answer key or the whole matrix: `seriation_order` (Fiedler), `order_accuracy`,
      `neighbour_accuracy`, `curve_vs_hops`, `arm_swap_residual`, `decoding_skill`.
- [x] `smn_lab/worldmodel.py`: `zone_xy` + `localization_weights` (self-frame
      localization, was copy-pasted ×3).
- [x] Migrated 6 scripts to import from the framework (self_model_topology, branched,
      world_in_self_graph, world_geometry_self_frame, reafference_cut, geometry sweep);
      deleted the local copies.
- [x] **Verified numerically**: `coupling` byte-identical, `transfer` Δ≈2e-17;
      re-ran → self-model `0.89±0.08 / 1.00`, branched `9/9·0.318`, `8/8·0.096`,
      world_geometry `slope 0.98 r 1.000` — all unchanged. (flagship sweep re-running.)
- [x] New docs page `self-model-and-measurement.md` (the model↔measurement boundary,
      C3 locality, the one-primitive generalization) + re-pointed the self-model
      page's snippets to inject from `smn_lab/` — doc ← framework → experiment now
      share one source.

### Phase 2b — Restamp each spine page with a Formalism block *(rung by rung)*
Template (from `formalism-and-code.md`): **equation → injected code → the single
parameter this page varies**, all snippets pulled from source via named anchors.
- [x] **Rung 3 — self-model (`self_model_topology.md`)**: added `## Formalism — the
      transmission gain G` (common-mode strip, \(G_{ij}\), Laplacian/Fiedler
      recovery), injecting `transfer` / `recover_order` / `commonmode` / `conditions`
      from `experiments/self_model_topology.py`; trimmed the old prose "computed"
      section to point at it. Strict build clean; 21 math spans; 4 anchors resolve.
- [x] **Rung 3 — branched body (`branched_self_model.md`)**: upgraded the prose
      "local rule" into `## Formalism — the same read-out, on a tree` — injects
      `coupling` + `local_edge` (framework), the varied parameter `configs` (body
      morphology, not stiffness), and the experimenter's `arm_swap_residual` from
      `metrics`. Makes the "same read-out, topology-general" point concrete. Build clean.
- [x] **Rung 1 — C0 (`c0_crawler.md`)**: `## Formalism — locomotion from local
      coupling` — the traveling-wave Kuramoto law (inject `control.py:beam_command`),
      pull-only opponent PD (`control.py:opponent_commands`), anisotropic drag
      (`crawler.py:drag`), and the experimenter's non-reciprocity/scallop check
      (`viz.py:loop_area`). C0 smoke-run unchanged (net_disp 1.37, gap 1.27).
- [x] **Rung 1 — S0 (`sweep_c0_coupling.md`)**: `## Formalism — the coupling is the
      independent variable` — injects the swept `couplings` (K) and the phase-coherence
      order parameter \(R=|\langle e^{i\Delta\varphi}\rangle|\) (`coherence`),
      referencing C0 for the wave law.
- [x] **Rung 2 — C1 (`c1_touch.md`)**: `## Formalism — objecthood as a halt` — the
      ventral touch skin \(\text{touch}_k=W+f_k\) (inject `touchskin`) and the
      touch-keyed HAP gate (inject `haltparams` + `halt`). Added an honest admonition:
      this contact-halt is inline (only one in the spine); it's the sibling of the
      framework's whisker-keyed `HAPExplorer`; promote a general HAP only if a second
      appears (no premature abstraction). C1 re-run unchanged (touch 1.52 vs 0.49 load,
      arrested 1.64 m).
- [x] **Rung 4 — Q2 (`q2_reafference.md`) + W3 (`reafference_cut_self_graph.md`)**:
      `## Formalism — the reafference cut` — the decomposition \(dm/dt = \nabla m\cdot v + \partial_t m|_{\text{world}}\),
      injecting Q2's gradient-projection forward model (`reaff`) and W3's per-zone
      self-graph version (`reaff`). Audit finding: there are **three** distinct
      forward models (framework `ReafferencePredictor` yaw-binned; Q2 gradient; W3
      per-zone) realizing **one** principle (residual = actual − predicted-self);
      genuinely different contingencies, not duplication — documented in a
      "one principle, three forward models" admonition rather than force-merged.
      Re-ran unchanged: W3 `21.5× / 8.7×`, node 5.3; Q2 ratio `2.2±0.3` vs foil `1.58±0.35`.
- [x] **World arc restamp (W1 / W2 / Q1)** — closes the self-world gap so ② World
      reads as consistently as ① Self: W1 (self-referred vs allocentric localization,
      inject `worldmodel.py:localize` + `world_in_self_graph.py:localize`), W2
      (world-geometry in self-graph node units, inject `separation`), Q1 (per-zone
      distributed reafference / dual-port, inject `dualport` + `modulate`; the
      resolution principle). Strict build clean; re-ran unchanged.
- [ ] Pivot pages S1 / Q1b (Phase I→II) — prose only, Formalism block optional
- [ ] Rung 7 — predictions ×3 (folded into phases; Formalism blocks optional)

### Phase 3 — The seminar layer
- [ ] Rebuild `lab-interface.md` as the symbol ↔ code-arg ↔ live-control map.
- [ ] One-command bootstrap + pinned deps + seed/determinism note (a TIFR skeptic
      reproduces a figure in minutes).
- [ ] "Reviewer's start here" — the spine walked in 10 minutes.

### Phase 4 — Paper revision derived from the spine
- [ ] Move formalisms into the main body; cite the docs for the living record.
- [ ] Keep each future paper scoped to one experiment set (short, easy to review).

---

## Open decisions
- Exact top-level nav labels for the spine vs. archive (Phase 2).
- Whether to adopt `mkdocstrings` (API-doc style) in addition to `snippets`
  (verbatim line ranges). Default: `snippets` only — simpler, exact.
