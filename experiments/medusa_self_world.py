# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The medusa's one-page figure: body plan, world, self-model, world-model, data.

Brings the medusa into the same standardized page the Hydra sac and the disk use
(:func:`smn_lab.report.experiment_page`), with one deliberate difference in panel 4.

* **Body plan / self-model.** The bell + tentacle ``f`` scaffold of
  :func:`smn_lab.medusa.medusa_spec`, and its self-model recovered from movement
  alone: the disk's babble (Ornstein-Uhlenbeck drive on every pull-only ``f``, no
  medium) and the same ``endpoint`` read-out -- so the medusa's recovery is directly
  comparable with the disk's.

* **World-model -- the order parameter itself, not a proxy.** The medusa's
  world-model is not a per-zone world signal (as in the Hydra sac); it is the held-out
  **decodability of the source's location** from the tip transducers'
  *self-caused change* (``experiments/medusa_world_model.py``). The default panel 4
  would paint the raw time-mean tip reading on the self-graph, which is exactly the
  quantity ``read_source`` excludes -- a sessile animal's tips still register the
  source, so that panel would show the sessile medusa "localizing" it, contradicting
  the razor. Panel 4 here therefore draws **decoded vs true source location** on the
  held-out trials, sessile (alpha = 0) beside swimming (alpha = max).

* **Scoring caveat, recorded rather than fixed here.**
  ``smn_lab.metrics.decoding_skill`` measures error with ``np.hypot(*(pred - P).T)``.
  For 3-D positions NumPy reads the third column as hypot's ``out`` buffer, so the
  published skill scores **horizontal (x-y) error only**; the vertical (swim-axis)
  error is dropped. This script reproduces the published x-y numbers exactly (the
  check that nothing else changed) and reports the full 3-D skill beside them.
  Panel 4 is drawn in top view because that is what the published number measures.

Run:  ../.venv/bin/python medusa_self_world.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE)); sys.path.insert(0, _HERE)
from smn_lab.medusa import medusa_spec, build_medusa
from smn_lab.self_model import coupling
from smn_lab.metrics import endpoint_recovery, decoding_skill
from smn_lab.report import RunRecord, experiment_page, render
import medusa_world_model as mw                     # the experiment of record -- reused, not copied

# babble settings: the disk's (diploblast_disk_self_model.py), so recovery is comparable
B_DT, T_WARM, T_REC, U_TC, U_SIG, SEED = 0.002, 2.0, 22.0, 0.15, 5.0, 0
K = 8                                                # kNN k, as in medusa_world_model


# ------------------------------------------------------------------ self-model ----
def babble_coupling(sp):
    m, d, bid = build_medusa(sp, cmax=mw.CMAX, seg_damp=mw.SEG_DAMP, lat_stiff=mw.LAT_STIFF)
    m.opt.timestep = B_DT
    rng = np.random.default_rng(SEED)
    nl, ns = m.nu, len(bid)
    nw, nr = int(T_WARM / B_DT), int(T_REC / B_DT)
    u = np.zeros(nl); DRV = np.zeros((nr, nl)); V = np.zeros((3, nr, ns))
    d.qpos[:] = 0; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    for i in range(nw + nr):
        u += (-u / U_TC) * B_DT + U_SIG * np.sqrt(B_DT) * rng.standard_normal(nl)
        ud = np.clip(u, 0.0, None)                   # pull-only f
        d.ctrl[:] = ud; mujoco.mj_step(m, d)
        if i >= nw:
            j = i - nw; DRV[j] = ud; V[:, j] = d.qvel.reshape(-1, 3).T
    V -= V.mean(2, keepdims=True)
    return sum(np.abs(coupling(DRV, V[k])) for k in range(3))


# ----------------------------------------------------------------- world-model ----
def trials(traj):
    """The exact trial set of ``mw.world_model_skill`` (same RNG stream, same order),
    returned so the held-out predictions can be drawn."""
    rng = np.random.default_rng(mw.SEED + 1)
    feats, locs = [], []
    for _ in range(mw.N_TRIAL):
        u = rng.standard_normal(3); u /= np.linalg.norm(u) + 1e-9
        dist = rng.uniform(mw.SRC_DMIN, mw.SRC_DMAX)
        src = u * dist + np.array([0, 0, 0.1])
        amp = rng.uniform(0.6, 1.4)
        feats.append(mw.read_source(traj, src, amp, rng)); locs.append(src)
    S, P = np.array(feats), np.array(locs)
    order = rng.permutation(len(S))
    return S[order], P[order]


