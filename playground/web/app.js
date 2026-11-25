// smn-playground — live smn-lab bodies on MuJoCo WASM, rendered with three.js (or a flat 2-D view)
import * as THREE from 'three';
import { OrbitControls } from './OrbitControls.js';
import loadMujoco from './mujoco.js';
import { CrawlerSim, MedusaSim, ScalarField, ZoneWorld, Terrain } from './smn.js';

const $ = s => document.querySelector(s);
const C1_OBJECT = [0.78, 0.0, 0.12];                  // experiments/c1_touch.py OBJECT
const state = { plan: 'chain', n: 3, habitat: 'aquarium', split: false, speed: 1, paused: false,
  tool: null, src: null, objects: [C1_OBJECT.slice()], walls: true, chem: true, touch: true, uneven: false };
// uneven ground preset: rough (×3) and slick (×1/3) patches, mostly along the crawler's first heading
const L3 = Math.log(3);
const TERRAIN = new Terrain([[0.45, 0.25, L3], [1.25, -0.15, -L3], [1.9, 0.45, L3], [1.6, -1.0, L3], [0.6, -1.2, -L3],
  [-0.4, 0.9, L3], [-1.3, -0.3, -L3], [0.2, 1.7, -L3], [-1.6, 1.4, L3], [1.0, 1.4, L3], [-0.9, -1.5, L3], [1.9, -1.8, -L3]]);
const SRC_AMP = 1.0, SRC_SIG = 0.9;                     // experiments/c0_crawler.py FIELD
const H = 0.07, W = 0.025, ARENA = 2.2, WALL_H = 0.10;   // build_crawler_xml defaults
const ROCK_R = 0.12;
const BELLY = 0.1 - W;                                  // z0 - w: where the segment's underside sits
let mj = null, DATA = null, views = [];

