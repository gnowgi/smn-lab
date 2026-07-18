# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Lattice body plans — chain / sheet / tube as linked linear-actuator CAZ.

A **muscle** is a chain of CAZ; a **sheet** is two such chains linked laterally; a
**tube** (worm, gut, vessel) is three or more chains linked longitudinally *and*
laterally, closed into a ring. In every case the **segments are point-mass
scaffolding** (a place to mount sensors) and every **link is one CAZ** — a
spring-tendon muscle-tendon unit with its own linear actuator. Longitudinal links
are longitudinal muscle; lateral links are circular muscle.

The point of this module is Phase I·①: the *same* self-model read-out
(:func:`smn_lab.self_model.coupling`) recovers the body graph whatever the topology
— a path (chain), a ladder (sheet), a cylinder (tube). One function, any body.

Segments are **overdamped** (``seg_damp``): soft tissue lives in the same
low-Reynolds regime as the crawler's medium, and in that regime a driven link's
force appears only at its two endpoints — which is exactly what makes the graph
locally recoverable however dense the lattice.
"""
from __future__ import annotations
import numpy as np


# --8<-- [start:edges]
def lattice_edges(n_col, n_row=1, closed=False):
    """The true body graph: (a, b) segment-index edges. Longitudinal links run
    within each row (a muscle); lateral links run between rows (circular), wrapped
    row ``n_row-1`` -> row ``0`` when ``closed`` and ``n_row >= 3`` (a tube)."""
    def idx(r, c):
        return r * n_col + c
    edges = []
    for r in range(n_row):
        for c in range(n_col - 1):
            edges.append((idx(r, c), idx(r, c + 1)))          # longitudinal
    row_pairs = [(r, r + 1) for r in range(n_row - 1)]
    if closed and n_row >= 3:
        row_pairs.append((n_row - 1, 0))                      # close the ring
    for ra, rb in row_pairs:
        for c in range(n_col):
            edges.append((idx(ra, c), idx(rb, c)))            # lateral
    return edges
# --8<-- [end:edges]


def lattice_positions(n_col, n_row, closed, dx=0.16, dy=0.16, z0=0.4):
    """Initial (x, y, z) of each segment. Chain/sheet lie flat (rows stacked in y);
    a closed tube wraps its rows around a circular cross-section (in the y-z plane)
    so every lateral neighbour — including the wrap — is equidistant."""
    pos = np.zeros((n_row * n_col, 3))
    ring = closed and n_row >= 3
    rho = dy / (2 * np.sin(np.pi / n_row)) if ring else 0.0
    for r in range(n_row):
        for c in range(n_col):
            i = r * n_col + c
            if ring:
                th = 2 * np.pi * r / n_row
                pos[i] = (-c * dx, rho * np.cos(th), z0 + rho * np.sin(th))
            else:
                pos[i] = (-c * dx, r * dy, z0)
    return pos


# --8<-- [start:nested_spec]
def nested_lattice_spec(n_super=3, mid_group=3, block_rows=2, block_cols=2,
                        bs=0.13, dy_mid=0.5, dx_super=1.9, z0=0.4):
    """A three-level nested lattice that **tapers** up the hierarchy — e.g. the
    default 36 segments -> 9 blocks -> 3 super-blocks. ``n_super`` super-blocks each
    hold ``mid_group`` blocks, each a ``block_rows x block_cols`` fine lattice.
    Every link is tagged by level: ``fine`` (segment-segment inside a block),
    ``mid`` (block-block inside a super-block), ``coarse`` (super-super). Returns the
    positions, the level-tagged edges, and each segment's block and super-block — so
    the same read-out can be renormalized to any level."""
    M = block_rows * block_cols
    per_super = mid_group * M
    def sid(sb, mb, r, c): return sb * per_super + mb * M + r * block_cols + c
    pos, seg_block, seg_super = [], [], []
    for sb in range(n_super):
        for mb in range(mid_group):
            for r in range(block_rows):
                for c in range(block_cols):
                    pos.append((sb * dx_super + c * bs, mb * dy_mid + r * bs, z0))
                    seg_block.append(sb * mid_group + mb)          # 0 .. n_block-1
                    seg_super.append(sb)                           # 0 .. n_super-1
    edges, level = [], []
    for sb in range(n_super):
        for mb in range(mid_group):                                # fine (intra-block)
            for r in range(block_rows):
                for c in range(block_cols - 1):
                    edges.append((sid(sb, mb, r, c), sid(sb, mb, r, c + 1))); level.append("fine")
            for r in range(block_rows - 1):
                for c in range(block_cols):
                    edges.append((sid(sb, mb, r, c), sid(sb, mb, r + 1, c))); level.append("fine")
        for mb in range(mid_group - 1):                            # mid (block -> block)
            edges.append((sid(sb, mb, block_rows - 1, 0), sid(sb, mb + 1, 0, 0))); level.append("mid")
    for sb in range(n_super - 1):                                  # coarse (super -> super)
        edges.append((sid(sb, 0, 0, block_cols - 1), sid(sb + 1, 0, 0, 0))); level.append("coarse")
    return dict(pos=np.array(pos), edges=edges, level=level,
                seg_block=np.array(seg_block), seg_super=np.array(seg_super),
                n_seg=len(pos), n_block=n_super * mid_group, n_super=n_super, M=M)
# --8<-- [end:nested_spec]


def _lattice_mjcf(pos, edges, lat_stiff, link_damp, seg_damp, seg_mass, cmax, name):
    """Shared MJCF assembly: point-mass segments (3-DOF, overdamped) + one
    spring-tendon CAZ actuator per edge. Used by both builders."""
    bodies = []
    for i, (x, y, z) in enumerate(pos):
        bodies.append(
            f'    <body name="b{i}" pos="{x:.5f} {y:.5f} {z:.5f}">\n'
            f'      <joint name="jx{i}" type="slide" axis="1 0 0" damping="{seg_damp}"/>\n'
            f'      <joint name="jy{i}" type="slide" axis="0 1 0" damping="{seg_damp}"/>\n'
            f'      <joint name="jz{i}" type="slide" axis="0 0 1" damping="{seg_damp}"/>\n'
            f'      <geom type="box" size="0.045 0.045 0.02" mass="{seg_mass}" '
            f'friction="0 0 0" rgba="0.30 0.50 0.80 1"/>\n'
            f'      <site name="s{i}" pos="0 0 0" size="0.012"/>\n    </body>')
    tendons, acts = [], []
    for L, (a, b) in enumerate(edges):
        rest = float(np.linalg.norm(np.asarray(pos[a]) - np.asarray(pos[b])))
        tendons.append(
            f'    <spatial name="t{L}" stiffness="{lat_stiff}" damping="{link_damp}" '
            f'springlength="{rest:.5f}">\n'
            f'      <site site="s{a}"/>\n      <site site="s{b}"/>\n    </spatial>')
        acts.append(f'    <motor name="m{L}" tendon="t{L}" gear="1" ctrlrange="{-cmax} {cmax}"/>')
    return f"""
