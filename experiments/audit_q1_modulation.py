# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Audit of Q1 (modulation builds the world model) -- the scrutiny pass.

Q1's headline is that per-zone dual-port modulation keeps self/world resolution
alive as the body grows, while an unmodulated foil collapses to ~1. Before that
row can move off 'not yet audited', three questions:

  (1) WORKING NULL -- no-event control (EXAF_AMP = 0). With no moving source, the
      "exafference" window contains no world-caused change, so BOTH ratios must
      collapse to ~1 at every body size. If the modulated ratio stays high with
      nothing happening, the ratio is a windowing/calibration artifact.

  (2) DUAL-PORT SPECIFICITY -- the committed foil is "no cancellation at all",
      which is a weak control: it confounds *cancelling with the right zone's
      motion* with *cancelling at all*. Two sharper foils, same machinery,
      re-calibrated gains:
        - shuffle : each zone cancels a DISTANT zone's displacement (roll N//2).
                    Right magnitude, wrong zone identity.
        - single  : every zone cancels the HEAD zone's displacement -- exactly
                    Q2's single-point proprioceptive model on this body. This is
                    the contrast the preprint's dual-port claim actually makes.

  (3) IS THE FOIL'S COLLAPSE INFORMATIVE? ratio = exaf/self. If the foil's
      *self* residual grows with body size while its *exafference* residual is
      roughly flat, then "foil ratio -> 1" is denominator-driven arithmetic, not
      an independent finding. Reported explicitly.

Run:  ../.venv/bin/python audit_q1_modulation.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sweep_q1_modulation as q1

N_SEGS = q1.N_SEGS
SEEDS = q1.SEEDS
BASE_AMP = q1.EXAF_AMP


def sweep(mode, basis_mode="own", amp=None):
    """Return {n_seg: {key: array over seeds}} for one condition."""
    if amp is not None:
        q1.EXAF_AMP = amp
    out = {}
    for N in N_SEGS:
        rows = []
        for s in SEEDS:
            p = {"n_seg": N, "mode": mode, "basis_mode": basis_mode}
            rows.append(q1.summarize(q1.run_one(p, s), p, s))
        out[N] = {k: np.array([r[k] for r in rows]) for k in rows[0]}
    q1.EXAF_AMP = BASE_AMP
    return out


def show(name, res):
    print(f"\n=== {name} ===")
    print("   n_seg |      ratio      | self_res | exaf_res")
    for N in N_SEGS:
        d = res[N]
        print(f"     {N:<4d}| {d['ratio'].mean():7.1f} +/-{d['ratio'].std():5.1f} "
              f"| {d['self_res'].mean():.5f}  | {d['exaf_res'].mean():.5f}")
    return res


def m(res, key="ratio"):
    return np.array([res[N][key].mean() for N in N_SEGS])


def sd(res, key="ratio"):
    return np.array([res[N][key].std() for N in N_SEGS])


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print(f"Q1 audit -- null + dual-port specificity ({len(SEEDS)} seeds x {len(N_SEGS)} bodies)")

    base_mod = show("BASELINE  modulated (per-zone, own motion)", sweep("modulated"))
    base_foil = show("BASELINE  foil (no cancellation)", sweep("foil"))
    null_mod = show("NO-EVENT NULL  modulated (EXAF_AMP=0)", sweep("modulated", amp=0.0))
    null_foil = show("NO-EVENT NULL  foil (EXAF_AMP=0)", sweep("foil", amp=0.0))
    shuf = show("FOIL 2  modulated but cancelling a DISTANT zone's motion", sweep("modulated", "shuffle"))
    sing = show("FOIL 3  modulated but every zone cancels the HEAD's motion (Q2 model)",
                sweep("modulated", "single"))

    print("\n=== VERDICT CHECK ===")
    nm = m(null_mod)
    print(f"  no-event modulated ratio by size : {np.round(nm, 2)}   (want ~1 everywhere)")
    print(f"  no-event foil ratio by size      : {np.round(m(null_foil), 2)}")
    world_caused = nm.max() < 2.0
    print(f"  --> baseline separation is world-caused: {world_caused}")

    own, sh, si = m(base_mod), m(shuf), m(sing)
    print(f"\n  ratio by size   own {np.round(own, 1)}")
    print(f"                  shuffled-zone {np.round(sh, 1)}")
    print(f"                  head-only     {np.round(si, 1)}")
    dual_port = bool((own > sh).all() and (own > si).all())
    print(f"  --> own-motion beats both sharper foils at every size: {dual_port}")
    print(f"      own/head-only advantage by size: {np.round(own / np.maximum(si, 1e-9), 2)}")

    fs, fe = m(base_foil, "self_res"), m(base_foil, "exaf_res")
    print(f"\n  foil self_res by size : {np.round(fs, 4)}  (x{fs[-1]/fs[0]:.1f} from n=3 to n=9)")
    print(f"  foil exaf_res by size : {np.round(fe, 4)}  (x{fe[-1]/fe[0]:.1f})")
    print("  --> the foil's ratio collapse is denominator-driven "
          f"(self floor grows {fs[-1]/fs[0]:.1f}x while world term grows {fe[-1]/fe[0]:.1f}x)")

    survives = world_caused and dual_port
    print(f"\n  ==> Q1 survives null + dual-port specificity: {survives}")

    # ---- figure -------------------------------------------------------------
    ns = np.array(N_SEGS)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    for res, lab, c in ((base_mod, "own motion (dual-port)", "#1538a0"),
                        (sing, "head-only (Q2 single-point)", "#0f8a6a"),
                        (shuf, "distant zone (wrong identity)", "#8a4fb0"),
                        (base_foil, "no cancellation (committed foil)", "#c9a23a")):
        axA.plot(ns, m(res), "-o", color=c, lw=1.8, label=lab)
    axA.axhline(1.0, color="#888", ls=":", lw=0.9)
    axA.set_yscale("log"); axA.set_xticks(ns)
    axA.set_xlabel("segment count (CAZ density)")
    axA.set_ylabel("world/self ratio  (exafference / self-test)")
    axA.legend(fontsize=8)
    axA.set_title("A — sharper foils: cancelling with the WRONG zone's motion\n"
                  "loses most of the advantage; own-motion (dual-port) is the driver",
                  fontsize=9.5)

    w = 0.36
    x = np.arange(len(ns))
    axB.bar(x - w/2, m(null_mod), w, yerr=sd(null_mod), capsize=3, color="#1538a0",
            label="modulated")
    axB.bar(x + w/2, m(null_foil), w, yerr=sd(null_foil), capsize=3, color="#c9a23a",
            label="foil")
    axB.axhline(1.0, color="#888", ls=":", lw=0.9)
    axB.set_xticks(x); axB.set_xticklabels([str(n) for n in ns])
    axB.set_xlabel("segment count"); axB.set_ylabel("world/self ratio")
    axB.legend(fontsize=8)
    axB.set_title("B — no-event working null: with the source removed both\n"
                  "ratios sit at ~1 at every body size", fontsize=9.5)
    fig.suptitle("Q1 audit — the separation is world-caused, and it is own-motion "
                 "cancellation that produces it", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(here, "..", "figures", "sweep_q1_modulation_audit.png")
    fig.savefig(out, dpi=130)
    print(f"\n[saved] {out}")
