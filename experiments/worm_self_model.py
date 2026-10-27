# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""The worm ladder's bodies, drawn — and their self-models, measured for the first time.

``nematode.py`` and ``earthworm.py`` are motor demonstrations: they drive a gait and plot
it, but never show the morphology they drive, and never read a self-model or a world-model.
This script does two things for each worm, without changing either body.

* **Body plan.** The full morphology from each script's own ``spec()``: every tissue and
  every link kind, as a cross-section (true geometry at one station) beside an unrolled
  side view (the tube cut along one line and laid flat, so every node is visible). Muscle
  ``f``s are drawn heavy; passive links light. Nothing is idealized away in the drawing —
  in particular the nematode's gut is drawn where it is in the model: a separate tube
  joined to nothing (the body graph has two connected components).

* **Self-model.** The disk's procedure, unchanged (``diploblast_disk_self_model.py``):
  Ornstein-Uhlenbeck babble on every actuated ``f``, no medium, then the ``endpoint``
  read-out (each ``f``'s two strongest co-moving segments are taken as its endpoints),
  scored by the house metric :func:`smn_lab.metrics.endpoint_recovery` (1 per ``f`` with
  both endpoints right, 0.5 with one), the same number the medusa, Hydra and disk report.
  The exact-match fraction (both endpoints right) is reported beside it.
  The read-out has one row per *actuated* ``f``, so it can recover the muscle network
  only; passive links (skin, cuticle, hydrostat struts, gut) are outside its reach by
  construction. The result is drawn on the body's own unrolled layout, green where the
  read-out named both of an ``f``'s endpoints, amber where it named one, red where neither. The
  house self/world card (``report.render``) is not used for the picture: its abstract
  force layout is illegible for a 195-node body. ``render`` still writes the
  machine-readable record.

**There is no world-model here**, because neither worm experiment has a world in it yet:
no source, and the nematode's transducer labels are never read. Drawing a world panel
would invent a result. The pages say so.

Run:  ../.venv/bin/python worm_self_model.py
"""
from __future__ import annotations
import os, sys
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mujoco

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE)); sys.path.insert(0, _HERE)
from smn_lab.self_model import coupling
from smn_lab.metrics import endpoint_recovery
from smn_lab.report import RunRecord, render
import nematode as NE
import earthworm as EW

FIGDIR = os.path.join(_HERE, "..", "figures")
B_DT, T_WARM, T_REC, U_TC, U_SIG, SEED = 0.002, 2.0, 22.0, 0.15, 5.0, 0   # the disk's babble


# ------------------------------------------------------------------ self-model ----
def babble(mod, S):
    """Disk babble on the actuated f's. Returns C (n_act x n_nodes) and act->edge map."""
    m, d, aoe = mod.build(S)
    rng = np.random.default_rng(SEED); nl, ns = m.nu, len(S["pos"])
    nw, nr = int(T_WARM / B_DT), int(T_REC / B_DT)
    u = np.zeros(nl); DRV = np.zeros((nr, nl)); V = np.zeros((3, nr, ns))
    d.qpos[:] = 0; d.qvel[:] = 0; mujoco.mj_forward(m, d)
    for i in range(nw + nr):
        u += (-u / U_TC) * B_DT + U_SIG * np.sqrt(B_DT) * rng.standard_normal(nl)
        ud = np.clip(u, 0.0, None)                     # pull-only f
        d.ctrl[:] = ud; mujoco.mj_step(m, d)
        if i >= nw:
            j = i - nw; DRV[j] = ud; V[:, j] = d.qvel.reshape(-1, 3).T
    V -= V.mean(2, keepdims=True)
    C = sum(np.abs(coupling(DRV, V[k])) for k in range(3))
    edge_of_act = [e for e, _ in sorted(aoe.items(), key=lambda kv: kv[1])]
    return C, edge_of_act


def score(S, C, edge_of_act):
    """Per kind: exact matches (both endpoints right) and half matches (one right). The
    house metric, ``metrics.endpoint_recovery``, scores these 1 and 0.5."""
    ok, half, tot, picks = Counter(), Counter(), Counter(), Counter()
    tis = S["tissue"]
    for a, e in enumerate(edge_of_act):
        truth = set(S["edges"][e])
        top = set(int(s) for s in np.argsort(C[a])[::-1][:2])
        k = str(S["etype"][e]); tot[k] += 1
        hit = len(truth & top)
        ok[k] += hit == 2; half[k] += hit == 1
        if hit < 2:
            picks[" + ".join(sorted(str(tis[t]) for t in top)) + f" ({hit} right)"] += 1
    return ok, half, tot, picks


def components(S):
    n = len(S["pos"]); p = list(range(n))
    def f(x):
        while p[x] != x:
            p[x] = p[p[x]]; x = p[x]
        return x
    for a, b in S["edges"]:
        p[f(a)] = f(b)
    comp = {}
    for i in range(n):
        comp.setdefault(f(i), []).append(i)
    return [sorted(set(map(str, S["tissue"][c]))) + [len(c)] for c in comp.values()]


# ------------------------------------------------------------------- layouts ------
def nematode_layout(S):
    """Unrolled side view: x = station along the body; each tissue its own band, nodes
    ordered round the circumference. Returns node -> (x, y), band labels, wrap edges."""
    lay, bands = {}, []
    y0 = 0.0
    for name, keymap, ncirc in (("skin", S["SK"], NE.NC), ("muscle", S["MU"], 4),
                                ("gut", S["GU"], NE.NCG)):
        if name == "muscle":
            for j, q in enumerate(NE.MQUAD):
                for k in range(NE.NX):
                    lay[keymap[(q, k)]] = (k, -(y0 + j))
            bands.append((name, y0, y0 + 3, list(NE.MQUAD)))
        else:
            for (k, c), i in keymap.items():
                lay[i] = (k, -(y0 + c))
            bands.append((name, y0, y0 + ncirc - 1, None))
        y0 += ncirc + 1.6
    skin_mid = -(NE.NC - 1) / 2
    lay[S["mouth"]] = (-1.4, skin_mid)
    lay[S["anus"][0]] = (NE.NX + 0.4, 0.0)
    lay[S["anus"][1]] = (NE.NX + 0.4, -NE.NC / 2)
    return lay, bands


def earthworm_layout(S):
    lay, bands = {}, []
    y0 = 0.0
    for name, keymap in (("circular", S["C"]), ("longitudinal", S["L"])):
        for (i, q), n in keymap.items():
            lay[n] = (i, -(y0 + EW.RING.index(q)))
        bands.append((name, y0, y0 + 3, EW.RING))
        y0 += 5.6
    for i, n in S["G"].items():
        lay[n] = (i, -y0)
    bands.append(("ganglia", y0, y0, None))
    return lay, bands


# -------------------------------------------------------------------- drawing -----
STYLE = {   # link kind -> (colour, width, label)
    # nematode
    "muscle": ("#c0392b", 2.4, "longitudinal muscle f (actuated)"),
    "mouth_radial": ("#d35400", 1.8, "pharyngeal radial f (actuated)"),
    "anus": ("#8e44ad", 1.8, "anal DV f (actuated)"),
    "skin_ring": ("#9db7cc", 0.9, "skin ring (passive)"),
    "cuticle": ("#5f88aa", 1.1, "cuticle, longitudinal (passive restoring)"),
    "gut": ("#b5a77a", 0.9, "gut (passive, no muscle)"),
    "attach": ("#7f8c8d", 0.6, "muscle-to-skin attachment (passive)"),
    # earthworm
    "circ_m": ("#c0392b", 2.4, "circular muscle f (actuated, segmental)"),
    "long_m": ("#2471a3", 2.4, "longitudinal muscle f (actuated, continuous)"),
    "circ_s": ("#e6b0aa", 0.9, "circular layer, axial (passive)"),
    "long_s": ("#a9cce3", 0.9, "longitudinal layer, ring (passive)"),
    "b_rad": ("#7f8c8d", 0.7, "hydrostat, radial strut (passive)"),
    "b_diag": ("#bfc9ca", 0.6, "hydrostat, diagonal strut (passive)"),
    "cord": ("#27ae60", 1.6, "ventral nerve cord (passive)"),
    "spoke": ("#a9dfbf", 0.5, "ganglion spoke (passive)"),
}
TISSUE_C = {"skin": "#5f88aa", "muscle": "#c0392b", "gut": "#b5a77a", "mouth_hub": "#d35400",
            "anus": "#8e44ad", "circ": "#c0392b", "long": "#2471a3", "gang": "#27ae60"}


def draw_unrolled(ax, S, lay, bands, wrap_kinds):
    """Edges between nodes of the same band row-ring that close the circle are drawn as
    short stubs off the band, so the unrolled tube does not sprout band-spanning lines."""
    drawn = set()
    order = sorted(set(map(str, S["etype"])), key=lambda k: STYLE[k][1])   # light first
    for kind in order:
        col, lw, _ = STYLE[kind]
        for (a, b), k in zip(S["edges"], S["etype"]):
            if k != kind:
                continue
            (x0, y0), (x1, y1) = lay[a], lay[b]
            if kind in wrap_kinds and abs(y1 - y0) > 1.5 and x0 == x1:
                top, bot = max(y0, y1), min(y0, y1)        # the ring's closing link
                ax.plot([x0, x0 + 0.18], [top, top + 0.45], color=col, lw=lw, ls=":")
                ax.plot([x0, x0 + 0.18], [bot, bot - 0.45], color=col, lw=lw, ls=":")
            else:
                ax.plot([x0, x1], [y0, y1], color=col, lw=lw, solid_capstyle="round")
            drawn.add(kind)
    xy = np.array([lay[i] for i in range(len(S["pos"]))])
    ax.scatter(*xy.T, s=11, c=[TISSUE_C[str(t)] for t in S["tissue"]], zorder=3,
               edgecolor="white", linewidth=0.4)
    sens = [(i, m) for i, m in enumerate(S.get("meta", [])) if isinstance(m, list)]
    if sens:
        tt = np.array([lay[i] for i, m in sens if "temp" in m])
        ph = np.array([lay[i] for i, m in sens if "photo" in m])
        ax.scatter(*tt.T, s=46, facecolor="none", edgecolor="#e67e22", lw=1.0, zorder=4)
        ax.scatter(*ph.T, s=22, marker="^", color="#f1c40f", edgecolor="#7d6608",
                   lw=0.5, zorder=5)
    for name, ya, yb, rows in bands:
        ax.text(-0.9 if name != "skin" else -2.3, -(ya + yb) / 2, name, ha="right",
                va="center", fontsize=8.5, color="#33414f", fontweight="bold")
        if rows:
            for j, q in enumerate(rows):
                ax.text(-0.35, -(ya + j), q, ha="right", va="center", fontsize=6.5,
                        color="#6b7b88")
    ax.set_aspect("equal"); ax.axis("off")
    h = [Line2D([], [], color=STYLE[k][0], lw=STYLE[k][1] + 0.4, label=STYLE[k][2])
         for k in sorted(drawn, key=lambda k: -STYLE[k][1])]
    if sens:
        h += [Line2D([], [], ls="", marker="o", ms=4, color="#5f88aa",
                     label="skin node: touch transducer (all)"),
              Line2D([], [], ls="", marker="o", ms=7, mfc="none", mec="#e67e22",
                     label="+ temperature transducer"),
              Line2D([], [], ls="", marker="^", ms=6, color="#f1c40f", mec="#7d6608",
                     label="+ photoreceptor (denser toward head)")]
    return h


def draw_section(ax, S, nodes, title):
    """True y-z geometry of one axial station (plus anything within it)."""
    P = S["pos"]; idx = set(nodes)
    for (a, b), k in zip(S["edges"], S["etype"]):
        if a in idx and b in idx:
            col, lw, _ = STYLE[str(k)]
            ax.plot(P[[a, b], 1], P[[a, b], 2], color=col, lw=lw)
    ax.scatter(P[nodes, 1], P[nodes, 2], s=36, c=[TISSUE_C[str(S["tissue"][i])] for i in nodes],
               zorder=3, edgecolor="white", linewidth=0.6)
    ax.axhline(0, color="#eeeeee", lw=0.6, zorder=0); ax.axvline(0, color="#eeeeee", lw=0.6, zorder=0)
    ax.text(0, P[nodes, 2].max() * 1.12, "dorsal", ha="center", va="bottom",
            fontsize=7, color="#6b7b88")
    ax.text(0, P[nodes, 2].min() * 1.12, "ventral", ha="center", va="top", fontsize=7,
            color="#6b7b88")
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=9.5, pad=14)


