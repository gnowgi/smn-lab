# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""F1 (revised) -- body topologies from chains of CAZ nodes, in the SMN grammar.

Different organizations of chains of CAZ nodes make different body topologies, and
each new layer anchors on the stabilized old one, adding zones NON-monotonically.
That non-monotonic anchoring is the reply to the objection that behaviour is
monotonic and so cannot ground generativity: generativity comes from a new layer
reorganizing an old, stable one -- not from adding symbols on top.

This module draws caricatures of the series (Panel-1 only -- pure morphology; the
self-model / world-model panels are computational and live elsewhere):

  1. nematode    -- a polarized, unsegmented tube: a bundle of longitudinal CAZ
                    chains of different lengths in an elastic substrate; dorsal /
                    ventral opponency drives an alternating planar wave.
  (2 earthworm, 3 appendicular -- to follow.)

Run:  ../.venv/bin/python fig_topologies.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, Polygon, Ellipse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.morphology import NETWORK_COLOR, MODALITY_COLORS

SUBSTRATE = "#eef4ef"
SUB_EDGE = "#9dc3a9"
ZONE = "#f4c542"        # an acting zone (a CAZ half)
INK = "#33414f"
AXIAL = "#2c3e50"       # the retained, stabilized axial core (BAP)
APPEND = "#e8902a"      # an emancipated appendage (HAP -> NAP)
CIRC = "#5f95bf"        # a circular CAZ chain (the longitudinal chains' antagonist)


def _capsule(ax, cx, cy, w, h, *, fc, ec, lw=1.6, z=2):
    rs = min(w, h) / 2 * 0.85
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle=f"round,pad=0,rounding_size={rs}", facecolor=fc,
                 edgecolor=ec, lw=lw, zorder=z))


