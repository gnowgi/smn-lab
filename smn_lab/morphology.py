# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The SMN diagram grammar -- a body schema and its canonical rendering.

A single source of truth for *both* the morphology diagram and (by sharing the
same parameters as ``crawler.build_crawler_xml``) the simulated body, so a
published figure cannot drift from the code that ran. ``viz.py`` imports the same
glyph primitives, so the dynamics (messaging-beam) view shares this vocabulary.

The grammar has two views of the same body:

- **Morphology view** (``render_morphology``) -- where things are mounted: a
  head-to-tail chain of segment blocks, CAZ zone-pairs, dense bilateral sensor
  strips, and literal anterior localizer icons.
- **Network view** (``render_network``) -- who couples to whom: zones (Z+/Z-) and
  sensors as nodes, joined by light-blue coupling lines (the messaging beam plus
  sensor->zone and opponency links).

Glyph conventions:
- **zone = a half-filled / half-unfilled circle** (OUR notation): the filled half
  is the acting interface, the unfilled half the sensing interface -- the
  *dual-interface* unit. A **CAZ is an opposed pair of zones**, labeled **Z+** and
  **Z-**, facing each other across the inter-segment joint.
- **sensor = an unfilled circle** with a modality-colored ring -- a single-
  interface transducer, drawn as a network node.
- borrowed: a head->tail kinematic chain; Braitenberg-style anterior eye/ear
  icons; color-coded distributed strips.

Conventions held fixed across every C-series figure:
- **anterior = +x (right)**, matching the crawler code (head = seg0 at +x);
- top view; **L = +y (warm)**, **R = -y (cool)**;
- one fixed modality->color table (``MODALITY_COLORS``), shown as a legend;
- the network coupling is one fixed color (``NETWORK_COLOR``);
- a small axis compass in every figure.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Wedge

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
ZONE_FILL = "#f4c542"            # the zone's acting (filled) interface
NETWORK_COLOR = "#7fb3d5"        # the coupling network (light blue)


@dataclass
class Transducer:
    """One mounted sensor block.

    kind      : 'field' (distributed strip), 'touch' (ventral skin), or
                'localizer' (paired anterior icon).
    modality  : key into MODALITY_COLORS.
    placement : 'bilateral' | 'ventral' | 'anterior'.
    """
    kind: str
    modality: str
    placement: str


@dataclass
class Segment:
    name: str
    is_head: bool = False
    transducers: list = field(default_factory=list)


@dataclass
class BodySchema:
    """An axial body: an ordered head->tail chain of segments, with a CAZ
    (inter-segment joint) between each consecutive pair, coupled by a beam."""
    name: str
    segments: list                       # head first
    beam: str = "nearest_neighbor"

    @property
    def n_caz(self) -> int:
        return max(0, len(self.segments) - 1)


def crawler_schema(n_seg: int = 3, touch: bool = True,
                   field_modalities=("chem", "thermal"),
                   localizers=("vision",)) -> BodySchema:
    """Build the schema for the standard axial crawler. The parameters mirror
    ``crawler.build_crawler_xml`` so the diagram and the MuJoCo body describe the
    same organism."""
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
    return BodySchema(name=f"A{n_seg}", segments=segs)


# ----------------------------------------------------------------- glyphs ------
def zone(ax, x, y, r, filled="bottom", face=ZONE_FILL, label=None,
         label_dy=0.0, z=6):
    """A dual-interface zone: a circle, one half filled (acting, ``face``), one
    half unfilled/white (sensing). ``filled`` is 'bottom' or 'top'. Shared with
    the dynamics view, where ``face`` may be a state color."""
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor="#222",
                        lw=1.3, zorder=z))
    t1, t2 = (180, 360) if filled == "bottom" else (0, 180)
    ax.add_patch(Wedge((x, y), r, t1, t2, facecolor=face, edgecolor="#222",
                       lw=1.3, zorder=z + 1))
    if label:
        ax.text(x, y + label_dy, label, ha="center", va="center", fontsize=7.5,
                weight="bold", color="#222", zorder=z + 2)


def sensor_node(ax, x, y, r, modality, z=6):
    """A transducer drawn as a network node: an unfilled circle (white) with a
    modality-colored ring."""
    c = MODALITY_COLORS.get(modality, "#555")
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=c, lw=2.2,
                        zorder=z))


def _eye(ax, x, y, s, color):
    """A literal eye icon: sclera ellipse + iris + pupil."""
    ax.add_patch(Ellipse((x, y), 1.7 * s, s, facecolor="white",
                         edgecolor="#222", lw=1.0, zorder=6))
    ax.add_patch(Circle((x, y), 0.34 * s, facecolor=color, edgecolor="none", zorder=7))
    ax.add_patch(Circle((x, y), 0.15 * s, facecolor="#111", edgecolor="none", zorder=8))


