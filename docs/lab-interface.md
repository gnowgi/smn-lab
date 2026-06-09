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

## Run it

```bash
pip install -r requirements-ui.txt      # one extra dependency: streamlit
streamlit run app.py                     # from the smn-lab/ directory
```

A GL backend is used to render the world (present on any desktop with a
display). The core bench — the experiments and the library — does not need
streamlit; it is an optional extra.
