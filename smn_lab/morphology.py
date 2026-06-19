# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The SMN diagram grammar -- a body schema and its canonical rendering.

A single source of truth for *both* the morphology diagram and (by sharing the
same parameters as ``crawler.build_crawler_xml``) the simulated body, so a
published figure cannot drift from the code that ran.

The grammar gives the same body two views, sharing one vocabulary:

- **Morphology view** (``render_morphology``) -- where things are mounted: a
  head-to-tail chain of segment blocks, with sensors mounted *inside* each block
  and a CAZ glyph at each inter-segment joint.
- **Network view** (``render_network``) -- who couples to whom: the same layout
  with light-blue coupling lines (sensor -> CAZ, CAZ <-> CAZ).

Glyph conventions:
- **segment = rounded rectangle** -- a body block (head shaded; chain head->tail).
- **sensor = an unfilled circle** with a modality-colored ring, drawn *inside* the
  segment it is mounted on. Bilateral sensors give an L node (upper inside) and an
  R node (lower inside); distal localizers (eye/ear) sit at the anterior face.
- **CAZ = one circle split in half**, one half filled (flexor), one half unfilled
  (extensor) -- the opponent pair actuating ONE degree of freedom. The split
  orientation encodes the DOF axis:
    * vertical split (left | right)  -> lateral bend (turn left/right);
    * horizontal split (top | bottom) -> dorsoventral bend (pitch up/down).
  One CAZ = one DOF = one flexor/extensor pair. Two CAZs of different orientation
  at a joint = two DOFs; two of the same orientation = a redundant additive pair.
  Every CAZ is *dual-interface* (it both senses and acts); that is defined here,
  not drawn.
- **network = light-blue coupling lines** (sensor->CAZ, CAZ<->CAZ).

Fixed across every C-series figure: anterior = +x (right); top view; L = +y
(warm), R = -y (cool); one modality->color table; one network color; a compass.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Wedge, RegularPolygon

# Fixed modality palette -- the same hue means the same modality in every figure.
MODALITY_COLORS = {
    "touch":    "#e8902a",   # orange  -- contact / force (ventral skin)
    "chem":     "#2ca25f",   # green   -- chemical gradient
    "thermal":  "#d7301f",   # red     -- thermal gradient
    "pressure": "#6a51a3",   # purple  -- pressure
    "vision":   "#2166ac",   # blue    -- distal: eye
    "audio":    "#01665e",   # teal    -- distal: ear
    "proprio":  "#888888",   # grey    -- proprioception (internal)
}
_DISTAL = {"vision": "eye", "audio": "ear"}      # which modalities are localizers
# Sensors are differentiated by SHAPE (not colour alone), so they remain
# distinguishable on a black-and-white display or for colour-blind readers; colour
# is a redundant cue. numVertices: 0 = circle. triangle=touch, square=chem,
# pentagon=thermal, hexagon=pressure, circle=vision, octagon=audio.
MODALITY_SHAPES = {"touch": 3, "chem": 4, "thermal": 5, "pressure": 6,
                   "vision": 0, "audio": 8, "proprio": 0}
_SHAPE_ORIENT = {"chem": np.pi / 4}              # axis-aligned square
_SHAPE_MARKER = {"touch": "^", "chem": "s", "thermal": "p", "pressure": "h",
                 "vision": "o", "audio": "8", "proprio": "o"}   # for legends
CAZ_FILL = "#f4c542"             # the CAZ's flexor (filled) half
NETWORK_COLOR = "#7fb3d5"        # the coupling network (light blue)
# The degrees of freedom a single CAZ (one opponent pair) can actuate. The two
# bending DOFs read as a split circle (split orientation = bend axis); the twist
# and telescoping DOFs read as a double-headed arrow (the two opposing pulls).
DOFS = ("lateral", "dorsoventral", "roll", "telescoping")


# ------------------------------------------------------------------ schema -----
@dataclass
class Transducer:
    """A mounted sensor. kind: 'field' | 'touch' | 'localizer'."""
    kind: str
    modality: str
    placement: str                # 'bilateral' | 'ventral' | 'anterior'


@dataclass
class CAZ:
    """One Coordinated Action Zone = one opponent (flexor/extensor) pair = one
    degree of freedom. ``dof`` is one of ``DOFS``: 'lateral' (yaw bend),
    'dorsoventral' (pitch bend), 'roll' (axial twist), or 'telescoping' (axial
    extend/contract -- peristalsis)."""
    dof: str = "lateral"


@dataclass
class Segment:
    name: str
    is_head: bool = False
    transducers: list = field(default_factory=list)


