# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P0-visual -- Register 3 (reafference: self vs world) at the visual level.

Same architecture, same phase structure, same residual-time-series shape as
``p0_reafference.py``; the **transducer** changes from a single rangefinder
whisker to a forward-facing camera, and the forward model changes from a
heading-keyed binned predictor of range to an analytical predictor of the next
frame from the current frame plus the agent's own yaw rate.

The eye is **minimal by design**: one undifferentiated camera, one flat 8×8
patch modulator. In SMN, perceptual resolution is a function of CAZ density on
the eye itself plus the agent's internal capacities (see ``smn_lab/vision.py``);
the camera's pixel count is a bandwidth placeholder. The whole point of the
experiment is to show that the reafference register survives the lift from 1
rangefinder reading to 64 patch tokens, *with the modulator gating unmodulated
input by default*.

Three phases mirror ``p0_reafference.py``:

  * CALIBRATION  -- agent sweeps in a static world; the modulator stores the
    per-patch residual magnitudes observed.
  * SELF-TEST    -- modulator frozen, world still static; mean residual sits
    at the floor; no patch fires.
  * EXAFFERENCE  -- modulator frozen; an object the agent did not move slides
    into view and oscillates; the patches covering its silhouette break the
    floor.

Outputs ``figures/p0_visual.png`` and prints summary stats.

Run:  ../.venv/bin/python p0_visual.py        (from this directory)
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.model import build_p0v_xml
from smn_lab.control import OpponentBoard
from smn_lab.vision import (EyeCamera, AnalyticalFramePredictor,
                            PatchResidualModulator)

# ---- physics + sweep parameters ------------------------------------------
SEED = 7
DT = 0.005                  # physics timestep (s)
RENDER_EVERY = 4            # render every N physics steps -> 50 Hz vision
SWEEP_AMP = 0.55            # rad (~31 deg) head sweep
SWEEP_F = 0.45              # Hz

# ---- camera + modulator parameters ---------------------------------------
FRAME = 128                 # camera width = height (pixels)
FOV_DEG = 90.0              # camera horizontal FOV
PATCH_GRID = 8              # 8x8 = 64 perceptual tokens per frame

# ---- world schedule -------------------------------------------------------
OBJ_HIDDEN = 3.0            # hidden behind +x wall (out of view)
OBJ_X_MEAN = 0.7            # exafference: object oscillates around this
OBJ_X_AMP = 0.25            # exafference oscillation amplitude (m)
OBJ_F = 0.5                 # exafference oscillation frequency (Hz)

T_CAL = 12.0                # calibration phase (learn noise floor)
T_SELFTEST = 8.0            # self-test (modulator frozen, world static)
T_EXAF = 10.0               # exafference (object oscillating)
T_POST = 3.0                # object removed
T_END = T_CAL + T_SELFTEST + T_EXAF + T_POST


