# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Map-guided foraging — when the map's decay rate is a survival pressure.

In `p2_basal_coupling.py` food was found by chance: the HAP steered by wall
affordances only, and the trajectory crossed food now and then. The map of the
world existed but the agent did not act on it.

Here the HAP **reads a second living-snapshot layer** — a *food memory* in
which each consumption deposits a fading marker at the agent's dead-reckoned
position. When the path is clear of walls and the food memory holds a live
point in recall range, the HAP biases the turn toward the closest one. The map
is now *for something the agent needs*, not only a picture the modeller reads.

Crucially the map's **decay rate** is now a direct survival pressure:

  * **Slow decay** — food memory persists across the regrowth period; the agent
    revisits known spots in time for the next meal.
  * **Fast decay** — the memory fades within seconds; the agent is effectively
    a random forager again, and starves under the same world.

Three conditions hold everything else fixed:

  C1.  no map guidance         — wall-affordance HAP only (the basal-coupling baseline)
  C2.  map-guided, slow decay  — food memory decay 0.02 / s  (half-life ~35 s)
  C3.  map-guided, fast decay  — food memory decay 1.00 / s  (half-life ~0.7 s)

The arena holds **3 perimeter + 3 interior** food items at a slow regrowth
(60 s), so wall-following alone struggles — and remembering interior locations
makes the difference between alive and dead at T_END = 240 s.

Run:  ../.venv/bin/python p2_map_guided_foraging.py
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.body import MouseSchema
from smn_lab.model import build_p2_xml
from smn_lab.control import CPG, HAPExplorer, DifferentialDrive, DeadReckoner
from smn_lab.worldmodel import OccupancyMap

SEED = 3
DT = 0.005
T_END = 300.0
ARENA = 1.4
MAP_HALF = ARENA + 0.1
MAX_RAY = 4.0
START = (-0.8, 0.7, -0.6)

# biology (same as basal coupling)
E_MAX = 100.0
E_INIT = 100.0
E_BASAL = 0.50
E_MOVE = 1.50
E_FOOD = 32.0
E_CRIT_LOW = 5.0
E_CRIT_HI = 20.0

# world — harsh regime so memory matters: only 4 foods, half interior, slow regrowth.
# Random wall-follower can subsist on perimeter alone — but not for the full 300 s.
# Map-guided slow-decay can additionally revisit interior foods. Fast decay can't.
WALL_DECAY = 0.10
T_REGROW = 90.0
R_EAT = 0.13
FOODS = [(0.8, 0.9), (-0.9, 0.7),      # 2 perimeter (random finds these via wall-following)
         (0.3, 0.2), (-0.4, -0.3)]     # 2 interior  (only remembered locations bring agent back)

# food-memory steering parameters
FOOD_THRESH = 0.2          # cells above this in food_map count as "remembered"
FOOD_DEPOSIT = 2           # number of add_hit calls per consumption (peak ≈ 2.0)
FOOD_MEM_CAP = 3.0
RECALL_R = 2.0             # the agent will steer toward memory within this radius
RECALL_MIN = 0.20          # ignore points the agent is already on (don't U-turn)
K_STEER = 2.0              # turn = clip(K_STEER · angular_error)


def energy_gate(E):
    if E <= E_CRIT_LOW:
        return 0.0
    if E >= E_CRIT_HI:
        return 1.0
    return (E - E_CRIT_LOW) / (E_CRIT_HI - E_CRIT_LOW)


