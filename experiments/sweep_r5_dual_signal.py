# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""R5 -- intra-body dual-signal residual: self-contact is a STRUCTURAL signature.

Register 5 of the preprint. Two CAZs of one SMN whose mechanical states co-determine
a shared sensory substrate are in *self-contact*: what CAZ_y's transducer reads
depends on where the partner CAZ_x is. Because the partner's configuration theta_x
is available through cross-zone broadcast, the reafference residual is fully
explained by the partner-as-stimulus form -- when the residual is regressed against

    Delta_shat = I [ exp(-(theta_y - theta_x)^2 / s^2) - exp(-(theta_y - phi0)^2 / s^2) ]

(phi0 the cold-start estimate), R^2 -> 1. For a DECOUPLED control, where the same
transducer reads an exogenous stimulus unrelated to the partner CAZ, the same
regression gives R^2 -> 0. The signature is STRUCTURAL (a fit quality), not a
magnitude difference -- so it is diagnostic and not confounded by noise level.

Pre-registration
----------------
- Hypothesis: in self-contact the residual is fully explained by the
  partner-as-stimulus form (R^2 -> 1); decoupled, it is not (R^2 -> 0).
- Order parameter: R^2 of the residual against the partner-as-stimulus regressor.
- Matched foil: decoupled (exogenous stimulus of the same magnitude & noise).
- Pass: R^2_self ~ 1  and  R^2_decoupled ~ 0.
- Falsify: R^2_self not >> R^2_decoupled -> no structural dual-signal.

Run:  ../.venv/bin/python sweep_r5_dual_signal.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DT = 0.002
T = 40.0
I0, SIGMA, PHI0 = 1.0, 0.35, 0.0     # receptive-field intensity, width, cold-start
SENSOR_NOISE = 0.02
SEEDS = range(6)


def build_two_caz_xml():
    return """
<mujoco model="two_caz">
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <worldbody>
    <body name="bx" pos="0 0 0.4">
      <joint name="jx" type="hinge" axis="0 0 1" damping="0.08" range="-60 60"/>
      <geom type="capsule" fromto="0 0 0 0.18 0 0" size="0.02" mass="0.1"/>
      <body name="by" pos="0.18 0 0">
        <joint name="jy" type="hinge" axis="0 0 1" damping="0.08" range="-60 60"/>
        <geom type="capsule" fromto="0 0 0 0.18 0 0" size="0.02" mass="0.1"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="mx" joint="jx" gear="1" ctrlrange="-2 2"/>
    <motor name="my" joint="jy" gear="1" ctrlrange="-2 2"/>
  </actuator>
</mujoco>
"""


def rf(theta_y, phi):
    """Gaussian receptive field: what CAZ_y reads when the stimulus is at phi."""
    return I0 * np.exp(-((theta_y - phi) ** 2) / SIGMA ** 2)


def run(seed):
    """Return theta_x, theta_y trajectories + an independent exogenous phi."""
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_two_caz_xml())
    data = mujoco.MjData(model)
    qx, qy = model.jnt_qposadr[model.joint("jx").id], model.jnt_qposadr[model.joint("jy").id]
    mx, my = model.actuator("mx").id, model.actuator("my").id
    n = int(T / DT)
    tau = np.zeros(2); tc, sig = 0.3, 3.0
    phi_exo = 0.0                              # exogenous stimulus (independent OU)
    THx, THy, PHI = np.empty(n), np.empty(n), np.empty(n)
    for i in range(n):
        tau += (-tau / tc) * DT + sig * np.sqrt(DT) * rng.standard_normal(2)
        data.ctrl[mx], data.ctrl[my] = float(np.clip(tau[0], -2, 2)), float(np.clip(tau[1], -2, 2))
        phi_exo += (-phi_exo / tc) * DT + 0.9 * np.sqrt(DT) * rng.standard_normal()
        mujoco.mj_step(model, data)
        THx[i], THy[i], PHI[i] = data.qpos[qx], data.qpos[qy], phi_exo
    return THx, THy, PHI


def r2_dual_signal(theta_x, theta_y, phi_stim, rng):
    """R^2 of the reafference residual against the partner-as-stimulus regressor."""
    s = rf(theta_y, phi_stim) + rng.normal(0, SENSOR_NOISE, size=theta_y.shape)   # actual reading
    s_cold = rf(theta_y, PHI0)                          # cold-start prediction
    r = s - s_cold                                     # reafference residual
    X = rf(theta_y, theta_x) - rf(theta_y, PHI0)        # partner-as-stimulus form (eq. sig5)
    # OLS r ~ a*X + b ; R^2
    A = np.vstack([X, np.ones_like(X)]).T
    coef, *_ = np.linalg.lstsq(A, r, rcond=None)
    resid = r - A @ coef
    ss_res = float(resid @ resid); ss_tot = float(((r - r.mean()) ** 2).sum())
    return 1.0 - ss_res / (ss_tot + 1e-12)


def main():
    figdir = os.path.join(os.path.dirname(__file__), "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    self_r2, dec_r2 = [], []
    for s in SEEDS:
        THx, THy, PHI = run(s)
        rng = np.random.default_rng(1000 + s)
        self_r2.append(r2_dual_signal(THx, THy, THx, rng))     # self-contact: phi = theta_x
        dec_r2.append(r2_dual_signal(THx, THy, PHI, rng))      # decoupled: phi = exogenous
    self_r2, dec_r2 = np.array(self_r2), np.array(dec_r2)

    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.bar([0, 1], [self_r2.mean(), dec_r2.mean()],
           yerr=[self_r2.std(), dec_r2.std()], capsize=5,
           color=["#2c6fbb", "#c0672a"], width=0.6)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["self-contact\n($\\phi=\\theta_x$)",
                                               "decoupled\n(exogenous $\\phi$)"])
    ax.set_ylabel("$R^2$ of residual vs partner-as-stimulus form")
    ax.set_ylim(0, 1.05)
    ax.set_title("R5 -- the dual-signal residual is a STRUCTURAL signature\n"
                 "self-contact $R^2\\to1$, decoupled $R^2\\to0$ (not a magnitude difference)",
                 fontsize=9.5)
    for x, v in zip([0, 1], [self_r2.mean(), dec_r2.mean()]):
        ax.text(x, v + 0.02, f"{v:.2f}", ha="center", fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = os.path.join(figdir, "sweep_r5_dual_signal.png")
    fig.savefig(out, dpi=130)
    print(f"[R5] R^2 self-contact = {self_r2.mean():.3f} +/- {self_r2.std():.3f}")
    print(f"[R5] R^2 decoupled    = {dec_r2.mean():.3f} +/- {dec_r2.std():.3f}")
    print(f"[R5] verdict: {'PASS' if self_r2.mean() > 0.9 and dec_r2.mean() < 0.2 else 'CHECK'}")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
