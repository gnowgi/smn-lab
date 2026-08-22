# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""World-model across morphologies -- one WORLD, several BODIES, one pipeline.

A wiring test with real science. We hold the WORLD constant (a single scalar-field
source at a fixed world coordinate) and vary only the AGENT'S MORPHOLOGY: a chain, a
SYMMETRIC branched body, and an ASYMMETRIC branched body. Each body babbles, recovers
its own self-model from that movement, senses the SAME world source at its node
positions, and localizes it in its OWN recovered self-frame.

Crucially, every body goes through the ONE results module (``smn_lab.report``): the
same recovery, the same self/world card, the same always-on emergent diagnostics, the
same machine-readable record. So this doubles as an end-to-end check that the pipeline
is wired correctly for a genuinely new morphology -- including the branched case that
exercises graph-first recovery, branch detection, and N_D (driver count), which a
chain does not.

What we expect (and assert as wiring):
  * chain      -> is_chain, N_D = 1, source lands on some chain node;
  * symmetric  -> branched (hub found), N_D > 1 (interchangeable arms -> degenerate
                  spectrum -- the symmetry shows up in the controllability read-out);
  * asymmetric -> branched (hub found), N_D = 1 (three different arms break the
                  degeneracy);
  * same world, but the source localizes on a body-specific node -> the Umwelt point.

Run:  MPLBACKEND=Agg ../.venv/bin/python worldmodel_across_morphologies.py
"""
from __future__ import annotations
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smn_lab import self_model as sm
from smn_lab.fields import ScalarField
from smn_lab.report import RunRecord, render
from branched_self_model import run, CONFIGS

# THE CONSTANT WORLD: one field source at a fixed world coordinate, same for every body.
WORLD = ScalarField([(0.35, 0.25, 1.0, 0.30)])

MORPHS = {
    "chain":      [(0.0, 7)],                          # a single straight arm
    "symmetric":  [(90.0, 3), (210.0, 3), (330.0, 3)],  # THREE equal arms (S3 star) -> N_D>1
    "asymmetric": CONFIGS["asymmetric"],               # three different arms -> N_D=1
}


def edge_recovery(C, true_edges):
    """Experimenter-side: fraction of recovered edges that are true body edges."""
    tset = {frozenset(e) for e in true_edges}
    rec = sm.recover_edges(C)
    return float(np.mean([frozenset(e) in tset for e in rec])) if rec else 0.0


def main():
    rows = []
    for name, arms in MORPHS.items():
        JV, OMEGA, positions, true_edges, joint_order, arm_struct = run(arms)
        # the body's self-model coupling, recovered from its OWN movement
        C = sm.coupling(JV, OMEGA)
        # the SAME world, sensed at THIS body's node positions
        node_field = {n: float(WORLD.sample(*positions[n])) for n in positions}
        er = edge_recovery(C, true_edges)

        out = render(
            RunRecord(
                name=f"morph_{name}",
                coupling_matrix=C,               # signed -> graph-first recovery
                positions=positions, true_edges=true_edges,
                node_field=node_field, modality="chem",
                metrics={"edge_recovery": er,
                         "peak_field": max(node_field.values())},
                meta={"morphology": name, "arms": arms},
            ),
            spec=dict(prefix=f"morph_{name}",
                      suptitle=f"World-model across morphologies — {name} body"),
        )
        d = out["diagnostics"]
        rows.append(dict(name=name, out=out, d=d, er=er,
                         card=out["figures"][0] if out["figures"] else None))

    # ---- cross-morphology comparison (the pipeline distinguishes them) ----
    print("\n" + "=" * 84)
    print("World-model across morphologies — one world, three bodies, one pipeline")
    print("=" * 84)
    print(f"{'morphology':<12}{'topology':<14}{'nodes':>6}{'edges':>6}{'N_D':>5}"
          f"{'regions':>8}{'src node':>9}{'edge_rec':>10}")
    for r in rows:
        d = r["d"]
        topo = "chain" if d["is_chain"] else f"branched@{d['branch_node']}"
        src = r["out"]["recovered"]["source_node"]
        print(f"{r['name']:<12}{topo:<14}{d['n_nodes']:>6}{d['n_edges']:>6}{d['N_D']:>5}"
              f"{d['n_regions']:>8}{str(src):>9}{r['er']:>10.2f}")
    print("=" * 84)

    # ---- WIRING ASSERTIONS (did the pipeline fire correctly for every body?) ----
    checks = []

    def ck(label, cond):
        checks.append(bool(cond)); print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("\nPipeline wiring checks:")
    by = {r["name"]: r for r in rows}
    for name, r in by.items():
        d = r["d"]
        ck(f"{name}: card + json written",
           r["card"] and os.path.exists(r["card"]) and os.path.exists(r["out"]["results_json"]))
        ck(f"{name}: node count matches the body", d["n_nodes"] == len(MORPHS_positions(name)))
        ck(f"{name}: source localized on a real node",
           r["out"]["recovered"]["source_node"] in range(d["n_nodes"]))
    ck("chain recovered as a chain (N_D=1)", by["chain"]["d"]["is_chain"] and by["chain"]["d"]["N_D"] == 1)
    ck("symmetric recovered as branched with a hub", by["symmetric"]["d"]["branch_node"] is not None)
    ck("asymmetric recovered as branched with a hub", by["asymmetric"]["d"]["branch_node"] is not None)
    ck("symmetry shows up: N_D(symmetric) > N_D(asymmetric)",
       by["symmetric"]["d"]["N_D"] > by["asymmetric"]["d"]["N_D"])

    n_ok, n = sum(checks), len(checks)
    print("=" * 84)
    print(f"PIPELINE WIRED across morphologies: {n_ok}/{n} checks "
          f"[{'PASS — ready to roll out' if n_ok == n else 'FAILURES — fix before rollout'}]")
    return 0 if n_ok == n else 1


# small helper so the assertion can know each body's node count without re-simulating
_POS_CACHE = {}


def MORPHS_positions(name):
    if name not in _POS_CACHE:
        from branched_self_model import build_branched_xml
        _, positions, *_ = build_branched_xml(MORPHS[name])
        _POS_CACHE[name] = positions
    return _POS_CACHE[name]


if __name__ == "__main__":
    sys.exit(main())