def _zone_chain_between(ax, p0, p1, n, *, r=0.10, z=6, fc=ZONE, beam_lw=1.8):
    """A chain of dual-interface zones along an arbitrary segment (split along the
    chain direction: acting half one side, sensing half the other)."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=NETWORK_COLOR, lw=beam_lw,
            zorder=z, solid_capstyle="round")
    ang = np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0]))
    for t in np.linspace(0, 1, n):
        c = p0 + t * (p1 - p0)
        ax.add_patch(Wedge(c, r, ang, ang + 180, facecolor=fc, edgecolor=INK, lw=0.8, zorder=z + 1))
        ax.add_patch(Wedge(c, r, ang + 180, ang + 360, facecolor="white", edgecolor=INK, lw=0.8, zorder=z + 1))


def _zone_chain(ax, x0, x1, y, n, *, r=0.11, z=4):
    """A longitudinal chain of zones (small dual-interface circles) joined by the
    messaging beam."""
    xs = np.linspace(x0, x1, n)
    ax.plot([x0, x1], [y, y], color=NETWORK_COLOR, lw=2.0, zorder=z, solid_capstyle="round")
    for x in xs:
        ax.add_patch(Wedge((x, y), r, 90, 270, facecolor=ZONE, edgecolor=INK, lw=0.9, zorder=z + 1))
        ax.add_patch(Wedge((x, y), r, -90, 90, facecolor="white", edgecolor=INK, lw=0.9, zorder=z + 1))
    return xs


def nematode(ax):
    L, R = 0.4, 10.6                      # tube extent
    hw = 1.15                             # half-width (radius) of the tube
    ax.add_patch(FancyBboxPatch((L, -hw), R - L, 2 * hw,
                 boxstyle="round,pad=0,rounding_size=1.1", facecolor=SUBSTRATE,
                 edgecolor=SUB_EDGE, lw=1.8, zorder=1))
    ax.text((L + R) / 2, hw + 0.42, "elastic substrate (hydrostatic)", ha="center",
            fontsize=8.5, color="#5b7d67", style="italic")

    # anterior / head at the left, with two chemosensory dots (amphids)
    ax.add_patch(Circle((L + 0.55, 0), 0.62, facecolor="#d7e7dc", edgecolor=SUB_EDGE, lw=1.4, zorder=2))
    for dy in (0.26, -0.26):
        ax.add_patch(Circle((L + 0.28, dy), 0.10, facecolor="white",
                     edgecolor=MODALITY_COLORS["chem"], lw=1.8, zorder=4))
    ax.annotate("anterior", (L + 0.55, 0), textcoords="offset points", xytext=(0, 44),
                ha="center", fontsize=8.5, color="#3a4a5a",
                arrowprops=dict(arrowstyle="-", color="#8aa0af", lw=1))

    # a BUNDLE of longitudinal zone-chains of DIFFERENT lengths, packed in the tube
    chains = [(2.1, 9.9, 0.78, 8), (1.7, 10.1, 0.30, 9),
              (1.9, 9.7, -0.30, 8), (2.3, 9.3, -0.78, 7)]
    for x0, x1, y, n in chains:
        _zone_chain(ax, x0, x1, y, n)
    ax.annotate("longitudinal CAZ chains\nof different lengths", (10.1, 0.30),
                textcoords="offset points", xytext=(22, 8), va="center", fontsize=8.5,
                color="#8a5200",
                bbox=dict(boxstyle="round,pad=0.35", fc="#fff4e3", ec=ZONE, lw=1.1))

    # the alternating planar wave the chains produce
    xx = np.linspace(L + 0.9, R - 0.4, 240)
    ax.plot(xx, 0.62 * np.sin(2 * np.pi * (xx - L) / 4.4), color="#b0632a",
            lw=1.6, alpha=0.45, ls=(0, (5, 3)), zorder=3)
    ax.annotate("alternating planar wave", (R - 1.0, 0.6 * np.sin(2 * np.pi * (R - 1.0 - L) / 4.4)),
                textcoords="offset points", xytext=(-6, 34), fontsize=8.5, color="#8a4a1c")

    ax.set_xlim(L - 1.4, R + 3.4); ax.set_ylim(-hw - 1.0, hw + 1.0)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("1 · Nematode — a polarized, unsegmented tube\n"
                 "a bundle of longitudinal CAZ chains of different lengths → "
                 "an alternating planar wave", fontsize=11)


def earthworm(ax):
    """2 -- a metamerically segmented tube. The nematode tube is REPEATED as a
    metamere; the septa are the new layer that reorganizes it into a serial chain.
    Segment widths trace a travelling peristaltic wave."""
    n_seg = 9
    base_r, amp = 0.80, 0.15
    baseL, Lamp = 1.10, 0.24
    x = 1.5
    seg = []
    for i in range(n_seg):
        phase = 2 * np.pi * i / 3.4               # peristaltic wavelength ~3.4 segments
        r = base_r - amp * np.cos(phase)          # thin where circular muscle contracts...
        Ln = baseL + Lamp * np.cos(phase)         # ...and then it is long: anti-correlated
        cx = x + Ln / 2
        seg.append((cx, r, Ln))
        x += Ln * 0.90                            # slight overlap -> a continuous body

    # anterior prostomium at the left, polarized, with two chemosensory dots
    hx = seg[0][0] - seg[0][2] / 2
    ax.add_patch(FancyBboxPatch((hx - 1.0, -base_r * 0.78), 1.05, 2 * base_r * 0.78,
                 boxstyle="round,pad=0,rounding_size=0.62", facecolor="#d7e7dc",
                 edgecolor=SUB_EDGE, lw=1.4, zorder=2))
    for dy in (0.22, -0.22):
        ax.add_patch(Circle((hx - 0.78, dy), 0.09, facecolor="white",
                     edgecolor=MODALITY_COLORS["chem"], lw=1.7, zorder=6))
    ax.annotate("anterior", (hx - 0.5, 0), textcoords="offset points", xytext=(0, 40),
                ha="center", fontsize=8.5, color="#3a4a5a",
                arrowprops=dict(arrowstyle="-", color="#8aa0af", lw=1))

    # segment bodies (each a retained tube-unit) + septa between them
    for cx, r, Ln in seg:
        _capsule(ax, cx, 0, Ln, 2 * r, fc=SUBSTRATE, ec=SUB_EDGE, lw=1.6, z=2)
    for cx, r, Ln in seg:
        ax.plot([cx - Ln / 2, cx - Ln / 2], [-r * 0.86, r * 0.86],
                color=SUB_EDGE, lw=1.3, zorder=3)

    # three longitudinal chains retained from the tube -- run straight through
    xs = [s[0] for s in seg]
    for y in (0.30, 0.0, -0.30):
        ax.plot([xs[0], xs[-1]], [y, y], color=NETWORK_COLOR, lw=1.6, zorder=5,
                solid_capstyle="round")
        for cx in xs:
            ax.add_patch(Wedge((cx, y), 0.09, 90, 270, facecolor=ZONE, edgecolor=INK, lw=0.7, zorder=6))
            ax.add_patch(Wedge((cx, y), 0.09, -90, 90, facecolor="white", edgecolor=INK, lw=0.7, zorder=6))

    # circular CAZ chains -- a ring at the CENTRE of each metamere (well clear of the
    # septa), sheathing the longitudinal bundle. Circular vs longitudinal is the
    # antagonist pair for peristalsis.
    for cx, r, Ln in seg:
        ax.add_patch(Ellipse((cx, 0), 0.30, 2 * r * 0.95, facecolor="none",
                     edgecolor=CIRC, lw=1.6, zorder=4))
        for sy in (r * 0.80, -r * 0.80):
            ax.add_patch(Wedge((cx, sy), 0.08, 90, 270, facecolor=CIRC, edgecolor=INK, lw=0.7, zorder=7))
            ax.add_patch(Wedge((cx, sy), 0.08, -90, 90, facecolor="white", edgecolor=INK, lw=0.7, zorder=7))

    # peristaltic wave arrow along the top
    top = max(s[1] for s in seg) + 0.5
    ax.annotate("", xy=(xs[-1], top), xytext=(xs[0], top),
                arrowprops=dict(arrowstyle="-|>", color="#b0632a", lw=1.8, alpha=0.7))
    ax.text((xs[0] + xs[-1]) / 2, top + 0.18, "peristaltic wave", ha="center",
            fontsize=8.5, color="#8a4a1c")

    # labels: the retained tube-unit, and the new layer
    ax.annotate("metamere —\na retained tube-unit", (seg[4][0], -seg[4][1]),
                textcoords="offset points", xytext=(0, -46), ha="center", fontsize=8.5,
                color="#8a5200", bbox=dict(boxstyle="round,pad=0.35", fc="#fff4e3", ec=ZONE, lw=1.1),
                arrowprops=dict(arrowstyle="-", color=ZONE, lw=1.2))
    ax.annotate("septum (the new layer)", (seg[6][0] - seg[6][2] / 2, seg[6][1] * 0.4),
                textcoords="offset points", xytext=(30, 30), fontsize=8.5, color="#3a6a4a",
                bbox=dict(boxstyle="round,pad=0.3", fc="#eef7f0", ec=SUB_EDGE, lw=1.0),
                arrowprops=dict(arrowstyle="-", color=SUB_EDGE, lw=1.1))

    # legend for the two antagonist muscle systems
    lx, ly = hx - 0.2, -base_r - 1.35
    ax.plot([lx, lx + 0.42], [ly, ly], color=ZONE, lw=4.5, solid_capstyle="round", zorder=6)
    ax.text(lx + 0.58, ly, "longitudinal CAZ chains", va="center", fontsize=8.5, color="#8a6a00")
    ax.add_patch(Ellipse((lx + 0.21, ly - 0.5), 0.20, 0.36, facecolor="none", edgecolor=CIRC, lw=1.6, zorder=6))
    ax.text(lx + 0.58, ly - 0.5, "circular CAZ chains (rings) — the antagonist → peristalsis",
            va="center", fontsize=8.5, color="#2f5f85")

    ax.set_xlim(hx - 2.6, xs[-1] + 2.0); ax.set_ylim(-base_r - 2.3, base_r + 1.3)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("2 · Earthworm — a metamerically segmented tube\n"
                 "longitudinal and circular CAZ chains (antagonists) woven per metamere → peristalsis",
                 fontsize=11)


def _leg(ax, base, ang_deg, seg_len, z=7):
    a = np.radians(ang_deg)
    knee = base + seg_len * np.array([np.cos(a), np.sin(a)])
    a2 = a - np.radians(48)                        # the joint bends outward
    foot = knee + seg_len * 0.95 * np.array([np.cos(a2), np.sin(a2)])
    _zone_chain_between(ax, base, knee, 2, r=0.095, fc=APPEND, z=z)
    _zone_chain_between(ax, knee, foot, 2, r=0.095, fc=APPEND, z=z)


def _wing(ax, base, ang_deg, length, z=6):
    a = np.radians(ang_deg); spread = np.radians(17)
    tip = base + length * np.array([np.cos(a), np.sin(a)])
    p1 = base + length * np.array([np.cos(a - spread), np.sin(a - spread)])
    p2 = base + length * np.array([np.cos(a + spread), np.sin(a + spread)])
    ax.add_patch(Polygon([base, p1, p2], closed=True, facecolor=APPEND, alpha=0.15,
                 edgecolor=APPEND, lw=1.0, zorder=z - 1))
    _zone_chain_between(ax, base, tip, 3, r=0.085, fc=APPEND, z=z)


def appendicular(ax):
    """3 -- a segmented trunk with emancipated appendages. The trunk (axial core) is
    retained and stabilized (BAP); each limb is itself a CAZ chain branching off a
    segment (HAP -> NAP). The old, stable layer ANCHORS the new -- non-monotonic
    layering. Limbs open new habitats, flight among them."""
    n_seg = 9
    r = 0.60
    Ln = 1.06
    x0 = 2.2
    cx = [x0 + i * Ln for i in range(n_seg)]

    # axial trunk: the retained, stabilized segmented core (dark)
    for c in cx:
        _capsule(ax, c, 0, Ln * 0.98, 2 * r, fc=AXIAL, ec="#1b2733", lw=1.4, z=3)
    for c in cx:
        ax.plot([c - Ln / 2, c - Ln / 2], [-r * 0.82, r * 0.82], color="#54687a", lw=1.1, zorder=4)
    # axial longitudinal chain (retained tube), one zone per segment
    ax.plot([cx[0], cx[-1]], [0, 0], color="#8aa0af", lw=1.4, zorder=5)
    for c in cx:
        ax.add_patch(Circle((c, 0), 0.085, facecolor="#dfe6ef", edgecolor="#1b2733", lw=0.9, zorder=6))

    # anterior head
    hx = cx[0] - Ln / 2
    ax.add_patch(Circle((hx - 0.42, 0), 0.52, facecolor=AXIAL, edgecolor="#1b2733", lw=1.4, zorder=3))
    for dy in (0.20, -0.20):
        ax.add_patch(Circle((hx - 0.66, dy), 0.085, facecolor="white",
                     edgecolor=MODALITY_COLORS["chem"], lw=1.6, zorder=6))

    # wings on the anterior dorsal segments (air), a bilateral pair each
    for c in (cx[2], cx[3]):
        _wing(ax, np.array([c, r]), 108, 1.7)
        _wing(ax, np.array([c, r]),  72, 1.7)
    # legs on the mid ventral segments (ground / water), jointed CAZ chains
    for c in (cx[3], cx[4], cx[5]):
        _leg(ax, np.array([c, -r]), -108, 0.72)
        _leg(ax, np.array([c, -r]),  -72, 0.72)

    # labels -- kept in four clear quadrants so no two boxes collide
    ax.annotate("wing — a CAZ chain + membrane (air)", (cx[2], r + 1.55),
                textcoords="offset points", xytext=(-40, 20), fontsize=8.5, color="#8a5200",
                bbox=dict(boxstyle="round,pad=0.35", fc="#fff4e3", ec=APPEND, lw=1.1))
    ax.annotate("axial core — retained & stabilized (BAP)", (cx[8], r * 0.5),
                textcoords="offset points", xytext=(24, 58), ha="center", fontsize=9,
                color="#e8eef4", va="center",
                bbox=dict(boxstyle="round,pad=0.4", fc=AXIAL, ec="#1b2733", lw=1.0),
                arrowprops=dict(arrowstyle="-", color="#8aa0af", lw=1.1))
    ax.annotate("leg — a jointed CAZ chain (ground / water)", (cx[5] + 0.35, -r - 1.55),
                textcoords="offset points", xytext=(70, -18), fontsize=8.5, color="#8a5200",
                bbox=dict(boxstyle="round,pad=0.35", fc="#fff4e3", ec=APPEND, lw=1.1),
                arrowprops=dict(arrowstyle="-", color=APPEND, lw=1.1))
    ax.annotate("the old layer anchors the new\n— non-monotonic layering", (cx[3], -r - 0.8),
                textcoords="offset points", xytext=(-70, -70), ha="center", fontsize=8.5,
                color="#7a3f14", style="italic")

    ax.set_xlim(hx - 2.4, cx[-1] + 1.6); ax.set_ylim(-r - 3.0, r + 3.0)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("3 · Appendicular — a segmented trunk with emancipated appendages\n"
                 "each limb is a CAZ chain branching off a segment; the stabilized core "
                 "anchors them → new habitats, flight among them", fontsize=11)


def _save(fig, name, dpi=140):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", name)
    fig.savefig(out, dpi=dpi)
    print(f"figure -> {os.path.normpath(out)}")


def main():
    for fn, name, size in [(nematode, "topology_nematode.png", (11, 4.2)),
                           (earthworm, "topology_earthworm.png", (11, 4.4)),
                           (appendicular, "topology_appendicular.png", (11, 5.6))]:
        fig, ax = plt.subplots(figsize=size)
        fn(ax); fig.tight_layout(); _save(fig, name); plt.close(fig)

    # the assembled series (this is F1): one new layer anchoring on the last
    fig, axes = plt.subplots(3, 1, figsize=(11, 14),
                             gridspec_kw=dict(height_ratios=[4.2, 4.4, 5.6]))
    nematode(axes[0]); earthworm(axes[1]); appendicular(axes[2])
    fig.suptitle("Body topologies from chains of CAZ nodes — "
                 "each new layer anchors on the stabilized old one", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    _save(fig, "topology_series.png", dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
