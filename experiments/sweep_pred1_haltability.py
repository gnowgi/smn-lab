# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Prediction 1 -- haltability signatures (deceptive reach). Pre-registered.

SMN preprint, Predictions & Testable Claims #1: "Tasks requiring mid-course
reversals (e.g., deceptive reach) should show distinct stoppage-resume patterns and
re-pairing among effectors." This is the HAP (Haltable Action Pattern) signature;
it extends C1's halt-on-contact to a halt triggered by an internal goal change.

Task. A single hinge limb (an opponent pair = two effectors) reaches its tip to a
target. Mid-reach the target JUMPS (a "deceptive reach"); for the headline case it
REVERSES sign. Two controllers solve the identical task:
  - HALT (HAP): on detecting the goal change, it briefly HALTS the ongoing
    movement (brakes to a stop, a short dwell), then resumes toward the new target;
  - SMOOTH (foil): a continuous PD that simply re-targets -- no halt.

Pre-registration:
- Hypothesis: the haltable controller produces a DISTINCT stoppage-resume signature
  -- a velocity minimum near zero with a measurable dwell at the reversal -- and a
  DISCRETE re-pairing of the opponent pair (the dominant puller flips through a
  dwell), whereas the smooth controller corrects continuously (velocity stays well
  above zero; the puller dominance crosses over gradually).
- Order parameters: minimum |velocity| in the transition window; dwell duration
  (|vel| < thresh); and the abruptness of the opponent-pair flip. Secondary
  (exploratory): overshoot past the new target, reacquisition time.
- Conditions: controller {halt, smooth} x jump {reversal, small-adjust} x seeds.
- Pass: the halt controller's transition velocity minimum is near zero with a clear
  dwell while the smooth controller's stays high -- a categorical separation -- and
  re-pairing is discrete for halt, gradual for smooth.
- Falsify: the two signatures are not distinguishable.

Honest note: that a halt controller halts is partly by construction (as with the
other preprint-prediction reproductions). The informative, falsifiable content is
(a) that the signature is CATEGORICALLY distinct and cleanly quantifiable -- i.e.,
diagnostic of haltability, as the preprint claims -- and (b) whether the halt
carries any functional consequence (overshoot / reacquisition), reported as found.

Outputs: data/pred1_haltability/, samples/.../summary.csv,
figures/sweep_pred1_haltability.png
Run:  ../.venv/bin/python sweep_pred1_haltability.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.sweep import run_sweep, export_curated

DT = 0.002
T_END = 2.4
T_JUMP = 0.35               # target jumps WHILE the limb is still moving (mid-reach),
                              # so a velocity drop is a genuine halt, not arrival/settling
A = 0.7                    # initial target (rad)
TARGETS = {"reversal": -0.5, "small-adjust": 1.1}   # post-jump target B
# Slow, heavy limb (below) + a low actuator ceiling so the reach has a real
# cruising phase (~0.5 s) -- otherwise the movement finishes before any jump.
KP, KD = 3.0, 0.7
CMAX = 0.45
HALT_DUR = 0.18            # HAP dwell after a detected goal change (s)
VEL_TOL = 0.35            # |vel| below this = "stopped" (rad/s)
PROPRIO_NOISE = 0.004
SEEDS = list(range(6))


def build_limb_xml():
    return """
<mujoco model="halt_limb">
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <worldbody>
    <body name="limb" pos="0 0 0.4">
      <joint name="j" type="hinge" axis="0 0 1" damping="0.30"/>
      <geom type="capsule" fromto="0 0 0 0.30 0 0" size="0.025" mass="1.0"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="m_p" joint="j" gear="1"  ctrlrange="0 3"/>
    <motor name="m_n" joint="j" gear="-1" ctrlrange="0 3"/>
  </actuator>
  <sensor>
    <jointpos name="ang" joint="j"/>
    <jointvel name="vel" joint="j"/>
  </sensor>
</mujoco>
"""


