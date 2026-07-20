# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Resolution exponent: fit R(rho_CAZ) = c * rho^a and characterize the
modulation gate.  Closes P3 of the physicist review -- 'resolution' gets an
operational definition and a *measured exponent*, not a slogan.

Operational definition
  resolution R = world-detection ratio
             = <|world-caused residual|> / <|self-caused residual|>   (dimensionless)
  R = 1 : world indistinguishable from the self-noise floor;  R > 1 : world resolved.
  (This is exactly the order parameter of sweep_q1b_resolution.)

Mechanism -> prediction
  Under per-zone modulation each zone cancels its own self-motion, so the
  self-noise floor averages down as rho^{-1/2} while the *distributed* world
  signal survives averaging.  Hence R ~ rho^{1/2}, i.e. exponent a = 0.5.
  Modulation is the multiplicative GATE (gain mu in [0,1]): mu=0 -> R~1 (foil),
  mu=1 -> R ~ sqrt(rho).  It is a gate, not a second power law.

Pre-registration
  - Order parameter: R (world/self ratio), reused from sweep_q1b_resolution.
  - Density fit: log R = a log rho + c, fitted PER SEED at full modulation (mu=1);
    report a = mean +/- sd.  Pass: a > 0 and consistent with 0.5; foil a <= 0.
  - Gate: at fixed rho, R rises monotonically with mu from ~1 toward sqrt(rho).

Run:  ../.venv/bin/python sweep_resolution_exponents.py
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sweep_q1b_resolution as q1b

N_GRID = [3, 5, 7, 9, 11, 13]        # CAZ density rho
GATE_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
N_FIXED = 9
SEEDS = list(range(6))


# --8<-- [start:resolution]
def ratio(N, gain, seed):
    """Resolution = world-detection ratio at CAZ density N and modulation gain."""
    log = q1b.run_one({"n_seg": N, "mode": "modulated", "gain": gain}, seed)
    return q1b.summarize(log, None, seed)["ratio"]


def density_slopes(gain):
    """Per-seed slope of log R vs log rho, and mean R at each rho."""
    slopes = []
    R_by_N = {N: [] for N in N_GRID}
    for s in SEEDS:
        logR = []
        for N in N_GRID:
            R = ratio(N, gain, s)
            R_by_N[N].append(R)
            logR.append(np.log(max(R, 1e-9)))
        slopes.append(float(np.polyfit(np.log(N_GRID), logR, 1)[0]))   # a per seed
    return np.array(slopes), R_by_N
# --8<-- [end:resolution]


def main():
    figdir = os.path.join(os.path.dirname(__file__), "..", "figures")
    os.makedirs(figdir, exist_ok=True)

    a_mod, Rmod = density_slopes(1.0)
    a_foil, Rfoil = density_slopes(0.0)

    def fmt(a):
        return f"{a.mean():+.3f} +/- {a.std(ddof=1):.3f} (95% CI +/-{1.96*a.std(ddof=1)/np.sqrt(len(a)):.3f}, N={len(a)})"

    print("\n[resolution] density exponent a in  R ~ rho_CAZ^a")
    print(f"  full modulation (mu=1): a = {fmt(a_mod)}    [predicted 0.5]")
    print(f"  foil            (mu=0): a = {fmt(a_foil)}")
    print("  mean R(rho) at mu=1:", {N: round(float(np.mean(Rmod[N])), 2) for N in N_GRID})
    print("  mean R(rho) at mu=0:", {N: round(float(np.mean(Rfoil[N])), 2) for N in N_GRID})

    print(f"\n[resolution] modulation gate  R(mu) at rho={N_FIXED}")
    Rg = {}
    for g in GATE_GRID:
        rs = [ratio(N_FIXED, g, s) for s in SEEDS]
        Rg[g] = (float(np.mean(rs)), float(np.std(rs, ddof=1)))
        print(f"  mu={g:.2f}:  R = {Rg[g][0]:6.2f} +/- {Rg[g][1]:.2f}")

    # ---------- figure ----------
    Ns = np.array(N_GRID, float)
    mmod = np.array([np.mean(Rmod[N]) for N in N_GRID])
    a_hat = float(a_mod.mean())
    c_hat = float(np.mean([np.log(np.mean(Rmod[N])) - a_hat * np.log(N) for N in N_GRID]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    ax1.loglog(Ns, mmod, "o", color="#1538a0", label="modulation ($\\mu{=}1$)")
    ax1.loglog(Ns, np.exp(c_hat) * Ns ** a_hat, "-", color="#1538a0",
               label=f"fit  $a={a_hat:.2f}$")
    ax1.loglog(Ns, [np.mean(Rfoil[N]) for N in N_GRID], "s--", color="#c9a23a",
               label="foil ($\\mu{=}0$)")
    ax1.loglog(Ns, mmod[0] * (Ns / Ns[0]) ** 0.5, ":", color="gray",
               label="slope $0.5$ ($\\sqrt{\\rho}$)")
    ax1.set_xlabel("CAZ density  $\\rho$  (segment count)")
    ax1.set_ylabel("resolution  $R$ = world/self ratio")
    ax1.set_title("density exponent", fontsize=10)
    ax1.legend(fontsize=8)

    gs = np.array(GATE_GRID)
    ax2.errorbar(gs, [Rg[g][0] for g in GATE_GRID], yerr=[Rg[g][1] for g in GATE_GRID],
                 fmt="o-", color="#1538a0", capsize=3)
    ax2.set_xlabel("modulation gain  $\\mu$")
    ax2.set_ylabel(f"resolution $R$  ($\\rho{{=}}{N_FIXED}$)")
    ax2.set_title("modulation gate", fontsize=10)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(figdir, "sweep_resolution_exponents.png")
    fig.savefig(out, dpi=130)
    print(f"\n[saved] {out}")


if __name__ == "__main__":
    main()
