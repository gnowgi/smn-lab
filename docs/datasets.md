# Datasets — the bench as a generative model

The bench is not a small observational dataset; it is a **generator**. Any
experiment can be run across a grid of parameters and a set of seeds, producing
tidy, self-describing data that a physicist, mathematician, or data scientist can
verify and mine with their own tools. "Small data" is a non-issue: sweep the grid
as wide as you like and regenerate.

This is the invitation to collaborators: *here is a generative model of embodied
cognition, with explicit parameters and order parameters — sweep them and tell us
what mathematical structure falls out (phase transitions? information flow?
manifold geometry?).*

## What a sweep produces

Every sweep (`smn_lab.sweep.run_sweep`) writes three artifacts to
`data/<name>/`:

| file | format | contents |
|---|---|---|
| `summary.csv` | CSV | one tidy row per run: every parameter, the `seed`, and the summary metrics. Load with pandas, polars, R, Excel — anything. |
| `timeseries.parquet` | Parquet (columnar) | long format, all runs stacked: `run_id`, `config_id`, `seed`, `t`, and the per-step signals. One file. |
| `manifest.json` | JSON | provenance: the parameter grid, the seeds, the **git commit**, the timestamp, and the column dictionary. |

The full `data/` tree is gitignored (it regenerates); a **curated copy of each
`summary.csv` + `manifest.json` ships in [`samples/`](https://github.com/gnowgi/smn-lab/tree/main/samples)**
so the headline tables are in the repo.

## Why this is strong data, not weak data

- **Parametric families.** Sweep CAZ count, coupling density, drag anisotropy,
  body geometry, field layout, seed → as many runs as you want, all from one
  generator.
- **Clean causality.** Every variable is known and controllable — the thing field
  data almost never offers.
- **A recognizable model system.** The messaging beam is a coupled-oscillator
  (Kuramoto-style) network with a cognitive interpretation; the hooks to
  Ising/percolation/information-theory tooling are immediate.
- **Reproducible.** Every run is keyed by an integer `seed` and stamped with the
  git commit it ran at. Same code + same seed → same numbers.

## Reproducing a sweep

```bash
cd experiments && ../.venv/bin/python sweep_c0_coupling.py
```

writes `data/s0_coupling/` and refreshes `samples/s0_coupling/summary.csv`. See
the [coupling sweep](experiments/sweep_c0_coupling.md) for the worked example —
including its matched non-modulatory foil and seed ensemble.

## Writing a new sweep

```python
from smn_lab.sweep import run_sweep, export_curated

def run_one(params, seed):          # deterministic given (params, seed)
    ...                             # -> {"t": [...], "x": [...], ...}

def summarize(log, params, seed):   # -> {"metric": value, ...}
    ...

summary = run_sweep("my_sweep", run_one,
                    grid={"coupling": [0, 1, 2], "n_seg": [3, 5]},
                    seeds=range(10), summarize_fn=summarize)
export_curated("my_sweep")          # copy the small summary into samples/
```
