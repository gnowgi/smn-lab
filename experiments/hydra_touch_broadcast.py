# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Hydra 'hello world', stage 1 -- the sac knows, everywhere, where it was touched.

A sessile two-layer sac (a closed-tube CAZ lattice -- the Hydra body plan) recovers
its OWN topology from movement, then a prey-touch at one node is (1) localized on the
recovered self-graph and (2) shown to be readable from the OPPOSITE end of the net --
the oral ring that was never touched. That is the IN broadcast: a LOCAL touch made
GLOBALLY available, so the whole net (not just the touched zone) knows where the prey
landed. It is the substrate for the whole-net capture reflex (stage 2).

Everything runs through the one results module (``smn_lab.report``): the self-model
card of the sac, the world (touch) localized on it, the canvas built from the touch,
and the emergent diagnostics -- with the lattice ``recovery="endpoint"`` mode.

Order parameters:
  * self-model endpoint recovery of the sac (the net recovers its own envelope);
  * localization: the touched node = the peak of the net's response (world on self-graph);
  * BROADCAST: decode the touch LOCATION from the far mouth ring alone, vs a shuffle
    control. Skill >> shuffle => the location is broadcast across the whole net.

Run:  ../.venv/bin/python hydra_touch_broadcast.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab.lattice import build_lattice_xml, lattice_edges, lattice_positions
from smn_lab.self_model import coupling
from smn_lab.metrics import endpoint_recovery, decoding_skill
from smn_lab.report import RunRecord, render

DT = 0.002
N_COL, N_ROW = 7, 6                 # 7 rings along the oral-aboral axis, 6 zones around
CLOSED = True                        # a closed tube -> the sac / envelope
NSEG = N_COL * N_ROW
T_WARM, T_REC = 2.0, 25.0            # babble (self-model)
U_TC, U_SIG = 0.15, 5.0
PULSE_STEPS, WIN_STEPS = 20, 200     # prey-touch pulse, then response window
FORCE = 9.0
REPS = 3
SEED = 0


def idx(r, c):
    return r * N_COL + c


def build():
    xml = build_lattice_xml(n_col=N_COL, n_row=N_ROW, closed=CLOSED)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(NSEG)]
    return m, d, bid


def seg_speed(d):
    v = d.qvel.reshape(-1, 3)                       # (NSEG, 3) slide velocities
    return np.linalg.norm(v, axis=1)


def recover_self_model(seed):
    """Babble each CAZ link independently -> coupling read-out -> endpoint recovery."""
    m, d, bid = build()
    nlink = m.nu
    rng = np.random.default_rng(seed)
    edges = lattice_edges(N_COL, N_ROW, CLOSED)
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    u = np.zeros(nlink)
    DRV = np.zeros((n_rec, nlink)); VX = np.zeros((n_rec, NSEG))
    VY = np.zeros((n_rec, NSEG)); VZ = np.zeros((n_rec, NSEG))
    for i in range(n_warm + n_rec):
        u += (-u / U_TC) * DT + U_SIG * np.sqrt(DT) * rng.standard_normal(nlink)
        u_drive = np.clip(u, 0.0, None)               # pull-only f: contraction amount >= 0
        d.ctrl[:] = u_drive
        mujoco.mj_step(m, d)
        if i >= n_warm:
            j = i - n_warm
            DRV[j] = u_drive
            vv = d.qvel.reshape(-1, 3)
            VX[j], VY[j], VZ[j] = vv[:, 0], vv[:, 1], vv[:, 2]
    for V in (VX, VY, VZ):
        V -= V.mean(1, keepdims=True)                # common-mode (reafference) removal
    C = np.abs(coupling(DRV, VX)) + np.abs(coupling(DRV, VY)) + np.abs(coupling(DRV, VZ))
    return C, edges


