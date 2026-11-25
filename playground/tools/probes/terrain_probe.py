"""Probe (25 Nov 2026): does terrain resistance change the wobble? Uniform friction scaled x0.3..x10,
entrainment off/on (inter, gain 2). Logs realized bend, f_beam, f_body, speed, muscle saturation."""
import sys, numpy as np, mujoco
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from smn_lab.crawler import build_crawler_xml, apply_ground_friction
from smn_lab.control import MessagingBeam, OpponentBoard
N=8; DT=0.002; T=20.0
def run(scale, entrain=0.0):
    m=mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N, gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)); d=mujoco.MjData(m)
    seg=[m.body(f"seg{k}").id for k in range(N)]
    jq=[m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1,N)]; jv=[m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1,N)]
    ap=[m.actuator(f"m_j{k}_p").id for k in range(1,N)]; an=[m.actuator(f"m_j{k}_n").id for k in range(1,N)]
    beam=MessagingBeam(n_joints=N-1, amp=0.8, freq=0.9, entrain=entrain, entrain_mode="inter")
    boards=[OpponentBoard(kp=4,kd=0.4,cmax=2.5) for _ in ap]
    mujoco.mj_forward(m,d); th_log=[]; p0=None; ph0=None; sat=0
    for i in range(int(T/DT)):
        th=np.array([d.qpos[q] for q in jq]); thd=np.array([d.qvel[v] for v in jv])
        tc=beam.command(DT, theta=th, theta_dot=thd)
        for k in range(N-1):
            a,b,_=boards[k].commands(th[k],thd[k],tc[k],0); d.ctrl[ap[k]]=a; d.ctrl[an[k]]=b; sat+= (a>=2.5 or b>=2.5)
        apply_ground_friction(m,d,seg,mu_long=0.15*scale,mu_trans=3.0*scale); mujoco.mj_step(m,d)
        if i==int(5/DT): p0=d.xpos[seg[0]][:2].copy(); ph0=beam.phase.copy()
        if i>=int(5/DT): th_log.append(th)
    th_log=np.array(th_log); amp=(th_log.max(0)-th_log.min(0))/2
    x=th_log[:,3]-th_log[:,3].mean(); zc=np.sum((x[:-1]<0)&(x[1:]>=0)); f_body=zc/(T-5)
    f_beam=(beam.phase[3]-ph0[3])/(2*np.pi*(T-5))
    disp=np.hypot(*(d.xpos[seg[0]][:2]-p0))
    return amp.mean(), f_beam, f_body, disp/(T-5), sat/((T/DT)*(N-1))
print(f"{'friction ×':>10} {'entrain':>7} {'bend amp (rad, cmd 0.8)':>23} {'f_beam':>7} {'f_body':>7} {'speed m/s':>9} {'muscle saturated':>16}")
for e in (0.0, 2.0):
    for s in (0.3, 1, 3, 10):
        a,fb,fo,v,sat=run(s,e); print(f"{s:>10} {e:>7} {a:>23.3f} {fb:>7.3f} {fo:>7.3f} {v:>9.3f} {sat:>15.0%}")

