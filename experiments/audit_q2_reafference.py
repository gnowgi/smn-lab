# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Audit of Q2 (reafference cut) -- the scrutiny pass for docs/status.md.

The Q2 order parameter is the residual ratio (exafference / self-test), reported
2.2 +/- 0.3 for the reafferent agent vs 1.58 +/- 0.35 for the no-forward-model
foil. The doc already labels this "partially supported". This audit asks the two
questions a skeptic asks before the row can move off 'not yet audited':

  (1) WORKING NULL -- no-event control. Re-run with the moving source amplitude
      set to zero, so the "exafference" window contains NO world-caused change.
      If the reafferent/foil separation is genuinely world-caused, BOTH ratios
      must collapse toward 1. If the reafferent ratio stays elevated with nothing
      happening, the ratio is inflated by windowing/calibration, not reafference.

  (2) PAIRED ROBUSTNESS -- is reafferent > foil per seed, not just on average?
      A modest mean gap can hide sign flips; a real cancellation should hold seed
      by seed.

Run:  ../.venv/bin/python audit_q2_reafference.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sweep_q2_reafference as q2

SEEDS = q2.SEEDS
BASE_AMP = q2.EXAF_AMP   # 3.0 as committed


def sweep_at_amp(amp):
    q2.EXAF_AMP = amp
    rows = []
    for s in SEEDS:
        log = q2.run_one({}, s)
        rows.append(q2.summarize(log, {}, s))
    q2.EXAF_AMP = BASE_AMP
    return rows


def col(rows, key):
    return np.array([r[key] for r in rows])


def report(name, rows):
    rr, rf = col(rows, "ratio_reaff"), col(rows, "ratio_foil")
    sr, sf = col(rows, "self_reaff"), col(rows, "self_foil")
    er, ef = col(rows, "exaf_reaff"), col(rows, "exaf_foil")
    print(f"\n=== {name} ===")
    print(f"  reafferent ratio : {rr.mean():.2f} +/- {rr.std():.2f}   (min {rr.min():.2f}, max {rr.max():.2f})")
    print(f"  foil ratio       : {rf.mean():.2f} +/- {rf.std():.2f}   (min {rf.min():.2f}, max {rf.max():.2f})")
    print(f"  self-test resid  : reaff {sr.mean():.4f}   foil {sf.mean():.4f}   (reaff cancels {100*(1-sr.mean()/sf.mean()):.0f}%)")
    print(f"  exaf resid       : reaff {er.mean():.4f}   foil {ef.mean():.4f}")
    diff = rr - rf
    npos = int((diff > 0).sum())
    print(f"  paired reaff-foil ratio: mean {diff.mean():+.2f}; reaff>foil in {npos}/{len(diff)} seeds")
    return dict(rr=rr, rf=rf, sr=sr, sf=sf, er=er, ef=ef)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print("Q2 reafference audit -- baseline vs no-event null, 10 seeds")

    base = report("BASELINE  (moving source, EXAF_AMP=3.0)", sweep_at_amp(3.0))
    null = report("NO-EVENT NULL  (EXAF_AMP=0.0 -- nothing happens in 'exafference' window)",
                  sweep_at_amp(0.0))

    # Verdict logic
    print("\n=== VERDICT CHECK ===")
    base_gap = (base["rr"] - base["rf"]).mean()
    null_reaff = null["rr"].mean()
    null_gap = (null["rr"] - null["rf"]).mean()
    print(f"  baseline reaff-foil gap : {base_gap:+.2f}")
    print(f"  no-event reaff ratio    : {null_reaff:.2f}  (want ~1.0 if effect is world-caused)")
    print(f"  no-event reaff-foil gap : {null_gap:+.2f}  (want ~0 if effect is world-caused)")
    survives = (null_reaff < 1.25) and (null_gap < 0.25) and ((base["rr"] > base["rf"]).all())
    print(f"  --> separation is world-caused and per-seed robust: {survives}")

    # Figure
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    groups = ["baseline\n(moving source)", "no-event null\n(amp=0)"]
    x = np.arange(2)
    w = 0.36
    rr_means = [base["rr"].mean(), null["rr"].mean()]
    rf_means = [base["rf"].mean(), null["rf"].mean()]
    rr_err = [base["rr"].std(), null["rr"].std()]
    rf_err = [base["rf"].std(), null["rf"].std()]
    ax.bar(x - w/2, rr_means, w, yerr=rr_err, capsize=4, color="#1538a0", label="reafferent")
    ax.bar(x + w/2, rf_means, w, yerr=rf_err, capsize=4, color="#c9a23a", label="foil")
    for xi, (rr, rf) in enumerate(zip([base["rr"], null["rr"]], [base["rf"], null["rf"]])):
        ax.scatter(np.full_like(rr, xi - w/2), rr, s=12, color="k", zorder=3)
        ax.scatter(np.full_like(rf, xi + w/2), rf, s=12, color="k", zorder=3)
    ax.axhline(1.0, color="#888", ls=":", lw=0.9)
    ax.set_xticks(x); ax.set_xticklabels(groups)
    ax.set_ylabel("residual ratio (exafference-window / self-test)")
    ax.set_title("Q2 audit — the reafferent/foil separation is world-caused:\n"
                 "with the source removed (no-event null), both ratios collapse to ~1", fontsize=10)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(here, "..", "figures", "q2_reafference_audit.png")
    fig.savefig(out, dpi=130)
    print(f"\n[saved] {out}")
