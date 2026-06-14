# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Virtual scalar fields over the arena (chemical / thermal).

MuJoCo simulates rigid-body mechanics, contacts, and actuators -- it does **not**
simulate diffusion or temperature, so there is no native chemical or thermal
sensor. Per the engine boundary (``design/engine_boundary.md``), distal/field
modalities are therefore *derived bench-side* from geometry: the engine gives a
sensor site's world position; the bench evaluates the field there.

This keeps the field fully under experimental control -- you place the sources,
set their spread, hold the world constant -- which is exactly what the
differentiation-field experiments need. A field is a sum of Gaussian sources; the
distributed bilateral strips read ``sample()`` at their site positions.
"""
from __future__ import annotations
import numpy as np


class ScalarField:
    """A sum of Gaussian sources over the x-y plane.

    sources: iterable of (x, y, amplitude, sigma). ``sample`` reads one point,
    ``sample_xy`` a batch, ``grid`` returns a meshgrid for plotting.
    """

    def __init__(self, sources):
        self.sources = [tuple(map(float, s)) for s in sources]

    def sample(self, x: float, y: float) -> float:
        v = 0.0
        for sx, sy, amp, sig in self.sources:
            r2 = (x - sx) ** 2 + (y - sy) ** 2
            v += amp * np.exp(-r2 / (2.0 * sig * sig))
        return float(v)

    def sample_xy(self, pts) -> np.ndarray:
        pts = np.asarray(pts, dtype=float).reshape(-1, 2)
        return np.array([self.sample(x, y) for x, y in pts])

    def grid(self, xlim, ylim, n: int = 120):
        xs = np.linspace(xlim[0], xlim[1], n)
        ys = np.linspace(ylim[0], ylim[1], n)
        X, Y = np.meshgrid(xs, ys)
        Z = np.zeros_like(X)
        for sx, sy, amp, sig in self.sources:
            Z += amp * np.exp(-((X - sx) ** 2 + (Y - sy) ** 2) / (2.0 * sig * sig))
        return X, Y, Z

    def nearest_source(self):
        """The (x, y) of the strongest source -- a convenient 'goal' marker."""
        if not self.sources:
            return (0.0, 0.0)
        sx, sy, amp, sig = max(self.sources, key=lambda s: s[2])
        return (sx, sy)