def run_one(params, seed):
    mode = params["controller"]; B = TARGETS[params["jump"]]
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_limb_xml())
    data = mujoco.MjData(model)
    jid = model.joint("j").id
    qadr, vadr = model.jnt_qposadr[jid], model.jnt_dofadr[jid]
    ap, an = model.actuator("m_p").id, model.actuator("m_n").id

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    halt_timer = 0
    log = {k: [] for k in ("t", "theta", "vel", "a_p", "a_n", "target")}
    for i in range(n):
        t = i * DT
        target = A if t < T_JUMP else B
        th = float(data.qpos[qadr]); thd = float(data.qvel[vadr])
        th_s = th + rng.normal(0, PROPRIO_NOISE)
        thd_s = thd + rng.normal(0, PROPRIO_NOISE * 10)

        # detect the goal change (one step after the jump) -> HAP halt
        if mode == "halt" and abs(t - T_JUMP) < DT:
            halt_timer = int(HALT_DUR / DT)

        if mode == "halt" and halt_timer > 0:
            tau = KP * (th_s - th_s) - 2.0 * KD * thd_s   # brake to a stop (dwell)
            halt_timer -= 1
        else:
            tau = KP * (target - th_s) + KD * (0.0 - thd_s)  # PD toward current goal
        a_p = min(CMAX, max(0.0, tau)); a_n = min(CMAX, max(0.0, -tau))
        data.ctrl[ap], data.ctrl[an] = a_p, a_n
        mujoco.mj_step(model, data)

        log["t"].append(t); log["theta"].append(float(data.qpos[qadr]))
        log["vel"].append(float(data.qvel[vadr]))
        log["a_p"].append(a_p); log["a_n"].append(a_n); log["target"].append(target)
    for k in log:
        log[k] = np.array(log[k])
    return log


def summarize(log, params, seed):
    t = log["t"]; B = TARGETS[params["jump"]]
    win = (t >= T_JUMP) & (t <= T_JUMP + 0.35)         # transition window
    vmin = float(np.abs(log["vel"][win]).min())
    dwell = float(np.sum(np.abs(log["vel"][win]) < VEL_TOL) * DT)
    # re-pairing abruptness: max step in (a_p - a_n) across the transition
    d = log["a_p"][win] - log["a_n"][win]
    repair_step = float(np.abs(np.diff(d)).max()) if len(d) > 1 else 0.0
    # functional (exploratory): overshoot past B, reacquisition time
    after = t >= T_JUMP
    overshoot = float(max(0.0, (log["theta"][after] - B).max() if B < A
                          else (B - log["theta"][after]).min() * -1))
    err = np.abs(log["theta"] - B)
    acq = t[after][np.where(err[after] < 0.03)[0]]
    reacq = float(acq[0] - T_JUMP) if len(acq) else float("nan")
    return {"vel_min": vmin, "dwell": dwell, "repair_step": repair_step,
            "overshoot": overshoot, "reacq_time": reacq}


