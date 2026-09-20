# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The medusa — a free-swimming cnidarian, one dial-turn from the sessile disk.

The disk experiments held the cnidarian *sessile*. A sessile animal senses only
**world-caused** change: it cannot generate the self-caused sensory flow whose
subtraction (reafference) is what makes a world-model worth having. The **medusa**
is the same body plan set free — the bell **swims** by pulsation and the tentacles
**move** — so the animal now produces self-caused change against which the world
stands out. (Body-plan dial, ``SMN_cnidarian_model_system.md``: sac→polyp,
**+tentacles→medusa**.)

Morphology (settled vocabulary — ``docs/vocabulary.md``). Point-mass **segments**
(``s``) on a shallow **dome** (a paraboloid umbrella, apex aboral/up at ``+z``);
every **link is one ``f``** — a pull-only contractile unit. Three link kinds:

- **coronal** — the circumferential (ring) links: the **subumbrellar swimming
  muscle**. Contracting the coronal ring squeezes the bell margin inward-and-under
  (the power stroke), sweeping the subumbrellar surface down; in a drag medium that
  sweep is the **jet** (see :func:`apply_medium`). These are the ``f``s driven to
  swim.
- **radial** — the spoke links (apex→ring, ring→ring): structural mesoglea that
  bears the dome and elastically restores it (the recovery stroke). Present as
  ``f``s but not driven for swimming.
