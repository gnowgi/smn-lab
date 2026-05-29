# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The constructed world model.

As the agent moves, each whisker hit is placed in world coordinates from the
agent's own pose (which it knows -- proprioception) plus the known whisker angle
and the measured distance. Accumulated, these hits are the "picture" the agent
builds of its world from action and modulated sensation -- a snapshot assembled
through the stream of its own exploration.
"""
from __future__ import annotations
import numpy as np


class OccupancyMap:
    """A 2D occupancy grid accumulated from whisker hit points."""

    def __init__(self, half: float, res: float = 0.04):
        self.half = half
        self.res = res
        self.n = int(2 * half / res)
        self.grid = np.zeros((self.n, self.n), dtype=np.int32)
        self.pts: list[tuple[float, float]] = []

    def _idx(self, x: float, y: float):
        return int((x + self.half) / self.res), int((y + self.half) / self.res)

    def add_hit(self, x: float, y: float) -> None:
        if abs(x) < self.half and abs(y) < self.half:
            i, j = self._idx(x, y)
            if 0 <= i < self.n and 0 <= j < self.n:
                self.grid[i, j] += 1
                self.pts.append((x, y))

    def discovered_mask(self, thresh: int = 1) -> np.ndarray:
        return self.grid >= thresh

    def score(self, truth_mask: np.ndarray):
        """Coverage = fraction of true surface cells discovered; precision =
        fraction of discovered cells that are true surface."""
        disc = self.discovered_mask()
        inter = np.logical_and(disc, truth_mask).sum()
        coverage = inter / max(int(truth_mask.sum()), 1)
        precision = inter / max(int(disc.sum()), 1)
        return float(coverage), float(precision)


def rasterize_truth(half: float, res: float, arena_half: float,
                    objects=(), band: float = 0.06) -> np.ndarray:
    """Ground-truth surface occupancy (inner wall faces + object footprints) on
    the same grid as OccupancyMap, dilated by `band` for fair comparison."""
    n = int(2 * half / res)
    xs = (np.arange(n) + 0.5) * res - half
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    ew = (np.abs(np.abs(X) - arena_half) <= band) & (np.abs(Y) <= arena_half)
    ns = (np.abs(np.abs(Y) - arena_half) <= band) & (np.abs(X) <= arena_half)
    m = ew | ns
    for o in objects:
        if o["type"] == "cyl":
            m |= ((X - o["x"]) ** 2 + (Y - o["y"]) ** 2) <= (o["r"] + band) ** 2
        else:  # box
            m |= (np.abs(X - o["x"]) <= o["hx"] + band) & (np.abs(Y - o["y"]) <= o["hy"] + band)
    return m


def surface_samples(arena_half: float, objects=(), step: float = 0.03) -> np.ndarray:
    """Dense sample points along the true surfaces (inner wall faces + object
    outlines). Used as ground truth for a banding-free, point-based score."""
    pts = []
    s = np.arange(-arena_half, arena_half + step, step)
    for c in (-arena_half, arena_half):
        for v in s:
            pts.append((c, v))   # E / W walls
            pts.append((v, c))   # N / S walls
    for o in objects:
        if o["type"] == "cyl":
            for th in np.arange(0, 2 * np.pi, step / o["r"]):
                pts.append((o["x"] + o["r"] * np.cos(th), o["y"] + o["r"] * np.sin(th)))
        else:
            for v in np.arange(-o["hx"], o["hx"] + step, step):
                pts.append((o["x"] + v, o["y"] - o["hy"]))
                pts.append((o["x"] + v, o["y"] + o["hy"]))
            for v in np.arange(-o["hy"], o["hy"] + step, step):
                pts.append((o["x"] - o["hx"], o["y"] + v))
                pts.append((o["x"] + o["hx"], o["y"] + v))
    return np.array(pts)


def coverage_precision(hit_pts, truth_pts, eps: float = 0.06, max_hits: int = 8000):
    """coverage = fraction of true-surface points within eps of some hit;
    precision = fraction of hits within eps of some true-surface point."""
    H = np.asarray(hit_pts, dtype=float)
    T = np.asarray(truth_pts, dtype=float)
    if len(H) == 0:
        return 0.0, 0.0
    if len(H) > max_hits:
        H = H[np.random.default_rng(0).choice(len(H), max_hits, replace=False)]

    def frac_within(A, B, eps):
        hit = 0
        for i in range(0, len(A), 512):
            d2 = ((A[i:i + 512, None, :] - B[None, :, :]) ** 2).sum(-1)
            hit += int((d2.min(1) <= eps * eps).sum())
        return hit / len(A)

    return float(frac_within(T, H, eps)), float(frac_within(H, T, eps))


def dump_npz(path: str, **arrays) -> None:
    """Persist run data (point clouds, trajectories, metrics) for reanalysis.
    A lab keeps its raw data; coverage/precision are derived, not the record."""
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    np.savez_compressed(path, **arrays)
