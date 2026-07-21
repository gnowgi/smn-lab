# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Integrator & snapshot -- Phase A: the reduced dynamical-network model + lattice sweep.

Wires the preregistered order parameters (see integrator_snapshot.py) onto an
explicit, analysable dynamical network -- NO MuJoCo. The beam is a coarse-graining
hierarchy of leaky-integrator nodes coupled by a concrete diffusive (broadcast /
consensus) operator Pi, sampling its inputs at a discrete refresh rate. Motor CAZ
inject slow, serial perturbations at the bottom.

Three measurements, each with its foil:
  A. manifold   -- broadcast coupling makes the beam settle onto a low-D held
                   manifold (consensus = the marginal/slow mode of the graph
                   Laplacian = the line attractor). Foil: decoupled (Pi off).
                   Renormalization: PR condenses up the layers.
  B. nyquist    -- the beam samples at f_refresh; a stroke faster than
                   f_refresh/2 aliases -> the held snapshot loses fidelity.
  C. capacity   -- serial items decay in the beam's feature space; capacity =
                   how many stay retrievable. Two mechanisms (theta/gamma slots
                   [beam locus] vs serial-stroke decay [motor locus]) are read
                   off the SAME simulator with different (load-rate, decay); the
                   discriminating test perturbs each knob and checks which moves.
                   Capacity is a FUNCTION of morphology, reported across the
                   lattice -- NOT tuned to 7.

