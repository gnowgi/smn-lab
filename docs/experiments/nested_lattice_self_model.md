# Nested lattice — one function, any *level* (scale-invariance)

## Why this experiment

The [lattice self-model](lattice_self_model.md) showed one function recovers any
*shape* (chain, tree, sheet, tube). This adds the **vertical** axis: one function
recovers the body at any *level of description*. A **three-level nested lattice** that
**tapers** up the hierarchy — **36 segments → 9 blocks → 3 super-blocks** — is read by
the **same** `coupling`, and the body graph comes out at **all three** levels from one
run: the fine graph of segments, then the block graph and the super-block graph, each
from motion averaged over the level below (a renormalization step, applied twice).

The taper is not incidental. Coarse-graining *pools* — each super-node is the
aggregate of the several units beneath it — so the count must **strictly decrease**
going up: the deepest layer holds the most units, each layer above holds fewer, the
apex holds one. Deeper = more detail; higher = more abstract. That decreasing count
*is* the renormalization factor.

This is the foundation for **morphological computing**: the body's layered topology
is what fixes the *data-structures* the body can represent, and hence what it can do.
It is also where **haltability** will build — a haltable pivot needs a layer beneath
it to pivot against, so *layering is the precondition of halting*, and halting is
what turns a nested topology into dexterity (why a body with the same topology but
without haltability cannot count or name beyond a few). This experiment establishes
the layering; haltability is the next step.

## The idea

A block is a small lattice of segments (a "cell" or module); a super-block is a small
group of blocks. A nested lattice is a lattice **of lattices of lattices**: `fine`
links wire segments within a block, `mid` links wire block to block within a
super-block, `coarse` links wire super-block to super-block. Each link is one CAZ (a
spring-tendon muscle), the tissue is overdamped, and every link is driven
independently — exactly as before, now at three scales at once.

## Formalism — the same read-out, coarse-grained

The wiring tags every link by level — `fine`, `mid`, or `coarse`:

```python
--8<-- "smn_lab/lattice.py:nested_spec"
```

The **fine** self-model is `coupling` over the segments, unchanged. Each higher level
is the *same* `coupling`, applied after **renormalizing** — averaging each group's
segments into one super-node — driven by that level's links:

```python
--8<-- "experiments/nested_lattice_self_model.py:coarsegrain"
```

```python
--8<-- "smn_lab/self_model.py:coupling"
```

### The n-level nested lattice, in general

Define the architecture recursively. A **level-0** node is a single segment (a point
mass). A **level-\(\ell\)** lattice is a graph whose nodes are themselves level-\((\ell-1)\)
lattices, joined by level-\(\ell\) CAZ links:

\[
\mathcal L^{(0)} = \{\text{segment}\},\qquad
\mathcal L^{(\ell)} = \bigl(V^{(\ell)}, E^{(\ell)}\bigr),\quad
v \in V^{(\ell)} \;\text{is a}\; \mathcal L^{(\ell-1)}.
\]

An \(n\)-level body is \(\mathcal L^{(n)}\); its segments are the leaves, and its
links are \(E^{(1)}\cup\cdots\cup E^{(n)}\) — CAZ at every level. Let \(u_L\) be a
link's drive and \(v_s\) a segment's motion. The read-out at the finest level is the
framework function

\[
C^{(0)}_{L,s} = \bigl|\mathrm{Xcorr}(u_L, v_s)\bigr|,\qquad
\hat G^{(0)} = \operatorname{recover}\,C^{(0)}.
\]

Introduce the **coarse-graining (renormalization) operator** \(\mathcal R\), which
averages the segments of each level-\(\ell\) node into one super-node observable and
keeps that level's links:

\[
v^{(\ell+1)}_V = \frac{1}{|V|}\sum_{s\in V} v^{(\ell)}_s,\qquad
C^{(\ell+1)}_{L,V} = \bigl|\mathrm{Xcorr}\bigl(u_L,\, v^{(\ell+1)}_V\bigr)\bigr|.
\]

