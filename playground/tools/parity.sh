#!/usr/bin/env bash
# Regenerate every bench reference, run the browser engine against it, and write web/models.json.
# Run from anywhere:  bash playground/tools/parity.sh      (needs: python3 + mujoco==4.0.1, node >= 20)
set -euo pipefail
PG="$(cd "$(dirname "$0")/.." && pwd)"; REPO="$(cd "$PG/.." && pwd)"; W="$PG/parity-out"; T="$PG/tools"
mkdir -p "$W"; cd "$PG"; [ -d node_modules ] || npm ci
python3 "$T/gen_models.py"              "$REPO" "$W/models_full.json"
python3 "$T/ref_xml_cases.py"           "$REPO" "$W/xml_cases.json"
python3 "$T/ref_baseline.py"            "$REPO" "$W/models_full.json" "$W/ref_baseline.json"
python3 "$T/ref_contact_reafference.py" "$REPO" "$W/ref_contact_reafference.json"
python3 "$T/ref_terrain.py"             "$REPO" "$W/ref_terrain.json"
python3 "$T/floors.py"                  "$REPO" "$W"
node "$T/parity_xml.mjs" "$W"; node "$T/parity_baseline.mjs" "$W"; node "$T/parity_contact.mjs" "$W"; node "$T/parity_terrain.mjs" "$W"
python3 "$T/build_data.py" "$W" "$PG/web/models.json"
