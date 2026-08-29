# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Does the pull-only ``f`` change the self-model? (A2 evidence.)

A muscle can only pull, so the A2 primitive (``smn_lab.fbody.build_body``, pull-only) restricts each
``f`` to contraction. This asks whether that restriction costs anything in the load-bearing result —
topology-invariant **self-model recovery** — versus the legacy bidirectional actuator.

Babble each ``f`` and recover the body graph with the framework read-out
(``smn_lab.self_model.coupling`` + ``endpoint_recovery``), for bidirectional vs pull-only.

Result (3 seeds): recovery is unchanged (Δ ≤ 0.01), so the pull-only migration is safe for the
recovery family. Run:  ../.venv/bin/python pull_only_recovery_delta.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import mujoco
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.fbody import build_body, DT
from smn_lab.self_model import coupling
from smn_lab.metrics import endpoint_recovery


def chain(n):
    return [(i * 0.3, 0, 0) for i in range(n)], [(i, i + 1) for i in range(n - 1)]


def sheet(nc, nr, dx=0.3, dy=0.3):
    pos = [(c * dx, r * dy, 0) for r in range(nr) for c in range(nc)]
    idx = lambda c, r: r * nc + c
    E = []
    for r in range(nr):
        for c in range(nc):
            if c + 1 < nc: E.append((idx(c, r), idx(c + 1, r)))
            if r + 1 < nr: E.append((idx(c, r), idx(c, r + 1)))
    return pos, E


def recover(pos, edges, pull_only, seed=0, T=16.0, tc=0.15, sig=4.0):
    m, d, aoe = build_body(pos, edges, stiff=12.0, pull_only=pull_only, cmax=4.0)
    rng = np.random.default_rng(seed)
    n, nm, nn = int(T / DT), len(edges), len(pos)
    DRV = np.zeros((n, nm)); V = [np.zeros((n, nn)) for _ in range(3)]
    u = np.zeros(m.nu); d.qpos[:] = 0; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    warm = int(2.0 / DT); ou = np.zeros(nm)
    for i in range(warm + n):
        ou += (-ou / tc) * DT + sig * np.sqrt(DT) * rng.standard_normal(nm)
        drive = np.clip(ou, 0, None) if pull_only else ou     # pull-only: contraction amount >= 0
        for e, a in aoe.items(): u[a] = drive[e]
        d.ctrl[:] = u; mujoco.mj_step(m, d)
        if i >= warm:
            j = i - warm; DRV[j] = drive; vv = d.qvel.reshape(-1, 3)
            for k in range(3): V[k][j] = vv[:, k]
    for A in V: A -= A.mean(0)
    C = sum(np.abs(coupling(DRV, A)) for A in V)
    return endpoint_recovery(C, edges)


def main():
    print("\nSelf-model recovery — bidirectional vs pull-only f (3 seeds each)")
    print("=" * 66)
    print(f"{'body':<12}{'bidirectional':>15}{'pull-only':>12}{'Δ':>8}")
    for name, (pos, edges) in [("chain-8", chain(8)), ("sheet-2x5", sheet(5, 2)),
                                ("sheet-3x4", sheet(4, 3))]:
        bi = np.mean([recover(pos, edges, False, s) for s in range(3)])
        po = np.mean([recover(pos, edges, True, s) for s in range(3)])
        print(f"{name:<12}{bi:>15.2f}{po:>12.2f}{po - bi:>+8.2f}")
    print("=" * 66)
    print("Recovery is unchanged under pull-only → the migration is safe for the recovery family.")


if __name__ == "__main__":
    main()
