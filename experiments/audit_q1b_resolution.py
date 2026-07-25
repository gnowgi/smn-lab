# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Audit of Q1b (resolution = CAZ density) -- the scrutiny pass.

Q1b is where the resolution claim rests, and its own page already names the
mechanism: the modulated world-detection ratio rises ~sqrt(N) because averaging N
per-zone residuals drives an independent self-noise floor down ~1/sqrt(N). That
admission is exactly what makes the audit necessary, because the claim on the page
is the preprint's: *resolution is CAZ density x internal capacity, NOT raw
transducer count*. If the gain is pure sample-averaging, it is not about CAZs at
all -- the same failure mode that withdrew the S1 field-scale control (a decoder
-dimensionality artifact dressed as a resolution principle).

Three questions:

  (1) WORKING NULL -- no-tide control (EXAF_RATE = 0). With no world change the
      ratio must be ~1 and FLAT in segment count. If it still rises with N when
      nothing is happening, the rising trend is an aggregation artifact.

  (2) DENSITY vs COUNT-OF-AVERAGED-ZONES -- hold the body FIXED at n_seg=9 and
      aggregate the residual over only k = 3,5,7,9 evenly spaced zones. If the
      ratio-vs-k curve reproduces the ratio-vs-n_seg curve, then "resolution
      scales with CAZ density" is really "the read-out averaged more zones" --
      a property of the aggregation operator, not of the body.

  (3) NOT RAW TRANSDUCER COUNT -- hold CAZ count FIXED at n_seg=3 and multiply the
      RAW TRANSDUCERS per sensor site (n_rep = 1,3,9; averaging n_rep independent
      reads divides sensor noise by sqrt(n_rep)). The preprint's clause says this
      should NOT buy resolution. If the ratio rises with n_rep the way it rises
      with CAZ count, the clause fails on this bench.

Run:  ../.venv/bin/python audit_q1b_resolution.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sweep_q1b_resolution as q1b

N_SEGS = q1b.N_SEGS
SEEDS = q1b.SEEDS
KS = [3, 5, 7, 9]
REPS = [1, 3, 9]
BASE_RATE = q1b.EXAF_RATE


def run_cond(params, rate=None):
    if rate is not None:
        q1b.EXAF_RATE = rate
    rows = [q1b.summarize(q1b.run_one(params, s), params, s) for s in SEEDS]
    q1b.EXAF_RATE = BASE_RATE
    return {k: np.array([r[k] for r in rows]) for k in rows[0]}


def sweep_over(key, values, base, rate=None):
    return {v: run_cond({**base, key: v}, rate) for v in values}


def show(name, res, label):
    print(f"\n=== {name} ===")
    print(f"  {label:>8} |      ratio      | self_res | exaf_res")
    for v, d in res.items():
        print(f"  {v:>8} | {d['ratio'].mean():7.2f} +/-{d['ratio'].std():5.2f} "
              f"| {d['self_res'].mean():.5f}  | {d['exaf_res'].mean():.5f}")
    return res


