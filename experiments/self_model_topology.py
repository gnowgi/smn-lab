# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Self-model from zone data: recover the body's *topology* from movement alone.

The question this experiment answers is prior to any world model: can an agent,
from the data its own zones generate while it moves, recover the geometry of its
own body? Per the SMN framework the self-model is primary -- the world model is
world-geometry expressed in the self-model's frame -- so this is the load-bearing
experiment for the self/world distinction.

The claim under test (GN's design):

  * The zones move (that is what zones do). The segments joining them are
    *elastic*, so when one zone moves, a farther zone displaces *less* than a
    nearer one -- displacement attenuates with the number of intervening
    segments (hops).
  * Therefore the co-movement between two zones is a monotone function of their
    hop-distance, and the body's connectivity graph can be read off the
    co-movement structure. We recover a *graph, not a ruler*: no metric distance,
    only who-is-near-whom in hops.
  * The computation is local and emergent: each zone asks only "whose movement
    co-varies with mine?" -- it never reads the whole body. No central fit, no
    homunculus. This is Commitment C6 (spatial cognition through differential
    displacement) doing the work, and it is the shared-state-space of C3 realized
    without a separate reader.

Design:
  * Body: an elastic axial chain (crawler with compliant torsional joints).
  * Behaviour: natural movement -- each zone (joint) is independently, actively
    driven (an OU torque), so the body is alive rather than being probed.
  * Common-mode removal: each zone attends to its motion *relative to the body*
    (per-step mean subtracted), so whole-body drift/rotation -- which moves every
    zone alike, regardless of hops -- is cancelled. Differential displacement is
    what remains. This is the reafference move.
  * Read-out (reafference): each zone correlates its *own* efference (the torque
    it commands) with every other zone's *afferent* motion. Because the zones'
    drives are independent, this isolates the transmission gain G[i,j] from zone i
    to zone j -- how much j moves *because i moved*. Elastic attenuation makes
    G[i,j] fall off with hop-distance; the self-model is the graph recovered from
    it (nearest neighbour per zone -> chain order via spectral seriation). This is
    a purely local read: zone i needs only its own efference copy and whatever it
    hears of j on the broadcast.

Foils:
  * rigid  -- stiff joints: the body moves (near-)rigidly, so its motion is almost
              all whole-body common mode; once that is removed (reafference), no
              differential displacement remains and the self-model does not form.
              Elasticity is what gives the zones something differential to read.
  * frozen -- elastic body, no drive: no movement, no self-model
              (the resolution principle: modulation, not transduction, builds it).

Run:  ../.venv/bin/python self_model_topology.py
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
# The read-out is the model (smn_lab.self_model); the scoring against ground truth
# is the experimenter's (smn_lab.metrics). See docs/self-model-and-measurement.md.
from smn_lab.self_model import transfer
from smn_lab.metrics import curve_vs_hops, seriation_order, order_accuracy, \
    neighbour_accuracy

DT = 0.002
N_SEG = 8                       # a long chain: 7 CAZ joints
T_WARM, T_REC = 4.0, 60.0       # warm-up then record
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
PROPRIO_NOISE = 0.02            # per-sample proprioceptive noise on the joint reading

# --8<-- [start:conditions]
CONDITIONS = {
    #             stiffness  drive?   label
    "elastic":  dict(stiffness=0.6,  drive=True),
    "rigid":    dict(stiffness=80.0, drive=True),
    "frozen":   dict(stiffness=0.6,  drive=False),
}
# --8<-- [end:conditions]


def run_one(cond, seed):
    """Run one body under one condition; return (TAU, VEL): the per-zone efference
    (commanded torque) and afferent motion (joint angular velocity), each
    n_rec x n_joints, common-mode removed."""
    p = CONDITIONS[cond]
    rng = np.random.default_rng(seed)
    xml = build_crawler_xml(n_seg=N_SEG, joint_stiffness=p["stiffness"],
                            joint_damping=0.05, bend_limit_deg=45.0)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)

    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    j_ids = [model.joint(f"j{k}").id for k in range(1, N_SEG)]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    nj = len(j_ids)

    # each zone's own independent, natural drive: an OU torque (mean-reverting).
    tau = np.zeros(nj)
    tau_tc, tau_sig = 0.15, 8.0

    n_warm = int(T_WARM / DT)
    n_rec = int(T_REC / DT)
    TAU = np.zeros((n_rec, nj)); VEL = np.zeros((n_rec, nj))

    for i in range(n_warm + n_rec):
        if p["drive"]:
            tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
            for k in range(nj):
                data.ctrl[aid_p[k]] = float(np.clip(tau[k], 0.0, 2.5))
                data.ctrl[aid_n[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i >= n_warm:
            r = i - n_warm
            TAU[r] = tau
            VEL[r] = np.array([float(data.qvel[v]) for v in j_vadr]) \
                     + rng.normal(0.0, PROPRIO_NOISE, nj)
    # --8<-- [start:commonmode]
    # afferent motion relative to the body: strip the whole-body common mode
    VEL = VEL - VEL.mean(axis=1, keepdims=True)
    # --8<-- [end:commonmode]
    return TAU, VEL


def main():
    seeds = list(range(5))
    results = {}
    for cond in CONDITIONS:
        Cs, curves, oacc, nacc = [], [], [], []
        for s in seeds:
            TAU, VEL = run_one(cond, s)
            C = transfer(TAU, VEL)
            Cs.append(C)
            hs, cv = curve_vs_hops(C)
            curves.append(cv)
            oacc.append(order_accuracy(seriation_order(C)))
            nacc.append(neighbour_accuracy(C))
        results[cond] = dict(
            C=np.mean(Cs, 0), hs=hs, curve=np.mean(curves, 0),
            curve_sd=np.std(curves, 0),
            order_acc=(np.mean(oacc), np.std(oacc)),
            nbr_acc=(np.mean(nacc), np.std(nacc)))

    # ---- report ----
    print(f"\nSelf-model from zone data -- {N_SEG}-segment elastic chain, "
          f"{len(seeds)} seeds\n" + "=" * 64)
    print(f"{'condition':<10}{'order recovery':<18}{'1-hop nbr acc':<16}"
          f"{'transfer 1hop->2hop':<20}")
    for cond, r in results.items():
        oa, osd = r["order_acc"]; na, nsd = r["nbr_acc"]
        c1, c2 = r["curve"][0], r["curve"][1]
        print(f"{cond:<10}{oa:5.2f} +/- {osd:4.2f}     {na:4.2f} +/- {nsd:4.2f}    "
              f"{c1:5.2f} -> {c2:5.2f}")
    print("=" * 64)
    print("Prediction: elastic -> co-movement DECAYS with hops, order recovered "
          "(~1.0);\n            rigid/frozen -> flat/na, order not recovered.\n")

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for cond, r in results.items():
        ax[0].errorbar(r["hs"], r["curve"], yerr=r["curve_sd"], marker="o",
                       capsize=3, label=cond)
    ax[0].set_xlabel("true hop-distance between zones")
    ax[0].set_ylabel("mean transfer gain  |corr(efference$_i$, motion$_j$)|")
    ax[0].set_title("Transfer gain decays with hops (elastic only)")
    ax[0].legend(); ax[0].grid(alpha=0.3)

    im = ax[1].imshow(results["elastic"]["C"], cmap="viridis")
    ax[1].set_title("Elastic: transfer matrix (band = chain adjacency)")
    ax[1].set_xlabel("zone j"); ax[1].set_ylabel("zone i")
    fig.colorbar(im, ax=ax[1], fraction=0.046)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "self_model_topology.png")
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
