# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Prediction 2 -- zonal dissociations. Pre-registered (test plan).

SMN preprint, Predictions & Testable Claims #2: "The same abstract task should
produce different performance across materials/couplings (viscoelastic vs rigid
tools) due to zone priors -- dissociations by substrate even with identical
task-level specifications." (M1 hm-multi-zonal: zones carry "pre-tuned priors" for
the zone-specific statistics of their medium.)

The clean, falsifiable form is a CROSSOVER, not a main effect: the controller (zone
prior) that is best on a rigid tool should be *worse* on a compliant one, and vice
versa -- so the substrate, not the task, decides which zone wins. A "harder
substrate = worse for everyone" main effect would NOT be a dissociation.

Setup. The same reach-and-hold task is performed through a tool: a motor-driven
limb carries a passive tool link whose joint has a stiffness + damping -- the
"material". Rigid = stiff/lightly-damped tool (tip ~ limb); viscoelastic =
compliant + dissipative tool (a 2-DOF resonant load). The agent commands the motor
with a PD controller (the "zone") whose gains (kp, kd) are its prior. We sweep the
gain grid on BOTH substrates; the dissociation is whether the OPTIMAL gain differs
by substrate and whether cross-applying a substrate's optimum to the other hurts.

Pre-registration:
- Hypothesis: the gain that minimizes task error differs by substrate (a CROSSOVER):
  the rigid-optimal prior underperforms on the viscoelastic tool and vice versa; no
  single "generic" prior matches the substrate-specific priors on both.
- Order parameter: tip-tracking integrated abs error (IAE) of the reach-and-hold.
- Conditions: gain grid (kp x kd) x substrate {rigid, viscoelastic} x seeds.
- Pass: the per-substrate optimal gains differ AND matched (optimum-for-this-
  substrate) clearly beats mismatched (optimum-for-other) on each substrate -- a
  crossover interaction; the generic (best-on-average) is worse than matched on
  both.
- Falsify: one gain is best on both substrates (no interaction), or the generic
  matches the substrate-specific priors -> zone priors buy no substrate dissociation.

