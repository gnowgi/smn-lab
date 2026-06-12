# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""E1 — objecthood as resistance-to-modulation (the manipulator unit).

The first experiment on the bilateral two-limb contact unit (see
`design/manipulator-unit.md`). One limb presses on a series of objects that
differ only in how they resist the agent's own pull:

  free            — nothing there;
  movable-light   — a light free box (yields easily; small field-friction);
  movable-heavy   — a heavy free box (yields, but more friction = field cost);
  compliant       — a spring-backed box (gives, then resists);
  fixed           — a welded box (cannot be pushed through).

The agent reads its **dual interface** (intended effort, proprioceptive
result, contact resistance) and we classify each step into the **register
lattice** (Contact × Effort × Motion). The claim is that *objecthood is the
force→result mapping*: the conditions occupy **distinct, separable subsets** of
the lattice — recovered by construction, no learning.

Foil: the same body driven by a **position ('stepper') controller** that commands
an angle. It overpresses what it cannot reach — the SMN press is force-bounded
and resistance-reading; the stepper is not.

Run:  ../.venv/bin/python p4_manipulator_objecthood.py
Outputs: ../figures/p4_manipulator_objecthood.png
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
from smn_lab.manipulator import (build_manip_xml, LimbInterface, RegisterLattice,
                                  OBJECT_KINDS, CMAX, JOINT_RANGE)

DT = 0.002
T_RAMP = 2.5
T_HOLD = 0.8
COCONTRACT = 0.2        # baseline antagonist tone (the opponent pair)
COLORS = {"free": "#6a9ec5", "movable-light": "#3aa0a0", "movable-heavy": "#2c7a2c",
          "compliant": "#c08a3e", "fixed": "#b03030"}


def run(kind, actuation="smn"):
    model = mujoco.MjModel.from_xml_string(
        build_manip_xml(left=kind, right="free", actuation=actuation))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    li = LimbInterface(model, "L", actuation)
    lat = RegisterLattice()
    movable = kind.startswith("movable")
    obj_bid = model.body("obj_L").id if movable else None
    y0 = float(data.xpos[obj_bid][1]) if movable else 0.0

    n = int((T_RAMP + T_HOLD) / DT)
    eff = np.zeros(n); ang = np.zeros(n); con = np.zeros(n); cmd = np.zeros(n)
    regs = []
    for k in range(n):
        frac = min(1.0, (k * DT) / T_RAMP)
        if actuation == "smn":
            li.drive(data, CMAX * frac, COCONTRACT)
        else:                                       # position/stepper: command the angle
            li.drive(data, JOINT_RANGE * frac)
        mujoco.mj_step(model, data)
        r = li.read(data)
        eff[k], ang[k], con[k] = r["effort"], r["ang"], r["contact"]
        cmd[k] = CMAX * frac
        regs.append(lat.classify(r))
    disp = abs(float(data.xpos[obj_bid][1]) - y0) if movable else None
    return dict(eff=eff, ang=ang, con=con, cmd=cmd, regs=regs, disp=disp, lat=lat)


