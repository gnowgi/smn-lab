# Order parameters — what is, and what is not

!!! abstract "Why this page exists"
    Every SMN claim is stated with a **declared order parameter and a matched foil**. But not every
    number a bench reports is an order parameter. This page fixes the test — so a reader can tell an
    order parameter from a *diagnostic* or a *control parameter*, and so the same test can be applied
    to any new experiment. It is also the cleanest way to compare the received view with the SMN
    model. (Reasoning: preprint §3, §11; project notes `SMN_order_parameters.md`.)

## The one-line test

> An **order parameter (OP)** is a **low-dimensional functional of the emergent *coordination
> configuration*** of the whole SMN (sensing + pulling + messaging) that **changes qualitatively
> under a control-parameter sweep**.

"Low-dimensional functional" means: a scalar (or a small fixed handful of numbers, O(1), not growing
with the number of units) computed from the *entire* configuration — the way magnetization is one
number for any number of spins. The **microstate** itself, a **per-unit** quantity, or the full
**coupling graph** are high-dimensional — they are the *object*; an OP is a scalar read *off* it.

## The four tests (all necessary)

1. **Emergent, not stipulated.** *The razor:* sweep a control parameter; a genuine OP **transitions**,
   a stipulated quantity stays **pinned**. A scripted gait phase fails — its "coherence" is ≈1 by
   construction. Dissociated heart cells that spontaneously synchronise as they couple pass.
2. **Collective and whole-loop.** A property of the coordination, read across
   sense → message → pull → mechanics — never a single `f`, never the messaging side alone.
3. **Morphology-invariant in form.** Computable across the ladder (cnidarian → limb): it reads the
   *balance / held state* against whatever the opposition is (pair, hydrostat, or network), and
   coincides with a pair-observable only in the appendicular limit.
4. **Separates from a matched foil at a transition.** (The bench's existing discipline — necessary,
   not sufficient on its own.)

## Order parameters vs diagnostics vs control parameters

| kind | what it does | is it an OP? | examples on this bench |
|---|---|---|---|
| **order parameter** | a low-dim functional of the emergent coordination that transitions | **yes** | locomotion onset (S0), objecthood/coupling-density transition (E4b), the self/world reafference residual, held-state cost (alert energy), an *emergent* co-activation-group count, Umwelt decodable richness |
| **diagnostic (recovery/validation)** | agreement of a read-out with *known* structure; no disordered phase; saturates | **no** — a validation metric | self-model recovery / endpoint-recovery / neighbour-acc, NMI vs true communities, rim/interior betweenness ratios, transmission %, two-network geometry/reach |
| **control parameter** | a knob we tune | **no** — an input | coupling, CAZ/muscle density, load, morphology |
| **stipulated / microscopic** | put in by hand, or a single unit | **no** | scripted gait phases, one `f`'s force, a *by-construction* tissue count |

A diagnostic becomes an OP **ingredient** only when swept against a control parameter until a
**threshold** appears — then the threshold, not the number, is the OP signature.

## The framework already applies this

Two rows of the [status ledger](status.md) are OP-admissibility failures caught in review:

- **[Q1b — resolution = CAZ density](experiments/sweep_q1b_resolution.md)** (🟠): the "order parameter"
  was a detection-SNR statistic that could not separate CAZ density from any other independent samples
  — it was not reading the coordination configuration, so it was never an OP.
- **[S1 field-scale control](experiments/sweep_geometry_worldmodel_fieldscale.md)** (⛔): withdrawn
  because the order parameter was confounded by decoder dimensionality.

Making the test explicit turns these from *reported* failures into *predicted* ones.

## Alert energy — an OP, stated in general form

**Alert energy** (the metabolic cost of maintaining a held configuration) is a genuine order
parameter. Its bench operationalisation as *antagonist tonic activation tracking agonist load*
([R1](experiments/sweep_r1_tonic_load.md), [R2](experiments/sweep_r2_resumption.md)) is the
**appendicular register** — a pair-limit proxy. The general OP is the **cost of holding a coordinated
equilibrium**, which is defined on a hydrostat and a cnidarian too, where there is no discrete
antagonist to read a "tone" from. Keep the antagonist-tone version as the limbed register; state the
OP generally.

## The levels — one object, read at several scales

A CAZ is a zone of coordinated action; its OPs are functionals of that one object at successive
levels: **coherence** (does an unprogrammed pattern emerge?) → **returnability + held cost**
(haltability) → **resolution/fineness** (dexterity) → **decodable richness** (Umwelt). There is no
single "primary" OP the others specialise — coordination is the base, Umwelt the most derived.
