# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Where the perturbation lands, and whether a rim exists: three propagation cases.

Comparison (G. Nagarjuna):
  1) tentacled disk, perturb a TENTACLE TIP  (the likely prey-contact point);
  2) tentacled disk, perturb the OUTER FACE  (not a tentacle);
  3) a closed two-shell SPHERE with NO rim, perturb the OUTER shell.

Cases 1-2 share the two-layer disk whose only mechanical bridge between the faces is the
RIM FOLD (the mesoglea carries only non-mechanical messaging). Tentacles are chains rooted
on the OUTER rim. Case 3 removes the rim entirely: the two shells close into a sphere and
are coupled mechanically THROUGH THE WALL everywhere (radial mesoglea links all over) --
so there is no single door.

Question in each: how does an outer perturbation travel in the net, and does it reach the
inner layer? Key comparator: response vs GRAPH DISTANCE from the touch, split by layer --
in the disk the inner face is many hops away (only via the rim); in the sphere it is ONE
hop away everywhere (through the wall).

Run:  ../.venv/bin/python disk_tentacle_sphere_propagation.py
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
PULSE_STEPS, WIN_STEPS = 20, 600
FORCE = 12.0
# disk params
N_SPOKE, N_RING, RSTEP, ZGAP = 8, 4, 0.09, 0.06
N_TENT, L_TENT = 6, 3
# sphere params
S_LON, S_LAT, R_OUT, R_IN = 8, 5, 0.34, 0.24


# =============================================================== morphologies ===
def disk_tentacle_spec():
    """Two-face disk + rim fold + tentacle chains on the outer rim."""
    pos, kind, layout = [], [], {}
    NPF = N_RING * N_SPOKE
    def io(r, c): return r * N_SPOKE + c
    def ii(r, c): return NPF + r * N_SPOKE + c
    XOFF = (N_RING + L_TENT + 2) * RSTEP * 2.3
    for fc, zf, xoff in (("outer", +ZGAP, 0.0), ("inner", -ZGAP, XOFF)):
        for r in range(N_RING):
            rad = (r + 1) * RSTEP
            for c in range(N_SPOKE):
                th = 2 * np.pi * c / N_SPOKE
                pos.append((rad * np.cos(th), rad * np.sin(th), zf)); kind.append(fc)
                layout[len(pos) - 1] = (xoff + rad * np.cos(th), rad * np.sin(th))
    edges = []
    for fn in (io, ii):
        for r in range(N_RING):
            for c in range(N_SPOKE):
                edges.append((fn(r, c), fn(r, (c + 1) % N_SPOKE)))
                if r < N_RING - 1:
                    edges.append((fn(r, c), fn(r + 1, c)))
    for c in range(N_SPOKE):
        edges.append((io(N_RING - 1, c), ii(N_RING - 1, c)))          # the rim fold
    tips = []
    spokes = [int(round(k * N_SPOKE / N_TENT)) % N_SPOKE for k in range(N_TENT)]
    for c in spokes:
        prev = io(N_RING - 1, c); th = 2 * np.pi * c / N_SPOKE
        for t in range(L_TENT):
            rad = (N_RING + 1 + t) * RSTEP
            pos.append((rad * np.cos(th), rad * np.sin(th), +ZGAP)); kind.append("tentacle")
            layout[len(pos) - 1] = (rad * np.cos(th), rad * np.sin(th))
            i = len(pos) - 1; edges.append((prev, i)); prev = i
        tips.append(len(pos) - 1)
    return dict(pos=np.array(pos), edges=edges, kind=np.array(kind), layout=layout,
                tips=tips, outer_mid=io(1, 0))


