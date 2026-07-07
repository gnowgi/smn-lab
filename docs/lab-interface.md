# The lab interface

`app.py` is a small, functional bench window — built so a reviewer can see that
the results are **the math in action**, computed on the spot, not synthesized.

It runs the real experiment code: the world view is the actual controller
stepping a MuJoCo body, and the result tables are produced by the same
measurement functions the figures come from.

## What it shows

- **World** — for the P3 experiment, press *Run approach* and watch the agent
  drive up to a chosen object under its own CPG + differential drive, read
  touch / vision / taste, and halt at it. The decoded reading and the object's
  located position are printed when it stops.
- **Graphs** — the result figures for the selected experiment.
- **Results** — for P3, the binding, localization, and resolution numbers
  computed live (press *Compute results*).
- **Documentation** — the experiment's own page, rendered inline.

The sidebar selects among all documented experiments; P3 is the interactive one.

## The self/world card (interactive)

Switch the sidebar **View** to *🕸️ Self/world card* for an interactive version of
the [self/world card](diagram-grammar.md#the-selfworld-card). Pick a body
(branched, chain, star, …); the bench moves it and recovers its self-model on the
spot (cached after the first run). Three live panels: the **designed agent**
(metric), the **recovered self-model** as a graph you can pan and hover — each
node shows the segments it couples — and the **world in the self-frame**, whose
shading follows a world source you slide along any limb. The self-graph is laid
out force-directed from the body's own recovered adjacency, and edge width is the
measured coupling.

## Run it

```bash
pip install -r requirements-ui.txt      # streamlit + plotly
streamlit run app.py                     # from the smn-lab/ directory
```

A GL backend is used to render the world (present on any desktop with a
display). The core bench — the experiments and the library — does not need
streamlit; it is an optional extra.
