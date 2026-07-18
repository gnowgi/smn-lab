# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""C1 -- the crawler under gravity: ventral touch skin, objects, halt-on-contact.

The v1 organism of Lesson 1. The three-block crawler now has mass under gravity
(gravity present; the body glides in its support plane); each segment carries a
**ventral touch skin** whose resting reading is its weight load and which
registers object/wall contact as force on top of that. An object sits in the
crawler's path to a chemical source.

The demonstration is the halt->aboutness precursor, in its simplest physical
form -- *objecthood as resistance*:
  1. a chemotactic BAP (traveling wave biased by the bilateral field) carries the
     crawler up the gradient;
  2. it meets the object; the ventral touch skin registers the contact as a force
     spike above the resting load, localized to the segment that touches;
  3. that contact recruits a HAP that **halts** the wave -- the object's
     resistance stops the action. The body comes to rest *against* the object: it
     has encountered something that does not yield to its modulation.

Full negotiation around the object (back up, reorient, resume) needs a richer
HAP/NAP and is a later experiment; here the point is that contact halts, and the
skin reads the object as resistance.

Outputs figures/c1_touch.png:
  (A) arena: field, object, the crawler's path arrested at the object;
  (B) the ventral touch skin over time: per-segment force, resting load, contact
      threshold, and the halt episodes;
  (C) the messaging beam at the contact frame, nodes coloured by touch force --
      the contacting (head) segment is hot.

Run:  ../.venv/bin/python c1_touch.py        (from this directory)
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag
from smn_lab.control import OpponentBoard, MessagingBeam
from smn_lab.fields import ScalarField
from smn_lab import viz

# ---- parameters -----------------------------------------------------------
SEED = 3
DT = 0.002
T_END = 55.0
N_SEG = 3
SOURCE = (1.9, 1.05)
OBJECT = (0.78, 0.00, 0.12)        # (x, y, radius) -- on the path, grazeable
FIELD = ScalarField([(*SOURCE, 1.0, 1.0)])
DRAG_LONG, DRAG_TRANS = 0.5, 7.0
TURN_GAIN = 4.0
BIAS_SIGN = -1.0
SEG_MASS = 0.05                  # must match build_crawler_xml default
GRAV = 9.81
WEIGHT = SEG_MASS * GRAV          # resting ventral load borne per segment (N)
# --8<-- [start:haltparams]
TOUCH_MARGIN = 0.03              # N of contact force above resting load = contact
                                  # (this slow drag-driven worm pushes only gently)
HALT_GATE = 0.12                 # wave amplitude while halted (a residual tonus)
HALT_S = 2.0                     # how long contact holds the halt
# --8<-- [end:haltparams]


def run():
    model = mujoco.MjModel.from_xml_string(build_crawler_xml(
        n_seg=N_SEG, gravity_on=True, with_floor=True, with_walls=True,
        touch=True, objects=[OBJECT]))
    data = mujoco.MjData(model)

    seg_ids = [model.body(f"seg{k}").id for k in range(N_SEG)]
    senseL, senseR = model.site("sense_L").id, model.site("sense_R").id
    j_ids = [model.joint(f"j{k}").id for k in range(1, N_SEG)]
    j_qadr = [model.jnt_qposadr[j] for j in j_ids]
    j_vadr = [model.jnt_dofadr[j] for j in j_ids]
    aid_p = [model.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)]
    aid_n = [model.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)]
    touch_adr = [model.sensor(f"touch{k}").adr[0] for k in range(N_SEG)]

    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9, turn_gain=TURN_GAIN)
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in j_ids]

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    halt_timer = 0
    baseline = WEIGHT                       # the steady resting ventral load
    log = {k: [] for k in ("t", "x", "y", "touch", "contact", "halted",
                           "node_xy", "dist")}

    for i in range(n):
        t = i * DT
        # --8<-- [start:touchskin]
        # ventral skin = resting weight load + simulated object/wall contact force
        contact_force = np.array([float(data.sensordata[touch_adr[k]]) for k in range(N_SEG)])
        touch = WEIGHT + contact_force
        contact = contact_force.max() > TOUCH_MARGIN
        # --8<-- [end:touchskin]

        cL = FIELD.sample(*data.site_xpos[senseL][:2])
        cR = FIELD.sample(*data.site_xpos[senseR][:2])
        # --8<-- [start:halt]
        if contact:                                       # contact recruits the HAP halt
            halt_timer = int(HALT_S / DT)
        halted = halt_timer > 0
        bias = BIAS_SIGN * (cL - cR)                     # chemotactic steer
        gate = HALT_GATE if halted else 1.0              # halt = drop the wave amplitude
        if halt_timer > 0:
            halt_timer -= 1

        theta_cmd = beam.command(DT, bias=bias) * gate   # the HAP gates the BAP wave
        # --8<-- [end:halt]
        for k in range(len(j_ids)):
            th, thd = float(data.qpos[j_qadr[k]]), float(data.qvel[j_vadr[k]])
            a_r, a_l, _ = boards[k].commands(th, thd, theta_cmd[k], 0.0)
            data.ctrl[aid_p[k]], data.ctrl[aid_n[k]] = a_r, a_l

        apply_anisotropic_drag(model, data, seg_ids,
                               c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)

        if i % 5 == 0:
            hx, hy = data.xpos[seg_ids[0]][:2]
            log["t"].append(t); log["x"].append(hx); log["y"].append(hy)
            log["touch"].append(touch)
            log["contact"].append(bool(contact))
            log["halted"].append(bool(halted))
            log["node_xy"].append(np.array([data.xpos[seg_ids[k]][:2].copy()
                                            for k in range(N_SEG)]))
            log["dist"].append(float(np.hypot(hx - SOURCE[0], hy - SOURCE[1])))

    for k in ("t", "x", "y", "touch", "contact", "halted", "dist"):
        log[k] = np.array(log[k])
    log["baseline"] = baseline
    return log