def occupancy(regs, lat, skip=0.3):
    """Fraction of (post-warmup) steps spent in each lattice cell."""
    cells = lat.cells()
    idx = {c: i for i, c in enumerate(cells)}
    v = np.zeros(len(cells))
    start = int(skip / DT)
    for r in regs[start:]:
        v[idx[r]] += 1
    return v / max(v.sum(), 1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    lat = RegisterLattice()
    cells = lat.cells()

    smn = {k: run(k, "smn") for k in OBJECT_KINDS}
    pos = {k: run(k, "position") for k in OBJECT_KINDS}

    for k in OBJECT_KINDS:                              # derive scalar signatures
        r = smn[k]
        r["impulse"] = float(r["con"].sum() * DT)       # ∫contact·dt — total resistance met
        r["occ"] = occupancy(r["regs"], lat, skip=0.1)
        pos[k]["impulse"] = float(pos[k]["con"].sum() * DT)

    print("\n=== E1 — objecthood as resistance-to-modulation ===")
    print(f"  {'condition':14s} {'final angle':>11s} {'impulse(N·s)':>13s} {'peak(N)':>8s} "
          f"{'dom. register':>30s} {'disp(m)':>8s}")
    for k in OBJECT_KINDS:
        r = smn[k]
        dom = cells[int(np.argmax(r["occ"]))]
        dsp = f"{r['disp']:.3f}" if r["disp"] is not None else "—"
        print(f"  {k:14s} {r['ang'][-1]:11.3f} {r['impulse']:13.3f} {r['con'].max():8.2f} "
              f"{str(dom):>30s} {dsp:>8s}")

    # separability: pairwise L1 distance between the conditions' occupancy vectors
    ks = list(OBJECT_KINDS)
    dmin = min(float(np.abs(smn[a]["occ"] - smn[b]["occ"]).sum())
               for i, a in enumerate(ks) for b in ks[i + 1:])
    print(f"\n  occupancy vectors over {len(ks)} conditions: min pairwise L1 = {dmin:.2f} "
          f"(all distinct if > 0)")
    print("  foil overpress (contact impulse, SMN vs position):")
    for k in OBJECT_KINDS:
        print(f"    {k:14s}  SMN {smn[k]['impulse']:6.3f}   position {pos[k]['impulse']:6.3f}")

    # --- figure (2x2) ---
    fig, axs = plt.subplots(2, 2, figsize=(13, 9))
    axA, axB, axC, axD = axs.ravel()

    # A: force -> result map (SMN)
    for k in OBJECT_KINDS:
        axA.plot(smn[k]["cmd"], smn[k]["ang"], color=COLORS[k], lw=2, label=k)
    axA.set_xlabel("commanded press (N·m)"); axA.set_ylabel("achieved |angle| (rad)")
    axA.set_title("(A) The force→result map\nobjecthood = how the object answers the pull", fontsize=10)
    axA.legend(fontsize=8); axA.grid(alpha=0.25)

    # B: the objecthood map — resistance (impulse) vs yielding (final angle)
    for k in OBJECT_KINDS:
        axB.scatter(smn[k]["impulse"], smn[k]["ang"][-1], s=140, color=COLORS[k],
                    edgecolors="k", lw=0.5, zorder=3)
        axB.annotate(k, (smn[k]["impulse"], smn[k]["ang"][-1]),
                     textcoords="offset points", xytext=(6, 4), fontsize=8)
    axB.set_xlabel("contact impulse (N·s) — resistance")
    axB.set_ylabel("final angle (rad) — yielding")
    axB.set_title("(B) The objecthood map\neach object a distinct (resistance, yielding)", fontsize=10)
    axB.grid(alpha=0.25)

    # C: register occupancy heatmap (SMN)
    M = np.array([smn[k]["occ"] for k in OBJECT_KINDS])
    im = axC.imshow(M, aspect="auto", cmap="magma", vmin=0, vmax=M.max())
    axC.set_yticks(range(len(OBJECT_KINDS))); axC.set_yticklabels(OBJECT_KINDS, fontsize=8)
    axC.set_xticks(range(len(cells)))
    axC.set_xticklabels(["·".join(c) for c in cells], rotation=90, fontsize=6)
    axC.set_title("(C) Register occupancy — which subset of the field", fontsize=10)
    fig.colorbar(im, ax=axC, fraction=0.046, pad=0.04)

    # D: foil overpress (contact impulse, SMN vs position)
    x = np.arange(len(OBJECT_KINDS)); w = 0.38
    axD.bar(x - w / 2, [smn[k]["impulse"] for k in OBJECT_KINDS], w, label="SMN (force-bounded)", color="#2c6a9c")
    axD.bar(x + w / 2, [pos[k]["impulse"] for k in OBJECT_KINDS], w, label="position (stepper)", color="#b03030")
    axD.set_xticks(x); axD.set_xticklabels(OBJECT_KINDS, rotation=30, ha="right", fontsize=8)
    axD.set_ylabel("contact impulse (N·s)")
    axD.set_title("(D) Foil: the stepper overpresses\nwhat it cannot reach", fontsize=10)
    axD.legend(fontsize=8); axD.grid(alpha=0.25, axis="y")

    fig.suptitle("E1 — objecthood as resistance-to-modulation: one pull-only limb, five objects, "
                 "read by construction into the register lattice", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(figdir, "p4_manipulator_objecthood.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
