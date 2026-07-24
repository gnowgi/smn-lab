# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Complex body: independent subsystems restore the self-model during behaviour.

[self_model_babble_behave.py] showed the self-model read-out collapses under the
single coordinated beam wave: one oscillator driving every zone makes
|corr(efference_i, motion_j)| track command PHASE, not mechanical distance. GN's
prediction: that collapse is a property of a SIMPLE single-chain body. A complex body
has independent subsystems (tubes, sheets, spindles; a fly's wings running one pattern
while the trunk runs another), so it can behave in several parts at once WITHOUT one
global rhythm hiding the body.

Test (morphology held fixed at an 8-segment chain, only the DRIVE varies): partition
the zones into K contiguous subsystems, each driven by its own beam. Sweep K and ask
whether the self-model returns.

  - `diff`: each subsystem runs at its own (random) frequency -> temporally incoherent
    across the body.
  - `same`: each subsystem runs at the SAME 0.9 Hz -> the control that isolates WHY:
    is it the partition, or the incoherence?
  - `ou`: independent OU torque per zone -> the babbling ceiling.

Result (chance neighbour-accuracy = 2/n = 0.25 for the 8-seg chain):
  * `diff` traces an INVERTED-U: 0.29 (K=1, the collapse) -> ~0.95 (K=3) -> back to
    chance as subsystems shrink to single low-SNR oscillators. A FEW independently
    tuned subsystems restore the body's topology while behaving.
  * `same` stays at the collapse (~0.29) for all K: partitioning alone does nothing.
    ** It is drive INCOHERENCE (distinct rates), not subsystems per se, that reveals
    the body. ** One global rhythm hides it; several distinct rhythms reveal it.

Reading: the collapse under coordinated locomotion is a simple-single-chain artifact,
as predicted. Complex, multi-rhythm bodies keep the self-model legible during
behaviour -- with an optimal intermediate number of independent subsystems.

NB this varies the DRIVE on a fixed chain to isolate the mechanism (drive coherence).
Whether real branched morphology supplies the same incoherence is the natural
follow-up; not claimed here.

Run:  ../.venv/bin/python self_model_complex_body.py
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
from smn_lab.metrics import curve_vs_hops, neighbour_accuracy

DT = 0.002
N_SEG = 8
T_WARM, T_REC = 4.0, 50.0
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
PROPRIO_NOISE = 0.02
STIFF = 0.6
SEEDS = [1, 2, 3, 4, 5]
KS = [1, 2, 3, 4, 5, 6, 7]
FREQ_BAND = (0.72, 1.08)        # subsystem frequencies drawn here (distinct rhythms)
CHANCE = 2.0 / N_SEG


def _groups(nj, K):
    return [list(g) for g in np.array_split(np.arange(nj), K) if len(g) > 0]


