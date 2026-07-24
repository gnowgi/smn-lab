# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""Regression tests for the proprioceptive-entrainment term in MessagingBeam.

The first version of the term had two bugs that reached a docs page before review
caught them: swapped arctan2 arguments (the pull was cos(2*phase), nonzero under
perfect tracking) and no magnitude gate (a still body was yanked via arctan2(0,0)=0).
The invariant that would have caught both, promoted here to a test:

    ** under perfect tracking the entrainment pull must be identically zero. **

No error, no pull. Pure-numpy, no MuJoCo -- safe to run in CI.

Run:  python tests/test_entrainment.py     (or: pytest tests/)
"""
from __future__ import annotations
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smn_lab.control import MessagingBeam

AMP = 0.8


def _perfect_tracking_state(beam):
    """The joint state a perfectly-tracking body would present for beam.phase:
    theta = amp*sin(phase), theta_dot = amp*w*cos(phase)."""
    th = beam.amp * np.sin(beam.phase)
    thd = beam.amp * beam.w * np.cos(beam.phase)
    return th, thd


def test_inter_pull_vanishes_under_perfect_tracking():
    beam = MessagingBeam(n_joints=4, amp=AMP, freq=0.9, entrain=3.0,
                         entrain_mode="inter")
    th, thd = _perfect_tracking_state(beam)
    beam.command(0.002, theta=th, theta_dot=thd)
    assert np.max(np.abs(beam.ent)) < 1e-9, \
        f"inter-segmental pull must vanish under perfect tracking; got {beam.ent}"


def test_self_pull_vanishes_under_perfect_tracking():
    # the ablation form must also be zero under perfect tracking (its defect is the
    # constant brake under *servo lag*, not a nonzero pull at zero error).
    beam = MessagingBeam(n_joints=4, amp=AMP, freq=0.9, entrain=3.0,
                         entrain_mode="self")
    th, thd = _perfect_tracking_state(beam)
    beam.command(0.002, theta=th, theta_dot=thd)
    assert np.max(np.abs(beam.ent)) < 1e-9, \
        f"self pull must vanish under perfect tracking; got {beam.ent}"


def test_old_swapped_argument_form_would_fail():
    # Documents the original bug: arctan2(thd/w, th) makes the pull cos(2*phase),
    # which is NOT zero under perfect tracking. This is what the tests above guard.
    beam = MessagingBeam(n_joints=4, amp=AMP, freq=0.9)
    th, thd = _perfect_tracking_state(beam)
    buggy = np.sin(np.arctan2(thd / beam.w, th) - beam.phase)   # swapped args
    assert np.allclose(buggy, np.cos(2 * beam.phase), atol=1e-9)
    assert np.max(np.abs(buggy)) > 0.5, "the old form was a full-amplitude 2w drive"


def test_head_is_pacemaker():
    # inter-segmental: the most anterior joint has no anterior neighbour -> no pull.
    beam = MessagingBeam(n_joints=4, amp=AMP, freq=0.9, entrain=3.0,
                         entrain_mode="inter")
    # a lagged (non-tracking) body so the interior pulls are generically nonzero
    th = beam.amp * np.sin(beam.phase - 0.3)
    thd = beam.amp * beam.w * np.cos(beam.phase - 0.3)
    beam.command(0.002, theta=th, theta_dot=thd)
    assert abs(beam.ent[0]) < 1e-12, "head must be the free pacemaker (ent[0]==0)"
    assert np.max(np.abs(beam.ent[1:])) > 1e-3, "interior joints should feel a pull"


def test_entrain_zero_is_open_loop():
    # entrain=0 must leave phase evolution identical whether or not theta is passed.
    a = MessagingBeam(n_joints=4, amp=AMP, freq=0.9, entrain=0.0)
    b = MessagingBeam(n_joints=4, amp=AMP, freq=0.9, entrain=0.0)
    th, thd = _perfect_tracking_state(a)
    for _ in range(50):
        a.command(0.002, bias=0.1)
        b.command(0.002, bias=0.1, theta=th, theta_dot=thd)
    assert np.allclose(a.phase, b.phase), "entrain=0 must be bit-for-bit open loop"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"\nall {len(fns)} entrainment regression tests passed")
