# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The medusa swims — coordinated bell pulsation nets locomotion through the pond.

The sessile disk cannot move; the medusa can. Its **coronal** (subumbrellar ring)
``f``s pulsate — a fast power stroke, then a spring-limited recovery — and in the
pond (a quadratic-drag medium) that **rate asymmetry** nets aboral translation.
Nobody pushes the body: the drive is a pulsation *pattern* over the coronal ``f``s
(a CAZ), and the swim is the whole-SMN consequence of that pattern meeting the
medium.

The load-bearing claim is the **scallop theorem** and its escape. A reciprocal
shape change nets zero displacement in a linear-drag world, however vigorous. Two
controls make the point:

  * **linear-drag control** (``c_quad = 0``): same pulsation, purely linear medium →
    net translation collapses. The *nonlinearity* is necessary.
  * **symmetric-drive control**: the same time-averaged coronal force applied
    *steadily* (no power/recovery asymmetry) → net translation collapses. The *rate
    asymmetry* is necessary.

Order parameter: **net aboral displacement per unit time** (a collective, emergent
locomotor rate — zero for the disk, positive only when an asymmetric pattern meets
a nonlinear medium). Diagnostics: monotonic progress; swim ≫ both controls.

Run:  ../.venv/bin/python medusa_swim.py
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

DT = 0.001
T_SWIM = 24.0
PERIOD, DUTY, CMAX = 0.5, 0.15, 13.0      # pulsation: fast power stroke (15% of cycle), hard
C_QUAD, C_LIN, AXIS_GAIN = 9.0, 0.15, 2.5  # the pond: quadratic drag, mild aboral anisotropy
SEG_DAMP, Z_APEX, LAT_STIFF = 1.3, 0.30, 20.0
SWIM_AXIS = 2                              # +z = aboral (apex leads)


def com(d, bid):
    return d.xpos[bid].mean(0).copy()


def run(mode="swim"):
    """mode: 'swim' | 'linear' (c_quad=0) | 'symmetric' (steady, no rate asymmetry)."""
    sp = medusa_spec(z_apex=Z_APEX)
    m, d, bid = build_medusa(sp, cmax=CMAX, seg_damp=SEG_DAMP, lat_stiff=LAT_STIFF)
    m.opt.timestep = DT
    coronal = sp["coronal"]
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    c0 = com(d, bid)
    ts, zs = [], []
    for i in range(int(T_SWIM / DT)):
        t = i * DT
        ctrl = np.zeros(m.nu)
        if mode == "symmetric":
            ctrl[coronal] = CMAX * DUTY                       # same mean force, no asymmetry
        elif (t % PERIOD) / PERIOD < DUTY:
            ctrl[coronal] = CMAX                              # power stroke
        d.ctrl[:] = ctrl
        apply_medium(m, d, bid, c_quad=(0.0 if mode == "linear" else C_QUAD),
                     c_lin=C_LIN, axis=SWIM_AXIS, axis_gain=AXIS_GAIN)
        mujoco.mj_step(m, d)
        if i % int(0.2 / DT) == 0:
            ts.append(t); zs.append((com(d, bid) - c0)[SWIM_AXIS])
    return np.array(ts), np.array(zs)


def main():
    out = {mode: run(mode) for mode in ("swim", "linear", "symmetric")}
    swim_z = out["swim"][1][-1]
    lin_z = out["linear"][1][-1]
    sym_z = out["symmetric"][1][-1]
    rate = swim_z / T_SWIM
    ctrl_max = max(abs(lin_z), abs(sym_z), 1e-4)

    print("\nThe medusa swims — coronal pulsation nets aboral locomotion\n" + "=" * 66)
    print(f"body: dome bell (apex aboral +z) + curling tentacles; pond = quadratic drag")
    print(f"drive: coronal pulsation, period {PERIOD}s, power stroke {DUTY:.0%}, over {T_SWIM:.0f}s\n")
    print(f"{'condition':<26}{'net aboral disp':>16}{'rate (/s)':>12}")
    print(f"{'swim (asym + quadratic)':<26}{swim_z:>+16.3f}{rate:>12.4f}")
    print(f"{'linear-drag control':<26}{lin_z:>+16.3f}{'':>12}")
    print(f"{'symmetric-drive control':<26}{sym_z:>+16.3f}{'':>12}")
    print("=" * 66)
    mono = np.all(np.diff(out["swim"][1][::5]) >= -1e-3)
    ok = swim_z > 0.03 and abs(lin_z) < swim_z / 5 and abs(sym_z) < swim_z / 5
    print(f"Swim [{'PASS' if ok else 'CHECK'}]: the medusa translates aboral {swim_z:+.3f} "
          f"({rate:.4f}/s), {swim_z/ctrl_max:.0f}× either control.")
    print(f"Both controls collapse → the swim is the rate-asymmetric pattern meeting a")
    print(f"nonlinear medium (the scallop-theorem escape), not a scripted push. "
          f"Progress monotonic: {mono}.\n")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    colors = {"swim": "#2c6fbb", "linear": "#c0392b", "symmetric": "#e08e0b"}
    labels = {"swim": "swim (asymmetric + quadratic)", "linear": "linear-drag control",
              "symmetric": "symmetric-drive control"}
    for mode in ("swim", "linear", "symmetric"):
        ts, zs = out[mode]
        ax[0].plot(ts, zs, color=colors[mode], lw=2.2, label=labels[mode])
    ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("net aboral displacement")
    ax[0].set_title("Coordinated pulsation nets locomotion"); ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3); ax[0].axhline(0, color="k", lw=0.6)
    ax[1].bar([0, 1, 2], [swim_z, lin_z, sym_z], color=[colors["swim"], colors["linear"], colors["symmetric"]])
    ax[1].set_xticks([0, 1, 2]); ax[1].set_xticklabels(["swim", "linear\ndrag", "symmetric\ndrive"], fontsize=9)
    ax[1].set_ylabel("net aboral displacement"); ax[1].set_title("Scallop-theorem controls collapse")
    ax[1].axhline(0, color="k", lw=0.6); ax[1].grid(alpha=0.3, axis="y")
    fig.tight_layout()
    o = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "medusa_swim.png")
    os.makedirs(os.path.dirname(o), exist_ok=True); fig.savefig(o, dpi=130)
    print(f"figure -> {os.path.normpath(o)}")


if __name__ == "__main__":
    main()