- **tentacle** — single chains of ``f`` hanging from the margin (oral, ``-z``);
  contracting a tentacle chain **curls/retracts** it, the series spring re-extends
  (single-chain curl — no aiming, the medusa's simplest movable appendage).

Coordination (which ``f``s fire together, and when) is the whole SMN's and is read
out, never imposed by a controller — the swim is a **pulsation pattern** over the
coronal ``f``s, a CAZ in the settled sense.

This module builds the ``f`` scaffold (via :func:`smn_lab.lattice._lattice_mjcf`)
and the swimming medium; the experiments drive it and read the self/world models.
"""
from __future__ import annotations
import numpy as np
import mujoco

from smn_lab.lattice import _lattice_mjcf

DT = 0.002


# =================================================================== morphology ===
def medusa_spec(n_spoke=8, n_ring=3, n_tent=6, l_tent=4,
                r_max=0.34, z_apex=0.22, t_step=0.085, t_drop=0.075):
    """A shallow-dome bell + single-chain tentacles on the margin.

    Returns a dict with ``pos`` (N,3), ``edges`` [(a,b)…], per-link ``edge_kind``
    ('coronal' | 'radial' | 'tentacle'), per-node ``node_kind`` ('apex' | 'bell' |
    'margin' | 'tentacle' | 'tip'), the ``coronal`` / ``radial`` / ``tentacle`` link
    id-lists, ``margin`` node ids, tentacle ``tips``, a 2-D ``layout`` (top view for
    the self/world card), and the aboral swim axis (``+z``).

    Geometry: ring ``r`` sits at radius ``rad_r = r_max·(r+1)/n_ring`` and height
    ``z = z_apex·(1 − (rad_r/r_max)²)`` — a paraboloid umbrella with the apex aboral
    (up). Tentacles hang oral (down, ``-z``) and outward from ``n_tent`` evenly-spaced
    margin spokes.
    """
    pos, node_kind, layout = [], [], {}

    apex = 0
    pos.append((0.0, 0.0, z_apex)); node_kind.append("apex"); layout[0] = (0.0, 0.0)

    def ring_id(r, c):
        return 1 + r * n_spoke + c

    for r in range(n_ring):
        rad = r_max * (r + 1) / n_ring
        z = z_apex * (1.0 - (rad / r_max) ** 2)
        for c in range(n_spoke):
            th = 2 * np.pi * c / n_spoke
            pos.append((rad * np.cos(th), rad * np.sin(th), z))
            node_kind.append("margin" if r == n_ring - 1 else "bell")
            layout[len(pos) - 1] = (rad * np.cos(th), rad * np.sin(th))

    edges, edge_kind = [], []

    # radial: apex -> ring 0 (structural mesoglea)
    for c in range(n_spoke):
        edges.append((apex, ring_id(0, c))); edge_kind.append("radial")
    # radial: ring r -> ring r+1
    for r in range(n_ring - 1):
        for c in range(n_spoke):
            edges.append((ring_id(r, c), ring_id(r + 1, c))); edge_kind.append("radial")
    # coronal: circumferential ring links (the swimming muscle)
    for r in range(n_ring):
        for c in range(n_spoke):
            edges.append((ring_id(r, c), ring_id(r, (c + 1) % n_spoke)))
            edge_kind.append("coronal")

    # tentacles: single chains hanging from evenly-spaced margin spokes. Each chain is
    # driven **longitudinal** ``f``s (contract → curl) plus passive **brace** ``f``s
    # (2-hop links = the mesoglea): a single floppy chain has no bending stiffness and
    # never re-extends, so the brace is the elastic antagonist that restores the
    # tentacle's rest shape — the muscular-hydrostat opponent, not a discrete pair.
    margin = [ring_id(n_ring - 1, c) for c in range(n_spoke)]
    spokes = sorted({int(round(k * n_spoke / n_tent)) % n_spoke for k in range(n_tent)})
    tips = []
    for c in spokes:
        root = ring_id(n_ring - 1, c)
        th = 2 * np.pi * c / n_spoke
        chain = [root]
        for t in range(l_tent):
            rad = r_max + (t + 1) * t_step
            z = -(t + 1) * t_drop
            pos.append((rad * np.cos(th), rad * np.sin(th), z))
            node_kind.append("tip" if t == l_tent - 1 else "tentacle")
            layout[len(pos) - 1] = (rad * np.cos(th), rad * np.sin(th))
            i = len(pos) - 1
            edges.append((chain[-1], i)); edge_kind.append("tentacle"); chain.append(i)
        tips.append(chain[-1])
        for j in range(len(chain) - 2):                    # 2-hop mesoglea braces (passive)
            edges.append((chain[j], chain[j + 2])); edge_kind.append("brace")

    edge_kind = np.array(edge_kind)
    return dict(
        pos=np.array(pos), edges=edges, edge_kind=edge_kind,
        node_kind=np.array(node_kind), layout=layout,
        coronal=np.flatnonzero(edge_kind == "coronal").tolist(),
        radial=np.flatnonzero(edge_kind == "radial").tolist(),
        tentacle=np.flatnonzero(edge_kind == "tentacle").tolist(),
        brace=np.flatnonzero(edge_kind == "brace").tolist(),
        margin=margin, tips=tips, spokes=spokes,
        n_spoke=n_spoke, n_ring=n_ring, swim_axis=2)


def build_medusa(spec, *, lat_stiff=18.0, link_damp=0.5, seg_damp=2.0,
                 seg_mass=0.05, cmax=4.0, name="medusa"):
    """MJCF for a :func:`medusa_spec` body: 3-DOF point-mass ``s`` nodes + one
    pull-only ``f`` per edge (via :func:`smn_lab.lattice._lattice_mjcf`). ``seg_damp``
    is left *lighter* than the sessile lattices (2.0 vs 4.0): swimming needs the bell
    to carry momentum between strokes, not to be fully overdamped. Returns
    ``(model, data, body_ids)``."""
    xml = _lattice_mjcf(spec["pos"], spec["edges"], lat_stiff=lat_stiff,
                        link_damp=link_damp, seg_damp=seg_damp, seg_mass=seg_mass,
                        cmax=cmax, name=name)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(len(spec["pos"]))]
    return m, d, bid


# ==================================================================== the medium ===
def apply_medium(model, data, body_ids, *, c_quad=6.0, c_lin=0.4, axis=2, axis_gain=2.0):
    """The pond, as an explicit drag law applied through ``xfrc_applied`` — the same
    inspectable-medium philosophy as the crawler, but **quadratic**.

    A pulsatile swimmer must escape the scallop theorem: a *reciprocal* shape change
    (contract then relax) nets zero displacement under **linear** drag, however fast.
    The escape is a **rate asymmetry** biting against a **nonlinear** law — the fast
    power stroke meets far more resistance than the slow recovery, so their drag
    impulses do not cancel. Hence ``f = -(c_lin + c_quad·|v|)·v`` per segment
    (``c_quad`` is the jet-bearing term; ``c_lin`` keeps the body from coasting
    forever). ``axis_gain`` mildly anisotropizes the medium along the swim ``axis``
    (a bell pushes more water along its axis than across it). Call once per step,
    before ``mj_step``. Set ``c_quad=0`` for the linear-drag control (swimming should
    then collapse — the scallop-theorem check)."""
    g = np.ones(3); g[axis] = axis_gain
    qv = data.qvel.reshape(-1, 3)                      # each node = 3 world-axis slides (jx,jy,jz)
    for i, bid in enumerate(body_ids):
        v = qv[i]                                      # world-frame linear velocity of node i
        speed = float(np.linalg.norm(v))
        data.xfrc_applied[bid, 0:3] = -(c_lin + c_quad * speed) * g * v
        data.xfrc_applied[bid, 3:6] = 0.0


def swim_drive(t, coronal_ids, nu, *, period=0.9, duty=0.18, amp=4.0):
    """A **pulsation** over the coronal (swimming) ``f``s: a fast power stroke (the
    first ``duty`` of each ``period`` at contraction ``amp``) then release (the spring
    recovers, slowly). Returns a length-``nu`` ctrl vector (pull-only, ≥0). Only the
    coronal ``f``s are driven; radial/tentacle stay at rest here. The rate asymmetry
    (sharp on, spring-limited off) is what :func:`apply_medium` converts to thrust —
    a *reciprocal* (symmetric) drive would net nothing."""
    ctrl = np.zeros(nu)
    phase = (t % period) / period
    if phase < duty:
        ctrl[coronal_ids] = amp                       # power stroke: fast, hard contraction
    return ctrl
