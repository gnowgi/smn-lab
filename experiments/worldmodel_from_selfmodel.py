# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Faithful world-model: built on a self-model RECOVERED FROM MOVEMENT (step 1).

This repairs the audit finding that every prior self-frame experiment *assumed* the
self-model (hard-coded node order / true positions). Here the self-model is recovered
inline from the body's own modulation, and the world-feature is localized in THAT
recovered frame -- in relative (ordinal) self-graph units, never metric coordinates.

The architecture-faithful chain (SMN):
  modulation (the body moves) --> self-model (which zone is where, recovered from the
  reafferent correlations of that movement) --> world-model (a world feature localized
  to a position in the recovered self-frame).
Freeze the modulation and the chain must BREAK: no movement -> no recoverable
self-model -> the (placeless) transducer readings cannot be assembled into a world.

Design: one body; a single field source is placed beside it near a swept position
k_src along the body. We ask: does the recovered self-frame location of the source
track its true location? Three conditions isolate the mechanism:
  (1) MOVING + recovered self-model   -- the faithful SMN agent.            expect: tracks
  (2) FROZEN + recovered self-model   -- no modulation -> no self-model.    expect: chance
  (3) FROZEN + TRUE self-model (cheat)-- readings are fine; only the self-  expect: tracks
      model is supplied from outside.
Contrast (1 vs 2): modulation is what builds the self-model. Contrast (2 vs 3, both
frozen): the readings are not the problem -- the missing SELF-MODEL is. Together:
no modulation, no self-model, no world-model.

Order parameter: |rank correlation| between true source position k_src and its
recovered self-frame node, across positions. (Relative, ordinal -- reflection-safe.)

Run:  ../.venv/bin/python worldmodel_from_selfmodel.py
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
from smn_lab.self_model import read_all
from smn_lab.metrics import seriation_order, order_accuracy
from smn_lab.worldmodel import localization_weights
from smn_lab.report import RunRecord, render

DT = 0.002
N_SEG = 8
H = 0.07
SEGLEN = 2 * H
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
T_WARM, T_REC = 3.0, 30.0
SRC_Y, SRC_AMP, SRC_SIG = 0.30, 1.0, 0.24
K_SRC = [1, 2, 3, 4, 5, 6]                 # true source position (segment) swept
SEEDS = [0, 1, 2]


def node_x(k):
    return -SEGLEN * k                      # nominal world-x of segment k (head=0)


