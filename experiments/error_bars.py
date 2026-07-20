# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Aggregate the headline register numbers over N seeds -> mean +/- sd (+95% CI),
so the paper's figures are reported as distributions, not single runs.

R5 and Q2 already report seed statistics in their own scripts; this script adds
the missing ones (R1 slope, R2 latency/advantage) and re-reports R5 at the same
N for a uniform table. The haltability hold (p6) is deterministic by design
(no noise / no seed), so it carries no seed variance -- its robustness is a
parameter sweep, not an error bar.

Run:  ../.venv/bin/python error_bars.py [N]      (default N=12)
"""
from __future__ import annotations
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sweep_r1_tonic_load as r1
import sweep_r2_resumption as r2
import sweep_r5_dual_signal as r5

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
SEEDS = range(N)


def report(name, x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = len(x)
    sd = x.std(ddof=1) if n > 1 else 0.0
    ci = 1.96 * sd / np.sqrt(n) if n > 1 else 0.0
    print(f"  {name:34s} = {x.mean():7.3f} +/- {sd:.3f}   (95% CI +/-{ci:.3f}, N={n})")


# ---- R1: fit the load->tone slope PER SEED ----
def r1_slopes(classical):
    out = []
    for s in SEEDS:
        F, AP = zip(*(r1.run_hold(load, classical, s) for load in r1.LOADS))
        out.append(float(np.polyfit(F, AP, 1)[0]))
    return np.array(out)


# ---- R2: per-seed latency at each load; advantage = foil - SMN ----
def r2_latency_matrix(classical):
    return np.array([[r2.run_trial(load, classical, s)[0] for load in r2.LOADS]
                     for s in SEEDS], float) * 1e3   # ms


# ---- R5: dual-signal R^2 per seed ----
def r5_r2():
    self_r2, dec_r2 = [], []
    for s in SEEDS:
        THx, THy, PHI = r5.run(s)
        rng = np.random.default_rng(1000 + s)
        self_r2.append(r5.r2_dual_signal(THx, THy, THx, rng))
        dec_r2.append(r5.r2_dual_signal(THx, THy, PHI, rng))
    return np.array(self_r2), np.array(dec_r2)


def main():
    pred = r1.BOARD["beta"] * r1.BOARD["rho"] * r1.BOARD["tau_E"]
    print(f"\n[R1] tonic-load slope   (predicted beta*rho*tau_E = {pred:.3f})")
    report("SMN slope", r1_slopes(False))
    report("classical-foil slope", r1_slopes(True))

    Lsmn = r2_latency_matrix(False)
    Lcls = r2_latency_matrix(True)
    print("\n[R2] resumption latency (ms)")
    report("SMN latency @ lowest load", Lsmn[:, 0])
    report("SMN latency @ highest load", Lsmn[:, -1])
    report("classical-foil latency", np.nanmean(Lcls, axis=1))
    report("advantage (foil - SMN, over loads)", np.nanmean(Lcls - Lsmn, axis=1))

    sr, dr = r5_r2()
    print("\n[R5] dual-signal R^2")
    report("self-contact R^2", sr)
    report("decoupled R^2", dr)
    print()


if __name__ == "__main__":
    main()