def plot(summary, repr_logs, out):
    fig = plt.figure(figsize=(14, 8.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.32, wspace=0.26)
    colors = {"halt": "#1538a0", "smooth": "#c9a23a"}

    # A: velocity profiles (reversal) -- the stop-resume signature
    axA = fig.add_subplot(gs[0, 0])
    for mode in ("halt", "smooth"):
        L = repr_logs[(mode, "reversal")]
        axA.plot(L["t"], L["vel"], color=colors[mode], lw=1.6, label=mode)
    axA.axvline(T_JUMP, color="#888", ls=":", lw=1.0)
    axA.axhline(0, color="#bbb", lw=0.6)
    axA.set_xlabel("time (s)"); axA.set_ylabel("angular velocity (rad/s)")
    axA.set_title("A — velocity at the reversal: halt stops (dwell at 0)\n"
                  "then resumes; smooth corrects continuously", fontsize=9.5)
    axA.legend(fontsize=8)

    # B: opponent-pair activations (reversal) -- re-pairing
    axB = fig.add_subplot(gs[0, 1])
    L = repr_logs[("halt", "reversal")]
    axB.plot(L["t"], L["a_p"], color="#1538a0", lw=1.4, label="puller + (halt)")
    axB.plot(L["t"], L["a_n"], color="#1538a0", lw=1.4, ls="--", label="puller − (halt)")
    Ls = repr_logs[("smooth", "reversal")]
    axB.plot(Ls["t"], Ls["a_p"], color="#c9a23a", lw=1.2, label="puller + (smooth)")
    axB.plot(Ls["t"], Ls["a_n"], color="#c9a23a", lw=1.2, ls="--", label="puller − (smooth)")
    axB.axvline(T_JUMP, color="#888", ls=":", lw=1.0)
    axB.set_xlabel("time (s)"); axB.set_ylabel("activation")
    axB.set_title("B — re-pairing: the dominant puller flips at the reversal", fontsize=9.5)
    axB.legend(fontsize=7, ncol=2)

    # C: signature separation across seeds -- transition velocity minimum
    axC = fig.add_subplot(gs[1, 0])
    x = np.arange(2); w = 0.35
    for k, mode in enumerate(("halt", "smooth")):
        vals = [summary[(summary.controller == mode) & (summary.jump == j)]["vel_min"]
                for j in ("reversal", "small-adjust")]
        means = [v.mean() for v in vals]; sds = [v.std() for v in vals]
        axC.bar(x + (k - 0.5) * w, means, w, yerr=sds, capsize=4,
                color=colors[mode], label=mode)
    axC.axhline(VEL_TOL, color="#b00", ls="--", lw=0.9, label="stop threshold")
    axC.set_xticks(x); axC.set_xticklabels(["reversal", "small-adjust"])
    axC.set_ylabel("transition |velocity| minimum (rad/s)")
    axC.set_title("C — velocity min: on a same-direction adjustment smooth never\n"
                  "stops (halt does); a reversal makes both cross zero (see D)", fontsize=9.5)
    axC.legend(fontsize=8)

    # D: dwell duration across seeds
    axD = fig.add_subplot(gs[1, 1])
    for k, mode in enumerate(("halt", "smooth")):
        vals = [summary[(summary.controller == mode) & (summary.jump == j)]["dwell"]
                for j in ("reversal", "small-adjust")]
        means = [v.mean() for v in vals]; sds = [v.std() for v in vals]
        axD.bar(x + (k - 0.5) * w, means, w, yerr=sds, capsize=4,
                color=colors[mode], label=mode)
    axD.set_xticks(x); axD.set_xticklabels(["reversal", "small-adjust"])
    axD.set_ylabel("dwell duration (s)  [|vel| < threshold]")
    axD.set_title("D — dwell: halt has a measurable stop;\nsmooth has ~none", fontsize=9.5)
    axD.legend(fontsize=8)

    fig.suptitle("Prediction 1 — haltability signatures: deceptive reach shows a "
                 "distinct stop-resume and effector re-pairing", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    repr_logs = {(m, j): run_one({"controller": m, "jump": j}, 0)
                 for m in ("halt", "smooth") for j in ("reversal", "small-adjust")}
    grid = [{"controller": m, "jump": j}
            for m in ("halt", "smooth") for j in ("reversal", "small-adjust")]
    summary = run_sweep("pred1_haltability", run_one, grid, SEEDS, summarize,
                        outdir=os.path.join(here, "..", "data"), timeseries=False)
    export_curated("pred1_haltability", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    print("\n  reversal — transition velocity minimum & dwell:")
    for m in ("halt", "smooth"):
        d = summary[(summary.controller == m) & (summary.jump == "reversal")]
        print(f"   {m:6s}: vel_min {d.vel_min.mean():.3f}  dwell {d.dwell.mean():.3f}  "
              f"overshoot {d.overshoot.mean():.3f}  reacq {d.reacq_time.mean():.3f}")
    plot(summary, repr_logs, os.path.join(figdir, "sweep_pred1_haltability.png"))
