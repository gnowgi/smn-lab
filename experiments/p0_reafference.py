# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P0 -- Register 3 (reafference: self vs world) in an embodied single CAZ.

A yaw 'head' (one Coordinated Action Zone, driven by a pull-only antagonist
pair) carries a rangefinder 'whisker' and sweeps a static walled arena. A
forward model learns the whisker reading as a function of heading during a
self-motion phase. We then test:

  * SELF-TEST window  -- agent keeps sweeping, world static  -> residual ~ noise floor
  * EXAFFERENCE window-- an object the agent did NOT move slides into the scene
                         -> residual jumps (world-caused, unpredicted change)

Reproduces, from real physics, the reafference register (self- vs world-caused
sensory change) predicted by the SMN architecture (Nagarjuna & Karnam,
arXiv:2605.26856). Outputs figures/p0_reafference.png and prints summary stats.

Run:  ../.venv/bin/python p0_reafference.py        (from this directory)
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.model import build_p0_xml
from smn_lab.control import OpponentBoard, ReafferencePredictor

# ---- parameters -----------------------------------------------------------
SEED = 7
DT = 0.005
SWEEP_AMP = 0.7        # rad (~40 deg) self-generated head sweep
SWEEP_F = 0.22         # Hz
SENSOR_NOISE = 0.005   # m, rangefinder noise -> the "noise floor"
MAX_RANGE = 5.0        # clamp for no-hit (-1) readings
OBJ_FAR = 2.6          # m, parked outside arena (whisker hits wall, not object)
OBJ_NEAR = 0.5         # m, slid in front of the agent for exafference

# phase boundaries (seconds)
T_LEARN = 20.0         # learn the contingency (world static, model updating)
T_SELFTEST = 12.0      # model frozen, world static -> residual should be floor
T_EXAF = 14.0          # object present -> residual should spike
T_POST = 4.0           # object removed -> residual returns to floor
T_END = T_LEARN + T_SELFTEST + T_EXAF + T_POST


def run():
    rng = np.random.default_rng(SEED)
    model = mujoco.MjModel.from_xml_string(build_p0_xml())
    data = mujoco.MjData(model)

    aid_r = model.actuator("m_right").id
    aid_l = model.actuator("m_left").id
    yaw_jid = model.joint("yaw").id
    obj_jid = model.joint("obj_slide").id
    yaw_qadr = model.jnt_qposadr[yaw_jid]
    yaw_vadr = model.jnt_dofadr[yaw_jid]
    obj_qadr = model.jnt_qposadr[obj_jid]

    board = OpponentBoard(kp=3.0, kd=0.3, cmax=1.5)
    predictor = ReafferencePredictor(n_bins=72)

    # park the object far away
    data.qpos[obj_qadr] = OBJ_FAR
    mujoco.mj_forward(model, data)

    n = int(T_END / DT)
    log = {k: np.zeros(n) for k in
           ("t", "theta", "a_r", "a_l", "reading", "pred", "res", "phase")}

    w = 2 * np.pi * SWEEP_F
    for i in range(n):
        t = i * DT
        theta = float(data.qpos[yaw_qadr])
        theta_dot = float(data.qvel[yaw_vadr])

        # self-generated exploratory sweep (efference)
        theta_cmd = SWEEP_AMP * np.sin(w * t)
        theta_dot_cmd = SWEEP_AMP * w * np.cos(w * t)
        a_r, a_l, _ = board.commands(theta, theta_dot, theta_cmd, theta_dot_cmd)
        data.ctrl[aid_r] = a_r
        data.ctrl[aid_l] = a_l

        # world schedule: object present only during the exafference window
        in_exaf = (T_LEARN + T_SELFTEST) <= t < (T_LEARN + T_SELFTEST + T_EXAF)
        data.qpos[obj_qadr] = OBJ_NEAR if in_exaf else OBJ_FAR

        mujoco.mj_step(model, data)

        # read the whisker (transducer S), add sensor noise -> the noise floor
        raw = float(data.sensor("whisker_range").data[0])
        if raw < 0:
            raw = MAX_RANGE
        reading = raw + rng.normal(0.0, SENSOR_NOISE)
        theta_post = float(data.qpos[yaw_qadr])

        # learn the contingency only during the learning phase, then freeze
        if t < T_LEARN:
            predictor.update(theta_post, reading)
            phase = 0
        elif t < T_LEARN + T_SELFTEST:
            phase = 1
        elif in_exaf:
            phase = 2
        else:
            phase = 3

        pred = predictor.predict(theta_post)
        res = reading - pred

        log["t"][i] = t
        log["theta"][i] = theta_post
        log["a_r"][i] = a_r
        log["a_l"][i] = a_l
        log["reading"][i] = reading
        log["pred"][i] = pred
        log["res"][i] = res
        log["phase"][i] = phase

    return log


