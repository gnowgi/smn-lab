# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Visual transducer + analytical reafference for the bench.

This module is the **minimal** visual layer: one undifferentiated forward-facing
MuJoCo camera, one analytical forward model keyed on the agent's own yaw rate,
and one coarse-grid modulator that pools intensity residuals into 8×8 patch
tokens and gates them against a calibrated noise floor. It is the visual analog
of the P0 whisker + ``ReafferencePredictor`` pair.

The class names use *eye* deliberately. The eventual SMN-faithful eye has its
own CAZ structure (many small modulating zones across the visual field); this
implementation stands in for that with a flat 8×8 grid. The camera's pixel
count (128×128 by default) is a **bandwidth placeholder**, not a claim about
perceptual resolution — in SMN, resolution is a function of CAZ density and the
agent's internal capacities, and the modulator drops unmodulated input by
default. Raising the pixel count alone would change nothing the architecture
can use.

The reafference principle, lifted from 1D whisker range to a 2D image:

  * Forward model predicts the next frame from the current frame and the
    agent's known yaw rate -- under the *static-world, rotation-about-camera-
    center* assumption the predicted next frame is the current frame shifted
    horizontally by ``ω·Δt × focal_px`` pixels.
  * The modulator compares the actual next frame against this prediction
    pixel-by-pixel; pools the absolute residual into 8×8 = 64 patch tokens;
    and gates each patch against a per-patch noise floor calibrated during a
    static-world self-motion phase.
  * Only patches whose residual magnitude exceeds the floor flow through to
    the snapshot. At rest -> nothing flows. During self-motion in a static
    world -> the floor catches it; nothing flows. When an object the agent
    did not move appears in view, the patches covering its silhouette break
    the floor and pass through.

Components:
- ``EyeCamera``: wraps ``mujoco.Renderer`` for one camera; returns a grayscale
  frame per ``snap()`` call.
- ``AnalyticalFramePredictor``: produces the predicted next frame from
  ``current`` and ``yaw_rate × render_dt × focal_px``.
- ``PatchResidualModulator``: pools per-pixel residual into a P×P grid;
  calibrates a per-patch noise floor; gates later residuals against it.