**Scale-invariance** is the statement that one functional \(\Phi=\operatorname{recover}\circ\,|\mathrm{Xcorr}|\)
recovers the true graph at *every* level — it commutes with \(\mathcal R\):

\[
\Phi\bigl(\mathcal R^{\ell} X\bigr) \;\approx\; G^{(\ell)}\quad\text{for all }\ell.
\]

The self-model is thus a **fixed point of the renormalization flow in form**: the
same read-out, coarse-grained \(\ell\) times, returns the level-\(\ell\) body graph.
This experiment realizes \(n=3\) (segments → blocks → super-blocks, 36 → 9 → 3); the
definition is general.

## Result — one function, three levels

![Three panels. FINE: 36 segments recover the nine 2×2 blocks (solid), but the inter-block links are misplaced (red) — the fine scale cannot localize them. MID: nine blocks recovered from block-averaged motion, chained within each super-block. COARSE: three super-blocks recovered from super-block-averaged motion.](../figures/nested_lattice_self_model.png)

| level | nodes | recovered by | recovery (3 seeds) |
|---|---|---|---|
| **fine** | 36 segments | `coupling` on segment motion | **0.88 ± 0.01** |
| **mid** | 9 blocks | the *same* `coupling`, block-averaged | **1.00 ± 0.00** |
| **coarse** | 3 super-blocks | the *same* `coupling`, super-averaged | **1.00 ± 0.00** |

All from **one simulation**, one function, renormalized twice. The active
(coarse-grained) levels are recovered **crisply** (1.00); the fine level is
**fainter** (0.88), and the misses are exactly the **higher-level links** — they
couple whole groups, so the fine scale cannot localize them.

### The deep layer is a canvas — a faint readout is a feature

That faintness is not a limitation to fix; it is the correct operating regime. The
deep layers are the **stable canvas on which the active top layers write**, and the
self-model does not need to sharply re-encode a stable substrate — a *sharp* deep
readout would be the pathology (a canvas that keeps redrawing itself). Two things
make this concrete:

- **The self-model of the writing does not depend on the fidelity of the canvas.**
  Across every perturbation regime we tried (uniform drive, stiff deep layer, faint
  deep drive), the **active levels stayed at 1.00** while the fine recovery wandered
  (0.87–1.00). The top-level self-model is robust to a faint canvas — so the model
  genuinely *needn't be of all layers below*.
- It is the **[reafference cut](q2_reafference.md) one level up**: the stable canvas
  is the predicted baseline, the active writing is the residual event that stands
  out. And it is the geometry-conserving view of cognition made mechanical — the deep
  canvas *conserves* the reference geometry while the top layers *transform* it.

So no single level is a flat, complete picture: the coarse structure is recoverable
*only* after renormalizing, and the deep structure is *meant* to sit faint beneath
the writing. **Layering is not decoration — it is figure and ground.**

## What this establishes

- **Scale-invariance of the self-model.** With [topology-invariance](lattice_self_model.md),
  the read-out is now invariant to both *shape* and *level*: one function, any body,
  any scale — the CAZ is scale-recursive (see the *physics at every layer* design
  note in the repository).
- **Layering is figure and ground**, not a redescription — the coarse graph cannot be
  read at the fine scale, and the deep layer is *meant* to sit faint beneath the
  active writing (a canvas, robust to under-resolution). This is the precondition the
  SMN needs for **haltability**: a pivot halts against the stable layer beneath it.
- **Morphological computing.** The layered topology fixes the data-structures the
  body can build (a chain → a sequence; a tree → a hierarchy; a tube → a cyclic
  buffer; nesting → recursion). Designing the anatomy designs the computation — for
  biological bodies *and* for non-human anatomies engineered to exceed our own, which
  the bench can now simulate. What turns these structures into *operations* is
  **[haltability](haltability.md)** — a stable hold against the canvas — the next step.

## Run

```bash
cd experiments && ../.venv/bin/python nested_lattice_self_model.py
```
