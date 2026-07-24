# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Proprioceptive entrainment -- closing the body -> rhythm loop.

A scientific-accuracy review pointed out that in the base bench the messaging
beam is *causally sealed off* from the body: `MessagingBeam.command()` advances
`self.phase` from omega + neighbour coupling alone, so if the crawler hits a wall
or the wave is gated off, the oscillator never knows -- it is a controller
commanding a body, not a body-and-controller in mutual entrainment. Real
undulators close that loop: lamprey edge cells and *C. elegans* stretch-receptor
coupling feed the mechanics back into the rhythm, to the point that the
"oscillator" is largely mechanosensory. That gap sits at exactly the layer where
the SMN thesis ("the body is the computer") is strongest, so closing it matters.

This experiment turns on the opt-in proprioceptive-entrainment term
(`MessagingBeam(entrain>0)`, fed the actually-sensed joint state) and asks a
falsifiable question: **can the body now perturb the rhythm?**

Panels (figures/entrainment.png):
  (A) The arrest. The HAP gates the wave off for 2 s (as in C1). Open loop
      (entrain=0): the phase winds straight through the halt -- ~1.8 cycles the
      body never executed. Closed loop (entrain>0): the oscillator is pulled
      toward the body's actual (arrested) state and largely stops winding.
  (B) Order parameter: cycles the beam winds during the 2 s halt vs the
      entrainment gain. Open loop = omega*T (the full free winding); rising gain
      progressively arrests the wave to the body.
  (C) An honest negative. Steady-state undulation frequency vs medium drag, open
      vs closed loop -- it stays pinned near the commanded value in BOTH. In this
      bench the drag resists body translation, not joint articulation, and the PD
      servo imposes the bend timing, so closing the loop does NOT reproduce the
      C. elegans water<->agar frequency law here. That needs a joint-loading
      model (a declared next step), not just the feedback path.

Run:  ../.venv/bin/python entrainment.py        (from this directory)
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag
from smn_lab.control import OpponentBoard, MessagingBeam

# ---- parameters -----------------------------------------------------------
DT = 0.002
N_SEG = 3
FREQ = 0.9                       # commanded beam frequency (the circuit constant)
AMP = 0.8
DRAG_LONG = 0.5
DRAG_TRANS = 7.0
HALT = (12.0, 14.0)              # 2 s gated halt (HAP suppresses the BAP wave)
T_HALT_RUN = 22.0
GAINS = [0.0, 1.0, 2.0, 3.0, 4.0, 6.0]     # entrainment gains for panels A/B
GAIN_ON = 6.0                    # the "closed loop" gain shown in panel A
DRAGS = [3.0, 7.0, 14.0, 25.0]  # medium-resistance sweep for panel C
FREQ_RUN = 30.0
W = 2 * np.pi * FREQ


def _build():
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N_SEG))
    data = mujoco.MjData(model)
    ids = dict(
        seg=[model.body(f"seg{k}").id for k in range(N_SEG)],
        jq=[model.jnt_qposadr[model.joint(f"j{k}").id] for k in range(1, N_SEG)],
        jv=[model.jnt_dofadr[model.joint(f"j{k}").id] for k in range(1, N_SEG)],
        ap=[model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)],
        an=[model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)],
    )
    return model, data, ids


def _sensed(data, ids):
    th = np.array([float(data.qpos[q]) for q in ids["jq"]])
    thd = np.array([float(data.qvel[v]) for v in ids["jv"]])
    return th, thd


