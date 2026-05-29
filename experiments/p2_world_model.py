# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P2 foundation -- a body-geometry-relative, self-localized world model.

This makes the body geometry explicit and the mapping honest. The 'mouse' is
built from a body schema (smn_lab.body.MouseSchema): two LOCATED rear drive
zones produce locomotion and steering from their positions, and a whisker fan
senses. Crucially, the agent does NOT read its absolute pose. It estimates its
pose by dead-reckoning its own proprioception (velocimeter + gyro), and places
every whisker hit using that estimate together with the known body-frame
position/angle of the whisker. The world model is thus built entirely from the
agent's own body geometry and self-motion sense -- in relation to its body, as
the architecture claims.

We report map quality (coverage / precision against the true arena) and the
dead-reckoning drift (final true-vs-estimated pose error). These are the
quantities the balance-beam topology sweep will compare.

Run:  ../.venv/bin/python p2_world_model.py        (from this directory)
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
from smn_lab.body import MouseSchema
from smn_lab.model import build_p2_xml
from smn_lab.control import CPG, HAPExplorer, DifferentialDrive, DeadReckoner
from smn_lab.worldmodel import OccupancyMap, surface_samples, coverage_precision

SEED = 3
DT = 0.005
T_END = 160.0
ARENA = 1.4
MAP_HALF = ARENA + 0.1
MAX_RAY = 4.0
START = (-0.8, 0.7, -0.6)   # the agent knows its own starting pose
OBJECTS = [
    {"type": "cyl", "x": 0.55, "y": 0.45, "r": 0.12},
    {"type": "box", "x": -0.6, "y": -0.35, "hx": 0.12, "hy": 0.18},
]


def run():
    schema = MouseSchema()
    angles = np.array([a for (_, _, a) in schema.whiskers])
    model = mujoco.MjModel.from_xml_string(build_p2_xml(schema, arena_half=ARENA))
    data = mujoco.MjData(model)

    bid = model.body("mouse").id
    qx = model.jnt_qposadr[model.joint("slide_x").id]
    qy = model.jnt_qposadr[model.joint("slide_y").id]
    qyaw = model.jnt_qposadr[model.joint("yaw").id]
    w_adr = [model.sensor_adr[model.sensor(f"whisker_{i}").id] for i in range(len(angles))]
    vel_adr = model.sensor_adr[model.sensor("vel").id]
    gyro_adr = model.sensor_adr[model.sensor("gyro").id]

    drive = DifferentialDrive(schema, amax=1.2, turn_gain=1.0)
    bap = CPG(thrust=0.6)        # base forward activation level
    hap = HAPExplorer(angles, seed=SEED)
    dr = DeadReckoner(*START)    # anchored at the known start

    data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = START
    mujoco.mj_forward(model, data)

    occ = OccupancyMap(half=MAP_HALF, res=0.04)
    n = int(T_END / DT)
    true_traj = np.zeros((n, 2))
    est_traj = np.zeros((n, 2))

    for k in range(n):
        t = k * DT
        dists = np.array([data.sensordata[a] for a in w_adr])
        dists = np.where(dists < 0, MAX_RAY, dists)

        turn, gate = hap.command(dists)
        forward = bap.drive(t) * gate
        acts = drive.activations(forward, turn)
        Fx, tau = drive.wrench(acts)

        yaw_real = data.qpos[qyaw]           # physics uses the true heading
        data.xfrc_applied[bid, 0] = Fx * math.cos(yaw_real)
        data.xfrc_applied[bid, 1] = Fx * math.sin(yaw_real)
        data.xfrc_applied[bid, 5] = tau

        mujoco.mj_step(model, data)

        # proprioception -> self-localization (the agent's only pose knowledge)
        vx, vy = data.sensordata[vel_adr], data.sensordata[vel_adr + 1]
        wz = data.sensordata[gyro_adr + 2]
        ex, ey, eyaw = dr.update(vx, vy, wz, DT)

        true_traj[k] = (data.qpos[qx], data.qpos[qy])
        est_traj[k] = (ex, ey)

        # place hits from the ESTIMATED pose + the known body-frame whisker geometry
        dists = np.array([data.sensordata[a] for a in w_adr])
        c, s = math.cos(eyaw), math.sin(eyaw)
        for i, (wx_b, wy_b, a_b) in enumerate(schema.whiskers):
            d = dists[i]
            if 0 <= d < MAX_RAY:
                sx = ex + wx_b * c - wy_b * s
                sy = ey + wx_b * s + wy_b * c
                ang = eyaw + a_b
                occ.add_hit(sx + d * math.cos(ang), sy + d * math.sin(ang))

    drift = float(np.hypot(true_traj[-1, 0] - est_traj[-1, 0],
                           true_traj[-1, 1] - est_traj[-1, 1]))
    return occ, true_traj, est_traj, drift


def plot(occ, true_traj, est_traj, cov, prec, drift, out):
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#999", lw=2))
    ax.add_patch(Circle((0.55, 0.45), 0.12, fill=False, ec="#999", lw=2))
    ax.add_patch(Rectangle((-0.72, -0.53), 0.24, 0.36, fill=False, ec="#999", lw=2))
    ax.plot(true_traj[:, 0], true_traj[:, 1], color="#999", lw=0.5, alpha=0.6, label="true path")
    ax.plot(est_traj[:, 0], est_traj[:, 1], color="#3a7", lw=0.6, alpha=0.7, label="self-estimated path")
    if occ.pts:
        p = np.array(occ.pts)
        ax.scatter(p[:, 0], p[:, 1], s=1.5, c="#c33", alpha=0.5, label="constructed map (self-localized)")
    ax.set_aspect("equal")
    ax.set_xlim(-MAP_HALF, MAP_HALF)
    ax.set_ylim(-MAP_HALF, MAP_HALF)
    ax.set_title("P2 foundation — world model built from body geometry +\n"
                 "proprioceptive self-localization (no god's-eye pose)")
    ax.legend(loc="upper right", fontsize=8, markerscale=4)
    ax.text(0, -MAP_HALF + 0.04,
            f"coverage = {cov*100:.0f}%   precision = {prec*100:.0f}%   "
            f"dead-reckoning drift = {drift*100:.1f} cm",
            ha="center", fontsize=10, color="#333")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    occ, true_traj, est_traj, drift = run()
    truth = surface_samples(ARENA, OBJECTS)
    cov, prec = coverage_precision(np.array(occ.pts), truth, eps=0.06)
    print("\n=== P2 foundation — self-localized world model ===")
    print(f"  whisker hits logged : {len(occ.pts)}")
    print(f"  coverage of surfaces: {cov*100:.1f}%")
    print(f"  precision           : {prec*100:.1f}%")
    print(f"  dead-reckoning drift: {drift*100:.2f} cm (final true-vs-estimated)")
    print("  verdict:", "PASS — built from its own body geometry + proprioception."
          if cov > 0.6 and prec > 0.6 else "PARTIAL — tune.")
    plot(occ, true_traj, est_traj, cov, prec, drift, os.path.join(figdir, "p2_world_model.png"))
