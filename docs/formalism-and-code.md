# Formalism ↔ code ↔ live bench

This page is the **template** every experiment page follows, and its own proof of
concept. It shows one quantity three ways that *cannot disagree*:

1. the **equation**, in the symbols used throughout the site;
2. the **exact function** that computes it — read from `smn_lab/self_model.py` at
   build time, not pasted (change the source and this page changes);
3. the **parameter** the live demo varies to make the quantity move.

---

## The quantity: joint ↔ segment coupling \(C\)

A joint (a CAZ) is the hinge between two body segments. While the body moves we log
two time-by-index arrays: each joint's own angular velocity \(\dot{\theta}_{t,j}\)
(`JV`) and each segment's world yaw-rate \(\omega_{t,s}\) (`OMEGA`). The self-model
read-out is the normalized cross-correlation of the two:

\[
C_{j,s} \;=\; \frac{1}{T}\sum_{t=1}^{T} \hat{z}(\dot{\theta})_{t,j}\,\hat{z}(\omega)_{t,s},
\qquad
\hat{z}(x)_{t,i} = \frac{x_{t,i}-\bar{x}_{\cdot,i}}{\sigma_{x,\cdot,i}+\varepsilon}.
\]

Each joint's strongest positive column is the segment it **co-rotates** with (its
child); its strongest negative column is the one it **counter-rotates** with (its
parent). The union of every joint's edge is the body graph — recovered locally,
with no zone ever reading the whole body.

## The code that computes it

Read verbatim from the source (`smn_lab/self_model.py`):

```python
--8<-- "smn_lab/self_model.py:coupling"
```

`J.T @ O` divided by `len(JV)` is exactly the sum over \(t\) above; the two
z-scoring lines are \(\hat{z}\). The equation and the function are the same object
because the function *is* the page.

## The parameter the live demo varies

The quantity is only informative because the substrate is **elastic**. Joint
stiffness \(k\) (`joint_stiffness` in `crawler.py`) controls how far a joint's
motion transmits along the chain:

| Condition | \(k\) | What happens to \(C\) |
|---|---|---|
| **elastic** | `0.6` | off-diagonal coupling **decays with hop-distance** → the chain order is recoverable |
| **rigid** | `80.0` | body moves as one → whole-body common mode, no differential structure to read |
| **frozen** | `0.6`, no drive | no movement → \(C\) undefined |

In the seminar, the slider is \(k\); the figure the audience watches is \(C\) losing
its hop-structure as \(k\) rises. Symbol (\(k\)) ↔ code argument (`joint_stiffness`)
↔ live control are the same knob. The ablation is pre-run in
[Self-model — body topology from movement](experiments/self_model_topology.md).
