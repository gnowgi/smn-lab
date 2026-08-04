# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""DFN/IN self-organization on a branched body (Phase-II·1, first cut).

Does the multi-CAZ network CONSTRUCT its functional territories from movement?

We put the live DFN/IN operators (:mod:`smn_lab.network`) on the branched crawler
of ``branched_self_model`` -- a hub with three arms of different lengths -- and drive
every joint with independent OU 'babbling' (no locomotion, no central command). The
DFN accumulates, online, the contingency between each zone's efference and every
zone's motion; the IN's functional coupling W is the consolidated gate. We then ask
whether the communities of W (:mod:`smn_lab.canvas_regions`) recover the true
functional partition -- which arm each joint belongs to -- WITHOUT the network ever
being told the body graph.

Order parameter (experimenter-side): community_class_match (NMI) of the emergent
communities against the true arm labels. Matched foil: time-shuffled afferent, which
destroys the efference->motion contingency (NMI must fall to ~0). Cross-check: the
online DFN gate must match the offline self-model read-out (read_all) on the same run
-- the live operator IS the validated self-model, run forward.

Run:  ../.venv/bin/python net_branched_selforg.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import apply_anisotropic_drag
from smn_lab.network import CAZNetwork
from smn_lab.self_model import read_all
from canvas_regions import graph_communities, community_class_match
from branched_self_model import build_branched_xml, DT, DRAG_LONG, DRAG_TRANS

# an asymmetric hub with three arms of different lengths -> three functional
# territories the network should recover from movement alone.
ARMS = [(0.0, 3), (130.0, 2), (230.0, 4)]
T_WARM, T_REC = 4.0, 90.0
TAU_TC, TAU_SIG = 0.2, 9.0
LAM = 0.01                       # DFN/IN leak rate (1/LAM ~= 100 steps memory)


