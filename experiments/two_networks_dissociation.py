# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Why an SMN agent needs TWO networks -- a double dissociation.

The passive Hydra sac showed a mechanical net builds a self-model but broadcasts a
touch only weakly. That is not a bug: it reveals the division of labour between the two
SMN networks, and this experiment turns it into a measurement.

ARCHITECTURE (careful): COORDINATION is NOT the IN's job -- it is the DFN's, through
OPPOSING ZONES, decentralized, with NO central control. The IN only INTEGRATES into a
globally-available SNAPSHOT (makes the body one *agent* = one unified perspective); it
cannot command or control. So the two axes below are DIFFERENTIATION (geometry) and
INTEGRATION (a globally-available snapshot) -- not "coordination".

  * The DAMPED, DIFFERENTIATED net (elastic springs / the DFN substrate) is DECREMENTAL --
    coupling falls off with distance. That attenuation IS the geometry signal: it lets a
    zone read how FAR another is, so the self-model (body geometry) is recoverable from it.
    (This same differentiated, opposing-zone net is where coordination happens -- locally,
    no central control -- which is NOT what we measure here.)
  * The INTEGRATING net (the IN board) is NON-DECREMENTAL -- it delivers an integrated
    signal to every zone equally, so the composed SNAPSHOT is globally available (the body
    known as one). But integration erases per-zone identity, so body GEOMETRY cannot be
    recovered from it -- and it neither commands nor controls.

The 2x2 (channel x function). Prediction: the diagonal is high, the off-diagonal collapses
-- each net does the one thing the other structurally cannot, so an agent that needs both
a body-model (differentiation) and a unified snapshot (integration) needs BOTH nets.

  |                    | GEOMETRY (differentiation) | GLOBAL SNAPSHOT (integration) |
  | damped mechanical  |          HIGH              |        LOW (attenuates)       |
  | integrating IN     |        CHANCE              |        HIGH (available to all)|

Run:  ../.venv/bin/python two_networks_dissociation.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab.self_model import coupling
from smn_lab.metrics import endpoint_recovery
from smn_lab.report import RunRecord, render
from hydra_sac import (build, touch, DT, T_WARM, T_REC, U_TC, U_SIG, N_ROW, N_COL, SEED)


def babble(m, d, bid, nlink, seed):
    rng = np.random.default_rng(seed)
    nseg = len(bid)
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    u = np.zeros(nlink)
    DRV = np.zeros((n_rec, nlink)); VX = np.zeros((n_rec, nseg))
    VY = np.zeros((n_rec, nseg)); VZ = np.zeros((n_rec, nseg))
    d.qpos[:] = 0; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    for i in range(n_warm + n_rec):
        u += (-u / U_TC) * DT + U_SIG * np.sqrt(DT) * rng.standard_normal(nlink)
        d.ctrl[:] = u; mujoco.mj_step(m, d)
        if i >= n_warm:
            j = i - n_warm; DRV[j] = u
            vv = d.qvel.reshape(-1, 3); VX[j], VY[j], VZ[j] = vv[:, 0], vv[:, 1], vv[:, 2]
    for V in (VX, VY, VZ):
        V -= V.mean(1, keepdims=True)
    return DRV, VX, VY, VZ


def coupling3(DRV, X, Y, Z):
    return np.abs(coupling(DRV, X)) + np.abs(coupling(DRV, Y)) + np.abs(coupling(DRV, Z))


