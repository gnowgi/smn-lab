# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The shared body builder — point-mass segments (``s``) joined by pull-only ``f``.

One primitive for every morphology (A2 of the bench revision). A body is a set of **nodes**
(``s`` — point masses, 3-DOF slide, overdamped) joined by **edges**, each edge one **``f``** — a
*contractile unit* (Sensation Modulator): a spring-tendon with, if actuated, a linear actuator.

**A muscle can only pull.** So an actuated ``f`` is **pull-only**: its series spring supplies the
restoring force (the elastic recoil / the opposition), and the actuator only ever *contracts*.
MuJoCo sign convention (verified in ``_selfcheck``): with ``gear=+1`` a positive ``ctrl``
*lengthens* a tendon. We therefore realize pull-only with **negative gear + ``ctrlrange="0 cmax"``**,
so a **non-negative ``ctrl`` is the contraction amount** (0 = relaxed, ``cmax`` = full pull). Same
convention ``crawler.py`` uses for its opponent pair.

A CAZ is *not* built here — a CAZ is a zone of coordinated action *over* ``f``s (the coordination
layer). This module only builds the ``f`` scaffold and returns the handles to drive and read it.

Run ``python -m smn_lab.fbody`` to self-check the pull-only sign convention.
"""
from __future__ import annotations
import numpy as np
import mujoco

DT = 0.002


def build_body(pos, edges, stiff, actuated=None, *, cmax=4.0, gear=1.0, pull_only=True,
               seg_size=0.015, seg_mass=0.05, seg_damp=3.0, link_damp=0.5, name="body"):
    """Build a MuJoCo body of point-mass ``s`` joined by spring-tendon ``f`` edges.

    pos       : (N,3) node positions.
    edges     : list of (a,b) index pairs — one ``f`` per edge.
    stiff     : per-edge spring stiffness (scalar broadcast, or length-len(edges) array).
    actuated  : per-edge bool (which ``f`` carry a linear actuator); default all True.
    cmax,gear : ctrl bound and actuator gear magnitude.
    pull_only : True  -> muscle can only CONTRACT (negative gear, ctrlrange 0..cmax; a
                         non-negative ctrl is the contraction amount);
                False -> bidirectional (legacy; ctrlrange -cmax..cmax, gear +).

    Returns (model, data, act_of_edge) where act_of_edge maps edge index -> actuator index.
    """
    pos = np.asarray(pos, float)
    n_e = len(edges)
    stiff = np.broadcast_to(np.asarray(stiff, float), (n_e,))
    actuated = np.ones(n_e, bool) if actuated is None else np.asarray(actuated, bool)
    g = -abs(gear) if pull_only else abs(gear)          # negative gear: +ctrl -> contract
    lo = 0.0 if pull_only else -cmax
    bodies = "".join(
        f'<body name="b{i}" pos="{x:.5f} {y:.5f} {z:.5f}">'
        f'<joint name="jx{i}" type="slide" axis="1 0 0" damping="{seg_damp}"/>'
        f'<joint name="jy{i}" type="slide" axis="0 1 0" damping="{seg_damp}"/>'
        f'<joint name="jz{i}" type="slide" axis="0 0 1" damping="{seg_damp}"/>'
        f'<geom type="sphere" size="{seg_size}" mass="{seg_mass}" friction="0 0 0"/>'
        f'<site name="s{i}" size="0.006"/></body>' for i, (x, y, z) in enumerate(pos))
    tend = "".join(
        f'<spatial name="t{e}" stiffness="{stiff[e]:.4f}" damping="{link_damp}" '
        f'springlength="{np.linalg.norm(pos[a]-pos[b]):.5f}"><site site="s{a}"/>'
        f'<site site="s{b}"/></spatial>' for e, (a, b) in enumerate(edges))
    acts = "".join(f'<motor name="m{e}" tendon="t{e}" gear="{g:.4f}" ctrlrange="{lo} {cmax}"/>'
                   for e in range(n_e) if actuated[e])
    xml = (f'<mujoco model="{name}"><option timestep="{DT}" gravity="0 0 0" '
           f'integrator="implicitfast"><flag contact="disable"/></option>'
           f'<worldbody>{bodies}</worldbody><tendon>{tend}</tendon>'
           f'<actuator>{acts}</actuator></mujoco>')
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    act_of_edge = {int(e): a for a, e in enumerate(np.where(actuated)[0])}
    return m, d, act_of_edge


def _selfcheck():
    """Assert the pull-only convention: a non-negative ctrl CONTRACTS (shortens) the f."""
    pos = [(0, 0, 0), (0.30, 0, 0)]
    m, d, aoe = build_body(pos, [(0, 1)], stiff=12.0, cmax=4.0, pull_only=True)
    d.qpos[:] = 0; mujoco.mj_forward(m, d)
    for _ in range(1500):
        d.ctrl[aoe[0]] = 3.0                       # non-negative = "contract"
        mujoco.mj_step(m, d)
    length = (0.30 + d.qpos[1]) - d.qpos[0]
    assert length < 0.30, f"pull-only broken: +ctrl gave length {length:.4f} (rest 0.300)"
    print(f"pull-only OK: +ctrl -> length {length:.4f} (contracted from 0.300)")
    m, d, aoe = build_body(pos, [(0, 1)], stiff=12.0, pull_only=True)
    d.qpos[:] = 0; mujoco.mj_forward(m, d)
    for _ in range(500):
        d.ctrl[aoe[0]] = 0.0; mujoco.mj_step(m, d)
    print(f"relaxed rest: length {(0.30 + d.qpos[1]) - d.qpos[0]:.4f} (≈0.300)")


if __name__ == "__main__":
    _selfcheck()
