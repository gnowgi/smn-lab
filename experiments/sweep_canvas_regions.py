# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Canvas regions -- the self-organizing canvas + the morphology sweep.

Wires the preregistered order parameters (canvas_regions.py) onto an explicit
model: modules of distinct functionalities broadcast to ONE undivided plastic
canvas (a self-organizing map); we ask whether functional regions CONSTRUCT
themselves, and whether growing the morphology grows the number of regions.

  structured (the claim): class-structured module signatures + a plastic canvas
                          -> functional regions self-organize.
  no-plasticity (foil 1): same signatures, canvas frozen -> regions cannot be
                          constructed.
  scrambled (foil 2):     signatures with no class structure + plastic canvas ->
                          the map organizes, but there is nothing functional to
                          segregate.

Morphology sweep: a simple (1-class) agent stays one undivided canvas; as
functional classes are added (viscera / axial / appendicular ...), the canvas
partitions itself, n_regions tracking the functional complexity.

Run:  ../.venv/bin/python sweep_canvas_regions.py
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from canvas_regions import canvas_segregation, n_regions

GRID = (20, 20)
DIM = 8
N_PER_CLASS = 10
ITERS = 4000

MORPHOLOGIES = [("simple\n(axial)", 1), ("axial +\nviscera", 2),
                ("segmented", 3), ("appendicular", 4),
                ("dexterous\n(L0/L1/L2)", 5)]


def _modules(n_classes, sig_mode, seed):
    """Module broadcast signatures + their functional class. `structured`: class
    prototypes + noise (functionality carries class structure). `scrambled`:
    independent random signatures with class labels decoupled from them."""
    rng = np.random.default_rng(seed)
    if sig_mode == "scrambled":
        m = n_classes * N_PER_CLASS
        sigs = rng.standard_normal((m, DIM))
        classes = rng.integers(0, n_classes, m)
    else:
        protos = rng.standard_normal((n_classes, DIM))
        sigs, classes = [], []
        for c in range(n_classes):
            for _ in range(N_PER_CLASS):
                sigs.append(protos[c] + 0.35 * rng.standard_normal(DIM))
                classes.append(c)
        sigs, classes = np.array(sigs), np.array(classes)
    sigs /= np.linalg.norm(sigs, axis=1, keepdims=True) + 1e-9
    return sigs, classes


def _som(sigs, plastic, seed):
    """A self-organizing canvas: broadcast a random module signature, pull the
    best-matching unit and its (shrinking) neighbourhood toward it. `plastic=False`
    leaves the canvas frozen at random init (the no-plasticity foil)."""
    rng = np.random.default_rng(seed + 1)
    H, W = GRID
    w = rng.standard_normal((H, W, DIM))
    w /= np.linalg.norm(w, axis=2, keepdims=True) + 1e-9
    if not plastic:
        return w
    ii, jj = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    for t in range(ITERS):
        x = sigs[rng.integers(len(sigs))]
        by, bx = np.unravel_index(np.argmin(np.sum((w - x) ** 2, axis=2)), (H, W))
        frac = t / ITERS
        sigma = 6.0 * (1 - frac) + 0.6
        lr = 0.5 * (1 - frac) + 0.02
        nb = np.exp(-((ii - by) ** 2 + (jj - bx) ** 2) / (2 * sigma ** 2))[:, :, None]
        w += lr * nb * (x - w)
    return w


def _label(w, sigs, classes):
    """Label each canvas unit by the functional CLASS whose prototype (mean module
    signature) its weight vector responds to most. Prototype-labelling is the
    honest test: when functionality carries class structure the prototypes are
    distinct and the canvas segregates by class; when functionality is scrambled
    the class prototypes collapse together and no class map can form (so the
    SOM's mere topographic smoothness cannot manufacture regions)."""
    K = int(classes.max()) + 1
    protos = np.array([sigs[classes == c].mean(0) for c in range(K)])
    protos /= np.linalg.norm(protos, axis=1, keepdims=True) + 1e-9
    H, W, d = w.shape
    flat = w.reshape(-1, d)
    d2 = (np.sum(flat ** 2, 1)[:, None] - 2 * flat @ protos.T + np.sum(protos ** 2, 1)[None, :])
    return np.argmin(d2, axis=1).reshape(H, W)


def run_one(n_classes, mode, seed=0):
    sig_mode = "scrambled" if mode == "scrambled" else "structured"
    sigs, classes = _modules(n_classes, sig_mode, seed)
    w = _som(sigs, plastic=(mode != "no_plasticity"), seed=seed)
    labels = _label(w, sigs, classes)
    return canvas_segregation(labels), n_regions(labels), labels


