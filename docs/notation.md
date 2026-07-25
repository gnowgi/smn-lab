# Experiment naming — how to read C0, S1, Q1b, W3, R5, E4b, P2

Every experiment on this bench carries a short label: a **letter** naming the
series it belongs to, a **number** giving its place in that series, and sometimes a
**trailing lower-case letter** marking a follow-up that closes a thread the parent
opened. `Q1b` is the second study of the first core question; `S0b` is a follow-up to
the first sweep; `E4b` follows `E4`.

The letters are not decorative and they are not chronological — each one says
something different about *what kind of claim the page is making*, and therefore how
much weight it can carry. This page is the key. It is descriptive: it records the
scheme the repository already uses, so a reader meeting `W3` in the
[status ledger](status.md) does not have to reverse-engineer it from context.

## The series

| prefix | series | what the label promises | pages |
|---|---|---|---|
| **C** | the **crawler** — the model organism | A demonstration on the canonical body, at a stated capability level, with a PASS/FAIL check. Not an ablation: nothing is varied against a foil. `C0` is crawler v0 (overdamped, gravity off); `C1` is v1 (gravity, ventral touch skin, objects). | [C0](experiments/c0_crawler.md), [C1](experiments/c1_touch.md) |
| **S** | **sweeps** of the organism itself | The independent variable is the bench's own architecture — coupling strength (`S0`), segment count (`S1`) — swept across a grid with replicated seeds and a matched foil or integrity control. `S0b` is the exception: a mechanism study of a *different* coupling — proprioceptive feedback from the body into the rhythm — checked against a `self`-entrainment ablation rather than a matched foil. | [S0](experiments/sweep_c0_coupling.md), [S0b](experiments/entrainment.md), [S1](experiments/sweep_geometry_worldmodel.md), [S1 field-scale control](experiments/sweep_geometry_worldmodel_fieldscale.md) |
| **Q** | the four core **questions** | The pre-registered spine of the [test plan](test-plan.md): can the agent build a world model from modulation (`Q1`), separate self from world (`Q2`), act on an individuated object (`Q3`), bind across modalities (`Q4`). A Q-number is a *question*, so it can outlive the experiments that attack it — `Q3` and `Q4` have no page of their own. | [Q1](experiments/sweep_q1_modulation.md), [Q1b](experiments/sweep_q1b_resolution.md), [Q2](experiments/q2_reafference.md) |
| **W** | the **world**-model series | The world-model built *in the agent's own frame*: locating a world feature on the self-graph (`W1`), reading the relation between two features in self-graph hops (`W2`), making the reafference cut in that frame (`W3`). Where Q asks whether the agent has a world model, W asks what its coordinates are. | [W1](experiments/world_in_self_graph.md), [W2](experiments/world_geometry_self_frame.md), [W3](experiments/reafference_cut_self_graph.md) |
| **R** | the preprint's **Registers** | A numbered register of the SMN architecture, reproduced on the bench. `R1`, `R2`, and `R5` open by naming theirs ("Register 1 …"). These are the pages most likely to be *analytic* — a consequence of the model's own equations rather than a contingent finding — and they say so where that is the case. | [R1](experiments/sweep_r1_tonic_load.md), [R2](experiments/sweep_r2_resumption.md), [R4](experiments/sweep_r4_adaptation.md), [R5](experiments/sweep_r5_dual_signal.md) |
| **E** | the later **exploratory** studies | Numbered like the going-forward series but evidentially still exploratory: all but [E3](experiments/p6_haltability_aboutness.md) carry the same "Exploratory trial — P/E series" note the P-pages do, yet these make claims the §5–§7 argument still leans on — objecthood as resistance through a manipulator (`E1`), self/field/object factoring (`E2`), the haltable pattern (`E3`), scaling and the objecthood transition (`E4`, `E4b`). Read as proofs-of-concept, not clean ablations. | [E1](experiments/p4_manipulator_objecthood.md), [E2](experiments/p5_self_field_object.md), [E3](experiments/p6_haltability_aboutness.md), [E4](experiments/p7_scaling_network.md), [E4b](experiments/p8_objecthood_transition.md) |
| **P** | **provenance** — the first exploratory studies | The bench's earliest line, built on a planar "mouse" with whiskers while the bench itself was being learned. Kept as provenance, explicitly *not* going-forward science: several runs are single-seed and some metrics saturate. See the [reproducibility note](reproducibility.md). | eleven pages — nine P-numbered, from [P0](experiments/p0_reafference.md) onward, plus two that never took a number; the ledger groups **P0–P2** as provenance and lists [P3](experiments/p3_crossmodal_discrimination.md) separately |

**Prediction 1 / 2 / 3** are a fourth kind of page and deliberately carry no letter:
they reproduce the preprint's own numbered testable claims —
[haltability signatures](experiments/sweep_pred1_haltability.md),
[zonal dissociations](experiments/sweep_pred2_zonal.md),
[antagonistic benefits](experiments/sweep_pred3_antagonistic.md).

## Numbering, and the trailing letter

