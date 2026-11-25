# SPDX-License-Identifier: GPL-3.0-or-later
"""Assemble web/models.json: the medusa spec (from smn-lab's own builder) + every parity result.
Usage: python3 build_data.py WORK OUT_JSON"""
import json, sys
W, OUT = sys.argv[1], sys.argv[2]
M = json.load(open(f"{W}/models_full.json")); F = json.load(open(f"{W}/floors.json"))
out = dict(commit=M["smn_lab_commit"], medusa=M["medusa"]["tent_6"],
           parity=json.load(open(f"{W}/parity_baseline.json")), parity2=json.load(open(f"{W}/parity_contact.json")),
           parity3=json.load(open(f"{W}/parity_terrain.json")), xml_parity=json.load(open(f"{W}/parity_xml.json")),
           self_floor={"te8_rocks": F["te8_rocks"], "c1like_aq3": F["c1like_aq3"], "medusa_z24": F["medusa_z24"]})
json.dump(out, open(OUT, "w")); print("wrote", OUT)
