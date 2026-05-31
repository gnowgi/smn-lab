# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P1-visual / static-world variant -- only agent-side modulation.

This experiment isolates the multi-CAZ eye's reafference register by holding
the world genuinely still (or nearly so), so the only motion the modulator
ever has to predict is the eye's own. Three conditions share the same body
geometry, same eye saccade schedule, same modulator -- only what the world is
doing differs:

  * **A. always-static cylinder** -- the cylinder is visible at the same
    place from t = 0 to t_end. The modulator calibrates *with* the cylinder
    in view. If the architecture is sound, the residual should sit at the
    noise floor in all three phases -- a complex object is not enough to
    fire the modulator if it doesn't change.

  * **B. visible-then-oscillating** -- the cylinder is visible-static during
    calibration and self-test, then oscillates during exafference. The
    modulator already knows the cylinder's appearance; the exafference signal
    is therefore *purely the object's motion against a familiar scene*.

  * **C. hidden-then-visible-static** -- the cylinder is hidden during cal /
    self-test and appears (static, no later motion) during exafference. The
    modulator has never seen the cylinder; the appearance event is the only
    world-caused change in the run.

The architectural prediction (and what the figure will test):

  * A: silent throughout. The agent's eye saccades are perfectly predicted;
    the cylinder is absorbed into the static world from the warp's view.
  * B: silent during cal/self-test, fires during exafference. Object motion
    against a known scene is what survives the modulator.
  * C: silent during cal/self-test, **transient spike at exafference start,
    then silent again**. The analytical predictor has no memory of the
    pre-cylinder world; once the cylinder is in the prev frame, the warp
    tracks it through subsequent saccades and the residual collapses.

If C goes quiet after the transient, the headline finding is: **the current
architecture is a change-detector, not a presence-detector**. Persistent
presence requires a snapshot accumulator on top (the natural next piece of
architecture).

Run:  ../.venv/bin/python p1v_static_world.py        (from this directory)
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
RENDER_EVERY = 2
FRAME = 128
FOV_DEG = 90.0
PATCH_GRID = 8

# eye saccades (used in all three conditions; -body yaw throughout)
EYE_RANGE_DEG = 15.0
EYE_RANGE_RAD = np.radians(EYE_RANGE_DEG)
EYE_FIXATION_S = 0.35

# cylinder positions
OBJ_HIDDEN = 3.0
OBJ_X_MEAN = 0.7
OBJ_X_AMP = 0.25      # used in condition B (oscillating) only
OBJ_F = 0.5

T_CAL = 12.0
T_SELFTEST = 8.0
T_EXAF = 10.0
T_POST = 3.0
T_END = T_CAL + T_SELFTEST + T_EXAF + T_POST


def object_x(t: float, condition: str, in_exaf: bool) -> float:
    """Cylinder x position as a function of time, per condition."""
    if condition == "always-static":
        return OBJ_X_MEAN
    if condition == "visible-then-oscillating":
        if in_exaf:
            t_in = t - (T_CAL + T_SELFTEST)
            return OBJ_X_MEAN + OBJ_X_AMP * np.sin(2 * np.pi * OBJ_F * t_in)
        return OBJ_X_MEAN
    if condition == "hidden-then-static":
        return OBJ_X_MEAN if in_exaf else OBJ_HIDDEN
    raise ValueError(condition)


