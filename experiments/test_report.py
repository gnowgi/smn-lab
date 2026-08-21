# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Thorough self-test of the always-invoked results module (smn_lab.report).

Synthetic records with KNOWN structure, so we can assert the module recovers it:
  * a chain body (correlated co-motion) -> chain recovered, 1 region, order ~ true;
  * a branched Y body (signed coupling) -> branch point found, edges exact, N_D>1;
  * a localized world source -> source lands on the right node (ordinal, label-based);
  * property tests: relabeling invariance and frame (reflection) relativity;
  * figures render and the machine-readable results JSON is written and valid.

Run:  MPLBACKEND=Agg ../.venv/bin/python test_report.py
"""
from __future__ import annotations
import os, sys, json, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.report import RunRecord, render, recover, diagnostics

TMP = tempfile.mkdtemp(prefix="report_test_")
SPEC = dict(outdir=TMP, results_dir=TMP)
PASS = []


def check(name, cond):
    PASS.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def chain_omega(n=8, T=4000, tau=1.2, seed=0):
    """Synthetic co-motion for a chain: covariance decays with |i-j| along the body,
    so neighbours co-move most -> the transfer read-out recovers the chain order."""
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    K = np.exp(-np.abs(idx[:, None] - idx[None, :]) / tau)
    L = np.linalg.cholesky(K + 1e-9 * np.eye(n))
    return rng.standard_normal((T, n)) @ L.T


def signed_Y():
    """Signed coupling C[joint, seg] for a Y body: segs 0..6, hub 0, three arms
    0-1-2, 0-3-4, 0-5-6. Each joint row marks +child / -parent."""
    edges = [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6)]
    n = 7
    C = np.zeros((len(edges), n))
    for j, (parent, child) in enumerate(edges):
        C[j, child] = 1.0; C[j, parent] = -1.0
        C[j] += 0.01 * np.random.default_rng(j).standard_normal(n)   # mild noise
    return C, edges


def abs_rankcorr(x, y):
    rx = np.argsort(np.argsort(x)).astype(float); ry = np.argsort(np.argsort(y)).astype(float)
    return abs(np.corrcoef(rx, ry)[0, 1])


def test_chain():
    print("\n== chain body ==")
    n = 8
    om = chain_omega(n=n)
    nf = {k: float(np.exp(-((k - (n - 1)) ** 2) / 2.0)) for k in range(n)}  # source at the tail
    rec = RunRecord(name="t_chain", omega=om, node_field=nf,
                    metrics=dict(order_acc=0.99, tracking=1.0))
    out = render(rec, dict(SPEC, prefix="t_chain"))
    d = out["diagnostics"]
    check("recovered as a chain (no branch point)", d["is_chain"] is True)
    check("one region (undivided body)", d["n_regions"] == 1)
    check("n_edges == n-1", d["n_edges"] == n - 1)
    check("recovered order matches true chain up to reflection",
          abs_rankcorr(out["recovered"]["order"], np.arange(n)) > 0.98)
    check("source localized at the tail node", out["recovered"]["source_node"] == n - 1)
    check("card + op-plot figures written", all(os.path.exists(f) for f in out["figures"]) and len(out["figures"]) == 2)
    check("results JSON valid", json.load(open(out["results_json"]))["name"] == "t_chain")


def test_branched():
    print("\n== branched (Y) body ==")
    C, edges = signed_Y()
    rec = RunRecord(name="t_Y", coupling_matrix=C,
                    positions={0: (0, 0), 1: (1, .3), 2: (2, .6), 3: (1, -.3),
                               4: (2, -.6), 5: (-1, 0), 6: (-2, 0)},
                    true_edges=edges)
    out = render(rec, dict(SPEC, prefix="t_Y"))
    d = out["diagnostics"]
    got = {frozenset(e) for e in out["recovered"]["rec_edges"]}
    want = {frozenset(e) for e in edges}
    check("branch point recovered at the hub (seg 0)", d["branch_node"] == 0)
    check("not flagged as a chain", d["is_chain"] is False)
    check("recovered edges == true Y edges", got == want)
    check("max degree == 3 (the hub)", d["max_degree"] == 3)
    check("N_D > 1 (arm symmetry -> degenerate spectrum)", d["N_D"] > 1)
    check("driver set size == N_D", d.get("driver_nodes") is not None and len(d["driver_nodes"]) == d["N_D"])


def test_relabeling_invariance():
    print("\n== property: relabeling invariance ==")
    n = 8
    om = chain_omega(n=n, seed=3)
    base = diagnostics(recover(RunRecord(name="b", omega=om)), RunRecord(name="b", omega=om))
    perm = np.random.default_rng(1).permutation(n)
    rec2 = RunRecord(name="p", omega=om[:, perm])
    perm_d = diagnostics(recover(rec2), rec2)
    check("is_chain invariant to relabeling", base["is_chain"] == perm_d["is_chain"])
    check("n_regions invariant to relabeling", base["n_regions"] == perm_d["n_regions"])
    check("N_D invariant to relabeling", base["N_D"] == perm_d["N_D"])
    check("algebraic connectivity invariant to relabeling",
          abs(base["algebraic_connectivity"] - perm_d["algebraic_connectivity"]) < 1e-9)


def test_frame_relativity():
    print("\n== property: frame (reflection) relativity ==")
    n = 8
    # a source at node 2 must localize at label 2 regardless of the recovered
    # order's arbitrary head/tail direction
    om = chain_omega(n=n, seed=7)
    nf = {k: float(np.exp(-((k - 2) ** 2) / 2.0)) for k in range(n)}
    out = render(RunRecord(name="t_frame", omega=om, node_field=nf), dict(SPEC, prefix="t_frame"))
    order = out["recovered"]["order"]
    check("order is a chain up to reflection", abs_rankcorr(order, np.arange(n)) > 0.98)
    check("source localizes on the correct LABEL (frame-independent)",
          out["recovered"]["source_node"] == 2)


def hydra_world_signal(n=6, T=300, w=25.0):
    """A SESSILE agent (no displacement): prey is conveyed across the tentacle zones,
    so each zone's world-caused signal peaks in sequence -> a dependency trajectory the
    canvas should recover as strata."""
    t = np.arange(T)
    tk = 40 + 38 * np.arange(n)                         # zone k peaks later than k-1
    return np.stack([np.exp(-((t - tk[k]) / w) ** 2) for k in range(n)], axis=1)


def test_canvas_always_on():
    print("\n== canvas built from modulation (sessile hydra, no displacement) ==")
    n = 6
    om = chain_omega(n=n, seed=5)                       # the tentacle self-model co-motion
    ws = hydra_world_signal(n=n)                        # world-caused signal per zone over time
    out = render(RunRecord(name="t_hydra", omega=om, world_signal=ws,
                           metrics={"prey_captured": 1.0}),
                 dict(SPEC, prefix="t_hydra"))
    d = out["diagnostics"]
    check("canvas was constructed with NO displacement", "canvas_live_strata" in d)
    check("world trajectory emerged as strata (>1)", d.get("canvas_live_strata", 0) > 1)
    check("canvas has at least one region", d.get("canvas_live_regions", 0) >= 1)
    check("canvas figure written", any(f.endswith("t_hydra_canvas.png") for f in out["figures"]))
    check("proximal snapshot derived from the world signal (source on a real node)",
          out["recovered"]["source_node"] in range(n))


def main():
    print(f"results/figs -> {TMP}")
    test_chain(); test_branched(); test_relabeling_invariance(); test_frame_relativity()
    test_canvas_always_on()
    n_ok, n = sum(PASS), len(PASS)
    print(f"\n{'=' * 60}\nreport module self-test: {n_ok}/{n} checks passed "
          f"[{'ALL PASS' if n_ok == n else 'FAILURES'}]")
    sys.exit(0 if n_ok == n else 1)


if __name__ == "__main__":
    main()
