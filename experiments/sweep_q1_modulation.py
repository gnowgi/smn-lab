# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Q1 -- modulation makes resolution scale with CAZ density. Pre-registered.

Q2 showed reafference works on the crawler but only partially, because a single
head-velocity proprioceptive signal cannot predict how DISTRIBUTED sensors move on
a BENDING body. The SMN preprint's answer is the **dual-port modulator**: each
zone *both measures and moves*, sensing ITS OWN motion. This experiment builds
exactly that -- **distributed, per-zone reafference** -- and tests the resolution
principle: resolution is CAZ density x internal capacity, not raw transducer count.

Mechanism + provenance: distributed dual-port modulators (each CAZ predicts its own
reafferent consequence from its own sensed velocity and local gradient). This is
the preprint's modulator (arXiv:2605.26856, hm-new-plan: "by both measuring and
moving, modulators implement the reafference principle in the body itself"). The
per-zone implementation is ours, declared.

The prediction (resolution principle), made precise:
- With per-zone **modulation**, each zone cancels its own self-motion, so its
  residual is ~independent noise; averaging N zones drives the noise down ~1/sqrt(N)
  while the world-caused term (seen by all) survives -> world-detection improves
  with zone count.
- Without modulation (**foil**), the uncancelled self-motion term is correlated
  across zones and does NOT average out -> no improvement with zone count.

Order parameter: world/self ratio = mean|aggregate residual| (exafference /
self-test). Pass: the modulated ratio RISES with segment count and exceeds the
foil; the foil stays flat. Falsify: foil rises as much as modulated -> modulation
adds nothing beyond raw count.

Outputs: data/q1_modulation/, samples/q1_modulation/summary.csv,
figures/sweep_q1_modulation.png
Run:  ../.venv/bin/python sweep_q1_modulation.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag
from smn_lab.control import OpponentBoard, MessagingBeam
from smn_lab.sweep import run_sweep, export_curated

DT = 0.002
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
N_SEGS = [3, 5, 7, 9]
MODES = ["modulated", "foil"]
SEEDS = list(range(6))
SENSOR_NOISE = 0.002
PROPRIO_NOISE = 0.03
WIN = 125
GRAD_A, GRAD_B = 1.6, 1.2          # static linear slope (reafference model exact)
T_LEARN, T_SELF, T_EXAF = 8.0, 12.0, 12.0
T_END = T_LEARN + T_SELF + T_EXAF
EXAF_AMP, EXAF_SIG = 3.0, 0.5
EXAF_START, EXAF_VEL = (-0.6, 1.6), (0.10, -0.20)


def run_one(params, seed):
    N = int(params["n_seg"]); mode = params["mode"]
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N))
    data = mujoco.MjData(model)
    seg_ids = [model.body(f"seg{k}").id for k in range(N)]
    sL = [model.site(f"seg{k}_L").id for k in range(N)]
    sR = [model.site(f"seg{k}_R").id for k in range(N)]
    j_ids = [model.joint(f"j{k}").id for k in range(1, N)]
    j_qadr = [model.jnt_qposadr[j] for j in j_ids]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N)]
    beam = MessagingBeam(n_joints=N - 1, amp=0.8, freq=0.9, coupling=4.0, turn_gain=0.0)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]

    def field_now(x, y, t):
        v = GRAD_A * x + GRAD_B * y
        if T_LEARN + T_SELF <= t:
            te = t - (T_LEARN + T_SELF)
            ex, ey = EXAF_START[0] + EXAF_VEL[0] * te, EXAF_START[1] + EXAF_VEL[1] * te
            v += EXAF_AMP * np.exp(-((x - ex) ** 2 + (y - ey) ** 2) / (2 * EXAF_SIG ** 2))
        return v

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    steer = 0.0
    vel = np.zeros(6)
    disp = np.zeros((N, 2))           # per-zone sensed displacement over the window
    r_prev = None
    scale = np.ones(N)
    cal_num, cal_den = np.zeros(N), np.zeros(N)
    log = {k: [] for k in ("t", "res", "phase")}
    for i in range(n):
        t = i * DT
        steer += (-steer / 2.5) * DT + 1.6 * np.sqrt(DT) * rng.normal()
        theta_cmd = beam.command(DT, bias=0.0)
        theta_cmd[0] += 0.6 * np.clip(steer, -1.5, 1.5)
        for k in range(len(j_ids)):
            th, thd = float(data.qpos[j_qadr[k]]), float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]], data.ctrl[aid_n[k]] = a_r, a_l
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)

        for k in range(N):            # each zone senses its OWN motion (dual-port)
            mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, seg_ids[k], vel, 0)
            disp[k, 0] += vel[3] * (1 + rng.normal(0, PROPRIO_NOISE)) * DT
            disp[k, 1] += vel[4] * (1 + rng.normal(0, PROPRIO_NOISE)) * DT

        if i % WIN != 0:
            continue
        pts, vals, r = [], [], np.zeros(N)
        for k in range(N):
            xL, yL = data.site_xpos[sL[k]][:2]; xR, yR = data.site_xpos[sR[k]][:2]
            vL = field_now(xL, yL, t) + rng.normal(0, SENSOR_NOISE)
            vR = field_now(xR, yR, t) + rng.normal(0, SENSOR_NOISE)
            r[k] = 0.5 * (vL + vR)
            pts += [(xL, yL), (xR, yR)]; vals += [vL, vR]
        pts = np.array(pts); vals = np.array(vals)
        A = np.column_stack([np.ones(len(pts)), pts[:, 0], pts[:, 1]])
        _, gx, gy = np.linalg.lstsq(A, vals, rcond=None)[0]
        basis = gx * disp[:, 0] + gy * disp[:, 1]          # per-zone predicted change
        if r_prev is not None:
            dr = r - r_prev
            if mode == "modulated":
                res = dr - scale * basis                    # per-zone reafferent cancel
            else:
                res = dr.copy()                             # foil: no cancellation
            agg = float(np.mean(res))                       # aggregate over zones
            if t < T_LEARN:
                cal_num += dr * basis; cal_den += basis ** 2
                phase = 0
            else:
                phase = 1 if t < (T_LEARN + T_SELF) else 2
            log["t"].append(t); log["res"].append(agg); log["phase"].append(phase)
            if t < T_LEARN:
                good = cal_den > 1e-12
                scale[good] = cal_num[good] / cal_den[good]
        r_prev = r
        disp[:] = 0.0
    for k in log:
        log[k] = np.array(log[k])
    return log