def body_plan_figure(name, S, lay, bands, section_nodes, section_title, wrap_kinds,
                     headline, note, out):
    fig = plt.figure(figsize=(14.5, 6.0))
    g = fig.add_gridspec(2, 2, width_ratios=[1, 2.6], height_ratios=[4, 1.1],
                         wspace=0.02, hspace=0.02)
    axs = fig.add_subplot(g[0, 0]); draw_section(axs, S, section_nodes, section_title)
    axu = fig.add_subplot(g[0, 1])
    handles = draw_unrolled(axu, S, lay, bands, wrap_kinds)
    axu.set_title("Unrolled side view — the tube cut along one line and laid flat "
                  "(head left; dotted stubs = a ring closing round the body)", fontsize=9.5)
    axl = fig.add_subplot(g[1, :]); axl.axis("off")
    axl.legend(handles=handles, ncol=3, fontsize=8, frameon=False, loc="upper center")
    fig.suptitle(headline, fontsize=12.5, y=0.99)
    axl.text(0.5, -0.05, note, ha="center", va="top", fontsize=8.5, color="#33414f",
             transform=axl.transAxes)
    fig.savefig(out, dpi=130, bbox_inches="tight"); plt.close(fig)
    print("figure ->", os.path.normpath(out))


def self_model_figure(name, S, lay, bands, C, eoa, er, ex, ok, tot, out):
    """Each actuated f's recovered endpoints, drawn on the body's own unrolled layout:
    green = the read-out named the f's true endpoints; red = it named two other nodes
    (the red line joins the nodes it DID name). Passive structure faint, for orientation."""
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    for (a, b), k in zip(S["edges"], S["etype"]):
        (x0, y0), (x1, y1) = lay[a], lay[b]
        if abs(y1 - y0) > 1.5 and x0 == x1 and str(k) in ("skin_ring", "gut", "circ_m", "long_s"):
            continue
        ax.plot([x0, x1], [y0, y1], color="#e3e8ec", lw=0.6, zorder=1)
    xy = np.array([lay[i] for i in range(len(S["pos"]))])
    ax.scatter(*xy.T, s=9, c=[TISSUE_C[str(t)] for t in S["tissue"]], alpha=0.55, zorder=2)
    n_bad = 0
    for a, e in enumerate(eoa):
        truth = tuple(sorted(S["edges"][e]))
        top = tuple(sorted(int(v) for v in np.argsort(C[a])[::-1][:2]))
        hit = len(set(top) & set(truth)); good = hit == 2
        col = {2: "#1e8449", 1: "#e0a800", 0: "#c0392b"}[hit]
        (x0, y0), (x1, y1) = lay[top[0]], lay[top[1]]
        if good and abs(y1 - y0) > 1.5 and x0 == x1:          # a correctly recovered ring closure
            ax.plot([x0, x0 + 0.18], [max(y0, y1), max(y0, y1) + 0.45], color="#1e8449", lw=2.2, ls=":")
            ax.plot([x0, x0 + 0.18], [min(y0, y1), min(y0, y1) - 0.45], color="#1e8449", lw=2.2, ls=":")
            continue
        ax.plot([x0, x1], [y0, y1], color=col,
                lw=2.4 if good else 1.6, alpha=0.95 if good else 0.85, zorder=3 + (2 - hit))
        n_bad += not good
    for nm, ya, yb, rows in bands:
        ax.text(-0.9 if nm != "skin" else -2.3, -(ya + yb) / 2, nm, ha="right", va="center",
                fontsize=8.5, color="#33414f", fontweight="bold")
    ax.set_aspect("equal"); ax.axis("off")
    per = " · ".join(f"{k} {ok[k]}/{tot[k]}" for k in tot)
    ax.set_title(f"{name.capitalize()} — self-model recovered from movement, on the body's "
                 f"unrolled layout\nendpoint recovery {er:.2f}   (exact, both endpoints: {per})", fontsize=11)
    ax.legend(handles=[Line2D([], [], color="#1e8449", lw=2.4, label="both endpoints right"),
                       Line2D([], [], color="#e0a800", lw=1.6, label="one endpoint right (half credit)"),
                       Line2D([], [], color="#c0392b", lw=1.6,
                              label="neither right — line joins the two nodes the read-out named"),
                       Line2D([], [], color="#d5dbe0", lw=1.0,
                              label="passive structure (not addressable by this read-out)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, fontsize=8, frameon=False)
    fig.savefig(out, dpi=130, bbox_inches="tight"); plt.close(fig)
    print("figure ->", os.path.normpath(out))


# ----------------------------------------------------------------------- main -----
def run_worm(name, mod, S, lay, bands, section_nodes, section_title, wrap_kinds, headline):
    comps = components(S)
    n_act = int(S["is_musc"].sum()); n_e = len(S["edges"])
    C, eoa = babble(mod, S)
    ok, half, tot, picks = score(S, C, eoa)
    act_edges = [S["edges"][e] for e in eoa]
    er = float(endpoint_recovery(C, act_edges))          # the house metric (partial credit)
    ex = sum(ok.values()) / n_act                         # exact: both endpoints right
    assert abs(er - (sum(ok.values()) + 0.5 * sum(half.values())) / n_act) < 1e-9
    print(f"\n[{name}] {len(S['pos'])} nodes, {n_e} links ({n_act} actuated f, "
          f"{n_e - n_act} passive); connected components: {len(comps)}")
    for c in comps:
        print(f"    component of {c[-1]} nodes: {', '.join(c[:-1])}")
    print(f"  self-model endpoint recovery over actuated f: {er:.3f} (house metric, partial "
          f"credit); exact {sum(ok.values())}/{n_act} = {ex:.3f}")
    for k in tot:
        print(f"    {k:13s} exact {ok[k]}/{tot[k]}, half {half[k]}, neither {tot[k]-ok[k]-half[k]}")
    if picks:
        print("  misses name instead:", "; ".join(f"{v}× {k}" for k, v in picks.most_common()))

    note = (f"{len(S['pos'])} nodes · {n_e} links, of which {n_act} are actuated muscle f's · "
            f"{len(comps)} connected component{'s' if len(comps) > 1 else ''}")
    if len(comps) > 1:
        lone = [c for c in comps if c[-1] < max(cc[-1] for cc in comps)]
        note += ("  —  the " + ", ".join(c[0] for c in lone) +
                 " is joined to nothing else in the model")
    body_plan_figure(name, S, lay, bands, section_nodes, section_title, wrap_kinds,
                     headline, note, os.path.join(FIGDIR, f"{name}_body_plan.png"))

    self_model_figure(name, S, lay, bands, C, eoa, er, ex, ok, tot,
                      os.path.join(FIGDIR, f"{name}_self_model.png"))
    # the machine-readable record, through the one results module (no card: the house
    # card's abstract force layout is illegible for a 195-node body; see the docstring)
    render(RunRecord(name=name, coupling_matrix=C, recovery="endpoint",
                     positions=lay, true_edges=act_edges,
                     metrics={"endpoint_recovery": er, "endpoint_exact": ex},
                     meta={"per_kind_exact": {k: f"{ok[k]}/{tot[k]}" for k in tot},
                           "per_kind_half": {k: int(half[k]) for k in tot},
                           "components": comps, "misses_name": dict(picks)}),
           dict(prefix=name, op_plot=False, card=False))
    return er


def main():
    S = NE.spec(); lay, bands = nematode_layout(S)
    k0 = 0
    sec = ([S["SK"][(k0, c)] for c in range(NE.NC)] + [S["MU"][(q, k0)] for q in NE.MQUAD]
           + [S["GU"][(k0, c)] for c in range(NE.NCG)])
    run_worm("nematode", NE, S, lay, bands, sec,
             "Cross-section, one station\n(skin ring · 4 muscle quadrants · gut)",
             {"skin_ring", "gut"},
             "Nematode — body plan: skin tube with transducers, four detached longitudinal "
             "muscle quadrants, gut tube")

    S = EW.spec(); lay, bands = earthworm_layout(S)
    i0 = 0
    sec = ([S["C"][(i0, q)] for q in EW.QUADS] + [S["L"][(i0, q)] for q in EW.QUADS]
           + [S["G"][i0]])
    run_worm("earthworm", EW, S, lay, bands, sec,
             "Cross-section, one segment\n(outer circular · inner longitudinal · ganglion)",
             {"circ_m", "long_s"},
             "Earthworm — body plan: six segments, outer circular and inner longitudinal "
             "muscle, coelomic hydrostat struts, ventral cord")


if __name__ == "__main__":
    main()
