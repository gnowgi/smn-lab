# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""smn_lab — an embodied, configurable experimental bench for the
Sensation Modulating Network (SMN) architecture, built on MuJoCo.

The control architecture the SMN specifies drives a physical body in a physics
world, so the architecture's predicted empirical contrasts (its *registers*) can
be reproduced from real sensorimotor engagement, and so the modulatory coupling
topology (the "balance beam") can be varied as an experimental independent
variable.

Architecture reference:
  Nagarjuna, G. & D. Karnam. The Sensation Modulating Network.
  arXiv:2605.26856 — https://arxiv.org/abs/2605.26856
"""
__all__ = ["model", "control"]
