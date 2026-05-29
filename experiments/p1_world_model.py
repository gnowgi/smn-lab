# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P1 -- a multi-CAZ mobile agent ('toy mouse') that builds a world model.

A planar agent with a steering Coordinated Action Zone (pull-only antagonist
pair) and a five-whisker rangefinder fan explores a walled arena containing two
objects. A Basal Action Pattern (CPG) provides the locomotor drive; a Haltable
Action Pattern, recruited by the whisker affordances, steers toward open space
and halts the drive when the front is blocked.

From its own pose (proprioception) plus each whisker's known angle and measured
distance, the agent places every hit in world coordinates and accumulates them
into an occupancy map -- the "picture" it constructs of its world from action and
modulated sensation. We then score that map against the true arena.

Run:  ../.venv/bin/python p1_world_model.py        (from this directory)
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.model import build_p1_xml
from smn_lab.control import OpponentBoard, CPG, HAPExplorer
from smn_lab.worldmodel import OccupancyMap, surface_samples, coverage_precision

# ---- parameters -----------------------------------------------------------
SEED = 3
DT = 0.005
T_END = 160.0
ARENA = 1.4
WHISK_DEG = (-60, -30, 0, 30, 60)
MAP_HALF = ARENA + 0.1
MAP_RES = 0.04
MAX_RAY = 4.0          # readings beyond this are treated as no-hit
OBJECTS = [
    {"type": "cyl", "x": 0.55, "y": 0.45, "r": 0.12},
    {"type": "box", "x": -0.6, "y": -0.35, "hx": 0.12, "hy": 0.18},
]


def run():
    rng = np.random.default_rng(SEED)
    angles = np.radians(WHISK_DEG)
    model = mujoco.MjModel.from_xml_string(build_p1_xml(arena_half=ARENA,
                                                        whisker_angles_deg=WHISK_DEG))
    data = mujoco.MjData(model)

    aid_r = model.actuator("m_yaw_right").id
    aid_l = model.actuator("m_yaw_left").id
    bid = model.body("mouse").id
    qx = model.jnt_qposadr[model.joint("slide_x").id]
    qy = model.jnt_qposadr[model.joint("slide_y").id]
    qyaw = model.jnt_qposadr[model.joint("yaw").id]
    vyaw = model.jnt_dofadr[model.joint("yaw").id]
    whisk_ids = [model.sensor(f"whisker_{i}").id for i in range(len(WHISK_DEG))]
    whisk_adr = [model.sensor_adr[s] for s in whisk_ids]
    whisk_site_ids = [model.site(f"whisker_{i}").id for i in range(len(WHISK_DEG))]

    board = OpponentBoard(kp=5.0, kd=0.6, cmax=2.5)
    bap = CPG(thrust=0.6)
    hap = HAPExplorer(angles, seed=SEED)
    occ = OccupancyMap(half=MAP_HALF, res=MAP_RES)

    # start somewhere off-centre, facing a random direction
    data.qpos[qx], data.qpos[qy] = -0.8, 0.7
    data.qpos[qyaw] = -0.6
    mujoco.mj_forward(model, data)

    n = int(T_END / DT)
    traj = np.zeros((n, 2))
    for k in range(n):
        t = k * DT
        x, y, yaw = data.qpos[qx], data.qpos[qy], data.qpos[qyaw]
        yaw_dot = data.qvel[vyaw]
        dists = np.array([data.sensordata[a] for a in whisk_adr])
        dists = np.where(dists < 0, MAX_RAY, dists)

        offset, gate = hap.command(dists)
        a_r, a_l, _ = board.commands(yaw, yaw_dot, yaw + offset, 0.0)
        data.ctrl[aid_r], data.ctrl[aid_l] = a_r, a_l

        thrust = bap.drive(t) * gate
        data.xfrc_applied[bid, 0] = thrust * math.cos(yaw)
        data.xfrc_applied[bid, 1] = thrust * math.sin(yaw)

        mujoco.mj_step(model, data)

        # place whisker hits in world coordinates using each whisker's exact
        # site frame (origin = site world position; direction = site +Z axis)
        traj[k] = (data.qpos[qx], data.qpos[qy])
        dists = np.array([data.sensordata[a] for a in whisk_adr])
        for i, d in enumerate(dists):
            if 0 <= d < MAX_RAY:
                sid = whisk_site_ids[i]
                ox, oy = data.site_xpos[sid][0], data.site_xpos[sid][1]
                zmat = data.site_xmat[sid].reshape(3, 3)
                occ.add_hit(ox + d * zmat[0, 2], oy + d * zmat[1, 2])

    return occ, traj


def plot(occ, traj, cov, prec, out):
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    # ground truth
    ax.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA,
                           fill=False, ec="#999", lw=2))
    ax.add_patch(Circle((0.55, 0.45), 0.12, fill=False, ec="#999", lw=2))
    ax.add_patch(Rectangle((-0.6 - 0.12, -0.35 - 0.18), 0.24, 0.36,
                           fill=False, ec="#999", lw=2))
    # trajectory + constructed point cloud
    ax.plot(traj[:, 0], traj[:, 1], color="#3a7", lw=0.5, alpha=0.6, label="exploration path")
    if occ.pts:
        p = np.array(occ.pts)
        ax.scatter(p[:, 0], p[:, 1], s=1.5, c="#c33", alpha=0.5, label="constructed map (whisker hits)")
    ax.set_aspect("equal")
    ax.set_xlim(-MAP_HALF, MAP_HALF)
    ax.set_ylim(-MAP_HALF, MAP_HALF)
    ax.set_title("P1 — the agent constructs a picture of its world\n"
                 "from its own pose + whisker readings")
    ax.legend(loc="upper right", fontsize=8, markerscale=4)
    ax.text(0, -MAP_HALF + 0.04,
            f"coverage of true surfaces = {cov*100:.0f}%   |   precision = {prec*100:.0f}%",
            ha="center", fontsize=10, color="#333")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    occ, traj = run()
    truth = surface_samples(ARENA, OBJECTS)
    cov, prec = coverage_precision(np.array(occ.pts), truth, eps=0.06)
    print("\n=== P1 world-model construction ===")
    print(f"  whisker hits logged : {len(occ.pts)}")
    print(f"  coverage of surfaces: {cov*100:.1f}%")
    print(f"  precision           : {prec*100:.1f}%")
    print("  verdict:", "PASS — the agent built a faithful map of its world."
          if cov > 0.6 and prec > 0.6 else "PARTIAL — tune exploration/params.")
    plot(occ, traj, cov, prec, os.path.join(figdir, "p1_world_model.png"))
