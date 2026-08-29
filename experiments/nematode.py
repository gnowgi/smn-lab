# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Nematode (tubular model system) — DV opponent-pair CAZ (canonical, corrected).

Reconstructed with the CAZ ontology and the sourced nematode biology (G. Nagarjuna):
a lattice NODE is a multicellular muscle-side REGION; a CAZ = one OPPONENT PAIR = one DOF.

Anatomy (sourced — WormAtlas; BioScience 64(6):476):
  * The muscle DETACHED from the epithelium: three tissues now —
      - SKIN: a passive epithelial tube carrying the transducers (touch all over, temperature
        interspersed, diffuse photoreceptors, denser anterior; NO eyes);
      - GUT: a passive tube, NO muscle;
      - MUSCLE: detached, riding on the skin.
  * The muscle is LONGITUDINAL ONLY (NO circular), in FOUR quadrants (two subdorsal, two
    subventral). Locomotion is a DORSOVENTRAL bend → sinusoidal wave (the worm lies on its side).
Opponent-pair CAZ (what actuates a DOF):
  * BODY CAZ = DORSAL-longitudinal ⊕ VENTRAL-longitudinal → a DV bend. The PASSIVE antagonist /
    restoring side is the elastic CUTICLE + hydrostatic pressure + resting tone (here: the skin
    tube's elasticity). There is NO circular muscle, so NO telescoping pair.
  * MOUTH CAZ = radial pharyngeal fibres ⊕ elastic recoil (the pump).
  * ANUS = dorsoventral muscle-cell pairs.
Contrast held explicit: nematode HAS a DV opponent pair and NO circular; the earthworm has NO DV
muscle (circular⊕longitudinal telescoping + left⊕right lateral).

Demo: an anti-phase dorsal/ventral contraction wave → a travelling DV bend (undulation).
Self-contained. Run:  ../.venv/bin/python nematode.py
"""
from __future__ import annotations
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.fbody import build_body   # shared pull-only f primitive (A2)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

NX, NC, NCG = 12, 8, 4                 # skin axial stations, skin circumference, gut circumference
L, R_S, R_G, R_M = 1.2, 0.10, 0.05, 0.085
DT = 0.002
K_SKIN, K_CUTI, K_GUT, K_ATT = 4.0, 0.7, 1.2, 16.0    # skin rings, cuticle (long. elastic), gut, muscle→skin
K_MUS = 40.0                                          # longitudinal muscle (the only active tissue)
# four muscle quadrants: two subdorsal (z+), two subventral (z-)
MQUAD = {"sdL": 120, "sdR": 60, "svL": 240, "svR": 300}      # degrees
DORSAL, VENTRAL = ["sdL", "sdR"], ["svL", "svR"]


def spec():
    pos, tissue, meta = [], [], []
    SK, GU, MU = {}, {}, {}
    xs = np.linspace(0, L, NX)
    def add(p, t, m): i = len(pos); pos.append(p); tissue.append(t); meta.append(m); return i
    # skin tube (passive) + transducers
    for k, x in enumerate(xs):
        for c in range(NC):
            th = 2 * np.pi * c / NC
            # transducer: touch everywhere; temp on a sparse interspersed set; photo denser anterior
            sensors = ["touch"]
            if (k + c) % 3 == 0: sensors.append("temp")
            if np.random.default_rng(k * NC + c).random() < 0.30 * (1 - x / L): sensors.append("photo")
            SK[(k, c)] = add((x, R_S * np.cos(th), R_S * np.sin(th)), "skin", sensors)
    # gut tube (passive, NO muscle)
    for k, x in enumerate(xs):
        for c in range(NCG):
            th = 2 * np.pi * c / NCG
            GU[(k, c)] = add((x, R_G * np.cos(th), R_G * np.sin(th)), "gut", [])
    # four longitudinal muscle chains (detached, riding on the skin)
    for q, deg in MQUAD.items():
        th = np.deg2rad(deg)
        for k, x in enumerate(xs):
            MU[(q, k)] = add((x, R_M * np.cos(th), R_M * np.sin(th)), "muscle", q)
    # mouth: a hub + radial pharyngeal fibres (anterior); anus DV pair (posterior)
    mouth = add((-0.06, 0, 0), "mouth_hub", "pharynx")
    anus = [add((L + 0.05, 0, R_M * s), "anus", "dv") for s in (+1, -1)]

    edges, etype, is_musc, stiff = [], [], [], []
    def E(a, b, t, m, k): edges.append((a, b)); etype.append(t); is_musc.append(m); stiff.append(k)
    # skin passive: circumferential rings + longitudinal (the elastic cuticle = restoring side)
    for k in range(NX):
        for c in range(NC):
            E(SK[(k, c)], SK[(k, (c + 1) % NC)], "skin_ring", False, K_SKIN)
    for c in range(NC):
        for k in range(NX - 1):
            E(SK[(k, c)], SK[(k + 1, c)], "cuticle", False, K_CUTI)     # passive elastic antagonist
    # gut passive
    for k in range(NX):
        for c in range(NCG):
            E(GU[(k, c)], GU[(k, (c + 1) % NCG)], "gut", False, K_GUT)
    for c in range(NCG):
        for k in range(NX - 1):
            E(GU[(k, c)], GU[(k + 1, c)], "gut", False, K_GUT)
    # longitudinal MUSCLE chains (actuated) + attach each muscle node to nearest skin node
    for q, deg in MQUAD.items():
        cc = int(round((deg / 360.0) * NC)) % NC
        for k in range(NX - 1):
            E(MU[(q, k)], MU[(q, k + 1)], "muscle", True, K_MUS)
        for k in range(NX):
            E(MU[(q, k)], SK[(k, cc)], "attach", False, K_ATT)          # muscle rides on the skin
    # mouth radial fibres (radial ⊕ elastic recoil) to the anterior skin ring
    for c in range(NC):
        E(mouth, SK[(0, c)], "mouth_radial", True, 18.0)
    # anus DV pair (opponent) to posterior skin
    for a, s in zip(anus, (0, NC // 2)):
        E(a, SK[(NX - 1, s)], "anus", True, 16.0)

    return dict(pos=np.array(pos), tissue=np.array(tissue), meta=np.array(meta, dtype=object),
                edges=edges, etype=np.array(etype), is_musc=np.array(is_musc, bool),
                stiff=np.array(stiff, float), SK=SK, GU=GU, MU=MU, mouth=mouth, anus=anus, xs=xs)


def build(S):
    # One shared, PULL-ONLY f primitive (a muscle only contracts; non-negative ctrl = contraction
    # amount; the elastic cuticle restores). Was gear=3/ctrlrange=-4 4 (bidirectional = could push).
    return build_body(S["pos"], S["edges"], S["stiff"], S["is_musc"], cmax=4.0, gear=3.0,
                      pull_only=True, seg_size=0.012, seg_mass=0.04, seg_damp=3.0, name="nematode")


def run(S, ctrl, T):
    m, d, aoe = build(S); n = int(T / DT); traj = np.zeros((n, len(S["pos"]), 3))
    d.qpos[:] = 0; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    for t in range(n):
        u = np.zeros(m.nu); ctrl(t * DT, S, aoe, u); d.ctrl[:] = u; mujoco.mj_step(m, d)
        traj[t] = d.qpos.reshape(-1, 3) + S["pos"]
    return traj


def centerline_z(S, P):
    return np.array([P[[S["SK"][(k, c)] for c in range(NC)]].mean(0)[2] for k in range(NX)])


def main():
    S = spec()
    nS = int((S["tissue"] == "skin").sum()); nG = int((S["tissue"] == "gut").sum())
    nM = int((S["tissue"] == "muscle").sum())
    n_touch = sum("touch" in m for m in S["meta"] if isinstance(m, list))
    n_temp = sum(isinstance(m, list) and "temp" in m for m in S["meta"])
    n_photo = sum(isinstance(m, list) and "photo" in m for m in S["meta"])
    print("\nNematode — tubular model system (DV opponent-pair CAZ)")
    print("=" * 70)
    print(f"  THREE tissues: passive SKIN {nS} (+transducers touch {n_touch}/temp {n_temp}/photo "
          f"{n_photo}) · passive GUT {nG} (no muscle) · detached MUSCLE {nM}")
    print(f"  muscle = LONGITUDINAL ONLY, 4 quadrants {list(MQUAD)} (NO circular)")
    print("  OPPONENT-PAIR CAZ (one DOF each):")
    print(f"    · body CAZ: DORSAL(sdL,sdR) ⊕ VENTRAL(svL,svR) longitudinal → DV bend "
          f"(cuticle/hydrostat = passive restoring)")
    print(f"    · mouth CAZ: radial pharyngeal fibres ⊕ elastic recoil (pump)")
    print(f"    · anus: dorsoventral muscle-cell pair")
    print(f"    · telescoping: NONE (no circular muscle)")
    print("=" * 70)

    musc_edges = np.where(S["etype"] == "muscle")[0]
    chain_of = {}                                   # muscle edge -> (quad, k)
    e = 0
    for q in MQUAD:
        for k in range(NX - 1):
            chain_of[musc_edges[e]] = (q, k); e += 1

    # Demo — travelling DV bend: dorsal & ventral chains driven anti-phase
    T_W, lam = 6.0, 0.9
    def ctrl_undulate(tt, S, aoe, u):
        for e, (q, k) in chain_of.items():
            x = S["xs"][k] / L
            phase = 2 * np.pi * (tt / 1.5 - x / lam)
            drive = np.sin(phase) if q in DORSAL else np.sin(phase + np.pi)   # DV opponent pair
            u[aoe[e]] = 4.0 * max(0.0, drive)
    tr = run(S, ctrl_undulate, T_W)
    Z = np.array([centerline_z(S, tr[t]) for t in range(tr.shape[0])])
    Z = Z - Z[0]
    amp = np.abs(Z).max()
    # count sign changes of the final centerline = number of body bends (a sinusoid)
    zf = Z[-1]; bends = int((np.diff(np.sign(zf[np.abs(zf) > 0.2 * amp + 1e-9])) != 0).sum())
    print(f"Demo · travelling DV bend: centreline deflection amplitude {amp:.3f} "
          f"({amp/R_S:.1f}×R_skin), a dorsoventral undulation wave (≈{bends} bends in the body)")
    print("=" * 70)

    fig = plt.figure(figsize=(14, 5.4))
    ax0 = fig.add_subplot(1, 2, 1)
    im = ax0.imshow(Z.T, aspect="auto", origin="lower", cmap="RdBu", extent=[0, T_W, 0, L],
                    vmin=-amp, vmax=amp)
    ax0.set_title("DV undulation — centreline z(body, time)\ndorsal ⊕ ventral opponent pair, "
                  "anti-phase travelling wave", fontsize=9.5)
    ax0.set_xlabel("time (s)"); ax0.set_ylabel("position along body (head→tail)")
    fig.colorbar(im, ax=ax0, fraction=0.046, label="dorsoventral deflection")
    ax1 = fig.add_subplot(1, 2, 2)
    xs = S["xs"]
    for frac, c in [(0.6, "#bbbbbb"), (0.8, "#e08a7a"), (1.0, "#c0392b")]:
        t = int(frac * (Z.shape[0] - 1))
        ax1.plot(xs, Z[t], "-", color=c, lw=2, label=f"t={frac*T_W:.1f}s")
    ax1.axhline(0, color="#ddd", lw=0.8)
    ax1.set_title("body midline (dorsoventral) at three times\n— a sinusoid travelling head→tail",
                  fontsize=9.5)
    ax1.set_xlabel("position along body"); ax1.set_ylabel("dorsoventral deflection")
    ax1.legend(fontsize=8)
    fig.suptitle("Nematode — DV opponent-pair CAZ (dorsal ⊕ ventral longitudinal), no circular; "
                 "cuticle = passive restoring", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "nematode.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print("figure ->", os.path.normpath(out))


if __name__ == "__main__":
    main()
