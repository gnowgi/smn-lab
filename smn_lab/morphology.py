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
from matplotlib.patches import (FancyBboxPatch, Circle, Ellipse, Wedge,
                                RegularPolygon, Rectangle, FancyArrowPatch)

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


CANVAS_FC = "#e7eef6"


def render_canvas(ax, x0, x1, y0, y1, regions=None, label=True):
    """The broadcasting substrate as a band. By default ONE undivided canvas -- a
    simple agent has no regions. `regions` is drawn only when regions have been
    CONSTRUCTED (e.g. read off a self-organized canvas); each is
    ``(name, x_lo, x_hi[, facecolor])``. Regions are never pre-given here."""
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=CANVAS_FC,
                 edgecolor="#9fb0bd", lw=1.2, zorder=1))
    if regions and all(isinstance(r, str) for r in regions):   # names -> even partition
        e = np.linspace(x0, x1, len(regions) + 1)
        regions = [(regions[i], e[i], e[i + 1]) for i in range(len(regions))]
    if regions:
        for r in regions:
            name, rx0, rx1 = r[0], r[1], r[2]
            fc = r[3] if len(r) > 3 else "#d6e6f6"
            ax.add_patch(Rectangle((rx0, y0), rx1 - rx0, y1 - y0, facecolor=fc,
                         edgecolor="#9fb0bd", lw=1.0, alpha=0.9, zorder=1))
            ax.text((rx0 + rx1) / 2, (y0 + y1) / 2, name, ha="center", va="center",
                    fontsize=9, color="#33414f", fontweight="bold", zorder=2)
    else:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, "one undivided canvas", ha="center",
                va="center", fontsize=10, color="#8496a6", style="italic", alpha=0.85)
    if label:
        ax.text((x0 + x1) / 2, y1 + 0.16,
                "the canvas — one broadcasting substrate (γ refresh · θ hold)",
                ha="center", va="bottom", fontsize=7.6, style="italic", color="#2a3742")


def _draw_orbit(ax, x, y, color, canvas_y):
    """An EYE is not a bare single-interface transducer -- it is the paradigm
    sensorimotor-contingency unit: mounted on an ORBIT (a small segment) carrying
    several extraocular CAZ pairs that move it. Draw the orbit + its CAZs + the
    eye, and a BUNDLE of lines (one per extraocular pair) reaching the canvas."""
    ow, oh = 0.5, 0.8
    ax.add_patch(FancyBboxPatch((x - ow, y - oh), 2 * ow, 2 * oh,
                 boxstyle="round,pad=0.0,rounding_size=0.12", facecolor="#eef3fa",
                 edgecolor="#3a4a5e", lw=1.2, zorder=3))
    for k, dof in enumerate(("lateral", "dorsoventral", "roll")):    # extraocular pairs
        caz_glyph(ax, x - ow + 0.02, y - oh + 0.34 + 0.62 * k, 0.15, dof=dof, z=6)
    _eye(ax, x + 0.16, y, 0.26, color)
    for dx in (-0.24, 0.0, 0.24):                                    # the bundle
        ax.plot([x + dx, x + dx], [y - oh - 0.04, canvas_y - 0.02], color=color,
                lw=1.1, alpha=0.75, zorder=2)
    ax.text(x, y + oh + 0.12, "orbit\n(extraocular CAZs)", fontsize=6.2, ha="center",
            va="bottom", color="#556")


