# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Prediction 3 -- antagonistic benefits. Pre-registered (test plan).

SMN preprint, Predictions & Testable Claims #3: "Perturbation studies should
reveal faster error correction when antagonistic tension is preserved vs
pharmacologically reduced." This is the equilibrium-point / impedance-control idea
Friston connected to (Latash, EPH): co-contraction stiffens the joint, steepening
the basin around the equilibrium point.

MECHANISM + DECLARED ADJUSTMENT (important, honest). The bench's existing
`OpponentBoard.cocontraction` adds tonic activation to two pull-only FORCE motors
(gears +1/-1); these sum to ZERO net torque and add NO stiffness -- co-contraction
as previously implemented is inert for impedance. So we add a muscle-impedance
model, faithful to the preprint (hm-new-plan: the modulator's "efferent modulation
signal adjusts the impedance ... of the antagonistic bundles") and to textbook
biomechanics:

  - co-contraction `coc` produces INTRINSIC, ZERO-DELAY stiffness & damping
    proportional to coc (active muscle is stiffer): tau_imp = -K*coc*theta
    - B*coc*theta_dot, applied from the CURRENT state (no delay);
  - neural feedback (kp,kd) acts with a realistic DELAY (a reflex loop);
  - tonic co-contraction costs ENERGY (both pullers active) with no net torque.

The genuine, non-trivial claim is therefore: intrinsic (zero-delay) co-contraction
stiffness rejects a perturbation faster than DELAYED feedback can -- at an energy
cost. Not a free lunch; a tradeoff.

Pre-registration:
- Hypothesis: higher antagonist co-contraction -> smaller peak deviation, smaller
  integrated error (IAE), faster settling after a perturbation, at higher energy
  cost. The benefit is larger for larger/faster perturbations (where delay hurts).
- Order parameters: peak deviation, IAE, settling time, energy.
- Foil: coc = 0 (the preprint's "pharmacologically reduced" tension).
- Pass: peak deviation & IAE decrease with coc; energy increases (a tradeoff);
  benefit larger for the large perturbation.
- Falsify: error metrics flat across coc -> no antagonistic benefit (the impedance
  does not help, or delay is not limiting).

Outputs: data/pred3_antagonistic/, samples/.../summary.csv,
figures/sweep_pred3_antagonistic.png
Run:  ../.venv/bin/python sweep_pred3_antagonistic.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.sweep import run_sweep, export_curated

DT = 0.002
T_SETTLE = 0.5               # let it sit at the set-point
T_PERT = 0.5                # perturbation onset (after settle)
PULSE = 0.015               # perturbation duration (s)
T_WIN = 1.5                 # response window measured after onset
T_END = T_SETTLE + T_WIN
DELAY = 20                  # neural feedback delay (steps) = 40 ms
KP, KD = 0.30, 0.010        # delayed reflex gains
K_MUSCLE, B_MUSCLE = 1.0, 0.05   # intrinsic stiffness/damping per unit co-contraction
CMAX = 3.0
PROPRIO_NOISE = 0.01        # noise on the sensed angle/rate (gives seed spread)
TOL = 0.01                  # settling tolerance (rad)
COCS = [0.0, 0.15, 0.3, 0.6, 1.2]
PERTS = {"small": 0.05, "large": 0.15}   # perturbation torque (N·m)
SEEDS = list(range(6))


def build_limb_xml():
    return """
<mujoco model="antagonist_limb">
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <worldbody>
    <body name="limb" pos="0 0 0.4">
      <joint name="j" type="hinge" axis="0 0 1" damping="0.005"/>
      <geom type="capsule" fromto="0 0 0 0.2 0 0" size="0.02" mass="0.1"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="m_p" joint="j" gear="1"  ctrlrange="0 3"/>
    <motor name="m_n" joint="j" gear="-1" ctrlrange="0 3"/>
  </actuator>
  <sensor>
    <jointpos name="ang" joint="j"/>
    <jointvel name="vel" joint="j"/>
  </sensor>
</mujoco>
"""


def run_one(params, seed):
    coc = float(params["coc"]); P = float(PERTS[params["pert"]])
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_limb_xml())
    data = mujoco.MjData(model)
    jid = model.joint("j").id
    qadr, vadr = model.jnt_qposadr[jid], model.jnt_dofadr[jid]
    ap, an = model.actuator("m_p").id, model.actuator("m_n").id

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    hist = []                                  # (theta, theta_dot) for delayed feedback
    log = {k: [] for k in ("t", "theta", "energy_rate")}
    for i in range(n):
        t = i * DT
        th = float(data.qpos[qadr]); thd = float(data.qvel[vadr])
        th_s = th + rng.normal(0, PROPRIO_NOISE)         # sensed (noisy)
        thd_s = thd + rng.normal(0, PROPRIO_NOISE * 10)
        hist.append((th_s, thd_s))
        th_d, thd_d = hist[-DELAY] if len(hist) > DELAY else (0.0, 0.0)

        tau_fb = KP * (0.0 - th_d) + KD * (0.0 - thd_d)         # DELAYED reflex
        tau_imp = -K_MUSCLE * coc * th - B_MUSCLE * coc * thd   # ZERO-DELAY impedance
        tau = tau_fb + tau_imp
        a_p = min(CMAX, max(0.0, tau) + coc)                    # +tonic co-contraction
        a_n = min(CMAX, max(0.0, -tau) + coc)
        data.ctrl[ap], data.ctrl[an] = a_p, a_n

        # perturbation: an external torque pulse the limb did not produce
        in_pulse = T_PERT <= t < (T_PERT + PULSE)
        data.qfrc_applied[vadr] = P if in_pulse else 0.0
        mujoco.mj_step(model, data)

        log["t"].append(t)
        log["theta"].append(float(data.qpos[qadr]))
        log["energy_rate"].append(a_p ** 2 + a_n ** 2)
    for k in log:
        log[k] = np.array(log[k])
    return log


def summarize(log, params, seed):
    t = log["t"]; th = np.abs(log["theta"])
    w = t >= T_PERT                                  # response window
    tw, thw = t[w], th[w]
    peak = float(thw.max())
    iae = float(np.trapezoid(thw, tw))
    energy = float(np.trapezoid(log["energy_rate"][w], tw))
    # settling time: last moment it exceeds TOL, measured from onset
    over = np.where(thw > TOL)[0]
    settle = float(tw[over[-1]] - T_PERT) if len(over) else 0.0
    return {"peak_dev": peak, "iae": iae, "settle_time": settle, "energy": energy}


def plot(summary, out):
    cocs = np.array(sorted(summary["coc"].unique()))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    pert_colors = {"small": "#2a8a4a", "large": "#b00000"}

    for pert in PERTS:
        d = summary[summary["pert"] == pert]
        for ax, key, lab in [(axes[0], "peak_dev", "peak deviation (rad)"),
                             (axes[1], "iae", "integrated abs error (rad·s)")]:
            g = d.groupby("coc")[key]
            m = g.mean().reindex(cocs).values
            ci = (1.96 * g.std(ddof=1) / np.sqrt(g.count())).reindex(cocs).values
            ax.fill_between(cocs, m - ci, m + ci, color=pert_colors[pert], alpha=0.18)
            ax.plot(cocs, m, "-o", color=pert_colors[pert], lw=1.8,
                    label=f"{pert} perturbation")
            ax.set_xlabel("co-contraction (antagonist tension)"); ax.set_ylabel(lab)
            ax.legend(fontsize=8)
    axes[0].set_title("A — peak deviation falls with antagonist tension\n"
                      "(faster error correction)", fontsize=9.5)
    axes[1].set_title("B — integrated error falls with antagonist tension",
                      fontsize=9.5)

    # the tradeoff: error vs energy, with coc as the swept variable
    for pert in PERTS:
        d = summary[summary["pert"] == pert].groupby("coc")
        e = d["energy"].mean().reindex(cocs).values
        ia = d["iae"].mean().reindex(cocs).values
        axes[2].plot(e, ia, "-o", color=pert_colors[pert], lw=1.8, label=f"{pert}")
        for c, ex, iy in zip(cocs, e, ia):
            axes[2].annotate(f"{c:g}", (ex, iy), fontsize=6, color="#555",
                             xytext=(3, 3), textcoords="offset points")
    axes[2].set_xlabel("energy cost (∫ activation² dt)")
    axes[2].set_ylabel("integrated error (rad·s)")
    axes[2].set_title("C — the tradeoff: antagonist tension buys\n"
                      "error correction at an energy cost (labels = coc)", fontsize=9.5)
    axes[2].legend(fontsize=8)
    fig.suptitle("Prediction 3 — antagonistic benefits: co-contraction speeds "
                 "perturbation correction, at a cost", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    grid = [{"coc": c, "pert": p} for c in COCS for p in PERTS]
    summary = run_sweep("pred3_antagonistic", run_one, grid, SEEDS, summarize,
                        outdir=os.path.join(here, "..", "data"), timeseries=False)
    export_curated("pred3_antagonistic", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    print("\n  large-perturbation peak deviation & energy by co-contraction:")
    for c in COCS:
        d = summary[(summary.coc == c) & (summary["pert"] == "large")]
        print(f"   coc={c}: peak {d.peak_dev.mean():.4f}  iae {d.iae.mean():.4f}  "
              f"energy {d.energy.mean():.3f}")
    plot(summary, os.path.join(figdir, "sweep_pred3_antagonistic.png"))