def run(condition: str, label: str):
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
    eye = EyeCamera(model, camera_name="eye", width=FRAME, height=FRAME,
                    smooth_passes=2)
    predictor = AnalyticalFramePredictor(width=FRAME, fov_deg=FOV_DEG)
    modulator = PatchResidualModulator(frame_size=FRAME, patch_grid=PATCH_GRID,
                                       percentile=90.0, floor_min=3.0)

    # initial cylinder position (so the renderer's first frame is consistent
    # with the condition's calibration content)
    data.qpos[obj_qadr] = object_x(0.0, condition, in_exaf=False)
    mujoco.mj_forward(model, data)

    n_steps = int(T_END / DT)
    render_dt = DT * RENDER_EVERY
    n_frames = n_steps // RENDER_EVERY + 2

    t_frame = np.zeros(n_frames)
    mean_res = np.zeros(n_frames)
    fired_count = np.zeros(n_frames, dtype=int)
    phase = np.zeros(n_frames, dtype=int)
    eye_log = np.zeros(n_frames)
    selftest_acc, exaf_acc, exaf_fire_acc = [], [], []
    sample = {"calibration": None, "self-test": None, "exafference": None,
              "exaf_transient": None}

    prev_frame = None
    prev_total_yaw = 0.0
    fi = 0
    exaf_first_done = False

    for k in range(n_steps):
        t = k * DT

        # head held at zero (no body CAZ activity)
        h_theta = float(data.qpos[head_qadr])
        h_theta_dot = float(data.qvel[head_vadr])
        a_hr, a_hl, _ = head_board.commands(h_theta, h_theta_dot, 0.0, 0.0)
        data.ctrl[aid_hr] = a_hr; data.ctrl[aid_hl] = a_hl

        # eye: random-fixation saccades
        eye_target = saccade.update(t)
        e_theta = float(data.qpos[eye_qadr])
        e_theta_dot = float(data.qvel[eye_vadr])
        a_er, a_el, _ = eye_board.commands(e_theta, e_theta_dot,
                                           eye_target, 0.0)
        data.ctrl[aid_er] = a_er; data.ctrl[aid_el] = a_el

        # cylinder schedule per condition
        in_exaf = (T_CAL + T_SELFTEST) <= t < (T_CAL + T_SELFTEST + T_EXAF)
        data.qpos[obj_qadr] = object_x(t, condition, in_exaf)

        mujoco.mj_step(model, data)

        if (k + 1) % RENDER_EVERY != 0:
            continue

        frame = eye.snap(data)
        total_yaw = float(data.qpos[head_qadr]) + float(data.qpos[eye_qadr])

        if prev_frame is None:
            prev_frame = frame
            prev_total_yaw = total_yaw
            t_frame[fi] = t; phase[fi] = 0
            fi += 1
            continue

        delta_theta = total_yaw - prev_total_yaw
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

        t_frame[fi] = t; mean_res[fi] = float(pooled.mean())
        phase[fi] = ph; eye_log[fi] = data.qpos[eye_qadr]
        if mask is not None:
            fired_count[fi] = int(mask.sum())

        if ph == 1 and t > T_CAL * 0.5 and sample["calibration"] is None:
            sample["calibration"] = dict(residual=np.abs(residual).copy())
        elif ph == 2 and sample["self-test"] is None:
            sample["self-test"] = dict(residual=np.abs(residual).copy())
        elif ph == 3:
            # the *first* exafference frame -- captures any transient
            if not exaf_first_done:
                sample["exaf_transient"] = dict(residual=np.abs(residual).copy())
                exaf_first_done = True
            # a steady-state exafference frame ~2 s in
            if t > (T_CAL + T_SELFTEST + 2.0) and sample["exafference"] is None:
                sample["exafference"] = dict(residual=np.abs(residual).copy())
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
    fired_count = fired_count[:fi]; phase = phase[:fi]; eye_log = eye_log[:fi]

    selftest_map = (np.stack(selftest_acc).mean(axis=0)
                    if selftest_acc else np.zeros((PATCH_GRID, PATCH_GRID)))
    exaf_map = (np.stack(exaf_acc).mean(axis=0)
                if exaf_acc else np.zeros((PATCH_GRID, PATCH_GRID)))
    fire_map = (np.stack(exaf_fire_acc).mean(axis=0)
                if exaf_fire_acc else np.zeros((PATCH_GRID, PATCH_GRID)))

    return dict(label=label, condition=condition,
                t=t_frame, mean_res=mean_res, fired=fired_count,
                phase=phase, eye_yaw=eye_log,
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
    )


