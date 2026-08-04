# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Multi-CAZ network: the DFN and IN operators of SMN §4.4, made explicit.

The preprint specifies the messaging network as two functional sub-networks and
then *defers their theory* (Appendix §2, "a note to a category theorist"). This
module implements them as running operators, so the deferred network dynamics can
be built and probed rather than assumed:

- **DFN (Differentiating & Filtering Network) -- the active-perception filter α.**
  For each board i and each broadcast channel j, a gate ``A[i, j]`` that measures how
  much zone i's *own efference* predicts channel j's *afferent motion*. It admits the
  streams a board's own action modulates (reafferent contingency) and lets fully
  self-explained / uncorrelated streams fall away. This is precision-weighting
  (Feldman & Friston 2010) realized in the body.

  It is the *online twin* of :func:`smn_lab.self_model.read_all`: the self-model
  correlates efference against the broadcast **offline** to recover the graph; the
  DFN does the same correlation **live**, as a leaky (EWMA) estimate, and uses it as
  a gate. Because the leaky estimate is an exponential integral of co-activity, the
  DFN gate *is* a Hebbian ("fire together, wire together") plastic weight -- attention
  (fast) and structure-learning (slow) are one operation read at two timescales.

- **IN (Integrating Network) -- the broadcast operator Π.** Pools the gated zone
  states into one body-wide canvas ``b = Π(x)`` that every board reads, with a
  functional coupling ``W`` (the symmetrized, consolidated DFN gate). The paper's one
  hard requirement is *network closure*: Π must be non-degenerate -- every zone both
  **writes** to the broadcast (∂b/∂x_j ≠ 0) and **reads** it. :meth:`CAZNetwork.closure`
  checks it.

Crucially, ``W`` is a **functional** coupling, not the anatomical one: it is built
from what actually co-varies under the body's own action, so its community structure
(:mod:`smn_lab.canvas_regions`) is *constructed*, not stipulated. On a branched body
that structure should recover the functional territories -- axis vs each appendage --
from movement alone.

