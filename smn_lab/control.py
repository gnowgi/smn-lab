# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""SMN control layer for the embodied bench.

These classes implement components of the Sensation Modulating Network
architecture (Nagarjuna & Karnam, arXiv:2605.26856) as controllers that drive
and read a physical MuJoCo body:

- OpponentBoard        -- a zone's communication board: routes a desired
                          modulation into pull-only antagonist activations.
- ReafferencePredictor -- a forward model keyed on the agent's own state; its
                          residual is the reafference signal that separates
                          self-caused from world-caused sensory change.

Keeping these in the control layer (rather than in MuJoCo physics) is deliberate:
the modulatory coupling -- the "balance beam" -- is the experiment's independent
variable, and lives here where it can be swapped (layered/distributed, +/-BAP,
+/-HAP).
"""
from __future__ import annotations
import numpy as np


class OpponentBoard:
    """Communication board for one CAZ: convert a desired joint torque into
    pull-only antagonist activations (a_right, a_left).

    A PD law on the commanded angle produces a desired torque; positive torque
    recruits the 'right' puller, negative the 'left'. `cocontraction` adds a
    tonic antagonist tone (a minimal stand-in for BAP-like baseline drive).
    """

    def __init__(self, kp: float = 3.0, kd: float = 0.3,
                 cmax: float = 1.5, cocontraction: float = 0.0):
        self.kp = kp
        self.kd = kd
        self.cmax = cmax
        self.coc = cocontraction

    def commands(self, theta, theta_dot, theta_cmd, theta_dot_cmd):
        tau = self.kp * (theta_cmd - theta) + self.kd * (theta_dot_cmd - theta_dot)
        a_r = float(np.clip(tau, 0.0, self.cmax))
        a_l = float(np.clip(-tau, 0.0, self.cmax))
        if self.coc:
            a_r = min(self.cmax, a_r + self.coc)
            a_l = min(self.cmax, a_l + self.coc)
        return a_r, a_l, tau


class ReafferencePredictor:
    """Forward model keyed on self-state (yaw angle).

    During a self-motion learning phase the agent observes, for each heading,
    the whisker reading produced by its *own* movement in a static world, and
    learns the contingency r = g(theta) as a binned running mean. Thereafter it
    predicts the expected reading from efference/proprioception alone, and the
    residual (actual - predicted) is the reafference signal:

        ~ sensor noise floor  for self-caused change (world static)
        >> noise floor        for world-caused change (exafference)

    This is the embodied form of Register 3 (reafference: self vs world).
    """

    def __init__(self, n_bins: int = 72, theta_range=(-np.pi, np.pi)):
        self.n_bins = n_bins
        self.lo, self.hi = theta_range
        self.sum = np.zeros(n_bins)
        self.cnt = np.zeros(n_bins)
        self._global = None

    def _bin(self, theta: float) -> int:
        # wrap to [lo, hi)
        span = self.hi - self.lo
        x = (theta - self.lo) % span
        return min(self.n_bins - 1, int(self.n_bins * x / span))

    def update(self, theta: float, reading: float) -> None:
        b = self._bin(theta)
        self.sum[b] += reading
        self.cnt[b] += 1
        self._global = None  # invalidate cache

    def predict(self, theta: float) -> float:
        b = self._bin(theta)
        if self.cnt[b] > 0:
            return self.sum[b] / self.cnt[b]
        # fall back to the global learned mean if this heading was never seen
        if self._global is None:
            seen = self.cnt > 0
            self._global = (self.sum[seen].sum() / self.cnt[seen].sum()
                            if seen.any() else 0.0)
        return self._global

    def residual(self, theta: float, reading: float) -> float:
        return reading - self.predict(theta)
