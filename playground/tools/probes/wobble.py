"""Probe (24 Nov 2026): what happens when the wobble is not uniform? 8-block crawler, water, 30 s.
Amplitude profiles, a dead joint, a one-sided bias, per-joint frequency spread with and without coupling."""
import sys, numpy as np, mujoco
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
from smn_lab.crawler import build_crawler_xml, apply_anisotropic_drag
from smn_lab.control import MessagingBeam, OpponentBoard
N=8; T=30.0; DT=0.002
def run(amp_profile=None, freq_profile=None, offset=None, coupling=4.0, seed=0):
    m=mujoco.MjModel.from_xml_string(build_crawler_xml(n_seg=N)); d=mujoco.MjData(m)
    seg=[m.body(f"seg{k}").id for k in range(N)]
    jq=[m.jnt_qposadr[m.joint(f"j{k}").id] for k in range(1,N)]; jv=[m.jnt_dofadr[m.joint(f"j{k}").id] for k in range(1,N)]
    ap=[m.actuator(f"m_j{k}_p").id for k in range(1,N)]; an=[m.actuator(f"m_j{k}_n").id for k in range(1,N)]
    beam=MessagingBeam(n_joints=N-1, amp=0.8, freq=0.9, coupling=coupling)
    if freq_profile is not None: beam.w = 2*np.pi*np.asarray(freq_profile)   # per-joint natural frequency
    A = np.ones(N-1) if amp_profile is None else np.asarray(amp_profile)
    O = np.zeros(N-1) if offset is None else np.asarray(offset)
    boards=[OpponentBoard(kp=4,kd=0.4,cmax=2.5) for _ in ap]
    mujoco.mj_forward(m,d); p0=d.xpos[seg[0]][:2].copy(); path=[p0.copy()]; ph0=None
    for i in range(int(T/DT)):
        tc = beam.command(DT)                      # amp*sin(phase)
        tc = A*tc + O
        for k in range(N-1):
            a,b,_=boards[k].commands(d.qpos[jq[k]],d.qvel[jv[k]],tc[k],0); d.ctrl[ap[k]]=a; d.ctrl[an[k]]=b
        apply_anisotropic_drag(m,d,seg,c_long=0.5,c_trans=7.0); mujoco.mj_step(m,d)
        if i==int(10/DT): ph0=beam.phase.copy()
        if i%250==0: path.append(d.xpos[seg[0]][:2].copy())
    path=np.array(path); net=np.hypot(*(path[-1]-path[0])); L=np.sum(np.hypot(*np.diff(path,axis=0).T))
    fr=(beam.phase-ph0)/(2*np.pi*(T-10))     # realised frequency per joint over last 20 s
    hd=np.arctan2(*(path[-1]-path[-20])[::-1]); h0=np.arctan2(*(path[20]-path[0])[::-1])
    turn=np.degrees(np.angle(np.exp(1j*(hd-h0))))
    return net, L, fr.max()-fr.min(), turn
tests = {
 "uniform (bench)":                    {},
 "amplitude tapers head->tail 1->0.3": dict(amp_profile=np.linspace(1,0.3,N-1)),
 "amplitude grows head->tail 0.3->1":  dict(amp_profile=np.linspace(0.3,1,N-1)),
 "one dead joint (j4 amp 0)":          dict(amp_profile=[1,1,1,0,1,1,1]),
 "left-right asymmetry (+0.15 rad)":   dict(offset=np.full(N-1,0.15)),
 "freq spread ±10%, coupling 4":       dict(freq_profile=0.9*np.linspace(0.9,1.1,N-1)),
 "freq spread ±40%, coupling 4":       dict(freq_profile=0.9*np.linspace(0.6,1.4,N-1)),
 "freq spread ±10%, coupling 0":       dict(freq_profile=0.9*np.linspace(0.9,1.1,N-1), coupling=0.0),
}
print(f"{'condition':38s} {'net disp':>8s} {'path':>6s} {'eff':>5s} {'freq spread Hz':>14s} {'heading change':>14s}")
for k,kw in tests.items():
    net,L,fs,turn=run(**kw); print(f"{k:38s} {net:8.2f} {L:6.2f} {net/L:5.2f} {fs:14.3f} {turn:13.0f}°")
