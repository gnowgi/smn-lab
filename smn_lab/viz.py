# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Visualization of the messaging beam: its structure and its dynamic state.

Two complementary views of the SMN messaging beam (the inter-zone coupling that
maintains and shares the network's state-space), beyond the usual bar/cartesian
plots:

- ``draw_beam_graph`` -- a node-link drawing of the beam. Nodes are placed at the
  CAZ/segment body coordinates, so the graph *is* the body schema: body geometry
  as the frame of reference, drawn literally. Node color = local state (e.g. the
  field a segment senses); edge width/color = the coupling 'message' on that link.

- ``plot_state_space`` -- the trajectory of the beam's shared state vector over
  time. For two coordinates this is drawn directly (and the enclosed loop area is
  the Purcell signature: net displacement per gait cycle); higher dimensions are
  projected to 2D by PCA (plain numpy SVD, no extra dependency).

Pure matplotlib + numpy -- consistent with every experiment in the bench, and
animatable frame-by-frame. networkx/plotly are only worth adding for abstract
board topologies (no natural coordinates) or interactive use.
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def draw_beam_graph(ax, node_xy, node_val, edges, edge_val=None,
                    node_labels=None, cmap="viridis", node_size=420,
                    title=None, vlim=None, edge_label="message",
                    node_cbar_label="node state"):
    """Draw the beam as a node-link graph at the given node coordinates.

    node_xy    : (N, 2) world coordinates of the nodes (segment COMs).
    node_val   : (N,) scalar per node -> node color.
    edges      : list of (i, j) index pairs.
    edge_val   : (E,) magnitude per edge -> line width + color (optional).
    """
    node_xy = np.asarray(node_xy, dtype=float)
    node_val = np.asarray(node_val, dtype=float)
    segs = [[node_xy[i], node_xy[j]] for (i, j) in edges]
    if edge_val is not None and len(edge_val):
        ev = np.abs(np.asarray(edge_val, dtype=float))
        widths = 1.5 + 6.0 * ev / max(ev.max(), 1e-9)
        lc = LineCollection(segs, colors="#444", linewidths=widths, zorder=1)
    else:
        lc = LineCollection(segs, colors="#888", linewidths=2.0, zorder=1)
    ax.add_collection(lc)
    vmin, vmax = (vlim if vlim is not None else (node_val.min(), node_val.max()))
    sc = ax.scatter(node_xy[:, 0], node_xy[:, 1], c=node_val, cmap=cmap,
                    s=node_size, vmin=vmin, vmax=vmax, edgecolors="k",
                    linewidths=1.2, zorder=2)
    if node_labels is not None:
        for (x, y), lab in zip(node_xy, node_labels):
            ax.annotate(lab, (x, y), ha="center", va="center", fontsize=8,
                        color="w", zorder=3)
    ax.set_aspect("equal")
    cb = ax.figure.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label(node_cbar_label, fontsize=8)
    if title:
        ax.set_title(title, fontsize=10)
    return sc


def _pca2(X):
    """Project rows of X to 2D via SVD; returns (Y, explained_ratio)."""
    Xc = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    Y = Xc @ Vt[:2].T
    ev = S ** 2
    return Y, (ev[:2].sum() / max(ev.sum(), 1e-12))


def _loop_area(xy):
    """Signed area enclosed by a closed path (shoelace)."""
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def plot_state_space(ax, trace, c=None, labels=("state 1", "state 2"),
                     title=None, cmap="plasma", show_area=True):
    """Plot the beam's shared-state trajectory.

    trace : (T, D) array of the shared state over time. D == 2 is drawn directly;
            D > 2 is projected to its first two principal components.
    c     : (T,) values to color the path by (e.g. time); default = time index.
    """
    trace = np.asarray(trace, dtype=float)
    if trace.shape[1] == 2:
        Y = trace
        xlab, ylab = labels
    else:
        Y, ratio = _pca2(trace)
        xlab, ylab = f"PC1", f"PC2 ({ratio*100:.0f}% var)"
    c = np.arange(len(Y)) if c is None else np.asarray(c)
    pts = Y.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, array=c[:-1], linewidths=1.6)
    ax.add_collection(lc)
    ax.scatter(Y[0, 0], Y[0, 1], c="k", s=30, zorder=3, label="start")
    ax.scatter(Y[-1, 0], Y[-1, 1], c="r", s=30, zorder=3, label="end")
    ax.set_xlabel(xlab, fontsize=9)
    ax.set_ylabel(ylab, fontsize=9)
    pad = 0.1 * (Y.max() - Y.min() + 1e-6)
    ax.set_xlim(Y[:, 0].min() - pad, Y[:, 0].max() + pad)
    ax.set_ylim(Y[:, 1].min() - pad, Y[:, 1].max() + pad)
    if show_area and trace.shape[1] == 2:
        area = _loop_area(Y)
        ax.text(0.03, 0.97, f"loop area = {area:+.3f}\n(non-reciprocal ⇒ net motion)",
                transform=ax.transAxes, va="top", ha="left", fontsize=8,
                bbox=dict(boxstyle="round", fc="white", ec="#aaa", alpha=0.85))
    ax.legend(loc="lower right", fontsize=7)
    if title:
        ax.set_title(title, fontsize=10)