@dataclass
class BodySchema:
    """An axial body: a head->tail chain of segments, with a list of CAZs at each
    inter-segment joint (``joints[k]`` couples segment k and k+1), coupled by a
    beam."""
    name: str
    segments: list                       # head first
    joints: list = field(default_factory=list)   # len = n_seg-1; each a list[CAZ]
    beam: str = "nearest_neighbor"

    @property
    def n_caz(self) -> int:
        return sum(len(j) for j in self.joints)


def crawler_schema(n_seg: int = 3, touch: bool = True,
                   field_modalities=("chem", "thermal"),
                   localizers=("vision",), dof: str = "lateral") -> BodySchema:
    """Schema for the standard axial crawler. Each inter-segment joint has one CAZ
    (one ``dof``), mirroring ``crawler.build_crawler_xml`` (a single hinge per
    joint, driven by one opponent pair)."""
    segs = []
    for k in range(n_seg):
        is_head = (k == 0)
        tx = []
        if touch:
            tx.append(Transducer("touch", "touch", "ventral"))
        for m in field_modalities:
            tx.append(Transducer("field", m, "bilateral"))
        if is_head:
            for m in localizers:
                tx.append(Transducer("localizer", m, "anterior"))
        segs.append(Segment(name=("head" if is_head else f"s{k}"),
                            is_head=is_head, transducers=tx))
    joints = [[CAZ(dof)] for _ in range(n_seg - 1)]
    return BodySchema(name=f"A{n_seg}", segments=segs, joints=joints)


# ------------------------------------------------------------------ glyphs -----
def caz_glyph(ax, x, y, r, dof="lateral", face_a=CAZ_FILL, face_b="white", z=6):
    """A CAZ: one opponent pair = one degree of freedom.

    Bending DOFs ('lateral', 'dorsoventral') are a circle split in half along the
    bend axis (``face_a`` the flexor half, ``face_b`` the extensor half; in the
    dynamics view both may carry state colors). The twist ('roll') and axial
    ('telescoping') DOFs are a circle with a double-headed arrow showing the two
    opposing pulls -- curved for twist, straight along the body axis for length."""
    if dof in ("lateral", "dorsoventral"):
        a, b = ((90, 270), (-90, 90)) if dof == "lateral" else ((0, 180), (180, 360))
        ax.add_patch(Wedge((x, y), r, *a, facecolor=face_a, edgecolor="#222", lw=1.2, zorder=z))
        ax.add_patch(Wedge((x, y), r, *b, facecolor=face_b, edgecolor="#222", lw=1.2, zorder=z))
    else:
        ax.add_patch(Circle((x, y), r, facecolor=face_a, edgecolor="#222", lw=1.2,
                            zorder=z, alpha=0.5))
        if dof == "telescoping":          # straight double arrow along the axis
            ax.annotate("", xy=(x + 0.72 * r, y), xytext=(x - 0.72 * r, y),
                        arrowprops=dict(arrowstyle="<->", color="#222", lw=1.6),
                        zorder=z + 2)
        else:                              # roll: curved double arrow (twist)
            ax.annotate("", xy=(x + 0.5 * r, y - 0.25 * r),
                        xytext=(x - 0.5 * r, y - 0.25 * r),
                        arrowprops=dict(arrowstyle="<->", color="#222", lw=1.6,
                                        connectionstyle="arc3,rad=0.8"), zorder=z + 2)
    ax.add_patch(Circle((x, y), r, facecolor="none", edgecolor="#222", lw=1.3, zorder=z + 1))


def sensor_node(ax, x, y, r, modality, z=6):
    """A transducer drawn as a node: an unfilled marker whose SHAPE encodes the
    modality (distinguishable without colour), with the modality colour as a
    redundant cue."""
    c = MODALITY_COLORS.get(modality, "#555")
    n = MODALITY_SHAPES.get(modality, 0)
    if n and n >= 3:
        ax.add_patch(RegularPolygon((x, y), n, radius=r * 1.18,
                     orientation=_SHAPE_ORIENT.get(modality, 0.0),
                     facecolor="white", edgecolor=c, lw=2.0, zorder=z))
    else:
        ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=c, lw=2.2, zorder=z))


def _eye(ax, x, y, s, color):
    ax.add_patch(Ellipse((x, y), 1.7 * s, s, facecolor="white",
                         edgecolor="#222", lw=1.0, zorder=6))
    ax.add_patch(Circle((x, y), 0.34 * s, facecolor=color, edgecolor="none", zorder=7))
    ax.add_patch(Circle((x, y), 0.15 * s, facecolor="#111", edgecolor="none", zorder=8))


def _ear(ax, x, y, s, color):
    ax.add_patch(Wedge((x, y), 0.6 * s, 300, 120, width=0.22 * s,
                       facecolor=color, edgecolor="#222", lw=0.8, zorder=6))


