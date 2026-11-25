# SPDX-License-Identifier: GPL-3.0-or-later
# smn-playground parity tooling. Run from the repository root via playground/tools/parity.sh.
import json, sys, numpy as np, mujoco
sys.path.insert(0, sys.argv[1])
from smn_lab.crawler import build_crawler_xml, apply_ground_friction
from smn_lab.control import MessagingBeam, OpponentBoard
BLOBS=[(0.9,0.1,np.log(3)),(1.7,-0.3,np.log(1/3)),(2.4,0.2,np.log(3)),(1.2,-0.9,np.log(3))]
def terrain(x,y,sig=0.35): return float(np.exp(sum(a*np.exp(-((x-cx)**2+(y-cy)**2)/(2*sig*sig)) for cx,cy,a in BLOBS)))
def run(n,T,uneven):
    m=mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=n, gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)); d=mujoco.MjData(m)
    seg=[m.body(f"seg{k}").id for k in range(n)]
    jq=[m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1,n)]; jv=[m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1,n)]
    ap=[m.actuator(f"m_j{k}_p").id for k in range(1,n)]; an=[m.actuator(f"m_j{k}_n").id for k in range(1,n)]
    beam=MessagingBeam(n_joints=n-1, amp=0.8, freq=0.9); boards=[OpponentBoard(kp=4,kd=0.4,cmax=2.5) for _ in ap]
    mujoco.mj_forward(m,d); out=dict(head=[],bend=[])
    for i in range(int(T/0.002)):
        tc=beam.command(0.002)
        for k in range(n-1):
            a,b,_=boards[k].commands(float(d.qpos[jq[k]]),float(d.qvel[jv[k]]),tc[k],0.0); d.ctrl[ap[k]]=a; d.ctrl[an[k]]=b
        if uneven:
            for b in seg:
                sc=terrain(*d.xpos[b][:2]); apply_ground_friction(m,d,[b],mu_long=0.15*sc,mu_trans=3.0*sc)
        else: apply_ground_friction(m,d,seg,mu_long=0.15,mu_trans=3.0)
        mujoco.mj_step(m,d)
        if (i+1)%250==0: out["head"].append(d.xpos[seg[0]][:2].tolist()); out["bend"].append([float(d.qpos[q]) for q in jq])
    return out
R={"te8_uneven":run(8,30,True),"te8_even":run(8,30,False)}
json.dump(dict(R=R,blobs=[list(b) for b in BLOBS]),open(sys.argv[2],"w"))
for k,v in R.items(): print(k, np.round(v["head"][-1],3))
