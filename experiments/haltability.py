# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Haltability needs a pivot layer (toward morphological computing).

The [nested lattice](../docs/experiments/nested_lattice_self_model.md) established
that a body has a stable deep **canvas** beneath its active top layers. This shows
what that layering *enables*: **haltability** -- the ability to bring an ongoing
action to a discrete, stable, individuated stop.

An active chain (the writing) is coarse-coupled and driven. To HALT node k, a
haltable action pattern clamps it to a HOME position. The claim (GN): a halt is a
stable, addressable hold ONLY against a stable reference -- the canvas. So:

  * canvas ON  (a stable deep layer): the halt clamps node k to its fixed home, and
    it is held at a discrete address k while the rest of the body keeps moving --
    a selective, individuated hold (the dexterity primitive; the N addresses are
    the enumeration / counting substrate).
  * canvas OFF (no stable layer): there is no fixed home to clamp to; the best a
    halt can do is freeze velocity, and the node still drifts with the flow -- no
    stable, addressable hold.

Why some bodies count and name many discrete things and others only a few is here:
not the topology (a chimp shares ours) but **haltable** nesting -- a pivot needs a
stable layer beneath it.

Run:  ../.venv/bin/python haltability.py
"""
from __future__ import annotations
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

DT = 0.002
T_WARM, T_REC = 2.0, 25.0
N = 6
D = 0.28                                       # spacing = the discrete addresses
DRIVE_SIG = 2.2
K_CLAMP, D_CLAMP = 45.0, 9.0                    # the halt's hold gains


def build_xml(coarse_k=8.0, seg_damp=2.0, seg_mass=0.05):
    bodies = "".join(
        f'<body name="a{i}" pos="{i * D} 0 0.1">'
        f'<joint name="ax{i}" type="slide" axis="1 0 0" damping="{seg_damp}"/>'
        f'<joint name="ay{i}" type="slide" axis="0 1 0" damping="{seg_damp}"/>'
        f'<geom type="box" size="0.04 0.04 0.02" mass="{seg_mass}" friction="0 0 0"/>'
        f'<site name="a{i}"/></body>' for i in range(N))
    coarse = "".join(
        f'<spatial name="cz{i}" stiffness="{coarse_k}" damping="0.4" springlength="{D}">'
        f'<site site="a{i}"/><site site="a{i + 1}"/></spatial>' for i in range(N - 1))
    return (f'<mujoco><option timestep="{DT}" gravity="0 0 0" integrator="implicitfast">'
            f'<flag contact="disable"/></option><worldbody>'
            f'<light pos="0 0 3" dir="0 0 -1"/>{bodies}</worldbody>'
            f'<tendon>{coarse}</tendon></mujoco>')


def run(halt_k, canvas_on, seed):
    """Drive the chain; HALT node k; log every node's position."""
    model = mujoco.MjModel.from_xml_string(build_xml())
    data = mujoco.MjData(model)
    rng = np.random.default_rng(seed)
    aid = [model.body(f"a{i}").id for i in range(N)]
    vadr = [(model.jnt_dofadr[model.joint(f"ax{i}").id],
             model.jnt_dofadr[model.joint(f"ay{i}").id]) for i in range(N)]
    home = np.arange(N) * D                     # the fixed canvas addresses
    f = np.zeros(N)
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    P = np.zeros((n_rec, N, 2))
    for i in range(n_warm + n_rec):
        f += (-f / 0.2) * DT + DRIVE_SIG * np.sqrt(DT) * rng.standard_normal(N)
        for j in range(N):
            px, py = data.xpos[aid[j]][:2]
            vx, vy = data.qvel[vadr[j][0]], data.qvel[vadr[j][1]]
            # --8<-- [start:halt]
            if j == halt_k:                     # the halt (a haltable action pattern)
                if canvas_on:                   # clamp to the fixed canvas home = address k
                    fx = -K_CLAMP * (px - home[j]) - D_CLAMP * vx
                    fy = -K_CLAMP * (py - 0.0) - D_CLAMP * vy
                else:                           # no stable reference: only freeze velocity
                    fx, fy = -D_CLAMP * vx, -D_CLAMP * vy
            else:                               # the rest keeps writing (BAP drive)
                fx, fy = f[j], 0.5 * f[j]
            # --8<-- [end:halt]
            data.xfrc_applied[aid[j], 0] = fx
            data.xfrc_applied[aid[j], 1] = fy
        mujoco.mj_step(model, data)
        if i >= n_warm:
            for j in range(N):
                P[i - n_warm, j] = data.xpos[aid[j]][:2]
    return P, home


