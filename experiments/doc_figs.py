# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Documentation figures: a 3D hero render + per-experiment 'setup' diagrams.

For visual orientation on the docs site. Each current-series experiment gets a
setup figure: the agent's morphology (in the diagram grammar) beside a schematic of
its world and the experimental conditions -- so the setup is visible at a glance.
Also renders one 3D screenshot of the MuJoCo world for the landing page.

Run:  ../.venv/bin/python doc_figs.py        (from this directory)
"""
from __future__ import annotations
import os, sys
os.environ.setdefault("MUJOCO_GL", "egl")        # headless 3D rendering
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml
from smn_lab.morphology import (crawler_schema, render_morphology, caz_glyph,
                                sensor_node, MODALITY_COLORS, NETWORK_COLOR)
from smn_lab.fields import ScalarField

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")


# ----------------------------------------------------------------- 3D render ---
def render_3d(xml, out, lookat, dist, elev, azim, w=900, h=560):
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    r = mujoco.Renderer(model, height=h, width=w)
    cam = mujoco.MjvCamera()
    cam.lookat[:] = lookat; cam.distance = dist
    cam.elevation = elev; cam.azimuth = azim
    r.update_scene(data, cam)
    img = r.render(); r.close()
    plt.imsave(out, img)
    print(f"[saved] {out}")


# --------------------------------------------------------- world schematics ---
def _field_contours(ax, sources, xlim, ylim, cmap="YlOrRd"):
    xs = np.linspace(*xlim, 120); ys = np.linspace(*ylim, 120)
    X, Y = np.meshgrid(xs, ys); Z = np.zeros_like(X)
    for sx, sy, amp, sig in sources:
        Z += amp * np.exp(-((X - sx) ** 2 + (Y - sy) ** 2) / (2 * sig * sig))
    ax.contourf(X, Y, Z, levels=16, cmap=cmap, alpha=0.85)


def _gradient_bg(ax, ga, gb, xlim, ylim):
    xs = np.linspace(*xlim, 60); ys = np.linspace(*ylim, 60)
    X, Y = np.meshgrid(xs, ys)
    ax.contourf(X, Y, ga * X + gb * Y, levels=16, cmap="YlOrRd", alpha=0.8)


def draw_world(ax, spec):
    """Top-down schematic of an experiment's world + conditions."""
    xlim = spec.get("xlim", (-2.2, 2.4)); ylim = spec.get("ylim", (-2.2, 2.2))
    if spec.get("sources"):
        _field_contours(ax, spec["sources"], xlim, ylim)
    if spec.get("gradient"):
        _gradient_bg(ax, *spec["gradient"], xlim, ylim)
    for (ox, oy, orr) in spec.get("objects", []):
        ax.add_patch(Circle((ox, oy), orr, color="#7a1d12", zorder=4))
    if spec.get("source_star"):
        ax.scatter(*spec["source_star"], marker="*", s=320, color="#b00000",
                   edgecolors="k", zorder=6)
    if spec.get("agent_at"):
        ax.add_patch(FancyBboxPatch((spec["agent_at"][0] - 0.18, spec["agent_at"][1] - 0.05),
                     0.36, 0.10, boxstyle="round,pad=0.0,rounding_size=0.03",
                     facecolor="#1538a0", edgecolor="k", zorder=5))
    for ar in spec.get("arrows", []):
        ax.add_patch(FancyArrowPatch(ar[0], ar[1], arrowstyle="-|>", mutation_scale=16,
                     color=ar[2] if len(ar) > 2 else "#333", lw=2.0, zorder=7))
    for (tx, ty, txt, col) in spec.get("labels", []):
        ax.text(tx, ty, txt, fontsize=8, color=col, ha="center", va="center",
                zorder=8, bbox=dict(boxstyle="round", fc="white", ec=col, alpha=0.85))
    ax.set_aspect("equal"); ax.set_xlim(xlim); ax.set_ylim(ylim)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    if spec.get("title"):
        ax.set_title(spec["title"], fontsize=9.5)


