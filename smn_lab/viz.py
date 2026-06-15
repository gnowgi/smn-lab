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
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection

from smn_lab.morphology import zone as _zone, NETWORK_COLOR


def _auto_radius(node_xy):
    """A node radius scaled to the nearest-neighbor spacing of the layout."""
    if len(node_xy) < 2:
        return 0.06
    d = np.sqrt(((node_xy[:, None, :] - node_xy[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    return 0.20 * float(np.median(d.min(axis=1)))


def draw_beam_graph(ax, node_xy, node_val, edges, edge_val=None,
                    node_labels=None, cmap="viridis", node_r=None,
                    title=None, vlim=None, edge_label="message",
                    node_cbar_label="node state"):
    """Draw the messaging beam as a node-link graph on the body geometry, in the
    shared grammar: **nodes are dual-interface zones** (half-filled circles, the
    filled half colored by the node's state) and **edges are light-blue coupling
    lines** (width = message magnitude). The graph *is* the body schema -- body
    geometry as the frame of reference, drawn literally.

    node_xy    : (N, 2) world coordinates of the nodes (zone/segment positions).
    node_val   : (N,) scalar per node -> filled-half color (the node's state).
    edges      : list of (i, j) index pairs.
    edge_val   : (E,) magnitude per edge -> line width (optional).
    """
    node_xy = np.asarray(node_xy, dtype=float)
    node_val = np.asarray(node_val, dtype=float)
    r = node_r if node_r is not None else _auto_radius(node_xy)

    # edges -- the coupling network (light blue), width by message magnitude
    segs = [[node_xy[i], node_xy[j]] for (i, j) in edges]
    if edge_val is not None and len(edge_val):
        ev = np.abs(np.asarray(edge_val, dtype=float))
        widths = 1.5 + 6.0 * ev / max(ev.max(), 1e-9)
    else:
        widths = 2.2
    ax.add_collection(LineCollection(segs, colors=NETWORK_COLOR,
                                     linewidths=widths, zorder=1))

    # nodes -- dual-interface zones, filled half colored by state
    vmin, vmax = (vlim if vlim is not None else (node_val.min(), node_val.max()))
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap_o = cm.get_cmap(cmap)
    for (x, y), v in zip(node_xy, node_val):
        _zone(ax, x, y, r, filled="bottom", face=cmap_o(norm(v)), z=4)
    if node_labels is not None:
        for (x, y), lab in zip(node_xy, node_labels):
            ax.annotate(lab, (x, y + r + 0.4 * r), ha="center", va="bottom",
                        fontsize=8, color="#222", zorder=7)
    ax.set_aspect("equal")
    sm = cm.ScalarMappable(norm=norm, cmap=cmap_o)
    sm.set_array([])
    cb = ax.figure.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label(node_cbar_label, fontsize=8)
    if title:
        ax.set_title(title, fontsize=10)
    # zones are patches, so the view does not autoscale -- set it from the nodes
    pad = 3 * r
    ax.set_xlim(node_xy[:, 0].min() - pad, node_xy[:, 0].max() + pad)
    ax.set_ylim(node_xy[:, 1].min() - pad, node_xy[:, 1].max() + pad)
    return sm


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
