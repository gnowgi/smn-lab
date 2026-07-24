# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Proprioceptive entrainment -- the mechanism, and an open problem.

A scientific-accuracy review pointed out that in the base bench the messaging beam
is causally sealed off from the body: `MessagingBeam.command()` advanced phase from
omega + neighbour coupling alone, so a wall or a load never reached the rhythm -- a
controller commanding a body, not a body-and-controller in mutual entrainment. Real
undulators close that loop (lamprey edge cells; C. elegans stretch-receptor coupling,
Wen et al. 2012, Neuron 76:750), which is exactly where the SMN thesis "the body is
the computer" is strongest.

Closing the loop honestly took THREE review rounds; this page reports the endpoint,
including two withdrawn claims.

  Round 1 -- added an opt-in entrainment term. **Bugs (round 2):** the arctan2
    arguments were swapped (the pull was cos(2*phase), a spurious 2w drive that did
    not vanish under perfect tracking) and the pull was ungated (a still body was
    yanked via arctan2(0,0)=0). The "arrest during a gated halt" figure was that
    edge case -- WITHDRAWN.
  Round 2 fix -- corrected argument order + magnitude gate. **But (round 3):** the
    term entrained each oscillator to its OWN joint, i.e. to a servo-delayed copy of
    its own output, so sin(psi-phase) = sin(-delta) was a constant brake. The
    "coupling drags freq to arrest" curve was pure frequency DETUNING, not the body
    shaping the rhythm -- WITHDRAWN.
  Round 3 fix (this file) -- the biologically faithful **inter-segmental** topology:
    each oscillator is entrained to its ANTERIOR neighbour's realized phase (the head
    is the free pacemaker). `entrain_mode="inter"` (default) vs the `"self"` ablation.

Panels (figures/entrainment.png):
  (A) Mechanism check / regression invariant. Under perfect tracking the corrected
      pull is identically zero; the first (swapped-argument) term was a full-amplitude
      cos(2*phase). This invariant is now enforced in tests/test_entrainment.py (CI).
  (B) Why topology matters. Free-run frequency vs gain, on a 5-segment body: the
      "self" ablation is a runaway self-brake (dragged toward arrest = detuning);
      the correct inter-segmental form is far more stable (the free pacemaker keeps
      the rhythm alive). Neither is a demonstration that the *body* shapes the rhythm.
  (C) The open problem (honest negative). Free-run frequency vs medium drag is FLAT
      under BOTH topologies. Closing the loop does not, by itself, make the rhythm
      track the medium: the anisotropic drag loads body translation, not joint
      articulation, so the entrainment sees a spatially-uniform servo lag with no
      medium gradient. A positive result -- medium-dependent frequency, the C. elegans
      water<->agar law -- needs a **joint-loading model** (drag torque on the bend, or
      a load-limited actuator). That is the declared next step; until it lands, the
      loop is closed with the correct mechanism but its payoff is not yet demonstrable.

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
N_SEG = 5                        # longer body: inter-segmental coupling is substantive
FREQ = 0.9
AMP = 0.8
DRAG_LONG = 0.5
DRAG_TRANS = 7.0
FREQ_RUN = 30.0
GAINS = [0.0, 1.0, 2.0, 4.0, 6.0]
DRAGS = [3.0, 5.0, 7.0, 10.0, 14.0, 20.0]
GAIN_C = 2.0
W = 2 * np.pi * FREQ


def _build(n_seg):
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=n_seg))
    data = mujoco.MjData(model)
    ids = dict(
        seg=[model.body(f"seg{k}").id for k in range(n_seg)],
        jq=[model.jnt_qposadr[model.joint(f"j{k}").id] for k in range(1, n_seg)],
        jv=[model.jnt_dofadr[model.joint(f"j{k}").id] for k in range(1, n_seg)],
        ap=[model.actuator(f"m_j{k}_p").id for k in range(1, n_seg)],
        an=[model.actuator(f"m_j{k}_n").id for k in range(1, n_seg)],
    )
    return model, data, ids


