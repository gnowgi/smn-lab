# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Resistance-signal probe — the foundation check for the manipulator unit.

Before building the bilateral two-limb unit (see design/manipulator-unit.md), we
must confirm the most basic thing the whole program rests on: that a SINGLE
pull-only antagonist joint, pressing on a target, yields a clean, monotone read
that *separates objecthood by resistance-to-modulation*.

One hinge limb (axis vertical, so gravity loads the structure but not the hinge
— isolating object resistance) is driven by a pull-only antagonist pair. We ramp
the press command from 0 and read the agent's dual interface:

  - command  : the intended modulation (actuator torque it applies),
  - angle    : the proprioceptive *result* (did the limb move?),
  - contact  : the tip touch force (the resistance met).

against four targets:

  free      — nothing there;
  movable   — a free box on the floor (resistance = inertia + field-dependent friction);
  compliant — a box on a spring (resistance rises with displacement);
  fixed     — a welded box (cannot be pushed through).

Pass criterion: the four conditions trace distinct, monotone, separable
trajectories in the (command -> result, contact) read — i.e. the force->result
mapping is legible by construction. If this is not clean, the unit will be muddy.

Run:  ../.venv/bin/python resistance_probe.py        (from design/)
Outputs: ../figures/resistance_probe.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

DT = 0.002
T_RAMP = 2.5            # seconds to ramp the press command 0 -> CMAX
T_HOLD = 0.8            # then hold, to expose a held halt vs continued motion
CMAX = 2.0             # pull-only actuator ctrl range (N·m at the joint)
ARM_LEN = 0.22
ARM_Z = 0.04           # limb height = box centre height (tip hits the box side)
BOX_HALF = (0.03, 0.03, 0.04)
BOX_POS = (0.20, 0.07, 0.04)   # just off the tip's swing path on the +y side
MOVABLE_MASS = 0.30
COMPLIANT_K = 120.0    # spring stiffness for the compliant target (N/m)

CONDITIONS = ("free", "movable", "compliant", "fixed")
COLORS = {"free": "#6a9ec5", "movable": "#2c7a2c",
          "compliant": "#c08a3e", "fixed": "#b03030"}


def target_xml(condition: str) -> str:
    x, y, z = BOX_POS
    hx, hy, hz = BOX_HALF
    g = (f'type="box" size="{hx} {hy} {hz}" rgba="0.6 0.6 0.6 1" '
         f'friction="1 0.01 0.001"')
    if condition == "free":
        return ""
    if condition == "fixed":                                   # welded to the world
        return f'<geom name="target" pos="{x} {y} {z}" {g}/>'
    if condition == "movable":                                 # free body, slides with friction
        return (f'<body name="target" pos="{x} {y} {z}">'
                f'<freejoint/><geom name="target" mass="{MOVABLE_MASS}" {g}/></body>')
    if condition == "compliant":                               # spring-backed along y
        return (f'<body name="target" pos="{x} {y} {z}">'
                f'<joint name="t" type="slide" axis="0 1 0" '
                f'stiffness="{COMPLIANT_K}" damping="2.0"/>'
                f'<geom name="target" mass="0.10" {g}/></body>')
    raise ValueError(condition)


def build_xml(condition: str) -> str:
    return f"""
<mujoco model="resistance_probe">
  <compiler angle="radian"/>
  <option timestep="{DT}" gravity="0 0 -9.81" integrator="implicitfast"/>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1" rgba="0.9 0.9 0.9 1" friction="1 0.01 0.001"/>
    <body name="limb" pos="0 0 {ARM_Z}">
      <joint name="press" type="hinge" axis="0 0 1" range="0 1.6" limited="true" damping="0.2"/>
      <geom name="arm" type="capsule" fromto="0 0 0 {ARM_LEN} 0 0" size="0.012" mass="0.20"/>
      <site name="tip" pos="{ARM_LEN} 0 0" size="0.02"/>
    </body>
    {target_xml(condition)}
  </worldbody>
  <actuator>
    <motor name="press"   joint="press" gear="1"  ctrlrange="0 {CMAX}"/>
    <motor name="retract" joint="press" gear="-1" ctrlrange="0 {CMAX}"/>
  </actuator>
  <sensor>
    <jointpos name="ang" joint="press"/>
    <jointvel name="vel" joint="press"/>
    <jointactuatorfrc name="cmd" joint="press"/>
    <touch name="tip_touch" site="tip"/>
  </sensor>
</mujoco>
"""


def run(condition: str):
    model = mujoco.MjModel.from_xml_string(build_xml(condition))
    data = mujoco.MjData(model)
    mp = model.actuator("press").id
    a_ang = model.sensor_adr[model.sensor("ang").id]
    a_cmd = model.sensor_adr[model.sensor("cmd").id]
    a_touch = model.sensor_adr[model.sensor("tip_touch").id]

    n = int((T_RAMP + T_HOLD) / DT)
    t = np.arange(n) * DT
    cmd = np.zeros(n); ang = np.zeros(n); touch = np.zeros(n)
    for k in range(n):
        press = CMAX * min(1.0, (k * DT) / T_RAMP)             # ramp then hold
        data.ctrl[mp] = press
        mujoco.mj_step(model, data)
        cmd[k] = abs(data.sensordata[a_cmd])
        ang[k] = abs(data.sensordata[a_ang])
        touch[k] = data.sensordata[a_touch]
    return dict(t=t, cmd=cmd, ang=ang, touch=touch)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    runs = {c: run(c) for c in CONDITIONS}

    LIMIT = 1.6
    print("\n=== resistance-signal probe ===")
    print(f"  {'condition':10s} {'final angle (rad)':>18s} {'peak contact (N)':>18s} "
          f"{'reached limit?':>15s} {'halted by object?':>18s}")
    for c in CONDITIONS:
        r = runs[c]
        reached = r["ang"][-1] > 0.9 * LIMIT                       # moved freely to the end
        halted = (not reached) and r["touch"].max() > 1.0          # stopped against resistance
        print(f"  {c:10s} {r['ang'][-1]:18.3f} {r['touch'].max():18.2f} "
              f"{str(reached):>15s} {str(halted):>18s}")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

    for c in CONDITIONS:
        r = runs[c]
        ax[0].plot(r["t"], r["ang"], color=COLORS[c], lw=2, label=c)
        ax[1].plot(r["t"], r["touch"], color=COLORS[c], lw=2, label=c)
        ax[2].plot(r["cmd"], r["ang"], color=COLORS[c], lw=2, label=c)
    ax[0].set_title("Result: achieved angle vs time"); ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("|joint angle| (rad)")
    ax[1].set_title("Resistance: tip contact force vs time"); ax[1].set_xlabel("time (s)"); ax[1].set_ylabel("contact force (N)")
    ax[2].set_title("The force→result map\n(achieved angle vs commanded torque)")
    ax[2].set_xlabel("commanded torque (N·m)"); ax[2].set_ylabel("|joint angle| (rad)")
    for a in ax:
        a.grid(alpha=0.25); a.legend(fontsize=9)
    fig.suptitle("Resistance-signal probe — one pull-only antagonist joint pressing four targets\n"
                 "(free / movable / compliant / fixed separate cleanly: objecthood as resistance-to-modulation)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = os.path.join(figdir, "resistance_probe.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