def plot_row(fig, gs_row, log, stats):
    t = log["t"]; ph = log["phase"]
    phases = [(1, "calibration", "#eef3ff"),
              (2, "self-test", "#e8f7e8"),
              (3, "exafference", "#fde8e8"),
              (4, "post", "#f2f2f2")]

    ax_time = fig.add_subplot(gs_row[0])
    ax_fire = fig.add_subplot(gs_row[1])
    ax_frame = fig.add_subplot(gs_row[2])

    for p, label, color in phases:
        m = ph == p
        if m.any():
            ax_time.axvspan(t[m][0], t[m][-1], color=color, alpha=0.7, lw=0)
            ax_time.text(t[m].mean(), 0.02, label, ha="center", va="bottom",
                         transform=ax_time.get_xaxis_transform(),
                         fontsize=7, color="#555")
    ax_time.plot(t, log["mean_res"], lw=0.7, color="#333")
    if log["floor"] is not None:
        ax_time.axhline(float(np.median(log["floor"])), color="#888", ls=":",
                        lw=0.8)
    ax_time.set_xlabel("time (s)"); ax_time.set_ylabel("mean |residual|")
    ax_time.set_title(
        f"{log['label']}: "
        f"selftest fire = {stats['fired_selftest_frac']:.3f},  "
        f"exaf fire = {stats['fired_exaf_frac']:.3f}  "
        f"(×{stats['fire_ratio']:.1f})", fontsize=10)
    ax_time.grid(alpha=0.25)

    im = ax_fire.imshow(log["fire_map"], vmin=0, vmax=1, cmap="Reds",
                        origin="upper")
    ax_fire.set_xticks([]); ax_fire.set_yticks([])
    ax_fire.set_title("exafference: fire-fraction", fontsize=9)
    fig.colorbar(im, ax=ax_fire, fraction=0.046, pad=0.04)

    # show transient if present (condition C), otherwise steady-state
    s = log["sample"].get("exaf_transient") or log["sample"].get("exafference")
    if s is not None:
        im = ax_frame.imshow(s["residual"], cmap="magma", origin="upper")
        fig.colorbar(im, ax=ax_frame, fraction=0.046, pad=0.04)
    ax_frame.set_xticks([]); ax_frame.set_yticks([])
    label = ("transient |frame − predicted|" if log["sample"].get("exaf_transient") is not None
             and log["condition"] == "hidden-then-static"
             else "exafference |frame − predicted|")
    ax_frame.set_title(label, fontsize=9)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    print("\n=== P1-visual / static-world variant: only agent-side modulation ===")
    configs = [
        ("always-static",          "A. cylinder visible-static throughout"),
        ("visible-then-oscillating", "B. visible-static → oscillating during exafference"),
        ("hidden-then-static",     "C. hidden → visible-static during exafference"),
    ]
    runs = [run(cond, label) for cond, label in configs]
    for r in runs:
        s = summarize(r)
        print(f"  {r['label']:50s}: "
              f"selftest fire = {s['fired_selftest_frac']:.3f}  "
              f"exaf fire = {s['fired_exaf_frac']:.3f}  ×{s['fire_ratio']:.1f}")

    fig = plt.figure(figsize=(13, 11))
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1],
                          width_ratios=[2.5, 1.0, 1.1],
                          hspace=0.55, wspace=0.30)
    for i, r in enumerate(runs):
        plot_row(fig, [gs[i, c] for c in range(3)], r, summarize(r))

    fig.suptitle("P1-visual / static-world — only agent-side modulation.\n"
                 "A: cylinder visible-static throughout. "
                 "B: cylinder static → oscillating in exafference. "
                 "C: cylinder hidden → visible-static in exafference. "
                 "The modulator is a change-detector: it fires under world motion (B), "
                 "transiently under appearance (C), and never under static presence (A).",
                 fontsize=10, y=0.995)
    out = os.path.join(figdir, "p1v_static_world.png")
    fig.savefig(out, dpi=120, bbox_inches="tight")
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