def run(use_map, food_decay, label):
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
    wall_map = OccupancyMap(half=MAP_HALF, res=0.04, decay=WALL_DECAY)
    food_map = OccupancyMap(half=MAP_HALF, res=0.04, decay=food_decay, cap=FOOD_MEM_CAP)

    data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = START
    mujoco.mj_forward(model, data)

    foods_alive = [True] * len(FOODS)
    eaten_at = [None] * len(FOODS)
    eaten_times = []
    n = int(T_END / DT)
    traj = np.zeros((n, 2))
    energy_log = np.zeros(n)
    used_memory_log = np.zeros(n, dtype=bool)   # was the turn map-guided this step?
    energy = E_INIT
    death_t = None
    ex, ey, eyaw = START

    for k in range(n):
        t = k * DT
        dists = np.array([data.sensordata[a] for a in w_adr])
        dists = np.where(dists < 0, MAX_RAY, dists)
        turn, gate = hap.command(dists)

        # map-guided override: only when the path is clear of walls (gate == 1)
        # and the food memory holds a live point in recall range
        used_memory = False
        if use_map and gate >= 1.0:
            live = food_map.live_points(FOOD_THRESH)
            if len(live):
                dx = live[:, 0] - ex
                dy = live[:, 1] - ey
                d = np.hypot(dx, dy)
                m = (d > RECALL_MIN) & (d < RECALL_R)
                if m.any():
                    pts = live[m]
                    ds = d[m]
                    idx = int(np.argmin(ds))
                    fx, fy = pts[idx]
                    ang = math.atan2(fy - ey, fx - ex)
                    err = math.atan2(math.sin(ang - eyaw), math.cos(ang - eyaw))
                    turn = max(-1.0, min(1.0, K_STEER * err))
                    used_memory = True

        forward = bap.drive(t) * gate * energy_gate(energy)
        acts = drive.activations(forward, turn)
        Fx, tau = drive.wrench(acts)
        yaw_real = data.qpos[qyaw]
        data.xfrc_applied[bid, 0] = Fx * math.cos(yaw_real)
        data.xfrc_applied[bid, 1] = Fx * math.sin(yaw_real)
        data.xfrc_applied[bid, 5] = tau
        mujoco.mj_step(model, data)

        # biological state
        drain = (E_BASAL + E_MOVE * abs(forward)) * DT
        energy = max(0.0, energy - drain)
        if energy <= 0.0 and death_t is None:
            death_t = t

        # food regrowth at the source
        for i in range(len(FOODS)):
            if (not foods_alive[i]) and eaten_at[i] is not None \
                    and (t - eaten_at[i]) >= T_REGROW:
                foods_alive[i] = True
                eaten_at[i] = None

        # dead-reckoned pose (the agent's own frame for both maps)
        vx, vy = data.sensordata[vel_adr], data.sensordata[vel_adr + 1]
        wz = data.sensordata[gyro_adr + 2]
        ex, ey, eyaw = dr.update(vx, vy, wz, DT)

        # food contact + deposit memory at the agent's estimated position
        bx, by = data.qpos[qx], data.qpos[qy]
        for i, (fx_w, fy_w) in enumerate(FOODS):
            if foods_alive[i] and (bx - fx_w) ** 2 + (by - fy_w) ** 2 < R_EAT * R_EAT:
                foods_alive[i] = False
                eaten_at[i] = t
                energy = min(E_MAX, energy + E_FOOD)
                for _ in range(FOOD_DEPOSIT):
                    food_map.add_hit(ex, ey)
                eaten_times.append((t, fx_w, fy_w))

        # both maps decay; wall map updates from whisker hits
        wall_map.decay_step(DT)
        food_map.decay_step(DT)
        c, s = math.cos(eyaw), math.sin(eyaw)
        for i, (wx_b, wy_b, a_b) in enumerate(schema.whiskers):
            d = dists[i]
            if 0 <= d < MAX_RAY:
                sx, sy = ex + wx_b * c - wy_b * s, ey + wx_b * s + wy_b * c
                ang = eyaw + a_b
                wall_map.add_hit(sx + d * math.cos(ang), sy + d * math.sin(ang))

        traj[k] = (bx, by)
        energy_log[k] = energy
        used_memory_log[k] = used_memory

    return dict(traj=traj, energy=energy_log, eaten=eaten_times,
                death_t=death_t, foods_alive=foods_alive,
                wall_live=wall_map.live_points(0.5),
                food_live=food_map.live_points(FOOD_THRESH),
                used_memory=used_memory_log,
                label=label)


