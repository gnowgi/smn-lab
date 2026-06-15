# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The SMN diagram grammar -- a body schema and its canonical rendering.

A single source of truth for *both* the morphology diagram and (by sharing the
same parameters as ``crawler.build_crawler_xml``) the simulated body, so a
published figure cannot drift from the code that ran. The grammar borrows the
recognizable conventions of the field where they exist, and uses one glyph of our
own where the SMN concept has no standard:

- **zone = a half-filled / half-unfilled circle** (OUR notation): the filled half
  is the acting interface, the unfilled half the sensing interface -- the
  *dual-interface* unit. A **CAZ is an opposed pair of zones** (the two sensation
  modulators), drawn facing each other across the inter-segment joint.
- a head-to-tail segment chain     (a kinematic tree / URDF-style body)
- literal anterior sensor icons    (Braitenberg-style front-mounted sensors)
- color-coded distributed strips   (abstract, dense, with a legend)

Conventions held fixed across every C-series figure:
- **anterior = +x (right)**, matching the crawler code (head = seg0 at +x);
- top view; **L = +y (warm)**, **R = -y (cool)**, matching the body's L/R sites;
- one fixed modality->color table (``MODALITY_COLORS``), shown as a shared legend;
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


ZONE_FILL = "#f4c542"            # the zone's acting (filled) interface


def _zone(ax, x, y, r, filled="bottom", color=ZONE_FILL, z=5):
    """A dual-interface zone: a circle, one half filled (acting), one half
    unfilled/white (sensing)."""
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor="#222",
                        lw=1.3, zorder=z))
    t1, t2 = (180, 360) if filled == "bottom" else (0, 180)
    ax.add_patch(Wedge((x, y), r, t1, t2, facecolor=color, edgecolor="#222",
                       lw=1.3, zorder=z + 1))


def _caz(ax, jx, r=0.20, dy=0.30):
    """A CAZ: an opposed pair of zones at the joint, filled halves facing each
    other across the inter-segment axis (the two sensation modulators)."""
    _zone(ax, jx, +dy, r, filled="bottom")     # upper zone, acts downward
    _zone(ax, jx, -dy, r, filled="top")        # lower zone, acts upward


# --------------------------------------------------------------- renderer ------
def render_morphology(ax, schema: BodySchema, seg_w: float = 2.0,
                      seg_h: float = 1.0, gap: float = 0.5,
                      show_labels: bool = True, compass: bool = True):
    """Draw ``schema`` in the canonical grammar onto ``ax``.

    Head is at the right (anterior = +x); the chain extends left. Returns the
    list of CAZ centers (for callers that also draw the beam graph)."""
    hw, hh = seg_w / 2, seg_h / 2
    pitch = seg_w + gap
    centers = [-pitch * k for k in range(len(schema.segments))]   # x of each seg
    caz_x = []

    for k, (cx, seg) in enumerate(zip(centers, schema.segments)):
        # --- ventral touch skin (drawn first, as a hatched underlay) ----------
        if any(t.kind == "touch" for t in seg.transducers):
            ax.add_patch(FancyBboxPatch(
                (cx - hw, -hh), seg_w, seg_h,
                boxstyle="round,pad=0.06,rounding_size=0.18",
                facecolor="none", edgecolor=MODALITY_COLORS["touch"],
                hatch="////", lw=0.0, alpha=0.55, zorder=1))
        # --- segment body -----------------------------------------------------
        face = "#bcd0f0" if seg.is_head else "#dfe6ef"
        ax.add_patch(FancyBboxPatch(
            (cx - hw, -hh), seg_w, seg_h,
            boxstyle="round,pad=0.0,rounding_size=0.18",
            facecolor=face, edgecolor="#3a4a5e", lw=1.4, zorder=2))
        if show_labels:
            ax.text(cx, -hh * 0.45, seg.name, ha="center", va="center",
                    fontsize=9, color="#33414f", zorder=3)

        # --- distributed bilateral field strips (ticks on both lateral edges) --
        fields = [t for t in seg.transducers if t.kind == "field"]
        for mi, t in enumerate(fields):
            c = MODALITY_COLORS.get(t.modality, "#555")
            row = hh + 0.10 + 0.16 * mi                 # stack modalities outward
            xs = np.linspace(cx - hw * 0.7, cx + hw * 0.7, 7)
            for side in (+1, -1):                        # +y = L, -y = R
                ax.vlines(xs, side * row, side * (row + 0.11), color=c, lw=2.2,
                          zorder=4)

        # --- anterior localizer icons (paired) --------------------------------
        for t in seg.transducers:
            if t.kind != "localizer":
                continue
            c = MODALITY_COLORS.get(t.modality, "#555")
            ic = _eye if _DISTAL.get(t.modality) == "eye" else _ear
            for side in (+1, -1):
                ic(ax, cx + hw + 0.45, side * hh * 0.55, 0.42, c)

        # --- CAZ: an opposed pair of dual-interface zones at the joint --------
        if k < len(schema.segments) - 1:
            jx = cx - pitch / 2
            caz_x.append(jx)
            _caz(ax, jx)

    # --- messaging beam: dashed link along the CAZ circles --------------------
    if len(caz_x) > 1:
        ax.plot(caz_x, [0] * len(caz_x), ls=(0, (4, 3)), color="#444",
                lw=1.6, zorder=4)

    # --- L/R labels at the head + axis compass --------------------------------
    head_x = centers[0]
    if show_labels:
        ax.text(head_x + hw + 0.1, hh + 0.55, "L", fontsize=8, color="#b03030",
                ha="center", weight="bold")
        ax.text(head_x + hw + 0.1, -hh - 0.55, "R", fontsize=8, color="#3050b0",
                ha="center", weight="bold")
    if compass:
        x0 = min(centers) - hw - 0.9
        ax.annotate("", xy=(x0 + 0.7, -hh - 1.0), xytext=(x0, -hh - 1.0),
                    arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.3))
        ax.text(x0 + 0.8, -hh - 1.0, "anterior", fontsize=7.5, va="center", color="#333")

    ax.set_aspect("equal")
    ax.set_xlim(min(centers) - hw - 1.2, head_x + hw + 1.4)
    ax.set_ylim(-hh - 1.5, hh + 1.5)
    ax.axis("off")
    return caz_x


def modality_legend(ax, modalities=None):
    """Draw the shared modality color legend on its own axis."""
    mods = modalities or list(MODALITY_COLORS)
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="s", ls="", markersize=10,
                      markerfacecolor=MODALITY_COLORS[m], markeredgecolor="#333",
                      label=m) for m in mods]
    ax.legend(handles=handles, loc="center", ncol=min(4, len(mods)),
              frameon=False, fontsize=8, title="modalities")
    ax.axis("off")
