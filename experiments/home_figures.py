# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The two figures on the documentation home page — generated, never hand-drawn.

1. ``figures/home_self_to_world.png`` — the bench's argument on one animal, the medusa:
   a body built from ``s`` and ``f``; the self-model it recovers from its own movement;
   and the world-model it builds only when it moves (decoded vs true location of a hidden
   source, sessile beside swimming, and the razor curve).

2. ``figures/home_bodies.png`` — one modular unit, many bodies: the ``s``/``f`` unit, then
   five bodies composed from it (two-layer disk, Hydra sac, medusa, earthworm, nematode),
   each drawn with the self-model it recovers coloured onto it, and its recovery score.

Nothing here is a new result. Every body is each experiment's own ``spec``; every number
is recomputed by that experiment's own procedure and scored by
:func:`smn_lab.metrics.endpoint_recovery` (1 per ``f`` with both endpoints right, 0.5
with one) or, for the world-model, by the medusa experiment's own trial set and decoder
(asserted to reproduce its published skill). All are 🟡 provisional on the ledger.

Run:  ../.venv/bin/python home_figures.py      (about five minutes)
"""
from __future__ import annotations
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE)); sys.path.insert(0, _HERE)
from smn_lab.metrics import endpoint_recovery, decoding_skill
from smn_lab.medusa import medusa_spec
import medusa_world_model as mw
import medusa_self_world as ms
import worm_self_model as wsm
import nematode as NE, earthworm as EW
import diploblast_disk_self_model as DK
from hydra_sac import build as hydra_build, N_COL, N_ROW, NOUT
from two_networks_dissociation import babble as hydra_babble, coupling3

FIGDIR = os.path.join(_HERE, "..", "figures")
GREEN, AMBER, RED, FAINT = "#1e8449", "#e0a800", "#c0392b", "#dfe5ea"
INK, MUTED = "#22303c", "#5b6b78"


# ------------------------------------------------------------- recovery overlay --
def draw_recovery(ax, lay, all_edges, act_edges, C, *, node_c="#9aa9b6", lw_ok=1.6, wrap=False):
    """Draw a body on ``lay`` with each actuated f coloured by what the read-out named:
    green both endpoints, amber one, red neither (the red/amber line joins the two nodes
    named). Passive links faint. ``wrap``: a correctly recovered ring closure on an
    unrolled layout (same x, far apart in y) is drawn as two short stubs."""
    act = {tuple(sorted(e)) for e in act_edges}
    for a, b in all_edges:
        if tuple(sorted((a, b))) in act:
            continue
        (x0, y0), (x1, y1) = lay[a], lay[b]
        if wrap and x0 == x1 and abs(y1 - y0) > 1.5:
            continue
        ax.plot([x0, x1], [y0, y1], color=FAINT, lw=0.5, zorder=1)
    xy = np.array([lay[i] for i in sorted(lay)])
    ax.scatter(*xy.T, s=5, color=node_c, zorder=2, linewidths=0)
    hits = []
    for L, (a, b) in enumerate(act_edges):
        top = [int(v) for v in np.argsort(C[L])[::-1][:2]]
        hit = len({a, b} & set(top)); hits.append(hit)
        (x0, y0), (x1, y1) = lay[top[0]], lay[top[1]]
        col = {2: GREEN, 1: AMBER, 0: RED}[hit]
        if hit == 2 and wrap and x0 == x1 and abs(y1 - y0) > 1.5:
            for yy, dy in ((max(y0, y1), 0.4), (min(y0, y1), -0.4)):
                ax.plot([x0, x0 + 0.15], [yy, yy + dy], color=col, lw=lw_ok, ls=":", zorder=3)
            continue
        ax.plot([x0, x1], [y0, y1], color=col, lw=lw_ok if hit == 2 else 1.1,
                alpha=0.95 if hit == 2 else 0.85, zorder=3 + (2 - hit), solid_capstyle="round")
    ax.set_aspect("equal"); ax.axis("off")
    return np.array(hits)


# -------------------------------------------------------------------- bodies -----
def body_disk():
    pos, edges, cls, layout, ring, ix, tent = DK.disk_spec(True)
    m, d, bid = DK.build(pos, edges, "disk_tent")
    C = DK.babble(m, d, bid, DK.SEED)
    return dict(name="Two-layer disk", sub="two faces, joined at the rim", lay=layout, edges=edges,
                act=edges, C=C, wrap=False)


def body_hydra():
    m, d, bid, pos, edges, roles, (io_, ii_, out_apex, in_apex) = hydra_build()
    DRV, VX, VY, VZ = hydra_babble(m, d, bid, m.nu, seed=0)
    C = coupling3(DRV, VX, VY, VZ)
    io = lambda r, c: r * N_COL + c
    ii = lambda r, c: NOUT + r * N_COL + c
    lay = {}
    for r in range(N_ROW):                                   # experiment_page_demo's layout
        for c in range(N_COL):
            lay[io(r, c)] = (-c, r); lay[ii(r, c)] = (-c + 0.34, r - 0.34)
    lay[out_apex] = (-(N_COL + 0.4), (N_ROW - 1) / 2)
    lay[in_apex] = (-(N_COL + 0.4) + 0.34, (N_ROW - 1) / 2 - 0.34)
    return dict(name="Hydra sac", sub="two layers, unrolled", lay=lay, edges=edges,
                act=edges, C=C, wrap=False)


def body_medusa():
    sp = medusa_spec(z_apex=mw.Z_APEX)
    C = ms.babble_coupling(sp)
    return dict(name="Medusa", sub="bell + tentacles, top view", lay=sp["layout"],
                edges=sp["edges"], act=sp["edges"], C=C, wrap=False, spec=sp)


def body_worm(mod, layout_fn, name, sub):
    S = mod.spec(); lay, _ = layout_fn(S)
    C, eoa = wsm.babble(mod, S)
    return dict(name=name, sub=sub, lay=lay, edges=S["edges"],
                act=[S["edges"][e] for e in eoa], C=C, wrap=True)


# ------------------------------------------------------------------ the unit -----
def draw_unit(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ya = 6.2
    for x in (1.6, 8.4):
        ax.add_patch(plt.Circle((x, ya), 0.62, color="#5f88aa", zorder=3))
        ax.text(x, ya, "s", color="white", ha="center", va="center", fontsize=12,
                fontweight="bold", zorder=4)
    zz = np.linspace(2.3, 4.6, 9)
    ax.plot(np.r_[2.22, zz, 4.75], np.r_[ya, ya + 0.38 * (-1) ** np.arange(9), ya],
            color=MUTED, lw=1.4)
    ax.add_patch(FancyBboxPatch((4.95, ya - 0.42), 2.5, 0.84, boxstyle="round,pad=0.05",
                                fc=RED, ec="none", zorder=3))
    ax.text(6.2, ya, "f", color="white", ha="center", va="center", fontsize=12,
            fontweight="bold", zorder=4)
    ax.plot([4.75, 4.95], [ya, ya], color=MUTED, lw=1.4); ax.plot([7.45, 7.78], [ya, ya], color=MUTED, lw=1.4)
    ax.annotate("", xy=(5.15, ya + 1.15), xytext=(7.25, ya + 1.15),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.2))
    ax.text(6.2, ya + 1.45, "pulls only", ha="center", fontsize=10, color=RED)
    ax.text(3.45, ya - 0.95, "series spring", ha="center", fontsize=9.5, color=MUTED)
    ax.text(5, 3.7, "s   a segment: one point mass\n"
                     "f   a contractile unit: pulls only,\n     through a series spring\n"
                     "every link in every body is one f", ha="center", va="top",
            fontsize=10.5, color=INK, linespacing=1.5)
    ax.set_title("The unit", fontsize=13, color=INK, loc="left", fontweight="bold", pad=20)


# ------------------------------------------------------------------- figure 2 -----
def fig_bodies(bodies, out):
    fig, axs = plt.subplots(2, 3, figsize=(12.5, 9.2),
                            gridspec_kw=dict(hspace=0.30, wspace=0.10))
    fig.subplots_adjust(top=0.84)
    draw_unit(axs[0, 0])
    scores = {}
    for ax, B in zip(axs.flat[1:], bodies):
        hits = draw_recovery(ax, B["lay"], B["edges"], B["act"], B["C"], wrap=B["wrap"])
        er = float(endpoint_recovery(B["C"], B["act"]))
        assert abs(er - np.mean(np.where(hits == 2, 1.0, np.where(hits == 1, 0.5, 0.0)))) < 1e-9
        scores[B["name"]] = er
        n_pass = len(B["edges"]) - len(B["act"])
        ax.set_title(f"{B['name']}   {er:.3f}", fontsize=13, color=INK,
                     loc="left", fontweight="bold", pad=20)
        ax.text(0.0, 1.015, f"{B['sub']} · {len(B['act'])} f"
                + (f" + {n_pass} passive" if n_pass else ""),
                transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")
    fig.legend(handles=[Line2D([], [], color=GREEN, lw=2, label="f: both endpoints recovered"),
                        Line2D([], [], color=AMBER, lw=1.4, label="one endpoint (half credit)"),
                        Line2D([], [], color=RED, lw=1.4, label="neither (line joins the nodes named)"),
                        Line2D([], [], color=FAINT, lw=1.4, label="passive link (not read)")],
               loc="lower center", ncol=2, fontsize=10.5, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("One modular unit, many bodies:\neach recovers a model of itself from its own movement",
                 fontsize=16, color=INK, y=1.0)
    fig.text(0.5, 0.905, "number = self-model score (each f: 1 if both endpoints recovered, 0.5 if one)",
             ha="center", fontsize=10.5, color=MUTED)
    fig.savefig(out, dpi=130, bbox_inches="tight"); plt.close(fig)
    print("figure ->", os.path.normpath(out))
    return scores


# ------------------------------------------------------------------- figure 1 -----
def fig_self_to_world(med, out):
    sp = med["spec"]; lay = sp["layout"]
    er = float(endpoint_recovery(med["C"], sp["edges"]))
    rows, draw = [], {}
    for a in mw.ALPHAS:
        traj = mw.tip_trajectory(a)
        S, P = ms.trials(traj)
        pred, Pte, Ptr = ms.knn_predict(S, P)
        s_xy, s_3d = ms.skills(pred, Pte, Ptr)
        pub = float(decoding_skill(S, P, np.random.default_rng(7), k=ms.K))
        assert abs(pub - s_xy) < 1e-9
        shuf = float(decoding_skill(S, P, np.random.default_rng(7), k=ms.K, shuffle=True))
        rows.append((a, s_xy, s_3d, shuf))
        if a in (mw.ALPHAS[0], mw.ALPHAS[-1]):
            draw[a] = (pred, Pte, s_3d)

    plt.rcParams.update({"font.size": 11})
    fig = plt.figure(figsize=(11.5, 10.6))
    g = fig.add_gridspec(2, 2, hspace=0.30, wspace=0.16)
    tips = sp["tips"]

    # 1 · body built from s and f
    ax = fig.add_subplot(g[0, 0])
    kc = {"coronal": RED, "radial": "#5f88aa", "tentacle": "#d35400", "brace": "#c9d3db"}
    for (u, v), k in zip(sp["edges"], sp["edge_kind"]):
        ax.plot(*np.array([lay[u], lay[v]]).T, color=kc[str(k)], lw=1.6 if k != "brace" else 0.8)
    xy = np.array([lay[i] for i in range(len(lay))]); ax.scatter(*xy.T, s=7, color="#33414f", zorder=3)
    ax.scatter(*np.array([lay[i] for i in tips]).T, s=46, color="#f0a500", edgecolor="#5a3a10",
               zorder=4)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("1 · A body, built from s and f", fontsize=13, loc="left", color=INK, fontweight="bold")
    ax.legend(handles=[Line2D([], [], color=RED, lw=2, label="coronal f — the swim muscle"),
                       Line2D([], [], color="#5f88aa", lw=2, label="radial f — the bell"),
                       Line2D([], [], color="#d35400", lw=2, label="tentacle f"),
                       Line2D([], [], ls="", marker="o", ms=7, color="#f0a500", mec="#5a3a10",
                              label="tip transducers")],
              loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=9.5, frameon=False)

    # 2 · self-model
    ax = fig.add_subplot(g[0, 1])
    draw_recovery(ax, lay, sp["edges"], sp["edges"], med["C"], lw_ok=2.0)
    ax.set_title("2 · Its self-model, from movement", fontsize=13, loc="left",
                 color=INK, fontweight="bold")
    ax.legend(handles=[Line2D([], [], color=GREEN, lw=2, label=f"f recovered (score {er:.3f})"),
                       Line2D([], [], color=AMBER, lw=1.4, label="one end right"),
                       Line2D([], [], color=RED, lw=1.4, label="misread")],
              loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=9.5, frameon=False)

    # 3 · world-model: decoded vs true, sessile and swimming
    sub = g[1, 0].subgridspec(1, 2, wspace=0.08)
    lim = mw.SRC_DMAX * 1.08
    for j, a in enumerate((mw.ALPHAS[0], mw.ALPHAS[-1])):
        ax = fig.add_subplot(sub[j])
        pred, Pte, s3 = draw[a]
        for (u, v) in sp["edges"]:
            ax.plot(*np.array([lay[u], lay[v]]).T, color="#dde4ea", lw=0.5)
        for p, t in zip(pred, Pte):
            ax.plot([t[0], p[0]], [t[1], p[1]], color=RED, lw=0.6, alpha=0.6)
        ax.scatter(*Pte[:, :2].T, s=9, color=GREEN, zorder=3)
        ax.scatter(*pred[:, :2].T, s=8, marker="x", color=RED, zorder=4, linewidths=0.9)
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color("#dde3e8")
        ax.text(0.5, -0.04, ("sessile, α = 0" if a == 0 else f"swimming, α = {a:g}") +
                f"\nskill {s3:.2f}", transform=ax.transAxes, fontsize=11, va="top", ha="center",
                color=RED if a == 0 else GREEN, fontweight="bold")
        if j == 0:
            ax.set_title("3 · Where is the source?", fontsize=13, loc="left",
                         color=INK, fontweight="bold", pad=24)
            ax.text(0.0, 1.03, "held-out sources: true ●   decoded ×", transform=ax.transAxes,
                    fontsize=9.5, color=MUTED, va="bottom")

    # 4 · the razor
    ax = fig.add_subplot(g[1, 1])
    A = [r[0] for r in rows]
    ax.plot(A, [r[2] for r in rows], "o-", color=GREEN, lw=2.4, label="world-model skill (3-D error)")
    ax.plot(A, [r[1] for r in rows], "o--", color="#2c6fbb", lw=1.4, ms=4,
            label="published skill (horizontal error only)")
    ax.plot(A, [r[3] for r in rows], "s:", color="#999999", lw=1.3, ms=4, label="shuffle control")
    ax.axhline(0, color="#cccccc", lw=0.8); ax.axvspan(-0.4, 0.4, color=RED, alpha=0.08)
    ax.text(0.5, 0.03, "sessile", color=RED, fontsize=10, transform=ax.get_xaxis_transform())
    ax.set_xlabel("self-motion α  (0 = sessile)", fontsize=11)
    ax.set_ylabel("skill (0 = chance)", fontsize=11)
    ax.set_title("4 · A world-model only when it moves", fontsize=13, loc="left",
                 color=INK, fontweight="bold")
    ax.legend(fontsize=9.5, frameon=False, loc="upper left"); ax.grid(alpha=0.25)
    ax.set_ylim(-0.2, 0.62)

    fig.suptitle("The medusa: a self-model from its own movement,\nand a world-model only when it moves",
                 fontsize=16, color=INK, y=0.995)
    fig.savefig(out, dpi=130, bbox_inches="tight"); plt.close(fig)
    print("figure ->", os.path.normpath(out))
    return er, rows


def main():
    med = body_medusa()
    er, rows = fig_self_to_world(med, os.path.join(FIGDIR, "home_self_to_world.png"))
    bodies = [body_disk(), body_hydra(), med,
              body_worm(EW, wsm.earthworm_layout, "Earthworm", "unrolled"),
              body_worm(NE, wsm.nematode_layout, "Nematode", "unrolled")]
    scores = fig_bodies(bodies, os.path.join(FIGDIR, "home_bodies.png"))
    print("\nself-model endpoint recovery (house metric):")
    for k, v in scores.items():
        print(f"  {k:16s} {v:.3f}")
    print("medusa world-model skill (alpha, x-y published, 3-D, shuffle):")
    for r in rows:
        print("  " + "  ".join(f"{x:6.2f}" for x in r))


if __name__ == "__main__":
    main()