def _ear(ax, x, y, s, color):
    """A literal ear icon: a small C-shaped arc."""
    ax.add_patch(Wedge((x, y), 0.6 * s, 300, 120, width=0.22 * s,
                       facecolor=color, edgecolor="#222", lw=0.8, zorder=6))


def _caz(ax, jx, r=0.20, dy=0.32, zone_labels=False, faces=(ZONE_FILL, ZONE_FILL),
         opponency=False):
    """A CAZ: an opposed pair of zones (Z+ upper, Z- lower), filled halves facing
    each other across the joint. Returns ((x, y+), (x, y-)) zone centers."""
    if opponency:                                    # the opponency coupling link
        ax.plot([jx, jx], [+dy, -dy], color=NETWORK_COLOR, lw=1.6, zorder=3)
    zone(ax, jx, +dy, r, filled="bottom", face=faces[0],
         label=("Z+" if zone_labels else None), label_dy=+(r + 0.17))
    zone(ax, jx, -dy, r, filled="top", face=faces[1],
         label=("Z−" if zone_labels else None), label_dy=-(r + 0.17))
    return (jx, +dy), (jx, -dy)


# ----------------------------------------------------- shared layout helper ----
def _layout(schema, seg_w, seg_h, gap):
    pitch = seg_w + gap
    centers = [-pitch * k for k in range(len(schema.segments))]
    caz_x = [centers[k] - pitch / 2 for k in range(len(schema.segments) - 1)]
    return pitch, centers, caz_x


def _compass(ax, centers, hw, hh):
    x0 = min(centers) - hw - 0.9
    ax.annotate("", xy=(x0 + 0.7, -hh - 1.0), xytext=(x0, -hh - 1.0),
                arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.3))
    ax.text(x0 + 0.8, -hh - 1.0, "anterior", fontsize=7.5, va="center", color="#333")


def _lr_labels(ax, head_x, hw, hh):
    ax.text(head_x + hw + 0.1, hh + 0.55, "L", fontsize=8, color="#b03030",
            ha="center", weight="bold")
    ax.text(head_x + hw + 0.1, -hh - 0.55, "R", fontsize=8, color="#3050b0",
            ha="center", weight="bold")


# --------------------------------------------------------- morphology view -----
def render_morphology(ax, schema: BodySchema, seg_w: float = 2.0,
                      seg_h: float = 1.0, gap: float = 0.5,
                      show_labels: bool = True, compass: bool = True,
                      zone_labels: bool = True, show_beam: bool = True):
    """Morphology view: blocks, CAZ zone-pairs, dense bilateral sensor strips,
    anterior localizer icons. Returns the CAZ x-positions."""
    hw, hh = seg_w / 2, seg_h / 2
    pitch, centers, caz_x = _layout(schema, seg_w, seg_h, gap)

    # messaging beam under the bodies (light blue), connecting the CAZ centers
    if show_beam and len(caz_x) > 1:
        ax.plot(caz_x, [0] * len(caz_x), color=NETWORK_COLOR, lw=2.0, zorder=1)

    for k, (cx, seg) in enumerate(zip(centers, schema.segments)):
        if any(t.kind == "touch" for t in seg.transducers):
            ax.add_patch(FancyBboxPatch(
                (cx - hw, -hh), seg_w, seg_h,
                boxstyle="round,pad=0.06,rounding_size=0.18",
                facecolor="none", edgecolor=MODALITY_COLORS["touch"],
                hatch="////", lw=0.0, alpha=0.55, zorder=1))
        face = "#bcd0f0" if seg.is_head else "#dfe6ef"
        ax.add_patch(FancyBboxPatch(
            (cx - hw, -hh), seg_w, seg_h,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor=face, edgecolor="#3a4a5e", lw=1.4, zorder=2))
        if show_labels:
            ax.text(cx, -hh * 0.45, seg.name, ha="center", va="center",
                    fontsize=9, color="#33414f", zorder=3)

        fields = [t for t in seg.transducers if t.kind == "field"]
        for mi, t in enumerate(fields):
            c = MODALITY_COLORS.get(t.modality, "#555")
            row = hh + 0.10 + 0.16 * mi
            xs = np.linspace(cx - hw * 0.7, cx + hw * 0.7, 7)
            for side in (+1, -1):
                ax.vlines(xs, side * row, side * (row + 0.11), color=c, lw=2.2,
                          zorder=4)

        for t in seg.transducers:
            if t.kind != "localizer":
                continue
            c = MODALITY_COLORS.get(t.modality, "#555")
            ic = _eye if _DISTAL.get(t.modality) == "eye" else _ear
            for side in (+1, -1):
                ic(ax, cx + hw + 0.45, side * hh * 0.55, 0.42, c)

        if k < len(schema.segments) - 1:
            _caz(ax, caz_x[k], zone_labels=zone_labels)

    if show_labels:
        _lr_labels(ax, centers[0], hw, hh)
    if compass:
        _compass(ax, centers, hw, hh)
    ax.set_aspect("equal")
    ax.set_xlim(min(centers) - hw - 1.2, centers[0] + hw + 1.4)
    ax.set_ylim(-hh - 1.5, hh + 1.5)
    ax.axis("off")
    return caz_x


