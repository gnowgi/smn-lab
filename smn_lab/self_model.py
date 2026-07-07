# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Recovering the self-model: a body's own connectivity graph, from movement.

Canonical, body-agnostic version of the read-out demonstrated in
``experiments/branched_self_model.py``. Each joint (a CAZ) is the hinge between
exactly two segments, and its own angular velocity IS their yaw-rate difference
(``JV = omega_child - omega_parent``). So a joint finds the two segments it
couples as the one it co-rotates with (its strongest positive correlate) and the
one it counter-rotates with (its strongest negative correlate). The union of every
joint's edge is the body graph -- a chain, a tree, whatever the body is -- recovered
locally, with no zone ever reading the whole body.

Inputs are two time-by-index arrays gathered while the body moves:
  JV[t, j]    -- each joint's own angular velocity;
  OMEGA[t, s] -- each segment's world yaw-rate.
"""
from __future__ import annotations
import numpy as np


def coupling(JV, OMEGA):
    """C[joint, segment] = corr(joint j's angular velocity, segment s's yaw-rate).
    Each joint's top positive column is its child, top negative its parent."""
    J = (JV - JV.mean(0)) / (JV.std(0) + 1e-9)
    O = (OMEGA - OMEGA.mean(0)) / (OMEGA.std(0) + 1e-9)
    return (J.T @ O) / len(JV)


def recover_edges(C):
    """Each joint's edge = (co-rotating segment, counter-rotating segment)."""
    return [(min(int(np.argmax(C[j])), int(np.argmin(C[j]))),
             max(int(np.argmax(C[j])), int(np.argmin(C[j]))))
            for j in range(C.shape[0])]


def edge_strength(C):
    """Per-joint coupling magnitude, normalized to [0, 1] -- for edge width."""
    s = np.array([abs(C[j].max()) + abs(C[j].min()) for j in range(C.shape[0])])
    return (s - s.min()) / (np.ptp(s) + 1e-9)


def degrees(edges):
    d = {}
    for a, b in edges:
        d[a] = d.get(a, 0) + 1; d[b] = d.get(b, 0) + 1
    return d


def branch_node(edges):
    """The highest-degree node if it is an actual branch point (degree >= 3),
    else None (a chain has no branch point)."""
    d = degrees(edges)
    if not d:
        return None
    n = max(d, key=d.get)
    return n if d[n] >= 3 else None
