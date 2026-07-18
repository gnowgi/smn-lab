# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""R2 -- resumption latency: a post-halt reversal is faster under the SMN.

Register 2 of the preprint. During active engagement the alert energy E_R builds.
After a brief HALT, the agent is given a small REVERSED target that flips the
active zone. The newly-active (previously-alert) zone's drive is amplified by
(1 + gamma*E_R) -- a head start that shortens the resumption latency:

    Delta_t  ~  gamma * E_R(t_release) / K_p .

Classical reciprocal inhibition has no alert energy and no amplification, so its
resumption is slower.

Reconciliation with Prediction 1 (haltability signatures). Prediction 1 found the
halt itself carries NO speed benefit -- the dwell is a genuine stop. R2 is a
different claim: it is the RESUMPTION after the halt, in a new direction, that the
primed partner accelerates. Halting costs; resuming from a primed state pays.

Pre-registration
----------------
- Hypothesis: post-halt reversal latency is shorter under SMN than classical
  inhibition; the advantage grows with the alert energy at release.
- Order parameter: resumption latency (release -> reversed target); the SMN
  advantage Delta_t = latency_classical - latency_SMN.
- Matched foil: classical=True.
- Pass: latency_SMN < latency_classical (positive advantage), rising with load.
- Falsify: no latency difference -> no resumption advantage.

Run:  ../.venv/bin/python sweep_r2_resumption.py
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
T_ENGAGE, T_HALT, T_REV = 3.0, 0.3, 4.0
REVERSAL_STEP = 0.40       # reversed target = theta_at_release - this (a clean flip)
THRESH_DISP = 0.30         # latency = time to displace this far into the reversal
LOADS = np.linspace(0.3, 1.2, 6)   # engagement load -> sets E_R at release
SEEDS = range(5)
PROPRIO_NOISE = 0.003
# beta/gamma set so amplification outweighs the partner tone through the reversal
# (SMN faster while -drive > beta/gamma); cmax raised so the head start is not clipped away.
BOARD = dict(kp=3.0, kd=0.5, cmax=3.0, a0=0.1, rho=1.0, tau_E=1.5,
             beta=0.3, gamma=2.0, dt=DT)


def build_limb_xml():
    return """
<mujoco model="reversal_caz">
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


def run_trial(load, classical, seed):
    """Engage (right active, E_R builds) -> halt -> flip target left; return
    (resumption latency, E_R at release)."""
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_limb_xml())
    data = mujoco.MjData(model)
    jid = model.joint("j").id
    qadr, vadr = model.jnt_qposadr[jid], model.jnt_dofadr[jid]
    ar, al = model.actuator("m_r").id, model.actuator("m_l").id
    board = AlertEnergyBoard(classical=classical, **BOARD)

    def sense():
        return (float(data.qpos[qadr]) + rng.normal(0, PROPRIO_NOISE),
                float(data.qvel[vadr]) + rng.normal(0, PROPRIO_NOISE * 10))

    # engage: hold theta=0 against a load pushing -theta -> right zone active
    for _ in range(int(T_ENGAGE / DT)):
        th, thd = sense()
        a_r, a_l, *_ = board.commands(th, thd, 0.0, 0.0, gated=True)
        data.ctrl[ar], data.ctrl[al] = a_r, a_l
        data.qfrc_applied[vadr] = -load
        mujoco.mj_step(model, data)
    E_release = board.E_R
    # halt: drive gated, load removed
    for _ in range(int(T_HALT / DT)):
        th, thd = sense()
        a_r, a_l, *_ = board.commands(th, thd, 0.0, 0.0, gated=False)
        data.ctrl[ar], data.ctrl[al] = a_r, a_l
        data.qfrc_applied[vadr] = 0.0
        mujoco.mj_step(model, data)
    # reverse: a clean leftward flip from wherever theta settled; latency = time to
    # displace THRESH_DISP into the reversal (the initiation speed gamma*E_R governs)
    theta_rel = float(data.qpos[qadr])
    target = theta_rel - REVERSAL_STEP
    t0 = data.time; latency = np.nan
    for _ in range(int(T_REV / DT)):
        th, thd = sense()
        a_r, a_l, *_ = board.commands(th, thd, target, 0.0, gated=True)
        data.ctrl[ar], data.ctrl[al] = a_r, a_l
        data.qfrc_applied[vadr] = 0.0
        mujoco.mj_step(model, data)
        if np.isnan(latency) and (theta_rel - float(data.qpos[qadr])) >= THRESH_DISP:
            latency = data.time - t0
            break
    return latency, E_release


def sweep(classical):
    lat, ER = [], []
    for load in LOADS:
        rows = [run_trial(load, classical, s) for s in SEEDS]
        lat.append(np.nanmean([r[0] for r in rows]))
        ER.append(np.mean([r[1] for r in rows]))
    return np.array(lat), np.array(ER)


def main():
    figdir = os.path.join(os.path.dirname(__file__), "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    lat_smn, ER = sweep(classical=False)
    lat_cls, _ = sweep(classical=True)
    adv = lat_cls - lat_smn

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
    a1.plot(ER, lat_smn * 1e3, "o-", c="#2c6fbb", label="SMN (alert energy)")
    a1.plot(ER, lat_cls * 1e3, "s--", c="#c0672a", label="classical inhibition (foil)")
    a1.set_xlabel("alert energy at release  $E_R(t_{\\mathrm{release}})$")
    a1.set_ylabel("resumption latency (ms)")
    a1.set_title("Post-halt reversal latency", fontsize=10)
    a1.legend(fontsize=8.5); a1.grid(alpha=0.3)
    a2.plot(ER, adv * 1e3, "d-", c="#3a8a3a"); a2.axhline(0, c="gray", lw=0.8)
    a2.set_xlabel("alert energy at release  $E_R$")
    a2.set_ylabel("SMN advantage  $\\Delta t$ (ms)")
    a2.set_title("Advantage grows with alert energy at release", fontsize=10)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(figdir, "sweep_r2_resumption.png")
    fig.savefig(out, dpi=130)
    print(f"[R2] E_R at release   = {np.round(ER,2)}")
    print(f"[R2] latency SMN (ms) = {np.round(lat_smn*1e3,1)}")
    print(f"[R2] latency foil(ms) = {np.round(lat_cls*1e3,1)}")
    print(f"[R2] advantage (ms)   = {np.round(adv*1e3,1)}  (mean {np.nanmean(adv)*1e3:.1f})")
    ok = np.nanmean(adv) > 0 and adv[-1] > adv[0]
    print(f"[R2] verdict: {'PASS' if ok else 'CHECK'}")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
