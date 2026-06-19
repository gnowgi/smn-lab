# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""A menagerie: complex agents composed from the same basic units.

One grammar, many bodies. These schematics show that the bench's primitives —
rigid **segments**, **CAZ** opponent-pair joints (whose split orientation sets the
degree of freedom), and shape-coded **sensors** — compose into worms, fish,
quadrupeds, birds, and bipeds by three moves:

  - **scale**   — add segments to the axial chain;
  - **branch**  — attach a chain of segments to a segment (a leg, wing, antenna);
  - **nest**    — a chain of small sub-segments makes a *flexible* part (a tail, a
                  finger): flexibility is rigid segments in series, as in a real
                  finger or tail;
  - **configure DOF** — choose each joint's CAZ (yaw / pitch / roll / telescoping).

Run:  ../.venv/bin/python menagerie_figs.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import caz_glyph, sensor_node, _eye, MODALITY_COLORS

TRUNK = "#3a4a5e"
LIMB = "#5b6b7e"


def seg(ax, p0, p1, color, lw):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=lw,
            solid_capstyle="round", zorder=1)


def chain(ax, start, ang, n, seglen, lw, color=LIMB, dof="lateral",
          curl=0.0, taper=0.88, caz_r=0.085, joints=True):
    """Draw a chain of n rigid segments from `start` along `ang` (rad), each turned
    by `curl` and scaled by `taper` from the previous (taper<1 → a flexible,
    tapering part = nesting). A CAZ marks each joint. Returns the joint points."""
    p = np.array(start, float); a = ang; L = seglen; w = lw
    pts = [p.copy()]
    for i in range(n):
        q = p + L * np.array([np.cos(a), np.sin(a)])
        seg(ax, p, q, color, w)
        if joints:
            caz_glyph(ax, p[0], p[1], caz_r, dof=dof)
        pts.append(q.copy())
        p, a, L, w = q, a + curl, L * taper, max(w * 0.9, 2.0)
    return pts


def sensors_on(ax, pts, mods, r=0.07):
    """Place shaped sensors near the given joint points (cycling modalities)."""
    for i, p in enumerate(pts):
        sensor_node(ax, p[0], p[1] + 0.12, r, mods[i % len(mods)])


def _ax(fig, gs, title, xlim, ylim):
    ax = fig.add_subplot(gs)
    ax.set_title(title, fontsize=9.5)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    return ax


def worm(ax):
    pts = chain(ax, (-1.6, 0), 0, 5, 0.62, 11, color=TRUNK, dof="lateral", taper=1.0)
    sensors_on(ax, pts[:5], ["chem", "thermal"])
    _eye(ax, pts[-1][0] + 0.12, 0.05, 0.13, MODALITY_COLORS["vision"])
    ax.text(0, -0.85, "scale by adding segments · lateral CAZ → undulation",
            ha="center", fontsize=7.5, color="#555")


def fish(ax):
    trunk = chain(ax, (-0.2, 0), 0, 4, 0.55, 13, color=TRUNK, dof="lateral", taper=1.0)
    # flexible tail = NESTED shrinking sub-segments
    chain(ax, (-0.2, 0), np.pi, 4, 0.34, 8, color=LIMB, dof="lateral",
          curl=0.18, taper=0.8)
    # pectoral fins (branches) + dorsal fin
    chain(ax, trunk[2], -1.9, 2, 0.32, 6, color=LIMB, dof="pitch", taper=0.8)
    chain(ax, trunk[2], 1.9, 2, 0.32, 6, color=LIMB, dof="pitch", taper=0.8)
    chain(ax, trunk[2], 1.4, 1, 0.4, 6, color=LIMB, dof="pitch")
    sensors_on(ax, trunk[:4], ["chem", "thermal", "pressure"])
    _eye(ax, trunk[-1][0] + 0.1, 0.05, 0.12, MODALITY_COLORS["vision"])
    ax.text(0, -1.15, "+ fins (branch) + flexible tail (nest)", ha="center",
            fontsize=7.5, color="#555")


def lizard(ax):
    spine = chain(ax, (-1.1, 0), 0, 5, 0.5, 12, color=TRUNK, dof="lateral", taper=1.0)
    for s in (spine[1], spine[3]):              # two leg girdles, 4 legs
        chain(ax, s, -2.5, 2, 0.34, 6, color=LIMB, dof="pitch", curl=0.5)
        chain(ax, s, -0.65, 2, 0.34, 6, color=LIMB, dof="pitch", curl=-0.5)
    chain(ax, spine[0], np.pi, 4, 0.3, 7, color=LIMB, dof="lateral",  # flexible tail
          curl=-0.12, taper=0.8)
    sensors_on(ax, spine[:5], ["chem", "thermal"])
    _eye(ax, spine[-1][0] + 0.1, 0.05, 0.12, MODALITY_COLORS["vision"])
    ax.text(0, -1.4, "+ 4 legs (branch, pitch CAZ) + flexible tail (nest)",
            ha="center", fontsize=7.5, color="#555")


