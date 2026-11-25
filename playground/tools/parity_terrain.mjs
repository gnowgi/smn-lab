// Uneven ground (playground extension) vs ref_terrain.py, which calls the bench's apply_ground_friction per segment.
// Usage: node parity_terrain.mjs WORK
import load from '@mujoco/mujoco'; import fs from 'fs'; import { CrawlerSim, Terrain } from '../web/smn.js';
const W = process.argv[2], mj = await load(); const { R, blobs } = JSON.parse(fs.readFileSync(`${W}/ref_terrain.json`)); const rows = [];
for (const [k, uneven] of [['te8_uneven', true], ['te8_even', false]]) {
  const s = new CrawlerSim(mj, 8, 'terrarium', { terrain: uneven ? new Terrain(blobs) : null }), h = [], b = [];
  for (let i = 0; i < 15000; i++) { s.step(); if ((i + 1) % 250 === 0) { h.push(s.head()); b.push(s.bends()); } }
  const md = (A, B) => Math.max(...A.flatMap((r, i) => r.map((v, j) => Math.abs(v - B[i][j]))));
  rows.push({ run: k, head_dev: md(R[k].head, h).toExponential(2), bend_dev: md(R[k].bend, b).toExponential(2) }); s.dispose();
}
console.table(rows); fs.writeFileSync(`${W}/parity_terrain.json`, JSON.stringify(rows, null, 1));
