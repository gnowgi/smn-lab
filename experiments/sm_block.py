# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The canonical SM block — H1 (self-model), H2 (no locomotion regression), H3 (exploratory: does the
tendon tell the body about the ground?). Pre-registered in docs/experiments/sm_block.md, including
the addendum fixed before this script was first run. Baselines are the bench's own scripts,
imported and called unchanged.

Run:  ../.venv/bin/python sm_block.py
"""
from __future__ import annotations
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from smn_lab.sm_block import build_sm_chain_xml, SMChain, K_SEE, F_MAX
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag, apply_ground_friction
from smn_lab.control import OpponentBoard, MessagingBeam
from smn_lab.fields import ScalarField
from smn_lab.self_model import transfer
from smn_lab.metrics import seriation_order, order_accuracy, neighbour_accuracy
import self_model_topology as SMT          # the bench's torque-motor self-model, unchanged
import c0_crawler as C0                    # the bench's C0, unchanged
import gravity_locomotion as GL            # the bench's ground crawler, unchanged

DT = 0.002
SEEDS = list(range(5))

# ---------------------------------------------------------------- H1: self-model --------------
H1_CONDITIONS = {                 # k_see, k_pee, drive
    "block":     (K_SEE, 0.6,  True),
    # "PEE-only" (k_see -> inf) is the torque-motor bench with k_pee = 0.6 -- see the protocol
    # deviation on the page: k_see = 1e6 on a 1 g CE is unstable at dt = 2 ms.
    "SEE-only":  (K_SEE, 0.0,  True),
    "rigid":     (K_SEE, 80.0, True),
    "frozen":    (K_SEE, 0.6,  False),
}


def h1_run(cond, seed):
    """self_model_topology.run_one, with the torque motors replaced by the SM block."""
    k_see, k_pee, drive = H1_CONDITIONS[cond]
    n_seg = SMT.N_SEG
    rng = np.random.default_rng(seed)
    m = mujoco.MjModel.from_xml_string(build_sm_chain_xml(n_seg, k_see=k_see, k_pee=k_pee,
                                                          joint_damping=0.05, bend_limit_deg=45.0))
    d = mujoco.MjData(m); c = SMChain(m, n_seg, k_see=k_see)
    nj = n_seg - 1
    tau = np.zeros(nj); tau_tc, tau_sig = 0.15, 8.0
    n_warm, n_rec = int(SMT.T_WARM / DT), int(SMT.T_REC / DT)
    TAU = np.zeros((n_rec, nj)); VEL = np.zeros((n_rec, nj)); at_limit = 0
    lim = np.deg2rad(45.0) - np.deg2rad(1.0)
    for i in range(n_warm + n_rec):
        if drive:
            tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
            c.set_from_board(d, np.clip(tau, 0.0, 2.5), np.clip(-tau, 0.0, 2.5))
        apply_anisotropic_drag(m, d, c.seg, c_long=SMT.DRAG_LONG, c_trans=SMT.DRAG_TRANS)
        mujoco.mj_step(m, d)
        if i >= n_warm:
            r = i - n_warm
            TAU[r] = tau
            VEL[r] = d.qvel[c.jv] + rng.normal(0.0, SMT.PROPRIO_NOISE, nj)
            at_limit += bool(np.any(np.abs(d.qpos[c.jq]) >= lim))
    VEL = VEL - VEL.mean(axis=1, keepdims=True)          # common-mode removal, as the bench
    return TAU, VEL, at_limit / n_rec


def score(TAU, VEL):
    C = transfer(TAU, VEL)
    return neighbour_accuracy(C), order_accuracy(seriation_order(C))


def h1():
    out = {}
    for cond in ["torque motors (bench)"] + list(H1_CONDITIONS):   # the first row doubles as PEE-only
        nb, od, lim = [], [], []
        for s in SEEDS:
            if cond == "torque motors (bench)":
                TAU, VEL = SMT.run_one("elastic", s); fl = float("nan")
            else:
                TAU, VEL, fl = h1_run(cond, s)
            a, o = score(TAU, VEL); nb.append(a); od.append(o); lim.append(fl)
        out[cond] = dict(nbr=(float(np.mean(nb)), float(np.std(nb))), order=(float(np.mean(od)), float(np.std(od))),
                         at_limit=float(np.nanmean(lim)) if cond != "torque motors (bench)" else None)
        print(f"  H1 {cond:<24} neighbour {out[cond]['nbr'][0]:.2f}±{out[cond]['nbr'][1]:.2f}   "
              f"order {out[cond]['order'][0]:.2f}±{out[cond]['order'][1]:.2f}"
              + (f"   time at bend limit {out[cond]['at_limit']:.0%}" if out[cond]['at_limit'] is not None else ""))
    return out


# ---------------------------------------------------------------- H2: locomotion ---------------
def c0_block():
    """c0_crawler.run with the torque motors replaced by the block (k_pee = 0)."""
    n = C0.N_SEG
    m = mujoco.MjModel.from_xml_string(build_sm_chain_xml(n, k_pee=0.0)); d = mujoco.MjData(m); c = SMChain(m, n)
    sL, sR = m.site("sense_L").id, m.site("sense_R").id
    beam = MessagingBeam(n_joints=n - 1, amp=0.8, freq=0.9, turn_gain=C0.TURN_GAIN)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in range(n - 1)]
    mujoco.mj_forward(m, d)
    x0 = d.xpos[c.seg[0]][:2].copy()
    d_start = np.hypot(*(x0 - np.array(C0.SOURCE)))
    for i in range(int(C0.T_END / DT)):
        bias = C0.BIAS_SIGN * (C0.FIELD.sample(*d.site_xpos[sL][:2]) - C0.FIELD.sample(*d.site_xpos[sR][:2]))
        tc = beam.command(DT, bias=bias)
        a_p, a_n = zip(*[boards[k].commands(float(d.qpos[c.jq[k]]), float(d.qvel[c.jv[k]]), tc[k], 0.0)[:2] for k in range(n - 1)])
        c.set_from_board(d, a_p, a_n)
        apply_anisotropic_drag(m, d, c.seg, c_long=C0.DRAG_LONG, c_trans=C0.DRAG_TRANS)
        mujoco.mj_step(m, d)
    x1 = d.xpos[c.seg[0]][:2]
    return dict(net_disp=float(np.hypot(*(x1 - x0))), closed_gap=float(d_start - np.hypot(*(x1 - np.array(C0.SOURCE)))))


def gl_block(scale=1.0, n=GL.N_SEG, T=GL.T_END, log=False):
    """gravity_locomotion.run(ratio=20) with the block (k_pee = 0); optionally logs H3 afferents."""
    m = mujoco.MjModel.from_xml_string(build_sm_chain_xml(n, k_pee=0.0, joint_damping=0.03, bend_limit_deg=50.0))
    d = mujoco.MjData(m); c = SMChain(m, n)
    beam = MessagingBeam(n_joints=n - 1, amp=0.8, freq=0.9)
    boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in range(n - 1)]
    mujoco.mj_forward(m, d); x0 = d.xpos[c.seg[0]][:2].copy(); L = dict(cmd=[], q=[], ten=[])
    for i in range(int(T / DT)):
        tc = beam.command(DT)
        a_p, a_n = zip(*[boards[k].commands(float(d.qpos[c.jq[k]]), float(d.qvel[c.jv[k]]), tc[k], 0.0)[:2] for k in range(n - 1)])
        c.set_from_board(d, a_p, a_n)
        apply_ground_friction(m, d, c.seg, mu_long=GL.MU_LONG * scale, mu_trans=GL.MU_LONG * 20 * scale)
        mujoco.mj_step(m, d)
        if log and i * DT >= 5.0:
            tp, tn = c.tendon_tension(d)
            L["cmd"].append(tc.copy()); L["q"].append(d.qpos[c.jq].copy()); L["ten"].append(tp + tn)
    disp = float(np.hypot(*(d.xpos[c.seg[0]][:2] - x0)))
    return disp, {k: np.array(v) for k, v in L.items()}


def gl_torque_log(scale, n=GL.N_SEG, T=20.0):
    """The bench's torque-motor ground crawler (gravity_locomotion settings), logging the same H3 quantities.
    Its 'force afferent' is the command itself: the torque the motor is told to make."""
    m = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=n, gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0))
    d = mujoco.MjData(m)
    seg = [m.body(f"seg{k}").id for k in range(n)]
    jq = [m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1, n)]; jv = [m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1, n)]
    ap = [m.actuator(f"m_j{k}_p").id for k in range(1, n)]; an = [m.actuator(f"m_j{k}_n").id for k in range(1, n)]
    beam = MessagingBeam(n_joints=n - 1, amp=0.8, freq=0.9); boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in ap]
    mujoco.mj_forward(m, d); x0 = d.xpos[seg[0]][:2].copy(); L = dict(cmd=[], q=[], ten=[])
    for i in range(int(T / DT)):
        tc = beam.command(DT); f = []
        for k in range(n - 1):
            a, b, _ = boards[k].commands(float(d.qpos[jq[k]]), float(d.qvel[jv[k]]), tc[k], 0.0)
            d.ctrl[ap[k]] = a; d.ctrl[an[k]] = b; f.append((a + b) * F_MAX / 2.5)   # commanded force, same units
        apply_ground_friction(m, d, seg, mu_long=GL.MU_LONG * scale, mu_trans=GL.MU_LONG * 20 * scale)
        mujoco.mj_step(m, d)
        if i * DT >= 5.0:
            L["cmd"].append(tc.copy()); L["q"].append(d.qpos[jq].copy()); L["ten"].append(np.array(f))
    return float(np.hypot(*(d.xpos[seg[0]][:2] - x0))), {k: np.array(v) for k, v in L.items()}


def h2():
    c0_log = C0.run(); c0_t = C0.summarize(c0_log)
    c0_b = c0_block()
    gl_t, _ = GL.run(20)
    gl_b, _ = gl_block()
    out = {"C0 net displacement (m)": (c0_t["net_disp"], c0_b["net_disp"]),
           "C0 distance closed to source (m)": (c0_t["closed_gap"], c0_b["closed_gap"]),
           "ground crawler net displacement (m)": (gl_t, gl_b)}
    for k, (t, b) in out.items():
        print(f"  H2 {k:<38} torque {t:6.3f}   block {b:6.3f}   ratio {b / t if t else float('nan'):5.2f}")
    return out


# ---------------------------------------------------------------- H3: exploratory --------------
def lag_s(cmd, q):
    """Lag of joint angle behind command, from the peak of their cross-correlation (mean over joints)."""
    lags = []
    for k in range(cmd.shape[1]):
        a = cmd[:, k] - cmd[:, k].mean(); b = q[:, k] - q[:, k].mean()
        cc = np.correlate(b, a, mode="full")[len(a) - 1:len(a) - 1 + int(1.0 / DT)]   # 0..1 s
        lags.append(np.argmax(cc) * DT)
    return float(np.mean(lags))


def h3():
    out = {}
    for name, fn in (("block", lambda s: gl_block(scale=s, T=20.0, log=True)), ("torque motors", lambda s: gl_torque_log(s))):
        rows = []
        for s in (0.3, 1.0, 3.0):
            disp, L = fn(s)
            bend = float(np.mean((L["q"].max(0) - L["q"].min(0)) / 2))
            rows.append(dict(friction=s, tension=float(L["ten"].mean()), lag=lag_s(L["cmd"], L["q"]), bend=bend, disp=disp))
            print(f"  H3 {name:<14} friction ×{s:<4} force afferent {rows[-1]['tension']:6.3f} N   lag {rows[-1]['lag']:.3f} s   "
                  f"bend {bend:.3f} rad   disp {disp:.2f} m")
        out[name] = rows
    return out


def figure(r1, r2, r3, path):
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    names = list(r1); x = np.arange(len(names)); w = 0.38
    ax[0].bar(x - w / 2, [r1[n]["nbr"][0] for n in names], w, yerr=[r1[n]["nbr"][1] for n in names], label="neighbour", color="#2c6fbb")
    ax[0].bar(x + w / 2, [r1[n]["order"][0] for n in names], w, yerr=[r1[n]["order"][1] for n in names], label="order", color="#9ab8de")
    ax[0].axhline(0.9, ls="--", color="#2c6fbb", lw=1); ax[0].axhline(0.6, ls=":", color="#c0392b", lw=1)
    ax[0].set_xticks(x); ax[0].set_xticklabels(names, rotation=25, ha="right", fontsize=8); ax[0].set_ylim(0, 1.05)
    ax[0].set_title("H1 — self-model recovery (5 seeds)"); ax[0].legend(fontsize=8)
    keys = list(r2); x = np.arange(len(keys))
    ax[1].bar(x - w / 2, [r2[k][0] for k in keys], w, label="torque motors (bench)", color="#888")
    ax[1].bar(x + w / 2, [r2[k][1] for k in keys], w, label="SM block", color="#2c6fbb")
    ax[1].set_xticks(x); ax[1].set_xticklabels([k.replace(" (m)", "") for k in keys], rotation=15, ha="right", fontsize=8)
    ax[1].set_ylabel("m"); ax[1].set_title("H2 — locomotion, unchanged gains"); ax[1].legend(fontsize=8)
    for name, col in (("block", "#2c6fbb"), ("torque motors", "#888")):
        f = [r["friction"] for r in r3[name]]
        ax[2].plot(f, [r["tension"] for r in r3[name]], "o-", color=col, label=f"{name}: force afferent (N)")
        ax[2].plot(f, [10 * r["lag"] for r in r3[name]], "s--", color=col, label=f"{name}: lag ×10 (s)")
    ax[2].set_xscale("log"); ax[2].set_xlabel("ground friction ×"); ax[2].set_title("H3 (exploratory) — does the afferent carry the ground?")
    ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=130)


def main():
    print(f"MuJoCo {mujoco.__version__}")
    r1 = h1(); r2 = h2(); r3 = h3()
    P1 = r1["block"]["nbr"][0] >= 0.90 and r1["block"]["order"][0] >= 0.80
    P2 = r1["rigid"]["nbr"][0] <= 0.60 and (r1["block"]["nbr"][0] - r1["rigid"]["nbr"][0]) >= 0.30
    pee = r1["torque motors (bench)"]          # = PEE-only (protocol deviation)
    P3 = abs(pee["nbr"][0] - r1["block"]["nbr"][0]) <= 0.10 and abs(pee["order"][0] - r1["block"]["order"][0]) <= 0.10
    H2 = all(b >= 0.5 * t for k, (t, b) in r2.items() if "displacement" in k) and r2["C0 distance closed to source (m)"][1] > 0
    verdict = dict(P1=P1, P2=P2, P3=P3, H2=H2)
    print("Verdicts (pre-registered thresholds):", verdict)
    os.makedirs(os.path.join(HERE, "..", "figures"), exist_ok=True)
    figure(r1, r2, r3, os.path.join(HERE, "..", "figures", "sm_block.png"))
    os.makedirs(os.path.join(HERE, "..", "samples", "sm_block"), exist_ok=True)
    json.dump(dict(mujoco=mujoco.__version__, H1=r1, H2=r2, H3=r3, verdict=verdict),
              open(os.path.join(HERE, "..", "samples", "sm_block", "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