Model/measurement discipline (see ``docs/assumptions.md``): everything here is **the
agent's own computation** -- each board uses only its own efference and what it hears
on the broadcast; no ground truth, no central reader (Commitment C3). Scoring the
emergent communities against the true body partition is the experimenter's job and
lives in :mod:`smn_lab.canvas_regions` / :mod:`smn_lab.metrics`.
"""
from __future__ import annotations
import numpy as np


class _EWMAStandardizer:
    """Per-channel running mean/variance (exponentially weighted) for online
    z-scoring. λ is the update rate; 1/λ is the effective memory in steps."""

    def __init__(self, n: int, lam: float = 0.01):
        self.lam = float(lam)
        self.mean = np.zeros(n)
        self.var = np.ones(n)
        self._warm = 0

    def z(self, v: np.ndarray) -> np.ndarray:
        v = np.asarray(v, dtype=float)
        self._warm += 1
        # update AFTER using the pre-update stats would bias early steps; update first
        d = v - self.mean
        self.mean += self.lam * d
        self.var = (1 - self.lam) * (self.var + self.lam * d * d)
        return (v - self.mean) / np.sqrt(self.var + 1e-6)


class CAZNetwork:
    """A network of CAZ boards over a body of ``n`` zones, running the DFN gate and
    the IN broadcast online.

    Feed it, each control step, the vector of zone **efferences** (commanded signed
    activations) and the vector of zone **afferent motions** (e.g. joint velocities).
    It maintains:

    - ``A[i, j]`` -- the DFN gate: leaky normalized cross-correlation of zone i's
      efference with zone j's afferent motion (directed; the online read_all).
    - ``W`` -- the IN functional coupling: symmetrized |A|, diagonal zeroed. This is
      the consolidated broadcast weight -- the canvas's constructed structure.

    Nothing here is handed the body graph. ``W`` is discovered from co-activity.
    """

    def __init__(self, n: int, lam: float = 0.01, gate_thresh: float = 0.0):
        self.n = int(n)
        self.lam = float(lam)
        self.gate_thresh = float(gate_thresh)     # α below this is treated as "not admitted"
        self._eff = _EWMAStandardizer(n, lam)
        self._aff = _EWMAStandardizer(n, lam)
        self.A = np.zeros((n, n))                 # DFN contingency (efference_i vs motion_j)
        self._steps = 0

    # --8<-- [start:dfn_step]
    def observe(self, efference: np.ndarray, afferent: np.ndarray) -> None:
        """One DFN update. Standardize efference and afferent motion online, then
        accumulate the leaky outer-product contingency A[i, j] += λ (z_eff_i · z_aff_j).
        Purely local per row: row i uses only zone i's efference and the broadcast."""
        ze = self._eff.z(efference)               # (n,) z-scored efference
        za = self._aff.z(afferent)                # (n,) z-scored afferent motion
        self.A = (1 - self.lam) * self.A + self.lam * np.outer(ze, za)
        self._steps += 1
    # --8<-- [end:dfn_step]

    # --8<-- [start:in_weights]
    @property
    def W(self) -> np.ndarray:
        """The IN functional coupling: symmetrized magnitude of the DFN gate, with
        the diagonal (self-term) removed. This is the consolidated broadcast weight
        -- each edge agreed by both endpoints from the shared broadcast."""
        G = np.abs(self.A)
        G = 0.5 * (G + G.T)
        np.fill_diagonal(G, 0.0)
        return G
    # --8<-- [end:in_weights]

    def alpha(self) -> np.ndarray:
        """The DFN admission gate α ∈ [0, 1]: the functional coupling W rescaled to
        its own max, then thresholded. α_ij ≈ 1 for a strongly co-modulated channel,
        ≈ 0 for one the board's action does not reach."""
        W = self.W
        m = W.max()
        a = W / (m + 1e-12)
        a[a < self.gate_thresh] = 0.0
        return a

    def broadcast(self, afferent: np.ndarray) -> np.ndarray:
        """The IN operator Π: the body-wide broadcast each board reads, as the
        α-gated pool of zone motions. b_i = Σ_j α_ij x_j (zone i's read of the canvas
        through its own admission gate). Returns the length-n broadcast vector."""
        return self.alpha() @ np.asarray(afferent, dtype=float)

    # --8<-- [start:closure]
    def closure(self, tol: float = 1e-6) -> dict:
        """Network-closure check (Π non-degeneracy): every zone must both WRITE to
        the broadcast (some outgoing weight) and READ it (some incoming weight).
        Returns per-zone booleans and the overall verdict. A zone that neither
        contributes to nor reads the broadcast is not part of the SMN."""
        W = self.W
        writes = W.sum(axis=0) > tol               # column j: does j's motion reach others
        reads = W.sum(axis=1) > tol                # row i: does i admit anything
        closed = bool(np.all(writes & reads))
        return dict(writes=writes, reads=reads, closed=closed,
                    n_orphan=int(np.sum(~(writes & reads))))


def kuramoto_step(phase: np.ndarray, W: np.ndarray, omega: float,
                  phase_lag: np.ndarray | float, dt: float, coupling: float = 4.0
                  ) -> np.ndarray:
    """One step of the network dynamics (preprint Eq. 21) on an ARBITRARY coupling
    ``W`` -- the generalization of ``MessagingBeam``'s hard-wired nearest-neighbour
    rule. dθ_i = ω + coupling · Σ_j W_ij sin(θ_j − θ_i − φ_ij).

    With ``W`` = the discovered IN coupling this shows the *same* operator that built
    the self-structure can also drive coordination: the wave is not hand-wired, it
    rides the functional graph the DFN/IN constructed. Returns the advanced phase."""
    n = len(phase)
    lag = phase_lag if np.ndim(phase_lag) else np.full((n, n), phase_lag)
    diff = phase[None, :] - phase[:, None] - lag      # θ_j - θ_i - φ_ij
    dphi = omega + coupling * np.sum(W * np.sin(diff), axis=1)
    return phase + dphi * dt
