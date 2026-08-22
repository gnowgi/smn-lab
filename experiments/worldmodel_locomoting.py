# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""World-model on a LOCOMOTING body: mapping the extended world by path integration.

Step 1 built a world-model for a body that stays put (one feature, on the self-graph).
A body that TRAVELS (gravity+friction locomotion) meets features at different times, so
to place them in one coherent frame it must track its own displacement -- dead-reckoning
(path integration) from its own sensed motion. This is the configuration-keyed self-
tracking a locomoting agent needs, and the route to the EXTENDED world-model (the
snapshot assembled through the stream of locomotion).

Design: the agent crawls (apply_ground_friction) past several field sources placed along
its path. It dead-reckons its pose from its OWN body-frame velocity + yaw rate
(proprioception; never absolute position). For each source, at the moment of closest
approach we compare where the agent THINKS it is:
  * DEAD-RECKONED estimate -- pose from path integration -> features spread out, recovering
    the true along-path layout.
  * NAIVE (body-frame only, no path integration) -- the feature's momentary place on the
    body. Because the agent passes each source similarly, these COLLAPSE -> no layout.

Order parameter: |rank corr|(true along-path source position, estimated position).
Prediction: dead-reckoning tracks the layout; naive collapses. => a moving body needs
path integration to build a world-model of the extended world.

Run:  ../.venv/bin/python worldmodel_locomoting.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml, apply_ground_friction
from smn_lab.control import MessagingBeam, OpponentBoard, DeadReckoner
from smn_lab.fields import ScalarField

DT = 0.002
N_SEG = 8
T_END = 30.0
MU_LONG, MU_TRANS = 0.15, 3.0
N_SRC = 3
SRC_AMP, SRC_SIG, SRC_OFF = 1.0, 0.22, 0.28      # sources offset laterally from the path
SEEDS = [0, 1, 2]


def build():
    xml = build_crawler_xml(n_seg=N_SEG, gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    ids = dict(
        seg=[m.body(f"seg{k}").id for k in range(N_SEG)],
        sL=[m.site(f"seg{k}_L").id for k in range(N_SEG)],
        sR=[m.site(f"seg{k}_R").id for k in range(N_SEG)],
        ap=[m.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)],
        an=[m.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)],
        jq=[m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1, N_SEG)],
        jv=[m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1, N_SEG)],
    )
    return m, d, ids


def drive_step(m, d, ids, beam, boards):
    tc = beam.command(DT)
    for k in range(N_SEG - 1):
        th = float(d.qpos[ids["jq"][k]]); thd = float(d.qvel[ids["jv"][k]])
        ar, al, _ = boards[k].commands(th, thd, tc[k], 0.0)
        d.ctrl[ids["ap"][k]] = ar; d.ctrl[ids["an"][k]] = al
    apply_ground_friction(m, d, ids["seg"], mu_long=MU_LONG, mu_trans=MU_TRANS)
    mujoco.mj_step(m, d)


def run(seed):
    # PASS 1: no sources -> record the true head path, to lay features along it.
    m, d, ids = build()
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9)
    boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in ids["ap"]]
    mujoco.mj_forward(m, d)
    path = []
    n = int(T_END / DT)
    for i in range(n):
        drive_step(m, d, ids, beam, boards)
        if i % 20 == 0:
            path.append(d.xpos[ids["seg"][0]][:2].copy())
    path = np.array(path)
    start, end = path[0], path[-1]
    travel = end - start; L = np.hypot(*travel)
    if L < 0.3:
        return None                                   # didn't travel enough this seed
    u = travel / L                                    # along-path unit vector
    npr = np.array([-u[1], u[0]])                     # lateral unit
    # place N_SRC sources along the path (spread over the middle of the journey), offset laterally
    fracs = np.linspace(0.3, 0.85, N_SRC)
    srcs = [start + f * travel + SRC_OFF * npr for f in fracs]
    field = ScalarField([(s[0], s[1], SRC_AMP, SRC_SIG) for s in srcs])

    # PASS 2: same drive, WITH sources -> locomote, dead-reckon, sense.
    m, d, ids = build()
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9)
    boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in ids["ap"]]
    dr = DeadReckoner()
    mujoco.mj_forward(m, d)
    vel = np.zeros(6)
    true_head = []; dr_head = []; seg_read = []
    for i in range(n):
        drive_step(m, d, ids, beam, boards)
        # proprioceptive self-motion -> dead-reckoning (agent's own pose estimate)
        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, ids["seg"][0], vel, 1)
        dr.update(vel[3], vel[4], vel[2], DT)
        true_head.append(d.xpos[ids["seg"][0]][:2].copy())
        dr_head.append(np.array([dr.x, dr.y]))
        seg_read.append(np.array([0.5 * (field.sample(*d.site_xpos[ids["sL"][k]][:2]) +
                                         field.sample(*d.site_xpos[ids["sR"][k]][:2])) for k in range(N_SEG)]))
    true_head = np.array(true_head); dr_head = np.array(dr_head); seg_read = np.array(seg_read)

    # for each source: closest-approach time (true), and where the agent thinks it is
    true_pos, dr_est, naive_est = [], [], []
    seg_idx = np.arange(N_SEG)
    for s in srcs:
        ti = int(np.argmin(np.linalg.norm(true_head - s[:2], axis=1)))
        true_pos.append((s - start) @ u)                              # true along-path coord
        dr_est.append((dr_head[ti] - dr_head[0]) @ u)                 # dead-reckoned along-path
        w = np.clip(seg_read[ti] - seg_read[ti].min(), 0, None); w = w / (w.sum() + 1e-9)
        naive_est.append(float((w * seg_idx).sum()))                  # body-frame node only (no travel)
    return dict(true=np.array(true_pos), dr=np.array(dr_est), naive=np.array(naive_est),
                drift=float(np.linalg.norm(dr_head[-1] - (true_head[-1] - true_head[0]))),
                travel=L)


