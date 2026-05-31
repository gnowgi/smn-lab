# P1-visual / static-world variant — only agent-side modulation

`experiments/p1v_static_world.py`

This experiment isolates the multi-CAZ eye's reafference register by holding
the world genuinely still (or nearly so), so the only motion the modulator
ever has to predict is the eye's own. The three conditions share the same
body, same eye-saccade schedule, same modulator — only the cylinder's
behaviour differs.

## The three conditions

| | calibration | self-test | exafference |
|---|---|---|---|
| **A. always-static cylinder** | cylinder visible-static | cylinder visible-static | cylinder visible-static |
| **B. visible → oscillating** | cylinder visible-static | cylinder visible-static | cylinder oscillates around the same position |
| **C. hidden → visible-static** | cylinder hidden (behind +x wall) | cylinder hidden | cylinder appears at the position and stays static |

In all three conditions, the head is held at 0 (no body CAZ activity); the
eye saccades with random fixation targets in `[−15°, +15°]` every 0.35 s; the
camera is mounted on the eye; the analytical predictor uses the eye's own
`Δθ` with the `sec²(α)` per-column correction; the modulator's per-patch
floor is the p90 of calibration residual magnitudes (clipped at 3.0).

## Result

```
A. cylinder visible-static throughout             : selftest fire = 0.000   exaf fire = 0.000   ×0.0
B. visible-static → oscillating during exafference: selftest fire = 0.000   exaf fire = 0.029   ×28.8
C. hidden → visible-static during exafference     : selftest fire = 0.000   exaf fire = 0.025   ×25.0
```

## Result & interpretation

![P1-visual static-world variant. Three rows, one per condition: residual time-series + exafference fire-fraction heatmap + representative residual frame. Row A is completely silent (no firing in any phase). Row B fires during exafference with a central blob over the oscillating cylinder. Row C fires during exafference at the cylinder location, both as an appearance transient and as sustained elevated baseline](../figures/p1v_static_world.png)

*Three rows, one condition per row. Per row, left to right: mean per-patch
`|residual|` time-series with the four phases shaded; the exafference
fire-fraction heatmap; and a representative `|frame − predicted|` frame
(transient for C; steady-state for A and B). Row A's residual is flat across
all phases with only periodic saccade transients; its fire heatmap is empty.
Row B's residual oscillates strongly during exafference with the cylinder's
motion. Row C's residual is elevated during exafference (starting with a
sharp appearance transient and then settling to a sustained baseline above
self-test).*

### What condition A shows — the user's predicted finding

**Condition A is silent throughout.** The cylinder is part of the world from
t = 0; the modulator's floor is calibrated *with* the cylinder in view; the
eye's saccades are perfectly predicted by `Δθ_eye · focal_px · sec²(α)`; the
warped previous frame matches the current frame to within the floor at every
patch. No patch fires in calibration, none fires in self-test, **none fires
in "exafference"** either — because nothing about the world is changing.

This is the cleanest possible statement of the architectural claim: **when
only the agent is moving and the predictor knows what's there, the snapshot
receives nothing**. The modulator's silence is the architecture working as
designed, not a bug.

### What B shows — motion against a known scene

The cylinder is visible-static during calibration; the modulator's floor at
the cylinder's patches accounts for the cylinder's own edges under saccade.
When the cylinder starts oscillating in the exafference window, the *motion*
is the world-caused change the modulator catches. Fire-fraction rises sharply
(×28.8 over self-test), concentrated on the patches the cylinder sweeps
through.

### What C shows — and the deeper finding about floor-as-memory

The naive prediction was that condition C would fire only as an *appearance
transient* (one frame when the cylinder teleports in, then silent — because
the analytical predictor has no explicit memory of the pre-cylinder world).
That prediction was wrong, in an architecturally informative way.

What actually happens: the cylinder's appearance produces a sharp transient
spike, **and then the residual settles to a sustained elevated baseline** for
the rest of the exafference window — almost as much firing as condition B's
moving cylinder.

