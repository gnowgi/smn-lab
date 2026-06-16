# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Q2 -- self/world distinction (reafference) on the crawler. Pre-registered.

The reafference principle, exactly: for a sensed field value m, its rate of change
decomposes as

    dm/dt  =  grad(m) . v        (self-caused: my own motion through the field)
           +  d m / d t |_world   (world-caused: the field itself changing).

A reafferent agent predicts the self term from what it can sense of its own
motion and the field gradient, and is left with the world term as a residual.

  - SELF-TEST window  -- the world is static, the agent moves -> residual ~ noise.
  - EXAFFERENCE window -- a source the agent did NOT move ramps up in the field ->
    residual spikes (a world-caused change the agent could not have predicted).

Mechanism + provenance: this is the reafference principle of the SMN preprint
(arXiv:2605.26856, "modulators ... bind transient events to body-centered
reference frames"). The operationalization -- predict dm from a plane-fit field
gradient times the agent's own (proprioceptively sensed, noisy) velocity -- is our
implementation choice, parameter-free, declared here.

Foil: no forward model (predicted self-term = 0), so the residual is the raw dm,
which is large under the agent's own motion -- no self/world separation.

Order parameter: residual ratio = mean|residual| in exafference / in self-test.
Pass: ratio >> 1 for the reafferent agent and ~1 for the foil, across seeds.

Outputs: data/q2_reafference/, samples/q2_reafference/summary.csv,
figures/q2_reafference.png
Run:  ../.venv/bin/python sweep_q2_reafference.py
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
from smn_lab.fields import ScalarField
from smn_lab.sweep import run_sweep, export_curated

DT = 0.002
N_SEG = 5
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
SEEDS = list(range(10))
SENSOR_NOISE = 0.002          # field-reading noise (the noise floor)
PROPRIO_NOISE = 0.03         # fractional noise on the agent's own velocity sense
WIN = 125                    # [adj] reafference evaluated per 0.25 s window: per-step
                              # field change is below the noise floor, so we compare
                              # m over a window where self-motion change clears noise
# The static world is a LINEAR gradient (a uniform chemical/thermal slope). This
# is the world where the reafference model -- predict self-caused change as
# (gradient . self-displacement) -- is *exact*, so the demonstration is clean and
# unrigged: any residual after cancellation is genuinely world-caused, not model
# error. (The curved multi-source field is the harder case; see the doc.) The
# agent's own motion through this slope produces a large self-caused change that,
# without reafference (the foil), swamps the world-caused signal.
GRAD_A, GRAD_B = 1.6, 1.2     # static-world gradient (per metre), in x and y
T_LEARN = 12.0               # calibrate the gradient->dm scale (world static)
T_SELF = 14.0                # self-test (world static)
T_EXAF = 14.0                # exafference (a source the agent did not move ramps in)
T_END = T_LEARN + T_SELF + T_EXAF
# Exafference = a strong source that MOVES across the agent's region (as in P0's
# sliding object) -- a large world-caused change the agent did not produce. A
# moving source gives a substantial dm/dt|_world, the term reafference cannot
# cancel. (amp, sigma, start x/y, velocity x/y)
EXAF_AMP, EXAF_SIG = 3.0, 0.5
EXAF_START = (-0.6, 1.6)
EXAF_VEL = (0.10, -0.20)          # m/s


def run_one(params, seed):
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N_SEG))
    data = mujoco.MjData(model)
    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    hid = seg_ids[0]
    sL = [model.site(f"seg{k}_L").id for k in range(N_SEG)]
    sR = [model.site(f"seg{k}_R").id for k in range(N_SEG)]
    j_ids = [model.joint(f"j{k}").id for k in range(1, N_SEG)]
    j_qadr = [model.jnt_qposadr[j] for j in j_ids]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9, coupling=4.0, turn_gain=0.0)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]

    def field_now(x, y, t):
        v = GRAD_A * x + GRAD_B * y                     # static linear slope
        if T_LEARN + T_SELF <= t:                       # exafference: a MOVING source
            te = t - (T_LEARN + T_SELF)
            ex = EXAF_START[0] + EXAF_VEL[0] * te
            ey = EXAF_START[1] + EXAF_VEL[1] * te
            v += EXAF_AMP * np.exp(-((x - ex) ** 2 + (y - ey) ** 2) / (2 * EXAF_SIG ** 2))
        return v

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    steer, m_prev = 0.0, None
    vel = np.zeros(6)
    scale = 1.0
    cal_num, cal_den = 0.0, 0.0
    dx_acc, dy_acc = 0.0, 0.0          # sensed self-displacement over the window
    log = {k: [] for k in ("t", "res_reaff", "res_foil", "phase", "m")}
    for i in range(n):
        t = i * DT
        steer += (-steer / 2.5) * DT + 1.6 * np.sqrt(DT) * rng.normal()
        theta_cmd = beam.command(DT, bias=0.0)
        theta_cmd[0] += 0.6 * np.clip(steer, -1.5, 1.5)
        for k in range(len(j_ids)):
            th, thd = float(data.qpos[j_qadr[k]]), float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]], data.ctrl[aid_n[k]] = a_r, a_l
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)

        # accumulate the agent's own (proprioceptive, noisy) displacement
        mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, hid, vel, 0)
        dx_acc += vel[3] * (1 + rng.normal(0, PROPRIO_NOISE)) * DT
        dy_acc += vel[4] * (1 + rng.normal(0, PROPRIO_NOISE)) * DT

        if i % WIN != 0:
            continue
        # gather sensor sites (world positions + noisy field readings)
        pts, vals = [], []
        for sid in sL + sR:
            x, y = data.site_xpos[sid][:2]
            pts.append((x, y)); vals.append(field_now(x, y, t) + rng.normal(0, SENSOR_NOISE))
        pts = np.array(pts); vals = np.array(vals)
        m = float(vals.mean())
        A = np.column_stack([np.ones(len(pts)), pts[:, 0], pts[:, 1]])
        _, gx, gy = np.linalg.lstsq(A, vals, rcond=None)[0]    # field gradient (world)
        pred_basis = gx * dx_acc + gy * dy_acc                 # grad . self-displacement
        pred_self = scale * pred_basis
        if m_prev is not None:
            dm = m - m_prev
            res_reaff = dm - pred_self                         # world term survives
            res_foil = dm                                      # no cancellation
            if t < T_LEARN:                                    # calibrate the self-gain
                cal_num += dm * pred_basis; cal_den += pred_basis ** 2
                phase = 0
            else:
                phase = 1 if t < (T_LEARN + T_SELF) else 2
            log["t"].append(t); log["m"].append(m)
            log["res_reaff"].append(res_reaff); log["res_foil"].append(res_foil)
            log["phase"].append(phase)
            if t < T_LEARN and cal_den > 1e-12:
                scale = cal_num / cal_den
        m_prev = m
        dx_acc, dy_acc = 0.0, 0.0
    for k in log:
        log[k] = np.array(log[k])
    return log


