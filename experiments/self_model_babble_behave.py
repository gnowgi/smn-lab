# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Babble vs behave -- when is the self-model recoverable?

A scientific-accuracy review asked the sharp question: the self-model read-out
(`transfer`/`coupling`) is scored in `self_model_topology.py` under an *independent
OU torque per zone* -- incoherent, exploratory movement. Does it survive the drive
the body was actually built for, the C0 traveling wave?

It does not. Under the coordinated beam, one oscillator drives every zone at fixed
phase offsets, so |corr(efference_i, motion_j)| becomes a function of the two zones'
PHASE DIFFERENCE, not their mechanical hop-distance. The read-out stops seeing the
body and starts seeing the command: neighbour-accuracy falls toward chance and the
hop-profile flattens/inverts (no elastic attenuation).

  Result to record honestly (8-segment chain, one seed):
    babble (OU)  : neighbour_acc 1.00, order 0.89, |G| by hop 0.20/0.08/0.04/0.05 (decays)
    behave (beam): neighbour_acc ~0.29 (chance 2/8=0.25), order ~0.46, |G| flat/inverted

  ** Chance for an n-zone chain is 2/n. ** For the 3-segment crawler (n=2) chance
  neighbour-accuracy is 1.00 -- the metric cannot fail there, so 3-segment self-model
  numbers are uninformative.

Interpretation (GN; a theoretical reading + prediction, NOT shown here):
  - Babbling may be a continuous background (a wake-up / body-schema calibration
    state), so G stays available while behaving. SMN commits to the modulation
    network, not to any one driving regime.
  - The dissociation is a property of a SIMPLE single-chain body. A complex body with
    independent layered subsystems (tubes, sheets, spindles; a fly's wings running a
    BAP while the trunk babbles) can babble in one part while behaving in another.
    ** Prediction: G-recovery-under-behaviour scales with the number of independent
    subsystems. ** (Testable next; not claimed here.)
  - G is for action (cf. Glenberg, "memory is for action"): the model must be stored
    and used. The babble -> behave -> perturb cycle is the build that closes that loop.

Run:  ../.venv/bin/python self_model_babble_behave.py
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
from smn_lab.self_model import transfer
from smn_lab.metrics import (curve_vs_hops, seriation_order, order_accuracy,
                             neighbour_accuracy)

DT = 0.002
N_SEG = 8
T_WARM, T_REC = 4.0, 60.0
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
PROPRIO_NOISE = 0.02
STIFF = 0.6
SEEDS = [1, 2, 3]