# --------------------------------------------------------- agent schematics ---
def draw_limb(ax, tool=False, tool_label=""):
    """A single hinge limb (an opponent-pair CAZ), optionally with a tool link."""
    ax.add_patch(Circle((0, 0), 0.05, color="#333", zorder=2))     # base pivot
    ax.plot([0, 1.0], [0, 0], color="#3a4a5e", lw=8, solid_capstyle="round", zorder=1)
    caz_glyph(ax, 0.0, 0.0, 0.16, dof="lateral")                   # the actuated CAZ
    ax.text(0.0, -0.3, "CAZ\n(opponent pair)", ha="center", fontsize=7, color="#333")
    ax.text(0.55, 0.18, "limb", ha="center", fontsize=8, color="#33414f")
    if tool:
        ax.plot([1.0, 1.7], [0, 0], color="#9a6a2f", lw=6, solid_capstyle="round", zorder=1)
        # spring symbol at the tool joint
        zz = np.linspace(1.0, 1.18, 9); ax.plot(zz, 0.06 * np.sin(np.linspace(0, 4 * np.pi, 9)),
                                                color="#9a6a2f", lw=1.4, zorder=3)
        ax.text(1.35, 0.18, "tool", ha="center", fontsize=8, color="#9a6a2f")
        if tool_label:
            ax.text(1.35, -0.28, tool_label, ha="center", fontsize=7.5, color="#9a6a2f")
        ax.scatter([1.7], [0], s=40, color="#b00000", zorder=4)    # tip
        ax.text(1.7, 0.16, "tip", ha="center", fontsize=7, color="#b00000")
        ax.set_xlim(-0.4, 2.0)
    else:
        ax.scatter([1.0], [0], s=40, color="#b00000", zorder=4)
        ax.text(1.0, 0.16, "tip", ha="center", fontsize=7, color="#b00000")
        ax.set_xlim(-0.4, 1.4)
    ax.set_ylim(-0.5, 0.5); ax.set_aspect("equal"); ax.axis("off")


def draw_agent(ax, spec):
    a = spec["agent"]
    if a == "limb":
        draw_limb(ax)
    elif a == "limb_tool":
        draw_limb(ax, tool=True, tool_label=spec.get("agent_note", ""))
    else:                                            # crawler schema
        render_morphology(ax, spec["schema"], compass=False, show_labels=False)
    if spec.get("agent_title"):
        ax.set_title(spec["agent_title"], fontsize=9.5)


# ------------------------------------------------------ per-experiment specs ---
def crawler(n=3, touch=False, fields=("chem",), eye=False):
    return crawler_schema(n_seg=n, touch=touch, field_modalities=fields,
                          localizers=(("vision",) if eye else ()))


