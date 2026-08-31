# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Two-layer disk: perturb the OUTER face -- does it reach the inner face, or stop at the rim?

Question (G. Nagarjuna): a perturbation on the outer layer -- how does it propagate across
the net? Does it reach the inner layer, or stop at the rim?

The mesoglea between the faces carries only messaging (IN) links, which are NON-mechanical.
So the ONLY mechanical bridge between the two faces is the RIM FOLD. A mechanical
perturbation on the outer face can therefore reach the inner face by exactly one route:
travel across the outer sheet to the rim, cross the fold, and spread inward. Prediction:
  * the response is large at the touch and DECAYS across the outer sheet (overdamped -> the
    DFN is decremental);
  * the inner face feels only a weak, RIM-FIRST echo (whatever leaked across the fold);
  * CUT the rim fold and the inner face feels NOTHING -- proving the rim is the sole gate.

So it does not 'stop at the rim'; the rim is the doorway. Everything that crosses, crosses
there. That is exactly the two-network point on this body: the mechanical (self-model) net
is decremental and rim-gated, so the inner face (the gut) is mechanically SHIELDED from every
poke on the skin. Knowing about the touch without being yanked by it is the job of the IN
messaging net (non-decremental, across the mesoglea) -- the motivation, not simulated here.

No self-model recovery here; a single mechanical pulse, watched as it spreads.