"""
from __future__ import annotations
import math
import numpy as np
import mujoco


def _box_blur_3x3(frame: np.ndarray) -> np.ndarray:
    """3x3 box smoothing in pure numpy (edge-replicating boundary).

    This stands in for the eye's optical point-spread function: an idealized
    pinhole renders perfectly sharp edges, but real receptors integrate over
    a finite area. A small spatial smoothing also makes the analytical sub-
    pixel warp predictor numerically faithful at large per-frame shifts
    (sharp edges + integer-pixel shifts cause large residuals at every edge
    crossing). The smoothing is mild enough that the modulator's task -- to
    surface world-caused intensity changes that are not self-predicted --
    remains intact.
    """
    p = np.pad(frame, 1, mode="edge")
    return (p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
            p[1:-1, :-2] + p[1:-1, 1:-1] + p[1:-1, 2:] +
            p[2:, :-2] + p[2:, 1:-1] + p[2:, 2:]) / 9.0


class EyeCamera:
    """One forward-facing MuJoCo camera, rendered offscreen.

    The camera is identified by ``camera_name`` in the MJCF; we wrap a
    ``mujoco.Renderer`` of size ``(height, width)``. ``snap`` returns a
    grayscale ``float32`` frame (mean over RGB channels), optionally
    smoothed by a 3x3 box (a minimal stand-in for the eye's point-spread
    function -- see ``_box_blur_3x3``). The SMN principle is that pixel
    count is a bandwidth placeholder and the modulator does the architectural
    work, so dropping colour at the transducer is consistent with treating
    the camera as a single undifferentiated bandwidth budget.
    """

    def __init__(self, model, camera_name: str = "eye",
                 width: int = 128, height: int = 128, smooth_passes: int = 1):
        self.width = width
        self.height = height
        self.camera_name = camera_name
        # number of 3x3 box-blur passes applied to each rendered frame; one pass
        # ~ sigma 0.7, two passes ~ sigma 1.0, three ~ sigma 1.2. Stronger
        # smoothing is needed once combined per-frame Δθ exceeds ~1 px, e.g.
        # under simultaneous head + eye motion.
        self.smooth_passes = int(smooth_passes)
        self.renderer = mujoco.Renderer(model, height=height, width=width)

    def snap(self, data) -> np.ndarray:
        self.renderer.update_scene(data, camera=self.camera_name)
        rgb = self.renderer.render()           # (H, W, 3) uint8
        gray = rgb.mean(axis=2).astype(np.float32)
        for _ in range(self.smooth_passes):
            gray = _box_blur_3x3(gray)
        return gray

    def close(self) -> None:
        self.renderer.close()


class AnalyticalFramePredictor:
    """Predicts the next frame from the camera's total angular displacement.

    Under the assumption that **the camera rotates about its own optical center
    in a static world**, the entire image translates horizontally by
    ``shift_px = Δθ · focal_px``, where ``focal_px = (W/2) / tan(fovx/2)`` and
    ``Δθ`` is the camera's *total* yaw displacement between the two frames.

    The predictor does not assume where the rotation comes from. With a rigid
    head the caller passes ``Δθ = head_yaw_now − head_yaw_prev``; with a
    multi-CAZ eye nested in the head, the caller passes
    ``Δθ = (head_yaw + eye_yaw)_now − (head_yaw + eye_yaw)_prev``. The forward
    model is the same; the SMN principle is that whichever CAZs produced the
    motion are the ones the modulator must predict away.

    Departures from this prediction therefore mean either: (a) the world is
    not static -- the *exafference* we are trying to surface -- or (b) the
    camera was not purely rotating about its own center (parallax from
    translation, an architectural choice we control via the body geometry by
    mounting the camera at the head's pivot).
    """

    def __init__(self, width: int, fov_deg: float):
        self.width = int(width)
        self.focal_px = (width / 2.0) / math.tan(math.radians(fov_deg) / 2.0)

    def shift_px(self, delta_theta_rad: float) -> float:
        # Yaw counter-clockwise about +z (Δθ > 0) rotates the camera's +x
        # toward its +y. World content fixed in the camera's +x direction
        # therefore moves to the camera's -y direction; in image coordinates
        # (image +u = camera -y) that is a shift of +Δθ·focal_px to the right.
        # (Linear approximation, exact only at image center.)
        return float(delta_theta_rad * self.focal_px)

    def shift_per_column(self, delta_theta_rad: float) -> np.ndarray:
        """Angle-correct per-column shift under rotation about the optical
        center.

        For a point at image column ``u`` (centered at 0), the actual shift
        under a camera rotation by ``Δθ`` is ``Δθ · focal_px · sec²(α)``,
        where ``tan(α) = u / focal_px``. The linear ``shift_px`` is exact only
        at the image center (``u = 0``); at the FOV edge it underestimates the
        true shift by a factor of 2. This method returns the per-column shift
        array so the warp tracks rotation faithfully across the whole image,
        not just the centre.
        """
        u_centered = (np.arange(self.width, dtype=np.float32)
                      - self.width / 2.0 + 0.5)
        sec_sq = 1.0 + (u_centered / self.focal_px) ** 2
        return delta_theta_rad * self.focal_px * sec_sq

    def predict(self, current: np.ndarray, delta_theta_rad: float,
                angle_correct: bool = False) -> np.ndarray:
        """Return the predicted next frame: ``current`` shifted by the
        per-column shift if ``angle_correct``, else by a uniform shift."""
        if angle_correct:
            return shift_horizontal(current,
                                    self.shift_per_column(delta_theta_rad))
        return shift_horizontal(current, self.shift_px(delta_theta_rad))


def shift_horizontal(frame: np.ndarray, shift_px) -> np.ndarray:
    """Sub-pixel horizontal shift via linear interpolation.

    ``shift_px`` may be either a scalar (uniform shift across all columns) or
    a 1D array of length ``W`` (per-output-column shift, used by the
    angle-correct predictor). Positive shift moves content to the right; the
    off-side column is extended by edge replication so the boundary
    contributes no spurious residual.
    """
    H, W = frame.shape
    if np.isscalar(shift_px):
        cols = np.arange(W, dtype=np.float32) - float(shift_px)
    else:
        s = np.asarray(shift_px, dtype=np.float32)
        cols = np.arange(W, dtype=np.float32) - s
    lo = np.floor(cols).astype(np.int64)
    hi = lo + 1
    a = (cols - lo)[None, :]
    lo_c = np.clip(lo, 0, W - 1)
    hi_c = np.clip(hi, 0, W - 1)
    f_lo = frame[:, lo_c]
    f_hi = frame[:, hi_c]
    return (1.0 - a) * f_lo + a * f_hi


class PatchResidualModulator:
    """Pools per-pixel residual into a P×P grid, gates against the floor.

    ``calibrate`` accumulates per-patch residual magnitudes during a static-
    world self-motion phase. ``finalize`` sets the per-patch floor to the
    p95 over the calibration window (clipped from below at ``floor_min``).
    ``gate`` returns the boolean fire mask: per-patch residual > per-patch
    floor.

    Pooling is mean(|residual|) over each ``patch_px × patch_px`` block, so the
    residual a patch token carries is in intensity units (camera grayscale,
    0-255), comparable across patches and across runs.
    """

    def __init__(self, frame_size: int, patch_grid: int = 8,
                 percentile: float = 95.0, floor_min: float = 1.5):
        assert frame_size % patch_grid == 0
        self.frame_size = int(frame_size)
        self.patch_grid = int(patch_grid)
        self.patch_px = self.frame_size // self.patch_grid
        self.percentile = float(percentile)
        self.floor_min = float(floor_min)
        self._cal: list[np.ndarray] = []
        self.floor = None

    def pool(self, residual_frame: np.ndarray) -> np.ndarray:
        """Mean-pool |residual| into a (patch_grid, patch_grid) field."""
        P = self.patch_px; G = self.patch_grid
        r = np.abs(residual_frame).reshape(G, P, G, P)
        return r.mean(axis=(1, 3))

    def calibrate(self, residual_frame: np.ndarray) -> np.ndarray:
        pooled = self.pool(residual_frame)
        self._cal.append(pooled)
        return pooled

    def finalize(self) -> np.ndarray:
        stack = np.stack(self._cal, axis=0)
        self.floor = np.maximum(
            np.percentile(stack, self.percentile, axis=0), self.floor_min)
        return self.floor

    def gate(self, residual_frame: np.ndarray):
        if self.floor is None:
            raise RuntimeError("Modulator not calibrated. Call finalize first.")
        pooled = self.pool(residual_frame)
        return pooled, pooled > self.floor
