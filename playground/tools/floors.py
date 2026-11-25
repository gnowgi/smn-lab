# SPDX-License-Identifier: GPL-3.0-or-later
"""The bench's own round-off floor: how far the PYTHON bench moves when its initial state is
perturbed by 1e-15. Browser-vs-bench deviations are judged against these numbers (contact runs and
the chaotic medusa cannot be bit-identical across builds; they should stay inside this floor).
Usage: python3 floors.py REPO_ROOT WORK"""
import json, sys, runpy, numpy as np, mujoco
REPO, W = sys.argv[1], sys.argv[2]
sys.path.insert(0, REPO)
from smn_lab.medusa import apply_medium
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag, apply_ground_friction
from smn_lab.control import MessagingBeam, OpponentBoard
from smn_lab.fields import ScalarField
sp = json.load(open(f"{W}/models_full.json"))["medusa"]["tent_6"]

def medusa_z24(eps):
    m = mujoco.MjModel.from_xml_string(sp["xml"]); d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(len(sp["pos"]))]
    d.qpos[0] += eps; mujoco.mj_forward(m, d); c0 = d.xpos[bid].mean(0).copy()
    for i in range(24000):
        c = np.zeros(m.nu)
        if ((i * 0.001) % 0.5) / 0.5 < 0.15: c[sp["coronal"]] = 13.0
        d.ctrl[:] = c; apply_medium(m, d, bid, c_quad=9.0, c_lin=0.15, axis=2, axis_gain=2.5); mujoco.mj_step(m, d)
    return float((d.xpos[bid].mean(0) - c0)[2])

KW = {"aquarium": {}, "terrarium": dict(gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)}
def contact(hab, n, T, eps, src=None, objects=(), add_at=None, add_obj=None):
    objs = [tuple(map(float, o)) for o in objects]
    def build(prev=None):
        m = mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=n, with_walls=True, touch=True, objects=objs, **KW[hab])); d = mujoco.MjData(m)
        if prev: d.qpos[:] = prev.qpos; d.qvel[:] = prev.qvel; d.ctrl[:] = prev.ctrl; d.qacc_warmstart[:] = prev.qacc_warmstart; d.time = prev.time
        mujoco.mj_forward(m, d); return m, d
    m, d = build(); d.qpos[0] += eps; mujoco.mj_forward(m, d)
    beam = MessagingBeam(n_joints=n - 1, amp=0.8, freq=0.9, turn_gain=(4.0 if src else 0.8))
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in range(n - 1)]; F = ScalarField([src]) if src else None; out = []
    for i in range(int(round(T / 0.002))):
        if add_at is not None and i == int(round(add_at / 0.002)): objs.append(tuple(map(float, add_obj))); m, d = build(d)
        seg = [m.body(f"seg{k}").id for k in range(n)]
        bias = -1.0 * (F.sample(*d.site_xpos[m.site("sense_L").id][:2]) - F.sample(*d.site_xpos[m.site("sense_R").id][:2])) if F else 0.0
        tc = beam.command(0.002, bias=bias)
        for k in range(n - 1):
            jq = m.jnt_qposadr[m.joint(f"j{k+1}").id]; jv = m.jnt_dofadr[m.joint(f"j{k+1}").id]
            a, b, _ = boards[k].commands(float(d.qpos[jq]), float(d.qvel[jv]), tc[k], 0.0)
            d.ctrl[m.actuator(f"m_j{k+1}_p").id] = a; d.ctrl[m.actuator(f"m_j{k+1}_n").id] = b
        if hab == "aquarium": apply_anisotropic_drag(m, d, seg, c_long=0.5, c_trans=7.0)
        else: apply_ground_friction(m, d, seg, mu_long=0.15, mu_trans=3.0)
        mujoco.mj_step(m, d)
        if (i + 1) % 250 == 0: out.append(d.xpos[seg[0]][:2].copy())
    return np.array(out)

floor = lambda f: float(np.abs(f(0.0) - f(1e-15)).max())
res = {
  "medusa_z24": sorted(medusa_z24(e) for e in (0, 1e-15, 2e-15, -1e-15, 3e-15, -2e-15, 5e-15, 1e-14, -1e-14, 2e-14)),
  "c1like_aq3": floor(lambda e: contact("aquarium", 3, 40, e, src=(1.9, 1.05, 1.0, 0.9), objects=[(0.78, 0.0, 0.12)])),
  "te8_rocks": floor(lambda e: contact("terrarium", 8, 30, e, objects=[(1.0, 0.1, 0.12), (1.6, -0.3, 0.2)], add_at=10.0, add_obj=(2.0, 0.2, 0.12))),
}
print(json.dumps(res, indent=1)); json.dump(res, open(f"{W}/floors.json", "w"))
