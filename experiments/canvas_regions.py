# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Canvas regions -- does the broadcasting canvas CONSTRUCT its own functional
regions? STARTER / PREREGISTRATION.

Status: PREREGISTERED, implementation in progress (branch exp/canvas-regions).

The broadcasting substrate (the canvas) is ONE undivided field. The framework's
claim is that functional regions are NOT pre-given (not a description) but
CONSTRUCTED -- they self-organize from the functional relations of the modules
that keep broadcasting to the canvas (cortical-map formation). This is a
PREDICTION of a construction, and its best test: build a body of modules
broadcasting to one undivided plastic canvas and ask whether regions emerge.

This file holds the ORDER PARAMETERS (the single source of truth):
  - canvas_segregation: how spatially clustered the canvas's functional labels are,
    normalized so 0 = unstructured (chance) and 1 = fully segregated regions;
  - n_regions: the number of contiguous label territories that have formed.

The plastic canvas (a self-organizing map) + the module-functionality body + the
two foils (no-plasticity, scrambled-functionality) + the morphology sweep are
wired next; see docs/experiments/canvas_regions.md.

Run:  ../.venv/bin/python canvas_regions.py
"""
from __future__ import annotations
import numpy as np


# --8<-- [start:segregation]
def canvas_segregation(labels):
    """Order parameter: the spatial segregation of the canvas's functional labels.

    `labels` is a 2-D integer array -- each canvas unit tagged by the module-class
    it responds to after broadcasting. Returns
        (s - chance) / (1 - chance),
    where s = fraction of 4-neighbour unit-pairs sharing a label and
    chance = sum_c p_c^2 (the same-label probability for a random arrangement with
    the same class proportions). 0 = unstructured (regions not constructed);
    1 = fully segregated contiguous regions. A single-class canvas returns 1 (one
    undivided region -- the simple agent)."""
    labels = np.asarray(labels)
    same = int(np.sum(labels[:, :-1] == labels[:, 1:]) +
               np.sum(labels[:-1, :] == labels[1:, :]))
    tot = labels[:, :-1].size + labels[:-1, :].size
    s = same / tot
    p = np.unique(labels, return_counts=True)[1] / labels.size
    chance = float(np.sum(p ** 2))
    return 1.0 if chance >= 1.0 else float((s - chance) / (1.0 - chance))
# --8<-- [end:segregation]


# --8<-- [start:regions]
def n_regions(labels):
    """Secondary order parameter: the number of contiguous, same-label territories
    the canvas has partitioned itself into (4-connected components). For a
    well-segregated canvas this equals the number of functional classes; a simple
    (single-class) agent gives 1 -- one undivided canvas."""
    labels = np.asarray(labels)
    H, W = labels.shape
    seen = np.zeros((H, W), bool)
    count = 0
    for i in range(H):
        for j in range(W):
            if seen[i, j]:
                continue
            count += 1
            lab = labels[i, j]
            stack = [(i, j)]; seen[i, j] = True
            while stack:
                y, x = stack.pop()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and not seen[ny, nx] \
                            and labels[ny, nx] == lab:
                        seen[ny, nx] = True; stack.append((ny, nx))
    return count
# --8<-- [end:regions]


def _self_test():
    """Synthetic self-test of the order parameters (NOT a canvas run): confirm they
    read a known segregated map, a random map, and a single-class map correctly."""
    rng = np.random.default_rng(0)
    H = W = 24

    seg = np.zeros((H, W), int); seg[:, W // 2:] = 1              # two clean blocks
    print(f"[segregated 2-block]  segregation={canvas_segregation(seg):.2f} "
          f"(expect ~1)   n_regions={n_regions(seg)} (expect 2)")

    rand = rng.integers(0, 2, (H, W))                            # unstructured
    print(f"[random / unstructured] segregation={canvas_segregation(rand):.2f} "
          f"(expect ~0)")

    one = np.zeros((H, W), int)                                  # simple agent
    print(f"[single class / simple agent] segregation={canvas_segregation(one):.2f} "
          f"(expect 1)   n_regions={n_regions(one)} (expect 1 -- one undivided canvas)")

    print("[canvas-regions] status: PREREGISTERED -- the self-organizing canvas, the "
          "module-functionality body, the two foils, and the morphology sweep are not "
          "yet wired. See docs/experiments/canvas_regions.md.")


if __name__ == "__main__":
    _self_test()
