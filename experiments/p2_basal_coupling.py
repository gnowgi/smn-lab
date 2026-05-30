# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Basal coupling — the first telling simulation of why a cognizing agent moves.

The constructive assumptions:

  * The basal action pattern (BAP) needs **energy** to fire. As energy depletes,
    the drive smoothly weakens; at zero, it fails and the agent halts forever.
  * Energy depletes with **movement** (and at a small basal rate even at rest).
  * Energy is replenished only by **food**, which is in the world.
  * The **map** of the world is a living snapshot (it decays where unrevisited).
  * Therefore: no movement → no live map; no food → no energy → no BAP → no
    movement. The same loop, closed through the body, is why an organism moves
    and why the cognitive substrate is inseparable from biology.

The simulation runs two conditions to make the coupling visible:

  A. **No food**: the agent moves, drains its reserve, and dies of starvation.
  B. **With food**: the agent encounters food while exploring (the map keeps it
     going to fresh territory), refills its reserve, and stays alive.

Run:  ../.venv/bin/python p2_basal_coupling.py        (from this directory)
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
from smn_lab.worldmodel import OccupancyMap

SEED = 3
DT = 0.005
T_END = 180.0
ARENA = 1.4
MAP_HALF = ARENA + 0.1
MAX_RAY = 4.0
START = (-0.8, 0.7, -0.6)

# --- biological state (the basal coupling) ---
E_MAX = 100.0          # maximum energy reserve
E_INIT = 100.0
E_BASAL = 0.50         # cost at rest, per second
E_MOVE = 1.50          # cost per unit forward drive, per second
E_FOOD = 25.0          # gain on consumption
E_CRIT_LOW = 5.0       # drive fails at or below this
E_CRIT_HI = 20.0       # drive at full above this
DECAY = 0.10           # living-snapshot decay rate
R_EAT = 0.13           # body reach for food contact (~ body half-width + food radius)
T_REGROW = 30.0        # food regrows at its source after this delay (an ecosystem)

FOODS = [(0.8, 0.9), (-0.9, 0.7), (0.6, -0.9), (-0.8, -0.7),
         (0.0, 1.1), (1.1, 0.0), (-1.1, -0.2), (0.3, -1.1)]


def energy_gate(E: float) -> float:
    """The BAP fires fully only when energy is well above the critical floor."""
    if E <= E_CRIT_LOW:
        return 0.0
    if E >= E_CRIT_HI:
        return 1.0
    return (E - E_CRIT_LOW) / (E_CRIT_HI - E_CRIT_LOW)


def run(food_positions):
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
    occ = OccupancyMap(half=MAP_HALF, res=0.04, decay=DECAY)

    data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = START
    mujoco.mj_forward(model, data)

    foods_alive = [True] * len(food_positions)
    eaten_at = [None] * len(food_positions)   # for regrowth
    eaten_times = []                          # every consumption event
    n = int(T_END / DT)
    traj = np.zeros((n, 2))
    energy_log = np.zeros(n)
    energy = E_INIT
    death_t = None

    for k in range(n):
        t = k * DT
        dists = np.array([data.sensordata[a] for a in w_adr])
        dists = np.where(dists < 0, MAX_RAY, dists)
        turn, gate = hap.command(dists)
        forward = bap.drive(t) * gate * energy_gate(energy)
        acts = drive.activations(forward, turn)
        Fx, tau = drive.wrench(acts)
        yaw_real = data.qpos[qyaw]
        data.xfrc_applied[bid, 0] = Fx * math.cos(yaw_real)
        data.xfrc_applied[bid, 1] = Fx * math.sin(yaw_real)
        data.xfrc_applied[bid, 5] = tau
        mujoco.mj_step(model, data)

        # biological state: energy drains with movement, basal cost at rest
        drain = (E_BASAL + E_MOVE * abs(forward)) * DT
        energy = max(0.0, energy - drain)
        if energy <= 0.0 and death_t is None:
            death_t = t

        # food regrows at its source after T_REGROW (an ecosystem, not a larder)
        for i in range(len(food_positions)):
            if (not foods_alive[i]) and eaten_at[i] is not None \
                    and (t - eaten_at[i]) >= T_REGROW:
                foods_alive[i] = True
                eaten_at[i] = None

        # food contact: a body-frame proximity check (no special sensing)
        bx, by = data.qpos[qx], data.qpos[qy]
        for i, (fx, fy) in enumerate(food_positions):
            if foods_alive[i] and (bx - fx) ** 2 + (by - fy) ** 2 < R_EAT * R_EAT:
                foods_alive[i] = False
                eaten_at[i] = t
                energy = min(E_MAX, energy + E_FOOD)
                eaten_times.append((t, fx, fy))

        # self-localized map (only meaningful while the agent moves)
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

        traj[k] = (bx, by)
        energy_log[k] = energy

    return dict(traj=traj, energy=energy_log, eaten=eaten_times,
                death_t=death_t, foods=food_positions,
                foods_alive=foods_alive, live_map=occ.live_points(0.5))


