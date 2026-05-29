# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Draw the agent's geometry -- the body schema and the agent placed in the
scene -- so the experimental setup is legible.

Left panel: the body schema in the body frame (where each zone sits, the
opponent drive pair, the whisker fan). Right panel: the agent at its start pose
inside the arena, with its whisker rays, against the objects it will map.

Everything is drawn from `MouseSchema` and the arena constants, so the picture
always matches the model actually simulated. A real MuJoCo render is attempted
as a bonus (`figures/scene_render.png`) but is not required.

Run:  ../.venv/bin/python scene_geometry.py        (from this directory)
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.body import MouseSchema

ARENA = 1.4
POSE = (-0.8, 0.7, -0.6)        # the agent's start pose (x, y, yaw)
BODY_HX, BODY_HY = 0.09, 0.06   # body half-extents (matches the MJCF geom)
OBJECTS = [("cyl", 0.55, 0.45, 0.12, None), ("box", -0.6, -0.35, 0.12, 0.18)]


def _R(yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return np.array([[c, -s], [s, c]])


def _body_box(ax, px, py, yaw, fc, lw=1.5, alpha=1.0):
    corners = np.array([[-BODY_HX, -BODY_HY], [BODY_HX, -BODY_HY],
                        [BODY_HX, BODY_HY], [-BODY_HX, BODY_HY]])
    w = (corners @ _R(yaw).T) + [px, py]
    ax.fill(w[:, 0], w[:, 1], facecolor=fc, edgecolor="#234", lw=lw, alpha=alpha, zorder=3)


def draw(schema: MouseSchema, out: str):
    fig, (axb, axs) = plt.subplots(1, 2, figsize=(13, 6.6))

    # ---- left: body schema (body frame) ----
    axb.set_title("The agent's geometry (body schema)", fontsize=12)
    _body_box(axb, 0, 0, 0, "#cfe0f7")
    axb.annotate("", xy=(0.30, 0), xytext=(0, 0),
                 arrowprops=dict(arrowstyle="-|>", color="#456", lw=1.5))
    axb.text(0.31, 0, "forward (+x)", va="center", fontsize=9, color="#456")
    axb.scatter([0], [0], c="#e8c000", s=60, zorder=4)
    axb.text(0.0, -0.035, "IMU\n(velocimeter+gyro)", ha="center", va="top", fontsize=8, color="#776")
    # drive zones (opponent pairs: forward + backward)
    for name, (x, y) in schema.drive_zones.items():
        axb.scatter([x], [y], c="#1a9c2a", s=90, zorder=4)
        axb.annotate("", xy=(x + 0.07, y), xytext=(x - 0.07, y),
                     arrowprops=dict(arrowstyle="<|-|>", color="#1a9c2a", lw=1.5))
        axb.text(x, y + 0.03, f"{name}\n({x:+.2f}, {y:+.2f})", ha="center", va="bottom",
                 fontsize=8, color="#176")
    # whisker fan
    for (wx, wy, a) in schema.whiskers:
        ex, ey = wx + 0.5 * math.cos(a), wy + 0.5 * math.sin(a)
        axb.plot([wx, ex], [wy, ey], color="#e07b00", lw=1.2, alpha=0.8, zorder=2)
        axb.scatter([wx], [wy], c="#e07b00", s=30, zorder=4)
        axb.text(ex, ey, f"{math.degrees(a):+.0f}°", fontsize=8, color="#a55", ha="left", va="center")
    axb.text(schema.whiskers[0][0], 0.0, "whisker fan (S)", fontsize=8, color="#a55",
             ha="left", va="bottom")
    axb.set_aspect("equal"); axb.set_xlim(-0.25, 0.8); axb.set_ylim(-0.45, 0.45)
    axb.set_xlabel("body x (m)"); axb.set_ylabel("body y (m)")

    # ---- right: agent in the scene ----
    px, py, yaw = POSE
    axs.set_title("The agent in the scene (at its start pose)", fontsize=12)
    axs.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#888", lw=2))
    for o in OBJECTS:
        if o[0] == "cyl":
            axs.add_patch(Circle((o[1], o[2]), o[3], facecolor="#f3d6d0", ec="#b66", lw=1.5))
        else:
            axs.add_patch(Rectangle((o[1] - o[3], o[2] - o[4]), 2 * o[3], 2 * o[4],
                                    facecolor="#d6f0da", ec="#6a6", lw=1.5))
    _body_box(axs, px, py, yaw, "#2a5cc8")
    Rk = _R(yaw)
    for (wx, wy, a) in schema.whiskers:
        sxy = Rk @ [wx, wy] + [px, py]
        ex, ey = sxy[0] + 0.55 * math.cos(yaw + a), sxy[1] + 0.55 * math.sin(yaw + a)
        axs.plot([sxy[0], ex], [sxy[1], ey], color="#e07b00", lw=1.2, alpha=0.85, zorder=2)
    for name, (x, y) in schema.drive_zones.items():
        dxy = Rk @ [x, y] + [px, py]
        axs.scatter([dxy[0]], [dxy[1]], c="#1a9c2a", s=45, zorder=4)
    axs.set_aspect("equal"); axs.set_xlim(-1.6, 1.6); axs.set_ylim(-1.6, 1.6)
    axs.set_xlabel("world x (m)"); axs.set_ylabel("world y (m)")
    axs.text(0, -1.55, "blue = body · green = located drive zones · orange = whisker rays",
             ha="center", fontsize=9, color="#444")

    fig.suptitle("smn-lab — agent geometry and scene", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


def try_render(schema: MouseSchema, out: str):
    """Bonus: a real top-down MuJoCo render, if a GL backend is available."""
    for backend in ("egl", "osmesa", "glfw"):
        try:
            os.environ["MUJOCO_GL"] = backend
            import mujoco
            from smn_lab.model import build_p2_xml
            model = mujoco.MjModel.from_xml_string(build_p2_xml(schema, arena_half=ARENA))
            data = mujoco.MjData(model)
            jx = model.jnt_qposadr[model.joint("slide_x").id]
            jy = model.jnt_qposadr[model.joint("slide_y").id]
            jw = model.jnt_qposadr[model.joint("yaw").id]
            data.qpos[jx], data.qpos[jy], data.qpos[jw] = POSE
            mujoco.mj_forward(model, data)
            cam = mujoco.MjvCamera()
            cam.lookat[:] = [0, 0, 0.12]; cam.distance = 4.2
            cam.elevation = -90; cam.azimuth = 90
            r = mujoco.Renderer(model, height=720, width=720)
            r.update_scene(data, cam)
            plt.imsave(out, r.render())
            print(f"[saved] {out}  (MUJOCO_GL={backend})")
            return
        except Exception as e:
            last = e
    print(f"[skip] MuJoCo render unavailable ({type(last).__name__}); schematic suffices.")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    schema = MouseSchema()
    draw(schema, os.path.join(figdir, "agent_geometry.png"))
    try_render(schema, os.path.join(figdir, "scene_render.png"))
