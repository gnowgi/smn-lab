# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""P3 -- cross-modal object discrimination, with localization and reafference.

This experiment puts to the test the SMN claim that recognition needs no new
mechanism beyond the basal architecture: the same located, opponent-modulated
zones that forage in P2 here *individuate an object*, and they do it actively,
with no labeled corpus and no backprop. Two results are targeted.

  Fig A -- **cross-modal binding.** Each object carries one feature bit per
    modality: touch (its angular extent in the whisker fan), vision (its
    luminance), taste (a chemical signature sampled near it). No single modality
    individuates the eight objects -- one modality collapses them 4-fold. The
    number of individuable categories is 2**(modalities *coupled through the
    cross-modal board*). Crucially, adding more whiskers (transducer density
    within one modality) does *not* substitute for coupling a second modality:
    a touch-only agent cannot read colour no matter how many whiskers it grows.
    Sensors are not modalities -- the dissociation no ML reviewer would predict.

  Fig B -- **localization needs reafference.** The agent reports not just *what*
    the object is but *where* it is, in its own dead-reckoned frame (the world
    model includes locating objects in space). Holding the object at a stable
    place while the agent itself moves toward it requires discounting self-caused
    sensory change: with reafference on, the located object sits at its true
    place; with it off, the agent attributes its own approach motion to the
    object and mislocalizes it by roughly the distance it travelled.

The object's tactile and visual bits are carried geometrically (radius, rgba);
the taste bit is an analytic chemical field. The rendered visual pathway
(`vision.EyeCamera` + `PatchResidualModulator`) can be swapped in later without
touching the body -- a camera is already mounted. Feature thresholds here are a
first calibration; the per-object raw features are printed so they can be tuned.

