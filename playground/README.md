# smn-playground

smn-lab bodies running **live in the browser** on MuJoCo's WebAssembly build. The playground is the
visible face of the bench, and it is meant to grow into an experimental bench in its own right for
embodied cognition and artificial life: blocks to assemble bodies, habitats to put them in, and
read-outs of what they construct.

Every creature on the page is the bench itself, not an animation:

- **Bodies.** The MJCF for each body comes from smn-lab's own builders. `build_crawler_xml` is ported
  to `web/crawler_xml.js`, and its output is byte-identical to the Python builder on 73 configurations.
- **Controllers and media.** The messaging beam, opponent board, anisotropic drag, ground friction, the
  medusa medium and Q1's per-zone reafference are ported line for line in `web/smn.js`. Each function
  names its Python original.
- **Parity.** `tools/parity.sh` reruns each configuration through the Python bench and through the
  browser engine, and records the deviations in `web/models.json`. The page shows them.

Status labels on the page follow the [status ledger](../docs/status.md). Anything that is not a bench
experiment is labelled as a playground extension.

## Layout

| path | what |
|---|---|
| `web/` | the page: `index.html`, `app.js` (UI and rendering), `smn.js` (bench port), `crawler_xml.js` (builder port), `models.json` (generated) |
| `tools/parity.sh` | regenerate bench references, run the browser engine against them, write `web/models.json` |
| `tools/build.sh` | assemble a deployable static site in `dist/` (page, pinned vendor files, CSP patch) |
| `tools/ref_*.py` | Python references; each calls smn-lab's own functions |
| `tools/parity_*.mjs` | the same runs through `web/smn.js` on MuJoCo WASM |
| `tools/floors.py` | the Python bench's own round-off floor (a 1e-15 perturbation), against which non-bit-level runs are judged |
| `tools/probes/` | one-off probes referred to in `LOG.md` |
| `patches/mujoco-js-noeval.patch` | a closure invoker for Embind when a page's CSP forbids `eval`/`new Function` |
| `LOG.md` | the record of steps, decisions and findings |

## Run

```bash
cd playground && npm ci              # @mujoco/mujoco 4.0.1, three 0.187.0 (pinned)
bash tools/parity.sh                 # needs python3 with mujoco==4.0.1 (same version as the WASM build)
bash tools/build.sh                  # -> playground/dist
python3 -m http.server -d dist 8000  # open http://localhost:8000
```

## Fidelity, as of the last parity run

| configuration | deviation from the Python bench | verdict |
|---|---|---|
| crawlers without contact (water, ground, with food) | ≤ 1.3e-15 m | bit-level |
| tank walls | 6.7e-16 m | bit-level |
| rocks and C1's object (contact) | 3.6e-5 to 1.1e-3 m | within the bench's own floor (7.7e-4 to 1.1e-3 m) |
| Q1 per-zone reafference residuals | 9.6e-15 on changes of ~1e-2 | round-off |
| uneven ground (extension) | 1.8e-15 m | bit-level |
| medusa (chaotic) | rises 0.065 at 24 s | bench's perturbed ensemble 0.058–0.064 (bench reports +0.061) |
