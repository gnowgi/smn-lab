# The lab interface

`app.py` is a small, functional bench window — built so a reviewer can see that the
results are **the math in action**, computed on the spot, not synthesized. It runs
the real experiment code: the world view is the actual controller stepping a MuJoCo
body, and the result tables come from the same measurement functions the figures do.

!!! note "What the app currently exercises"
    The interactive **World / Graphs / Results** view was built in the provenance era
    and currently drives the **P3** cross-modal experiment (a
    [provenance study](reproducibility.md)), *not* the current spine (self-model,
    lattice, world-model, haltability). The **Self/world card** view below *is*
    current — it runs the consolidated `self_model.coupling` read-out. A going-forward
    interactive layer that maps each **symbol ↔ code argument ↔ live slider** for the
    spine experiments (the seminar demo) is planned but not yet built.

## What it shows (P3)

- **World** — press *Run approach* and watch the agent drive up to a chosen object
  under its own CPG + differential drive, read touch / vision / taste, and halt at it.
  The decoded reading and the object's located position print when it stops.
- **Graphs** — the result figures for the selected experiment.
- **Results** — the binding, localization, and resolution numbers computed live.
- **Documentation** — the experiment's own page, rendered inline.

## The self/world card (interactive — current)

Switch the sidebar **View** to *🕸️ Self/world card* for an interactive version of the
[self/world card](diagram-grammar.md#the-selfworld-card). Pick a body (branched, chain,
star, …); the bench moves it and recovers its self-model on the spot with the same
framework read-out (cached after the first run). Three live panels: the **designed
agent** (metric), the **recovered self-model** as a graph you can pan and hover — each
node shows the segments it couples — and the **world in the self-frame**, whose shading
follows a source you slide along any limb. The self-graph is laid out force-directed
from the body's own recovered adjacency, edge width = the measured coupling.

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

A GL backend renders the world (present on any desktop with a display). The core
bench — the experiments and the library — does not need streamlit; it is optional.