def m(res, key="ratio"):
    return np.array([res[v][key].mean() for v in res])


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print(f"Q1b audit -- null + density-vs-averaging + transducer-count "
          f"({len(SEEDS)} seeds)")

    base_mod = show("BASELINE modulated (body grows)",
                    sweep_over("n_seg", N_SEGS, {"mode": "modulated"}), "n_seg")
    base_foil = show("BASELINE foil",
                     sweep_over("n_seg", N_SEGS, {"mode": "foil"}), "n_seg")
    null_mod = show("NO-TIDE NULL modulated (EXAF_RATE=0)",
                    sweep_over("n_seg", N_SEGS, {"mode": "modulated"}, rate=0.0), "n_seg")
    null_foil = show("NO-TIDE NULL foil (EXAF_RATE=0)",
                     sweep_over("n_seg", N_SEGS, {"mode": "foil"}, rate=0.0), "n_seg")
    subset = show("ZONE SUBSET  (body FIXED at n_seg=9; aggregate over k zones)",
                  sweep_over("k_zones", KS, {"n_seg": 9, "mode": "modulated"}), "k")
    trans = show("RAW TRANSDUCERS  (CAZ count FIXED at n_seg=3; n_rep reads per site)",
                 sweep_over("n_rep", REPS, {"n_seg": 3, "mode": "modulated"}), "n_rep")

    print("\n=== VERDICT CHECK ===")
    bm, nm = m(base_mod), m(null_mod)
    print(f"  baseline modulated ratio vs n_seg : {np.round(bm, 1)}  "
          f"(rise {bm[-1]/bm[0]:.2f}x, sqrt(3)=1.73)")
    print(f"  no-tide  modulated ratio vs n_seg : {np.round(nm, 2)}  (want ~1 and flat)")
    null_ok = bool(nm.max() < 2.0 and (nm[-1] / nm[0]) < 1.35)
    print(f"  --> the rise is world-caused, not an aggregation artifact: {null_ok}")

    sm = m(subset)
    print(f"\n  ratio vs BODY size  (n_seg 3->9, k=all)  : {np.round(bm, 1)}  "
          f"rise {bm[-1]/bm[0]:.2f}x")
    print(f"  ratio vs ZONES AVERAGED (body fixed n=9)  : {np.round(sm, 1)}  "
          f"rise {sm[-1]/sm[0]:.2f}x")
    density_is_extra = bool((bm[-1] / bm[0]) > 1.5 * (sm[-1] / sm[0]))
    print(f"  --> body density buys more than averaging more zones does: {density_is_extra}")
    print("      (if the two curves match, 'resolution = CAZ density' reduces to "
          "'the read-out averaged more zones')")

    tm = m(trans)
    print(f"\n  ratio vs RAW TRANSDUCERS (n_seg fixed 3, n_rep 1->9): {np.round(tm, 1)}  "
          f"rise {tm[-1]/tm[0]:.2f}x")
    not_transducers = bool((tm[-1] / tm[0]) < 1.25)
    print(f"  --> 'not raw transducer count' holds: {not_transducers}")

    print(f"\n  ==> null OK: {null_ok} | density beyond averaging: {density_is_extra} "
          f"| transducer clause holds: {not_transducers}")

    # ---- figure -------------------------------------------------------------
    ns = np.array(N_SEGS)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.8, 4.6))
    axA.plot(ns, bm, "-o", color="#1538a0", lw=1.9, label="modulated (tide present)")
    axA.plot(ns, m(base_foil), "-o", color="#c9a23a", lw=1.9, label="foil")
    axA.plot(ns, nm, "--s", color="#1538a0", lw=1.4, alpha=0.65,
             label="modulated, NO-TIDE null")
    axA.plot(ns, m(null_foil), "--s", color="#c9a23a", lw=1.4, alpha=0.65,
             label="foil, NO-TIDE null")
    axA.axhline(1.0, color="#888", ls=":", lw=0.9)
    axA.set_xticks(ns); axA.set_xlabel("segment count (CAZ density)")
    axA.set_ylabel("world-detection ratio")
    axA.legend(fontsize=8)
    axA.set_title("A — working null: with no tide the ratio sits at ~1 and does\n"
                  "not rise with density, so the trend is world-caused", fontsize=9.5)

    axB.plot(ns, bm / bm[0], "-o", color="#1538a0", lw=1.9,
             label="grow the BODY (CAZ density), 3→9")
    axB.plot(np.array(KS), sm / sm[0], "-o", color="#0f8a6a", lw=1.9,
             label="fixed 9-body, average k zones")
    axB.plot(3 * np.array(REPS), tm / tm[0], "-o", color="#b0334f", lw=1.9,
             label="fixed 3-body, ×1/×3/×9 raw transducers")
    ref = np.linspace(3, 27, 60)
    axB.plot(ref, np.sqrt(ref / 3.0), ":", color="#555", lw=1.2, label="√N reference")
    axB.axhline(1.0, color="#888", ls=":", lw=0.8)
    axB.set_xscale("log")
    axB.minorticks_off()
    axB.set_xticks([3, 5, 7, 9, 15, 27])
    axB.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axB.annotate("9 raw reads:\n9 CAZs ≈ 3 CAZs × 3 transducers",
                 xy=(9, tm[1] / tm[0]), xytext=(9.6, 1.15), fontsize=7.5,
                 arrowprops=dict(arrowstyle="->", lw=0.8, color="#444"))
    axB.set_xlabel("independent samples aggregated (zones × transducers per zone)")
    axB.set_ylabel("ratio, normalised to the 3-zone value")
    axB.legend(fontsize=8, loc="upper left")
    axB.set_title("B — is it density, or just averaging more samples?\n"
                  "the three ways of adding samples, on one axis", fontsize=9.5)
    fig.suptitle("Q1b audit — separating the resolution principle from "
                 "noise-averaging", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(here, "..", "figures", "sweep_q1b_resolution_audit.png")
    fig.savefig(out, dpi=130)
    print(f"\n[saved] {out}")
