# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""E2 — self / field / object factoring (the manipulator's force-reafference).

The three-way generalization of the self/world register (P0), now in the force
domain and in a real gravitational field. A single sagittal limb (hinge axis y,
so gravity loads it) lifts against the field. The agent carries a **force-
reafference forward model**: by self-motion it learns the effort its own pull
needs to move its limb *against gravity alone* — i.e. it learns to predict the
**field**. Thereafter:

  - the **field** is factored out as the predictable baseline effort;
  - an **object** shows up as effort/contact *beyond* that baseline (residual);
  - an **external** cause shows up as motion with *no efference* (the limb moves
    though the agent did not pull) — exafference.

So the same upward motion of the limb is attributed to **self+field**, **object**,
or **external** by construction (the forward model + the dual interface), not by a
trained classifier. This is the field-domain form of "the world model includes
separating self-caused from world-caused change", with the field as a third,
always-present term.

Run:  ../.venv/bin/python p5_self_field_object.py
Outputs: ../figures/p5_self_field_object.png
"""
from __future__ import annotations
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.control import ReafferencePredictor

DT = 0.002
T = 2.0                 # seconds per run
CMAX = 1.5
PIVOT_Z = 0.40         # above the arm length, so the limb never reaches the floor
ARM_LEN = 0.25
INIT_ANG = 1.40        # start hanging (tip down); the agent lifts from here
OBJ_POS = (0.22, 0.0, 0.28)     # a fixed block in the lift arc (tip passes here near θ≈0.5)
RES_THR = 0.30         # residual-effort threshold (object beyond field; self residual ≈ 0)
CON_THR = 0.5          # contact threshold
EFF_THR = 0.12         # efference threshold (is the agent pulling?)
VEL_THR = 0.15         # motion threshold


def build_xml(with_object: bool) -> str:
    obj = (f'<geom name="obj" type="box" pos="{OBJ_POS[0]} {OBJ_POS[1]} {OBJ_POS[2]}" '
           f'size="0.03 0.03 0.03" rgba="0.6 0.6 0.62 1"/>') if with_object else ""
    return f"""
<mujoco model="self_field_object">
  <compiler angle="radian"/>
  <option timestep="{DT}" gravity="0 0 -9.81" integrator="implicitfast"/>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1" rgba="0.9 0.9 0.9 1"/>
    <body name="limb" pos="0 0 {PIVOT_Z}">
      <joint name="j" type="hinge" axis="0 1 0" range="-0.5 1.6" limited="true" damping="0.3"/>
      <geom name="arm" type="capsule" fromto="0 0 0 {ARM_LEN} 0 0" size="0.012" mass="0.30"
            rgba="0.2 0.4 0.9 1"/>
      <site name="tip" pos="{ARM_LEN} 0 0" size="0.02"/>
    </body>
    {obj}
  </worldbody>
  <actuator>
    <motor name="lift"  joint="j" gear="-1" ctrlrange="0 {CMAX}"/>
    <motor name="press" joint="j" gear="1"  ctrlrange="0 {CMAX}"/>
  </actuator>
  <sensor>
    <jointpos name="ang" joint="j"/>
    <jointvel name="vel" joint="j"/>
    <jointactuatorfrc name="cmd" joint="j"/>
    <touch name="touch" site="tip"/>
  </sensor>