def main():
    print("=== morphology sweep (structured: modules broadcast to one plastic canvas) ===")
    print(f"{'morphology':<16}{'classes':>8}{'segregation':>13}{'n_regions':>11}")
    seg_struct, nreg, maps = [], [], {}
    ks = [k for _, k in MORPHOLOGIES]
    for (name, k) in MORPHOLOGIES:
        s = np.median([run_one(k, "structured", seed=r)[0] for r in range(3)])
        rr = int(np.median([run_one(k, "structured", seed=r)[1] for r in range(3)]))
        seg_struct.append(s); nreg.append(rr)
        maps[k] = run_one(k, "structured", seed=0)[2]
        print(f"{name.replace(chr(10),' '):<16}{k:>8}{s:>13.2f}{rr:>11}")

    print("\n=== the two foils (at 4 functional classes; K=4) ===")
    k_foil = 4

    def _foil(mode):
        return (float(np.median([run_one(k_foil, mode, seed=r)[0] for r in range(3)])),
                int(np.median([run_one(k_foil, mode, seed=r)[1] for r in range(3)])))
    seg_np, nreg_np = _foil("no_plasticity")
    seg_sc, nreg_sc = _foil("scrambled")
    print(f"  no-plasticity (frozen canvas):     segregation={seg_np:.2f}  n_regions={nreg_np}")
    print(f"  scrambled functionality (plastic): segregation={seg_sc:.2f}  n_regions={nreg_sc}")
    print("  (the discriminator is n_regions ≈ K: the SOM smooths any input, so a high "
          "segregation\n   alone does not mean the regions are FUNCTIONAL — matched region "
          "count does.)")

    seg_struct = np.array(seg_struct); nreg = np.array(nreg); ks_a = np.array(ks)
    multi = ks_a > 1
    # structured: high segregation AND region count matches class count (+/-1)
    struct_ok = (np.all(seg_struct[multi] > 0.7)
                 and np.all(np.abs(nreg - ks_a) <= 1) and nreg[0] == 1
                 and np.all(np.diff(nreg) >= 0))
    # foils fail to reproduce the structured signature:
    np_fails = seg_np < 0.2                              # no construction at all
    sc_fails = nreg_sc > 2 * k_foil                      # regions do not match classes
    ok = struct_ok and np_fails and sc_fails
    print("\nverdict:", "PASS -- structured broadcasting constructs functional regions "
          "(high segregation AND n_regions ≈ class count, tracking morphology; simple "
          "agent = one undivided canvas). Neither foil reproduces it: the frozen canvas "
          "builds nothing; scrambled functionality gives a smooth-but-fragmented map that "
          "does not match the classes."
          if ok else "INCONCLUSIVE -- see order parameters above.")

    _plot(MORPHOLOGIES, ks, seg_struct, nreg, (seg_np, nreg_np), (seg_sc, nreg_sc),
          maps, k_foil)


def _plot(morphs, ks, seg_struct, nreg, foil_np, foil_sc, maps, k_foil):
    (seg_np, nreg_np), (seg_sc, nreg_sc) = foil_np, foil_sc
    fig = plt.figure(figsize=(14, 4.6))
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 0.15, 1.5], wspace=0.35)

    for col, k in enumerate((1, 3, 5)):
        ax = fig.add_subplot(gs[0, col])
        ax.imshow(maps[k], cmap="tab10", vmin=0, vmax=9, interpolation="nearest")
        title = [m for m, kk in morphs if kk == k][0].replace("\n", " ")
        ax.set_title(f"{title}\n{k} class{'es' if k > 1 else ''} → "
                     f"{nreg[ks.index(k)]} region{'s' if nreg[ks.index(k)] > 1 else ''}",
                     fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])

    ax = fig.add_subplot(gs[0, 4])
    ax.plot(ks, nreg, "-o", color="#1538a0", label="structured — n_regions")
    ax.plot([min(ks), max(ks)], [min(ks), max(ks)], ls="--", color="0.6",
            label="n_regions = K  (match)")
    ax.plot(k_foil, min(nreg_sc, 11.4), "^", color="#e8902a", ms=10,
            label=f"scrambled foil (n={nreg_sc} ≫ K)")
    ax.annotate(f"no-plasticity foil:\nn_regions={nreg_np} (off scale — builds nothing)",
                xy=(3.0, 10.3), fontsize=7.5, color="#b00000", ha="center")
    ax.set_xlabel("functional classes  (morphology grows →)")
    ax.set_ylabel("emergent regions  (n_regions)")
    ax.set_ylim(0, 12); ax.set_xticks(ks)
    ax.set_title("regions are CONSTRUCTED and track morphology\n"
                 "(structured on the diagonal; foils off it)", fontsize=9)
    ax.legend(fontsize=7.3, loc="center left")

    here = os.path.dirname(os.path.abspath(__file__))
    figdir = os.path.join(here, "..", "figures"); os.makedirs(figdir, exist_ok=True)
    out = os.path.join(figdir, "canvas_regions.png")
    fig.savefig(out, dpi=130, bbox_inches="tight"); print(f"[saved] {out}")


if __name__ == "__main__":
    main()
