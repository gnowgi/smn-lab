# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Field-scale control for the S1 world-model null.

S1 (sweep_geometry_worldmodel.py) found decoding skill FLAT in segment count and
read it as consistent with the SMN resolution principle (resolution = CAZ density,
not transducer count). But there is a mundane competing explanation: the S1 field's
spatial scale (sigma ~ 0.8-0.9 m) is far larger than the body (~0.2 m), so every
segment reads a nearly identical value -- extra segments add almost no INDEPENDENT
information whatever the theory says. The two explanations make the same flat
prediction under a large-sigma field, so S1 cannot separate them.

This control repeats the sweep under a BODY-SCALE field (small sigma, tiled so the
body always spans a gradient), where segments genuinely read different values:
  - if skill STILL does not rise with n_seg -> the resolution-principle reading (1)
    survives;
  - if skill RISES with n_seg under the body-scale field -> the S1 null was the
    field-geometry artifact (2), and should not be cited as evidence for (1).

We report the contrast; we do not tune to a preferred outcome.

Run:  ../.venv/bin/python sweep_geometry_worldmodel_fieldscale.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import mujoco
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag
from smn_lab.control import OpponentBoard, MessagingBeam
from smn_lab.fields import ScalarField
from smn_lab.metrics import decoding_skill as _knn_skill

DT = 0.002
T_END = 75.0             # match S1's coverage/sample budget for a clean-enough signal
LOG_EVERY = 25
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
N_SEGS = [3, 5, 9]
SEEDS = list(range(8))
STEER_TAU, STEER_SD, STEER_GAIN = 2.5, 1.6, 0.6

# The original S1 world: 3 broad sources, sigma ~ 0.8 m >> body.
FIELD_LARGE = ScalarField([(1.6, 1.1, 1.0, 0.8), (-1.4, 0.9, 0.9, 0.9),
                           (0.2, -1.6, 1.1, 0.7)])

def _bodyscale_field(sigma=0.22, n_fine=48, half=2.2, seed=0):
    """A DECODABLE body-scale field. A periodic grid would alias position (the first
    attempt at this control did exactly that and read ~shuffle, undecodable). So we
    keep the three broad S1 sources -- which make absolute position globally
    recoverable -- and ADD an aperiodic scatter of narrow Gaussians (sigma ~ body
    length) that give body-scale texture: different segments then read different
    values, and extra segments sample independent local gradient. Aperiodic (rng
    placement) avoids aliasing; deterministic seed keeps it fixed across runs."""
    rng = np.random.default_rng(seed)
    srcs = [(1.6, 1.1, 1.0, 0.8), (-1.4, 0.9, 0.9, 0.9), (0.2, -1.6, 1.1, 0.7)]
    for _ in range(n_fine):
        x, y = rng.uniform(-half, half, 2)
        amp = rng.uniform(0.5, 1.0) * (1.0 if rng.random() < 0.5 else -1.0)
        srcs.append((float(x), float(y), float(amp), sigma))
    return ScalarField(srcs)

FIELD_BODY = _bodyscale_field()
FIELDS = {"large_sigma (~0.85 m, original S1)": FIELD_LARGE,
          "body_scale (broad + fine texture, ~0.22 m)": FIELD_BODY}