def _arena(ax):
    ax.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#bbb", lw=1))
    ax.set_aspect("equal"); ax.set_xlim(-MAP_HALF, MAP_HALF); ax.set_ylim(-MAP_HALF, MAP_HALF)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    print("\n=== basal coupling — viability under (energy · food · map · motion) ===")
    a = run([])
    b = run(FOODS)
    def state(c):
        return "alive" if c["death_t"] is None else f"died at t = {c['death_t']:.1f} s"
    print(f"  no food  : {state(a)}   (final energy = {a['energy'][-1]:.1f})")
    print(f"  with food: {state(b)},  consumption events = {len(b['eaten'])},"
          f"  final energy = {b['energy'][-1]:.1f}")

    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5),
                             gridspec_kw={"height_ratios": [1.3, 0.9]})
    state_a = "alive" if a["death_t"] is None else f"died at t={a['death_t']:.0f}s"
    state_b = "alive" if b["death_t"] is None else f"died at t={b['death_t']:.0f}s"
    for col, (cond, name) in enumerate([(a, f"no food → {state_a}"),
                                        (b, f"with food → {state_b}")]):
        ax = axes[0, col]; _arena(ax)
        # food (alive = green dot, eaten = gray ×)
        for i, (fx, fy) in enumerate(cond["foods"]):
            if cond["foods_alive"][i]:
                ax.scatter([fx], [fy], s=60, c="#2c7a2c", marker="o", zorder=4, edgecolors="white", lw=1)
            else:
                ax.scatter([fx], [fy], s=40, c="#888", marker="x", zorder=4)
        # live map (red) and trajectory (faint)
        if len(cond["live_map"]):
            ax.scatter(cond["live_map"][:, 0], cond["live_map"][:, 1], s=1.5, c="#c33", alpha=0.5)
        ax.plot(cond["traj"][:, 0], cond["traj"][:, 1], color="#444", lw=0.4, alpha=0.5)
        ax.set_title(name, fontsize=11)

        ax = axes[1, col]
        t = np.arange(len(cond["energy"])) * DT
        ax.plot(t, cond["energy"], color="#c33", lw=1.2)
        ax.axhline(0, color="#888", ls=":", lw=0.8)
        ax.axhline(E_CRIT_LOW, color="#e09000", ls=":", lw=0.8, label="BAP fails ≤ 5")
        for (te, _, _) in cond["eaten"]:
            ax.axvline(te, color="#2c7a2c", lw=0.7, alpha=0.7)
        if cond["death_t"] is not None:
            ax.axvline(cond["death_t"], color="#900", lw=1.0, label=f"death t={cond['death_t']:.0f}s")
        ax.set_xlim(0, T_END); ax.set_ylim(-2, E_MAX + 5)
        ax.set_xlabel("time (s)"); ax.set_ylabel("energy")
        ax.legend(fontsize=8, loc="upper right"); ax.grid(alpha=0.25)

    fig.suptitle("Basal coupling — the agent stays alive only because it moves, moves only\n"
                 "because it has energy, has energy only because food is found, finds food\n"
                 "only by moving.   (Living-snapshot map decay = "
                 f"{DECAY}/s)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = os.path.join(figdir, "p2_basal_coupling.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