</mujoco>
"""


def _handles(model):
    return dict(
        lift=model.actuator("lift").id,
        dof=model.jnt_dofadr[model.joint("j").id],
        qadr=model.jnt_qposadr[model.joint("j").id],
        a_ang=model.sensor_adr[model.sensor("ang").id],
        a_vel=model.sensor_adr[model.sensor("vel").id],
        a_cmd=model.sensor_adr[model.sensor("cmd").id],
        a_touch=model.sensor_adr[model.sensor("touch").id],
    )


def calibrate_field():
    """Learn the effort the agent's own pull needs to lift the limb against
    gravity alone (no object) — the field model, as a ReafferencePredictor keyed
    on |angle|."""
    model = mujoco.MjModel.from_xml_string(build_xml(with_object=False))
    data = mujoco.MjData(model)
    h = _handles(model)
    data.qpos[h["qadr"]] = INIT_ANG; mujoco.mj_forward(model, data)
    fm = ReafferencePredictor(n_bins=48, theta_range=(-0.6, 1.6))
    n = int(T / DT)
    for k in range(n):                                   # self-motion at the SAME profile as the test
        data.ctrl[h["lift"]] = CMAX * min(1.0, k * DT / (T * 0.7))
        mujoco.mj_step(model, data)
        ang = float(data.sensordata[h["a_ang"]])        # signed
        eff = abs(float(data.sensordata[h["a_cmd"]]))
        fm.update(ang, eff)
    return fm


def run(condition: str, fm):
    model = mujoco.MjModel.from_xml_string(build_xml(with_object=(condition == "object")))
    data = mujoco.MjData(model)
    h = _handles(model)
    data.qpos[h["qadr"]] = INIT_ANG; mujoco.mj_forward(model, data)
    n = int(T / DT)
    t = np.arange(n) * DT
    ang = np.zeros(n); eff = np.zeros(n); con = np.zeros(n); res = np.zeros(n)
    efr = np.zeros(n); vel = np.zeros(n); label = []
    for k in range(n):
        frac = min(1.0, k * DT / (T * 0.7))
        if condition == "external":                      # world lifts the limb; agent passive
            data.ctrl[h["lift"]] = 0.0
            data.qfrc_applied[h["dof"]] = -CMAX * frac    # -torque about y = lift (tip up)
        else:                                            # self+field, or self into an object
            data.ctrl[h["lift"]] = CMAX * frac
        mujoco.mj_step(model, data)
        a = float(data.sensordata[h["a_ang"]])           # signed lift angle
        e = abs(float(data.sensordata[h["a_cmd"]]))
        c = float(data.sensordata[h["a_touch"]])
        v = abs(float(data.sensordata[h["a_vel"]]))
        efference = CMAX * frac if condition != "external" else 0.0
        residual = e - fm.predict(a)                     # effort beyond the field baseline
        ang[k], eff[k], con[k], res[k], efr[k], vel[k] = a, e, c, residual, efference, v
    res_s = np.convolve(res, np.ones(15) / 15, mode="same")   # reject transient spikes
    label = [factor(efr[k], res_s[k], con[k], vel[k], ang[k]) for k in range(n)]
    return dict(t=t, ang=ang, eff=eff, con=con, res=res, efr=efr, vel=vel, label=label)


def factor(efference, residual, contact, vel, angle):
    """The self/field/object board. Field is already factored out (residual is
    effort *beyond* the predicted field baseline)."""
    lifted = angle < INIT_ANG - 0.25                     # held away from gravity's rest
    if efference < EFF_THR and (vel > VEL_THR or lifted):
        return "external"                                # motion/holding with no pull = world-caused
    if contact > CON_THR or residual > RES_THR:
        return "object"                                  # resistance beyond the field
    return "self+field"                                  # moving/holding against the known field


CLASSES = ("self+field", "object", "external")
CONDITIONS = ("self+field", "object", "external")
CCOL = {"self+field": "#2c6a9c", "object": "#c08a3e", "external": "#b03030"}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    fm = calibrate_field()
    cond_key = {"self+field": "self", "object": "object", "external": "external"}
    runs = {c: run(cond_key[c], fm) for c in CONDITIONS}

    print("\n=== E2 — self / field / object factoring ===")
    print(f"  {'condition':12s} {'mean residual':>13s} {'peak contact':>13s} "
          f"{'attribution (fraction)':>40s}")
    for c in CONDITIONS:
        r = runs[c]
        # attribution over the active phase (skip the first 0.2 s)
        s = int(0.2 / DT)
        labs = r["label"][s:]
        frac = {cl: labs.count(cl) / max(len(labs), 1) for cl in CLASSES}
        fr = "  ".join(f"{cl}={frac[cl]:.2f}" for cl in CLASSES)
        print(f"  {c:12s} {r['res'][s:].mean():13.3f} {r['con'].max():13.2f}   {fr}")

    # --- figure ---
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(15, 4.6))

    # A: effort vs lift-angle, with the calibrated field baseline
    aa = np.linspace(0.02, 1.2, 60)
    axA.plot(aa, [fm.predict(a) for a in aa], "k--", lw=1.5, label="field model (baseline)")
    for c in CONDITIONS:
        r = runs[c]
        axA.plot(r["ang"], r["eff"], color=CCOL[c], lw=2, label=c)
    axA.set_xlabel("lift angle |θ| (rad)"); axA.set_ylabel("effort (actuator torque, N·m)")
    axA.set_title("(A) Effort vs angle\nfield = predictable baseline; object rises above it", fontsize=10)
    axA.legend(fontsize=8); axA.grid(alpha=0.25)

    # B: residual (effort beyond the field) over time
    for c in CONDITIONS:
        axB.plot(runs[c]["t"], runs[c]["res"], color=CCOL[c], lw=2, label=c)
    axB.axhline(RES_THR, color="#888", ls=":", lw=1)
    axB.set_xlabel("time (s)"); axB.set_ylabel("residual effort (N·m)")
    axB.set_title("(B) Residual = effort − field prediction\n≈0 for self+field, >0 for object", fontsize=10)
    axB.legend(fontsize=8); axB.grid(alpha=0.25)

    # C: attribution per condition (stacked fractions)
    s = int(0.2 / DT)
    bottom = np.zeros(len(CONDITIONS))
    for cl in CLASSES:
        vals = [runs[c]["label"][s:].count(cl) / max(len(runs[c]["label"][s:]), 1) for c in CONDITIONS]
        axC.bar(range(len(CONDITIONS)), vals, bottom=bottom, label=cl, color=CCOL[cl])
        bottom += np.array(vals)
    axC.set_xticks(range(len(CONDITIONS))); axC.set_xticklabels(CONDITIONS, fontsize=9)
    axC.set_ylabel("attribution (fraction of time)")
    axC.set_title("(C) The board's attribution\n(same motion → self+field / object / external)", fontsize=10)
    axC.legend(fontsize=8)

    fig.suptitle("E2 — self / field / object: the field factored out by force-reafference, "
                 "object and external surfaced by construction", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(figdir, "p5_self_field_object.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