def _arena(ax):
    ax.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#bbb", lw=1))
    ax.set_aspect("equal"); ax.set_xlim(-MAP_HALF, MAP_HALF); ax.set_ylim(-MAP_HALF, MAP_HALF)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    print("\n=== map-guided foraging — the map's decay rate is a survival pressure ===")
    runs = [
        run(use_map=False, food_decay=0.0, label="C1 random (no map guidance)"),
        run(use_map=True, food_decay=0.02, label="C2 map-guided, slow decay (0.02/s)"),
        run(use_map=True, food_decay=1.0, label="C3 map-guided, fast decay (1.0/s)"),
    ]
    def state(c):
        return "alive" if c["death_t"] is None else f"died at t={c['death_t']:5.1f}s"
    for r in runs:
        guided_frac = r["used_memory"].mean()
        print(f"  {r['label']:42s}: {state(r):20s} "
              f"events={len(r['eaten']):3d}  mean E={r['energy'].mean():5.1f}  "
              f"guided={100*guided_frac:4.1f}%")

    fig, axes = plt.subplots(2, 3, figsize=(14.5, 8.5),
                             gridspec_kw={"height_ratios": [1.3, 0.9]})
    for col, r in enumerate(runs):
        ax = axes[0, col]; _arena(ax)
        # the trajectory (light)
        ax.plot(r["traj"][:, 0], r["traj"][:, 1], color="#444", lw=0.4, alpha=0.5)
        # wall live map (faint red)
        if len(r["wall_live"]):
            ax.scatter(r["wall_live"][:, 0], r["wall_live"][:, 1],
                       s=1.5, c="#c33", alpha=0.35)
        # food memory live points — orange squares, what the agent thinks it remembers
        if len(r["food_live"]):
            ax.scatter(r["food_live"][:, 0], r["food_live"][:, 1],
                       s=22, c="#e09000", alpha=0.85, marker="s", zorder=4,
                       edgecolors="white", lw=0.5, label="food memory")
        # food (alive = green dot, currently eaten = gray ×) — ground truth
        for i, (fx, fy) in enumerate(FOODS):
            if r["foods_alive"][i]:
                ax.scatter([fx], [fy], s=70, c="#2c7a2c", marker="o",
                           zorder=6, edgecolors="white", lw=1)
            else:
                ax.scatter([fx], [fy], s=40, c="#555", marker="x", zorder=6)
        ax.set_title(f"{r['label']}\n→ {state(r)}", fontsize=10)
        if col == 0:
            ax.legend(loc="lower left", fontsize=8)

        ax = axes[1, col]
        t = np.arange(len(r["energy"])) * DT
        ax.plot(t, r["energy"], color="#c33", lw=1.2)
        ax.axhline(0, color="#888", ls=":", lw=0.8)
        ax.axhline(E_CRIT_LOW, color="#e09000", ls=":", lw=0.8)
        for (te, _, _) in r["eaten"]:
            ax.axvline(te, color="#2c7a2c", lw=0.5, alpha=0.6)
        if r["death_t"] is not None:
            ax.axvline(r["death_t"], color="#900", lw=1.0)
        ax.set_xlim(0, T_END); ax.set_ylim(-2, E_MAX + 5)
        ax.set_xlabel("time (s)"); ax.set_ylabel("energy")
        ax.grid(alpha=0.25)
        ax.set_title(f"consumption events: {len(r['eaten'])},  "
                     f"mean E: {r['energy'].mean():.0f}", fontsize=9)

    fig.suptitle("Map-guided foraging — when the map's decay rate is a survival pressure.\n"
                 "(Same world, same body, same biology; only the food-memory decay differs.)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(figdir, "p2_map_guided_foraging.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
