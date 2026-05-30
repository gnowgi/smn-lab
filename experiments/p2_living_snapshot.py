# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The living snapshot -- a world model that decays where it is not revisited.

The SMN holds that the snapshot is not stored but continuously revised: "always
already becoming a different snapshot." Here the occupancy map is given a decay
rate, so cells lose evidence unless the agent keeps seeing them. The world model
becomes a dynamic equilibrium between mapping (whisker hits reinforce) and
forgetting (decay) -- a *living* snapshot rather than a monotonic record.

Two results:
  * a time-lapse of the live map at a moderate decay -- a region of recent
    knowledge that trails the agent and fades behind it;
  * coverage of the full arena vs decay rate -- how much of the world the agent
    can hold at once falls as the snapshot fades faster than it is refreshed.

Run:  ../.venv/bin/python p2_living_snapshot.py        (from this directory)
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.gridspec import GridSpec
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.body import MouseSchema
from smn_lab.model import build_p2_xml
from smn_lab.control import CPG, HAPExplorer, DifferentialDrive, DeadReckoner
from smn_lab.worldmodel import OccupancyMap, surface_samples, coverage_precision

SEED = 3
DT = 0.005
T_END = 120.0
ARENA = 1.4
MAP_HALF = ARENA + 0.1
MAX_RAY = 4.0
THRESH = 0.5
START = (-0.8, 0.7, -0.6)
OBJECTS = [{"type": "cyl", "x": 0.55, "y": 0.45, "r": 0.12},
           {"type": "box", "x": -0.6, "y": -0.35, "hx": 0.12, "hy": 0.18}]
DECAYS = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8]   # per-second; 0 = accumulator
TL_DECAY = 0.4                             # decay used for the time-lapse
TL_TIMES = [25.0, 60.0, 95.0, 119.0]


def run_decay(decay, snapshot_times=()):
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
    bap = CPG(thrust=0.6)
    hap = HAPExplorer(angles, seed=SEED)
    dr = DeadReckoner(*START)
    occ = OccupancyMap(half=MAP_HALF, res=0.04, decay=decay)

    data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = START
    mujoco.mj_forward(model, data)

    pending = sorted(snapshot_times)
    snaps = {}
    n = int(T_END / DT)
    for k in range(n):
        t = k * DT
        dists = np.array([data.sensordata[a] for a in w_adr])
        dists = np.where(dists < 0, MAX_RAY, dists)
        turn, gate = hap.command(dists)
        forward = bap.drive(t) * gate
        acts = drive.activations(forward, turn)
        Fx, tau = drive.wrench(acts)
        yaw_real = data.qpos[qyaw]
        data.xfrc_applied[bid, 0] = Fx * math.cos(yaw_real)
        data.xfrc_applied[bid, 1] = Fx * math.sin(yaw_real)
        data.xfrc_applied[bid, 5] = tau
        mujoco.mj_step(model, data)

        vx, vy = data.sensordata[vel_adr], data.sensordata[vel_adr + 1]
        wz = data.sensordata[gyro_adr + 2]
        ex, ey, eyaw = dr.update(vx, vy, wz, DT)

        occ.decay_step(DT)
        dists = np.array([data.sensordata[a] for a in w_adr])
        c, s = math.cos(eyaw), math.sin(eyaw)
        for i, (wx_b, wy_b, a_b) in enumerate(schema.whiskers):
            d = dists[i]
            if 0 <= d < MAX_RAY:
                sx, sy = ex + wx_b * c - wy_b * s, ey + wx_b * s + wy_b * c
                ang = eyaw + a_b
                occ.add_hit(sx + d * math.cos(ang), sy + d * math.sin(ang))

        if pending and t >= pending[0]:
            snaps[pending.pop(0)] = (occ.live_points(THRESH), (ex, ey))

    truth = surface_samples(ARENA, OBJECTS)
    cov, prec = coverage_precision(occ.live_points(THRESH), truth, eps=0.06)
    return cov, prec, snaps


def _arena(ax):
    ax.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#bbb", lw=1))
    ax.add_patch(Circle((0.55, 0.45), 0.12, fill=False, ec="#bbb", lw=1))
    ax.add_patch(Rectangle((-0.72, -0.53), 0.24, 0.36, fill=False, ec="#bbb", lw=1))
    ax.set_aspect("equal"); ax.set_xlim(-MAP_HALF, MAP_HALF); ax.set_ylim(-MAP_HALF, MAP_HALF)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    print("\n=== living snapshot: coverage of the full arena vs decay rate ===")
    print(f"  {'decay (1/s)':>11s} {'half-life':>10s} {'live coverage':>14s}")
    covs = []
    for d in DECAYS:
        cov, prec, _ = run_decay(d)
        covs.append(cov)
        hl = "inf" if d == 0 else f"{math.log(2)/d:.1f} s"
        print(f"  {d:11.2f} {hl:>10s} {cov*100:13.1f}%")

    _, _, snaps = run_decay(TL_DECAY, TL_TIMES)

    fig = plt.figure(figsize=(12, 7))
    gs = GridSpec(2, 4, figure=fig, height_ratios=[1.0, 0.8])
    for col, t in enumerate(TL_TIMES):
        ax = fig.add_subplot(gs[0, col])
        _arena(ax)
        pts, (ex, ey) = snaps[t]
        if len(pts):
            ax.scatter(pts[:, 0], pts[:, 1], s=2.0, c="#c33", alpha=0.6)
        ax.scatter([ex], [ey], s=30, c="#2a5cc8", marker="o", zorder=5)  # agent
        ax.set_title(f"t = {t:.0f} s", fontsize=10)
    axc = fig.add_subplot(gs[1, :])
    axc.plot(DECAYS, [c * 100 for c in covs], "o-", color="#c33")
    axc.axvline(TL_DECAY, color="#2a5cc8", ls=":", lw=1, label=f"time-lapse decay = {TL_DECAY}/s")
    axc.set_xlabel("decay rate (1/s)  —  faster forgetting →")
    axc.set_ylabel("live coverage of\nfull arena (%)")
    axc.set_ylim(0, 100); axc.grid(alpha=0.3); axc.legend(fontsize=8, loc="upper right")
    fig.suptitle("The living snapshot: the world model fades where it is not revisited\n"
                 "(top: the held map trails the agent at decay = "
                 f"{TL_DECAY}/s; bottom: how much it can hold at once vs decay rate)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(figdir, "p2_living_snapshot.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")
    print(f"  accumulator (decay 0) holds {covs[0]*100:.0f}% of the arena; "
          f"at {DECAYS[-1]}/s only {covs[-1]*100:.0f}% — a moving local snapshot.")


if __name__ == "__main__":
    main()
