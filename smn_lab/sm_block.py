# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The canonical Sensation Modulator block (preprint v3, §3.3–3.5), built from MuJoCo constructors.

v3 asks two things of the elastic substrate, and they are different physics:

* **§3.5, text** — each Sensation Modulator is "an active contractile element in series with a
  passive elastic one" (a muscle–tendon unit);
* **Eq. 3** — the joint carries a passive restoring term ``k (q − q0)``.

A force-producing contractile element in series with a spring supplies **no** restoring
stiffness: the series spring transmits whatever force the contractile element makes, wherever the
joint is (see ``tests/test_sm_block.py::test_series_spring_alone_does_not_restore``). So the block
is the classical three-element (Hill-type) muscle:

* **CE** — contractile element: a pull-only force ``F = a · F_max`` (motor on an internal slide
  DOF ``x``, ``x`` = CE shortening), with linear viscosity ``b_ce`` standing in for force–velocity;
* **SEE** — series elastic element (tendon): a *fixed* tendon of length ``L = c·q + x`` with
  stiffness ``k_see`` and a dead band ``springlength="-10 0"``, so it pulls when stretched
  (``L > 0``) and goes slack otherwise — pull-only, as v3 Eq. 1 requires;
* **PEE** — parallel elastic element: the joint's own stiffness ``k_pee``, i.e. v3 Eq. 3's
  ``k (q − q0)``.

In the differentiated limit (v3 §3.4) one joint carries one opponent pair: a flexor (``p``,
muscle–tendon length ``ℓ0 − r q``) and an extensor (``n``, ``ℓ0 + r q``), with moment arm ``r``.

Afferents are read from the same tissue (v3 Eq. 2, ``s = Ψ(q, q̇, F)``): the SEE length
(→ tendon tension, a tendon-organ signal), the CE force, and the joint angle/velocity (the
muscle–tendon length and its rate, a spindle-like signal).

