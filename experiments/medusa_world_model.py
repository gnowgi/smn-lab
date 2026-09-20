# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""A sessile cnidarian builds no world-model; a moving medusa does. (The razor.)

G. Nagarjuna's thesis for Phase B: *a sessile cnidarian is unlikely to construct a
valuable world-model.* Here it is made a measured transition, not an assertion.

Setup. The medusa hangs in a pond that also holds one **world source** — a Gaussian
field peak (chemical/thermal) at a fixed 3-D location, of randomized strength. The
source does **not** push the body (a distal field, evaluated bench-side at each
sensor's position — ``smn_lab.fields``); it only registers on the **tentacle-tip
transducers**. So the animal's self-motion is *independent* of where the source is:
one swim, many possible worlds.

The world-model = **decodability of the source's location** from the tip-sensor
stream (held-out kNN skill, ``smn_lab.metrics.decoding_skill``; shuffle control).
Why motion should matter: a **sessile** animal reads the field from one fixed set of
tip positions — a single projection, and with the source strength unknown, the raw
reading fixes neither distance nor (well) bearing. A **moving** animal sweeps its
tips through a self-generated **baseline** (the swim) and self-generated
**configurations** (tentacle curl); the source is then seen with parallax, so its
location becomes decodable. The self-caused change is the information — which is the
whole point of not being sessile.

The **order-parameter razor** (``docs/order-parameters.md``): sweep **self-motion
amplitude** ``α`` (the control parameter: coronal + tentacle drive, ``α = 0`` is the
sessile disk) and read **world-model skill** (the OP). Stipulated quantities stay put;
an emergent world-model turns on only as the animal moves. Diagnostic: skill(α=0) at
chance/low, rising with α; shuffle ~ 0 throughout.

Run:  ../.venv/bin/python medusa_world_model.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.medusa import medusa_spec, build_medusa, apply_medium
from smn_lab.metrics import decoding_skill

DT = 0.001
T_PROBE = 3.5
PERIOD, DUTY = 0.5, 0.15
C_QUAD, C_LIN, AXIS_GAIN = 9.0, 0.15, 2.5
SEG_DAMP, Z_APEX, LAT_STIFF = 1.3, 0.30, 20.0
CMAX = 13.0
SAMPLE_EVERY = 50                       # sensor sample cadence (0.05 s)
ALPHAS = [0.0, 2.0, 4.0, 7.0, 10.0, 13.0]   # self-motion amplitude sweep (0 = sessile)
N_TRIAL = 96                            # random source placements
SRC_DMIN, SRC_DMAX = 0.8, 1.8          # source distance range (world units)
SRC_SIGMA = 0.7
NOISE = 0.02                            # transducer noise (fraction of local reading scale)
SEED = 0


def tip_trajectory(alpha):
    """One source-independent run at self-motion amplitude ``alpha``; return the
    tip-site world positions over time, shape (n_samples, n_tips, 3). ``alpha`` drives
    the coronal (swim) pulsation and a tentacle-curl rhythm together — ``alpha = 0`` is
    the sessile animal (no drive, tips fixed)."""
    sp = medusa_spec(z_apex=Z_APEX)
    m, d, bid = build_medusa(sp, cmax=CMAX, seg_damp=SEG_DAMP, lat_stiff=LAT_STIFF)
    m.opt.timestep = DT
    coronal, tent = sp["coronal"], sp["tentacle"]
    tip_bids = np.array(bid)[sp["tips"]]
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    traj = []
    for i in range(int(T_PROBE / DT)):
        t = i * DT
        ctrl = np.zeros(m.nu)
        if alpha > 0:
            if (t % PERIOD) / PERIOD < DUTY:
                ctrl[coronal] = alpha                       # swim power stroke
            # tentacle curl rhythm, offset half a period from the bell (its own probe)
            if ((t + PERIOD / 2) % PERIOD) / PERIOD < 0.45:
                ctrl[tent] = 0.4 * alpha
        d.ctrl[:] = ctrl
        apply_medium(m, d, bid, c_quad=C_QUAD, c_lin=C_LIN, axis=2, axis_gain=AXIS_GAIN)
        mujoco.mj_step(m, d)
        if i % SAMPLE_EVERY == 0:
            traj.append(d.xpos[tip_bids].copy())
    return np.array(traj)                                   # (n_samp, n_tips, 3)


def read_source(traj, src, amp, rng):
    """Tip readings of a Gaussian source over the trajectory → a per-trial feature
    vector built ONLY from **self-caused change**: per tip [range(max−min), net
    drift(final−initial)]. This is the SMN commitment that the world-model is grounded
    in *modulated* (self-caused) sensation, not a raw static read (cf. Q1). The static
    ``mean`` is deliberately excluded — it would hand a sessile animal a free
    fixed-array bearing; here, no self-motion means no change means no world-model."""
    d2 = ((traj - src[None, None, :]) ** 2).sum(-1)         # (n_samp, n_tips)
    read = amp * np.exp(-d2 / (2 * SRC_SIGMA ** 2))
    read = read + NOISE * read.mean() * rng.standard_normal(read.shape)
    rng_ = read.max(0) - read.min(0)                        # how much each tip's view swept
    drift = read[-1] - read[0]                              # net change over the trajectory
    return np.concatenate([rng_, drift])


def world_model_skill(traj, rng):
    """Decode source LOCATION from the tip-sensor stream across ``N_TRIAL`` random
    sources sampled along this one trajectory. Returns (skill, shuffle)."""
    feats, locs = [], []
    for _ in range(N_TRIAL):
        u = rng.standard_normal(3); u /= np.linalg.norm(u) + 1e-9
        dist = rng.uniform(SRC_DMIN, SRC_DMAX)
        src = u * dist + np.array([0, 0, 0.1])              # sources around the animal
        amp = rng.uniform(0.6, 1.4)                         # unknown strength → raw reading ≠ distance
        feats.append(read_source(traj, src, amp, rng)); locs.append(src)
    S, P = np.array(feats), np.array(locs)
    order = rng.permutation(len(S)); S, P = S[order], P[order]   # de-correlate the time split
    skill = float(decoding_skill(S, P, np.random.default_rng(7), k=8))
    shuf = float(decoding_skill(S, P, np.random.default_rng(7), k=8, shuffle=True))
    return skill, shuf


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for a in ALPHAS:
        traj = tip_trajectory(a)
        swept = np.linalg.norm(traj[-1].mean(0) - traj[0].mean(0))   # net tip baseline
        skill, shuf = world_model_skill(traj, np.random.default_rng(SEED + 1))
        rows.append((a, swept, skill, shuf))

    print("\nA sessile cnidarian builds no world-model; a moving medusa does\n" + "=" * 66)
    print(f"world source: Gaussian peak, random location (d∈[{SRC_DMIN},{SRC_DMAX}]) & strength;")
    print(f"read by {len(medusa_spec(z_apex=Z_APEX)['tips'])} tentacle-tip transducers over {T_PROBE:.1f}s; "
          f"{N_TRIAL} placements.\n")
    print(f"{'self-motion α':>14}{'tip baseline':>14}{'world skill':>13}{'shuffle':>10}")
    for a, swept, skill, shuf in rows:
        tag = "  (sessile)" if a == 0 else ""
        print(f"{a:>14.1f}{swept:>14.3f}{skill:>13.2f}{shuf:>10.2f}{tag}")
    print("=" * 66)
    s0 = rows[0][2]; sm = rows[-1][2]
    ok = s0 < 0.25 and sm > s0 + 0.25 and all(abs(r[3]) < 0.15 for r in rows)
    print(f"Razor [{'PASS' if ok else 'CHECK'}]: world-model skill rises from {s0:.2f} at α=0 "
          f"(sessile) to {sm:.2f} as the")
    print(f"medusa moves — the world-model is EMERGENT in self-motion, not stipulated. The")
    print(f"self-caused sweep of the tips (baseline {rows[-1][1]:.2f}) is the information; a")
    print(f"sessile animal, one fixed projection, cannot localize the source. Shuffle ~ 0.\n")

    A = [r[0] for r in rows]; SK = [r[2] for r in rows]; SH = [r[3] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    ax[0].plot(A, SK, "o-", color="#2c6fbb", lw=2.3, label="world-model skill")
    ax[0].plot(A, SH, "s--", color="#999999", lw=1.6, label="shuffle control")
    ax[0].axvspan(-0.3, 0.3, color="#c0392b", alpha=0.10)
    ax[0].text(0.05, 0.04, "sessile", color="#c0392b", fontsize=9, transform=ax[0].get_yaxis_transform())
    ax[0].set_xlabel("self-motion amplitude α  (control parameter)")
    ax[0].set_ylabel("world-model skill  (order parameter)")
    ax[0].set_title("Valuable world-model turns on with motion"); ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)
    base = [r[1] for r in rows]
    ax[1].plot(base, SK, "o-", color="#1f8a5b", lw=2.3)
    ax[1].set_xlabel("self-generated tip baseline (parallax)")
    ax[1].set_ylabel("world-model skill")
    ax[1].set_title("Skill tracks the self-generated baseline"); ax[1].grid(alpha=0.3)
    fig.tight_layout()
    o = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "medusa_world_model.png")
    os.makedirs(os.path.dirname(o), exist_ok=True); fig.savefig(o, dpi=130)
    print(f"figure -> {os.path.normpath(o)}")


if __name__ == "__main__":
    main()