In the going-forward series (C, S, Q, W, R, E) a number is claimed once and identifies
one study, so `S1` means the same thing in a commit message, an issue, and the ledger.
The P-series is looser and predates the convention: `P0`, `P1`, and `P2` each span
two or three pages, told apart by a suffix word or by title — `P0` vs `P0-visual`, and three
different `P2` pages (world model, basal coupling, map-guided foraging). Numbers are
*not* a reading order and *not* a difficulty ranking; the reading order is the
[Phase I → Phase II](phase2.md) argument laid out on the [home page](index.md).

A trailing lower-case letter marks a study that **exists because of its parent**:
either closing a question the parent left open or auditing something the parent
assumed. `Q1b` was written to close the density thread `Q1` left dangling; `Q1c` (still
pre-registered, no page yet) is the re-test that `Q1b`'s audit demands; `S0b` follows
`S0` into the mechanism; `E4b` sharpens `E4`. The suffix is a dependency, so a
withdrawn or downgraded parent should always be read before its children. The rule is
not applied everywhere: the ⛔ [S1 field-scale control](experiments/sweep_geometry_worldmodel_fieldscale.md)
is a child of `S1` in exactly this sense but is named descriptively rather than `S1b`.

Gaps in a series are real and mean the number was allocated to a question or a register
rather than a page. `Q3`'s directedness half is reported on
[E3](experiments/p6_haltability_aboutness.md) and its selection half is deferred; `Q4`
awaits a binding mechanism the bench does not yet have; `R3` names the reafference
register — [P0-visual](experiments/p0_visual.md) is the only page that opens on it, and
the reafference work otherwise lives under `Q2`/`W3` rather than under an R-number. The
[test plan](test-plan.md) is where a gap is accounted for.

## Pages with no label

Not every experiment has a prefix, and the unlabeled ones are not an oversight. The
self-model pages all exercise *one* function under varied conditions rather than
answering a numbered question, so they are named for whatever they vary — three by the
body ([branched](experiments/branched_self_model.md),
[sheet & tube](experiments/lattice_self_model.md),
[nested lattice](experiments/nested_lattice_self_model.md)), one by the read-out itself
([the read-out](experiments/self_model_topology.md), on the chain), and two that stay on
a fixed chain and vary the drive
([babble vs behave](experiments/self_model_babble_behave.md), and
[complex body](experiments/self_model_complex_body.md), which is titled for the body it
emulates but varies drive incoherence). The same
holds for the mechanism and capability studies —
[resolution exponent](experiments/sweep_resolution_exponents.md),
[canvas regions](experiments/canvas_regions.md),
[integrator & snapshot](experiments/integrator_snapshot.md),
[haltability](experiments/haltability.md) — and for two provenance pages that never took
a P-number, the [balance-beam sweep](experiments/p2_topology_sweep.md) and the
[living snapshot](experiments/p2_living_snapshot.md). Where a page has no letter, cite it
by title.

One inconsistency is worth knowing about rather than tripping over:
[proprioceptive entrainment](experiments/entrainment.md) is referred to as **S0b** in
the navigation and the [status ledger](status.md), but its own page is titled without
the label. Both names point at the same study.

## Letters that mean something else

Three of these letters are also used in the framework's own vocabulary, and the
collisions are easy to trip on:

- **S, M, N** in *Sensation Modulating Network* are architecture components — **S** is
  a transducer, **M** a modulator, **N** the communication board (the messaging beam).
  An `S` *followed by a digit* is a sweep; an `S` in a sentence about the architecture
  is a transducer. See [concepts](concepts.md).
- **Commitment C3**, **Commitment C6** are the preprint's numbered commitments — that
  the self-model is computed with no central reader, that elasticity is load-bearing.
  These are always written with the word *Commitment*, and are unrelated to `C0`/`C1`.
- **M1** names the SMN monograph and, by extension, the stage of the research programme
  this bench builds — the **unmediated agent**; **M2** names the next stage, **mediated
  cognition**, which is where object-*selection* and cross-modal binding are deferred to
  ("Phase II / M2", "M2 territory").

## Labels and file names

The label is a property of the *page*, not the file, and only some series put it in the
filename. **C, P, Q and R do**: `c0_crawler.py`, `p3_crossmodal_discrimination.py`,
`sweep_q1_modulation.py`, `sweep_r5_dual_signal.py`. **S, W and E do not** — their
scripts are named for what they do, so `S1` lives in
`experiments/sweep_geometry_worldmodel.py`, `W1` in `experiments/world_in_self_graph.py`,
and the whole E-series in the files `p4_…` through `p8_…` (`E1` is
`p4_manipulator_objecthood.py`), a mismatch left over from the E-pages sharing the
P-series' file numbering.

When hunting for the code behind a label, the reliable route is the **Run** section every
experiment page carries: it names the script and the command. One caveat — on a
preregistered page the command does not yet reproduce a result, because there is none:
[R4](experiments/sweep_r4_adaptation.md)'s script currently runs a synthetic self-test of
the estimator rather than the bench measurement.

## Adding a label

New experiments follow the [contributing checklist](contributing.md). If the work
answers one of the four core questions, it takes a `Q` number with a suffix letter
(`Q1c`); if it varies a structural parameter of the organism, an `S`; if it reproduces a
register, an `R`. When it does none of those — a mechanism study, a capability check —
leave it unlabeled and give it a descriptive title rather than inventing a series for
it. A label is a promise about the kind of evidence a page offers, so an unearned
letter is a small dishonesty of exactly the sort the [status ledger](status.md) exists
to prevent.
