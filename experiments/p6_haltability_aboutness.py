# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""E3 — haltability generates aboutness (the manipulator unit).

The claim: a **halt-in-contact** is not a stop but a *directed state* — the
agent's limb committed to the object. We show that halt is

  - **persistent** : it holds while the agent presses (the object + the press
    are a halt equilibrium), and is restored after a perturbation;
  - **returnable** : on withdraw → re-press the agent re-acquires the SAME object
    (the object's place is a returnable possibility of modulation);
  - **side-specific** : an object on the left makes the LEFT limb halt-in-contact
    while the right limb, given the same command, swings free — the bilateral
    asymmetry (L-halt / R-free) *is* directedness toward the object.

That triad — persistent, returnable, side-specific — is what we mean by the
halt being *about* the object.

Foil: a **CPG** drives the limb rhythmically. It touches the object every cycle
but can never *hold* a directed halt — the object state only flickers. Rhythm is
not aboutness; haltability is.

(The deeper "co-activated equilibrium with tunable stiffness in free space" needs
muscle/tendon actuators — a later refinement; here the object supplies the
equilibrium and the press restores it after perturbation.)

Run:  ../.venv/bin/python p6_haltability_aboutness.py
Outputs: ../figures/p6_haltability_aboutness.png
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

DT = 0.002
T = 6.0
PERIOD = 2.0            # acquire–HOLD–withdraw–rest cycle for the SMN press
PERTURB_WINDOW = (0.85, 1.05)   # push the limb off the object during cycle 1's hold
PERTURB_TORQUE = 2.5
CON_THR = 0.5
VEL_THR = 0.30
CPG_FREQ = 1.2


def smn_press(t):
    """Haltable press: acquire → a long committed HOLD → withdraw → rest, repeated.
    The hold is sustained as long as the agent chooses — the mark of a halt."""
    ph = t % PERIOD
    if ph < 0.40:
        return CMAX * (ph / 0.40)
    if ph < 1.40:
        return CMAX                              # the hold — a committed, sustained halt
    if ph < 1.70:
        return CMAX * (1.0 - (ph - 1.40) / 0.30)
    return 0.0


def cpg_press(t):
    """A rhythm: presses and releases every cycle, never holds."""
    return CMAX * max(0.0, math.sin(2 * math.pi * CPG_FREQ * t))


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

    smn = run(smn_press)
    cpg = run(cpg_press)

    print("\n=== E3 — haltability generates aboutness ===")
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
    fig, (axA, axB, axC) = plt.subplots(3, 1, figsize=(11, 9), sharex=False)

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
    axA.set_title("(A) SMN: the halt is persistent, returnable, side-specific\n"
                  "(left holds the object across cycles & restores after perturbation; right never holds)", fontsize=10)
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

    fig.suptitle("E3 — haltability generates aboutness: a halt-in-contact that is persistent, "
                 "returnable, and side-specific", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(figdir, "p6_haltability_aboutness.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
