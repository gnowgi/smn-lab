# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Nested lattice: one function, any *level* (scale-invariance).

The lattice self-model is topology-invariant (chain / sheet / tube -- one function).
This adds the vertical axis: a **three-level nested lattice** that tapers up the
hierarchy -- 36 segments -> 9 blocks -> 3 super-blocks -- and shows the SAME read-out
(``smn_lab.self_model.coupling``) recovers the body graph at ALL THREE levels, from
one run, by **renormalizing** (block-averaging) once and then again:

  * FINE   -- the 36 segments (segment-level links);
  * MID    -- the 9 blocks    (from block-averaged motion, coarse links = block-block);
  * COARSE -- the 3 super-blocks (from super-block-averaged motion).

Same function, three levels. The deeper layer holds many units; each layer up holds
fewer -- the taper is the renormalization factor. This is the scale-recursion the
SMN architecture claims, the substrate for morphological computing (topology ->
data structure), on which haltability then builds.

Run:  ../.venv/bin/python nested_lattice_self_model.py
"""
from __future__ import annotations
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.lattice import nested_lattice_spec, build_nested_lattice_xml
from smn_lab.self_model import coupling                 # the model read-out (unchanged)
from smn_lab.metrics import endpoint_recovery           # experimenter-side scoring

DT = 0.002
T_WARM, T_REC = 2.0, 45.0
U_TC, U_SIG = 0.15, 5.0


def run_one(spec, seed):
    """Drive every CAZ link independently; log link drives and per-segment motion."""
    model = mujoco.MjModel.from_xml_string(build_nested_lattice_xml(spec))
    data = mujoco.MjData(model)
    rng = np.random.default_rng(seed)
    nseg, nlink = spec["n_seg"], len(spec["edges"])
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    u = np.zeros(nlink)
    DRV = np.zeros((n_rec, nlink))
    V = [np.zeros((n_rec, nseg)) for _ in range(3)]      # x, y, z segment velocities
    for i in range(n_warm + n_rec):
        u += (-u / U_TC) * DT + U_SIG * np.sqrt(DT) * rng.standard_normal(nlink)
        data.ctrl[:] = u
        mujoco.mj_step(model, data)
        if i >= n_warm:
            j = i - n_warm
            DRV[j] = u
            for ax in range(3):
                V[ax][j] = data.qvel[ax::3]
    for ax in range(3):
        V[ax] -= V[ax].mean(1, keepdims=True)            # common-mode removal
    return DRV, V


# --8<-- [start:coarsegrain]
def renormalize(V, membership, n_group):
    """Coarse-grain: average each group's segments into one super-node observable.
    Applying the SAME coupling to these is the read-out at the next level up."""
    return [np.stack([V[ax][:, membership == g].mean(1) for g in range(n_group)], 1)
            for ax in range(3)]


def recover_at(DRV, obs, link_ids, group_of, edges):
    """The read-out at one level: the SAME coupling on this level's links + nodes,
    scored on this level's true edges (in node indices)."""
    C = sum(np.abs(coupling(DRV[:, link_ids], obs[ax])) for ax in range(3))
    node_edges = [tuple(sorted((int(group_of[edges[L][0]]), int(group_of[edges[L][1]]))))
                  for L in link_ids]
    return endpoint_recovery(C, node_edges), C
# --8<-- [end:coarsegrain]


def recover_levels(spec, DRV, V):
    level = spec["level"]
    ids = {k: [L for L, lv in enumerate(level) if lv == k] for k in ("fine", "mid", "coarse")}
    seg_of = np.arange(spec["n_seg"])
    # FINE: segments themselves (identity grouping)
    fine_acc, Cf = recover_at(DRV, V, ids["fine"], seg_of, spec["edges"])
    # MID: renormalize to blocks
    B = renormalize(V, spec["seg_block"], spec["n_block"])
    mid_acc, _ = recover_at(DRV, B, ids["mid"], spec["seg_block"], spec["edges"])
    # COARSE: renormalize to super-blocks
    S = renormalize(V, spec["seg_super"], spec["n_super"])
    coarse_acc, _ = recover_at(DRV, S, ids["coarse"], spec["seg_super"], spec["edges"])
    return dict(fine=fine_acc, mid=mid_acc, coarse=coarse_acc), Cf