def measure(canvas_on, seeds=(0, 1)):
    """Over every halt target k: how tight is the hold, and is it at address k?"""
    home = np.arange(N) * D
    held_spread, active_spread, addr_ok, held_mean = [], [], [], np.zeros(N)
    for k in range(N):
        sp_k, mean_k = [], []
        for s in seeds:
            P, _ = run(k, canvas_on, s)
            spread = P.std(0).mean(1)
            sp_k.append(spread[k])
            active_spread.append(np.delete(spread, k).mean())
            mean_k.append(P[:, k, 0].mean())
            addr_ok.append(int(np.argmin(np.abs(P[:, k, 0].mean() - home)) == k))
        held_spread.append(np.mean(sp_k)); held_mean[k] = np.mean(mean_k)
    return dict(held_spread=float(np.mean(held_spread)),
                active_spread=float(np.mean(active_spread)),
                address=float(np.mean(addr_ok)), held_mean=held_mean, home=home)


def plot(on, off, out):
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 4.8))
    # A: a held node's position over time -- ON pinned, OFF drifts
    k = N // 2
    Pon, home = run(k, True, 0)
    Poff, _ = run(k, False, 0)
    t = np.arange(Pon.shape[0]) * DT
    axA.axhline(home[k], color="#999", ls=":", lw=1, label=f"address k={k}")
    axA.plot(t, Pon[:, k, 0], color="#1538a0", lw=1.6, label="canvas ON — held")
    axA.plot(t, Poff[:, k, 0], color="#c0392b", lw=1.2, label="canvas OFF — drifts")
    axA.set_xlabel("time (s)"); axA.set_ylabel("held node position x")
    axA.set_title("A halt is a stable hold only against the canvas", fontsize=10)
    axA.legend(fontsize=8, loc="upper left")
    # B: addressability -- held mean position vs commanded address, all k
    axB.plot(off["home"], off["home"], color="#bbb", lw=1, zorder=0)
    axB.scatter(on["home"], on["held_mean"], s=90, color="#1538a0",
                label=f"canvas ON  (addressed {on['address']:.0%})", zorder=2)
    axB.scatter(off["home"], off["held_mean"], s=90, marker="x", color="#c0392b",
                label=f"canvas OFF ({off['address']:.0%})", zorder=2)
    axB.set_xlabel("commanded halt address  k"); axB.set_ylabel("where the node was held (x)")
    axB.set_title(f"{N} addressable holds — the counting substrate\n"
                  f"hold spread: ON {on['held_spread']:.3f} vs OFF {off['held_spread']:.3f}",
                  fontsize=10)
    axB.legend(fontsize=8, loc="upper left")
    fig.suptitle("Haltability needs a pivot layer — a stable hold, individuated by "
                 "the canvas beneath", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


def main():
    on, off = measure(True), measure(False)
    print("\nHaltability on the layered body — a halt needs a pivot layer\n" + "=" * 60)
    print(f"{'':<28}{'canvas ON':>14}{'canvas OFF':>14}")
    print(f"{'held-node spread (hold)':<28}{on['held_spread']:>14.4f}{off['held_spread']:>14.4f}")
    print(f"{'active-node spread (write)':<28}{on['active_spread']:>14.4f}{off['active_spread']:>14.4f}")
    print(f"{'address correct (of ' + str(N) + ')':<28}{on['address']:>14.2f}{off['address']:>14.2f}")
    print("=" * 60)
    print("A stable, addressable hold needs the stable deep layer to pivot against.\n")
    figdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    plot(on, off, os.path.join(figdir, "haltability.png"))


if __name__ == "__main__":
    main()
