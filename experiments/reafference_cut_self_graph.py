# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""W3 -- the reafference cut, made in the self-graph frame.

This closes the self/world arc. The self-model (topology) was built from movement;
W1 placed a world feature on the self-graph; W2 read the relation between two
features in self-units. W3 asks the question the whole paper is about: when a
zone's reading changes, was it the body that moved, or the world? -- and it
answers it *per node, on the self-graph*.

Mechanism (reafference against the self-model). Each zone knows how its own
reading changes when it moves (a local field gradient g_k learned during
calibration). The self-referred reading removes that self-caused part:

    s_self_k = s_k - g_k . (pos_k - nominal_k)

Its deviation from the calibrated baseline is then the *world-caused* change, and
its profile over the self-graph nodes says *where* on the body the world changed.

Two challenges, one after the other, with the body moving (a systematic sweep +
jitter) throughout:
  self-motion -- source static: the body sweeps toward and away from the source,
                 so raw readings swing a lot. A naive detector (raw deviation from
                 baseline) fires -- a false alarm. The reafferent detector stays
                 silent: the change was self-caused.
  exafference -- a second source fades in at a node: a genuine world change. Both
                 detectors fire; the reafferent one localizes it to the right
                 self-graph node.

Read-outs:
  discriminability -- (detector during exafference) / (detector during self-motion).
                      reafferent >> 1 (separates self from world); naive ~ 1 (cannot).
  localization     -- reafferent deviation peak node vs the true exafference node.

Run:  ../.venv/bin/python reafference_cut_self_graph.py
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
from smn_lab.fields import ScalarField
from smn_lab.worldmodel import zone_xy

DT = 0.002
N_SEG = 8
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
SENSOR_NOISE = 0.01
T_CAL, T_SELF, T_EXAF = 10.0, 10.0, 10.0
SEGLEN = 0.14
SRC_Y = 0.30
A_NODE = 3                              # the standing source (static throughout)
B_NODE = 6                             # the exafference source (fades in during exaf)
SRC_AMP, SRC_SIG = 1.0, 0.24
SWEEP_AMP, SWEEP_HZ = 0.9, 0.15        # systematic whole-body self-motion (a slow sweep)


def node_x(k):
    return -SEGLEN * k


