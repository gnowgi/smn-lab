# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Mechanical invariants of the canonical SM block (smn_lab/sm_block.py).

These are statics checks of the construction, not results: they fix what the block IS before any
experiment uses it.
  1. at rest nothing pulls;
  2. series equilibrium — a held CE force F stretches its tendon until tension = F;
  3. pull-only — the antagonist's tendon is slack while the agonist pulls;
  4. the parallel element sets the static angle: q = r F / k_pee;
  5. co-contraction holds the joint at its set point with both tendons taut;
  6. a series spring alone does NOT restore the joint (the reason the block has a parallel element).

Run:  python tests/test_sm_block.py     (or: pytest tests/)
"""
from __future__ import annotations
import os, sys
import numpy as np
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.sm_block import build_sm_chain_xml, SMChain, R_ARM


def _settle(k_pee=0.6, f_p=0.0, f_n=0.0, push=0.0, t_hold=1.0, t_push=0.0, t_after=0.0):
    m = mujoco.MjModel.from_xml_string(build_sm_chain_xml(3, k_pee=k_pee)); d = mujoco.MjData(m)
    c = SMChain(m, 3)
    f = np.zeros(2); fp = np.array([f_p, 0.0]); fn = np.array([f_n, 0.0])
    c.set_forces(d, fp, fn)
    for _ in range(int(t_hold / 0.002)): mujoco.mj_step(m, d)
    q_hold = d.qpos[c.jq[0]]
    for _ in range(int(t_push / 0.002)): d.qfrc_applied[c.jv[0]] = push; mujoco.mj_step(m, d)
    q_push = d.qpos[c.jq[0]]; d.qfrc_applied[:] = 0
    for _ in range(int(t_after / 0.002)): mujoco.mj_step(m, d)
    tp, tn = c.tendon_tension(d)
    return dict(q_hold=q_hold, q_push=q_push, q_after=d.qpos[c.jq[0]], tp=tp[0], tn=tn[0])


def test_rest():
    r = _settle()
    assert abs(r["q_hold"]) < 1e-9 and r["tp"] == 0 and r["tn"] == 0


def test_series_equilibrium_pull_only_and_parallel_statics():
    r = _settle(f_p=2.0, t_hold=2.0)
    assert abs(r["tp"] - 2.0) < 1e-3                       # tension = CE force
    assert r["tn"] == 0.0                                  # antagonist slack: pull-only
    assert abs(r["q_hold"] - R_ARM * 2.0 / 0.6) < 1e-3     # q = r F / k_pee
    r = _settle(f_n=2.0, t_hold=2.0)
    assert abs(r["q_hold"] + R_ARM * 2.0 / 0.6) < 1e-3


def test_cocontraction_holds_with_both_taut():
    r = _settle(f_p=2.0, f_n=2.0, t_hold=2.0)
    assert abs(r["q_hold"]) < 1e-6 and abs(r["tp"] - 2.0) < 1e-3 and abs(r["tn"] - 2.0) < 1e-3


def test_parallel_element_restores():
    r = _settle(k_pee=0.6, f_p=2.0, f_n=2.0, push=0.02, t_push=1.0, t_after=1.5)
    assert r["q_push"] > 0.02 and abs(r["q_after"]) < 1e-3


def test_series_spring_alone_does_not_restore():
    r = _settle(k_pee=0.0, f_p=2.0, f_n=2.0, push=0.02, t_push=1.0, t_after=1.5)
    assert r["q_push"] > 0.5 and r["q_after"] > 0.5          # pushed away, never comes back


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("pass", name)