def render_two_network(ax, schema: BodySchema, regions=None, seg_w: float = 2.4,
                       seg_h: float = 1.3, gap: float = 0.8, show_labels: bool = True):
    """Both networks of an agent, from its schema, as THREE functional layers:
    the MECHANICAL body (segment blocks, dual-interface CAZ, single-interface
    transducers); the DFN -- the differentiating + filtering network where the
    sensory bundle and the motor efference MEET and the modulation filter alpha
    (C4) acts (only modulated data enters); and the IN -- the one integrating
    CANVAS, whose regions are CONSTRUCTED, not given. The DFN's filtered output
    enters the canvas; the canvas drives the actuators, closing the loop. An EYE is
    an orbit unit (several extraocular CAZs) with its own bundle to the DFN: vision
    is the paradigm sensorimotor contingency, not a passive sensor."""
    hw, hh = seg_w / 2, seg_h / 2
    _, centers, caz_x = _layout(schema, seg_w, seg_h, gap)
    _blocks(ax, schema, centers, hw, hh)
    if show_labels:
        for cx, seg in zip(centers, schema.segments):
            ax.text(cx, hh - 0.16, seg.name, ha="center", va="center",
                    fontsize=8, color="#33414f", zorder=2)

    sensors = _sensor_sites(schema, centers, hw, hh)
    simple = [(x, y, m) for (x, y, m, k) in sensors
              if not (k == "localizer" and _DISTAL.get(m) == "eye")]
    eye_mods = []
    for (x, y, m, k) in sensors:
        if k == "localizer" and _DISTAL.get(m) == "eye" and m not in eye_mods:
            eye_mods.append(m)
    for (x, y, m) in simple:
        sensor_node(ax, x, y, 0.13, m)
    caz_pts = []
    for j, jx in enumerate(caz_x):
        for (x, y, dof) in _caz_sites(_joint(schema, j), jx, CAZ_R):
            caz_glyph(ax, x, y, CAZ_R, dof=dof); caz_pts.append(x)

    orbit_x = centers[0] + hw + 1.0
    cx0 = min(centers) - hw - 0.3
    cx1 = (orbit_x + 0.7) if eye_mods else (centers[0] + hw + 0.3)
    gx = (min(centers) + centers[0]) / 2

    # DFN band -- differentiate + filter (alpha); sensory + motor messages meet here
    dfn_y1 = -hh - 1.05
    dfn_y0 = dfn_y1 - 0.72
    dfn_mid = (dfn_y0 + dfn_y1) / 2
    ax.add_patch(Rectangle((cx0, dfn_y0), cx1 - cx0, dfn_y1 - dfn_y0,
                 facecolor="#fbeee6", edgecolor="#a06a4a", lw=1.2, zorder=1))
    ax.add_patch(Circle((gx, dfn_mid), 0.17, facecolor="white", edgecolor="#a02",
                 lw=1.6, zorder=5))
    ax.text(gx, dfn_mid, r"$\alpha$", ha="center", va="center", fontsize=8.5,
            color="#a02", zorder=6)

    # IN canvas below the DFN
    cy1 = dfn_y0 - 0.95
    cy0 = cy1 - 1.55
    render_canvas(ax, cx0, cx1, cy0, cy1, regions=regions, label=False)

    # sensory bundle -> DFN (colour-coded); eyes' orbit bundle -> DFN
    for (sx, sy, m) in simple:
        ax.plot([sx, gx], [sy, dfn_y1 + 0.04], color=MODALITY_COLORS.get(m, "#555"),
                lw=1.1, alpha=0.85, zorder=2)
    for i, m in enumerate(eye_mods):
        _draw_orbit(ax, orbit_x, -1.7 * i, MODALITY_COLORS.get(m, "#2166ac"), dfn_y1)
    # efferent + afferent: each CAZ <-> DFN (the sensorimotor exchange)
    for jx in caz_pts:
        ax.add_patch(FancyArrowPatch((jx, -hh - 0.12), (jx, dfn_y1 + 0.02),
                     arrowstyle="<|-|>", mutation_scale=10, lw=1.6, color="#2a3742",
                     zorder=3))
    # DFN filtered output -> IN canvas
    for x in np.linspace(cx0 + (cx1 - cx0) * 0.28, cx0 + (cx1 - cx0) * 0.72, 3):
        ax.add_patch(FancyArrowPatch((x, dfn_y0), (x, cy1 - 0.02), arrowstyle="-|>",
                     mutation_scale=11, lw=1.7, color="#a06a4a", zorder=4))
    # IN canvas -> actuators (loop closes)
    lx = cx0 + 0.28
    ax.add_patch(FancyArrowPatch((lx, cy1), (lx, -hh - 0.1), arrowstyle="-|>",
                 mutation_scale=9, lw=1.2, color="#3a5a7a", alpha=0.6,
                 connectionstyle="arc3,rad=-0.3", zorder=2))

    if show_labels:
        ax.text(cx0, hh + 0.55, "mechanical network", fontsize=7.5, ha="left",
                color="#2a3742", style="italic")
        ax.text(cx1 + 0.14, dfn_mid, "DFN\ndifferentiate\n+ filter (C4·α)", fontsize=6.6,
                va="center", ha="left", color="#a06a4a")
        ax.text(cx1 + 0.14, (cy0 + cy1) / 2, "IN\nthe canvas\n(integrate)", fontsize=6.6,
                va="center", ha="left", color="#3a5a7a")
        ax.text(lx - 0.12, (cy1 - hh) / 2, "IN →\nmotor\n(loop)", fontsize=5.8,
                ha="right", va="center", color="#3a5a7a")
    _lr_labels(ax, centers[0], hw, hh)
    ax.set_aspect("equal")
    ax.set_xlim(cx0 - 1.0, cx1 + 1.6)
    ax.set_ylim(cy0 - 0.5, hh + 1.1)
    ax.axis("off")