def bird(ax):
    trunk = chain(ax, (-0.4, 0), 0.2, 3, 0.55, 13, color=TRUNK, dof="lateral", taper=1.0)
    chain(ax, trunk[1], 2.2, 3, 0.42, 6, color=LIMB, dof="pitch", curl=-0.25)   # wings
    chain(ax, trunk[1], 0.95, 3, 0.42, 6, color=LIMB, dof="pitch", curl=0.25)
    chain(ax, trunk[1], -1.7, 2, 0.34, 6, color=LIMB, dof="pitch", curl=0.4)    # legs
    chain(ax, trunk[1], -1.4, 2, 0.34, 6, color=LIMB, dof="pitch", curl=-0.4)
    chain(ax, trunk[-1], 0.5, 1, 0.35, 6, color=LIMB)                           # beak/neck
    sensors_on(ax, trunk[:3], ["chem", "pressure"])
    _eye(ax, trunk[-1][0] + 0.15, trunk[-1][1] + 0.18, 0.12, MODALITY_COLORS["vision"])
    ax.text(0, -1.3, "wings + legs (branch); flight needs roll CAZ + a lift medium",
            ha="center", fontsize=7.5, color="#555")


def biped(ax):
    trunk = chain(ax, (0, -0.2), np.pi / 2, 3, 0.5, 14, color=TRUNK, dof="pitch", taper=1.0)
    _eye(ax, trunk[-1][0] - 0.05, trunk[-1][1] + 0.2, 0.14, MODALITY_COLORS["vision"])
    # arms (branch) ending in a hand = nested fingers (flexible)
    armL = chain(ax, trunk[2], np.pi + 0.55, 2, 0.36, 7, color=LIMB, dof="pitch", curl=0.35)
    armR = chain(ax, trunk[2], -0.55, 2, 0.36, 7, color=LIMB, dof="pitch", curl=-0.35)
    for hand in (armL[-1], armR[-1]):           # two nested fingers per hand
        for df in (-0.25, 0.25):
            chain(ax, hand, -np.pi / 2 + df, 3, 0.11, 2.5, color=LIMB, dof="pitch",
                  curl=0.22, taper=0.8, joints=False)
    chain(ax, trunk[0], -np.pi / 2 - 0.25, 2, 0.42, 9, color=LIMB, dof="pitch")  # legs
    chain(ax, trunk[0], -np.pi / 2 + 0.25, 2, 0.42, 9, color=LIMB, dof="pitch")
    ax.text(0, -1.65, "arms + legs (branch) + nested fingers (flexible)",
            ha="center", fontsize=7.5, color="#555")


def principles(ax):
    ax.text(0, 2.3, "Three moves, one grammar", ha="center", fontsize=9, weight="bold")
    # scale
    chain(ax, (-2.3, 1.4), 0, 4, 0.32, 8, color=TRUNK, taper=1.0)
    ax.text(-1.6, 1.0, "scale: add segments", ha="center", fontsize=7, color="#555")
    # branch
    b = chain(ax, (0.6, 1.5), 0, 3, 0.32, 8, color=TRUNK, taper=1.0)
    chain(ax, b[1], -1.2, 2, 0.3, 6, color=LIMB, dof="pitch")
    ax.text(1.2, 1.0, "branch: a segment\non a segment", ha="center", fontsize=7, color="#555")
    # nest
    chain(ax, (-2.0, -0.6), -0.2, 6, 0.3, 7, color=LIMB, curl=0.32, taper=0.78)
    ax.text(-1.4, -1.4, "nest: small segments\nin series → flexible", ha="center",
            fontsize=7, color="#555")
    # DOF
    for i, (d, lab) in enumerate([("lateral", "yaw"), ("pitch", "pitch"),
                                  ("roll", "roll"), ("telescoping", "tele")]):
        caz_glyph(ax, 0.7 + i * 0.7, -0.6, 0.22, dof=d)
        ax.text(0.7 + i * 0.7, -1.0, lab, ha="center", fontsize=6.5, color="#555")
    ax.text(1.75, -0.05, "configure DOF per joint", ha="center", fontsize=7, color="#555")
    ax.set_xlim(-3, 3); ax.set_ylim(-2, 2.6); ax.set_aspect("equal"); ax.axis("off")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    fig = plt.figure(figsize=(13.5, 9))
    gs = fig.add_gridspec(2, 3, hspace=0.28, wspace=0.12)
    worm(_ax(fig, gs[0, 0], "Worm", (-2.0, 1.4), (-1.1, 1.0)))
    fish(_ax(fig, gs[0, 1], "Fish", (-2.2, 2.6), (-1.4, 1.4)))
    lizard(_ax(fig, gs[0, 2], "Lizard / quadruped", (-2.6, 1.7), (-1.7, 1.2)))
    bird(_ax(fig, gs[1, 0], "Bird", (-1.6, 2.2), (-1.6, 1.8)))
    biped(_ax(fig, gs[1, 1], "Biped (human-like)", (-1.8, 1.8), (-1.9, 2.2)))
    principles(fig.add_subplot(gs[1, 2]))
    fig.suptitle("A menagerie from one grammar — scale · branch · nest · configure DOF",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = os.path.join(figdir, "menagerie.png")
    fig.savefig(out, dpi=130); print(f"[saved] {out}")
