# Q2 — self/world distinction (reafference) on the crawler

## The two networks

The [two networks](../diagram-grammar.md#the-two-networks-body-and-canvas) of this
agent — the mechanical body above, and the one broadcasting **canvas** below that
every CAZ writes to and reads from (network closure); single-interface transducers
reach it only through a CAZ's modulation (*only modulated data enters*). The canvas
is undivided — regions are **constructed** by broadcasting only as anatomy grows,
not drawn in advance.

![The two networks of this agent — mechanical body and one broadcasting canvas](../figures/two_network_q2_reafference.png)

## Setup at a glance
*Agent morphology (left) and the world / experimental conditions (right).*

![Setup — agent morphology and the world](../figures/setup_q2_reafference.png)

Pre-registered in the [test plan](../test-plan.md). The reafference principle:
sensed change decomposes as `dm/dt = ∇m·v` (self-caused) `+ ∂m/∂t|world`
(world-caused); a reafferent agent predicts the self term and is left with the
world term.

## What it tests
The crawler explores a static **linear field** (a uniform slope — the world where
the reafference model `∇m·v` is *exact*, so any residual after cancellation is
genuinely world-caused, not model error). Then:
- **self-test** — world static, agent moving → residual should fall to ~noise;
- **exafference** — a strong source *moves* across the agent's region (as in P0's
  sliding object) → residual should spike (a world-caused change the agent did not
  produce).

Order parameter: residual ratio = mean |residual| (exafference / self-test).
**Foil:** no forward model (no cancellation). Pass: ratio ≫ 1 for the reafferent
agent and ≈ 1 for the foil.

## Formalism — the reafference cut

A sensed change decomposes into a self-caused and a world-caused part:

\[
\frac{dm}{dt} = \underbrace{\nabla m \cdot v}_{\text{self-caused}}
              + \underbrace{\left.\tfrac{\partial m}{\partial t}\right|_{\text{world}}}_{\text{exafference}}.
\]

A reafferent agent predicts the self term and keeps the residual as the world term.
On this crawler the forward model is a **gradient projection**: the field gradient
\((g_x,g_y)\) (a least-squares plane-fit over the sensor sites) dotted with the
agent's own sensed displacement, with an online-calibrated gain:

\[
\widehat{\Delta m}_{\text{self}} = \text{scale}\,(g_x\,\Delta x + g_y\,\Delta y),
\quad
r_{\text{reaff}} = \Delta m - \widehat{\Delta m}_{\text{self}},
\quad
r_{\text{foil}} = \Delta m.
\]

```python
--8<-- "experiments/sweep_q2_reafference.py:reaff"
```

The **order parameter** is the residual ratio — mean \(|r|\) in the exafference
window over the self-test window; \(\gg 1\) for the reafferent agent, \(\approx 1\)
for the foil.

!!! note "One principle, three forward models"
    The residual operation \(r = \text{actual} - \widehat{\text{self}}\) is the
    invariant; the *forward model* producing \(\widehat{\text{self}}\) is body-plan
    specific. The framework's [`ReafferencePredictor`](../concepts.md)
    (`smn_lab/control.py`) learns it as a **yaw-binned running mean** (used by the
    P-series); Q2 uses a **gradient projection** (its contingency is
    reading-vs-displacement); [W3](reafference_cut_self_graph.md) uses a **per-zone**
    gain in the self-graph frame. Different contingencies, one cut — so the forward
    models are genuinely distinct, not copies to merge. What they share — the
    residual and the exafference/self-test ratio — is what's worth stating once.

## Declared adjustments

This was the hardest port so far, and several choices were needed — all declared,
and the modeling trail is reported rather than hidden:

- **Windowed evaluation (0.25 s).** Per-step field change is below the sensor-noise
  floor; reafference is evaluated over a window where self-caused change clears
  noise.
- **Linear field + moving source.** Chosen by principle, not by result: the linear
  field makes the gradient model exact, and a moving source (P0-style) gives a
  strong world-caused term. Earlier curved-field and slow-ramp versions were
  discarded because the signal sat near the noise floor (an honest SNR failure,
  not a finding).
- **Self-gain calibration.** A scalar relating `∇m·(self-displacement)` to the
  observed change is fit during a static-world phase.

None of these is in the SMN preprint; they are operationalizations of its
reafference principle.

## Result

![Q2 — the reafferent residual is lower than the foil during self-motion and spikes during exafference; ratio 2.2 vs foil 1.58 across 10 seeds](../figures/q2_reafference.png)

