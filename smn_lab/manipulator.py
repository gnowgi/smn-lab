# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The bilateral two-limb contact manipulator unit.

A single body **segment** (a series of these, coupled by an activation wave,
becomes the crawler) with a **left and a right limb**, each a hinge driven by a
**pull-only antagonist pair** (no steppers — you modulate two opposing pulls).
Each limb presses on an object resting in the world; the agent reads its **dual
interface** — the intended modulation (actuator effort), the proprioceptive
result (angle, velocity), and the resistance met (tip contact). See
`design/manipulator-unit.md`.

The probe (`design/resistance_probe.py`) validated the single-joint read; this
module is the bilateral body, the dual-interface reader, and the **register
lattice** that maps the raw read into the finite state-space the experiments
occupy.

Geometry: each limb swings in the horizontal plane (hinge axis z), so gravity
loads the structure but not the hinge — isolating **object** resistance for the
objecthood experiment, while the field still enters through the movable object's
weight-dependent friction. (The vertical/field-lift variant for the self/field/
object experiment is a later extension.)
"""
from __future__ import annotations
import numpy as np

# body constants (mirror the validated probe geometry, one per side)
ARM_LEN = 0.22
ARM_Z = 0.04
BASE_HY = 0.10          # half the track: left pivot at +BASE_HY, right at -BASE_HY
OBJ_X = 0.20
OBJ_OFF = 0.07          # object offset from the pivot along the swing direction
CMAX = 2.0
JOINT_RANGE = 2.0       # rad; a generous safety limit (the spring, not the limit, sets rest)
STIFFNESS = 1.5         # hinge restoring spring: free swing settles at press/STIFFNESS,
                        #   so an unobstructed limb reaches a press-proportional angle
                        #   (no limit-slam), and an object truncates that swing
BOX_HALF = (0.03, 0.03, 0.04)
MASS_LIGHT, MASS_HEAVY = 0.15, 0.50
COMPLIANT_K = 120.0

OBJECT_KINDS = ("free", "movable-light", "movable-heavy", "compliant", "fixed")


def _box(name, mass=None):
    hx, hy, hz = BOX_HALF
    m = f'mass="{mass}"' if mass is not None else ""
    return (f'type="box" size="{hx} {hy} {hz}" {m} '
            f'friction="1 0.01 0.001" rgba="0.6 0.6 0.62 1"')


def _target(tag, side, kind):
    """A target on one limb's swing side. side = +1 (left/+y) or -1 (right/-y)."""
    if kind in ("free", "none"):
        return ""
    x, sy, z = OBJ_X, side * (BASE_HY + OBJ_OFF), ARM_Z
    if kind == "fixed":                                    # welded to the world
        return f'<geom name="obj_{tag}" pos="{x} {sy} {z}" {_box(f"obj_{tag}")}/>'
    if kind.startswith("movable"):                         # free body; slides with friction
        mass = MASS_HEAVY if "heavy" in kind else MASS_LIGHT
        return (f'<body name="obj_{tag}" pos="{x} {sy} {z}">'
                f'<freejoint/><geom name="obj_{tag}" {_box(f"obj_{tag}", mass)}/></body>')
    if kind == "compliant":                                # spring-backed along the swing axis
        return (f'<body name="obj_{tag}" pos="{x} {sy} {z}">'
                f'<joint name="obj_{tag}_s" type="slide" axis="0 1 0" '
                f'stiffness="{COMPLIANT_K}" damping="2.0"/>'
                f'<geom name="obj_{tag}" {_box(f"obj_{tag}", 0.10)}/></body>')
    raise ValueError(kind)


def _limb(tag, side, actuation):
    """One limb: hinge (axis z) + arm + tip site, driven either by a pull-only
    antagonist pair (actuation='smn' — you modulate two opposing pulls) or by a
    position servo (actuation='position' — the 'stepper' foil the design forbids:
    you command an angle, so it drives to its force limit to reach an obstructed
    target)."""
    py = side * BASE_HY
    # press swings the tip toward the object on this side: gear = side
    if actuation == "smn":
        acts = (f'    <motor name="press_{tag}"   joint="j_{tag}" gear="{side}"  ctrlrange="0 {CMAX}"/>\n'
                f'    <motor name="retract_{tag}" joint="j_{tag}" gear="{-side}" ctrlrange="0 {CMAX}"/>')
    else:  # position/"stepper" foil: command an angle; servo winds up to reach it
        acts = (f'    <position name="pos_{tag}" joint="j_{tag}" kp="25" '
                f'ctrlrange="-{JOINT_RANGE} {JOINT_RANGE}" forcerange="-4 4"/>')
    body = (f'    <body name="limb_{tag}" pos="0 {py} {ARM_Z}">\n'
            f'      <joint name="j_{tag}" type="hinge" axis="0 0 1" '
            f'range="-{JOINT_RANGE} {JOINT_RANGE}" limited="true" '
            f'stiffness="{STIFFNESS}" damping="0.3"/>\n'
            f'      <geom name="arm_{tag}" type="capsule" fromto="0 0 0 {ARM_LEN} 0 0" '
            f'size="0.012" mass="0.20" rgba="0.2 0.4 0.9 1"/>\n'
            f'      <site name="tip_{tag}" pos="{ARM_LEN} 0 0" size="0.02"/>\n'
            f'    </body>')
    sensors = (f'    <jointpos name="ang_{tag}" joint="j_{tag}"/>\n'
               f'    <jointvel name="vel_{tag}" joint="j_{tag}"/>\n'
               f'    <jointactuatorfrc name="cmd_{tag}" joint="j_{tag}"/>\n'
               f'    <touch name="touch_{tag}" site="tip_{tag}"/>')
    return body, acts, sensors


