# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""E4 --- the world model scales with the network of coupled zones.

The clinching demonstration of the SMN thesis: scaling the complexity of
modulation *is* scaling the world model. A single CAZ registers one
\\emph{difference} (a differentia); an \\emph{object} is a composition of
differentiae; composition requires a network of zones coupled through the board.
So the question "where is the network?" has a concrete answer --- the body is a
network of zones, and the constructed world grows with it.

We build a row of $K$ pull-only antagonist \\emph{press pads} (zones). Each pad
presses one facet of an object and reads that facet's resistance differentia
(hard vs soft), exactly as in E1. The board composes the bound zones' differentiae
into an object code. We then measure the agent's \\textbf{world-model capacity} ---
the number of objects it can individuate --- as a function of how many zones the
network binds.

Result we expect (and test against real per-pad reads): capacity $=2^{(\\text{zones
bound by the board})}$ --- exponential in the \\emph{networked} zones, while zones
that are present but unbound add nothing (a single difference, capacity $2$,
flat). The world model is built by the network, not by the sensor count.

Run:  ../.venv/bin/python p7_scaling_network.py
Outputs: ../figures/p7_scaling_network.png
"""
from __future__ import annotations
import os
import sys
import itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DT = 0.002
T = 1.2
CMAX = 10.0
SPACING = 0.12
PAD_Z = 0.30
FACET_Z = 0.12          # raised off the floor so a soft facet has room to yield
PAD_STIFF = 40.0
SOFT_K = 120.0          # compliant-facet spring (soft); hard facet is welded
KMAX = 5                # scale the network up to this many zones


def build_xml(facets) -> str:
    """A row of K press pads over K facets; each facet 'hard' (welded) or 'soft'
    (spring-backed). Each pad is a pull-only antagonist prismatic zone."""
    K = len(facets)
    facet_xml, pad_xml, act_xml, sen_xml = [], [], [], []
    for i, f in enumerate(facets):
        x = i * SPACING
        if f == "hard":
            facet_xml.append(f'<geom name="facet_{i}" type="box" pos="{x} 0 {FACET_Z}" '
                             f'size="0.035 0.035 0.04" rgba="0.45 0.45 0.5 1"/>')
        else:  # soft: a box on a vertical spring
            facet_xml.append(f'<body name="facet_{i}" pos="{x} 0 {FACET_Z}">'
                             f'<joint name="fs_{i}" type="slide" axis="0 0 1" '
                             f'stiffness="{SOFT_K}" damping="3"/>'
                             f'<geom type="box" size="0.035 0.035 0.04" rgba="0.7 0.8 0.7 1"/></body>')
        pad_xml.append(
            f'<body name="pad_{i}" pos="{x} 0 {PAD_Z}">'
            f'<joint name="p_{i}" type="slide" axis="0 0 1" range="-0.24 0.02" limited="true" '
            f'stiffness="{PAD_STIFF}" damping="1.0"/>'
            f'<geom name="tip_{i}" type="box" size="0.025 0.025 0.02" rgba="0.2 0.4 0.9 1" mass="0.1"/>'
            f'<site name="s_{i}" type="box" pos="0 0 -0.025" size="0.03 0.03 0.02"/></body>')
        act_xml.append(f'<motor name="down_{i}" joint="p_{i}" gear="-1" ctrlrange="0 {CMAX}"/>'
                       f'<motor name="up_{i}" joint="p_{i}" gear="1" ctrlrange="0 {CMAX}"/>')
        sen_xml.append(f'<touch name="touch_{i}" site="s_{i}"/>')
    return f"""
<mujoco model="smn_scaling_network">
  <compiler angle="radian"/>
  <option timestep="{DT}" gravity="0 0 -9.81" integrator="implicitfast"/>
  <worldbody>
    <geom name="floor" type="plane" size="3 3 0.1" rgba="0.9 0.9 0.9 1"/>
    {' '.join(facet_xml)}
    {' '.join(pad_xml)}
  </worldbody>
  <actuator>
    {' '.join(act_xml)}
  </actuator>
  <sensor>
    {' '.join(sen_xml)}
  </sensor>
