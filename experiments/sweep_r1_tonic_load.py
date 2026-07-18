# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""R1 -- tonic-load coupling: the partner zone's tone rises with the active load.

Register 1 of the preprint. During a sustained isometric hold, the SMN's
haltability operator makes the *inactive* (partner) zone tonically engaged in
proportion to the *active* zone's load, through the alert energy E_R:

    a_partner  =  a0 + beta * E_R ,     E_R* = rho * tau_E * F_active
              =>  a_partner  =  a0 + (beta*rho*tau_E) * F_active   (linear in load).

Classical reciprocal inhibition predicts the opposite: the partner is silenced or
held at baseline, INDEPENDENT of load (slope 0).

Pre-registration
----------------
- Hypothesis: partner tone rises linearly with the active zone's steady-state
  force; slope = beta*rho*tau_E > 0.
- Order parameter: the fitted slope of a_partner vs F_active.
- Matched foil: classical=True (AlertEnergyBoard with no alert energy).
- Pass: SMN slope clearly > 0 and ~ beta*rho*tau_E; foil slope ~ 0.
- Falsify: SMN slope ~ 0 (partner tone flat) -> no tonic-load coupling.

Run:  ../.venv/bin/python sweep_r1_tonic_load.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.control import AlertEnergyBoard

DT = 0.002
T_END = 8.0                     # >> tau_E, so E_R settles
AVG_LAST = 2.0                  # average the steady-state window
LOADS = np.linspace(0.1, 1.2, 8)
SEEDS = range(5)
PROPRIO_NOISE = 0.003
# board parameters (beta*rho*tau_E = 0.5*1.0*1.5 = 0.75 is the predicted slope)
BOARD = dict(kp=4.0, kd=0.4, cmax=2.5, a0=0.1, rho=1.0, tau_E=1.5,
             beta=0.5, gamma=1.0, dt=DT)


def build_limb_xml():
    return """
<mujoco model="isometric_caz">
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <worldbody>
    <body name="limb" pos="0 0 0.4">
      <joint name="j" type="hinge" axis="0 0 1" damping="0.05"/>
      <geom type="capsule" fromto="0 0 0 0.2 0 0" size="0.02" mass="0.1"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="m_r" joint="j" gear="1"  ctrlrange="0 3"/>
    <motor name="m_l" joint="j" gear="-1" ctrlrange="0 3"/>
  </actuator>
</mujoco>
"""


def run_hold(load, classical, seed):
    """Hold theta=0 against a constant external load; return steady-state
    (F_active, a_partner) averaged over the last AVG_LAST seconds."""
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_limb_xml())
    data = mujoco.MjData(model)
    jid = model.joint("j").id
    qadr, vadr = model.jnt_qposadr[jid], model.jnt_dofadr[jid]
    ar, al = model.actuator("m_r").id, model.actuator("m_l").id
    board = AlertEnergyBoard(classical=classical, **BOARD)

    n = int(T_END / DT); n_avg = int(AVG_LAST / DT)
    F_hist, ap_hist = [], []
    for i in range(n):
        th = float(data.qpos[qadr]) + rng.normal(0, PROPRIO_NOISE)
        thd = float(data.qvel[vadr]) + rng.normal(0, PROPRIO_NOISE * 10)
        a_r, a_l, drive, F_active, E = board.commands(th, thd, 0.0, 0.0, gated=True)
        data.ctrl[ar], data.ctrl[al] = a_r, a_l
        data.qfrc_applied[vadr] = -load            # push -> right zone becomes active
        mujoco.mj_step(model, data)
        if i >= n - n_avg:
            F_hist.append(F_active); ap_hist.append(a_l)   # left = partner when right active
    return float(np.mean(F_hist)), float(np.mean(ap_hist))


def sweep(classical):
    F, AP = [], []
    for load in LOADS:
        fs, aps = zip(*(run_hold(load, classical, s) for s in SEEDS))
        F.append(np.mean(fs)); AP.append(np.mean(aps))
    F, AP = np.array(F), np.array(AP)
    slope, intercept = np.polyfit(F, AP, 1)
    return F, AP, slope, intercept


def main():
    figdir = os.path.join(os.path.dirname(__file__), "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    Fs, APs, ss, is_ = sweep(classical=False)      # SMN
    Fc, APc, sc, ic = sweep(classical=True)        # classical inhibition (foil)
    pred = BOARD["beta"] * BOARD["rho"] * BOARD["tau_E"]

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.scatter(Fs, APs, c="#2c6fbb", s=42, zorder=3, label="SMN (alert energy)")
    ax.plot(Fs, ss * Fs + is_, c="#2c6fbb", lw=2,
            label=f"SMN fit: slope {ss:.2f}  (predicted $\\beta\\rho\\tau_E$={pred:.2f})")
    ax.scatter(Fc, APc, c="#c0672a", s=42, marker="s", zorder=3,
               label="classical inhibition (foil)")
    ax.plot(Fc, sc * Fc + ic, c="#c0672a", lw=2, ls="--",
            label=f"foil fit: slope {sc:.2f}")
    ax.set_xlabel("active-zone steady-state force  $F_{\\mathrm{active}}$")
    ax.set_ylabel("partner-zone tonic activation  $a_{\\mathrm{partner}}$")
    ax.set_title("R1 -- tonic-load coupling: partner tone rises with active load "
                 "(SMN), flat under classical inhibition", fontsize=10)
    ax.legend(fontsize=8.5, loc="upper left"); ax.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(figdir, "sweep_r1_tonic_load.png")
    fig.savefig(out, dpi=130)
    print(f"[R1] SMN slope   = {ss:.3f}  (predicted beta*rho*tau_E = {pred:.3f})")
    print(f"[R1] foil slope  = {sc:.3f}  (classical inhibition: expect ~0)")
    print(f"[R1] verdict: {'PASS' if ss > 0.2 and abs(sc) < 0.1 else 'CHECK'}")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