def run():
    rng = np.random.default_rng(0)
    xml = build_crawler_xml(n_seg=N_SEG, joint_stiffness=0.22, joint_damping=0.04,
                            bend_limit_deg=45.0)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    sL = [model.site(f"seg{k}_L").id for k in range(N_SEG)]
    sR = [model.site(f"seg{k}_R").id for k in range(N_SEG)]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    nj = len(aid_p)
    node_idx = np.arange(N_SEG, dtype=float)
    for d in [model.jnt_dofadr[model.joint(n).id] for n in ("slide_x", "slide_y", "yaw")]:
        model.dof_damping[d] = 40.0

    fieldA = ScalarField([(node_x(A_NODE), SRC_Y, SRC_AMP, SRC_SIG)])

    def b_amp(t):                                    # exafference source fades in
        if t < T_CAL + T_SELF:
            return 0.0
        f = (t - (T_CAL + T_SELF)) / T_EXAF
        return SRC_AMP * min(1.0, f / 0.4)           # ramp over the first 40% then hold

    tau = np.zeros(nj); tau_tc, tau_sig = 0.25, 6.0
    nom = np.zeros((N_SEG, 2)); nom_n = 0
    cal = [dict(dp=[], ds=[]) for _ in range(N_SEG)]
    g = np.zeros((N_SEG, 2)); base = np.zeros(N_SEG); base_n = 0
    s_prev = None; pos_prev = None

    log = {k: [] for k in ("t", "phase", "reaf", "naive", "reaf_node", "true_node",
                           "reaf_prof")}
    n_steps = int((T_CAL + T_SELF + T_EXAF) / DT)
    for i in range(n_steps):
        t = i * DT
        field = ScalarField([(node_x(A_NODE), SRC_Y, SRC_AMP, SRC_SIG),
                             (node_x(B_NODE), SRC_Y, b_amp(t), SRC_SIG)])
        # systematic self-motion: a slow common bend + OU jitter
        sweep = SWEEP_AMP * np.sin(2 * np.pi * SWEEP_HZ * t)
        tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
        for k in range(nj):
            u = tau[k] + sweep
            data.ctrl[aid_p[k]] = float(np.clip(u, 0.0, 2.5))
            data.ctrl[aid_n[k]] = float(np.clip(-u, 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)

        pos = np.array([zone_xy(data, sL, sR, k) for k in range(N_SEG)])
        s = np.array([field.sample(*pos[k]) for k in range(N_SEG)]) \
            + rng.normal(0.0, SENSOR_NOISE, N_SEG)

        if t < T_CAL:                                 # learn g_k, nominal, baseline
            nom = (nom * nom_n + pos) / (nom_n + 1); nom_n += 1
            if s_prev is not None:
                for k in range(N_SEG):
                    cal[k]["dp"].append(pos[k] - pos_prev[k]); cal[k]["ds"].append(s[k] - s_prev[k])
            if i == int(T_CAL / DT) - 1:
                for k in range(N_SEG):
                    dp = np.array(cal[k]["dp"]); ds = np.array(cal[k]["ds"])
                    g[k], *_ = np.linalg.lstsq(np.column_stack([dp[:, 0], dp[:, 1]]), ds, rcond=None)
            s_prev, pos_prev = s, pos
            continue

        # baseline: mean self-referred reading over an early settle inside self-motion
        # --8<-- [start:reaff]
        # per-zone reafference: subtract each zone's learned self-term g_k.(pos-nom)
        s_self = s - np.einsum("kd,kd->k", g, pos - nom)
        if t < T_CAL + 2.0:
            base = (base * base_n + s_self) / (base_n + 1); base_n += 1

        reaf_dev = s_self - base                       # world-caused change, per node
        naive_dev = s - base                           # raw deviation (self + world)
        # --8<-- [end:reaff]
        phase = 1 if t < T_CAL + T_SELF else 2
        # localize the world change on the self-graph (positive-deviation centroid)
        w = np.clip(reaf_dev, 0.0, None)
        rnode = float((w * node_idx).sum() / w.sum()) if w.sum() > 1e-6 else float("nan")
        true_node = A_NODE if phase == 1 else B_NODE

        log["t"].append(t); log["phase"].append(phase)
        log["reaf"].append(float(np.mean(np.abs(reaf_dev))))
        log["naive"].append(float(np.mean(np.abs(naive_dev))))
        log["reaf_node"].append(rnode); log["true_node"].append(true_node)
        log["reaf_prof"].append(reaf_dev.copy())
        s_prev, pos_prev = s, pos

    for k in log:
        log[k] = np.array(log[k])
    return log


def main():
    log = run()
    m1 = log["phase"] == 1; m2 = log["phase"] == 2
    # steady exafference = second half of the exaf window (after the ramp)
    t2 = log["t"][m2]; steady = m2 & (log["t"] >= t2[0] + 0.5 * T_EXAF)
    reaf_self, reaf_exaf = log["reaf"][m1].mean(), log["reaf"][steady].mean()
    naive_self, naive_exaf = log["naive"][m1].mean(), log["naive"][steady].mean()
    loc = log["reaf_node"][steady]
    loc_err = float(np.nanmean(np.abs(loc - B_NODE)))

    print(f"\nW3 -- the reafference cut in the self-graph frame ({N_SEG}-seg chain)\n"
          + "=" * 66)
    print(f"{'detector':<16}{'self-motion':<16}{'exafference':<16}{'discriminability':<16}")
    print(f"{'reafferent':<16}{reaf_self:<16.3f}{reaf_exaf:<16.3f}{reaf_exaf/reaf_self:<16.1f}")
    print(f"{'naive':<16}{naive_self:<16.3f}{naive_exaf:<16.3f}{naive_exaf/naive_self:<16.1f}")
    print("=" * 66)
    print(f"reafferent localizes the world change at self-graph node "
          f"{np.nanmean(loc):.1f}  (true {B_NODE}, err {loc_err:.2f})")
    print("Reading: reafferent is ~flat under self-motion and jumps for a real world\n"
          "change; naive fires for both (it mistakes the body's motion for the world).\n")

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
    ax[0].plot(log["t"], log["naive"], color="tab:orange", alpha=0.7, label="naive (raw deviation)")
    ax[0].plot(log["t"], log["reaf"], color="tab:blue", alpha=0.9, label="reafferent (self-referred)")
    ax[0].axvspan(T_CAL, T_CAL + T_SELF, color="0.92", label="source static (self-motion)")
    ax[0].axvspan(T_CAL + T_SELF, log["t"][-1], color="0.83", label="exafference (world change)")
    ax[0].set_xlabel("time (s)  -- body sweeping throughout")
    ax[0].set_ylabel("change detector  (mean |deviation|)")
    ax[0].set_title("Reafferent cut: silent to self, fires for the world")
    ax[0].legend(fontsize=8, loc="upper left"); ax[0].grid(alpha=0.3)

    prof = np.vstack(log["reaf_prof"]).T             # nodes x time
    im = ax[1].imshow(prof, aspect="auto", origin="lower", cmap="RdBu_r",
                      vmin=-np.abs(prof).max(), vmax=np.abs(prof).max(),
                      extent=[log["t"][0], log["t"][-1], -0.5, N_SEG - 0.5])
    ax[1].axhline(B_NODE, color="k", ls="--", lw=1, alpha=0.7)
    ax[1].axvline(T_CAL + T_SELF, color="k", lw=1, alpha=0.5)
    ax[1].set_xlabel("time (s)"); ax[1].set_ylabel("self-graph node")
    ax[1].set_title("World change localized on the self-graph (node 6)")
    fig.colorbar(im, ax=ax[1], fraction=0.046, label="reafferent deviation")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "reafference_cut_self_graph.png")
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
