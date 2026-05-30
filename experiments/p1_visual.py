# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P1-visual -- the multi-CAZ eye: reafference under eye saccades, with and
without body yaw.

Builds on ``p0_visual.py`` by adding a CAZ pair on the **eye itself**: the eye
is a small body nested in the head with its own hinge joint and its own pull-
only opponent pair, driven by a basic saccade generator (random fixation
target every 0.30 s). The camera now sits on the eye, so the camera's total
yaw in world is ``head_yaw + eye_yaw`` and the analytical forward model
predicts the next frame from the *sum* -- whichever CAZ pair produced the
motion is the one the modulator predicts away.

The point of the experiment is to compare two conditions, identical except
for whether the body's head CAZ is active:

  * **+body yaw** -- the head sweeps (as in P0-visual) AND the eye saccades.
    The reafference register holds under combined head + eye motion.
  * **-body yaw** -- the head is held at 0 (no body CAZ activity); only the
    eye saccades. The reafference register holds with eye motion alone --
    the snapshot is built from saccade-driven self-motion in a stationary
    body.

Both conditions share the same three-phase structure as P0-visual --
calibration (learn per-patch noise floor), self-test (modulator frozen, world
static), exafference (object oscillates) -- and the same modulator
(percentile 90, floor_min 3.0).

This is the bench's first demonstration that **gazing-while-still is itself a
constructive modulating activity**: the snapshot is what survives the eye's
own predicted self-motion, not the body's.

Run:  ../.venv/bin/python p1_visual.py        (from this directory)
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.model import build_p1v_xml
from smn_lab.control import OpponentBoard, SaccadeController
from smn_lab.vision import (EyeCamera, AnalyticalFramePredictor,
                            PatchResidualModulator)

SEED = 7
DT = 0.005
RENDER_EVERY = 2                # 100 Hz vision: per-frame Δθ < 1 px under
                                # combined head+eye motion, keeping the warp accurate
FRAME = 128
FOV_DEG = 90.0
PATCH_GRID = 8

# head sweep (only used in +body-yaw condition)
HEAD_SWEEP_AMP = 0.30           # rad (~17 deg)
HEAD_SWEEP_F = 0.40             # Hz

# eye saccades (used in both conditions)
EYE_RANGE_DEG = 15.0
EYE_RANGE_RAD = np.radians(EYE_RANGE_DEG)
EYE_FIXATION_S = 0.35

# exafference object (same as p0_visual)
OBJ_HIDDEN = 3.0
OBJ_X_MEAN = 0.7
OBJ_X_AMP = 0.25
OBJ_F = 0.5

T_CAL = 12.0
T_SELFTEST = 8.0
T_EXAF = 10.0
T_POST = 3.0
T_END = T_CAL + T_SELFTEST + T_EXAF + T_POST


