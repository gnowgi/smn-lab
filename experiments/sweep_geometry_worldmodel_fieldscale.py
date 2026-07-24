# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Field-scale control for the S1 world-model null -- and why it is INCONCLUSIVE.

S1 (sweep_geometry_worldmodel.py) found held-out decoding skill flat in segment count
and read it as consistent with the resolution principle. The competing explanation is
field geometry: under a large-sigma field every segment reads nearly the same value,
so extra segments add no independent information whatever the theory says. This page
was meant to separate the two with a body-scale field.

** A scientific-accuracy review checked the harness and it does NOT separate them. **
Three confounds, all reproduced below, break the original "resolution survives" verdict:

  1. Decoder dimensionality. The order parameter was the slope of *kNN* skill vs
     n_seg. kNN degrades with state dimension (2*n_seg channels), so it produces a
     NEGATIVE slope even for `broad_only` -- a field that by construction carries NO
     independent per-segment information. A negative slope is thus manufactured by the
     decoder, not the world. A dimension-robust ridge readout puts `broad_only` flat.
  2. Field masking. The "body-scale" field kept the three broad S1 sources "for
     decodability" -- but those dominate the decodable signal and are n_seg-flat, so
     they SWAMP the fine body-scale component whose n_seg-dependence is the whole test.
     Remove/weaken the broad sources (`fine_only`, `weakbroad+fine`) and the ridge
     slope goes POSITIVE: a genuinely body-scale field does show more-body-more-world.
  3. Trajectory noise. Skill is strongly trajectory-dependent -- the curves are
     non-monotone (a dip at n_seg=5 across *all* fields) with wide seed variance
     (+/-0.2..0.6), so a slope at this budget cannot resolve the question.

Conclusion: the control is INCONCLUSIVE and the "resolution-principle survives"
reading is WITHDRAWN. See docs/experiments/sweep_geometry_worldmodel_fieldscale.md.

Run:  ../.venv/bin/python sweep_geometry_worldmodel_fieldscale.py     (~8-10 min)
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
from smn_lab.metrics import decoding_skill as knn_skill, ridge_skill

DT = 0.002
T_END = 75.0
LOG_EVERY = 25
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
N_SEGS = [3, 5, 9]
SEEDS = list(range(8))
STEER_TAU, STEER_SD, STEER_GAIN = 2.5, 1.6, 0.6


def _broad(scale=1.0):
    return [(1.6, 1.1, 1.0 * scale, 0.8), (-1.4, 0.9, 0.9 * scale, 0.9),
            (0.2, -1.6, 1.1 * scale, 0.7)]


def _fine(sigma=0.22, n_fine=48, half=2.2, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_fine):
        x, y = rng.uniform(-half, half, 2)
        amp = rng.uniform(0.5, 1.0) * (1.0 if rng.random() < 0.5 else -1.0)
        out.append((float(x), float(y), float(amp), sigma))
    return out


# broad_only = the original large-sigma S1 field (= a dimensionality control: no
# independent per-segment info). broad+fine = the first version of this control.
# weakbroad+fine = decodable AND not broad-masked (broad only anchors global position).
FIELDS = {
    "broad_only (=S1 large-σ; dim. control)": ScalarField(_broad(1.0)),
    "broad+fine (the first control field)":   ScalarField(_broad(1.0) + _fine()),
    "weakbroad+fine (decodable, unmasked)":   ScalarField(_broad(0.35) + _fine()),
}


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
    return knn_skill(S, P, rng2), ridge_skill(S, P, rng2)


def main():
    knn = {n: {N: [] for N in N_SEGS} for n in FIELDS}
    rdg = {n: {N: [] for N in N_SEGS} for n in FIELDS}
    for name, field in FIELDS.items():
        print(f"=== {name} ===")
        for N in N_SEGS:
            for s in SEEDS:
                a, b = run_one(field, N, s)
                knn[name][N].append(a); rdg[name][N].append(b)
            print(f"   n_seg={N}: kNN {np.mean(knn[name][N]):+.3f}±{np.std(knn[name][N]):.2f}"
                  f"   ridge {np.mean(rdg[name][N]):+.3f}±{np.std(rdg[name][N]):.2f}")

    def slope(d, name):
        return float(np.polyfit(N_SEGS, [np.mean(d[name][N]) for N in N_SEGS], 1)[0])
    names = list(FIELDS)
    print("\nslopes (skill per segment):")
    for n in names:
        print(f"   {n:42s}  kNN {slope(knn,n):+.4f}   ridge {slope(rdg,n):+.4f}")

    print("\nVERDICT: INCONCLUSIVE -- 'resolution survives' WITHDRAWN.")
    print(f"  (1) dim. confound: broad_only kNN slope {slope(knn,names[0]):+.3f} "
          f"(negative for a NO-info field) vs ridge {slope(rdg,names[0]):+.3f} (~flat).")
    print(f"  (2) masking: broad+fine ridge {slope(rdg,names[1]):+.3f} (flat) vs "
          f"weakbroad+fine ridge {slope(rdg,names[2]):+.3f} (positive -> more body helps).")
    print("  (3) trajectory noise: non-monotone (n_seg=5 dip), wide variance.")
    _plot(knn, rdg, slope)


def _plot(knn, rdg, slope):
    fig, (axK, axR) = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for name, mk in zip(FIELDS, ("-o", "-s", "-^")):
        yk = [np.mean(knn[name][N]) for N in N_SEGS]
        ek = [np.std(knn[name][N]) for N in N_SEGS]
        yr = [np.mean(rdg[name][N]) for N in N_SEGS]
        er = [np.std(rdg[name][N]) for N in N_SEGS]
        axK.errorbar(N_SEGS, yk, yerr=ek, fmt=mk, capsize=3,
                     label=f"{name}  (slope {slope(knn,name):+.3f})")
        axR.errorbar(N_SEGS, yr, yerr=er, fmt=mk, capsize=3,
                     label=f"{name}  (slope {slope(rdg,name):+.3f})")
    for ax, t in ((axK, "kNN decoder (dimension-cursed)"),
                  (axR, "ridge decoder (dimension-robust)")):
        ax.axhline(0, ls="--", color="0.6", lw=1)
        ax.set_xlabel("segment count (n_seg)"); ax.set_xticks(N_SEGS)
        ax.set_title(t, fontsize=10); ax.legend(fontsize=7, loc="lower left")
    axK.set_ylabel("held-out decoding skill")
    fig.suptitle("Field-scale control is CONFOUNDED: kNN slope is a dimensionality "
                 "artifact;\nunmasking the body-scale field makes ridge slope positive "
                 "-> 'resolution survives' withdrawn", fontsize=10)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "sweep_geometry_worldmodel_fieldscale.png")
    fig.savefig(out, dpi=130, bbox_inches="tight"); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
