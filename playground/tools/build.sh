#!/usr/bin/env bash
# Assemble a deployable static site in playground/dist: page + pinned vendor files + the CSP patch.
set -euo pipefail
PG="$(cd "$(dirname "$0")/.." && pwd)"; D="$PG/dist"; cd "$PG"; [ -d node_modules ] || npm ci
rm -rf "$D"; mkdir -p "$D"
cp web/index.html web/app.js web/smn.js web/crawler_xml.js web/models.json "$D/"
cp node_modules/@mujoco/mujoco/mujoco.js node_modules/@mujoco/mujoco/mujoco.wasm "$D/"
cp node_modules/three/build/three.module.js node_modules/three/build/three.core.js node_modules/three/examples/jsm/controls/OrbitControls.js "$D/"
( cd "$D" && patch -p1 < "$PG/patches/mujoco-js-noeval.patch" )
echo "built $D  — serve it with any static server, e.g.  python3 -m http.server -d $D"
