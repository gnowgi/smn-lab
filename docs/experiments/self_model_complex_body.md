# Complex body — independent subsystems restore the self-model during behaviour

!!! success "GN's prediction, tested and confirmed (with a control that says *why*)"
    [Babble vs behave](self_model_babble_behave.md) showed the self-model read-out
    collapses under a single coordinated beam. GN predicted that collapse is a property
    of a **simple single-chain** body: a body with independent subsystems can behave in
    several parts at once without one global rhythm hiding it. Tested here — **confirmed**,
    and a same-rhythm control shows the mechanism is drive *incoherence*, not partition.
    Marked 🟡 (fresh, one-session, drive-on-fixed-chain; awaiting independent check + a
    real-morphology follow-up). See the [status ledger](../status.md).

## What it tests

Morphology is held fixed at the 8-segment chain; **only the drive varies.** The zones
are partitioned into `K` contiguous subsystems, each driven by its own beam, and `K` is
swept. Three drives:

- **`diff`** — each subsystem runs at its own (random) frequency → the body's rhythms
  are **temporally incoherent** across subsystems (the fly: wings and trunk on different
  clocks).
- **`same`** — every subsystem runs at the **same** 0.9 Hz → the control that isolates
  the cause: is recovery from *having subsystems*, or from *incoherence*?
- **`ou`** — independent OU torque per zone → the babbling ceiling.

## Result — an inverted-U

Chance neighbour-accuracy = 2/8 = **0.25**; babbling ceiling ≈ 1.00.

8-segment chain, 5 seeds, neighbour-accuracy:

| K (independent subsystems) | `diff` — distinct rhythms | `same` — one rhythm (control) |
|---|---|---|
| 1 (single global beam) | 0.229 ± 0.070 | 0.286 |
| 2 | 0.771 ± 0.171 | 0.286 |
| **3** | **0.857 ± 0.156** | 0.143 |
| 4 | 0.771 ± 0.171 | 0.286 |
| 5 | 0.486 ± 0.171 | 0.000 |
| 6 | 0.314 ± 0.057 | 0.571 |
| 7 | 0.257 ± 0.190 | 0.286 |

![Neighbour accuracy vs number of independent subsystems: distinct-rhythm subsystems trace an inverted-U peaking near K=3 (close to the babble ceiling) while the same-rhythm control stays at the collapse; hop profiles show K=3 and babble decay while K=1 is flat](../figures/self_model_complex_body.png)

- **A few distinctly-tuned subsystems restore the self-model while behaving.**
  Neighbour-accuracy climbs from the single-beam collapse (0.23) to a peak of **0.86 at
  K = 3**, then falls back toward chance as subsystems shrink to single, low-SNR
  oscillators. The hop profile flips with it: flat/inverted at K=1 (reads the command),
  back to elastic-attenuation **decay** at K=3 and under babbling (reads the body).
- **The same-rhythm control does not follow.** It stays low and erratic (mean ≈ 0.28,
  no systematic recovery) rather than tracing the `diff` inverted-U — so partitioning
  into subsystems does nothing by itself. **It is drive incoherence — distinct rhythms —
  that reveals the body.** (One deterministic same-rhythm point, K=6 = 0.571, is shown
  as-is and not smoothed; it does not form the smooth hump the distinct-rhythm sweep
  does.) Broadband OU babbling is the limit of maximal incoherence — the ceiling (1.00).

## Interpretation

- **The collapse was a simple-single-chain artifact — GN's prediction was right.** A
  single oscillator commanding every zone is the worst case; give a body a handful of
  independently-clocked subsystems and its topology is legible *during behaviour*, no
  babbling pause required.
- **There is an optimal intermediate number of subsystems.** Too few (K=1) and one
  rhythm dominates; too many (K→n) and each subsystem is a single weak oscillator with
  little transmission signal. The peak near K=3 is a richer claim than "more is better."
- **Frequency diversity keeps the body-schema legible in action.** Real animals run
  wings, legs, gut, and heart on different clocks; this says that very diversity is what
  lets the self-model stay current while the animal behaves — and it reconnects the
  behaving regime to babbling as two points on one incoherence axis.

## Scope, and what is *not* claimed

- This varies the **drive** on a fixed chain to isolate the mechanism (drive coherence).
  It does **not** yet show that real **branched morphology** supplies that incoherence —
  that is the natural follow-up (independent limbs / layered subsystems), not claimed here.
- Fresh result, one session; the mechanism should get an independent check like the
  claims that preceded it. The single-zone extreme (K≈7) is low-SNR, near chance.
- G is still not **stored** or **used** — the [babble → behave → perturb cycle](self_model_babble_behave.md)
  remains the build that closes model → use.

## Run

```bash
cd experiments && ../.venv/bin/python self_model_complex_body.py
```

Writes `figures/self_model_complex_body.png`.