Run:  ../.venv/bin/python p3_crossmodal_discrimination.py
"""
from __future__ import annotations
import os, sys, math, itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.body import MouseSchema
from smn_lab.model import build_p3_xml
from smn_lab.control import (CrossModalBoard, SubsumptionArbiter, DeadReckoner,
                             CPG, DifferentialDrive)
from smn_lab.vision import EyeCamera, AnalyticalFramePredictor, PatchResidualModulator

DT = 0.005
ARENA = 1.4
START = (0.0, 0.0, 0.0)            # agent starts at origin, facing +x
MAX_RAY = 4.0
MAXSTEP = int(6.0 / DT)

# --- the three modality bits -> physical realization -------------------------
SMALL_R, BIG_R = 0.06, 0.30        # tactile bit: object radius (angular extent)
DARK, LIGHT = 0.35, 0.85           # visual bit: object luminance (-> grayscale)
BITTER, SWEET = -1.0, +1.0         # taste bit: sign of the chemical source

OBJ_DIST = 1.05                    # objects sit ahead at this radius...
BEARINGS_DEG = np.linspace(-22, 22, 8)   # ...spread (L/R/front), inside whisker fan + camera FOV

# taste field: a Gaussian chemical source at the object; the agent reads the
# signed concentration where it stands, so it must approach to taste.
TASTE_PEAK, TASTE_SIGMA = 1.0, 0.6

# feature noise (sensor floor) and the cross-modal board's decision geometry
NOISE = {"touch": 2.5, "vision": 0.04, "taste": 0.06}      # std-devs (feature units)
BOUNDARIES = {"touch": 10.0, "vision": 0.60, "taste": 0.0}  # the bit split per modality
FLOORS = {"touch": 6.0, "vision": 0.10, "taste": 0.18}      # modulation gate (drop below)
MODALITY_ORDER = ("touch", "vision", "taste")

# approach controller
STOP_GAP = 0.30                    # the HAP halts when the nearest whisker is this close
K_TURN = 3.0                       # strong centering so the object stays head-on
TURN_MAX = 2.5

WHISKERS_5 = (-60, -30, 0, 30, 60)
WHISKERS_9 = (-60, -45, -30, -15, 0, 15, 30, 45, 60)

# rendered visual channel (vision.EyeCamera). Resolution is set by the patch
# grid (the visual CAZ density), not the pixel count -- raising VFRAME alone
# changes nothing the architecture uses.
VFRAME = 64                        # camera pixels (a bandwidth placeholder)
VPATCH = 8                         # patch-token grid = visual CAZ density
VFLOOR = 14.0                      # modulation gate: tokens deviating from the
                                   # background by less than this are dropped (0-255)
_VISION_OK = None                  # lazily probed: is a GL backend available?

_RNG = np.random.default_rng(7)


def _vision_available(model, data):
    """Probe once whether mujoco can render (a GL backend is present). When it
    is not -- e.g. a headless box with no EGL/OSMesa -- the experiment falls
    back to analytic luminance so it still runs."""
    global _VISION_OK
    if _VISION_OK is None:
        try:
            cam = EyeCamera(model, width=VFRAME, height=VFRAME)
            cam.snap(data); cam.close()
            _VISION_OK = True
            print(f"  [vision] rendered path active (MUJOCO_GL={os.environ.get('MUJOCO_GL', 'auto')})")
        except Exception as e:
            print(f"  [vision] rendered path unavailable ({type(e).__name__}); "
                  f"using analytic luminance.")
            _VISION_OK = False
    return _VISION_OK


def render_tokens(model, data, qadr, pose):
    """Render the closest-approach view and pool it into VPATCH x VPATCH
    luminance tokens (resolution = token/CAZ density, not pixel count). Returns
    the token grid (0-255), or None if no GL backend is available."""
    if not _vision_available(model, data):
        return None
    try:
        qx, qy, qyaw = qadr
        data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = pose   # closest-approach view
        mujoco.mj_forward(model, data)
        cam = EyeCamera(model, width=VFRAME, height=VFRAME)
        frame = cam.snap(data); cam.close()
        G, P = VPATCH, VFRAME // VPATCH
        return frame.reshape(G, P, G, P).mean(axis=(1, 3))     # patch-token luminance
    except Exception:
        return None


VLOOM_PUSH = 0.06                  # forward probe (m) used to surface the object by looming
VLOOM_FLOOR = 12.0                 # reafference gate on mean|residual| per patch (0-255)


def reafferent_luminance(model, data, qadr, pose):
    """Surface the object by *reafference*, then read its luminance.

    At closest approach the agent makes a small forward probe. Its rotation-only
    forward model (`AnalyticalFramePredictor`) predicts no image shift from this
    pure translation, so the residual between the actual and predicted view is
    the object's unpredicted **looming** -- self-caused change the forward model
    cannot explain, which is exactly what the modulator (`PatchResidualModulator`)
    surfaces against its floor. The gated patches *locate* the object; its
    luminance is read at their centroid -- the object body, away from the
    edge-mixed annulus the looming residual itself sits on. Returns luminance
    (0-1), or None if rendering is unavailable or nothing is surfaced (the caller
    then falls back to the static contrast read)."""
    if not _vision_available(model, data):
        return None
    try:
        qx, qy, qyaw = qadr; px, py, pyaw = pose
        cam = EyeCamera(model, width=VFRAME, height=VFRAME)
        data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = px, py, pyaw
        mujoco.mj_forward(model, data); A = cam.snap(data)
        data.qpos[qx] = px + VLOOM_PUSH * math.cos(pyaw)       # pure forward translation
        data.qpos[qy] = py + VLOOM_PUSH * math.sin(pyaw)
        mujoco.mj_forward(model, data); B = cam.snap(data)
        cam.close()
        pred = AnalyticalFramePredictor(VFRAME, 90.0).predict(A, 0.0)   # yaw unchanged: no shift
        residual = np.abs(B - pred)                            # = unpredicted looming
        G, P = VPATCH, VFRAME // VPATCH
        mod = PatchResidualModulator(VFRAME, VPATCH, floor_min=VLOOM_FLOOR)
        mod.floor = np.full((G, G), VLOOM_FLOOR)               # fixed reafference floor
        _, mask = mod.gate(residual)
        band = np.zeros((G, G), bool); band[1:G // 2, 1:G - 1] = True   # above the floor horizon
        obj = mask & band
        if not obj.any():
            return None
        # the looming gate locates the object (figure-ground). Read its albedo at
        # the object *body* -- the most-deviant-from-background token inside the
        # surfaced region (dilated by one) -- not on the edge-mixed looming annulus.
        ii, jj = np.where(obj)
        roi = np.zeros((G, G), bool)
        roi[max(0, ii.min() - 1):ii.max() + 2, max(0, jj.min() - 1):jj.max() + 2] = True
        roi &= band
        LA = A.reshape(G, P, G, P).mean(axis=(1, 3))
        bg = float(np.median(np.concatenate([LA[0, :], LA[-1, :], LA[:, 0], LA[:, -1]])))
        dev = np.abs(LA - bg); dev[~roi] = -1.0
        i, j = np.unravel_index(int(np.argmax(dev)), LA.shape)
        return float(LA[i, j]) / 255.0
    except Exception:
        return None


def luminance_from_tokens(L):
    """The visual bit from the token grid. The frame border estimates the
    uniform background (skybox + floor + walls); the object body is the
    most-deviant token in the upper-central band -- above the bright floor
    horizon line -- read near its albedo under the scene's flat lighting. This
    is the modulated read: only the token that breaks from the background flows.
    """
    G = L.shape[0]
    border = np.concatenate([L[0, :], L[-1, :], L[:, 0], L[:, -1]])
    bg = float(np.median(border))
    dev = np.abs(L - bg)
    band = np.zeros((G, G), bool); band[1:G // 2, 1:G - 1] = True
    dev[~band] = -1.0
    i, j = np.unravel_index(int(np.argmax(dev)), L.shape)
    return float(L[i, j]) / 255.0


def make_objects():
    """The eight objects: every combination of the three modality bits, each
    placed at a distinct bearing so localization also exercises body geometry."""
    objs = []
    for k, (tac, vis, tas) in enumerate(itertools.product((0, 1), repeat=3)):
        b = math.radians(BEARINGS_DEG[k])
        objs.append(dict(
            bits=(tac, vis, tas),
            radius=BIG_R if tac else SMALL_R,
            lum=LIGHT if vis else DARK,
            flavor=SWEET if tas else BITTER,
            pos=(OBJ_DIST * math.cos(b), OBJ_DIST * math.sin(b)),
        ))
    return objs


def _rgba(lum):
    return f"{lum:.3f} {lum:.3f} {lum:.3f} 1"


def run_trial(obj, whisker_angles, reaff_on, watch=False, cosmetic=False, frame_cb=None):
    """Approach one object, then read all three modalities and localize it.

    Returns the raw per-modality feature readings and the localization error
    under the chosen reafference setting. With ``watch=True`` an interactive
    MuJoCo viewer opens and the approach runs in real time (for `--watch`);
    ``cosmetic=True`` uses the legible coloured-room scene for that viewer.
    ``frame_cb(rgb, info)`` -- if given, a third-person frame is rendered during
    the approach and handed to the callback (used by the Streamlit lab UI to show
    the live world); the very same control code drives it."""
    wdeg = np.asarray(whisker_angles, dtype=float)
    wrad = np.radians(wdeg)
    ci = int(np.argmin(np.abs(wdeg)))                  # the centre (0 deg) whisker
    model = mujoco.MjModel.from_xml_string(
        build_p3_xml(obj["radius"], _rgba(obj["lum"]), obj["pos"],
                     arena_half=ARENA, whisker_angles_deg=tuple(whisker_angles),
                     cosmetic=cosmetic))
    data = mujoco.MjData(model)
    bid = model.body("mouse").id
    qx = model.jnt_qposadr[model.joint("slide_x").id]
    qy = model.jnt_qposadr[model.joint("slide_y").id]
    qyaw = model.jnt_qposadr[model.joint("yaw").id]
    w_adr = [model.sensor_adr[model.sensor(f"whisker_{i}").id] for i in range(len(wdeg))]
    vel_adr = model.sensor_adr[model.sensor("vel").id]
    gyro_adr = model.sensor_adr[model.sensor("gyro").id]

    # the SAME locomotion machinery as the P2 foraging experiments: a basal
    # action pattern (CPG) for thrust, and a differential drive that turns the
    # (forward, turn) command into a body wrench from the two LOCATED drive zones
    # -- so the controller that forages is the controller that approaches.
    schema = MouseSchema()
    drive = DifferentialDrive(schema, amax=1.5, turn_gain=2.0)
    bap = CPG(thrust=0.8)

    data.qpos[qx], data.qpos[qy], data.qpos[qyaw] = START
    mujoco.mj_forward(model, data)
    dr = DeadReckoner(*START)
    ex, ey, eyaw = START

    # Approach, recording the *closest-approach* frame. Reading at closest
    # approach (not at the final step) is what the agent's modulators do, and it
    # makes the read robust to a small/peripheral object the agent grazes past:
    # we stop the moment the object leaves the fan again, before any wall fills
    # it, and report the frame where the object best subtended the whiskers.
    viewer = None
    if watch:
        from mujoco import viewer as _mjviewer       # aliased: don't shadow module-global `mujoco`
        import time as _time
        viewer = _mjviewer.launch_passive(model, data,
                                          show_left_ui=False, show_right_ui=False)
        viewer.cam.lookat[:] = [0.4, 0.0, 0.10]      # frame the agent + the object ahead
        viewer.cam.distance, viewer.cam.elevation, viewer.cam.azimuth = 3.0, -45.0, 90.0

    scene_renderer = None                            # third-person render for the lab UI
    if frame_cb is not None:
        scene_renderer = mujoco.Renderer(model, height=420, width=600)
        scene_cam = mujoco.MjvCamera()
        scene_cam.lookat[:] = [0.4, 0.0, 0.10]
        scene_cam.distance, scene_cam.elevation, scene_cam.azimuth = 3.0, -45.0, 90.0

    best_min, best_ranges, best_pose, best_qpos = float("inf"), None, START, START
    acquired = False
    ranges = np.full(len(wdeg), MAX_RAY)
    for k in range(MAXSTEP):
        t = k * DT
        raw = np.array([data.sensordata[a] for a in w_adr])
        ranges = np.where((raw < 0) | (raw > MAX_RAY), MAX_RAY, raw)
        minr = float(ranges.min())
        if minr < 0.70:                                # object is in the fan
            acquired = True
        if acquired and minr < best_min:
            best_min, best_ranges, best_pose = minr, ranges.copy(), (ex, ey, eyaw)
            best_qpos = (data.qpos[qx], data.qpos[qy], data.qpos[qyaw])
        if minr < STOP_GAP:                            # close enough -> the HAP halts
            break
        if acquired and minr > best_min + 0.08:        # receding from closest approach -> passed it
            break
        # the haltable action pattern, recruited by the object affordance: steer
        # toward the whisker that senses it (the approach mirror of the foraging
        # avoid-HAP) and let the BAP cruise, gated down off-centre.
        imin = int(np.argmin(ranges))
        turn = float(np.clip(K_TURN * wrad[imin], -TURN_MAX, TURN_MAX))
        forward = bap.drive(t) * (1.0 if abs(wrad[imin]) < math.radians(12) else 0.30)
        acts = drive.activations(forward, turn)        # located-zone differential drive
        Fx, tau = drive.wrench(acts)
        yaw = data.qpos[qyaw]
        data.xfrc_applied[bid, 0] = Fx * math.cos(yaw)
        data.xfrc_applied[bid, 1] = Fx * math.sin(yaw)
        data.xfrc_applied[bid, 5] = tau
        mujoco.mj_step(model, data)
        vx, vy = data.sensordata[vel_adr], data.sensordata[vel_adr + 1]
        wz = data.sensordata[gyro_adr + 2]
        ex, ey, eyaw = dr.update(vx, vy, wz, DT)
        if viewer is not None:                          # live, real-time playback
            viewer.sync(); _time.sleep(DT)
            if not viewer.is_running():
                break
        if scene_renderer is not None and k % 3 == 0:   # feed the lab UI a third-person frame
            scene_renderer.update_scene(data, scene_cam)
            frame_cb(scene_renderer.render(), {"t": t, "minr": float(ranges.min())})

    if viewer is not None:                              # hold at closest approach until closed
        while viewer.is_running():
            viewer.sync(); _time.sleep(0.03)
        viewer.close()
    if scene_renderer is not None:
        scene_renderer.close()
    if best_ranges is not None:                         # report the closest-approach frame
        ranges, (ex, ey, eyaw) = best_ranges, best_pose

    # --- modality readings at closest approach -------------------------------
    # whiskers on the object: near the closest hit AND closer than any wall
    # (the object sits ~0.6 m away at the stop; walls are farther) -- so a
    # mis-acquired frame near a wall does not masquerade as a huge object.
    OBJ_MAXR = 0.70
    hit = (ranges < ranges.min() + 0.25) & (ranges < OBJ_MAXR)
    extent = float(wdeg[hit].max() - wdeg[hit].min()) if hit.sum() > 1 else 0.0
    touch_f = extent + _RNG.normal(0, NOISE["touch"])

    L = render_tokens(model, data, (qx, qy, qyaw), best_qpos)   # rendered patch tokens
    if L is None:                                              # no GL: analytic stand-in
        vision_f = obj["lum"] + _RNG.normal(0, NOISE["vision"])
        vis_tokens = np.full(VPATCH * VPATCH, obj["lum"])
    else:
        # reafference/looming gate surfaces the object; fall back to the static
        # contrast read if the probe surfaces nothing.
        vloom = reafferent_luminance(model, data, (qx, qy, qyaw), best_qpos)
        vision_f = vloom if vloom is not None else luminance_from_tokens(L)
        vis_tokens = L.flatten() / 255.0                       # raw patch tokens (visual stream)

    d_obj = math.hypot(ex - obj["pos"][0], ey - obj["pos"][1])  # taste: sampled where agent stands
    taste_f = (obj["flavor"] * TASTE_PEAK * math.exp(-d_obj ** 2 / (2 * TASTE_SIGMA ** 2))
               + _RNG.normal(0, NOISE["taste"]))

    readings = {"touch": touch_f, "vision": vision_f, "taste": taste_f}

    # --- localization: place the object in the agent's frame -----------------
    # reaff on  -> use the dead-reckoned pose (self-motion discounted)
    # reaff off -> use the START pose (the agent ignores that it moved, so the
    #              object is placed as if the agent never approached -> smear)
    px, py, pyaw = (ex, ey, eyaw) if reaff_on else START
    imin = int(np.argmin(ranges))                      # the whisker actually on the object
    a = wrad[imin]
    wx, wy = 0.10, 0.0                                  # whisker mount (body frame)
    sx = px + wx * math.cos(pyaw) - wy * math.sin(pyaw)
    sy = py + wx * math.sin(pyaw) + wy * math.cos(pyaw)
    rdir = pyaw + a
    r = ranges[imin]
    cx = sx + (r + obj["radius"]) * math.cos(rdir)     # surface hit -> centre
    cy = sy + (r + obj["radius"]) * math.sin(rdir)
    loc_err = math.hypot(cx - obj["pos"][0], cy - obj["pos"][1])

    # the raw sensory stream a corpus-trained net would be fed (pre-modulation):
    # whisker ranges + central camera tokens + the taste scalar.
    raw = np.concatenate([np.asarray(ranges, float), vis_tokens, [taste_f]])
    return dict(readings=readings, loc_err=loc_err, est=(cx, cy),
                traveled=math.hypot(ex, ey), raw=raw)


def individuate(objs, coupled, whisker_angles, modulate=True):
    """Decode every object with the given coupling and return (n_classes,
    bit_accuracy): distinct decoded signatures, and how often a resolved bit
    matched the truth."""
    board = CrossModalBoard(coupled, BOUNDARIES, FLOORS, modulate=modulate)
    sigs, correct, total = [], 0, 0
    for o in objs:
        tr = run_trial(o, whisker_angles, reaff_on=True)
        bits, _ = board.decode(tr["readings"])
        sigs.append(board.code(tr["readings"]))
        truth = dict(zip(MODALITY_ORDER, o["bits"]))
        for m in coupled:
            if bits[m] is not None:
                total += 1
                correct += int(bits[m] == truth[m])
    return len(set(sigs)), (correct / total if total else 0.0)


def subsumption_individuate(objs, priority=MODALITY_ORDER):
    """The Brooks foil, measured: the SAME body, sensors, and reactive approach,
    but a SubsumptionArbiter (fixed-priority suppression) in place of the
    cross-modal board. Suppression yields one surviving channel, so all three
    modalities still individuate at most 2 categories. Returns n_classes."""
    arb = SubsumptionArbiter(priority, BOUNDARIES, FLOORS)
    sigs = [arb.code(run_trial(o, WHISKERS_5, reaff_on=True)["readings"]) for o in objs]
    return len(set(sigs))


# --- resolution principle: modulation turns sensor count into resolution -----
RES_SIGNAL = 0.18                  # true feature separation of the two classes
RES_SIGMA = 0.45                   # per-channel transducer noise
RES_NS = (1, 2, 3, 5, 9, 15)       # number of redundant sensor channels (CAZ density)
RES_TRIALS = 20000


def resolution_sweep(signal=RES_SIGNAL, sigma=RES_SIGMA, Ns=RES_NS, trials=RES_TRIALS):
    """Discriminate two classes from N noisy redundant channels, two ways.

    modulation ON  -- the modulator integrates across the N gated zones (mean),
                      so effective noise falls as sigma/sqrt(N): resolution rises
                      with CAZ density.
    modulation OFF -- unmodulated input is dropped; the agent commits on a single
                      raw channel, so adding sensors changes nothing.

    The ML default expectation is the ON curve (a linear readout pools all
    channels for free). The SMN claim is that the rise is *bought by the
    modulatory architecture*: strip it (OFF) and more sensors are flat. Returns
    (Ns, acc_on, acc_off)."""
    rng = np.random.default_rng(11)
    acc_on, acc_off = [], []
    for N in Ns:
        true = rng.choice([-signal, signal], size=trials)
        chans = true[:, None] + rng.normal(0, sigma, size=(trials, N))
        acc_on.append(float((np.sign(chans.mean(axis=1)) == np.sign(true)).mean()))
        acc_off.append(float((np.sign(chans[:, 0]) == np.sign(true)).mean()))
    return list(Ns), acc_on, acc_off


# --- deep-net foil: a corpus-trained classifier on the raw sensory stream -----
DN_SIZES = (8, 16, 32, 64, 128, 256, 512, 1024)    # labeled training-set sizes
DN_TEST = 2000
DN_SEEDS = 3
RAW_NOISE = {"ranges": 0.03, "tokens": 0.03, "taste": 0.06}   # per-channel sampling noise


class TinyMLP:
    """A small fully-connected classifier -- one hidden ReLU layer, softmax out,
    mini-batch SGD on cross-entropy. Pure numpy, so the bench stays dependency
    free. It stands in for the 'deep net' the foil compares against: unlike SMN
    it must *learn* the features (extent from ranges, luminance from tokens) from
    a labeled corpus."""

    def __init__(self, n_in, n_hidden, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 1 / np.sqrt(n_in), (n_in, n_hidden)); self.b1 = np.zeros(n_hidden)
        self.W2 = rng.normal(0, 1 / np.sqrt(n_hidden), (n_hidden, n_out)); self.b2 = np.zeros(n_out)

    def _fwd(self, X):
        z1 = X @ self.W1 + self.b1; a1 = np.maximum(z1, 0.0)
        z2 = a1 @ self.W2 + self.b2
        z2 -= z2.max(1, keepdims=True); e = np.exp(z2)
        return z1, a1, e / e.sum(1, keepdims=True)

    def fit(self, X, y, epochs=300, lr=0.15, batch=32, seed=0):
        rng = np.random.default_rng(seed); n, K = len(X), self.b2.shape[0]
        Y = np.eye(K)[y]
        for _ in range(epochs):
            idx = rng.permutation(n)
            for s in range(0, n, batch):
                b = idx[s:s + batch]; Xb, Yb = X[b], Y[b]
                z1, a1, p = self._fwd(Xb)
                g2 = (p - Yb) / len(b)
                g1 = (g2 @ self.W2.T) * (z1 > 0)
                self.W2 -= lr * (a1.T @ g2); self.b2 -= lr * g2.sum(0)
                self.W1 -= lr * (Xb.T @ g1); self.b1 -= lr * g1.sum(0)
        return self

    def predict(self, X):
        return self._fwd(X)[2].argmax(1)


def smn_decode_raw(vec, board, wdeg):
    """Decode one raw sensory vector the SMN way (its fixed architecture, no
    training): extent from the whisker ranges, luminance from the camera tokens,
    taste from the scalar -> cross-modal code. Lets SMN be scored on the *same*
    generative test set as the deep net."""
    nr = len(wdeg)
    ranges = vec[:nr]
    L = vec[nr:nr + VPATCH * VPATCH].reshape(VPATCH, VPATCH) * 255.0
    hit = (ranges < ranges.min() + 0.25) & (ranges < 0.70)
    extent = float(wdeg[hit].max() - wdeg[hit].min()) if hit.sum() > 1 else 0.0
    readings = {"touch": extent, "vision": luminance_from_tokens(L), "taste": float(vec[-1])}
    return board.code(readings)


def deep_net_baseline(objs):
    """Learning curve: a net trained on the raw sensory stream (whisker ranges +
    camera tokens + taste) vs SMN, which decodes the *same* test set with zero
    labeled examples. Each object's raw vector is measured once; a generative
    sampler adds channel noise (the same kind the SMN decode faces), so the two
    are compared on identical inputs. Returns (sizes, accs, chance, untrained,
    smn_acc)."""
    means = np.array([np.mean([run_trial(o, WHISKERS_5, True)["raw"] for _ in range(3)], axis=0)
                      for o in objs])
    D, nr, K = means.shape[1], len(WHISKERS_5), len(objs)
    noise = np.concatenate([np.full(nr, RAW_NOISE["ranges"]),
                            np.full(D - nr - 1, RAW_NOISE["tokens"]),
                            [RAW_NOISE["taste"]]])

    def sample(n, rng):
        idx = rng.integers(0, K, n)
        return means[idx] + rng.normal(0, 1, (n, D)) * noise, idx

    mu_sd, _ = sample(4000, np.random.default_rng(0))
    mu, sd = mu_sd.mean(0), mu_sd.std(0) + 1e-9                 # standardize inputs
    Xte_raw, yte = sample(DN_TEST, np.random.default_rng(1))
    Xte = (Xte_raw - mu) / sd
    # SMN decodes the SAME test set with its fixed architecture (zero training).
    board = CrossModalBoard(MODALITY_ORDER, BOUNDARIES, FLOORS, modulate=True)
    wdeg = np.asarray(WHISKERS_5, float)
    smn_acc = float(np.mean([smn_decode_raw(x, board, wdeg) == objs[i]["bits"]
                             for x, i in zip(Xte_raw, yte)]))
    # untrained net (0 labeled examples): the same architecture, random weights.
    # This is the fair zero-corpus comparison point for SMN -- the raw stream is
    # not self-organizing, so without training (or SMN's structure) it is chance.
    untrained = float(np.mean([(TinyMLP(D, 32, K, seed=s).predict(Xte) == yte).mean()
                               for s in range(DN_SEEDS)]))
    accs = []
    for M in DN_SIZES:
        a = []
        for s in range(DN_SEEDS):
            Xtr, ytr = sample(M, np.random.default_rng(100 + s))
            net = TinyMLP(D, 32, K, seed=s).fit((Xtr - mu) / sd, ytr, seed=s)
            a.append(float((net.predict(Xte) == yte).mean()))
        accs.append(float(np.mean(a)))
    return list(DN_SIZES), accs, 1.0 / K, untrained, smn_acc


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    objs = make_objects()

    # diagnostics: raw features per object (to calibrate boundaries/floors)
    print("\n=== P3 cross-modal discrimination — raw features (calibration) ===")
    print("  bits(t,v,a)  touch°   vision   taste")
    for o in objs:
        tr = run_trial(o, WHISKERS_5, reaff_on=True)
        r = tr["readings"]
        print(f"  {o['bits']}    {r['touch']:6.1f}  {r['vision']:6.2f}  {r['taste']:6.2f}")

    # --- Fig A: individuable categories vs modalities coupled ----------------
    print("\n--- binding: individuable categories vs coupling ---")
    couplings = [("touch",), ("touch", "vision"), ("touch", "vision", "taste")]
    classes, accs = [], []
    for c in couplings:
        n, acc = individuate(objs, c, WHISKERS_5)
        classes.append(n); accs.append(acc)
        print(f"  coupled={'+'.join(c):20s}: {n} classes,  bit-acc={acc:.2f}")
    # density does NOT substitute: touch-only with 9 whiskers is still 1 bit
    n9, _ = individuate(objs, ("touch",), WHISKERS_9)
    print(f"  touch only, 9 whiskers          : {n9} classes  (density ≠ modality)")
    # the Brooks foil, measured: all 3 sensors, but suppression not modulation
    n_sub = subsumption_individuate(objs)
    print(f"  subsumption, all 3 sensors      : {n_sub} classes  (suppression, no binding)")

    # --- Fig B: localization error, reafference on vs off --------------------
    print("\n--- localization: reafference on vs off ---")
    err_on = np.mean([run_trial(o, WHISKERS_5, reaff_on=True)["loc_err"] for o in objs])
    err_off = np.mean([run_trial(o, WHISKERS_5, reaff_on=False)["loc_err"] for o in objs])
    print(f"  reafference ON : mean loc error = {err_on:.3f} m")
    print(f"  reafference OFF: mean loc error = {err_off:.3f} m")

    # --- resolution principle: modulation vs sensor count --------------------
    print("\n--- resolution principle: modulation ON vs OFF, vs sensor count ---")
    Ns, acc_on, acc_off = resolution_sweep()
    for N, a_on, a_off in zip(Ns, acc_on, acc_off):
        print(f"  N={N:2d} channels:  modulation ON acc={a_on:.3f}   OFF acc={a_off:.3f}")

    # --- figure --------------------------------------------------------------
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(15, 4.8))

    labels = ["touch", "touch\n+vision", "touch\n+vision\n+taste",
              "touch\n×9 whiskers", "subsumption\n(3 sensors)"]
    vals = classes + [n9, n_sub]
    cols = ["#6a9ec5", "#6a9ec5", "#2c6a9c", "#c08a3e", "#7a5a8a"]
    axA.bar(labels, vals, color=cols)
    axA.axhline(8, color="#888", ls=":", lw=1)
    axA.set_ylabel("individuable categories")
    axA.set_title("Binding: categories = 2^(modalities coupled)\n"
                  "(more whiskers, or suppression, ≠ more categories)", fontsize=9)
    for i, v in enumerate(vals):
        axA.text(i, v + 0.1, str(v), ha="center", fontsize=10)
    axA.tick_params(axis="x", labelsize=7)

    axB.bar(["reafference\nON", "reafference\nOFF"], [err_on, err_off],
            color=["#2c7a2c", "#b03030"])
    axB.set_ylabel("mean localization error (m)")
    axB.set_title("Localization needs the self/world split", fontsize=10)
    for i, v in enumerate([err_on, err_off]):
        axB.text(i, v + 0.005, f"{v:.2f}", ha="center", fontsize=10)

    axC.add_patch(Rectangle((-ARENA, -ARENA), 2 * ARENA, 2 * ARENA, fill=False, ec="#bbb"))
    for o in objs:
        axC.add_patch(Circle(o["pos"], o["radius"], facecolor=str(o["lum"]),
                             ec="#c33" if o["flavor"] > 0 else "#36c", lw=2))
    axC.plot(0, 0, "s", color="#2a5cc8", ms=10)
    axC.set_aspect("equal"); axC.set_xlim(-ARENA, ARENA); axC.set_ylim(-0.4, ARENA)
    axC.set_xticks([]); axC.set_yticks([])
    axC.set_title("Scene: 8 objects (size=touch, fill=vision,\nedge=taste)", fontsize=10)

    fig.suptitle("P3 — recognition as an SMN result: cross-modal binding + located object, "
                 "no labeled corpus", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(figdir, "p3_crossmodal_discrimination.png")
    fig.savefig(out, dpi=120)
    print(f"\n[saved] {out}")

    # --- second figure: the resolution principle -----------------------------
    fig2, ax = plt.subplots(figsize=(6.2, 4.8))
    ax.plot(Ns, acc_on, "o-", color="#2c6a9c", lw=2, label="modulation ON (zones integrated)")
    ax.plot(Ns, acc_off, "s--", color="#b03030", lw=2, label="modulation OFF (extras dropped)")
    ax.axhline(0.5, color="#888", ls=":", lw=1)
    ax.set_xlabel("number of sensor channels  (CAZ density)")
    ax.set_ylabel("discrimination accuracy")
    ax.set_ylim(0.45, 1.0)
    ax.set_title("Resolution scales with modulation, not sensor count\n"
                 "(ML expects the blue rise for free; SMN: the rise is the modulation)",
                 fontsize=10)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.25)
    fig2.tight_layout()
    out2 = os.path.join(figdir, "p3_resolution_principle.png")
    fig2.savefig(out2, dpi=120)
    print(f"[saved] {out2}")

    # --- third figure: the deep-net foil (no labeled corpus) -----------------
    print("\n--- foil: deep net (labeled corpus) vs SMN (zero corpus, same test set) ---")
    sizes, dn_acc, chance, dn_untrained, smn_acc = deep_net_baseline(objs)
    reach = next((m for m, a in zip(sizes, dn_acc) if a >= smn_acc - 0.02), None)
    print(f"  deep net, untrained (0 examples):  acc={dn_untrained:.3f}  (≈ chance)")
    for m, a in zip(sizes, dn_acc):
        print(f"  deep net, {m:4d} labeled examples:  acc={a:.3f}")
    print(f"  SMN, 0 labeled examples:  acc={smn_acc:.3f}  "
          f"(deep net reaches it at ~{reach} examples)")

    fig3, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.semilogx(sizes, dn_acc, "o-", color="#b03030", lw=2,
                label="deep net (raw stream, trained)")
    ax.plot([1], [dn_untrained], "D", color="#b03030", ms=9, mfc="white",
            label="deep net, untrained (0 ex)")
    ax.axhline(smn_acc, color="#2c6a9c", ls="--", lw=2)
    ax.plot([1], [smn_acc], "*", color="#2c6a9c", ms=18,
            label="SMN (no corpus, online)")
    ax.axhline(chance, color="#888", ls=":", lw=1, label=f"chance (1/{len(objs)})")
    ax.set_xlabel("labeled training examples")
    ax.set_ylabel("8-way discrimination accuracy")
    ax.set_ylim(0, 1.02)
    ax.set_title("The foil: a deep net needs a labeled corpus to reach\n"
                 "what the SMN architecture achieves with none", fontsize=10)
    ax.legend(loc="center right", fontsize=9)
    ax.grid(alpha=0.25, which="both")
    fig3.tight_layout()
    out3 = os.path.join(figdir, "p3_deepnet_foil.png")
    fig3.savefig(out3, dpi=120)
    print(f"[saved] {out3}")


def watch():
    """Open the MuJoCo viewer and watch the agent approach and read a few
    objects in real time. Use `--watch` to invoke. The scene is the legible
    coloured-room variant (the batch run uses the flat gray camera scene)."""
    objs = make_objects()
    print("\n=== P3 watch — the agent approaches and reads each object ===")
    print("  The agent drives up to the object (a grey cylinder ahead) and halts at it.")
    print("  It pauses there until you CLOSE the window, then the next object loads.\n")
    for k in (0, 4, 7):                                 # small-dark, big-dark, big-light
        o = objs[k]
        size = "big" if o["bits"][0] else "small"
        shade = "light" if o["bits"][1] else "dark"
        print(f"  → object: {size}, {shade}  (bits t,v,a = {o['bits']}) — close the window to continue")
        tr = run_trial(o, WHISKERS_5, reaff_on=True, watch=True, cosmetic=True)
        r = tr["readings"]
        print(f"    read: touch={r['touch']:5.1f}°  vision={r['vision']:.2f}  taste={r['taste']:+.2f}  "
              f"located at ({tr['est'][0]:+.2f}, {tr['est'][1]:+.2f}) m (err {tr['loc_err']:.2f})\n")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch()
    else:
        main()
