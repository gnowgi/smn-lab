# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""C0 -- the minimal axial crawler: non-inertial movement + the messaging beam.

The disciplined model organism of Lesson 1. A three-block axial crawler
(``n_seg=3`` -> two inter-segment CAZ joints) swims in an overdamped, anisotropic
medium. The messaging beam (nearest-neighbor coupled oscillators) produces a
traveling wave of bends; because two joints make the joint-angle cycle
non-reciprocal, the body clears Purcell's scallop theorem and nets a
displacement. A bilateral chemical field sensed at the head biases the wave, so
the crawler climbs the gradient toward the source -- the minimal aboutness-
precursor (directed movement toward a 'where').

Outputs figures/c0_crawler.png:
  (A) arena: the field, the crawler's path and a few body postures, the source;
  (B) the messaging beam as a graph drawn on the body, nodes = segments coloured
      by the field they sense, edges = inter-segment coupling messages;
  (C) the beam's shared actuation state-space (theta_j1, theta_j2): the gait loop
      whose enclosed area is the non-reciprocity that yields net motion.

Run:  ../.venv/bin/python c0_crawler.py        (from this directory)
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
from smn_lab import viz

# ---- parameters -----------------------------------------------------------
SEED = 3
DT = 0.002              # must match the MJCF <option timestep>
T_END = 60.0
N_SEG = 3                       # three blocks -> two joints: the minimal mover
SOURCE = (1.6, 0.9)            # chemical source (the 'goal')
FIELD = ScalarField([(*SOURCE, 1.0, 0.9)])
DRAG_LONG, DRAG_TRANS = 0.5, 7.0    # transverse >> tangential -> net thrust
TURN_GAIN = 4.0                # chemotactic steering strength
SS_WINDOW = (14.0, 22.0)      # time window shown in the state-space panel
BIAS_SIGN = -1.0              # set so the bias steers TOWARD the source


def run():
    rng = np.random.default_rng(SEED)
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N_SEG))
    data = mujoco.MjData(model)

    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    senseL = model.site("sense_L").id
    senseR = model.site("sense_R").id
    segL = [model.site(f"seg{k}_L").id for k in range(N_SEG)]
    segR = [model.site(f"seg{k}_R").id for k in range(N_SEG)]
    j_ids = [model.joint(f"j{k}").id for k in range(1, N_SEG)]
    j_qadr = [model.jnt_qposadr[j] for j in j_ids]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]

    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9,
                         turn_gain=TURN_GAIN)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    log = {k: [] for k in ("t", "x", "y", "theta", "phase", "msg",
                           "node_field", "node_xy", "dist")}

    for i in range(n):
        t = i * DT
        # chemotactic bias from the head's bilateral field sense (the strips)
        cL = FIELD.sample(*data.site_xpos[senseL][:2])
        cR = FIELD.sample(*data.site_xpos[senseR][:2])
        bias = BIAS_SIGN * (cL - cR)

        theta_cmd = beam.command(DT, bias=bias)
        for k in range(len(j_ids)):
            th = float(data.qpos[j_qadr[k]])
            thd = float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]] = a_r
            data.ctrl[aid_n[k]] = a_l

        apply_anisotropic_drag(model, data, seg_ids,
                               c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)

        if i % 4 == 0:                         # log at 50 Hz
            hx, hy = data.xpos[seg_ids[0]][:2]
            node_field = [0.5 * (FIELD.sample(*data.site_xpos[segL[k]][:2]) +
                                 FIELD.sample(*data.site_xpos[segR[k]][:2]))
                          for k in range(N_SEG)]
            node_xy = [data.xpos[seg_ids[k]][:2].copy() for k in range(N_SEG)]
            log["t"].append(t)
            log["x"].append(hx); log["y"].append(hy)
            log["theta"].append([float(data.qpos[j_qadr[k]]) for k in range(len(j_ids))])
            log["phase"].append(beam.phase.copy())
            log["msg"].append(beam.msg.copy())
            log["node_field"].append(node_field)
            log["node_xy"].append(np.array(node_xy))
            log["dist"].append(float(np.hypot(hx - SOURCE[0], hy - SOURCE[1])))

    for k in ("t", "x", "y", "theta", "phase", "msg", "node_field", "dist"):
        log[k] = np.array(log[k])
    return log


