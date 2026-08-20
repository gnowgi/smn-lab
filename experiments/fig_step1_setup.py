# SPDX-License-Identifier: GPL-3.0-or-later
"""Tutorial figure for worldmodel_from_selfmodel (step 1): one body, one field source."""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

H, W, OFF, SEGLEN = 0.07, 0.025, 0.06, 0.14
SRC_Y, SIG = 0.30, 0.24


def field_at(x, y, sx):
    return np.exp(-((x - sx) ** 2 + (y - SRC_Y) ** 2) / (2 * SIG * SIG))


fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for ax, k_src, title in [(axes[0], 2, "source beside segment k_src = 2"),
                         (axes[1], 5, "source beside segment k_src = 5")]:
    sx = -SEGLEN * k_src
    xs = np.linspace(-1.15, 0.25, 240); ys = np.linspace(-0.15, 0.6, 160)
    X, Y = np.meshgrid(xs, ys)
    ax.contourf(X, Y, field_at(X, Y, sx), levels=16, cmap="YlOrRd")
    # the straight body (phase-2 sensing pose): 8 segments, head at 0 toward +x
    for k in range(8):
        cx = -SEGLEN * k
        ax.add_patch(Rectangle((cx - H, -W), 2 * H, 2 * W,
                               fc="#2c6fbb" if k == 0 else "0.5", ec="k", lw=0.5, zorder=3))
        ax.scatter([cx], [W + OFF], c="#c0392b", s=22, zorder=4)          # left sensor
        ax.scatter([cx], [-(W + OFF)], c="#2050c0", s=22, zorder=4)       # right sensor
        ax.text(cx, -0.11, f"{k}", ha="center", fontsize=7, color="0.3")
    ax.plot(sx, SRC_Y, "k*", ms=16, zorder=5)
    ax.annotate("the ONE source", (sx, SRC_Y), (sx - 0.15, SRC_Y + 0.12), fontsize=8,
                arrowprops=dict(arrowstyle="->"))
    ax.text(0.02, -0.02, "head", fontsize=7, color="#2c6fbb")
    ax.set_title(title, fontsize=9); ax.set_aspect("equal"); ax.set_xlabel("world x")
    ax.set_ylabel("world y")
fig.suptitle("Step 1 setup: ONE 8-segment body, ONE scalar-field source (swept along the body). "
             "No objects, no walls, no gravity.", fontsize=10)
fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "step1_setup_tutorial.png")
fig.savefig(out, dpi=130); print("saved", os.path.normpath(out))
