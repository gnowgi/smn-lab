# The disk experiments — what is the rim?

These three experiments flatten the cnidarian sac into a **two-layer disk** and ask one
question from three angles: *what is the rim?* The rim is where the outer and inner faces
fold into each other — the seam that, in a polyp, becomes the mouth. Here the mesoglea
between the faces carries only messaging edges, **no mechanical CAZ springs**, so the rim
fold is the **only mechanical bridge between the two layers**. That single fact turns out
to shape the self-model, gate every perturbation, and — when removed — decide whether the
body has a special place at all.

All three run through the one [results module](../results-module.md); see the
[cnidarian model system](../cnidarians.md) for the framing.

## 1 · The rim announces itself in the self-model

Give the disk nothing but its own **babbling** movement — no world, no perturbation — and
recover its self-model (its connectivity graph) from the co-motion. The discriminating
observable is not degree (rim nodes have ordinary degree ~4) but **betweenness
centrality**: the fraction of shortest paths that run through a node. Because the rim fold
is the sole bridge, *every* path between the two faces passes through the rim.

![Two-layer disk self-model — rim nodes carry the highest betweenness; a radial gradient rises to the rim; tentacles are low-betweenness pendants](../figures/diploblast_disk_self_model.png)

| zone class | betweenness (recovered) | betweenness (true) | degree |
|---|---|---|---|
| **rim** | **0.53 ± 0.26** | 1.00 | ~4 |
| interior | 0.28 ± 0.20 | 0.55 | 3.7 |
| tentacle | 0.14 ± 0.13 | 0.15 | **1.7** |

Three things, recovered from babbling alone (self-model recovery **0.98**):

- **The rim reads highest** — a betweenness maximum, ~1.9× the interior. The mouth-to-be
  is singled out by morphology *before any world or dynamics*, and it shows up in the
  body's own self-model.
- **It is a gradient, not a step.** Betweenness rises monotonically from the disk centre
  out to the rim (right-hand panels) — the self-model already says *the roads converge on
  the rim*. (That gradient is why the "interior" spread is so wide.)
- **Tentacles read at the opposite extreme** — low degree, low betweenness *pendants*. So
  the body carries, in its self-model, the two ingredients of an attractor at once: a
  high-centrality **collector rim** and low-centrality peripheral **feelers**.

The effect is ~2×, not 10×, because the fold is a whole **ring** of parallel bridges —
the bottleneck is shared. Collapsing it toward a single point (a **hypostome**) should
sharpen the rim into a true single sink; that is a pre-registered next test.

!!! note "Does it change if you run longer? — it converges, it does not drift"
    ![Convergence — recovery plateaus by ~16 s; the rim/interior ratio stabilises](../figures/disk_convergence.png)
    The self-model read-out is a time-averaged correlation, so more babbling is just more
    samples. Below ~8 s the graph is under-recovered and the rim is not yet distinguished
    (recovery 0.35 at 2 s, ratio < 1); by ~16 s recovery plateaus (~0.97) and the
    rim/interior ratio settles into a stable band. Past saturation the numbers scatter but
    do not trend — babbling is stationary. Honest caveats: recovery plateaus *below* 1.0
    (a few fold-ring edges stay ambiguous, which flattens the recovered rim peak), and
    seed-to-seed scatter is real (3-seed mean ratio ~1.2–1.6; the single-run 1.9 above sat
    on the high side). The *conclusion* — rim highest, gradient toward it, tentacles lowest
    — is robust and converges quickly; the exact multiplier should be read as a multi-seed
    mean.

## 2 · A perturbation on the outer face — the rim is the only door

Now perturb: pulse one outer-face zone and watch the response spread. The mechanical
question is whether it reaches the inner face or stops at the rim. Two conditions —
**rim fold intact**, and **rim fold cut**.

![Outer-face perturbation — with the rim intact a weak rim-first echo reaches the inner face; cut the rim and the inner face is sealed off](../figures/disk_perturbation_propagation.png)

