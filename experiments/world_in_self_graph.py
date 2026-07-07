# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""W1 -- placing a world feature as a position in the self-graph.

Prerequisite: the self-model. ``self_model_topology.py`` showed the body's
connectivity graph (which zone is how many hops from which) is recovered from
movement alone, locally, with no central reader. This is the first step of the
world model, and it takes the framework's order literally: the world model is
world-geometry expressed *in the self-model's frame*.

Setup. The same elastic chain, base pinned so it deforms in place, bends
naturally beside a single Gaussian field source (a 'where' in the world). Each
zone reads the field at its bilateral sites. We ask: where is the source?

Two ways to answer, and the contrast is the point:

  * self-referred -- report the location as a position on the *self-graph*: the
    reading-weighted centroid of the zone *node indices*. The answer is a node,
    a place in the body's own topology. It needs no external frame.

  * allocentric   -- report the location in absolute *world* coordinates: the
    reading-weighted centroid of the zones' *world positions*. This needs an
    external frame, and it moves whenever the body moves, because the zones
    carry the readings to new places as they bend.

The claim: the self-referred (body-anchored) location is stable while the body
moves and tracks the source when the source moves; the allocentric location is
corrupted by the body's own movement. The world is knowable as geometry-in-the-
self-frame without a God's-eye external frame -- exactly what the framework says.

Phases:
  self-motion  -- source static, body moving: self-referred holds; allocentric drifts.
  world-motion -- source sweeping along the body: self-referred tracks it cleanly.

Run:  ../.venv/bin/python world_in_self_graph.py
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
T_CAL, T_SELF, T_WORLD = 8.0, 12.0, 16.0
SRC_AMP, SRC_SIG = 1.0, 0.26          # a localized Gaussian 'where'
SRC_Y = 0.30                           # offset to one side of the axial chain
SRC_X0, SRC_X1 = -0.20, -0.80          # source sweeps across the body in phase 3
SHARP = 4.0                            # weight sharpening exponent for localization


def zone_xy(data, sL, sR, k):
    return 0.5 * (data.site_xpos[sL[k]][:2] + data.site_xpos[sR[k]][:2])


def weights(readings):
    """Above-baseline, sharpened reading weights (peakier -> less centroid bias)."""
    w = np.clip(readings - readings.min(), 0.0, None)
    if w.max() < 1e-9:
        return np.ones_like(w) / len(w)
    w = (w / w.max()) ** SHARP
    return w / w.sum()


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

    head_dofs = [model.jnt_dofadr[model.joint(n).id] for n in ("slide_x", "slide_y", "yaw")]
    for d in head_dofs:
        model.dof_damping[d] = 40.0            # pin base: body deforms in place

    tau = np.zeros(nj); tau_tc, tau_sig = 0.2, 13.0

    def src_x(t):
        if t < T_CAL + T_SELF:
            return SRC_X0
        f = (t - (T_CAL + T_SELF)) / T_WORLD
        return SRC_X0 + (SRC_X1 - SRC_X0) * f

    nom = np.zeros((N_SEG, 2)); nom_n = 0        # nominal zone positions (from calibration)
    log = {k: [] for k in ("t", "true", "self", "allo", "phase")}
    n_steps = int((T_CAL + T_SELF + T_WORLD) / DT)
    for i in range(n_steps):
        t = i * DT
        field = ScalarField([(src_x(t), SRC_Y, SRC_AMP, SRC_SIG)])
        tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
        for k in range(nj):
            data.ctrl[aid_p[k]] = float(np.clip(tau[k], 0.0, 2.5))
            data.ctrl[aid_n[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)

        pos = np.array([zone_xy(data, sL, sR, k) for k in range(N_SEG)])
        s = np.array([field.sample(*zone_xy(data, sL, sR, k)) for k in range(N_SEG)]) \
            + rng.normal(0.0, SENSOR_NOISE, N_SEG)

        if t < T_CAL:
            nom = (nom * nom_n + pos) / (nom_n + 1); nom_n += 1
            continue

        w = weights(s)
        # self-referred: centroid over self-graph node indices (body-anchored)
        self_node = float((w * node_idx).sum())
        # allocentric: centroid over world x, mapped to nearest nominal node
        allo_x = float((w * pos[:, 0]).sum())
        allo_node = float(np.argmin(np.abs(nom[:, 0] - allo_x)))
        # ground truth: node whose NOMINAL position is nearest the source
        src = np.array([src_x(t), SRC_Y])
        true_node = float(np.argmin(np.linalg.norm(nom - src, axis=1)))

        phase = 1 if t < T_CAL + T_SELF else 2
        log["t"].append(t); log["phase"].append(phase)
        log["true"].append(true_node); log["self"].append(self_node); log["allo"].append(allo_node)

    for k in log:
        log[k] = np.array(log[k])
    return log


def summarize(log):
    out = {}
    for name, ph in (("self-motion", 1), ("world-motion", 2)):
        m = log["phase"] == ph
        true = log["true"][m]
        row = {}
        for est in ("self", "allo"):
            e = log[est][m]
            row[est] = dict(
                err=float(np.mean(np.abs(e - true))),
                jitter=float(np.std(e - true)),
                track=(float(np.corrcoef(e, true)[0, 1]) if true.std() > 1e-6 else float("nan")))
        out[name] = row
    return out


def main():
    log = run()
    S = summarize(log)
    print(f"\nW1 -- world feature located on the self-graph ({N_SEG}-segment chain)\n"
          + "=" * 70)
    for phase, row in S.items():
        moving = "fixed" if phase == "self-motion" else "sweeping"
        print(f"\n[{phase}]  (source {moving})")
        print(f"  {'frame':<24}{'node err':<12}{'jitter':<12}{'tracks source':<14}")
        for est, lbl in (("self", "self-referred (self-graph)"), ("allo", "allocentric (world xy)")):
            r = row[est]
            tr = "n/a" if np.isnan(r["track"]) else f"{r['track']:.2f}"
            print(f"  {lbl:<24}{r['err']:<12.2f}{r['jitter']:<12.2f}{tr:<14}")
    print("\n" + "=" * 70)
    print("Expect: self-motion -> self-referred low err/jitter, allocentric drifts;\n"
          "        world-motion -> self-referred tracks the source (high corr).\n")

    fig, ax = plt.subplots(figsize=(10, 4.3))
    ax.plot(log["t"], log["true"], "k-", lw=2.6, label="true (nearest node)")
    ax.plot(log["t"], log["allo"], color="tab:orange", alpha=0.65, label="allocentric (world xy)")
    ax.plot(log["t"], log["self"], color="tab:blue", alpha=0.95, label="self-referred (self-graph)")
    ax.axvspan(T_CAL, T_CAL + T_SELF, color="0.92", label="source static (self-motion)")
    ax.axvspan(T_CAL + T_SELF, log["t"][-1], color="0.83", label="source sweeping (world-motion)")
    ax.set_xlabel("time (s)"); ax.set_ylabel("feature location  (self-graph node)")
    ax.set_title("W1: the world feature located on the self-graph")
    ax.legend(loc="upper right", fontsize=8, ncol=2); ax.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "world_in_self_graph.png")
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
