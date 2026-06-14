# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The minimal axial crawler -- the bench's disciplined model organism.

This is the body of *Lesson 1* (``design/lesson1_construction_of_experience.md``):
an axial chain of ``n_seg`` segments (blocks), each with mass, joined by hinge
CAZs each driven by a pull-only antagonist pair (the opponent pair is the atomic
dynamical unit). The default ``n_seg=3`` is the minimal morphology that can
*initiate* non-inertial movement: with two joints the joint-angle cycle is
non-reciprocal, so it clears Purcell's scallop theorem and nets a displacement.

Non-inertial regime. The world is overdamped -- nothing coasts. Rather than fight
MuJoCo's fluid solver we apply an explicit, inspectable **anisotropic drag**
(transverse >> tangential) via ``xfrc_applied``: that anisotropy is what converts
a traveling wave of bends into net forward thrust (the *C. elegans* recipe).
Keeping the drag law in plain Python is deliberate -- collaborators can read,
verify, and replace it.

v0 is a planar swimmer (gravity off; the drag *is* the medium). Gravity, a
ventral touch skin reading contact force, and walls/objects are the v1 increment.
"""
from __future__ import annotations
import numpy as np
import mujoco


def build_crawler_xml(n_seg: int = 3, h: float = 0.07, w: float = 0.025,
                      seg_mass: float = 0.05, cmax: float = 2.5,
                      z0: float = 0.1, sense_off: float = 0.06,
                      bend_limit_deg: float = 60.0) -> str:
    """MJCF for an n_seg axial crawler.

    Segments lie head (seg0, +x front) to tail along -x; each segment carries
    bilateral field-sensing sites (seg{k}_L / seg{k}_R); the head also carries
    forward bilateral sites (sense_L / sense_R) used for chemotactic steering.
    Each inter-segment hinge j{k} is actuated by a pull-only opponent pair
    (m_j{k}_p, m_j{k}_n).
    """
    seglen = 2 * h

    def seg_body(k: int) -> str:
        is_head = (k == 0)
        if is_head:
            joints = (
                '      <joint name="slide_x" type="slide" axis="1 0 0" damping="0.5"/>\n'
                '      <joint name="slide_y" type="slide" axis="0 1 0" damping="0.5"/>\n'
                '      <joint name="yaw" type="hinge" axis="0 0 1" damping="0.3"/>')
        else:
            joints = (f'      <joint name="j{k}" type="hinge" axis="0 0 1" pos="{h} 0 0" '
                      f'range="{-bend_limit_deg} {bend_limit_deg}" damping="0.02"/>')
        shade = max(0.30, 0.62 - 0.08 * k)
        color = f"0.20 0.45 0.90" if is_head else f"0.30 {shade:.2f} 0.78"
        geom = (f'      <geom name="seg{k}_geom" type="box" size="{h} {w} {w}" '
                f'mass="{seg_mass}" rgba="{color} 1"/>')
        sites = (f'      <site name="seg{k}_L" pos="0 {w + sense_off} 0" size="0.006" rgba="0.85 0.25 0.25 1"/>\n'
                 f'      <site name="seg{k}_R" pos="0 {-(w + sense_off)} 0" size="0.006" rgba="0.25 0.25 0.85 1"/>')
        if is_head:
            sites += (f'\n      <site name="sense_L" pos="{h} {w + sense_off} 0" size="0.009" rgba="1 0.35 0.35 1"/>\n'
                      f'      <site name="sense_R" pos="{h} {-(w + sense_off)} 0" size="0.009" rgba="0.35 0.35 1 1"/>')
        if k < n_seg - 1:
            child = f'\n      <body name="seg{k + 1}" pos="{-seglen} 0 0">\n{seg_body(k + 1)}\n      </body>'
        else:
            child = ''
        return f"{joints}\n{geom}\n{sites}{child}"

    acts, sens = [], []
    for k in range(1, n_seg):
        acts.append(f'    <motor name="m_j{k}_p" joint="j{k}" gear="0.05"  ctrlrange="0 {cmax}"/>')
        acts.append(f'    <motor name="m_j{k}_n" joint="j{k}" gear="-0.05" ctrlrange="0 {cmax}"/>')
        sens.append(f'    <jointpos name="ang_j{k}" joint="j{k}"/>')
        sens.append(f'    <jointvel name="vel_j{k}" joint="j{k}"/>')
    acts, sens = "\n".join(acts), "\n".join(sens)

    return f"""
<mujoco model="smn_crawler_a{n_seg}">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.7 0.7 0.7" ambient="0.4 0.4 0.4"/>
  </visual>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <body name="seg0" pos="0 0 {z0}">
{seg_body(0)}
    </body>
  </worldbody>

  <actuator>
{acts}
  </actuator>

  <sensor>
{sens}
  </sensor>
</mujoco>
"""


def apply_anisotropic_drag(model, data, body_ids,
                           c_long: float = 0.5, c_trans: float = 7.0,
                           c_rot: float = 0.03) -> None:
    """Apply overdamped, anisotropic drag to each segment via xfrc_applied.

    Drag is computed in each segment's local frame -- ``c_long`` along the body
    (the long axis, cheap) and ``c_trans`` across it (expensive) -- then rotated
    to world. ``c_trans >> c_long`` is the anisotropy that makes a transverse
    push net forward thrust; ``c_rot`` damps spin. Call once per step *before*
    ``mj_step``.
    """
    res = np.zeros(6)
    for bid in body_ids:
        mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, bid, res, 1)
        w_local, v_local = res[0:3], res[3:6]
        f_local = np.array([-c_long * v_local[0], -c_trans * v_local[1], 0.0])
        t_local = np.array([0.0, 0.0, -c_rot * w_local[2]])
        R = data.xmat[bid].reshape(3, 3)
        data.xfrc_applied[bid, 0:3] = R @ f_local
        data.xfrc_applied[bid, 3:6] = R @ t_local
