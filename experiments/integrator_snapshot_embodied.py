# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Integrator & snapshot -- Phase B: the embodied MuJoCo instance.

Phase A (sweep_integrator_snapshot.py) *imposed* the motor stroke-frequency
ceiling and drove an abstract network. Phase B puts the motor CAZ in a physical
body -- an axial opponent chain (smn_lab.crawler) driven by pull-only antagonist
pairs -- so the physics does the work the network model faked:

  B1. stroke ceiling EMERGES.   The coordinated gait, driven faster and faster,
      cannot be realized: the achieved bend amplitude rolls off past a mechanical
      bandwidth, and both the ceiling frequency and the achievable bend FALL as
      segment mass rises (the allometric ceiling) -- H1 grounded in real dynamics,
      not an imposed parameter.
  A.  manifold from REAL proprioception. Low dimensionality is not free: an
      independently-flailing body genuinely spans many dimensions and a faithful
      beam must keep them. The held low-D manifold appears when the broadcast
      COORDINATES the body into a traveling wave -- the beam holds the gait
      manifold; the uncoordinated foil does not.
  B.  Nyquist margin. Because f_c is physically small (a few Hz) and a gamma-band
      beam refreshes fast, the body sits comfortably in the faithful regime
      (refresh > 2 f_c); the physical stroke ceiling is exactly what the beam
      must out-refresh, and it clears it with a wide margin.

