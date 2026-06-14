# Reproducibility note — the P3 review discrepancy

## Context

An external [formal review](https://github.com/gnowgi/smn-lab) of the bench raised,
as its most concrete finding, that the **P3** documentation overstates its
results. Specifically (review, *Primary Findings* #6): running the P3 script was
reported to produce **3** touch-only classes with 9 whiskers, and a neural-net
foil matching SMN at roughly **32** labeled examples — whereas the docs state
**2** classes and **~128** examples.

This note records a check of that claim.

## What we verified

P3 (`experiments/p3_crossmodal_discrimination.py`) is **fully deterministic** —
every stochastic component is seeded (`numpy.random.default_rng(7 / 11 / 0 / …)`).
The script is **unchanged since it was added** (commit `07f2a2b`), which predates
the review commit (`54b0266`). Re-running it on 2026-06-14 produced:

**Binding** — individuable categories vs coupling:

| coupling | individuable categories |
|---|---|
| touch | 2 |
| touch + vision | 4 |
| touch + vision + taste | 8 |
| **touch only, 9 whiskers** | **2** |
| subsumption, 3 sensors | 2 |

**Foil** — deep net (labeled corpus) vs SMN (zero corpus, same test set):

| labeled examples | deep-net accuracy |
|---|---|
| 0 | 0.12 (≈ chance) |
| 32 | 0.74 |
| 64 | 0.86 |
| **128** | **0.94** |
| 256 | 0.99 |
| 512 | 1.00 |
| **SMN (0 examples)** | **0.955** |

The deep net reaches SMN's zero-corpus accuracy (~0.955) at **~128** examples
(it is at 0.74 with 32). The result figures regenerate **byte-identical** to the
committed versions.

## Conclusion

The current P3 documentation is **accurate to the deterministic code**: 2
touch-only classes at 9 whiskers, and ~128 examples for the net to match SMN. The
review's contrary numbers (3 classes, ~32 examples) **do not reproduce** here.
Because the code is seeded and unchanged since before the review, the most likely
explanations are a different or locally-modified version, a different environment,
or a transcription error in the review. We record this so the discrepancy is on
the record rather than silently contradicting the review document.

The review's **methodological** observations — single-seed demonstrations,
saturating metrics, the mixed-ablation [topology sweep](experiments/p2_topology_sweep.md),
and foil balance — remain valid. They are addressed by reframing the P/E series as
[exploratory trials](index.md#the-two-experiment-series) and by the disciplined
C-series ([C0](experiments/c0_crawler.md), [C1](experiments/c1_touch.md)) going
forward.