def render_two_network_graph(ax, positions, edges, *, head=0, regions=None):
    """Both networks for a NON-axial body (branched, sheet, tube, appendicular):
    the mechanical body graph above (segment blocks + a CAZ glyph on each edge +
    the beam), and the ONE broadcasting canvas below. A broadcast arrow runs from
    each CAZ (edge midpoint) down to the canvas -- write + read = closure."""
    P = _norm_positions(positions, edges)
    _draw_graph_body(ax, positions, edges, head=head)
    xs = [p[0] for p in P.values()]; ys = [p[1] for p in P.values()]
    x0, x1 = min(xs) - 0.6, max(xs) + 0.6
    cy1 = min(ys) - 1.1
    cy0 = cy1 - 1.3
    render_canvas(ax, x0, x1, cy0, cy1, regions=regions)
    for (a, b) in edges:                                # CAZ at each edge midpoint
        mx, my = (P[a][0] + P[b][0]) / 2, (P[a][1] + P[b][1]) / 2
        ax.add_patch(FancyArrowPatch((mx, my - 0.18), (mx, cy1 - 0.02),
                     arrowstyle="<|-|>", mutation_scale=8, lw=1.3, color="#2a3742",
                     zorder=3))
    ax.set_xlim(x0 - 0.4, x1 + 0.4); ax.set_ylim(cy0 - 0.4, max(ys) + 0.6)
    ax.set_aspect("equal"); ax.axis("off")


def render_emergent_canvas(ax, nodes, edges, x0, x1, y0, y1, core=None, label=True):
    """The canvas as an EMERGENT dependency digraph, drawn into the box
    [x0,x1] x [y0,y1]. `edges` are directed (u -> v : v depends on u). The layers
    are NOT stipulated: each node's stratum is its longest dependency path from the
    core (nodes with no incoming edge), so the NUMBER of strata emerges from the
    graph. Node size = degree (weight); node colour = emergent stratum. This is the
    constructive canvas -- layers derived from the messaging graph, not drawn."""
    incoming = {n: 0 for n in nodes}
    for (u, v) in edges:
        incoming[v] = incoming.get(v, 0) + 1
    src = core or [n for n in nodes if incoming.get(n, 0) == 0]
    depth = {n: 0 for n in src}
    for _ in range(len(nodes)):                          # relax longest paths
        for (u, v) in edges:
            depth[v] = max(depth.get(v, 0), depth.get(u, 0) + 1)
    for n in nodes:
        depth.setdefault(n, 0)
    deg = {n: 0 for n in nodes}
    for (u, v) in edges:
        deg[u] += 1; deg[v] += 1
    levels = sorted(set(depth.values()))
    yof = {lv: (y1 - (y1 - y0) * (i / max(1, len(levels) - 1)))
           for i, lv in enumerate(levels)}
    pos = {}
    for lv in levels:
        row = [n for n in nodes if depth[n] == lv]
        xs = (np.linspace(x0 + 0.6, x1 - 0.6, len(row)) if len(row) > 1
              else [(x0 + x1) / 2])
        for n, x in zip(row, xs):
            pos[n] = (x, yof[lv])
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, max(1, len(levels))))
    r0 = min(0.22, (x1 - x0) / (3.0 * max(len(nodes), 1)) + 0.09)
    for (u, v) in edges:
        ax.add_patch(FancyArrowPatch(pos[u], pos[v], arrowstyle="-|>", mutation_scale=8,
                     color="#9fb0bd", lw=1.0, shrinkA=7, shrinkB=7,
                     connectionstyle="arc3,rad=0.06", zorder=2))
    for n in nodes:
        x, y = pos[n]
        ax.add_patch(Circle((x, y), r0 + 0.02 * deg[n],
                     facecolor=cmap[levels.index(depth[n])], edgecolor="#33414f",
                     lw=1.1, zorder=3))
    if label:
        ax.text((x0 + x1) / 2, y1 + 0.2,
                f"the canvas — an EMERGENT dependency digraph "
                f"({len(levels)} strata emerged, not stipulated)",
                ha="center", va="bottom", fontsize=7.6, style="italic", color="#2a3742")