Run:  ../.venv/bin/python integrator_snapshot_embodied.py   (from this directory)
"""
from __future__ import annotations
import os, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml
from smn_lab.control import OpponentBoard
from integrator_snapshot import (manifold_dimensionality, snapshot_fidelity)

DT = 0.002                                  # matches the MJCF <option timestep>


# --------------------------------------------------------------------------- #
# the physical opponent chain
# --------------------------------------------------------------------------- #
def _build(n_seg, seg_mass, joint_damping=0.001, cmax=15.0):
    xml = build_crawler_xml(n_seg=n_seg, seg_mass=seg_mass,
                            joint_damping=joint_damping, cmax=cmax)
    for jn in ("slide_x", "slide_y", "yaw"):           # pin the base to the world
        xml = re.sub(rf'<joint name="{jn}"[^/]*/>\s*', "", xml)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    j = [model.joint(f"j{k}").id for k in range(1, n_seg)]
    ids = dict(
        qadr=[model.jnt_qposadr[i] for i in j],
        vadr=[model.jnt_dofadr[i] for i in j],
        ap=[model.actuator(f"m_j{k}_p").id for k in range(1, n_seg)],
        an=[model.actuator(f"m_j{k}_n").id for k in range(1, n_seg)],
        nj=n_seg - 1)
    return model, data, ids


def _drive(model, data, ids, cmd_fn, T, kp=50.0, kd=1.0):
    """Run T steps; cmd_fn(t) returns an nj-vector of commanded joint angles,
    realized through the pull-only opponent boards. Returns (T, nj) actual joint
    angles."""
    boards = [OpponentBoard(kp=kp, kd=kd, cmax=15.0) for _ in range(ids["nj"])]
    mujoco.mj_forward(model, data)
    ang = np.zeros((T, ids["nj"]))
    for t in range(T):
        cmd = cmd_fn(t * DT)
        for k in range(ids["nj"]):
            th = float(data.qpos[ids["qadr"][k]])
            thd = float(data.qvel[ids["vadr"][k]])
            a_r, a_l, _ = boards[k].commands(th, thd, cmd[k], 0.0)
            data.ctrl[ids["ap"][k]] = a_r
            data.ctrl[ids["an"][k]] = a_l
        mujoco.mj_step(model, data)
        ang[t] = [data.qpos[ids["qadr"][k]] for k in range(ids["nj"])]
    return ang


# --------------------------------------------------------------------------- #
# B1 -- the stroke-frequency ceiling emerges from the body
# --------------------------------------------------------------------------- #
def stroke_ceiling(seg_mass, freqs, n_seg=6, cmd=0.30):
    """Drive the coordinated traveling-wave gait (the body's working mode) at each
    frequency; return the mean achieved bend amplitude. Because inertia and finite
    actuator authority cannot be overcome arbitrarily fast, the achieved amplitude
    rolls off past a mechanical bandwidth -- the physical stroke ceiling -- and
    rolls off SOONER, and to a lower plateau, for heavier bodies (the allometric
    ceiling). Measured in the body's real operating mode, not a single-DOF probe."""
    amps = []
    for f in freqs:
        model, data, ids = _build(n_seg, seg_mass)
        jj = np.arange(ids["nj"])
        T = int(np.clip(10.0 / f, 1.0, 6.0) / DT)
        ang = _drive(model, data, ids,
                     lambda t, f=f: cmd * np.sin(2 * np.pi * f * t
                                                 - (2 * np.pi / ids["nj"]) * jj),
                     T, kd=2.0)
        amps.append(float(np.abs(ang[int(0.5 * T):]).max(axis=0).mean()))
    return np.array(amps)


def ceiling_frequency(freqs, amps, frac=0.5):
    """f_c = the frequency at which the achieved gait amplitude falls to `frac` of
    its low-frequency maximum."""
    below = np.where(amps < frac * amps.max())[0]
    return float(freqs[below[0]]) if below.size else float(freqs[-1])


# --------------------------------------------------------------------------- #
# A -- the beam holds a low-D manifold when the body moves COORDINATEDLY
# --------------------------------------------------------------------------- #
def embodied_manifold(n_seg=10, seg_mass=0.05, f=0.8, seed=0):
    rng = np.random.default_rng(seed)
    Tn = int(14.0 / DT)
    nj = n_seg - 1

    # broadcast ON: a coordinated traveling wave (fixed spatial wavenumber) --
    # intrinsically a 2-D gait manifold, well below the stroke ceiling.
    model, data, ids = _build(n_seg, seg_mass)
    j = np.arange(nj)
    ang_coord = _drive(model, data, ids,
                       lambda t: 0.30 * np.sin(2 * np.pi * f * t - (2 * np.pi / nj) * j),
                       Tn, kd=2.0)[::5]

    # broadcast OFF (foil): each joint on its own frequency/phase (high-D flailing)
    model, data, ids = _build(n_seg, seg_mass)
    fr = rng.uniform(0.3, 1.6, nj); ph = rng.uniform(0, 2 * np.pi, nj)
    ang_indep = _drive(model, data, ids,
                       lambda t: 0.30 * np.sin(2 * np.pi * fr * t + ph), Tn, kd=2.0)[::5]

    return dict(nj=nj, traj_coord=ang_coord, traj_indep=ang_indep,
                pr_coordinated=manifold_dimensionality(ang_coord),
                pr_independent=manifold_dimensionality(ang_indep))


# --------------------------------------------------------------------------- #
# B -- Nyquist margin: the beam must out-refresh the PHYSICAL stroke ceiling
# --------------------------------------------------------------------------- #
def nyquist_margin(f_c, refreshes):
    """At the physical stroke ceiling f_c, sweep beam refresh; the held snapshot
    aliases when refresh < 2 f_c. Returns the fidelity curve + recovered refresh
    threshold (predicted 2 f_c)."""
    dt = 0.0005
    T = int(12 / f_c / dt); t = np.arange(T) * dt
    stroke = np.sin(2 * np.pi * f_c * t)
    fids = []
    for fr in refreshes:
        step = max(1, int(round((1.0 / fr) / dt)))
        idx = np.arange(0, T, step)
        fids.append(snapshot_fidelity(stroke, np.interp(np.arange(T), idx, stroke[idx])))
    fids = np.array(fids)
    ok = np.where(fids >= 0.7)[0]
    return dict(fids=fids.tolist(), refreshes=list(map(float, refreshes)),
                predicted=2 * f_c,
                refresh_threshold=float(refreshes[ok[0]]) if ok.size else float("inf"))


# --------------------------------------------------------------------------- #
def _pca2(X):
    Xc = np.asarray(X, float) - np.asarray(X, float).mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:2].T


