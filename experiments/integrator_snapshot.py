# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Integrator & snapshot -- the beam holds the canvas: STARTER / PREREGISTRATION.

Status: PREREGISTERED, implementation in progress (branch exp/integrator-snapshot).

The broadcasting beam (the integrating network / nervous system) is a fast,
two-timescale integrator that *holds* a low-dimensional snapshot of a body whose
motor zones can only stroke it slowly and serially. Three order parameters:

  A. dimensionality -- the snapshot is a held low-dimensional manifold.
  B. nyquist        -- the beam refresh must exceed the fastest stroke, else the
                       held snapshot aliases (a temporal-resolution condition).
  C. capacity       -- working-memory capacity is a FUNCTION of morphology, read
                       off the configuration lattice; NOT tuned to 7. Two
                       mechanisms are run as distinct points in the config space
                       (theta/gamma slots vs serial-stroke decay), each with a
                       preregistered law that responds to a different knob.

Pre-registration: see docs/experiments/integrator_snapshot.md for the full
hypotheses, matched foils, pass/falsify thresholds, and the discriminating
design. The estimators below are the single source of truth for those order
parameters.

Run:  ../.venv/bin/python integrator_snapshot.py
"""
from __future__ import annotations
import numpy as np


# --8<-- [start:dimensionality]
def manifold_dimensionality(states):
    """Order parameter A: the effective dimensionality of the beam's held state,
    as the participation ratio of the top-layer covariance spectrum,
    PR = (sum lambda)^2 / sum(lambda^2). A held low-dimensional manifold (a line
    or plane attractor) gives PR ~ 1-2; an unintegrated scatter gives PR ~ D.
    `states` is a (T, D) top-layer trajectory."""
    X = np.asarray(states, float)
    X = X - X.mean(axis=0, keepdims=True)
    lam = np.clip(np.linalg.eigvalsh(np.cov(X, rowvar=False)), 0.0, None)
    return float(lam.sum() ** 2 / (lam ** 2).sum()) if lam.sum() > 0 else 0.0


def along_manifold_drift(states_after_release, dt):
    """Companion to A: the drift speed of the held state after the driving stroke
    is removed (RMS step along the trajectory per unit time). A true line
    attractor holds (drift ~ 0); a point attractor relaxes away; instability
    diverges."""
    X = np.asarray(states_after_release, float)
    if len(X) < 2:
        return 0.0
    return float(np.sqrt((np.diff(X, axis=0) ** 2).sum(axis=1)).mean() / dt)
# --8<-- [end:dimensionality]


# --8<-- [start:nyquist]
def snapshot_fidelity(true_stroke, held_snapshot):
    """Order parameter B (pointwise): the correlation between the driving stroke
    pattern and the beam-held snapshot's reconstruction of it. Falls toward 0 as
    the stroke frequency approaches/exceeds the beam Nyquist (refresh / 2)."""
    a = np.asarray(true_stroke, float); b = np.asarray(held_snapshot, float)
    a = a - a.mean(); b = b - b.mean()
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / d) if d > 0 else 0.0


def aliasing_threshold(f_stroke, fidelity, crit=0.7):
    """Order parameter B (summary): the lowest stroke frequency at which snapshot
    fidelity drops below `crit` -- predicted ~ beam_refresh / 2 (Nyquist).
    Returns inf if fidelity never falls below criterion in the swept range."""
    f = np.asarray(f_stroke, float); y = np.asarray(fidelity, float)
    below = np.where(y < crit)[0]
    return float(f[below[0]]) if below.size else float("inf")
# --8<-- [end:nyquist]


# --8<-- [start:capacity]
def wm_capacity(retrieval_by_load, crit=0.5):
    """Order parameter C: working-memory capacity = the largest serial load whose
    retrieval accuracy stays above `crit`. `retrieval_by_load` is {N_items: acc}.
    This is a quantity READ OFF a configuration -- NOT a target. Human ~7 is one
    point on the curve; a configuration at 70 is a valid prediction. The result
    is the mapping capacity(morphology), reported across the whole lattice
    (failures included), not any single value."""
    ok = [n for n, acc in sorted(retrieval_by_load.items()) if acc >= crit]
    return max(ok) if ok else 0
# --8<-- [end:capacity]


# --8<-- [start:laws]
def capacity_theta_gamma(tau_hold, dt_refresh):
    """Preregistered law, mechanism A (BEAM locus): capacity = hold-window /
    refresh-slot = theta/gamma ratio. Discriminating prediction: perturb the beam
    bands (refresh, hold) and capacity shifts; perturb the motor CAZ and it does
    not."""
    return tau_hold / dt_refresh


def capacity_serial_decay(tau_decay, f_stroke):
    """Preregistered law, mechanism B (MOTOR locus): capacity = decay-time *
    stroke-rate. Discriminating prediction: perturb the motor rate/decay and
    capacity shifts; perturb the beam bands and it does not."""
    return tau_decay * f_stroke
# --8<-- [end:laws]


# The configuration lattice IS the experimental variable (Phase II: morphology
# sets computational capacity). Each row is one body; the sweep reports
# capacity(config), not a target number. `layers` is the coarse-graining
# hierarchy (motor CAZ -> beam integrators).
LATTICE = [
    dict(name="mammal-like", layers=(36, 9, 3),
         beam_refresh_hz=40.0, hold_theta_hz=6.0, motor_stroke_hz=5.0, tau_decay_s=1.2),
    dict(name="fast-beam",   layers=(36, 9, 3),
         beam_refresh_hz=80.0, hold_theta_hz=6.0, motor_stroke_hz=5.0, tau_decay_s=1.2),
    dict(name="slow-hold",   layers=(36, 9, 3),
         beam_refresh_hz=40.0, hold_theta_hz=3.0, motor_stroke_hz=5.0, tau_decay_s=1.2),
    dict(name="fast-motor",  layers=(36, 9, 3),
         beam_refresh_hz=40.0, hold_theta_hz=6.0, motor_stroke_hz=9.0, tau_decay_s=1.2),
    dict(name="long-decay",  layers=(36, 9, 3),
         beam_refresh_hz=40.0, hold_theta_hz=6.0, motor_stroke_hz=5.0, tau_decay_s=6.0),
    dict(name="deep-tree",   layers=(27, 9, 3, 1),
         beam_refresh_hz=40.0, hold_theta_hz=6.0, motor_stroke_hz=5.0, tau_decay_s=1.2),
]


def _self_test():
    """Synthetic self-test of the three estimators (NOT a bench measurement):
    recover a known dimensionality, aliasing threshold, and capacity, and show
    the two capacity laws respond to different knobs. Wiring the layered-network
    model and the lattice sweep is the next step."""
    rng = np.random.default_rng(0)

    # A: an (essentially) 1-D held manifold -> PR ~ 1; a full-rank scatter -> PR ~ D.
    t = np.linspace(0, 1, 500)
    line = np.outer(np.sin(2 * np.pi * t), [1, 0.5, -0.3, 0.2, 0.1]) + rng.normal(0, 1e-3, (500, 5))
    scatter = rng.normal(0, 1, (500, 5))
    print(f"[A dimensionality] held-manifold PR={manifold_dimensionality(line):.2f} "
          f"(expect ~1)   scatter PR={manifold_dimensionality(scatter):.2f} (expect ~5)")

    # B: fidelity high below a Nyquist cut, collapsing above it -> threshold recovered.
    f = np.arange(1, 21, dtype=float)
    fid = np.where(f < 10.0, 0.95, 0.1)
    print(f"[B nyquist] aliasing_threshold={aliasing_threshold(f, fid):.1f} (expect ~10)")

    # C: retrieval stays above criterion up to a load, then falls -> capacity recovered.
    retr = {n: (1.0 if n <= 7 else 0.2) for n in range(1, 12)}
    print(f"[C capacity] wm_capacity={wm_capacity(retr)} (expect 7 for THIS synthetic body)")

    # C-laws: each responds to its own knob only.
    print(f"[C law A theta/gamma] cap={capacity_theta_gamma(1/6, 1/40):.1f} "
          f"(beam knob); doubling refresh -> {capacity_theta_gamma(1/6, 1/80):.1f}")
    print(f"[C law B serial-decay] cap={capacity_serial_decay(1.2, 5.0):.1f} "
          f"(motor knob); doubling stroke-rate -> {capacity_serial_decay(1.2, 10.0):.1f}")

    print(f"[lattice] {len(LATTICE)} configurations preregistered; the sweep reports "
          "capacity(config), failures included -- not a target.")
    print("[integrator-snapshot] status: PREREGISTERED -- the layered-network model "
          "and lattice sweep are not yet wired. See "
          "docs/experiments/integrator_snapshot.md.")


if __name__ == "__main__":
    _self_test()