# ----------------------------------------- graph views (any body, not just axial)
# The chain renderers above lay segments out in a line. These generalize the same
# vocabulary -- segment blocks, the dual-interface CAZ glyph, the light-blue beam --
# to an arbitrary body *graph* (positions + edges), so a branched body, its
# recovered self-model, and the world expressed in its self-frame all read in one
# visual language.

def graph_layout(nodes, edges, *, seed=0, iters=300, k=1.0):
    """Force-directed (Fruchterman-Reingold) layout from adjacency ALONE.

    Used to draw a graph the agent *recovered* from movement: it knows the
    topology (who couples to whom) but not metric positions, so its self-model is
    laid out purely from connectivity -- deliberately NOT the physical body's
    coordinates. Same connectivity, an embedding the agent could compute itself."""
    nodes = list(nodes)
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    rng = np.random.default_rng(seed)
    pos = rng.standard_normal((n, 2)) * 0.1
    E = [(idx[a], idx[b]) for a, b in edges]
    for it in range(iters):
        disp = np.zeros((n, 2))
        for i in range(n):                              # repulsion, all pairs
            d = pos[i] - pos
            dist = np.hypot(d[:, 0], d[:, 1]); dist[i] = 1.0
            disp[i] += (((k * k) / dist**2)[:, None] * (d / dist[:, None])).sum(0)
        for i, j in E:                                  # attraction along edges
            d = pos[i] - pos[j]
            dist = float(np.hypot(*d)) or 1e-4
            f = (dist * dist / k) * (d / dist)
            disp[i] -= f; disp[j] += f
        t = 0.1 * (1 - it / iters) + 1e-3               # cooling
        for i in range(n):
            dl = float(np.hypot(*disp[i])) or 1e-9
            pos[i] += (disp[i] / dl) * min(dl, t)
    return {v: (float(pos[idx[v]][0]), float(pos[idx[v]][1])) for v in nodes}


def graph_layout_weighted(nodes, W, *, seed=0, iters=400, k=1.0):
    """Force-directed layout of a WEIGHTED graph: attraction between two nodes is
    proportional to their coupling weight W[i,j], repulsion is uniform. A
    potentially-complete broadcast graph, laid out by the weights of differentiated
    action, collapses to the self-model whose shape the morphology predicts."""
    nodes = list(nodes)
    n = len(nodes)
    rng = np.random.default_rng(seed)
    pos = rng.standard_normal((n, 2)) * 0.1
    Wn = np.asarray(W, float).copy()
    np.fill_diagonal(Wn, 0.0)
    Wn = Wn / (Wn.max() + 1e-9)
    for it in range(iters):
        disp = np.zeros((n, 2))
        for i in range(n):                              # repulsion, all pairs
            d = pos[i] - pos
            dist = np.hypot(d[:, 0], d[:, 1]); dist[i] = 1.0
            disp[i] += (((k * k) / dist**2)[:, None] * (d / dist[:, None])).sum(0)
        for i in range(n):                              # attraction, weighted
            for j in range(n):
                if i == j or Wn[i, j] <= 0:
                    continue
                d = pos[i] - pos[j]
                dist = float(np.hypot(*d)) or 1e-4
                disp[i] -= Wn[i, j] * (dist * dist / k) * (d / dist)
        t = 0.1 * (1 - it / iters) + 1e-3
        for i in range(n):
            dl = float(np.hypot(*disp[i])) or 1e-9
            pos[i] += (disp[i] / dl) * min(dl, t)
    return {v: (float(pos[i, 0]), float(pos[i, 1])) for i, v in enumerate(nodes)}


