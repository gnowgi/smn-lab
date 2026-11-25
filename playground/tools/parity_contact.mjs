// Contact (walls, objects, touch skin, mid-run object insertion) and Q1 reafference vs ref_contact_reafference.py. Usage: node parity_contact.mjs WORK
import load from '@mujoco/mujoco'; import fs from 'fs';
import { CrawlerSim, ZoneWorld, ScalarField } from '../web/smn.js';
const W = process.argv[2], mj = await load(); const REF = JSON.parse(fs.readFileSync(`${W}/ref_contact_reafference.json`));
function run(hab, n, T, { src = null, objects = [], walls = true, touch = true, addAt = null, addObj = null, reaf = false } = {}) {
  const s = new CrawlerSim(mj, n, hab, { field: src ? new ScalarField([src]) : null, objects, walls, touch });
  const zw = reaf ? new ZoneWorld(s) : null; const out = { head: [], touch: [], res: [], dr: [] };
  for (let i = 0; i < Math.round(T / 0.002); i++) {
    if (addAt !== null && i === Math.round(addAt / 0.002)) s.setObjects([...s.opts.objects, addObj]);
    s.step();
    if (zw) { const f = zw.afterStep(); if (f) { out.res.push([...f.res]); out.dr.push([...f.dr]); } }
    if ((i + 1) % 250 === 0) { out.head.push(s.head()); out.touch.push(s.touchForces() || []); }
  }
  s.dispose(); return out;
}
const JS = {
  c1like_aq3: run('aquarium', 3, 40, { src: [1.9, 1.05, 1.0, 0.9], objects: [[0.78, 0.0, 0.12]] }),
  te8_rocks: run('terrarium', 8, 30, { objects: [[1.0, 0.1, 0.12], [1.6, -0.3, 0.2]], addAt: 10.0, addObj: [2.0, 0.2, 0.12] }),
  aq8_walls: run('aquarium', 8, 40, {}),
  reaf_aq6: run('aquarium', 6, 30, { src: [1.5, 0.8, 1.0, 0.9], reaf: true }),
};
const md = (a, b) => { let m = 0; a.forEach((r, i) => r.forEach((v, j) => m = Math.max(m, Math.abs(v - b[i][j])))); return m; };
const rows = Object.keys(REF).map(k => ({ run: k, head_dev: md(REF[k].head, JS[k].head).toExponential(2),
  touch_dev: md(REF[k].touch, JS[k].touch).toExponential(2), touch_max: Math.max(0, ...REF[k].touch.flat()).toFixed(3),
  res_dev: REF[k].res.length ? md(REF[k].res, JS[k].res).toExponential(2) : '–',
  res_scale: REF[k].res.length ? Math.max(...REF[k].dr.flat().map(Math.abs)).toExponential(2) : '–' }));
console.table(rows); fs.writeFileSync(`${W}/parity_contact.json`, JSON.stringify(rows, null, 1));