def summarize(log):
    res = log["res"]
    phase = log["phase"]
    b = np.abs(res[phase == 1])   # self-test (world static)
    c = np.abs(res[phase == 2])   # exafference
    stats = dict(
        selftest_mean=b.mean(), selftest_p95=np.percentile(b, 95),
        exaf_mean=c.mean(), exaf_p95=np.percentile(c, 95), exaf_max=c.max(),
        noise_floor=SENSOR_NOISE,
        ratio_mean=c.mean() / max(b.mean(), 1e-9),
    )
    return stats


def plot(log, stats, out):
    t = log["t"]
    phases = [(0, "learn", "#eef3ff"), (1, "self-test", "#e8f7e8"),
              (2, "exafference", "#fde8e8"), (3, "post", "#f2f2f2")]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for ph, label, color in phases:
        m = log["phase"] == ph
        if m.any():
            ax1.axvspan(t[m][0], t[m][-1], color=color, alpha=0.7, lw=0)
            ax2.axvspan(t[m][0], t[m][-1], color=color, alpha=0.7, lw=0)
            ax1.text(t[m].mean(), 0.02, label, ha="center", va="bottom",
                     transform=ax1.get_xaxis_transform(), fontsize=8, color="#555")
    ax1.plot(t, log["reading"], lw=0.6, color="#cc4422", label="whisker reading (actual)")
    ax1.plot(t, log["pred"], lw=0.9, color="#225599", label="forward-model prediction")
    ax1.set_ylabel("whisker range (m)")
    ax1.legend(loc="upper right", fontsize=8)
    ax1.set_title("P0 — Register 3 (reafference): single embodied CAZ + whisker")

    ax2.plot(t, log["res"], lw=0.6, color="#333")
    ax2.axhline(SENSOR_NOISE, color="#888", ls=":", lw=0.8)
    ax2.axhline(-SENSOR_NOISE, color="#888", ls=":", lw=0.8, label="±noise floor")
    ax2.set_ylabel("residual (m)\nactual − predicted")
    ax2.set_xlabel("time (s)")
    ax2.legend(loc="upper right", fontsize=8)
    cap = (f"self-test mean|res|={stats['selftest_mean']*1000:.2f} mm  |  "
           f"exafference mean|res|={stats['exaf_mean']*1000:.1f} mm  "
           f"(×{stats['ratio_mean']:.0f}), max={stats['exaf_max']*1000:.0f} mm")
    fig.text(0.5, 0.005, cap, ha="center", fontsize=9, color="#333")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    log = run()
    stats = summarize(log)
    print("\n=== P0 Register 3 (reafference) — embodied ===")
    for k, v in stats.items():
        print(f"  {k:16s} {v:.5f}")
    verdict = ("PASS: self-caused change cancels (residual ~ noise floor); "
               "world-caused change does not (residual jumps)."
               if stats["ratio_mean"] > 5 and stats["selftest_mean"] < 3 * SENSOR_NOISE
               else "INCONCLUSIVE — tune params.")
    print("  verdict:", verdict)
    plot(log, stats, os.path.join(figdir, "p0_reafference.png"))