| quantity | reafferent | foil |
|---|---|---|
| self-test residual | **0.0104** | 0.0164 |
| exafference residual | 0.0228 | 0.0252 |
| ratio (exaf / self) | **2.2 ± 0.3** | 1.58 ± 0.35 |

**Partially supported — a real but modest effect.** Reafference **cancels ~37% of
self-caused change** (self-test residual 0.0104 vs the foil's 0.0164) and lifts the
self/world ratio to 2.2 vs the foil's 1.58, across 10 seeds. So the principle
*works* on the crawler — self-caused change is partly cancelled and world-caused
change stands out more — but far less cleanly than in
[P0](p0_reafference.md) (single whisker, ~9× ratio).

## Interpretation — why only partial, and what it implies

The cancellation does **not** reach the noise floor even though the field model is
exact. The reason is a genuine, interesting limitation: the agent predicts from a
single **head-velocity** proprioceptive signal, but its sensors are **distributed**
over a **bending** body — so the head's motion is a poor proxy for how a tail
sensor actually moves. Single-point proprioception cannot fully predict
distributed reafference.

This is not a failure of the principle; it is a pointer to the mechanism the
architecture actually specifies. The SMN preprint's **dual-port modulator** has
each zone *both measure and move* — i.e., each zone senses **its own** motion. That
is exactly what would let each distributed sensor predict its own reafferent
consequence. So Q2's limitation directly motivates the
[Q1](sweep_q1_modulation.md) modulation mechanism: **distributed, per-zone
reafference**. P0 remains the clean canonical demonstration of the principle;
the crawler shows it is real but needs distributed modulation to be clean.

## Audit — the working null (2026-07-24)

The scrutiny pass this page had not yet had. The order parameter compares each
agent's *own* exafference/self-test ratio, so a skeptic asks: is the reafferent's
elevated ratio actually caused by the moving source, or is the "exafference"
window simply different (windowing, calibration drift, non-stationarity) in a way
that would inflate the ratio even with nothing happening? The matched foil rules
out "no forward model", but not "no world event".

**The null:** re-run with the moving-source amplitude set to **zero**, so the
exafference window contains no world-caused change. If the reafferent/foil
separation is genuinely world-caused, both ratios must collapse toward 1.

![Q2 audit — with the source removed, both ratios collapse to ~1; the baseline
separation is world-caused](../figures/q2_reafference_audit.png)

| quantity (10 seeds) | baseline (source moves) | no-event null (amp = 0) |
|---|---|---|
| reafferent ratio | 2.20 ± 0.28 | **1.02 ± 0.22** |
| foil ratio | 1.58 ± 0.33 | 0.92 ± 0.15 |
| reafferent − foil gap | **+0.62** | +0.10 |
| reafferent > foil | **10 / 10 seeds** | 6 / 10 seeds |
| self-test cancellation | 37 % | 37 % (unchanged) |

**Survives.** With the source removed the reafferent ratio drops to 1.02 and the
reafferent/foil gap shrinks from +0.62 to +0.10 — so **≈ 84 % of the separation is
world-caused**, and the elevated ratio is not a windowing artifact. The
separation is also **per-seed robust** (reafferent > foil in every seed of the
baseline), and the 37 % self-test cancellation is identical with and without the
event, confirming it is a stable property of the self-motion prediction rather
than something the event induces. One honest refinement the null adds: a small
**+0.10 residual offset** persists with no event (reafferent ratio sits at 1.02,
foil at 0.92), so ~16 % of the raw gap is a structural bias, not world signal — it
does not overturn the effect but is now on the record. The reproduction script is
[`audit_q2_reafference.py`](https://github.com/gnowgi/smn-lab/blob/main/experiments/audit_q2_reafference.py).

This audit confirms the page's existing **"partially supported — real but modest"**
claim rather than changing it; the row moves from 🟡 (not yet audited) to ✅
(consistency-checked) **for that modest claim** — not for clean reafference, which
the page already says the crawler does not achieve without distributed modulation.

## What's measured and plotted
**Raw data (per run = one seed):** each step, the agent's own (proprioceptive,
noisy) head displacement `(dx, dy)` is accumulated. Every 0.25 s window: the mean
field reading `m` over the body's sensor sites; a phase tag (learn / self-test /
exafference). **Computed:** the gradient plane-fit, the predicted self-term, the
reafferent and foil residuals, and the residual ratio — defined as running code in
[Formalism](#formalism-the-reafference-cut) above.

**Plotted:** **A** `|residual|` over time (one seed), reafferent vs foil, with the self-test and exafference windows shaded; **B** the ratio across seeds, reafferent vs foil.

## Run
```bash
cd experiments && ../.venv/bin/python sweep_q2_reafference.py
```
