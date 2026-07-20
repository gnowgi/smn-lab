# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Q1b -- does resolution scale UP with CAZ density? (closes the Q1 open thread)

Q1 left one question open. It showed the modulation *advantage* widens with CAZ
density, but the *absolute* modulated ratio FELL with segment count -- because the
exafference was a LOCALIZED moving source, so on a longer body most zones were far
from it and the whole-body mean diluted the world signal. We could not say whether
resolution scales UP with density.

This closes it with one principled change: a DISTRIBUTED world-caused change -- a
spatially uniform 'tide' that rises everywhere, so every zone sees it equally and
the per-zone aggregate no longer dilutes it. Everything else is the Q1 setup
(per-zone dual-port modulation vs foil, linear static field, noisy sensors).

Pre-registration (written before running):
- Hypothesis: with a distributed world signal and per-zone MODULATION, the
  world-detection ratio RISES with CAZ density -- each zone cancels its own
  self-motion, so averaging N zones drives the self-noise floor down ~1/sqrt(N)
  while the (shared) world signal survives. The FOIL falls (its uncancelled
  self-motion floor grows with density, per Q1).
- Order parameter: world/self ratio = mean|aggregate residual| (exafference /
  self-test).
- Pass: modulated ratio increases with segment count; foil does not.
- Falsify: modulated ratio also flat/declining with a distributed stimulus ->
  resolution does NOT scale with CAZ density even with modulation.

Outputs: data/q1b_resolution/, samples/q1b_resolution/summary.csv,
figures/sweep_q1b_resolution.png
Run:  ../.venv/bin/python sweep_q1b_resolution.py
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
EXAF_RATE = 0.05                   # DISTRIBUTED exafference: a uniform global tide
                                   # rising at this rate (same change at every zone)


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
        v = GRAD_A * x + GRAD_B * y                     # static linear slope
        if T_LEARN + T_SELF <= t:                       # DISTRIBUTED uniform tide
            v += EXAF_RATE * (t - (T_LEARN + T_SELF))
        return v

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    steer = 0.0
    vel = np.zeros(6)
    disp = np.zeros((N, 2))
    r_prev = None
    scale = np.ones(N)
    gain = params.get("gain", 1.0 if mode == "modulated" else 0.0)   # modulation strength mu
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

        for k in range(N):
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
        basis = gx * disp[:, 0] + gy * disp[:, 1]
        if r_prev is not None:
            dr = r - r_prev
            res = dr - gain * scale * basis
            agg = float(np.mean(res))
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
                 label=("per-zone modulation" if mode == "modulated" else "foil"))
    axA.set_xlabel("segment count  (CAZ density)")
    axA.set_ylabel("world-detection ratio  (exafference / self-test)")
    axA.set_xticks(ns); axA.legend(fontsize=8, loc="upper left")
    axA.set_title("A — with a DISTRIBUTED world signal, does resolution\n"
                  "scale with CAZ density?", fontsize=9.5)

    for mode in MODES:
        d = summary[summary["mode"] == mode].groupby("n_seg")["self_res"]
        axB.plot(ns, d.mean().reindex(ns).values, "-o", color=colors[mode], lw=1.7,
                 label=("modulated" if mode == "modulated" else "foil"))
    axB.set_xlabel("segment count"); axB.set_ylabel("self-test residual (noise floor)")
    axB.set_xticks(ns); axB.legend(fontsize=8)
    axB.set_title("B — the self-noise floor vs density\n"
                  "(modulated should fall ~1/√N; foil should grow)", fontsize=9.5)
    fig.suptitle(f"Q1b — resolution vs CAZ density, distributed stimulus "
                 f"({len(SEEDS)} seeds × {len(N_SEGS)} bodies)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    grid = [{"n_seg": N, "mode": m} for N in N_SEGS for m in MODES]
    summary = run_sweep("q1b_resolution", run_one, grid, SEEDS, summarize,
                        outdir=os.path.join(here, "..", "data"), timeseries=False)
    export_curated("q1b_resolution", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    print("\n  world-detection ratio by segment count:")
    for N in N_SEGS:
        md = summary[(summary.n_seg == N) & (summary["mode"] == "modulated")].ratio
        fo = summary[(summary.n_seg == N) & (summary["mode"] == "foil")].ratio
        print(f"   n_seg={N}: modulated {md.mean():.2f}±{md.std():.2f}   "
              f"foil {fo.mean():.2f}±{fo.std():.2f}")
    plot(summary, os.path.join(figdir, "sweep_q1b_resolution.png"))