def touch_response(m, d, bid, k, rng):
    """Apply a brief prey-touch pulse at node k; integrate the net's per-node response
    over the window. Returns (response_field[NSEG], response_over_time[WIN, NSEG])."""
    d.qpos[:] = 0.0; d.qvel[:] = 0.0; d.ctrl[:] = 0.0; d.xfrc_applied[:] = 0.0
    mujoco.mj_forward(m, d)
    direction = rng.standard_normal(3); direction /= np.linalg.norm(direction) + 1e-9
    resp = np.zeros(NSEG); over_time = np.zeros((WIN_STEPS, NSEG))
    for i in range(PULSE_STEPS + WIN_STEPS):
        d.xfrc_applied[:] = 0.0
        if i < PULSE_STEPS:
            d.xfrc_applied[bid[k], 0:3] = FORCE * direction
        mujoco.mj_step(m, d)
        if i >= PULSE_STEPS:
            s = seg_speed(d)
            resp += s; over_time[i - PULSE_STEPS] = s
    return resp, over_time


def main():
    rng = np.random.default_rng(SEED)
    C, edges = recover_self_model(SEED)
    er = float(endpoint_recovery(C, edges))

    # touch sites = the body/tentacle rings (cols 1..N_COL-1); the MOUTH ring is col 0
    # (the oral end), which is never touched -- our far read-out for the broadcast test.
    sites = [idx(r, c) for c in range(1, N_COL) for r in range(N_ROW)]
    mouth = [idx(r, 0) for r in range(N_ROW)]
    pos_un = {i: (-(i % N_COL), i // N_COL) for i in range(NSEG)}   # unrolled 2-D layout

    m, d, bid = build()
    rng_sites = np.random.default_rng(SEED + 1)
    order = rng_sites.permutation(len(sites))       # site-level split for generalization
    feats, labels, loc_ok = [], [], []
    rep_field, rep_time = None, None
    for oi in order:
        k = sites[oi]
        for _ in range(REPS):
            resp, over_time = touch_response(m, d, bid, k, rng)
            feats.append(resp[mouth])               # FAR read-out: the mouth ring only
            labels.append(pos_un[k])                # true touch location (unrolled)
            loc_ok.append(int(np.argmax(resp) == k))  # localization: peak == touched node
            if rep_field is None and k == sites[len(sites) // 2]:
                rep_field, rep_time = resp.copy(), over_time.copy()
    S = np.array(feats); P = np.array(labels, float)
    loc_acc = float(np.mean(loc_ok))

    # BROADCAST: decode the touch location from the mouth ring alone (site-level split)
    bcast = float(decoding_skill(S, P, np.random.default_rng(7), k=6))
    shuf = float(decoding_skill(S, P, np.random.default_rng(7), k=6, shuffle=True))

    print("\nHydra sac -- the net knows, everywhere, where it was touched\n" + "=" * 66)
    print(f"body: closed tube {N_ROW}x{N_COL} = {NSEG} zones, {len(edges)} CAZ links")
    print(f"self-model endpoint recovery (the net recovers its own sac): {er:.2f}")
    print(f"localization (touched node = peak of the net's response):     {loc_acc:.2f}")
    print(f"BROADCAST -- decode touch LOCATION from the far mouth ring:")
    print(f"    decoding skill = {bcast:.2f}   (shuffle control = {shuf:.2f})")
    ok = er > 0.9 and loc_acc > 0.9 and bcast > 0.3 and bcast > shuf + 0.2
    print("=" * 66)
    print(f"Verdict: a LOCAL touch is made GLOBALLY available -- the oral ring, never")
    print(f"touched, encodes where the prey landed  [{'PASS' if ok else 'CHECK'}]\n")

    # everything through the one module: self-model card of the sac + world + canvas
    node_field = {i: float(rep_field[i]) for i in range(NSEG)}
    render(
        RunRecord(name="hydra_sac", coupling_matrix=C, recovery="endpoint",
                  positions=pos_un, true_edges=edges,
                  node_field=node_field, world_signal=rep_time, modality="touch",
                  metrics={"endpoint_recovery": er, "localization": loc_acc,
                           "broadcast_skill": bcast, "shuffle": shuf},
                  meta={"body": f"tube_{N_ROW}x{N_COL}", "n_zones": NSEG}),
        spec=dict(prefix="hydra_sac",
                  suptitle="Hydra sac — self-model, prey-touch localized, broadcast"))


if __name__ == "__main__":
    main()