- **Transmission to the inner face: 0.60% (intact) → 0.01% (cut).** Cutting the one fold
  drops inner-face motion ~60×, to the numerical noise floor. Essentially **100% of what
  reaches the inner face crosses at the rim**.
- **Rim-first:** within the inner face the rim ring responds **55×** more than the centre.
  The echo enters at the inner rim and dies out inward.
- **Late:** the outer touch peaks at 129 ms; the inner rim not until 379 ms — the
  wavefront must travel to the rim and cross the fold first (right-hand panels).

So the disturbance does **not** stop at the rim — the rim is the **doorway**, and cutting
it seals the inner face off entirely. But it crosses *weakly, rim-first, and late*, so the
inner face (the gut lining) is effectively **mechanically shielded** from pokes on the
skin. That is a feature: a digestive interior should not be yanked by every external
touch, and the future mouth is precisely the one place the world-facing surface and the
gut are coupled. This is the [DFN](../cnidarians.md) being decremental and rim-gated; for
the gut to *know* about the touch without being moved by it, you would need an integrating
channel — the flagged next step.

## 3 · Where the touch lands, and whether a rim exists

Three bodies, one pulse each: a tentacled disk touched on a **tentacle tip** (the likely
prey-contact point); the same disk touched on the **outer face**; and a **closed sphere
with no rim**, its two shells coupled through the wall everywhere, touched on the outer
shell.

![Three cases — tentacle-tip and outer-face keep the inner layer far away and rim-gated; the no-rim sphere crosses through the wall locally](../figures/disk_tentacle_sphere_propagation.png)

| case | transmission to inner | nearest inner node |
|---|---|---|
| tentacle tip | **0.19%** | 4 hops |
| outer face | **0.41%** | 3 hops |
| **sphere (no rim)** | **27.1%** | **1 hop** |

The right-column decay plots tell it: in the two disk cases the inner layer (blue) is a
*separate, far, attenuated* cluster; in the sphere it interleaves with the outer points at
every distance.

- **Tentacle tip vs outer face.** Both are rim-gated and small, but the tentacle transmits
  *less* — the tip is the farthest point on the body, so the signal decays down the cable
  before it even reaches the rim, and it funnels into one rim sector rather than spreading
  to all of them. So a tentacle is a **reach-and-aim** device (catch prey far out, deliver
  it to a specific mouth sector), **not** a signal amplifier. Getting the tentacle-tip news
  to the mouth *strongly* is, again, the integrating net's job.
- **Disk vs sphere.** The rim keeps the inner layer three-to-four hops away and
  mechanically shielded (<0.5%). Remove the rim and couple the wall throughout, and every
  inner node sits **one hop** under its outer partner — the touch crosses locally and
  immediately, everywhere: 27%, no rim-first, no special place.

!!! tip "The deep point — an attractor needs broken uniformity"
    A special location — a mouth, an attractor — *requires* broken symmetry. The rim is a
    symmetry-breaking seam, and that is what makes one place distinguished. A uniformly
    through-wall-coupled sphere is "every place is the same place" and has **no** attractor
    at all. So the morphological asymmetry is not incidental to the mouth being special —
    it is the **precondition** for it. (Modelling choice: the sphere's shells are coupled
    mechanically through the wall everywhere. If instead they were messaging-only like the
    disk, transmission would be ~0% — the "no door at all" case.)

## Run them

```bash
cd experiments
../.venv/bin/python diploblast_disk_self_model.py       # 1 · rim betweenness in the self-model
../.venv/bin/python disk_perturbation_propagation.py    # 2 · the rim is the only door
../.venv/bin/python disk_tentacle_sphere_propagation.py # 3 · tentacle-tip / outer-face / no-rim sphere
```

Sources:
[`diploblast_disk_self_model.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/diploblast_disk_self_model.py) ·
[`disk_perturbation_propagation.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/disk_perturbation_propagation.py) ·
[`disk_tentacle_sphere_propagation.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/disk_tentacle_sphere_propagation.py).
