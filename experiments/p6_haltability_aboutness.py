# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""E3 — the haltable action *pattern* generates object-directedness.

Consistent with the progression, the agent first builds its **self-model**, then
its object-directedness *in that self-frame*.

1. **Self-model (first).** In free space the agent drives its two limbs with
   independent probes and applies the SAME framework read-out
   (:func:`smn_lab.self_model.coupling`): each zone responds to its *own* efference
   and not the other's -- an off-diagonal ~ 0 coupling. That recovers the
   self-referred frame: *I have a left zone and a right zone, independently
   modulable.* (Being bilateral, the two are mirror-alike -- as in the
   [branched body], a symmetric self cannot yet tell its mirror-zones apart.)

2. **Object-directedness (in the self-frame).** With an object on the left, a
   haltable action **pattern** -- not a one-time halt -- produces a halt-in-contact
   that is

     - **persistent** : it holds while the agent presses, and is restored after a
       perturbation (recoverable);
     - **returnable** : withdraw -> re-press re-acquires the SAME object (recurrent,
       recognisable-as-same);
     - **side-specific** : the LEFT self-zone halts while the RIGHT, given the same
       command, swings free.

   The object breaks the bilateral symmetry: it individuates the self's left zone
   AND the object together. That recurrent, recognisable, side-specific pattern --
   expressed in the self-frame -- *is* being directed at the object. Haltability is
   the capacity ([the pivot demo]); this pattern is what makes it *about* something.

Foil: a **CPG** rhythm touches the object every cycle but never *holds* a directed
halt -- rhythm is not aboutness; the haltable *pattern* is.