def run_one(drive, seed):
    """Log per-zone efference (net commanded torque) and afferent motion under
    either 'babble' (independent OU torque per zone) or 'behave' (the beam wave)."""
    rng = np.random.default_rng(seed)
    xml = build_crawler_xml(n_seg=N_SEG, joint_stiffness=STIFF,
                            joint_damping=0.05, bend_limit_deg=45.0)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    seg = [model.body(f"seg{k}").id for k in range(N_SEG)]
    ji = [model.joint(f"j{k}").id for k in range(1, N_SEG)]
    jq = [model.jnt_qposadr[j] for j in ji]
    jv = [model.jnt_dofadr[j] for j in ji]
    ap = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    an = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    nj = len(ji)
    tau = np.zeros(nj); tau_tc, tau_sig = 0.15, 8.0
    beam = MessagingBeam(n_joints=nj, amp=0.8, freq=0.9, coupling=4.0, turn_gain=0.0)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in ji]
    nw, nr = int(T_WARM / DT), int(T_REC / DT)
    TAU = np.zeros((nr, nj)); VEL = np.zeros((nr, nj))
    for i in range(nw + nr):
        if drive == "babble":
            tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
            eff = tau.copy()
            for k in range(nj):
                data.ctrl[ap[k]] = float(np.clip(tau[k], 0.0, 2.5))
                data.ctrl[an[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        else:                                            # behave: the C0 beam wave
            th = np.array([float(data.qpos[q]) for q in jq])
            thd = np.array([float(data.qvel[v]) for v in jv])
            tc = beam.command(DT, bias=0.0)
            eff = np.zeros(nj)
            for k in range(nj):
                a_r, a_l, _ = boards[k].commands(th[k], thd[k], tc[k], 0.0)
                data.ctrl[ap[k]] = a_r; data.ctrl[an[k]] = a_l
                eff[k] = a_r - a_l                        # net commanded torque
        apply_anisotropic_drag(model, data, seg, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i >= nw:
            r = i - nw
            TAU[r] = eff
            VEL[r] = np.array([float(data.qvel[v]) for v in jv]) \
                     + rng.normal(0.0, PROPRIO_NOISE, nj)
    VEL = VEL - VEL.mean(axis=1, keepdims=True)          # strip whole-body common mode
    C = transfer(TAU, VEL)
    hops, g = curve_vs_hops(C)
    return dict(C=C, hops=hops, g=g,
                nacc=neighbour_accuracy(C),
                oacc=order_accuracy(seriation_order(C)))


def main():
    chance = 2.0 / N_SEG
    agg = {d: {"nacc": [], "oacc": [], "g": []} for d in ("babble", "behave")}
    rep = {}
    for d in ("babble", "behave"):
        for s in SEEDS:
            r = run_one(d, s)
            agg[d]["nacc"].append(r["nacc"]); agg[d]["oacc"].append(r["oacc"])
            agg[d]["g"].append(r["g"][:4])
            if s == SEEDS[0]:
                rep[d] = r
    print(f"\n=== self-model: babble vs behave ({N_SEG}-seg chain, {len(SEEDS)} seeds) ===")
    print(f"  chance neighbour_acc = 2/{N_SEG} = {chance:.3f}")
    for d in ("babble", "behave"):
        na = np.array(agg[d]["nacc"]); oa = np.array(agg[d]["oacc"])
        gm = np.mean(agg[d]["g"], axis=0)
        gs = ", ".join(f"{v:.3f}" for v in gm)
        print(f"  {d:7s}: neighbour_acc {na.mean():.3f}±{na.std():.3f}  "
              f"order_acc {oa.mean():.3f}±{oa.std():.3f}  |G| by hop [{gs}]")
    print("  reading: the self-model is recoverable from EXPLORATORY (babbling) drive; "
          "coordinated locomotion collapses it toward chance (this simple single-chain "
          "body). See the doc for the interpretation + the complex-body prediction.")

    # ---- figure: hop profiles + the two transfer matrices ----
    fig = plt.figure(figsize=(13.5, 4.4))
    gs_ = fig.add_gridspec(1, 3, width_ratios=[1.3, 1, 1], wspace=0.3)
    axP = fig.add_subplot(gs_[0, 0])
    for d, c, mk in (("babble", "#1538a0", "-o"), ("behave", "#b00000", "-s")):
        gm = np.mean(agg[d]["g"], axis=0)
        na = np.mean(agg[d]["nacc"])
        axP.plot(np.arange(1, len(gm) + 1), gm, mk, color=c,
                 label=f"{d} (neighbour_acc {na:.2f})")
    axP.set_xlabel("hop distance along the chain"); axP.set_ylabel("mean |G|")
    axP.set_title("A — |G| vs hop: babble decays (reads the body),\n"
                  "behave is flat (reads the command)", fontsize=9.5)
    axP.legend(fontsize=8); axP.set_xticks(range(1, 5))
    for d, ax_i, ttl in (("babble", 1, "B — babble: adjacency band"),
                         ("behave", 2, "C — behave: no band")):
        ax = fig.add_subplot(gs_[0, ax_i])
        im = ax.imshow(np.abs(rep[d]["C"]), cmap="magma", aspect="equal")
        ax.set_title(ttl, fontsize=9.5)
        ax.set_xlabel("segment"); ax.set_ylabel("joint (zone)")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(f"Self-model needs exploratory movement — {N_SEG}-seg chain "
                 f"(chance neighbour_acc = 2/{N_SEG} = {2/N_SEG:.2f})", fontsize=11)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "self_model_babble_behave.png")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out, dpi=130); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