Idealizations (declared): CE has no force–length curve and only linear viscosity; the moment arm is
constant; the CE slide DOF carries a small numerical mass ``m_ce``. The body itself is the bench
crawler (``smn_lab.crawler.build_crawler_xml``) with its ideal torque motors replaced by the block.
"""
from __future__ import annotations
import re
import numpy as np

from smn_lab.crawler import build_crawler_xml

# Defaults chosen so the block matches the bench's torque motors at full drive:
# r · F_max = 0.025 m × 5 N = 0.125 N·m = gear 0.05 × ctrl 2.5.  k_see gives a tendon stretch of
# F_max / k_see = 2.8 mm at full force, i.e. 0.11 rad of joint-equivalent compliance per muscle.
R_ARM = 0.025
F_MAX = 5.0
K_SEE = 1800.0
B_CE = 2.0
M_CE = 1e-3
CE_RANGE = (-0.02, 0.05)


def build_sm_chain_xml(n_seg: int = 3, k_see: float = K_SEE, k_pee: float = 0.0,
                       r: float = R_ARM, f_max: float = F_MAX, b_ce: float = B_CE,
                       m_ce: float = M_CE, **crawler_kw) -> str:
    """MJCF for an axial chain whose every joint is driven by one opponent pair of SM blocks.

    ``crawler_kw`` passes through to ``build_crawler_xml`` (habitat, walls, objects, touch,
    damping, bend limit …); its ``joint_stiffness`` is set from ``k_pee``.
    Names: CE motor ``ce_j{k}_{p|n}``, CE DOF ``x_j{k}_{p|n}``, SEE tendon ``see_j{k}_{p|n}``,
    sensors ``seelen_…`` (tendon length) and ``cef_…`` (CE force).
    """
    xml = build_crawler_xml(n_seg=n_seg, joint_stiffness=k_pee, **crawler_kw)
    xml = re.sub(r"\s*<actuator>.*?</actuator>", "", xml, flags=re.S)       # drop torque motors
    lo, hi = CE_RANGE
    for k in range(n_seg - 1):                     # joint j{k+1}'s muscles live in parent seg k
        ce = "".join(
            f'\n      <body name="ce_j{k + 1}_{s}" pos="0 0 0">'
            f'<inertial pos="0 0 0" mass="{m_ce}" diaginertia="1e-8 1e-8 1e-8"/>'
            f'<joint name="x_j{k + 1}_{s}" type="slide" axis="1 0 0" damping="{b_ce}" '
            f'range="{lo} {hi}"/></body>' for s in "pn")
        xml, n = re.subn(rf'(<geom name="seg{k}_geom"[^>]*/>)', lambda mt: mt.group(1) + ce, xml, count=1)
        assert n == 1, f"segment {k} geom not found"
    ten, act, sen = [], [], []
    for j in range(1, n_seg):
        for s, c in (("p", -r), ("n", +r)):        # flexor: ℓ0 − r q ; extensor: ℓ0 + r q
            ten.append(f'    <fixed name="see_j{j}_{s}" stiffness="{k_see}" springlength="-10 0">'
                       f'<joint joint="j{j}" coef="{c}"/><joint joint="x_j{j}_{s}" coef="1"/></fixed>')
            act.append(f'    <motor name="ce_j{j}_{s}" joint="x_j{j}_{s}" gear="1" ctrlrange="0 {f_max}"/>')
            sen.append(f'    <tendonpos name="seelen_j{j}_{s}" tendon="see_j{j}_{s}"/>\n'
                       f'    <actuatorfrc name="cef_j{j}_{s}" actuator="ce_j{j}_{s}"/>')
    block = ("  <tendon>\n" + "\n".join(ten) + "\n  </tendon>\n  <actuator>\n" + "\n".join(act) +
             "\n  </actuator>\n  <sensor>\n" + "\n".join(sen))
    return xml.replace("  <sensor>", block, 1)


class SMChain:
    """Index helper for a compiled SM chain: actuator ids, joint addresses, afferent read-outs."""

    def __init__(self, model, n_seg: int, k_see: float = K_SEE, f_max: float = F_MAX):
        m = model
        self.n, self.k_see, self.f_max = n_seg, k_see, f_max
        J = range(1, n_seg)
        self.seg = [m.body(f"seg{k}").id for k in range(n_seg)]
        self.jq = [m.jnt_qposadr[m.joint(f"j{j}").id] for j in J]
        self.jv = [m.jnt_dofadr[m.joint(f"j{j}").id] for j in J]
        self.ap = [m.actuator(f"ce_j{j}_p").id for j in J]
        self.an = [m.actuator(f"ce_j{j}_n").id for j in J]
        self.tp = [m.tendon(f"see_j{j}_p").id for j in J]
        self.tn = [m.tendon(f"see_j{j}_n").id for j in J]

    def set_forces(self, data, f_p, f_n):
        """CE forces in newtons (clipped to [0, F_max] by ctrlrange)."""
        data.ctrl[self.ap] = f_p; data.ctrl[self.an] = f_n

    def set_from_board(self, data, a_p, a_n, cmax: float = 2.5):
        """Map OpponentBoard activations (0..cmax, as sent to the bench's torque motors) onto CE
        force: F = (a / cmax) · F_max, so full drive gives the same peak torque as before."""
        s = self.f_max / cmax
        self.set_forces(data, np.asarray(a_p) * s, np.asarray(a_n) * s)

    def tendon_tension(self, data):
        """Afferent: SEE tension (tendon-organ signal), flexor and extensor, per joint."""
        L = data.ten_length
        tp = self.k_see * np.maximum(0.0, L[self.tp]); tn = self.k_see * np.maximum(0.0, L[self.tn])
        return tp, tn

    def joint_state(self, data):
        return data.qpos[self.jq].copy(), data.qvel[self.jv].copy()