def summarize(log, params, seed):
    ph = log["phase"]
    sr = np.abs(log["res_reaff"]); sf = np.abs(log["res_foil"])
    self_r, exaf_r = sr[ph == 1].mean(), sr[ph == 2].mean()
    self_f, exaf_f = sf[ph == 1].mean(), sf[ph == 2].mean()
    return {"self_reaff": float(self_r), "exaf_reaff": float(exaf_r),
            "ratio_reaff": float(exaf_r / max(self_r, 1e-12)),
            "self_foil": float(self_f), "exaf_foil": float(exaf_f),
            "ratio_foil": float(exaf_f / max(self_f, 1e-12))}


def plot(summary, repr_log, out):
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    t = repr_log["t"]; ph = repr_log["phase"]
    shade = [(1, "self-test (world static)", "#e8f7e8"),
             (2, "exafference (world-caused)", "#fde8e8")]
    for p, lab, c in shade:
        msk = ph == p
        if msk.any():
            axA.axvspan(t[msk][0], t[msk][-1], color=c, alpha=0.8, lw=0)
            axA.text(t[msk].mean(), 0.96, lab, transform=axA.get_xaxis_transform(),
                     ha="center", va="top", fontsize=8, color="#555")
    axA.plot(t, np.abs(repr_log["res_foil"]), lw=0.5, color="#c9a23a",
             label="foil |dm| (no cancellation)")
    axA.plot(t, np.abs(repr_log["res_reaff"]), lw=0.6, color="#1538a0",
             label="reafferent residual")
    axA.set_xlabel("time (s)"); axA.set_ylabel("|sensory change| per step")
    axA.legend(fontsize=8, loc="upper left"); axA.set_ylim(bottom=0)
    axA.set_title("A — reafference cancels self-caused change;\nworld-caused change "
                  "(exafference) survives  [one seed]", fontsize=9.5)

    rr = summary["ratio_reaff"].values; rf = summary["ratio_foil"].values
    x = np.arange(2)
    axB.bar(x, [rr.mean(), rf.mean()], yerr=[rr.std(), rf.std()], capsize=5,
            color=["#1538a0", "#c9a23a"], width=0.6)
    for xi, vals in zip(x, [rr, rf]):
        axB.scatter(np.full_like(vals, xi), vals, color="k", s=14, zorder=3)
    axB.axhline(1.0, color="#888", ls=":", lw=0.9)
    axB.set_xticks(x); axB.set_xticklabels(["reafferent", "foil"])
    axB.set_ylabel("residual ratio  (exafference / self-test)")
    axB.set_title(f"B — self/world separation across {len(rr)} seeds\n"
                  "(ratio ≫ 1 = world-caused change stands out)", fontsize=9.5)
    fig.suptitle("Q2 — self/world distinction (reafference) on the crawler", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    repr_log = run_one({}, SEEDS[0])      # representative trace for panel A
    summary = run_sweep("q2_reafference", run_one, {"agent": ["crawler"]}, SEEDS,
                        summarize, outdir=os.path.join(here, "..", "data"),
                        timeseries=False)
    export_curated("q2_reafference", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    print(f"\n  reafferent ratio: {summary.ratio_reaff.mean():.1f} ± {summary.ratio_reaff.std():.1f}")
    print(f"  foil ratio:       {summary.ratio_foil.mean():.2f} ± {summary.ratio_foil.std():.2f}")
    plot(summary, repr_log, os.path.join(figdir, "q2_reafference.png"))
