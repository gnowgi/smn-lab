# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Proprioceptive entrainment -- closing the body -> rhythm loop.

A scientific-accuracy review pointed out that in the base bench the messaging
beam is *causally sealed off* from the body: `MessagingBeam.command()` advanced
`self.phase` from omega + neighbour coupling alone, so if the crawler hits a wall
or lags under load, the oscillator never knows -- a controller commanding a body,
not a body-and-controller in mutual entrainment. Real undulators close that loop:
lamprey edge cells and C. elegans stretch-receptor coupling feed the mechanics
back into the rhythm. That gap sits exactly where the SMN thesis ("the body is the
computer") is strongest.

The opt-in entrainment term (`MessagingBeam(entrain>0)`) pulls each oscillator
toward the phase its own segment is *actually* bent to:
    psi = arctan2(theta, theta_dot/omega)      # realized gait phase
    dphi += entrain * (r/(r+eps)) * sin(psi - phase),  r = |bend|
so the pull is identically zero under perfect tracking (no error -> no pull) and
fades as the body stops (a still body carries no phase, like a silent stretch
receptor).

  ** Correction (this file supersedes the first version). ** A review caught two
  bugs in the first term: (1) the arctan2 arguments were swapped, so the pull was
  cos(2*phase) -- a spurious 2*omega drive that did NOT vanish under perfect
  tracking; (2) the pull was ungated, so during a gated halt the beam was arrested
  only because arctan2(0,0)=0 pulled the phase to a fixed 0 -- an edge case, not
  the mechanism. Both are fixed here (argument order + magnitude gate). The old
  "arrest during a gated halt" figure was carried by bug (2) and is withdrawn;
  the corrected term's real effect is shown below.

Panels (figures/entrainment.png):
  (A) Mechanism check. The pull under perfect tracking, vs gait phase: the old
      (swapped) term is a full-amplitude cos(2*phase); the corrected term is
      identically zero. A well-formed stretch term must not pull when the body is
      doing exactly what it was told.
  (B) The body enters the rhythm. Free-run realized undulation frequency vs the
      entrainment gain: with the loop closed the oscillator locks to the actually-
      lagging PD-driven body, so the realized rhythm falls below the commanded
      0.9 Hz and, as coupling rises, is dragged all the way to arrest. The rhythm
      is no longer the intrinsic omega -- the body shapes it.
  (C) An honest negative (unchanged by the fix). Realized frequency vs medium drag
      stays flat: the anisotropic drag resists body translation, not joint
      articulation, so there is no articulation load for the medium to modulate.
      The C. elegans water<->agar frequency law needs a joint-loading model (drag
      torque on the bend, or a load-limited actuator), not just the feedback path.

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
FREQ_RUN = 30.0
GAINS = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0]   # entrainment gains, panel B
GAIN_TRACE = 2.0                 # the "closed loop" exemplar in the text/print
DRAGS = [3.0, 7.0, 14.0, 25.0]   # medium-resistance sweep, panel C
GAIN_C = 2.0                     # gain used for the drag sweep
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


def realized_freq(entrain, c_trans=DRAG_TRANS):
    """Dominant frequency of the actual head-joint angle in a free crawl."""
    model, data, ids = _build()
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=AMP, freq=FREQ,
                         turn_gain=0.0, entrain=entrain)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in ids["jq"]]
    mujoco.mj_forward(model, data)
    n = int(FREQ_RUN / DT)
    th0 = []
    for i in range(n):
        th = np.array([float(data.qpos[q]) for q in ids["jq"]])
        thd = np.array([float(data.qvel[v]) for v in ids["jv"]])
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


def perfect_tracking_pull(phi):
    """The entrainment pull under perfect tracking (th = amp*sin(phi),
    thd/w = amp*cos(phi)), for the swapped (old) and corrected argument order."""
    th = AMP * np.sin(phi)
    thd_w = AMP * np.cos(phi)
    old = np.sin(np.arctan2(thd_w, th) - phi)      # as first coded: == cos(2 phi)
    r = np.hypot(th, thd_w)
    new = (r / (r + 1e-3)) * np.sin(np.arctan2(th, thd_w) - phi)   # corrected: == 0
    return old, new


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)

    phi = np.linspace(0, 2 * np.pi, 200)
    old_pull, new_pull = perfect_tracking_pull(phi)

    freqs = [realized_freq(g) for g in GAINS]        # panel B
    f_drag = [realized_freq(GAIN_C, c) for c in DRAGS]   # panel C

    print("\n=== Proprioceptive entrainment (corrected term) ===")
    print(f"  perfect-tracking pull: max|old|={np.max(np.abs(old_pull)):.3f} "
          f"(spurious 2w drive)   max|corrected|={np.max(np.abs(new_pull)):.2e} (~0)")
    print(f"  free-run realized freq vs gain (commanded {FREQ} Hz):")
    for g, f in zip(GAINS, freqs):
        print(f"     eps={g:4.1f}  ->  {f:.3f} Hz")
    print(f"  freq vs drag (eps={GAIN_C}): {[round(v,3) for v in f_drag]}  (flat)")
    dragged = freqs[0] - min(freqs)
    verdict = ("LOOP CLOSED (correctly): the body shapes the rhythm -- closing the "
               f"loop drags the realized frequency from {freqs[0]:.2f} Hz down to "
               f"{min(freqs):.2f} Hz (arrest) as coupling rises, because the "
               "oscillator locks to the actually-lagging body."
               if dragged > 0.3 else "WEAK -- check the term.")
    print("  verdict:", verdict)

    # ---- figure ----
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(15, 4.6))

    axA.axhline(0, color="#999", lw=0.8)
    axA.plot(phi, old_pull, color="#b00000", lw=1.8,
             label=r"first (buggy) term $=\cos 2\varphi$")
    axA.plot(phi, new_pull, color="#1538a0", lw=2.2,
             label="corrected term $\\equiv 0$")
    axA.set_xlabel(r"gait phase $\varphi$ (rad)")
    axA.set_ylabel("entrainment pull under perfect tracking")
    axA.set_title("A — mechanism check: no error should mean no pull", fontsize=10)
    axA.legend(loc="lower right", fontsize=7)

    axB.axhline(FREQ, ls=":", color="#333", lw=1.0, label="commanded freq (0.9 Hz)")
    axB.plot(GAINS, freqs, "-o", color="#1538a0")
    axB.set_xlabel("entrainment gain  $\\varepsilon$")
    axB.set_ylabel("free-run realized freq (Hz)")
    axB.set_ylim(0, FREQ * 1.15)
    axB.set_title("B — the body enters the rhythm: coupling drags freq to arrest",
                  fontsize=10)
    axB.legend(loc="upper right", fontsize=7)

    axC.plot(DRAGS, f_drag, "-s", color="#1538a0",
             label=f"closed loop (ε={GAIN_C:.0f})")
    axC.axhline(FREQ, ls=":", color="#333", lw=1.0, label="commanded freq")
    axC.set_ylim(0, FREQ * 1.15)
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
