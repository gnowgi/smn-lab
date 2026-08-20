# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Gravity + friction locomotion: the agent displaces by pushing against gravity-set
friction (the belly-scale model), not a viscous medium.

Step (world-model paper): replace the frictionless anisotropic-drag idealization with
genuine dry GROUND friction whose magnitude is set by the gravity-borne weight
(mu * m * g), anisotropic along vs across the body (Hu et al. 2009). A lateral
undulation then produces net forward thrust -- and only because the friction is
anisotropic: with isotropic friction the body cannot displace ('without friction /
its anisotropy, the agent cannot displace').

Pre-registration: net head displacement over 15 s vs the friction anisotropy ratio
mu_trans/mu_long. Prediction: displacement RISES with anisotropy (opposite of isotropic
ground contact, where it FALLS); the isotropic case (ratio 1) barely moves.

Honest scope: the body is planar-constrained (stable 'snake on flat ground'); full 3-D
contact (lifting, tipping, climbing) is a further refinement -- free-rooted thin
segments tumble under weight-scaled horizontal friction and need contact-point force
application + tuning.

Run:  ../.venv/bin/python gravity_locomotion.py
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
from smn_lab.control import MessagingBeam, OpponentBoard

DT = 0.002
N_SEG = 8
T_END = 15.0
MU_LONG = 0.15
RATIOS = [1, 3, 6, 12, 20]


def run(ratio, amp=0.8):
    xml = build_crawler_xml(n_seg=N_SEG, gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    seg_ids = [m.body(f"seg{k}").id for k in range(N_SEG)]
    ap = [m.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    an = [m.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    jq = [m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1, N_SEG)]
    jv = [m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1, N_SEG)]
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=amp, freq=0.9)
    boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in ap]
    mujoco.mj_forward(m, d)
    x0 = d.xpos[seg_ids[0]][:2].copy(); path = [x0.copy()]
    for i in range(int(T_END / DT)):
        tc = beam.command(DT)
        for k in range(N_SEG - 1):
            th = float(d.qpos[jq[k]]); thd = float(d.qvel[jv[k]])
            ar, al, _ = boards[k].commands(th, thd, tc[k], 0.0)
            d.ctrl[ap[k]] = ar; d.ctrl[an[k]] = al
        apply_ground_friction(m, d, seg_ids, mu_long=MU_LONG, mu_trans=MU_LONG * ratio)
        mujoco.mj_step(m, d)
        if i % 25 == 0:
            path.append(d.xpos[seg_ids[0]][:2].copy())
    x1 = d.xpos[seg_ids[0]][:2]
    return float(np.hypot(*(x1 - x0))), np.array(path)


def main():
    disp = {}; paths = {}
    for r in RATIOS:
        disp[r], paths[r] = run(r)
    print("\nGravity + friction locomotion (weight-proportional anisotropic dry friction)\n" + "=" * 68)
    print("net head displacement over 15 s vs friction anisotropy (body length ~1.0):")
    for r in RATIOS:
        print(f"  anisotropy mu_trans/mu_long = {r:>2}  ->  net displacement = {disp[r]:.2f}")
    print("=" * 68)
    rise = disp[RATIOS[-1]] > 3 * disp[RATIOS[0]]
    print(f"Isotropic (ratio 1) barely moves ({disp[1]:.2f}); displacement RISES with anisotropy "
          f"to {disp[RATIOS[-1]]:.2f}  [{'PASS' if rise else 'CHECK'}]")
    print("The agent displaces by pushing against gravity-set friction; the anisotropy (belly\n"
          "scales) is what converts undulation into forward thrust. No anisotropy -> no travel.\n")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.9, len(RATIOS)))
    for c, r in zip(cmap, RATIOS):
        p = paths[r]
        ax[0].plot(p[:, 0], p[:, 1], color=c, lw=1.8, label=f"ratio {r}")
        ax[0].scatter(p[-1, 0], p[-1, 1], color=c, s=30, zorder=3)
    ax[0].scatter(0, 0, c="k", marker="o", s=40, zorder=4, label="start")
    ax[0].set_aspect("equal"); ax[0].set_xlabel("world x"); ax[0].set_ylabel("world y")
    ax[0].set_title("Head path (15 s) by friction anisotropy"); ax[0].legend(fontsize=7.5); ax[0].grid(alpha=0.3)
    ax[1].plot(RATIOS, [disp[r] for r in RATIOS], "o-", color="#2c6fbb", lw=2)
    ax[1].axhline(disp[1], ls="--", color="0.6", lw=1, label="isotropic (no thrust)")
    ax[1].set_xlabel("friction anisotropy  mu_trans / mu_long")
    ax[1].set_ylabel("net displacement (body lengths ~ /1.0)")
    ax[1].set_title("Displacement rises with anisotropy\n(gravity-set friction, belly-scale thrust)")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "gravity_locomotion.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