def summarize(log):
    x, y = log["x"], log["y"]
    path_len = float(np.sum(np.hypot(np.diff(x), np.diff(y))))
    net_disp = float(np.hypot(x[-1] - x[0], y[-1] - y[0]))
    d0, d1 = log["dist"][0], log["dist"][-1]
    # cumulative non-reciprocity: signed area swept by (theta1, theta2) over the
    # whole run (~ area_per_cycle x n_cycles); the per-loop area is shown in panel C
    th = log["theta"]
    swept = abs(viz._loop_area(th)) if th.shape[1] == 2 else float("nan")
    return dict(path_len=path_len, net_disp=net_disp,
                dist_start=d0, dist_end=d1, closed_gap=d0 - d1,
                swept_area=swept)


def plot(log, stats, out):
    fig = plt.figure(figsize=(15, 5.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.0, 1.0], wspace=0.32)

    # (A) arena: field + path + postures
    axA = fig.add_subplot(gs[0, 0])
    pad = 0.5
    xlim = (min(log["x"].min(), SOURCE[0]) - pad, max(log["x"].max(), SOURCE[0]) + pad)
    ylim = (min(log["y"].min(), SOURCE[1]) - pad, max(log["y"].max(), SOURCE[1]) + pad)
    X, Y, Z = FIELD.grid(xlim, ylim, 140)
    axA.contourf(X, Y, Z, levels=18, cmap="YlOrRd", alpha=0.8)
    axA.plot(log["x"], log["y"], color="#1538a0", lw=1.6, label="head path", zorder=2)
    for idx in np.linspace(0, len(log["node_xy"]) - 1, 7).astype(int):  # body postures
        nx = log["node_xy"][idx]
        axA.plot(nx[:, 0], nx[:, 1], "-o", color="#222", lw=1.4, ms=3, alpha=0.55, zorder=3)
    axA.scatter(*SOURCE, marker="*", s=320, color="#b00000", edgecolors="k",
                zorder=5, label="source")
    axA.scatter(log["x"][0], log["y"][0], s=40, color="k", zorder=5, label="start")
    axA.set_aspect("equal"); axA.set_xlim(xlim); axA.set_ylim(ylim)
    axA.set_xlabel("x (m)"); axA.set_ylabel("y (m)")
    axA.legend(loc="lower left", fontsize=7)
    axA.set_title("A — chemotaxis: the 3-block crawler climbs the field", fontsize=10)

    # (B) messaging beam as a graph on the body (final posture)
    axB = fig.add_subplot(gs[0, 1])
    node_xy = log["node_xy"][-1]
    node_val = log["node_field"][-1]
    edges = [(k, k + 1) for k in range(N_SEG - 1)]
    edge_val = log["msg"][-1]
    viz.draw_beam_graph(axB, node_xy, node_val, edges, edge_val=edge_val,
                        node_labels=[f"s{k}" for k in range(N_SEG)],
                        node_cbar_label="field at segment",
                        title="B — messaging beam (nodes=segments, edges=coupling)")
    axB.set_xlabel("x (m)"); axB.set_ylabel("y (m)")

    # (C) shared actuation state-space: a few cruising cycles -> a clean gait loop
    axC = fig.add_subplot(gs[0, 2])
    m = (log["t"] >= SS_WINDOW[0]) & (log["t"] <= SS_WINDOW[1])
    viz.plot_state_space(axC, log["theta"][m], c=log["t"][m],
                         labels=(r"$\theta_{j1}$ (rad)", r"$\theta_{j2}$ (rad)"),
                         title=f"C — beam state-space ({SS_WINDOW[0]:.0f}–{SS_WINDOW[1]:.0f}s gait loop)")

    cap = (f"net displacement = {stats['net_disp']:.2f} m  |  "
           f"gap to source closed = {stats['closed_gap']:+.2f} m  "
           f"({stats['dist_start']:.2f} → {stats['dist_end']:.2f})  |  "
           f"swept area = {stats['swept_area']:.2f}")
    fig.text(0.5, 0.01, cap, ha="center", fontsize=9, color="#333")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    log = run()
    stats = summarize(log)
    print("\n=== C0 — minimal axial crawler ===")
    for k, v in stats.items():
        print(f"  {k:12s} {v:.4f}")
    verdict = ("PASS: non-inertial locomotion (net displacement) AND it closed "
               "the gap to the source (chemotaxis)."
               if stats["net_disp"] > 0.3 and stats["closed_gap"] > 0.3
               else "INCONCLUSIVE — tune drag/wave/turn params.")
    print("  verdict:", verdict)
    plot(log, stats, os.path.join(figdir, "c0_crawler.png"))
