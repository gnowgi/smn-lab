# SPDX-License-Identifier: GPL-3.0-or-later
# smn-playground parity tooling. Run from the repository root via playground/tools/parity.sh.
"""Reference runs for v2: contacts (bench functions) and Q1 per-zone reafference (Q1's code, noise-free)."""
import json, sys
import numpy as np, mujoco
sys.path.insert(0, sys.argv[1])
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag, apply_ground_friction
from smn_lab.control import MessagingBeam, OpponentBoard
from smn_lab.fields import ScalarField
KW = {"aquarium": {}, "terrarium": dict(gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)}

def run(hab, n, T, src=None, objects=(), walls=True, touch=True, add_at=None, add_obj=None, reaf=False):
    objs = [tuple(map(float, o)) for o in objects]
    def build(prev=None):
        m = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=n, with_walls=walls, touch=touch, objects=objs, **KW[hab]))
        d = mujoco.MjData(m)
        if prev:
            pm, pd = prev
            d.qpos[:] = pd.qpos; d.qvel[:] = pd.qvel; d.ctrl[:] = pd.ctrl; d.qacc_warmstart[:] = pd.qacc_warmstart; d.time = pd.time
        mujoco.mj_forward(m, d); return m, d
    m, d = build()
    ids = lambda m: dict(seg=[m.body(f"seg{k}").id for k in range(n)],
        jq=[m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1, n)], jv=[m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1, n)],
        ap=[m.actuator(f"m_j{k}_p").id for k in range(1, n)], an=[m.actuator(f"m_j{k}_n").id for k in range(1, n)],
        sL=m.site("sense_L").id, sR=m.site("sense_R").id,
        zL=[m.site(f"seg{k}_L").id for k in range(n)], zR=[m.site(f"seg{k}_R").id for k in range(n)],
        ta=[m.sensor(f"touch{k}").adr[0] for k in range(n)] if touch else [])
    I = ids(m)
    beam = MessagingBeam(n_joints=n-1, amp=0.8, freq=0.9, turn_gain=(4.0 if src else 0.8))
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in I["ap"]]
    F = ScalarField([src]) if src else None
    # Q1 state
    WIN, T_LEARN = 125, 8.0
    vel = np.zeros(6); disp = np.zeros((n, 2)); r_prev = None; scale = np.ones(n); cn = np.zeros(n); cd = np.zeros(n)
    out = dict(head=[], touch=[], res=[], dr=[])
    for i in range(int(round(T / 0.002))):
        if add_at is not None and i == int(round(add_at / 0.002)):
            objs.append(tuple(map(float, add_obj))); m, d = build((m, d)); I = ids(m)
        bias = 0.0
        if F: bias = -1.0 * (F.sample(*d.site_xpos[I["sL"]][:2]) - F.sample(*d.site_xpos[I["sR"]][:2]))
        tc = beam.command(0.002, bias=bias)
        for k in range(n-1):
            ar, al, _ = boards[k].commands(float(d.qpos[I["jq"][k]]), float(d.qvel[I["jv"][k]]), tc[k], 0.0)
            d.ctrl[I["ap"][k]] = ar; d.ctrl[I["an"][k]] = al
        if hab == "aquarium": apply_anisotropic_drag(m, d, I["seg"], c_long=0.5, c_trans=7.0)
        else: apply_ground_friction(m, d, I["seg"], mu_long=0.15, mu_trans=3.0)
        mujoco.mj_step(m, d)
        if reaf:
            t = i * 0.002
            for k in range(n):
                mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, I["seg"][k], vel, 0)
                disp[k, 0] += vel[3] * 0.002; disp[k, 1] += vel[4] * 0.002
            if i % WIN == 0:
                pts, vals, r = [], [], np.zeros(n)
                for k in range(n):
                    xL, yL = d.site_xpos[I["zL"][k]][:2]; xR, yR = d.site_xpos[I["zR"][k]][:2]
                    vL = F.sample(xL, yL) if F else 0.0; vR = F.sample(xR, yR) if F else 0.0
                    r[k] = 0.5 * (vL + vR); pts += [(xL, yL), (xR, yR)]; vals += [vL, vR]
                pts = np.array(pts); vals = np.array(vals)
                A = np.column_stack([np.ones(len(pts)), pts[:, 0], pts[:, 1]])
                _, gx, gy = np.linalg.lstsq(A, vals, rcond=None)[0]
                basis = gx * disp[:, 0] + gy * disp[:, 1]
                if r_prev is not None:
                    dr = r - r_prev; res = dr - scale * basis
                    if t < T_LEARN: cn += dr * basis; cd += basis ** 2
                    out["res"].append(res.tolist()); out["dr"].append(dr.tolist())
                    if t < T_LEARN:
                        g = cd > 1e-12; scale[g] = cn[g] / cd[g]
                r_prev = r; disp[:] = 0.0
        if (i + 1) % 250 == 0:
            out["head"].append(d.xpos[I["seg"][0]][:2].tolist())
            out["touch"].append([float(d.sensordata[a]) for a in I["ta"]])
    return out

R = {
 "c1like_aq3": run("aquarium", 3, 40, src=(1.9, 1.05, 1.0, 0.9), objects=[(0.78, 0.0, 0.12)]),
 "te8_rocks": run("terrarium", 8, 30, objects=[(1.0, 0.1, 0.12), (1.6, -0.3, 0.2)], add_at=10.0, add_obj=(2.0, 0.2, 0.12)),
 "aq8_walls": run("aquarium", 8, 40, objects=[], walls=True),
 "reaf_aq6": run("aquarium", 6, 30, src=(1.5, 0.8, 1.0, 0.9), objects=[], reaf=True),
}
json.dump(R, open(sys.argv[2], "w"))
for k, v in R.items():
    tmax = max((max(x) for x in v["touch"] if x), default=0)
    print(k, "head end", np.round(v["head"][-1], 3), "touch max", round(tmax, 3), "res windows", len(v["res"]))