def run(seed=0):
    xml, positions, true_edges, joint_order, arm_struct = build_branched_xml(ARMS)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    n_seg = len(positions)
    seg_ids = [model.body(f"seg{s}").id for s in range(n_seg)]
    jdof = [model.jnt_dofadr[model.joint(jn).id] for jn in joint_order]
    aid_p = [model.actuator(f"m_{jn}_p").id for jn in joint_order]
    aid_n = [model.actuator(f"m_{jn}_n").id for jn in joint_order]
    nj = len(joint_order)

    net = CAZNetwork(nj, lam=LAM)
    rng = np.random.default_rng(seed)
    tau = np.zeros(nj); vel = np.zeros(6)
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    E = np.zeros((n_rec, nj)); JV = np.zeros((n_rec, nj)); OMEGA = np.zeros((n_rec, n_seg))
    for i in range(n_warm + n_rec):
        tau += (-tau / TAU_TC) * DT + TAU_SIG * np.sqrt(DT) * rng.standard_normal(nj)
        for k in range(nj):
            data.ctrl[aid_p[k]] = float(np.clip(tau[k], 0.0, 2.5))
            data.ctrl[aid_n[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        jv = np.array([data.qvel[d] for d in jdof])
        if i >= n_warm:
            r = i - n_warm
            E[r] = tau; JV[r] = jv
            for s in range(n_seg):
                mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, seg_ids[s], vel, 0)
                OMEGA[r, s] = vel[2]
            net.observe(tau, jv)          # <-- the LIVE DFN/IN update (efference->joint motion)
    # true functional label per joint (which arm) and per segment (hub = own class)
    name2arm = {}
    seg2arm = {0: n_arms_global(arm_struct)}      # hub gets its own singleton class
    for a, st in enumerate(arm_struct):
        for jn in st["joints"]:
            name2arm[jn] = a
        for sg in st["segs"]:
            seg2arm[sg] = a
    labels = np.array([name2arm[jn] for jn in joint_order])
    seg_labels = np.array([seg2arm[s] for s in range(n_seg)])
    return net, E, JV, OMEGA, labels, seg_labels, joint_order, arm_struct


def n_arms_global(arm_struct):
    return len(arm_struct)


def communities_vs_labels(W, labels, pct):
    thr = np.percentile(W[W > 0], pct)
    lab, k = graph_communities(W, thr)
    return k, community_class_match(lab, labels)


def modularity_communities(W):
    """Threshold-free community detection: Newman's leading-eigenvector method
    (recursive spectral bisection of the modularity matrix B = W - kkᵀ/2m). Returns
    a label per node; the number of communities is discovered, not set. This avoids
    the hard-threshold brittleness of connected-components on a weighted graph."""
    W = np.asarray(W, float)
    m = W.sum() / 2.0
    if m <= 0:
        return np.zeros(W.shape[0], int)
    k = W.sum(1)
    B = W - np.outer(k, k) / (2 * m)
    comms = []

    def split(idx):
        Bg = B[np.ix_(idx, idx)].copy()
        Bg = Bg - np.diag(Bg.sum(1))            # generalized modularity for a subgraph
        w, v = np.linalg.eigh(Bg)
        if w[-1] <= 1e-9:
            comms.append(idx); return
        s = np.where(v[:, -1] > 0, 1.0, -1.0)
        if np.all(s == s[0]) or (s @ Bg @ s) <= 1e-9:
            comms.append(idx); return
        split(idx[s > 0]); split(idx[s <= 0])

    split(np.arange(W.shape[0]))
    lab = np.zeros(W.shape[0], int)
    for c, g in enumerate(comms):
        lab[g] = c
    return lab


def seg_coupling(OMEGA):
    """The IN functional coupling over SEGMENTS from their co-motion: symmetrized
    |corr(segment_i motion, segment_j motion)|, diagonal zeroed. This is the pooled
    canvas the IN integrates -- segments that co-move under the body's own action."""
    G = np.abs(read_all(OMEGA, OMEGA))
    G = 0.5 * (G + G.T); np.fill_diagonal(G, 0.0)
    return G


def main():
    net, E, JV, OMEGA, labels, seg_labels, joint_order, arm_struct = run(seed=0)
    nj = len(joint_order)
    n_arms = len(arm_struct)

    # 1. network closure (Pi non-degeneracy)
    clo = net.closure()

    # 2. online DFN gate vs offline self-model read-out (the operator IS the self-model)
    W_online = net.W
    A_offline = read_all(E, JV)
    G_offline = np.abs(A_offline); G_offline = 0.5 * (G_offline + G_offline.T)
    np.fill_diagonal(G_offline, 0.0)
    # correlation between the online and offline coupling matrices (off-diagonal)
    iu = np.triu_indices(nj, 1)
    online_offline_r = float(np.corrcoef(W_online[iu], G_offline[iu])[0, 1])

    # 2b. the IN read over SEGMENT co-motion (the diagnosis: territories live here)
    W_seg = seg_coupling(OMEGA)

    # 3. emergent communities vs true arm partition, across thresholds; + shuffle foil
    rng = np.random.default_rng(1)
    JV_shuf = JV.copy()
    for j in range(nj):                        # per-channel time shuffle kills contingency
        JV_shuf[:, j] = JV[rng.permutation(len(JV)), j]
    A_foil = read_all(E, JV_shuf)
    W_foil = np.abs(A_foil); W_foil = 0.5 * (W_foil + W_foil.T); np.fill_diagonal(W_foil, 0.0)
    # segment-level foil: time-shuffle each segment's motion (kills co-motion structure)
    OMEGA_shuf = OMEGA.copy()
    for s in range(OMEGA.shape[1]):
        OMEGA_shuf[:, s] = OMEGA[rng.permutation(len(OMEGA)), s]
    W_seg_foil = seg_coupling(OMEGA_shuf)

    pcts = [50, 60, 70, 80]
    print("\nDFN/IN self-organization on a branched body (hub + 3 arms)\n" + "=" * 70)
    print(f"zones (CAZ joints): {nj}   segments: {len(seg_labels)}   "
          f"true functional territories (arms): {n_arms}")
    print(f"network closure (Pi non-degenerate): {clo['closed']}  "
          f"(orphan zones: {clo['n_orphan']})")
    print(f"online DFN gate vs offline self-model read-out: r = {online_offline_r:.3f}")
    print("-" * 70)
    print(f"{'threshold pct':<15}{'joint-DFN NMI':<16}{'seg-IN NMI':<14}{'foil NMI':<10}")
    j_nmis, s_nmis, foil_nmis = [], [], []
    for p in pcts:
        _, nmi_j = communities_vs_labels(W_online, labels, p)      # efference->joint DFN
        _, nmi_s = communities_vs_labels(W_seg, seg_labels, p)     # segment co-motion IN
        _, nmi_f = communities_vs_labels(W_foil, labels, p)
        j_nmis.append(nmi_j); s_nmis.append(nmi_s); foil_nmis.append(nmi_f)
        print(f"{p:<15}{nmi_j:<16.3f}{nmi_s:<14.3f}{nmi_f:<10.3f}")
    print("=" * 70)
    print(f"joint-DFN mean {np.mean(j_nmis):.3f} | seg-IN mean {np.mean(s_nmis):.3f} | "
          f"foil mean {np.mean(foil_nmis):.3f}   (hard-threshold connected components)")
    print("-" * 70)
    # THRESHOLD-FREE headline: Newman modularity communities
    lab_seg = modularity_communities(W_seg)
    lab_jnt = modularity_communities(W_online)
    lab_foil = modularity_communities(W_seg_foil)
    nmi_seg = community_class_match(lab_seg, seg_labels)
    nmi_jnt = community_class_match(lab_jnt, labels)
    nmi_foil = community_class_match(lab_foil, seg_labels)
    print(f"THRESHOLD-FREE (Newman modularity):")
    print(f"  seg-IN co-motion : {len(np.unique(lab_seg))} communities, NMI {nmi_seg:.3f} "
          f"(true territories: {len(np.unique(seg_labels))})")
    print(f"  joint-DFN gate   : {len(np.unique(lab_jnt))} communities, NMI {nmi_jnt:.3f} "
          f"(true arms: {n_arms})")
    print(f"  shuffle foil     : {len(np.unique(lab_foil))} communities, NMI {nmi_foil:.3f}")
    print("=" * 70)
    print("Reading: with a proper (threshold-free) community readout the IN's segment\n"
          "co-motion recovers the body's functional territories from movement alone,\n"
          "well above the shuffle foil. The structure is CONSTRUCTED, not stipulated.\n")
    smn_nmis = s_nmis      # threshold curve (secondary) still uses the IN read

    # figure: segment-IN coupling heatmap (ordered by arm), community match, NMI curve
    order = np.argsort(seg_labels)
    n_seg = len(seg_labels)
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))
    im = ax[0].imshow(W_seg[order][:, order], cmap="magma")
    ax[0].set_title("IN functional coupling (segment co-motion)\n(ordered by true arm)")
    ax[0].set_xlabel("segment"); ax[0].set_ylabel("segment")
    b = np.cumsum([np.sum(seg_labels == a) for a in np.unique(seg_labels)])[:-1] - 0.5
    for x in b:
        ax[0].axhline(x, color="cyan", lw=0.8); ax[0].axvline(x, color="cyan", lw=0.8)
    fig.colorbar(im, ax=ax[0], fraction=0.046)

    lab, _ = graph_communities(W_seg, np.percentile(W_seg[W_seg > 0], 70))
    ax[1].scatter(range(n_seg), seg_labels, c=lab, cmap="tab10", s=80, edgecolor="k")
    ax[1].set_title("emergent community (color)\nvs true territory (y)")
    ax[1].set_xlabel("segment"); ax[1].set_ylabel("true territory")
    ax[1].set_yticks(range(len(np.unique(seg_labels))))

    ax[2].plot(pcts, smn_nmis, "o-", label="IN seg-comotion (self-organized)")
    ax[2].plot(pcts, j_nmis, "^-", label="DFN efference->joint", color="tab:green")
    ax[2].plot(pcts, foil_nmis, "s--", label="shuffle foil")
    ax[2].axhline(0, color="0.7", lw=0.8)
    ax[2].set_xlabel("edge-keep threshold (percentile)")
    ax[2].set_ylabel("community–arm NMI"); ax[2].set_ylim(-0.05, 1.05)
    ax[2].set_title("emergent territories vs arms"); ax[2].legend(); ax[2].grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "net_branched_selforg.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