def sphere_spec():
    """Two concentric shells (outer/inner), coupled THROUGH THE WALL everywhere. No rim."""
    pos, kind, layout = [], [], {}
    per = S_LAT * S_LON + 2                                            # ring nodes + 2 poles
    def idx(shell, lat, c): return shell * per + lat * S_LON + c
    def npole(shell): return shell * per + S_LAT * S_LON
    def spole(shell): return shell * per + S_LAT * S_LON + 1
    DX = 0.16
    for shell, (name, R, xoff) in enumerate((("outer", R_OUT, 0.0), ("inner", R_IN, (S_LON + 3) * DX))):
        for lat in range(S_LAT):
            theta = np.pi * (lat + 1) / (S_LAT + 1)
            for c in range(S_LON):
                phi = 2 * np.pi * c / S_LON
                pos.append((R * np.sin(theta) * np.cos(phi), R * np.sin(theta) * np.sin(phi),
                            R * np.cos(theta)))
                kind.append(name); layout[len(pos) - 1] = (xoff + c * DX, -(lat + 1) * DX)
        pos.append((0, 0, R)); kind.append(name); layout[len(pos) - 1] = (xoff + (S_LON - 1) * DX / 2, 0.0)
        pos.append((0, 0, -R)); kind.append(name); layout[len(pos) - 1] = (xoff + (S_LON - 1) * DX / 2, -(S_LAT + 1) * DX)
    edges = []
    for shell in range(2):
        for lat in range(S_LAT):
            for c in range(S_LON):
                edges.append((idx(shell, lat, c), idx(shell, lat, (c + 1) % S_LON)))     # longitude ring
                if lat < S_LAT - 1:
                    edges.append((idx(shell, lat, c), idx(shell, lat + 1, c)))            # latitude
        for c in range(S_LON):
            edges.append((npole(shell), idx(shell, 0, c)))
            edges.append((spole(shell), idx(shell, S_LAT - 1, c)))
    # through-wall radial links -- EVERY node (the mesoglea couples the shells all over)
    for lat in range(S_LAT):
        for c in range(S_LON):
            edges.append((idx(0, lat, c), idx(1, lat, c)))
    edges.append((npole(0), npole(1))); edges.append((spole(0), spole(1)))
    edges = [(a, b) for (a, b) in edges if a != b]
    touch = idx(0, S_LAT // 2, 0)                                       # an outer equatorial node
    beneath = idx(1, S_LAT // 2, 0)                                     # the inner node right under it
    return dict(pos=np.array(pos), edges=edges, kind=np.array(kind), layout=layout,
                touch=touch, beneath=beneath)


# ==================================================================== physics ===
def build(pos, edges, name):
    xml = _lattice_mjcf(pos, edges, lat_stiff=20.0, link_damp=0.6, seg_damp=4.0,
                        seg_mass=0.05, cmax=3.0, name=name)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    bid = [m.body(f"b{i}").id for i in range(len(pos))]
    return m, d, bid


def pulse(m, d, bid, k, seed=0):
    nseg = len(bid)
    d.qpos[:] = 0; d.qvel[:] = 0; d.ctrl[:] = 0; d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    rng = np.random.default_rng(seed)
    dirn = rng.standard_normal(3); dirn /= np.linalg.norm(dirn) + 1e-9
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


# ==================================================================== one case ===
def run(spec, touch, name, inner_label="inner"):
    m, d, bid = build(spec["pos"], spec["edges"], name)
    resp, over = pulse(m, d, bid, touch)
    n = len(spec["pos"]); kind = spec["kind"]
    gd = graph_dist(spec["edges"], n, touch)
    ttp = np.argmax(over, axis=0) * DT
    outer_mask = np.isin(kind, ["outer", "tentacle"])
    inner_mask = kind == inner_label
    outer_tot = resp[outer_mask].sum(); inner_tot = resp[inner_mask].sum()
    trans = inner_tot / (outer_tot + 1e-12)
    # where does the inner layer first/most respond?
    inner_idx = np.where(inner_mask)[0]
    peak_inner = inner_idx[np.argmax(resp[inner_idx])]
    inner_gd = gd[inner_mask]; inner_gd = inner_gd[inner_gd > 0]
    return dict(name=name, spec=spec, resp=resp, gd=gd, ttp=ttp, touch=touch,
                trans=trans, peak_inner=peak_inner,
                inner_min_hops=int(inner_gd.min()) if len(inner_gd) else -1,
                outer_tot=outer_tot, inner_tot=inner_tot, kind=kind)


KCOL = {"outer": "#c0392b", "inner": "#2c7fb8", "tentacle": "#27ae60"}


def draw_map(ax, R, title, vmax):
    lay = R["spec"]["layout"]; resp = R["resp"]; edges = R["spec"]["edges"]
    for a, b in edges:
        ax.plot([lay[a][0], lay[b][0]], [lay[a][1], lay[b][1]], color="#e2e8ef", lw=0.4, zorder=1)
    xs = [lay[i][0] for i in range(len(resp))]; ys = [lay[i][1] for i in range(len(resp))]
    v = np.clip(resp, vmax * 1e-4, None)
    sc = ax.scatter(xs, ys, c=v, cmap="inferno", norm=LogNorm(vmin=vmax * 1e-3, vmax=vmax),
                    s=32, edgecolor="k", linewidth=0.25, zorder=3)
    tx, ty = lay[R["touch"]]
    ax.scatter([tx], [ty], s=170, facecolor="none", edgecolor="#00c2ff", lw=2.2, zorder=6)
    ax.annotate("perturb", (tx, ty), color="#0080a0", fontsize=8, xytext=(tx, ty + 0.1), ha="center")
    px, py = lay[R["peak_inner"]]
    ax.scatter([px], [py], s=120, facecolor="none", edgecolor="#2c7fb8", lw=1.8, zorder=6)
    ax.set_title(title, fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    plt.colorbar(sc, ax=ax, fraction=0.035, pad=0.02, label="response (log)")


def draw_decay(ax, R):
    gd, resp, kind = R["gd"], R["resp"], R["kind"]
    for kk in ["outer", "tentacle", "inner"]:
        sel = (kind == kk) & (gd >= 0)
        if not sel.any():
            continue
        ax.scatter(gd[sel] + np.random.default_rng(1).normal(0, 0.06, sel.sum()),
                   np.clip(resp[sel], 1e-7, None), s=22, color=KCOL[kk], alpha=0.8,
                   edgecolor="k", linewidth=0.2, label=kk)
    ax.set_yscale("log"); ax.set_xlabel("graph distance from perturbation (hops)")
    ax.set_ylabel("response (log)"); ax.legend(fontsize=7.5); ax.grid(alpha=0.3, which="both")
    ax.set_title(f"decay & where the inner layer sits (nearest inner = {R['inner_min_hops']} hops)",
                 fontsize=9.5)


def main():
    dt = disk_tentacle_spec()
    R1 = run(dt, dt["tips"][0], "tentacle_tip")
    R2 = run(dt, dt["outer_mid"], "outer_face")
    sp = sphere_spec()
    R3 = run(sp, sp["touch"], "sphere_outer")

    print("\nThree propagation cases -- where the touch lands, and whether a rim exists")
    print("=" * 82)
    for R, desc in ((R1, "1) tentacled disk, perturb a TENTACLE TIP"),
                    (R2, "2) tentacled disk, perturb the OUTER FACE"),
                    (R3, "3) closed SPHERE (no rim), perturb the OUTER shell")):
        print(f"  {desc}")
        print(f"       transmission to inner layer = {100*R['trans']:6.2f}%   "
              f"nearest inner node = {R['inner_min_hops']} hops from the touch   "
              f"(outer {R['outer_tot']:.3f} | inner {R['inner_tot']:.4f})")
    print("=" * 82)
    print("Reading: on the disk the inner face is many hops away and reachable only via the rim,")
    print("so transmission is small and rim-gated -- whether the touch is on a tentacle (1) or the")
    print("body (2). The tentacle tip is the FARTHEST (down the cable, to the rim, across the fold),")
    print("so it transmits least but delivers to one rim sector -- the tentacle aims the signal at")
    print("the door. On the sphere (3) there is no rim: every inner node is ONE hop under its outer")
    print("partner (through the wall), so the touch crosses LOCALLY and immediately, everywhere --")
    print("no bottleneck, no rim-first, no special place. The rim is what MAKES a special place.\n")

    vmax = max(R1["resp"].max(), R2["resp"].max(), R3["resp"].max())
    fig, ax = plt.subplots(3, 2, figsize=(17, 15), gridspec_kw=dict(width_ratios=[2.1, 1]))
    draw_map(ax[0, 0], R1, "1 · tentacle-tip touch — travels down the cable to the rim", vmax)
    draw_decay(ax[0, 1], R1)
    draw_map(ax[1, 0], R2, "2 · outer-face touch — spreads to the rim, crosses there", vmax)
    draw_decay(ax[1, 1], R2)
    draw_map(ax[2, 0], R3, "3 · closed sphere (no rim) — crosses through the wall, locally", vmax)
    draw_decay(ax[2, 1], R3)
    fig.suptitle("Where it lands and whether a rim exists: tentacle-tip vs outer-face vs no-rim sphere",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures",
                       "disk_tentacle_sphere_propagation.png")
    os.makedirs(os.path.dirname(out), exist_ok=True); fig.savefig(out, dpi=130)
    print(f"figure -> {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
