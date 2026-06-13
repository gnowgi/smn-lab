# Formal Review of `smn-lab`

## Executive Judgment

The bench is a credible exploratory simulation environment for instantiating parts of the SMN architecture, but it does not yet provide equally strong support for all four stated research questions. Its strongest evidence is for `self/world distinction` and for `world-model construction` in a limited, idealized sense. Its evidence for `haltability as object-directedness` and especially for `cross-modal object construction/distinction` is suggestive, but not yet strong enough to support the broader claims currently made in the README.

## Scope of Review

This review evaluates the bench against the stated objective of testing the SMN architecture through four core questions:

1. Can an agent modeled as SMN generate a world model based on sensation modulation?
2. Can self/world distinction be achieved by the agent?
3. Can haltability as situated in the architecture provide object directedness?
4. Can SMN architecture distinguish and construct an object using multi/cross-modal modulation?

The review is based on the repository README, experiment documentation, and experiment implementations currently present in the project.

## Primary Findings

1. `World-model construction` is only partially established. The mapping experiments do show that an embodied agent can accumulate a useful body-relative surface map from action and sensing. But the dependent variable is a permissive surface-hit score, not a richer test of world-model structure. This supports `map-like reconstruction`, not yet a general claim that SMN constructs a world model in the stronger cognitive sense.

2. `Self/world distinction` is the best-supported claim. P0 is a clean and focused design: the agent learns a self-motion contingency, predictions are frozen, and externally introduced change produces a much larger residual. This is the clearest case where the experiment matches the stated objective and where the conclusion is proportional to the measurement.

3. `Balance-beam topology as the key independent variable` is not tested cleanly enough to support the README framing. The README presents topology as the experimental IV with body/world/task fixed, but the sweep changes routing, whisker count, drive-zone width, BAP, HAP, and proprioceptive noise together. That is a mixed ablation panel, not a topology-isolation experiment.

4. `Haltability as object-directedness` is not yet directly demonstrated. The current HAP implementations mainly gate movement or steer by immediate affordance structure such as open space, blockage, or remembered food location. That shows action interruption and redirection. It does not yet isolate the stronger claim that haltability yields genuine object-directedness rather than reactive control plus memory bias.

5. `Cross-modal object distinction/construction` is the weakest evidential area relative to the strength of the claims. P3 uses hand-defined feature boundaries, hand-set floors, staged one-object-at-a-time encounters, and engineered decoding rules. That is a valid constructive prototype, but it does not yet demonstrate that objecthood or recognition emerges from the architecture alone.

6. The project documentation currently overstates at least some P3 conclusions. The checked-in docs claim 9 whiskers still yield only 2 touch-only classes and that a deep net needs about 128 examples to match SMN. In the current codebase, running the script produced `3` touch-only classes with 9 whiskers and a neural net matching SMN by roughly `32` examples. That makes the present writeup scientifically too assertive relative to the implementation.

## Review Against the Four Core Questions

## 1. Can an agent modeled as SMN generate a world model based on sensation modulation?

Partially yes.

### What the bench shows

- The agent can accumulate a stable body-relative spatial surface map from whisker hits while moving.
- Removing key control components such as BAP or HAP degrades map coverage substantially.

### What it does not yet show strongly enough

- That the map depends specifically on `sensation modulation` rather than on a useful combination of sensor geometry, dead reckoning, and a hand-designed exploration controller.
- That the resulting internal structure deserves the stronger label `world model` rather than `surface occupancy accumulation`.

### Assessment

Strong as a constructive demonstration of embodied mapping. Moderate at best as evidence for the theoretical SMN claim that world-model construction is specifically due to modulation.

## 2. Can self/world distinction be achieved by the agent?

Yes, within the limits of the simplified setup.

### Why this is convincing

- The experiment is tightly scoped.
- The manipulation is understandable.
- The dependent variable is directly tied to the claim: prediction residual under self-caused versus externally caused change.

### Limits

- It is a scheduled, low-dimensional setup.
- The predictor is a simple binned mean over heading.
- It shows reafference in a narrow form, not full self/world distinction in richer dynamic scenes.

### Assessment

This is the bench’s strongest result and does support the claim in a restricted but meaningful sense.

## 3. Can haltability as situated in the architecture provide object directedness?

Not yet convincingly.

### What is shown

- HAP can halt, gate, or redirect movement based on sensed conditions.
- In foraging variants, action can be biased toward remembered food locations.

### Why this falls short

- Object-directedness would require showing that halting/recruitment is organized around individuated objects as objects, not merely local cues or trajectories.
- Current controllers are reactive heuristics over clearance, nearest target direction, and simple memory traces.
- There is no clean comparison between mere obstacle response and true object-directed approach, persistence, reacquisition, or object-specific action selection.

