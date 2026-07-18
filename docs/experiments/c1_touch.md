# C1 — crawler under gravity: touch skin, objects, halt-on-contact

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_c1_touch.png)

## What it shows
The v1 organism of [The Construction of Experience](../construction-of-experience.md): the crawler under gravity, with a
ventral touch skin and objects. It demonstrates the **halt→aboutness** precursor
in its simplest physical form — **objecthood as resistance**: a chemotactic crawl
meets an object, the ventral touch skin registers it as a force spike above the
resting weight load, and that contact **halts** the wave. The body comes to rest
against the thing that does not yield to its modulation.

## The agent
In the [diagram grammar](../diagram-grammar.md): the same three-block crawler as
[C0](c0_crawler.md), now with a **ventral touch skin** added to each block
(orange hatch) alongside the bilateral chemical sensors. One CAZ per joint; no
localizer.

![C1 agent — the A3 crawler with chemical sensing and a ventral touch skin, in the diagram grammar](../figures/c1_agent.png)

## Setup
- **Body** — `build_crawler_xml(..., gravity_on=True, with_floor=True,
  with_walls=True, touch=True, objects=[(x, y, r)])`: gravity present; each
  segment carries a **ventral touch skin**; an object sits in the path to the source.
- **Touch skin** — each segment's skin reads its resting weight load plus any
  simulated object/wall **contact force**.
- **HAP** — on contact, a haltable action pattern drops the traveling-wave
  amplitude, so the action halts at the object.

## Formalism — objecthood as a halt

Two model pieces added on top of the [C0 locomotion](c0_crawler.md#formalism-locomotion-from-local-coupling)
turn "meeting an object" into "the action stops."

**1 · The ventral touch skin (the transducer, now under gravity).** Each segment's
skin reads its resting weight load \(W = m g\) plus any contact force \(f_k\); a
contact is a spike above that baseline:

\[
\text{touch}_k = W + f_k,\qquad \text{contact} = \big(\max_k f_k > \tau_{\text{margin}}\big).
\]

```python
--8<-- "experiments/c1_touch.py:touchskin"
```

**2 · The halt — a touch-keyed HAP.** On contact the agent recruits a *haltable
action pattern* that gates the BAP wave down to a residual tonus for a fixed
refractory window, then resumes. The object interrupts the body's own action —
**objecthood as resistance to modulation**:

\[
\text{gate} = \begin{cases}\text{HALT\_GATE} & \text{halted}\\ 1 & \text{else}\end{cases},
\qquad \theta^{\text{cmd}} = \text{gate}\cdot\texttt{beam.command}(dt,\,b).
\]

```python
--8<-- "experiments/c1_touch.py:haltparams"
```

```python
--8<-- "experiments/c1_touch.py:halt"
```

!!! note "Where this HAP lives"
    This halt is written **inline** because it is keyed on *contact force* and is
    the only contact-halt in the progression. It is the sibling of the framework's
    whisker-keyed [`HAPExplorer`](../concepts.md) (`smn_lab/control.py`), which
    halts on *rangefinder clearance* instead. Both are HAPs — an affordance gating
    the BAP. If a second contact-halt appears, the general HAP (affordance →
    threshold → gate) should be promoted to `control.py`; until then, promoting one
    instance would be premature abstraction.

## Assumptions specific to C1
(in addition to the [common assumptions](../assumptions.md))
- The body **glides in its support plane** (a frictionless-support idealization);
  the resting ventral load is modeled as segment weight and physical object/wall
  contact adds to it. A genuine free-body floor-rest (`free_root`) needs
  contact-dynamics tuning and is a later refinement.
- **Full negotiation** around the object (back up, reorient, resume) needs a
  richer HAP/NAP and is a later experiment. Here contact **halts**.


## What's measured and plotted
**Raw data (logged):** head `(x, y)`; per-segment **ventral touch** = resting weight
load + simulated object/wall contact force (MuJoCo touch sensor); a contact flag; a
halted flag; segment positions; distance to source. **Computed:** `weight_baseline`,
`contact`, `touch_peak` (the spike on meeting the object), `contact_frac`,
`net_disp`, `closed_gap` — the touch/contact/halt quantities defined as running code
in [Formalism](#formalism-objecthood-as-a-halt) above.

**Plotted:** **A** field + object + the path arrested at the object; **B** ventral touch per segment over time, with the resting-load line, the contact threshold, and the halt episode shaded; **C** the beam graph at the peak-contact frame, nodes coloured by touch force.

## Run
```bash
cd experiments && ../.venv/bin/python c1_touch.py
```

## Outputs
- `figures/c1_touch.png` — (A) field + object + path arrested at the object;
  (B) the ventral touch skin per segment over time with the halt episode shaded;
  (C) the beam at the contact frame, nodes coloured by touch force.
- printed stats: resting load, touch peak, halt fraction, distance arrested from
  the source; verdict.

## Result & interpretation

![C1 — chemotactic crawl arrested at an object; the ventral touch skin spiking on contact; the beam at contact](../figures/c1_touch.png)

*A: the crawl is arrested at the object. B: the ventral skin — the head segment
spikes well above the resting load during the shaded halt episode while the
trailing segments stay at baseline. C: the messaging beam at the contact frame,
the contacting head node hot.*

Touch peaks at ~1.5 N against a ~0.49 N resting load; the crawler halts for ~half
the run, arrested at the object ~1.6 m from the source. Contact halts the action —
the object is encountered as **resistance** to the body's modulation, the physical
seed of object-directedness.
