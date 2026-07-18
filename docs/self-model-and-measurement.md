# The self-model read-out: model vs. measurement

The experiment pages compute a handful of functions — a coupling matrix, a graph,
some accuracy scores — that turn the raw logs an agent generates while it moves
into a **self-model** (and, later, a world-model). This page documents *what those
functions are, why they exist, where they live, and why the line between two kinds
of them matters*. It is the answer to a question worth asking of any bench: **which
computations are the agent's cognition, and which are the experimenter's ruler?**

## Why the functions exist

Nothing hands the agent its own body-graph. It has to be *recovered* — from the
only thing available, the covariation between what each zone commands and what it
then hears move. That recovery is a read-out, and it recurs: the same operation
builds the chain self-model, the branched-body self-model, and (in the self-frame)
the world-model. Because it recurs, it belongs in the framework, not copied into
each script.

## The line that matters: cognition vs. measurement

Two kinds of function look similar but are categorically different:

| Kind | Test | Lives in | Examples |
|---|---|---|---|
| **The model** — the agent's own computation | a single zone could do it from its own efference + the broadcast | [`smn_lab/self_model.py`](https://github.com/gnowgi/smn-lab) | `local_read`, `read_all`, `coupling`, `transfer`, `local_edge`, `recover_edges` |
| **The measurement** — the experimenter's score | needs the *answer key* (true body order, true position) or the *whole matrix at once* | [`smn_lab/metrics.py`](https://github.com/gnowgi/smn-lab) | `seriation_order`, `order_accuracy`, `neighbour_accuracy`, `curve_vs_hops`, `decoding_skill` |

Keeping them in **separate modules** is deliberate: it makes the
[`simulated / computed / assumed`](assumptions.md) boundary visible in the code
layout itself. If a function needs the answer key, it is a metric and cannot be
part of the agent; if a zone could compute it locally, it is the model.

## The model is local (Commitment C3)

C3 says the shared state-space must be computed **without a central reader** — "the
graph *is* the computer." The atomic operation honours this: **one zone** reads its
own efference against the broadcast, and nothing else.

```python
--8<-- "smn_lab/self_model.py:local_read"
```

Stacking every zone's read into a matrix is a *vectorization convenience*, not a
shared computation — row `i` still depends only on zone `i`'s signal and the
broadcast:

```python
--8<-- "smn_lab/self_model.py:read_all"
```

The body graph is then the union of each zone's **own** edge — a local decision, no
global fit:

```python
--8<-- "smn_lab/self_model.py:local_edge"
```

By contrast, ordering the whole chain needs the entire matrix (a Fiedler
eigendecomposition). No zone can do that, so it is honestly labelled the
experimenter's summary and kept in `metrics.py`:

```python
--8<-- "smn_lab/metrics.py:seriation_order"
```

This is the discipline that lets the bench claim C3 rather than merely assert it:
the *recovery* is local; only the *scoring* is global, and the two never mix.

## One primitive, generalized

The three read-outs that used to be copy-pasted across scripts (`transfer` in the
chain experiment, `couple_matrix` in the branched experiment, and `coupling` in the
package) are **one operation** — the normalized cross-correlation of two
multichannel time-series:

\[
\mathrm{Xcorr}(A,B) = \tfrac{1}{n}\,\hat z(A)^{\!\top}\hat z(B),
\qquad \hat z(x) = \frac{x-\bar x}{\sigma_x+\varepsilon}.
\]

`coupling` is the signed version (efference ↔ motion, giving child/parent);
`transfer` is `|Xcorr|` symmetrized (an undirected gain). Two named specializations,
one primitive:

```python
--8<-- "smn_lab/self_model.py:coupling"
```

```python
--8<-- "smn_lab/self_model.py:transfer"
```

The same consolidation applies to the world-model: locating a world feature in the
self-frame (`zone_xy`, `localization_weights`) now lives once in
[`smn_lab/worldmodel.py`](https://github.com/gnowgi/smn-lab), and the world-model
score (`decoding_skill` + shuffle control) in `metrics.py`.

## Why this was worth doing

Before, a load-bearing computation lived in an experiment script, re-typed in two
places, with no guard that the copies agreed — exactly the drift the
[formalism ↔ code](formalism-and-code.md) commitment exists to prevent, one level
down. Promoting it into the framework forced the question *is this cognition or
measurement?* to be answered explicitly, and the answer is now legible in the
module boundary, in the docstrings, and — because every snippet on this page is
read from source at build time — on this page.
