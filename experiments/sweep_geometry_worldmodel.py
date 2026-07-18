# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Flagship S1 -- geometry -> world model (pre-registered in docs/test-plan.md).

Hypothesis: with the world held fixed, the world an agent can *differentiate*
scales with its body's sensory geometry. We hold a fixed multi-source scalar field
constant and vary only the body's segment count. As the crawler explores, we log
its internal sensory state (the per-segment bilateral field readings) and its true
position. A model-free kNN decoder then asks: **can the agent's position in the
world be read out of its internal state?** -- on held-out trajectory, so it cannot
memorize.

Order parameter: decoding skill = 1 - MAE_decoder / MAE_naive (0 = no better than
guessing the mean position; 1 = perfect). The naive normalization controls for
differences in explored area across body sizes.

Control (the integrity check): a **shuffle control** decodes from state<->position
pairs that have been shuffled. It must sit at skill ~ 0; if the real decoder is no
better than shuffle, there is no body-relative world model and the claim fails.

This is the clean, hard-to-rig part of "can SMN build a world model": held-out
decoding + a shuffle control means the result cannot be tuned into existence.

Outputs:
  data/s1_geometry/{summary.csv, timeseries.parquet, manifest.json}
  samples/s1_geometry/summary.csv (curated)
  figures/sweep_geometry_worldmodel.png

Run:  ../.venv/bin/python sweep_geometry_worldmodel.py   (from this directory)
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
from smn_lab.fields import ScalarField
from smn_lab.sweep import run_sweep, export_curated
# held-out decoding skill + shuffle control (the experimenter's world-model score).
from smn_lab.metrics import decoding_skill as _knn_skill

DT = 0.002
T_END = 90.0              # [adj] longer run -> comparable coverage + more samples
LOG_EVERY = 25            # [adj] ~1800 samples/run, enough for kNN at up to 18 dims
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
N_SEGS = [3, 5, 7, 9]
SEEDS = list(range(8))
# A FIXED structured world (three sources break radial symmetry, so position is
# in principle recoverable from field values). Identical across every run.
FIELD = ScalarField([(1.6, 1.1, 1.0, 0.8), (-1.4, 0.9, 0.9, 0.9),
                     (0.2, -1.6, 1.1, 0.7)])
# [adj] Exploration steers the ANTERIOR joint only (head steering), not every
# joint uniformly -- the uniform bias over-drove and destabilized long bodies.
STEER_TAU = 2.5          # head-steer autocorrelation time
STEER_SD = 1.6           # head-steer drive
STEER_GAIN = 0.6         # head-steer offset gain (rad)


def run_one(params, seed):
    N = int(params["n_seg"])
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

    beam = MessagingBeam(n_joints=N - 1, amp=0.8, freq=0.9, coupling=4.0,
                         turn_gain=0.0)       # [adj] steer the head joint, not all
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    steer = 0.0
    log = {"t": [], "x": [], "y": [], "S": []}
    for i in range(n):
        # exploration: an OU head-steer offset roams the body over the field
        steer += (-steer / STEER_TAU) * DT + STEER_SD * np.sqrt(DT) * rng.normal()
        theta_cmd = beam.command(DT, bias=0.0)
        theta_cmd[0] += STEER_GAIN * np.clip(steer, -1.5, 1.5)   # anterior steer
        for k in range(len(j_ids)):
            th, thd = float(data.qpos[j_qadr[k]]), float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]], data.ctrl[aid_n[k]] = a_r, a_l
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i % LOG_EVERY == 0:                # log internal state + true position
            hx, hy = data.xpos[seg_ids[0]][:2]
            S = [FIELD.sample(*data.site_xpos[sL[k]][:2]) for k in range(N)] + \
                [FIELD.sample(*data.site_xpos[sR[k]][:2]) for k in range(N)]
            log["t"].append(i * DT); log["x"].append(hx); log["y"].append(hy)
            log["S"].append(S)
    log["t"] = np.array(log["t"]); log["x"] = np.array(log["x"])
    log["y"] = np.array(log["y"]); log["S"] = np.array(log["S"])
    return log


def summarize(log, params, seed):
    rng = np.random.default_rng(1000 + seed)
    S, P = log["S"], np.column_stack([log["x"], log["y"]])
    skill = _knn_skill(S, P, rng, shuffle=False)
    skill_shuf = _knn_skill(S, P, rng, shuffle=True)
    # coverage: area of the explored bounding box (a fair-exploration check)
    cover = float((log["x"].max() - log["x"].min()) * (log["y"].max() - log["y"].min()))
    return {"skill": skill, "skill_shuffle": skill_shuf,
            "state_dim": int(S.shape[1]), "coverage": cover,
            "net_disp": float(np.hypot(log["x"][-1] - log["x"][0],
                                       log["y"][-1] - log["y"][0]))}


def plot(summary, out):
    ns = np.array(sorted(summary["n_seg"].unique()))
    g = summary.groupby("n_seg")
    m = g["skill"].mean().reindex(ns).values
    ci = (1.96 * g["skill"].std(ddof=1) / np.sqrt(g["skill"].count())).reindex(ns).values
    ms = g["skill_shuffle"].mean().reindex(ns).values
    cov = g["coverage"].mean().reindex(ns).values

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    axA.fill_between(ns, m - ci, m + ci, color="#7fb3d5", alpha=0.35, label="95% CI")
    axA.plot(ns, m, "-o", color="#1538a0", lw=1.9, label="world-model skill")
    axA.plot(ns, ms, "--s", color="#b00000", lw=1.4, ms=5,
             label="shuffle control (≈ 0)")
    axA.axhline(0, color="#888", lw=0.8, ls=":")
    axA.set_xlabel("segment count  (body sensory geometry)")
    axA.set_ylabel("held-out position-decoding skill")
    axA.set_title("A — a real world model at every body size,\n"
                  "but it does NOT scale with segment count (skill ≫ shuffle; "
                  "flat in n_seg)", fontsize=9.5)
    axA.set_xticks(ns); axA.legend(fontsize=8, loc="center right")

    axB.plot(ns, cov, "-o", color="#2a8a4a", lw=1.7)
    axB.set_xlabel("segment count")
    axB.set_ylabel("explored bounding-box area (m²)")
    axB.set_title("B — exploration coverage\n(context for the skill, by geometry)",
                  fontsize=10)
    axB.set_xticks(ns)
    fig.suptitle(f"Flagship S1 — geometry → world model  "
                 f"({len(SEEDS)} seeds × {len(N_SEGS)} bodies, world fixed)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    summary = run_sweep("s1_geometry", run_one, {"n_seg": N_SEGS}, SEEDS,
                        summarize, outdir=os.path.join(here, "..", "data"),
                        timeseries=False)   # state S is 2D per step; skill is in summary
    export_curated("s1_geometry", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    print("\n  skill by segment count (mean ± sd over seeds), vs shuffle:")
    for N in N_SEGS:
        s = summary[summary.n_seg == N]
        print(f"   n_seg={N}: skill {s.skill.mean():.3f} ± {s.skill.std():.3f}"
              f"   shuffle {s.skill_shuffle.mean():+.3f}")
    plot(summary, os.path.join(figdir, "sweep_geometry_worldmodel.png"))