def run_halt(entrain):
    """Crawl with a 2 s gated halt; log the head-joint oscillator phase."""
    model, data, ids = _build()
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=AMP, freq=FREQ,
                         turn_gain=0.0, entrain=entrain)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in ids["jq"]]
    mujoco.mj_forward(model, data)
    n = int(T_HALT_RUN / DT)
    t_log, ph_log = [], []
    ph_start = ph_end = None
    for i in range(n):
        t = i * DT
        th, thd = _sensed(data, ids)
        gate = 0.0 if (HALT[0] <= t < HALT[1]) else 1.0
        theta_cmd = beam.command(DT, bias=0.0, theta=th, theta_dot=thd) * gate
        for k in range(len(ids["jq"])):
            a_r, a_l, _ = boards[k].commands(th[k], thd[k], theta_cmd[k], 0.0)
            data.ctrl[ids["ap"][k]] = a_r
            data.ctrl[ids["an"][k]] = a_l
        apply_anisotropic_drag(model, data, ids["seg"], c_long=DRAG_LONG,
                               c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if abs(t - HALT[0]) < DT / 2:
            ph_start = float(beam.phase[0])
        if abs(t - HALT[1]) < DT / 2:
            ph_end = float(beam.phase[0])
        if i % 4 == 0:
            t_log.append(t); ph_log.append(float(beam.phase[0]))
    wound = ph_end - ph_start                      # rad wound during the halt
    return np.array(t_log), np.array(ph_log), wound


def realized_freq(entrain, c_trans):
    """Dominant frequency of the actual head-joint angle in a free crawl."""
    model, data, ids = _build()
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=AMP, freq=FREQ,
                         turn_gain=0.0, entrain=entrain)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in ids["jq"]]
    mujoco.mj_forward(model, data)
    n = int(FREQ_RUN / DT)
    th0 = []
    for i in range(n):
        th, thd = _sensed(data, ids)
        theta_cmd = beam.command(DT, bias=0.0, theta=th, theta_dot=thd)
        for k in range(len(ids["jq"])):
            a_r, a_l, _ = boards[k].commands(th[k], thd[k], theta_cmd[k], 0.0)
            data.ctrl[ids["ap"][k]] = a_r
            data.ctrl[ids["an"][k]] = a_l
        apply_anisotropic_drag(model, data, ids["seg"], c_long=DRAG_LONG,
                               c_trans=c_trans)
        mujoco.mj_step(model, data)
        if i % 4 == 0:
            th0.append(float(data.qpos[ids["jq"][0]]))
    x = np.asarray(th0)[len(th0) // 4:]            # drop the transient
    x = x - x.mean()
    if np.allclose(x, 0):
        return 0.0
    f = np.fft.rfftfreq(len(x), d=DT * 4)
    p = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    p[0] = 0.0
    return float(f[np.argmax(p)])


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)

    # panels A/B -- the arrest
    t_off, ph_off, w_off = run_halt(0.0)
    t_on, ph_on, w_on = run_halt(GAIN_ON)
    wound = [run_halt(g)[2] for g in GAINS]
    cyc = np.array(wound) / (2 * np.pi)

    # panel C -- the honest frequency negative
    f_off = [realized_freq(0.0, c) for c in DRAGS]
    f_on = [realized_freq(GAIN_ON, c) for c in DRAGS]

    print("\n=== Proprioceptive entrainment ===")
    print(f"  free winding target omega*T = {W * (HALT[1]-HALT[0]):.2f} rad "
          f"= {FREQ*(HALT[1]-HALT[0]):.2f} cycles")
    print(f"  cycles wound during {HALT[1]-HALT[0]:.0f}s halt: "
          f"open loop {cyc[0]:.2f}  ->  closed loop (g={GAIN_ON}) {cyc[-1]:.2f}")
    print(f"  realized freq vs drag  open: {[round(v,3) for v in f_off]}")
    print(f"  realized freq vs drag  closed: {[round(v,3) for v in f_on]}")
    arrested = cyc[0] - cyc[-1]
    verdict = ("LOOP CLOSED: the body arrests the rhythm -- entrainment removes "
               f"{arrested:.2f} of the {cyc[0]:.2f} cycles the open-loop beam winds "
               "through a halt it cannot execute."
               if arrested > 0.5 else
               "WEAK -- raise the entrainment gain.")
    print("  verdict:", verdict)

    # ---- figure ----
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(15, 4.6))

    axA.axvspan(*HALT, color="#bbb", alpha=0.45, label="wave gated off (halt)")
    axA.plot(t_off, ph_off / (2*np.pi), color="#b00000", lw=1.8,
             label="open loop (entrain=0)")
    axA.plot(t_on, ph_on / (2*np.pi), color="#1538a0", lw=1.8,
             label=f"closed loop (entrain={GAIN_ON:.0f})")
    axA.set_xlabel("time (s)"); axA.set_ylabel("beam phase (cycles)")
    axA.set_title("A — the arrest: does the halt reach the rhythm?", fontsize=10)
    axA.legend(loc="upper left", fontsize=7)

    axB.plot(GAINS, cyc, "-o", color="#1538a0")
    axB.axhline(FREQ * (HALT[1]-HALT[0]), ls="--", color="#b00000", lw=1.2,
                label=r"open-loop free winding ($\omega T$)")
    axB.set_xlabel("entrainment gain  $\\varepsilon$")
    axB.set_ylabel("cycles wound during the 2 s halt")
    axB.set_title("B — the body progressively arrests the wave", fontsize=10)
    axB.legend(loc="upper right", fontsize=7)

    axC.plot(DRAGS, f_off, "-o", color="#b00000", label="open loop")
    axC.plot(DRAGS, f_on, "-s", color="#1538a0", label=f"closed loop (ε={GAIN_ON:.0f})")
    axC.axhline(FREQ, ls=":", color="#333", lw=1.0, label="commanded freq")
    axC.set_ylim(0, FREQ * 1.4)
    axC.set_xlabel("transverse drag (medium resistance)")
    axC.set_ylabel("realized undulation freq (Hz)")
    axC.set_title("C — honest negative: freq does NOT adapt to the medium",
                  fontsize=10)
    axC.legend(loc="lower left", fontsize=7)

    fig.tight_layout()
    out = os.path.join(figdir, "entrainment.png")
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
