# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""A parametric sweep + export harness -- the bench as a generative model.

The bench is not a small observational dataset; it is a *generator*. This harness
runs an experiment across a grid of parameters and a set of seeds, and writes
collaborator-ready, self-describing output:

- ``summary.csv``      -- one tidy row per run: every parameter, the seed, and the
                          summary metrics. Load with anything (pandas, polars, R,
                          Excel).
- ``timeseries.parquet`` -- long format, all runs stacked (run_id + params + seed
                          + t + per-step signals). One file, columnar, efficient.
- ``manifest.json``    -- provenance: the grid, the seeds, the git commit, the
                          timestamp, and the column dictionary, so a run is
                          reproducible and self-explained.

Determinism is the point: every run is keyed by an explicit integer ``seed`` and
the code records the git commit it ran at. "Small data" is a non-issue -- sweep
the grid as wide as you like and regenerate.
"""
from __future__ import annotations
import os, json, itertools, subprocess
from datetime import datetime, timezone

import numpy as np
import pandas as pd


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True,
                              cwd=os.path.dirname(os.path.abspath(__file__))
                              ).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _configs(grid):
    """Cartesian product of a {param: [values]} grid -> list of param dicts.
    A list of dicts is passed through unchanged (for irregular designs)."""
    if isinstance(grid, list):
        return grid
    keys = list(grid)
    return [dict(zip(keys, combo)) for combo in itertools.product(*(grid[k] for k in keys))]


def run_sweep(name, run_fn, grid, seeds, summarize_fn, outdir="data",
              decimate=1, timeseries=True, verbose=True):
    """Run ``run_fn(params, seed)`` over every (config, seed) and export.

    run_fn(params: dict, seed: int) -> log: dict
        ``log`` holds equal-length time-series arrays (one must be ``'t'``) and/or
        scalars. Must be deterministic given (params, seed).
    summarize_fn(log, params, seed) -> dict[str, scalar]
        the per-run summary metrics.

    Returns the summary ``DataFrame`` and writes ``outdir/name/{summary.csv,
    timeseries.parquet, manifest.json}``.
    """
    base = os.path.join(outdir, name)
    os.makedirs(base, exist_ok=True)
    configs = _configs(grid)
    runs = [(ci, cfg, s) for ci, cfg in enumerate(configs) for s in seeds]

    rows, ts_frames, ts_keys = [], [], None
    for run_id, (ci, cfg, seed) in enumerate(runs):
        log = run_fn(cfg, seed)
        metrics = summarize_fn(log, cfg, seed)
        rows.append({"run_id": run_id, "config_id": ci, **cfg, "seed": seed, **metrics})

        if timeseries and "t" in log:
            t = np.asarray(log["t"])
            cols = {k: np.asarray(v) for k, v in log.items()
                    if isinstance(v, (list, np.ndarray)) and np.asarray(v).shape == t.shape}
            ts_keys = sorted(cols) if ts_keys is None else ts_keys
            df = pd.DataFrame({k: cols[k][::decimate] for k in cols})
            df.insert(0, "seed", seed)
            df.insert(0, "config_id", ci)
            df.insert(0, "run_id", run_id)
            ts_frames.append(df)
        if verbose:
            print(f"  [{run_id + 1:3d}/{len(runs)}] cfg={cfg} seed={seed} -> "
                  + ", ".join(f"{k}={v:.3g}" for k, v in metrics.items()
                              if isinstance(v, (int, float))))

    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(base, "summary.csv"), index=False)
    if ts_frames:
        pd.concat(ts_frames, ignore_index=True).to_parquet(
            os.path.join(base, "timeseries.parquet"), index=False)

    manifest = {
        "name": name,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": _git_sha(),
        "n_configs": len(configs), "n_seeds": len(seeds), "n_runs": len(runs),
        "grid": grid if isinstance(grid, dict) else "explicit-list",
        "seeds": list(seeds),
        "summary_columns": list(summary.columns),
        "timeseries_columns": (["run_id", "config_id", "seed"] + (ts_keys or [])),
        "decimate": decimate,
    }
    with open(os.path.join(base, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    if verbose:
        print(f"[sweep] {len(runs)} runs -> {base}/  (summary.csv, "
              f"timeseries.parquet, manifest.json)")
    return summary


def export_curated(name, columns=None, src="data", dst="samples"):
    """Copy the small, committable artifacts (summary.csv, manifest.json) into
    ``samples/`` -- the full ``data/`` tree is gitignored; the curated summary is
    what ships in the repo for collaborators."""
    sbase, dbase = os.path.join(src, name), os.path.join(dst, name)
    os.makedirs(dbase, exist_ok=True)
    df = pd.read_csv(os.path.join(sbase, "summary.csv"))
    if columns:
        df = df[columns]
    df.to_csv(os.path.join(dbase, "summary.csv"), index=False)
    man = os.path.join(sbase, "manifest.json")
    if os.path.exists(man):
        with open(man) as f:
            data = json.load(f)
        with open(os.path.join(dbase, "manifest.json"), "w") as f:
            json.dump(data, f, indent=2)
    print(f"[curated] {dbase}/summary.csv (+ manifest.json)")
