# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Demo of the standardized one-page experiment figure (`smn_lab.report.experiment_page`).

Fills the template for the diploblastic Hydra sac: body plan, world (a moving prey), the
self-model recovered from movement, the world-model (canvas), and the data plots -- all in
the diagram grammar, on a single page-length figure for the paper.

Run:  ../.venv/bin/python experiment_page_demo.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab.metrics import endpoint_recovery
from smn_lab.report import RunRecord, experiment_page
from hydra_sac import build, touch, N_COL, N_ROW, NOUT
from two_networks_dissociation import babble, coupling3


def io(r, c): return r * N_COL + c
def ii(r, c): return NOUT + r * N_COL + c


def main():
    m, d, bid, pos, edges, roles, ix = build()
    io_, ii_, out_apex, in_apex = ix
    DRV, VX, VY, VZ = babble(m, d, bid, m.nu, seed=0)
    C = coupling3(DRV, VX, VY, VZ)
    er = float(endpoint_recovery(C, edges))

    k = io(2, N_COL // 2)                       # a prey contact on the ectoderm
    resp, over = touch(m, d, bid, k, np.random.default_rng(3))
    loc = int(np.argmax(resp) == k)
    node_field = {i: float(resp[i]) for i in range(len(bid))}

    # 2-D unrolled layout for the body panel (outer grid over inner grid + apexes)
    pos2d = {}
    for r in range(N_ROW):
        for c in range(N_COL):
            pos2d[io(r, c)] = (-c, r); pos2d[ii(r, c)] = (-c, r - (N_ROW + 1))
    pos2d[out_apex] = (-(N_COL + 0.4), (N_ROW - 1) / 2)
    pos2d[in_apex] = (-(N_COL + 0.4), (N_ROW - 1) / 2 - (N_ROW + 1))
    mouth = [io(r, 0) for r in range(N_ROW)]

    def world_draw(ax):
        # the pond: the sessile sac (faint), the mouth, and a MOVING prey at the contact
        for a, b in edges:
            ax.plot([pos2d[a][0], pos2d[b][0]], [pos2d[a][1], pos2d[b][1]],
                    color="#e3e8ee", lw=0.6, zorder=1)
        xs = [pos2d[i][0] for i in range(len(bid))]; ys = [pos2d[i][1] for i in range(len(bid))]
        ax.scatter(xs, ys, s=8, color="#c4cdd6", zorder=2)
        ax.scatter([pos2d[i][0] for i in mouth], [pos2d[i][1] for i in mouth],
                   s=22, color="#27ae60", zorder=3, label="mouth")
        px, py = pos2d[k]
        ax.annotate("", xy=(px, py), xytext=(px + 1.4, py + 1.1),
                    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.6))
        ax.scatter([px + 1.4], [py + 1.1], s=90, color="#c0392b", edgecolor="k", zorder=5)
        ax.text(px + 1.6, py + 1.2, "moving prey", fontsize=8, color="#c0392b", va="center")
        ax.scatter([px], [py], s=70, facecolor="none", edgecolor="#c0392b", lw=1.8, zorder=5)
        ax.text(0.5, -0.02, "a water-flea (moving mass beyond threshold) contacts an ectoderm zone",
                transform=ax.transAxes, ha="center", va="top", fontsize=7.5, color="#556")
        ax.set_aspect("equal"); ax.axis("off"); ax.legend(loc="lower left", fontsize=7, frameon=False)

    def plots_draw(fig, cell):
        sub = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=cell, wspace=0.28)
        a0 = fig.add_subplot(sub[0]); a1 = fig.add_subplot(sub[1])
        # localization: per-zone response, peak at the contact
        order = np.argsort(resp)[::-1]
        a0.bar(range(len(resp)), resp[np.argsort(resp)[::-1]] if False else resp, color="#8aa0b6")
        a0.bar([k], [resp[k]], color="#c0392b")
        a0.set_title("localization: response per zone (peak = contact)", fontsize=9)
        a0.set_xlabel("zone"); a0.set_ylabel("response"); a0.grid(alpha=0.25, axis="y")
        # the touch as it propagates in time at a few zones (the world-signal)
        t = np.arange(over.shape[0]) * 0.002
        a1.plot(t, over[:, k], color="#c0392b", lw=1.8, label=f"contact zone {k}")
        a1.plot(t, over[:, mouth].mean(1), color="#27ae60", lw=1.6, label="mouth ring")
        a1.plot(t, over.mean(1), color="#5b7089", lw=1.2, label="whole body")
        a1.set_title("the touch propagating (world-signal in time)", fontsize=9)
        a1.set_xlabel("time (s)"); a1.set_ylabel("response"); a1.legend(fontsize=7); a1.grid(alpha=0.25)
        a0.text(-0.14, 1.12, "5 · Data (order parameters)", transform=a0.transAxes,
                fontsize=10, fontweight="normal")

    experiment_page(
        RunRecord(name="Hydra sac — prey touch, localization & broadcast",
                  coupling_matrix=C, recovery="endpoint",
                  positions=pos2d, true_edges=edges,
                  node_field=node_field, world_signal=over, modality="touch",
                  metrics={"endpoint_recovery": er, "localization": float(loc)}),
        spec=dict(prefix="hydra_sac",
                  description=("Sessile two-layer sac (ectoderm/endoderm, nerve net in the mesoglea). A moving "
                               "prey contacts one ectoderm zone; the net recovers its body from movement, "
                               "localizes the touch, and integrates the world-signal into the canvas."),
                  world_draw=world_draw, plots_draw=plots_draw))


if __name__ == "__main__":
    main()