SETUPS = {
    "c0_crawler": dict(
        agent="crawler", schema=crawler(3, fields=("chem",)),
        agent_title="3-block crawler · bilateral chemical sensing",
        world=dict(sources=[(1.6, 1.1, 1.0, 0.9)], source_star=(1.6, 1.1),
                   agent_at=(0, 0), xlim=(-0.6, 2.4), ylim=(-0.8, 1.8),
                   title="World: one chemical source (climb the gradient)")),
    "c1_touch": dict(
        agent="crawler", schema=crawler(3, touch=True, fields=("chem",)),
        agent_title="3-block crawler · touch skin + chemical sensing",
        world=dict(sources=[(1.9, 1.05, 1.0, 1.0)], source_star=(1.9, 1.05),
                   objects=[(0.78, 0.0, 0.12)], agent_at=(0, 0),
                   xlim=(-0.6, 2.6), ylim=(-0.8, 1.7),
                   title="World: source + an object on the path (gravity on)")),
    "sweep_c0_coupling": dict(
        agent="crawler", schema=crawler(3, fields=()),
        agent_title="3-block crawler · coupling strength is swept",
        world=dict(agent_at=(0, 0), xlim=(-1.5, 1.5), ylim=(-1.2, 1.2),
                   arrows=[((0.2, 0), (1.2, 0), "#1538a0")],
                   labels=[(0.7, 0.35, "pure locomotion\n(no field)", "#1538a0")],
                   title="World: empty — locomotion only")),
    "sweep_geometry_worldmodel": dict(
        agent="crawler", schema=crawler(7, fields=("chem",)),
        agent_title="crawler · segment count swept (3,5,7,9)",
        world=dict(sources=[(1.6, 1.1, 1.0, 0.8), (-1.4, 0.9, 0.9, 0.9),
                            (0.2, -1.6, 1.1, 0.7)], agent_at=(0, 0),
                   title="World: fixed 3-source field (held constant; body varied)")),
    "q2_reafference": dict(
        agent="crawler", schema=crawler(5, fields=("chem",)),
        agent_title="5-block crawler · reafference",
        world=dict(gradient=(1.6, 1.2), agent_at=(0, 0),
                   arrows=[((-0.6, 1.6), (0.4, 0.3), "#b00000")],
                   labels=[(0.0, 1.9, "moving exafference\nsource", "#b00000")],
                   title="World: static gradient + a MOVING source (exafference)")),
    "sweep_q1_modulation": dict(
        agent="crawler", schema=crawler(7, fields=("chem",)),
        agent_title="crawler · per-zone modulation vs foil; count swept",
        world=dict(gradient=(1.6, 1.2), agent_at=(0, 0),
                   labels=[(0.4, 0.3, "localized\nworld change", "#b00000")],
                   title="World: static gradient + LOCALIZED world change")),
    "sweep_q1b_resolution": dict(
        agent="crawler", schema=crawler(7, fields=("chem",)),
        agent_title="crawler · modulation vs foil; count swept",
        world=dict(gradient=(1.6, 1.2), agent_at=(0, 0),
                   labels=[(0.0, 1.6, "uniform 'tide' —\nDISTRIBUTED change", "#b00000")],
                   title="World: static gradient + DISTRIBUTED world change")),
    "sweep_pred1_haltability": dict(
        agent="limb", agent_title="single hinge limb (an opponent pair)",
        world=dict(xlim=(-1.3, 1.3), ylim=(-1.0, 1.0),
                   arrows=[((0.9, 0.55), (-0.7, 0.55), "#b00000")],
                   labels=[(0.9, 0.78, "target A", "#1538a0"),
                           (-0.7, 0.78, "target B (jumps mid-reach)", "#b00000")],
                   title="Task: reach a target that JUMPS mid-movement")),
    "sweep_pred2_zonal": dict(
        agent="limb_tool", agent_title="limb + passive tool (the 'material')",
        agent_note="rigid  vs  viscoelastic",
        world=dict(xlim=(-1.3, 1.3), ylim=(-1.0, 1.0),
                   labels=[(-0.6, 0.4, "rigid tool\n(stiff)", "#333"),
                           (0.6, -0.4, "viscoelastic tool\n(compliant)", "#9a6a2f"),
                           (0, 0.75, "same reach-and-hold task", "#1538a0")],
                   title="Same task, two materials (rigid vs viscoelastic)")),
    "sweep_pred3_antagonistic": dict(
        agent="limb", agent_title="single hinge limb (an opponent pair)",
        world=dict(xlim=(-1.3, 1.3), ylim=(-1.0, 1.0),
                   arrows=[((0.0, 0.6), (0.0, 0.1), "#b00000")],
                   labels=[(0.0, 0.8, "perturbation pulse", "#b00000"),
                           (0.0, -0.5, "co-contraction swept", "#1538a0")],
                   title="Task: hold a set-point under a perturbation")),
}


def setup_fig(key, spec, out):
    fig = plt.figure(figsize=(11, 4.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.22)
    draw_agent(fig.add_subplot(gs[0]), spec)
    draw_world(fig.add_subplot(gs[1]), spec["world"])
    fig.suptitle(f"Setup — {key}", fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    # landing hero: a real 3D render of the crawler in its world
    render_3d(build_crawler_xml(n_seg=3, gravity_on=True, with_floor=True,
                                with_walls=True, touch=True, objects=[(0.78, 0.0, 0.12)]),
              os.path.join(FIG, "hero_world_3d.png"),
              lookat=[0.38, 0.0, 0.08], dist=1.75, elev=-26, azim=130)
    for key, spec in SETUPS.items():
        setup_fig(key, spec, os.path.join(FIG, f"setup_{key}.png"))
