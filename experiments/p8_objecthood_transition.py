# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""E4b --- the onset of objecthood as a coupling-density transition.

E4 established that each zone reliably registers one differentia (a difference;
hard/soft read at accuracy 1.00) and that the world model scales 2^K with the
zones the board *binds*. Here we ask the network-physics question that follows:
as the board's coupling density rises, *when* do differentiae bind into an object?

Model the board as a random graph G(K, p): each pair of zones is coupled with
probability p, and composition binds zones within a connected component (coupled
zones share their differentiae into one joint code). The richest single object the
agent can hold is then the largest bound component, and its capacity is
2^(largest component). Sweeping p, this undergoes a **percolation-like
transition**: below a critical coupling density the differentiae stay fragmented
(no object), and a giant bound object emerges past it. The per-zone differentiae
are the real bench reads (E4); what is swept here is the board's connectivity.

This is the onset of objecthood as a phase transition in a complex network --- a
question for random-matrix / network-dynamics methods, on a system the bench
supplies.

Run:  ../.venv/bin/python p8_objecthood_transition.py
Outputs: ../figures/p8_objecthood_transition.png
"""
from __future__ import annotations
import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

K = 24                      # zones in the body's modulation network
TRIALS = 400               # random boards averaged per coupling density
P_MAX = 0.32
N_P = 40
SEED = 7


def largest_component(adj_pairs, k):
    """Union-find over coupled pairs; return the size of the largest component."""
    parent = list(range(k))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in adj_pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    sizes = {}
    for i in range(k):
        r = find(i)
        sizes[r] = sizes.get(r, 0) + 1
    return max(sizes.values())


def sweep():
    rng = np.random.default_rng(SEED)
    ps = np.linspace(0.0, P_MAX, N_P)
    iu = np.triu_indices(K, 1)                      # candidate undirected edges
    S = np.zeros(N_P)                               # order parameter: largest comp / K
    cap = np.zeros(N_P)                             # capacity: 2^(largest comp)
    for j, p in enumerate(ps):
        lc = np.zeros(TRIALS)
        for t in range(TRIALS):
            mask = rng.random(iu[0].shape[0]) < p
            pairs = list(zip(iu[0][mask].tolist(), iu[1][mask].tolist()))
            lc[t] = largest_component(pairs, K)
        S[j] = lc.mean() / K
        cap[j] = float(np.mean(2.0 ** lc))         # mean richest-object capacity
    return ps, S, cap


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    ps, S, cap = sweep()
    p_giant = 1.0 / K                              # giant-component onset
    p_conn = math.log(K) / K                       # full connectivity

    print("\n=== E4b — onset of objecthood as a coupling-density transition ===")
    print(f"  K={K} zones; p_c(giant)=1/K={p_giant:.3f}; p_c(connected)=lnK/K={p_conn:.3f}")
    for frac in (0.5, 1.0, 2.0):
        p = frac * p_giant
        j = int(np.argmin(np.abs(ps - p)))
        print(f"  p={ps[j]:.3f} (={frac:g}/K): largest bound object = {S[j]*K:4.1f}/{K} zones "
              f"-> capacity 2^{S[j]*K:.0f}")

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.8))

    axA.plot(ps, S, "o-", color="#2c6a9c", lw=2, ms=3)
    axA.axvline(p_giant, color="#b03030", ls="--", lw=1, label=r"$p_c=1/K$ (giant object)")
    axA.axvline(p_conn, color="#c08a3e", ls=":", lw=1, label=r"$p=\ln K/K$ (fully bound)")
    axA.set_xlabel("board coupling density $p$")
    axA.set_ylabel("largest bound object / $K$  (order parameter)")
    axA.set_title("Onset of objecthood: a giant bound object\nemerges past a critical coupling density", fontsize=10)
    axA.legend(fontsize=8); axA.grid(alpha=0.25)

    axB.semilogy(ps, cap, "o-", color="#2c7a2c", lw=2, ms=3)
    axB.axvline(p_giant, color="#b03030", ls="--", lw=1)
    axB.axvline(p_conn, color="#c08a3e", ls=":", lw=1)
    axB.set_xlabel("board coupling density $p$")
    axB.set_ylabel("world-model capacity  $2^{\\mathrm{largest\\ bound\\ object}}$")
    axB.set_title("World-model capacity jumps at the transition", fontsize=10)
    axB.grid(alpha=0.25, which="both")

    fig.suptitle(f"E4b --- the world model's objecthood is a percolation-like transition in the "
                 f"board's coupling density (K={K} zones)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(figdir, "p8_objecthood_transition.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