<mujoco model="{name}">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast">
    <flag contact="disable"/>
  </option>
  <visual><headlight diffuse="0.7 0.7 0.7" ambient="0.4 0.4 0.4"/></visual>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
{chr(10).join(bodies)}
  </worldbody>
  <tendon>
{chr(10).join(tendons)}
  </tendon>
  <actuator>
{chr(10).join(acts)}
  </actuator>
</mujoco>
"""


def build_nested_lattice_xml(spec, lat_stiff=20.0, link_damp=0.6,
                             seg_damp=4.0, seg_mass=0.05, cmax=3.0) -> str:
    """MJCF for a :func:`nested_lattice_spec` two-level lattice (blocks of lattices)."""
    return _lattice_mjcf(spec["pos"], spec["edges"], lat_stiff, link_damp,
                         seg_damp, seg_mass, cmax, f"smn_nested_{spec['n_block']}")


def build_lattice_xml(n_col=8, n_row=1, closed=False, dx=0.16, dy=0.16,
                      seg_mass=0.05, lat_stiff=20.0, link_damp=0.6,
                      seg_damp=4.0, cmax=3.0) -> str:
    """MJCF for an ``n_row x n_col`` lattice. ``n_row=1`` -> chain (a muscle);
    ``n_row=2`` -> sheet; ``n_row>=3, closed=True`` -> tube. Each segment is a
    3-DOF point mass (slide x/y/z, overdamped); each :func:`lattice_edges` edge is a
    spring-tendon CAZ (``lat_stiff``) with its own linear actuator ``m{L}``."""
    pos = lattice_positions(n_col, n_row, closed, dx, dy)
    bodies = []
    for i, (x, y, z) in enumerate(pos):
        bodies.append(
            f'    <body name="b{i}" pos="{x:.5f} {y:.5f} {z:.5f}">\n'
            f'      <joint name="jx{i}" type="slide" axis="1 0 0" damping="{seg_damp}"/>\n'
            f'      <joint name="jy{i}" type="slide" axis="0 1 0" damping="{seg_damp}"/>\n'
            f'      <joint name="jz{i}" type="slide" axis="0 0 1" damping="{seg_damp}"/>\n'
            f'      <geom type="box" size="0.05 0.05 0.02" mass="{seg_mass}" '
            f'friction="0 0 0" rgba="0.30 0.50 0.80 1"/>\n'
            f'      <site name="s{i}" pos="0 0 0" size="0.012"/>\n'
            f'    </body>')
    edges = lattice_edges(n_col, n_row, closed)
    tendons, acts = [], []
    for L, (a, b) in enumerate(edges):
        rest = float(np.linalg.norm(pos[a] - pos[b]))         # rest = initial gap
        tendons.append(
            f'    <spatial name="t{L}" stiffness="{lat_stiff}" damping="{link_damp}" '
            f'springlength="{rest:.5f}">\n'
            f'      <site site="s{a}"/>\n      <site site="s{b}"/>\n    </spatial>')
        acts.append(f'    <motor name="m{L}" tendon="t{L}" gear="1" '
                    f'ctrlrange="{-cmax} {cmax}"/>')
    bodies = "\n".join(bodies)
    tendons = "\n".join(tendons)
    acts = "\n".join(acts)
    return f"""
<mujoco model="smn_lattice_{n_row}x{n_col}">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast">
    <flag contact="disable"/>
  </option>
  <visual><headlight diffuse="0.7 0.7 0.7" ambient="0.4 0.4 0.4"/></visual>
  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
{bodies}
  </worldbody>
  <tendon>
{tendons}
  </tendon>
  <actuator>
{acts}
  </actuator>
</mujoco>
"""