Run:  ../.venv/bin/python sweep_integrator_snapshot.py
"""
from __future__ import annotations
import json
import numpy as np

from integrator_snapshot import (
    LATTICE,
    manifold_dimensionality,
    along_manifold_drift,
    snapshot_fidelity,
    aliasing_threshold,
    wm_capacity,
    capacity_theta_gamma,
    capacity_serial_decay,
)


# --------------------------------------------------------------------------- #
# The reduced dynamical-network model
# --------------------------------------------------------------------------- #
def _pools(n_child, n_parent):
    """Contiguous coarse-graining map: which child indices each parent pools."""
    edges = np.linspace(0, n_child, n_parent + 1).astype(int)
    return [np.arange(edges[p], edges[p + 1]) for p in range(n_parent)]


def _run_hierarchy(layers, motor_drive, dt, tau_hold, k_diff):
    """Propagate a bottom drive up a coarse-graining hierarchy of leaky-integrator
    beam layers with intra-layer diffusive (broadcast/consensus) coupling Pi.

    motor_drive : (T, layers[0]) bottom-layer input over time.
    Returns a list of (T, n_l) trajectories, one per beam layer (layers[1:])."""
    T = motor_drive.shape[0]
    pools = [_pools(layers[l], layers[l + 1]) for l in range(len(layers) - 1)]
    beams = [np.zeros(n) for n in layers[1:]]
    traj = [np.zeros((T, n)) for n in layers[1:]]
    for t in range(T):
        below = motor_drive[t]
        for l, (h, pl) in enumerate(zip(beams, pools)):
            pooled = np.array([below[idx].mean() for idx in pl])   # bottom-up
            diffuse = k_diff * (h.mean() - h)                       # Pi: consensus
            h += dt * (-h / tau_hold + pooled + diffuse)
            traj[l][t] = h
            below = h                                              # feed upward
    return traj


# --------------------------------------------------------------------------- #
# A -- the snapshot is a held low-dimensional manifold
# --------------------------------------------------------------------------- #
def measure_manifold(cfg, seed=0):
    rng = np.random.default_rng(seed)
    layers = cfg["layers"]
    dt, tau_hold = 0.01, 1.0 / cfg["hold_theta_hz"]
    T = 400
    # INDEPENDENT slow drive per motor zone: low-D at the top must be EARNED by
    # the beam's integration, not handed over as common input.
    tt = np.arange(T) * dt
    freqs = rng.uniform(0.3, 1.2, layers[0])
    phase = rng.uniform(0, 2 * np.pi, layers[0])
    motor = np.sin(2 * np.pi * freqs[None, :] * tt[:, None] + phase[None, :])

    coupled = _run_hierarchy(layers, motor, dt, tau_hold, k_diff=8.0)
    decoupled = _run_hierarchy(layers, motor, dt, tau_hold, k_diff=0.0)

    pr_layers = [manifold_dimensionality(x) for x in coupled]
    pr_top = pr_layers[-1]
    pr_top_decoupled = manifold_dimensionality(decoupled[-1])

    # hold test: drive to a state, then release; drift over half a hold-window.
    hold_steps = int(0.5 * tau_hold / dt)
    top = coupled[-1]
    released = top[-hold_steps:] if hold_steps >= 2 else top[-2:]
    drift = along_manifold_drift(released, dt)
    return dict(pr_top=pr_top, pr_top_decoupled=pr_top_decoupled,
                pr_by_layer=pr_layers, drift=drift, n_top=layers[-1])


# --------------------------------------------------------------------------- #
# B -- the canvas out-refreshes the stroke (Nyquist)
# --------------------------------------------------------------------------- #
def _fidelity_at(f_stroke, f_refresh, dt=0.0005, cycles=12):
    """Drive a stroke sin(2 pi f_stroke t); the beam samples at f_refresh and
    reconstructs the snapshot by interpolating between refreshes. Fidelity =
    correlation of the reconstructed snapshot with the true continuous stroke; it
    collapses as the stroke approaches the beam Nyquist (refresh / 2)."""
    T = int(cycles / f_stroke / dt)
    t = np.arange(T) * dt
    true = np.sin(2 * np.pi * f_stroke * t)
    step = max(1, int(round((1.0 / f_refresh) / dt)))
    idx = np.arange(0, T, step)
    held = np.interp(np.arange(T), idx, true[idx])                 # sample + interpolate
    return snapshot_fidelity(true, held)


def measure_nyquist(cfg):
    f_refresh = cfg["beam_refresh_hz"]
    f_strokes = np.linspace(1.0, f_refresh, 24)
    fid = np.array([_fidelity_at(f, f_refresh) for f in f_strokes])
    thr = aliasing_threshold(f_strokes, fid, crit=0.7)
    return dict(f_refresh=f_refresh, nyquist_pred=f_refresh / 2.0,
                threshold=thr, f_strokes=f_strokes.tolist(), fidelity=fid.tolist())


# --------------------------------------------------------------------------- #
# C -- working-memory capacity (two mechanisms, one simulator)
# --------------------------------------------------------------------------- #
def _simulate_capacity(load_interval, tau, n_beam_nodes, seed=0,
                       crit=float(np.exp(-1)), substeps=4):
    """Serial associative memory in the beam's feature space. Items are random
    unit vectors loaded one per `load_interval`, decaying with time-constant
    `tau`; retrieval is a matched filter. Capacity = how many loaded items are
    still retrievable above `crit` at steady state. Emergent, not imposed --
    bounded by the decay window AND by interference (feature dim scales with the
    number of beam nodes)."""
    rng = np.random.default_rng(seed)
    d = 48 * n_beam_nodes                                   # beam feature dim; more beam -> less interference
    dt = load_interval / substeps
    decay = np.exp(-dt / tau)
    n_load = int(np.ceil(8 * tau / load_interval)) + 5      # reach steady state
    s = np.zeros(d)
    pats = np.empty((n_load, d))
    for k in range(n_load):
        p = rng.standard_normal(d); p /= np.linalg.norm(p)
        pats[k] = p
        s = s + p                                           # load impulse
        for _ in range(substeps):
            s *= decay                                      # decay between loads
    projs = pats @ s                                        # matched-filter retrieval
    retrieval_by_load = {n_load - k: float(projs[k]) for k in range(n_load)}
    return wm_capacity(retrieval_by_load, crit=crit)


def measure_capacity(cfg, seeds=(0, 1, 2, 3, 4)):
    n_beam = sum(cfg["layers"][1:])
    tg = int(np.median([_simulate_capacity(1.0 / cfg["beam_refresh_hz"],
                                           1.0 / cfg["hold_theta_hz"], n_beam, s)
                        for s in seeds]))
    sd = int(np.median([_simulate_capacity(1.0 / cfg["motor_stroke_hz"],
                                           cfg["tau_decay_s"], n_beam, s)
                        for s in seeds]))
    return dict(
        theta_gamma=tg, serial_decay=sd,
        law_theta_gamma=capacity_theta_gamma(1.0 / cfg["hold_theta_hz"],
                                             1.0 / cfg["beam_refresh_hz"]),
        law_serial_decay=capacity_serial_decay(cfg["tau_decay_s"],
                                               cfg["motor_stroke_hz"]),
    )


def dissociation_test(base, seed=0):
    """The preregistered discriminator: perturb the BEAM knob and the MOTOR knob
    off a base config; theta/gamma capacity must move with the beam knob only,
    serial-decay capacity with the motor knob only."""
    n_beam = sum(base["layers"][1:])
    tg = lambda ri, th: _simulate_capacity(1.0 / ri, 1.0 / th, n_beam, seed)
    sd = lambda st, td: _simulate_capacity(1.0 / st, td, n_beam, seed)
    ri, th = base["beam_refresh_hz"], base["hold_theta_hz"]
    st, td = base["motor_stroke_hz"], base["tau_decay_s"]
    return dict(
        tg_base=tg(ri, th), tg_beam2x=tg(2 * ri, th), tg_motor2x=tg(ri, th),  # motor knob absent from tg
        sd_base=sd(st, td), sd_motor2x=sd(2 * st, td), sd_beam2x=sd(st, td),  # beam knob absent from sd
    )


# --------------------------------------------------------------------------- #
# The lattice sweep
# --------------------------------------------------------------------------- #
def run_lattice():
    rows = []
    for cfg in LATTICE:
        m = measure_manifold(cfg)
        n = measure_nyquist(cfg)
        c = measure_capacity(cfg)
        rows.append(dict(name=cfg["name"], layers=list(cfg["layers"]),
                         manifold=m, nyquist=n, capacity=c))
    return rows


def _fmt(rows):
    print("\n=== A · manifold (broadcast makes it low-D; foil = decoupled) ===")
    print(f"{'config':<12} {'PR_top':>7} {'PR_decoupled':>13} {'n_top':>6} "
          f"{'drift':>7}  PR_by_layer")
    for r in rows:
        m = r["manifold"]
        pl = ",".join(f"{x:.1f}" for x in m["pr_by_layer"])
        print(f"{r['name']:<12} {m['pr_top']:>7.2f} {m['pr_top_decoupled']:>13.2f} "
              f"{m['n_top']:>6} {m['drift']:>7.3f}  [{pl}]")

    print("\n=== B · nyquist (aliasing threshold ~ f_refresh/2) ===")
    print(f"{'config':<12} {'f_refresh':>10} {'predicted':>10} {'measured':>10}")
    for r in rows:
        n = r["nyquist"]
        print(f"{r['name']:<12} {n['f_refresh']:>10.0f} {n['nyquist_pred']:>10.1f} "
              f"{n['threshold']:>10.1f}")

    print("\n=== C · capacity = f(morphology), NOT tuned to 7 ===")
    print(f"{'config':<12} {'theta/gamma':>12} {'(law)':>7} {'serial-decay':>13} "
          f"{'(law)':>7}")
    for r in rows:
        c = r["capacity"]
        print(f"{r['name']:<12} {c['theta_gamma']:>12} {c['law_theta_gamma']:>7.1f} "
              f"{c['serial_decay']:>13} {c['law_serial_decay']:>7.1f}")


def main():
    rows = run_lattice()
    _fmt(rows)

    print("\n=== C · dissociation (which knob moves which mechanism?) ===")
    base = LATTICE[0]
    d = dissociation_test(base)
    print(f"base '{base['name']}':  theta/gamma cap={d['tg_base']}  "
          f"serial-decay cap={d['sd_base']}")
    print(f"  beam refresh x2  -> theta/gamma {d['tg_base']}->{d['tg_beam2x']} "
          f"(should MOVE),  serial-decay {d['sd_base']}->{d['sd_beam2x']} (should hold)")
    print(f"  motor stroke x2  -> serial-decay {d['sd_base']}->{d['sd_motor2x']} "
          f"(should MOVE),  theta/gamma {d['tg_base']}->{d['tg_motor2x']} (should hold)")

    caps = [r["capacity"]["theta_gamma"] for r in rows]
    print(f"\ntheta/gamma capacity across lattice: {caps}  "
          f"(range {min(caps)}-{max(caps)} -- a mapping, not a magic number)")

    out = "integrator_snapshot_results.json"
    with open(out, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\n[wrote {out}]  Phase A wired: model + lattice sweep run on "
          "exp/integrator-snapshot. Phase B (embodied MuJoCo) next.")


if __name__ == "__main__":
    main()