// ------------------------------------------------------------------ helpers -------------
const v3 = (a, i) => new THREE.Vector3(a[i], a[i + 2], -a[i + 1]);      // mj z-up -> three y-up
function quatFromXmat(xm, b, q) {
  const k = 9 * b, r = i => xm[k + i];
  return q.setFromRotationMatrix(new THREE.Matrix4().set(r(0), r(2), -r(1), 0, r(6), r(8), -r(7), 0, -r(3), -r(5), r(4), 0, 0, 0, 0, 1));
}
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function noiseTex(base, specks, n = 512, seed = 7) {
  const c = document.createElement('canvas'); c.width = c.height = n;
  const g = c.getContext('2d'), R = rng(seed);
  g.fillStyle = base; g.fillRect(0, 0, n, n);
  for (const [col, count, rmax] of specks) { g.fillStyle = col;
    for (let i = 0; i < count; i++) { g.globalAlpha = 0.25 + 0.6 * R(); g.beginPath(); g.arc(R() * n, R() * n, 0.6 + R() * rmax, 0, 7); g.fill(); } }
  g.globalAlpha = 1;
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(30, 30);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
let GLOW = null;
function terrainTex() {                    // paint the friction field itself: dark = rough, pale = slick
  const n = 512, c = document.createElement('canvas'); c.width = c.height = n; const g = c.getContext('2d'), img = g.createImageData(n, n), half = ARENA + 0.6, R = rng(3);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = -half + (i + 0.5) / n * 2 * half, y = half - (j + 0.5) / n * 2 * half, e = Math.log(TERRAIN.scale(x, y)) / Math.log(3), k = 4 * (j * n + i), grain = (R() - 0.5) * 18;
    const a = Math.min(1, Math.abs(e)); const col = e > 0 ? [92, 70, 42] : [232, 214, 170];
    img.data[k] = col[0] + grain; img.data[k + 1] = col[1] + grain; img.data[k + 2] = col[2] + grain; img.data[k + 3] = 235 * a;
  }
  g.putImageData(img, 0, 0); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function glowTex() {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'), gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, 'rgba(255,120,80,0.55)'); gr.addColorStop(0.35, 'rgba(255,120,80,0.22)'); gr.addColorStop(1, 'rgba(255,120,80,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const pure = () => !state.walls && state.objects.length === 0;

// ------------------------------------------------------------------ labels --------------
const ST = { ok: 'var(--ok)', prov: 'var(--prov)' };
function labelFor(plan, hab, n) {
  if (plan === 'bell') return { t: 'Medusa · experiments/medusa_swim.py', st: 'prov',
    s: 'Provisional: on the bench, not yet independently audited.',
    b: 'A dome of 49 point masses and 90 pull-only muscle units. The ring units fire a fast power stroke and elastic links recover the bell slowly. In the pond\'s quadratic drag that asymmetry nets a slow rise.' };
  const world = pure() ? '' : ' Walls and rocks are build_crawler_xml\'s contact geometry, as in C1, but without C1\'s halt: the body keeps pushing against them.';
  const steer = state.src && state.chem;
  if (hab === 'aquarium') {
    const ok = n === 3 && pure();
    return { t: `${n === 3 ? 'C0 · minimal axial crawler' : `Axial crawler, ${n} blocks`} · experiments/c0_crawler.py`, st: ok ? 'ok' : 'prov',
      s: ok ? 'Consistency-checked on the bench ledger (C0).' : (n === 3 ? 'Provisional: C0 is consistency-checked in an empty world. This world adds contact.' : 'Provisional: the same bench code is consistency-checked at 3 blocks (C0) in an empty world.'),
      b: 'Viscous medium: an explicit drag law, 14× stiffer sideways than along the body (the C. elegans recipe), with gravity off.' + world };
  }
  return { t: `Ground crawler, ${n} blocks · experiments/gravity_locomotion.py`, st: 'prov',
    s: 'Provisional: a bench experiment, not yet on the audit ledger.' + (steer ? ' Food steering adds C0\'s chemotaxis to this body. That pairing has not been run as a bench experiment.' : ''),
    b: 'Ground: weight-set dry friction, with the belly gripping 20× harder sideways than along the body (Hu et al. 2009). The body slides in a plane.' + world
      + (state.uneven ? ' Uneven ground is a playground extension, not on the bench: the same friction law with its coefficient varying from place to place, from 1/3 to 3 times the bench value.' : '') };
}

// ------------------------------------------------------------------ the agent's-frame panel ---
const COLS = 160;                                       // 160 windows x 0.25 s = 40 s of history
class SelfPanel {
  constructor(view) {
    this.v = view;
    this.el = document.createElement('div'); this.el.className = 'card selfp';
    this.el.innerHTML = `<div class="sp-h"><h3></h3><span class="sp-st"></span></div><div class="fig sp-fig"><canvas></canvas></div>`;
    $('#selfPanels').append(this.el);
    this.el.querySelector('h3').textContent = (view.hab === 'aquarium' ? 'Aquarium' : 'Terrarium') + ': what the creature registers, in its own frame';
    this.cv = this.el.querySelector('canvas'); this.ctx = this.cv.getContext('2d');
    this.ro = new ResizeObserver(() => this.size()); this.ro.observe(this.el.querySelector('.sp-fig'));
    this.reset();
  }
  size() { const f = this.el.querySelector('.sp-fig'), dpr = Math.min(devicePixelRatio, 2);
    this.W = f.clientWidth; this.H = f.clientHeight; this.cv.width = this.W * dpr; this.cv.height = this.H * dpr; this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0); this.draw(); }
  reset() {
    const n = state.plan === 'chain' ? state.n : 1;
    this.env = null; this.bands = ['dr', 'res', 'touch', 'bend'].map(() => { const c = document.createElement('canvas'); c.width = COLS; c.height = n; const g = c.getContext('2d'); g.fillStyle = '#10181a'; g.fillRect(0, 0, COLS, n); return c; });
    this.S = 1e-4; this.Tmax = 0.3; this.last = null; this.touch = null; this.draw();
  }
  push(frame, touch, bendEnv) {
    this.last = frame; this.touch = touch; this.env = bendEnv;
    const n = frame.r.length;
    const med = frame.dr.map(Math.abs).sort((a, b) => a - b)[frame.dr.length >> 1];   // robust scale: a jump saturates
    this.S = Math.max(1e-6, this.S + 0.05 * (3 * med - this.S));
    const tm = touch ? Math.max(...touch) : 0; this.Tmax = Math.max(this.Tmax * 0.999, tm, 0.3);
    const col = (g, k, rgb) => { g.fillStyle = rgb; g.fillRect(COLS - 1, k, 1, 1); };
    const sig = (v, S) => { const a = Math.min(1, Math.sqrt(Math.abs(v) / S)); return v >= 0 ? `rgb(${16 + 239 * a | 0},${24 + 82 * a | 0},${26 + 51 * a | 0})` : `rgb(${16 + 43 * a | 0},${24 + 87 * a | 0},${26 + 190 * a | 0})`; };
    this.bands.forEach((c, b) => {
      const g = c.getContext('2d'); g.drawImage(c, -1, 0);
      for (let k = 0; k < n; k++) {
        if (b < 2) col(g, k, state.chem ? sig(b === 0 ? frame.dr[k] : frame.res[k], this.S) : '#2a3436');
        else if (b === 2) { const a = touch && state.touch ? Math.min(1, touch[k] / this.Tmax) : 0; col(g, k, state.touch ? `rgb(${16 + 239 * a | 0},${24 + 160 * a | 0},${26 + 20 * a | 0})` : '#2a3436'); }
        else { const a = k > 0 && bendEnv ? Math.min(1, bendEnv[k - 1] / 0.8) : 0; col(g, k, k > 0 ? `rgb(${16 + 70 * a | 0},${24 + 190 * a | 0},${26 + 130 * a | 0})` : '#10181a'); }
      }
    });
    this.draw();
  }
  draw() {
    const g = this.ctx, Wd = this.W, Hd = this.H; if (!g || !Wd) return;
    const dark = matchMedia('(prefers-color-scheme: dark)').matches && document.documentElement.dataset.theme !== 'light' || document.documentElement.dataset.theme === 'dark';
    g.clearRect(0, 0, Wd, Hd);
    const ink = dark ? '#e6ecea' : '#14201f', mute = dark ? '#97a6a3' : '#5b6967';
    if (state.plan !== 'chain') {
      g.fillStyle = mute; g.font = '14px Inter, sans-serif';
      wrapText(g, 'The bell\'s world-model is measured on the bench by decoding a hidden source from its tentacle tips\' self-caused motion. That decoder runs offline, so it is not shown live here.', 16, 30, Wd - 32, 20); return;
    }
    const n = state.n, narrow = Wd < 560, bodyW = narrow ? 92 : 150, top = 26, bottom = Hd - 10, rowH = (bottom - top) / n;
    // --- the body as its own frame: a column of zones, head at the top
    g.font = '12px Inter, sans-serif'; g.fillStyle = mute; g.fillText(narrow ? 'body' : 'its body (head on top)', 8, 15);
    const cx = narrow ? 46 : 70, f = this.last, t = this.touch;
    const rmax = f ? Math.max(1e-6, ...f.r) : 1;
    g.strokeStyle = mute; g.lineWidth = 2; g.beginPath(); g.moveTo(cx, top + rowH / 2); g.lineTo(cx, top + rowH * (n - 0.5)); g.stroke();
    for (let k = 0; k < n; k++) {
      const y = top + rowH * (k + 0.5), rr = Math.min(11, rowH * 0.36);
      const lev = f && state.chem ? f.r[k] / rmax : 0;
      for (const sx of [-1, 1]) { g.beginPath(); g.arc(cx + sx * (rr + 12), y, Math.max(3, rr * 0.45), 0, 7);
        if (state.chem) { g.fillStyle = `rgba(${sx < 0 ? '216,69,60' : '59,111,216'},${0.25 + 0.75 * lev})`; g.fill(); } else { g.strokeStyle = mute; g.lineWidth = 1; g.stroke(); } }
      const wv = f && state.chem ? Math.min(1, Math.sqrt(Math.abs(f.res[k]) / this.S)) : 0;
      g.beginPath(); g.arc(cx, y, rr, 0, 7); g.fillStyle = k === 0 ? '#2f5fd0' : '#5a7fbf'; g.fill();
      if (wv > 0.02) { g.beginPath(); g.arc(cx, y, rr, 0, 7); g.fillStyle = `rgba(255,106,77,${wv})`; g.fill(); }
      if (state.touch && t && t[k] > 1e-3) { g.beginPath(); g.arc(cx, y, rr + 4, 0, 7); g.strokeStyle = '#ffb020'; g.lineWidth = 1 + 4 * Math.min(1, t[k] / this.Tmax); g.stroke(); }
    }
    // --- three kymograph bands, newest at the right
    const x0 = bodyW, bw = (Wd - x0 - 10) / 4 - 9, labels = ['felt change', 'caused by the world', 'touch', 'bend it achieves'];
    this.bands.forEach((c, b) => {
      const x = x0 + b * (bw + 12);
      g.fillStyle = ink; g.font = `600 ${narrow ? 11 : 12}px Inter, sans-serif`; g.fillText(narrow ? ['felt', 'world', 'touch', 'bend'][b] : labels[b], x, 15);
      g.imageSmoothingEnabled = false; g.drawImage(c, x, top, bw, bottom - top);
      const off = (b < 2 && !state.chem) || (b === 2 && !state.touch);
      if (off) { g.fillStyle = 'rgba(16,24,26,0.75)'; g.fillRect(x, top, bw, bottom - top); g.fillStyle = '#c9d3d1'; g.font = '12px Inter, sans-serif'; wrapText(g, b < 2 ? 'No chemical sensors mounted: this body has no chemical world.' : 'No touch skin mounted: contact exists but is not registered.', x + 8, top + 22, bw - 16, 16); }
    });
    g.fillStyle = mute; g.font = '11px Inter, sans-serif'; g.fillText('← 40 s', x0, Hd - 1); g.textAlign = 'right'; g.fillText('now', Wd - 12, Hd - 1); g.textAlign = 'left';
  }
  status(text) { this.el.querySelector('.sp-st').textContent = text; }
  dispose() { this.ro.disconnect(); this.el.remove(); }
}
function wrapText(g, s, x, y, w, lh) { let line = ''; for (const word of s.split(' ')) { const t = line ? line + ' ' + word : word; if (g.measureText(t).width > w && line) { g.fillText(line, x, y); y += lh; line = word; } else line = t; } g.fillText(line, x, y); }

// ------------------------------------------------------------------ a view --------------
class View {
  constructor(hab) {
    this.hab = hab;
    this.el = document.createElement('div'); this.el.className = 'view';
    this.canvas = document.createElement('canvas'); this.el.append(this.canvas);
    this.el.insertAdjacentHTML('beforeend',
      `<div class="hname">${hab === 'aquarium' ? 'Aquarium · water' : 'Terrarium · ground'}</div>
       <div class="hint"></div><div class="label"></div>
       <div class="read"><span>time<b class="r-t">0.0 s</b></span><span class="r-ak">distance<b class="r-d">0.00 m</b></span><span class="r-bk">speed<b class="r-v">–</b></span></div>`);
    $('#stage').append(this.el);
    try {
      this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, failIfMajorPerformanceCaveat: false });
      this.gl = true;
    } catch (err) {                                     // e.g. Firefox with WebGL blocked: fall back to 2-D
      this.gl = false; this.canvas.remove(); this.canvas = document.createElement('canvas'); this.el.prepend(this.canvas);
      this.ctx = this.canvas.getContext('2d'); this.zoom = 1;
      showGlNote(err);
    }
    if (this.gl) {
      this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      this.renderer.shadowMap.enabled = true; this.renderer.shadowMap.type = THREE.PCFShadowMap;
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(42, 1, 0.01, 200);
      this.controls = new OrbitControls(this.camera, this.canvas);
      this.controls.enableDamping = true; this.controls.maxPolarAngle = Math.PI * 0.49;
      this.controls.minDistance = 0.25; this.controls.maxDistance = 12;
      this.world();
    } else this.canvas.addEventListener('wheel', e => { e.preventDefault(); this.zoom *= e.deltaY > 0 ? 0.9 : 1.1; }, { passive: false });
    this.ro = new ResizeObserver(() => this.resize()); this.ro.observe(this.el);
    this.panel = new SelfPanel(this);
    this.bindClick(); this.build();
  }
  resize() {
    const w = this.el.clientWidth, h = this.el.clientHeight; if (!w || !h) return;
    if (this.gl) { this.renderer.setSize(w, h, false); this.camera.aspect = w / h; this.camera.updateProjectionMatrix(); }
    else { const dpr = Math.min(devicePixelRatio, 2); this.canvas.width = w * dpr; this.canvas.height = h * dpr; this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0); this.cw = w; this.ch = h; }
  }
  world() {
    const S = this.scene, aq = this.hab === 'aquarium';
    const sky = new THREE.Color(aq ? 0x0e5463 : 0xd8c7a2);
    S.background = sky; S.fog = new THREE.FogExp2(sky, aq ? 0.13 : 0.08);
    S.add(new THREE.HemisphereLight(aq ? 0xbfefff : 0xfff2d8, aq ? 0x0a2a30 : 0x6b5434, aq ? 1.5 : 1.7));
    const sun = new THREE.DirectionalLight(aq ? 0xd8fbff : 0xffe7bf, aq ? 1.6 : 2.4);
    sun.position.set(2, 6, 3); sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024);
    Object.assign(sun.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3, near: 0.5, far: 20 });
    S.add(sun, sun.target); this.sun = sun;
    const tex = aq ? noiseTex('#4f6d64', [['#2c403b', 2600, 2.2], ['#7f9b8e', 1200, 1.6], ['#a8b79a', 300, 1.2]])
                   : noiseTex('#a07c4c', [['#7a5a33', 3200, 2.0], ['#c39f6b', 1600, 1.6], ['#5d7a3a', 260, 2.4]]);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; S.add(floor); this.floor = floor;
    // scenery: only OUTSIDE the arena, so nothing in reach looks solid without being solid
    const R = rng(aq ? 11 : 23), M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
    const stones = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(1, 0), new THREE.MeshStandardMaterial({ color: aq ? 0x5e7f78 : 0x8d8172, roughness: 0.95, flatShading: true }), 220);
    for (let i = 0; i < 220; i++) { const r = 3.3 + R() * 16, a = R() * 6.283, s = 0.05 + R() * R() * (aq ? 0.4 : 0.3);
      q.setFromEuler(e.set(R() * 3, R() * 3, R() * 3)); M.compose(new THREE.Vector3(Math.cos(a) * r, s * 0.35, Math.sin(a) * r), q, new THREE.Vector3(s, s * 0.6, s * 0.9)); stones.setMatrixAt(i, M); }
    stones.receiveShadow = true;
    const tuft = new THREE.InstancedMesh(new THREE.ConeGeometry(0.035, 1, 5), new THREE.MeshStandardMaterial({ color: aq ? 0x2f7d5a : 0x6f8f3a, roughness: 0.8 }), aq ? 160 : 220);
    for (let i = 0; i < tuft.count; i++) { const r = 3.3 + R() * 14, a = R() * 6.283, h = aq ? 0.4 + R() * 1.4 : 0.06 + R() * 0.18;
      q.setFromEuler(e.set((R() - 0.5) * 0.4, 0, (R() - 0.5) * 0.4)); M.compose(new THREE.Vector3(Math.cos(a) * r, h / 2, Math.sin(a) * r), q, new THREE.Vector3(1, h, 1)); tuft.setMatrixAt(i, M); }
    this.decor = new THREE.Group(); this.decor.add(stones, tuft); S.add(this.decor);
    if (aq) { const N = 260, g = new THREE.BufferGeometry(), p = new Float32Array(3 * N);
      for (let i = 0; i < N; i++) { p[3 * i] = (R() - 0.5) * 8; p[3 * i + 1] = R() * 3; p[3 * i + 2] = (R() - 0.5) * 8; }
      g.setAttribute('position', new THREE.BufferAttribute(p, 3));
      this.bubbles = new THREE.Points(g, new THREE.PointsMaterial({ color: 0xd9fbff, size: 0.018, transparent: true, opacity: 0.55 })); S.add(this.bubbles); }
    GLOW ??= glowTex();
    this.halo = new THREE.Mesh(new THREE.PlaneGeometry(6 * SRC_SIG, 6 * SRC_SIG), new THREE.MeshBasicMaterial({ map: GLOW, transparent: true, depthWrite: false }));
    this.halo.rotation.x = -Math.PI / 2; this.halo.position.y = 0.004;
    this.pellet = new THREE.Mesh(new THREE.IcosahedronGeometry(0.045, 1), new THREE.MeshStandardMaterial({ color: 0xff6a4d, emissive: 0xff3a1a, emissiveIntensity: 0.6 }));
    this.food = new THREE.Group(); this.food.add(this.halo, this.pellet); this.food.visible = false; S.add(this.food);
    this.ground = new THREE.Mesh(new THREE.PlaneGeometry(2 * ARENA + 1.2, 2 * ARENA + 1.2), new THREE.MeshStandardMaterial({ map: terrainTex(), transparent: true, roughness: 1, depthWrite: false }));
    this.ground.rotation.x = -Math.PI / 2; this.ground.receiveShadow = true; this.ground.visible = false; S.add(this.ground);
    this.solid = new THREE.Group(); S.add(this.solid);                  // walls + rocks: the contact geometry
    this.rockMat = new THREE.MeshStandardMaterial({ map: noiseTex(aq ? '#6d7f78' : '#8c7a66', [['#4b5753', 900, 3], ['#a9b3ad', 500, 2]], 256, 5), roughness: 0.9 });
    this.rockMat.map.repeat.set(2, 1);
    this.wallMat = aq ? new THREE.MeshPhysicalMaterial({ color: 0xcfefff, transparent: true, opacity: 0.28, roughness: 0.05 })
                      : new THREE.MeshStandardMaterial({ color: 0x7b5a3a, roughness: 0.9 });
  }
  solids() {                                          // draw exactly what build_crawler_xml collides with
    if (!this.gl) return;
    this.solid.children.forEach(o => o.geometry.dispose()); this.solid.clear();
    if (state.plan !== 'chain') return;
    if (state.walls) for (const [px, py, sx, sy] of [[0, ARENA, ARENA + 0.05, 0.05], [0, -ARENA, ARENA + 0.05, 0.05], [ARENA, 0, 0.05, ARENA + 0.05], [-ARENA, 0, 0.05, ARENA + 0.05]]) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(2 * sx, 2 * WALL_H, 2 * sy), this.wallMat); m.position.set(px, WALL_H, -py); m.castShadow = m.receiveShadow = true; this.solid.add(m); }
    for (const [x, y, r] of state.objects) {
      const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 2 * WALL_H, 28), this.rockMat); m.position.set(x, WALL_H, -y); m.castShadow = m.receiveShadow = true; this.solid.add(m); }
  }
  bindClick() {
    const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -0.1);
    let down = null;
    this.el.addEventListener('pointerdown', e => { down = [e.clientX, e.clientY]; });
    this.el.addEventListener('pointerup', e => {
      if (e.target !== this.canvas || !down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
      if (!state.tool || state.plan !== 'chain') return;
      const r = this.canvas.getBoundingClientRect(); let xy;
      if (this.gl) { ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
        ray.setFromCamera(ndc, this.camera); const p = new THREE.Vector3(); if (!ray.ray.intersectPlane(plane, p)) return; xy = [p.x, -p.z]; }
      else xy = this.unproject(e.clientX - r.left, e.clientY - r.top);
      if (state.tool === 'food') setSource(xy); else addRock(xy, this);
    });
  }
  build() {
    this.disposeSim();
    this.el.querySelector('.void')?.remove();
    this.acc = 0; this.panel.reset(); this.hist = null; this.winMax = null;
    const chain = state.plan === 'chain';
    this.el.querySelector('.r-ak').firstChild.textContent = chain ? 'distance' : 'rise';
    this.el.querySelector('.r-bk').style.display = chain ? '' : 'none';
    this.hint();
    if (this.gl) { this.body = new THREE.Group(); this.scene.add(this.body); this.solids(); }
    if (!chain && this.hab === 'terrarium') {
      this.sim = null; this.panel.status('');
      this.el.insertAdjacentHTML('beforeend', `<div class="void"><div><h3>Not on the bench</h3>smn-lab has no ground model for the bell body plan. A medusa on land would not swim, and this page only shows what the bench has actually built.</div></div>`);
      this.label({ t: 'Medusa on ground', st: 'prov', s: 'Not simulated.', b: '' }); return;
    }
    if (this.gl) { const fy = !chain ? -0.9 : this.hab === 'terrarium' ? BELLY : 0;
      this.floor.position.y = fy; this.decor.position.y = fy; this.food.position.y = 0; this.halo.position.y = fy + 0.004;
      this.ground.visible = chain && this.hab === 'terrarium' && state.uneven; this.ground.position.y = fy + 0.002; }
    if (chain) {
      const field = state.src && state.chem ? new ScalarField([[state.src[0], state.src[1], SRC_AMP, SRC_SIG]]) : null;
      this.sim = new CrawlerSim(mj, state.n, this.hab, { field, objects: state.objects, walls: state.walls, touch: true, terrain: this.hab === 'terrarium' && state.uneven ? TERRAIN : null });
      this.zw = new ZoneWorld(this.sim);
      if (this.gl) this.makeCrawler();
    } else { this.sim = new MedusaSim(mj, DATA.medusa); this.zw = null; if (this.gl) this.makeMedusa(); }
    this.start = this.center().clone();
    if (this.gl) {
      const c = this.start, L = chain ? 0.14 * state.n : 0.7;
      this.controls.target.copy(c);
      this.camera.position.copy(c).add(chain ? new THREE.Vector3(-0.55 * L - 0.5, 0.55 * L + 0.6, 0.85 * L + 0.8) : new THREE.Vector3(0.2, 0.35, 2.1));
      this.sync();
    }
    this.relabel();
  }
  relabel() { this.label(labelFor(state.plan, this.hab, state.n)); }
  statusText(f) {
    if (f.learning) return 'Calibrating its own motion (first 8 s)…';
    if (!this.sim.terrain) return '';
    const x = this.sim.d.xpos, b = this.sim.seg[0], sc = this.sim.terrain.scale(x[3 * b], x[3 * b + 1]);
    return `Ground under the head: ${sc > 1.15 ? 'rough' : sc < 0.87 ? 'slick' : 'ordinary'}, ×${sc.toFixed(2)} friction`;
  }
  hint() { const t = state.tool === 'food' ? '. Click the floor to drop or move food.' : state.tool === 'rock' ? '. Click the floor to place a rock.' : '';
    this.el.querySelector('.hint').textContent = (this.gl ? 'Drag to orbit, scroll to zoom' : 'Flat view: scroll to zoom') + t; }
  label(L) {
    const el = this.el.querySelector('.label'); el.style.setProperty('--st', ST[L.st]); el.innerHTML = '';
    for (const [c, txt] of [['t', L.t], ['s', L.s], ['', L.b]]) { const d = document.createElement('div'); if (c) d.className = c; d.textContent = txt; el.append(d); }
  }
  makeCrawler() {
    const n = state.n, m = this.sim.m;
    const segGeo = new THREE.CapsuleGeometry(W, 2 * H - 2 * W, 6, 14); segGeo.rotateZ(Math.PI / 2);
    this.segs = [...Array(n).keys()].map(k => { const mesh = new THREE.Mesh(segGeo, new THREE.MeshStandardMaterial({ color: k === 0 ? 0x2f5fd0 : new THREE.Color().setHSL(0.6, 0.45, Math.max(0.36, 0.56 - 0.025 * k)), roughness: 0.45, emissive: 0x000000 }));
      mesh.castShadow = true; this.body.add(mesh); return mesh; });
    const musGeo = new THREE.CylinderGeometry(0.0075, 0.0075, 1, 8);
    this.mus = [];
    for (let k = 1; k < n; k++) for (const side of [-1, 1]) {
      const mesh = new THREE.Mesh(musGeo, new THREE.MeshStandardMaterial({ color: 0x5a2a28, roughness: 0.6 }));
      this.body.add(mesh); this.mus.push({ mesh, k, side, p: side < 0 }); }
    const sg = new THREE.SphereGeometry(1, 12, 8);
    this.matL = new THREE.MeshStandardMaterial({ color: 0xd8453c, emissive: 0x5a0f0a }); this.matR = new THREE.MeshStandardMaterial({ color: 0x3b6fd8, emissive: 0x0a1a5a });
    this.sens = [];
    for (let k = 0; k < n; k++) for (const [nm, mat] of [[`seg${k}_L`, this.matL], [`seg${k}_R`, this.matR]]) { const s = new THREE.Mesh(sg, mat); s.scale.setScalar(0.011); this.body.add(s); this.sens.push([nm, s, k]); }
    for (const [nm, mat] of [['sense_L', this.matL], ['sense_R', this.matR]]) { const s = new THREE.Mesh(sg, mat); s.scale.setScalar(0.017); this.body.add(s); this.sens.push([nm, s, 0]); }
    this.stalk = new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(6 * (2 * n + 2)), 3)), new THREE.LineBasicMaterial({ color: 0x9fb2b0, transparent: true, opacity: 0.7 }));
    this.body.add(this.stalk);
  }
  makeMedusa() {
    const sp = DATA.medusa, N = sp.pos.length;
    this.nodes = new THREE.InstancedMesh(new THREE.SphereGeometry(0.016, 10, 8), new THREE.MeshStandardMaterial({ color: 0xf3e6ff, emissive: 0x3a2050 }), N); this.body.add(this.nodes);
    const idx = [], rid = (r, c) => 1 + r * 8 + (c % 8);
    for (let c = 0; c < 8; c++) idx.push(0, rid(0, c + 1), rid(0, c));
    for (let r = 0; r < 2; r++) for (let c = 0; c < 8; c++) idx.push(rid(r, c), rid(r, c + 1), rid(r + 1, c + 1), rid(r, c), rid(r + 1, c + 1), rid(r + 1, c));
    const bg = new THREE.BufferGeometry(); bg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(3 * N), 3)); bg.setIndex(idx);
    this.bell = new THREE.Mesh(bg, new THREE.MeshPhysicalMaterial({ color: 0xffc9e6, transparent: true, opacity: 0.42, side: THREE.DoubleSide, roughness: 0.25, emissive: 0x401530 })); this.body.add(this.bell);
    this.medE = sp.edges.filter((_, i) => sp.edge_kind[i] !== 'brace'); this.medK = sp.edge_kind.filter(k => k !== 'brace');
    const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6 * this.medE.length), 3)); lg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(6 * this.medE.length), 3));
    this.medL = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ vertexColors: true })); this.body.add(this.medL);
  }
  center() {
    const x = this.sim.d.xpos;
    if (state.plan === 'chain') { const c = new THREE.Vector3(); for (const b of this.sim.seg) c.add(v3(x, 3 * b)); return c.divideScalar(this.sim.seg.length); }
    const c = this.sim.com(); return new THREE.Vector3(c[0], c[2], -c[1]);
  }
  sync() {
    const s = this.sim, d = s.d, x = d.xpos, xm = d.xmat;
    if (state.plan === 'chain') {
      const seg = s.seg, ctrl = d.ctrl, sx = d.site_xpos, cmax = s.P.cmax, touch = s.touchForces();
      seg.forEach((b, k) => { const m = this.segs[k]; m.position.copy(v3(x, 3 * b)); quatFromXmat(xm, b, m.quaternion);
        const tf = state.touch ? Math.min(1, touch[k] / 0.5) : 0; m.material.emissive.setRGB(0.8 * tf, 0.45 * tf, 0); });
      const up = new THREE.Vector3(0, 1, 0);
      for (const u of this.mus) {
        const a = seg[u.k - 1], b = seg[u.k];
        const ya = new THREE.Vector3(xm[9 * a + 1], xm[9 * a + 7], -xm[9 * a + 4]), yb = new THREE.Vector3(xm[9 * b + 1], xm[9 * b + 7], -xm[9 * b + 4]);
        const off = (W + 0.008) * u.side, p0 = v3(x, 3 * a).addScaledVector(ya, off), p1 = v3(x, 3 * b).addScaledVector(yb, off), dv = p1.clone().sub(p0), len = dv.length();
        u.mesh.position.copy(p0).addScaledVector(dv, 0.5); u.mesh.quaternion.setFromUnitVectors(up, dv.normalize()); u.mesh.scale.set(1, len * 0.62, 1);
        const a01 = Math.min(1, ctrl[u.p ? s.ap[u.k - 1] : s.an[u.k - 1]] / cmax);
        u.mesh.material.color.setRGB(0.35 + 0.65 * a01, 0.17 + 0.2 * a01, 0.16 + 0.08 * a01); u.mesh.material.emissive.setRGB(0.9 * a01, 0.25 * a01, 0.1 * a01);
      }
      const SP = this.stalk.geometry.attributes.position.array;
      if (this.siteFor !== s.m) { this.siteIds = this.sens.map(([nm]) => s.m.site(nm).id); this.siteFor = s.m; }
      this.sens.forEach(([nm, sph, k], i) => { const id = this.siteIds[i]; sph.position.copy(v3(sx, 3 * id)); sph.visible = state.chem;
        const c = this.segs[k].position; SP.set(state.chem ? [c.x, c.y, c.z, sph.position.x, sph.position.y, sph.position.z] : [0, 0, 0, 0, 0, 0], 6 * i); });
      this.stalk.geometry.attributes.position.needsUpdate = true;
    } else {
      const bid = s.bid, M = new THREE.Matrix4(), P = this.bell.geometry.attributes.position.array;
      bid.forEach((b, i) => { const p = v3(x, 3 * b); P[3 * i] = p.x; P[3 * i + 1] = p.y; P[3 * i + 2] = p.z; M.makeTranslation(p.x, p.y, p.z); this.nodes.setMatrixAt(i, M); });
      this.nodes.instanceMatrix.needsUpdate = true; this.bell.geometry.attributes.position.needsUpdate = true; this.bell.geometry.computeVertexNormals();
      const L = this.medL.geometry.attributes.position.array, C = this.medL.geometry.attributes.color.array, on = s.stroke;
      this.medE.forEach(([a, b], i) => { for (let j = 0; j < 3; j++) { L[6 * i + j] = P[3 * a + j]; L[6 * i + 3 + j] = P[3 * b + j]; }
        const k = this.medK[i], col = k === 'coronal' ? (on ? [1, 0.38, 0.25] : [0.75, 0.45, 0.6]) : k === 'tentacle' ? [0.95, 0.8, 0.95] : [0.7, 0.62, 0.8]; C.set(col, 6 * i); C.set(col, 6 * i + 3); });
      this.medL.geometry.attributes.position.needsUpdate = true; this.medL.geometry.attributes.color.needsUpdate = true;
    }
  }
  tick(dt) {
    if (this.sim && !state.paused) {
      this.acc += Math.min(dt, 0.05) * state.speed;
      let k = 0; const h = this.sim.dt;
      while (this.acc >= h && k < 2000) {
        this.sim.step(); this.acc -= h; k++;
        if (this.zw) {
          const th = this.sim.bends(); this.winMax ??= th.map(() => 0); th.forEach((v, j) => this.winMax[j] = Math.max(this.winMax[j], Math.abs(v)));
          const f = this.zw.afterStep();
          if (f) {
            (this.hist ??= []).push(this.winMax); if (this.hist.length > 5) this.hist.shift(); this.winMax = th.map(() => 0);
            const env = this.hist[0].map((_, j) => Math.max(...this.hist.map(h => h[j])));        // bend envelope over ~1.25 s
            this.panel.push(f, this.sim.touchForces(), env); this.panel.status(this.statusText(f));
          }
        }
      }
      if (this.gl) this.sync();
    }
    if (!this.sim) { if (this.gl) { this.controls.update(); this.renderer.render(this.scene, this.camera); } return; }
    const c = this.center(), t = this.sim.t, chain = state.plan === 'chain';
    const dist = chain ? Math.hypot(c.x - this.start.x, c.z - this.start.z) : c.y - this.start.y;
    this.el.querySelector('.r-t').textContent = `${t.toFixed(1)} s`;
    this.el.querySelector('.r-d').textContent = `${dist.toFixed(chain ? 2 : 3)} m`;
    if (chain) this.el.querySelector('.r-v').textContent = t > 2 ? `${(dist / (0.14 * state.n) / t * 60).toFixed(1)} body lengths/min` : '–';
    if (!this.gl) { this.flat(c); return; }
    const T = this.controls.target, nt = T.clone().lerp(c, 0.06);
    this.camera.position.add(nt.clone().sub(T)); T.copy(nt);
    this.sun.position.set(c.x + 2, 6, c.z + 3); this.sun.target.position.copy(c);
    if (this.bubbles) { const p = this.bubbles.geometry.attributes.position.array;
      for (let i = 0; i < p.length; i += 3) { p[i + 1] += dt * (0.12 + (i % 7) * 0.02); if (p[i + 1] > 3) { p[i + 1] = 0; p[i] = c.x + (Math.random() - 0.5) * 8; p[i + 2] = c.z + (Math.random() - 0.5) * 8; } }
      this.bubbles.geometry.attributes.position.needsUpdate = true; }
    if (this.food.visible) this.pellet.position.y = 0.06 + 0.012 * Math.sin(performance.now() / 400);
    this.controls.update(); this.renderer.render(this.scene, this.camera);
  }
  // ---- flat 2-D renderer (top view for chains, side view for the bell)
  view2d(c) { const chain = state.plan === 'chain', L = chain ? 0.14 * state.n : 0.8;
    const k = Math.min(this.cw, this.ch) / (L * 2.6 + 0.6) * this.zoom; this.cam = chain ? [c.x, -c.z] : [c.x, c.y]; this.k = k; }
  proj(x, y) { return [this.cw / 2 + (x - this.cam[0]) * this.k, this.ch / 2 - (y - this.cam[1]) * this.k]; }
  unproject(px, py) { return [this.cam[0] + (px - this.cw / 2) / this.k, this.cam[1] - (py - this.ch / 2) / this.k]; }
  flat(c) {
    const g = this.ctx, aq = this.hab === 'aquarium', s = this.sim, d = s.d, x = d.xpos, xm = d.xmat; if (!this.cw) return;
    this.view2d(c);
    g.fillStyle = aq ? '#0e5463' : '#b8955f'; g.fillRect(0, 0, this.cw, this.ch);
    g.strokeStyle = aq ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)'; g.lineWidth = 1;
    for (let gx = Math.floor(this.unproject(0, 0)[0] / 0.25) * 0.25; gx < this.unproject(this.cw, 0)[0]; gx += 0.25) { const [px] = this.proj(gx, 0); g.beginPath(); g.moveTo(px, 0); g.lineTo(px, this.ch); g.stroke(); }
    for (let gy = Math.floor(this.unproject(0, this.ch)[1] / 0.25) * 0.25; gy < this.unproject(0, 0)[1]; gy += 0.25) { const [, py] = this.proj(0, gy); g.beginPath(); g.moveTo(0, py); g.lineTo(this.cw, py); g.stroke(); }
    if (state.plan !== 'chain') {                       // the bell, side view (x, z)
      const sp = DATA.medusa, P = s.bid.map(b => [x[3 * b], x[3 * b + 2]]);
      sp.edges.forEach(([a, b], i) => { const k = sp.edge_kind[i]; if (k === 'brace') return; g.strokeStyle = k === 'coronal' ? (s.stroke ? '#ff6040' : '#d8a0c8') : '#f0d8f0'; g.lineWidth = 1.5;
        const p = this.proj(...P[a]), q = this.proj(...P[b]); g.beginPath(); g.moveTo(...p); g.lineTo(...q); g.stroke(); });
      return;
    }
    if (this.sim.terrain) for (const [bx, by, a] of this.sim.terrain.blobs) { const [px, py] = this.proj(bx, by), r = 2.2 * this.sim.terrain.sig * this.k, gr = g.createRadialGradient(px, py, 0, px, py, r);
      const c = a > 0 ? '92,70,42' : '232,214,170'; gr.addColorStop(0, `rgba(${c},0.85)`); gr.addColorStop(1, `rgba(${c},0)`); g.fillStyle = gr; g.fillRect(px - r, py - r, 2 * r, 2 * r); }
    if (state.src) { const [px, py] = this.proj(...state.src), r = 3 * SRC_SIG * this.k, gr = g.createRadialGradient(px, py, 0, px, py, r);
      gr.addColorStop(0, 'rgba(255,120,80,0.5)'); gr.addColorStop(1, 'rgba(255,120,80,0)'); g.fillStyle = gr; g.fillRect(px - r, py - r, 2 * r, 2 * r);
      g.fillStyle = '#ff6a4d'; g.beginPath(); g.arc(px, py, 6, 0, 7); g.fill(); }
    g.fillStyle = aq ? 'rgba(207,239,255,0.5)' : '#7b5a3a';
    if (state.walls) for (const [px, py, sx, sy] of [[0, ARENA, ARENA + 0.05, 0.05], [0, -ARENA, ARENA + 0.05, 0.05], [ARENA, 0, 0.05, ARENA + 0.05], [-ARENA, 0, 0.05, ARENA + 0.05]]) {
      const [a, b] = this.proj(px - sx, py + sy); g.fillRect(a, b, 2 * sx * this.k, 2 * sy * this.k); }
    g.fillStyle = aq ? '#6d7f78' : '#8c7a66';
    for (const [ox, oy, r] of state.objects) { const [px, py] = this.proj(ox, oy); g.beginPath(); g.arc(px, py, r * this.k, 0, 7); g.fill(); }
    const touch = s.touchForces();
    s.seg.forEach((b, k) => { const [px, py] = this.proj(x[3 * b], x[3 * b + 1]), yaw = Math.atan2(xm[9 * b + 3], xm[9 * b]);
      g.save(); g.translate(px, py); g.rotate(-yaw); g.fillStyle = k === 0 ? '#2f5fd0' : '#6f8fc8';
      if (state.touch && touch[k] > 1e-3) { g.shadowColor = '#ffb020'; g.shadowBlur = 12; }
      g.beginPath(); g.roundRect(-H * this.k, -W * this.k, 2 * H * this.k, 2 * W * this.k, W * this.k); g.fill(); g.restore(); });
    if (state.chem) for (let k = 0; k < s.n; k++) for (const [id, col] of [[s.zL[k], '#d8453c'], [s.zR[k], '#3b6fd8']]) {
      const [px, py] = this.proj(d.site_xpos[3 * id], d.site_xpos[3 * id + 1]); g.fillStyle = col; g.beginPath(); g.arc(px, py, 2.5, 0, 7); g.fill(); }
  }
  disposeSim() {
    if (this.zw) this.zw.dispose(); this.zw = null;
    if (this.sim) this.sim.dispose(); this.sim = null;
    if (this.gl && this.body) { this.scene.remove(this.body); this.body.traverse(o => { o.geometry?.dispose(); o.material?.dispose?.(); }); this.body = null; }
  }
  dispose() { this.disposeSim(); this.ro.disconnect(); this.panel.dispose();
    if (this.gl) { this.controls.dispose(); this.renderer.dispose(); this.renderer.forceContextLoss(); } this.el.remove(); }
}
function showGlNote(err) {
  const n = $('#glnote'); n.hidden = false;
  n.querySelector('span').textContent = String(err && err.message || err).replace(/\.+$/, '');
}