def realized_freq(entrain, mode="inter", c_trans=DRAG_TRANS):
    model, data, ids = _build(N_SEG)
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=AMP, freq=FREQ, turn_gain=0.0,
                         entrain=entrain, entrain_mode=mode)
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
    x = np.asarray(th0)[len(th0) // 4:]
    x = x - x.mean()
    if np.allclose(x, 0):
        return 0.0
    f = np.fft.rfftfreq(len(x), d=DT * 4)
    p = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    p[0] = 0.0
    return float(f[np.argmax(p)])


def perfect_tracking_pull(phi):
    th = AMP * np.sin(phi)
    thd_w = AMP * np.cos(phi)
    old = np.sin(np.arctan2(thd_w, th) - phi)          # swapped args: == cos(2 phi)
    r = np.hypot(th, thd_w)
    new = (r / (r + 1e-3)) * np.sin(np.arctan2(th, thd_w) - phi)   # corrected: == 0
    return old, new


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)

    phi = np.linspace(0, 2 * np.pi, 200)
    old_pull, new_pull = perfect_tracking_pull(phi)

    f_self = [realized_freq(g, "self") for g in GAINS]
    f_inter = [realized_freq(g, "inter") for g in GAINS]
    c_self = [realized_freq(GAIN_C, "self", c) for c in DRAGS]
    c_inter = [realized_freq(GAIN_C, "inter", c) for c in DRAGS]

    print("\n=== Proprioceptive entrainment (round-3: inter-segmental) ===")
    print(f"  perfect-tracking pull: max|swapped|={np.max(np.abs(old_pull)):.3f}  "
          f"max|corrected|={np.max(np.abs(new_pull)):.2e}")
    print("  free-run freq vs gain (Hz):")
    for g, a, b in zip(GAINS, f_self, f_inter):
        print(f"     eps={g:4.1f}   self={a:.3f}   inter={b:.3f}")
    print(f"  freq vs drag (eps={GAIN_C}):")
    print(f"     self : {[round(v,3) for v in c_self]}")
    print(f"     inter: {[round(v,3) for v in c_inter]}")
    flat = (max(c_inter) - min(c_inter)) < 0.06
    print("  verdict:", (
        "MECHANISM CORRECT, PAYOFF DEFERRED: inter-segmental topology is stable and "
        "vanishes under perfect tracking (CI-tested), but freq is flat vs drag under "
        "both topologies -- medium adaptation needs the articulation-load step."
        if flat else "inter shows a drag dependence -- investigate."))

    # ---- figure ----
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(15, 4.6))

    axA.axhline(0, color="#999", lw=0.8)
    axA.plot(phi, old_pull, color="#b00000", lw=1.8,
             label=r"round-1 (buggy) $=\cos 2\varphi$")
    axA.plot(phi, new_pull, color="#1538a0", lw=2.4,
             label="corrected $\\equiv 0$ (CI-tested)")
    axA.set_xlabel(r"gait phase $\varphi$ (rad)")
    axA.set_ylabel("pull under perfect tracking")
    axA.set_title("A — invariant: no error → no pull", fontsize=10)
    axA.legend(loc="lower right", fontsize=7)

    axB.axhline(FREQ, ls=":", color="#333", lw=1.0, label="commanded (0.9 Hz)")
    axB.plot(GAINS, f_self, "-o", color="#b00000",
             label="self (ablation): runaway brake")
    axB.plot(GAINS, f_inter, "-s", color="#1538a0",
             label="inter-segmental (correct)")
    axB.set_xlabel("entrainment gain  $\\varepsilon$")
    axB.set_ylabel("free-run realized freq (Hz)")
    axB.set_ylim(0, FREQ * 1.15)
    axB.set_title("B — why topology matters (5-segment body)", fontsize=10)
    axB.legend(loc="lower left", fontsize=7)

    axC.plot(DRAGS, c_self, "-o", color="#b00000", label="self (ε=2)")
    axC.plot(DRAGS, c_inter, "-s", color="#1538a0", label="inter (ε=2)")
    axC.axhline(FREQ, ls=":", color="#333", lw=1.0, label="commanded")
    axC.set_ylim(0, FREQ * 1.15)
    axC.set_xlabel("transverse drag (medium resistance)")
    axC.set_ylabel("free-run realized freq (Hz)")
    axC.set_title("C — open problem: flat until articulation load", fontsize=10)
    axC.legend(loc="lower left", fontsize=7)

    fig.tight_layout()
    out = os.path.join(figdir, "entrainment.png")
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