# ----------------------------------------------------- layout + placement ------
def _layout(schema, seg_w, seg_h, gap):
    pitch = seg_w + gap
    centers = [-pitch * k for k in range(len(schema.segments))]
    caz_x = [centers[k] - pitch / 2 for k in range(len(schema.segments) - 1)]
    return pitch, centers, caz_x


def _sensor_sites(schema, centers, hw, hh):
    """Where each sensor sits *inside* its segment (or at the anterior face for
    localizers). Returns list of (x, y, modality, kind)."""
    sites = []
    for cx, seg in zip(centers, schema.segments):
        fields = [t for t in seg.transducers if t.kind == "field"]
        n = max(1, len(fields))
        xs = cx + np.linspace(-hw * 0.5, hw * 0.5, n)
        for xi, t in zip(xs, fields):
            sites.append((xi, +hh * 0.5, t.modality, "field"))    # L (upper inside)
            sites.append((xi, -hh * 0.5, t.modality, "field"))    # R (lower inside)
        if any(t.kind == "touch" for t in seg.transducers):
            sites.append((cx, 0.0, "touch", "touch"))             # ventral, center
        for t in seg.transducers:
            if t.kind == "localizer":
                for side in (+1, -1):
                    sites.append((cx + hw + 0.42, side * hh * 0.55, t.modality,
                                  "localizer"))
    return sites


def _joint(schema, k):
    """The CAZs at inter-segment joint k; default a single lateral CAZ if the
    schema does not specify joints (e.g. a plain skeleton)."""
    if schema.joints and k < len(schema.joints):
        return schema.joints[k]
    return [CAZ("lateral")]


def _caz_sites(joint_cazs, jx, r):
    """Stack the CAZs of one joint vertically; return [(x, y, dof)]."""
    n = len(joint_cazs)
    ys = (np.linspace(-(n - 1) / 2, (n - 1) / 2, n) * (2.4 * r)) if n > 1 else [0.0]
    return [(jx, float(y), c.dof) for y, c in zip(ys, joint_cazs)]


def _compass(ax, centers, hw, hh):
    x0 = min(centers) - hw - 0.9
    ax.annotate("", xy=(x0 + 0.7, -hh - 1.0), xytext=(x0, -hh - 1.0),
                arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.3))
    ax.text(x0 + 0.8, -hh - 1.0, "anterior", fontsize=7.5, va="center", color="#333")


def _lr_labels(ax, head_x, hw, hh):
    ax.text(head_x + hw + 0.05, hh + 0.4, "L", fontsize=8, color="#b03030",
            ha="center", weight="bold")
    ax.text(head_x + hw + 0.05, -hh - 0.4, "R", fontsize=8, color="#3050b0",
            ha="center", weight="bold")


def _blocks(ax, schema, centers, hw, hh, faint=False):
    for cx, seg in zip(centers, schema.segments):
        if not faint and any(t.kind == "touch" for t in seg.transducers):
            ax.add_patch(FancyBboxPatch(
                (cx - hw, -hh), 2 * hw, 2 * hh,
                boxstyle="round,pad=0.06,rounding_size=0.18", facecolor="none",
                edgecolor=MODALITY_COLORS["touch"], hatch="////", lw=0.0,
                alpha=0.5, zorder=1))
        if faint:
            fc, ec, lw = "#f3f5f8", "#c4ccd6", 1.0
        else:
            fc, ec, lw = ("#bcd0f0" if seg.is_head else "#dfe6ef"), "#3a4a5e", 1.4
        ax.add_patch(FancyBboxPatch(
            (cx - hw, -hh), 2 * hw, 2 * hh,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor=fc, edgecolor=ec, lw=lw, zorder=1))


def _finish(ax, centers, hw, hh, compass):
    if compass:
        _compass(ax, centers, hw, hh)
    _lr_labels(ax, centers[0], hw, hh)
    ax.set_aspect("equal")
    ax.set_xlim(min(centers) - hw - 1.2, centers[0] + hw + 1.5)
    ax.set_ylim(-hh - 1.4, hh + 1.4)
    ax.axis("off")


# --------------------------------------------------------- the two views -------
CAZ_R = 0.26


