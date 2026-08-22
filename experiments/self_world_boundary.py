# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The self/world boundary is EARNED -- a constant load becomes self, a moving prey stays world.

Question (G. Nagarjuna): if a force is applied at a node at t0 and is still there at
t1..tn, it is just a weight at that node. How does the agent know it is NOT part of the
body, since it is constantly there?

Answer: it does not -- and should not. The self/world cut is not about where a force
comes from; it is about whether it produces ONGOING, UNPREDICTED change. The agent
carries a slowly-adapting baseline (the self-model's expectation = the forward model).
The reafference residual is (actual - baseline). A CONSTANT load makes one transient and
then settles; the baseline tracks it, the residual decays to ~0 -> the load is ABSORBED
INTO THE SELF (recalibrated as body). A MOVING prey keeps changing faster than the
baseline can track; the residual stays elevated -> it stays WORLD (an other). Habituation
is exactly this: you stop feeling your clothes; a barnacle becomes part of the whale.

On the two-layered creature: apply the same-magnitude force at one ectoderm zone, once
constant, once moving. Order parameter: the reafference residual (world-signal) over time
-- it decays for the constant load (self) and persists for the moving prey (world). A
control: after the constant load is absorbed, REMOVING it is itself a world-event (the
baseline expected it) -- proof the load had truly become self.

Run:  ../.venv/bin/python self_world_boundary.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hydra_sac import build, N_COL, N_ROW, DT


NOUT = N_COL * N_ROW


def io(r, c):                # outer-shell (ectoderm) node index, per hydra_sac.sac_spec
    return r * N_COL + c


def ii(r, c):                # inner-shell (endoderm) node index
    return NOUT + r * N_COL + c


# the aboral (foot) end is anchored -- a sessile animal; a constant force then reaches a
# static equilibrium (springs balance it) instead of drifting the whole body away.
FOOT = ([io(r, N_COL - 1) for r in range(N_ROW)] + [ii(r, N_COL - 1) for r in range(N_ROW)]
        + [2 * NOUT, 2 * NOUT + 1])


KA, CA = 80.0, 8.0           # soft (spring-damper) anchor: holds the foot near rest smoothly


def anchor(d, bid, pos0):
    for j in FOOT:
        aj = bid[j]
        d.xfrc_applied[aj, 0:3] = -KA * (d.xpos[aj] - pos0[j]) - CA * d.qvel[3 * j:3 * j + 3]

TAU = 1.5                    # self-model adaptation timescale (s): slow (absorbs the constant)
PRESS_S, HOLD_S, RELEASE_S = 0.5, 25.0, 2.0
FORCE = 8.0
PREY_HZ = 1.5                # struggle freq: body FOLLOWS it, but the slow baseline cannot track it


def run(kind, k):
    m, d, bid, *_ = build()
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    nseg = len(bid)
    pos0 = np.array([d.xpos[bid[i]].copy() for i in range(nseg)])
    baseline = np.zeros((nseg, 3))          # the self-model's expected displacement (adapts)
    alpha = DT / TAU
    n_press, n_hold, n_rel = (int(PRESS_S / DT), int(HOLD_S / DT), int(RELEASE_S / DT))
    ws, phase = [], []
    for i in range(n_press + n_hold + n_rel):
        d.xfrc_applied[:] = 0
        on = i >= n_press and i < n_press + n_hold        # the load/prey is present during HOLD
        if on:
            t = (i - n_press) * DT
            ramp = min(1.0, t / 0.5)                       # smooth onset -> avoids step-ringing
            f = FORCE * ramp if kind == "constant" else FORCE * ramp * np.sin(2 * np.pi * PREY_HZ * t)
            d.xfrc_applied[bid[k], 2] = f
        anchor(d, bid, pos0)
        mujoco.mj_step(m, d)
        disp = np.array([d.xpos[bid[j]] for j in range(nseg)]) - pos0
        baseline += alpha * (disp - baseline)             # the self-model tracks slow change
        resid = disp - baseline                            # reafference residual = world-caused
        ws.append(float(np.linalg.norm(resid[k])))         # world-signal at the loaded zone
        phase.append(2 if (not on and i >= n_press) else (1 if on else 0))
    return np.array(ws), np.array(phase)


def main():
    k = io(2, N_COL // 2)                                # an ectoderm zone (outer shell)
    ws_c, ph = run("constant", k)
    ws_m, _ = run("moving", k)
    t = np.arange(len(ws_c)) * DT
    hold = ph == 1
    # settled world-signal = mean over the last 40% of the HOLD window
    hold_idx = np.where(hold)[0]
    tail = hold_idx[int(0.6 * len(hold_idx)):]
    settled_c = float(ws_c[tail].mean()); settled_m = float(ws_m[tail].mean())
    peak_c = float(ws_c[hold_idx[:len(hold_idx)//10]].max())   # onset transient (constant)
    # the removal control: world-signal right after the constant load is released
    rel_idx = np.where(ph == 2)[0]
    removal_spike = float(ws_c[rel_idx[:len(rel_idx)//5]].max()) if len(rel_idx) else 0.0

    print("\nThe self/world boundary is EARNED -- constant load -> self, moving prey -> world\n" + "=" * 74)
    print(f"two-layered creature; same force at ectoderm zone {k}; adaptation TAU={TAU}s")
    print(f"reafference residual (world-signal) at the zone:")
    print(f"  CONSTANT load : onset transient {peak_c:.4f}  ->  SETTLED {settled_c:.4f}  (absorbed into self)")
    print(f"  MOVING prey   :                         SETTLED {settled_m:.4f}  (stays world)")
    print(f"  ratio moving/constant (settled) = {settled_m/max(settled_c,1e-9):.0f}x")
    print(f"  CONTROL -- removing the absorbed constant load spikes the residual to "
          f"{removal_spike:.4f}")
    print(f"            (its removal is now a WORLD-event: the load had become self)")
    ok = settled_m > 3 * settled_c and peak_c > 2.5 * settled_c and removal_spike > 2.5 * settled_c
    print("=" * 74)
    print(f"Verdict [{'PASS' if ok else 'CHECK'}]: a constantly-present force is absorbed into the self-model")
    print(f"(residual decays to ~0); only ONGOING, unpredicted change (the moving prey) stays world.")
    print(f"The agent cannot -- and need not -- tell a constant load from the body; the reafference")
    print(f"cut earns the boundary. Removing the absorbed load is itself a world-event.\n")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
    ax[0].axvspan(PRESS_S, PRESS_S + HOLD_S, color="#f2f2f2", label="load / prey present")
    ax[0].plot(t, ws_c, color="#2c9e5b", lw=2.2, label="constant load")
    ax[0].plot(t, ws_m, color="#c0392b", lw=2.0, label="moving prey")
    ax[0].axvline(PRESS_S + HOLD_S, ls="--", color="0.5", lw=1)
    ax[0].annotate("removal = world-event", (PRESS_S + HOLD_S, removal_spike),
                   fontsize=8, color="#2c9e5b", xytext=(PRESS_S + HOLD_S + 0.2, removal_spike),
                   va="bottom")
    ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("reafference residual (world-signal)")
    ax[0].set_title("Constant load is absorbed into the self;\nmoving prey stays world")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
    ax[1].bar([0, 1], [settled_c, settled_m], color=["#2c9e5b", "#c0392b"])
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["constant load\n(became self)", "moving prey\n(stays world)"])
    ax[1].set_ylabel("settled world-signal"); ax[1].set_title("After adaptation: only change is 'world'")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "self_world_boundary.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
