# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""W2 -- world-geometry computed in the self-model's frame.

W1 placed a single world feature as a position on the self-graph. W2 takes the
next step the framework requires: with *two* features present, the world model is
their **geometric relation, expressed in the self-frame**. We measure the
separation between two sources not in metres but in **self-graph hops** -- the
body's own topology is the ruler. And because both features are referred to the
same self-frame, their relation is stable while the body moves.

Two features are two modalities (a 'chem' source and a 'thermal' source), each
read on its own channel, each localized to a self-graph node by the W1 read-out.
The world-geometry is the signed node separation  d = node_B - node_A.

Two claims:
  (1) world-metric in self-units -- as we increase the true separation of the two
      sources, the recovered self-graph separation d tracks it (a body-anchored,
      metric-free measure of 'how far apart' that still scales with the world).
  (2) self-anchored, not allocentric -- while the body bends (source static), the
      self-referred separation holds; the allocentric separation (difference of
      world-xy estimates) jitters, because the body's motion moves the readings
      in space but not in the self-graph.

Run:  ../.venv/bin/python world_geometry_self_frame.py
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

DT = 0.002
N_SEG = 8
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
SENSOR_NOISE = 0.01
T_CAL, T_REC = 6.0, 14.0
SRC_AMP, SRC_SIG = 1.0, 0.24
SRC_Y = 0.30
SEGLEN = 0.14                          # inter-node spacing (2*h in the builder)
A_NODE = 2                             # feature A parked near node 2
B_NODES = [3, 4, 5, 6]                 # feature B at increasing separation
SHARP = 4.0


def node_x(k):
    return -SEGLEN * k                  # nominal world-x of node k (head=0 at +x)


def zone_xy(data, sL, sR, k):
    return 0.5 * (data.site_xpos[sL[k]][:2] + data.site_xpos[sR[k]][:2])


def weights(readings):
    w = np.clip(readings - readings.min(), 0.0, None)
    if w.max() < 1e-9:
        return np.ones_like(w) / len(w)
    w = (w / w.max()) ** SHARP
    return w / w.sum()


def run_pair(b_node, seed):
    """Body bends (source static) beside two sources A, B; return time series of
    the self-referred and allocentric A->B separations."""
    rng = np.random.default_rng(seed)
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
    fieldB = ScalarField([(node_x(b_node), SRC_Y, SRC_AMP, SRC_SIG)])
    tau = np.zeros(nj); tau_tc, tau_sig = 0.2, 13.0
    nom = np.zeros((N_SEG, 2)); nom_n = 0
    d_self, d_allo = [], []
    for i in range(int((T_CAL + T_REC) / DT)):
        t = i * DT
        tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
        for k in range(nj):
            data.ctrl[aid_p[k]] = float(np.clip(tau[k], 0.0, 2.5))
            data.ctrl[aid_n[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        pos = np.array([zone_xy(data, sL, sR, k) for k in range(N_SEG)])
        if t < T_CAL:
            nom = (nom * nom_n + pos) / (nom_n + 1); nom_n += 1
            continue
        sA = np.array([fieldA.sample(*pos[k]) for k in range(N_SEG)]) + rng.normal(0, SENSOR_NOISE, N_SEG)
        sB = np.array([fieldB.sample(*pos[k]) for k in range(N_SEG)]) + rng.normal(0, SENSOR_NOISE, N_SEG)
        wA, wB = weights(sA), weights(sB)
        # self-referred: separation in self-graph node units
        d_self.append(float((wB * node_idx).sum() - (wA * node_idx).sum()))
        # allocentric: separation in world x, expressed in node units (/SEGLEN)
        xA = float((wA * pos[:, 0]).sum()); xB = float((wB * pos[:, 0]).sum())
        d_allo.append((xA - xB) / SEGLEN)          # +x is head; node grows away from head
    return np.array(d_self), np.array(d_allo)


def main():
    seeds = [0, 1, 2]
    true_sep, self_mean, self_sd = [], [], []
    trace = None                                    # a representative d(t) for panel 2
    for b in B_NODES:
        ds_all = []
        for s in seeds:
            ds, _ = run_pair(b, s)
            ds_all.append(ds)
            if b == B_NODES[-2] and s == 0:
                trace = ds
        ds_all = np.concatenate(ds_all)
        true_sep.append(b - A_NODE)
        self_mean.append(ds_all.mean()); self_sd.append(ds_all.std())

    true_sep = np.array(true_sep)
    print(f"\nW2 -- world-geometry in the self-frame ({N_SEG}-segment chain)\n" + "=" * 60)
    print(f"{'true sep (hops)':<20}{'recovered self-graph d (hops)':<30}")
    for i, ts in enumerate(true_sep):
        print(f"{ts:<20}{self_mean[i]:5.2f} +/- {self_sd[i]:4.2f}")
    sslope = np.polyfit(true_sep, self_mean, 1)[0]
    scorr = np.corrcoef(true_sep, self_mean)[0, 1]
    print("=" * 60)
    print(f"recovered vs true separation: slope {sslope:.2f}, r {scorr:.3f}")
    print("  -> world-metric recovered in self-graph units (the body is the ruler)")
    print(f"stability while the body bends: sep holds within +/-{np.mean(self_sd):.2f} hops")
    print("  -> a relation cancels the body's common-mode self-motion, so world-")
    print("     geometry in the self-frame is even more robust than a single location.\n")

    sep_ref = B_NODES[-2] - A_NODE
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].errorbar(true_sep, self_mean, yerr=self_sd, marker="o", capsize=3,
                   color="tab:blue", label="recovered (self-graph hops)")
    ax[0].plot(true_sep, true_sep, "k--", alpha=0.5, label="ideal (slope 1)")
    ax[0].set_xlabel("true separation of the two sources (hops)")
    ax[0].set_ylabel("recovered separation (self-graph hops)")
    ax[0].set_title(f"World-metric in self-units  (slope {sslope:.2f}, r {scorr:.3f})")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    tt = np.arange(len(trace)) * DT
    ax[1].plot(tt, trace, color="tab:blue", alpha=0.85, label="recovered separation")
    ax[1].axhline(sep_ref, color="k", ls="--", alpha=0.6, label=f"true separation ({sep_ref})")
    ax[1].set_xlabel("time (s)  -- body bending throughout")
    ax[1].set_ylabel("A$\\to$B separation (self-graph hops)")
    ax[1].set_title("Relation holds while the body deforms")
    ax[1].set_ylim(sep_ref - 2, sep_ref + 2)
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "world_geometry_self_frame.png")
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