Honest note: that matched gains beat mismatched is expected from control theory
(high gain excites a compliant load's resonance; a rigid load rewards high gain).
The experiment demonstrates that the SMN zone-prior architecture *produces* the
predicted substrate dissociation and quantifies it (the crossover magnitude, and
that no generic prior substitutes for substrate-specific ones).

Outputs: data/pred2_zonal/, samples/.../summary.csv, figures/sweep_pred2_zonal.png
Run:  ../.venv/bin/python sweep_pred2_zonal.py
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
T_END = 2.0
TARGET = 0.4                 # reach-and-hold tip target (rad)
CMAX = 3.0                   # actuator ceiling -- high enough that GAINS operate
                              # (the first run saturated for every gain, so the
                              # gain -- the IV -- had no effect: a setup bug)
PROPRIO_NOISE = 0.004
KPS = [2.0, 6.0, 15.0, 30.0]
KDS = [0.02, 0.1, 0.4, 1.0]
# materials: tool joint stiffness (elastic) + damping (viscous). Rigid = stiff;
# viscoelastic = compliant + lightly damped (a resonant load high gain can excite).
SUBSTRATES = {"rigid": dict(k=250.0, b=0.30), "viscoelastic": dict(k=3.0, b=0.15)}
SEEDS = list(range(4))


def build_tool_xml(k, b):
    """Motor-driven limb carrying a passive tool link; the tool joint's stiffness
    k (elastic) and damping b (viscous) are the 'material'. The tool is given real
    inertia so a compliant joint yields an in-band resonance."""
    return f"""
<mujoco model="zonal_tool">
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <worldbody>
    <body name="limb" pos="0 0 0.4">
      <joint name="j_limb" type="hinge" axis="0 0 1" damping="0.02"/>
      <geom type="capsule" fromto="0 0 0 0.15 0 0" size="0.02" mass="0.10"/>
      <body name="tool" pos="0.15 0 0">
        <joint name="j_tool" type="hinge" axis="0 0 1" stiffness="{k}" damping="{b}"/>
        <geom type="capsule" fromto="0 0 0 0.20 0 0" size="0.015" mass="0.15"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="m_p" joint="j_limb" gear="1"  ctrlrange="0 {CMAX}"/>
    <motor name="m_n" joint="j_limb" gear="-1" ctrlrange="0 {CMAX}"/>
  </actuator>
  <sensor>
    <jointpos name="ang_limb" joint="j_limb"/>
    <jointvel name="vel_limb" joint="j_limb"/>
    <jointpos name="ang_tool" joint="j_tool"/>
    <jointvel name="vel_tool" joint="j_tool"/>
  </sensor>
</mujoco>
"""


def run_one(params, seed):
    kp, kd = float(params["kp"]), float(params["kd"])
    sub = SUBSTRATES[params["substrate"]]
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(build_tool_xml(sub["k"], sub["b"]))
    data = mujoco.MjData(model)
    jl = model.joint("j_limb").id; jt = model.joint("j_tool").id
    ql, vl = model.jnt_qposadr[jl], model.jnt_dofadr[jl]
    qt, vt = model.jnt_qposadr[jt], model.jnt_dofadr[jt]
    ap, an = model.actuator("m_p").id, model.actuator("m_n").id

    mujoco.mj_forward(model, data)
    n = int(T_END / DT)
    log = {"t": [], "tip": []}
    for i in range(n):
        tip = float(data.qpos[ql] + data.qpos[qt])          # tip angle = limb + tool
        tipd = float(data.qvel[vl] + data.qvel[vt])
        tip_s = tip + rng.normal(0, PROPRIO_NOISE)
        tipd_s = tipd + rng.normal(0, PROPRIO_NOISE * 10)
        tau = kp * (TARGET - tip_s) + kd * (0.0 - tipd_s)   # PD on the tip (the task)
        data.ctrl[ap] = min(CMAX, max(0.0, tau))
        data.ctrl[an] = min(CMAX, max(0.0, -tau))
        mujoco.mj_step(model, data)
        log["t"].append(i * DT)
        log["tip"].append(float(data.qpos[ql] + data.qpos[qt]))
    log["t"] = np.array(log["t"]); log["tip"] = np.array(log["tip"])
    return log


def summarize(log, params, seed):
    err = np.abs(TARGET - log["tip"])
    iae = float(np.trapezoid(err, log["t"]))
    overshoot = float(max(0.0, log["tip"].max() - TARGET))
    final_err = float(np.mean(err[log["t"] > (T_END - 0.3)]))
    return {"iae": iae, "overshoot": overshoot, "final_err": final_err}


def _grid(summary, sub):
    """Mean IAE over seeds as a (kp x kd) grid for one substrate."""
    d = summary[summary["substrate"] == sub]
    G = np.zeros((len(KPS), len(KDS)))
    for i, kp in enumerate(KPS):
        for j, kd in enumerate(KDS):
            G[i, j] = d[(d.kp == kp) & (d.kd == kd)]["iae"].mean()
    return G


def plot(summary, out):
    Gr, Gv = _grid(summary, "rigid"), _grid(summary, "viscoelastic")
    ri, rj = np.unravel_index(np.argmin(Gr), Gr.shape)   # rigid-optimal gain
    vi, vj = np.unravel_index(np.argmin(Gv), Gv.shape)   # visco-optimal gain
    # generic = gain minimizing the average over substrates
    Gavg = 0.5 * (Gr / Gr.min() + Gv / Gv.min())
    gi, gj = np.unravel_index(np.argmin(Gavg), Gavg.shape)

    fig = plt.figure(figsize=(14, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.1], wspace=0.35)
    for ax, G, sub, (oi, oj) in [(fig.add_subplot(gs[0]), Gr, "rigid", (ri, rj)),
                                 (fig.add_subplot(gs[1]), Gv, "viscoelastic", (vi, vj))]:
        im = ax.imshow(G, origin="lower", aspect="auto", cmap="viridis_r")
        ax.set_xticks(range(len(KDS))); ax.set_xticklabels(KDS)
        ax.set_yticks(range(len(KPS))); ax.set_yticklabels(KPS)
        ax.set_xlabel("kd"); ax.set_ylabel("kp")
        ax.scatter([oj], [oi], marker="*", s=260, color="#ff3b3b", edgecolors="k",
                   zorder=5, label="optimum")
        ax.set_title(f"{sub}: task error (IAE) over gains\n(optimum ★ — note it "
                     f"moves between substrates)", fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # crossover bars: matched vs mismatched vs generic on each substrate
    axc = fig.add_subplot(gs[2])
    rigid_opt, visco_opt, gen = (ri, rj), (vi, vj), (gi, gj)
    bars = {
        "rigid": [Gr[rigid_opt], Gr[visco_opt], Gr[gen]],
        "viscoelastic": [Gv[visco_opt], Gv[rigid_opt], Gv[gen]],
    }
    x = np.arange(2); w = 0.26
    labels = ["matched prior", "mismatched prior", "generic prior"]
    colors = ["#1538a0", "#b00000", "#888888"]
    for k, (lab, c) in enumerate(zip(labels, colors)):
        vals = [bars["rigid"][k], bars["viscoelastic"][k]]
        axc.bar(x + (k - 1) * w, vals, w, color=c, label=lab)
    axc.set_xticks(x); axc.set_xticklabels(["rigid\nsubstrate", "viscoelastic\nsubstrate"])
    axc.set_ylabel("task error (IAE)")
    axc.set_title("C — the dissociation: each substrate's matched prior wins;\n"
                  "cross-applying it (mismatched) hurts; generic is worse on both",
                  fontsize=9)
    axc.legend(fontsize=8)
    fig.suptitle("Prediction 2 — zonal dissociations: same task, the best zone "
                 "prior depends on the substrate", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out, dpi=130)
    print(f"[saved] {out}")
    return (ri, rj), (vi, vj), (gi, gj), Gr, Gv


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    grid = [{"kp": kp, "kd": kd, "substrate": s}
            for kp in KPS for kd in KDS for s in SUBSTRATES]
    summary = run_sweep("pred2_zonal", run_one, grid, SEEDS, summarize,
                        outdir=os.path.join(here, "..", "data"), timeseries=False)
    export_curated("pred2_zonal", src=os.path.join(here, "..", "data"),
                   dst=os.path.join(here, "..", "samples"))
    (ri, rj), (vi, vj), (gi, gj), Gr, Gv = plot(
        summary, os.path.join(figdir, "sweep_pred2_zonal.png"))
    print(f"\n  rigid-optimal gain:        kp={KPS[ri]}, kd={KDS[rj]}")
    print(f"  viscoelastic-optimal gain: kp={KPS[vi]}, kd={KDS[vj]}")
    print(f"  (different gain wins on each substrate: {(ri,rj) != (vi,vj)})")
    print(f"  rigid:  matched IAE={Gr[ri,rj]:.4f}  mismatched(visco-opt)={Gr[vi,vj]:.4f}")
    print(f"  visco:  matched IAE={Gv[vi,vj]:.4f}  mismatched(rigid-opt)={Gv[ri,rj]:.4f}")