def run(with_body_yaw: bool, label: str):
    model = mujoco.MjModel.from_xml_string(
        build_p1v_xml(fov_deg=FOV_DEG, eye_yaw_range_deg=EYE_RANGE_DEG))
    data = mujoco.MjData(model)

    aid_hr = model.actuator("m_head_right").id
    aid_hl = model.actuator("m_head_left").id
    aid_er = model.actuator("m_eye_right").id
    aid_el = model.actuator("m_eye_left").id

    head_jid = model.joint("head_yaw").id
    eye_jid = model.joint("eye_yaw").id
    obj_jid = model.joint("obj_slide").id
    head_qadr = model.jnt_qposadr[head_jid]
    head_vadr = model.jnt_dofadr[head_jid]
    eye_qadr = model.jnt_qposadr[eye_jid]
    eye_vadr = model.jnt_dofadr[eye_jid]
    obj_qadr = model.jnt_qposadr[obj_jid]

    head_board = OpponentBoard(kp=3.0, kd=0.3, cmax=1.5)
    eye_board = OpponentBoard(kp=8.0, kd=1.2, cmax=1.5)
    saccade = SaccadeController(range_rad=EYE_RANGE_RAD,
                                fixation_s=EYE_FIXATION_S, seed=SEED)
    # Two smoothing passes (~σ 1.0) — combined head + eye motion needs softer
    # edges than head-only sweep does, see top of vision.py.
    eye = EyeCamera(model, camera_name="eye", width=FRAME, height=FRAME,
                    smooth_passes=2)
    predictor = AnalyticalFramePredictor(width=FRAME, fov_deg=FOV_DEG)
    modulator = PatchResidualModulator(frame_size=FRAME, patch_grid=PATCH_GRID,
                                       percentile=90.0, floor_min=3.0)

    data.qpos[obj_qadr] = OBJ_HIDDEN
    mujoco.mj_forward(model, data)

    n_steps = int(T_END / DT)
    render_dt = DT * RENDER_EVERY
    n_frames = n_steps // RENDER_EVERY + 2

    t_frame = np.zeros(n_frames)
    mean_res = np.zeros(n_frames)
    fired_count = np.zeros(n_frames, dtype=int)
    phase = np.zeros(n_frames, dtype=int)
    head_log = np.zeros(n_frames)
    eye_log = np.zeros(n_frames)
    selftest_acc, exaf_acc, exaf_fire_acc = [], [], []
    sample = {"calibration": None, "self-test": None, "exafference": None}

    prev_frame = None
    prev_total_yaw = 0.0
    w_head = 2 * np.pi * HEAD_SWEEP_F
    fi = 0

    for k in range(n_steps):
        t = k * DT

        # head: sweep if condition allows, else hold at 0
        if with_body_yaw:
            theta_cmd = HEAD_SWEEP_AMP * np.sin(w_head * t)
            theta_dot_cmd = HEAD_SWEEP_AMP * w_head * np.cos(w_head * t)
        else:
            theta_cmd, theta_dot_cmd = 0.0, 0.0
        h_theta = float(data.qpos[head_qadr])
        h_theta_dot = float(data.qvel[head_vadr])
        a_hr, a_hl, _ = head_board.commands(h_theta, h_theta_dot,
                                            theta_cmd, theta_dot_cmd)
        data.ctrl[aid_hr] = a_hr; data.ctrl[aid_hl] = a_hl

        # eye: saccades to randomly-changing fixation targets
        eye_target = saccade.update(t)
        e_theta = float(data.qpos[eye_qadr])
        e_theta_dot = float(data.qvel[eye_vadr])
        a_er, a_el, _ = eye_board.commands(e_theta, e_theta_dot,
                                           eye_target, 0.0)
        data.ctrl[aid_er] = a_er; data.ctrl[aid_el] = a_el

        # world schedule
        in_exaf = (T_CAL + T_SELFTEST) <= t < (T_CAL + T_SELFTEST + T_EXAF)
        if in_exaf:
            t_in = t - (T_CAL + T_SELFTEST)
            data.qpos[obj_qadr] = OBJ_X_MEAN + OBJ_X_AMP * np.sin(
                2 * np.pi * OBJ_F * t_in)
        else:
            data.qpos[obj_qadr] = OBJ_HIDDEN

        mujoco.mj_step(model, data)

        if (k + 1) % RENDER_EVERY != 0:
            continue

        frame = eye.snap(data)
        # camera total yaw in world = head + eye (both about z, head upright)
        total_yaw = float(data.qpos[head_qadr]) + float(data.qpos[eye_qadr])

        if prev_frame is None:
            prev_frame = frame
            prev_total_yaw = total_yaw
            t_frame[fi] = t; phase[fi] = 0
            fi += 1
            continue

        delta_theta = total_yaw - prev_total_yaw
        # angle_correct=True uses the sec²(α) per-column shift; required once
        # head sweep takes wall content through the image edges where the
        # linear approximation underpredicts the true shift by up to 2×.
        predicted = predictor.predict(prev_frame, delta_theta,
                                      angle_correct=True)
        residual = frame - predicted

        if t < T_CAL:
            ph = 1
            pooled = modulator.calibrate(residual); mask = None
        else:
            if modulator.floor is None:
                modulator.finalize()
            pooled, mask = modulator.gate(residual)
            ph = (2 if t < T_CAL + T_SELFTEST else
                  3 if in_exaf else 4)

        t_frame[fi] = t
        mean_res[fi] = float(pooled.mean())
        phase[fi] = ph
        head_log[fi] = data.qpos[head_qadr]
        eye_log[fi] = data.qpos[eye_qadr]
        if mask is not None:
            fired_count[fi] = int(mask.sum())

        if ph == 1 and t > T_CAL * 0.5 and sample["calibration"] is None:
            sample["calibration"] = dict(frame=frame.copy(), residual=np.abs(residual).copy())
        elif ph == 2 and sample["self-test"] is None:
            sample["self-test"] = dict(frame=frame.copy(), residual=np.abs(residual).copy())
        elif ph == 3 and t > (T_CAL + T_SELFTEST + 2.0) and sample["exafference"] is None:
            sample["exafference"] = dict(frame=frame.copy(), residual=np.abs(residual).copy())
        if ph == 2:
            selftest_acc.append(pooled)
        elif ph == 3:
            exaf_acc.append(pooled)
            if mask is not None:
                exaf_fire_acc.append(mask.astype(np.float32))

        prev_frame = frame
        prev_total_yaw = total_yaw
        fi += 1

    eye.close()
    t_frame = t_frame[:fi]; mean_res = mean_res[:fi]
    fired_count = fired_count[:fi]; phase = phase[:fi]
    head_log = head_log[:fi]; eye_log = eye_log[:fi]

    selftest_map = (np.stack(selftest_acc).mean(axis=0)
                    if selftest_acc else np.zeros((PATCH_GRID, PATCH_GRID)))
    exaf_map = (np.stack(exaf_acc).mean(axis=0)
                if exaf_acc else np.zeros((PATCH_GRID, PATCH_GRID)))
    fire_map = (np.stack(exaf_fire_acc).mean(axis=0)
                if exaf_fire_acc else np.zeros((PATCH_GRID, PATCH_GRID)))

    return dict(label=label, t=t_frame, mean_res=mean_res, fired=fired_count,
                phase=phase, head_yaw=head_log, eye_yaw=eye_log,
                floor=modulator.floor.copy() if modulator.floor is not None else None,
                selftest_map=selftest_map, exaf_map=exaf_map, fire_map=fire_map,
                sample=sample)