def run():
    model = mujoco.MjModel.from_xml_string(build_p0v_xml(fov_deg=FOV_DEG))
    data = mujoco.MjData(model)

    aid_r = model.actuator("m_right").id
    aid_l = model.actuator("m_left").id
    yaw_jid = model.joint("yaw").id
    obj_jid = model.joint("obj_slide").id
    yaw_qadr = model.jnt_qposadr[yaw_jid]
    yaw_vadr = model.jnt_dofadr[yaw_jid]
    obj_qadr = model.jnt_qposadr[obj_jid]

    board = OpponentBoard(kp=3.0, kd=0.3, cmax=1.5)
    eye = EyeCamera(model, camera_name="eye", width=FRAME, height=FRAME)
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
    selftest_acc = []
    exaf_acc = []
    exaf_fire_acc = []
    # representative frames for the figure
    sample_frames = {"calibration": None, "self-test": None, "exafference": None}

    prev_frame = None
    prev_yaw = 0.0
    w_sweep = 2 * np.pi * SWEEP_F
    fi = 0

    for k in range(n_steps):
        t = k * DT
        theta = float(data.qpos[yaw_qadr])
        theta_dot = float(data.qvel[yaw_vadr])

        # self-generated sweep (efference)
        theta_cmd = SWEEP_AMP * np.sin(w_sweep * t)
        theta_dot_cmd = SWEEP_AMP * w_sweep * np.cos(w_sweep * t)
        a_r, a_l, _ = board.commands(theta, theta_dot, theta_cmd, theta_dot_cmd)
        data.ctrl[aid_r] = a_r
        data.ctrl[aid_l] = a_l

        # world schedule
        in_exaf = (T_CAL + T_SELFTEST) <= t < (T_CAL + T_SELFTEST + T_EXAF)
        if in_exaf:
            t_in_exaf = t - (T_CAL + T_SELFTEST)
            data.qpos[obj_qadr] = OBJ_X_MEAN + OBJ_X_AMP * np.sin(
                2 * np.pi * OBJ_F * t_in_exaf)
        else:
            data.qpos[obj_qadr] = OBJ_HIDDEN

        mujoco.mj_step(model, data)

        if (k + 1) % RENDER_EVERY != 0:
            continue

        frame = eye.snap(data)
        yaw_now = float(data.qpos[yaw_qadr])

        if prev_frame is None:
            prev_frame = frame
            prev_yaw = yaw_now
            t_frame[fi] = t
            phase[fi] = 0
            fi += 1
            continue

        # Δθ between the two frames drives the analytical predictor — taken
        # from the joint position, so it captures whatever rotation actually
        # happened in the render interval (no need to integrate the rate).
        delta_theta = yaw_now - prev_yaw
        predicted = predictor.predict(prev_frame, delta_theta)
        residual = frame - predicted

        # phase
        if t < T_CAL:
            ph = 1
            pooled = modulator.calibrate(residual)
            mask = None
        elif t < T_CAL + T_SELFTEST:
            ph = 2
            if modulator.floor is None:
                modulator.finalize()
            pooled, mask = modulator.gate(residual)
        elif in_exaf:
            ph = 3
            if modulator.floor is None:
                modulator.finalize()
            pooled, mask = modulator.gate(residual)
        else:
            ph = 4
            if modulator.floor is None:
                modulator.finalize()
            pooled, mask = modulator.gate(residual)

        t_frame[fi] = t
        mean_res[fi] = float(pooled.mean())
        phase[fi] = ph
        if mask is not None:
            fired_count[fi] = int(mask.sum())
        # record one representative sample per phase (mid-window)
        for name, m in [("calibration", ph == 1 and t > T_CAL * 0.5 and sample_frames["calibration"] is None),
                        ("self-test", ph == 2 and sample_frames["self-test"] is None),
                        ("exafference", ph == 3 and t > (T_CAL + T_SELFTEST + 2.0) and sample_frames["exafference"] is None)]:
            if m:
                sample_frames[name] = dict(frame=frame.copy(), predicted=predicted.copy(),
                                           residual=np.abs(residual).copy())
        # per-phase pooled accumulation for heatmaps
        if ph == 2:
            selftest_acc.append(pooled)
        elif ph == 3:
            exaf_acc.append(pooled)
            if mask is not None:
                exaf_fire_acc.append(mask.astype(np.float32))

        prev_frame = frame
        prev_yaw = yaw_now
        fi += 1

    eye.close()

    t_frame = t_frame[:fi]; mean_res = mean_res[:fi]
    fired_count = fired_count[:fi]; phase = phase[:fi]

    selftest_map = (np.stack(selftest_acc).mean(axis=0)
                    if selftest_acc else np.zeros((PATCH_GRID, PATCH_GRID)))
    exaf_map = (np.stack(exaf_acc).mean(axis=0)
                if exaf_acc else np.zeros((PATCH_GRID, PATCH_GRID)))
    fire_map = (np.stack(exaf_fire_acc).mean(axis=0)
                if exaf_fire_acc else np.zeros((PATCH_GRID, PATCH_GRID)))

    return dict(t=t_frame, mean_res=mean_res, fired=fired_count, phase=phase,
                floor=modulator.floor.copy() if modulator.floor is not None else None,
                selftest_map=selftest_map, exaf_map=exaf_map, fire_map=fire_map,
                sample_frames=sample_frames)


def summarize(log):
    res = log["mean_res"]; ph = log["phase"]
    selftest = res[ph == 2]; exaf = res[ph == 3]
    n_tokens = PATCH_GRID * PATCH_GRID
    return dict(
        selftest_mean=float(selftest.mean()) if len(selftest) else float("nan"),
        exaf_mean=float(exaf.mean()) if len(exaf) else float("nan"),
        exaf_max=float(exaf.max()) if len(exaf) else float("nan"),
        ratio_mean=(float(exaf.mean() / max(selftest.mean(), 1e-9))
                    if len(selftest) and len(exaf) else float("nan")),
        floor_median=float(np.median(log["floor"])) if log["floor"] is not None else float("nan"),
        fired_selftest_frac=(float(log["fired"][ph == 2].mean()) / n_tokens
                             if (ph == 2).any() else float("nan")),
        fired_exaf_frac=(float(log["fired"][ph == 3].mean()) / n_tokens
                         if (ph == 3).any() else float("nan")),
    )


