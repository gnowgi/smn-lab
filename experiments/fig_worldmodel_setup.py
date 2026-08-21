# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Tutorial figure: what the worldmodel_morphology experiment actually is.
A: the world (scalar field). B: the four morphologies to scale. C: one body,
static and straight, reading the field at its 16 sensor points."""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

FIELD = [(0.9, 0.7, 1.0, 0.35), (-0.8, 0.6, 0.9, 0.35), (0.1, -0.9, 1.0, 0.35),
         (-0.6, -0.5, 0.8, 0.35), (0.7, -0.2, 0.9, 0.35)]
BODIES = {"small-narrow": (0.05, 0.04), "small-wide": (0.05, 0.13),
          "large-narrow": (0.10, 0.04), "large-wide": (0.10, 0.13)}
W = 0.025


def field_grid(xlim, ylim, n=200):
    xs = np.linspace(*xlim, n); ys = np.linspace(*ylim, n)
    X, Y = np.meshgrid(xs, ys); Z = np.zeros_like(X)
    for sx, sy, a, s in FIELD:
        Z += a * np.exp(-((X - sx) ** 2 + (Y - sy) ** 2) / (2 * s * s))
    return X, Y, Z


def body_sites(h, off, x0=0.0, y0=0.0):
    """Straight body, head at (x0,y0), extends toward -x. Returns seg centers and
    L/R sensor points."""
    seglen = 2 * h
    cx = np.array([x0 - k * seglen for k in range(8)]); cy = np.full(8, y0)
    L = np.column_stack([cx, cy + (W + off)]); R = np.column_stack([cx, cy - (W + off)])
    return cx, cy, L, R


fig = plt.figure(figsize=(15, 5))

# A: the world
axA = fig.add_subplot(1, 3, 1)
X, Y, Z = field_grid((-1.6, 1.6), (-1.6, 1.6))
axA.contourf(X, Y, Z, levels=18, cmap="YlOrRd")
for sx, sy, a, s in FIELD:
    axA.plot(sx, sy, "k*", ms=12)
axA.add_patch(Rectangle((-1, -1), 2, 2, fill=False, ec="black", ls="--", lw=1.5))
axA.text(0, 1.06, "poses sampled in here (heading fixed)", ha="center", fontsize=8)
axA.set_title("A. The WORLD = one fixed scalar field\n(5 Gaussian 'sources', ★). No objects, no walls.", fontsize=9)
axA.set_aspect("equal"); axA.set_xlabel("world x"); axA.set_ylabel("world y")

# B: the four morphologies to scale
axB = fig.add_subplot(1, 3, 2)
for i, (name, (h, off)) in enumerate(BODIES.items()):
    y0 = -i * 0.45
    cx, cy, L, R = body_sites(h, off, x0=0.7, y0=y0)
    for k in range(8):
        axB.add_patch(Rectangle((cx[k] - h, cy[k] - W), 2 * h, 2 * W,
                                fc="0.55" if k else "#2c6fbb", ec="k", lw=0.4))
    axB.scatter(L[:, 0], L[:, 1], c="#c0392b", s=14, zorder=3)
    axB.scatter(R[:, 0], R[:, 1], c="#2050c0", s=14, zorder=3)
    axB.text(-1.05, y0, f"{name}\nh={h}, off={off}", va="center", fontsize=7.5)
axB.set_xlim(-1.15, 0.9); axB.set_ylim(-1.5, 0.35)
axB.set_title("B. The four MORPHOLOGIES (to scale)\nsame 8 segments; vary length h and sensor offset\n"
              "red=left sensor, blue=right sensor", fontsize=9)
axB.set_aspect("equal"); axB.axis("off")

# C: one body reading the field
axC = fig.add_subplot(1, 3, 3)
axC.contourf(X, Y, Z, levels=18, cmap="YlOrRd", alpha=0.85)
cx, cy, L, R = body_sites(0.10, 0.13, x0=-0.1, y0=0.25)
for k in range(8):
    axC.add_patch(Rectangle((cx[k] - 0.10, cy[k] - W), 0.20, 2 * W, fc="0.4", ec="k", lw=0.4, zorder=2))
axC.scatter(L[:, 0], L[:, 1], c="#c0392b", s=30, zorder=4, label="16 field readings")
axC.scatter(R[:, 0], R[:, 1], c="#2050c0", s=30, zorder=4)
axC.set_xlim(-1.6, 1.6); axC.set_ylim(-1.6, 1.6); axC.set_aspect("equal")
axC.set_title("C. One body, TELEPORTED to a pose, held STRAIGHT & STILL.\n"
              "It reads the field at its 16 sensor points. Nothing moves.\n"
              "Task: from those 16 numbers, where am I? (x,y)", fontsize=9)
axC.legend(loc="lower left", fontsize=8)

fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "worldmodel_setup_tutorial.png")
fig.savefig(out, dpi=130)
print("saved", os.path.normpath(out))
