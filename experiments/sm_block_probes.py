# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""EXPLORATORY probes run AFTER the pre-registered sm_block.py results were seen (not pre-registered).

Question: the pre-registered SEE-only condition (k_pee = 0) recovered the self-model while spending 72%
of its time at the 45° bend limits. Is the recovery carried by the stops, i.e. by a restoring element
the condition was meant to lack?

  A. SEE-only with the bend limit opened (45° -> 90° -> 170°);
  B. SEE-only at 170° with the CE slides' travel stops also moved out of reach;
  C. the bench's torque-motor chain with joint stiffness 0 (no elasticity at all), at 45° and at 170°,
     plus a stiffness ladder 0.6 / 5 / 20 / 80 for context.
Runs flagged 'unstable' had MuJoCo QACC warnings (the body folded through itself); their scores are
reported but are not a measurement of a well-posed body.

Run:  ../.venv/bin/python sm_block_probes.py
"""
from __future__ import annotations
import os, sys, io, contextlib
import numpy as np
import mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import smn_lab.sm_block as M
from smn_lab.sm_block import build_sm_chain_xml, SMChain, K_SEE
from smn_lab.crawler import apply_anisotropic_drag
import self_model_topology as SMT
import sm_block as SB

SEEDS = range(5)


def block_run(k_pee, bend, seed, ce_range=None):
    saved = M.CE_RANGE
    if ce_range: M.CE_RANGE = ce_range
    xml = build_sm_chain_xml(8, k_see=K_SEE, k_pee=k_pee, joint_damping=0.05, bend_limit_deg=bend)
    M.CE_RANGE = saved
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m); c = SMChain(m, 8)
    lo, hi = ce_range or saved; lim = np.deg2rad(bend) - np.deg2rad(1)
    xadr = [m.jnt_qposadr[m.joint(f"x_j{j}_{s}").id] for j in range(1, 8) for s in "pn"]
    rng = np.random.default_rng(seed); tau = np.zeros(7); TAU, VEL = [], []; at_q = at_x = 0; bad = False
    for i in range(int(64 / 0.002)):
        tau += (-tau / 0.15) * 0.002 + 8.0 * np.sqrt(0.002) * rng.standard_normal(7)
        c.set_from_board(d, np.clip(tau, 0, 2.5), np.clip(-tau, 0, 2.5))
        apply_anisotropic_drag(m, d, c.seg, c_long=0.6, c_trans=4.0); mujoco.mj_step(m, d)
        bad |= d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number > 0
        if i >= 2000:
            x = d.qpos[xadr]; at_x += np.mean((x <= lo + 1e-3) | (x >= hi - 1e-3))
            at_q += bool(np.any(np.abs(d.qpos[c.jq]) >= lim))
            TAU.append(tau.copy()); VEL.append(d.qvel[c.jv] + rng.normal(0, 0.02, 7))
    TAU = np.array(TAU); VEL = np.array(VEL); VEL -= VEL.mean(1, keepdims=True)
    n = len(TAU); return (*SB.score(TAU, VEL), at_q / n, at_x / n, bad)


def torque_run(k, bend, seed):
    SMT.CONDITIONS["probe"] = dict(stiffness=k, drive=True); orig = SMT.build_crawler_xml
    SMT.build_crawler_xml = lambda **kw: orig(**{**kw, "bend_limit_deg": bend})
    import tempfile
    tmp = tempfile.TemporaryFile(); sys.stdout.flush(); saved = [os.dup(1), os.dup(2)]
    try:
        os.dup2(tmp.fileno(), 1); os.dup2(tmp.fileno(), 2)   # MuJoCo prints its instability warning from C
        TAU, VEL = SMT.run_one("probe", seed)
    finally:
        os.dup2(saved[0], 1); os.dup2(saved[1], 2); [os.close(x) for x in saved]; SMT.build_crawler_xml = orig
    tmp.seek(0); bad = b"unstable" in tmp.read()
    return (*SB.score(np.nan_to_num(TAU), np.nan_to_num(VEL)), bad)


def report(label, rows):
    r = np.array(rows, dtype=float)
    extra = ""
    if r.shape[1] == 5: extra = f"  at bend limit {r[:,2].mean():.0%}  CE at a stop {r[:,3].mean():.0%}"
    unstable = int(r[:, -1].sum())
    print(f"{label:<58} neighbour {r[:,0].mean():.2f}±{r[:,0].std():.2f}  order {r[:,1].mean():.2f}±{r[:,1].std():.2f}{extra}"
          + (f"  UNSTABLE in {unstable}/5" if unstable else ""))


if __name__ == "__main__":
    print(f"MuJoCo {mujoco.__version__}  (exploratory, not pre-registered)")
    for bend in (45, 90, 170):
        report(f"A  SEE-only, bend limit {bend}°", [block_run(0.0, bend, s) for s in SEEDS])
    report("B  SEE-only, bend 170°, CE stops out of reach", [block_run(0.0, 170, s, ce_range=(-1.0, 1.0)) for s in SEEDS])
    for k, bend in ((0.0, 45), (0.0, 170), (0.6, 45), (5.0, 45), (20.0, 45), (80.0, 45)):
        report(f"C  torque motors, joint stiffness {k}, bend limit {bend}°", [torque_run(k, bend, s) for s in SEEDS])