# ------------------------------------------------------------ network view -----
def render_network(ax, schema: BodySchema, seg_w: float = 2.0,
                   seg_h: float = 1.0, gap: float = 0.5, compass: bool = True):
    """Network view: zones (Z+/Z-) and sensors as nodes, joined by light-blue
    coupling lines -- the messaging beam (CAZ<->CAZ), opponency (Z+<->Z- within a
    CAZ), and sensor->nearest-CAZ links. The body blocks are drawn faintly for
    grounding."""
    hw, hh = seg_w / 2, seg_h / 2
    pitch, centers, caz_x = _layout(schema, seg_w, seg_h, gap)
    caz_centers = [(jx, 0.0) for jx in caz_x]

    def nearest_caz(x):
        return min(caz_x, key=lambda jx: abs(jx - x)) if caz_x else None

    # --- faint body outline (grounding) ---
    for cx, seg in zip(centers, schema.segments):
        ax.add_patch(FancyBboxPatch(
            (cx - hw, -hh), seg_w, seg_h,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor="#f3f5f8", edgecolor="#c4ccd6", lw=1.0, zorder=0))

    # --- collect sensor nodes per segment ---
    sensors = []                          # (x, y, modality)
    for cx, seg in zip(centers, schema.segments):
        fields = [t for t in seg.transducers if t.kind == "field"]
        for mi, t in enumerate(fields):
            xo = cx + (mi - (len(fields) - 1) / 2) * (hw * 0.7)
            sensors.append((xo, +(hh + 0.75), t.modality))     # L
            sensors.append((xo, -(hh + 0.75), t.modality))     # R
        if any(t.kind == "touch" for t in seg.transducers):
            sensors.append((cx, 0.0, "touch"))                 # ventral, central
        for t in seg.transducers:
            if t.kind == "localizer":
                for side in (+1, -1):
                    sensors.append((cx + hw + 0.5, side * hh * 0.55, t.modality))

    # --- edges first (so nodes sit on top) ---
    if len(caz_centers) > 1:               # the messaging beam
        ax.plot([c[0] for c in caz_centers], [0] * len(caz_centers),
                color=NETWORK_COLOR, lw=2.4, zorder=2)
    for sx, sy, _ in sensors:              # sensor -> nearest CAZ
        jx = nearest_caz(sx)
        if jx is not None:
            ax.plot([sx, jx], [sy, 0.0], color=NETWORK_COLOR, lw=1.0,
                    alpha=0.8, zorder=2)

    # --- CAZ zone-pairs (with opponency link + Z+/Z- labels) ---
    for jx in caz_x:
        _caz(ax, jx, zone_labels=True, opponency=True)

    # --- sensor nodes on top ---
    for sx, sy, m in sensors:
        sensor_node(ax, sx, sy, 0.16, m)

    if compass:
        _compass(ax, centers, hw, hh)
    _lr_labels(ax, centers[0], hw, hh)
    ax.set_aspect("equal")
    ax.set_xlim(min(centers) - hw - 1.2, centers[0] + hw + 1.6)
    ax.set_ylim(-hh - 1.6, hh + 1.6)
    ax.axis("off")


def modality_legend(ax, modalities=None, with_network=True):
    """Draw the shared modality color legend (and the network-coupling key)."""
    from matplotlib.lines import Line2D
    mods = modalities or list(MODALITY_COLORS)
    handles = [Line2D([0], [0], marker="s", ls="", markersize=10,
                      markerfacecolor=MODALITY_COLORS[m], markeredgecolor="#333",
                      label=m) for m in mods]
    if with_network:
        handles.append(Line2D([0], [0], color=NETWORK_COLOR, lw=2.4,
                              label="coupling (network)"))
    ax.legend(handles=handles, loc="center", ncol=min(5, len(handles)),
              frameon=False, fontsize=8, title="modalities")
    ax.axis("off")