def run_one(mode, K, seed):
    """mode: 'diff' (per-subsystem random freq) | 'same' (all 0.9) | 'ou' (babble)."""
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
    if mode == "ou":
        tau = np.zeros(nj); tau_tc, tau_sig = 0.15, 8.0
    else:
        grps = _groups(nj, K)
        freqs = (np.full(len(grps), 0.9) if mode == "same"
                 else rng.uniform(*FREQ_BAND, len(grps)))
        beams = [MessagingBeam(n_joints=len(g), amp=0.8, freq=float(freqs[gi]),
                               coupling=4.0, turn_gain=0.0) for gi, g in enumerate(grps)]
        boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in ji]
    nw, nr = int(T_WARM / DT), int(T_REC / DT)
    TAU = np.zeros((nr, nj)); VEL = np.zeros((nr, nj))
    for i in range(nw + nr):
        eff = np.zeros(nj)
        if mode == "ou":
            tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
            eff = tau.copy()
            for k in range(nj):
                data.ctrl[ap[k]] = float(np.clip(tau[k], 0.0, 2.5))
                data.ctrl[an[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        else:
            th = np.array([float(data.qpos[q]) for q in jq])
            thd = np.array([float(data.qvel[v]) for v in jv])
            for gi, g in enumerate(grps):
                tc = beams[gi].command(DT, bias=0.0)
                for local, k in enumerate(g):
                    a_r, a_l, _ = boards[k].commands(th[k], thd[k], tc[local], 0.0)
                    data.ctrl[ap[k]] = a_r; data.ctrl[an[k]] = a_l
                    eff[k] = a_r - a_l
        apply_anisotropic_drag(model, data, seg, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i >= nw:
            r = i - nw
            TAU[r] = eff
            VEL[r] = np.array([float(data.qvel[v]) for v in jv]) \
                     + rng.normal(0.0, PROPRIO_NOISE, nj)
    VEL = VEL - VEL.mean(axis=1, keepdims=True)
    C = transfer(TAU, VEL)
    _, g = curve_vs_hops(C)
    return neighbour_accuracy(C), g[:4]


def main():
    diff = {K: [] for K in KS}
    same = {K: [] for K in KS}
    hop = {}                                          # representative hop profiles
    for K in KS:
        for s in SEEDS:
            na, g = run_one("diff", K, s)
            diff[K].append(na)
            if s == SEEDS[0] and K in (1, 3):
                hop[f"K={K}"] = g
            na2, _ = run_one("same", K, s)
            same[K].append(na2)
    ou = [run_one("ou", 0, s) for s in SEEDS]
    ou_na = np.mean([x[0] for x in ou]); hop["babble"] = ou[0][1]

    print(f"\n=== complex body: independent subsystems on an {N_SEG}-seg chain ===")
    print(f"  chance neighbour_acc = 2/{N_SEG} = {CHANCE:.3f}   babble ceiling = {ou_na:.3f}")
    print(f"  {'K':>2}  {'diff-freq':>16}  {'same-freq (ctrl)':>16}")
    for K in KS:
        d = np.array(diff[K]); s = np.array(same[K])
        print(f"  {K:>2}  {d.mean():.3f} ± {d.std():.3f}     {s.mean():.3f} ± {s.std():.3f}")
    peak = max(KS, key=lambda K: np.mean(diff[K]))
    print(f"  peak: K={peak} at {np.mean(diff[peak]):.3f} (vs K=1 collapse "
          f"{np.mean(diff[1]):.3f}); same-freq flat at collapse -> incoherence, not "
          f"partition, is the cause.")

    # ---- figure ----
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 4.6))
    dm = [np.mean(diff[K]) for K in KS]; de = [np.std(diff[K]) for K in KS]
    sm = [np.mean(same[K]) for K in KS]; se = [np.std(same[K]) for K in KS]
    axA.errorbar(KS, dm, yerr=de, fmt="-o", color="#1538a0", capsize=3,
                 label="distinct rhythms (diff freq)")
    axA.errorbar(KS, sm, yerr=se, fmt="-s", color="#b00000", capsize=3,
                 label="same rhythm (control)")
    axA.axhline(CHANCE, ls=":", color="#888", label=f"chance ({CHANCE:.2f})")
    axA.axhline(ou_na, ls="--", color="#2a8", label=f"babble ceiling ({ou_na:.2f})")
    axA.set_xlabel("independent subsystems  K"); axA.set_ylabel("neighbour accuracy")
    axA.set_ylim(0, 1.05); axA.set_xticks(KS)
    axA.set_title("A — a few distinctly-tuned subsystems restore the self-model\n"
                  "(behaving, 8-seg chain); same-rhythm partition does not", fontsize=9.5)
    axA.legend(fontsize=7, loc="upper right")

    for lab, c, mk in (("K=1", "#b00000", "-s"), ("K=3", "#1538a0", "-o"),
                       ("babble", "#2a8", "-^")):
        if lab in hop:
            axB.plot(range(1, len(hop[lab]) + 1), hop[lab], mk, color=c, label=lab)
    axB.set_xlabel("hop distance"); axB.set_ylabel("mean |G|")
    axB.set_xticks(range(1, 5))
    axB.set_title("B — hop profile: K=1 flat (reads command),\n"
                  "K=3 & babble decay (read the body)", fontsize=9.5)
    axB.legend(fontsize=8)

    fig.suptitle(f"Independent subsystems restore the self-model during behaviour "
                 f"(chance = 2/{N_SEG} = {CHANCE:.2f})", fontsize=11)
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "self_model_complex_body.png")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out, dpi=130); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