def build_manip_xml(left="free", right="free", actuation="smn") -> str:
    """The bilateral unit, pinned to the world, with a target on each side."""
    bL, aL, sL = _limb("L", +1, actuation)
    bR, aR, sR = _limb("R", -1, actuation)
    return f"""
<mujoco model="smn_manipulator_unit">
  <compiler angle="radian"/>
  <option timestep="0.002" gravity="0 0 -9.81" integrator="implicitfast"/>
  <worldbody>
    <geom name="floor" type="plane" size="2 2 0.1" rgba="0.9 0.9 0.9 1" friction="1 0.01 0.001"/>
    <geom name="base" type="box" pos="0 0 {ARM_Z}" size="0.03 {BASE_HY} 0.02" rgba="0.3 0.3 0.35 1"/>
{bL}
{bR}
    {_target("L", +1, left)}
    {_target("R", -1, right)}
  </worldbody>
  <actuator>
{aL}
{aR}
  </actuator>
  <sensor>
{sL}
{sR}
  </sensor>
</mujoco>
"""


class LimbInterface:
    """The dual interface of one limb: by-name handles to act (the pull-only
    pair, or the foil's torque) and to sense (effort, angle, velocity, contact)."""

    def __init__(self, model, tag, actuation="smn"):
        self.tag = tag
        self.actuation = actuation
        if actuation == "smn":
            self.press = model.actuator(f"press_{tag}").id
            self.retract = model.actuator(f"retract_{tag}").id
        else:
            self.pos = model.actuator(f"pos_{tag}").id
        sid = lambda n: model.sensor_adr[model.sensor(n).id]
        self.a_ang = sid(f"ang_{tag}")
        self.a_vel = sid(f"vel_{tag}")
        self.a_cmd = sid(f"cmd_{tag}")
        self.a_touch = sid(f"touch_{tag}")

    def drive(self, data, cmd, cocontract=0.0):
        """Act. SMN: ``cmd`` is the press force toward the object; ``cocontract``
        adds a baseline antagonist tone (the opponent pair). Position foil:
        ``cmd`` is a *target angle* the servo drives toward (and overshoots into
        an obstacle to reach)."""
        if self.actuation == "smn":
            data.ctrl[self.press] = float(np.clip(cmd + cocontract, 0.0, CMAX))
            data.ctrl[self.retract] = float(np.clip(cocontract, 0.0, CMAX))
        else:
            data.ctrl[self.pos] = float(np.clip(cmd, -JOINT_RANGE, JOINT_RANGE))

    def read(self, data):
        """Sense: (effort, angle, velocity, contact) — the dual-interface read."""
        return dict(effort=abs(float(data.sensordata[self.a_cmd])),
                    ang=abs(float(data.sensordata[self.a_ang])),
                    vel=abs(float(data.sensordata[self.a_vel])),
                    contact=float(data.sensordata[self.a_touch]))


class RegisterLattice:
    """Maps a dual-interface read into the finite register space the experiments
    occupy: Contact × Effort × Motion. The lattice is fixed by the body's
    structure; an experiment records which cells it occupies.

    (Horizontal-swing unit: Contact ∈ {free, object} — the 'ground' cell and the
    with-field/against-field split arrive with the vertical/field variant.)"""

    CONTACT = ("free", "object")
    EFFORT = ("slack", "working", "straining")
    MOTION = ("moving", "halted")

    def __init__(self, contact_thr=0.5, eff_lo=0.5, eff_hi=1.3, vel_thr=0.20):
        self.contact_thr = contact_thr
        self.eff_lo, self.eff_hi = eff_lo, eff_hi
        self.vel_thr = vel_thr

    def classify(self, read: dict):
        C = "object" if read["contact"] > self.contact_thr else "free"
        e = read["effort"]
        E = "slack" if e < self.eff_lo else ("working" if e < self.eff_hi else "straining")
        M = "moving" if read["vel"] > self.vel_thr else "halted"
        return (C, E, M)

    def cells(self):
        return [(c, e, m) for c in self.CONTACT for e in self.EFFORT for m in self.MOTION]
