# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""R4 -- world-model adaptation dynamics (kappa > 0): STARTER / PREREGISTRATION.

Status: PREREGISTERED, implementation in progress (branch exp/r4-adaptation).

Mastery of the world is not only a *static* decoding skill (cf. S1/Q1) but an
adaptation *process*: after the world changes, the world-model re-fits and the
rolling-RMS reafference residual decays back toward the noise floor. R4 measures
that decay.

Pre-registration
----------------
- Hypothesis: after a step change in the world (a field remap / an object move),
  the rolling-RMS reafference residual decays toward the noise floor at a rate
  kappa > 0 under modulation; a non-modulatory foil does not adapt (kappa ~ 0;
  the residual stays elevated).
- Order parameter: kappa, the exponential decay rate of the post-change
  rolling-RMS residual (fit r(t) = r_inf + (r0 - r_inf) * exp(-kappa t)).
- Matched foil: the unmodulated control (same body, same world change,
  modulation off).
- Pass: kappa_SMN > 0 and the residual returns to within 10% of the noise floor;
  foil kappa ~ 0 (no return).
- Falsify: kappa ~ 0 under modulation -> mastery is not a dynamic process here.

Run:  ../.venv/bin/python sweep_r4_adaptation.py
"""
from __future__ import annotations
import numpy as np


# --8<-- [start:kappa]
def adaptation_rate(t, residual_rms):
    """Order parameter kappa: the decay rate of the rolling-RMS reafference
    residual after a world-state change. Fits r(t) = r_inf + (r0 - r_inf) *
    exp(-kappa t) by a log-linear regression on (r - r_inf), with the noise
    floor r_inf estimated from the tail. Returns (kappa, r_inf)."""
    t = np.asarray(t, float)
    r = np.asarray(residual_rms, float)
    r_inf = float(np.mean(r[-max(1, len(r) // 5):]))    # noise floor = last 20%
    y = r - r_inf
    mask = y > 1e-9                                      # regress only above floor
    if mask.sum() < 2:
        return 0.0, r_inf
    slope = np.polyfit(t[mask], np.log(y[mask]), 1)[0]
    return float(-slope), r_inf
# --8<-- [end:kappa]


def _self_test():
    """Synthetic self-test of the estimator (NOT a bench measurement): generate a
    decay with a known kappa and confirm it is recovered. The modulated-vs-foil
    sweep on the two-CAZ body is the next step to wire in."""
    rng = np.random.default_rng(0)
    t = np.linspace(0.0, 5.0, 400)
    kappa_true, r0, r_inf = 1.5, 1.0, 0.05
    r = r_inf + (r0 - r_inf) * np.exp(-kappa_true * t) + rng.normal(0, 0.005, t.shape)
    kappa_hat, floor_hat = adaptation_rate(t, r)
    print(f"[R4 estimator self-test] kappa_true={kappa_true:.2f} "
          f"kappa_hat={kappa_hat:.2f} floor_hat={floor_hat:.3f}")
    print("[R4] status: PREREGISTERED -- the modulated-vs-foil bench sweep is "
          "not yet wired. See docs/experiments/sweep_r4_adaptation.md.")


if __name__ == "__main__":
    _self_test()
