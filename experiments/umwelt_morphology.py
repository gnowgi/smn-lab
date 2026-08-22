# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Umwelt by morphology: same world, different anatomies -> different world-models.

The headline experiment. One FIXED enriched world (walls + solid cylinders that are
simultaneously (a) field sources, (b) touchable solids, (c) visible objects), placed at
tiered lateral offsets from the crawl corridor: NEAR (brushed by the body), MID (within
field/vision reach, not contacted), FAR (line-of-sight only). The world is held constant.

We vary only the AGENT'S ANATOMY:
  * sensory access -- which transducers the body is wired to read (field / touch / vision
    / all). The physical body is identical (it still collides with the solids); only the
    SENSING differs.
  * size -- segment scale h (a larger body sweeps/reaches/sees differently).

For each morphology we measure, per world-aspect, what its Umwelt manages to construct:
  DETECTION FRACTION = fraction of the world's objects the anatomy registers via that
  aspect, at that aspect's own natural detection event --
    field:  gradient read above baseline at closest approach (reach ~ field sigma);
    touch:  a segment's touch skin fires on contact (reach ~ body sweep, contact-only);
    vision: the reafference patch-modulator's aggregate residual breaks its calibrated
            self-motion floor while the object is in the FOV (reach ~ line of sight).
  A morphology lacking a transducer yields a STRUCTURAL ZERO for that aspect -- the
  Umwelt simply does not contain it. Where the transducer is present, the score is graded
  by the modality's reach and by body size.

The result is a morphology x world-aspect coverage matrix: each anatomy constructs a
different, non-interchangeable subset of the same world -- the Umwelt / caterpillar-butterfly
thesis, made a measurement.

