# SPDX-License-Identifier: GPL-3.0-or-later
# smn-playground parity tooling. Run from the repository root via playground/tools/parity.sh.
"""Reference trajectories from smn-lab's OWN classes (not a re-implementation)."""
import json, sys
import numpy as np, mujoco
sys.path.insert(0, sys.argv[1])
from smn_lab.crawler import apply_anisotropic_drag, apply_ground_friction
from smn_lab.control import MessagingBeam, OpponentBoard
from smn_lab.fields import ScalarField
from smn_lab.medusa import apply_medium
M = json.load(open(sys.argv[2]))

def crawler(hab, n, T, field=None, every=0.5):
    m = mujoco.MjModel.from_xml_string(M["crawler"][f"{hab}_{n}"]); d = mujoco.MjData(m)
    seg = [m.body(f"seg{k}").id for k in range(n)]
    jq = [m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1, n)]
    jv = [m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1, n)]
    ap = [m.actuator(f"m_j{k}_p").id for k in range(1, n)]; an = [m.actuator(f"m_j{k}_n").id for k in range(1, n)]
    beam = MessagingBeam(n_joints=n-1, amp=0.8, freq=0.9, turn_gain=(4.0 if field else 0.8))
    boards = [OpponentBoard(kp=4.0, kd=0.4, cmax=2.5) for _ in ap]
    F = ScalarField(field) if field else None
    sL, sR = m.site("sense_L").id, m.site("sense_R").id
    mujoco.mj_forward(m, d); out = []
    for i in range(int(round(T / 0.002))):
        bias = 0.0
        if F: bias = -1.0 * (F.sample(*d.site_xpos[sL][:2]) - F.sample(*d.site_xpos[sR][:2]))
        tc = beam.command(0.002, bias=bias)
        for k in range(n-1):
            ar, al, _ = boards[k].commands(float(d.qpos[jq[k]]), float(d.qvel[jv[k]]), tc[k], 0.0)
            d.ctrl[ap[k]] = ar; d.ctrl[an[k]] = al
        if hab == "aquarium": apply_anisotropic_drag(m, d, seg, c_long=0.5, c_trans=7.0)
        else: apply_ground_friction(m, d, seg, mu_long=0.15, mu_trans=3.0)
        mujoco.mj_step(m, d)
        if (i + 1) % int(round(every / 0.002)) == 0: out.append(d.xpos[seg[0]][:2].tolist())
    return out

def medusa(T, every=0.5):
    sp = M["medusa"]["tent_6"]; m = mujoco.MjModel.from_xml_string(sp["xml"]); d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(len(sp["pos"]))]; out = []
    mujoco.mj_forward(m, d)
    for i in range(int(round(T / 0.001))):
        t = i * 0.001; ctrl = np.zeros(m.nu)
        if (t % 0.5) / 0.5 < 0.15: ctrl[sp["coronal"]] = 13.0
        d.ctrl[:] = ctrl
        apply_medium(m, d, bid, c_quad=9.0, c_lin=0.15, axis=2, axis_gain=2.5)
        mujoco.mj_step(m, d)
        if (i + 1) % int(round(every / 0.001)) == 0: out.append(d.xpos[bid].mean(0).tolist())
    return out

SRC = [[1.6, 0.9, 1.0, 0.9]]
R = {
  "aq3_chemo": crawler("aquarium", 3, 30, SRC),
  "aq8": crawler("aquarium", 8, 15),
  "te8": crawler("terrarium", 8, 15),
  "te8_chemo": crawler("terrarium", 8, 40, [[1.5, 1.2, 1.0, 0.9]]),
  "te12": crawler("terrarium", 12, 15),
  "medusa": medusa(12),
}
json.dump(R, open(sys.argv[3], "w"))
for k, v in R.items(): print(k, np.round(v[-1], 4))
