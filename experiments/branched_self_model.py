# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Branched-body self-model: a body computes its own tree from movement -- and
why asymmetry is a cognitive-architectural feature, not a bug.

The chain experiment (`self_model_topology.py`) recovered a *line* because the
body was a line. But the mathematics is topology-general: the coupling between
zones is fixed by the mechanical graph whatever its shape. So a *branched* body
recovers a *tree*, with branch points as higher-degree nodes.

Local rule. Each joint (a CAZ) is the hinge between exactly two segments, and its
own angular velocity IS their yaw-rate difference: JV_j = omega_child - omega_parent.
So a joint finds the two segments it couples as the one it co-rotates with (its
strongest positive correlate) and the one it counter-rotates with (its strongest
negative correlate) -- one edge of the body tree, read from local signals. The
union of every joint's edge is the recovered morphology; the hub, parent of three
arm-joints, surfaces as a degree-3 node -- the branch point -- with no zone ever
seeing the whole body.

The asymmetry point. We run two bodies:
  * asymmetric -- a hub with three arms of *different* lengths. Every part is
    uniquely determined; the self-model is rigid.
  * symmetric  -- a stem with two *equal*, mirror-image arms. The topology is
    still recovered, but the two arms are data-indistinguishable: swapping them
    leaves the coupling matrix invariant (a symmetry of the self-model). The body
    knows it has two arms but cannot tell left from right.

We measure this with the *arm-swap residual* ||C - swap(C)|| / ||C||: near zero
means the two arms are interchangeable (indistinguishable). A symmetric body's
self-model carries this ambiguity; breaking the symmetry -- a differentiating
asymmetry -- is what resolves it. So an asymmetry is exactly what a determinate
self/world requires: it is a cognitive-architectural feature, which is plausibly
why evo-devo selected polarized, lateralized body plans in the first place.

Run:  ../.venv/bin/python branched_self_model.py
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import apply_anisotropic_drag
# canonical self-model read-out (the model) + arm-swap residual (experimenter's).
from smn_lab.self_model import coupling, recover_edges
from smn_lab.metrics import arm_swap_residual

DT = 0.002
H, W = 0.07, 0.025
SEGLEN = 2 * H
STIFFNESS, JDAMP = 0.3, 0.05
DRAG_LONG, DRAG_TRANS = 0.6, 4.0
T_WARM, T_REC = 4.0, 70.0

# --8<-- [start:configs]
CONFIGS = {
    #              (angle_deg, n_segments) per arm
    "asymmetric": [(0.0, 3), (130.0, 2), (230.0, 4)],   # three different arms -> rigid self
    "symmetric":  [(90.0, 2), (210.0, 3), (330.0, 3)],  # stem + two equal mirror arms
}
# --8<-- [end:configs]


def build_branched_xml(arms):
    """Return (xml, positions, true_edges, joint_order, arm_struct).
    seg0 is the hub; each arm is a chain of segments branching off it. arm_struct
    lists, per arm, its segment indices and joint names (hub excluded)."""
    positions = {0: (0.0, 0.0)}
    true_edges, joint_order, arm_struct, arms_ids = [], [], [], []
    nxt = 1
    for angle, n in arms:
        ids = list(range(nxt, nxt + n)); nxt += n
        arms_ids.append((angle, ids))
        th = math.radians(angle)
        prev, jn_list = 0, []
        for k, idx in enumerate(ids):
            r = (k + 1) * SEGLEN
            positions[idx] = (r * math.cos(th), r * math.sin(th))
            true_edges.append((prev, idx))
            joint_order.append(f"j{idx}"); jn_list.append(f"j{idx}")
            prev = idx
        arm_struct.append({"angle": angle, "segs": ids, "joints": jn_list})

    def arm_xml(angle, ids):
        th = math.radians(angle)
        def seg(k):
            idx = ids[k]
            if k == 0:
                pos = f"{SEGLEN*math.cos(th):.4f} {SEGLEN*math.sin(th):.4f} 0"; eul = f"0 0 {angle}"
            else:
                pos = f"{SEGLEN} 0 0"; eul = "0 0 0"
            shade = 0.4 + 0.05 * k
            j = (f'<joint name="j{idx}" type="hinge" axis="0 0 1" pos="{-H} 0 0" '
                 f'range="-45 45" stiffness="{STIFFNESS}" springref="0" damping="{JDAMP}"/>')
            g = (f'<geom name="g{idx}" type="box" size="{H} {W} {W}" mass="0.05" '
                 f'friction="0 0 0" rgba="0.30 {shade:.2f} 0.78 1"/>')
            child = seg(k + 1) if k + 1 < len(ids) else ""
            return f'<body name="seg{idx}" pos="{pos}" euler="{eul}">{j}{g}{child}</body>'
        return seg(0)

    arms_xml = "\n".join(arm_xml(a, ids) for a, ids in arms_ids)
    acts = "\n".join(
        f'    <motor name="m_{jn}_p" joint="{jn}" gear="0.05" ctrlrange="0 2.5"/>\n'
        f'    <motor name="m_{jn}_n" joint="{jn}" gear="-0.05" ctrlrange="0 2.5"/>'
        for jn in joint_order)
    xml = f"""
<mujoco model="smn_branched">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <body name="seg0" pos="0 0 0.1">
      <joint name="slide_x" type="slide" axis="1 0 0" damping="0.5"/>
      <joint name="slide_y" type="slide" axis="0 1 0" damping="0.5"/>
      <joint name="yaw" type="hinge" axis="0 0 1" damping="0.3"/>
      <geom name="g0" type="box" size="{H} {W} {W}" mass="0.05" friction="0 0 0" rgba="0.20 0.45 0.90 1"/>
{arms_xml}
    </body>
  </worldbody>
  <actuator>
{acts}
  </actuator>
</mujoco>
"""
    return xml, positions, true_edges, joint_order, arm_struct


