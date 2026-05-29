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


class CPG:
    """A Basal Action Pattern: an endogenous locomotor drive (baseline
    self-propulsion), optionally with a gentle gait-like oscillation. It returns
    a forward thrust magnitude; the affordance layer (HAP) gates it."""

    def __init__(self, thrust: float = 0.8, osc_amp: float = 0.0, freq: float = 1.0):
        self.thrust = thrust
        self.osc_amp = osc_amp
        self.w = 2 * np.pi * freq

    def drive(self, t: float) -> float:
        return self.thrust * (1.0 + self.osc_amp * np.sin(self.w * t))


class HAPExplorer:
    """A Haltable Action Pattern recruited by whisker affordances: cruise toward
    open space, and -- when the forward arc is blocked -- halt the drive and
    rotate in place toward the more open side until the way is clear. It thus
    interrupts and recomposes the BAP-driven locomotion on the basis of what the
    transducers sense.

    `command(dists)` returns `(heading_offset, drive_gate)`:
      heading_offset -- per-step turn command (rad; + = toward the agent's left);
      drive_gate     -- in [0, 1], multiplies the BAP thrust (0 = halt).
    """

    def __init__(self, angles_rad, d_halt: float = 0.4, d_go: float = 0.7,
                 turn: float = 0.9, steer_gain: float = 0.5, d_cap: float = 1.6,
                 wander: float = 0.05, flip_prob: float = 0.15,
                 routing: str = "flat", seed: int = 0):
        self.angles = np.asarray(angles_rad, dtype=float)
        self.d_halt = d_halt
        self.d_go = d_go
        self.turn = turn
        self.steer_gain = steer_gain
        self.d_cap = d_cap
        self.wander = wander
        self.flip_prob = flip_prob
        self.routing = routing            # "flat" | "hierarchical" -- the balance-beam topology
        self.rng = np.random.default_rng(seed)
        self.front_mask = np.abs(self.angles) <= np.radians(45) + 1e-6
        # whisker groups for hierarchical (layered) routing
        self._groups = [self.angles > np.radians(15),
                        np.abs(self.angles) <= np.radians(15),
                        self.angles < -np.radians(15)]
        self.turning = False
        self.sign = 1.0

    def _steer_offset(self, d):
        """Route whisker clearances into a steering angle. `flat`: pool all
        whiskers at once (distributed). `hierarchical`: summarize each whisker
        group first (layer 1), then combine the group summaries (layer 2)."""
        if self.routing == "flat":
            return float((self.angles * d).sum() / max(d.sum(), 1e-6))
        ga, gc = [], []
        for m in self._groups:
            if m.any():
                ga.append(float(self.angles[m].mean()))
                gc.append(float(d[m].mean()))
        ga, gc = np.array(ga), np.array(gc)
        return float((ga * gc).sum() / max(gc.sum(), 1e-6))

    def command(self, dists):
        d = np.clip(np.asarray(dists, dtype=float), 0.0, self.d_cap)
        front = float(d[self.front_mask].min())
        # enter a committed turn when the forward arc is blocked
        if not self.turning and front < self.d_halt:
            self.turning = True
            left, right = d[self.angles > 0].sum(), d[self.angles < 0].sum()
            self.sign = 1.0 if left >= right else -1.0
            if self.rng.random() < self.flip_prob:   # occasional flip breaks limit cycles
                self.sign = -self.sign
        if self.turning:
            if front > self.d_go:                     # cleared: resume cruising
                self.turning = False
            else:
                return self.sign * self.turn, 0.0     # halt and rotate in place
        # cruise: steer toward open space, via the configured routing topology
        offset = self.steer_gain * self._steer_offset(d)
        offset += self.rng.normal(0.0, self.wander)
        gate = float(np.clip((front - self.d_halt) / (self.d_go - self.d_halt), 0.0, 1.0))
        return offset, gate


class DifferentialDrive:
    """Communication board for the two located rear drive zones. It converts a
    desired (forward, turn) command into pull-only activations of the drive
    modulators, and computes the net body-frame force and z-torque from the
    zones' positions -- so locomotion and steering both emerge from the body
    geometry rather than from a central thrust."""

    def __init__(self, schema, amax: float = 1.2, turn_gain: float = 1.0):
        self.zones = schema.drive_zones
        self.amax = amax
        self.turn_gain = turn_gain

    def activations(self, forward: float, turn: float) -> dict:
        # Each drive zone is an opponent pair (a forward AND a backward puller),
        # so its net activation is signed. This is what lets the agent rotate in
        # place: drive_L backward + drive_R forward gives pure torque, no net
        # force -- impossible with forward-only thrusters.
        d = self.turn_gain * turn
        return {"drive_L": float(np.clip(forward - d, -self.amax, self.amax)),
                "drive_R": float(np.clip(forward + d, -self.amax, self.amax))}

    def wrench(self, acts: dict):
        """Net body-frame forward force Fx and z-torque tau from the located,
        pull-only forward drives (force F at (x, y) gives z-torque -y*F)."""
        Fx = float(sum(acts.values()))
        tau = float(sum(-y * acts[name] for name, (x, y) in self.zones.items()))
        return Fx, tau


class DeadReckoner:
    """Self-localization from proprioception. The agent never reads its absolute
    position; it integrates the body-frame linear velocity (velocimeter) and yaw
    rate (gyro) that it senses, building its world model in this self-estimated
    frame, anchored at its known starting pose. Estimation error accumulates --
    which is exactly the kind of thing the coupling-topology experiment probes."""

    def __init__(self, x0: float = 0.0, y0: float = 0.0, yaw0: float = 0.0):
        self.x, self.y, self.yaw = x0, y0, yaw0

    def update(self, vx_body: float, vy_body: float, wz: float, dt: float):
        self.yaw += wz * dt
        c, s = np.cos(self.yaw), np.sin(self.yaw)
        self.x += (vx_body * c - vy_body * s) * dt
        self.y += (vx_body * s + vy_body * c) * dt
        return self.x, self.y, self.yaw
