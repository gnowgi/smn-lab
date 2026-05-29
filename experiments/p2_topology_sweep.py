# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The balance-beam sweep -- does the structure of the modulatory coupling and
the body geometry determine the structure of the world the agent can build?

Each condition runs the self-localized mapper (P2 foundation) under a different
"balance beam", varying BOTH:
  (a) information-routing topology -- how whisker affordances are routed into the
      steering command: flat/distributed vs hierarchical/layered;
  (b) physical body geometry -- number/placement of zones: whisker count and
      drive-zone track width;
plus the architectural toggles +/-BAP (the locomotor drive) and +/-HAP (the
affordance-recruited haltable action), and proprioceptive noise.

For each, we measure the constructed world model (coverage, precision) and the
dead-reckoning drift, all built from the agent's own body geometry + self-motion
sense. Output: a results table and a grid of the constructed maps.

Run:  ../.venv/bin/python p2_topology_sweep.py        (from this directory)
"""
from __future__ import annotations
import os, sys, math, csv, re
from dataclasses import dataclass, field
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

DT = 0.005
T_END = 120.0
ARENA = 1.4
MAP_HALF = ARENA + 0.1
MAX_RAY = 4.0
START = (-0.8, 0.7, -0.6)
OBJECTS = [
    {"type": "cyl", "x": 0.55, "y": 0.45, "r": 0.12},
    {"type": "box", "x": -0.6, "y": -0.35, "hx": 0.12, "hy": 0.18},
]
FIVE = (-60, -30, 0, 30, 60)


@dataclass
class Condition:
    name: str
    whiskers: tuple = FIVE
    drive_offset_y: float = 0.05
    routing: str = "flat"
    bap: bool = True
    hap: bool = True
    prop_noise: float = 0.0


CONDITIONS = [
    Condition("full (5w · flat · BAP+HAP)"),
    Condition("hierarchical routing", routing="hierarchical"),
    Condition("sparse (3 whiskers)", whiskers=(-50, 0, 50)),
    Condition("dense (9 whiskers)", whiskers=(-72, -54, -36, -18, 0, 18, 36, 54, 72)),
    Condition("narrow track", drive_offset_y=0.025),
    Condition("wide track", drive_offset_y=0.10),
    Condition("- BAP (no drive)", bap=False),
    Condition("- HAP (no steering)", hap=False),
    Condition("noisy proprioception", prop_noise=0.08),
]


def run_condition(cond: Condition, seed: int = 3):
    schema = MouseSchema(whisker_angles_deg=cond.whiskers, drive_offset_y=cond.drive_offset_y)
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
    hap = HAPExplorer(angles, routing=cond.routing, seed=seed) if cond.hap else None
    dr = DeadReckoner(*START)
    nrng = np.random.default_rng(seed + 100)

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

        if hap is not None:
            turn, gate = hap.command(dists)
        else:                       # -HAP: drive straight, never halt or steer
            turn, gate = 0.0, 1.0
        forward = (bap.drive(t) if cond.bap else 0.0) * gate
        acts = drive.activations(forward, turn)
        Fx, tau = drive.wrench(acts)

        yaw_real = data.qpos[qyaw]
        data.xfrc_applied[bid, 0] = Fx * math.cos(yaw_real)
        data.xfrc_applied[bid, 1] = Fx * math.sin(yaw_real)
        data.xfrc_applied[bid, 5] = tau
        mujoco.mj_step(model, data)

        vx = data.sensordata[vel_adr] + nrng.normal(0, cond.prop_noise)
        vy = data.sensordata[vel_adr + 1] + nrng.normal(0, cond.prop_noise)
        wz = data.sensordata[gyro_adr + 2] + nrng.normal(0, cond.prop_noise * 1.5)
        ex, ey, eyaw = dr.update(vx, vy, wz, DT)

        dists = np.array([data.sensordata[a] for a in w_adr])
        c, s = math.cos(eyaw), math.sin(eyaw)
        for i, (wx_b, wy_b, a_b) in enumerate(schema.whiskers):
            d = dists[i]
            if 0 <= d < MAX_RAY:
                sx, sy = ex + wx_b * c - wy_b * s, ey + wx_b * s + wy_b * c
                ang = eyaw + a_b
                occ.add_hit(sx + d * math.cos(ang), sy + d * math.sin(ang))
        true_traj[k] = (data.qpos[qx], data.qpos[qy])
        est_traj[k] = (ex, ey)

    drift = float(np.hypot(true_traj[-1, 0] - est_traj[-1, 0], true_traj[-1, 1] - est_traj[-1, 1]))
    truth = surface_samples(ARENA, OBJECTS)
    cov, prec = coverage_precision(np.array(occ.pts), truth, eps=0.06) if occ.pts else (0.0, 0.0)
    return dict(cov=cov, prec=prec, drift=drift,
                pts=np.array(occ.pts) if occ.pts else np.empty((0, 2)),
                true_traj=true_traj, est_traj=est_traj)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    rng = np.random.default_rng(0)

    results = []
    print("\n=== balance-beam sweep — constructed world model per condition ===")
    print(f"  {'condition':28s} {'coverage':>9s} {'precision':>10s} {'drift(cm)':>10s}")
    for cond in CONDITIONS:
        r = run_condition(cond)
        results.append((cond, r))
        print(f"  {cond.name:28s} {r['cov']*100:8.1f}% {r['prec']*100:9.1f}% {r['drift']*100:9.2f}")

    # ---- persist the data (a lab keeps its raw data) ----
    datadir = os.path.join(here, "..", "data")
    os.makedirs(datadir, exist_ok=True)
    with open(os.path.join(datadir, "sweep_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["condition", "coverage", "precision", "drift_cm", "n_hits",
                    "whiskers", "drive_offset_y", "routing", "bap", "hap", "prop_noise"])
        for cond, r in results:
            w.writerow([cond.name, f"{r['cov']:.4f}", f"{r['prec']:.4f}", f"{r['drift']*100:.3f}",
                        len(r["pts"]), "|".join(map(str, cond.whiskers)), cond.drive_offset_y,
                        cond.routing, int(cond.bap), int(cond.hap), cond.prop_noise])
    np.savez_compressed(os.path.join(datadir, "truth_surface.npz"),
                        truth=surface_samples(ARENA, OBJECTS))
    for cond, r in results:
        slug = re.sub(r"[^a-z0-9]+", "_", cond.name.lower()).strip("_")
        np.savez_compressed(os.path.join(datadir, f"sweep_{slug}.npz"),
                            hits=r["pts"], true_traj=r["true_traj"], est_traj=r["est_traj"],
                            cov=r["cov"], prec=r["prec"], drift=r["drift"])
    print(f"[saved] data/sweep_results.csv + per-condition .npz ({len(results)} conditions)")

    fig, axes = plt.subplots(3, 3, figsize=(11, 11))
    for ax, (cond, r) in zip(axes.ravel(), results):
        ax.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#bbb", lw=1))
        ax.add_patch(Circle((0.55, 0.45), 0.12, fill=False, ec="#bbb", lw=1))
        ax.add_patch(Rectangle((-0.72, -0.53), 0.24, 0.36, fill=False, ec="#bbb", lw=1))
        p = r["pts"]
        if len(p) > 3000:
            p = p[rng.choice(len(p), 3000, replace=False)]
        if len(p):
            ax.scatter(p[:, 0], p[:, 1], s=1.0, c="#c33", alpha=0.5)
        ax.set_aspect("equal")
        ax.set_xlim(-MAP_HALF, MAP_HALF)
        ax.set_ylim(-MAP_HALF, MAP_HALF)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{cond.name}\ncov {r['cov']*100:.0f}% · drift {r['drift']*100:.1f} cm", fontsize=9)
    fig.suptitle("The balance-beam sweep: does the modulatory coupling + body geometry\n"
                 "shape the world model the agent can construct?", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = os.path.join(figdir, "p2_topology_sweep.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
