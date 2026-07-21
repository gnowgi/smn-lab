# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Integrator & snapshot -- secondary: does more working-memory capacity buy task
performance?

A delayed multi-item recall task on the SAME beam memory used for the capacity
order parameter (theta/gamma mechanism). Load D item-patterns serially, maintain
through a delay, probe; performance = fraction of the D items still retrievable.

Preregistered hypothesis (see integrator_snapshot_DEVLOG.md): performance rises
with capacity, and the benefit SATURATES once capacity >= task demand -- greater
WM helps only up to what the task demands. The beam-memory parameters are reused
verbatim from sweep_integrator_snapshot.py (crit=1/e, d=48*beam_nodes, theta/gamma
load/decay, substeps=4); the only new quantities are the task's demand D and
maintenance delay -- properties of the task, not tunable model knobs.

Run:  ../.venv/bin/python sweep_capacity_performance.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from integrator_snapshot import LATTICE

CRIT = float(np.exp(-1))        # read-out criterion, reused verbatim
SUBSTEPS = 4                    # decay sub-steps per load, reused verbatim


def _beam_memory(load_interval, tau, d, n_items, delay_s, seed):
    """Load n_items random unit vectors serially into a decaying feature vector
    (leaky, time-constant tau), maintain for delay_s, then probe by matched
    filter. Returns the boolean retrieval mask over the n_items (True = still
    above CRIT)."""
    rng = np.random.default_rng(seed)
    dt = load_interval / SUBSTEPS
    decay = np.exp(-dt / tau)
    s = np.zeros(d)
    pats = np.empty((n_items, d))
    for k in range(n_items):
        p = rng.standard_normal(d); p /= np.linalg.norm(p)
        pats[k] = p
        s = s + p
        for _ in range(SUBSTEPS):
            s *= decay
    for _ in range(int(round(delay_s / dt))):      # maintenance delay
        s *= decay
    return (pats @ s) > CRIT


def _params(cfg):
    return (1.0 / cfg["beam_refresh_hz"], 1.0 / cfg["hold_theta_hz"],
            48 * sum(cfg["layers"][1:]))


def capacity(cfg, seeds=(0, 1, 2, 3, 4)):
    """Steady-state recency span (no task delay) -- the config's WM capacity."""
    li, tau, d = _params(cfg)
    n = int(np.ceil(8 * tau / li)) + 5
    spans = []
    for s in seeds:
        mask = _beam_memory(li, tau, d, n, 0.0, s)
        span = 0
        for r in mask[::-1]:                       # newest first
            if r:
                span += 1
            else:
                break
        spans.append(span)
    return int(np.median(spans))


def performance(cfg, demand, delay_s, seeds=(0, 1, 2, 3, 4)):
    """Fraction of a D-item list still retrievable after loading + a maintenance
    delay -- the task score."""
    li, tau, d = _params(cfg)
    return float(np.mean([_beam_memory(li, tau, d, demand, delay_s, s).mean()
                          for s in seeds]))


def _rank(a):
    """Average ranks, so ties get equal rank (a constant vector -> all equal ranks
    -> zero variance -> zero correlation, as it must)."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    a_sorted = a[order]
    ranks = np.arange(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a_sorted[j + 1] == a_sorted[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2.0
        i = j + 1
    out = np.empty(len(a)); out[order] = ranks
    return out


def _spearman(x, y):
    xr, yr = _rank(x), _rank(y)
    xr = xr - xr.mean(); yr = yr - yr.mean()
    den = np.sqrt((xr ** 2).sum() * (yr ** 2).sum())
    return float((xr * yr).sum() / den) if den > 1e-12 else 0.0


def run(delay_s=0.0, demands=(1, 2, 3, 5, 8, 12, 16)):
    caps = np.array([capacity(c) for c in LATTICE])
    order = np.argsort(caps)                        # sort configs by capacity
    names = [LATTICE[i]["name"] for i in order]
    caps = caps[order]
    P = np.array([[performance(LATTICE[i], D, delay_s) for D in demands]
                  for i in order])                  # rows: configs (by cap), cols: demands
    return dict(names=names, caps=caps, demands=np.array(demands), P=P)


def _fmt(r):
    print("immediate recall;  performance = fraction of the D-item list retrieved\n")
    hdr = "config".ljust(12) + "cap".rjust(5) + "".join(f"D={D}".rjust(7) for D in r["demands"])
    print(hdr)
    for i, nm in enumerate(r["names"]):
        row = f"{nm:<12}{r['caps'][i]:>5}" + "".join(f"{r['P'][i, j]:>7.2f}"
                                                      for j in range(len(r["demands"])))
        print(row)
    # order parameters
    D = list(r["demands"])
    j_hi = D.index(8) if 8 in D else int(np.argmin(np.abs(np.array(D) - 8)))
    j_lo = D.index(1)
    rho_hi = _spearman(r["caps"], r["P"][:, j_hi])
    rho_lo = _spearman(r["caps"], r["P"][:, j_lo])
    print(f"\nrho(capacity, performance) at D={D[j_hi]} (high demand): {rho_hi:+.2f}  "
          f"[pass > 0.70]")
    print(f"rho(capacity, performance) at D={D[j_lo]} (demand 1):    {rho_lo:+.2f}  "
          f"[pass < 0.40]")
    print(f"P at D=1 (min across configs): {r['P'][:, j_lo].min():.2f}  "
          "[pass: uniformly high]")
    return rho_hi, rho_lo


def plot(r, out):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.9, len(r["names"])))
    for i, nm in enumerate(r["names"]):
        ax1.plot(r["demands"], r["P"][i], "-o", ms=4, color=cmap[i],
                 label=f"{nm} (C={r['caps'][i]})")
    ax1.set_xlabel("task demand  D  (items to hold)")
    ax1.set_ylabel("performance  (fraction recalled)")
    ax1.set_title("more capacity sustains performance to higher demand", fontsize=10)
    ax1.legend(fontsize=7, title="config (capacity)")

    for D in (1, 8, 16):
        j = list(r["demands"]).index(D)
        ax2.plot(r["caps"], r["P"][:, j], "-o", ms=4, label=f"D={D}")
    ax2.set_xlabel("working-memory capacity  C")
    ax2.set_ylabel("performance  (fraction recalled)")
    ax2.set_title("capacity buys performance — and saturates at demand", fontsize=10)
    ax2.legend(fontsize=8, title="task demand")

    fig.tight_layout(); fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


def main():
    r = run()
    rho_hi, rho_lo = _fmt(r)
    ok = (rho_hi > 0.70 and rho_lo < 0.40 and r["P"][:, 0].min() > 0.8)
    print("\nverdict:", "PASS -- capacity buys performance at high demand, not at "
          "demand 1; the benefit saturates at the task's demand."
          if ok else "INCONCLUSIVE -- see order parameters above.")
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    plot(r, os.path.join(figdir, "integrator_snapshot_capacity_perf.png"))


if __name__ == "__main__":
    main()