def knn_predict(S, P):
    """decoding_skill's split and predictor, verbatim, exposing the predictions."""
    cut = int(0.6 * len(S))
    Str, Ptr, Ste, Pte = S[:cut], P[:cut], S[cut:], P[cut:]
    mu, sd = Str.mean(0), Str.std(0) + 1e-9
    A, B = (Str - mu) / sd, (Ste - mu) / sd
    idx = np.argsort(((B[:, None] - A[None]) ** 2).sum(-1), axis=1)[:, :K]
    return Ptr[idx].mean(1), Pte, Ptr


def skills(pred, Pte, Ptr):
    def sk(dims):
        mae = np.linalg.norm((pred - Pte)[:, dims], axis=1).mean()
        naive = np.linalg.norm((Pte - Ptr.mean(0))[:, dims], axis=1).mean()
        return 1.0 - mae / max(naive, 1e-9)
    return sk([0, 1]), sk([0, 1, 2])


def main():
    sp = medusa_spec(z_apex=mw.Z_APEX)
    n = len(sp["pos"])

    C = babble_coupling(sp)
    er = float(endpoint_recovery(C, sp["edges"]))

    rows, draw = [], {}
    for a in mw.ALPHAS:
        traj = mw.tip_trajectory(a)
        S, P = trials(traj)
        pred, Pte, Ptr = knn_predict(S, P)
        s_xy, s_3d = skills(pred, Pte, Ptr)
        published = float(decoding_skill(S, P, np.random.default_rng(7), k=K))
        assert abs(published - s_xy) < 1e-9, "x-y skill must reproduce decoding_skill exactly"
        shuf = float(decoding_skill(S, P, np.random.default_rng(7), k=K, shuffle=True))
        rows.append((a, s_xy, s_3d, shuf))
        if a in (mw.ALPHAS[0], mw.ALPHAS[-1]):
            draw[a] = (pred, Pte, Ptr, s_xy)

    print("\nmedusa — self-model and world-model\n" + "=" * 60)
    print(f"{n} segments, {len(sp['edges'])} f-links; self-model endpoint recovery = {er:.2f}")
    print(f"\n{'alpha':>7}{'skill x-y (published)':>24}{'skill 3-D':>12}{'shuffle':>10}")
    for a, sxy, s3, sh in rows:
        print(f"{a:>7.1f}{sxy:>24.2f}{s3:>12.2f}{sh:>10.2f}")
    print("=" * 60)

    a0, a1 = mw.ALPHAS[0], mw.ALPHAS[-1]
    tips = set(sp["tips"]); tent = {i for i in range(n) if sp["node_kind"][i] in ("tentacle", "tip")}
    lay = sp["layout"]; R = float(np.max(np.hypot(*np.array(list(lay.values())).T)))

    def body_outline(ax, alpha=1.0):
        for (u, v), k in zip(sp["edges"], sp["edge_kind"]):
            (x0, y0), (x1, y1) = lay[u], lay[v]
            ax.plot([x0, x1], [y0, y1], color="#8fb3d1" if k != "brace" else "#d3dde6",
                    lw=1.0, alpha=alpha, zorder=1)
        xy = np.array([lay[i] for i in sorted(tips)])
        ax.scatter(*xy.T, s=26, color="#e0902a", edgecolor="#5a3a10", zorder=3,
                   alpha=alpha, label="tip transducers")

    def world_draw(ax):
        _, Pte, Ptr, _ = draw[a1]
        body_outline(ax)
        ax.scatter(*Ptr[:, :2].T, s=10, color="#b9c3cc", label="training sources", zorder=2)
        ax.scatter(*Pte[:, :2].T, s=16, color="#2a7a4b", label="held-out sources", zorder=2)
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color("#dde3e8")
        ax.legend(fontsize=6.5, loc="upper left", frameon=False, bbox_to_anchor=(1.0, 1.0))
        ax.text(1.03, 0.0, f"{mw.N_TRIAL} sources in 3-D, d∈[{mw.SRC_DMIN},{mw.SRC_DMAX}],\n"
                "random strength — top view", transform=ax.transAxes, ha="left",
                va="bottom", fontsize=6.5, color="#5b6b78")

    def worldmodel_draw(fig, cell):
        sub = cell.subgridspec(1, 2, wspace=0.06)
        lim = mw.SRC_DMAX * 1.08
        for j, a in enumerate((a0, a1)):
            ax = fig.add_subplot(sub[0, j])
            pred, Pte, _, sxy = draw[a]
            body_outline(ax, alpha=0.35)
            for p, t in zip(pred, Pte):
                ax.plot([t[0], p[0]], [t[1], p[1]], color="#c0392b", lw=0.8, alpha=0.7, zorder=2)
            ax.scatter(*Pte[:, :2].T, s=14, color="#2a7a4b", zorder=3)
            ax.scatter(*pred[:, :2].T, s=10, marker="x", color="#c0392b", zorder=4)
            ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values(): s.set_color("#dde3e8")
            ax.set_title(f"4{'ab'[j]} · {'sessile' if a == 0 else 'swimming'}, α={a:g}\n"
                         f"skill (x-y) = {sxy:.2f}", fontsize=8.5,
                         color="#c0392b" if a == 0 else "#1f5f3a")
            ax.set_xlabel("decoded ×  vs  true ●  (held-out, top view)" if j == 0 else
                          "4 · World-model", fontsize=7.5, color="#5b6b78")

    def plots_draw(fig, cell):
        sub = cell.subgridspec(1, 2, wspace=0.28)
        A = [r[0] for r in rows]
        ax = fig.add_subplot(sub[0, 0])
        ax.plot(A, [r[1] for r in rows], "o-", color="#2c6fbb", lw=2, label="skill, x-y (published)")
        ax.plot(A, [r[2] for r in rows], "^-", color="#7d4fb3", lw=1.6, label="skill, 3-D")
        ax.plot(A, [r[3] for r in rows], "s--", color="#999999", lw=1.3, label="shuffle control")
        ax.axvspan(-0.3, 0.3, color="#c0392b", alpha=0.10)
        ax.axhline(0, color="#bbbbbb", lw=0.8)
        ax.set_xlabel("self-motion amplitude α  (control parameter)", fontsize=8.5)
        ax.set_ylabel("world-model skill  (order parameter)", fontsize=8.5)
        ax.set_title("5 · Data — the razor", fontsize=10); ax.legend(fontsize=7); ax.grid(alpha=0.3)
        ax = fig.add_subplot(sub[0, 1]); ax.axis("off")
        ax.text(0.0, 0.95,
                "Self-model: the disk's babble, endpoint read-out\n"
                f"  endpoint recovery = {er:.2f}\n\n"
                "World-model: held-out kNN decoding of source\n"
                "location from tip self-caused change only\n"
                "(range and drift; the static mean excluded).\n\n"
                "Scoring caveat: metrics.decoding_skill scores\n"
                "x-y error only (np.hypot with three columns).\n"
                "The 3-D curve is the full error.",
                va="top", fontsize=7.8, family="monospace", color="#33414f")

    rec = RunRecord(name="medusa", coupling_matrix=C, recovery="endpoint",
                    positions=lay, true_edges=sp["edges"],
                    metrics={"endpoint_recovery": er,
                             "skill_xy_sessile": rows[0][1], "skill_xy_swim": rows[-1][1],
                             "skill_3d_swim": rows[-1][2]},
                    meta={"tentacle_nodes": sorted(tent), "tips": sorted(tips)})
    render(rec, dict(prefix="medusa", suptitle="Medusa — designed body and recovered self-model",
                     op_plot=False))
    experiment_page(rec, dict(
        prefix="medusa",
        description="A shallow-dome bell (3 rings × 8 spokes) with six 4-segment tentacles; "
                    "pull-only f on every link. Self-model from babble; world-model = "
                    "decodability of a hidden source's location from the tips' self-caused change.",
        world_draw=world_draw, worldmodel_draw=worldmodel_draw, plots_draw=plots_draw))


if __name__ == "__main__":
    main()