def render_morphology(ax, schema: BodySchema, seg_w: float = 2.4,
                      seg_h: float = 1.3, gap: float = 0.8,
                      show_labels: bool = True, compass: bool = True):
    """Morphology view: blocks with sensors mounted inside, a CAZ glyph at each
    joint, localizer icons at the anterior. Returns the CAZ x-positions."""
    hw, hh = seg_w / 2, seg_h / 2
    pitch, centers, caz_x = _layout(schema, seg_w, seg_h, gap)
    _blocks(ax, schema, centers, hw, hh)

    if show_labels:
        for cx, seg in zip(centers, schema.segments):
            ax.text(cx, hh - 0.16, seg.name, ha="center", va="center",
                    fontsize=8.5, color="#33414f", zorder=2)

    for (x, y, m, kind) in _sensor_sites(schema, centers, hw, hh):
        if kind == "localizer":
            ic = _eye if _DISTAL.get(m) == "eye" else _ear
            ic(ax, x, y, 0.34, MODALITY_COLORS.get(m, "#555"))
        else:
            sensor_node(ax, x, y, 0.13, m)

    for j, jx in enumerate(caz_x):
        for (x, y, dof) in _caz_sites(_joint(schema, j), jx, CAZ_R):
            caz_glyph(ax, x, y, CAZ_R, dof=dof)

    _finish(ax, centers, hw, hh, compass)
    return caz_x


def render_network(ax, schema: BodySchema, seg_w: float = 2.4,
                   seg_h: float = 1.3, gap: float = 0.8, compass: bool = True):
    """Network view: the same body (drawn faintly) with light-blue coupling
    lines -- each sensor to its nearest CAZ, and CAZ to CAZ along the body."""
    hw, hh = seg_w / 2, seg_h / 2
    pitch, centers, caz_x = _layout(schema, seg_w, seg_h, gap)
    _blocks(ax, schema, centers, hw, hh, faint=True)
    sensors = _sensor_sites(schema, centers, hw, hh)

    def nearest(x):
        return min(caz_x, key=lambda jx: abs(jx - x)) if caz_x else None

    # edges first
    if len(caz_x) > 1:                              # the messaging beam
        ax.plot(caz_x, [0] * len(caz_x), color=NETWORK_COLOR, lw=2.6, zorder=2)
    for (sx, sy, _, _) in sensors:                 # sensor -> nearest CAZ
        jx = nearest(sx)
        if jx is not None:
            ax.plot([sx, jx], [sy, 0.0], color=NETWORK_COLOR, lw=1.1, alpha=0.85,
                    zorder=2)
    # nodes on top
    for (x, y, m, _) in sensors:
        sensor_node(ax, x, y, 0.13, m)
    for j, jx in enumerate(caz_x):
        for (x, y, dof) in _caz_sites(_joint(schema, j), jx, CAZ_R):
            caz_glyph(ax, x, y, CAZ_R, dof=dof)

    _finish(ax, centers, hw, hh, compass)


# --------------------------------------------------------------- legends -------
def modality_legend(ax, modalities=None, with_network=True):
    from matplotlib.lines import Line2D
    mods = modalities or list(MODALITY_COLORS)
    handles = [Line2D([0], [0], marker=_SHAPE_MARKER.get(m, "o"), ls="", markersize=11,
                      markerfacecolor="white", markeredgecolor=MODALITY_COLORS[m],
                      markeredgewidth=2.0, label=m) for m in mods]
    if with_network:
        handles.append(Line2D([0], [0], color=NETWORK_COLOR, lw=2.6,
                              label="coupling (network)"))
    ax.legend(handles=handles, loc="center", ncol=min(5, len(handles)),
              frameon=False, fontsize=8, title="sensors (shape = modality) · coupling")
    ax.axis("off")


def caz_key(ax):
    """A small key showing how the CAZ glyph encodes degrees of freedom."""
    items = [
        (0.0,  [CAZ("lateral")],      "1 CAZ · yaw\n(bend L/R)"),
        (2.4,  [CAZ("dorsoventral")], "1 CAZ · pitch\n(bend up/down)"),
        (4.8,  [CAZ("roll")],         "1 CAZ · roll\n(axial twist)"),
        (7.2,  [CAZ("telescoping")],  "1 CAZ · telescoping\n(extend/contract)"),
        (9.8,  [CAZ("lateral"), CAZ("dorsoventral")], "2 CAZ · two DOF\n(yaw + pitch)"),
        (12.2, [CAZ("lateral"), CAZ("lateral")],      "2 CAZ · same DOF\n(redundant, additive)"),
    ]
    for x0, cazs, label in items:
        for (xx, yy, dof) in _caz_sites(cazs, x0, 0.26):
            caz_glyph(ax, xx, yy + 0.25, 0.26, dof=dof)
        ax.text(x0, -0.85, label, ha="center", va="top", fontsize=7.5, color="#333")
    ax.set_xlim(-1.4, 13.6)
    ax.set_ylim(-1.7, 1.1)
    ax.set_aspect("equal")
    ax.set_title("CAZ = one opponent pair = one DOF · split = bend axis · "
                 "double-arrow = twist / telescoping · stack = more DOF or redundancy",
                 fontsize=9)
    ax.axis("off")