def summarize(log):
    x, y = log["x"], log["y"]
    return dict(
        net_disp=float(np.hypot(x[-1] - x[0], y[-1] - y[0])),
        dist_start=float(log["dist"][0]), dist_end=float(log["dist"][-1]),
        closed_gap=float(log["dist"][0] - log["dist"][-1]),
        weight_baseline=float(log["baseline"]),
        touch_peak=float(log["touch"].max()),
        contact_frac=float(log["contact"].mean()),
        halt_frac=float(log["halted"].mean()),
        dist_at_halt=_dist_at_first_halt(log),
    )


def _dist_at_first_halt(log):
    idx = np.argmax(log["halted"]) if log["halted"].any() else -1
    return float(log["dist"][idx]) if idx >= 0 else float("nan")


def plot(log, stats, out):
    fig = plt.figure(figsize=(15, 5.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1.15, 0.95], wspace=0.30)

    # (A) arena
    axA = fig.add_subplot(gs[0, 0])
    pad = 0.5
    xlim = (min(log["x"].min(), 0) - pad, max(log["x"].max(), SOURCE[0]) + pad)
    ylim = (min(log["y"].min(), 0) - pad, max(log["y"].max(), SOURCE[1]) + pad)
    X, Y, Z = FIELD.grid(xlim, ylim, 140)
    axA.contourf(X, Y, Z, levels=18, cmap="YlOrRd", alpha=0.75)
    axA.add_patch(plt.Circle(OBJECT[:2], OBJECT[2], color="#7a1d12", zorder=4))
    axA.plot(log["x"], log["y"], color="#1538a0", lw=1.7, zorder=3, label="head path")
    cm = log["contact"]
    axA.scatter(log["x"][cm], log["y"][cm], s=14, color="#00b0b0", zorder=5,
                label="contact")
    axA.scatter(*SOURCE, marker="*", s=300, color="#b00000", edgecolors="k",
                zorder=6, label="source")
    axA.scatter(log["x"][0], log["y"][0], s=40, color="k", zorder=6, label="start")
    axA.set_aspect("equal"); axA.set_xlim(xlim); axA.set_ylim(ylim)
    axA.set_xlabel("x (m)"); axA.set_ylabel("y (m)")
    axA.legend(loc="lower right", fontsize=7)
    axA.set_title("A — chemotactic crawl arrested at the object (resistance)", fontsize=10)

    # (B) ventral touch skin over time
    axB = fig.add_subplot(gs[0, 1])
    for k in range(N_SEG):
        axB.plot(log["t"], log["touch"][:, k], lw=0.8, label=f"seg{k}")
    axB.axhline(stats["weight_baseline"], color="#888", ls=":", lw=0.9,
                label="resting weight")
    axB.axhline(stats["weight_baseline"] + TOUCH_MARGIN, color="#b00", ls="--",
                lw=0.8, label="contact threshold")
    halt_t = log["t"][log["halted"]]                     # shade the halt episodes
    if len(halt_t):
        axB.axvspan(halt_t.min(), halt_t.max(), color="#00b0b0", alpha=0.10, lw=0,
                    label="halted")
    axB.set_xlabel("time (s)"); axB.set_ylabel("touch force (N)")
    axB.legend(loc="upper right", fontsize=7, ncol=2)
    axB.set_title("B — ventral touch skin (force per segment)", fontsize=10)

    # (C) beam graph at the peak-contact frame, nodes coloured by touch force
    axC = fig.add_subplot(gs[0, 2])
    fr = int(np.argmax(log["touch"].max(axis=1)))
    node_xy = log["node_xy"][fr]
    node_val = log["touch"][fr]
    edges = [(k, k + 1) for k in range(N_SEG - 1)]
    viz.draw_beam_graph(axC, node_xy, node_val, edges,
                        node_labels=[f"s{k}" for k in range(N_SEG)],
                        cmap="inferno", node_cbar_label="touch force (N)",
                        title="C — beam at contact (node = touch)")
    axC.add_patch(plt.Circle(OBJECT[:2], OBJECT[2], color="#7a1d12", alpha=0.4, zorder=0))
    axC.set_xlabel("x (m)"); axC.set_ylabel("y (m)")

    cap = (f"resting load = {stats['weight_baseline']:.2f} N  |  "
           f"touch peak on contact = {stats['touch_peak']:.2f} N  |  "
           f"halted {100*stats['halt_frac']:.0f}% of the run, "
           f"arrested {stats['dist_at_halt']:.2f} m from source")
    fig.text(0.5, 0.01, cap, ha="center", fontsize=9, color="#333")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    log = run()
    stats = summarize(log)
    print("\n=== C1 — crawler under gravity: touch skin + objects ===")
    for k, v in stats.items():
        print(f"  {k:16s} {v:.4f}")
    verdict = ("PASS: chemotactic crawl; the ventral touch skin registers the "
               "object as a force spike; contact halts the wave (objecthood as "
               "resistance)."
               if stats["touch_peak"] > stats["weight_baseline"] + TOUCH_MARGIN
               and stats["net_disp"] > 0.3 and stats["halt_frac"] > 0.05
               else "INCONCLUSIVE — tune drag/touch/halt params.")
    print("  verdict:", verdict)
    plot(log, stats, os.path.join(figdir, "c1_touch.png"))
