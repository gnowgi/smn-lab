# scratch: does the self-model betweenness change with recording length? (disk only)
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diploblast_disk_self_model as M
from smn_lab.metrics import endpoint_recovery
from smn_lab.report import RunRecord, recover as report_recover

DURATIONS = [2, 4, 8, 16, 32, 64]      # seconds of babbling recorded
SEEDS = [0, 1, 2]

pos, edges, cls, layout, ring, ix, tent = M.disk_spec(False)
cls = np.array(cls)
n = len(pos)
rows = []
for T in DURATIONS:
    M.T_REC = float(T)
    ratios, rims, ints, recs = [], [], [], []
    for s in SEEDS:
        m, d, bid = M.build(pos, edges, "disk")
        C = M.babble(m, d, bid, s)
        er = float(endpoint_recovery(C, edges))
        rec = report_recover(RunRecord(name="d", coupling_matrix=C, recovery="endpoint",
                                       positions=layout, true_edges=edges))
        bt = M.betweenness(M.adjacency(rec["rec_edges"], n))
        btv = np.array([bt[i] for i in range(n)])
        rim = btv[cls == "rim"].mean(); inr = btv[cls == "interior"].mean()
        ratios.append(rim / (inr + 1e-9)); rims.append(rim); ints.append(inr); recs.append(er)
    rows.append((T, np.mean(recs), np.std(recs), np.mean(ratios), np.std(ratios),
                 np.mean(rims), np.std(rims)))
    print(f"T={T:>3}s  steps={int(T/M.DT):>6}  recovery={np.mean(recs):.3f}+/-{np.std(recs):.3f}  "
          f"rim/interior={np.mean(ratios):.2f}+/-{np.std(ratios):.2f}  "
          f"rim_bt={np.mean(rims):.3f}+/-{np.std(rims):.3f}")

R = np.array(rows)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
ax[0].errorbar(R[:, 0], R[:, 1], yerr=R[:, 2], marker="o", color="#2c7fb8", capsize=3)
ax[0].set_xscale("log", base=2); ax[0].set_xlabel("recording length (s)")
ax[0].set_ylabel("self-model recovery"); ax[0].set_ylim(0, 1.02)
ax[0].set_title("recovery fidelity vs run length"); ax[0].grid(alpha=0.3)
ax[1].errorbar(R[:, 0], R[:, 3], yerr=R[:, 4], marker="o", color="#c0392b", capsize=3)
ax[1].axhline(1.8, ls="--", color="0.5", lw=1, label="true-graph ratio ~ 1.8")
ax[1].set_xscale("log", base=2); ax[1].set_xlabel("recording length (s)")
ax[1].set_ylabel("rim / interior betweenness"); ax[1].set_title("rim prominence vs run length")
ax[1].legend(); ax[1].grid(alpha=0.3)
fig.suptitle("Two-layer disk: the self-model stabilizes with run length (3 seeds), it does not drift",
             fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.95))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                   "disk_convergence.png")
fig.savefig(out, dpi=130); print("figure ->", os.path.normpath(out))
