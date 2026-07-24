# Babble vs behave — when is the self-model recoverable?

!!! warning "Audited claim, honestly revised — and a prediction it generates"
    A scientific-accuracy review checked whether the [self-model read-out](self_model_topology.md)
    survives the drive the body was built for. It does **not** — under coordinated
    locomotion the read-out tracks command phase, not body topology. That is recorded
    here in full, together with the interpretation and the falsifiable prediction it
    generates. See the [status ledger](../status.md) and [release notes](../release-notes.md).

## The question

`self_model_topology.py` scores the read-out under an **independent OU torque per
zone** — incoherent, *exploratory* movement. Does the same read-out recover the body
under the **C0 traveling wave** (the drive the crawler was built for)?

## Result — it needs exploratory movement

Same 8-segment chain, same read-out, only the drive changes:

8-segment chain, 3 seeds (chance neighbour-accuracy = 2/8 = **0.250**):

| drive | neighbour_acc | order_acc | \|G\| by hop (1,2,3,4) |
|---|---|---|---|
| **babble** (exploratory / OU) | **1.000 ± 0.000** | 0.845 ± 0.067 | 0.195, 0.084, 0.042, 0.037 — **decays** |
| **behave** (beam locomotion) | **0.286 ± 0.000** *(≈ chance)* | 0.464 ± 0.000 | 0.632, 0.517, 0.706, 0.674 — **flat/inverted** |

![Babble vs behave: |G| decays with hop distance under babbling (reads the body) but is flat/inverted under the beam (reads the command); the adjacency band is present in the babble transfer matrix and absent under behave](../figures/self_model_babble_behave.png)

**The diagnosis is the hop profile.** Under babbling, `|G|` **decays** with hop
distance — elastic attenuation, the physical structure the read-out is meant to read,
so nearest-neighbours are the strongest co-movers and the chain assembles. Under the
beam, one oscillator drives every zone at fixed phase offsets, so
`|corr(efference_i, motion_j)|` becomes a function of the two zones' **phase
difference**, not their mechanical distance: the profile flattens (even peaks at a far
hop), and neighbour-accuracy falls toward chance. **The read-out stops seeing the body
and starts seeing the command.**

!!! danger "A metric floor that invalidates the small-body results"
    Chance neighbour-accuracy for an *n*-zone chain is exactly **2/n**. For the
    **3-segment crawler** used across §5–§6 (n = 2), chance is **1.000** — the metric
    *cannot fail*. Any self-model number reported on a 3-segment body is uninformative
    and is being dropped or replaced. (The 8-segment chain here, chance 0.25, is a fair
    test.)

## Interpretation — GN (a theoretical reading + a prediction, not shown here)

The collapse is **not** a refutation; it is a property of a *simple, single-chain*
body, and it sharpens the framework rather than denting it:

- **Babbling may be continuous** — a background *wake-up / body-schema calibration*
  state — so G stays available *while* behaving. SMN is committed to the
  sensation-**modulation** network, not to any one physical driving regime; a body
  that never stops exploring keeps its self-model current.
- **The dissociation is a small-body artifact.** One oscillator commanding every zone
  is exactly what makes the read-out see phase instead of body. Real animals are not
  single chains: they have many CAZ nodes and **layered subsystems** — tubes, sheets,
  spindles. Such a body can **babble in one part while behaving in another** (a fly's
  wings running a BAP-like pattern while the trunk explores). Then the behaving
  subsystem's coordinated drive does not contaminate the babbling subsystem's G.

    !!! quote "The prediction"
        **G-recovery-under-behaviour scales with the number of independent
        subsystems.** A single chain collapses; a multi-subsystem body should keep its
        self-model recoverable while behaving. Falsifiable, native to the "more body"
        thesis (§7), and the natural next experiment — *not claimed here.*

- **G is for action.** Following Glenberg's "memory is for action": the self-model has
  to be *stored* and *used*, or it is decorative. The
  **babble → behave → perturb** cycle (babble to learn G and freeze it; behave using
  the stored G to address zones; perturb a joint; measure whether behaviour degrades
  and a re-babble restores it) is the build that closes the model → use loop and tests
  the SMN thesis directly: *if the graph is the computer, breaking the graph should
  break the agent.*

Self, world, and object are taken here as **co-evolving** — the document's
self→world→object ordering is expository, not an ontological claim about the path an
agent must follow.

## What this establishes, and does not

- **Establishes:** the read-out recovers body topology from **exploratory** movement
  (clean elastic attenuation, neighbour-accuracy at ceiling on a fair-sized body), and
  fails under coordinated locomotion in a single chain — both reported, neither buried.
- **Does not (yet):** show the self-model recoverable *during behaviour* (predicted for
  complex bodies, untested), stored, or used. Those are the next builds.

## Run

```bash
cd experiments && ../.venv/bin/python self_model_babble_behave.py
```

Writes `figures/self_model_babble_behave.png`.