Run:        MUJOCO_GL=osmesa MPLBACKEND=Agg ../.venv/bin/python umwelt_morphology.py
Diagnose:   MUJOCO_GL=osmesa MPLBACKEND=Agg ../.venv/bin/python umwelt_morphology.py diag
"""
from __future__ import annotations
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.crawler import build_crawler_xml, apply_ground_friction, apply_anisotropic_drag
from smn_lab.control import MessagingBeam, OpponentBoard, DeadReckoner
from smn_lab.fields import ScalarField
from smn_lab.vision import EyeCamera, AnalyticalFramePredictor, PatchResidualModulator
from smn_lab.self_model import read_all
from smn_lab.metrics import seriation_order, order_accuracy
from smn_lab.report import RunRecord, render

DT = 0.002
N_SEG = 8
T_END = 60.0                          # all sizes reach the far wall by 60 s -> travel-matched
MU_LONG, MU_TRANS = 0.15, 3.0
FRAME = 64
FOV = 90.0
RENDER_EVERY = 50                     # vision cadence (steps): 0.10 s (yaw drifts slowly)
SAMPLE_EVERY = 20                     # field/touch/pose logging cadence

# ---- THE FIXED WORLD (object x, y, radius, tier) -- identical for every morphology ----
# tiers: 'near' (contactable), 'mid' (field+vision), 'far' (vision only)
WORLD_OBJ = [
    (0.55,  0.09, 0.06, "near"),
    (0.85, -0.09, 0.06, "near"),
    (1.15,  0.30, 0.06, "mid"),
    (1.45, -0.30, 0.06, "mid"),
    (1.25,  0.62, 0.06, "far"),
    (1.70, -0.62, 0.06, "far"),
]
SRC_AMP, SRC_SIG = 1.0, 0.18          # each object is also a Gaussian field source
FIELD_THRESH = 0.15                   # gradient read counts as "sensed"
TOUCH_THRESH = 1e-3                   # touch skin fires
ARENA = 2.2

# ---- MORPHOLOGIES (world constant; anatomy varies) ----
# full-body scale: h (length), w (width) and sense_off (sensor stand-off) scale together,
# so a 'large' body genuinely has greater lateral sweep and a wider sensor baseline.
_W0, _SO0 = 0.025, 0.06
def _scale(h):
    f = h / 0.07
    return dict(h=h, w=_W0 * f, sense_off=_SO0 * f)

MORPHS = [
    dict(name="field-only", mods={"field"},          **_scale(0.07)),
    dict(name="touch-only", mods={"touch"},          **_scale(0.07)),
    dict(name="vision-only", mods={"vision"},        **_scale(0.07)),
    dict(name="all-normal", mods={"field","touch","vision"}, **_scale(0.07)),
    # size axis: longitudinal (h) scaling only, held travel-matched (all reach the far
    # wall by T_END). Full-body scaling (w+sense_off too) was tried but re-introduces a
    # locomotion-efficiency confound (a wider body drags more and travels less), so the
    # clean size test keeps width/stand-off fixed. See note in the paper doc.
    dict(name="all-large",  mods={"field","touch","vision"}, h=0.11, w=_W0, sense_off=_SO0),
]
SEEDS = [0, 1, 2]


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def build(h, want_vision, w=0.025, sense_off=0.06):
    objects = [(o[0], o[1], o[2]) for o in WORLD_OBJ]
    xml = build_crawler_xml(n_seg=N_SEG, h=h, w=w, sense_off=sense_off,
                            gravity_on=False, joint_damping=0.03,
                            bend_limit_deg=50.0, with_walls=True, arena_half=ARENA,
                            objects=objects, touch=True)
    if want_vision:
        cam = ('\n      <camera name="eye" pos="%.3f 0 0.03" xyaxes="0 -1 0 0 0 1" '
               'fovy="%.1f"/>' % (h, FOV))
        xml = xml.replace('<body name="seg0" pos="0 0 0.1">',
                          '<body name="seg0" pos="0 0 0.1">' + cam)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    ids = dict(
        seg=[m.body(f"seg{k}").id for k in range(N_SEG)],
        sL=[m.site(f"seg{k}_L").id for k in range(N_SEG)],
        sR=[m.site(f"seg{k}_R").id for k in range(N_SEG)],
        ap=[m.actuator(f"m_j{k}_p").id for k in range(1, N_SEG)],
        an=[m.actuator(f"m_j{k}_n").id for k in range(1, N_SEG)],
        jq=[m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1, N_SEG)],
        jv=[m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1, N_SEG)],
        touch=[m.sensor_adr[m.sensor(f"touch{k}").id] for k in range(N_SEG)],
        yaw=m.jnt_qposadr[m.joint("yaw").id],
        seg_geom={m.geom(f"seg{k}_geom").id for k in range(N_SEG)},
        obj_geom={m.geom(f"obj{j}").id: j for j in range(len(WORLD_OBJ))},
    )
    return m, d, ids


def run_morph(morph, seed):
    want_vision = "vision" in morph["mods"]
    rng = np.random.default_rng(seed)
    m, d, ids = build(morph["h"], want_vision, w=morph["w"], sense_off=morph["sense_off"])
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9)
    boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in ids["ap"]]
    dr = DeadReckoner()
    field = ScalarField([(o[0], o[1], SRC_AMP, SRC_SIG) for o in WORLD_OBJ])
    if want_vision:
        eye = EyeCamera(m, "eye", width=FRAME, height=FRAME)
        pred = AnalyticalFramePredictor(width=FRAME, fov_deg=FOV)
        mod = PatchResidualModulator(frame_size=FRAME, patch_grid=8)
    mujoco.mj_forward(m, d)

    vel = np.zeros(6)
    true_head, dr_head = [], []
    field_read = []                     # per-sample max-over-segments field reading
    touched = np.zeros(len(WORLD_OBJ), bool)   # per-object contact registered (skin)
    seg_geom, obj_geom = ids["seg_geom"], ids["obj_geom"]
    # vision logs (decimated)
    vframes, vyaw, vhead, vheading = [], [], [], []

    n = int(T_END / DT)
    for i in range(n):
        tc = beam.command(DT)
        for k in range(N_SEG - 1):
            th = float(d.qpos[ids["jq"][k]]); thd = float(d.qvel[ids["jv"][k]])
            # mild seed-dependent gait perturbation -> genuinely different trajectories,
            # so the coverage pattern is shown robust (not a single lucky run)
            tcm = tc[k] + 0.15 * rng.standard_normal()
            ar, al, _ = boards[k].commands(th, thd, tcm, 0.0)
            d.ctrl[ids["ap"][k]] = ar; d.ctrl[ids["an"][k]] = al
        apply_ground_friction(m, d, ids["seg"], mu_long=MU_LONG, mu_trans=MU_TRANS)
        mujoco.mj_step(m, d)
        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, ids["seg"][0], vel, 1)
        dr.update(vel[3], vel[4], vel[2], DT)

        # per-object contact attribution: a segment geom touching obj{j} geom
        for c in range(d.ncon):
            g1, g2 = d.contact[c].geom1, d.contact[c].geom2
            if g1 in seg_geom and g2 in obj_geom:
                touched[obj_geom[g2]] = True
            elif g2 in seg_geom and g1 in obj_geom:
                touched[obj_geom[g1]] = True

        if i % SAMPLE_EVERY == 0:
            hx, hy = d.xpos[ids["seg"][0]][:2]
            true_head.append(np.array([hx, hy]))
            dr_head.append(np.array([dr.x, dr.y]))
            rr = [0.5 * (field.sample(*d.site_xpos[ids["sL"][k]][:2]) +
                         field.sample(*d.site_xpos[ids["sR"][k]][:2])) for k in range(N_SEG)]
            field_read.append(float(np.max(rr)))
        if want_vision and i % RENDER_EVERY == 0:
            fr = eye.snap(d)
            yaw = float(d.qpos[ids["yaw"]])
            vframes.append(fr); vyaw.append(yaw)
            vhead.append(d.xpos[ids["seg"][0]][:2].copy()); vheading.append(yaw)

    if want_vision:
        eye.close()

    true_head = np.array(true_head); dr_head = np.array(dr_head)
    field_read = np.array(field_read)

    # ---- per-object detection ----
    win = max(2, int(0.6 / (DT * SAMPLE_EVERY)))    # +/- window (samples) around closest approach
    field_det, touch_det, vision_det = [], [], []
    field_dr, vision_dr = [], []                     # dead-reckoned est at detection (layout)
    travel = float(np.linalg.norm(true_head[-1] - true_head[0]))

    # vision floor calibration: aggregate residual on EMPTY-FOV frames
    vis_resid = None; vis_floor = None
    if want_vision and len(vframes) > 3:
        agg = []; infov_obj = []
        for t in range(1, len(vframes)):
            dtheta = vyaw[t] - vyaw[t - 1]
            phat = pred.predict(vframes[t - 1], dtheta)
            agg.append(float(np.abs(vframes[t] - phat).mean()))
            # which objects are in FOV at frame t (experimenter bookkeeping via true pose)
            hx, hy = vhead[t]; head_dir = vheading[t]
            inf = set()
            for j, o in enumerate(WORLD_OBJ):
                bearing = wrap(math.atan2(o[1] - hy, o[0] - hx) - head_dir)
                dist = math.hypot(o[0] - hx, o[1] - hy)
                if abs(bearing) < math.radians(FOV / 2) and dist < 2.2 and (o[0] - hx) > -0.05:
                    inf.add(j)
            infov_obj.append(inf)
        agg = np.array(agg)
        empty = np.array([len(s) == 0 for s in infov_obj])
        if empty.sum() >= 3:
            vis_floor = float(np.percentile(agg[empty], 95))
        else:
            vis_floor = float(np.percentile(agg, 50))    # fallback
        vis_resid = (agg, infov_obj)

    for j, o in enumerate(WORLD_OBJ):
        d2 = np.linalg.norm(true_head - np.array(o[:2]), axis=1)
        ci = int(np.argmin(d2))
        lo, hi = max(0, ci - win), min(len(true_head), ci + win + 1)
        # FIELD -- attributed to THIS object's own Gaussian at closest approach
        # (reach set by the field sigma; not the summed ambient field)
        if "field" in morph["mods"]:
            close_j = float(d2[ci])
            fval = SRC_AMP * math.exp(-close_j ** 2 / (2 * SRC_SIG ** 2))
            det = fval > FIELD_THRESH
            field_det.append(det)
            if det:
                field_dr.append(((o[0], o[1]), (dr_head[ci][0], dr_head[ci][1])))
        else:
            field_det.append(False)
        # TOUCH (contact-attributed to this specific object)
        if "touch" in morph["mods"]:
            touch_det.append(bool(touched[j]))
        else:
            touch_det.append(False)
        # VISION
        if want_vision and vis_resid is not None:
            agg, infov_obj = vis_resid
            seen = False
            for t in range(len(agg)):
                if j in infov_obj[t] and agg[t] > vis_floor:
                    seen = True; break
            vision_det.append(seen)
        else:
            vision_det.append(False)

    return dict(
        travel=travel,
        field=np.array(field_det, float),
        touch=np.array(touch_det, float),
        vision=np.array(vision_det, float),
        field_read=field_read, touched=touched,
        vis_floor=vis_floor,
    )


def diag():
    print("DIAGNOSTIC: all-normal, seed 0 -- corridor & per-object encounter geometry")
    m, d, ids = build(0.07, True)
    beam = MessagingBeam(n_joints=N_SEG - 1, amp=0.8, freq=0.9)
    boards = [OpponentBoard(kp=4, kd=0.4, cmax=2.5) for _ in ids["ap"]]
    field = ScalarField([(o[0], o[1], SRC_AMP, SRC_SIG) for o in WORLD_OBJ])
    mujoco.mj_forward(m, d)
    path = []
    close = [1e9] * len(WORLD_OBJ)
    fpeak = [0.0] * len(WORLD_OBJ)
    tpeak = [0.0] * len(WORLD_OBJ)
    for i in range(int(T_END / DT)):
        tc = beam.command(DT)
        for k in range(N_SEG - 1):
            th = float(d.qpos[ids["jq"][k]]); thd = float(d.qvel[ids["jv"][k]])
            ar, al, _ = boards[k].commands(th, thd, tc[k], 0.0)
            d.ctrl[ids["ap"][k]] = ar; d.ctrl[ids["an"][k]] = al
        apply_ground_friction(m, d, ids["seg"], mu_long=MU_LONG, mu_trans=MU_TRANS)
        mujoco.mj_step(m, d)
        if i % SAMPLE_EVERY == 0:
            hx, hy = d.xpos[ids["seg"][0]][:2]
            path.append((hx, hy))
            rr = max(0.5 * (field.sample(*d.site_xpos[ids["sL"][k]][:2]) +
                            field.sample(*d.site_xpos[ids["sR"][k]][:2])) for k in range(N_SEG))
            tt = max(d.sensordata[a] for a in ids["touch"])
            for j, o in enumerate(WORLD_OBJ):
                dist = math.hypot(hx - o[0], hy - o[1])
                if dist < close[j]:
                    close[j] = dist
                fpeak[j] = max(fpeak[j], rr if dist < 0.4 else 0.0)
                tpeak[j] = max(tpeak[j], tt if dist < 0.35 else 0.0)
    path = np.array(path)
    print(f"travel = {np.linalg.norm(path[-1]-path[0]):.2f}; head x range "
          f"{path[:,0].min():.2f}..{path[:,0].max():.2f}; y range {path[:,1].min():.2f}..{path[:,1].max():.2f}")
    for j, o in enumerate(WORLD_OBJ):
        print(f"  obj{j} {o[3]:>4} at ({o[0]:.2f},{o[1]:+.2f}) closest={close[j]:.3f} "
              f"field_peak~{fpeak[j]:.2f} touch_peak~{tpeak[j]:.3f}")


BAB_WARM, BAB_REC = 3.0, 20.0
PROBE_Y, PROBE_AMP, PROBE_SIG = 0.30, 1.0, 0.24


def selfframe_run(morph, seed=0):
    """Give a morphology its faithful SELF-FRAME world-model (the diagram-grammar card),
    on a self-model RECOVERED FROM MOVEMENT -- not head-pose.

    Coordinated locomotion tracks command phase, not body topology, so we recover the
    self-model from an independent-babble phase (the modulation that earns a self-model);
    then, with the body still, we read a probe field beside the mid-body and localize it
    on the recovered self-graph. Returns (OMEGA, node_field-or-None, order_acc).
    """
    rng = np.random.default_rng(seed)
    m, d, ids = build(morph["h"], want_vision=False, w=morph["w"], sense_off=morph["sense_off"])
    nj = len(ids["ap"]); vel = np.zeros(6)
    mujoco.mj_forward(m, d)

    # --- PHASE A: babble -> recover the self-model from segment co-motion ---
    tau = np.zeros(nj)
    n_warm, n_rec = int(BAB_WARM / DT), int(BAB_REC / DT)
    OMEGA = np.zeros((n_rec, N_SEG))
    for i in range(n_warm + n_rec):
        tau += (-tau / 0.15) * DT + 8.0 * np.sqrt(DT) * rng.standard_normal(nj)
        for k in range(nj):
            d.ctrl[ids["ap"][k]] = float(np.clip(tau[k], 0.0, 2.5))
            d.ctrl[ids["an"][k]] = float(np.clip(-tau[k], 0.0, 2.5))
        apply_anisotropic_drag(m, d, ids["seg"], c_long=0.6, c_trans=4.0)
        mujoco.mj_step(m, d)
        if i >= n_warm:
            for s in range(N_SEG):
                mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, ids["seg"][s], vel, 0)
                OMEGA[i - n_warm, s] = vel[2]
    G = np.abs(read_all(OMEGA, OMEGA)); G = 0.5 * (G + G.T); np.fill_diagonal(G, 0.0)
    oacc = float(order_accuracy(seriation_order(G)))

    # --- PHASE B: still -> read a probe field beside the mid-body (field-sensing only) ---
    node_field = None
    if "field" in morph["mods"]:
        d.qpos[:] = 0.0; d.qvel[:] = 0.0; d.ctrl[:] = 0.0
        mujoco.mj_forward(m, d)
        mid = N_SEG // 2
        mx = 0.5 * (d.site_xpos[ids["sL"][mid]][0] + d.site_xpos[ids["sR"][mid]][0])
        my = 0.5 * (d.site_xpos[ids["sL"][mid]][1] + d.site_xpos[ids["sR"][mid]][1])
        probe = ScalarField([(mx, my + PROBE_Y, PROBE_AMP, PROBE_SIG)])
        acc = np.zeros(N_SEG)
        for _ in range(200):
            apply_anisotropic_drag(m, d, ids["seg"], c_long=0.6, c_trans=4.0)
            mujoco.mj_step(m, d)
            acc += [0.5 * (probe.sample(*d.site_xpos[ids["sL"][s]][:2]) +
                           probe.sample(*d.site_xpos[ids["sR"][s]][:2])) for s in range(N_SEG)]
        node_field = {s: float(acc[s] / 200.0) for s in range(N_SEG)}
    return OMEGA, node_field, oacc


def selfframe_records(cov):
    """Route every morphology through the ONE results module: recover its self-model,
    localize the world on the recovered self-graph, emit the canonical card + emergent
    diagnostics + JSON, with the Umwelt coverage fractions attached as metrics. This is
    the diagram-grammar-faithful world-model (self-graph, not head-pose)."""
    print("\nSelf-frame world-model per morphology (recovered self-graph) via smn_lab.report")
    print("-" * 78)
    for mo in MORPHS:
        omega, node_field, oacc = selfframe_run(mo, seed=0)
        c = cov[mo["name"]]
        render(
            RunRecord(
                name=f"umwelt_{mo['name']}",
                omega=omega, node_field=node_field, modality="chem",
                metrics={"field_cov": float(np.mean(c["field"])),
                         "touch_cov": float(np.mean(c["touch"])),
                         "vision_cov": float(np.mean(c["vision"])),
                         "selfmodel_order_acc": oacc},
                meta={"morphology": mo["name"], "modalities": sorted(mo["mods"]), "h": mo["h"]},
            ),
            spec=dict(prefix=f"umwelt_{mo['name']}",
                      suptitle=f"Umwelt — {mo['name']} (world-model on the recovered self-graph)"),
        )


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "diag":
        diag(); return
    # aspects x morph coverage
    cov = {mo["name"]: {"field": [], "touch": [], "vision": []} for mo in MORPHS}
    travels = {mo["name"]: [] for mo in MORPHS}
    for mo in MORPHS:
        for s in SEEDS:
            r = run_morph(mo, s)
            for asp in ("field", "touch", "vision"):
                cov[mo["name"]][asp].append(r[asp].mean())
            travels[mo["name"]].append(r["travel"])

    names = [mo["name"] for mo in MORPHS]
    M = np.array([[np.mean(cov[n][a]) for a in ("field", "touch", "vision")] for n in names])
    S = np.array([[np.std(cov[n][a]) for a in ("field", "touch", "vision")] for n in names])
    print(f"\nUmwelt coverage matrix ({len(SEEDS)} perturbed-gait seeds): fraction of the world "
          f"each anatomy constructs, per aspect")
    print("=" * 78)
    print(f"{'morphology':<14} {'FIELD':>10} {'TOUCH':>10} {'VISION':>10}   travel")
    for i, n in enumerate(names):
        print(f"{n:<14} {M[i,0]:>5.2f}+/-{S[i,0]:.2f} {M[i,1]:>5.2f}+/-{S[i,1]:.2f} "
              f"{M[i,2]:>5.2f}+/-{S[i,2]:.2f}   {np.mean(travels[n]):.2f}")
    print("=" * 78)
    print("Structural zeros where the transducer is absent; graded by reach & size where present.")
    print("Same world, different anatomies -> different Umwelten.\n")

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["field", "touch", "vision"])
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names)
    for i in range(len(names)):
        for jx in range(3):
            ax.text(jx, i, f"{M[i,jx]:.2f}", ha="center", va="center",
                    color="w" if M[i, jx] < 0.6 else "k", fontsize=10)
    ax.set_title("Umwelt coverage matrix\nfraction of the world constructed, by anatomy x aspect")
    fig.colorbar(im, label="detection fraction")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "umwelt_morphology.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")

    # canonical per-morphology records through the ONE module: the world-model now sits
    # on each anatomy's RECOVERED SELF-GRAPH (diagram-grammar faithful), not head-pose.
    selfframe_records(cov)


if __name__ == "__main__":
    main()
