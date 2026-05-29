# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The body schema -- the single source of truth for the agent's geometry.

The SMN architecture holds that the world model is constructed *in relation to
the body geometry*: the agent knows where each of its zones sits, and places
sensations and self-motion relative to that body schema. This module is that
schema. It is used both to build the MuJoCo body (where the sites go) and by the
agent itself (what it knows about where its zones are) -- so the two can never
drift apart.

Zones in this toy 'mouse':
  - two located rear drive zones (drive_L, drive_R): pull-only forward
    modulators; together they produce locomotion (both active) and steering
    (differential). They have explicit body-frame positions.
  - a fan of whisker transducers (S) at the front, each with a body-frame
    position and a pointing angle.
  - an IMU site at the body origin for proprioception (the agent's sense of its
    own linear and angular velocity).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class MouseSchema:
    drive_offset_x: float = -0.07     # drive zones sit behind the body centre
    drive_offset_y: float = 0.05      # half the track width
    whisker_x: float = 0.10           # whiskers mounted at the front
    whisker_angles_deg: tuple = (-60, -30, 0, 30, 60)

    @property
    def drive_zones(self) -> dict[str, tuple[float, float]]:
        """name -> (x, y) body-frame position of each located drive zone."""
        return {
            "drive_L": (self.drive_offset_x, +self.drive_offset_y),
            "drive_R": (self.drive_offset_x, -self.drive_offset_y),
        }

    @property
    def whiskers(self) -> list[tuple[float, float, float]]:
        """list of (x, y, angle_rad) for each whisker transducer (body frame)."""
        return [(self.whisker_x, 0.0, float(np.radians(d)))
                for d in self.whisker_angles_deg]
