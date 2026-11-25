# SPDX-License-Identifier: GPL-3.0-or-later
# smn-playground parity tooling. Run from the repository root via playground/tools/parity.sh.
import json, sys
sys.path.insert(0, sys.argv[1])
from smn_lab.crawler import build_crawler_xml
cases = []
objs = [(0.78, 0.0, 0.12), (1.3, -0.45, 0.12), (-1.0, 1.25, 0.2), (2.0, 2.0, 0.12)]
for n in (3, 7, 12):
    for hab in ("aq", "te"):
        for walls in (False, True):
            for touch in (False, True):
                for no in (0, 1, 4):
                    kw = dict(n_seg=n, with_walls=walls, touch=touch, objects=objs[:no])
                    if hab == "te": kw.update(gravity_on=False, joint_damping=0.03, bend_limit_deg=50.0)
                    cases.append(dict(kw=kw, xml=build_crawler_xml(**kw)))
cases.append(dict(kw=dict(n_seg=3, gravity_on=True, with_floor=True, with_walls=True, touch=True, objects=[(0.78, 0.0, 0.12)]),
                  xml=build_crawler_xml(n_seg=3, gravity_on=True, with_floor=True, with_walls=True, touch=True, objects=[(0.78, 0.0, 0.12)])))
json.dump(cases, open(sys.argv[2], "w")); print(len(cases), "cases")
