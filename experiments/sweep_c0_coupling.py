# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Sweep S0 -- coupling vs locomotion, with a matched foil, across seeds.

The first harness demonstration, and a clean network-effect result. The three-
block crawler's locomotion comes from a traveling wave on the messaging beam. We
sweep the beam's **coupling strength** and, for each value, run many seeds whose
*initial joint phases are randomized*. The coupling has to re-establish a coherent
traveling wave from those random phases.

  - coupling = 0  is the **matched foil**: identical body, identical actuators,
    identical drag -- only the inter-zone coupling removed. The two oscillators
    keep whatever random phase offset they started with, so net displacement is a
    lottery (high variance, lower mean).
  - coupling > 0  pulls the joints to the productive phase lag regardless of where
    they started, so every seed locks into the same forward-driving wave (mean
    rises, across-seed spread collapses).

This is the SMN claim under test in its smallest form: locomotion is a *network*
effect (it lives in the coupling), not a property of the parts. The order
parameter is net displacement; the foil and the seed ensemble make the contrast
falsifiable -- exactly the methodology the formal review asked for.

Outputs (via smn_lab.sweep):
  data/s0_coupling/{summary.csv, timeseries.parquet, manifest.json}
  samples/s0_coupling/summary.csv   (curated, committed)
  figures/sweep_c0_coupling.png

Run:  ../.venv/bin/python sweep_c0_coupling.py        (from this directory)
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
T_END = 30.0
N_SEG = 3
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
COUPLINGS = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]    # 0.0 = the matched foil
SEEDS = list(range(10))


def run_one(params, seed):
    coupling = float(params["coupling"])
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N_SEG))
    data = mujoco.MjData(model)

    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    j_ids = [model.joint(f"j{k}").id for k in range(1, N_SEG)]
    j_qadr = [model.jnt_qposadr[j] for j in j_ids]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]

    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9,
                         coupling=coupling, turn_gain=0.0)
    beam.phase = rng.uniform(-np.pi, np.pi, N_SEG - 1)   # randomized start
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    log = {k: [] for k in ("t", "x", "y", "dphi")}
    for i in range(n):
        theta_cmd = beam.command(DT, bias=0.0)
        for k in range(len(j_ids)):
            th, thd = float(data.qpos[j_qadr[k]]), float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]], data.ctrl[aid_n[k]] = a_r, a_l
        apply_anisotropic_drag(model, data, seg_ids,
                               c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i % 5 == 0:
            hx, hy = data.xpos[seg_ids[0]][:2]
            log["t"].append(i * DT); log["x"].append(hx); log["y"].append(hy)
            log["dphi"].append(float(beam.phase[0] - beam.phase[1]))
    for k in log:
        log[k] = np.array(log[k])
    return log


def summarize(log, params, seed):
    x, y = log["x"], log["y"]
    net = float(np.hypot(x[-1] - x[0], y[-1] - y[0]))
    path = float(np.sum(np.hypot(np.diff(x), np.diff(y))))
    # temporal phase-lag coherence: |<e^{i dphi}>| over the run
    coh = float(np.abs(np.mean(np.exp(1j * log["dphi"]))))
    return {"net_disp": net, "path_len": path, "phase_coherence": coh,
            "straightness": net / max(path, 1e-9)}


def plot(summary, out):
    g = summary.groupby("coupling")["net_disp"]
    cs = np.array(sorted(summary["coupling"].unique()))
    mean = g.mean().reindex(cs).values
    sem = (g.std(ddof=1) / np.sqrt(g.count())).reindex(cs).values
    ci = 1.96 * sem

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    # A: net displacement vs coupling (mean +/- 95% CI), foil highlighted
    axA.fill_between(cs, mean - ci, mean + ci, color="#7fb3d5", alpha=0.35,
                     label="95% CI over seeds")
    axA.plot(cs, mean, "-o", color="#1538a0", lw=1.8, label="mean net displacement")
    axA.scatter([0], [mean[0]], s=120, facecolor="none", edgecolor="#b00000",
                lw=2.0, zorder=5, label="foil (coupling = 0)")
    axA.set_xlabel("messaging-beam coupling strength")
    axA.set_ylabel("net displacement (m)")
    axA.set_title("A — locomotion is a network effect\n(mean rises as coupling "
                  "locks the wave)", fontsize=10)
    axA.legend(fontsize=8, loc="lower right")

    # B: across-seed spread collapses as coupling locks every seed to one wave
    spread = (g.std(ddof=1)).reindex(cs).values
    axB.plot(cs, spread, "-o", color="#b06000", lw=1.8)
    axB.scatter([0], [spread[0]], s=120, facecolor="none", edgecolor="#b00000",
                lw=2.0, zorder=5)
    axB.set_xlabel("messaging-beam coupling strength")
    axB.set_ylabel("across-seed std of net displacement (m)")
    axB.set_title("B — coupling collapses seed-to-seed variance\n(random starts "
                  "all lock to the same wave)", fontsize=10)
    fig.suptitle("Sweep S0 — coupling sweep with a matched foil "
                 f"({len(SEEDS)} seeds × {len(COUPLINGS)} couplings)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    summary = run_sweep("s0_coupling", run_one, {"coupling": COUPLINGS}, SEEDS,
                        summarize, outdir=os.path.join(here, "..", "data"))
    export_curated("s0_coupling", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    # headline contrast
    foil = summary[summary.coupling == 0]["net_disp"]
    best = summary[summary.coupling == summary.coupling.max()]["net_disp"]
    print(f"\n  foil (coupling=0): net_disp {foil.mean():.3f} ± {foil.std():.3f} m")
    print(f"  coupled (max):     net_disp {best.mean():.3f} ± {best.std():.3f} m")
    plot(summary, os.path.join(figdir, "sweep_c0_coupling.png"))