The mechanism is the **per-patch floor calibration**. In condition C, the
cylinder is *hidden* during calibration; the floor at the patches where the
cylinder will later appear is calibrated against wall + floor-texture content
only. When the cylinder is present during exafference, its silhouette
contributes residual at every saccade — not because anything is moving in
the world, but because the sub-pixel warp on the cylinder's sharp edges
generates a small residual at *each* saccade, and this residual exceeds the
floor that was calibrated *without* those edges. Every saccade renews the
fire.

This reveals that **the modulator's per-patch floor calibration is the
architecture's first-order "scene memory"**. The modulator catches anything
that differs from calibration:

- *motion* (B),
- *appearance* (C-transient),
- *persistent presence whose edges the floor wasn't calibrated against*
  (C-sustained).

The contrast between A and C is the cleanest expression: same scene, same
agent motion, same modulator — only the calibration content differs. In A
the floor "knows" the cylinder and stays silent under it; in C the floor
doesn't, and fires on it. Memory of the scene lives in the calibration.

## What this experiment shows (and does not)

It **does** say:

- **Only agent-side modulation produces no snapshot input.** Condition A is
  literally silent across all phases — the closed loop "no modulation, no
  input" runs even when the world is static. The agent's BAP-and-eye motion
  generates no perception when there is nothing in the world to surprise it.
- **The modulator catches departures from calibration**, of any kind — motion
  (B), novel appearance (C-transient), or novel persistent content whose
  noise statistics weren't in the calibration distribution (C-sustained).
- **Floor calibration is implicit scene memory.** The architecture has a
  real, first-order form of "what's expected here" — not as a learned forward
  model, not as an explicit map, but as the per-patch residual distribution
  the modulator built up during calibration. Departures from that
  distribution are what the snapshot sees.

It **does not** say:

- That the architecture has *persistent* memory beyond the calibration
  window. The floor is frozen once `finalize()` is called; the modulator does
  not update it during self-test or exafference. A truly novel object that
  appeared and stayed forever would keep firing forever — there is no
  *habituation* mechanism. (Adding one — a slowly updating floor that
  re-learns the scene — is a natural successor experiment.)
- That the calibration floor can distinguish "moving cylinder" from "static
  novel cylinder" by signal magnitude alone. Conditions B and C have
  comparable exafference fire-fractions (×28.8 vs ×25.0); the *spatial
  pattern* and *temporal structure* would distinguish them (B is sustained
  across cylinder's swept positions; C has a sharp transient + steady baseline
  at a single position), but the scalar fire-fraction does not.
- Anything about depth or about a *learned* forward model. The predictor is
  still analytical; the "memory" demonstrated here is purely the floor's
  shape, not a model of how the world evolves.

## What it adds to the assumptions

[Common assumptions](../assumptions.md) hold, plus the
[P1-visual](p1_visual.md) ones — same multi-CAZ eye, same predictor with the
`sec²(α)` correction, same modulator. This experiment **adds**:

- The world's behaviour during the exafference window is the experimental
  variable — three discrete choices: same-as-calibration, oscillating around
  the same position, or appearing-from-hidden.
- The modulator's floor is explicitly understood as *scene memory* (the
  per-patch residual distribution calibrated against the calibration scene),
  and the experiment's conditions exercise it directly.

What is **not** added: a habituation mechanism (the floor stays frozen after
calibration); a snapshot accumulator that integrates fires into a persistent
map; an explicit learned forward model. These are the natural next pieces of
architecture this experiment motivates.

## Why this experiment is in the bench

It pins down the modulator's discrimination boundary at the cleanest possible
operating point: only the agent moves. Condition A is the bench's first
**negative result** demonstrating that the architecture's silence under
pure self-motion is real and complete, not a hidden source of noise. Condition
B reproduces the standard exafference detection under known-scene conditions.
Condition C reveals — as a *finding*, not a planned demonstration — that the
modulator's floor calibration already encodes a primitive form of scene
memory, and that "novel persistent presence" is detected through the same
mechanism as "novel motion," modulated by the calibration history rather
than by an explicit world model.

Together the three conditions read as the architecture's first careful
statement of *what counts as a sensation the snapshot must absorb*: any
patch-level residual that the calibration didn't account for, by any
mechanism.

## Run it

```bash
cd experiments && ../.venv/bin/python p1v_static_world.py
```

Outputs: `figures/p1v_static_world.png`. Runtime: ~70 s on a laptop CPU.