// ------------------------------------------------------------------ app -----------------
function setSource(xy) {
  state.src = xy;
  for (const v of views) {
    if (v.gl) { v.food.visible = !!xy; if (xy) v.food.position.set(xy[0], 0, -xy[1]); }
    if (v.sim && state.plan === 'chain') { v.sim.setField(xy && state.chem ? new ScalarField([[xy[0], xy[1], SRC_AMP, SRC_SIG]]) : null); v.relabel(); }
  }
}
function addRock(xy, view) {
  if (state.objects.length >= 12) return flash('Twelve rocks is the limit.');
  const s = view.sim, near = s.seg.some(b => Math.hypot(s.d.xpos[3 * b] - xy[0], s.d.xpos[3 * b + 1] - xy[1]) < ROCK_R + 0.12);
  if (near) return flash('Too close to the body: a rock cannot be placed inside it.');
  if (Math.abs(xy[0]) > ARENA - 0.1 || Math.abs(xy[1]) > ARENA - 0.1) return flash('Place rocks inside the tank.');
  state.objects.push([+xy[0].toFixed(3), +xy[1].toFixed(3), ROCK_R]); applyWorld();
}
function applyWorld() {                       // recompile the MJCF with the new contact geometry, keep the state
  for (const v of views) { if (v.sim && state.plan === 'chain') v.sim.setWorld({ objects: state.objects, walls: state.walls }); v.solids(); v.relabel(); }
}
function flash(msg) { const f = $('#flash'); f.textContent = msg; f.hidden = false; clearTimeout(flash.t); flash.t = setTimeout(() => f.hidden = true, 2600); }
function rebuildViews() {
  views.forEach(v => v.dispose());
  const habs = state.split ? ['aquarium', 'terrarium'] : [state.habitat];
  $('#stage').classList.toggle('split', state.split); $('#selfPanels').classList.toggle('two', state.split);
  views = habs.map(h => new View(h)); views[0].el.classList.add('first'); setSource(state.src);
}
function rebuildSims() { views.forEach(v => v.build()); setSource(state.src); }
function press(ids, on) { ids.forEach(id => $(id).setAttribute('aria-pressed', String(id === on))); }
function tray() { $('#tray').innerHTML = '<i></i>'.repeat(state.n); $('#count').textContent = `${state.n} blocks`; $('#minus').disabled = state.n <= 3; $('#plus').disabled = state.n >= 12; }
function bodyUI() {
  const chain = state.plan === 'chain';
  $('#chainCtl').style.display = chain ? '' : 'none';
  $('#bodyNote').textContent = chain
    ? 'Three blocks is the fewest that can travel: with two joints the stroke is not reversible. Each change rebuilds the body with smn-lab\'s own builder.'
    : 'The bell uses the same pull-only muscle unit. Ring units squeeze, spoke units hold the dome, and tentacle units curl. Its size is fixed at the bench\'s configuration.';
}
function setTool(t) {
  state.tool = state.tool === t ? null : t;
  $('#t-food').setAttribute('aria-pressed', String(state.tool === 'food')); $('#t-rock').setAttribute('aria-pressed', String(state.tool === 'rock'));
  views.forEach(v => v.hint());
}
function wire() {
  const habIds = ['#h-aquarium', '#h-terrarium', '#h-split'];
  $('#h-aquarium').onclick = () => { state.habitat = 'aquarium'; state.split = false; press(habIds, '#h-aquarium'); rebuildViews(); };
  $('#h-terrarium').onclick = () => { state.habitat = 'terrarium'; state.split = false; press(habIds, '#h-terrarium'); rebuildViews(); };
  $('#h-split').onclick = () => { state.split = true; press(habIds, '#h-split'); rebuildViews(); };
  $('#sp1').onclick = () => { state.speed = 1; press(['#sp1', '#sp4'], '#sp1'); };
  $('#sp4').onclick = () => { state.speed = 4; press(['#sp1', '#sp4'], '#sp4'); };
  $('#pause').onclick = () => { state.paused = !state.paused; $('#pause').setAttribute('aria-pressed', String(state.paused)); $('#pause').textContent = state.paused ? 'Play' : 'Pause'; };
  $('#reset').onclick = () => rebuildSims();
  $('#minus').onclick = () => { if (state.n > 3) { state.n--; tray(); rebuildSims(); } };
  $('#plus').onclick = () => { if (state.n < 12) { state.n++; tray(); rebuildSims(); } };
  $('#b-chain').onclick = () => { state.plan = 'chain'; press(['#b-chain', '#b-bell'], '#b-chain'); bodyUI(); rebuildSims(); };
  $('#b-bell').onclick = () => { state.plan = 'bell'; state.speed = 4; press(['#sp1', '#sp4'], '#sp4'); press(['#b-chain', '#b-bell'], '#b-bell'); bodyUI(); setSource(null); rebuildSims(); };
  $('#t-food').onclick = () => setTool('food');
  $('#t-rock').onclick = () => setTool('rock');
  $('#t-clear').onclick = () => { state.objects = []; setSource(null); applyWorld(); };
  $('#m-chem').onclick = () => { state.chem = !state.chem; $('#m-chem').setAttribute('aria-pressed', String(state.chem)); setSource(state.src); views.forEach(v => v.panel.reset()); };
  $('#m-touch').onclick = () => { state.touch = !state.touch; $('#m-touch').setAttribute('aria-pressed', String(state.touch)); views.forEach(v => v.panel.reset()); };
  $('#m-ground').onclick = () => { state.uneven = !state.uneven; $('#m-ground').setAttribute('aria-pressed', String(state.uneven)); rebuildSims(); };
  $('#m-walls').onclick = () => { state.walls = !state.walls; $('#m-walls').setAttribute('aria-pressed', String(state.walls)); applyWorld(); };
}
function parityTable() {
  $('#sha').textContent = DATA.commit;
  const rows = [
    ['3 blocks, water, with food', 'c0_crawler.py', DATA.parity[0].max_abs_dev, 'bit-level', 'ok'],
    ['8 blocks, water', 'c0_crawler.py settings', DATA.parity[1].max_abs_dev, 'bit-level', 'prov'],
    ['8 blocks, ground', 'gravity_locomotion.py', DATA.parity[2].max_abs_dev, 'bit-level', 'prov'],
    ['12 blocks, ground', 'gravity_locomotion.py', DATA.parity[4].max_abs_dev, 'bit-level', 'prov'],
    ['8 blocks, water, tank walls', 'build_crawler_xml walls', DATA.parity2[2].head_dev, 'bit-level', 'prov'],
    ['3 blocks, water, C1\'s object, food', 'c1_touch.py world, no halt', DATA.parity2[0].head_dev, 'within the bench\'s own 7.7 × 10⁻⁴', 'prov'],
    ['8 blocks, ground, rocks (one added at 10 s)', 'gravity_locomotion.py + objects', DATA.parity2[1].head_dev, 'within the bench\'s own 1.1 × 10⁻³', 'prov'],
    ['Agent\'s-frame world (6 blocks, water, food)', 'Q1 per-zone reafference (Q1 itself is consistency-checked)', DATA.parity2[3].res_dev, 'to round-off, on changes of ~10⁻²', 'prov'],
    ['Bell, water', 'medusa_swim.py', DATA.parity[5].max_abs_dev, 'within the bench\'s own chaos', 'prov'],
  ];
  const tb = $('#parity tbody');
  for (const [cfg, src, dev, verdict, st] of rows) {
    const tr = document.createElement('tr');
    [cfg, src, `${dev}`, verdict].forEach((c, i) => { const td = document.createElement('td'); td.textContent = c; if (i === 2) td.className = 'n'; tr.append(td); });
    const td = document.createElement('td'), p = document.createElement('span'); p.className = 'pill'; p.textContent = st === 'ok' ? 'Consistency-checked' : 'Provisional';
    p.style.background = ST[st]; td.append(p); tr.append(td); tb.append(tr);
  }
}

(async () => {
  wire(); tray(); bodyUI();
  try {
    [mj, DATA] = await Promise.all([loadMujoco(), fetch('./models.json').then(r => r.json())]);
    parityTable(); rebuildViews();
    let last = performance.now();
    const loop = now => { const dt = (now - last) / 1000; last = now; views.forEach(v => v.tick(dt)); requestAnimationFrame(loop); };
    requestAnimationFrame(loop);
  } catch (err) {
    $('#stage').insertAdjacentHTML('beforeend', `<div class="void" style="background:#0d4b57"><div><h3>The physics engine could not start</h3><span id="errmsg"></span></div></div>`);
    $('#errmsg').textContent = String(err && err.message || err); console.error(err);
  }
})();