def summarize(log, params, seed):
    ph = log["phase"]; res = np.abs(log["res"])
    self_r = res[ph == 1].mean(); exaf_r = res[ph == 2].mean()
    return {"self_res": float(self_r), "exaf_res": float(exaf_r),
            "ratio": float(exaf_r / max(self_r, 1e-12))}


def plot(summary, out):
    ns = np.array(sorted(summary["n_seg"].unique()))
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    colors = {"modulated": "#1538a0", "foil": "#c9a23a"}
    for mode in MODES:
        d = summary[summary["mode"] == mode].groupby("n_seg")["ratio"]
        m = d.mean().reindex(ns).values
        ci = (1.96 * d.std(ddof=1) / np.sqrt(d.count())).reindex(ns).values
        axA.fill_between(ns, m - ci, m + ci, color=colors[mode], alpha=0.2)
        axA.plot(ns, m, "-o", color=colors[mode], lw=1.9,
                 label=("per-zone modulation" if mode == "modulated" else "foil (no modulation)"))
    axA.set_xlabel("segment count  (CAZ / dual-port modulator density)")
    axA.set_ylabel("world/self ratio  (exafference / self-test)")
    axA.set_xticks(ns); axA.legend(fontsize=8, loc="upper right")
    axA.set_title("A — without modulation, self/world resolution collapses as the\n"
                  "body grows (foil → 1); modulation preserves it (gap widens)",
                  fontsize=9.5)

    for mode in MODES:
        d = summary[summary["mode"] == mode].groupby("n_seg")["self_res"]
        axB.plot(ns, d.mean().reindex(ns).values, "-o", color=colors[mode], lw=1.7,
                 label=("modulated" if mode == "modulated" else "foil"))
    axB.set_xlabel("segment count"); axB.set_ylabel("self-test residual (aggregate)")
    axB.set_xticks(ns); axB.legend(fontsize=8)
    axB.set_title("B — modulation holds self-caused residual at the noise floor at\n"
                  "every size; without it, residual GROWS with zone count", fontsize=9.5)
    fig.suptitle(f"Q1 — modulation & the resolution principle "
                 f"({len(SEEDS)} seeds × {len(N_SEGS)} bodies)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    grid = [{"n_seg": N, "mode": m} for N in N_SEGS for m in MODES]
    summary = run_sweep("q1_modulation", run_one, grid, SEEDS, summarize,
                        outdir=os.path.join(here, "..", "data"), timeseries=False)
    export_curated("q1_modulation", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    print("\n  world/self ratio by segment count:")
    for N in N_SEGS:
        md = summary[(summary.n_seg == N) & (summary["mode"] == "modulated")].ratio
        fo = summary[(summary.n_seg == N) & (summary["mode"] == "foil")].ratio
        print(f"   n_seg={N}: modulated {md.mean():.2f}±{md.std():.2f}   "
              f"foil {fo.mean():.2f}±{fo.std():.2f}")
    plot(summary, os.path.join(figdir, "sweep_q1_modulation.png"))