def _norm_positions(positions, edges):
    """Rescale node positions so the median edge length is 1.0 (glyphs then size
    consistently regardless of the body's physical scale)."""
    import numpy as _np
    if edges:
        L = _np.median([_np.hypot(positions[a][0] - positions[b][0],
                                  positions[a][1] - positions[b][1]) for a, b in edges])
    else:
        L = 1.0
    L = L or 1.0
    return {n: (x / L, y / L) for n, (x, y) in positions.items()}


def _seg_block(ax, x, y, s, label=None, fc="#dfe6ef", ec="#3a4a5e", lw=1.3, z=4):
    ax.add_patch(FancyBboxPatch((x - s / 2, y - s / 2), s, s,
                 boxstyle="round,pad=0,rounding_size=0.1",
                 facecolor=fc, edgecolor=ec, lw=lw, zorder=z))
    if label is not None:
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5,
                color="#33414f", zorder=z + 1)


def _draw_graph_body(ax, positions, edges, *, head=0, beam=True, caz=True,
                     labels=True, edge_status=None, node_fc=None, hl=None,
                     faint=False, block=0.40, cazr=0.115, node_style="block",
                     edge_w=None, node_role=None):
    """Core renderer for two node styles in one vocabulary.

    ``node_style='block'`` draws the *physical body*: segment blocks with a CAZ
    split-glyph on each joint and the messaging beam. ``node_style='dot'`` draws
    the *abstract graph* the body recovers: plain circular nodes and edges (whose
    width can encode the measured coupling), with no body dress -- so a recovered
    self-model never looks like a redrawn body.

    edge_status[i] in {'ok','bad'} colours recovered edges; edge_w[i] in [0,1]
    scales edge width; node_fc / node_role map nodes to face colours; hl maps a
    node to a highlight ring (branch point / localized world source)."""
    P = _norm_positions(positions, edges)
    node_fc = node_fc or {}; hl = hl or {}; node_role = node_role or {}
    dot = (node_style == "dot")
    beam_c = "#d9e4ee" if faint else ("#9fb0bd" if dot else NETWORK_COLOR)
    for i, (a, b) in enumerate(edges):
        xa, ya = P[a]; xb, yb = P[b]
        if beam:
            c = beam_c
            if edge_status is not None:
                c = "#3f6d99" if edge_status[i] == "ok" else "#d1483f"
            lw = (3.0 if not faint else 1.6)
            if edge_w is not None:
                lw = 1.0 + 4.2 * float(edge_w[i])
            ax.plot([xa, xb], [ya, yb], color=c, lw=lw, zorder=2, solid_capstyle="round")
        if caz and not dot and not faint:
            caz_glyph(ax, (xa + xb) / 2, (ya + yb) / 2, cazr, dof="lateral", z=6)
    for n, (x, y) in P.items():
        if dot:
            fc = node_fc.get(n) or node_role.get(n, "#8fb4d6")
            ax.add_patch(Circle((x, y), block * 0.46, facecolor=fc,
                         edgecolor=("#c4ccd6" if faint else "#33414f"),
                         lw=1.1 if faint else 1.5, zorder=4))
            if labels:
                ax.text(x, y, str(n), ha="center", va="center", fontsize=7.5,
                        color=("#5c6b78" if faint else "#132029"), zorder=5)
        else:
            fc = node_fc.get(n, "#f3f5f8" if faint else ("#bcd0f0" if n == head else "#dfe6ef"))
            _seg_block(ax, x, y, block, label=(str(n) if labels else None), fc=fc,
                       ec=("#c4ccd6" if faint else "#3a4a5e"), lw=1.1 if faint else 1.3)
        if n in hl:
            ax.add_patch(Circle((x, y), block * (0.78 if dot else 0.85), facecolor="none",
                         edgecolor=hl[n], lw=2.6, zorder=8))
    ax.set_aspect("equal"); ax.axis("off")


