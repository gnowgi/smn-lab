# samples/ — curated demo data

Small, committed examples of the data the experiments produce, so you can see
the **format** without running anything.

The full, dynamically generated data is written to `../data/` (gitignored —
regenerable from fixed seeds). Versioned, citable snapshots (including Zenodo
DOIs) will accompany the paper.

## Files

### `demo_full_baseline.npz`
A representative run: the *full (5 whiskers · flat routing · BAP+HAP)* condition
of the balance-beam sweep. Load with `numpy.load`:

| key | shape | meaning |
|---|---|---|
| `hits` | (4000, 2) | whisker hit points in world coordinates — the constructed map. Subsampled from ~120k for size. |
| `true_traj` | (T, 2) | the agent's true (x, y) path; decimated 20×. |
| `est_traj` | (T, 2) | the agent's self-localized (dead-reckoned) (x, y) path; decimated 20×. |
| `cov`, `prec`, `drift` | scalar | coverage, precision, dead-reckoning drift (m). |

```python
import numpy as np
d = np.load("samples/demo_full_baseline.npz")
print(float(d["cov"]), float(d["drift"]))
hits = d["hits"]            # (N, 2) constructed map
```

### `sweep_results.csv`
Machine-readable summary of all nine sweep conditions: `coverage`, `precision`,
`drift_cm`, `n_hits`, and every parameter (`whiskers`, `drive_offset_y`,
`routing`, `bap`, `hap`, `prop_noise`).

### `truth_surface.npz`
`truth` (M, 2): ground-truth points sampled along the true arena surfaces
(walls + objects), the reference for coverage/precision.

## Regenerating the full data
```bash
cd experiments && ../.venv/bin/python p2_topology_sweep.py   # writes ../data/
```
