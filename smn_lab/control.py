# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""SMN control layer for the embodied bench.

These classes implement components of the Sensation Modulating Network
architecture (Nagarjuna & Karnam, arXiv:2605.26856) as controllers that drive
and read a physical MuJoCo body:

- OpponentBoard        -- a zone's communication board: routes a desired
                          modulation into pull-only antagonist activations.
- ReafferencePredictor -- a forward model keyed on the agent's own state; its
                          residual is the reafference signal that separates
                          self-caused from world-caused sensory change.

Keeping these in the control layer (rather than in MuJoCo physics) is deliberate:
the modulatory coupling -- the "balance beam" -- is the experiment's independent
variable, and lives here where it can be swapped (layered/distributed, +/-BAP,
+/-HAP).
"""
from __future__ import annotations
import numpy as np


class OpponentBoard:
    """Communication board for one CAZ: convert a desired joint torque into
    pull-only antagonist activations (a_right, a_left).

    A PD law on the commanded angle produces a desired torque; positive torque
    recruits the 'right' puller, negative the 'left'. `cocontraction` adds a
    tonic antagonist tone (a minimal stand-in for BAP-like baseline drive).
    """

    def __init__(self, kp: float = 3.0, kd: float = 0.3,
                 cmax: float = 1.5, cocontraction: float = 0.0):
        self.kp = kp
        self.kd = kd
        self.cmax = cmax
        self.coc = cocontraction

    # --8<-- [start:opponent_commands]
    def commands(self, theta, theta_dot, theta_cmd, theta_dot_cmd):
        tau = self.kp * (theta_cmd - theta) + self.kd * (theta_dot_cmd - theta_dot)
        a_r = float(np.clip(tau, 0.0, self.cmax))
        a_l = float(np.clip(-tau, 0.0, self.cmax))
        if self.coc:
            a_r = min(self.cmax, a_r + self.coc)
            a_l = min(self.cmax, a_l + self.coc)
        return a_r, a_l, tau
    # --8<-- [end:opponent_commands]


class AlertEnergyBoard:
    """The haltability operator + board routing of a single CAZ (the alert-energy
    and board equations of the preprint).

    The board's state variable is the ALERT ENERGY ``E_R`` -- the metabolic cost of
    holding a recruited co-activation. It accumulates in proportion to the active
    zone's load while driving, and decays passively::

        dE_R/dt = rho * F_active * 1[g=1]  -  E_R / tau_E

    Two consequences, both testable, distinguish this from classical inhibition:

    - the partner (inactive) zone is tonically engaged at ``a0 + beta*E_R``, so the
      partner's tone RISES with the active zone's load (Register 1); its steady
      state is ``a0 + beta*rho*tau_E*F_active`` (linear in load);
    - when the active zone flips (drive changes sign), the previously-alert zone's
      drive is amplified by ``(1 + gamma*E_R)`` -- a post-halt resumption advantage
      (Register 2).

    The matched foil is ``classical=True`` (classical reciprocal inhibition): no
    alert energy, the partner held flat at ``a0``, no post-flip amplification.
    """

    def __init__(self, kp=3.0, kd=0.3, cmax=1.5, a0=0.1,
                 rho=1.0, tau_E=2.0, beta=0.6, gamma=1.0, dt=0.002,
                 classical=False):
        self.kp, self.kd, self.cmax, self.a0 = kp, kd, cmax, a0
        self.rho, self.tau_E, self.beta, self.gamma = rho, tau_E, beta, gamma
        self.dt = dt
        self.classical = classical
        self.E_R = 0.0

    # --8<-- [start:alert_energy]
    def _update_energy(self, F_active, gated):
        # dE_R/dt = rho * F_active * 1[g=1]  -  E_R / tau_E
        build = self.rho * F_active if gated else 0.0
        self.E_R += self.dt * (build - self.E_R / self.tau_E)
        return self.E_R
    # --8<-- [end:alert_energy]

    # --8<-- [start:alert_board]
    def commands(self, theta, theta_dot, theta_cmd, theta_dot_cmd, gated=True):
        """Route a desired configuration into pull-only antagonist activations
        (a_right, a_left), with partner tone and post-flip amplification set by the
        alert energy. Returns (a_r, a_l, drive, F_active, E_R)."""
        drive = self.kp * (theta_cmd - theta) + self.kd * (theta_dot_cmd - theta_dot)
        F_active = min(self.cmax, abs(drive))              # the active zone's force
        E = self._update_energy(F_active, gated)
        partner = self.a0 + (0.0 if self.classical else self.beta * E)
        if not gated:                                      # halt: both at baseline
            a = float(np.clip(self.a0, 0.0, self.cmax))
            return a, a, drive, F_active, E
        if drive >= 0:                                     # right active, left = partner
            a_r = float(np.clip(drive, 0.0, self.cmax))
            a_l = float(np.clip(partner, 0.0, self.cmax))
        else:                                              # left active (post-flip amplified)
            amp = 1.0 if self.classical else (1.0 + self.gamma * E)
            a_l = float(np.clip(-drive * amp, 0.0, self.cmax))
            a_r = float(np.clip(partner, 0.0, self.cmax))
        return a_r, a_l, drive, F_active, E
    # --8<-- [end:alert_board]


class ReafferencePredictor:
    """Forward model keyed on self-state (yaw angle).

    During a self-motion learning phase the agent observes, for each heading,
    the whisker reading produced by its *own* movement in a static world, and
    learns the contingency r = g(theta) as a binned running mean. Thereafter it
    predicts the expected reading from efference/proprioception alone, and the
    residual (actual - predicted) is the reafference signal:

        ~ sensor noise floor  for self-caused change (world static)
        >> noise floor        for world-caused change (exafference)

    This is the embodied form of Register 3 (reafference: self vs world).
    """

    def __init__(self, n_bins: int = 72, theta_range=(-np.pi, np.pi)):
        self.n_bins = n_bins
        self.lo, self.hi = theta_range
        self.sum = np.zeros(n_bins)
        self.cnt = np.zeros(n_bins)
        self._global = None

    def _bin(self, theta: float) -> int:
        # wrap to [lo, hi)
        span = self.hi - self.lo
        x = (theta - self.lo) % span
        return min(self.n_bins - 1, int(self.n_bins * x / span))

    def update(self, theta: float, reading: float) -> None:
        b = self._bin(theta)
        self.sum[b] += reading
        self.cnt[b] += 1
        self._global = None  # invalidate cache

    def predict(self, theta: float) -> float:
        b = self._bin(theta)
        if self.cnt[b] > 0:
            return self.sum[b] / self.cnt[b]
        # fall back to the global learned mean if this heading was never seen
        if self._global is None:
            seen = self.cnt > 0
            self._global = (self.sum[seen].sum() / self.cnt[seen].sum()
                            if seen.any() else 0.0)
        return self._global

    def residual(self, theta: float, reading: float) -> float:
        return reading - self.predict(theta)


class BAPG:
    """Basal Action Pattern Generator -- the SMN's distributed, innermost layer:
    an endogenous self-propulsive drive (optionally a gentle oscillation) that the
    affordance/haltable layers (HAP) gate. Unlike a *central* pattern generator
    (CPG), the BAPG is not central: it is the floor of the architecture, the
    evolutionarily ancient innermost layer, distributed across the body's zones.
    It supplies the continuous baseline modulation that fills the spaces *between*
    the discrete differentiae -- which is why the constructed world is not
    pixelated: it is generated by coupled dynamical systems, not by linear
    algebra."""

    def __init__(self, thrust: float = 0.8, osc_amp: float = 0.0, freq: float = 1.0):
        self.thrust = thrust
        self.osc_amp = osc_amp
        self.w = 2 * np.pi * freq

    def drive(self, t: float) -> float:
        return self.thrust * (1.0 + self.osc_amp * np.sin(self.w * t))


CPG = BAPG          # deprecated alias: the literature's term; we use BAPG.


class HAPExplorer:
    """A Haltable Action Pattern recruited by whisker affordances: cruise toward
    open space, and -- when the forward arc is blocked -- halt the drive and
    rotate in place toward the more open side until the way is clear. It thus
    interrupts and recomposes the BAP-driven locomotion on the basis of what the
    transducers sense.

    `command(dists)` returns `(heading_offset, drive_gate)`:
      heading_offset -- per-step turn command (rad; + = toward the agent's left);
      drive_gate     -- in [0, 1], multiplies the BAP thrust (0 = halt).
    """

    def __init__(self, angles_rad, d_halt: float = 0.4, d_go: float = 0.7,
                 turn: float = 0.9, steer_gain: float = 0.5, d_cap: float = 1.6,
                 wander: float = 0.05, flip_prob: float = 0.15,
                 routing: str = "flat", seed: int = 0):
        self.angles = np.asarray(angles_rad, dtype=float)
        self.d_halt = d_halt
        self.d_go = d_go
        self.turn = turn
        self.steer_gain = steer_gain
        self.d_cap = d_cap
        self.wander = wander
        self.flip_prob = flip_prob
        self.routing = routing            # "flat" | "hierarchical" -- the balance-beam topology
        self.rng = np.random.default_rng(seed)
        self.front_mask = np.abs(self.angles) <= np.radians(45) + 1e-6
        # whisker groups for hierarchical (layered) routing
        self._groups = [self.angles > np.radians(15),
                        np.abs(self.angles) <= np.radians(15),
                        self.angles < -np.radians(15)]
        self.turning = False
        self.sign = 1.0

    def _steer_offset(self, d):
        """Route whisker clearances into a steering angle. `flat`: pool all
        whiskers at once (distributed). `hierarchical`: summarize each whisker
        group first (layer 1), then combine the group summaries (layer 2)."""
        if self.routing == "flat":
            return float((self.angles * d).sum() / max(d.sum(), 1e-6))
        ga, gc = [], []
        for m in self._groups:
            if m.any():
                ga.append(float(self.angles[m].mean()))
                gc.append(float(d[m].mean()))
        ga, gc = np.array(ga), np.array(gc)
        return float((ga * gc).sum() / max(gc.sum(), 1e-6))

    def command(self, dists):
        d = np.clip(np.asarray(dists, dtype=float), 0.0, self.d_cap)
        front = float(d[self.front_mask].min())
        # enter a committed turn when the forward arc is blocked
        if not self.turning and front < self.d_halt:
            self.turning = True
            left, right = d[self.angles > 0].sum(), d[self.angles < 0].sum()
            self.sign = 1.0 if left >= right else -1.0
            if self.rng.random() < self.flip_prob:   # occasional flip breaks limit cycles
                self.sign = -self.sign
        if self.turning:
            if front > self.d_go:                     # cleared: resume cruising
                self.turning = False
            else:
                return self.sign * self.turn, 0.0     # halt and rotate in place
        # cruise: steer toward open space, via the configured routing topology
        offset = self.steer_gain * self._steer_offset(d)
        offset += self.rng.normal(0.0, self.wander)
        gate = float(np.clip((front - self.d_halt) / (self.d_go - self.d_halt), 0.0, 1.0))
        return offset, gate


class DifferentialDrive:
    """Communication board for the two located rear drive zones. It converts a
    desired (forward, turn) command into pull-only activations of the drive
    modulators, and computes the net body-frame force and z-torque from the
    zones' positions -- so locomotion and steering both emerge from the body
    geometry rather than from a central thrust."""

    def __init__(self, schema, amax: float = 1.2, turn_gain: float = 1.0):
        self.zones = schema.drive_zones
        self.amax = amax
        self.turn_gain = turn_gain

    def activations(self, forward: float, turn: float) -> dict:
        # Each drive zone is an opponent pair (a forward AND a backward puller),
        # so its net activation is signed. This is what lets the agent rotate in
        # place: drive_L backward + drive_R forward gives pure torque, no net
        # force -- impossible with forward-only thrusters.
        d = self.turn_gain * turn
        return {"drive_L": float(np.clip(forward - d, -self.amax, self.amax)),
                "drive_R": float(np.clip(forward + d, -self.amax, self.amax))}

    def wrench(self, acts: dict):
        """Net body-frame forward force Fx and z-torque tau from the located,
        pull-only forward drives (force F at (x, y) gives z-torque -y*F)."""
        Fx = float(sum(acts.values()))
        tau = float(sum(-y * acts[name] for name, (x, y) in self.zones.items()))
        return Fx, tau


class SaccadeController:
    """A minimal saccade generator for one rotational eye DOF.

    The eye fixates at a target angle for ``fixation_s`` seconds and then
    jumps to a new uniformly-random target within ``[-range, +range]``. Paired
    with an ``OpponentBoard`` driving the eye joint, this produces basic
    saccade-and-fixation behaviour: brief, fast traverses between stable
    fixations.

    This is intentionally the simplest possible eye motor; the architecturally
    interesting fact is that whichever CAZ pair produces a motion -- body or
    eye -- the modulator must predict its sensory consequences away. The
    bench's first multi-CAZ-eye experiment uses this controller with the
    forward model summing head_yaw + eye_yaw before predicting the frame.
    """

    def __init__(self, range_rad: float, fixation_s: float = 0.30,
                 seed: int = 0):
        self.range = float(range_rad)
        self.fixation_s = float(fixation_s)
        self.rng = np.random.default_rng(seed)
        self.target = 0.0
        self.t_next = 0.0

    def update(self, t: float) -> float:
        if t >= self.t_next:
            self.target = float(self.rng.uniform(-self.range, self.range))
            self.t_next = t + self.fixation_s
        return self.target


class CrossModalBoard:
    """Cross-modal communication board -- the 'balance beam' for the object
    discrimination experiment, and that experiment's independent variable.

    Each modality delivers one scalar feature reading about the object in front
    of the agent (touch -> angular extent; vision -> luminance; taste -> chemical
    signature). The board does two things, and both are the SMN claim under test:

      (a) **Modulation.** Each reading is gated against a per-modality noise
          floor: only a reading whose margin from the decision boundary exceeds
          the floor is *resolved* into a bit; an unresolved channel contributes
          nothing. This is the principle that raw transducer signal which is not
          modulated does not flow -- so adding ungated channels (or more sensors
          of the *same* modality) adds no usable bits.

      (b) **Coupling.** The resolved bits of the wired-in modalities are
          concatenated into a single object code. The object is the cross-modal
          invariant: the number of individuable categories is 2**(resolved
          modalities), so it is the *coupling of distinct modalities* -- not
          transducer richness within one -- that individuates the object.

    Two knobs make it the IV:
      coupled   -- tuple of modality names wired into the board this run, e.g.
                   ('touch',) or ('touch', 'vision', 'taste').
      modulate  -- if False the gate is removed: every reading is forced to a
                   bit regardless of margin. This is the 'raw transducer, no
                   modulation' condition; under noise an ungated channel can only
                   decode at chance, so stacking such channels buys nothing.

    `boundaries[m]` is the feature value separating modality m's two bits;
    `floors[m]` is its modulation gate (in the same units as the reading).
    """

    def __init__(self, coupled, boundaries, floors, modulate: bool = True):
        self.coupled = tuple(coupled)
        self.boundaries = dict(boundaries)
        self.floors = dict(floors)
        self.modulate = bool(modulate)

    def decode(self, readings: dict):
        """Return (bits, resolved): bits[m] in {0, 1} or None if unresolved;
        resolved[m] is the boolean gate outcome for modality m."""
        bits, resolved = {}, {}
        for m in self.coupled:
            margin = readings[m] - self.boundaries[m]
            if self.modulate and abs(margin) < self.floors[m]:
                bits[m], resolved[m] = None, False        # dropped below the floor
            else:
                bits[m], resolved[m] = (1 if margin >= 0 else 0), True
        return bits, resolved

    def code(self, readings: dict):
        """A hashable signature of the resolved bits, in the fixed modality
        order of `coupled`. Unresolved modalities appear as None, so two objects
        that differ only along an unread axis collapse to the same signature --
        which is exactly why fewer coupled modalities means fewer individuable
        categories."""
        bits, _ = self.decode(readings)
        return tuple(bits[m] for m in self.coupled)


class SubsumptionArbiter:
    """The Brooks/subsumption foil: fixed-priority *suppression* instead of
    modulation, and no constructed snapshot.

    Behaviour layers are ordered by priority. The highest-priority layer that
    fires (its reading clears its floor) suppresses the rest, and its single bit
    is the output. Crucially the layers are never *combined*: suppression
    replaces, it does not bind. So however many modalities are wired in, the
    arbiter yields one surviving bit -- at most two categories. That is the
    architectural ceiling subsumption hits and [[CrossModalBoard]] (which couples
    the resolved bits through modulation) breaks through.

    Reactive locomotion -- steering toward the nearest affordance, halting at an
    obstacle -- is shared with the SMN agent (it, too, is a reactive behaviour);
    what subsumption lacks is the modulatory coupling that binds modalities into
    an object, and the self-localized snapshot that places it. So a subsumption
    agent can *approach* an object it cannot *individuate* or *locate*.
    """

    def __init__(self, priority, boundaries, floors):
        self.priority = tuple(priority)
        self.boundaries = dict(boundaries)
        self.floors = dict(floors)

    def decode(self, readings: dict):
        """Return (winning_modality, bit) for the highest-priority layer that
        fires; (None, None) if none clears its floor."""
        for m in self.priority:
            margin = readings[m] - self.boundaries[m]
            if abs(margin) >= self.floors[m]:        # this layer fires -> suppresses the rest
                return m, (1 if margin >= 0 else 0)
        return None, None

    def code(self, readings: dict):
        """The one surviving channel's bit -- never a tuple of bits, because
        suppression does not combine layers."""
        _, bit = self.decode(readings)
        return (bit,)


class MessagingBeam:
    """The SMN messaging beam over the crawler's inter-segment joints.

    Each inter-segment joint hosts one CAZ-oscillator. Neighbors exchange phase
    'messages' (a Kuramoto-style nearest-neighbor coupling) that pull each pair of
    adjacent oscillators toward a fixed phase difference, so a **traveling wave**
    of bends emerges from local coupling alone -- no center. The wave is the basal
    action pattern (BAP); the anisotropic medium turns it into net thrust.

    A bilateral field gradient sensed at the head biases the wave -- a constant
    offset added to every joint command curves the body, turning locomotion toward
    higher field (chemotaxis). That is the minimal aboutness-precursor: directed
    movement toward a 'where' in the body's differentiation field.

    State exposed for visualization:
      phase  -- (n,) oscillator phase per joint (node/edge dynamic state);
      msg    -- (n,) last coupling message magnitude per joint (edge 'flow');
      theta_cmd of `command()` -- the per-joint angle command (the shared
      actuation state whose trajectory is the gait loop).
    """

    def __init__(self, n_joints: int, amp: float = 0.6, freq: float = 0.8,
                 phase_lag: float = 1.2, coupling: float = 4.0,
                 turn_gain: float = 0.8, entrain: float = 0.0,
                 entrain_mode: str = "inter"):
        self.n = int(n_joints)
        self.amp = amp
        self.w = 2 * np.pi * freq
        self.phase_lag = phase_lag          # desired head->tail phase difference
        self.coupling = coupling
        self.turn_gain = turn_gain
        self.entrain = entrain              # proprioceptive-entrainment gain (0 = open loop)
        self.entrain_mode = entrain_mode    # "inter" (correct) | "self" (ablation only)
        self.phase = -phase_lag * np.arange(self.n, dtype=float)
        self.msg = np.zeros(self.n)
        self.ent = np.zeros(self.n)         # last proprioceptive pull per joint

    # --8<-- [start:beam_command]
    def command(self, dt: float, bias: float = 0.0,
                theta: np.ndarray | None = None,
                theta_dot: np.ndarray | None = None) -> np.ndarray:
        """Advance the coupled oscillators by dt and return per-joint angle
        commands (traveling wave + chemotactic turn bias).

        Proprioceptive entrainment (the stretch-receptor / lamprey-edge-cell loop):
        when ``entrain > 0`` and the actually-sensed joint state ``theta`` (and,
        optionally, ``theta_dot``) is passed, mechanics feed back into the rhythm.
        ``entrain_mode`` selects the coupling topology:

        - ``"inter"`` (default, correct) -- the biologically faithful form
          (Wen et al. 2012): each oscillator is entrained to its **anterior
          neighbour's** realized phase, offset by the intended head->tail lag, so the
          wave propagates *through the body*. The head is the free pacemaker (no
          anterior neighbour -> no pull).
        - ``"self"`` (ablation only) -- each oscillator entrains to its **own** joint.
          Because the joint is just the beam's own servo-delayed output, this reduces
          to a constant self-brake ``sin(-delta)`` (delta = servo lag): it can only
          detune the frequency, never carry a medium dependence. Kept solely as the
          control that shows why ``"inter"`` is needed. Do not use it as a model.

        Both forms are **identically zero under perfect tracking** (no error, no
        pull) and gated by the bend magnitude ``r`` (a still body, like a silent
        stretch receptor, exerts no pull). With ``entrain == 0`` or ``theta is None``
        the phase evolves from omega + neighbour coupling alone (the sealed open-loop
        default), so prior results reproduce exactly. See docs/experiments/entrainment.
        """
        dphi = np.full(self.n, self.w)
        for i in range(self.n):
            m = 0.0
            if i > 0:
                m += np.sin((self.phase[i - 1] - self.phase[i]) - self.phase_lag)
            if i < self.n - 1:
                m += np.sin((self.phase[i + 1] - self.phase[i]) + self.phase_lag)
            self.msg[i] = m
            dphi[i] += self.coupling * m
        if self.entrain > 0.0 and theta is not None:
            # Realized gait phase per joint: the command is amp*sin(phase), so under
            # perfect tracking th = amp*sin(phase), thd/w = amp*cos(phase), hence
            # psi = arctan2(th, thd/w) = phase. r is the bend magnitude (receptor drive).
            th = np.asarray(theta, dtype=float)
            thd = (np.zeros(self.n) if theta_dot is None
                   else np.asarray(theta_dot, dtype=float))
            psi = np.arctan2(th, thd / self.w)          # body's realized gait phase
            r = np.hypot(th, thd / self.w)              # bend magnitude (receptor drive)
            gate = r / (r + 1e-3)
            self.ent = np.zeros(self.n)
            if self.entrain_mode == "self":
                # ablation: entrain to one's OWN (servo-delayed) joint -> constant brake.
                self.ent = gate * np.sin(psi - self.phase)
            elif self.n > 1:
                # inter-segmental: pull each joint toward its anterior neighbour's
                # realized phase (offset by the head->tail lag); head is the pacemaker.
                self.ent[1:] = gate[1:] * np.sin((psi[:-1] - self.phase_lag)
                                                 - self.phase[1:])
            dphi += self.entrain * self.ent
        self.phase = self.phase + dphi * dt
        return self.amp * np.sin(self.phase) + self.turn_gain * bias
    # --8<-- [end:beam_command]


class DeadReckoner:
    """Self-localization from proprioception. The agent never reads its absolute
    position; it integrates the body-frame linear velocity (velocimeter) and yaw
    rate (gyro) that it senses, building its world model in this self-estimated
    frame, anchored at its known starting pose. Estimation error accumulates --
    which is exactly the kind of thing the coupling-topology experiment probes."""

    def __init__(self, x0: float = 0.0, y0: float = 0.0, yaw0: float = 0.0):
        self.x, self.y, self.yaw = x0, y0, yaw0

    def update(self, vx_body: float, vy_body: float, wz: float, dt: float):
        self.yaw += wz * dt
        c, s = np.cos(self.yaw), np.sin(self.yaw)
        self.x += (vx_body * c - vy_body * s) * dt
        self.y += (vx_body * s + vy_body * c) * dt
        return self.x, self.y, self.yaw