Run:  ../.venv/bin/python p6_haltability_aboutness.py
"""
from __future__ import annotations
import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.manipulator import build_manip_xml, LimbInterface, CMAX
from smn_lab.self_model import coupling            # the self-model read-out (unchanged)

DT = 0.002
T = 6.0
PERIOD = 2.0            # acquire–HOLD–withdraw–rest cycle for the SMN press
PERTURB_WINDOW = (0.85, 1.05)   # push the limb off the object during cycle 1's hold
PERTURB_TORQUE = 2.5
CON_THR = 0.5
VEL_THR = 0.30
CPG_FREQ = 1.2


# --8<-- [start:pattern]
def smn_press(t):
    """The haltable action PATTERN: acquire -> a long committed HOLD -> withdraw ->
    rest, REPEATED every PERIOD. A pattern, not a one-time halt: the hold recurs and
    is recognisable across cycles (returnable), and is restored after a perturbation
    (recoverable). That recurrent, recognisable hold is what makes it *about* the
    object."""
    ph = t % PERIOD
    if ph < 0.40:
        return CMAX * (ph / 0.40)
    if ph < 1.40:
        return CMAX                              # the hold — a committed, sustained halt
    if ph < 1.70:
        return CMAX * (1.0 - (ph - 1.40) / 0.30)
    return 0.0
# --8<-- [end:pattern]


def cpg_press(t):
    """A rhythm: presses and releases every cycle, never holds."""
    return CMAX * max(0.0, math.sin(2 * math.pi * CPG_FREQ * t))


# --8<-- [start:selfmodel]
def self_model(seed=0, T_probe=4.0):
    """Self-model FIRST. In free space, drive each limb with an independent probe
    and apply the framework read-out coupling(efference, motion). Each zone responds
    to its OWN efference and not the other's (off-diagonal ~ 0): the two zones are
    independently modulable -- the self-referred frame (my-left, my-right), each
    fixed by its own efference->motion contingency, prior to any object."""
    model = mujoco.MjModel.from_xml_string(
        build_manip_xml(left="free", right="free", actuation="smn"))
    data = mujoco.MjData(model); mujoco.mj_forward(model, data)
    liL, liR = LimbInterface(model, "L", "smn"), LimbInterface(model, "R", "smn")
    rng = np.random.default_rng(seed)
    n = int(T_probe / DT)
    DRV = np.zeros((n, 2)); VEL = np.zeros((n, 2))
    cL = cR = 0.0
    for k in range(n):
        cL += (-cL / 0.3) * DT + 3.0 * np.sqrt(DT) * rng.standard_normal()   # independent
        cR += (-cR / 0.3) * DT + 3.0 * np.sqrt(DT) * rng.standard_normal()   # probes
        liL.drive(data, CMAX * (0.5 + 0.5 * math.tanh(cL)))
        liR.drive(data, CMAX * (0.5 + 0.5 * math.tanh(cR)))
        mujoco.mj_step(model, data)
        DRV[k] = (cL, cR); VEL[k] = (liL.read(data)["vel"], liR.read(data)["vel"])
    C = np.abs(coupling(DRV, VEL))               # 2x2 zone self-model
    return C / (C.max() + 1e-9)
# --8<-- [end:selfmodel]


def run(drive):
    model = mujoco.MjModel.from_xml_string(
        build_manip_xml(left="fixed", right="free", actuation="smn"))
    data = mujoco.MjData(model); mujoco.mj_forward(model, data)
    liL = LimbInterface(model, "L", "smn")
    liR = LimbInterface(model, "R", "smn")
    dofL = model.jnt_dofadr[model.joint("j_L").id]

    n = int(T / DT)
    t = np.arange(n) * DT
    conL = np.zeros(n); velL = np.zeros(n); conR = np.zeros(n); velR = np.zeros(n)
    press = np.zeros(n); perturb = np.zeros(n)
    for k in range(n):
        tk = k * DT
        p = drive(tk)
        liL.drive(data, p)
        liR.drive(data, p)                       # same command to both limbs
        if PERTURB_WINDOW[0] <= tk < PERTURB_WINDOW[1] and drive is smn_press:
            data.qfrc_applied[dofL] = -PERTURB_TORQUE     # shove the left limb off the object
            perturb[k] = 1
        else:
            data.qfrc_applied[dofL] = 0.0
        mujoco.mj_step(model, data)
        rL, rR = liL.read(data), liR.read(data)
        conL[k], velL[k] = rL["contact"], rL["vel"]
        conR[k], velR[k] = rR["contact"], rR["vel"]
        press[k] = p
    haltL = (conL > CON_THR) & (velL < VEL_THR)   # halt-in-contact = directed halt
    haltR = (conR > CON_THR) & (velR < VEL_THR)
    return dict(t=t, conL=conL, conR=conR, haltL=haltL, haltR=haltR,
                press=press, perturb=perturb)


def episodes(halt):
    """Number of distinct halt-in-contact episodes (returnability)."""
    return int(np.sum((halt[1:].astype(int) - halt[:-1].astype(int)) == 1)) + int(halt[0])


def held_fraction(halt, press):
    """Fraction of press-active time spent in a held directed halt."""
    active = press > 0.3 * CMAX
    return float((halt & active).sum() / max(active.sum(), 1))


def longest_halt(halt):
    """Longest continuous held-halt episode (s) — can the agent *sustain* a
    directed halt, or is it forced to release? This is the aboutness signature."""
    best = cur = 0
    for h in halt:
        cur = cur + 1 if h else 0
        best = max(best, cur)
    return best * DT


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    # --- self-model first (the self-referred frame the aboutness is expressed in) ---
    C = self_model()
    offdiag = 0.5 * (C[0, 1] + C[1, 0])
    print("\n=== E3 — the haltable pattern generates object-directedness ===")
    print("  [1] self-model (free space, framework coupling):")
    print(f"      zone-coupling matrix (normalized)  L: [{C[0,0]:.2f} {C[0,1]:.2f}]  "
          f"R: [{C[1,0]:.2f} {C[1,1]:.2f}]")
    print(f"      off-diagonal = {offdiag:.2f}  ->  two independently-modulable zones "
          f"(my-left, my-right); a bilateral self cannot yet tell them apart.")
    print("  [2] object-directedness (the object breaks the symmetry, in the self-frame):")

    smn = run(smn_press)
    cpg = run(cpg_press)

    print(f"  {'agent/limb':18s} {'longest halt (s)':>16s} {'episodes':>10s} {'held fraction':>14s}")
    rows = [("SMN left (object)", smn["haltL"], smn["press"]),
            ("SMN right (none)", smn["haltR"], smn["press"]),
            ("CPG left (object)", cpg["haltL"], cpg["press"])]
    for name, halt, press in rows:
        print(f"  {name:18s} {longest_halt(halt):16.2f} {episodes(halt):10d} "
              f"{held_fraction(halt, press):14.2f}")
    print(f"\n  persistent: SMN sustains a {longest_halt(smn['haltL']):.1f}s halt vs "
          f"CPG's {longest_halt(cpg['haltL']):.1f}s; returnable: re-acquired "
          f"{episodes(smn['haltL'])}×; side-specific: right longest halt "
          f"{longest_halt(smn['haltR']):.2f}s")

    # --- figure ---
    fig = plt.figure(figsize=(13, 8))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 2.6])
    axSM = fig.add_subplot(gs[0, 0])          # self-model (computed first)
    axC = fig.add_subplot(gs[1, 0])           # summary bar
    axA = fig.add_subplot(gs[0, 1])           # SMN time series
    axB = fig.add_subplot(gs[1, 1])           # CPG time series

    # SM: the self-model — a 2x2 zone-coupling matrix (off-diagonal ~ 0 = two zones)
    im = axSM.imshow(C, cmap="Blues", vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            axSM.text(j, i, f"{C[i,j]:.2f}", ha="center", va="center",
                      color="white" if C[i, j] > 0.5 else "#333", fontsize=11)
    axSM.set_xticks([0, 1]); axSM.set_yticks([0, 1])
    axSM.set_xticklabels(["L", "R"]); axSM.set_yticklabels(["L", "R"])
    axSM.set_title("(1) self-model, first\ncoupling(efference, motion):\ntwo decoupled zones "
                   f"(off-diag {offdiag:.2f})", fontsize=9)

    # A: SMN — left vs right contact; halt episodes shaded; perturbation marked
    axA.plot(smn["t"], smn["conL"], color="#2c6a9c", lw=1.5, label="left (object)")
    axA.plot(smn["t"], smn["conR"], color="#b0b0b0", lw=1.2, label="right (no object)")
    axA.fill_between(smn["t"], 0, smn["conL"].max() * 1.05, where=smn["haltL"],
                     color="#2c6a9c", alpha=0.12, label="held directed halt")
    pw = smn["perturb"] > 0
    if pw.any():
        axA.axvspan(smn["t"][pw][0], smn["t"][pw][-1], color="#b03030", alpha=0.25)
        axA.text(smn["t"][pw][0], smn["conL"].max(), " perturbation", color="#b03030", fontsize=8, va="top")
    axA.set_ylabel("contact force (N)")
    axA.set_title("(2) object-directedness in the self-frame: the halt is persistent, returnable, "
                  "side-specific\n(the LEFT self-zone holds the object across cycles & restores after "
                  "perturbation; the RIGHT never holds)", fontsize=9.5)
    axA.legend(fontsize=8, loc="upper right"); axA.grid(alpha=0.25)

    # B: CPG — left contact flickers, never a sustained held halt
    axB.plot(cpg["t"], cpg["conL"], color="#c08a3e", lw=1.5, label="CPG left (object)")
    axB.fill_between(cpg["t"], 0, max(cpg["conL"].max(), 1) * 1.05, where=cpg["haltL"],
                     color="#c08a3e", alpha=0.15, label="held halt (brief flickers)")
    axB.set_ylabel("contact force (N)"); axB.set_xlabel("time (s)")
    axB.set_title("(B) CPG foil: rhythm touches but never holds — the object state only flickers", fontsize=10)
    axB.legend(fontsize=8, loc="upper right"); axB.grid(alpha=0.25)

    # C: summary — longest sustained directed halt (the aboutness signature)
    labels = ["SMN left\n(object)", "SMN right\n(no object)", "CPG left\n(object)"]
    vals = [longest_halt(smn["haltL"]), longest_halt(smn["haltR"]), longest_halt(cpg["haltL"])]
    axC.bar(labels, vals, color=["#2c6a9c", "#b0b0b0", "#c08a3e"])
    axC.set_ylabel("longest sustained\ndirected halt (s)")
    axC.set_title("(C) Aboutness = a *sustained* directed halt: only SMN, only on the object side", fontsize=10)
    for i, v in enumerate(vals):
        axC.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9)

    fig.suptitle("E3 — self-model first, then the haltable action pattern → object-directedness "
                 "(persistent · returnable · side-specific)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(figdir, "p6_haltability_aboutness.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