def run_one(field, n_seg, seed):
    N = int(n_seg)
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N))
    data = mujoco.MjData(model)
    seg_ids = [model.body(f"seg{k}").id for k in range(N)]
    sL = [model.site(f"seg{k}_L").id for k in range(N)]
    sR = [model.site(f"seg{k}_R").id for k in range(N)]
    j_ids = [model.joint(f"j{k}").id for k in range(1, N)]
    j_qadr = [model.jnt_qposadr[j] for j in j_ids]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N)]
    beam = MessagingBeam(n_joints=N - 1, amp=0.8, freq=0.9, coupling=4.0, turn_gain=0.0)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]
    mujoco.mj_forward(model, data)
    steer = 0.0
    Xs, Ys, Ss = [], [], []
    for i in range(int(T_END / DT)):
        steer += (-steer / STEER_TAU) * DT + STEER_SD * np.sqrt(DT) * rng.normal()
        theta_cmd = beam.command(DT, bias=0.0)
        theta_cmd[0] += STEER_GAIN * np.clip(steer, -1.5, 1.5)
        for k in range(len(j_ids)):
            th, thd = float(data.qpos[j_qadr[k]]), float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]], data.ctrl[aid_n[k]] = a_r, a_l
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i % LOG_EVERY == 0:
            hx, hy = data.xpos[seg_ids[0]][:2]
            S = [field.sample(*data.site_xpos[sL[k]][:2]) for k in range(N)] + \
                [field.sample(*data.site_xpos[sR[k]][:2]) for k in range(N)]
            Xs.append(hx); Ys.append(hy); Ss.append(S)
    S = np.array(Ss); P = np.column_stack([Xs, Ys])
    rng2 = np.random.default_rng(1000 + seed)
    return _knn_skill(S, P, rng2, shuffle=False), _knn_skill(S, P, rng2, shuffle=True)


def main():
    rows = {name: {N: [] for N in N_SEGS} for name in FIELDS}
    shuf = {name: [] for name in FIELDS}
    for name, field in FIELDS.items():
        print(f"=== {name} ===")
        for N in N_SEGS:
            for s in SEEDS:
                sk, sh = run_one(field, N, s)
                rows[name][N].append(sk); shuf[name].append(sh)
            m = np.mean(rows[name][N])
            print(f"   n_seg={N}: skill {m:.3f} ± {np.std(rows[name][N]):.3f}")

    # order parameter: slope of skill vs n_seg (does more body add decodable world?)
    def slope(name):
        x = np.array(N_SEGS, float)
        y = np.array([np.mean(rows[name][N]) for N in N_SEGS])
        return np.polyfit(x, y, 1)[0]
    s_large = slope(list(FIELDS)[0]); s_body = slope(list(FIELDS)[1])
    print(f"\nskill-vs-n_seg slope:  large-sigma {s_large:+.4f}   body-scale {s_body:+.4f}")
    RISE = 0.010                       # a rise of >0.01 skill per segment counts
    if s_body > RISE and s_large <= RISE:
        verdict = ("ARTIFACT: skill rises with n_seg under a body-scale field but not "
                   "the large-sigma one -> the S1 flat-null was field geometry, not the "
                   "resolution principle. Do not cite S1 as evidence for it.")
    elif s_body <= RISE:
        verdict = ("RESOLUTION-PRINCIPLE SURVIVES: skill stays flat in n_seg even under a "
                   "body-scale field, so the S1 null is not merely a field-geometry artifact.")
    else:
        verdict = "INCONCLUSIVE: both slopes above threshold; see numbers."
    print("verdict:", verdict)

    _plot(rows, shuf, s_large, s_body)


def _plot(rows, shuf, s_large, s_body):
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for name, marker in zip(FIELDS, ("-o", "-s")):
        y = [np.mean(rows[name][N]) for N in N_SEGS]
        e = [np.std(rows[name][N]) for N in N_SEGS]
        ax.errorbar(N_SEGS, y, yerr=e, fmt=marker, capsize=3, label=name)
    sh = np.mean([v for vv in shuf.values() for v in vv])
    ax.axhline(sh, ls="--", color="0.6", lw=1, label=f"shuffle control (~{sh:.2f})")
    ax.set_xlabel("segment count  (n_seg)"); ax.set_ylabel("held-out decoding skill")
    ax.set_xticks(N_SEGS)
    ax.set_title("Field-scale control for the S1 world-model null\n"
                 f"slope vs n_seg: large-sigma {s_large:+.3f}, body-scale {s_body:+.3f}",
                 fontsize=10)
    ax.legend(fontsize=8)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "sweep_geometry_worldmodel_fieldscale.png")
    fig.savefig(out, dpi=130, bbox_inches="tight"); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