### Assessment

The bench demonstrates interruptible situated control. It does not yet establish the stronger philosophical or architectural claim about object-directedness.

## 4. Can SMN architecture distinguish and construct an object using multi/cross-modal modulation?

Suggestive, but not yet established at the level claimed.

### What P3 does well

- It turns cross-modal binding into an explicit and testable mechanism.
- It compares coupled modalities against same-modality sensor density.
- It includes foil systems.

### Why the evidence remains weak

- Objects are predefined as 3 binary features, already factored into modality-specific channels.
- The decoder is explicitly engineered around those factors.
- Encounters are staged one object at a time.
- The localization `reafference off` condition is not a mechanism ablation; it substitutes the start pose for the estimated pose.
- The deep-net comparison is not balanced because SMN gets strong hand-built inductive structure while the net must discover features from raw input.

### Assessment

Good as a proof-of-concept implementation of one possible SMN-style binding scheme. Not yet sufficient to claim that SMN architecture, as such, constructs objecthood or outperforms alternative accounts in a general way.

## Design Strengths

- Clear architecture-to-simulation mapping in the repository and docs.
- Good separation between body, control, model, and experiment logic.
- Reproducible seeds and persistent output artifacts.
- Honest assumptions document, which improves interpretability.
- P0 and P2 build cumulatively rather than as isolated demos.

## Design Weaknesses

- Many experiments are single-seed demonstrations rather than replicated studies.
- Several headline conclusions depend on manually chosen thresholds and floors.
- The benchmark tasks are too easy and too structured to meaningfully separate architectural alternatives.
- Some foil comparisons are not methodologically balanced.
- Metrics are narrow and often saturate.
- README claims are ahead of the evidential base in the code.

## Suggested Experimental Designs

## 1. Stronger world-model experiment

- Use multiple arenas with held-out layouts, not one fixed arena.
- Compare `SMN full`, `no modulation`, `random exploration`, `same sensors with non-modulatory controller`.
- Measure:
  - map coverage/precision
  - free-space correctness
  - object-count accuracy
  - revisitation efficiency
  - prediction of future sensor input from the built map

### Key claim supported

Whether modulation contributes something beyond geometry plus exploration.

## 2. Stronger self/world distinction experiment

- Replace scheduled single-object exafference with several perturbation classes:
  - external object motion
  - wall motion
  - self-motion only
  - self-motion plus independent world motion
- Test across whisker and visual channels in the same protocol.
- Compare residual distributions statistically over many runs.

### Key claim supported

Whether self/world distinction generalizes beyond the toy register.

## 3. Direct haltability-to-object-directedness experiment

- Create tasks with multiple simultaneously present objects offering different affordances.
- Require the agent to interrupt ongoing action and selectively orient to one object class over another.
- Include reacquisition after occlusion or temporary disappearance.
- Compare:
  - HAP-based interruption
  - no haltability
  - purely reactive obstacle avoidance
- Measure:
  - successful object approach
  - latency to interrupt prior action
  - persistence toward target object
  - recovery after distraction

### Key claim supported

Whether haltability yields aboutness-like directed action rather than generic reactivity.

## 4. Stronger cross-modal objecthood experiment

- Move from 3 preassigned binary bits to families of objects with overlapping, noisy, partially ambiguous cues.
- Present multiple objects in clutter, not one at a time.
- Require the agent to bind modalities across time and movement, not at a single best-approach frame.
- Test whether the same object remains unified across:
  - changing viewpoint
  - temporary sensory dropout
  - conflicting single-modality evidence
- Compare against:
  - uncoupled modality streams
  - suppression-only controller
  - alternative structured non-SMN baselines
- Measure:
  - object identity consistency over time
  - object persistence through occlusion
  - localization consistency
  - confusion under cue conflict

### Key claim supported

Whether cross-modal modulation constructs stable objecthood rather than just decoding hand-designed feature tuples.

## 5. Balanced foil design

- If comparing to learned models, compare against:
  - models with equivalent access to engineered features
  - models with equivalent priors
  - simpler structured baselines, not only raw-input MLPs
- Report sample efficiency curves with confidence intervals across seeds.

### Key claim supported

Whether SMN’s advantage is architectural, or just prior structure plus task simplification.

## Recommendation

The project should presently frame itself as:

- an embodied experimental bench for implementing and probing SMN hypotheses,
- with strong preliminary evidence for reafference-based self/world discrimination,
- moderate evidence for body-relative map construction,
- exploratory evidence for viability coupling and map-guided behavior,
- and early, not yet decisive, evidence for cross-modal object construction and object-directedness.

That framing would be defensible. The current stronger claims should be reserved until the experiments are redesigned around cleaner ablations, harder tasks, replicated runs, and better-balanced comparisons.
