// Contact-free crawlers and the medusa against ref_baseline.py. Usage: node parity_baseline.mjs WORK
import load from '@mujoco/mujoco'; import fs from 'fs';
import { CrawlerSim, MedusaSim, ScalarField } from '../web/smn.js';
const W = process.argv[2], mj = await load();
const M = JSON.parse(fs.readFileSync(`${W}/models_full.json`)), REF = JSON.parse(fs.readFileSync(`${W}/ref_baseline.json`));
function crawler(hab, n, T, src) {
  const s = new CrawlerSim(mj, n, hab, { field: src ? new ScalarField(src) : null }), out = [];
  for (let i = 0; i < Math.round(T / 0.002); i++) { s.step(); if ((i + 1) % 250 === 0) out.push(s.head()); }
  s.dispose(); return out;
}
function medusa(T) {
  const s = new MedusaSim(mj, M.medusa.tent_6), out = [];
  for (let i = 0; i < Math.round(T / 0.001); i++) { s.step(); if ((i + 1) % 500 === 0) out.push(s.com()); }
  s.dispose(); return out;
}
const JS = { aq3_chemo: crawler('aquarium', 3, 30, [[1.6, 0.9, 1.0, 0.9]]), aq8: crawler('aquarium', 8, 15), te8: crawler('terrarium', 8, 15),
  te8_chemo: crawler('terrarium', 8, 40, [[1.5, 1.2, 1.0, 0.9]]), te12: crawler('terrarium', 12, 15), medusa: medusa(12) };
const rows = Object.keys(REF).map(k => { const a = REF[k], b = JS[k]; let mx = 0;
  a.forEach((r, i) => r.forEach((v, j) => mx = Math.max(mx, Math.abs(v - b[i][j]))));
  return { run: k, samples: a.length, max_abs_dev: mx.toExponential(2), path_scale: Math.hypot(...a.at(-1).map((v, j) => v - a[0][j])).toFixed(3) }; });
console.table(rows); fs.writeFileSync(`${W}/parity_baseline.json`, JSON.stringify(rows, null, 1));