def render_body_graph(ax, positions, edges, *, head=0, title=None):
    """The DESIGNED agent as a body graph: segment blocks, a CAZ glyph on each
    joint, the messaging beam along the edges. Branch points read as high-degree
    nodes automatically."""
    _draw_graph_body(ax, positions, edges, head=head)
    if title:
        ax.set_title(title, fontsize=10)


def render_self_model(ax, positions, rec_edges, *, true_edges=None, branch=None,
                      head=0, title=None, edge_w=None):
    """The RECOVERED self-model, drawn as an ABSTRACT GRAPH (not a body): plain
    nodes, edges (width = measured coupling if ``edge_w`` given), the branch point
    ringed. Nodes are coloured by recovered degree -- leaf, internal, branch --
    and edges by correctness (blue = matches the true body, red = spurious)."""
    status = None
    if true_edges is not None:
        tset = {frozenset(e) for e in true_edges}
        status = ["ok" if frozenset(e) in tset else "bad" for e in rec_edges]
    deg = {}
    for a, b in rec_edges:
        deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
    role = {n: ("#e8902a" if deg.get(n, 0) >= 3 else
                ("#cdd6dd" if deg.get(n, 0) <= 1 else "#7aa7cf")) for n in positions}
    hl = {branch: "#e8902a"} if branch is not None else None
    _draw_graph_body(ax, positions, rec_edges, head=head, edge_status=status, hl=hl,
                     node_style="dot", node_role=role, edge_w=edge_w, caz=False)
    if title:
        ax.set_title(title, fontsize=10)


def render_world_in_self(ax, positions, edges, node_field, *, source_node=None,
                         modality="chem", head=0, title=None):
    """The WORLD, expressed in the self-frame: the self-graph with each node shaded
    by the world-field intensity it senses (in the modality's colour), and the
    localized source ringed. No absolute coordinates -- the world is painted onto
    the body's own graph."""
    import numpy as _np
    from matplotlib.colors import to_rgba
    base = MODALITY_COLORS.get(modality, "#2ca25f")
    v = _np.array([node_field[n] for n in positions])
    lo, hi = float(v.min()), float(v.max())
    rng = (hi - lo) or 1.0
    node_fc = {n: to_rgba(base, alpha=0.12 + 0.88 * (node_field[n] - lo) / rng)
               for n in positions}
    hl = {source_node: "#111111"} if source_node is not None else None
    _draw_graph_body(ax, positions, edges, head=head, node_fc=node_fc, hl=hl,
                     faint=True, node_style="dot", caz=False)
    if title:
        ax.set_title(title, fontsize=10)


def self_world_card(positions, edges, rec_edges, *, head=0, branch=None,
                    edge_w=None, node_field=None, source_node=None,
                    modality="chem", suptitle=None, layout_seed=3, fig_h=5.2):
    """Assemble the three-view self/world card for ANY body (chain, tree, ...).

    Panel 1 -- the designed agent, at metric coordinates (a body).
    Panel 2 -- the recovered self-model, an abstract graph laid out from its OWN
               adjacency (force-directed), edge width = measured coupling.
    Panel 3 -- (only if ``node_field`` given) the world in the self-frame: the
               field painted onto the recovered graph.

    Returns the matplotlib Figure so the caller can save or tweak it."""
    has_world = node_field is not None
    ncol = 3 if has_world else 2
    fig, ax = plt.subplots(1, ncol, figsize=(4.7 * ncol, fig_h))
    lay = graph_layout(list(positions.keys()), rec_edges, seed=layout_seed)
    render_body_graph(ax[0], positions, edges, head=head,
                      title="1 · Designed agent\n(metric — what we built)")
    render_self_model(ax[1], lay, rec_edges, true_edges=edges, branch=branch,
                      edge_w=edge_w,
                      title="2 · Recovered self-model\n(abstract graph from movement; edge width = coupling)")
    if has_world:
        render_world_in_self(ax[2], lay, rec_edges, node_field, source_node=source_node,
                             modality=modality,
                             title="3 · World in the self-frame\n(source localized on the recovered graph)")
    if suptitle:
        fig.suptitle(suptitle, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.94] if suptitle else None)
    return fig


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
