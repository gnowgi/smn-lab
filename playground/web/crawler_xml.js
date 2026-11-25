// Port of smn_lab/crawler.py :: build_crawler_xml — emits the identical MJCF string.
// Python formats floats with repr() (60.0 -> "60.0"); pf() reproduces that. Ints stay ints.
const pf = x => (Number.isInteger(x) ? x.toFixed(1) : String(x)).replace(/^-?0\.0$/, m => m);
export function buildCrawlerXml({ n_seg = 3, h = 0.07, w = 0.025, seg_mass = 0.05, cmax = 2.5, z0 = 0.1,
  sense_off = 0.06, bend_limit_deg = 60.0, gravity_on = false, with_floor = false, with_walls = false,
  arena_half = 2.2, wall_h = 0.10, objects = null, touch = false, floor_friction = 0.0, free_root = false,
  joint_stiffness = 0.0, joint_damping = 0.02 } = {}) {
  const seglen = 2 * h;
  objects = objects || [];
  const segBody = k => {
    const isHead = k === 0;
    let joints;
    if (isHead && free_root) joints = '      <freejoint name="root"/>';
    else if (isHead) joints =
      '      <joint name="slide_x" type="slide" axis="1 0 0" damping="0.5"/>\n' +
      '      <joint name="slide_y" type="slide" axis="0 1 0" damping="0.5"/>\n' +
      '      <joint name="yaw" type="hinge" axis="0 0 1" damping="0.3"/>';
    else joints = `      <joint name="j${k}" type="hinge" axis="0 0 1" pos="${pf(h)} 0 0" ` +
      `range="${pf(-bend_limit_deg)} ${pf(bend_limit_deg)}" ` +
      `stiffness="${pf(joint_stiffness)}" springref="0" ` +
      `damping="${pf(joint_damping)}"/>`;
    const shade = Math.max(0.30, 0.62 - 0.08 * k);
    const color = isHead ? '0.20 0.45 0.90' : `0.30 ${shade.toFixed(2)} 0.78`;
    const geom = `      <geom name="seg${k}_geom" type="box" size="${pf(h)} ${pf(w)} ${pf(w)}" ` +
      `mass="${pf(seg_mass)}" friction="0 0 0" rgba="${color} 1"/>`;
    let sites = `      <site name="seg${k}_L" pos="0 ${pf(w + sense_off)} 0" size="0.006" rgba="0.85 0.25 0.25 1"/>\n` +
      `      <site name="seg${k}_R" pos="0 ${pf(-(w + sense_off))} 0" size="0.006" rgba="0.25 0.25 0.85 1"/>`;
    if (touch) sites += `\n      <site name="touch${k}" type="box" pos="0 0 0" ` +
      `size="${pf(h)} ${pf(w)} ${pf(w)}" rgba="0.95 0.55 0.10 0.18"/>`;
    if (isHead) sites += `\n      <site name="sense_L" pos="${pf(h)} ${pf(w + sense_off)} 0" size="0.009" rgba="1 0.35 0.35 1"/>\n` +
      `      <site name="sense_R" pos="${pf(h)} ${pf(-(w + sense_off))} 0" size="0.009" rgba="0.35 0.35 1 1"/>`;
    const child = k < n_seg - 1 ? `\n      <body name="seg${k + 1}" pos="${pf(-seglen)} 0 0">\n${segBody(k + 1)}\n      </body>` : '';
    return `${joints}\n${geom}\n${sites}${child}`;
  };
  const acts = [], sens = [];
  for (let k = 1; k < n_seg; k++) {
    acts.push(`    <motor name="m_j${k}_p" joint="j${k}" gear="0.05"  ctrlrange="0 ${pf(cmax)}"/>`);
    acts.push(`    <motor name="m_j${k}_n" joint="j${k}" gear="-0.05" ctrlrange="0 ${pf(cmax)}"/>`);
    sens.push(`    <jointpos name="ang_j${k}" joint="j${k}"/>`);
    sens.push(`    <jointvel name="vel_j${k}" joint="j${k}"/>`);
  }
  if (touch) for (let k = 0; k < n_seg; k++) sens.push(`    <touch name="touch${k}" site="touch${k}"/>`);
  const gravity = gravity_on ? '0 0 -9.81' : '0 0 0';
  const world = [];
  world.push('    <light pos="0 0 3" dir="0 0 -1"/>');
  if (with_floor) world.push(`    <geom name="floor" type="plane" size="4 4 0.1" ` +
    `friction="${pf(floor_friction)} 0 0" rgba="0.93 0.93 0.93 1"/>`);
  if (with_walls) {
    const W = [['wall_n', [0, arena_half, arena_half + 0.05, 0.05]], ['wall_s', [0, -arena_half, arena_half + 0.05, 0.05]],
               ['wall_e', [arena_half, 0, 0.05, arena_half + 0.05]], ['wall_w', [-arena_half, 0, 0.05, arena_half + 0.05]]];
    const fmt = v => (typeof v === 'object' ? pf(v.f) : String(v));   // ints that are literal 0 in Python
    for (const [nm, [px, py, sx, sy]] of W) {
      const P = (v, lit0) => (lit0 && v === 0 ? '0' : pf(v));
      world.push(`    <geom name="${nm}" type="box" pos="${P(px, true)} ${P(py, true)} ${pf(wall_h)}" ` +
        `size="${pf(sx)} ${pf(sy)} ${pf(wall_h)}" rgba="0.6 0.6 0.6 1"/>`);
    }
  }
  objects.forEach(([ox, oy, orr], i) => world.push(`    <geom name="obj${i}" type="cylinder" pos="${pf(ox)} ${pf(oy)} ${pf(wall_h)}" ` +
    `size="${pf(orr)} ${pf(wall_h)}" rgba="0.85 0.30 0.20 1"/>`));
  return `
<mujoco model="smn_crawler_a${n_seg}">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.002" gravity="${gravity}" integrator="implicitfast"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.7 0.7 0.7" ambient="0.4 0.4 0.4"/>
  </visual>

  <worldbody>
${world.join('\n')}
    <body name="seg0" pos="0 0 ${pf(z0)}">
${segBody(0)}
    </body>
  </worldbody>

  <actuator>
${acts.join('\n')}
  </actuator>

  <sensor>
${sens.join('\n')}
  </sensor>
</mujoco>
`;
}