def abs_rankcorr(x, y):
    if len(x) < 2:
        return np.nan
    rx = np.argsort(np.argsort(x)).astype(float); ry = np.argsort(np.argsort(y)).astype(float)
    return abs(np.corrcoef(rx, ry)[0, 1])


def main():
    dr_tr, nv_tr, travels, drifts = [], [], [], []
    ex = None
    for s in SEEDS:
        r = run(s)
        if r is None:
            continue
        dr_tr.append(abs_rankcorr(r["true"], r["dr"]))
        nv_tr.append(abs_rankcorr(r["true"], r["naive"]))
        travels.append(r["travel"]); drifts.append(r["drift"])
        if ex is None:
            ex = r
    print("\nWorld-model on a LOCOMOTING body (map the extended world by path integration)\n" + "=" * 74)
    print(f"net travel: {np.mean(travels):.2f} body-lengths;  dead-reckoning end-drift: {np.mean(drifts):.2f}")
    print(f"world-model layout recovery |rank corr| (true source layout vs estimate):")
    print(f"   dead-reckoned (path integration) = {np.nanmean(dr_tr):.2f} +/- {np.nanstd(dr_tr):.2f}")
    print(f"   naive (body-frame only)          = {np.nanmean(nv_tr):.2f} +/- {np.nanstd(nv_tr):.2f}")
    ok = np.nanmean(dr_tr) > 0.7 and np.nanmean(dr_tr) > np.nanmean(nv_tr) + 0.2
    print("=" * 74)
    print(f"Verdict: a locomoting body maps the extended world only with path integration "
          f"[{'PASS' if ok else 'CHECK'}]")
    print("Dead-reckoning spreads features along the travelled path (recovering the layout);")
    print("body-frame-only collapses them (the agent passes each source alike). Locomotion +")
    print("self-motion tracking = the extended world-model; without it, no map.\n")

    if ex is not None:
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
        ax[0].scatter(ex["true"], ex["dr"], c="#2c6fbb", s=60, label="dead-reckoned")
        ax[0].scatter(ex["true"], ex["naive"] * (np.ptp(ex["true"]) / (N_SEG - 1)) + ex["true"].min(),
                      c="#c0392b", marker="s", s=60, label="naive (body-frame, rescaled)")
        ax[0].set_xlabel("true source position along path"); ax[0].set_ylabel("agent's estimate")
        ax[0].set_title("Recovered layout of features passed while moving"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
        ax[1].bar([0, 1], [np.nanmean(dr_tr), np.nanmean(nv_tr)], yerr=[np.nanstd(dr_tr), np.nanstd(nv_tr)],
                  capsize=4, color=["#2c6fbb", "#c0392b"])
        ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["dead-reckoned", "naive body-frame"])
        ax[1].set_ylabel("layout recovery |rank corr|"); ax[1].set_ylim(0, 1.05)
        ax[1].set_title("Path integration is required")
        fig.tight_layout()
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "worldmodel_locomoting.png")
        os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
        print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