def main():
    m, d, bid, pos, edges, roles, ix = build()
    io, ii, out_apex, in_apex = ix
    nlink, nseg = m.nu, len(bid)
    DRV, VX, VY, VZ = babble(m, d, bid, nlink, SEED)

    # --- GEOMETRY (self-model) through each channel ---
    # DAMPED: each zone reports its OWN local (differentiated, decremental) motion.
    C_mech = coupling3(DRV, VX, VY, VZ)
    er_mech = float(endpoint_recovery(C_mech, edges))
    # INTEGRATING IN: each zone reports the BROADCAST board = mean over all zones (the
    # integrated signal, non-decremental). Integration erases per-zone identity.
    def board(V): return np.repeat(V.mean(1, keepdims=True), nseg, axis=1)
    C_in = coupling3(DRV, board(VX), board(VY), board(VZ))
    er_in = float(endpoint_recovery(C_in, edges))
    # chance baseline for endpoint recovery (random coupling)
    rngc = np.random.default_rng(99)
    er_chance = float(np.mean([endpoint_recovery(rngc.random((nlink, nseg)), edges)
                               for _ in range(5)]))

    # --- NON-DECREMENTAL REACH: how much of a local touch a FAR zone experiences ---
    sites = [io(r, c) for c in range(1, N_COL) for r in range(N_ROW)]
    far_nodes = [io(r, 0) for r in range(N_ROW)] + [ii(r, 0) for r in range(N_ROW)]
    rng = np.random.default_rng(SEED + 5)
    near, far, brd = [], [], []
    for k in sites:
        resp, _ = touch(m, d, bid, k, rng)
        near.append(resp[k])                          # the touched zone (mechanical peak)
        far.append(np.mean(resp[far_nodes]))          # far zones' LOCAL mechanical response
        brd.append(np.mean(resp))                     # the IN board (integrated, uniform to all)
    near, far, brd = map(np.array, (near, far, brd))
    reach_mech = float(np.mean(far / near))           # decremental: small
    reach_in = 1.0                                    # the board is identical at every zone
    # what a FAR zone actually receives from each channel (the decisive contrast):
    far_gets_mech = float(np.mean(far / near))        # its own local mechanics -> tiny
    far_gets_in = float(np.mean(brd / near))          # the broadcast board -> larger, distance-free

    print("\nWhy an SMN agent needs TWO networks -- a double dissociation\n" + "=" * 68)
    print(f"body: diploblast sac, {nseg} zones, {nlink} CAZ links")
    print(f"(coordination is the DFN's job via opposing zones, no central control -- NOT")
    print(f" measured here; the IN only integrates a globally-available snapshot.)")
    print(f"\n                        GEOMETRY(differentiation)  GLOBAL SNAPSHOT(integration)")
    print(f"  damped mechanical   {er_mech:>14.2f}          far/near = {reach_mech:.2f}  (decremental)")
    print(f"  integrating IN      {er_in:>14.2f}          far/near = {reach_in:.2f}  (uniform)")
    print(f"  (chance geometry = {er_chance:.2f})")
    print(f"\nWhat a FAR zone receives of a local touch: via its own mechanics {far_gets_mech:.2f} "
          f"vs via the IN board {far_gets_in:.2f}  ({far_gets_in/max(far_gets_mech,1e-9):.0f}x more)")
    ok = (er_mech > 0.85 and er_in < er_mech * 0.5 and reach_mech < 0.5)
    print("=" * 68)
    print(f"Double dissociation [{'PASS' if ok else 'CHECK'}]: the damped/DIFFERENTIATED net BUILDS geometry ({er_mech:.2f})")
    print(f"but stays local ({reach_mech:.2f}); the INTEGRATING net makes the snapshot available to all")
    print(f"({reach_in:.2f}) but cannot build geometry ({er_in:.2f}, ~chance). Attenuation IS the self-model's")
    print(f"signal; non-decrement IS the snapshot's. One medium cannot be both -> two nets forced.")
    print(f"(COORDINATION lives in the differentiated net's opposing zones; the IN cannot command.)\n")

    # figures: the 2x2 matrix, and both self-model cards (clean vs garbled) via the module
    M = np.array([[er_mech, reach_mech], [er_in, reach_in]])
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    im = ax.imshow(M, cmap="magma", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["geometry\n(differentiation)",
                                               "global snapshot\n(integration)"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["damped\nmechanical (DFN)", "integrating\nIN"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center",
                    color="w" if M[i, j] < 0.55 else "k", fontsize=13, fontweight="bold")
    ax.set_title("Two networks, double dissociation\ndifferentiation builds geometry · "
                 "integration makes the snapshot global\n(coordination = the DFN's opposing zones, not the IN)")
    fig.colorbar(im, label="score")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "two_networks_dissociation.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")

    pos2d = {}
    for r in range(N_ROW):
        for c in range(N_COL):
            pos2d[io(r, c)] = (-c, r); pos2d[ii(r, c)] = (-c, r - (N_ROW + 1))
    pos2d[out_apex] = (-(N_COL + 0.4), (N_ROW - 1) / 2)
    pos2d[in_apex] = (-(N_COL + 0.4), (N_ROW - 1) / 2 - (N_ROW + 1))
    render(RunRecord(name="dissoc_damped", coupling_matrix=C_mech, recovery="endpoint",
                     positions=pos2d, true_edges=edges,
                     metrics={"endpoint_recovery": er_mech}),
           spec=dict(prefix="dissoc_damped", card=True, op_plot=False,
                     suptitle="Self-model from the DAMPED net — geometry recovered"))
    render(RunRecord(name="dissoc_integrated", coupling_matrix=C_in, recovery="endpoint",
                     positions=pos2d, true_edges=edges,
                     metrics={"endpoint_recovery": er_in}),
           spec=dict(prefix="dissoc_integrated", card=True, op_plot=False,
                     suptitle="Self-model from the INTEGRATING net — geometry lost"))


if __name__ == "__main__":
    main()
