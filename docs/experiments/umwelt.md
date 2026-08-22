# Umwelt — same world, different anatomy, different world

!!! abstract "The claim"
    Hold the **world** fixed and vary the **body**. What an agent can construct of that
    one world is set by its **sensory anatomy** — which transducers it has, and how far
    and finely they reach. Two animals in the same pond do not live in the same world;
    each builds its own **Umwelt**. This experiment makes that a measured coverage matrix.

## The idea (von Uexküll, on the bench)

Jakob von Uexküll's *Umwelt* is the world *as an animal can construct it* — the tick's
world is warmth and butyric acid; the same meadow is something else entirely to a
jackdaw. The SMN version is sharp and testable: because the world-model is built from an
agent's own **modulated transducers**, in its own body frame, the world an agent can
build is a direct function of the transducers its morphology carries. Change the anatomy
and you change the world — even though the physical world outside is byte-for-byte the
same.

The experiment keeps one world (a corridor of objects in a scalar field) and runs
several anatomies through it, scoring how much of the world each aspect of the body can
construct.

## The coverage matrix

Coverage is the fraction of the world an agent constructs through each sensory aspect:
a **field** sense (bilateral chemical/thermal strips), a **touch** skin, and **vision**.
Same world, different anatomies:

| morphology | FIELD | TOUCH | VISION | self-model |
|---|---|---|---|---|
| **all-normal** | 0.67 | 0.33 | 1.00 | 0.976 |
| **all-large** | 0.67 | 0.33 | 1.00 | 0.976 |
| **field-only** | 0.67 | — (0.00) | — (0.00) | 0.976 |
| **touch-only** | — (0.00) | 0.33 | — (0.00) | 0.976 |
| **vision-only** | — (0.00) | — (0.00) | 1.00 | 0.976 |

![The Umwelt coverage matrix — fraction of the world constructed, by anatomy × sensory aspect](../figures/umwelt_morphology.png)

Two things stand out, and they are the whole point:

- **Where a transducer is absent, coverage is a structural zero.** A vision-only body
  constructs the world's *visible* structure completely (1.00) and is blind to what only
  touch or the field would reveal (0.00). The zeros are not failures of degree; they are
  parts of the world that **do not exist for that body**.
- **Where a transducer is present, coverage is graded by reach and size.** Vision reaches
  the whole corridor (1.00); the bilateral field sense picks up two-thirds of it (0.67);
  the touch skin only registers what the body actually brushes against (0.33). Different
  senses carve out different-sized slices of the *same* world.

Meanwhile the **self-model is recovered at 0.976 for every anatomy** — each body knows
*itself* equally well. What differs across the Umwelten is not self-knowledge; it is the
**world** each self can build.

![A per-anatomy self/world card — the world painted onto the recovered self-graph](../figures/umwelt_all-normal_self_world_card.png)
*Each anatomy's world-model is expressed on its own recovered self-graph — the world in the body's own frame.*

## Why this belongs next to the world-model pages

This is the sensory-anatomy face of a claim the world-model pages make from the other
side: that the SMN world-model is **body-grounded**, expressed in the self-model's frame,
and therefore **not** the body-agnostic map a SLAM system would build. The
[cross-body transfer experiment](world_geometry_self_frame.md) shows the same conclusion
by decoding: a world-model trained on one body does not transfer to a different body,
while an allocentric observer's read transfers freely. Umwelt shows it by **coverage**:
the very *contents* of the world depend on which transducers the morphology carries.
Same world, different anatomies → **different Umwelten**.

## Run it

```bash
cd experiments && MUJOCO_GL=osmesa ../.venv/bin/python umwelt_morphology.py
```

(The sweep uses vision, so it needs a headless GL backend — `MUJOCO_GL=osmesa` or a
display.) Source:
[`umwelt_morphology.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/umwelt_morphology.py).
Every card and coverage figure is generated through the one [results module](../results-module.md).