def summarize(log):
    res = log["mean_res"]; ph = log["phase"]
    selftest = res[ph == 2]; exaf = res[ph == 3]
    n_tokens = PATCH_GRID * PATCH_GRID
    fire_selftest = (float(log["fired"][ph == 2].mean()) / n_tokens
                     if (ph == 2).any() else float("nan"))
    fire_exaf = (float(log["fired"][ph == 3].mean()) / n_tokens
                 if (ph == 3).any() else float("nan"))
    return dict(
        selftest_mean=float(selftest.mean()) if len(selftest) else float("nan"),
        exaf_mean=float(exaf.mean()) if len(exaf) else float("nan"),
        fired_selftest_frac=fire_selftest,
        fired_exaf_frac=fire_exaf,
        fire_ratio=fire_exaf / max(fire_selftest, 1e-3),
        floor_median=float(np.median(log["floor"])) if log["floor"] is not None else float("nan"),
    )


def plot_one_condition(fig, gs_row, log, stats):
    """Render one row (two columns wide) for a single condition."""
    t = log["t"]; ph = log["phase"]
    phases = [(1, "calibration", "#eef3ff"),
              (2, "self-test", "#e8f7e8"),
              (3, "exafference", "#fde8e8"),
              (4, "post", "#f2f2f2")]

    ax_time = fig.add_subplot(gs_row[0])
    ax_yaws = fig.add_subplot(gs_row[1])
    ax_fire = fig.add_subplot(gs_row[2])
    ax_exaf_f = fig.add_subplot(gs_row[3])

    # residual time series
    for p, label, color in phases:
        m = ph == p
        if m.any():
            ax_time.axvspan(t[m][0], t[m][-1], color=color, alpha=0.7, lw=0)
            ax_time.text(t[m].mean(), 0.02, label, ha="center", va="bottom",
                         transform=ax_time.get_xaxis_transform(),
                         fontsize=7, color="#555")
    ax_time.plot(t, log["mean_res"], lw=0.7, color="#333",
                 label="mean |residual|")
    if log["floor"] is not None:
        ax_time.axhline(float(np.median(log["floor"])), color="#888", ls=":",
                        lw=0.8)
    ax_time.set_ylabel("mean |residual|"); ax_time.set_xlabel("time (s)")
    ax_time.set_title(f"{log['label']}: "
                      f"fire-fraction selftest={stats['fired_selftest_frac']:.3f}, "
                      f"exaf={stats['fired_exaf_frac']:.3f} "
                      f"(×{stats['fire_ratio']:.1f})", fontsize=10)
    ax_time.grid(alpha=0.25)

    # yaw schedules (head + eye)
    ax_yaws.plot(t, log["head_yaw"], lw=0.7, color="#225599", label="head yaw")
    ax_yaws.plot(t, log["eye_yaw"], lw=0.5, color="#cc4422", label="eye yaw")
    ax_yaws.set_ylabel("yaw (rad)"); ax_yaws.set_xlabel("time (s)")
    ax_yaws.legend(fontsize=7, loc="upper right")
    ax_yaws.grid(alpha=0.25)

    # fire-fraction heatmap during exafference
    im = ax_fire.imshow(log["fire_map"], vmin=0, vmax=1, cmap="Reds",
                        origin="upper")
    ax_fire.set_xticks([]); ax_fire.set_yticks([])
    ax_fire.set_title("exafference: fire-fraction", fontsize=9)
    fig.colorbar(im, ax=ax_fire, fraction=0.046, pad=0.04)

    # representative exafference |residual| frame
    s = log["sample"].get("exafference")
    if s is not None:
        im = ax_exaf_f.imshow(s["residual"], cmap="magma", origin="upper")
        fig.colorbar(im, ax=ax_exaf_f, fraction=0.046, pad=0.04)
    ax_exaf_f.set_xticks([]); ax_exaf_f.set_yticks([])
    ax_exaf_f.set_title("exafference |frame − predicted|", fontsize=9)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    print("\n=== P1-visual: multi-CAZ eye, ±body yaw ===")
    run_plus = run(with_body_yaw=True, label="+body yaw (head sweeps + eye saccades)")
    run_minus = run(with_body_yaw=False, label="−body yaw (eye saccades only)")
    for r in (run_plus, run_minus):
        s = summarize(r)
        print(f"  {r['label']:46s}: "
              f"fire-fraction selftest={s['fired_selftest_frac']:.3f}  "
              f"exaf={s['fired_exaf_frac']:.3f}  ×{s['fire_ratio']:.1f}")

    fig = plt.figure(figsize=(15, 8.5))
    # 2 conditions x 4 panels each (time / yaw / fire / exafframe)
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1],
                          width_ratios=[2.2, 1.2, 1.0, 1.0],
                          hspace=0.45, wspace=0.30)
    plot_one_condition(fig, [gs[0, c] for c in range(4)],
                       run_plus, summarize(run_plus))
    plot_one_condition(fig, [gs[1, c] for c in range(4)],
                       run_minus, summarize(run_minus))

    fig.suptitle("P1-visual — the multi-CAZ eye. The reafference register survives "
                 "both with and without body yaw: whichever CAZ pair "
                 "(head, eye, or both) produced the motion is the one the "
                 "modulator predicts away.",
                 fontsize=10)
    out = os.path.join(figdir, "p1_visual.png")
    fig.savefig(out, dpi=120, bbox_inches="tight")
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