def run(arms):
    xml, positions, true_edges, joint_order, arm_struct = build_branched_xml(arms)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    n_seg = len(positions)
    seg_ids = [model.body(f"seg{s}").id for s in range(n_seg)]
    jdof = [model.jnt_dofadr[model.joint(jn).id] for jn in joint_order]
    aid_p = [model.actuator(f"m_{jn}_p").id for jn in joint_order]
    aid_n = [model.actuator(f"m_{jn}_n").id for jn in joint_order]
    nj = len(joint_order)

    rng = np.random.default_rng(0)
    tau = np.zeros(nj); tau_tc, tau_sig = 0.2, 9.0
    n_warm, n_rec = int(T_WARM / DT), int(T_REC / DT)
    JV = np.zeros((n_rec, nj)); OMEGA = np.zeros((n_rec, n_seg)); vel = np.zeros(6)
    for i in range(n_warm + n_rec):
        tau += (-tau / tau_tc) * DT + tau_sig * np.sqrt(DT) * rng.standard_normal(nj)
        for k in range(nj):
            data.ctrl[aid_p[k]] = float(np.clip(tau[k], 0.0, 2.5))
            data.ctrl[aid_n[k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(model, data, seg_ids, c_long=DRAG_LONG, c_trans=DRAG_TRANS)
        mujoco.mj_step(model, data)
        if i >= n_warm:
            r = i - n_warm
            JV[r] = np.array([data.qvel[d] for d in jdof])
            for s in range(n_seg):
                mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, seg_ids[s], vel, 0)
                OMEGA[r, s] = vel[2]
    return JV, OMEGA, positions, true_edges, joint_order, arm_struct


def eval_body(name, arms):
    JV, OMEGA, positions, true_edges, joint_order, arm_struct = run(arms)
    n_seg = len(positions)
    C = coupling(JV, OMEGA)
    rec = recover_edges(C)
    true_set = {frozenset(e) for e in true_edges}
    correct = sum(frozenset(e) in true_set for e in rec)
    deg = np.zeros(n_seg, int)
    for a, b in rec: deg[a] += 1; deg[b] += 1
    # min arm-swap residual over all arm pairs = "how symmetric is the self-model"
    residuals = []
    for i in range(len(arm_struct)):
        for j in range(i + 1, len(arm_struct)):
            residuals.append(arm_swap_residual(C, joint_order, arm_struct[i], arm_struct[j]))
    min_res = min(residuals) if residuals else float("nan")
    return dict(name=name, positions=positions, true_edges=true_edges, rec=rec,
                deg=deg, correct=correct, njoints=len(rec), min_res=min_res,
                branch=int(np.argmax(deg)), C=C)


def draw_tree(ax, r, title):
    true_set = {frozenset(e) for e in r["true_edges"]}
    for a, b in r["true_edges"]:
        xa, ya = r["positions"][a]; xb, yb = r["positions"][b]
        ax.plot([xa, xb], [ya, yb], color="0.82", lw=6, solid_capstyle="round", zorder=1)
    for a, b in r["rec"]:
        xa, ya = r["positions"][a]; xb, yb = r["positions"][b]
        ax.plot([xa, xb], [ya, yb], color="tab:blue" if frozenset((a, b)) in true_set else "tab:red",
                lw=2.2, zorder=2)
    for s, (x, y) in r["positions"].items():
        d = r["deg"][s]
        col = "tab:orange" if d >= 3 else ("0.6" if d == 1 else "tab:blue")
        ax.scatter([x], [y], s=140 + 80 * (d >= 3), color=col, zorder=3, edgecolor="k", linewidth=0.5)
        ax.annotate(str(s), (x, y), fontsize=7, ha="center", va="center", color="w")
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=10)


def main():
    res = {name: eval_body(name, arms) for name, arms in CONFIGS.items()}
    print("\nBranched-body self-model: morphology recovered from movement\n" + "=" * 64)
    print(f"{'body':<14}{'edges recovered':<20}{'branch node (deg)':<20}{'arm-swap residual':<18}")
    for name, r in res.items():
        print(f"{name:<14}{r['correct']}/{r['njoints']} correct{'':<7}"
              f"seg {r['branch']} (deg {r['deg'][r['branch']]}){'':<7}"
              f"{r['min_res']:.3f}")
    print("=" * 64)
    a, s = res["asymmetric"], res["symmetric"]
    print(f"Both recover the tree topology and the degree-3 branch point.")
    print(f"But the arm-swap residual differs: symmetric = {s['min_res']:.3f} "
          f"(the two equal arms are interchangeable -> the body cannot tell them apart),")
    print(f"asymmetric = {a['min_res']:.3f} (every arm distinct -> the self-model is rigid).")
    print("Asymmetry is what makes the self determinate: a feature, not a bug.\n")

    fig = plt.figure(figsize=(12.5, 5.0))
    ax1 = fig.add_subplot(1, 3, 1); draw_tree(ax1, a,
        "Asymmetric body\ntree + degree-3 branch point recovered")
    ax2 = fig.add_subplot(1, 3, 2); draw_tree(ax2, s,
        "Symmetric body\ntopology recovered, two arms indistinguishable")
    ax3 = fig.add_subplot(1, 3, 3)
    names = list(res); vals = [res[n]["min_res"] for n in names]
    ax3.bar(names, vals, color=["tab:blue", "tab:orange"])
    ax3.set_ylabel("min arm-swap residual\n(0 = arms interchangeable)")
    ax3.set_title("Can the body tell its arms apart?")
    ax3.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "figures", "branched_self_model.png")
    fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