Run:  ../.venv/bin/python disk_perturbation_propagation.py
"""
from __future__ import annotations
import os, sys, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import mujoco

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.lattice import _lattice_mjcf

DT = 0.002
N_SPOKE, N_RING = 8, 4
RSTEP = 0.09
ZGAP = 0.06
PULSE_STEPS, WIN_STEPS = 20, 600            # 0.04 s push, then 1.2 s to watch it spread
FORCE = 12.0
THR = 2e-4                                   # speed threshold for 'the wavefront arrived'


def disk_spec(rim_fold=True):
    """Two coaxial polar-disk faces; within-face f springs; the rim fold is the ONLY
    mechanical bridge (omitted when rim_fold=False). Returns pos, edges, face, ring, layout."""
    pos, face, ring, layout = [], [], [], {}
    NPF = N_RING * N_SPOKE

    def io(r, c): return r * N_SPOKE + c
    def ii(r, c): return NPF + r * N_SPOKE + c

    XOFF = (N_RING + 2) * RSTEP * 2.4
    for fc, zf, xoff in (("outer", +ZGAP, 0.0), ("inner", -ZGAP, XOFF)):
        for r in range(N_RING):
            rad = (r + 1) * RSTEP
            for c in range(N_SPOKE):
                th = 2 * np.pi * c / N_SPOKE
                pos.append((rad * np.cos(th), rad * np.sin(th), zf))
                face.append(fc); ring.append(r)
                layout[len(pos) - 1] = (xoff + rad * np.cos(th), rad * np.sin(th))

    edges = []
    for fn in (io, ii):
        for r in range(N_RING):
            for c in range(N_SPOKE):
                edges.append((fn(r, c), fn(r, (c + 1) % N_SPOKE)))
                if r < N_RING - 1:
                    edges.append((fn(r, c), fn(r + 1, c)))
    if rim_fold:
        for c in range(N_SPOKE):
            edges.append((io(N_RING - 1, c), ii(N_RING - 1, c)))     # the ONLY bridge
    return (np.array(pos), edges, np.array(face), np.array(ring), layout, io, ii)


def build(pos, edges, name):
    xml = _lattice_mjcf(pos, edges, lat_stiff=20.0, link_damp=0.6, seg_damp=4.0,
                        seg_mass=0.05, cmax=3.0, name=name)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(len(pos))]
    return m, d, bid


def pulse(m, d, bid, k):
    """Pulse-force zone k; return per-zone integrated response and the full speed trace."""
    nseg = len(bid)
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    dirn = np.array([0.0, 0.0, 1.0])                  # push out of plane (into the disk stack)
    resp = np.zeros(nseg); over = np.zeros((PULSE_STEPS + WIN_STEPS, nseg))
    for i in range(PULSE_STEPS + WIN_STEPS):
        d.xfrc_applied[:] = 0
        if i < PULSE_STEPS:
            d.xfrc_applied[bid[k], 0:3] = FORCE * dirn
        mujoco.mj_step(m, d)
        s = np.linalg.norm(d.qvel.reshape(-1, 3), axis=1)
        resp += s * DT; over[i] = s
    return resp, over


def graph_dist(edges, n, src):
    adj = collections.defaultdict(set)
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    dist = {src: 0}; Q = collections.deque([src])
    while Q:
        v = Q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1; Q.append(w)
    return np.array([dist.get(i, -1) for i in range(n)])


def agg(vals, face, ring, reducer=np.mean):
    """Aggregate a per-node quantity by (face, ring), averaging over spokes (symmetry)."""
    out = {}
    for fc in ("outer", "inner"):
        for r in range(N_RING):
            sel = (face == fc) & (ring == r)
            v = vals[sel]
            v = v[~np.isnan(v)] if reducer is np.nanmean else v
            out[(fc, r)] = reducer(v) if len(v) else np.nan
    return out


def run(rim_fold, touch_ring=1):
    pos, edges, face, ring, layout, io, ii = disk_spec(rim_fold)
    m, d, bid = build(pos, edges, "disk_perturb")
    # average the RADIAL profile over all spokes at touch_ring (disk symmetry -> clean profile)
    resp_sum = np.zeros(len(pos)); rep_over = None; rep_k = io(touch_ring, 0)
    for c in range(N_SPOKE):
        k = io(touch_ring, c)
        resp, over = pulse(m, d, bid, k)
        resp_sum += resp
        if c == 0:
            rep_over = over
    resp_mean = resp_sum / N_SPOKE
    ttp = np.argmax(rep_over, axis=0) * DT                     # time-to-peak per zone (robust)
    gdist = graph_dist(edges, len(pos), rep_k)                 # graph distance from the touch
    return dict(pos=pos, edges=edges, face=face, ring=ring, layout=layout,
                rim_fold=rim_fold, resp=resp_mean, ttp=ttp, gdist=gdist,
                rep_k=rep_k, io=io, ii=ii, r_by=agg(resp_mean, face, ring),
                t_by=agg(ttp, face, ring))


def summarize(A, B):
    fa, r = A["face"], A["resp"]
    outer_tot = r[fa == "outer"].sum(); inner_tot = r[fa == "inner"].sum()
    trans = inner_tot / (outer_tot + 1e-12)
    inner_rim = A["r_by"][("inner", N_RING - 1)]; inner_ctr = A["r_by"][("inner", 0)]
    innerB = B["resp"][B["face"] == "inner"].sum()
    print("\nTwo-layer disk -- perturb the OUTER face: does it reach the inner face? (rim = only bridge)")
    print("=" * 84)
    print(f"pulse on an outer zone (ring {1}); response = time-integrated speed per zone\n")
    print(f"  A  rim fold INTACT :  outer-face response {outer_tot:8.4f} | inner-face {inner_tot:9.5f}"
          f"   -> transmission to inner = {100*trans:.2f}%")
    print(f"  B  rim fold CUT    :  outer-face response {B['resp'][B['face']=='outer'].sum():8.4f} | "
          f"inner-face {innerB:9.5f}   -> transmission to inner = "
          f"{100*innerB/(B['resp'][B['face']=='outer'].sum()+1e-12):.2f}%")
    print(f"\n  within the inner face (condition A): rim ring {inner_rim:.5f}  vs  centre {inner_ctr:.5f}"
          f"   -> rim/centre = {inner_rim/(inner_ctr+1e-12):.1f}x  (it arrives RIM-FIRST)")
    ttp_touch = A["t_by"][("outer", 1)]; ttp_inner_rim = A["t_by"][("inner", N_RING - 1)]
    print(f"  time-to-peak: outer touch-ring {1000*ttp_touch:.0f} ms  ->  inner rim "
          f"{1000*ttp_inner_rim:.0f} ms  ({1000*ttp_inner_rim - 1000*ttp_touch:.0f} ms later -- "
          f"the wavefront must reach the rim and cross the fold first)")
    print("=" * 84)
    gated = innerB < 0.02 * inner_tot and inner_rim > 1.5 * inner_ctr
    print(f"Verdict [{'PASS' if gated else 'CHECK'}]: it does NOT stop at the rim -- the rim is the")
    print("DOORWAY. With the fold intact a weak, rim-first echo reaches the inner face "
          f"({100*trans:.1f}% of the")
    print("outer response); cut the fold and the inner face feels NOTHING. So the outer skin can be")
    print("poked hard while the inner gut stays mechanically shielded -- it only feels what leaks")
    print("through the one rim gate. Letting the gut KNOW without being yanked is the IN messaging")
    print("net's job (non-decremental, across the mesoglea) -- the next experiment.\n")
    return trans


def draw_faces(ax, R, title, vmax):
    lay = R["layout"]; resp = R["resp"]
    for a, b in R["edges"]:
        ax.plot([lay[a][0], lay[b][0]], [lay[a][1], lay[b][1]], color="#dfe5ec", lw=0.5, zorder=1)
    xs = [lay[i][0] for i in range(len(resp))]; ys = [lay[i][1] for i in range(len(resp))]
    v = np.clip(resp, vmax * 1e-4, None)
    sc = ax.scatter(xs, ys, c=v, cmap="inferno", norm=LogNorm(vmin=vmax * 1e-3, vmax=vmax),
                    s=40, edgecolor="k", linewidth=0.3, zorder=3)
    kx, ky = lay[R["rep_k"]]
    ax.scatter([kx], [ky], s=180, facecolor="none", edgecolor="#00c2ff", lw=2.2, zorder=6)
    ax.annotate("perturb", (kx, ky), color="#0080a0", fontsize=8,
                xytext=(kx, ky + 0.12), ha="center")
    ax.text(0.02, 0.98, "outer face", transform=ax.transAxes, fontsize=8, va="top", color="#556")
    ax.text(0.60, 0.98, "inner face", transform=ax.transAxes, fontsize=8, va="top", color="#556")
    ax.set_title(title, fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    plt.colorbar(sc, ax=ax, fraction=0.035, pad=0.02, label="response (log)")


def main():
    A = run(True); B = run(False)
    trans = summarize(A, B)
    vmax = max(A["resp"].max(), B["resp"].max())

    fig, ax = plt.subplots(2, 2, figsize=(17, 11), gridspec_kw=dict(width_ratios=[2.1, 1]))
    draw_faces(ax[0, 0], A, "A · rim fold INTACT — the echo crosses at the rim", vmax)
    draw_faces(ax[1, 0], B, "B · rim fold CUT — the inner face is sealed off", vmax)

    # radial response profile: outer & inner faces, A vs B
    axp = ax[0, 1]
    rings = np.arange(N_RING)
    for R, ls, tag in ((A, "-", "intact"), (B, "--", "cut")):
        axp.plot(rings, [R["r_by"][("outer", r)] for r in rings], ls, color="#c0392b",
                 marker="o", label=f"outer ({tag})")
        axp.plot(rings, [R["r_by"][("inner", r)] for r in rings], ls, color="#2c7fb8",
                 marker="s", label=f"inner ({tag})")
    axp.axvline(N_RING - 1, ls=":", color="0.5", lw=1); axp.text(N_RING - 1, axp.get_ylim()[1],
                                                                 "rim", ha="center", fontsize=8, color="#555", va="bottom")
    axp.set_yscale("log"); axp.set_xlabel("ring (centre → rim)"); axp.set_ylabel("response (log)")
    axp.set_title("response by ring — decays to the rim, weak echo on the inner face", fontsize=10)
    axp.set_xticks(rings); axp.legend(fontsize=7.5); axp.grid(alpha=0.3, which="both")

    # the WAVEFRONT (condition A): time-to-peak vs graph distance from the touch, by face
    axl = ax[1, 1]
    gd, ttp, fa = A["gdist"], A["ttp"], A["face"]
    floor = 5e-5                                          # only zones that genuinely moved
    moved = A["resp"] > floor
    for fc, col in (("outer", "#c0392b"), ("inner", "#2c7fb8")):
        sel = (fa == fc) & moved
        axl.scatter(gd[sel] + np.random.default_rng(0).normal(0, 0.05, sel.sum()),
                    1000 * ttp[sel], s=30, color=col, alpha=0.85, edgecolor="k",
                    linewidth=0.2, label=f"{fc} face")
    axl.text(0.02, 0.97, "(zones above the noise floor only)", transform=axl.transAxes,
             fontsize=7.5, va="top", color="#667")
    axl.set_xlabel("graph distance from the perturbed zone (hops)")
    axl.set_ylabel("time-to-peak (ms)")
    axl.set_title("the wavefront — inner-face zones are farthest (via the rim), so peak last",
                  fontsize=10)
    axl.legend(fontsize=8); axl.grid(alpha=0.3)

    fig.suptitle("Outer-face perturbation on the two-layer disk: the rim fold is the only door "
                 "to the inner face", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "disk_perturbation_propagation.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