</mujoco>
"""


def read_object(facets):
    """Press every pad and return the per-pad contact impulse (the resistance
    differentia each zone registers)."""
    model = mujoco.MjModel.from_xml_string(build_xml(facets))
    data = mujoco.MjData(model); mujoco.mj_forward(model, data)
    K = len(facets)
    down = [model.actuator(f"down_{i}").id for i in range(K)]
    touch = [model.sensor_adr[model.sensor(f"touch_{i}").id] for i in range(K)]
    n = int(T / DT)
    imp = np.zeros(K)
    for k in range(n):
        f = CMAX * min(1.0, k * DT / (T * 0.7))
        for i in range(K):
            data.ctrl[down[i]] = f
        mujoco.mj_step(model, data)
        for i in range(K):
            imp[i] += data.sensordata[touch[i]] * DT
    return imp


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)

    # 1) per-zone read: confirm a pad cleanly separates hard from soft
    imp_hard = read_object(("hard",))[0]
    imp_soft = read_object(("soft",))[0]
    thr = 0.5 * (imp_hard + imp_soft)
    print("\n=== E4 — the world model scales with the network of zones ===")
    print(f"  per-zone differentia: hard impulse={imp_hard:.2f}  soft impulse={imp_soft:.2f}  "
          f"threshold={thr:.2f}")

    def read_bits(facets):
        return tuple(int(v > thr) for v in read_object(facets))

    # 2) scaling: for each network size K, read every 2^K object and count how many
    #    distinct object codes the bound network individuates.
    Ks = list(range(1, KMAX + 1))
    networked, unbound, correct = [], [], []
    for K in Ks:
        objs = list(itertools.product(("soft", "hard"), repeat=K))
        truth = [tuple(1 if f == "hard" else 0 for f in o) for o in objs]
        reads = [read_bits(o) for o in objs]
        cap_net = len(set(reads))                       # the coupled board binds all K zones
        cap_unb = len(set(r[0] for r in reads))         # unbound: one zone, a single difference
        acc = np.mean([r == t for r, t in zip(reads, truth)])
        networked.append(cap_net); unbound.append(cap_unb); correct.append(acc)
        print(f"  K={K}: networked capacity={cap_net:3d} (2^K={2**K})  unbound={cap_unb}  "
              f"per-object read acc={acc:.2f}")

    # --- figure ---
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.8))

    axA.plot(Ks, networked, "o-", color="#2c6a9c", lw=2, label="networked (board binds the zones)")
    axA.plot(Ks, unbound, "s--", color="#b03030", lw=2, label="unbound (a single difference)")
    axA.plot(Ks, [2 ** k for k in Ks], ":", color="#888", lw=1, label="$2^{K}$")
    axA.set_yscale("log", base=2)
    axA.set_xlabel("number of zones in the network $K$")
    axA.set_ylabel("world-model capacity (individuable objects)")
    axA.set_title("Scaling: the world model grows $2^{K}$ with the\ncoupled network of zones, not with sensor count", fontsize=10)
    axA.set_xticks(Ks); axA.legend(fontsize=8); axA.grid(alpha=0.25, which="both")

    axB.bar([str(k) for k in Ks], correct, color="#2c7a2c")
    axB.set_ylim(0, 1.05); axB.set_xlabel("number of zones $K$")
    axB.set_ylabel("per-object read accuracy")
    axB.set_title("Each composed object is read correctly\nfrom real per-zone presses", fontsize=10)
    for i, v in enumerate(correct):
        axB.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)

    fig.suptitle("E4 — objecthood as composition of differentiae: the world model scales with the network of zones",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(figdir, "p7_scaling_network.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
