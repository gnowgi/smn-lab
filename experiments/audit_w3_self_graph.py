# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Audit of W3 (reafference cut in the self-graph frame) -- scrutiny pass.

W3 as committed is SINGLE-SEED (default_rng(0)), which the repo's own ground rules
(test-plan.md: "replicated seeds with reported spread, not single runs") say to
avoid. This audit does three things a skeptic asks before the row moves off
'not yet audited':

  (1) REPLICATE -- run 10 seeds and report spread on the discriminability and
      localization headline numbers (21.5x, node 5.3 were one seed).

  (2) WORKING NULL -- no-event control (exaf_on=False): the exafference source B
      never fades in, so the "exafference" window is pure self-motion. If the
      reafferent discriminability > 1 is genuinely world-caused, it must collapse
      to ~1; and the localizer must NOT keep pointing at node 6 when nothing is
      there.

  (3) LOCALIZATION SPECIFICITY -- move the world change to node 2 (b_node=2) and
      confirm the reafferent centroid follows to ~2, i.e. the localizer reads the
      world, not a fixed bias toward high node indices.

Run:  ../.venv/bin/python audit_w3_self_graph.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import reafference_cut_self_graph as w3

SEEDS = list(range(10))
T_EXAF = w3.T_EXAF


def summarize(log, b_node):
    m1 = log["phase"] == 1
    m2 = log["phase"] == 2
    t2 = log["t"][m2]
    steady = m2 & (log["t"] >= t2[0] + 0.5 * T_EXAF)     # after the ramp
    reaf_self = log["reaf"][m1].mean()
    reaf_exaf = log["reaf"][steady].mean()
    naive_self = log["naive"][m1].mean()
    naive_exaf = log["naive"][steady].mean()
    loc = log["reaf_node"][steady]
    return dict(
        reaf_self=float(reaf_self), reaf_exaf=float(reaf_exaf),
        disc_reaf=float(reaf_exaf / max(reaf_self, 1e-12)),
        naive_self=float(naive_self), naive_exaf=float(naive_exaf),
        disc_naive=float(naive_exaf / max(naive_self, 1e-12)),
        loc_mean=float(np.nanmean(loc)),
        loc_err=float(np.nanmean(np.abs(loc - b_node))),
    )


def col(rows, k):
    return np.array([r[k] for r in rows])


def block(name, rows, b_node):
    dr, dn = col(rows, "disc_reaf"), col(rows, "disc_naive")
    rs = col(rows, "reaf_self"); re = col(rows, "reaf_exaf")
    lm, le = col(rows, "loc_mean"), col(rows, "loc_err")
    print(f"\n=== {name} ===")
    print(f"  reaf detector : self-motion {rs.mean():.3f} +/- {rs.std():.3f}   exaf {re.mean():.3f} +/- {re.std():.3f}")
    print(f"  discriminability: reaf {dr.mean():.1f} +/- {dr.std():.1f}   naive {dn.mean():.1f} +/- {dn.std():.1f}")
    print(f"  reaf > naive discriminability in {int((dr>dn).sum())}/{len(dr)} seeds")
    print(f"  localization  : node {lm.mean():.1f} +/- {lm.std():.1f}   (true {b_node}, err {le.mean():.2f})")
    return dict(dr=dr, dn=dn, rs=rs, re=re, lm=lm, le=le)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print("W3 audit -- replicate + no-event null + localization specificity")

    base = block("BASELINE  (10 seeds, source B fades in at node 6)",
                 [summarize(w3.run(seed=s, exaf_on=True), w3.B_NODE) for s in SEEDS],
                 w3.B_NODE)
    null = block("NO-EVENT NULL  (exaf_on=False -- B never appears)",
                 [summarize(w3.run(seed=s, exaf_on=False), w3.B_NODE) for s in SEEDS],
                 w3.B_NODE)
    swap = block("LOCALIZATION SWAP  (world change moved to node 2)",
                 [summarize(w3.run(seed=s, exaf_on=True, b_node=2), 2) for s in SEEDS],
                 2)

    print("\n=== VERDICT CHECK ===")
    null_disc = null["dr"].mean()
    print(f"  baseline reaf discriminability : {base['dr'].mean():.1f}")
    print(f"  no-event reaf discriminability : {null_disc:.1f}   (want ~1 if world-caused)")
    print(f"  localization node6 (base) {base['lm'].mean():.1f} vs node2 (swap) {swap['lm'].mean():.1f}"
          f"  -> follows world: {swap['lm'].mean() < base['lm'].mean() - 1.5}")
    survives = (null_disc < 2.0) and (base["dr"].mean() > base["dn"].mean()) \
        and (swap["lm"].mean() < base["lm"].mean() - 1.5)
    print(f"  --> discriminability world-caused, reaf beats naive, localizer tracks: {survives}")

    # Figure: discriminability baseline vs null; localization base vs swap
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.0, 4.4))
    x = np.arange(2); w = 0.36
    axA.bar(x - w/2, [base["dr"].mean(), null["dr"].mean()], w,
            yerr=[base["dr"].std(), null["dr"].std()], capsize=4, color="#1538a0", label="reafferent")
    axA.bar(x + w/2, [base["dn"].mean(), null["dn"].mean()], w,
            yerr=[base["dn"].std(), null["dn"].std()], capsize=4, color="#c9a23a", label="naive")
    axA.axhline(1.0, color="#888", ls=":", lw=0.9)
    axA.set_xticks(x); axA.set_xticklabels(["baseline\n(source fades in)", "no-event null\n(no source)"])
    axA.set_ylabel("discriminability (exafference / self-motion)")
    axA.set_title("A — discriminability collapses to ~1 with no world event", fontsize=10)
    axA.legend()

    axB.axhline(6, color="#1538a0", ls="--", lw=1, alpha=0.6)
    axB.axhline(2, color="#c9a23a", ls="--", lw=1, alpha=0.6)
    axB.scatter(np.zeros(len(base["lm"])), base["lm"], color="#1538a0", s=22, label="true node 6")
    axB.scatter(np.ones(len(swap["lm"])), swap["lm"], color="#c9a23a", s=22, label="true node 2")
    axB.set_xticks([0, 1]); axB.set_xticklabels(["B at node 6", "B at node 2"])
    axB.set_ylabel("localized self-graph node"); axB.set_ylim(0, 8)
    axB.set_title("B — the localizer tracks where the world changed", fontsize=10)
    axB.legend(fontsize=8)
    fig.suptitle("W3 audit — self-graph reafference cut: world-caused and localizing", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(here, "..", "figures", "reafference_cut_self_graph_audit.png")
    fig.savefig(out, dpi=130)
    print(f"\n[saved] {out}")
