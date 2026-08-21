# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Experimenter-side network-controllability analysis -- NOT the agent's computation.

For payoff 3 (morphology-dependent control). Given a body's CAZ coupling graph, how
many *driver* zones must a controller inject drive at to steer the whole body?

Exact controllability (Yuan, Zhao, Di, Wang & Lai, Nat. Commun. 2013): for a network
with diffusive (Laplacian) coupling L, the minimum number of driver nodes is

    N_D = max_i  (geometric multiplicity of eigenvalue lambda_i of L),

and a minimal driver set is any set that makes every eigenspace controllable (the PBH
eigenvector test). For a SYMMETRIC coupling matrix geometric = algebraic multiplicity,
so N_D is just the largest eigenvalue multiplicity -- which is set by the body's
SYMMETRY: interchangeable arms give degenerate eigenvalues (N_D > 1), and breaking the
symmetry lifts the degeneracy (N_D -> 1).

These are GLOBAL spectral computations over the whole coupling matrix -- an analyst's
tool. They are deliberately kept OUT of ``smn_lab.network`` (the agent's local
per-zone operators), the same model/measurement firewall the rest of the bench keeps.
"""
from __future__ import annotations
import numpy as np


def graph_laplacian(W: np.ndarray) -> np.ndarray:
    """Combinatorial Laplacian L = D - W of a symmetric non-negative coupling W."""
    W = np.asarray(W, float)
    W = 0.5 * (W + W.T)
    np.fill_diagonal(W, 0.0)
    return np.diag(W.sum(1)) - W


def _eigenspaces(L: np.ndarray, tol: float = 1e-6):
    """Eigenvalues/vectors of a symmetric L, with indices grouped into eigenspaces by
    near-equal eigenvalue (relative tolerance ``tol``)."""
    w, V = np.linalg.eigh(L)
    groups, cur = [], [0]
    for i in range(1, len(w)):
        if abs(w[i] - w[cur[-1]]) <= tol * max(1.0, abs(w[i])):
            cur.append(i)
        else:
            groups.append(cur); cur = [i]
    groups.append(cur)
    return w, V, groups


def exact_controllability_nd(W: np.ndarray, tol: float = 1e-6) -> int:
    """N_D = the largest eigenvalue multiplicity of the coupling Laplacian."""
    _, _, groups = _eigenspaces(graph_laplacian(W), tol)
    return max(len(g) for g in groups)


def is_controllable(W: np.ndarray, drivers, tol: float = 1e-6) -> bool:
    """PBH eigenvector test: driving the node set ``drivers`` makes the diffusively
    coupled network controllable iff, for every eigenspace, the rows of its eigenvector
    basis indexed by the drivers span the eigenspace (rank == multiplicity)."""
    L = graph_laplacian(W)
    _, V, groups = _eigenspaces(L, tol)
    D = np.asarray(list(drivers), int)
    if D.size == 0:
        return L.shape[0] == 0
    for g in groups:
        Vg = V[:, g]                                   # n x mult eigenspace basis
        if np.linalg.matrix_rank(Vg[D, :], tol=1e-6) < len(g):
            return False
    return True


def min_driver_set(W: np.ndarray, tol: float = 1e-6):
    """A provably minimal driver set. Its size equals :func:`exact_controllability_nd`
    (the theoretical minimum, Yuan et al.), so we search combinations *at that size* and
    return the first controllable one -- guaranteed to exist. Returns driver indices."""
    from itertools import combinations
    n = W.shape[0]
    nd = exact_controllability_nd(W, tol)
    for combo in combinations(range(n), nd):
        if is_controllable(W, combo, tol):
            return list(combo)
    return list(range(nd))                                  # fallback (should not trigger)