def plot(log, stats, out):
    t = log["t"]; ph = log["phase"]
    phases = [(1, "calibration", "#eef3ff"),
              (2, "self-test", "#e8f7e8"),
              (3, "exafference", "#fde8e8"),
              (4, "post", "#f2f2f2")]

    fig = plt.figure(figsize=(12, 8.5))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.0, 0.85, 0.85])
    ax_time = fig.add_subplot(gs[0, :])
    ax_self_h = fig.add_subplot(gs[1, 0])
    ax_exaf_h = fig.add_subplot(gs[1, 1])
    ax_fire_h = fig.add_subplot(gs[1, 2])
    ax_cal_f = fig.add_subplot(gs[2, 0])
    ax_self_f = fig.add_subplot(gs[2, 1])
    ax_exaf_f = fig.add_subplot(gs[2, 2])

    # top: residual time series, phases shaded
    for p, label, color in phases:
        m = ph == p
        if m.any():
            ax_time.axvspan(t[m][0], t[m][-1], color=color, alpha=0.7, lw=0)
            ax_time.text(t[m].mean(), 0.02, label, ha="center", va="bottom",
                         transform=ax_time.get_xaxis_transform(),
                         fontsize=8, color="#555")
    ax_time.plot(t, log["mean_res"], lw=0.7, color="#333",
                 label="mean per-patch |residual|")
    if log["floor"] is not None:
        ax_time.axhline(float(np.median(log["floor"])), color="#888", ls=":",
                        lw=0.8,
                        label=f"median noise floor ({float(np.median(log['floor'])):.2f} intensity)")
    ax_time.set_xlabel("time (s)")
    ax_time.set_ylabel("mean per-patch |residual|")
    ax_time.set_title("P0-visual — Register 3 (reafference) at the visual level "
                      f"(8×8 = {PATCH_GRID*PATCH_GRID} perceptual tokens)")
    ax_time.legend(loc="upper left", fontsize=8)
    ax_time.grid(alpha=0.25)

    # middle row: per-phase residual maps
    vmax = max(log["selftest_map"].max(), log["exaf_map"].max(), 1e-3)
    for ax, mp, title in [(ax_self_h, log["selftest_map"], "self-test ⟨|residual|⟩"),
                          (ax_exaf_h, log["exaf_map"], "exafference ⟨|residual|⟩")]:
        im = ax.imshow(mp, vmin=0, vmax=vmax, cmap="magma", origin="upper")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    im = ax_fire_h.imshow(log["fire_map"], vmin=0, vmax=1, cmap="Reds",
                          origin="upper")
    ax_fire_h.set_xticks([]); ax_fire_h.set_yticks([])
    ax_fire_h.set_title("exafference: fraction of frames patch fires",
                        fontsize=10)
    fig.colorbar(im, ax=ax_fire_h, fraction=0.046, pad=0.04)

    # bottom row: representative absolute-residual frames (per phase)
    for ax, name in [(ax_cal_f, "calibration"),
                     (ax_self_f, "self-test"),
                     (ax_exaf_f, "exafference")]:
        s = log["sample_frames"].get(name)
        if s is not None:
            im = ax.imshow(s["residual"], cmap="magma", origin="upper")
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{name}: |frame − predicted|", fontsize=10)

    cap = (f"self-test: mean |res| = {stats['selftest_mean']:.2f}, "
           f"floor median = {stats['floor_median']:.2f}, "
           f"fire-frac = {stats['fired_selftest_frac']:.3f}   |   "
           f"exafference: mean |res| = {stats['exaf_mean']:.2f} "
           f"(×{stats['ratio_mean']:.1f}), fire-frac = {stats['fired_exaf_frac']:.3f}")
    fig.text(0.5, 0.005, cap, ha="center", fontsize=9, color="#333")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    print("\n=== P0-visual: Register 3 (reafference) at the visual level ===")
    log = run()
    stats = summarize(log)
    for k, v in stats.items():
        print(f"  {k:24s} {v:.4f}")
    # The architectural claim is "self-caused change cancels, world-caused
    # change does not". The pertinent contrast is the *fire-fraction* —
    # how many patches break the per-patch floor — between phases, not the
    # mean residual over all 64 patches (most patches see no object at all).
    fire_ratio = (stats["fired_exaf_frac"]
                  / max(stats["fired_selftest_frac"], 1e-3))
    verdict = ("PASS: self-caused change cancels (almost no patch fires "
               "above its per-patch floor); world-caused change does not "
               f"(fire-fraction ×{fire_ratio:.1f} above self-test)."
               if fire_ratio > 2.5
               and stats["fired_exaf_frac"] > 0.05
               and stats["fired_selftest_frac"] < 0.10
               else f"INCONCLUSIVE (fire-fraction ratio ×{fire_ratio:.1f}) — tune.")
    print("  verdict:", verdict)
    plot(log, stats, os.path.join(figdir, "p0_visual.png"))