def run(k_src, moving, seed):
    """Two phases. PHASE 1 (move or frozen): the body babbles; from its own segment
    co-motion it recovers its self-model (the zone ordering). PHASE 2 (sense): the body
    is reset to a still, straight pose beside the source and reads the field once -- a
    clean world-reading, localized in the self-frame recovered in phase 1. This mirrors
    development: motor babbling builds the body schema, then the world is perceived in
    it. (On a locomoting body the two phases interleave and need reafference -- the
    gravity step.) Returns (order_acc, self_node_recovered, self_node_true)."""
    rng = np.random.default_rng(seed)
    field = ScalarField([(node_x(k_src), SRC_Y, SRC_AMP, SRC_SIG)])
    xml = build_crawler_xml(n_seg=N_SEG, joint_stiffness=0.25, joint_damping=0.04,
                            bend_limit_deg=45.0)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    sL = [model.site(f"seg{k}_L").id for k in range(N_SEG)]
    sR = [model.site(f"seg{k}_R").id for k in range(N_SEG)]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    nj = len(aid_p); vel = np.zeros(6)

    # --- PHASE 1: MOVE -> recover the self-model from segment co-motion ---
    tau = np.zeros(nj)
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    OMEGA = np.zeros((n_rec, N_SEG))
    for i in range(n_warm + n_rec):
        if moving:                                    # MODULATION: independent babbling
            tau += (-tau / 0.15) * DT + 8.0 * np.sqrt(DT) * rng.standard_normal(nj)
            for k in range(nj):
                data.ctrl[aid_p[k]] = float(np.clip(tau[k], 0.0, 2.5))
                data.ctrl[aid_n[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i >= n_warm:
            for s in range(N_SEG):
                mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY,
                                         seg_ids[s], vel, 0)
                OMEGA[i - n_warm, s] = vel[2]
    G = np.abs(read_all(OMEGA, OMEGA)); G = 0.5 * (G + G.T); np.fill_diagonal(G, 0.0)
    order = seriation_order(G)                        # recovered segment ordering
    oacc = order_accuracy(order)
    rec_pos = np.empty(N_SEG); rec_pos[order] = np.arange(N_SEG)
    true_pos = np.arange(N_SEG, dtype=float)

    # --- PHASE 2: SENSE -> reset to a still straight pose, read the world once ---
    data.qpos[:] = 0.0; data.qvel[:] = 0.0; data.ctrl[:] = 0.0
    read_acc = np.zeros(N_SEG)
    for _ in range(200):                              # a brief still read (body does not move)
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        read_acc += [0.5 * (field.sample(*data.site_xpos[sL[s]][:2]) +
                            field.sample(*data.site_xpos[sR[s]][:2])) for s in range(N_SEG)]
    w = localization_weights(read_acc / 200.0)
    # also return the raw arrays the canonical results module needs: the movement
    # trace it recovers the self-model from, and the per-segment world reading.
    return (oacc, float((w * rec_pos).sum()), float((w * true_pos).sum()),
            OMEGA, read_acc / 200.0)


def abs_rankcorr(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return abs(np.corrcoef(rx, ry)[0, 1])


def main():
    # collect per condition, ORGANIZED BY SEED -- tracking is measured WITHIN each
    # agent's own recovered self-frame (frames are not comparable across agents),
    # then averaged. Pooling self_node across seeds would conflate incommensurable frames.
    conds = ("moving+recovered", "frozen+recovered", "frozen+true(cheat)")
    per_seed = {c: {"track": [], "oacc": []} for c in conds}
    scatter = {c: {"k": [], "node": []} for c in conds}          # seed-0 only, for the figure
    rep = {}                                                     # representative run for the card
    for seed in SEEDS:
        nodes = {c: [] for c in conds}; oaccs = {c: [] for c in conds}
        for k in K_SRC:
            oacc_m, node_rec_m, _, omega_m, read_m = run(k, moving=True, seed=seed)
            oacc_f, node_rec_f, node_true_f, _, _ = run(k, moving=False, seed=seed)
            if seed == SEEDS[0] and k == K_SRC[len(K_SRC) // 2]:
                rep = dict(omega=omega_m, read=read_m)          # mid-body source, moving, seed 0
            nodes["moving+recovered"].append(node_rec_m); oaccs["moving+recovered"].append(oacc_m)
            nodes["frozen+recovered"].append(node_rec_f); oaccs["frozen+recovered"].append(oacc_f)
            nodes["frozen+true(cheat)"].append(node_true_f); oaccs["frozen+true(cheat)"].append(oacc_f)
        for c in conds:
            per_seed[c]["track"].append(abs_rankcorr(np.array(K_SRC), np.array(nodes[c])))
            per_seed[c]["oacc"].append(np.mean(oaccs[c]))
            if seed == SEEDS[0]:
                scatter[c]["k"] = list(K_SRC); scatter[c]["node"] = nodes[c]

    print("\nFaithful world-model on a self-model RECOVERED FROM MOVEMENT\n" + "=" * 72)
    print("Order parameter: |rank corr| (source position vs self-frame node), WITHIN each")
    print("agent's own recovered frame, mean +/- sd over seeds.")
    print(f"{'condition':<24}{'self-model order acc':<22}{'world-model tracking':<20}")
    print("-" * 72)
    res = {}
    for c in conds:
        oacc = np.mean(per_seed[c]["oacc"])
        track = np.mean(per_seed[c]["track"]); tsd = np.std(per_seed[c]["track"])
        res[c] = (oacc, track)
        print(f"{c:<24}{oacc:<22.2f}{track:.2f} +/- {tsd:.2f}")
    print("=" * 72)
    mv = res["moving+recovered"][1]; fz = res["frozen+recovered"][1]; ch = res["frozen+true(cheat)"][1]
    print("Reading:")
    print(f"  (1 vs 2) modulation builds the self-model: tracking {mv:.2f} moving vs {fz:.2f} frozen"
          f"  [{'PASS' if mv > 0.7 and fz < 0.4 else 'CHECK'}]")
    print(f"  (2 vs 3) both frozen; readings are fine -- only the SELF-MODEL was missing:"
          f" recovered {fz:.2f} vs true-cheat {ch:.2f}  [{'PASS' if ch > 0.7 else 'CHECK'}]")
    print("  => no modulation -> no self-model -> no world-model. The world-model is built on\n"
          "     a self-model the body EARNS by moving, in relative self-frame units.\n")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    col = {"moving+recovered": "#2c6fbb", "frozen+recovered": "#c0392b", "frozen+true(cheat)": "#7f8c8d"}
    for c in conds:
        ax[0].scatter(scatter[c]["k"], scatter[c]["node"], c=col[c], s=48, alpha=0.85,
                      label=f"{c} (|r|={res[c][1]:.2f})")
    ax[0].set_xlabel("true source position (segment k_src)")
    ax[0].set_ylabel("source's localized self-frame node (seed 0)")
    ax[0].set_title("Does the world-model track the source?\n(within one recovered frame; diagonal = yes)")
    ax[0].legend(fontsize=7.5); ax[0].grid(alpha=0.3)
    oa = [res[c][0] for c in conds]; tk = [res[c][1] for c in conds]
    x = np.arange(len(conds))
    ax[1].bar(x - 0.2, oa, 0.4, label="self-model order accuracy", color="#8e44ad")
    ax[1].bar(x + 0.2, tk, 0.4, label="world-model tracking |r|", color="#27ae60")
    ax[1].set_xticks(x); ax[1].set_xticklabels(conds, rotation=15, ha="right", fontsize=7.5)
    ax[1].set_ylim(0, 1.05); ax[1].set_title("self-model quality drives world-model"); ax[1].legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "worldmodel_from_selfmodel.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")

    # --- canonical results via the ONE always-invoked module ---
    # Hand the recovered-from-movement trace and the per-segment world reading to
    # smn_lab.report: it recovers the self-model graph-first, localizes the source on
    # it (the self/world card), computes emergent diagnostics, and writes the record.
    node_field = {s: float(rep["read"][s]) for s in range(N_SEG)}
    render(RunRecord(name="worldmodel_from_selfmodel",
                     omega=rep["omega"], node_field=node_field, modality="chem",
                     metrics={"order_acc": float(res["moving+recovered"][0]),
                              "tracking": float(res["moving+recovered"][1])},
                     meta={"conditions": {c: {"order_acc": float(res[c][0]),
                                              "tracking": float(res[c][1])} for c in conds}}),
           spec=dict(suptitle="World-model on a self-model recovered from movement"))


if __name__ == "__main__":
    main()