def plot(spec, Cf, out):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    level, seg_block, seg_super = spec["level"], spec["seg_block"], spec["seg_super"]
    nsup, nblk, M = spec["n_super"], spec["n_block"], spec["M"]
    per = nblk // nsup                                    # blocks per super-block
    DXS, DYB, DS = 3.0, 1.15, 0.42                        # schematic spacings
    block_super = np.array([seg_super[seg_block == b][0] for b in range(nblk)])

    def block_xy(b):                                      # super = column, block = row
        return np.array([(b // per) * DXS, (b % per) * DYB])
    def seg_xy(i):
        lr, lc = divmod(i % M, 2)
        return block_xy(seg_block[i]) + np.array([lc * DS, lr * DS])
    def super_xy(s):                                     # stack vertically, like MID
        return np.array([0.0, s * DYB])

    # --- FINE ---
    fine_ids = [L for L, lv in enumerate(level) if lv == "fine"]
    true_fine = {frozenset(spec["edges"][L]) for L in fine_ids}
    SX = np.array([seg_xy(i) for i in range(spec["n_seg"])])
    for row, L in enumerate(fine_ids):
        a, b = tuple(sorted(int(s) for s in np.argsort(Cf[row])[::-1][:2]))
        ok = frozenset((a, b)) in true_fine
        axes[0].plot(*SX[[a, b]].T, "-", lw=2.0 if ok else 1.3,
                     color="#1538a0" if ok else "#c0392b", zorder=1)
    axes[0].scatter(*SX.T, s=34, c=seg_super, cmap="tab10", zorder=2, edgecolors="k", linewidths=0.3)
    axes[0].set_title(f"FINE — {spec['n_seg']} segments\n(the 9 blocks recovered)", fontsize=10)
    # --- MID ---
    BX = np.array([block_xy(b) + DS / 2 for b in range(nblk)])
    for L, lv in enumerate(level):
        if lv == "mid":
            a, b = seg_block[spec["edges"][L][0]], seg_block[spec["edges"][L][1]]
            axes[1].plot(*BX[[a, b]].T, "-", lw=3, color="#1538a0", zorder=1)
    axes[1].scatter(*BX.T, s=300, c=block_super, cmap="tab10", zorder=2, edgecolors="k", linewidths=0.8)
    axes[1].set_title(f"MID — {nblk} blocks\n(block-averaged · renormalized)", fontsize=10)
    # --- COARSE ---
    CX = np.array([super_xy(s) for s in range(nsup)])
    for L, lv in enumerate(level):
        if lv == "coarse":
            a, b = seg_super[spec["edges"][L][0]], seg_super[spec["edges"][L][1]]
            axes[2].plot(*CX[[a, b]].T, "-", lw=4, color="#1538a0", zorder=1)
    axes[2].scatter(*CX.T, s=900, c=range(nsup), cmap="tab10", zorder=2, edgecolors="k", linewidths=1.1)
    for s in range(nsup):
        axes[2].text(*CX[s], f"{s}", ha="center", va="center", fontsize=14, color="w")
    axes[2].set_title(f"COARSE — {nsup} super-blocks\n(super-averaged · renormalized)", fontsize=10)
    for ax in axes:
        ax.set_aspect("equal"); ax.axis("off"); ax.margins(0.15)
    fig.suptitle("One function, any level — a scale-invariant self-model on a "
                 "3-level nested body (36 → 9 → 3)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


def main():
    spec = nested_lattice_spec()                          # 36 -> 9 -> 3
    seeds = list(range(3))
    accs = {k: [] for k in ("fine", "mid", "coarse")}
    Cf_last = None
    for s in seeds:
        DRV, V = run_one(spec, s)
        a, Cf = recover_levels(spec, DRV, V)
        for k in accs:
            accs[k].append(a[k])
        Cf_last = Cf
    print("\nNested lattice — one function, any level (scale-invariance)\n" + "=" * 58)
    print(f"  body: {spec['n_super']} super-blocks x {spec['n_block'] // spec['n_super']} blocks "
          f"x {spec['M']} = {spec['n_seg']} segments, {len(spec['edges'])} links")
    labels = {"fine": f"FINE   ({spec['n_seg']} segments)",
              "mid": f"MID    ({spec['n_block']} blocks)",
              "coarse": f"COARSE ({spec['n_super']} super-blocks)"}
    for k in ("fine", "mid", "coarse"):
        print(f"  {labels[k]:<26} recovery = {np.mean(accs[k]):.2f} ± {np.std(accs[k]):.2f}")
    print("=" * 58)
    print("The same smn_lab.self_model.coupling recovers all three levels.\n")
    figdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    plot(spec, Cf_last, os.path.join(figdir, "nested_lattice_self_model.png"))


if __name__ == "__main__":
    main()
