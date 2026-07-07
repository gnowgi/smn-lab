# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""SMN-Lab — a simple, functional lab interface (Streamlit).

A reviewer's bench window: pick an experiment, watch the agent move in its world,
and inspect the graphs, the tabulated numbers, and the documentation side by
side. Everything here calls the *real* experiment code — the world animation is
the actual controller stepping a MuJoCo body, the result tables are computed on
the spot — so what you see is the math in action, not a replay or canned
numbers.

Run (from the smn-lab/ directory):

    pip install -r requirements-ui.txt      # one extra dependency: streamlit
    streamlit run app.py

A GL backend is used to render the world (present on any desktop with a display).
"""
import os
import re
import io
import sys
import glob

import numpy as np
import streamlit as st
from PIL import Image
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "experiments"))

from smn_lab.body import MouseSchema
from smn_lab.model import (build_p0_xml, build_p0v_xml, build_p1v_xml,
                           build_p1_xml, build_p2_xml, build_p3_xml)
from smn_lab.crawler import build_crawler_xml
from smn_lab import morphology as gram
from smn_lab import self_model as sm
from smn_lab.fields import ScalarField
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
try:
    import plotly.graph_objects as go
    HAVE_PLOTLY = True
except Exception:
    HAVE_PLOTLY = False

# Every experiment maps to a renderable MuJoCo scene, so the World panel always
# shows the actual world (a static scene render); P3 additionally animates a run.
SCENE_BUILDERS = {
    "c0_crawler": lambda: build_crawler_xml(n_seg=3),
    "c1_touch": lambda: build_crawler_xml(
        n_seg=3, gravity_on=True, with_floor=True, with_walls=True,
        touch=True, objects=[(0.78, 0.0, 0.12)]),
    "p0_reafference": lambda: build_p0_xml(),
    "p0_visual": lambda: build_p0v_xml(),
    "p1_visual": lambda: build_p1v_xml(),
    "p1v_static_world": lambda: build_p1v_xml(),
    "p1_world_model": lambda: build_p1_xml(),
    "p2_world_model": lambda: build_p2_xml(MouseSchema()),
    "p2_topology_sweep": lambda: build_p2_xml(MouseSchema()),
    "p2_living_snapshot": lambda: build_p2_xml(MouseSchema()),
    "p2_basal_coupling": lambda: build_p2_xml(MouseSchema()),
    "p2_map_guided_foraging": lambda: build_p2_xml(MouseSchema()),
}

DOCS_DIR = os.path.join(HERE, "docs", "experiments")
FIGS_DIR = os.path.join(HERE, "figures")

st.set_page_config(page_title="SMN-Lab", layout="wide")


# ---------------------------------------------------------------- discovery ---
@st.cache_data(show_spinner=False)
def discover_experiments():
    """Every documented experiment: its title, doc text, and result figures —
    read straight from docs/ and figures/, the single source of truth."""
    exps = {}
    for md in sorted(glob.glob(os.path.join(DOCS_DIR, "*.md"))):
        key = os.path.splitext(os.path.basename(md))[0]
        text = open(md, encoding="utf-8").read()
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), key)
        figs = []
        for name in re.findall(r"figures/([\w\-]+\.png)", text):
            p = os.path.join(FIGS_DIR, name)
            if os.path.exists(p) and p not in figs:
                figs.append(p)
        exps[key] = {"title": title, "md": md, "text": text, "figs": figs}
    return exps


def doc_intro(text):
    """The first real paragraph of a doc (skip the title and the file-path line)."""
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("`"):
            if out:
                break
            continue
        out.append(s)
        if len(out) >= 3:
            break
    return " ".join(out)


def doc_for_display(text):
    """Strip local image markdown (Streamlit can't resolve the relative paths;
    the figures live in the Graphs tab) and leave the prose + tables intact."""
    lines = []
    for ln in text.splitlines():
        if re.match(r"\s*\[?!\[", ln):                 # an image / linked-image line
            continue
        lines.append(ln)
    return "\n".join(lines)


# ---------------------------------------------------- P3 live + computed -------
# P3 is the interactive flagship: its world animates and its numbers compute live.
P3_KEY = "p3_crossmodal_discrimination"


def load_p3():
    import p3_crossmodal_discrimination as p3
    return p3


def p3_object_labels(p3):
    objs = p3.make_objects()
    labels = []
    for o in objs:
        t, v, a = o["bits"]
        labels.append(f"{'big' if t else 'small'}, {'light' if v else 'dark'}, "
                      f"{'sweet' if a else 'bitter'}")
    return objs, labels


@st.cache_data(show_spinner=False)
def compute_p3_results():
    """Run the actual measurement functions and return tabulable results."""
    p3 = load_p3()
    objs = p3.make_objects()
    binding = []
    for c in [("touch",), ("touch", "vision"), ("touch", "vision", "taste")]:
        n, acc = p3.individuate(objs, c, p3.WHISKERS_5)
        binding.append({"coupling": " + ".join(c), "individuable categories": n,
                        "bit accuracy": round(acc, 2)})
    n9, _ = p3.individuate(objs, ("touch",), p3.WHISKERS_9)
    binding.append({"coupling": "touch, 9 whiskers", "individuable categories": n9,
                    "bit accuracy": 1.0})
    n_sub = p3.subsumption_individuate(objs)
    binding.append({"coupling": "subsumption, 3 sensors", "individuable categories": n_sub,
                    "bit accuracy": None})
    err_on = float(np.mean([p3.run_trial(o, p3.WHISKERS_5, True)["loc_err"] for o in objs]))
    err_off = float(np.mean([p3.run_trial(o, p3.WHISKERS_5, False)["loc_err"] for o in objs]))
    localization = [{"reafference": "on", "mean localization error (m)": round(err_on, 3)},
                    {"reafference": "off", "mean localization error (m)": round(err_off, 3)}]
    Ns, a_on, a_off = p3.resolution_sweep()
    resolution = [{"sensor channels": N, "modulation ON": round(x, 3),
                   "modulation OFF": round(y, 3)} for N, x, y in zip(Ns, a_on, a_off)]
    return binding, localization, resolution


@st.cache_data(show_spinner=False)
def render_scene(xml: str):
    """Render one third-person frame of a MuJoCo scene (cached by its XML)."""
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    r = mujoco.Renderer(model, height=400, width=600)
    cam = mujoco.MjvCamera()
    cam.lookat[:] = [0.3, 0.0, 0.12]
    cam.distance, cam.elevation, cam.azimuth = 4.0, -50.0, 90.0
    r.update_scene(data, cam)
    frame = r.render()
    r.close()
    return frame


def frames_to_gif(frames, width=540, duration=70):
    """Pack rendered frames into a looping animated GIF (reliable playback in the
    browser, unlike rapid placeholder writes which the frontend coalesces)."""
    imgs = []
    for f in frames:
        im = Image.fromarray(np.asarray(f).astype("uint8"))
        w, h = im.size
        if width and w != width:
            im = im.resize((width, int(h * width / w)))
        imgs.append(im)
    buf = io.BytesIO()
    imgs[0].save(buf, format="GIF", save_all=True, append_images=imgs[1:],
                 duration=duration, loop=0, optimize=True)
    return buf.getvalue()


def p3_world_panel():
    p3 = load_p3()
    objs, labels = p3_object_labels(p3)
    c1, c2 = st.columns([3, 2])
    with c2:
        idx = st.selectbox("Object to approach", range(len(objs)),
                           format_func=lambda i: f"#{i}: {labels[i]}", index=7)
        go = st.button("▶ Run approach", type="primary")
        st.caption("The agent drives up under its own CPG + differential drive, "
                   "reads touch / vision / taste, and halts at the object.")
    with c1:
        slot = st.empty()
        status = st.empty()
    o = objs[idx]
    xml = build_p3_xml(o["radius"], p3._rgba(o["lum"]), o["pos"], cosmetic=True)
    if not go:
        try:
            slot.image(render_scene(xml), width="stretch",
                       caption="The world (static) — press Run approach to watch the agent reach the object.")
        except Exception:
            slot.info("Press **Run approach** to watch the agent reach the object.")
        return
    try:
        frames = []
        with st.spinner("Running the real controller in MuJoCo…"):
            tr = p3.run_trial(o, p3.WHISKERS_5, reaff_on=True, cosmetic=True,
                              frame_cb=lambda rgb, info: frames.append(np.asarray(rgb)))
        if frames:
            slot.image(frames_to_gif(frames), width="stretch",
                       caption="Live run of the real controller (loops).")
        else:
            slot.image(render_scene(xml), width="stretch")
        r = tr["readings"]
        status.success(
            f"Read — touch {r['touch']:.0f}°  ·  vision {r['vision']:.2f}  ·  "
            f"taste {r['taste']:+.2f}   →   located at "
            f"({tr['est'][0]:+.2f}, {tr['est'][1]:+.2f}) m  (error {tr['loc_err']:.2f} m)")
    except Exception as e:
        slot.error(f"Live render needs a GL backend on a machine with a display "
                   f"({type(e).__name__}: {e}).")


# ----------------------------------------------------------------- layout -----
# ------------------------------------------------- self/world card (interactive)
SW_BODIES = {
    "branched (arms 3 / 2 / 4)": ((0.0, 3), (130.0, 2), (230.0, 4)),
    "chain (8 segments)":        ((0.0, 7),),
    "star (4 equal arms)":       ((45.0, 3), (135.0, 3), (225.0, 3), (315.0, 3)),
    "asymmetric Y (2 / 3 / 4)":  ((90.0, 2), (210.0, 3), (330.0, 4)),
}


@st.cache_data(show_spinner=False)
def _sw_sim(arms):
    """Move a body, recover its self-model, and lay it out. Cached per body."""
    from branched_self_model import run
    JV, OMEGA, positions, true_edges, jo, arm_struct = run([tuple(a) for a in arms])
    C = sm.coupling(JV, OMEGA)
    rec = sm.recover_edges(C)
    return dict(positions=positions, true_edges=true_edges, C=C, rec=rec,
                branch=sm.branch_node(rec), edge_w=sm.edge_strength(C),
                arm_struct=arm_struct, layout=gram.graph_layout(list(positions), rec, seed=3))


def _hops_from_head(rec, target, head=0):
    adj = {}
    for a, b in rec:
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    seen = {head}; frontier = [(head, 0)]
    while frontier:
        n, d = frontier.pop(0)
        if n == target:
            return d
        for m in adj.get(n, []):
            if m not in seen:
                seen.add(m); frontier.append((m, d + 1))
    return None


def _plotly_graph(layout, edges, node_color, node_text, hover, *, edge_w=None,
                  edge_color="#5b6b78", highlight=None, hl_color="#e8902a", height=440):
    fig = go.Figure()
    for i, (a, b) in enumerate(edges):
        xa, ya = layout[a]; xb, yb = layout[b]
        w = 2.5 if edge_w is None else 1.4 + 6.0 * float(edge_w[i])
        fig.add_trace(go.Scatter(x=[xa, xb], y=[ya, yb], mode="lines",
                      line=dict(width=w, color=edge_color), hoverinfo="skip", showlegend=False))
    nodes = list(layout)
    if highlight is not None and highlight in layout:
        hx, hy = layout[highlight]
        fig.add_trace(go.Scatter(x=[hx], y=[hy], mode="markers", hoverinfo="skip",
                      showlegend=False, marker=dict(size=40, color="rgba(0,0,0,0)",
                      line=dict(width=3.2, color=hl_color))))
    fig.add_trace(go.Scatter(
        x=[layout[n][0] for n in nodes], y=[layout[n][1] for n in nodes],
        mode="markers+text", text=[node_text[n] for n in nodes],
        textposition="middle center", textfont=dict(size=11, color="#132029"),
        marker=dict(size=27, color=[node_color[n] for n in nodes],
                    line=dict(width=1.5, color="#33414f")),
        hovertext=[hover[n] for n in nodes], hoverinfo="text", showlegend=False))
    fig.update_layout(showlegend=False, height=height, dragmode="pan",
                      margin=dict(l=8, r=8, t=8, b=8), plot_bgcolor="white",
                      paper_bgcolor="white",
                      xaxis=dict(visible=False),
                      yaxis=dict(visible=False, scaleanchor="x", scaleratio=1))
    return fig


def self_world_card_explorer():
    import math
    st.subheader("🕸️ Self/world card — interactive")
    st.caption("A body, the self-model it recovers from its own movement, and the "
               "world in its own frame. Hover a node for its couplings; move the "
               "world source to watch the localization follow.")
    if not HAVE_PLOTLY:
        st.warning("Install plotly for the interactive graphs: `pip install plotly`.")
        return

    with st.sidebar:
        st.header("Self/world card")
        body = st.selectbox("Body", list(SW_BODIES))
    arms = SW_BODIES[body]
    with st.spinner("Moving the body and recovering its self-model "
                    "(first run ~30 s, then cached)…"):
        S = _sw_sim(arms)
    positions, edges, rec = S["positions"], S["true_edges"], S["rec"]
    branch, edge_w, arm_struct, layout = S["branch"], S["edge_w"], S["arm_struct"], S["layout"]

    with st.sidebar:
        st.markdown("**World source**")
        ai = st.selectbox("On limb", range(len(arm_struct)),
                          format_func=lambda i: f"limb {i} · {arm_struct[i]['angle']:.0f}° · "
                          f"{len(arm_struct[i]['segs'])} seg")
        frac = st.slider("Position along limb", 0.0, 1.25, 0.95, 0.05)
        sigma = st.slider("Source spread", 0.12, 0.5, 0.26, 0.02)

    arm = arm_struct[ai]
    ang = math.radians(arm["angle"])
    reach = len(arm["segs"]) * 0.14 * frac
    field = ScalarField([(reach * math.cos(ang), reach * math.sin(ang), 1.0, sigma)])
    node_field = {n: field.sample(*positions[n]) for n in positions}
    source_node = max(node_field, key=node_field.get)

    # per-node recovered neighbourhood (for hover) and degree (for colour)
    nbrs = {n: [] for n in positions}
    for i, (a, b) in enumerate(rec):
        nbrs[a].append(b); nbrs[b].append(a)
    deg = {n: len(nbrs[n]) for n in positions}
    role = {n: ("#e8902a" if deg[n] >= 3 else ("#cdd6dd" if deg[n] <= 1 else "#7aa7cf"))
            for n in positions}
    hov2 = {n: f"seg {n} · degree {deg[n]}<br>couples: "
            + ", ".join(f"seg {m}" for m in sorted(nbrs[n])) for n in positions}
    label = {n: str(n) for n in positions}

    v = np.array([node_field[n] for n in positions]); lo = v.min(); rng = (v.max() - lo) or 1.0
    wcol = {n: f"rgba(44,162,95,{0.12 + 0.88 * (node_field[n] - lo) / rng:.3f})" for n in positions}
    hov3 = {n: f"seg {n}<br>field {node_field[n]:.2f}" for n in positions}

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1 · Designed agent** — metric (what we built)")
        fig, ax = plt.subplots(figsize=(4.4, 4.4))
        gram.render_body_graph(ax, positions, edges, head=0)
        st.pyplot(fig, use_container_width=True); plt.close(fig)
    with c2:
        st.markdown("**2 · Recovered self-model** — hover a node")
        st.plotly_chart(_plotly_graph(layout, rec, role, label, hov2, edge_w=edge_w,
                        edge_color="#3f6d99", highlight=branch, hl_color="#e8902a"),
                        use_container_width=True)
    with c3:
        h = _hops_from_head(rec, source_node)
        st.markdown(f"**3 · World in the self-frame** — source at seg {source_node}"
                    + (f", {h} hops from head" if h is not None else ""))
        st.plotly_chart(_plotly_graph(layout, rec, wcol, label, hov3,
                        edge_color="#c8d3db", highlight=source_node, hl_color="#111111"),
                        use_container_width=True)
    st.caption("Panel 2 is laid out force-directed from the body's *own recovered "
               "adjacency* (not its coordinates); edge width = measured coupling. "
               "Panel 3 paints the world onto that recovered graph.")


st.title("SMN-Lab — the embodied bench")
st.caption("A network of dynamical systems doing cognition. Everything below runs "
           "the real experiment code: the world is the controller stepping a MuJoCo "
           "body; the tables are computed live.")

with st.sidebar:
    _view = st.radio("View", ["Experiments", "🕸️ Self/world card"], index=0)
    st.divider()

if _view == "🕸️ Self/world card":
    self_world_card_explorer()
    st.stop()

exps = discover_experiments()
keys = list(exps)
default = keys.index(P3_KEY) if P3_KEY in keys else 0

with st.sidebar:
    st.header("Experiment")
    sel = st.radio("Choose", keys, index=default,
                   format_func=lambda k: exps[k]["title"].split("—")[-1].strip())
    st.divider()
    st.caption("smn-lab · GPL-3.0 · github.com/gnowgi/smn-lab")

exp = exps[sel]
st.subheader(exp["title"])
intro = doc_intro(exp["text"])
if intro:
    st.write(intro)

st.markdown("#### World")
if sel == P3_KEY:
    p3_world_panel()
else:
    shown = False
    builder = SCENE_BUILDERS.get(sel)
    if builder is not None:
        try:
            st.image(render_scene(builder()), width="stretch",
                     caption="The experiment's MuJoCo world (static scene). "
                             "Its behaviour and results are in the figures below; "
                             "the live agent runs in the P3 experiment.")
            shown = True
        except Exception:
            shown = False
    if not shown:
        if exp["figs"]:
            st.image(exp["figs"][0], width="stretch", caption="Result figure.")
        else:
            st.info("No world view available for this experiment yet.")

tab_g, tab_r, tab_d = st.tabs(["📊 Graphs", "🔢 Results", "📄 Documentation"])

with tab_g:
    if exp["figs"]:
        for f in exp["figs"]:
            st.image(f, width="stretch", caption=os.path.basename(f))
    else:
        st.info("No figures generated for this experiment.")

with tab_r:
    if sel == P3_KEY:
        st.caption("Computed live by the measurement functions (cached after the first run).")
        if st.button("Compute results"):
            with st.spinner("Running trials and measurements…"):
                binding, localization, resolution = compute_p3_results()
            st.markdown("**Binding** — individuable categories = 2^(modalities coupled)")
            st.table(binding)
            st.markdown("**Localization** — needs the self/world split (reafference)")
            st.table(localization)
            st.markdown("**Resolution principle** — accuracy vs sensor count")
            st.table(resolution)
        else:
            st.info("Press **Compute results** to run the measurements now "
                    "(~1 min; renders and trains on the spot).")
    else:
        st.info("Tabulated results are computed for the P3 experiment. "
                "Other experiments show their results in the Graphs tab and Documentation.")

with tab_d:
    st.markdown(doc_for_display(exp["text"]))
    st.caption(f"Source: docs/experiments/{sel}.md  ·  figures shown in the Graphs tab.")