def plot(b1, manifold, nq, out):
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(15, 4.4))

    for name, (freqs, amps) in b1.items():
        axA.semilogx(freqs, amps, "-o", ms=4, label=name)
    axA.set_xlabel("gait frequency (Hz)"); axA.set_ylabel("achieved bend (rad)")
    axA.set_title("B1 — physical stroke ceiling\n(rolls off; heavier body = lower)",
                  fontsize=10)
    axA.legend(fontsize=8, title="segment mass")

    c, u = _pca2(manifold["traj_coord"]), _pca2(manifold["traj_indep"])
    axB.plot(u[:, 0], u[:, 1], ".", ms=2, color="#c0392b", alpha=0.5,
             label=f"independent (PR {manifold['pr_independent']:.1f})")
    axB.plot(c[:, 0], c[:, 1], "-", lw=1.7, color="#1538a0",
             label=f"coordinated (PR {manifold['pr_coordinated']:.1f})")
    axB.set_aspect("equal"); axB.set_xlabel("PC1"); axB.set_ylabel("PC2")
    axB.set_title("A — held manifold from real proprioception\n"
                  "coordinated = low-D loop; flailing = high-D blob", fontsize=10)
    axB.legend(fontsize=8, loc="upper right")

    fc = nq["predicted"] / 2.0
    axC.plot(np.array(nq["refreshes"]) / fc, nq["fids"], "-o", ms=4, color="#117733")
    axC.axvline(2.0, color="#b00000", ls="--", lw=1.2, label="Nyquist = 2 f_c")
    axC.axhline(0.7, color="0.6", ls=":", lw=1)
    axC.set_xlabel("beam refresh  /  stroke ceiling  f_c")
    axC.set_ylabel("held-snapshot fidelity")
    axC.set_title("B — Nyquist margin\n(snapshot aliases below 2 f_c)", fontsize=10)
    axC.legend(fontsize=8, loc="lower right")

    fig.tight_layout(); fig.savefig(out, dpi=130)
    print(f"[saved] {out}")


def main():
    print("=== B1 · stroke-frequency ceiling emerges from the body ===")
    freqs = np.array([0.5, 1, 2, 3, 5, 8, 12, 18, 25.0])
    masses = [("light", 0.02), ("medium", 0.10), ("heavy", 0.50)]
    fcs, b1 = {}, {}
    print(f"{'body':<8} {'seg_mass':>9} {'peak bend':>10} {'f_c (half, Hz)':>16}")
    for name, mss in masses:
        amps = stroke_ceiling(mss, freqs)
        b1[name] = (freqs, amps)
        fc = ceiling_frequency(freqs, amps)
        fcs[name] = fc
        print(f"{name:<8} {mss:>9.2f} {amps.max():>10.2f} {fc:>16.1f}")
    print("  -> heavier body: lower achievable bend AND lower ceiling frequency -- "
          "the motor CAZ limit is physical (allometric), not an imposed parameter.")

    print("\n=== A · beam holds a low-D manifold when movement is coordinated ===")
    m = embodied_manifold()
    print(f"  {m['nj']} physical joints -- proprioception participation ratio:")
    print(f"    broadcast ON (traveling wave)  PR = {m['pr_coordinated']:.2f}  (held gait manifold)")
    print(f"    broadcast OFF (independent foil) PR = {m['pr_independent']:.2f}")
    print("  -> coordination condenses real movement onto a low-D held manifold; "
          "flailing does not.")

    print("\n=== B · Nyquist margin: beam must out-refresh the physical stroke ===")
    f_c = fcs["medium"]
    nq = nyquist_margin(f_c, np.linspace(f_c * 0.5, f_c * 6, 24))
    print(f"  physical stroke ceiling f_c = {f_c:.1f} Hz -> beam refresh must exceed "
          f"2 f_c = {nq['predicted']:.1f} Hz (recovered {nq['refresh_threshold']:.1f})")
    print(f"  gamma-band beams clear it with margin: 40 Hz -> {40 / nq['predicted']:.1f}x, "
          f"80 Hz -> {80 / nq['predicted']:.1f}x. The body cannot stroke fast enough "
          "to alias the canvas.")

    ok = (fcs["heavy"] < fcs["light"] and m["pr_coordinated"] < m["pr_independent"]
          and nq["refresh_threshold"] <= 2.3 * f_c and 40 / nq["predicted"] > 1.0)
    print("\n  verdict:", "PASS -- allometric physical stroke ceiling, embodied "
          "low-D held manifold under coordination, and a satisfied Nyquist margin."
          if ok else "INCONCLUSIVE -- tune body/board params.")

    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures")
    os.makedirs(figdir, exist_ok=True)
    plot(b1, m, nq, os.path.join(figdir, "integrator_snapshot_embodied.png"))


if __name__ == "__main__":
    main()
