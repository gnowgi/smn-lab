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


class EyeCamera:
    """One forward-facing MuJoCo camera, rendered offscreen.

    The camera is identified by ``camera_name`` in the MJCF; we wrap a
    ``mujoco.Renderer`` of size ``(height, width)``. ``snap`` returns a
    grayscale ``uint8`` frame (mean over RGB channels) -- the SMN principle is
    that pixel count is a bandwidth placeholder and the modulator does the
    architectural work, so dropping colour at the transducer is consistent
    with treating the camera as a single undifferentiated bandwidth budget.
    """

    def __init__(self, model, camera_name: str = "eye",
                 width: int = 128, height: int = 128):
        self.width = width
        self.height = height
        self.camera_name = camera_name
        self.renderer = mujoco.Renderer(model, height=height, width=width)

    def snap(self, data) -> np.ndarray:
        self.renderer.update_scene(data, camera=self.camera_name)
        rgb = self.renderer.render()           # (H, W, 3) uint8
        return rgb.mean(axis=2).astype(np.float32)

    def close(self) -> None:
        self.renderer.close()


class AnalyticalFramePredictor:
    """Predicts the next frame from the agent's yaw rate (efference).

    Under the assumption that **the camera rotates about its own optical center
    in a static world**, the entire image translates horizontally by
    ``shift_px = ω_z · Δt · focal_px``, where
    ``focal_px = (W/2) / tan(fovx/2)``. We implement the prediction as a
    sub-pixel horizontal shift of the current frame (linear interpolation
    between the two integer-pixel neighbours), with the off-side column held
    constant.

    Departures from this prediction therefore mean either: (a) the world is
    not static -- the *exafference* we are trying to surface -- or (b) the
    camera was not purely rotating about its own center (parallax from
    translation, an architectural choice we control via the body geometry by
    mounting the camera at the head's pivot).
    """

    def __init__(self, width: int, fov_deg: float):
        self.width = int(width)
        self.focal_px = (width / 2.0) / math.tan(math.radians(fov_deg) / 2.0)

    def shift_px(self, omega_z: float, render_dt: float) -> float:
        # Yaw counter-clockwise about +z (omega_z > 0) rotates the head's +x
        # toward the head's +y. World content fixed in the head's +x direction
        # therefore moves to the head's -y direction; in image coordinates
        # (image +u = head -y) that is a shift of +omega_z·Δt·focal_px to the
        # right.
        return float(omega_z * render_dt * self.focal_px)

    def predict(self, current: np.ndarray, omega_z: float,
                render_dt: float) -> np.ndarray:
        """Return the predicted next frame: ``current`` shifted by ``shift_px``."""
        s = self.shift_px(omega_z, render_dt)
        return shift_horizontal(current, s)


def shift_horizontal(frame: np.ndarray, shift_px: float) -> np.ndarray:
    """Sub-pixel horizontal shift via linear interpolation.

    Positive ``shift_px`` shifts content to the right. The off-side column is
    extended by edge replication so the boundary contributes no spurious
    residual.
    """
    H, W = frame.shape
    s = float(shift_px)
    int_s = int(math.floor(s))
    frac = s - int_s
    # source column for output column j: j - s
    cols = np.arange(W, dtype=np.float32) - s
    lo = np.floor(cols).astype(np.int64)
    hi = lo + 1
    a = (cols - lo)[None, :]  # shape (1, W)
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
