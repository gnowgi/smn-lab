# Vocabulary — the settled units of the SMN bench

This page fixes the words the bench uses, after a clarification (2026-08) that resolved a long-running
conflict in how "CAZ" was described. Everything else in the docs and code should be read through these
definitions. The reasoning behind them is in the preprint (arXiv 2605.26856v2, §3, §11) and the
project notes (`SMN_order_parameters.md`, `SMN_v3_caz_revision_flags.md`).

## The units

| term | what it is | what it is **not** |
|---|---|---|
| **`s` — segment** | a **node**: a body region (a point mass in the bench). | — |
| **`f` — contractile unit** | an **edge**: a *Sensation Modulator* — a spring-tendon muscle-tendon unit with its own actuator. It can only **pull** (pull-only), and is **one side** of an opponent relation. A spindle is a bundle of `f`s taken as one, so `f` is scale-recursive. | **not** a CAZ; **not** a whole muscle-with-its-antagonist. |
| **opposition** | the resistance every `f` pulls against — an elastic recoil, a hydrostat, the connected network, or a discrete antagonist. Mechanical, always present; its **form** differentiates up the ladder. | not a separate module. |
| **CAZ — Coordinated Action Zone** | a **zone of coordinated action**: a coordination of the *timing* of `f`s (which act together, which after which), realized by the **whole SMN** (sensing + pulling + messaging) and **read out**, never imposed by a controller. | **not** a single `f`, **not** a single node, **not** the neurons alone. |
| **opponent pair** | the **differentiated (appendicular) limit** of a CAZ — two pull-only `f`s across a shared variable (a joint), with a communication board. The split-circle glyph. | not the *definition* of a CAZ — its limit case. |

## The regimes (all one substance)

- **BAP ≡ CAZ** — a Basal Action Pattern (e.g. a heartbeat) *is* a CAZ: "zone" (spatial) and "pattern"
  (temporal) are two views of one spatiotemporal coordination object.
- **HAP** — a **Haltable Action Pattern**: a CAZ in its **held-and-returnable** regime. **Haltability**
  is a *special state* of an already-available CAZ (occupy and return to a chosen point in the pattern's
  state-space, at a real metabolic cost — *alert energy*).
- **dexterity** = **fineness** of the same CAZ (finer `f`s → finer haltability → tool use, speech).
- **NAP** — **Nested Action Patterns** = nested CAZs → generativity (the next rung).

## The two networks (as before)

- **DFN** — the differentiating net: opposing-zone coupling, damped/decremental, geometry-bearing,
  local; **coordination happens here**, decentralized (no central command).
- **IN** — the integrating net: a non-decremental broadcast board that composes a globally-available
  **snapshot**; it integrates, it does not command.
- *(A cnidarian's inter-layer rim coupling is **neither** — a distinct, more primitive inter-tissue
  gateway; see the cnidarian pages.)*

## Order parameter — the measurement word

An **order parameter (OP)** is a **low-dimensional functional of the emergent coordination
configuration** that **transitions under a control-parameter sweep**. It is *not* a stipulated or
scripted quantity, *not* a per-unit quantity, and *not* a recovery/validation metric (those are
**diagnostics**). Full test and re-sort: `SMN_order_parameters.md`.

## One-line reminder

> A **node** is an `s`; an **edge** is an `f` (one pull-only side); a **CAZ** is the *coordination* over
> `f`s — an opponent pair only in the appendicular limit. Coordination is the whole SMN's, not the
> neurons'.
