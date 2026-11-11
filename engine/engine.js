'use strict';
// Theo6k reel engine: draws every frame of a 9:16 football story reel on a canvas.
// The page exposes window.loadSpec(spec), window.getInfo() and window.frame(t).

const W = 1080, H = 1920, FOC = 1150, CY = H * 0.56, NEAR = 0.6;
const cv = document.getElementById('c');
let ctx = cv.getContext('2d');
const S = { spec: null, beats: [], dur: 0, events: [], accent: '#3FE0C5' };

// ---------- math ----------
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const eOut = t => 1 - Math.pow(1 - t, 3);
const eBack = t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const pr = (t, a, d) => clamp((t - a) / d, 0, 1);
function rng(seed) {
  let s = (Math.imul(seed | 0, 2654435761) >>> 0) || 1;
  return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
}
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const nrm = a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const lerp3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
function hex(c) {
  c = c.replace('#', '');
  if (c.length === 3) c = c.split('').map(x => x + x).join('');
  const n = parseInt(c, 16);
  return [n >> 16 & 255, n >> 8 & 255, n & 255];
}
function rgba(c, a = 1) { const [r, g, b] = hex(c); return `rgba(${r},${g},${b},${a})`; }
function shade(c, k) {
  const f = v => Math.round(clamp(k < 0 ? v * (1 + k) : v + (255 - v) * k, 0, 255));
  const [r, g, b] = hex(c);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
function rrect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
function font(weight, size, family = 'Inter', spacing = '0px') {
  ctx.font = `${weight} ${size}px ${family}`;
  ctx.letterSpacing = spacing;
}

// ---------- camera ----------
const CAMS = {
  aerial: { pos: [0, 115, -170], tgt: [0, 0, -6] },
  high: { pos: [0, 50, -72], tgt: [0, 0, 22] },
  stand: { pos: [0, 14, -70], tgt: [0, 3, 12] },
  pitch: { pos: [0, 2.6, -26], tgt: [0, 2.3, 20] },
  player: { pos: [0, 1.0, -4.6], tgt: [0, 1.0, 12] },
  side: { pos: [-75, 24, 0], tgt: [0, 0, 0] },
};
function camPreset(c) {
  if (!c) return CAMS.high;
  if (typeof c === 'string') return CAMS[c] || CAMS.high;
  return c;
}
function mkCam(pos, tgt) {
  const f = nrm(sub(tgt, pos));
  const r = nrm(cross([0, 1, 0], f));
  const u = cross(f, r);
  return { pos, f, r, u };
}
function toCam(c, p) { const d = sub(p, c.pos); return [dot(d, c.r), dot(d, c.u), dot(d, c.f)]; }
function proj(q) { return [W / 2 + FOC * q[0] / q[2], CY - FOC * q[1] / q[2], q[2]]; }

function camInBeat(i, lt) {
  const b = S.beats[i];
  if (b.orbit) {   // cinematic orbit: the camera circles a point at a constant distance (degrees: 0 = in front, looking toward +z)
    const o = b.orbit, k = ease(pr(lt, 0, o.dur || b.move || 3)), a = (lerp(o.from, o.to, k)) * Math.PI / 180, c = o.center;
    const pos = [c[0] + Math.sin(a) * o.r, o.h != null ? lerp(o.h, o.h2 != null ? o.h2 : o.h, k) : c[1], c[2] - Math.cos(a) * o.r];
    return { pos, tgt: [c[0], c[1], c[2]] };
  }
  if (b.camFollow) {   // broadcast camera following the ball of the beat's pass web (smoothed so it glides)
    const it = webCard(b), F = b.camFollow;
    if (it) { const ct = b.start + lt - it.start; let sx = 0, sz = 0; for (let j = 0; j < 8; j++) { const p = webBall(it.obj, ct - j * 0.12).p; sx += p[0]; sz += p[2]; }
      const bx = sx / 8, bz = sz / 8; return { pos: [bx + (F.side || 0), F.h || 9, bz - (F.back || 14)], tgt: [bx, 0.5, bz + (F.ahead || 3)] }; }
  }
  const base = camBase(i, lt);
  if (!b._follow) return base;
  // hype: once a goal-bound shot is struck, the camera swings after the ball (and creeps toward it), then holds on the net
  const F = b._follow, u = F.slowmo === false ? pr(lt, F.t, F.dur) : ballSlow(pr(lt, F.t, F.dur)), P = F.pts;
  const bw = [0, 1, 2].map(j => (1 - u) ** 2 * P[0][j] + 2 * (1 - u) * u * P[1][j] + u * u * P[2][j]);
  const w = (F.amount || 0.6) * ease(pr(lt, F.t - 0.1, 0.4));
  if (w <= 0) return base;
  const tgt = lerp3(base.tgt, bw, w), d = sub(bw, base.pos);
  return { pos: [base.pos[0] + d[0] * 0.12 * w, base.pos[1] + d[1] * 0.05 * w, base.pos[2] + d[2] * 0.12 * w], tgt };
}
function camBase(i, lt) {
  const b = S.beats[i];
  const to = camPreset(b.camera);
  const from = (i === 0 || b.cut) ? camPreset(b.camFrom || b.camera) : camEnd(i - 1);
  const md = b.move != null ? b.move : Math.min(2.4, b.dur * 0.8);
  const k = b.moveEase === 'linear' ? pr(lt, 0, md) : ease(pr(lt, 0, md));   // linear: tracking a runner at constant speed
  let pos = lerp3(from.pos, to.pos, k);
  const tgt = lerp3(from.tgt, to.tgt, k);
  const dr = (b.drift != null ? b.drift : 0.012) * lt;
  const d = sub(tgt, pos);
  pos = [pos[0] + d[0] * dr, pos[1] + d[1] * dr, pos[2] + d[2] * dr];
  // gentle handheld sway on absolute time, so it stays continuous across beats
  const T = b.start + lt, amp = Math.hypot(d[0], d[1], d[2]) * 0.006 * (b.sway != null ? b.sway : 1);
  pos = [pos[0] + Math.sin(T * 0.45) * amp * 3, pos[1] + Math.sin(T * 0.31 + 1) * amp * 1.5, pos[2]];
  return { pos, tgt };
}
function camEnd(i) { return camInBeat(i, S.beats[i].dur); }

// ---------- 3D drawing ----------
function clipNear(q) {
  const out = [];
  for (let i = 0; i < q.length; i++) {
    const a = q[i], b = q[(i + 1) % q.length];
    const ain = a[2] >= NEAR, bin = b[2] >= NEAR;
    if (ain) out.push(a);
    if (ain !== bin) {
      const t = (NEAR - a[2]) / (b[2] - a[2]);
      out.push([lerp(a[0], b[0], t), lerp(a[1], b[1], t), NEAR]);
    }
  }
  return out;
}
function fillPoly3(cam, pts, fill) {
  const q = clipNear(pts.map(p => toCam(cam, p)));
  if (q.length < 3) return;
  ctx.beginPath();
  q.forEach((c, i) => { const s = proj(c); i ? ctx.lineTo(s[0], s[1]) : ctx.moveTo(s[0], s[1]); });
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
}
function line3(cam, a, b, w = 0.13, col = 'rgba(255,255,255,0.9)') {
  const len = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
  const n = Math.max(1, Math.ceil(len / 5));
  ctx.strokeStyle = col;
  ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    let p = toCam(cam, lerp3(a, b, i / n)), q = toCam(cam, lerp3(a, b, (i + 1) / n));
    if (p[2] < NEAR && q[2] < NEAR) continue;
    if (p[2] < NEAR) { const t = (NEAR - p[2]) / (q[2] - p[2]); p = [lerp(p[0], q[0], t), lerp(p[1], q[1], t), NEAR]; }
    else if (q[2] < NEAR) { const t = (NEAR - q[2]) / (p[2] - q[2]); q = [lerp(q[0], p[0], t), lerp(q[1], p[1], t), NEAR]; }
    const s1 = proj(p), s2 = proj(q);
    ctx.lineWidth = clamp(FOC * w / ((p[2] + q[2]) / 2), 0.7, 16);
    ctx.beginPath(); ctx.moveTo(s1[0], s1[1]); ctx.lineTo(s2[0], s2[1]); ctx.stroke();
  }
}
function path3(cam, pts, w, col) { for (let i = 0; i < pts.length - 1; i++) line3(cam, pts[i], pts[i + 1], w, col); }
function arcPts(cx, cz, r, a0, a1, n = 40) {
  const out = [];
  for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); out.push([cx + Math.cos(a) * r, 0, cz + Math.sin(a) * r]); }
  return out;
}

// ---------- stadium world ----------
const worldCache = new Map();
function buildWorld(scene) {
  const key = JSON.stringify(scene);
  if (worldCache.has(key)) return worldCache.get(key);
  const R = rng(scene.seed || 7);
  const crowd = scene.crowd || ['#2b4bbf', '#ffffff'];
  const N = 168, a = 41, b = 59.5, n = 4, D = 34, h0 = 1.2, h1 = 27;
  const ring = [];
  for (let i = 0; i < N; i++) {
    const th = i / N * Math.PI * 2, c = Math.cos(th), s = Math.sin(th);
    const x = a * Math.sign(c) * Math.pow(Math.abs(c), 2 / n);
    const z = b * Math.sign(s) * Math.pow(Math.abs(s), 2 / n);
    let nx = Math.sign(x) * Math.pow(Math.abs(x) / a, n - 1) / a;
    let nz = Math.sign(z) * Math.pow(Math.abs(z) / b, n - 1) / b;
    const l = Math.hypot(nx, nz) || 1;
    ring.push({ x, z, nx: nx / l, nz: nz / l });
  }
  const segs = [];
  for (let i = 0; i < N; i++) {
    const p = ring[i], q = ring[(i + 1) % N];
    const in0 = [p.x, h0, p.z], in1 = [q.x, h0, q.z];
    const out0 = [p.x + p.nx * D, h1, p.z + p.nz * D], out1 = [q.x + q.nx * D, h1, q.z + q.nz * D];
    const dots = [];
    const rows = 30, len = Math.hypot(q.x - p.x, q.z - p.z), cols = Math.max(1, Math.round(len / 0.8));
    for (let r = rows - 1; r >= 0; r--) {
      const v = (r + 0.5) / rows;
      const A = lerp3(in0, out0, v), B = lerp3(in1, out1, v);
      for (let c = 0; c < cols; c++) {
        if (R() < 0.16) continue;
        const P = lerp3(A, B, (c + 0.3 + R() * 0.4) / cols);
        P[1] += 0.35;
        const roll = R();
        const col = roll < 0.05 ? '#e9ecf2' : roll < 0.1 ? '#59627a' : crowd[Math.floor(R() * crowd.length)];
        dots.push({ p: P, col, fl: R() < 0.025 ? R() * 6.28 : -1, sz: 0.5 + R() * 0.25 });
      }
    }
    const mid = lerp3(lerp3(in0, in1, 0.5), lerp3(out0, out1, 0.5), 0.5);
    segs.push({ quad: [in0, in1, out1, out0], dots, mid, top: [out0, out1], light: i % 8 === 0 });
  }
  const w = { segs };
  worldCache.set(key, w);
  return w;
}

function drawSky(scene) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#07090e');
  g.addColorStop(0.42, '#121722');
  g.addColorStop(1, '#1b2231');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
}

function drawPitch(cam, scene) {
  const g1 = scene.grass1 || '#3c8a3d', g2 = scene.grass2 || '#469a45';
  fillPoly3(cam, [[-400, 0, -400], [400, 0, -400], [400, 0, 400], [-400, 0, 400]], '#0f131b');
  fillPoly3(cam, [[-46, 0, -64], [46, 0, -64], [46, 0, 64], [-46, 0, 64]], '#2c6a2f');
  for (let k = 0; k < 18; k++) {
    const z0 = -58.5 + k * 6.5;
    fillPoly3(cam, [[-40, 0, z0], [40, 0, z0], [40, 0, z0 + 6.5], [-40, 0, z0 + 6.5]], k % 2 ? g1 : g2);
  }
  const L = 'rgba(255,255,255,0.9)', w = 0.14;
  path3(cam, [[-34, 0, -52.5], [34, 0, -52.5], [34, 0, 52.5], [-34, 0, 52.5], [-34, 0, -52.5]], w, L);
  line3(cam, [-34, 0, 0], [34, 0, 0], w, L);
  path3(cam, arcPts(0, 0, 9.15, 0, Math.PI * 2, 48), w, L);
  for (const s of [-1, 1]) {
    const e = 52.5 * s;
    path3(cam, [[-20.16, 0, e], [-20.16, 0, e - 16.5 * s], [20.16, 0, e - 16.5 * s], [20.16, 0, e]], w, L);
    path3(cam, [[-9.16, 0, e], [-9.16, 0, e - 5.5 * s], [9.16, 0, e - 5.5 * s], [9.16, 0, e]], w, L);
    const spot = e - 11 * s, ang = Math.acos(5.5 / 9.15);
    const base = s > 0 ? -Math.PI / 2 : Math.PI / 2;
    path3(cam, arcPts(0, spot, 9.15, base - ang, base + ang, 20), w, L);
  }
}
// Goals are drawn after the stands, so the stand behind never paints over the crossbar.
function netBulge(x, y, side) {
  let b = 0;
  for (const g of S.goals || []) {
    if (Math.sign(g.p[2]) !== side) continue;
    const dt = S.t - g.t;
    if (dt < 0 || dt > 1.6) continue;
    const amp = 0.9 * Math.exp(-dt * 3) * (1 + 0.25 * Math.sin(dt * 18));
    b += amp * Math.exp(-((x - g.p[0]) ** 2 + (y - g.p[1]) ** 2) / 1.6);
  }
  return b;
}
function crowdJump() {
  let j = 0;
  for (const g of S.goals || []) { const dt = S.t - g.t; if (dt > 0 && dt < 3) j = Math.max(j, Math.min(1, dt * 4) * (1 - dt / 3)); }
  return j;
}
function drawGoals(cam) {
  for (const s of [-1, 1]) {
    const e = 52.5 * s, gz = e + 2.0 * s, net = 'rgba(255,255,255,0.42)';
    const bz = (x, y) => gz + s * netBulge(x, y, s);
    fillPoly3(cam, [[-3.66, 0, e], [-3.66, 2.44, e], [-3.66, 2.1, gz], [-3.66, 0, gz]], 'rgba(255,255,255,0.06)');
    fillPoly3(cam, [[3.66, 0, e], [3.66, 2.44, e], [3.66, 2.1, gz], [3.66, 0, gz]], 'rgba(255,255,255,0.06)');
    fillPoly3(cam, [[-3.66, 2.1, gz], [3.66, 2.1, gz], [3.66, 0, gz], [-3.66, 0, gz]], 'rgba(255,255,255,0.08)');
    for (let x = -3.66; x <= 3.67; x += 0.61) {
      const pts = [[x, 2.44, e]];
      for (let y = 2.1; y >= -0.01; y -= 0.3) pts.push([x, Math.max(0, y), bz(x, y)]);
      path3(cam, pts, 0.025, net);
    }
    for (let y = 0.3; y < 2.2; y += 0.3) {
      const pts = [];
      for (let x = -3.66; x <= 3.67; x += 0.61) pts.push([x, y, bz(x, y)]);
      path3(cam, pts, 0.025, net);
      path3(cam, [[-3.66, y * 1.16, e], [-3.66, y, gz]], 0.025, net);
      path3(cam, [[3.66, y * 1.16, e], [3.66, y, gz]], 0.025, net);
    }
    for (let z = 0.5; z < 2.0; z += 0.5) path3(cam, [[-3.66, 2.44 - z * 0.17, e + z * s], [3.66, 2.44 - z * 0.17, e + z * s]], 0.025, net);
    path3(cam, [[-3.66, 0, e], [-3.66, 2.44, e], [3.66, 2.44, e], [3.66, 0, e]], 0.17, '#ffffff');
  }
}

function drawStadium(cam, t, world) {
  const jump = crowdJump();
  const segs = world.segs.map(s => ({ s, d: toCam(cam, s.mid)[2] })).filter(o => o.d > -45).sort((a, b) => b.d - a.d);
  for (const { s } of segs) {
    fillPoly3(cam, s.quad, '#1a1f2c');
    for (const d of s.dots) {
      const q = toCam(cam, d.p);
      if (q[2] < NEAR) continue;
      const sp = proj(q);
      if (sp[0] < -12 || sp[0] > W + 12 || sp[1] < -12 || sp[1] > H + 12) continue;
      const w = clamp(FOC * d.sz / q[2], 1.1, 9);
      let col = d.col;
      if (d.fl >= 0 && Math.pow(Math.max(0, Math.sin(t * 2.3 + d.fl)), 40) > 0.3) col = '#ffffff';
      if (jump > 0) sp[1] -= jump * w * 1.6 * Math.abs(Math.sin(t * 9 + d.sz * 40));
      ctx.fillStyle = col;
      ctx.fillRect(sp[0] - w / 2, sp[1] - w * 1.3, w, Math.max(w * 1.3, 1.1));
    }
    line3(cam, s.quad[0], s.quad[1], 0.35, 'rgba(255,255,255,0.45)');
    line3(cam, s.top[0], s.top[1], 1.2, '#0b0e15');
  }
  ctx.globalCompositeOperation = 'lighter';
  for (const s of world.segs) {
    if (!s.light) continue;
    const q = toCam(cam, [s.top[0][0], s.top[0][1] + 1.5, s.top[0][2]]);
    if (q[2] < NEAR) continue;
    const sp = proj(q), r = clamp(FOC * 3.2 / q[2], 3, 55);
    const g = ctx.createRadialGradient(sp[0], sp[1], 0, sp[0], sp[1], r * 4);
    g.addColorStop(0, 'rgba(255,255,240,0.85)');
    g.addColorStop(0.15, 'rgba(255,255,230,0.35)');
    g.addColorStop(1, 'rgba(255,255,230,0)');
    ctx.fillStyle = g;
    ctx.fillRect(sp[0] - r * 4, sp[1] - r * 4, r * 8, r * 8);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.arc(sp[0], sp[1], r * 0.3, 0, 7); ctx.fill();
  }
  ctx.globalCompositeOperation = 'source-over';
}

function drawStudio(t, scene) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0a0c12');
  g.addColorStop(1, '#161b26');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(255,255,255,0.035)';
  ctx.lineWidth = 2;
  for (let x = 0; x <= W; x += 90) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y <= H; y += 90) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  const s = ctx.createRadialGradient(W / 2, H * 0.55, 0, W / 2, H * 0.55, W * 0.8);
  s.addColorStop(0, rgba(scene.glow || S.accent, 0.12));
  s.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = s;
  ctx.fillRect(0, 0, W, H);
}

// ---------- theatre stage ----------
const FLOOR_Y = 1300;
function stageCamAt(i, lt) {
  const b = S.beats[i];
  const to = b.zoom != null ? b.zoom : 1;
  const from = (i === 0 || b.cut) ? (b.zoomFrom != null ? b.zoomFrom : to) : stageCamAt(i - 1, S.beats[i - 1].dur);
  const md = b.move != null ? b.move : Math.min(2.4, b.dur * 0.8);
  return lerp(from, to, ease(pr(lt, 0, md))) * (1 + 0.006 * lt);
}
function railY(k, x) { const d = (x - W / 2) / (W / 2); return [610, 800, 975][k] + 30 * d * d; }
const stageCache = new Map();
function buildStage(scene) {
  const key = JSON.stringify(scene);
  if (stageCache.has(key)) return stageCache.get(key);
  const R = rng(scene.seed || 9);
  const pal = scene.crowd || ['#6b2a2e', '#8a3a35', '#4a1c20', '#b9935a', '#d8c3a0', '#3a1518'];
  const dots = [];
  const bands = [[() => 430, x => railY(0, x) - 14, 12], [x => railY(0, x) + 24, x => railY(1, x) - 14, 13],
    [x => railY(1, x) + 24, x => railY(2, x) - 14, 14], [x => railY(2, x) + 26, () => FLOOR_Y - 24, 17]];
  for (const [ya, yb, st] of bands) {
    for (let x = 120; x < W - 120; x += st * 0.95) {
      for (let y = ya(x); y < yb(x); y += st) {
        if (R() < 0.12) continue;
        dots.push({ x: x + R() * 4, y: y + R() * 3, c: pal[Math.floor(R() * pal.length)], s: st * (0.4 + R() * 0.15), fl: R() < 0.02 ? R() * 6.28 : -1 });
      }
    }
  }
  const st = { dots };
  stageCache.set(key, st);
  return st;
}
function goldGrad(x0, x1) {
  const g = ctx.createLinearGradient(x0, 0, x1, 0);
  g.addColorStop(0, '#8a5c10'); g.addColorStop(0.45, '#ffe9a8'); g.addColorStop(0.6, '#f1c453'); g.addColorStop(1, '#8a5c10');
  return g;
}
function stagePlayers(lt, players) {
  return players.map(p => {
    let a = 1, dy = 0, walk = 0;
    if (p.enter === 'fade' || p.enter === 'walk') {
      const k = pr(lt, p.delay || 0, p.enter === 'walk' ? 1.4 : 0.6);
      a = eOut(k); dy = (1 - eOut(k)) * -40; walk = p.enter === 'walk' && k < 1 ? 1 : 0;
    }
    if (p.exitAt != null) a *= 1 - pr(lt, p.exitAt, 0.5);
    const sc = p.scale || 1;
    return { p, a, walk, x: (p.sx != null ? p.sx : 0.5) * W, y: (p.sy || 1610) + dy, u: 440 * sc };
  }).sort((m, n) => m.y - n.y);
}
function drawStage(t, b, zoom, plt) {
  const st = buildStage(b.sceneObj);
  ctx.save();
  ctx.translate(W / 2 + Math.sin(t * 0.4) * 6, 1250 + Math.sin(t * 0.27) * 4); ctx.scale(zoom, zoom); ctx.translate(-W / 2, -1250);
  let g = ctx.createLinearGradient(0, 0, 0, FLOOR_Y);
  g.addColorStop(0, '#12070a'); g.addColorStop(1, '#2a1013');
  ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, FLOOR_Y + 300);
  for (const d of st.dots) {
    ctx.fillStyle = d.fl >= 0 && Math.pow(Math.max(0, Math.sin(t * 2.1 + d.fl)), 40) > 0.3 ? '#fff6dc' : d.c;
    ctx.fillRect(d.x - d.s / 2, d.y - d.s * 1.2, d.s, d.s * 1.2);
  }
  for (let k = 0; k < 3; k++) {
    const path = dy => { ctx.beginPath(); for (let x = -300; x <= W + 300; x += 20) { const y = railY(k, x) + dy; x === -300 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); } };
    path(14); ctx.lineWidth = 24; ctx.strokeStyle = '#2b0f12'; ctx.stroke();
    path(0); ctx.lineWidth = 9; ctx.strokeStyle = goldGrad(0, W); ctx.stroke();
    ctx.globalCompositeOperation = 'lighter';
    for (let x = 30; x < W; x += 38) {
      const y = railY(k, x) + 15, gl = ctx.createRadialGradient(x, y, 0, x, y, 9);
      gl.addColorStop(0, 'rgba(255,230,170,0.9)'); gl.addColorStop(1, 'rgba(255,200,120,0)');
      ctx.fillStyle = gl; ctx.fillRect(x - 9, y - 9, 18, 18);
    }
    ctx.globalCompositeOperation = 'source-over';
  }
  g = ctx.createLinearGradient(0, FLOOR_Y, 0, H);
  g.addColorStop(0, '#4a2a16'); g.addColorStop(1, '#1c0f07');
  ctx.fillStyle = g; ctx.fillRect(-300, FLOOR_Y, W + 600, H - FLOOR_Y + 400);
  ctx.strokeStyle = 'rgba(0,0,0,0.28)'; ctx.lineWidth = 2;
  for (let i = -16; i <= 16; i++) { ctx.beginPath(); ctx.moveTo(W / 2 + i * 24, FLOOR_Y); ctx.lineTo(W / 2 + i * 150, H + 300); ctx.stroke(); }
  ctx.fillStyle = goldGrad(0, W); ctx.fillRect(-300, FLOOR_Y - 5, W + 600, 7);

  const ps = stagePlayers(plt, b.playersArr);
  for (const o of ps) S.anchors[b.playersArr.indexOf(o.p)] = { x: o.x, y: o.y, u: o.u };
  drawUnderPens();
  ctx.globalCompositeOperation = 'lighter';
  for (const o of ps) {
    if (o.p.ghost || o.p.spot === false) continue;
    const a = o.a * (b.spotDim != null ? b.spotDim : 1);
    const topX = o.x * 0.7 + W / 2 * 0.3;
    g = ctx.createLinearGradient(0, -100, 0, o.y);
    g.addColorStop(0, `rgba(255,236,190,${0.02 * a})`); g.addColorStop(1, `rgba(255,226,170,${0.2 * a})`);
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(topX - 30, -100); ctx.lineTo(topX + 30, -100); ctx.lineTo(o.x + 230, o.y); ctx.lineTo(o.x - 230, o.y); ctx.closePath(); ctx.fill();
    g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, 240);
    g.addColorStop(0, `rgba(255,225,160,${0.5 * a})`); g.addColorStop(1, 'rgba(255,225,160,0)');
    ctx.save(); ctx.translate(o.x, o.y); ctx.scale(1, 0.22); ctx.translate(-o.x, -o.y);
    ctx.fillStyle = g; ctx.fillRect(o.x - 240, o.y - 240, 480, 480);
    ctx.restore();
    const R = rng(Math.round(o.x));
    for (let i = 0; i < 36; i++) {
      const f = R(), yy = lerp(0, o.y - 40, (R() + t * 0.02 * (0.5 + R())) % 1);
      const half = lerp(30, 230, yy / o.y), xx = lerp(topX, o.x, yy / o.y) + (f - 0.5) * 2 * half * 0.8 + Math.sin(t + i) * 8;
      ctx.fillStyle = `rgba(255,240,210,${0.5 * a})`; ctx.fillRect(xx, yy, 2.5, 2.5);
    }
  }
  ctx.globalCompositeOperation = 'source-over';
  for (const o of ps) { drawPlayer(o.x, o.y, o.u, o.p, plt, o.walk, o.a); S.anchors[b.playersArr.indexOf(o.p)] = { x: o.x, y: o.y, u: o.u }; }

  for (const side of [-1, 1]) {
    for (let i = 0; i < 6; i++) {
      const x = side < 0 ? -80 + i * 38 : W + 80 - (i + 1) * 38;
      g = ctx.createLinearGradient(x, 0, x + 38, 0);
      g.addColorStop(0, '#3e070c'); g.addColorStop(0.5, '#a3162a'); g.addColorStop(1, '#3e070c');
      ctx.fillStyle = g; ctx.fillRect(x, -300, 39, H + 600);
    }
  }
  ctx.fillStyle = '#5a0a12'; ctx.fillRect(-300, -300, W + 600, 380);
  for (let x = -60; x < W + 60; x += 120) {
    ctx.beginPath(); ctx.ellipse(x + 60, 80, 62, 70, 0, 0, Math.PI); ctx.fillStyle = '#7a0f1c'; ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = goldGrad(x, x + 120); ctx.stroke();
  }
  ctx.restore();
}

// ---------- commentary booth ----------
// A broadcast booth high in the stand: blurred stadium through the window, desk, monitors, ON AIR light.
function drawBooth(t, b, plt) {
  const scene = b.sceneObj;
  const cam = mkCam([Math.sin(t * 0.3) * 1.5, 24, -78 + t * 0.05], [0, 0, 18]);
  drawSky(scene); drawPitch(cam, scene); drawStadium(cam, t, b.world); drawGoals(cam);
  bgx.clearRect(0, 0, W / Q, H / Q); bgx.filter = 'blur(2px)'; bgx.drawImage(cv, 0, 0, W / Q, H / Q); bgx.filter = 'none';
  ctx.save(); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(bgc, 0, 0, W, H); ctx.restore();
  ctx.fillStyle = 'rgba(10,12,18,0.25)'; ctx.fillRect(0, 0, W, H);
  const sh = ctx.createLinearGradient(0, 300, W, 1100);
  sh.addColorStop(0.35, 'rgba(255,255,255,0)'); sh.addColorStop(0.42, 'rgba(255,255,255,0.07)'); sh.addColorStop(0.5, 'rgba(255,255,255,0)');
  ctx.fillStyle = sh; ctx.fillRect(0, 0, W, H);
  // window frame + wall
  ctx.fillStyle = '#14161c';
  ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.rect(70, 560, W - 140, 760); ctx.fill('evenodd');
  ctx.fillRect(W / 2 - 9, 560, 18, 760);
  ctx.fillStyle = 'rgba(255,255,255,0.06)'; ctx.fillRect(70, 560, W - 140, 4);
  // ON AIR light
  const on = 0.75 + 0.25 * Math.sin(t * 3);
  ctx.save(); rrect(W - 330, 600, 220, 64, 12); ctx.fillStyle = `rgba(200,20,30,${on})`; ctx.shadowColor = '#ff2a3a'; ctx.shadowBlur = 30 * on; ctx.fill(); ctx.restore();
  font(800, 34, 'Inter', '4px'); ctx.fillStyle = '#ffe8e8'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('ON AIR', W - 220, 633);
  // commentator(s) behind the desk
  drawUnderPens();
  for (const [k, p] of b.playersArr.entries()) {
    const x = (p.sx != null ? p.sx : 0.5) * W, y = 1880, u = 980 * (p.scale || 1);
    drawPlayer(x, y, u, p, plt, 0, 1);
    S.anchors[k] = { x, y, u };
  }
  // desk
  let g = ctx.createLinearGradient(0, 1430, 0, 1500); g.addColorStop(0, '#3a3d46'); g.addColorStop(1, '#23252c');
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-40, 1500); ctx.lineTo(110, 1430); ctx.lineTo(W - 110, 1430); ctx.lineTo(W + 40, 1500); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#17181d'; ctx.fillRect(0, 1500, W, H - 1500);
  const lamp = ctx.createRadialGradient(W / 2, 1460, 0, W / 2, 1460, 520); lamp.addColorStop(0, 'rgba(255,214,150,0.18)'); lamp.addColorStop(1, 'rgba(255,214,150,0)');
  ctx.fillStyle = lamp; ctx.fillRect(0, 1100, W, 820);
  // monitors
  for (const [mx, lines] of [[90, scene.screenLeft || ['BRA 0–2 GER', "23'"]], [W - 370, scene.screenRight || ['LIVE', 'WORLD CUP · SEMI-FINAL']]]) {
    rrect(mx, 1250, 280, 180, 10); ctx.fillStyle = '#0d0e12'; ctx.fill();
    const sg = ctx.createLinearGradient(0, 1262, 0, 1418); sg.addColorStop(0, '#1d3b66'); sg.addColorStop(1, '#0f1d33');
    ctx.fillStyle = sg; ctx.fillRect(mx + 12, 1262, 256, 156);
    ctx.fillStyle = '#e8f1ff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const fit = (txt, w, sz, fam, ls) => { let z = sz; do { font(fam === 'Mono' ? 600 : 800, z, fam, ls); z -= 1; } while (ctx.measureText(txt).width > w && z > 10); };
    fit(lines[0], 230, 40, 'Inter', '0px'); ctx.fillText(lines[0], mx + 140, 1322);
    fit(lines[1], 232, 20, 'Mono', '2px'); ctx.fillStyle = '#9fb7d8'; ctx.fillText(lines[1], mx + 140, 1378);
    ctx.fillStyle = '#0d0e12'; ctx.fillRect(mx + 125, 1430, 30, 14);
  }
}

// ---------- players ----------
function drawTrophy(x, y, u) {
  const w = u * 0.2;
  const g = ctx.createLinearGradient(x - w / 2, 0, x + w / 2, 0);
  g.addColorStop(0, '#9aa1ab'); g.addColorStop(0.45, '#f4f6f8'); g.addColorStop(1, '#7c838e');
  ctx.strokeStyle = '#c9ced6'; ctx.lineWidth = u * 0.018;
  ctx.beginPath(); ctx.arc(x - w * 0.55, y - w * 0.55, w * 0.22, Math.PI * 0.4, Math.PI * 1.6); ctx.stroke();
  ctx.beginPath(); ctx.arc(x + w * 0.55, y - w * 0.55, w * 0.22, -Math.PI * 0.6, Math.PI * 0.6); ctx.stroke();
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.moveTo(x - w / 2, y - w * 1.0);
  for (let i = 0; i <= 6; i++) ctx.lineTo(x - w / 2 + w * i / 6, y - w * (i % 2 ? 1.12 : 1.0));
  ctx.quadraticCurveTo(x + w / 2, y - w * 0.15, x + w * 0.08, y - w * 0.05);
  ctx.lineTo(x + w * 0.08, y + w * 0.25); ctx.lineTo(x - w * 0.08, y + w * 0.25); ctx.lineTo(x - w * 0.08, y - w * 0.05);
  ctx.quadraticCurveTo(x - w / 2, y - w * 0.15, x - w / 2, y - w * 1.0);
  ctx.fill();
  ctx.fillStyle = '#6e1f2a';
  ctx.fillRect(x - w * 0.32, y + w * 0.25, w * 0.64, w * 0.32);
}


// ---------- animated rig: jointed players with actions ----------
// Pose angles: 0 = limb points straight down, positive = towards screen-right. Legs are [angle, fold] where fold (0..1)
// bends the knee back (foot lifts behind, seen from behind). Arms are [angle, elbow bend]. hy = hip lift (u), px = shift (u),
// rot = whole-body rotation around the hip, lean = torso lean.
const P0 = { rot: 0, px: 0, hy: 0, lean: 0, armsFront: 0, L: [-0.06, 0], R: [0.06, 0], AL: [-0.16, 0.25], AR: [0.16, 0.25] };
const ACTIONS = {
  kick: { dur: 1.0, contact: 0.42, keys: [
    [0.0, { L: [-0.06, 0], R: [0.06, 0], AL: [-0.25, 0.3], AR: [0.25, 0.3] }],
    [0.25, { L: [-0.04, 0], R: [0.38, 0.95], AL: [-0.95, 0.2], AR: [0.55, 0.45], lean: 0.12, hy: 0.01 }],
    [0.42, { L: [-0.04, 0.05], R: [-0.35, 0.05], AL: [-1.15, 0.1], AR: [0.9, 0.3], lean: -0.08 }],
    [0.62, { L: [-0.02, 0.12], R: [-0.95, 0.15], AL: [-1.3, 0.05], AR: [1.05, 0.2], lean: -0.18, hy: -0.035 }],
    [1.0, { L: [-0.06, 0], R: [-0.08, 0.05], AL: [-0.3, 0.3], AR: [0.3, 0.3], lean: -0.04 }]] },
  dive: { dur: 0.95, keys: [
    [0.0, { L: [-0.25, 0.25], R: [0.25, 0.25], AL: [-0.9, 0.4], AR: [0.9, 0.4], hy: 0.05 }],
    [0.16, { L: [-0.3, 0.35], R: [0.3, 0.35], AL: [-1.0, 0.4], AR: [1.0, 0.4], hy: 0.08, rot: 0.12 }],
    [0.45, { L: [-0.15, 0.15], R: [0.3, 0.4], AL: [Math.PI - 0.2, 0], AR: [Math.PI + 0.15, 0], hy: -0.22, rot: 1.25, px: 0.55 }],
    [0.7, { L: [-0.1, 0.2], R: [0.35, 0.5], AL: [Math.PI - 0.1, 0], AR: [Math.PI + 0.2, 0], hy: 0.12, rot: 1.5, px: 0.78 }],
    [1.0, { L: [-0.05, 0.3], R: [0.3, 0.5], AL: [Math.PI - 0.3, 0.2], AR: [Math.PI + 0.1, 0.2], hy: 0.4, rot: 1.56, px: 0.86 }]] },
  slide: { dur: 1.1, keys: [   // sliding tackle: drop, lean back, leading leg out, skid along the grass, then settle
    [0.0, { L: [-0.15, 0.4], R: [0.25, 0.5], AL: [-0.5, 0.6], AR: [0.5, 0.6], lean: 0.15, hy: 0.04 }],
    [0.2, { L: [0.5, 0.9], R: [1.2, 0.1], AL: [-1.9, 0.3], AR: [1.0, 0.5], rot: 0.55, hy: 0.18, px: 0.1 }],
    [0.45, { L: [0.8, 1.0], R: [1.45, 0.0], AL: [-2.3, 0.2], AR: [0.6, 0.6], rot: 1.15, hy: 0.38, px: 0.25 }],
    [0.8, { L: [0.85, 1.0], R: [1.5, 0.0], AL: [-2.4, 0.2], AR: [0.5, 0.6], rot: 1.25, hy: 0.42, px: 0.3 }],
    [1.0, { L: [0.8, 1.1], R: [1.35, 0.15], AL: [-2.2, 0.3], AR: [0.6, 0.7], rot: 1.2, hy: 0.42, px: 0.3 }]] },
};
function mixPose(a, b, k) {
  const o = {};
  for (const key of Object.keys(P0)) {
    const x = a[key] != null ? a[key] : P0[key], y = b[key] != null ? b[key] : P0[key];
    o[key] = Array.isArray(x) ? [lerp(x[0], y[0], k), lerp(x[1], y[1], k)] : lerp(x, y, k);
  }
  return o;
}
function keyPose(keys, f) {
  for (let i = 1; i < keys.length; i++) if (f <= keys[i][0]) return mixPose(keys[i - 1][1], keys[i][1], ease((f - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0])));
  return mixPose(keys[keys.length - 1][1], keys[keys.length - 1][1], 0);
}
function loopPose(name, t) {
  if (name === 'run') {   // athletic run: arms tucked and pumping, strong knee drive, a bob twice per stride (the old one looked goofy)
    const ph = t / 0.42 * Math.PI * 2, s = Math.sin(ph), c2 = Math.cos(ph * 2);
    return { ...P0, L: [-0.05 + 0.03 * s, Math.max(0, s) * 1.35], R: [0.05 + 0.03 * s, Math.max(0, -s) * 1.35],
      AL: [-0.12, lerp(0.35, -2.4, (1 + s) / 2)], AR: [0.12, lerp(0.35, -2.4, (1 - s) / 2)], armsFront: 1,   // arms swing in front of the body (seen from behind)
      hy: -0.035 * (0.5 + 0.5 * c2), rot: 0.035 * s, px: 0.012 * s, lean: 0 };
  }
  if (name === 'celebrate') {
    const ph = t / 0.7 * Math.PI * 2, j = Math.abs(Math.sin(ph));
    return { ...P0, L: [-0.12, 0.3 * j], R: [0.12, 0.3 * j], AL: [Math.PI - 0.35 + 0.15 * Math.sin(ph * 2), 0.1], AR: [Math.PI + 0.35 - 0.15 * Math.sin(ph * 2), 0.1], hy: -0.09 * j };
  }
  if (name === 'ready') return { ...P0, L: [-0.25, 0.25], R: [0.25, 0.25], AL: [-0.9, 0.4], AR: [0.9, 0.4], hy: 0.05 + 0.01 * Math.sin(t * 6) };
  const b = Math.sin(t * 2.6);
  return { ...P0, AL: [-0.16 - 0.03 * b, 0.25], AR: [0.16 + 0.03 * b, 0.25], hy: 0.004 * b };
}
function poseFor(p, t, walking) {
  const d = p.actionDelay != null ? p.actionDelay : 0, A = ACTIONS[p.action];
  if (A) {
    const dur = p.actionDur || A.dur;
    const act = f => {
      const ps = keyPose(A.keys, f);
      if (p.dir === -1 || (p.foot === 'left' && p.action === 'kick')) { ps.rot = -ps.rot; /* foot: 'left' mirrors the strike for left-footers (Messi) */ ps.px = -ps.px; [ps.AL, ps.AR] = [[-ps.AR[0], ps.AR[1]], [-ps.AL[0], ps.AL[1]]]; [ps.L, ps.R] = [[-ps.R[0], ps.R[1]], [-ps.L[0], ps.L[1]]]; }
      return ps;
    };
    const pre = tt => walking || p.path ? loopPose('run', tt) : loopPose(p.before || 'idle', tt);
    let ps;
    if (t >= d && t < d + dur) {   // blend in over 0.12s so the move doesn't snap
      ps = act((t - d) / dur);
      if (t - d < 0.12) ps = mixPose(pre(t), ps, ease((t - d) / 0.12));
    } else if (t >= d + dur) {
      ps = p.after ? loopPose(p.after, t - d - dur) : act(1);
      if (p.after && t - d - dur < 0.2) ps = mixPose(act(1), ps, ease((t - d - dur) / 0.2));
    } else ps = pre(t);
    return withHops(p, ps, t);
  }
  return withHops(p, walking ? loopPose('run', t) : loopPose(p.action || 'idle', t), t);
}
function withHops(p, ps, t) {   // "hops": [{t, dur}] — a small jump (e.g. hurdling a slide tackle)
  for (const h of p.hops || []) {
    const k = pr(t, h.t, h.dur || 0.45);
    if (k > 0 && k < 1) { ps = { ...ps }; ps.hy -= (h.height || 0.16) * Math.sin(Math.PI * k); ps.L = [ps.L[0], ps.L[1] + 0.8 * Math.sin(Math.PI * k)]; ps.R = [ps.R[0], ps.R[1] + 0.8 * Math.sin(Math.PI * k)]; }
  }
  return ps;
}
// Where a rigged player's hands are (screen px, relative to his feet), mirroring rigBody's transforms. Used for real saves.
function rigHands(u, p, t) {
  const ps = poseFor(p, t, false), out = [];
  for (const [side, arm] of [[-1, ps.AL], [1, ps.AR]]) {
    const [a, e] = arm;
    let x = side * u * 0.15, y = -u * 0.3;
    x += Math.sin(a) * u * 0.14; y += Math.cos(a) * u * 0.14;
    x += Math.sin(a + side * e) * u * 0.15; y += Math.cos(a + side * e) * u * 0.15;
    const r1 = ps.lean, x1 = x * Math.cos(r1) - y * Math.sin(r1), y1 = x * Math.sin(r1) + y * Math.cos(r1);
    const r2 = ps.rot, x2 = x1 * Math.cos(r2) - y1 * Math.sin(r2), y2 = x1 * Math.sin(r2) + y1 * Math.cos(r2);
    out.push([x2 + ps.px * u, y2 + (-0.5 + ps.hy) * u]);
  }
  return out;
}
function limb(x, y, a, len, w, col) {
  const x2 = x + Math.sin(a) * len, y2 = y + Math.cos(a) * len;
  ctx.strokeStyle = col; ctx.lineWidth = w; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x2, y2); ctx.stroke();
  return [x2, y2];
}
function rigBody(u, p, t, walking, c) {
  const ps = poseFor(p, t, walking);
  ctx.save();
  ctx.translate(ps.px * u, (-0.5 + ps.hy) * u);
  ctx.rotate(ps.rot);
  const lw = u * 0.075, Lt = u * 0.24, Ls = u * 0.25;
  for (const [side, leg] of [[-1, ps.L], [1, ps.R]]) {
    const [a, f] = leg, hx = side * u * 0.05;
    const [kx, ky] = limb(hx, u * 0.04, a, Lt * (1 - 0.15 * f), lw, c.skin);
    const sa = a + side * 0.25 * f + (f > 0 ? Math.PI * 0.0 : 0);
    const shinLen = Ls * (1 - 0.55 * f);
    const mx = kx + Math.sin(sa) * shinLen * 0.35, my = ky + Math.cos(sa) * shinLen * 0.35;
    limb(kx, ky, sa, shinLen * 0.35, lw * 0.95, c.skin);
    const [ax, ay] = limb(mx, my, sa, shinLen * 0.65, lw * 1.02, c.socks);
    ctx.save(); ctx.translate(ax, ay); ctx.rotate(-sa);
    ctx.fillStyle = '#15171c'; rrect(-lw * 0.62, -u * 0.015 - f * u * 0.03, lw * 1.24, u * 0.045 + f * u * 0.035, lw * 0.3); ctx.fill();
    ctx.restore();
  }
  ctx.fillStyle = c.shorts; rrect(-u * 0.135, -u * 0.06, u * 0.27, u * 0.15, u * 0.02); ctx.fill();
  ctx.rotate(ps.lean);
  const drawRigArms = () => {
    for (const [side, arm] of [[-1, ps.AL], [1, ps.AR]]) {
      const [a, e] = arm, sx = side * u * 0.15, sy = -u * 0.3;
      const [ex, ey] = limb(sx, sy, a, u * 0.14, u * 0.07, c.k.sleeves || c.shirt);
      const [hx, hy] = limb(ex, ey, a + side * e, u * 0.15, u * 0.06, c.skin);
      if (p.gloves) { ctx.fillStyle = p.gloves; ctx.beginPath(); ctx.arc(hx, hy, u * 0.045, 0, 7); ctx.fill(); }
    }
  };
  if (ps.armsFront && !p.front) drawRigArms();
  ctx.fillStyle = c.shirt;
  ctx.beginPath(); ctx.moveTo(-u * 0.16, -u * 0.32); ctx.lineTo(u * 0.16, -u * 0.32); ctx.lineTo(u * 0.135, -u * 0.03); ctx.lineTo(-u * 0.135, -u * 0.03); ctx.closePath(); ctx.fill();
  if (c.k.stripes || c.k.checks || c.k.hoops) {
    ctx.save(); ctx.clip();
    const sq = u * 0.045;
    if (c.k.stripes) for (let i = -4; i <= 4; i++) { ctx.fillStyle = c.k.stripes[(i + 8) % 2]; ctx.fillRect(i * sq - sq / 2, -u * 0.33, sq, u * 0.31); }
    else if (c.k.hoops) for (let r = 0; r < 6; r++) { ctx.fillStyle = c.k.hoops[r % 2]; ctx.fillRect(-u * 0.2, -u * 0.33 + r * u * 0.055, u * 0.4, u * 0.055); }
    else for (let r = 0; r < 8; r++) for (let cc = -4; cc <= 4; cc++) { ctx.fillStyle = c.k.checks[(r + cc + 16) % 2]; ctx.fillRect(cc * sq - sq / 2, -u * 0.33 + r * sq, sq, sq); }
    ctx.restore();
  }
  if (u > 50) {
    ctx.fillStyle = c.txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.front) { if (p.num != null) { font(800, u * 0.07, 'Inter', '0px'); ctx.fillText(String(p.num), u * 0.06, -u * 0.2); } }
    else {
      if (p.name) { font(700, Math.max(6, u * 0.034), 'Mono', `${u * 0.004}px`); ctx.fillText(p.name.toUpperCase(), 0, -u * 0.245); }
      if (p.num != null) { font(800, u * 0.12, 'Inter', '0px'); ctx.fillText(String(p.num), 0, -u * 0.1); }
    }
  }
  if (!(ps.armsFront && !p.front)) drawRigArms();
  ctx.fillStyle = c.skin; ctx.fillRect(-u * 0.025, -u * 0.37, u * 0.05, u * 0.06);
  ctx.beginPath(); ctx.arc(0, -u * 0.41, u * 0.062, 0, 7); ctx.fill();
  ctx.fillStyle = c.hair; ctx.beginPath();
  if (p.front) ctx.arc(0, -u * 0.425, u * 0.062, Math.PI * 1.05, Math.PI * 1.95);
  else ctx.arc(0, -u * 0.418, u * 0.06, Math.PI * 0.92, Math.PI * 2.08);
  ctx.fill();
  ctx.restore();
  return ps;
}

function drawPlayer(x, y, u, p, t, walk, alpha) {
  if (typeof toyOn === 'function' && toyOn()) return drawToyFigure(x, y, u, p, t, walk, alpha);
  let k = p.kit || {}, skin = p.skin || '#c68a63', hair = p.hair || '#1b1410';
  if (p.ghost) {
    k = { shirt: '#a9c0e4', shorts: '#a9c0e4', socks: '#a9c0e4', text: '#ffffff' };
    skin = '#c4d4ee'; hair = '#93a9cf'; alpha *= 0.5;
  }
  const shirt = k.shirt || '#c8102e', shorts = k.shorts || '#ffffff', socks = k.socks || shirt;
  const txt = k.text || '#ffffff';
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
  if (p.action || p.rig || (p.hops && p.hops.length)) {
    const ps = poseFor(p, t, walk > 0);
    const lift = Math.max(0, -ps.hy) * 3;
    ctx.fillStyle = `rgba(0,0,0,${0.3 / (1 + lift)})`;
    ctx.beginPath(); ctx.ellipse(ps.px * u + Math.sin(ps.rot) * u * 0.3, 0, u * (0.17 + Math.abs(Math.sin(ps.rot)) * 0.3), u * 0.035, 0, 0, 7); ctx.fill();
    rigBody(u, p, t, walk > 0, { k, skin, hair, shirt, shorts, socks, txt });
    if (p.tag != null) drawTag(u, p, t);
    drawNameLabel(u, p, t);
    ctx.restore();
    return;
  }
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.beginPath(); ctx.ellipse(0, 0, u * 0.17, u * 0.035, 0, 0, 7); ctx.fill();
  const sw = Math.sin(t * 9) * walk, legW = u * 0.075, gap = u * 0.05;
  const suit = p.outfit === 'suit', suitC = p.suitColor || '#1a1d26';
  if (suit) {   // award-night suit: trousers, black shoes, jacket, white shirt and bow tie, no number
    for (const side of [-1, 1]) {
      const lift = Math.max(0, side * sw) * u * 0.05, lx = side * gap;
      ctx.fillStyle = suitC; rrect(lx - legW * 0.6, -u * 0.56 - lift, legW * 1.2, u * 0.53, legW * 0.2); ctx.fill();
      ctx.fillStyle = '#0b0c10'; rrect(lx - legW * 0.75, -u * 0.045 - lift, legW * 1.5, u * 0.05, legW * 0.3); ctx.fill();
    }
  }
  for (const side of suit ? [] : [-1, 1]) {
    const lift = Math.max(0, side * sw) * u * 0.05, lx = side * gap;
    ctx.fillStyle = skin; ctx.fillRect(lx - legW / 2, -u * 0.47 - lift, legW, u * 0.2);
    ctx.fillStyle = socks; rrect(lx - legW / 2, -u * 0.28 - lift, legW, u * 0.25, legW * 0.3); ctx.fill();
    ctx.fillStyle = '#15171c'; rrect(lx - legW * 0.6, -u * 0.04 - lift, legW * 1.2, u * 0.045, legW * 0.3); ctx.fill();
  }
  if (!suit) { ctx.fillStyle = shorts; rrect(-u * 0.135, -u * 0.56, u * 0.27, u * 0.15, u * 0.02); ctx.fill(); }
  const armsUp = p.pose === 'arms_up';
  // Arms are drawn after the torso, hanging just outside it, so they read as arms (they used to sit behind the shirt,
  // leaving only the hands poking out at the hips).
  const drawArms = () => {
    const sleeve = suit ? suitC : (k.sleeves || shirt), edge = shade(sleeve, -0.35);
    for (const side of [-1, 1]) {
      ctx.save();
      ctx.translate(side * u * 0.165, -u * 0.8);
      ctx.rotate(armsUp ? side * 0.25 + Math.PI : p.pose === 'keeper' ? side * 0.95 : p.pose === 'wings' ? -side * (1.4 + Math.sin(t * 7) * 0.08) : p.pose === 'fists' ? -side * (2.35 + Math.sin(t * 9) * 0.12) : p.pose === 'shake' && side === (p.shakeSide || 1) ? -side * (0.95 + Math.sin(t * 9 + (p.x || 0)) * 0.12) : side * 0.1);
      ctx.lineWidth = Math.max(1, u * 0.006); ctx.strokeStyle = edge;
      if (suit) {
        rrect(-u * 0.04, -u * 0.01, u * 0.08, u * 0.28, u * 0.03); ctx.fillStyle = sleeve; ctx.fill(); ctx.stroke();
        ctx.fillStyle = '#f4f4f2'; ctx.fillRect(-u * 0.032, u * 0.255, u * 0.064, u * 0.02);
        ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(0, u * 0.3, u * 0.033, 0, 7); ctx.fill();
      } else {
        ctx.fillStyle = skin; rrect(-u * 0.028, u * 0.08, u * 0.056, u * 0.21, u * 0.028); ctx.fill();
        rrect(-u * 0.042, -u * 0.01, u * 0.084, u * 0.11, u * 0.025); ctx.fillStyle = sleeve; ctx.fill(); ctx.stroke();
        ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(0, u * 0.29, u * 0.03, 0, 7); ctx.fill();
      }
      if (p.gloves) { ctx.fillStyle = p.gloves; ctx.beginPath(); ctx.arc(0, u * 0.3, u * 0.042, 0, 7); ctx.fill(); }
      ctx.restore();
    }
  };
  ctx.fillStyle = suit ? suitC : shirt;
  ctx.beginPath();
  ctx.moveTo(-u * 0.16, -u * 0.82); ctx.lineTo(u * 0.16, -u * 0.82);
  ctx.lineTo(u * 0.135, suit ? -u * 0.5 : -u * 0.53); ctx.lineTo(-u * 0.135, suit ? -u * 0.5 : -u * 0.53); ctx.closePath(); ctx.fill();
  if (suit && p.front) {
    ctx.fillStyle = '#f4f4f2';   // shirt in the V of the jacket
    ctx.beginPath(); ctx.moveTo(-u * 0.055, -u * 0.82); ctx.lineTo(u * 0.055, -u * 0.82); ctx.lineTo(0, -u * 0.66); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = shade(suitC, 0.25); ctx.lineWidth = u * 0.008;   // lapels
    ctx.beginPath(); ctx.moveTo(-u * 0.06, -u * 0.82); ctx.lineTo(-u * 0.005, -u * 0.64); ctx.moveTo(u * 0.06, -u * 0.82); ctx.lineTo(u * 0.005, -u * 0.64); ctx.stroke();
    if (p.tie) {   // business suit (managers on the touchline): a long tie instead of a bow tie
      ctx.fillStyle = p.tie === true ? '#7a1420' : p.tie;
      ctx.beginPath(); ctx.moveTo(-u * 0.014, -u * 0.815); ctx.lineTo(u * 0.014, -u * 0.815); ctx.lineTo(u * 0.009, -u * 0.8); ctx.lineTo(u * 0.016, -u * 0.69);
      ctx.lineTo(0, -u * 0.665); ctx.lineTo(-u * 0.016, -u * 0.69); ctx.lineTo(-u * 0.009, -u * 0.8); ctx.closePath(); ctx.fill();
    } else {
    ctx.fillStyle = '#0b0c10';   // bow tie
    ctx.beginPath(); ctx.moveTo(0, -u * 0.8); ctx.lineTo(-u * 0.032, -u * 0.815); ctx.lineTo(-u * 0.032, -u * 0.785); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.moveTo(0, -u * 0.8); ctx.lineTo(u * 0.032, -u * 0.815); ctx.lineTo(u * 0.032, -u * 0.785); ctx.closePath(); ctx.fill();
    }
    ctx.fillStyle = shade(suitC, 0.4);
    for (const by of [-0.6, -0.55]) { ctx.beginPath(); ctx.arc(0, by * u, u * 0.007, 0, 7); ctx.fill(); }
  }
  if (!suit && (k.stripes || k.checks || k.hoops)) {
    ctx.save();
    ctx.clip();
    const sq = u * 0.045;
    if (k.stripes) {
      for (let i = -4; i <= 4; i++) { ctx.fillStyle = k.stripes[(i + 8) % 2]; ctx.fillRect(i * sq - sq / 2, -u * 0.83, sq, u * 0.31); }
    } else if (k.hoops) {   // horizontal bands (QPR)
      for (let r = 0; r < 6; r++) { ctx.fillStyle = k.hoops[r % 2]; ctx.fillRect(-u * 0.2, -u * 0.83 + r * u * 0.055, u * 0.4, u * 0.055); }
    } else {
      for (let r = 0; r < 8; r++) for (let c = -4; c <= 4; c++) {
        ctx.fillStyle = k.checks[(r + c + 16) % 2]; ctx.fillRect(c * sq - sq / 2, -u * 0.83 + r * sq, sq, sq);
      }
    }
    ctx.restore();
  }
  if (!suit) { ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(-u * 0.135, -u * 0.56, u * 0.27, u * 0.03); }
  drawArms();   // before the lettering, so sleeves never cover the name
  const fitName = (txt, weight, size, fam, sp, maxW) => {   // shrink the name until it fits between the sleeves
    font(weight, size, fam, sp); const w = ctx.measureText(txt).width;
    if (w > maxW) font(weight, size * maxW / w, fam, sp);
  };
  if (suit) { /* no name or number on a suit */ }
  else if (u > 50 && p.front && p.chest) {   // hero shot from the front: name and big number on the chest
    ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.name) { fitName(p.name.toUpperCase(), 800, u * 0.04, 'Inter', `${u * 0.003}px`, u * 0.2); ctx.fillText(p.name.toUpperCase(), 0, -u * 0.735); }
    if (p.num != null) { font(800, u * 0.12, 'Inter', '0px'); ctx.fillText(String(p.num), 0, -u * 0.6); }
  } else if (u > 50 && p.front) {
    ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.num != null) { font(800, u * 0.07, 'Inter', '0px'); ctx.fillText(String(p.num), u * 0.06, -u * 0.7); }
  } else if (u > 50) {
    ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.name) { fitName(p.name.toUpperCase(), 700, Math.max(6, u * 0.034), 'Mono', `${u * 0.004}px`, u * 0.2); ctx.fillText(p.name.toUpperCase(), 0, -u * 0.745); }
    if (p.num != null) { font(800, u * 0.12, 'Inter', '0px'); ctx.fillText(String(p.num), 0, -u * 0.6); }
  }
  ctx.fillStyle = skin; ctx.fillRect(-u * 0.025, -u * 0.87, u * 0.05, u * 0.06);
  ctx.beginPath(); ctx.arc(0, -u * 0.91, u * 0.062, 0, 7); ctx.fill();
  ctx.fillStyle = hair; ctx.beginPath();
  if (p.front) ctx.arc(0, -u * 0.925, u * 0.062, Math.PI * 1.05, Math.PI * 1.95);
  else ctx.arc(0, -u * 0.918, u * 0.06, Math.PI * 0.92, Math.PI * 2.08);
  ctx.fill();
  if (p.headset) {
    ctx.strokeStyle = '#1c1d22'; ctx.lineWidth = u * 0.016; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(0, -u * 0.915, u * 0.072, Math.PI * 1.08, Math.PI * 1.92); ctx.stroke();
    ctx.fillStyle = '#26272d';
    for (const sd of [-1, 1]) { rrect(sd * u * 0.07 - u * 0.022, -u * 0.94, u * 0.044, u * 0.06, u * 0.015); ctx.fill(); }
    ctx.lineWidth = u * 0.008; ctx.beginPath(); ctx.moveTo(u * 0.07, -u * 0.89); ctx.quadraticCurveTo(u * 0.12, -u * 0.86, u * 0.1, -u * 0.83); ctx.stroke();
  }
  if (armsUp && p.trophy) drawTrophy(0, -u * 1.2, u);
  if (p.tag != null) drawTag(u, p, t);
  drawNameLabel(u, p, t);
  ctx.restore();
}
// Name label: a small pill above a player's head (label, labelDelay|labelAt), so a player is named on screen the moment he's named in the voice.
function drawNameLabel(u, p, t) {
  if (!p.label) return;
  const k = eBack(pr(t, p.labelDelay != null ? p.labelDelay : (p.delay || 0) + 0.3, 0.3)); if (k <= 0) return;
  const fs = clamp(u * 0.075, 20, 40), y = -u * (p.tag != null ? 1.55 : 1.1);
  ctx.save(); ctx.translate(0, y); ctx.scale(k, k); font(700, fs, 'Inter');
  const w = ctx.measureText(p.label).width + fs * 1.1;
  ctx.fillStyle = 'rgba(255,255,255,0.94)'; rrect(-w / 2, -fs * 0.8, w, fs * 1.6, fs * 0.8); ctx.fill();
  ctx.fillStyle = '#16181d'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(p.label, 0, fs * 0.06);
  ctx.restore();
}
function drawTag(u, p, t) {
  {
    const kt = pr(t, p.tagDelay != null ? p.tagDelay : 0.4, 0.4);
    if (kt > 0) {
      ctx.save();
      ctx.translate(0, -u * 1.13);
      ctx.scale(eBack(kt), eBack(kt));
      font(800, u * 0.3, 'Inter', '-2px');
      ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      const g = ctx.createLinearGradient(0, -u * 0.25, 0, 0);
      g.addColorStop(0, GOLD[0]); g.addColorStop(1, GOLD[2]);
      ctx.fillStyle = g; ctx.shadowColor = 'rgba(241,196,83,0.5)'; ctx.shadowBlur = 30;
      ctx.fillText(String(p.tag), 0, 0);
      if (p.tagLabel) {
        ctx.shadowBlur = 0; font(600, u * 0.036, 'Mono', `${u * 0.006}px`); ctx.fillStyle = '#d8c8a0';
        ctx.fillText(p.tagLabel.toUpperCase(), 0, u * 0.065);
      }
      ctx.restore();
    }
  }
}

function drawPlayers(cam, lt, players) {
  const list = [];
  for (let p of players) {
    const pIdx = players.indexOf(p);
    let x = p.x || 0, z = p.z || 0, walk = 0, heading = [0, 1];
    const wp = (p.web != null || p.webRival != null) ? webPlayerPos(p, lt) : null;
    if (wp) { x = wp.x; z = wp.z; walk = wp.walk; heading = wp.heading;
      if (wp.tackle) { p = Object.assign({}, p, { action: 'slide', actionDelay: wp.tackle.delay, actionDur: 1.1, dir: wp.tackle.dir }); walk = 0; } }
    else if (p.path) {   // runs along a route at a steady pace (no easing, so he never looks like he's running on the spot)
      const pts = p.path, segs = []; let total = 0;
      for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); segs.push(d); total += d; }
      const k = clamp((lt - (p.delay || 0)) / (p.pathDur || 3), 0, 1);
      let dist = k * total, i = 0;
      while (i < segs.length - 1 && dist > segs[i]) { dist -= segs[i]; i++; }
      const f = segs[i] ? dist / segs[i] : 0;
      x = lerp(pts[i][0], pts[i + 1][0], f); z = lerp(pts[i][1], pts[i + 1][1], f);
      heading = [(pts[i + 1][0] - pts[i][0]) / (segs[i] || 1), (pts[i + 1][1] - pts[i][1]) / (segs[i] || 1)];
      walk = k > 0 && k < 1 ? 1 : 0;
    } else if (p.action === 'kick' && p.runup !== false && p.actionDelay != null && S.cur && S.cur._hype) {   // hype: a short run-up into the strike
      const rd = p.runupDur || 0.75, back = p.runup || 3.2, k = pr(lt, p.actionDelay - rd, rd), sd = p.foot === 'left' ? 1 : -1, dir = p.front ? -1 : 1;
      x = lerp(x + sd * back * 0.35, x, k); z = lerp(z - dir * back, z, k);
      heading = [-sd * 0.35, dir]; walk = k > 0 && k < 1 ? 1 : 0;
    } else if (p.enter === 'walk') {
      const k = pr(lt, p.delay || 0, p.walkDur || 1.8);
      x = lerp(p.fromX != null ? p.fromX : x, x, eOut(k));
      z = lerp(p.fromZ != null ? p.fromZ : z - 6, z, eOut(k));
      walk = k < 1 ? 1 - k * 0.6 : 0;
    }
    const q = toCam(cam, [x, 0, z]);
    if (q[2] < NEAR + 0.5) continue;
    list.push({ p, q, walk, idx: pIdx });
    if (p.dribble && (walk > 0 || (p.action === 'run' && !p.path))) {   // he runs with the ball: a touch every other stride pushes it ahead
      const ph = ((lt / 0.84) % 1), push = Math.sin(ph * Math.PI), dirz = p.front ? -1 : 1, lead = 0.45 + 0.55 * push;
      const hx = p.path ? heading[0] : 0, hz = p.path ? heading[1] : dirz;   // the ball runs ahead in the direction he's going
      const side = p.foot === 'left' ? -0.18 : 0.18;   // ball on his stronger foot
      const bp = [x + side * hz + hx * lead, 0.11, z + hz * lead - side * hx];
      const bq = toCam(cam, bp);
      if (bq[2] > NEAR) list.push({ q: bq, dribbleBall: true, spin: lt * 12 });
    }
  }
  for (const o of list) {
    const s = proj(o.q);
    S.anchors[o.idx != null ? o.idx : players.indexOf(o.p)] = { x: s[0], y: s[1], u: FOC * 1.85 / o.q[2] };
  }
  // balls in the world (resting ball, shots) are drawn in depth order with the players, so they pass behind or in front correctly
  for (const it of S.cur ? S.cur.cards : []) {
    const c = it.obj, ct = S.t - it.start;
    if (ct < 0 || !(c.type === 'ball' || c.type === 'vehicle' || (c.type === 'ballpath' && c.world))) continue;
    if (c.type === 'ball' && c.until != null && ct >= c.until) continue;
    if (c.type === 'ballpath' && ct >= (c.dur || 1.6) && c.flash === false && c.saveBy == null) continue;
    const q = toCam(cam, c.type === 'ball' ? c.point : c.type === 'vehicle' ? vehicleWorld(c, ct) : ballWorld(c, ct));
    if (q[2] < NEAR) continue;
    list.push({ q, ball: c, ct });
  }
  list.sort((a, b) => b.q[2] - a.q[2]);
  drawShotMaps(cam);
  drawUnderPens();
  for (const o of list) {
    if (o.ball) { ctx.save(); CARDS[o.ball.type](o.ball, o.ct, W / 2, 0, 0); ctx.restore(); continue; }
    if (o.dribbleBall) {
      const s2 = proj(o.q), r = Math.max(3, FOC * 0.11 / o.q[2]);
      ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.beginPath(); ctx.ellipse(s2[0], s2[1] + r * 0.9, r * 1.3, r * 0.35, 0, 0, 7); ctx.fill();
      ctx.save(); ctx.translate(s2[0], s2[1]); ctx.rotate(o.spin); drawBall(0, 0, r); ctx.restore();
      continue;
    }
    const s = proj(o.q), u = FOC * 1.85 / o.q[2];
    const alpha = o.p.enter === 'fade' ? eOut(pr(lt, o.p.delay || 0, 0.5)) : 1;
    drawPlayer(s[0], s[1], u, o.p, lt, o.walk, alpha);
    S.anchors[players.indexOf(o.p)] = { x: s[0], y: s[1], u };
  }
}

function drawConfetti(lt, colors, seed) {
  const R = rng(seed);
  for (let i = 0; i < 190; i++) {
    const x0 = R() * W, sp = 140 + R() * 240, ph = R() * 6.28, delay = R() * 1.4, sz = 9 + R() * 12;
    const c = colors[Math.floor(R() * colors.length)];
    const tt = lt - delay;
    if (tt < 0) continue;
    const y = -40 + (tt * sp) % (H + 80);
    ctx.save();
    ctx.translate(x0 + Math.sin(tt * 2 + ph) * 40, y);
    ctx.rotate(tt * 3 + ph);
    ctx.scale(1, Math.cos(tt * 5 + ph));
    ctx.fillStyle = c;
    ctx.fillRect(-sz / 2, -sz / 4, sz, sz / 2);
    ctx.restore();
  }
}

// ---------- text ----------
function parseHL(s) {
  const out = [];
  let acc = false, space = false;
  for (const part of String(s).split(/(\[|\])/)) {
    if (part === '[') { acc = true; continue; }
    if (part === ']') { acc = false; continue; }
    for (const w of part.split(/(\s+)/)) {
      if (!w) continue;
      if (/^\s+$/.test(w)) { space = true; continue; }
      out.push({ w, acc, space: space && out.length > 0 });
      space = false;
    }
  }
  return out;
}
const HL = { size: 78, lh: 90, x: 80, y: 410, maxW: 920 };
function layoutHL(s) {
  font(700, HL.size, 'Inter', '-1.5px');
  const sp = ctx.measureText(' ').width, lines = [[]];
  let x = 0;
  for (const tk of parseHL(s)) {
    const w = ctx.measureText(tk.w).width, gap = tk.space ? sp : 0;
    if (tk.space && x + gap + w > HL.maxW && lines[lines.length - 1].length) { lines.push([]); x = 0; }
    else x += gap;
    lines[lines.length - 1].push({ ...tk, x });
    x += w;
  }
  return lines;
}
function drawHeadline(text, inT, outT, accent, wordT) {
  if (typeof toyOn === 'function' && toyOn()) return drawToyHeadline(text, inT, outT, accent, wordT);
  const lines = layoutHL(text);
  font(700, HL.size, 'Inter', '-1.5px');
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  const n = lines.reduce((m, l) => m + l.length, 0);
  let idx = 0;
  lines.forEach((line, li) => {
    const a = eOut(pr(inT, 0.05 + li * 0.08, 0.45));
    const o = outT != null ? pr(outT, 0, 0.22) : 0;
    ctx.save();
    ctx.globalAlpha = a * (1 - o);
    const y = HL.y + li * HL.lh + (1 - a) * 30 - o * 14;
    for (const tk of line) {
      if (wordT != null) {   // hook: the whole claim is readable on frame 0 (half of viewers decide in the first second, on mute);
        // each word then punches up in turn, roughly with the voice, so the text still moves
        const k = pr(wordT, 0.1 + idx * (1.4 / Math.max(1, n)), 0.3); idx++;
        const w = ctx.measureText(tk.w).width, pk = Math.sin(Math.PI * k), sc = 1 + 0.07 * pk;
        ctx.save();
        ctx.translate(HL.x + tk.x + w / 2, y - HL.size * 0.35); ctx.scale(sc, sc); ctx.translate(-(HL.x + tk.x + w / 2), -(y - HL.size * 0.35));
        ctx.fillStyle = tk.acc ? (accent || S.accent) : '#f4f2ec'; ctx.fillText(tk.w, HL.x + tk.x, y);
        if (!tk.acc && pk > 0) { ctx.globalAlpha *= 0.75 * pk; ctx.fillStyle = accent || S.accent; ctx.fillText(tk.w, HL.x + tk.x, y); }   // the word being said flashes
        ctx.restore(); continue;
      }
      ctx.fillStyle = tk.acc ? (accent || S.accent) : '#f4f2ec';
      ctx.fillText(tk.w, HL.x + tk.x, y);
    }
    ctx.restore();
  });
}
function drawKicker(text, a) {
  if (typeof toyOn === 'function' && toyOn()) return drawToyKicker(text, a);
  if (!text) return;
  ctx.save();
  ctx.globalAlpha = a;
  font(500, 23, 'Mono', '5px');
  ctx.fillStyle = '#8b919c'; ctx.textAlign = 'left';
  ctx.fillText('— ' + text.toUpperCase(), HL.x, HL.y - 92);
  ctx.restore();
}
// The channel's shirt logo: a blue shirt with yellow trim and a yellow 6 (user's choice). spec.brandShirt: [body, trim] overrides.
function drawBrandShirt(cx, cy, size) {
  const [body, trim] = S.spec.brandShirt || ['#1f4fd1', '#f7d117'];
  drawShirtIcon(cx, cy, size, body, null);
  ctx.save(); ctx.translate(cx, cy);
  const s = size;
  ctx.strokeStyle = trim; ctx.lineWidth = Math.max(2, s * 0.05); ctx.lineJoin = 'round';
  ctx.beginPath();   // outline trim, same path as drawShirtIcon
  ctx.moveTo(-s * 0.18, -s * 0.4); ctx.lineTo(-s * 0.5, -s * 0.22); ctx.lineTo(-s * 0.4, 0); ctx.lineTo(-s * 0.3, -s * 0.06);
  ctx.lineTo(-s * 0.3, s * 0.42); ctx.lineTo(s * 0.3, s * 0.42); ctx.lineTo(s * 0.3, -s * 0.06); ctx.lineTo(s * 0.4, 0);
  ctx.lineTo(s * 0.5, -s * 0.22); ctx.lineTo(s * 0.18, -s * 0.4); ctx.quadraticCurveTo(0, -s * 0.25, -s * 0.18, -s * 0.4);
  ctx.stroke();
  ctx.fillStyle = trim;   // collar and sleeve cuffs
  ctx.beginPath(); ctx.moveTo(-s * 0.18, -s * 0.4); ctx.quadraticCurveTo(0, -s * 0.25, s * 0.18, -s * 0.4); ctx.quadraticCurveTo(0, -s * 0.17, -s * 0.18, -s * 0.4); ctx.fill();
  font(900, s * 0.42, 'Inter'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = trim;
  ctx.fillText('6', 0, s * 0.1);
  ctx.restore();
}
function drawBrand() {
  if (typeof toyOn === 'function' && toyOn()) return drawToyBrand();
  const x = HL.x, y = 220, name = S.spec.brand || 'theo6k', st = S.spec.brandStyle || 'shirt', acc = S.accent;
  ctx.save(); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  if (st === 'pill') {   // frosted pill with a live dot and a small strapline
    font(800, 30, 'Inter', '-0.5px'); const tw = ctx.measureText(name).width;
    ctx.fillStyle = 'rgba(255,255,255,0.1)'; rrect(x - 6, y - 40, tw + 92, 58, 29); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.lineWidth = 2; rrect(x - 6, y - 40, tw + 92, 58, 29); ctx.stroke();
    ctx.fillStyle = acc; ctx.beginPath(); ctx.arc(x + 24, y - 11, 9, 0, 7); ctx.fill();
    ctx.fillStyle = '#f4f2ec'; ctx.fillText(name, x + 46, y);
    font(600, 16, 'Mono', '4px'); ctx.fillStyle = '#8b919c'; ctx.fillText('FOOTBALL STORIES', x + tw + 104, y - 3);
  } else if (st === 'ball') {   // a football as the "o", bold italic wordmark with an accent underline
    font(900, 40, 'Inter', '-1px'); ctx.fillStyle = '#f4f2ec';
    ctx.save(); ctx.translate(x, y); ctx.transform(1, 0, -0.18, 1, 0, 0);
    const pre = name.slice(0, name.indexOf('o')), post = name.slice(name.indexOf('o') + 1);
    ctx.fillText(pre.toUpperCase(), 0, 0); let w = ctx.measureText(pre.toUpperCase()).width;
    drawBall(w + 19, -14, 16); w += 40; ctx.fillStyle = '#f4f2ec'; ctx.fillText(post.toUpperCase(), w, 0); w += ctx.measureText(post.toUpperCase()).width;
    ctx.fillStyle = acc; ctx.fillRect(0, 10, w, 5);
    ctx.restore();
  } else if (st === 'shirt') {   // a shirt badge carrying the 6, then the name
    drawBrandShirt(x + 28, y - 14, 62);
    font(800, 34, 'Inter', '-0.5px'); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#f4f2ec'; ctx.fillText(name, x + 66, y);
  } else if (st === 'scoreboard') {   // broadcast score-bug: THEO | 6K with a live tab
    const h = 54, segs = [['THEO', '#141820', '#f4f2ec'], ['6K', acc, '#0d1016']];
    let cx = x; font(800, 28, 'Mono', '2px');
    for (const [t, bg, fg] of segs) { const w = ctx.measureText(t).width + 36; ctx.fillStyle = bg; ctx.fillRect(cx, y - 40, w, h); ctx.fillStyle = fg; ctx.fillText(t, cx + 18, y - 3); cx += w; }
    ctx.fillStyle = '#d6283b'; ctx.fillRect(cx, y - 40, 86, h); ctx.fillStyle = '#fff'; font(800, 18, 'Mono', '2px');
    ctx.beginPath(); ctx.arc(cx + 18, y - 13, 6, 0, 7); ctx.fill(); ctx.fillText('LIVE', cx + 30, y - 6);
  } else if (st === 'marker') {   // hand-drawn tactics-board marker, circled
    font(400, 46, 'Marker'); const tw = ctx.measureText(name).width;
    ctx.fillStyle = '#f4f2ec'; ctx.fillText(name, x + 8, y);
    ctx.strokeStyle = acc; ctx.lineWidth = 4; ctx.beginPath(); ctx.ellipse(x + 8 + tw / 2, y - 16, tw / 2 + 26, 36, -0.04, 0.15, Math.PI * 2 - 0.1); ctx.stroke();
  } else {   // classic: accent tile with a target, mono wordmark
    rrect(x, y - 30, 40, 40, 10); ctx.fillStyle = acc; ctx.fill();
    ctx.fillStyle = '#0d1016'; ctx.beginPath(); ctx.arc(x + 20, y - 10, 9, 0, 7); ctx.fill();
    ctx.fillStyle = acc; ctx.beginPath(); ctx.arc(x + 20, y - 10, 3.2, 0, 7); ctx.fill();
    font(700, 26, 'Mono', '1px'); ctx.fillStyle = '#d6dae1'; ctx.fillText(name, x + 54, y);
  }
  ctx.restore();
}

// ---------- cards ----------
const GOLD = ['#fff4c9', '#f1c453', '#b77d16'];
function cardY(c) {
  const y = c.y != null ? c.y : { top: 0.4, mid: 0.47, center: 0.55, low: 0.8 }[c.pos || 'mid'] * H;
  // Cards never sit on the headline (user: the date and points cards overlapped a two-line headline):
  // measure the card's real top edge once and push it down to leave a clear gap under the headline.
  if (S.hlBottom == null || NO_CLEAR.has(c.type) || c.clear === false) return y;
  const top = cardTop(c, y);
  return top == null || top > 900 ? y : Math.max(y, S.hlBottom + 56 + top);
}
const NO_CLEAR = new Set(['ball', 'ballpath', 'vehicle', 'pen', 'flytext', 'redcard', 'comments', 'shotmap', 'speedlines']);
let probeCtx = null;
function cardTop(c, y) {   // distance from the card's centre line up to its highest drawn pixel, in its settled state
  if (c._top !== undefined && c._topY === y) return c._top;
  c._topY = y; c._top = null;
  const fn = CARDS[c.type]; if (!fn) return null;
  if (!probeCtx) { const pc = document.createElement('canvas'); pc.width = W; pc.height = H; probeCtx = pc.getContext('2d', { willReadFrequently: true }); }
  const saved = ctx, savedHL = S.hlBottom; ctx = probeCtx; S.hlBottom = null;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
  const ct = c.hideT != null ? Math.max(0.5, Math.min(2.5, c.hideT - 0.05)) : 2.5;
  try { ctx.save(); fn(c, ct, W / 2 + (c.shiftX || 0), y, 0); ctx.restore(); } catch (e) { /* a card that can't draw offscreen just isn't moved */ }
  ctx = saved; S.hlBottom = savedHL;
  const rows = Math.max(1, Math.min(H, Math.floor(y))), d = probeCtx.getImageData(0, 0, W, rows).data;
  for (let yy = 0; yy < rows; yy++) for (let x = 0; x < W; x += 3) if (d[(yy * W + x) * 4 + 3] > 40) { c._top = y - yy; return c._top; }
  return c._top;
}
function cardBox(cx, cy, w, h, label) {
  rrect(cx - w / 2, cy - h / 2, w, h, 22);
  ctx.fillStyle = 'rgba(12,14,20,0.86)'; ctx.fill();
  ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,0.14)'; ctx.stroke();
  if (label) {
    font(500, 21, 'Mono', '5px');
    ctx.fillStyle = '#8d94a1'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.fillText(label.toUpperCase(), cx, cy - h / 2 + 46);
  }
}
function fmt(v, c) {
  const d = c.decimals || 0;
  let s = v.toFixed(d);
  if (c.comma) s = Number(s).toLocaleString('en-GB', { minimumFractionDigits: d, maximumFractionDigits: d });
  return (c.prefix || '') + s + (c.suffix || '');
}
function countVal(c, ct, start = 0.35, dur = 1.4) {
  return (c.from || 0) + ((c.value || 0) - (c.from || 0)) * eOut(pr(ct, start, dur));
}
function digitCell(x, y, w, h, v, place) {
  rrect(x, y, w, h, 10); ctx.fillStyle = '#1c2029'; ctx.fill();
  const dv = v / place, d = Math.floor(dv) % 10;
  let frac;
  if (place === 1) frac = dv - Math.floor(dv);
  else { const lower = v % place; frac = Math.max(0, lower - (place - 1)); }
  ctx.save();
  rrect(x, y, w, h, 10); ctx.clip();
  ctx.fillStyle = '#f4f2ec'; font(800, h * 0.68, 'Inter', '0px');
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(String(d), x + w / 2, y + h / 2 + 4 - frac * h);
  ctx.fillText(String((d + 1) % 10), x + w / 2, y + h / 2 + 4 + h - frac * h);
  ctx.restore();
  ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(x, y + h / 2 - 1, w, 2);
}

const CARDS = {
  flip(c, ct, cx, cy) {
    const cw = 100, ch = 136, g = 10, gg = 56;
    const widths = c.groups.map(gr => gr.digits * cw + (gr.digits - 1) * g);
    let total = widths.reduce((a, b) => a + b, 0) + gg * (c.groups.length - 1);
    if (c.side) total += 170;
    const bw = total + 100, bh = 320;
    cardBox(cx, cy, bw, bh, c.label);
    let x = cx - total / 2;
    const y = cy - ch / 2 + 10;
    c.groups.forEach((gr, i) => {
      const v = countVal({ value: gr.value, from: gr.from }, ct, 0.35 + i * 0.25, 1.5);
      for (let k = 0; k < gr.digits; k++) digitCell(x + k * (cw + g), y, cw, ch, v, Math.pow(10, gr.digits - 1 - k));
      font(500, 21, 'Mono', '5px'); ctx.fillStyle = '#8d94a1'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(gr.label.toUpperCase(), x + widths[i] / 2, y + ch + 44);
      x += widths[i] + gg;
    });
    if (c.side) {
      ctx.fillStyle = 'rgba(255,255,255,0.14)'; ctx.fillRect(x - gg + 30, y - 6, 2, ch + 12);
      const sx = x - gg + 30 + 85;
      ctx.textAlign = 'center';
      font(500, 22, 'Mono', '4px'); ctx.fillStyle = '#8d94a1';
      ctx.fillText(c.side.top || '', sx, y + 26);
      font(800, 58, 'Inter', '0px'); ctx.fillStyle = '#f4f2ec';
      ctx.fillText(c.side.big || '', sx, y + 92);
      font(500, 22, 'Mono', '4px'); ctx.fillStyle = '#8d94a1';
      ctx.fillText(c.side.bottom || '', sx, y + 132);
    }
  },
  big(c, ct, cx, cy) {
    const v = countVal(c, ct, 0.25, c.countDur || 1.3);
    const pop = 1 + 0.06 * Math.sin(Math.PI * pr(ct, 0.25 + (c.countDur || 1.3), 0.35));
    const size = c.size || 260;
    ctx.save();
    ctx.translate(cx, cy); ctx.scale(pop, pop);
    font(800, size, 'Inter', '-6px');
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const gold = c.style !== 'accent';
    const g = ctx.createLinearGradient(0, -size * 0.45, 0, size * 0.45);
    if (gold) { g.addColorStop(0, GOLD[0]); g.addColorStop(0.5, GOLD[1]); g.addColorStop(1, GOLD[2]); }
    else { g.addColorStop(0, shade(S.accent, 0.5)); g.addColorStop(1, S.accent); }
    ctx.shadowColor = gold ? 'rgba(241,196,83,0.45)' : rgba(S.accent, 0.45); ctx.shadowBlur = 50;
    ctx.fillStyle = g;
    ctx.fillText(fmt(v, c), 0, 0);
    ctx.restore();
    if (c.label) {
      font(600, 24, 'Mono', '6px'); ctx.fillStyle = '#c3c8d1'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(c.label.toUpperCase(), cx, cy + size * 0.55 + 20);
    }
  },
  vs(c, ct, cx, cy) {
    const n = c.items.length, colW = c.colW || 280, bw = colW * n + 60, bh = 330;
    cardBox(cx, cy, bw, bh, c.label);
    c.items.forEach((it, i) => {
      const x = cx - (colW * n) / 2 + colW * (i + 0.5);
      const v = countVal(it, ct, 0.35 + i * 0.3, 1.2);
      font(800, c.size || 140, 'Inter', '-3px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.fillStyle = it.accent ? S.accent : '#f4f2ec';
      ctx.fillText(fmt(v, it), x, cy + 62);
      font(500, 21, 'Mono', '5px'); ctx.fillStyle = '#8d94a1';
      ctx.fillText(it.label.toUpperCase(), x, cy + 118);
    });
  },
  table(c, ct, cx, cy) {
    if (c.scale && !c._scaling) { ctx.save(); ctx.translate(cx, cy); ctx.scale(c.scale, c.scale); c._scaling = true; try { CARDS.table(c, ct, 0, 0); } finally { c._scaling = false; ctx.restore(); } return; }
    const rows = c.rows, rh = 78, bw = 780, bh = 110 + rows.length * rh;
    cardBox(cx, cy, bw, bh, c.label);
    const top = cy - bh / 2 + 82;
    const mk = c.moveT != null ? ease(pr(ct, c.moveT, 0.9)) : 1;   // table climb: rows slide from fromRow to their place
    rows.forEach((r, i) => {
      const a = eOut(pr(ct, 0.25 + i * 0.12, 0.4)), slot = r.fromRow != null ? lerp(r.fromRow, i, mk) : i;
      ctx.save(); ctx.globalAlpha *= a;
      const y = top + slot * rh + rh / 2 + (1 - a) * 20, x0 = cx - bw / 2 + 50;
      if (r.highlight && r.fromRow != null && mk > 0 && mk < 1) { ctx.save(); ctx.globalAlpha *= 0.35 * Math.sin(Math.PI * mk); ctx.fillStyle = S.accent; rrect(cx - bw / 2 + 16, y - rh / 2 + 6, bw - 32, rh - 12, 14); ctx.fill(); ctx.restore(); }
      font(500, 26, 'Mono', '0px'); ctx.fillStyle = '#6f7684'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillText(String(r.fromPos != null && mk < 0.5 ? r.fromPos : r.pos), x0, y);
      drawShirtIcon(x0 + 70, y, 46, r.color || '#888', r.color2);
      font(700, 30, 'Mono', '3px'); ctx.fillStyle = '#eef0f3';
      ctx.fillText(r.name.toUpperCase(), x0 + 115, y);
      const v = c.moveT != null && r.from != null ? lerp(r.from, r.pts, mk) : countVal({ value: r.pts, from: r.from || 0 }, ct, 0.5, 1.3);
      font(800, 52, 'Inter', '0px'); ctx.textAlign = 'right';
      ctx.fillStyle = r.highlight ? S.accent : '#eef0f3';
      ctx.fillText(String(Math.round(v)), cx + bw / 2 - 50, y + 2);
      ctx.restore();
    });
    if (c.pill) {
      const k = pr(ct, c.moveT != null ? c.moveT + 1.0 : 1.9, 0.35), s = k > 0 ? eBack(k) : 0;
      if (s > 0) {
        const px = cx + bw / 2 - 200, py = top + (c.pillRow != null ? c.pillRow : 0.5) * rh + rh / 2;
        ctx.save(); ctx.translate(px, py); ctx.scale(s, s);
        rrect(-56, -28, 112, 56, 28); ctx.fillStyle = S.accent; ctx.fill();
        font(800, 32, 'Inter', '0px'); ctx.fillStyle = '#0d1016'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(c.pill, 0, 2);
        ctx.restore();
      }
    }
  },
  dots(c, ct, cx, cy) {
    const states = c.states || Array.from({ length: c.n }, (_, i) => (i < (c.filled != null ? c.filled : c.n) ? 'hit' : 'empty'));
    const per = Math.min(states.length, 10), rowsN = Math.ceil(states.length / per), sp = 70;
    const bw = Math.max(per * sp + 100, 640), bh = 210 + rowsN * sp;
    cardBox(cx, cy, bw, bh, c.label);
    const step = c.step || 0.17;
    states.forEach((st, i) => {
      const col = i % per, row = Math.floor(i / per);
      const x = cx - (per - 1) * sp / 2 + col * sp, y = cy - bh / 2 + 110 + row * sp;
      const k = pr(ct, 0.4 + i * step, 0.25), s = st === 'empty' ? 0 : eBack(k);
      ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,0.22)';
      ctx.beginPath(); ctx.arc(x, y, 24, 0, 7); ctx.stroke();
      if (s > 0) {
        ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
        if (st === 'miss') {
          ctx.strokeStyle = '#ff5a5a'; ctx.lineWidth = 6; ctx.lineCap = 'round';
          ctx.beginPath(); ctx.moveTo(-10, -10); ctx.lineTo(10, 10); ctx.moveTo(10, -10); ctx.lineTo(-10, 10); ctx.stroke();
        } else {
          ctx.fillStyle = S.accent; ctx.beginPath(); ctx.arc(0, 0, 24, 0, 7); ctx.fill();
        }
        ctx.restore();
      }
    });
    const hits = states.filter(s => s === 'hit').length;
    const shown = states.slice(0, Math.floor(clamp((ct - 0.4) / step + 1, 0, states.length))).filter(s => s === 'hit').length;
    font(800, 54, 'Inter', '0px'); ctx.fillStyle = S.accent; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.fillText(String(c.counter === false ? hits : shown), cx, cy + bh / 2 - 62);
    if (c.caption) {
      font(500, 21, 'Mono', '5px'); ctx.fillStyle = '#8d94a1';
      ctx.fillText(c.caption.toUpperCase(), cx, cy + bh / 2 - 26);
    }
  },
  bars(c, ct, cx, cy) {
    const rows = c.rows, rh = 96, bw = 820, bh = 110 + rows.length * rh;
    cardBox(cx, cy, bw, bh, c.label);
    const max = c.max || Math.max(...rows.map(r => r.value));
    const x0 = cx - bw / 2 + 50, trackX = x0 + 200, trackW = bw - 100 - 200 - 110;
    rows.forEach((r, i) => {
      const y = cy - bh / 2 + 100 + i * rh + rh / 2;
      const k = eOut(pr(ct, 0.4 + i * 0.35, 1.3));
      font(700, 28, 'Mono', '3px'); ctx.fillStyle = '#eef0f3'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillText(r.name.toUpperCase(), x0, y);
      rrect(trackX, y - 20, trackW, 40, 20); ctx.fillStyle = 'rgba(255,255,255,0.07)'; ctx.fill();
      const w = Math.max(40, trackW * (r.value / max) * k);
      rrect(trackX, y - 20, w, 40, 20); ctx.fillStyle = r.accent ? S.accent : (r.color || '#d6dae1'); ctx.fill();
      font(800, 46, 'Inter', '0px'); ctx.textAlign = 'right';
      ctx.fillStyle = r.accent ? S.accent : '#eef0f3';
      ctx.fillText(fmt(r.value * k, r), cx + bw / 2 - 45, y + 2);
    });
  },
  orb(c, ct, cx, cy) {
    const r = c.radius || 200, v = countVal(c, ct, 0.3, 1.8), lvl = v / 100;
    ctx.save();
    ctx.shadowColor = 'rgba(241,196,83,0.5)'; ctx.shadowBlur = 60;
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.fillStyle = '#2a1d08'; ctx.fill();
    ctx.restore();
    ctx.save();
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.clip();
    const surf = cy + r - 2 * r * lvl;
    const g = ctx.createLinearGradient(0, cy - r, 0, cy + r);
    g.addColorStop(0, GOLD[0]); g.addColorStop(0.45, GOLD[1]); g.addColorStop(1, GOLD[2]);
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(cx - r, cy + r);
    for (let x = -r; x <= r; x += 8) ctx.lineTo(cx + x, surf + Math.sin(x / 28 + ct * 4) * 7);
    ctx.lineTo(cx + r, cy + r); ctx.closePath(); ctx.fill();
    const hl = ctx.createRadialGradient(cx - r * 0.4, cy - r * 0.45, 0, cx - r * 0.4, cy - r * 0.45, r * 0.9);
    hl.addColorStop(0, 'rgba(255,255,255,0.35)'); hl.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = hl; ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    ctx.restore();
    ctx.lineWidth = 4; ctx.strokeStyle = '#e8bb4a'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.stroke();
    font(800, r * 0.62, 'Inter', '-3px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = '#fffaf0'; ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 16;
    ctx.fillText(fmt(v, { suffix: '%', ...c }), cx, cy + 6);
    ctx.shadowBlur = 0;
    if (c.label) {
      font(600, 22, 'Mono', '6px'); ctx.fillStyle = '#e8bb4a'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(c.label.toUpperCase(), cx, cy + r + 60);
    }
  },
};
function drawShirtIcon(x, y, s, c1, c2) {
  ctx.save(); ctx.translate(x, y);
  ctx.fillStyle = c1;
  ctx.beginPath();
  ctx.moveTo(-s * 0.18, -s * 0.4); ctx.lineTo(-s * 0.5, -s * 0.22); ctx.lineTo(-s * 0.4, 0); ctx.lineTo(-s * 0.3, -s * 0.06);
  ctx.lineTo(-s * 0.3, s * 0.42); ctx.lineTo(s * 0.3, s * 0.42); ctx.lineTo(s * 0.3, -s * 0.06); ctx.lineTo(s * 0.4, 0);
  ctx.lineTo(s * 0.5, -s * 0.22); ctx.lineTo(s * 0.18, -s * 0.4); ctx.quadraticCurveTo(0, -s * 0.25, -s * 0.18, -s * 0.4);
  ctx.fill();
  if (c2) { ctx.fillStyle = c2; ctx.fillRect(-s * 0.3, -s * 0.06, s * 0.6, s * 0.08); }
  ctx.restore();
}

function drawBall(x, y, r) {
  ctx.fillStyle = '#f4f4f2'; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
  ctx.fillStyle = '#1d1d22'; ctx.beginPath(); ctx.arc(x, y, r * 0.32, 0, 7); ctx.fill();
  for (let a = 0; a < 5; a++) {
    const an = a * 1.2566 - 1.57;
    ctx.beginPath(); ctx.arc(x + Math.cos(an) * r * 0.78, y + Math.sin(an) * r * 0.78, r * 0.2, 0, 7); ctx.fill();
  }
}
const ballPtsCache = new Map();
function ballPoints(text, size, step) {
  const key = text + '|' + size + '|' + step;
  if (ballPtsCache.has(key)) return ballPtsCache.get(key);
  const oc = document.createElement('canvas'), c2 = oc.getContext('2d');
  c2.font = `800 ${size}px Inter`;
  const w = Math.ceil(c2.measureText(text).width) + 20, h = Math.ceil(size * 1.1);
  oc.width = w; oc.height = h;
  c2.font = `800 ${size}px Inter`; c2.textBaseline = 'middle'; c2.fillStyle = '#fff';
  c2.fillText(text, 10, h / 2);
  const data = c2.getImageData(0, 0, w, h).data, pts = [];
  for (let y = step / 2; y < h; y += step) for (let x = step / 2; x < w; x += step) {
    if (data[(Math.floor(y) * w + Math.floor(x)) * 4 + 3] > 140) pts.push([x - w / 2, y - h / 2]);
  }
  ballPtsCache.set(key, pts);
  return pts;
}
// Props stand on (x, b) and are s px tall.
function drawProp(kind, x, b, s, text) {
  ctx.save();
  if (kind === 'cup') {
    const w = s / 1.69;
    drawTrophy(x, b - 0.57 * w, w / 0.2);
  } else if (kind === 'worldcup') {
    ctx.fillStyle = goldGrad(x - 0.22 * s, x + 0.22 * s);
    ctx.fillRect(x - 0.2 * s, b - 0.18 * s, 0.4 * s, 0.18 * s);
    ctx.fillStyle = '#2e7d4f';
    ctx.fillRect(x - 0.2 * s, b - 0.15 * s, 0.4 * s, 0.03 * s); ctx.fillRect(x - 0.2 * s, b - 0.08 * s, 0.4 * s, 0.03 * s);
    ctx.fillStyle = goldGrad(x - 0.22 * s, x + 0.22 * s);
    ctx.beginPath();
    ctx.moveTo(x - 0.17 * s, b - 0.18 * s);
    ctx.bezierCurveTo(x - 0.06 * s, b - 0.35 * s, x - 0.06 * s, b - 0.5 * s, x - 0.2 * s, b - 0.72 * s);
    ctx.lineTo(x + 0.2 * s, b - 0.72 * s);
    ctx.bezierCurveTo(x + 0.06 * s, b - 0.5 * s, x + 0.06 * s, b - 0.35 * s, x + 0.17 * s, b - 0.18 * s);
    ctx.closePath(); ctx.fill();
    const g = ctx.createRadialGradient(x - 0.06 * s, b - 0.88 * s, 0, x, b - 0.83 * s, 0.18 * s);
    g.addColorStop(0, '#fff3c4'); g.addColorStop(0.6, '#f1c453'); g.addColorStop(1, '#9a6a12');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, b - 0.83 * s, 0.17 * s, 0, 7); ctx.fill();
  } else if (kind === 'ball') {
    const r = 0.4 * s, cy = b - 0.55 * s;
    ctx.fillStyle = goldGrad(x - 0.15 * s, x + 0.15 * s); ctx.fillRect(x - 0.13 * s, b - 0.16 * s, 0.26 * s, 0.16 * s);
    const g = ctx.createRadialGradient(x - r * 0.35, cy - r * 0.4, 0, x, cy, r);
    g.addColorStop(0, '#fff6cf'); g.addColorStop(0.55, '#f1c453'); g.addColorStop(1, '#8a5c10');
    ctx.shadowColor = 'rgba(241,196,83,0.55)'; ctx.shadowBlur = 50;
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, cy, r, 0, 7); ctx.fill();
    ctx.shadowBlur = 0; ctx.strokeStyle = 'rgba(120,80,10,0.5)'; ctx.lineWidth = 2;
    for (const e of [0.35, 0.75]) { ctx.beginPath(); ctx.ellipse(x, cy, r * e, r, 0, 0, 7); ctx.stroke(); }
    ctx.beginPath(); ctx.ellipse(x, cy, r, r * 0.35, 0, 0, 7); ctx.stroke();
    if (text) {
      font(800, r * 1.1, 'Inter', '0px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = '#fffaf0'; ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 14;
      ctx.fillText(text, x, cy + 6);
    }
  } else if (kind === 'ballondor') {
    // The real trophy's shape: a gold ball with engraved panel seams, held by a short collar on a tapered gold pedestal.
    const r = 0.36 * s, baseH = 0.36 * s, cy = b - baseH - r * 0.92;
    const bw0 = 0.36 * s, bw1 = 0.2 * s;   // pedestal: wide foot, narrow top
    const pg = ctx.createLinearGradient(x - bw0, 0, x + bw0, 0);
    pg.addColorStop(0, '#7a520e'); pg.addColorStop(0.35, '#e9b949'); pg.addColorStop(0.55, '#fff0b8'); pg.addColorStop(1, '#8a5c10');
    ctx.fillStyle = pg;
    ctx.beginPath(); ctx.moveTo(x - bw0, b); ctx.lineTo(x + bw0, b); ctx.lineTo(x + bw1, b - baseH); ctx.lineTo(x - bw1, b - baseH); ctx.closePath(); ctx.fill();
    ctx.fillStyle = 'rgba(60,38,6,0.55)'; ctx.fillRect(x - bw0, b - 0.05 * s, bw0 * 2, 0.05 * s);              // foot plinth
    ctx.fillStyle = 'rgba(60,38,6,0.35)'; ctx.fillRect(x - bw1 * 1.35, b - baseH * 0.62, bw1 * 2.7, 0.018 * s);   // engraved line
    if (s > 90) { font(700, Math.max(7, 0.045 * s), 'Inter', `${0.01 * s}px`); ctx.fillStyle = 'rgba(70,45,8,0.75)'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText("BALLON D'OR", x, b - baseH * 0.38); }
    ctx.fillStyle = pg; ctx.beginPath(); ctx.ellipse(x, b - baseH, bw1 * 1.05, 0.03 * s, 0, 0, 7); ctx.fill();   // collar
    // the ball
    const g = ctx.createRadialGradient(x - r * 0.4, cy - r * 0.45, r * 0.05, x, cy, r);
    g.addColorStop(0, '#fff7d6'); g.addColorStop(0.35, '#f3cc62'); g.addColorStop(0.8, '#b98219'); g.addColorStop(1, '#6e4609');
    ctx.shadowColor = 'rgba(241,196,83,0.55)'; ctx.shadowBlur = 0.3 * s;
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, cy, r, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
    // engraved panels: a pentagon facing us, seams running out to the edge, and the next ring of panels
    ctx.save(); ctx.beginPath(); ctx.arc(x, cy, r, 0, 7); ctx.clip();
    ctx.strokeStyle = 'rgba(95,60,8,0.75)'; ctx.lineWidth = Math.max(1, 0.012 * s); ctx.lineJoin = 'round';
    const P = (rr, a0) => [...Array(5)].map((_, i) => [x + Math.cos(a0 + i * 1.2566) * rr, cy + Math.sin(a0 + i * 1.2566) * rr]);
    const inner = P(r * 0.3, -Math.PI / 2 + 0.15), outer = P(r * 0.78, -Math.PI / 2 + 0.15 + 0.628);
    ctx.beginPath(); inner.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py))); ctx.closePath(); ctx.stroke();
    inner.forEach(([px, py], i) => { const a = -Math.PI / 2 + 0.15 + i * 1.2566; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(x + Math.cos(a) * r * 0.58, cy + Math.sin(a) * r * 0.58); ctx.stroke(); });
    inner.forEach((_, i) => {   // hexagon edges between the seams
      const a = -Math.PI / 2 + 0.15 + i * 1.2566, a2 = a + 1.2566, m = [x + Math.cos(a) * r * 0.58, cy + Math.sin(a) * r * 0.58], m2 = [x + Math.cos(a2) * r * 0.58, cy + Math.sin(a2) * r * 0.58], o = outer[i];
      ctx.beginPath(); ctx.moveTo(...m); ctx.lineTo(...o); ctx.lineTo(...m2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(...o); ctx.lineTo(x + Math.cos(a + 0.628) * r * 1.05, cy + Math.sin(a + 0.628) * r * 1.05); ctx.stroke();
    });
    ctx.restore();
    ctx.fillStyle = 'rgba(255,255,240,0.55)'; ctx.beginPath(); ctx.ellipse(x - r * 0.38, cy - r * 0.45, r * 0.18, r * 0.1, -0.6, 0, 7); ctx.fill();   // shine
    if (text) {
      font(800, r * 1.0, 'Inter', '0px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = '#fffaf0'; ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 14; ctx.fillText(text, x, cy + 6);
    }
  } else if (kind === 'boot') {
    const P = [[-0.45, 0], [0.5, 0], [0.56, -0.08], [0.35, -0.18], [0.1, -0.22], [-0.05, -0.42], [-0.4, -0.45], [-0.47, -0.3]];
    ctx.fillStyle = goldGrad(x - 0.5 * s, x + 0.5 * s);
    ctx.shadowColor = 'rgba(241,196,83,0.45)'; ctx.shadowBlur = 40;
    ctx.beginPath(); P.forEach(([px, py], i) => (i ? ctx.lineTo(x + px * s, b + py * s) : ctx.moveTo(x + px * s, b + py * s))); ctx.closePath(); ctx.fill();
    ctx.shadowBlur = 0; ctx.fillStyle = '#7a520e';
    for (const sx of [-0.35, -0.2, 0.15, 0.3, 0.42]) ctx.fillRect(x + sx * s, b, 0.05 * s, 0.04 * s);
  }
  ctx.restore();
}
Object.assign(CARDS, {
  ballnumber(c, ct, cx, cy, ek) {
    const size = c.size || 380, step = c.step || 24, r = step * 0.6, R = rng(5);
    for (const [px, py] of ballPoints(String(c.text), size, step)) {
      const sx = (R() - 0.5) * W * 1.6, sy = (R() - 0.5) * H * 0.8 - 200, d = R() * 0.7, ang = R() * 6.28, sp = 200 + R() * 400;
      const k = eOut(pr(ct, 0.1 + d, 0.8));
      if (k <= 0) continue;
      let x = lerp(cx + sx, cx + px, k), y = lerp(cy + sy, cy + py, k);
      if (ek > 0) { x += Math.cos(ang) * sp * ek; y += Math.sin(ang) * sp * ek + 300 * ek * ek; }
      ctx.save(); ctx.globalAlpha *= Math.min(1, k * 1.5) * (1 - ek); drawBall(x, y, r); ctx.restore();
    }
    if (c.label) {
      let txt = c.label;
      if (c.count != null) txt = txt.replace('{n}', Math.round(countVal({ value: c.count, from: c.countFrom || 0 }, ct, 0.3, 1.6)));
      ctx.save(); ctx.globalAlpha *= (1 - ek) * eOut(pr(ct, 0.3, 0.4));
      font(600, 22, 'Mono', '5px'); ctx.fillStyle = '#e2d3ad'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(txt.toUpperCase(), cx, cy + size * 0.5 + 34);
      ctx.restore();
    }
  },
  balls(c, ct, cx, cy) {
    const r = c.r || 20, sp = r * 2.5, per = Math.min(c.n, c.per || 12), rows = Math.ceil(c.n / per);
    for (let i = 0; i < c.n; i++) {
      const k = pr(ct, 0.3 + i * (c.step || 0.12), 0.3);
      if (k <= 0) continue;
      const col = i % per, row = Math.floor(i / per), s = eBack(k);
      const x = cx - (per - 1) * sp / 2 + col * sp, y = cy - (rows - 1) * sp / 2 + row * sp;
      ctx.save(); ctx.translate(x, y); ctx.scale(s, s); drawBall(0, 0, r); ctx.restore();
    }
    if (c.label) {
      font(600, 22, 'Mono', '5px'); ctx.fillStyle = '#e2d3ad'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(c.label.toUpperCase(), cx, cy + rows * sp / 2 + 36);
    }
  },
  ruler(c, ct, cx, cy) {
    const w = c.width || 700, x0 = cx - w / 2, X = v => x0 + w * (v - c.min) / (c.max - c.min);
    const g = eOut(pr(ct, 0.1, 0.7));
    if (c.panel !== false) {
      rrect(x0 - 70, cy - 170, w + 140, 330, 24);
      ctx.fillStyle = 'rgba(14,7,8,0.72)'; ctx.fill();
    }
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (c.style === 'dots') {
      const n = c.n || 36;
      ctx.lineWidth = 2.5; ctx.strokeStyle = '#d9b45a';
      for (let i = 0; i < n && i / (n - 1) <= g; i++) { ctx.beginPath(); ctx.arc(lerp(x0, x0 + w, i / (n - 1)), cy, 7, 0, 7); ctx.stroke(); }
    } else {
      rrect(x0, cy - 9, Math.max(18, w * g), 18, 9); ctx.fillStyle = goldGrad(x0, x0 + w); ctx.fill();
    }
    const step = c.step || 1;
    font(500, 19, 'Mono', '2px'); ctx.fillStyle = '#b9a881';
    for (let v = c.min; v <= c.max + 1e-9; v += step) {
      const x = X(v);
      if (x > x0 + w * g + 1) break;
      ctx.fillRect(x - 1, cy + 12, 2, 12);
      ctx.fillText(c.fmt ? c.fmt.replace('{v}', v) : String(v), x, cy + 50);
    }
    (c.markers || []).forEach((m, i) => {
      const k = eOut(pr(ct, m.t != null ? m.t : 0.8 + i * 0.5, 0.4));   // markers can land on their words (at)
      if (k <= 0) return;
      const x = X(m.value), up = m.side !== 'below', len = (m.len || 80) * k, col = m.accent ? S.accent : '#e7eaef';
      ctx.save(); ctx.globalAlpha *= k;
      ctx.fillStyle = col; ctx.fillRect(x - 1.5, up ? cy - len : cy, 3, len);
      ctx.beginPath(); ctx.arc(x, cy, 10, 0, 7); ctx.fill();
      font(600, 20, 'Mono', '3px');
      const lines = String(m.label).toUpperCase().split('\n');
      const tw = Math.max(...lines.map(l => ctx.measureText(l).width)) + 28, th = 22 + lines.length * 26;
      const by = up ? cy - len - th : cy + len;
      const bx = clamp(x - tw / 2, 20, W - 20 - tw);
      rrect(bx, by, tw, th, 10); ctx.fillStyle = 'rgba(12,8,8,0.88)'; ctx.fill();
      ctx.strokeStyle = rgba(m.accent ? S.accent : '#ffffff', 0.35); ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = col;
      lines.forEach((l, li) => ctx.fillText(l, bx + tw / 2, by + 36 + li * 26));
      ctx.restore();
    });
    if (c.bracket) {
      const bk = c.bracket, k = eOut(pr(ct, 0.8 + (c.markers || []).length * 0.5, 0.5));
      if (k > 0) {
        const xa = X(bk.from), xb = lerp(xa, X(bk.to), k), y = cy + (bk.y || 40);
        ctx.strokeStyle = S.accent; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(xa, y - 12); ctx.lineTo(xa, y); ctx.lineTo(xb, y); ctx.lineTo(xb, y - 12); ctx.stroke();
        font(700, 22, 'Mono', '3px'); ctx.fillStyle = S.accent;
        ctx.globalAlpha *= pr(ct, 1.3 + (c.markers || []).length * 0.5, 0.3);
        ctx.fillText(bk.label.toUpperCase(), (xa + X(bk.to)) / 2, y + 34);
      }
    }
    for (const [lbl, x] of [[c.left, x0], [c.right, x0 + w]]) {
      if (!lbl) continue;
      font(700, 20, 'Mono', '3px'); ctx.fillStyle = '#e2d3ad';
      ctx.fillText(lbl.toUpperCase(), x, cy - 26);
    }
  },
  trophies(c, ct) {
    c.items.forEach((it, i) => {
      const k = eOut(pr(ct, 0.2 + i * (c.stagger != null ? c.stagger : 0.5), c.rise || 0.9));
      if (k <= 0) return;
      const x = (it.sx != null ? it.sx : 0.5) * W, base = c.floor || 1660, top = base - (it.h != null ? it.h : 420) * k, s = it.size || 170;
      if (it.h !== 0) {
        const g = ctx.createLinearGradient(x - 60, 0, x + 60, 0);
        g.addColorStop(0, '#140905'); g.addColorStop(0.5, '#3a2414'); g.addColorStop(1, '#140905');
        ctx.fillStyle = g; ctx.fillRect(x - 58, top, 116, base - top);
        ctx.fillStyle = goldGrad(x - 66, x + 66); ctx.fillRect(x - 66, top, 132, 12);
      }
      ctx.save(); ctx.globalAlpha *= k;
      drawProp(it.kind, x, top, s, it.text);
      if (it.label) {
        font(600, 20, 'Mono', '4px'); ctx.fillStyle = '#e2d3ad'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
        ctx.fillText(it.label.toUpperCase(), x, top - s - 22);
      }
      ctx.restore();
    });
  },
  meter(c, ct, cx, cy) {
    const x = cx + (c.dx != null ? c.dx : 300), h = c.height || 620, bot = cy + h / 2, top = cy - h / 2, max = c.max;
    const v = countVal(c, ct, 0.4, c.countDur || 2.2), cell = h / max;
    rrect(x - 24, top - 10, 48, h + 20, 24); ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.2)'; ctx.lineWidth = 2; ctx.stroke();
    for (let j = 0; j < Math.floor(v); j++) drawBall(x, bot - (j + 0.5) * cell, Math.min(17, cell * 0.46));
    for (const m of c.markers || []) {
      const y = bot - m.value * cell;
      ctx.setLineDash([6, 6]); ctx.strokeStyle = 'rgba(255,255,255,0.45)'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(x - 70, y); ctx.lineTo(x + 34, y); ctx.stroke(); ctx.setLineDash([]);
      font(600, 20, 'Mono', '3px'); ctx.fillStyle = '#e7eaef'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      ctx.fillText(`${m.label} ${m.value}`.toUpperCase(), x - 80, y);
    }
    font(800, 92, 'Inter', '-2px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = goldGrad(x - 60, x + 60); ctx.fillText(String(Math.floor(v)), x, top - 30);
    if (c.icon) {
      const ix = cx + (c.icon.dx != null ? c.icon.dx : -250), iy = cy + (c.icon.dy || 60);
      drawProp(c.icon.kind, ix, iy, c.icon.size || 200);
      if (c.icon.label) {
        font(600, 20, 'Mono', '4px'); ctx.fillStyle = '#e2d3ad'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
        String(c.icon.label).toUpperCase().split('\n').forEach((l, i) => ctx.fillText(l, ix, iy + 50 + i * 28));
      }
    }
  },
});
const FLAP_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
function flapCell(x, y, w, h, oldC, newC, lt, active, seed) {
  const dur = 0.42;
  let ch = newC, squash = 1;
  if (oldC !== newC && lt < dur) {
    if (lt < 0) ch = oldC;
    else {
      const step = Math.floor(lt * 28);
      ch = FLAP_CHARS[(seed * 7 + step * 13) % FLAP_CHARS.length];
      squash = 0.75 + 0.25 * Math.abs(Math.cos((lt * 28 % 1) * Math.PI));
    }
  }
  rrect(x, y, w, h, 6); ctx.fillStyle = active ? '#1d2129' : '#14171e'; ctx.fill();
  if (ch && ch !== ' ') {
    ctx.save();
    ctx.translate(x + w / 2, y + h / 2); ctx.scale(1, squash);
    font(700, h * 0.6, 'Mono', '0px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = active ? '#f6f3ea' : '#5d6472';
    ctx.fillText(ch, 0, 3);
    ctx.restore();
  }
  ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(x, y + h / 2 - 1, w, 2);
}
function boardText(r, nc, vc, useFrom) {
  const v = useFrom && r.from != null ? r.from : (r.prefix || '') + String(r.value);
  return { name: String(r.name).toUpperCase().padEnd(nc).slice(0, nc), val: String(v).padStart(vc).slice(-vc) };
}
function boardFocus(c, ct) {
  if (c.focusPath) {
    let f = c.focusPath[0].row;
    for (let i = 1; i < c.focusPath.length; i++) {
      const b = c.focusPath[i];
      f = lerp(f, b.row, ease(pr(ct, b.t, 0.4)));
    }
    return f;
  }
  if (c.focus == null) return null;
  const from = c._prev && c._prev.focus != null ? c._prev.focus : c.focus;
  return lerp(from, c.focus, ease(pr(ct, 0.15, 0.45)));
}
CARDS.board = function (c, ct, cx, cy) {
  const nc = c.cols || 9, vc = c.vcols || 4, cw = c.cell || 54, chh = c.cellH || 76, g = 6, rg = 14, mid = 34;
  const iw = (nc + vc) * (cw + g) - g + mid, bw = iw + 70, bh = 108 + c.rows.length * (chh + rg) + 6;
  rrect(cx - bw / 2, cy - bh / 2, bw, bh, 22);
  ctx.fillStyle = 'rgba(10,12,17,0.9)'; ctx.fill();
  ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.stroke();
  if (c.label) {
    font(600, 21, 'Mono', '6px'); ctx.fillStyle = c.labelColor || S.accent; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.fillText(c.label.toUpperCase(), cx, cy - bh / 2 + 46);
  }
  const x0 = cx - iw / 2, y0 = cy - bh / 2 + 76;
  const f = boardFocus(c, ct);
  if (f != null) {
    ctx.save();
    rrect(x0 - 14, y0 + f * (chh + rg) - 8, iw + 28, chh + 16, 12);
    ctx.shadowColor = rgba(S.accent, 0.6); ctx.shadowBlur = 24;
    ctx.lineWidth = 3.5; ctx.strokeStyle = S.accent; ctx.stroke();
    ctx.restore();
  }
  c.rows.forEach((r, i) => {
    const y = y0 + i * (chh + rg), active = f != null && Math.abs(f - i) < 0.5;
    const pr0 = c._prev && c._prev.rows[i];
    const old = pr0 ? boardText(pr0, nc, vc, false) : { name: ' '.repeat(nc), val: ' '.repeat(vc) };
    const first = boardText(r, nc, vc, true), fin = boardText(r, nc, vc, false);
    const rowT = ct - 0.15 - i * 0.07;
    for (let j = 0; j < nc; j++) flapCell(x0 + j * (cw + g), y, cw, chh, old.name[j], first.name[j], rowT - j * 0.025, active, i * 31 + j);
    const vx = x0 + nc * (cw + g) + mid - g;
    const corr = r.from != null || r.strike;
    const swapAt = c.swapAt || 1.5;
    for (let j = 0; j < vc; j++) {
      const cx2 = vx + j * (cw + g), seed = i * 17 + j + 100;
      if (corr && ct - swapAt - j * 0.04 >= 0) {
        const before = r.from != null ? first.val : old.val;
        flapCell(cx2, y, cw, chh, before[j], fin.val[j], ct - swapAt - j * 0.04, active, seed);
      } else {
        flapCell(cx2, y, cw, chh, old.val[j], first.val[j], rowT - (nc + j) * 0.025, active, seed);
      }
    }
    if (corr) {
      const k = pr(ct, swapAt - 0.6, 0.3), fade = 1 - pr(ct, swapAt, 0.2);
      if (k > 0 && fade > 0) {
        ctx.save(); ctx.globalAlpha *= fade;
        ctx.strokeStyle = '#ff4d5e'; ctx.lineWidth = 5; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(vx - 6, y + chh * 0.62); ctx.lineTo(vx - 6 + (vc * (cw + g) + 6) * k, y + chh * 0.38); ctx.stroke();
        ctx.restore();
      }
    }
    if (r.delta) {
      const k = pr(ct, swapAt + 0.35, 0.3);
      if (k > 0) {
        ctx.save(); ctx.translate(vx + vc * (cw + g) - 50, y - 4); ctx.scale(eBack(k), eBack(k));
        font(800, 26, 'Inter', '0px'); ctx.fillStyle = '#ff4d5e'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(r.delta, 0, 0);
        ctx.restore();
      }
    }
  });
  if (c.caption) {
    const k = pr(ct, c.captionAt != null ? c.captionAt : 2.0, 0.35);
    if (k > 0) {
      ctx.save(); ctx.globalAlpha *= k; ctx.translate(0, (1 - eOut(k)) * 14);
      font(700, 21, 'Mono', '4px');
      const tw = ctx.measureText(c.caption.toUpperCase()).width + 44, py = cy + bh / 2 + 34;
      rrect(cx - tw / 2, py - 22, tw, 44, 22); ctx.fillStyle = 'rgba(10,12,17,0.92)'; ctx.fill();
      ctx.strokeStyle = rgba(S.accent, 0.6); ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = '#f0e6c8'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(c.caption.toUpperCase(), cx, py + 1);
      ctx.restore();
    }
  }
};
// Draws pen strokes marked layer "under" (e.g. a ring on the grass) before the players, so legs and cards sit on top.
function drawUnderPens() {
  const b = S.cur;
  if (!b) return;
  for (const it of b.cards) {
    const web = it.obj.type === 'passweb' || it.obj.type === 'varlines';
    if (!web && (it.obj.type !== 'pen' || !it.obj.strokes.some(s => s.layer === 'under'))) continue;
    const ct = S.t - it.start;
    if (ct < 0 || (it.obj.hideT != null && ct >= it.obj.hideT)) continue;   // hideAt applies to grass layers too
    ctx.save();
    it.obj._under = true; CARDS[it.obj.type](it.obj, ct); it.obj._under = false;
    ctx.restore();
  }
}
// TV-analysis pen: marker strokes that draw themselves on over the shot (screen px, 1080x1920).
// strokes: [{kind: ellipse|arrow|line|x|text, t, dur, color, width, ...}]
function penPoints(s) {
  const R = rng(s.seed || 7), pts = [];
  if (s.kind === 'ellipse') {
    const turns = s.turns || 1.12, a0 = s.start != null ? s.start : -1.9;
    for (let i = 0; i <= 80 * turns; i++) {
      const a = a0 + i / 80 * Math.PI * 2, k = 1 + (R() - 0.5) * 0.03 + i * 0.0009;
      pts.push([s.cx + Math.cos(a) * s.rx * k, s.cy + Math.sin(a) * s.ry * k]);
    }
  } else if (s.kind === 'x') {
    const r = s.r || 60;
    return [[[s.cx - r, s.cy - r], [s.cx + r, s.cy + r]], [[s.cx + r, s.cy - r], [s.cx - r, s.cy + r]]];
  } else {
    const P = s.points, n = 40;
    for (let i = 0; i < P.length - 1; i++) {
      for (let j = 0; j < n; j++) {
        const u = j / n;
        if (P.length === 3) {
          const t = (i + u) / 2, a = P[0], b = P[1], c = P[2];
          pts.push([(1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]]);
        } else pts.push([lerp(P[i][0], P[i + 1][0], u), lerp(P[i][1], P[i + 1][1], u)]);
      }
      if (P.length === 3) break;
    }
    pts.push(P[P.length - 1]);
  }
  return [pts];
}
function markerPath(pts, k, col, w, dash) {
  const m = Math.max(2, Math.floor(pts.length * k));
  for (const [pass, a, lw] of [[0, 0.5, w * 1.8], [1, 0.95, w]]) {
    ctx.save();
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = col; ctx.globalAlpha *= a; ctx.lineWidth = lw;
    if (pass === 0) { ctx.shadowColor = col; ctx.shadowBlur = 18; }
    if (dash) ctx.setLineDash(dash);
    ctx.beginPath(); for (let i = 0; i < m; i++) i ? ctx.lineTo(...pts[i]) : ctx.moveTo(...pts[i]); ctx.stroke();
    ctx.restore();
  }
  return pts[m - 1];
}
function anchorStroke(s, a) {
  const P = ([dx, dy]) => [a.x + dx * a.u, a.y + dy * a.u];
  const o = { ...s };
  if (s.cx != null) [o.cx, o.cy] = P([s.cx, s.cy]);
  if (s.rx != null) { o.rx = s.rx * a.u; o.ry = s.ry * a.u; }
  if (s.r != null) o.r = s.r * a.u;
  if (s.points) o.points = s.points.map(P);
  if (s.x != null) [o.x, o.y] = P([s.x, s.y]);
  if (s.size != null && s.size < 5) o.size = s.size * a.u;   // anchored text: size in player-heights too
  return o;
}
CARDS.pen = function (c, ct) {
  const a = c.anchor != null ? S.anchors[c.anchor] : null;
  if (c.anchor != null && !a) return;
  for (const s0 of c.strokes) {
    if ((s0.layer === 'under') !== !!c._under) continue;
    const s = a ? anchorStroke(s0, a) : s0;
    const k = eOut(pr(ct, s.t || 0, s.dur || 0.6));
    if (k <= 0) continue;
    const col = s.color || '#ffe14d', w = s.width || 9;
    if (s.kind === 'text') {
      ctx.save();
      ctx.translate(s.x, s.y); ctx.rotate(s.rot || -0.08);
      font(400, s.size || 64, 'Marker', '1px'); ctx.textAlign = s.align || 'left'; ctx.textBaseline = 'alphabetic';
      const tw = ctx.measureText(s.text).width, x0 = s.align === 'center' ? -tw / 2 : 0;
      ctx.beginPath(); ctx.rect(x0 - 10, -(s.size || 64) * 1.2, (tw + 20) * k, (s.size || 64) * 1.6); ctx.clip();
      ctx.lineJoin = 'round'; ctx.lineWidth = (s.size || 64) * 0.18; ctx.strokeStyle = 'rgba(8,10,14,0.85)'; ctx.strokeText(s.text, 0, 0);
      ctx.shadowColor = col; ctx.shadowBlur = 16; ctx.fillStyle = col; ctx.fillText(s.text, 0, 0);
      ctx.restore();
      continue;
    }
    const paths = penPoints(s);
    if (s.kind === 'x') {
      markerPath(paths[0], Math.min(1, k * 2), col, w);
      if (k > 0.5) markerPath(paths[1], (k - 0.5) * 2, col, w);
      continue;
    }
    const tip = markerPath(paths[0], k, col, w, s.dashed ? [2, w * 2.4] : null);
    if (s.kind === 'arrow' && k > 0.97) {
      const p = paths[0], a = p[p.length - 1], b = p[p.length - 6];
      const ang = Math.atan2(a[1] - b[1], a[0] - b[0]), L = w * 4.2;
      markerPath([[a[0] - Math.cos(ang - 0.55) * L, a[1] - Math.sin(ang - 0.55) * L], a, [a[0] - Math.cos(ang + 0.55) * L, a[1] - Math.sin(ang + 0.55) * L]], 1, col, w);
    }
  }
};
CARDS.pen.noSlide = true;

// Receipt that prints line by line (money stories). lines: [[label, value, accent?]], total: [label, value].
CARDS.receipt = function (c, ct, cx, cy) {
  const w = c.w || 640, lh = 64, lines = c.lines || [], step = c.step || 0.45;
  const fullH = 210 + lines.length * lh + (c.total ? 130 : 0) + 120;
  const shown = Math.min(lines.length + (c.total ? 1 : 0) + 1, (ct - 0.2) / step + 1);
  const h = Math.max(150, Math.min(fullH, 200 + Math.max(0, shown) * lh + (shown > lines.length ? 140 : 0)));
  const top = cy - fullH / 2;
  ctx.save();
  ctx.translate(cx, top); ctx.rotate(c.tilt != null ? c.tilt : -0.025);
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12;
  ctx.fillStyle = '#f6f3ec';
  ctx.beginPath(); ctx.moveTo(-w / 2, 0); ctx.lineTo(w / 2, 0); ctx.lineTo(w / 2, h);
  for (let x = w / 2; x > -w / 2; x -= 20) { ctx.lineTo(x - 10, h + 12); ctx.lineTo(x - 20, h); }
  ctx.closePath(); ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.beginPath(); ctx.rect(-w / 2, 0, w, h); ctx.clip();
  const ink = '#1d1c1a';
  ctx.fillStyle = ink; ctx.textBaseline = 'alphabetic';
  font(800, 40, 'Mono', '2px'); ctx.textAlign = 'center'; ctx.fillText((c.title || 'RECEIPT').toUpperCase(), 0, 76);
  font(500, 20, 'Mono', '2px'); ctx.fillText((c.sub || '').toUpperCase(), 0, 112);
  const dash = y => { ctx.setLineDash([8, 7]); ctx.strokeStyle = 'rgba(29,28,26,0.6)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(-w / 2 + 30, y); ctx.lineTo(w / 2 - 30, y); ctx.stroke(); ctx.setLineDash([]); };
  dash(140);
  lines.forEach((ln, i) => {
    const y = 200 + i * lh;
    if (i + 1 > shown) return;
    font(600, 26, 'Mono', '1px'); ctx.textAlign = 'left'; ctx.fillStyle = ink; ctx.fillText(String(ln[0]).toUpperCase(), -w / 2 + 34, y);
    font(800, 30, 'Mono', '1px'); ctx.textAlign = 'right'; ctx.fillStyle = ln[2] ? '#c41e2e' : ink; ctx.fillText(String(ln[1]), w / 2 - 34, y);
  });
  if (c.total && shown > lines.length) {
    const y = 200 + lines.length * lh + 10;
    dash(y - 30);
    font(800, 30, 'Mono', '2px'); ctx.textAlign = 'left'; ctx.fillStyle = ink; ctx.fillText(String(c.total[0]).toUpperCase(), -w / 2 + 34, y + 30);
    font(900, 56, 'Inter', '0px'); ctx.textAlign = 'right'; ctx.fillStyle = '#c41e2e'; ctx.fillText(String(c.total[1]), w / 2 - 34, y + 40);
    for (let i = 0, x = -w / 2 + 60; x < w / 2 - 60; i++) { const bw = 2 + ((i * 7) % 5); ctx.fillStyle = ink; ctx.fillRect(x, y + 80, bw, 50); x += bw + 3 + ((i * 3) % 4); }
  }
  ctx.restore();
};
CARDS.receipt.noSlide = true;

// Rubber stamp that slams down over the frame ("GUILTY", "APPEALED").
CARDS.stamp = function (c, ct, cx, cy) {
  const k = pr(ct, 0, 0.18);
  if (k <= 0) return;
  const sc = lerp(2.6, 1, eOut(k)), shake = k >= 1 ? Math.max(0, 1 - (ct - 0.18) / 0.25) * 8 * Math.sin(ct * 90) : 0;
  const col = c.color || '#d6283b', size = c.size || 120;
  ctx.save();
  ctx.translate(cx + (c.dx || 0) + shake, cy + shake * 0.5); ctx.rotate(c.rot != null ? c.rot : -0.16); ctx.scale(sc, sc);
  ctx.globalAlpha *= Math.min(1, k * 1.6) * 0.92;
  font(900, size, 'Inter', '6px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const tw = ctx.measureText(c.text).width + 70, th = size * 1.25;
  ctx.strokeStyle = col; ctx.lineWidth = 10; rrect(-tw / 2, -th / 2, tw, th, 18); ctx.stroke();
  ctx.lineWidth = 3; rrect(-tw / 2 + 14, -th / 2 + 14, tw - 28, th - 28, 10); ctx.stroke();
  ctx.fillStyle = col; ctx.fillText(c.text, 0, 6);
  if (c.sub) { font(800, size * 0.22, 'Mono', '4px'); ctx.fillText(c.sub.toUpperCase(), 0, th / 2 + size * 0.28); }
  ctx.globalCompositeOperation = 'destination-out';
  const R = rng(13);
  for (let i = 0; i < 260; i++) { ctx.fillStyle = `rgba(0,0,0,${0.3 + R() * 0.5})`; ctx.beginPath(); ctx.arc((R() - 0.5) * tw, (R() - 0.5) * th, 1 + R() * 3, 0, 7); ctx.fill(); }
  ctx.restore();
};
CARDS.stamp.noSlide = true;

// Team sheet (backlog "formation" item, built): a pitch card where the players pop into formation one by one, with an optional empty,
// pulsing slot for the man left out. {type: "lineup", title, items: [{name, x, y, color, text, t|at}], empty: {x, y, label, t|at}, w, instant}
// x, y are 0–1 on the pitch (y 0 = attacking end at the top).
CARDS.lineup = function (c, ct, cx, cy) {
  const w = c.w || 800, h = w * 1.22, k = eBack(pr(ct, 0, 0.45)), sc = w / 800;
  if (k <= 0) return;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(k * (1 + 0.012 * ct), k * (1 + 0.012 * ct)); ctx.rotate(c.tilt != null ? c.tilt : -0.015);
  ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 16;
  ctx.fillStyle = '#12301c'; rrect(-w / 2, -h / 2, w, h, 26 * sc); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.save(); rrect(-w / 2, -h / 2, w, h, 26 * sc); ctx.clip();
  for (let i = 0; i < 8; i++) { ctx.fillStyle = i % 2 ? '#1f6b3a' : '#237a41'; ctx.fillRect(-w / 2, -h / 2 + i * h / 8, w, h / 8); }
  ctx.strokeStyle = 'rgba(255,255,255,0.55)'; ctx.lineWidth = 4 * sc; const m = 26 * sc;
  ctx.strokeRect(-w / 2 + m, -h / 2 + m, w - 2 * m, h - 2 * m);
  ctx.strokeRect(-w * 0.28, -h / 2 + m, w * 0.56, h * 0.15); ctx.strokeRect(-w * 0.12, -h / 2 + m, w * 0.24, h * 0.055);
  ctx.beginPath(); ctx.arc(0, h / 2 - m, w * 0.16, Math.PI, 2 * Math.PI); ctx.stroke();
  ctx.restore();
  if (c.title) { font(800, 30 * sc, 'Inter', `${3 * sc}px`); const tw = ctx.measureText(c.title.toUpperCase()).width + 44 * sc;
    ctx.fillStyle = '#0d1016'; rrect(-tw / 2, -h / 2 - 30 * sc, tw, 60 * sc, 30 * sc); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.title.toUpperCase(), 0, -h / 2 + 2 * sc); }
  const r = (c.r || 40) * sc;
  (c.items || []).forEach((it, i) => {
    const tt = it.t != null ? it.t : 0.25 + i * 0.07; if (!c.instant && ct <= tt) return;
    const pk = c.instant ? 1 : eBack(pr(ct, tt, 0.28));
    const x = (it.x - 0.5) * (w - 2 * m), y = (it.y - 0.5) * (h - 2 * m), hot = !c.instant && it.t != null && ct - it.t < 0.9;
    ctx.save(); ctx.translate(x, y + Math.sin(ct * 2 + i) * 2 * sc); ctx.scale(pk, pk);
    if (hot) { ctx.strokeStyle = '#f1c453'; ctx.lineWidth = 5 * sc; ctx.globalAlpha = 1 - (ct - it.t) / 0.9; ctx.beginPath(); ctx.arc(0, 0, r + (ct - it.t) * 60 * sc, 0, 7); ctx.stroke(); ctx.globalAlpha = 1; }
    ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.beginPath(); ctx.arc(2 * sc, 5 * sc, r, 0, 7); ctx.fill();
    ctx.fillStyle = it.color || '#f4f4f2'; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 3 * sc; ctx.beginPath(); ctx.arc(0, 0, r - 5 * sc, 0, 7); ctx.stroke();
    font(700, 21 * sc, 'Inter'); const nw = ctx.measureText(it.name).width + 22 * sc;
    ctx.fillStyle = 'rgba(13,16,22,0.92)'; rrect(-nw / 2, r + 6 * sc, nw, 32 * sc, 16 * sc); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(it.name, 0, r + 23 * sc);
    ctx.restore();
  });
  if (c.empty) { const e = c.empty, ek = c.instant && e.t == null ? 1 : eBack(pr(ct, e.t != null ? e.t : 1.2, 0.3));
    if (ek > 0) { const x = (e.x - 0.5) * (w - 2 * m), y = (e.y - 0.5) * (h - 2 * m), pu = 1 + 0.1 * Math.sin(ct * 7);
      ctx.save(); ctx.translate(x, y); ctx.scale(ek * pu, ek * pu);
      ctx.fillStyle = 'rgba(214,40,59,0.22)'; ctx.beginPath(); ctx.arc(0, 0, r * 1.15, 0, 7); ctx.fill();
      ctx.setLineDash([10 * sc, 8 * sc]); ctx.strokeStyle = '#ff4d5e'; ctx.lineWidth = 5 * sc; ctx.beginPath(); ctx.arc(0, 0, r * 1.15, 0, 7); ctx.stroke(); ctx.setLineDash([]);
      font(800, 44 * sc, 'Inter'); ctx.fillStyle = '#ff4d5e'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('?', 0, 3 * sc);
      if (e.label) { font(800, 23 * sc, 'Inter', `${2 * sc}px`); const nw = ctx.measureText(e.label.toUpperCase()).width + 26 * sc;
        ctx.fillStyle = '#d6283b'; rrect(-nw / 2, r * 1.15 + 8 * sc, nw, 36 * sc, 18 * sc); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillText(e.label.toUpperCase(), 0, r * 1.15 + 27 * sc); }
      ctx.restore(); } }
  ctx.restore();
};
CARDS.lineup.noSlide = true;

// Ballot box: voting slips fly in and drop through the slot while the box bounces. {type: "ballot", title, sub, color, n, dur, shiftX}
CARDS.ballot = function (c, ct, cx, cy) {
  const k = eBack(pr(ct, 0, 0.4)), col = c.color || '#f1c453', n = c.n || 16, dur = c.dur || 2.2, bw = c.w || 340, bh = bw * 0.8;
  if (k <= 0) return;
  let bounce = 0; const R = rng(c.seed || 12);
  ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k);
  const slips = [];
  for (let i = 0; i < n; i++) { const t0 = 0.35 + i / n * dur, a = (ct - t0) / 0.55, sx = (R() - 0.5) * 700, sy = -520 - R() * 260, rot = (R() - 0.5) * 2;
    if (a > 0 && a < 1) slips.push({ a, sx, sy, rot }); if (a >= 1 && a < 1.3) bounce = Math.max(bounce, 1 - (a - 1) / 0.3); }
  for (const sl of slips) { const e = sl.a * sl.a, x = lerp(sl.sx, 0, eOut(sl.a)), y = lerp(sl.sy, -bh / 2 - 6, e);
    ctx.save(); ctx.translate(x, y); ctx.rotate(sl.rot * (1 - sl.a)); ctx.scale(1, lerp(1, 0.35, pr(sl.a, 0.8, 0.2)));
    ctx.fillStyle = '#f7f3e8'; rrect(-52, -36, 104, 72, 8); ctx.fill();
    ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-20, 0); ctx.lineTo(-6, 14); ctx.lineTo(22, -16); ctx.stroke(); ctx.restore(); }
  ctx.translate(0, bounce * 8);
  ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 36; ctx.shadowOffsetY = 14;
  ctx.fillStyle = '#171a22'; rrect(-bw / 2, -bh / 2, bw, bh, 22); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = col; rrect(-bw / 2, -bh / 2, bw, 26, 13); ctx.fill();
  ctx.fillStyle = '#05060a'; rrect(-bw * 0.3, -bh / 2 + 6, bw * 0.6, 12, 6); ctx.fill();
  font(800, 40, 'Inter', '1px'); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText((c.title || 'VOTES').toUpperCase(), 0, -6);
  if (c.sub) { font(600, 23, 'Mono', '3px'); ctx.fillStyle = col; ctx.fillText(c.sub.toUpperCase(), 0, 50); }
  ctx.restore();
};
CARDS.ballot.noSlide = true;

// Photo finish: two bars race to a chequered line with the numbers counting; the loser stops just short and the gap is called out.
// {type: "photofinish", title, rows: [{name, value, color}] (winner first or second, either), floor, dur, suffix: "%", decimals: 1, gap: "0.8%", gapT|gapAt}
CARDS.photofinish = function (c, ct, cx, cy) {
  const w = c.w || 960, rows = c.rows, rh = 150, h = rows.length * rh + 130, k = eOut(pr(ct, 0, 0.4)), dur = c.dur || 1.8, dec = c.decimals != null ? c.decimals : 1;
  const mx = Math.max(...rows.map(r => r.value)), fl = c.floor != null ? c.floor : mx * 0.9, x0 = -w / 2 + 40, L = w - 270, t0 = 0.35;
  const gT = c.gapT != null ? c.gapT : t0 + dur + 0.25, done = ct > t0 + dur;
  ctx.save(); ctx.globalAlpha *= k; ctx.translate(cx, cy + (1 - k) * 40);
  ctx.fillStyle = 'rgba(8,10,15,0.82)'; rrect(-w / 2, -h / 2, w, h, 26); ctx.fill();
  if (c.title) { font(600, 24, 'Mono', '5px'); ctx.fillStyle = '#c9ced6'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.title.toUpperCase(), 0, -h / 2 + 46); }
  const fx = x0 + L;   // finish line
  for (let i = 0; i < Math.ceil((h - 110) / 16); i++) for (let j = 0; j < 2; j++) { ctx.fillStyle = (i + j) % 2 ? '#fff' : '#111'; ctx.fillRect(fx + j * 16, -h / 2 + 84 + i * 16, 16, 16); }
  const tips = [];
  rows.forEach((r, i) => {
    const y = -h / 2 + 100 + i * rh + rh / 2, frac = clamp((r.value - fl) / (mx - fl), 0, 1), e = ease(pr(ct, t0, dur));
    const wob = done ? 0 : Math.sin(ct * 9 + i * 2) * 0.012 * (1 - e), len = L * clamp(e * (0.25 + 0.75 * frac) + wob + (e >= 1 ? 0 : 0), 0, 1) * (e < 1 ? 1 : 1);
    const full = L * (0.25 + 0.75 * frac), cur = Math.min(full, Math.max(0, len / (0.25 + 0.75 * frac) * (0.25 + 0.75 * frac)));
    font(800, 34, 'Inter'); ctx.fillStyle = '#f4f2ec'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(r.name, x0, y - 44);
    ctx.fillStyle = 'rgba(255,255,255,0.08)'; rrect(x0, y - 16, L, 44, 22); ctx.fill();
    ctx.fillStyle = r.color || '#6cabdd'; rrect(x0, y - 16, Math.max(44, cur), 44, 22); ctx.fill();
    drawBall(x0 + Math.max(44, cur) - 4, y + 6, 26);
    font(800, 44, 'Inter', '-1px'); ctx.textAlign = 'right'; ctx.fillStyle = done && r.value === mx ? '#f1c453' : '#f4f2ec';
    ctx.fillText((r.value * e).toFixed(dec) + (c.suffix != null ? c.suffix : '%'), w / 2 - 30, y + 8);
    tips.push([x0 + Math.max(44, cur), y + 6]);
  });
  if (done) { const fk = 1 - pr(ct, t0 + dur, 0.35); if (fk > 0) { ctx.fillStyle = `rgba(255,255,255,${0.6 * fk})`; rrect(-w / 2, -h / 2, w, h, 26); ctx.fill(); } }
  if (c.gap && ct >= gT && tips.length > 1) { const gk = eBack(pr(ct, gT, 0.3)), a = tips.reduce((p, q) => p[0] < q[0] ? p : q), bx = (a[0] + fx) / 2 + 14, pu = 1 + 0.08 * Math.sin(ct * 8);
    ctx.strokeStyle = '#ff4d5e'; ctx.lineWidth = 6; ctx.setLineDash([8, 8]); ctx.beginPath(); ctx.moveTo(a[0] + 22, a[1] - 60); ctx.lineTo(a[0] + 22, a[1] + 60); ctx.stroke(); ctx.setLineDash([]);
    ctx.save(); ctx.translate(bx + 10, a[1]); ctx.scale(gk * pu, gk * pu); font(900, 46, 'Inter'); const tw = ctx.measureText(c.gap).width + 40;
    ctx.fillStyle = '#d6283b'; rrect(-tw / 2, -32, tw, 64, 14); ctx.fill(); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.gap, 0, 3); ctx.restore(); }
  ctx.restore();
};
CARDS.photofinish.noSlide = true;

// Cross-off calendar (backlog item, built): a wall-calendar month whose days get crossed off one by one, for bans, suspensions, waits and countdowns.
// {type: "crossoff", title: "SUSPENDED", days: 30, cols: 6, crossT|crossAt (when the crossing starts), dur (s for all days), color, caption ("{n} days")}
CARDS.crossoff = function (c, ct, cx, cy) {
  const days = c.days || 30, cols = c.cols || 6, rows = Math.ceil(days / cols), cell = c.cell || 104, w = cols * cell + 60, hh = 120, h = hh + rows * cell + 140;
  const k = eBack(pr(ct, 0, 0.45)), col = c.color || '#d6283b', t0 = c.crossT != null ? c.crossT : 0.5, dur = c.dur || 1.6;
  if (k <= 0) return;
  const done = Math.floor(clamp((ct - t0) / dur, 0, 1) * days), fin = ct > t0 + dur, sh = fin ? Math.max(0, 1 - (ct - t0 - dur) / 0.3) * 7 * Math.sin(ct * 80) : 0;
  ctx.save(); ctx.translate(cx + sh, cy); ctx.scale(k, k); ctx.rotate(-0.025 + 0.012 * Math.sin(ct * 1.4));
  ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 16;
  ctx.fillStyle = '#f4efe2'; rrect(-w / 2, -h / 2, w, h, 18); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.save(); rrect(-w / 2, -h / 2, w, h, 18); ctx.clip(); ctx.fillStyle = col; ctx.fillRect(-w / 2, -h / 2, w, hh); ctx.restore();
  for (const hx of [-w / 4, w / 4]) { ctx.fillStyle = '#2a2116'; ctx.beginPath(); ctx.arc(hx, -h / 2 + 4, 13, 0, 7); ctx.fill(); ctx.strokeStyle = '#c9c2b0'; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(hx, -h / 2 - 8, 16, Math.PI * 0.9, Math.PI * 2.1); ctx.stroke(); }
  font(800, 50, 'Inter', '3px'); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText((c.title || 'SUSPENDED').toUpperCase(), 0, -h / 2 + hh / 2 + 6);
  for (let i = 0; i < days; i++) {
    const x = -w / 2 + 30 + (i % cols + 0.5) * cell, y = -h / 2 + hh + 22 + (Math.floor(i / cols) + 0.5) * cell;
    ctx.strokeStyle = 'rgba(42,33,22,0.14)'; ctx.lineWidth = 2; ctx.strokeRect(x - cell / 2 + 5, y - cell / 2 + 5, cell - 10, cell - 10);
    font(700, 38, 'Inter'); ctx.fillStyle = i < done ? 'rgba(42,33,22,0.35)' : '#2a2116'; ctx.fillText(String(i + 1), x, y + 2);
    const xk = pr(ct, t0 + i / days * dur, 0.14);
    if (xk > 0) { const q = cell * 0.3; ctx.strokeStyle = col; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.beginPath();
      ctx.moveTo(x - q, y - q); ctx.lineTo(x - q + 2 * q * Math.min(1, xk * 2), y - q + 2 * q * Math.min(1, xk * 2));
      if (xk > 0.5) { const u = (xk - 0.5) * 2; ctx.moveTo(x + q, y - q); ctx.lineTo(x + q - 2 * q * u, y - q + 2 * q * u); } ctx.stroke(); }
  }
  font(800, 46, 'Inter', '-1px'); ctx.fillStyle = fin ? col : '#2a2116';
  ctx.fillText((c.caption || '{n} days').replace('{n}', Math.max(done, fin ? days : done)), 0, h / 2 - 52);
  ctx.restore();
};
CARDS.crossoff.noSlide = true;

// Phone (the "it happened in a video / a post" moment): a smartphone slides up showing a video post with the player drawn inside,
// a running timer, a progress bar and hearts floating up. We never put words in a real person's mouth: the caption is a plain fact.
// {type: "phone", player: {...}, caption: "5 Nov 2026 · retirement announced", tag: "VIDEO", w, h, bg: [c1, c2], hearts: true}
CARDS.phone = function (c, ct, cx, cy) {
  const w = c.w || 470, h = c.h || 860, k = eBack(pr(ct, 0, 0.55)), bz = 16;
  if (k <= 0) return;
  ctx.save(); ctx.translate(cx, cy + (1 - k) * 900); ctx.rotate((c.tilt != null ? c.tilt : 0.045) * (1 + 0.25 * Math.sin(ct * 1.6)));
  const z = 1 + 0.02 * ct; ctx.scale(z, z);
  ctx.shadowColor = 'rgba(0,0,0,0.65)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 22;
  ctx.fillStyle = '#0c0d11'; rrect(-w / 2, -h / 2, w, h, 54); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = '#3a3d47'; ctx.lineWidth = 4; rrect(-w / 2, -h / 2, w, h, 54); ctx.stroke();
  const sw = w - 2 * bz, shh = h - 2 * bz;
  ctx.save(); rrect(-sw / 2, -shh / 2, sw, shh, 40); ctx.clip();
  const bg = c.bg || ['#2a2f3a', '#0d0f14'], g = ctx.createLinearGradient(0, -shh / 2, 0, shh / 2); g.addColorStop(0, bg[0]); g.addColorStop(1, bg[1]);
  ctx.fillStyle = g; ctx.fillRect(-sw / 2, -shh / 2, sw, shh);
  const p = Object.assign({ front: true, chest: true }, c.player);
  drawPlayer(0, shh * 0.98, shh * 1.3, p, ct, 0, 1);
  const sd = ctx.createLinearGradient(0, shh * 0.1, 0, shh / 2); sd.addColorStop(0, 'rgba(8,9,12,0)'); sd.addColorStop(1, 'rgba(8,9,12,0.92)'); ctx.fillStyle = sd; ctx.fillRect(-sw / 2, 0, sw, shh / 2);
  // top bar: live dot, tag, timer
  const sec = Math.floor(ct * 1.0), tm = `0:${String(sec % 60).padStart(2, '0')}`;
  ctx.fillStyle = Math.sin(ct * 7) > 0 ? '#ff3b4a' : '#7a1c24'; ctx.beginPath(); ctx.arc(-sw / 2 + 40, -shh / 2 + 78, 9, 0, 7); ctx.fill();
  font(800, 24, 'Inter', '3px'); ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText((c.tag || 'VIDEO').toUpperCase(), -sw / 2 + 60, -shh / 2 + 80);
  font(700, 24, 'Mono'); ctx.textAlign = 'right'; ctx.fillText(tm, sw / 2 - 34, -shh / 2 + 80);
  // caption + progress
  if (c.caption) { font(700, 27, 'Inter'); ctx.textAlign = 'left'; ctx.fillStyle = '#fff'; String(c.caption).split('\n').forEach((l, j) => ctx.fillText(l, -sw / 2 + 32, shh / 2 - 118 + j * 36)); }
  ctx.fillStyle = 'rgba(255,255,255,0.25)'; rrect(-sw / 2 + 32, shh / 2 - 46, sw - 64, 7, 4); ctx.fill();
  ctx.fillStyle = '#fff'; rrect(-sw / 2 + 32, shh / 2 - 46, (sw - 64) * Math.min(1, 0.08 + ct * 0.16), 7, 4); ctx.fill();
  // hearts floating up the right side
  if (c.hearts !== false) { const R = rng(5); for (let i = 0; i < 14; i++) { const t0 = 0.5 + i * 0.28 + R() * 0.2, a = ct - t0, dx = (R() - 0.5) * 50; if (a < 0 || a > 1.8) continue;
    const hx = sw / 2 - 58 + dx + Math.sin(a * 5 + i) * 12, hy = shh / 2 - 170 - a * 300, hs = 15 + 9 * Math.sin(Math.min(1, a * 4) * Math.PI / 2);
    ctx.save(); ctx.globalAlpha *= Math.max(0, 1 - a / 1.8); ctx.fillStyle = i % 3 ? '#ff4d6a' : '#ffffff'; ctx.translate(hx, hy); ctx.beginPath();
    ctx.moveTo(0, hs * 0.9); ctx.bezierCurveTo(-hs * 1.5, -hs * 0.3, -hs * 0.6, -hs * 1.2, 0, -hs * 0.4); ctx.bezierCurveTo(hs * 0.6, -hs * 1.2, hs * 1.5, -hs * 0.3, 0, hs * 0.9); ctx.fill(); ctx.restore(); } }
  ctx.restore();
  ctx.fillStyle = '#0c0d11'; rrect(-56, -h / 2 + bz + 12, 112, 30, 15); ctx.fill();   // camera island
  ctx.restore();
};
CARDS.phone.noSlide = true;

// VAR offside check: the shot holds while two lines draw across the real pitch (drawn on the grass, under the players):
// blue for the last defender (def = z in metres), red for the attacker (att), then the gap between them glows.
// {type: "varlines", att, def, x0, x1, dur, gapAt (s, card time), label: "VAR · CHECKING OFFSIDE", y}
CARDS.varlines = function (c, ct, cx, cy) {
  const dur = c.dur || 0.7, x0 = c.x0 != null ? c.x0 : -34, x1 = c.x1 != null ? c.x1 : 34;
  if (c._under) {
    if (!S.cam) return;
    const P = (x, z) => { const v = toCam(S.cam, [x, 0.04, z]); return v[2] < NEAR ? null : proj(v); };
    const line = (z, col, t0) => {
      const k = ease(pr(ct - t0, 0, dur)); if (k <= 0) return;
      const pts = []; for (let i = 0; i <= 24; i++) { const q = P(lerp(x0, lerp(x0, x1, k), i / 24), z); if (q) pts.push(q); }
      if (pts.length < 2) return;
      ctx.save(); ctx.strokeStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.lineWidth = 7; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(...pts[0]); for (const q of pts.slice(1)) ctx.lineTo(...q); ctx.stroke(); ctx.restore();
    };
    const gk = pr(ct - (c.gapAt != null ? c.gapAt : dur * 2 + 0.2), 0, 0.4);
    if (gk > 0) {   // the offside gap
      const a = [P(x0, c.def), P(x1, c.def), P(x1, c.att), P(x0, c.att)];
      if (a.every(Boolean)) { ctx.save(); ctx.globalAlpha = gk * (0.35 + 0.15 * Math.sin(ct * 8)); ctx.fillStyle = c.gapColor || '#ff3b4a';
        ctx.beginPath(); ctx.moveTo(...a[0]); a.slice(1).forEach(q => ctx.lineTo(...q)); ctx.closePath(); ctx.fill(); ctx.restore(); }
    }
    line(c.def, c.defColor || '#3fa0ff', 0);
    line(c.att, c.attColor || '#ff3b4a', dur + 0.1);
    return;
  }
  if (c.label === false) return;   // the on-screen VAR badge
  const k = ease(pr(ct, 0, 0.35)), y = c.y || 640, txt = c.label || 'VAR · CHECKING OFFSIDE';
  ctx.save(); ctx.globalAlpha *= k; font(800, 34, 'Inter'); const w = ctx.measureText(txt).width + 90;
  rrect(W / 2 - w / 2, y - 34 + (1 - k) * 20, w, 68, 34); ctx.fillStyle = 'rgba(12,14,20,0.82)'; ctx.fill();
  ctx.fillStyle = (Math.sin(ct * 9) > 0) ? '#ff3b4a' : '#7a1c24'; ctx.beginPath(); ctx.arc(W / 2 - w / 2 + 36, y + (1 - k) * 20, 9, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(txt, W / 2 - w / 2 + 58, y + 2 + (1 - k) * 20);
  ctx.restore();
};
CARDS.varlines.noSlide = true;


// Newspaper front page that spins in (archive / reaction beats). Masthead is fictional: never imitate a real paper.
CARDS.newspaper = function (c, ct, cx, cy) {
  const k = eOut(pr(ct, 0, c.spin || 1.4)), sc = c.scale || 1;   // spin: seconds to spin in (user: 0.9 was too quick)
  if (k <= 0) return;
  const w = c.w || 760, h = c.h || 980;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(lerp(-Math.PI * (c.turns || 3), c.tilt != null ? c.tilt : -0.05, k));
  const drift = 1 + 0.035 * Math.max(0, ct - (c.spin || 1.4));   // keeps pushing in after it lands
  ctx.scale(lerp(0.05, sc, k) * drift, lerp(0.05, sc, k) * drift);
  ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 16;
  ctx.fillStyle = '#f1ece0'; ctx.fillRect(-w / 2, -h / 2, w, h);
  ctx.shadowColor = 'transparent';
  const R = rng(9);
  for (let i = 0; i < 900; i++) { ctx.fillStyle = `rgba(90,70,40,${R() * 0.06})`; ctx.fillRect(-w / 2 + R() * w, -h / 2 + R() * h, 2, 2); }
  const serif = 'Liberation Serif, DejaVu Serif, serif';
  ctx.fillStyle = '#16130e'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.font = `700 64px ${serif}`; ctx.fillText(c.masthead || 'THE FINAL WHISTLE', 0, -h / 2 + 90);
  ctx.fillRect(-w / 2 + 30, -h / 2 + 110, w - 60, 4);
  ctx.font = `500 20px Mono`; ctx.fillText((c.dateline || '').toUpperCase(), 0, -h / 2 + 140);
  ctx.fillRect(-w / 2 + 30, -h / 2 + 156, w - 60, 2);
  // headline: "\n" for lines, each auto-fitted to the page width (user: a long headline ran off the page)
  let hy = -h / 2 + 170;
  for (const l of String(c.headline || '').split('\n')) {
    ctx.font = `900 100px Inter`; const fs = Math.min(c.size || 300, 100 * (w - 70) / Math.max(1, ctx.measureText(l).width));
    ctx.font = `900 ${fs}px Inter`; ctx.fillStyle = c.color || '#16130e'; hy += fs * 0.86; ctx.fillText(l, 0, hy); hy += fs * 0.1;
  }
  ctx.fillStyle = '#16130e';
  const subY = hy + 64;
  String(c.sub || '').split('\n').forEach((l, i) => { ctx.font = `700 54px ${serif}`; const fs = Math.min(54, 54 * (w - 70) / Math.max(1, ctx.measureText(l).width)); ctx.font = `700 ${fs}px ${serif}`; ctx.fillText(l, 0, subY + i * 60); });
  ctx.fillStyle = 'rgba(22,19,14,0.35)';
  const top = subY + 60 * String(c.sub || '').split('\n').length + 10;
  for (let col = 0; col < 3; col++) for (let y = top; y < h / 2 - 40; y += 18) {
    const x0 = -w / 2 + 40 + col * (w - 80) / 3;
    ctx.fillRect(x0, y, (w - 80) / 3 - 24 - (R() < 0.15 ? 60 : 0), 7);
  }
  ctx.restore();
};
CARDS.newspaper.noSlide = true;

const ballSlow = u => (u < 0.55 ? u / 0.55 * 0.8 : 0.8 + 0.2 * eOut((u - 0.55) / 0.45));
function ballWorld(c, ct) {
  const k0 = pr(ct, 0, c.dur || 1.6), u = c.slowmo === false ? k0 : ballSlow(k0), [a, b, d] = c.points;
  return [0, 1, 2].map(i => (1 - u) ** 2 * a[i] + 2 * (1 - u) * u * b[i] + u * u * d[i]);
}
// Slow-motion ball path: the ball races along a curve, slows to a crawl near the end, leaves a trail, then the net flashes.
CARDS.ballpath = function (c, ct) {
  const dur = c.dur || 1.6, k0 = pr(ct, 0, dur);
  if (k0 <= 0 || (c.world && !S.cam)) return;
  if (k0 >= 1 && c.flash === false && c.hide !== false && c.saveBy == null) return;
  let P = c.points, r0 = c.r || 18, r1 = c.rEnd || 8, held = null;
  if (c.world) {
    const q = c.points.map(p => toCam(S.cam, p));
    if (q.some(v => v[2] < NEAR)) return;
    P = q.map(proj);
    r0 = Math.max(4, FOC * 0.11 / q[0][2]); r1 = Math.max(3, FOC * 0.11 / q[2][2]);
    const kp = c.saveBy != null && S.cur && S.cur.playersArr[c.saveBy], an = kp && S.anchors[c.saveBy];
    if (kp && an) {   // a real save: the ball ends in the keeper's gloves at the moment of contact, then stays held as he falls
      const lt = S.t - S.cur.playersStart, contact = lt - ct + dur;
      const hands = t => { const h = rigHands(an.u, kp, t); return [an.x + (h[0][0] + h[1][0]) / 2, an.y + (h[0][1] + h[1][1]) / 2]; };
      const end = hands(Math.min(lt, contact));
      P = [P[0], P[1], end]; r1 = Math.max(3, an.u * 0.11 / 1.85 * 1.0);
      if (k0 >= 1) held = hands(lt);
    }
  }
  if (held) { ctx.save(); drawBall(held[0], held[1], r1); ctx.restore(); return; }
  const slow = ballSlow;
  const at = u => { const a = P[0], b = P[1], d = P[2]; return [(1 - u) ** 2 * a[0] + 2 * (1 - u) * u * b[0] + u * u * d[0], (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * b[1] + u * u * d[1]]; };
  const u = c.slowmo === false ? k0 : slow(k0);
  ctx.save();
  ctx.lineCap = 'round';
  for (let i = 0; i < 40; i++) {
    const v = Math.max(0, u - i * 0.012), p = at(v), q = at(Math.max(0, v - 0.012));
    ctx.strokeStyle = `rgba(255,255,255,${0.5 * (1 - i / 40)})`; ctx.lineWidth = lerp(r0, r1, v) * 1.1 * (1 - i / 40);
    ctx.beginPath(); ctx.moveTo(...q); ctx.lineTo(...p); ctx.stroke();
  }
  for (let g = 3; g >= 1; g--) { const p = at(Math.max(0, u - g * 0.03)); ctx.globalAlpha = 0.18 * (4 - g); drawBall(p[0], p[1], lerp(r0, r1, u)); }
  ctx.globalAlpha = 1;
  const p = at(u); drawBall(p[0], p[1], lerp(r0, r1, u));
  const fk = pr(ct, dur, 0.5);
  if (c.flash !== false && fk > 0 && fk < 1) {
    const e = P[2], g = ctx.createRadialGradient(e[0], e[1], 0, e[0], e[1], 160 * fk + 20);
    g.addColorStop(0, `rgba(255,255,255,${0.8 * (1 - fk)})`); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(e[0] - 200, e[1] - 200, 400, 400);
  }
  ctx.restore();
};
CARDS.ballpath.noSlide = true;
// Pass web: the ball pings from player to player, each pass leaving a line, with a pop per pass. Three looks:
//  - stadium (default): glowing lines on the grass, drawn under the players. Bind rigged players to it with player "web": k (node k)
//    or "webRival": j (they move for real, running when they move). "tokens": true draws top-down player discs instead (bird's-eye shots,
//    e.g. an "orbit" with h ≈ 40). Beat "camFollow": {h, back, side} makes a broadcast camera follow the ball.
//  - board: "chalk": a tactics chalkboard (screen card) with chalk O's, X's chasing the ball, and pass lines scratching in.
// nodes: [[x, z], ...] pitch metres; drift (m, players wander), pass (s per pass), trail, color, seed, loft (share of lofted passes),
// rivals: {nodes, color, chase} (opponents shuffle towards the ball); kit: {shirt, ring} and rivalKit for tokens;
// counter: from, to, dur, label, y (or counter: false). Chalk: w, h, area [x0, z0, x1, z1], zoom [from, to], follow (0–1).
function passSeq(c) {
  if (c._seq) return c._seq;
  if (c.play) {   // a real move: build up from the back, mostly forward and sideways, then recycle to the back and go again
    const R = rng(c.seed || 7), N = c.nodes, n = N.length, zs = N.map(q => q[1]), zmin = Math.min(...zs), zmax = Math.max(...zs);
    let cur = c.start != null ? c.start : zs.indexOf(zmin); const seq = [cur];
    for (let i = 0; i < 400; i++) {
      const z = N[cur][1], front = (z - zmin) / Math.max(1, zmax - zmin) > 0.75;
      let opts = N.map((q, j) => j).filter(j => j !== cur && Math.hypot(N[j][0] - N[cur][0], N[j][1] - N[cur][1]) < (c.reach || 22));
      if (front && R() < 0.6) opts = opts.filter(j => N[j][1] < z - 4);           // recycle it back
      else { const fw = opts.filter(j => N[j][1] > z - 2); if (fw.length && R() < 0.8) opts = fw; }   // play forward or across
      if (!opts.length) opts = N.map((q, j) => j).filter(j => j !== cur);
      if (seq.length > 1) { const nb = opts.filter(j => j !== seq[seq.length - 2]); if (nb.length) opts = nb; }   // no instant back-and-forth
      cur = opts[Math.floor(R() * opts.length)]; seq.push(cur);
    }
    return (c._seq = seq);
  }
  const R = rng(c.seed || 7), n = c.nodes.length, seq = [c.start || 0];
  for (let i = 0; i < 400; i++) { let j; do { j = Math.floor(R() * n); } while (j === seq[seq.length - 1]); seq.push(j); }
  return (c._seq = seq);
}
function webHash(j, k) { const x = Math.sin(j * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); }
function webNode(c, j, t) {   // each player wanders on his own rhythm (user: they moved as one block)
  const b = c.nodes[j], d = c.drift != null ? c.drift : 0, f1 = 0.45 + 0.5 * webHash(j, 1), f2 = 0.35 + 0.45 * webHash(j, 2), ph = webHash(j, 3) * 6.28;
  const push = c.push ? Math.min(c.pushMax || 8, c.push * Math.max(0, t)) : 0;   // the team squeezes up the pitch as the move goes on
  return [b[0] + d * (0.6 + 0.6 * webHash(j, 4)) * Math.sin(t * f1 + ph), b[1] + push + d * (0.5 + 0.5 * webHash(j, 5)) * Math.cos(t * f2 + ph * 1.3)];
}
function webDash(c, j, t) {   // play mode: after receiving, a player carries the ball forward a few metres, then eases back into shape
  if (!c.play || t < 0) return [0, 0];
  const pd = c.pass || 0.34, cf = c.carryFrac != null ? c.carryFrac : 0.45, seq = passSeq(c), cur = Math.floor(t / pd);
  let i = cur; while (i >= 0 && cur - i < 40 && seq[i] !== j) i--;
  if (i < 0 || seq[i] !== j) return [0, 0];
  const s = t - i * pd, rise = eOut(Math.min(1, s / (cf * pd))), decay = Math.exp(-Math.max(0, s - cf * pd) / 1.2);
  const C = c.carry != null ? c.carry : 3, a = (webHash(i, 31) - 0.5) * 1.2;
  return [Math.sin(a) * C * rise * decay, Math.cos(a) * C * rise * decay];
}
function webPos(c, j, t) { const n = webNode(c, j, t), d = webDash(c, j, t); return [n[0] + d[0], n[1] + d[1]]; }
function webPass(c, i) {   // where pass i starts and ends, and how high it travels
  const pd = c.pass || 0.34, seq = passSeq(c), R = rng(1000 + i * 7 + (c.seed || 7));
  if (c.play) {
    const cf = c.carryFrac != null ? c.carryFrac : 0.45;
    return { a: webPos(c, seq[i], (i + cf) * pd), b: webPos(c, seq[i + 1], (i + 1) * pd), arc: R() < (c.loft != null ? c.loft : 0.15) ? 2.2 : 0.1, bend: (R() - 0.5) * 0.35 };
  }
  return { a: webNode(c, seq[i], i * pd), b: webNode(c, seq[i + 1], (i + 1) * pd), arc: R() < (c.loft != null ? c.loft : 0.2) ? 2.4 : 0.15, bend: 0 };
}
function webCurve(P, u) {   // a point along a (slightly bent) pass on the ground
  const mx = (P.a[0] + P.b[0]) / 2, mz = (P.a[1] + P.b[1]) / 2, dx = P.b[0] - P.a[0], dz = P.b[1] - P.a[1];
  const cx = mx - dz * P.bend, cz = mz + dx * P.bend;
  return [(1 - u) ** 2 * P.a[0] + 2 * (1 - u) * u * cx + u * u * P.b[0], (1 - u) ** 2 * P.a[1] + 2 * (1 - u) * u * cz + u * u * P.b[1]];
}
function webBall(c, ct) {   // [x, y, z] of the ball and the pass index
  const pd = c.pass || 0.34, t = Math.max(0, ct);
  let cur = Math.floor(t / pd), k = t / pd - cur;
  if (c.stopAt != null && t >= c.stopAt) { cur = Math.floor(c.stopAt / pd); k = 1; }
  if (c.play) {
    const cf = c.carryFrac != null ? c.carryFrac : 0.45, seq = passSeq(c);
    if (k < cf) {   // at the receiver's feet, touched ahead as he carries it
      const q = webPos(c, seq[cur], t), d = webDash(c, seq[cur], t), dl = Math.hypot(d[0], d[1]) || 1, lead = 0.5 + 0.25 * Math.abs(Math.sin(t * 9));
      return { p: [q[0] + d[0] / dl * lead * Math.min(1, dl), 0.11, q[1] + d[1] / dl * lead * Math.min(1, dl) + (dl < 0.05 ? lead : 0)], cur, k: 0, carry: true };
    }
    const P = webPass(c, cur), u = (k - cf) / (1 - cf), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2, g = webCurve(P, e);
    return { p: [g[0], 0.11 + P.arc * Math.sin(Math.PI * u), g[1]], cur, k: u };
  }
  const P = webPass(c, cur), e = eOut(k);
  return { p: [lerp(P.a[0], P.b[0], e), 0.11 + P.arc * Math.sin(Math.PI * k), lerp(P.a[1], P.b[1], e)], cur, k };
}
function webTackles(c) {   // play mode: now and then the nearest defender slides in on the man receiving it (deterministic, so any frame renders the same)
  if (c._tk) return c._tk;
  const pd = c.pass || 0.34, seq = passSeq(c), out = [], every = c.tackleEvery || 0.22;
  if (c.rivals && c.tackles !== false) for (let i = 3; i < 200; i++) {
    if (webHash(i, 41) > every) continue;
    const te = i * pd, r = webNode(c, seq[i], te);
    let best = -1, bd = 1e9; c.rivals.nodes.forEach((_, j) => { const q = webRivalBase(c, j, te), d = Math.hypot(q[0] - r[0], q[1] - r[1]); if (d < bd) { bd = d; best = j; } });
    if (best >= 0 && !out.some(o => o.j === best && Math.abs(o.te - te) < 2.5)) out.push({ te, j: best, i });
  }
  return (c._tk = out);
}
function webRival(c, j, t) {
  const base = webRivalBase(c, j, t);
  if (!c.play) return base;
  for (const tk of webTackles(c)) {
    if (tk.j !== j || t < tk.te - 0.7 || t > tk.te + 1.4) continue;
    const r = webPos(c, passSeq(c)[tk.i], Math.min(t, tk.te + 0.2)), w = t < tk.te ? eOut(pr(t, tk.te - 0.7, 0.7)) : 1 - eOut(pr(t, tk.te + 0.6, 0.8));
    return [lerp(base[0], r[0] + 0.9, w), lerp(base[1], r[1] + 0.4, w)];
  }
  return base;
}
function webRivalTackle(c, j, t) { if (!c.play) return null; for (const tk of webTackles(c)) if (tk.j === j && t >= tk.te - 0.45 && t <= tk.te + 0.75) return tk; return null; }
function webRivalBase(c, j, t) {   // opponents press individually: each reacts on its own delay, the nearest ones press hardest, the rest hold shape
  const R = c.rivals, b = R.nodes[j], ch = R.chase != null ? R.chase : 0.45;
  const lag = 0.3 + 0.8 * webHash(j, 7), ball = webBall(c, t - lag).p;
  const dist = Math.hypot(ball[0] - b[0], ball[2] - b[1]), pull = ch * (0.25 + 0.75 * Math.exp(-dist / 14)) * (0.7 + 0.5 * webHash(j, 8));
  const tx = ball[0] + (webHash(j, 9) - 0.5) * 6, tz = ball[2] + (webHash(j, 10) - 0.5) * 6 + 2.5;   // goal side of the ball, never on top of it
  const f1 = 0.6 + 0.6 * webHash(j, 11), f2 = 0.5 + 0.5 * webHash(j, 12), ph = webHash(j, 13) * 6.28;
  return [lerp(b[0], tx, pull) + 1.2 * Math.sin(t * f1 + ph), lerp(b[1], tz, pull) + 1.0 * Math.cos(t * f2 + ph)];
}
function webCard(b) { for (const it of b ? b.cards : []) if (it.obj.type === 'passweb') return it; return null; }
function webPlayerPos(p, lt) {   // a rigged player bound to the pass web: where he is, and whether he's running
  const it = webCard(S.cur); if (!it) return null;
  const c = it.obj, ct = S.t - it.start, f = t => p.web != null ? webNode(c, p.web, t) : webRival(c, p.webRival, t);
  const g = t => p.web != null ? webPos(c, p.web, t) : webRival(c, p.webRival, t);
  const a = g(ct), b0 = g(ct - 0.12), sp = Math.hypot(a[0] - b0[0], a[1] - b0[1]) / 0.12;
  const tk = p.webRival != null ? webRivalTackle(c, p.webRival, ct) : null;
  return { x: a[0], z: a[1], walk: sp > 0.9 ? 1 : 0, heading: sp > 0.01 ? [(a[0] - b0[0]) / (sp * 0.12), (a[1] - b0[1]) / (sp * 0.12)] : [0, 1],
    tackle: tk ? { delay: lt - (ct - (tk.te - 0.45)), dir: (a[0] - webPos(c, passSeq(c)[tk.i], tk.te)[0]) > 0 ? 1 : -1 } : null };
}
function webTokenW(cam, x, z, r, fill, ring, alpha, label, hot) {   // a top-down player disc on the pitch (label = shirt number, hot = on the ball)
  const c0 = toCam(cam, [x, 0.03, z]); if (c0[2] < NEAR) return;
  const s = proj(c0), sx = proj(toCam(cam, [x + r, 0.03, z])), sz = proj(toCam(cam, [x, 0.03, z + r]));
  const rx = Math.max(3, Math.hypot(sx[0] - s[0], sx[1] - s[1])), ry = Math.max(2, Math.hypot(sz[0] - s[0], sz[1] - s[1]));
  ctx.save(); ctx.globalAlpha *= alpha == null ? 1 : alpha;
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.beginPath(); ctx.ellipse(s[0] + rx * 0.15, s[1] + ry * 0.3, rx, ry, 0, 0, 7); ctx.fill();
  ctx.fillStyle = fill; ctx.beginPath(); ctx.ellipse(s[0], s[1], rx, ry, 0, 0, 7); ctx.fill();
  ctx.lineWidth = Math.max(2, rx * 0.22); ctx.strokeStyle = hot ? '#f1c453' : ring; ctx.stroke();
  if (label != null && rx > 9) { font(800, rx * 0.95, 'Inter'); ctx.fillStyle = ring; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(label), s[0], s[1] + rx * 0.05); }
  ctx.restore();
}
CARDS.passweb = function (c, ct, cx, cy) {
  if (c.board === 'chalk') { if (!c._under) CARDS.passweb.chalk(c, ct, cx, cy); return; }
  if (c._under) {
    if (!S.cam) return;
    const pd = c.pass || 0.34, { cur, k } = webBall(c, ct), trail = c.trail || 16, col = c.color || '#ffffff';
    const P = w => { const v = toCam(S.cam, [w[0], 0.05, w[1]]); return v[2] < NEAR ? null : proj(v); };
    if (c.play) {   // a TV analysis graphic: bent pass lines that draw behind the ball, the last few fading, an arrowhead on each, carries dotted
      const bb = webBall(c, ct), cf = c.carryFrac != null ? c.carryFrac : 0.45, tr = c.trail || 6, seq = passSeq(c);
      const curve = (W, u0, u1, n) => { const out = []; for (let s2 = 0; s2 <= n; s2++) { const g = webCurve(W, lerp(u0, u1, s2 / n)), q = P(g); if (q) out.push(q); } return out; };
      const stroke = (pts, w, al, dash) => { if (pts.length < 2) return; ctx.globalAlpha = al; ctx.lineWidth = w; ctx.setLineDash(dash || []); ctx.beginPath(); ctx.moveTo(...pts[0]); for (const q of pts.slice(1)) ctx.lineTo(...q); ctx.stroke(); };
      const head = (pts, sz, al) => { if (pts.length < 2) return; const a1 = pts[pts.length - 2], a2 = pts[pts.length - 1], an = Math.atan2(a2[1] - a1[1], a2[0] - a1[0]);
        ctx.globalAlpha = al; ctx.setLineDash([]); ctx.beginPath(); ctx.moveTo(...a2); ctx.lineTo(a2[0] - sz * Math.cos(an - 0.5), a2[1] - sz * Math.sin(an - 0.5)); ctx.lineTo(a2[0] - sz * Math.cos(an + 0.5), a2[1] - sz * Math.sin(an + 0.5)); ctx.closePath(); ctx.fill(); };
      ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = col; ctx.fillStyle = col; ctx.shadowColor = col;
      for (let i = Math.max(0, bb.cur - tr); i < bb.cur; i++) {
        const W = webPass(c, i), f = 1 - (bb.cur - i - 1) / tr, pts = curve(W, 0, 1, 18);
        ctx.shadowBlur = 10 * f; stroke(pts, 2 + 5 * f, 0.15 + 0.6 * f, W.arc > 1 ? [14, 10] : null); head(pts, 10 + 8 * f, 0.15 + 0.6 * f);
        const d0 = P(W.b), nxt = webPass(c, i + 1), d1 = P(nxt.a);   // the carry that followed
        if (d0 && d1 && i + 1 < bb.cur) { ctx.shadowBlur = 0; stroke([d0, d1], 2 + 2 * f, 0.15 + 0.4 * f, [4, 8]); }
      }
      if (!bb.carry) { const W = webPass(c, bb.cur), pts = curve(W, 0, bb.k, 18); ctx.shadowBlur = 16; stroke(pts, 7, 0.9, W.arc > 1 ? [14, 10] : null); }
      ctx.restore();
      if (c.tokens) {
        const kit = c.kit || { shirt: '#f4f4f2', ring: '#132257' }, rk = c.rivalKit || { shirt: '#c4122e', ring: '#1b458f' };
        if (c.rivals) c.rivals.nodes.forEach((_, j) => { const q = webRival(c, j, ct); webTokenW(S.cam, q[0], q[1], 0.95, rk.shirt, rk.ring, 1, (c.rivals.numbers || [])[j]); });
        const recv = seq[bb.carry ? bb.cur : bb.cur + 1], rq = webPos(c, recv, ct), pk = bb.carry ? pr(ct / pd - bb.cur, 0, cf) : 0;
        if (bb.carry && pk < 1) { const s0 = toCam(S.cam, [rq[0], 0.03, rq[1]]); if (s0[2] > NEAR) { const sp0 = proj(s0), rr = FOC * (1.2 + 2.4 * pk) / s0[2];
          ctx.save(); ctx.strokeStyle = col; ctx.globalAlpha = 0.85 * (1 - pk); ctx.lineWidth = 4; ctx.beginPath(); ctx.ellipse(sp0[0], sp0[1], rr, rr * Math.abs(S.cam.f[1]), 0, 0, 7); ctx.stroke(); ctx.restore(); } }
        c.nodes.forEach((_, j) => { const q = webPos(c, j, ct); webTokenW(S.cam, q[0], q[1], 1.05, kit.shirt, kit.ring, 1, (c.numbers || [])[j], j === recv); });
      }
      const v = toCam(S.cam, bb.p); if (v[2] < NEAR) return;
      const sp = proj(v), r = Math.max(5, FOC * 0.16 / v[2]) * (c.tokens ? 1.5 : 1), g = toCam(S.cam, [bb.p[0], 0.02, bb.p[2]]);
      if (g[2] > NEAR) { const sg = proj(g); ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.beginPath(); ctx.ellipse(sg[0], sg[1], r, r * 0.4, 0, 0, 7); ctx.fill(); }
      drawBall(sp[0], sp[1], r);
      return;
    }
    ctx.save(); ctx.lineCap = 'round';
    for (let i = Math.max(0, cur - trail); i < cur; i++) {   // completed passes, older ones fading
      const W = webPass(c, i), a = P(W.a), b = P(W.b); if (!a || !b) continue;
      const f = 1 - (cur - i) / (trail + 1);
      ctx.strokeStyle = col; ctx.globalAlpha = 0.12 + 0.6 * f; ctx.lineWidth = 2 + 6 * f; ctx.shadowColor = col; ctx.shadowBlur = 16 * f;
      if (W.arc > 1) ctx.setLineDash([14, 12]); else ctx.setLineDash([]);   // lofted passes dashed, like a TV graphic
      ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke();
    }
    ctx.setLineDash([]);
    { const W = webPass(c, cur), a = P(W.a), bp = P([lerp(W.a[0], W.b[0], eOut(k)), lerp(W.a[1], W.b[1], eOut(k))]);   // the pass in flight draws itself
      if (a && bp) { ctx.globalAlpha = 0.85; ctx.strokeStyle = col; ctx.lineWidth = 7; ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...bp); ctx.stroke(); } }
    ctx.restore();
    if (c.tokens) {   // bird's-eye: player discs, rivals chasing, a pulse on whoever just received it
      const kit = c.kit || { shirt: '#f4f4f2', ring: '#132257' }, rk = c.rivalKit || { shirt: '#c4122e', ring: '#1b458f' };
      if (c.rivals) c.rivals.nodes.forEach((_, j) => { const p = webRival(c, j, ct); webTokenW(S.cam, p[0], p[1], 0.9, rk.shirt, rk.ring); });
      const seq = passSeq(c), rec = webNode(c, seq[cur], cur * pd), pk = pr(k, 0, 0.5);
      if (pk < 1) { const s0 = toCam(S.cam, [rec[0], 0.03, rec[1]]); if (s0[2] > NEAR) { const s = proj(s0), rr = FOC * (1 + 2.2 * pk) / s0[2];
        ctx.save(); ctx.strokeStyle = col; ctx.globalAlpha = 0.8 * (1 - pk); ctx.lineWidth = 4; ctx.beginPath(); ctx.ellipse(s[0], s[1], rr, rr * Math.abs(S.cam.f[1]), 0, 0, 7); ctx.stroke(); ctx.restore(); } }
      c.nodes.forEach((_, j) => { const p = webNode(c, j, ct); webTokenW(S.cam, p[0], p[1], 1.0, kit.shirt, kit.ring); });
    }
    if (c.stopAt != null && ct >= c.stopAt) return;
    const bw = webBall(c, ct).p, v = toCam(S.cam, bw); if (v[2] < NEAR) return;
    const s = proj(v), r = Math.max(5, FOC * 0.16 / v[2]) * (c.tokens ? 1.6 : 1), g = toCam(S.cam, [bw[0], 0.02, bw[2]]);
    if (g[2] > NEAR) { const sg = proj(g); ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.beginPath(); ctx.ellipse(sg[0], sg[1], r, r * 0.4, 0, 0, 7); ctx.fill(); }
    drawBall(s[0], s[1], r);
    return;
  }
  if (c.counter === false) return;
  const k = ease(pr(ct, 0, c.dur || 4)), v = Math.round(lerp(c.from || 0, c.to, k)), fin = k >= 1;
  const pop = fin ? 1 + 0.12 * Math.max(0, 1 - (ct - (c.dur || 4)) / 0.3) : 1;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(pop, pop);
  // the box always wraps its label and the final number (user: the label ran outside the box)
  const lab = (c.label || 'Passes completed').toUpperCase();
  font(600, 26, 'Mono', '5px'); let lw = ctx.measureText(lab).width, ls = 26;
  if (lw > 900) { ls = 26 * 900 / lw; font(600, ls, 'Mono', '4px'); lw = ctx.measureText(lab).width; }
  font(800, 150, 'Inter', '-3px'); const nw = ctx.measureText(Number(c.to).toLocaleString('en-GB')).width;
  const bw = Math.max(560, lw + 90, nw + 120);
  ctx.fillStyle = 'rgba(10,12,18,0.82)'; rrect(-bw / 2, -120, bw, 236, 28); ctx.fill();
  ctx.strokeStyle = fin && c.gold !== false ? 'rgba(241,196,83,0.55)' : 'rgba(255,255,255,0.12)'; ctx.lineWidth = 2; rrect(-bw / 2, -120, bw, 236, 28); ctx.stroke();
  font(800, 150, 'Inter', '-3px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  if (fin) { ctx.shadowColor = c.gold === false ? 'transparent' : '#f1c453'; ctx.shadowBlur = 30; }
  ctx.fillStyle = fin && c.gold !== false ? '#f1c453' : '#ffffff'; ctx.fillText(v.toLocaleString('en-GB'), 0, 50); ctx.shadowBlur = 0;
  font(600, ls, 'Mono', ls < 26 ? '4px' : '5px'); ctx.fillStyle = '#9aa3b2'; ctx.fillText(lab, 0, 90);
  ctx.restore();
};
CARDS.passweb.chalk = function (c, ct, cx, cy) {   // tactics chalkboard version
  const bw = c.w || 960, bh = c.h || 1180, A = c.area || [-34, 0, 34, 52.5], pad = 40, a = eOut(pr(ct, 0, 0.35));
  const toB = (x, z) => [-bw / 2 + pad + (x - A[0]) / (A[2] - A[0]) * (bw - 2 * pad), bh / 2 - pad - (z - A[1]) / (A[3] - A[1]) * (bh - 2 * pad)];
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy + (1 - a) * 60); ctx.rotate(c.tilt != null ? c.tilt : -0.015);
  ctx.fillStyle = '#5b3a1e'; rrect(-bw / 2 - 22, -bh / 2 - 22, bw + 44, bh + 44, 12); ctx.fill();
  const g = ctx.createRadialGradient(0, 0, 50, 0, 0, bh * 0.7); g.addColorStop(0, '#2c3a33'); g.addColorStop(1, '#18201c');
  ctx.fillStyle = g; ctx.fillRect(-bw / 2, -bh / 2, bw, bh);
  ctx.save(); ctx.beginPath(); ctx.rect(-bw / 2, -bh / 2, bw, bh); ctx.clip();
  // camera on the board: slow push-in that leans towards the ball
  const zm = c.zoom || [1, 1.25], zk = lerp(zm[0], zm[1], pr(ct, 0, c.zoomDur || 6));
  let fx = 0, fy = 0;
  if (c.follow) { let sx = 0, sy = 0; for (let i = 0; i < 6; i++) { const p = webBall(c, ct - i * 0.15).p, q = toB(p[0], p[2]); sx += q[0]; sy += q[1]; } fx = sx / 6 * c.follow; fy = sy / 6 * c.follow; }
  ctx.scale(zk, zk); ctx.translate(-fx, -fy);
  const R = rng(3); ctx.fillStyle = 'rgba(255,255,255,0.035)';   // old chalk smudges
  for (let i = 0; i < 16; i++) { ctx.beginPath(); ctx.ellipse((R() - 0.5) * bw, (R() - 0.5) * bh, 60 + R() * 120, 20 + R() * 40, R() * 3, 0, 7); ctx.fill(); }
  const L = (x1, z1, x2, z2, s, w, col, k) => { const p = toB(x1, z1), q = toB(x2, z2); chalkLine(p[0], p[1], q[0], q[1], k == null ? 1 : k, s, w, col); };
  const dim = 'rgba(245,245,238,0.45)';   // the pitch markings
  L(A[0], A[3], A[2], A[3], 1, 6, dim); L(A[0], A[1], A[0], A[3], 2, 6, dim); L(A[2], A[1], A[2], A[3], 3, 6, dim);
  if (A[1] <= 0) L(A[0], 0, A[2], 0, 4, 6, dim);
  const bx = 20.16, bz = 52.5 - 16.5, sx = 9.16, sz = 52.5 - 5.5;
  L(-bx, 52.5, -bx, bz, 5, 6, dim); L(-bx, bz, bx, bz, 6, 6, dim); L(bx, bz, bx, 52.5, 7, 6, dim);
  L(-sx, 52.5, -sx, sz, 8, 5, dim); L(-sx, sz, sx, sz, 9, 5, dim); L(sx, sz, sx, 52.5, 10, 5, dim);
  { const c0 = toB(0, 0), rr = 9.15 / (A[2] - A[0]) * (bw - 2 * pad); ctx.save(); ctx.strokeStyle = dim; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(c0[0], c0[1], rr, Math.PI, 2 * Math.PI); ctx.stroke(); ctx.restore(); }
  // passes: completed ones stay (chalk), the one in flight scratches in behind the ball
  const pd = c.pass || 0.34, { cur, k } = webBall(c, ct), col = c.color || 'rgba(245,245,238,0.92)', trail = c.trail || 40;
  for (let i = Math.max(0, cur - trail); i < cur; i++) { const W = webPass(c, i); L(W.a[0], W.a[1], W.b[0], W.b[1], 50 + i, 5, col); }
  { const W = webPass(c, cur); L(W.a[0], W.a[1], W.b[0], W.b[1], 50 + cur, 7, col, eOut(k)); }
  // rivals (X) chasing, players (O)
  const rcol = (c.rivals && c.rivals.color) || '#ff8a96';
  if (c.rivals) c.rivals.nodes.forEach((_, j) => { const p = webRival(c, j, ct), q = toB(p[0], p[1]), s = 20;
    chalkLine(q[0] - s, q[1] - s, q[0] + s, q[1] + s, 1, 300 + j, 8, rcol); chalkLine(q[0] + s, q[1] - s, q[0] - s, q[1] + s, 1, 400 + j, 8, rcol); });
  const hcol = (c.kit && c.kit.chalk) || '#ffffff', seq = passSeq(c);
  c.nodes.forEach((_, j) => { const p = webNode(c, j, ct), q = toB(p[0], p[1]);
    ctx.save(); ctx.strokeStyle = hcol; ctx.lineWidth = 8; ctx.globalAlpha *= 0.92; ctx.beginPath(); ctx.arc(q[0], q[1], 24, 0, 7); ctx.stroke(); ctx.restore(); });
  const rec = webNode(c, seq[cur], cur * pd), pk = pr(k, 0, 0.45), rq = toB(rec[0], rec[1]);   // a chalk ring pulses on the receiver
  if (pk < 1) { ctx.save(); ctx.strokeStyle = '#f1c453'; ctx.globalAlpha *= 1 - pk; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(rq[0], rq[1], 24 + 30 * pk, 0, 7); ctx.stroke(); ctx.restore(); }
  const bp = webBall(c, ct).p, bq = toB(bp[0], bp[2]);
  ctx.fillStyle = '#f1c453'; ctx.beginPath(); ctx.arc(bq[0], bq[1] - bp[1] * 6, 11, 0, 7); ctx.fill();
  ctx.restore();
  if (c.note) { font(400, 46, 'Marker'); ctx.fillStyle = 'rgba(245,245,238,0.9)'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.note, 0, -bh / 2 + 54); }
  ctx.restore();
};
CARDS.passweb.noSlide = true;
// A ball resting at a world point until 'until' seconds (e.g. waiting to be kicked).
CARDS.ball = function (c, ct) {
  if (!S.cam || (c.until != null && ct >= c.until)) return;
  const q = toCam(S.cam, c.point);
  if (q[2] < NEAR) return;
  const s = proj(q);
  ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.beginPath(); ctx.ellipse(s[0], s[1] + FOC * 0.1 / q[2], FOC * 0.14 / q[2], FOC * 0.04 / q[2], 0, 0, 7); ctx.fill();
  drawBall(s[0], s[1], Math.max(3, FOC * 0.11 / q[2]));
};
CARDS.ball.noSlide = true;

// ---------- ideas from the reference creator (literal visual metaphors, rain-in counters, fly-through words) ----------
// A vehicle (bus, van) that drives onto the pitch and parks: "parks the bus", a sponsor's van, a money truck.
// from/to are pitch points [x, 0, z]; drawn side-on, depth-sorted with the players.
function vehicleWorld(c, ct) {
  const k = eOut(pr(ct, 0, c.dur || 1.6));
  return lerp3(c.from || c.to, c.to, k);
}
CARDS.vehicle = function (c, ct) {
  if (!S.cam) return;
  const p = vehicleWorld(c, ct), q = toCam(S.cam, p);
  if (q[2] < NEAR + 1) return;
  const s = proj(q), m = FOC / q[2];               // pixels per metre at that depth
  const a = proj(toCam(S.cam, c.from || c.to)), b = proj(toCam(S.cam, c.to));
  const dir = (b[0] - a[0]) >= 0 ? 1 : -1;         // which way it faces on screen
  const kind = c.kind || 'bus', L = (c.length || (kind === 'bus' ? 11 : 6.2)) * m, Hh = (kind === 'bus' ? 3.1 : 2.5) * m;
  const dur = c.dur || 1.6, moving = ct < dur, speed = moving ? 1 - pr(ct, 0, dur) : 0;
  const brake = ct > dur ? Math.exp(-(ct - dur) * 6) * Math.sin((ct - dur) * 18) * 0.035 : 0;
  const col = c.color || '#1d2440', stripe = c.stripe || '#f1c453';
  ctx.save();
  ctx.translate(s[0], s[1]);
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.beginPath(); ctx.ellipse(0, 0, L * 0.55, m * 0.5, 0, 0, 7); ctx.fill();
  // speed lines behind it while it moves
  if (speed > 0.05) {
    ctx.strokeStyle = `rgba(255,255,255,${0.5 * speed})`; ctx.lineCap = 'round';
    const R = rng(5);
    for (let i = 0; i < 9; i++) {
      const yy = -Hh * (0.1 + R() * 0.85), len = L * (0.4 + R() * 0.8) * speed, x0 = -dir * (L * 0.55 + R() * L * 0.2);
      ctx.lineWidth = Math.max(2, m * 0.08); ctx.beginPath(); ctx.moveTo(x0, yy); ctx.lineTo(x0 - dir * len, yy); ctx.stroke();
    }
  }
  ctx.rotate(dir * brake + Math.sin(ct * 30) * 0.004 * speed);
  ctx.scale(dir, 1);
  const bounce = moving ? Math.sin(ct * 22) * m * 0.03 : 0;
  ctx.translate(0, bounce);
  // body
  const x0 = -L / 2, wr = m * 0.5;
  ctx.fillStyle = col; rrect(x0, -Hh - wr * 0.6, L, Hh, m * 0.35); ctx.fill();
  ctx.fillStyle = shade(col, -0.35); ctx.fillRect(x0, -wr * 0.6 - m * 0.35, L, m * 0.35);
  ctx.fillStyle = stripe; ctx.fillRect(x0, -Hh * 0.38 - wr * 0.6, L, m * 0.16);
  // windows
  const winY = -Hh - wr * 0.6 + m * 0.3, winH = Hh * (kind === 'bus' ? 0.36 : 0.32);
  if (kind === 'bus') {
    const n = 6, ww = (L - m * 1.4) / n;
    for (let i = 0; i < n; i++) { ctx.fillStyle = 'rgba(140,170,210,0.55)'; rrect(x0 + m * 0.4 + i * ww, winY, ww - m * 0.18, winH, m * 0.12); ctx.fill(); }
    ctx.fillStyle = 'rgba(190,215,240,0.75)'; rrect(L / 2 - m * 0.95, winY, m * 0.75, winH * 1.5, m * 0.15); ctx.fill();
  } else {
    ctx.fillStyle = 'rgba(190,215,240,0.75)'; rrect(L / 2 - m * 1.4, winY, m * 1.1, winH, m * 0.2); ctx.fill();
  }
  ctx.fillStyle = '#ffe9a8'; ctx.beginPath(); ctx.arc(L / 2 - m * 0.12, -wr * 0.6 - m * 0.75, m * 0.14, 0, 7); ctx.fill();
  // side label
  if (c.label) {
    ctx.save(); ctx.scale(dir, 1);
    font(800, Math.max(8, m * (kind === 'bus' ? 0.55 : 0.6)), 'Inter', `${m * 0.04}px`);
    ctx.fillStyle = c.labelColor || '#ffffff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const ly = kind === 'bus' ? -Hh * 0.62 - wr * 0.6 : -Hh * 0.5 - wr * 0.6, lx = dir * (kind === 'bus' ? 0 : -m * 0.8);
    ctx.fillText(c.label, lx, ly + (kind === 'bus' ? m * 0.55 : 0));
    ctx.restore();
  }
  // wheels, spinning while it moves
  const spin = ct < dur ? (c.from ? Math.hypot(...sub(p, c.from)) : 0) / 0.5 : (c.from ? Math.hypot(...sub(c.to, c.from)) / 0.5 : 0);
  for (const wx of [x0 + L * 0.2, x0 + L * 0.8]) {
    ctx.fillStyle = '#111318'; ctx.beginPath(); ctx.arc(wx, -wr * 0.6 + bounce * -1, wr, 0, 7); ctx.fill();
    ctx.fillStyle = '#9aa1ad'; ctx.beginPath(); ctx.arc(wx, -wr * 0.6, wr * 0.45, 0, 7); ctx.fill();
    ctx.strokeStyle = '#3a3f4a'; ctx.lineWidth = Math.max(1, wr * 0.12);
    for (let j = 0; j < 3; j++) { const an = spin + j * 2.094; ctx.beginPath(); ctx.moveTo(wx, -wr * 0.6); ctx.lineTo(wx + Math.cos(an) * wr * 0.45, -wr * 0.6 + Math.sin(an) * wr * 0.45); ctx.stroke(); }
  }
  ctx.restore();
};
CARDS.vehicle.noSlide = true;

// Icons rain down into a grid while a counter below counts them (the reference's "0 → 37 → 73 → 113 goals").
// groups: [{n, color, t|at, dur}], empty: unfilled slots (outlined, pulse at emptyT/emptyAt), icon: ball|doc|dot, counter label.
function rainLayout(c) {
  const n = c.groups.reduce((s, g) => s + g.n, 0) + (c.empty || 0), cols = c.cols || 12, cell = c.cell || 62;
  return { n, cols, cell, rows: Math.ceil(n / cols) };
}
function rainIcon(kind, x, y, r, col) {
  if (kind === 'ball') { drawBall(x, y, r); if (col && col !== S.accent) { ctx.save(); ctx.globalAlpha *= 0.55; ctx.fillStyle = col; ctx.globalCompositeOperation = 'multiply'; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); ctx.restore(); } return; }   // a group colour tints the ball
  if (kind === 'doc') {
    ctx.fillStyle = col; rrect(x - r * 0.78, y - r, r * 1.56, r * 2, r * 0.18); ctx.fill();
    ctx.fillStyle = 'rgba(0,0,0,0.28)';
    for (let i = 0; i < 3; i++) ctx.fillRect(x - r * 0.5, y - r * 0.5 + i * r * 0.42, r * (i === 2 ? 0.6 : 1.0), r * 0.14);
    return;
  }
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.beginPath(); ctx.arc(x - r * 0.3, y - r * 0.3, r * 0.35, 0, 7); ctx.fill();
}
CARDS.rain = function (c, ct, cx, cy) {
  const { cols, cell, rows } = rainLayout(c), gw = cols * cell, top = cy - rows * cell / 2, r = cell * 0.36;
  const slot = i => [cx - gw / 2 + (i % cols + 0.5) * cell, top + (Math.floor(i / cols) + 0.5) * cell];
  let idx = 0, landed = 0;
  const R = rng(c.seed || 9);
  // empty slots first (outlines), so filled icons sit on top
  const total = c.groups.reduce((s, g) => s + g.n, 0);
  for (let i = 0; i < total + (c.empty || 0); i++) {
    const [x, y] = slot(i);
    ctx.strokeStyle = 'rgba(255,255,255,0.13)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.stroke();
  }
  for (const g of c.groups) {
    const t0 = g.t || 0, d = g.dur || 1.6;
    for (let j = 0; j < g.n; j++, idx++) {
      const land = t0 + (g.n > 1 ? j / (g.n - 1) : 0) * d + 0.45, f = pr(ct, land - 0.45, 0.45);
      R(); const sx = (R() - 0.5) * 600;
      if (f <= 0) continue;
      const [x, y] = slot(idx);
      if (f >= 1) landed++;
      const yy = f < 1 ? lerp(top - 900 - R() * 200, y, f * f) : y - Math.max(0, Math.sin(Math.min(1, (ct - land) / 0.25) * Math.PI)) * cell * 0.15;
      const xx = f < 1 ? lerp(x + sx, x, f) : x;
      ctx.globalAlpha = Math.min(1, f * 3);
      rainIcon(c.icon || 'dot', xx, yy, r, g.color || S.accent);
      ctx.globalAlpha = 1;
    }
  }
  if (c.empty) {
    const pk = c.emptyT != null ? pr(ct, c.emptyT, 0.4) : 0;
    for (let i = total; i < total + c.empty; i++) {
      const [x, y] = slot(i);
      if (pk > 0) {
        ctx.strokeStyle = c.emptyColor || '#ffffff'; ctx.lineWidth = 4;
        ctx.globalAlpha = 0.6 + 0.4 * Math.sin(ct * 8);
        ctx.beginPath(); ctx.arc(x, y, r * (1 + 0.4 * eBack(pk)), 0, 7); ctx.stroke();
        ctx.globalAlpha = 1;
      }
    }
    if (pk > 0 && c.emptyLabel) {
      const [x, y] = slot(total + c.empty - 1);
      ctx.globalAlpha = pk; font(700, 26, 'Mono', '3px'); ctx.fillStyle = c.emptyColor || '#ffffff'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      ctx.fillText(c.emptyLabel.toUpperCase(), x - r * 1.8, y + cell); ctx.globalAlpha = 1;
    }
  }
  // counter
  const by = top + rows * cell + (c.counterGap || 130);
  font(800, c.counterSize || 120, 'Inter', '-3px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = '#f4f2ec'; ctx.fillText(String(landed) + (c.suffix || ''), cx, by);
  if (c.label) { font(600, 24, 'Mono', '6px'); ctx.fillStyle = '#9aa1ad'; ctx.fillText(c.label.toUpperCase(), cx, by + 48); }
};
CARDS.rain.noSlide = true;

// A giant word whips across the screen (with a motion trail and a flash), then settles as a label or flies past the camera.
// mode: "sweep" (default; settle: true keeps it at the end size) or "through" (zooms toward the camera and out: a transition).
CARDS.flytext = function (c, ct, cx, cy) {
  const d = c.dur || 0.7, size = c.size || 300, col = c.color || '#ffffff';
  font(900, size, 'Inter', '-4px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const tw = ctx.measureText(c.text).width;
  const draw = (x, sc, a, blur) => {
    ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, cy); ctx.scale(sc, sc);
    if (c.outline !== false) { ctx.lineWidth = 14; ctx.strokeStyle = 'rgba(8,10,15,0.85)'; ctx.lineJoin = 'round'; ctx.strokeText(c.text, 0, 0); }
    ctx.shadowColor = rgba(col, 0.6); ctx.shadowBlur = blur; ctx.fillStyle = col; ctx.fillText(c.text, 0, 0);
    ctx.restore();
  };
  if (c.mode === 'through') {
    const k = pr(ct, 0, d); if (k <= 0 || k >= 1) return;
    const sc = 0.3 * Math.pow(30, k * k);
    draw(cx, sc, 1 - pr(k, 0.6, 0.4), 20);
    return;
  }
  const end = c.endScale != null ? c.endScale : 0.38, dir = c.dir || -1;
  const k = pr(ct, 0, d), e = eOut(k);
  const x0 = cx - dir * (W / 2 + tw / 2 + 40), x1 = c.settle === false ? cx + dir * (W / 2 + tw / 2 + 40) : cx;
  const x = lerp(x0, x1, c.settle === false ? k : e), sc = c.settle === false ? 1 : lerp(1, end, ease(pr(ct, d * 0.35, d * 0.65)));
  if (k < 1) for (let g = 4; g >= 1; g--) draw(x - dir * g * 70 * (1 - e), sc, 0.12 * (5 - g), 0);
  if (c.settle === false && k >= 1) return;
  draw(x, sc, 1, k < 1 ? 40 : 18);
  const fk = pr(ct, d, 0.45);
  if (c.settle !== false && fk > 0 && fk < 1) {   // sparkle burst as it lands
    const R = rng(21); ctx.fillStyle = `rgba(255,255,255,${1 - fk})`;
    for (let i = 0; i < 40; i++) { const an = R() * 6.28, rr = (60 + R() * 260) * eOut(fk) * end * 2; ctx.fillRect(cx + Math.cos(an) * rr, cy + Math.sin(an) * rr * 0.5, 4, 4); }
  }
};
CARDS.flytext.noSlide = true;

// ---------- ideas from statbolthq (Reference 6) ----------
// Word-by-word captions: each word appears as it is spoken, the current phrase only; key words get a selection box.
// Words and times come from cues.py (spec.captionWords), so they follow the real voice.
function drawCaptions(t) {
  const W0 = S.spec.captionWords || [];
  let cur = -1;
  for (let i = 0; i < W0.length; i++) if (W0[i].t <= t) cur = i;
  if (cur < 0 && W0.length) { const g0 = W0[0].g; cur = W0.filter(w => w.g === g0).length - 1; t = W0[cur].t + 1; }   // frame 1 (thumbnail): the opening phrase, whole
  if (cur < 0) return;
  const g = W0[cur].g, words = W0.filter((w, i) => w.g === g && i <= cur);
  const last = W0.filter(w => w.g === g).slice(-1)[0], nextG = W0.find(w => w.g > g);
  const fade = nextG ? 1 : 1 - pr(t, last.t + 1.6, 0.3);   // the final phrase fades after its last word
  if (fade <= 0) return;
  const size = S.spec.captionSize || 80, lh = size * 1.18, maxW = 940;
  font(800, size, 'Inter', '-1.5px');
  const sp = ctx.measureText(' ').width, lines = [[]];
  let x = 0;
  for (const w of words) {
    const ww = ctx.measureText(w.w).width;
    if (x > 0 && x + sp + ww > maxW) { lines.push([]); x = 0; }
    else if (x > 0) x += sp;
    lines[lines.length - 1].push({ ...w, x, ww });
    x += ww;
  }
  const y0 = S.spec.captionY || 440;
  ctx.save(); ctx.globalAlpha = fade; ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  lines.forEach((line, li) => {
    const lw = line.length ? line[line.length - 1].x + line[line.length - 1].ww : 0, ox = W / 2 - lw / 2, y = y0 + li * lh;
    for (const w of line) {
      const age = t - w.t, isCur = w === line[line.length - 1] && li === lines.length - 1;
      const pop = eBack(Math.min(1, age / 0.16));
      ctx.save(); ctx.translate(ox + w.x + w.ww / 2, y - size * 0.35); ctx.scale(0.9 + 0.1 * pop, 0.9 + 0.1 * pop); ctx.translate(-(ox + w.x + w.ww / 2), -(y - size * 0.35));
      if (w.key) {   // selection box with two handles, like a design tool
        const core = w.w.replace(/[,.;:?!]+$/, ''), cw = ctx.measureText(core).width;
        const k = eOut(Math.min(1, age / 0.2)), pad = 10, bx = ox + w.x - pad, by = y - size * 0.86, bw = cw + pad * 2, bh = size * 1.08;
        ctx.strokeStyle = S.spec.captionBox || '#4fb3ff'; ctx.lineWidth = 3;
        ctx.strokeRect(bx, by, bw * k, bh);
        ctx.fillStyle = ctx.strokeStyle;
        ctx.beginPath(); ctx.arc(bx, by, 7, 0, 7); ctx.fill();
        if (k > 0.9) { ctx.beginPath(); ctx.arc(bx + bw, by + bh, 7, 0, 7); ctx.fill(); }
      }
      ctx.fillStyle = w.key || isCur ? '#ffffff' : '#7d838e';
      font(w.key || isCur ? 800 : 600, size, 'Inter', '-1.5px');
      ctx.fillText(w.w, ox + w.x, y);
      ctx.restore();
    }
  });
  ctx.restore();
}

// Whiteboard tactics board, "drawn from match reports": numbered discs, marker names, and the ball travelling
// along hand-drawn pass lines. The view can zoom and follow the move (cam keyframes).
// Board spots you can aim at by name, so shots always end in the goal (user: "the shot lines aren't even in the goal"):
// "goal", "goal-left", "goal-right" (inside the posts, on the line), "spot" (penalty spot).
function tacSpot(name, bw, bh) {
  const m = 34, PW = bw - 2 * m, PH = bh - 2 * m, gy = (m - 4) / bh, half = PW * 0.045 / bw;
  return { goal: [0.5, gy], 'goal-left': [0.5 - half, gy], 'goal-right': [0.5 + half, gy], spot: [0.5, (m + PH * 0.135) / bh] }[name];
}
function tacXY(c, p, bw, bh) {
  if (typeof p === 'string') p = tacSpot(p, bw, bh) || [0.5, 0.03];
  const v = typeof p === 'number' ? [c.players[p].x + 0.035, c.players[p].y + 0.025] : p;
  return [(v[0] - 0.5) * bw, (v[1] - 0.5) * bh];
}
CARDS.tactic = function (c, ct, cx, cy) {
  const bw = c.w || 980, bh = c.h || 1180, home = c.home || '#d0263a', away = c.away || '#e9dcb4';
  const dark = c.theme === 'dark', ink = dark ? '#ecebe6' : '#17181c', a = eOut(pr(ct, 0, 0.5));
  // camera on the board: keyframes {t, s, x, y} in board fractions
  const cam = c.cam || [];
  let fs = 1, fx = 0.5, fy = 0.5;
  if (cam.length) {   // each keyframe starts its move when its word is said, and takes about a second
    let i = -1; while (i < cam.length - 1 && ct >= (cam[i + 1].t || 0)) i++;
    if (i >= 0) {
      const A = i > 0 ? cam[i - 1] : { s: 1, x: 0.5, y: 0.5 }, B = cam[i], k = ease(pr(ct, B.t || 0, B.dur || 1.0));
      fs = lerp(A.s ?? 1, B.s ?? 1, k); fx = lerp(A.x ?? 0.5, B.x ?? 0.5, k); fy = lerp(A.y ?? 0.5, B.y ?? 0.5, k);
    }
  }
  ctx.save();
  ctx.beginPath(); ctx.rect(0, c.clipTop != null ? c.clipTop : 520, W, H); ctx.clip();   // zooming never covers the captions
  ctx.globalAlpha *= a;
  ctx.translate(cx, cy + (1 - a) * 80);
  fs *= 1 + (c.drift != null ? c.drift : 0.03) * ct;   // slow push-in so the board is never static
  ctx.scale(fs, fs);
  ctx.translate(-(fx - 0.5) * bw, -(fy - 0.5) * bh);
  ctx.rotate(c.tilt != null ? c.tilt : -0.012);
  // paper
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 20;
  ctx.fillStyle = dark ? '#0f1214' : '#eceef0'; ctx.fillRect(-bw / 2, -bh / 2, bw, bh);
  ctx.shadowColor = 'transparent';
  const R = rng(4);
  if (!dark) for (let i = 0; i < 500; i++) { ctx.fillStyle = `rgba(120,130,140,${R() * 0.07})`; ctx.fillRect(-bw / 2 + R() * bw, -bh / 2 + R() * bh, 3, 3); }
  // half pitch, goal at the top
  ctx.strokeStyle = dark ? 'rgba(205,215,180,0.32)' : 'rgba(40,44,52,0.38)'; ctx.lineWidth = 3;
  const m = 34, L = -bw / 2 + m, T = -bh / 2 + m, PW = bw - 2 * m, PH = bh - 2 * m;
  if (dark) { const pg = ctx.createLinearGradient(0, T, 0, T + PH); pg.addColorStop(0, 'rgba(88,104,52,0.30)'); pg.addColorStop(1, 'rgba(40,52,30,0.10)'); ctx.fillStyle = pg; ctx.fillRect(L, T, PW, PH); }
  ctx.strokeRect(L, T, PW, PH);
  ctx.strokeRect(L + PW * 0.2, T, PW * 0.6, PH * 0.2);
  ctx.strokeRect(L + PW * 0.37, T, PW * 0.26, PH * 0.07);
  ctx.strokeRect(L + PW * 0.44, T - 14, PW * 0.12, 14);
  ctx.beginPath(); ctx.arc(L + PW / 2, T + PH * 0.2, PW * 0.12, 0.25 * Math.PI, 0.75 * Math.PI); ctx.stroke();
  ctx.save(); ctx.fillStyle = ctx.strokeStyle; ctx.beginPath(); ctx.arc(L + PW / 2, T + PH * 0.135, 5, 0, 7); ctx.fill(); ctx.restore();   // penalty spot
  ctx.beginPath(); ctx.arc(L + PW / 2, T + PH, PW * 0.17, Math.PI, 2 * Math.PI); ctx.stroke();
  if (c.note !== false && !(dark && c.note == null)) { font(400, 22, 'Marker'); ctx.fillStyle = ink; ctx.textAlign = 'right'; ctx.fillText((c.note || 'Drawn from match reports').toUpperCase(), bw / 2 - 40, -bh / 2 + 26); }
  // pass lines drawn so far, X where each pass starts
  const moves = c.moves || [];
  let ball = tacXY(c, c.ball != null ? c.ball : (moves[0] ? moves[0].from : 0), bw, bh), moving = false;
  ctx.strokeStyle = ink; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const involved = new Map();
  for (const mv of moves) {
    const k = pr(ct, mv.t || 0, mv.dur || 0.7);
    if (k <= 0) continue;
    const p0 = tacXY(c, mv.from, bw, bh), p1 = tacXY(c, mv.to, bw, bh), e = mv.kind === 'shot' ? k : ease(k);
    const mid = mv.curve ? [(p0[0] + p1[0]) / 2 + mv.curve * (p1[1] - p0[1]), (p0[1] + p1[1]) / 2 - mv.curve * (p1[0] - p0[0])] : null;
    const at = u => mid ? [(1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * mid[0] + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * mid[1] + u * u * p1[1]] : [lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)];
    const shotDash = dark && mv.kind === 'shot';
    ctx.save(); ctx.strokeStyle = mv.color || (shotDash ? '#ff4d5e' : ink);
    ctx.setLineDash(mv.kind === 'run' ? [14, 14] : shotDash ? [10, 10] : []);
    ctx.beginPath(); ctx.moveTo(...p0);
    for (let s = 1; s <= 24; s++) ctx.lineTo(...at(e * s / 24));
    ctx.stroke(); ctx.setLineDash([]);
    if (shotDash && k >= 1) { const q = at(0.97), ang = Math.atan2(p1[1] - q[1], p1[0] - q[0]); ctx.fillStyle = ctx.strokeStyle; ctx.beginPath(); ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p1[0] - 20 * Math.cos(ang - 0.45), p1[1] - 20 * Math.sin(ang - 0.45)); ctx.lineTo(p1[0] - 20 * Math.cos(ang + 0.45), p1[1] - 20 * Math.sin(ang + 0.45)); ctx.fill(); }
    ctx.restore();
    if (mv.kind !== 'run' && !(dark && mv.kind === 'shot')) {
      const r = 11; ctx.beginPath(); ctx.moveTo(p0[0] - r, p0[1] - r); ctx.lineTo(p0[0] + r, p0[1] + r); ctx.moveTo(p0[0] + r, p0[1] - r); ctx.lineTo(p0[0] - r, p0[1] + r); ctx.stroke();
      ball = at(e); moving = k < 1;
    } else if (mv.kind === 'shot' && mv.ball !== false) { ball = at(e); moving = k < 1; }
    if (typeof mv.from === 'number') involved.set(mv.from, mv.t || 0);
    if (typeof mv.to === 'number') involved.set(mv.to, Math.min(involved.get(mv.to) ?? 1e9, (mv.t || 0) + (mv.dur || 0.7) * 0.8));
  }
  // players
  for (const [i, p] of c.players.entries()) {
    const x = (p.x - 0.5) * bw + Math.sin(ct * 1.3 + i * 1.7) * 4, y = (p.y - 0.5) * bh + Math.cos(ct * 1.1 + i * 2.3) * 4, r = c.r || 34;   // players shuffle slightly
    const pk = eBack(pr(ct, (p.t || 0) + 0.1 + i * 0.02, 0.3));
    if (pk <= 0) continue;
    ctx.save(); ctx.translate(x, y); ctx.scale(pk, pk);
    const col = p.team === 'away' ? away : home;
    ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.beginPath(); ctx.arc(2, 5, r, 0, 7); ctx.fill();
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill();
    ctx.strokeStyle = p.team === 'away' ? 'rgba(0,0,0,0.15)' : 'rgba(255,255,255,0.8)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(0, 0, r - 5, 0, 7); ctx.stroke();
    if (p.ring) { ctx.strokeStyle = p.ring; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(0, 0, r + 9 + 3 * Math.sin(ct * 6), 0, 7); ctx.stroke(); }
    font(800, r * 0.78, 'Inter'); ctx.fillStyle = p.team === 'away' ? (c.awayText || '#3b3424') : '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(String(p.n), 0, 2);
    ctx.restore();
    const nt = p.nameT != null ? p.nameT : involved.get(i);
    if (p.name && nt != null && ct >= nt) {
      const nk = Math.min(1, (ct - nt) / 0.35), txt = p.name.toUpperCase();
      if (dark) font(800, 24, 'Inter', '2px'); else font(400, 30, 'Marker'); ctx.fillStyle = ink; ctx.textBaseline = 'middle';
      const left = p.label === 'left'; ctx.textAlign = left ? 'right' : 'left';
      ctx.save(); ctx.beginPath();
      const tw = ctx.measureText(txt).width;
      ctx.rect(left ? x - r - 12 - tw * nk : x + r + 10, y - 30, tw * nk + 4, 60); ctx.clip();
      ctx.fillText(txt, left ? x - r - 10 : x + r + 10, y + 1);
      ctx.restore();
    }
  }
  // event tags that pop on the board ("HANDBALL", "17' PEN"): {t, x, y, text, color}
  for (const tg of c.tags || []) {
    const tk = eBack(pr(ct, tg.t || 0, 0.3)); if (tk <= 0) continue;
    const [x, y] = [(tg.x - 0.5) * bw, (tg.y - 0.5) * bh];
    font(800, 24, 'Inter', '3px'); const tw = ctx.measureText(tg.text.toUpperCase()).width + 34;
    ctx.save(); ctx.translate(x, y); ctx.scale(tk, tk); ctx.rotate(-0.04);
    ctx.fillStyle = tg.color || '#d6283b'; rrect(-tw / 2, -22, tw, 44, 10); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(tg.text.toUpperCase(), 0, 1); ctx.restore();
  }
  // ball
  const br = 15 + (moving ? 3 : 0);
  if (c.showBall !== false) drawBall(ball[0], ball[1], br);
  ctx.restore();
};
CARDS.tactic.noSlide = true;

// xG spheres: one glossy sphere per team, its size growing with the expected-goals value while the number counts up above it.
// items: [{label, value, from, color, t}], max (value of the biggest sphere), title, dur, gap.
CARDS.xg = function (c, ct, cx, cy) {
  const items = c.items, max = c.max || Math.max(...items.map(it => it.value)), gap = c.gap || 440;
  items.forEach((it, i) => {
    const t0 = it.t || 0, k = ease(pr(ct, t0, c.dur || 1.4)), a = pr(ct, t0, 0.25);
    if (a <= 0) return;
    const v = lerp(it.from != null ? it.from : 0, it.value, k), x = cx + (i - (items.length - 1) / 2) * gap;
    const r = 34 + 150 * Math.sqrt(Math.max(0, v) / max), col = it.color || '#d6283b';
    ctx.save(); ctx.globalAlpha *= a;
    // floor ring + shadow
    // floor: a thin coloured ring, then a soft contact shadow right under the ball (user: the old shading looked like a second ball)
    ctx.strokeStyle = col; ctx.globalAlpha *= 0.7; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(x, cy, r * 1.3, r * 0.2, 0, 0, 7); ctx.stroke(); ctx.globalAlpha /= 0.7;
    const sh = ctx.createRadialGradient(x, cy, 0, x, cy, r * 1.0); sh.addColorStop(0, 'rgba(0,0,0,0.6)'); sh.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.save(); ctx.translate(x, cy); ctx.scale(1, 0.18); ctx.translate(-x, -cy); ctx.fillStyle = sh; ctx.beginPath(); ctx.arc(x, cy, r * 1.0, 0, 7); ctx.fill(); ctx.restore();
    // the sphere: one light from the top left, shading falling away to the bottom right, a faint bounce light on the lower rim
    const bx = x, by = cy - r;
    const g = ctx.createRadialGradient(bx - r * 0.4, by - r * 0.45, r * 0.05, bx - r * 0.1, by - r * 0.1, r * 1.15);
    g.addColorStop(0, '#ffffff'); g.addColorStop(0.1, shade(col, 0.35)); g.addColorStop(0.45, col); g.addColorStop(0.85, shade(col, -0.45)); g.addColorStop(1, shade(col, -0.7));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(bx, by, r, 0, 7); ctx.fill();
    const rim = ctx.createRadialGradient(bx, by + r * 0.95, 0, bx, by + r * 0.95, r * 0.7); rim.addColorStop(0, 'rgba(255,255,255,0.12)'); rim.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.save(); ctx.beginPath(); ctx.arc(bx, by, r, 0, 7); ctx.clip(); ctx.fillStyle = rim; ctx.fillRect(bx - r, by, 2 * r, r); ctx.restore();
    // number + label above
    const ny = cy - 2 * r - 46;
    font(700, 76, 'Mono'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = it.textColor || (i ? '#f1c453' : '#ffffff');
    ctx.fillText(v.toFixed(2), x, ny);
    font(600, 22, 'Mono', '4px'); ctx.fillStyle = '#9aa3b2'; ctx.fillText((it.label || '').toUpperCase(), x, ny + 34);
    if (it.badge) drawBadge(x, ny - 100, 56, it.badge);
    ctx.restore();
  });
  if (c.title) { font(600, 26, 'Mono', '6px'); ctx.fillStyle = '#c9ced8'; ctx.textAlign = 'center'; ctx.fillText(c.title.toUpperCase(), cx, cy + 90); }
};
CARDS.xg.noSlide = true;

// Before / after swing: each row shows a stat from the first half crossing over to the second (numbers count, an arrow draws).
// rows: [{label, from, to, t, decimals, good}], title.
CARDS.swing = function (c, ct, cx, cy) {
  ctx.save(); const fz = 1 + 0.02 * ct; ctx.translate(cx, cy + Math.sin(ct * 1.2) * 6); ctx.scale(fz, fz); ctx.translate(-cx, -cy);   // gentle float + push
  const rows = c.rows, rh = c.rowH || 170, w = c.w || 900, top = cy - rows.length * rh / 2;
  if (c.title) { font(600, 24, 'Mono', '6px'); ctx.fillStyle = '#9aa3b2'; ctx.textAlign = 'center'; ctx.fillText(c.title.toUpperCase(), cx, top - 24); }
  font(600, 20, 'Mono', '5px'); ctx.fillStyle = '#6f7785'; ctx.textAlign = 'center';
  ctx.fillText('1ST HALF', cx - w * 0.28, top + 8); ctx.fillText('2ND HALF', cx + w * 0.28, top + 8);
  rows.forEach((r, i) => {
    const t0 = r.t != null ? r.t : 0.2 + i * 0.6, a = eOut(pr(ct, t0, 0.35)), k = ease(pr(ct, t0 + 0.35, 1.0));
    if (a <= 0) return;
    const y = top + 30 + i * rh + rh / 2, d = r.decimals || 0, good = r.good !== false;
    ctx.save(); ctx.globalAlpha *= a; ctx.translate((1 - a) * 80, 0);
    ctx.fillStyle = 'rgba(12,14,20,0.82)'; rrect(cx - w / 2, y - rh / 2 + 10, w, rh - 20, 22); ctx.fill();
    font(700, 26, 'Inter', '1px'); ctx.fillStyle = '#c9ced8'; ctx.textAlign = 'center'; ctx.fillText(r.label, cx, y - rh / 2 + 44);
    font(800, 84, 'Inter', '-2px'); ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#8a92a0'; ctx.fillText(Number(r.from).toFixed(d), cx - w * 0.28, y + 48);
    const v = lerp(r.from, r.to, k); ctx.fillStyle = k >= 1 ? (good ? '#3fe08a' : '#ff4d5e') : '#ffffff';
    if (k >= 1) { ctx.shadowColor = ctx.fillStyle; ctx.shadowBlur = 18 + 12 * Math.sin(ct * 4 + i); }
    ctx.fillText(v.toFixed(d), cx + w * 0.28, y + 48); ctx.shadowBlur = 0;
    const x0 = cx - w * 0.1, x1 = lerp(x0, cx + w * 0.1, k);   // the arrow draws across
    ctx.strokeStyle = '#f1c453'; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x0, y + 20); ctx.lineTo(x1, y + 20); ctx.stroke();
    if (k > 0.05) { ctx.fillStyle = '#f1c453'; ctx.beginPath(); ctx.moveTo(x1 + 14, y + 20); ctx.lineTo(x1 - 6, y + 6); ctx.lineTo(x1 - 6, y + 34); ctx.fill(); }
    ctx.restore();
  });
  ctx.restore();
};
CARDS.swing.noSlide = true;

// Drawn player card (idea backlog): a trading-card frame with the player drawn from the chest up and a tag strip ("MALEN · 17' PEN").
// player: {name, num, kit, skin, hair}, tag, side: right|left, color (frame), tilt.
CARDS.pcard = function (c, ct, cx, cy) {
  const k = eBack(pr(ct, 0, 0.5)), side = c.side === 'left' ? -1 : 1, w = c.w || 420, h = c.h || 560;
  if (k <= 0) return;
  ctx.save(); ctx.translate(cx + side * (1 - k) * 700, cy); ctx.rotate((c.tilt != null ? c.tilt : 0.05) * side * (1.4 - 0.4 * k));
  ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 18;
  ctx.fillStyle = c.color || '#f1c453'; rrect(-w / 2 - 10, -h / 2 - 10, w + 20, h + 20, 22); ctx.fill(); ctx.shadowColor = 'transparent';
  const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2); g.addColorStop(0, '#2a2f3a'); g.addColorStop(1, '#0d0f14');
  ctx.fillStyle = g; rrect(-w / 2, -h / 2, w, h, 16); ctx.fill();
  ctx.save(); rrect(-w / 2, -h / 2, w, h, 16); ctx.clip();
  const p = Object.assign({ front: true, chest: true }, c.player);
  drawPlayer(0, h * 0.95, h * 1.25, p, ct, 0, 1);
  const sh = ctx.createLinearGradient(0, h * 0.1, 0, h / 2); sh.addColorStop(0, 'rgba(13,15,20,0)'); sh.addColorStop(1, 'rgba(13,15,20,0.9)'); ctx.fillStyle = sh; ctx.fillRect(-w / 2, 0, w, h / 2);
  ctx.restore();
  if (c.tag) { font(800, 26, 'Inter', '3px'); const tw = ctx.measureText(c.tag.toUpperCase()).width + 30;
    ctx.fillStyle = c.tagColor || '#f1c453'; rrect(-w / 2 + 18, -h / 2 + 18, tw, 46, 8); ctx.fill();
    ctx.fillStyle = '#111'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(c.tag.toUpperCase(), -w / 2 + 33, -h / 2 + 42); }
  if (c.caption) { font(800, 40, 'Inter'); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(c.caption, 0, h / 2 - 30); }
  ctx.restore();
};
CARDS.pcard.noSlide = true;

// Stacked stat counter: each new stat counts up big at the bottom and pushes the older ones up, smaller and dimmer.
CARDS.stack = function (c, ct, cx, cy) {
  const items = c.items, size = c.size || 150;
  const shown = items.filter(it => ct >= (it.t || 0));
  shown.forEach((it, i) => {
    const depth = shown.length - 1 - i;
    // how far this item has been pushed up (eases when newer ones arrive)
    let push = 0;
    for (let j = i + 1; j < shown.length; j++) push += eOut(pr(ct, shown[j].t || 0, 0.4));
    const sc = Math.pow(0.5, push), y = cy - push * size * (c.gap || 1.3), al = Math.pow(0.75, push);
    const ink = eOut(pr(ct, it.t || 0, 0.35));
    const v = (it.value) * eOut(pr(ct, (it.t || 0), it.countDur || 0.7));
    const txt = (it.prefix || '') + v.toFixed(it.decimals || 0) + (it.suffix || '');
    ctx.save(); ctx.globalAlpha *= al * ink; ctx.translate(cx, y + (1 - ink) * 40); ctx.scale(sc, sc);
    font(800, size, 'Inter', '-3px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 24;   // stays readable over the pitch and players
    if (it.gold) { const g = ctx.createLinearGradient(0, -size * 0.8, 0, 0); g.addColorStop(0, GOLD[0]); g.addColorStop(1, GOLD[2]); ctx.fillStyle = g; }
    else ctx.fillStyle = it.color || '#f4f2ec';
    ctx.fillText(txt, 0, 0);
    if (it.label) { font(600, 32, 'Inter', '0px'); ctx.fillStyle = '#b3b9c3'; ctx.fillText(it.label, 0, 54); }
    ctx.restore();
    void depth;
  });
};
CARDS.stack.noSlide = true;

// Shot map on the real pitch: each shot pops as a dot with a ring where it was taken (world x, z in metres);
// blocked shots turn red with a cross at blockedT, goals turn gold. Drawn on the grass, under the players.
function drawShotMaps(cam) {
  for (const it of S.cur ? S.cur.cards : []) {
    const c = it.obj, ct = S.t - it.start;
    if (c.type !== 'shotmap' || ct < 0) continue;
    c.shots.forEach((s, i) => {
      const t0 = (s.t != null ? s.t : (c.step || 0.12) * i), k = pr(ct, t0, 0.35);
      if (k <= 0) return;
      const q = toCam(cam, [s.x, 0.02, s.z]);
      if (q[2] < NEAR) return;
      const p = proj(q), m = FOC / q[2] * (c.scale || 1);   // scale: bigger markers for aerial shots
      const bt = s.blocked ? (c.blockedT != null ? c.blockedT + i * 0.06 : null) : null;
      const isB = bt != null && ct >= bt, col = s.goal ? '#f1c453' : isB ? '#ff4d5e' : (s.color || c.color || '#f4f2ec');
      const ring = 1 - pr(ct, t0, 0.6);
      ctx.strokeStyle = col; ctx.lineWidth = Math.max(3, m * 0.14);
      if (ring > 0) { ctx.globalAlpha = ring; ctx.beginPath(); ctx.ellipse(p[0], p[1], m * (1 + 3 * (1 - ring)), m * (1 + 3 * (1 - ring)) * 0.36, 0, 0, 7); ctx.stroke(); ctx.globalAlpha = 1; }
      ctx.beginPath(); ctx.ellipse(p[0], p[1], m * 1.1, m * 0.4, 0, 0, 7); ctx.stroke();
      ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(p[0], p[1], m * 0.6 * eBack(k), m * 0.22 * eBack(k), 0, 0, 7); ctx.fill();
      if (isB) { const r = m * 0.7; ctx.beginPath(); ctx.moveTo(p[0] - r, p[1] - r * 0.4); ctx.lineTo(p[0] + r, p[1] + r * 0.4); ctx.moveTo(p[0] + r, p[1] - r * 0.4); ctx.lineTo(p[0] - r, p[1] + r * 0.4); ctx.stroke(); }
    });
  }
}
CARDS.shotmap = function () {};
CARDS.shotmap.noSlide = true;

// A stylised club badge (shield in club colours with initials). Not a real crest: never draw real club logos.
function drawBadge(x, y, h, b) {
  const w = h * 0.82, c1 = b.colors[0], c2 = b.colors[1] || '#ffffff', c3 = b.colors[2];
  ctx.save(); ctx.translate(x, y);
  const shield = () => { ctx.beginPath(); ctx.moveTo(-w / 2, -h / 2); ctx.lineTo(w / 2, -h / 2); ctx.lineTo(w / 2, h * 0.05);
    ctx.quadraticCurveTo(w / 2, h * 0.35, 0, h / 2); ctx.quadraticCurveTo(-w / 2, h * 0.35, -w / 2, h * 0.05); ctx.closePath(); };
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 6;
  shield(); ctx.fillStyle = c1; ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.save(); shield(); ctx.clip();
  if (b.style === 'stripes') { ctx.fillStyle = c2; for (let i = -3; i <= 3; i += 2) ctx.fillRect(i * w / 7 - w / 14, -h / 2, w / 7, h); }
  else if (b.style === 'diamond') { ctx.fillStyle = c2; ctx.beginPath(); ctx.moveTo(0, -h * 0.4); ctx.lineTo(w * 0.28, -h * 0.14); ctx.lineTo(0, h * 0.12); ctx.lineTo(-w * 0.28, -h * 0.14); ctx.closePath(); ctx.fill();
    if (c3) { ctx.fillStyle = c3; ctx.beginPath(); ctx.moveTo(0, -h * 0.26); ctx.lineTo(w * 0.13, -h * 0.14); ctx.lineTo(0, -h * 0.02); ctx.lineTo(-w * 0.13, -h * 0.14); ctx.closePath(); ctx.fill(); } }
  else { ctx.fillStyle = c2; ctx.fillRect(-w / 2, -h / 2, w, h * 0.26); }   // band across the top
  ctx.restore();
  ctx.strokeStyle = c3 && b.style !== 'diamond' ? c3 : '#f1c453'; ctx.lineWidth = Math.max(2, h * 0.04); shield(); ctx.stroke();
  if (b.text) {   // text is sized to fit inside the shield (it narrows towards the point)
    const diamond = b.style === 'diamond', ty = diamond ? h * 0.3 : h * 0.12, maxW = w * (diamond ? 0.5 : 0.72);
    let fs = h * (diamond ? 0.17 : 0.26);
    font(900, fs, 'Inter', '0px');
    const tw = ctx.measureText(b.text).width;
    if (tw > maxW) { fs *= maxW / tw; font(900, fs, 'Inter', '0px'); }
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    if (diamond) { ctx.fillStyle = b.textColor || c2; ctx.fillText(b.text, 0, ty); }
    else { ctx.fillStyle = b.textColor || '#ffffff'; ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = Math.max(2, fs * 0.08); ctx.strokeText(b.text, 0, ty); ctx.fillText(b.text, 0, ty); }
  }
  ctx.restore();
}

// Trophy-cabinet shelf (idea list): a lit glass cabinet whose slots fill as honours are named.
// items: [{kind: ball|cup|worldcup|boot, label, sub, t|at}], slots (total, extra ones stay empty), instant (already full),
// empty slot pulse with emptyT|emptyAt + emptyLabel.
CARDS.shelf = function (c, ct, cx, cy) {
  const n = Math.max(c.slots || 0, c.items.length), cw = c.w || 960, ch = c.h || 420;
  const a = eOut(pr(ct, 0, 0.45));
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(0, (1 - a) * 40);
  // cabinet
  const L = cx - cw / 2, T = cy - ch / 2;
  const g = ctx.createLinearGradient(0, T, 0, T + ch);
  g.addColorStop(0, '#20140c'); g.addColorStop(1, '#0d0805');
  ctx.fillStyle = g; rrect(L, T, cw, ch, 18); ctx.fill();
  ctx.strokeStyle = goldGrad(L, L + cw); ctx.lineWidth = 6; rrect(L, T, cw, ch, 18); ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,0.04)'; ctx.fillRect(L + 14, T + 14, cw * 0.18, ch - 28);   // glass glint
  const shelfY = T + ch - 70;
  ctx.fillStyle = goldGrad(L, L + cw); ctx.fillRect(L + 18, shelfY, cw - 36, 10);
  if (c.title) { font(600, 22, 'Mono', '5px'); ctx.fillStyle = '#e2d3ad'; ctx.textAlign = 'center'; ctx.fillText(c.title.toUpperCase(), cx, T - 22); }
  const sw = (cw - 60) / n;
  for (let i = 0; i < n; i++) {
    const x = L + 30 + sw * (i + 0.5), it = c.items[i];
    const t0 = it ? (c.instant ? -1 : (it.t != null ? it.t : 0.3 + i * 0.4)) : null;
    const k = it ? pr(ct, t0, 0.5) : 0;
    if (k <= 0) {   // empty slot
      ctx.setLineDash([8, 8]); ctx.strokeStyle = 'rgba(226,211,173,0.25)'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(x, shelfY - 70, 46, 0, 7); ctx.stroke(); ctx.setLineDash([]);
      if (!it && c.emptyT != null && ct >= c.emptyT) {
        const pk = pr(ct, c.emptyT, 0.4), pulse = 0.6 + 0.4 * Math.sin((ct - c.emptyT) * 6);
        ctx.strokeStyle = rgba(c.emptyColor || '#ff4d5e', pulse); ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(x, shelfY - 70, 46 * (1 + 0.2 * eBack(pk)), 0, 7); ctx.stroke();
        font(800, 54, 'Inter'); ctx.fillStyle = rgba(c.emptyColor || '#ff4d5e', pk); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText('?', x, shelfY - 66);
        if (c.emptyLabel) { font(600, 19, 'Mono', '3px'); ctx.textBaseline = 'alphabetic'; ctx.fillText(c.emptyLabel.toUpperCase(), x, shelfY + 44); }
      }
      continue;
    }
    // spotlight cone + item dropping onto the shelf
    const sp = ctx.createRadialGradient(x, shelfY - 60, 0, x, shelfY - 60, sw * 0.7);
    sp.addColorStop(0, `rgba(255,226,150,${0.22 * k})`); sp.addColorStop(1, 'rgba(255,226,150,0)');
    ctx.fillStyle = sp; ctx.fillRect(x - sw, T, sw * 2, ch);
    const drop = (1 - eOut(k)) * -120, s = Math.min(sw * 0.95, c.size || 150);
    ctx.save(); ctx.globalAlpha *= Math.min(1, k * 2);
    drawProp(it.kind || 'ball', x, shelfY + drop, s, it.text);
    ctx.restore();
    if (it.badge) {   // club badge pops in above the trophy
      const bk = eBack(pr(ct, t0 + 0.15, 0.35));
      if (bk > 0) { ctx.save(); ctx.translate(x, T + (c.badgeY || 112)); ctx.scale(bk, bk); drawBadge(0, 0, Math.min(sw * 0.8, c.badgeSize || 120), it.badge); ctx.restore(); }
    }
    const lk = pr(ct, t0 + 0.25, 0.3);
    if (lk > 0) {
      ctx.save(); ctx.globalAlpha *= lk; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      font(700, Math.min(26, sw * 0.17), 'Inter'); ctx.fillStyle = '#f4f2ec'; ctx.fillText(it.label || '', x, shelfY + 42);
      if (it.sub) { font(600, 19, 'Mono', '3px'); ctx.fillStyle = '#e2b84f'; ctx.fillText(String(it.sub).toUpperCase(), x, shelfY + 66 - 0); }
      ctx.restore();
    }
  }
  ctx.restore();
};
CARDS.shelf.noSlide = true;

// Tale of the tape (idea list): two names, bars sliding out from the middle for each stat; the bigger side wins the accent.
// left/right: {name, color}, rows: [{label, left, right, t|at, fmt: "comma"}]
CARDS.tape = function (c, ct, cx, cy) {
  const bw = c.w || 960, rows = c.rows, rh = c.rowH || 150, top = cy - (rows.length * rh) / 2;
  const a = eOut(pr(ct, 0, 0.4));
  ctx.save(); ctx.globalAlpha *= a;
  const lc = c.left.color || '#d0263a', rc = c.right.color || '#e8e8ea';
  font(800, 46, 'Inter', '-1px'); ctx.textBaseline = 'alphabetic';
  ctx.textAlign = 'left'; ctx.fillStyle = '#f4f2ec'; ctx.fillText(c.left.name, cx - bw / 2, top - 30);
  ctx.textAlign = 'right'; ctx.fillText(c.right.name, cx + bw / 2, top - 30);
  ctx.fillStyle = lc; ctx.fillRect(cx - bw / 2, top - 18, 80, 6); ctx.fillStyle = rc; ctx.fillRect(cx + bw / 2 - 80, top - 18, 80, 6);
  rows.forEach((r, i) => {
    const t0 = r.t != null ? r.t : 0.3 + i * 0.5, k = ease(pr(ct, t0, 0.9));
    const y = top + i * rh + rh * 0.55, mx = Math.max(r.left, r.right), half = bw / 2 - 20;
    // scale bars so the difference reads: the smaller side is measured against the bigger, from a floor
    const floor = r.floor != null ? r.floor : 0, wl = half * (r.left - floor) / (mx - floor), wr = half * (r.right - floor) / (mx - floor);
    font(600, 22, 'Mono', '4px'); ctx.fillStyle = '#9aa1ad'; ctx.textAlign = 'center'; ctx.fillText(r.label.toUpperCase(), cx, y - 46);
    ctx.fillStyle = 'rgba(255,255,255,0.06)'; rrect(cx - half - 10, y - 26, half * 2 + 20, 52, 26); ctx.fill();
    ctx.fillStyle = lc; rrect(cx - 4 - wl * k, y - 20, wl * k, 40, 20); ctx.fill();
    ctx.fillStyle = rc; rrect(cx + 4, y - 20, wr * k, 40, 20); ctx.fill();
    const f = v => (c.comma === false ? String(Math.round(v)) : Math.round(v).toLocaleString('en-GB'));
    const vk = pr(ct, t0 + 0.2, 0.8);
    font(r.left >= r.right ? 900 : 700, 50, 'Inter', '-1px'); ctx.textAlign = 'left';
    ctx.fillStyle = r.left >= r.right ? (c.win || '#f1c453') : '#cfd3da'; if (vk > 0) ctx.fillText(f(r.left * eOut(vk)), cx - bw / 2, y + 72);
    font(r.right > r.left ? 900 : 700, 50, 'Inter', '-1px'); ctx.textAlign = 'right';
    ctx.fillStyle = r.right > r.left ? (c.win || '#f1c453') : '#cfd3da'; if (vk > 0) ctx.fillText(f(r.right * eOut(vk)), cx + bw / 2, y + 72);
  });
  const capT = c.captionT != null ? c.captionT : c.captionAt;
  if (c.caption && capT != null && ct >= capT) {
    const pk = eBack(pr(ct, capT, 0.35)), y = top + rows.length * rh + 70;
    ctx.save(); ctx.translate(cx, y); ctx.scale(pk, pk);
    font(700, 28, 'Mono', '3px'); const tw = ctx.measureText(c.caption.toUpperCase()).width + 60;
    ctx.fillStyle = c.captionColor || '#f1c453'; rrect(-tw / 2, -32, tw, 64, 32); ctx.fill();
    ctx.fillStyle = '#16130e'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.caption.toUpperCase(), 0, 2);
    ctx.restore();
  }
  ctx.restore();
};
CARDS.tape.noSlide = true;

// Knockout tally (idea list: penalty-shootout dots): a row of circles, one per game, each with a small label underneath.
// `done` are already filled; the next one fills at `newAt`/`newT` with a slam. `mark: "x"` (red cross) or "check" (green tick).
// title, left/right labels for who the tally is about, `score` shows "done / n" big under the row.
CARDS.tally = function (c, ct, cx, cy) {
  if (c.items) return CARDS.tally.seq(c, ct, cx, cy);
  const n = c.n || 6, r = c.r || 58, gap = c.gap || 30, w = n * r * 2 + (n - 1) * gap, a = eOut(pr(ct, 0, 0.35));
  const filled = (c.done || 0) + (c.newT != null && ct >= c.newT ? 1 : 0);
  ctx.save(); ctx.globalAlpha *= a;
  ctx.fillStyle = 'rgba(8,10,15,0.72)'; rrect(cx - w / 2 - 40, cy - r - 90, w + 80, r * 2 + 200, 28); ctx.fill();
  if (c.title) { font(600, 24, 'Mono', '5px'); ctx.fillStyle = '#c9ced6'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(c.title.toUpperCase(), cx, cy - r - 44); }
  const col = c.mark === 'check' ? '#2ecc71' : '#ff4d5e';
  for (let i = 0; i < n; i++) {
    const x = cx - w / 2 + r + i * (2 * r + gap), on = i < filled, isNew = c.newT != null && i === (c.done || 0);
    const k = isNew ? pr(ct, c.newT, 0.3) : on ? 1 : 0;
    ctx.lineWidth = 5; ctx.strokeStyle = on ? col : 'rgba(255,255,255,0.22)';
    ctx.beginPath(); ctx.arc(x, cy, r, 0, 7); ctx.stroke();
    if (k > 0) {
      const sc = isNew ? lerp(1.8, 1, eOut(k)) : 1;
      ctx.save(); ctx.translate(x, cy); ctx.scale(sc, sc); ctx.globalAlpha *= Math.min(1, k * 2);
      ctx.fillStyle = rgba(col, 0.22); ctx.beginPath(); ctx.arc(0, 0, r - 4, 0, 7); ctx.fill();
      ctx.strokeStyle = col; ctx.lineWidth = 10; ctx.lineCap = 'round'; ctx.beginPath();
      if (c.mark === 'check') { ctx.moveTo(-r * 0.4, 0); ctx.lineTo(-r * 0.1, r * 0.32); ctx.lineTo(r * 0.45, -r * 0.35); }
      else { const q = r * 0.38; ctx.moveTo(-q, -q); ctx.lineTo(q, q); ctx.moveTo(q, -q); ctx.lineTo(-q, q); }
      ctx.stroke(); ctx.restore();
    }
    if (c.labels && c.labels[i]) {
      font(700, 19, 'Mono', '1px'); ctx.fillStyle = on ? '#f4f2ec' : '#7d838e'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      String(c.labels[i]).split('\n').forEach((l, j) => ctx.fillText(l.toUpperCase(), x, cy + r + 38 + j * 24));
    }
  }
  if (c.score) {
    font(800, 40, 'Inter', '-1px'); ctx.textAlign = 'center'; ctx.fillStyle = '#f4f2ec';
    ctx.fillText(c.score.replace('{n}', filled), cx, cy + r + 98);
  }
  ctx.restore();
};
CARDS.tally.noSlide = true;
// Sequence mode: each slot has its own mark and time, e.g. seven wins then three defeats.
// items: [{mark: "check"|"x", t|at, label}], r, gap, title, score ("{w}–{l}" counts the marks shown so far), rows (slots per row, default all)
CARDS.tally.seq = function (c, ct, cx, cy) {
  const I = c.items, n = I.length, per = c.perRow || n, rowsN = Math.ceil(n / per), r = c.r || 40, gap = c.gap || 18, rg = c.rowGap || 34;
  const w = per * r * 2 + (per - 1) * gap, h = rowsN * r * 2 + (rowsN - 1) * rg, a = eOut(pr(ct, 0, 0.3));
  ctx.save(); ctx.globalAlpha *= a;
  ctx.fillStyle = 'rgba(8,10,15,0.72)'; rrect(cx - w / 2 - 36, cy - h / 2 - (c.title ? 84 : 36), w + 72, h + (c.title ? 84 : 36) + (c.score ? 104 : 36), 28); ctx.fill();
  if (c.title) { font(600, 24, 'Mono', '5px'); ctx.fillStyle = '#c9ced6'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(c.title.toUpperCase(), cx, cy - h / 2 - 34); }
  let W = 0, L = 0;
  I.forEach((it, i) => {
    const col = i % per, row = Math.floor(i / per), x = cx - w / 2 + r + col * (2 * r + gap), y = cy - h / 2 + r + row * (2 * r + rg);
    const k = pr(ct, it.t || 0, it.mark === 'x' ? 0.28 : 0.2), mc = it.mark === 'x' ? '#ff4d5e' : '#2ecc71';
    ctx.lineWidth = 4; ctx.strokeStyle = k > 0 ? mc : 'rgba(255,255,255,0.22)'; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.stroke();
    if (k > 0) {
      if (it.mark === 'x') L++; else W++;
      const sc = lerp(it.mark === 'x' ? 2.2 : 1.6, 1, eOut(k));
      ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.globalAlpha *= Math.min(1, k * 2.5);
      ctx.fillStyle = rgba(mc, 0.25); ctx.beginPath(); ctx.arc(0, 0, r - 3, 0, 7); ctx.fill();
      ctx.strokeStyle = mc; ctx.lineWidth = r * 0.2; ctx.lineCap = 'round'; ctx.beginPath();
      if (it.mark === 'x') { const q = r * 0.38; ctx.moveTo(-q, -q); ctx.lineTo(q, q); ctx.moveTo(q, -q); ctx.lineTo(-q, q); }
      else { ctx.moveTo(-r * 0.4, 0); ctx.lineTo(-r * 0.1, r * 0.32); ctx.lineTo(r * 0.45, -r * 0.35); }
      ctx.stroke(); ctx.restore();
    }
    if (it.label) { font(700, 17, 'Mono', '1px'); ctx.fillStyle = k > 0 ? '#f4f2ec' : '#7d838e'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(String(it.label).toUpperCase(), x, y + r + 26); }
  });
  if (c.score) { font(800, 50, 'Inter', '-1px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#f4f2ec';
    ctx.fillText(c.score.replace('{w}', W).replace('{l}', L), cx, cy + h / 2 + 76); }
  ctx.restore();
};

// The referee's red card: an arm swings up from the bottom of the frame holding the card, which glows and shakes.
CARDS.redcard = function (c, ct, cx, cy) {
  const k = eBack(pr(ct, 0, 0.45)), sh = ct > 0.45 && ct < 0.8 ? Math.sin(ct * 70) * 8 * (1 - (ct - 0.45) / 0.35) : 0;
  if (k <= 0) return;
  ctx.save(); ctx.translate(cx + (c.dx || 180) + sh, cy + (1 - k) * 700); ctx.rotate(lerp(0.5, c.rot != null ? c.rot : 0.12, k));
  ctx.fillStyle = '#111318'; rrect(-36, 40, 72, 520, 30); ctx.fill();              // black referee sleeve
  ctx.fillStyle = '#e2b08c'; ctx.beginPath(); ctx.ellipse(0, 30, 46, 52, 0, 0, 7); ctx.fill();   // hand
  const g = ctx.createRadialGradient(0, -120, 10, 0, -120, 260); g.addColorStop(0, c.color ? 'rgba(255,220,40,0.45)' : 'rgba(255,40,60,0.45)'); g.addColorStop(1, 'rgba(255,40,60,0)');
  ctx.fillStyle = g; ctx.fillRect(-300, -420, 600, 600);
  ctx.fillStyle = c.color || '#e3132b'; rrect(-95, -270, 190, 270, 14); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.18)'; rrect(-95, -270, 60, 270, 14); ctx.fill();
  ctx.fillStyle = '#e2b08c'; ctx.beginPath(); ctx.ellipse(-60, -20, 26, 40, -0.3, 0, 7); ctx.fill();   // thumb over the card
  ctx.restore();
  if (c.label && ct > 0.5) { const a = pr(ct, 0.5, 0.3); ctx.save(); ctx.globalAlpha *= a; font(800, 44, 'Inter'); ctx.fillStyle = '#fff'; ctx.textAlign = 'center';
    ctx.strokeStyle = 'rgba(0,0,0,0.6)'; ctx.lineWidth = 8; const lx = cx + (c.dx || 180), ly = cy - 310; ctx.strokeText(c.label, lx, ly); ctx.fillText(c.label, lx, ly); ctx.restore(); }
};
CARDS.redcard.noSlide = true;

// Viral "shout" text (meme-thumbnail style): heavy slanted caps, yellow fill, thick black outline, white glow, tilted,
// popping in with an overshoot. "\n" splits lines; each line is auto-fitted to `w` (default 1000px) up to `size`.
// text, size (max px, default 190), color, stroke, rot (radians, default -0.07), skew (default -0.18), w, glow (colour or false)
CARDS.shout = function (c, ct, cx, cy) {
  const k = eBack(pr(ct, 0, 0.35)), a = pr(ct, 0, 0.12);
  if (k <= 0) return;
  const lines = String(c.text).split('\n'), maxW = c.w || 1000, gap = c.gap != null ? c.gap : 0.92;
  const sizes = lines.map(l => { font(900, 100, 'Inter', '-2px'); return Math.min(c.size || 190, 100 * maxW / Math.max(1, ctx.measureText(l).width)); });
  const total = sizes.reduce((m, z) => m + z * gap, 0);
  const sh = ct < 0.6 ? Math.sin(ct * 60) * 6 * (1 - ct / 0.6) : 0;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx + sh, cy); ctx.rotate(c.rot != null ? c.rot : -0.07);
  ctx.scale(0.4 + 0.6 * k, 0.4 + 0.6 * k); ctx.transform(1, 0, c.skew != null ? c.skew : -0.18, 1, 0, 0);
  ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.lineJoin = 'round';
  let y = -total / 2;
  lines.forEach((l, i) => {
    const z = sizes[i]; y += z * gap; font(900, z, 'Inter', '-2px');
    if (c.glow !== false) { ctx.save(); ctx.shadowColor = c.glow || 'rgba(255,255,255,0.75)'; ctx.shadowBlur = z * 0.35; ctx.strokeStyle = 'rgba(0,0,0,0)'; ctx.fillStyle = c.stroke || '#0a0a0a'; ctx.fillText(l, 0, y); ctx.restore(); }
    ctx.lineWidth = z * 0.2; ctx.strokeStyle = c.stroke || '#0a0a0a'; ctx.strokeText(l, 0, y);   // fat outline
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillText(l, z * 0.04, y + z * 0.06);                  // drop shadow inside the outline
    const g = ctx.createLinearGradient(0, y - z * 0.8, 0, y); g.addColorStop(0, c.color2 || '#fff36b'); g.addColorStop(1, c.color || '#ffc400');
    ctx.fillStyle = g; ctx.fillText(l, 0, y);
  });
  ctx.restore();
};
CARDS.shout.noSlide = true;

// Chalkboard tally: a wooden-framed blackboard; chalk tally marks (gates of five) draw themselves one by one.
// n marks, done already drawn, next one at newAt/newT; title and score in chalk handwriting.
function chalkLine(x1, y1, x2, y2, k, seed, w, col) {
  const R = rng(seed), xe = lerp(x1, x2, k), ye = lerp(y1, y2, k);
  ctx.save(); ctx.lineCap = 'round'; ctx.strokeStyle = col || 'rgba(245,245,238,0.92)'; ctx.lineWidth = w || 9;
  ctx.beginPath(); ctx.moveTo(x1, y1); const steps = 10;
  for (let i = 1; i <= steps; i++) { const u = i / steps; ctx.lineTo(lerp(x1, xe, u) + (R() - 0.5) * 3, lerp(y1, ye, u) + (R() - 0.5) * 3); }
  ctx.stroke();
  ctx.globalCompositeOperation = 'destination-out'; ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 2;   // chalk grain
  for (let i = 0; i < 6; i++) { const u = R(); ctx.beginPath(); ctx.moveTo(lerp(x1, xe, u) - 4, lerp(y1, ye, u) - 3); ctx.lineTo(lerp(x1, xe, u) + 3, lerp(y1, ye, u) + 2); ctx.stroke(); }
  ctx.restore();
}
CARDS.chalk = function (c, ct, cx, cy) {
  const bw = c.w || 900, bh = c.h || 560, n = c.n || 6, a = eOut(pr(ct, 0, 0.4));
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy); ctx.rotate(c.tilt != null ? c.tilt : -0.02);
  ctx.fillStyle = '#5b3a1e'; rrect(-bw / 2 - 22, -bh / 2 - 22, bw + 44, bh + 44, 12); ctx.fill();
  const g = ctx.createRadialGradient(0, 0, 50, 0, 0, bw * 0.7); g.addColorStop(0, '#2c3a33'); g.addColorStop(1, '#1b2420');
  ctx.fillStyle = g; ctx.fillRect(-bw / 2, -bh / 2, bw, bh);
  const R = rng(3); ctx.fillStyle = 'rgba(255,255,255,0.035)';   // old chalk smudges
  for (let i = 0; i < 14; i++) { ctx.beginPath(); ctx.ellipse((R() - 0.5) * bw, (R() - 0.5) * bh, 60 + R() * 120, 20 + R() * 40, R() * 3, 0, 7); ctx.fill(); }
  font(400, 54, 'Marker'); ctx.fillStyle = 'rgba(245,245,238,0.92)'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (c.title) ctx.fillText(c.title, 0, -bh / 2 + 70);
  // tally marks, gates of five
  const done = (c.done || 0) + (c.newT != null && ct >= c.newT ? 1 : 0), mh = 150, sp = 46, top = -40;
  const groups = Math.ceil(n / 5), gw = 4 * sp + 70, total = groups * gw + (groups - 1) * 60;
  for (let i = 0; i < n; i++) {
    const gi = Math.floor(i / 5), j = i % 5, gx = -total / 2 + gi * (gw + 60);
    const isNew = c.newT != null && i === (c.done || 0);
    const k = i < (c.done || 0) ? 1 : isNew ? pr(ct, c.newT, 0.35) : c.step ? pr(ct, (c.start || 0.4) + (i - (c.done || 0)) * c.step, 0.3) : 0;
    if (k <= 0) continue;
    if (j < 4) chalkLine(gx + j * sp, top, gx + j * sp + 6, top + mh, k, 11 + i);
    else chalkLine(gx - 22, top + mh * 0.8, gx + 3 * sp + 26, top + mh * 0.15, k, 11 + i);
    if (c.labels && c.labels[i] && k >= 1) { font(400, 22, 'Marker'); ctx.fillStyle = 'rgba(245,245,238,0.6)'; ctx.fillText(c.labels[i], j < 4 ? gx + j * sp + 3 : gx + 3 * sp + 40, top + mh + 34 + (j % 2) * 26); }
  }
  void done;
  if (c.score) { font(400, 64, 'Marker'); ctx.fillStyle = c.scoreColor || '#ff8a8a'; ctx.fillText(c.score, 0, bh / 2 - 60); }
  ctx.restore();
};
CARDS.chalk.noSlide = true;

// Matchday tickets (idea list): a fanned stack of paper tickets, one per game, each stamped as it's named.
// tickets: [{comp, teams, score, date}], stamp text (e.g. "LOST"), done/newAt like the tally.
CARDS.tickets = function (c, ct, cx, cy) {
  const T = c.tickets, n = T.length, tw = c.tw || 560, th = c.th || 210, a = eOut(pr(ct, 0, 0.4));
  const shown = (c.done || 0) + (c.newT != null && ct >= c.newT ? 1 : 0);
  ctx.save(); ctx.globalAlpha *= a;
  T.forEach((tk, i) => {
    const isNew = c.newT != null && i === (c.done || 0), k = i < (c.done || 0) ? 1 : isNew ? eOut(pr(ct, c.newT, 0.45)) : 0;
    if (k <= 0 && !c.showAll) return;
    const ang = (i - (n - 1) / 2) * 0.09, ox = (i - (n - 1) / 2) * 52 + (c.dx || 40), oy = Math.abs(i - (n - 1) / 2) * 12 + (1 - k) * 300;
    ctx.save(); ctx.translate(cx + ox, cy + oy); ctx.rotate(ang);
    ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 10;
    ctx.fillStyle = '#f3ead2'; rrect(-tw / 2, -th / 2, tw, th, 14); ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.fillStyle = tk.color || '#1f3b7a'; ctx.fillRect(-tw / 2, -th / 2, 26, th);
    ctx.strokeStyle = 'rgba(60,40,10,0.35)'; ctx.setLineDash([6, 8]); ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(tw / 2 - 120, -th / 2 + 10); ctx.lineTo(tw / 2 - 120, th / 2 - 10); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = '#2a2116'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    font(700, 20, 'Mono', '3px'); ctx.fillText(tk.comp.toUpperCase(), -tw / 2 + 50, -th / 2 + 44);
    font(800, 36, 'Inter', '-0.5px'); ctx.fillText(tk.teams, -tw / 2 + 50, -th / 2 + 96);
    font(800, 52, 'Inter', '-1px'); ctx.fillText(tk.score, -tw / 2 + 50, -th / 2 + 160);
    ctx.save(); ctx.translate(tw / 2 - 60, 0); ctx.rotate(-Math.PI / 2); font(700, 18, 'Mono', '3px'); ctx.textAlign = 'center'; ctx.fillText(tk.date.toUpperCase(), 0, 6); ctx.restore();
    if (c.stamp && k >= 1) {
      const sk = isNew ? pr(ct, c.newT + 0.45, 0.2) : 1;
      if (sk > 0) {
        ctx.save(); ctx.translate(40, 10); ctx.rotate(-0.18); ctx.scale(lerp(2, 1, eOut(sk)), lerp(2, 1, eOut(sk))); ctx.globalAlpha *= 0.88;
        font(900, 64, 'Inter', '4px'); const sw = ctx.measureText(c.stamp).width + 40;
        ctx.strokeStyle = '#d6283b'; ctx.lineWidth = 7; rrect(-sw / 2, -44, sw, 88, 10); ctx.stroke();
        ctx.fillStyle = '#d6283b'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.stamp, 0, 4);
        ctx.restore();
      }
    }
    ctx.restore();
  });
  if (c.count) { font(800, 44, 'Inter', '-1px'); ctx.fillStyle = '#f4f2ec'; ctx.textAlign = 'center'; ctx.fillText(c.count.replace('{n}', shown), cx, cy + th / 2 + 140); }
  ctx.restore();
};
CARDS.tickets.noSlide = true;

// Polaroid photo prop that spins in and can rip in half (virality: "something breaks" before 3s).
// scene: "bath" draws a young player (photo.player) leaning over a baby in a tub with bubbles; caption under the picture.
// ripT|ripAt: the photo tears down a jagged line, halves fly apart with a shake. Without ripT it simply stays.
function drawPhotoScene(c, w, h, t) {
  const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2); g.addColorStop(0, '#d9e8f2'); g.addColorStop(1, '#b8cfdf');
  ctx.fillStyle = g; ctx.fillRect(-w / 2, -h / 2, w, h);
  ctx.fillStyle = 'rgba(255,255,255,0.35)'; for (let i = 0; i < 6; i++) ctx.fillRect(-w / 2 + i * w / 6, -h / 2, 2, h * 0.55);   // tiled wall
  ctx.fillStyle = 'rgba(255,255,255,0.35)'; for (let j = 0; j < 4; j++) ctx.fillRect(-w / 2, -h / 2 + j * h * 0.14, w, 2);
  const pl = c.player || {};
  ctx.save(); ctx.beginPath(); ctx.rect(-w / 2, -h / 2, w, h); ctx.clip();
  drawPlayer(-w * 0.12, h * 0.62, h * 1.1, Object.assign({ front: true }, pl), t, 0, 1);
  // tub
  ctx.fillStyle = '#f4f7fa'; ctx.beginPath(); ctx.ellipse(w * 0.08, h * 0.3, w * 0.34, h * 0.12, 0, 0, Math.PI); ctx.fill();
  ctx.fillStyle = '#e3ebf2'; ctx.fillRect(-w * 0.26, h * 0.18, w * 0.68, h * 0.13);
  ctx.fillStyle = '#9fd0f0'; ctx.beginPath(); ctx.ellipse(w * 0.08, h * 0.18, w * 0.34, h * 0.05, 0, 0, 7); ctx.fill();
  // baby
  ctx.fillStyle = c.babySkin || '#8a5a3c'; ctx.beginPath(); ctx.arc(w * 0.12, h * 0.1, h * 0.075, 0, 7); ctx.fill();
  ctx.fillStyle = '#1a1210'; ctx.beginPath(); ctx.arc(w * 0.12, h * 0.07, h * 0.06, Math.PI * 1.05, Math.PI * 1.95); ctx.fill();
  // bubbles
  const R = rng(5);
  for (let i = 0; i < 18; i++) { const bx = w * (-0.2 + R() * 0.6), by = h * 0.16 - ((t * 30 * (0.5 + R()) + R() * 200) % (h * 0.5)), br = 4 + R() * 10;
    ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(bx, by, br, 0, 7); ctx.stroke(); }
  ctx.restore();
}
CARDS.photo = function (c, ct, cx, cy) {
  const W0 = c.w || 640, H0 = c.h || 720, pad = 34, bottom = 130, ih = H0 - pad - bottom, iw = W0 - pad * 2;
  const k = eOut(pr(ct, 0, c.spin || 0.9));
  const ripT = c.ripT, rk = ripT != null ? pr(ct, ripT, 0.6) : 0;
  if (rk >= 1 && c.vanish !== false) return;
  ctx.save();
  ctx.translate(cx, cy); ctx.rotate(lerp(-0.6, c.tilt != null ? c.tilt : -0.05, k)); ctx.scale(lerp(0.6, 1, k), lerp(0.6, 1, k));
  ctx.globalAlpha *= Math.min(1, k * 2) * (1 - rk * 0.9);
  const half = (side) => {
    ctx.save();
    // jagged tear line down the middle
    ctx.beginPath();
    const R = rng(9), pts = []; for (let y = -H0 / 2; y <= H0 / 2; y += 40) pts.push([(R() - 0.5) * 40, y]);
    if (side === 0) ctx.rect(-W0 / 2 - 50, -H0 / 2 - 50, W0 + 100, H0 + 100);   // whole photo, no tear seam
    else if (side < 0) { ctx.moveTo(-W0 / 2 - 2, -H0 / 2 - 2); pts.forEach(p => ctx.lineTo(...p)); ctx.lineTo(-W0 / 2 - 2, H0 / 2 + 2); }
    else { ctx.moveTo(W0 / 2 + 2, -H0 / 2 - 2); pts.forEach(p => ctx.lineTo(...p)); ctx.lineTo(W0 / 2 + 2, H0 / 2 + 2); }
    ctx.closePath(); ctx.clip();
    ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 18;
    ctx.fillStyle = '#f7f4ec'; ctx.fillRect(-W0 / 2, -H0 / 2, W0, H0); ctx.shadowColor = 'transparent';
    ctx.save(); ctx.translate(0, -H0 / 2 + pad + ih / 2); ctx.beginPath(); ctx.rect(-iw / 2, -ih / 2, iw, ih); ctx.clip();
    if (c.scene === 'bath') drawPhotoScene(c, iw, ih, ct);
    ctx.filter = 'none'; ctx.fillStyle = 'rgba(160,110,40,0.12)'; ctx.fillRect(-iw / 2, -ih / 2, iw, ih);   // old-photo warmth
    ctx.restore();
    if (c.caption) { font(400, 54, 'Marker'); ctx.fillStyle = '#2a2a33'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c.caption, 0, H0 / 2 - bottom / 2 + 4); }
    ctx.restore();
  };
  if (ripT == null || ct < ripT) half(0);
  else {
    const e = eOut(rk);
    ctx.save(); ctx.translate(-e * 420, e * 120); ctx.rotate(-e * 0.6); half(-1); ctx.restore();
    ctx.save(); ctx.translate(e * 420, e * 160); ctx.rotate(e * 0.7); half(1); ctx.restore();
  }
  ctx.restore();
};
CARDS.photo.noSlide = true;

// A handwritten letter that writes itself: paper sheet, a date in the corner and lines of handwriting appearing.
// Content is never put in the person's mouth: lines are illegible scribbles unless `lines` are given (only real quotes).
CARDS.letter = function (c, ct, cx, cy) {
  const w = c.w || 620, h = c.h || 780, a = eOut(pr(ct, 0, 0.6));
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy + (1 - a) * 60); ctx.rotate(c.tilt != null ? c.tilt : 0.04);
  ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 16;
  ctx.fillStyle = '#fbf8f0'; ctx.fillRect(-w / 2, -h / 2, w, h); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = 'rgba(80,120,190,0.25)'; ctx.lineWidth = 2;
  for (let y = -h / 2 + 140; y < h / 2 - 40; y += 46) { ctx.beginPath(); ctx.moveTo(-w / 2 + 30, y); ctx.lineTo(w / 2 - 30, y); ctx.stroke(); }
  font(400, 34, 'Marker'); ctx.fillStyle = '#1e2a55'; ctx.textAlign = 'right'; ctx.textBaseline = 'alphabetic';
  if (c.date) ctx.fillText(c.date, w / 2 - 40, -h / 2 + 90);
  const R = rng(17), rows = Math.floor((h - 200) / 46), wk = pr(ct, 0.5, c.write || 2.5);
  ctx.strokeStyle = '#1e2a55'; ctx.lineWidth = 3.2; ctx.lineCap = 'round';
  for (let r = 0; r < rows; r++) {
    const y = -h / 2 + 132 + r * 46, len = (w - 120) * (r === rows - 1 ? 0.4 : 0.75 + R() * 0.25), rowK = clamp(wk * rows - r, 0, 1);
    if (rowK <= 0) break;
    ctx.beginPath(); let x = -w / 2 + 50; ctx.moveTo(x, y);
    const end = x + len * rowK;
    while (x < end) { const s = 8 + R() * 10; ctx.quadraticCurveTo(x + s / 2, y - 10 - R() * 8, x + s, y - R() * 3); x += s; if (R() < 0.12) { x += 14; ctx.moveTo(x, y); } }
    ctx.stroke();
  }
  ctx.restore();
};
CARDS.letter.noSlide = true;

// Wall-calendar time-lapse: big year pages tear off and fly away, from `from` to `to` over `dur` seconds (accelerating),
// then the last page lands with a slam. `caption` under the final year. Good for "N years later" jumps.
CARDS.calendar = function (c, ct, cx, cy) {
  const a = eOut(pr(ct, 0, 0.3)), w = c.w || 560, h = c.h || 640, from = c.from, to = c.to, n = to - from;
  const k = pr(ct, c.start || 0.5, c.dur || 2.2), f = Math.pow(k, 1.6) * n, cur = Math.min(to, from + Math.floor(f));
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy);
  const page = (yr, x, y, rot, al) => {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.globalAlpha *= al;
    ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12;
    ctx.fillStyle = '#f7f4ec'; ctx.fillRect(-w / 2, -h / 2, w, h); ctx.shadowColor = 'transparent';
    ctx.fillStyle = c.color || '#d6283b'; ctx.fillRect(-w / 2, -h / 2, w, 120);
    font(800, 36, 'Mono', '8px'); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText((c.title || 'YEAR').toUpperCase(), 0, -h / 2 + 62);
    font(900, 230, 'Inter', '-8px'); ctx.fillStyle = '#16181d'; ctx.fillText(String(yr), 0, 40);
    ctx.fillStyle = 'rgba(22,24,29,0.12)'; for (let i = 0; i < 4; i++) ctx.fillRect(-w / 2 + 50, h / 2 - 150 + i * 30, w - 100, 10);
    ctx.restore();
  };
  // rings on top
  page(cur + (cur < to ? 1 : 0), 0, 0, 0, 1);   // the next page underneath
  if (cur < to) {
    const sub = f - Math.floor(f);   // the current page tearing away
    page(cur, sub * 700, -sub * 500, sub * 0.9, 1 - sub);
  } else {
    const lk = pr(ct, (c.start || 0.5) + (c.dur || 2.2), 0.3);
    if (c.caption && lk > 0) { font(800, 42, 'Inter'); ctx.fillStyle = c.captionColor || '#f1c453'; ctx.textAlign = 'center'; ctx.globalAlpha *= lk; ctx.fillText(c.caption, 0, h / 2 + 70); }
  }
  ctx.fillStyle = '#9aa1ad'; for (const x of [-w / 3, 0, w / 3]) { ctx.beginPath(); ctx.arc(x, -h / 2 + 8, 12, 0, 7); ctx.fill(); }
  ctx.restore();
};
CARDS.calendar.noSlide = true;

// Match clock (idea list): a broadcast-style clock that races from `from` to `to` minutes over `dur` seconds,
// with an optional phase label ("EXTRA TIME") and score; `events: [{min, text}]` pop in as the clock passes them.
CARDS.clock = function (c, ct, cx, cy) {
  const a = eOut(pr(ct, 0, 0.35)), k = ease(pr(ct, 0.3, c.dur || 2.2));
  const m = lerp(c.from ?? 90, c.to ?? 120, k), mm = Math.floor(m), ss = Math.floor((m - mm) * 60);   // ?? so a clock can start at 0'
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy); ctx.scale(c.scale || 1, c.scale || 1);
  const w = 640, h = 150;
  ctx.fillStyle = '#0d1016'; rrect(-w / 2, -h / 2, w, h, 20); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.12)'; ctx.lineWidth = 3; rrect(-w / 2, -h / 2, w, h, 20); ctx.stroke();
  font(800, 96, 'Mono', '2px'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = k < 1 ? '#f4f2ec' : (c.endColor || '#f1c453');
  ctx.fillText(String(mm).padStart(2, '0') + ':' + String(ss).padStart(2, '0'), 0, 6);
  if (c.phase) {
    const pk = pr(ct, 0.3 + (c.dur || 2.2) * (c.phaseAt || 0.0), 0.3);
    if (pk > 0) { ctx.globalAlpha *= pk; font(800, 26, 'Mono', '5px'); const tw = ctx.measureText(c.phase).width + 40;
      ctx.fillStyle = '#d6283b'; rrect(-tw / 2, h / 2 + 18, tw, 48, 24); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillText(c.phase, 0, h / 2 + 43); }
  }
  ctx.restore();
  (c.events || []).forEach((e, i) => {
    const ek = pr(m, e.min - 0.6, 0.6);   // pops as the clock reaches it (also when the clock stops exactly on that minute)
    if (ek <= 0) return;
    ctx.save(); ctx.globalAlpha *= Math.min(1, ek * 2) * a;
    const y = cy - 75 * (c.scale || 1) - 60 - i * 70; font(700, 30, 'Inter'); const tw = ctx.measureText(e.text).width + 50;
    ctx.translate(cx, y); ctx.scale(0.8 + 0.2 * eBack(Math.min(1, ek)), 0.8 + 0.2 * eBack(Math.min(1, ek)));
    ctx.fillStyle = 'rgba(244,242,236,0.95)'; rrect(-tw / 2, -28, tw, 56, 28); ctx.fill();
    ctx.fillStyle = '#16181d'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(e.text, 0, 2);
    ctx.restore();
  });
};
CARDS.clock.noSlide = true;

// VHS rewind (idea list): scanlines, tracking noise, colour split and a "◀◀ label" for the first `dur` seconds of a beat.
function vhsRewind(lt, label, dur) {
  const k = 1 - pr(lt, dur * 0.6, dur * 0.4);
  if (k <= 0) return;
  const fx = fullc.getContext('2d');
  fx.clearRect(0, 0, W, H); fx.drawImage(cv, 0, 0);
  ctx.save();
  // horizontal tearing: bands of the frame shifted sideways
  const R = rng(Math.floor(lt * 30) + 7);
  for (let i = 0; i < 16; i++) {
    const y = R() * H, h = 12 + R() * 70, dx = (R() - 0.5) * 220 * k;
    ctx.drawImage(fullc, 0, y, W, h, dx, y, W, h);
  }
  // colour split
  ctx.globalAlpha = 0.35 * k; ctx.globalCompositeOperation = 'lighter';
  ctx.filter = 'sepia(1) hue-rotate(-50deg) saturate(4)'; ctx.drawImage(fullc, 8 * k, 0);
  ctx.filter = 'sepia(1) hue-rotate(150deg) saturate(4)'; ctx.drawImage(fullc, -8 * k, 0);
  ctx.filter = 'none'; ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  // scanlines + tracking noise bar
  ctx.fillStyle = `rgba(0,0,0,${0.22 * k})`; for (let y = 0; y < H; y += 6) ctx.fillRect(0, y, W, 2);
  const by = (lt * 900) % (H + 200) - 100; ctx.fillStyle = `rgba(255,255,255,${0.12 * k})`; ctx.fillRect(0, by, W, 60);
  for (let i = 0; i < 300; i++) { ctx.fillStyle = `rgba(255,255,255,${R() * 0.3 * k})`; ctx.fillRect(R() * W, by + R() * 60, 3, 2); }
  // on-screen display
  ctx.globalAlpha = k; font(800, 110, 'Mono', '6px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = '#ffffff'; ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 8;
  if (Math.floor(lt * 4) % 2 === 0) ctx.fillText('◀◀ ' + (label || 'REWIND'), W / 2 + (R() - 0.5) * 16, H * 0.62);
  ctx.restore();
}

// Golden balance scales: two names weighed against each other; the beam tips toward the heavier side.
// left/right: {name, value, color}, tilt (radians, exaggerate small gaps), question
CARDS.scales = function (c, ct, cx, cy) {
  const a = eOut(pr(ct, 0, 0.5)), settle = pr(ct, 0.4, 1.6);
  const dir = c.left.value >= c.right.value ? -1 : 1;   // the heavier pan drops
  const tilt = dir * (c.tilt != null ? c.tilt : 0.12) * (1 - Math.exp(-settle * 5) * Math.cos(settle * 14));
  const arm = c.arm || 330, gold = goldGrad(cx - arm, cx + arm);
  ctx.save(); ctx.globalAlpha *= a;
  // pillar and base
  ctx.fillStyle = gold; ctx.fillRect(cx - 10, cy, 20, 380); rrect(cx - 120, cy + 370, 240, 30, 12); ctx.fill();
  ctx.beginPath(); ctx.arc(cx, cy, 22, 0, 7); ctx.fill();
  // beam
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(tilt);
  ctx.fillStyle = gold; rrect(-arm, -9, arm * 2, 18, 9); ctx.fill();
  ctx.restore();
  for (const side of [-1, 1]) {
    const o = side < 0 ? c.left : c.right;
    const px = cx + side * arm * Math.cos(tilt), py = cy + side * arm * Math.sin(tilt), drop = 230;
    ctx.strokeStyle = '#d9b45a'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px - 110, py + drop); ctx.moveTo(px, py); ctx.lineTo(px + 110, py + drop); ctx.stroke();
    ctx.fillStyle = gold; ctx.beginPath(); ctx.ellipse(px, py + drop, 130, 26, 0, 0, Math.PI); ctx.fill();
    ctx.fillRect(px - 130, py + drop - 6, 260, 8);
    // the player's name plate sitting in the pan
    ctx.fillStyle = o.color || '#dc052d'; rrect(px - 100, py + drop - 92, 200, 82, 14); ctx.fill();
    font(800, 34, 'Inter'); ctx.fillStyle = o.text || '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(o.name.toUpperCase(), px, py + drop - 64);
    font(700, 26, 'Mono', '2px'); ctx.fillText(Math.round(o.value * eOut(pr(ct, 0.3, 1.2))).toLocaleString('en-GB') + ' PTS', px, py + drop - 30);
  }
  ctx.restore();
};
CARDS.scales.noSlide = true;

// Poll sticker, Instagram style: question + two options with "?" percentages and a tapping finger.
CARDS.poll = function (c, ct, cx, cy) {
  const a = eBack(pr(ct, 0, 0.45)), w = c.w || 760, opts = c.options, h = 150 + opts.length * 120;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(a, a); ctx.rotate(c.rot != null ? c.rot : -0.03);
  ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
  ctx.fillStyle = '#ffffff'; rrect(-w / 2, -h / 2, w, h, 36); ctx.fill(); ctx.shadowColor = 'transparent';
  font(800, 44, 'Inter', '-1px'); ctx.fillStyle = '#16181d'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(c.question, 0, -h / 2 + 76);
  opts.forEach((o, i) => {
    const y = -h / 2 + 170 + i * 120, fill = eOut(pr(ct, 0.6 + i * 0.25, 0.8)) * (o.fill || 0.5);
    ctx.fillStyle = '#eef0f3'; rrect(-w / 2 + 40, y - 46, w - 80, 92, 46); ctx.fill();
    ctx.save(); rrect(-w / 2 + 40, y - 46, w - 80, 92, 46); ctx.clip();
    ctx.fillStyle = o.color || '#dc052d'; ctx.globalAlpha *= 0.9; ctx.fillRect(-w / 2 + 40, y - 46, (w - 80) * fill, 92); ctx.restore();
    font(800, 38, 'Inter'); ctx.fillStyle = '#16181d'; ctx.textAlign = 'left'; ctx.fillText(o.label.toUpperCase(), -w / 2 + 80, y + 2);
    ctx.textAlign = 'right'; ctx.fillText(o.pct || '?%', w / 2 - 80, y + 2);
  });
  // tapping finger (simple hand: circle + finger) bobbing over option 1
  const tap = Math.abs(Math.sin(ct * 4)), fx = -w / 2 + 40 + (w - 80) * 0.7, fy = -h / 2 + 170 + 30 + tap * 14;
  ctx.fillStyle = '#f2c9a5'; ctx.strokeStyle = '#16181d'; ctx.lineWidth = 4;
  rrect(fx - 16, fy, 32, 70, 16); ctx.fill(); ctx.stroke();
  rrect(fx - 34, fy + 50, 80, 70, 26); ctx.fill(); ctx.stroke();
  ctx.restore();
};
CARDS.poll.noSlide = true;

// Comment bubbles floating up like a live chat (sample viewer opinions; illustrative, not real comments).
CARDS.comments = function (c, ct, cx, cy) {
  const items = c.items, R = rng(c.seed || 3);
  items.forEach((it, i) => {
    const t0 = (it.t != null ? it.t : 0.2 + i * (c.step || 0.45)), k = ct - t0;
    if (k < 0) return;
    const rise = Math.min(1, k / 0.5), x = cx + (it.x != null ? it.x : (R() - 0.5) * 520), y = (it.y != null ? it.y : cy + 300 - i * 120) - eOut(rise) * 60 - k * 18;
    ctx.save(); ctx.globalAlpha *= Math.min(1, k * 3); ctx.translate(x, y); ctx.scale(0.8 + 0.2 * eBack(rise), 0.8 + 0.2 * eBack(rise));
    font(700, 34, 'Inter'); const tw = ctx.measureText(it.text).width + 110;
    ctx.fillStyle = 'rgba(255,255,255,0.96)'; rrect(-tw / 2, -40, tw, 80, 40); ctx.fill();
    ctx.beginPath(); ctx.moveTo(-tw / 2 + 40, 36); ctx.lineTo(-tw / 2 + 30, 60); ctx.lineTo(-tw / 2 + 64, 38); ctx.fill();
    ctx.fillStyle = it.color || '#dc052d'; ctx.beginPath(); ctx.arc(-tw / 2 + 42, 0, 22, 0, 7); ctx.fill();
    ctx.fillStyle = '#16181d'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(it.text, -tw / 2 + 78, 2);
    ctx.restore();
  });
};
CARDS.comments.noSlide = true;

// Radial speed lines (hero intro, big moments). Beat key: "speedlines": [{t|at, dur}]
function drawSpeedlines(b, lt) {
  for (const sl of b.speedlines || []) {
    const r = lt - (sl.t || 0), d = sl.dur || 1.2;
    if (r < 0 || r > d) continue;
    const a = (1 - r / d) * (sl.amount || 1), R = rng(31), cx = W / 2, cy = sl.y || H * 0.6;
    ctx.save(); ctx.lineCap = 'round';
    for (let i = 0; i < 70; i++) {
      const an = R() * 6.28, ph = R(), sp = 0.6 + R();
      const u = ((ph + r * sp * 1.6) % 1), r0 = 380 + u * 900, len = 120 + R() * 260;
      ctx.strokeStyle = `rgba(255,255,255,${0.35 * a * (1 - u)})`; ctx.lineWidth = 2 + R() * 3;
      ctx.beginPath(); ctx.moveTo(cx + Math.cos(an) * r0, cy + Math.sin(an) * r0); ctx.lineTo(cx + Math.cos(an) * (r0 + len), cy + Math.sin(an) * (r0 + len)); ctx.stroke();
    }
    ctx.restore();
  }
}
CARDS.ballnumber.selfExit = true;
CARDS.trophies.noSlide = true;
CARDS.meter.noSlide = true;

// Sound cue times each card produces, relative to the card's start time.
function cardEvents(c) {
  const ev = [];
  const ticks = (a, d) => { for (let t = a; t < a + d; t += 0.075) ev.push({ t, type: 'tick' }); };
  switch (c.type) {
    case 'flip': c.groups.forEach((g, i) => ticks(0.35 + i * 0.25, 1.3)); break;
    case 'big': ticks(0.25, (c.countDur || 1.3) * 0.85); ev.push({ t: 0.25 + (c.countDur || 1.3), type: 'impact' }); break;
    case 'vs': c.items.forEach((g, i) => ticks(0.35 + i * 0.3, 1.0)); break;
    case 'table': ticks(0.5, 1.1); if (c.moveT != null) ev.push({ t: c.moveT, type: 'swipe' }); if (c.pill) ev.push({ t: c.moveT != null ? c.moveT + 1.0 : 1.9, type: 'pop' }); break;
    case 'tally': if (c.items) c.items.forEach(it => ev.push({ t: it.t || 0, type: it.mark === 'x' ? 'impact' : 'pop' })); else if (c.newT != null) ev.push({ t: c.newT, type: 'impact' }); break;
    case 'bars': c.rows.forEach((r, i) => ticks(0.4 + i * 0.35, 1.1)); break;
    case 'orb': ticks(0.3, 1.6); ev.push({ t: 2.1, type: 'impact' }); break;
    case 'ballnumber': ev.push({ t: 1.0, type: 'impact' }); if (c.count != null) ticks(0.3, 1.5); break;
    case 'board': {
      const n = c.rows.length, end = 0.15 + n * 0.07 + 13 * 0.025 + 0.4;
      if (!c._prev || c.rows.some((r, i) => !c._prev.rows[i] || c._prev.rows[i].name !== r.name || c._prev.rows[i].value !== r.value)) {
        for (let t = 0.15; t < end; t += 0.035) ev.push({ t, type: 'tick' });
      }
      if (c.rows.some(r => r.from != null || r.strike)) {
        ev.push({ t: (c.swapAt || 1.5) - 0.6, type: 'swish' });
        for (let t = c.swapAt || 1.5; t < (c.swapAt || 1.5) + 0.5; t += 0.035) ev.push({ t, type: 'tick' });
      }
      if (c.rows.some(r => r.delta)) ev.push({ t: (c.swapAt || 1.5) + 0.35, type: 'pop' });
      if (c.caption) ev.push({ t: c.captionAt != null ? c.captionAt : 2.0, type: 'pop' });
      (c.focusPath || []).slice(1).forEach(p => ev.push({ t: p.t, type: 'swipe' }));
      break;
    }
    case 'newspaper': ev.push({ t: 0, type: 'whoosh' }, { t: c.spin || 1.4, type: 'impact' }); break;
    case 'ballpath': ev.push({ t: 0, type: 'swish' }); if (c.flash !== false) ev.push({ t: c.dur || 1.6, type: 'crowd' }); else ev.push({ t: c.dur || 1.6, type: 'pop' }); break;
    case 'receipt': { const n = (c.lines || []).length + (c.total ? 1 : 0) + 1; for (let i = 0; i < n; i++) for (let t = 0.2 + i * (c.step || 0.45); t < 0.2 + i * (c.step || 0.45) + 0.25; t += 0.03) ev.push({ t, type: 'tick' }); break; }
    case 'stamp': ev.push({ t: 0.16, type: 'impact' }); break;
    case 'lineup': ev.push({ t: 0, type: 'whoosh' }); if (!c.instant) (c.items || []).forEach((it, i) => ev.push({ t: it.t != null ? it.t : 0.25 + i * 0.07, type: it.t != null ? 'pop' : 'tick' })); if (c.empty) ev.push({ t: c.empty.t != null ? c.empty.t : 1.2, type: 'impact' }); break;
    case 'ballot': { ev.push({ t: 0, type: 'pop' }); const n = c.n || 16, d = c.dur || 2.2; for (let i = 0; i < n; i += 2) ev.push({ t: 0.9 + i / n * d, type: 'tick' }); break; }
    case 'photofinish': { const d = c.dur || 1.8; ev.push({ t: 0.3, type: 'whoosh' }); for (let t = 0.4; t < 0.35 + d; t += 0.08) ev.push({ t, type: 'tick' }); ev.push({ t: 0.35 + d, type: 'impact' }); if (c.gap) ev.push({ t: c.gapT != null ? c.gapT : 0.6 + d, type: 'pop' }); break; }
    case 'crossoff': { ev.push({ t: 0, type: 'whoosh' }); const t0 = c.crossT != null ? c.crossT : 0.5, d = c.dur || 1.6; for (let t = t0; t < t0 + d; t += 0.07) ev.push({ t, type: 'tick' }); ev.push({ t: t0 + d, type: 'impact' }); break; }
    case 'phone': ev.push({ t: 0, type: 'whoosh' }, { t: 0.5, type: 'pop' }); break;
    case 'varlines': ev.push({ t: 0, type: 'whoosh' }, { t: (c.dur || 0.7) + 0.1, type: 'whoosh' }, { t: c.gapAt != null ? c.gapAt : (c.dur || 0.7) * 2 + 0.2, type: 'tick' }); break;
    case 'redcard': ev.push({ t: 0.1, type: 'whoosh' }, { t: 0.45, type: 'impact' }); break;
    case 'passweb': { const pd = c.pass || 0.34, end = c.stopAt != null ? c.stopAt : (c.passFor || 6); for (let t = pd; t < end; t += pd) ev.push({ t, type: 'pop' });
      if (c.counter !== false) { ticks(0.1, (c.dur || 4) * 0.9); ev.push({ t: c.dur || 4, type: 'impact' }); } break; }
    case 'shout': ev.push({ t: 0, type: 'whoosh' }, { t: 0.3, type: 'impact' }); break;
    case 'toyresults': (c.items || []).forEach((it, i) => { const t0 = it.t != null ? it.t : i * 0.5; ev.push({ t: t0, type: 'whoosh' }, { t: t0 + 0.32, type: it.win ? 'pop' : 'impact' }); }); break;
    case 'toydoors': (c.doors || []).forEach(d => { ev.push({ t: d.t || 0, type: 'pop' }); if (d.shut != null) ev.push({ t: d.shut, type: 'impact' }); }); break;
    case 'toyquote': ev.push({ t: 0, type: 'whoosh' }, { t: 0.3, type: 'pop' }); break;
    case 'claynum': ev.push({ t: 0, type: 'whoosh' }, { t: 0.31, type: 'impact' }); break;
    case 'whiteboard': ev.push({ t: 0, type: 'whoosh' }); (c.lines || []).forEach(L => { const n = L.text.length, sp = L.speed || 0.045; for (let t = (L.t || 0); t < (L.t || 0) + n * sp; t += 0.09) ev.push({ t, type: 'tick' }); if (L.circle) ev.push({ t: L.circle.t != null ? L.circle.t : (L.t || 0) + n * sp + 0.2, type: 'swish' }); }); break;
    case 'toytable': ev.push({ t: 0, type: 'whoosh' }, { t: c.teamAt != null ? c.teamAt + 0.3 : 0.6, type: 'pop' }); (c.zones || []).forEach(z => ev.push({ t: z.t || 0, type: 'pop' })); (c.moves || []).forEach(m => ev.push({ t: m.t || 0, type: 'swipe' }, { t: (m.t || 0) + 0.6, type: 'impact' })); break;
    case 'xg': c.items.forEach(it => { ticks((it.t || 0) + 0.05, (c.dur || 1.4) * 0.9); ev.push({ t: (it.t || 0) + (c.dur || 1.4), type: 'pop' }); }); break;
    case 'swing': c.rows.forEach((r, i) => { const t0 = r.t != null ? r.t : 0.2 + i * 0.6; ev.push({ t: t0, type: 'swipe' }); ticks(t0 + 0.35, 0.9); ev.push({ t: t0 + 1.35, type: 'pop' }); }); break;
    case 'pcard': ev.push({ t: 0, type: 'whoosh' }, { t: 0.45, type: 'pop' }); break;
    case 'photo': ev.push({ t: 0, type: 'whoosh' }); if (c.ripT != null) ev.push({ t: c.ripT, type: 'impact' }, { t: c.ripT, type: 'swish' }); break;
    case 'calendar': { const n = c.to - c.from; for (let i = 1; i <= n; i++) ev.push({ t: (c.start || 0.5) + Math.pow(i / n, 1 / 1.6) * (c.dur || 2.2), type: 'swipe' }); ev.push({ t: (c.start || 0.5) + (c.dur || 2.2), type: 'impact' }); break; }
    case 'letter': for (let t = 0.5; t < 0.5 + (c.write || 2.5); t += 0.12) ev.push({ t, type: 'tick' }); break;
    case 'chalk': if (c.newT != null) ev.push({ t: c.newT, type: 'swipe' }); if (c.step) for (let i = c.done || 0; i < c.n; i++) ev.push({ t: (c.start || 0.4) + (i - (c.done || 0)) * c.step, type: 'swipe' }); break;
    case 'clock': for (let t = 0.3; t < 0.3 + (c.dur || 2.2); t += 0.075) ev.push({ t, type: 'tick' }); ev.push({ t: 0.3 + (c.dur || 2.2), type: 'impact' }); break;
    case 'tickets': if (c.newT != null) ev.push({ t: c.newT, type: 'swish' }, { t: c.newT + 0.5, type: 'impact' }); break;
    case 'scales': ev.push({ t: 0.3, type: 'swish' }, { t: 0.9, type: 'impact' }); for (let t = 0.3; t < 1.5; t += 0.075) ev.push({ t, type: 'tick' }); break;
    case 'poll': ev.push({ t: 0, type: 'pop' }, { t: 0.6, type: 'swipe' }); break;
    case 'comments': c.items.forEach((it, i) => ev.push({ t: it.t != null ? it.t : 0.2 + i * (c.step || 0.45), type: 'pop' })); break;
    case 'shelf': if (!c.instant) c.items.forEach((it, i) => ev.push({ t: (it.t != null ? it.t : 0.3 + i * 0.4) + 0.4, type: 'impact' })); if (c.emptyT != null) ev.push({ t: c.emptyT, type: 'pop' }); break;
    case 'tape': c.rows.forEach((r, i) => { const t0 = r.t != null ? r.t : 0.3 + i * 0.5; ev.push({ t: t0, type: 'swish' }); for (let t = t0 + 0.2; t < t0 + 0.9; t += 0.075) ev.push({ t, type: 'tick' }); }); if ((c.captionT ?? c.captionAt) != null) ev.push({ t: c.captionT ?? c.captionAt, type: 'pop' }); break;
    case 'tactic': (c.moves || []).forEach(m => { ev.push({ t: m.t || 0, type: m.kind === 'shot' ? 'whoosh' : 'swipe' }); if (m.kind === 'shot') ev.push({ t: (m.t || 0) + (m.dur || 0.7), type: 'impact' }); }); break;
    case 'stack': c.items.forEach(it => { ev.push({ t: it.t || 0, type: 'pop' }); for (let t = (it.t || 0); t < (it.t || 0) + 0.6; t += 0.075) ev.push({ t, type: 'tick' }); }); break;
    case 'shotmap': c.shots.forEach((sh, i) => ev.push({ t: sh.t != null ? sh.t : (c.step || 0.12) * i, type: 'pop' })); if (c.blockedT != null) ev.push({ t: c.blockedT, type: 'swish' }); break;
    case 'vehicle': ev.push({ t: 0, type: 'whoosh' }, { t: (c.dur || 1.6) - 0.1, type: 'impact' }); break;
    case 'flytext': ev.push({ t: 0, type: 'whoosh' }); if (c.mode !== 'through' && c.settle !== false) ev.push({ t: c.dur || 0.7, type: 'impact' }); break;
    case 'rain': {
      for (const g of c.groups) for (let j = 0; j < g.n; j += Math.max(1, Math.ceil(g.n / 30))) ev.push({ t: (g.t || 0) + (g.n > 1 ? j / (g.n - 1) : 0) * (g.dur || 1.6) + 0.45, type: 'tick' });
      if (c.emptyT != null) ev.push({ t: c.emptyT, type: 'pop' });
      break;
    }
    case 'pen': c.strokes.forEach(s => ev.push({ t: s.t || 0, type: 'swipe' })); break;
    case 'balls': for (let i = 0; i < c.n; i++) ev.push({ t: 0.3 + i * (c.step || 0.12), type: 'pop' }); break;
    case 'ruler': (c.markers || []).forEach((m, i) => ev.push({ t: 0.8 + i * 0.5, type: 'pop' })); if (c.bracket) ev.push({ t: 0.8 + (c.markers || []).length * 0.5, type: 'swipe' }); break;
    case 'trophies': c.items.forEach((it, i) => ev.push({ t: 0.2 + (c.rise || 0.9) + i * (c.stagger != null ? c.stagger : 0.5), type: 'impact' })); break;
    case 'meter': ticks(0.4, (c.countDur || 2.2) * 0.85); ev.push({ t: 0.4 + (c.countDur || 2.2), type: 'impact' }); break;
    case 'dots': {
      const n = c.states ? c.states.length : c.n;
      for (let i = 0; i < n; i++) ev.push({ t: 0.4 + i * (c.step || 0.17), type: 'pop' });
      break;
    }
  }
  ev.unshift({ t: 0.05, type: 'swipe' });
  return ev;
}

// ---------- timeline ----------
function wordsOf(s) { return String(s || '').trim().split(/\s+/).filter(Boolean).length; }
window.loadSpec = async function (spec) {
  S.spec = spec;
  S.accent = spec.accent || S.accent;
  await Promise.all([document.fonts.load('700 80px Inter'), document.fonts.load('800 80px Inter'),
    document.fonts.load('500 24px Mono'), document.fonts.load('700 24px Mono'), document.fonts.load('40px Marker')]);
  let t = 0, prev = null;
  S.beats = spec.beats.map((b, i) => {
    const B = { ...b };
    B.dur = b.duration || Math.max(2.4, wordsOf(b.vo) / 2.7 + 0.7);
    if (i === spec.beats.length - 1) B.dur += spec.tail != null ? spec.tail : 0.8;
    B.start = t; t += B.dur;
    B.sceneObj = b.scene || (prev ? prev.sceneObj : { type: 'stadium' });
    B.world = B.sceneObj.type === 'stadium' || B.sceneObj.type === 'booth' ? buildWorld(B.sceneObj) : null;
    if (B.sceneObj.type === 'stage') buildStage(B.sceneObj);
    if (b.split) B.splitWorld = buildWorld(b.split.scene);
    if (b.players === undefined && prev) { B.playersArr = prev.playersArr; B.playersStart = prev.playersStart; }
    else { B.playersArr = b.players || []; B.playersStart = B.start - (b.timeShift || 0); }   // timeShift: start the action part-way through (replays)
    B.kickerText = b.kicker !== undefined ? b.kicker : (prev ? prev.kickerText : '');
    B.cards = [];
    for (const c of b.card == null ? [] : Array.isArray(b.card) ? b.card : [b.card]) {
      if (c === 'same') { if (prev) B.cards.push(...prev.cards); }
      else {
        const pb = prev && c.id && prev.cards.find(x => x.obj.id === c.id);
        // same id, not a board: it simply stays on screen as it was (boards flip their changed cells instead)
        if (pb && c.type !== 'board') { B.cards.push(pb); continue; }
        if (pb) c._prev = pb.obj;
        // beat 1 is the hook: its cards are already in on frame 1 (the frame people see while scrolling)
        const delay = (c.delay != null ? c.delay : (i === 0 ? -0.45 : 0.3)) - (c.noShift ? 0 : (b.timeShift || 0));
        B.cards.push({ obj: c, start: pb ? B.start : B.start + delay });
      }
    }
    if (b.confetti) { B.confettiStart = prev && prev.confetti ? prev.confettiStart : B.start + (b.confettiDelay || 0); }
    prev = B;
    return B;
  });
  // short, subtle end screen after the last beat
  // the hook always opens with a burst of speed lines on frame 0 (unless the beat sets its own)
  if (S.beats[0] && !S.beats[0].speedlines && spec.hookZoom !== false) S.beats[0].speedlines = [{ t: 0, dur: 0.8, amount: 0.5 }];
  S.outro = spec.outro === false ? null : { start: t, dur: spec.outroDur || 1.8 };
  if (S.outro) t += S.outro.dur;
  S.dur = t;
  S.events = [];
  if (S.outro) S.events.push({ t: S.outro.start, type: 'swipe' }, { t: S.outro.start + 0.45, type: 'pop' });
  S.beats.forEach((b, i) => {
    if (i > 0 && (b.cut || b.headline !== S.beats[i - 1].headline)) S.events.push({ t: Math.max(0, b.start - 0.12), type: b.cut ? 'whoosh' : 'swish' });
    for (const it of b.cards) {
      if (i > 0 && S.beats[i - 1].cards.includes(it)) continue;
      for (const e of cardEvents(it.obj)) S.events.push({ t: it.start + e.t, type: e.type });
    }
    if (b.confetti && !(i > 0 && S.beats[i - 1].confetti)) S.events.push({ t: b.confettiStart, type: 'crowd' });
  });
  // real saves: time each keeper's dive so the ball meets his gloves at full stretch, then he lands holding it
  S.beats.forEach(b => {
    for (const it of b.cards) {
      const c = it.obj, kp = c.type === 'ballpath' && c.saveBy != null && b.playersArr && b.playersArr[c.saveBy];
      if (!kp || kp._autoDive === it) continue;
      const dur = kp.actionDur || (ACTIONS[kp.action] || { dur: 0.95 }).dur;
      kp.actionDelay = +(it.start + (c.dur || 1.6) - b.playersStart - 0.7 * dur).toFixed(3); kp._autoDive = it;
    }
  });
  S.goals = [];
  S.beats.forEach((b, i) => {
    for (const it of b.cards) {
      const c = it.obj;
      if (c.type === 'ballpath' && c.world && c.flash !== false && !(i > 0 && S.beats[i - 1].cards.includes(it))) {
        S.goals.push({ t: it.start + (c.dur || 1.6), p: c.points[2] });
        S.events.push({ t: it.start + (c.dur || 1.6) + 0.05, type: 'impact' });
      }
    }
    for (const p of b.punch || []) S.events.push({ t: b.start + p.t, type: 'whoosh' });
    if (b.freeze != null) S.events.push({ t: b.start + b.freeze, type: 'impact' });
    for (const p of b.playersArr || []) if (p.action === 'kick' && p.actionDelay != null && b.playersStart === b.start) S.events.push({ t: b.start + p.actionDelay + 0.42 * (p.actionDur || 1), type: 'pop' });
  });
  // hype (default on; spec or beat "hype": false to turn off): every goal-bound shot in a stadium gets a run-up, a punch-in at the strike,
  // speed lines, a camera that follows the ball and a shake when it hits the net. Hand-made punch/shake on the beat are kept.
  S.beats.forEach((b, i) => {
    if (spec.hype === false || b.hype === false || !b.world || b.sceneObj.type !== 'stadium' || b.orbit) return;
    const shots = b.cards.filter(it => it.obj.type === 'ballpath' && it.obj.world && it.obj.flash !== false && it.obj.saveBy == null && it.start >= b.start - 0.05);
    if (!shots.length) return;
    b._hype = true; if (!b.flashes) b.flashes = 8;   // phone flashes in the stands
    const it = shots[shots.length - 1], c = it.obj, t0 = it.start - b.start, dur = c.dur || 1.6;
    if (shots.length === 1) b._follow = { t: t0, dur, pts: c.points, slowmo: c.slowmo, amount: b.follow != null ? b.follow : 0.6 };
    b.punch = (b.punch || []).concat(shots.map(s => ({ t: s.start - b.start - 0.04, amount: 0.13, dur: Math.min(1.4, (s.obj.dur || 1.6) + 0.7) })));
    b.shake = (b.shake || []).concat(shots.map(s => ({ t: s.start - b.start + (s.obj.dur || 1.6), amount: 20 })));
    b.speedlines = (b.speedlines || []).concat(shots.map(s => ({ t: s.start - b.start - 0.05, dur: 0.7, amount: 0.4 })));
    for (const s of shots) S.events.push({ t: s.start - 0.04, type: 'whoosh' });
  });
  S.events = S.events.filter(e => e.t < S.dur);
  return window.getInfo();
};
window.getInfo = () => ({
  duration: S.dur,
  events: S.events,
  beats: S.beats.map(b => ({ start: b.start, dur: b.dur, headline: b.headline })),
  scenes: S.beats.map(b => b.sceneObj.type),
});
function beatIdx(t) {
  for (let i = S.beats.length - 1; i >= 0; i--) if (t >= S.beats[i].start) return i;
  return 0;
}

// ---------- frame ----------
// Blur is done on a quarter-size copy and scaled back up: far cheaper than a full-size canvas filter.
const Q = 4, bgc = document.createElement('canvas');
bgc.width = W / Q; bgc.height = H / Q;
const bgx = bgc.getContext('2d');
// Polaroid flashback: the new scene starts as a tilted, sepia instant photo and grows to fill the frame.
const fullc = document.createElement('canvas');
fullc.width = W; fullc.height = H;
function polaroid(lt, label) {
  const k = ease(pr(lt, 0.25, 0.9));
  if (k >= 1) return;
  const fx = fullc.getContext('2d');
  fx.clearRect(0, 0, W, H); fx.drawImage(cv, 0, 0);
  ctx.fillStyle = '#0b0c10'; ctx.fillRect(0, 0, W, H);
  const s = lerp(0.6, 1.0, k), pw = W * s, ph = H * 0.72 * s + (H * 0.28 * s) * k;
  ctx.save();
  ctx.translate(W / 2, H * 0.5); ctx.rotate(lerp(-0.09, 0, k));
  const bw = lerp(30, 0, k), bb = lerp(150, 0, k);
  ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 50;
  ctx.fillStyle = '#f6f3ea'; ctx.fillRect(-pw / 2 - bw, -ph / 2 - bw, pw + bw * 2, ph + bw + bb);
  ctx.shadowBlur = 0;
  ctx.filter = `sepia(${((1 - k) * 0.85).toFixed(2)}) contrast(${(1 + (1 - k) * 0.1).toFixed(2)})`;
  const sh = Math.min(H, W * ph / pw);
  ctx.drawImage(fullc, 0, (H - sh) / 2, W, sh, -pw / 2, -ph / 2, pw, ph);
  ctx.filter = 'none';
  if (label && k < 0.6) {
    ctx.globalAlpha = 1 - k / 0.6;
    font(400, 72, 'Marker', '1px'); ctx.fillStyle = '#2b2b33'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(label, 0, ph / 2 + bb / 2);
  }
  ctx.restore();
}

// Punch-ins (quick zoom towards a point, e.g. on a kick) and impact shake, applied to the scene only.
function cameraFX(b, lt, hook) {
  let s = 1, cx = W / 2, cy = H * 0.58, dx = 0, dy = 0;
  if (hook && S.spec.hookZoom !== false) s = 1 + 0.14 * (1 - eOut(pr(lt, 0, 0.9)));   // the video opens mid-move: a zoom-out burst from frame 0
  for (const p of b.punch || []) {
    const r = lt - p.t, d = p.dur || 1.2;
    if (r < 0 || r > d) continue;
    const k = r < 0.14 ? eOut(r / 0.14) : r > d - 0.35 ? ease((d - r) / 0.35) : 1;
    s = Math.max(s, 1 + (p.amount || 0.25) * k);
    if (p.anchor != null && S.anchors[p.anchor]) { const a = S.anchors[p.anchor]; cx = a.x; cy = a.y - a.u * 0.5; }
    else { cx = p.x != null ? p.x : cx; cy = p.y != null ? p.y : cy; }
  }
  for (const sh of b.shake || []) {
    const r = lt - sh.t;
    if (r < 0 || r > 0.45) continue;
    const a = (sh.amount || 18) * (1 - r / 0.45);
    dx += Math.sin(r * 90) * a; dy += Math.cos(r * 73) * a * 0.7;
  }
  if (s === 1 && dx === 0 && dy === 0) return;
  const fx = fullc.getContext('2d');
  fx.clearRect(0, 0, W, H); fx.drawImage(cv, 0, 0);
  ctx.save();
  ctx.translate(cx + dx, cy + dy); ctx.scale(s, s); ctx.translate(-cx, -cy);
  ctx.drawImage(fullc, 0, 0);
  ctx.restore();
}

// Out-of-focus fans in the foreground: gives stadium shots depth.
function drawFans(t, scene) {
  const R = rng(77), cols = scene.crowd || ['#1d4fb8'];
  bgx.clearRect(0, 0, W / Q, H / Q);
  bgx.save(); bgx.scale(1 / Q, 1 / Q);
  const main = ctx;
  ctx = bgx; // draw the fans at quarter size, then upscale: they come out soft
  for (let row = 0; row < 3; row++) {
    const base = H * (0.9 + row * 0.05), r = 44 + row * 14, n = 8 - row;
    for (let k = 0; k < n + 1; k++) {
      const x = (k + R() * 0.6 - 0.3) * W / n, ph = R() * 6.28;
      const y = base + Math.sin(t * 1.3 + ph) * 4 + R() * 20;
      const c = R() < 0.35 ? shade(cols[Math.floor(R() * cols.length)], -0.7) : '#0b0e14';
      ctx.fillStyle = c;
      ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
      rrect(x - r * 1.7, y + r * 0.8, r * 3.4, r * 3, r); ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,0.07)'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(x, y, r, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke();
    }
  }
  bgx.restore();
  ctx = main;
  ctx.save(); ctx.globalAlpha = 0.95; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(bgc, 0, 0, W, H);
  ctx.restore();
}
// Split screen: the beat's own scene fills the left half and "split": {scene, players, camera, camFrom, move, lights} the right,
// each with its own stadium, crowd, camera and lighting, divided by a glowing diagonal. Each half is centred on its camera's target.
// "split.at" (a phrase) slides the right half in on that word; without it both halves are there from the first frame.
let splitA = null, splitB = null;
function drawSplit(b, ts, lts, lt) {
  const sp = b.split;
  if (!splitA) { splitA = document.createElement('canvas'); splitB = document.createElement('canvas'); for (const c of [splitA, splitB]) { c.width = W; c.height = H; } }
  const ax = splitA.getContext('2d'), bx = splitB.getContext('2d');
  ax.clearRect(0, 0, W, H); ax.drawImage(cv, 0, 0);
  const to = camPreset(sp.camera), from = camPreset(sp.camFrom || sp.camera), k = pr(lts, 0, sp.move || b.dur);
  const cam = mkCam(lerp3(from.pos, to.pos, k), lerp3(from.tgt, to.tgt, k));
  S.cam = cam; ctx.clearRect(0, 0, W, H);
  drawSky(sp.scene); drawPitch(cam, sp.scene); drawStadium(cam, ts, b.splitWorld); drawGoals(cam);
  drawPlayers(cam, ts - b.playersStart, sp.players || []);
  if (sp.lights != null && sp.lights < 1) { ctx.fillStyle = `rgba(4,6,10,${(1 - sp.lights) * 0.8})`; ctx.fillRect(0, 0, W, H); }
  bx.clearRect(0, 0, W, H); bx.drawImage(cv, 0, 0);
  const inK = sp.t != null ? eOut(pr(lt, sp.t, 0.45)) : 1, lean = sp.lean != null ? sp.lean : 70, mid = lerp(W + lean + 10, W / 2, inK);
  ctx.clearRect(0, 0, W, H);
  ctx.save(); ctx.translate(lerp(0, -W / 4, inK), 0); ctx.drawImage(splitA, 0, 0); ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.moveTo(mid + lean, 0); ctx.lineTo(W, 0); ctx.lineTo(W, H); ctx.lineTo(mid - lean, H); ctx.closePath(); ctx.clip();
  ctx.translate(mid - W / 2 + W / 4, 0); ctx.drawImage(splitB, 0, 0); ctx.restore();
  ctx.save(); ctx.strokeStyle = '#fff'; ctx.shadowColor = sp.glow || '#ffffff'; ctx.shadowBlur = 30; ctx.lineWidth = 8 + 2 * Math.sin(lt * 5);
  ctx.beginPath(); ctx.moveTo(mid + lean, -10); ctx.lineTo(mid - lean, H + 10); ctx.stroke(); ctx.restore();
}
// Whip-pan transition: the new scene whips in sideways with a motion smear (beat "transition": "whip", "whipDir": 1|-1).
function whipPan(lt, dir) {
  const d = 0.34; if (lt >= d) return;
  const k = eOut(lt / d), off = (1 - k) * W * 0.9 * (dir || 1), fx = fullc.getContext('2d');
  fx.clearRect(0, 0, W, H); fx.drawImage(cv, 0, 0);
  ctx.save(); ctx.fillStyle = '#05070b'; ctx.fillRect(0, 0, W, H);
  for (let j = 7; j >= 0; j--) { ctx.globalAlpha = j === 0 ? 1 : 0.22; ctx.drawImage(fullc, off * (1 + j * 0.16), 0); if (j) ctx.drawImage(fullc, off * (1 + j * 0.16) - Math.sign(off || 1) * W, 0); }
  ctx.restore();
}
function renderAt(t) {
  const i = beatIdx(t), b = S.beats[i], lt = t - b.start, next = S.beats[i + 1];
  const scene = b.sceneObj;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  // freeze frame: from b.freeze (s into the beat) the scene stops (camera, players, ball, crowd) while cards keep animating
  const fz = b.freeze != null && lt > b.freeze ? b.freeze : null;
  const ts = fz != null ? b.start + fz : t, lts = fz != null ? fz : lt;
  S.anchors = []; S.cam = null; S.cur = b; S.t = ts;
  if (scene.type === 'stage') drawStage(ts, b, stageCamAt(i, lts), ts - b.playersStart);
  else if (scene.type === 'booth') {   // slow push-in toward the desk so the booth never sits still (zoomFrom/zoom override)
    const z = lerp(b.zoomFrom != null ? b.zoomFrom : 1, b.zoom != null ? b.zoom : 1.15, pr(lts, 0, b.dur));   // linear, so the end of the beat keeps moving
    ctx.save(); ctx.translate(W / 2, H * 0.55); ctx.scale(z, z); ctx.translate(-W / 2, -H * 0.55);
    drawBooth(ts, b, ts - b.playersStart); ctx.restore();
  }
  else if (scene.type === 'studio') drawStudio(ts, scene);
  else if (scene.type === 'toy') drawToyScene(ts, b, i, lts);   // one-off toy/clay look (toy.js)
  else {
    const c = camInBeat(i, lts), cam = mkCam(c.pos, c.tgt);
    S.cam = cam;
    drawSky(scene);
    drawPitch(cam, scene);
    drawStadium(cam, ts, b.world);
    drawGoals(cam);
    drawPlayers(cam, ts - b.playersStart, b.playersArr);
    if (b.split) drawSplit(b, ts, lts, lt);
  }
  if (b.punch || b.shake || i === 0) cameraFX(b, lts, i === 0);
  S.t = t;
  if (b.freeze != null && lt > b.freeze) {   // drain the colour and flash white, like a paused broadcast
    const k = pr(lt, b.freeze, 0.3), fx = fullc.getContext('2d');
    fx.clearRect(0, 0, W, H); fx.drawImage(cv, 0, 0);
    const z = 1 + 0.05 * (lt - b.freeze);   // slow push-in on the frozen frame so it never sits still
    ctx.save(); ctx.globalAlpha = 1; ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
    ctx.filter = k < 1 ? 'none' : 'grayscale(1) contrast(1.15) brightness(0.8)'; ctx.drawImage(fullc, 0, 0);
    if (k < 1) { ctx.globalAlpha = k; ctx.filter = 'grayscale(1) contrast(1.15) brightness(0.8)'; ctx.drawImage(fullc, 0, 0); }
    ctx.restore();
    const fl = 1 - pr(lt, b.freeze, 0.35);
    if (fl > 0) { ctx.fillStyle = `rgba(255,255,255,${0.55 * fl})`; ctx.fillRect(0, 0, W, H); }
  }
  if (b.letterbox) {   // cinematic bars (drone replays, big moments)
    const k = eOut(pr(lt, 0, 0.4)), hb = 150 * k;
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, hb); ctx.fillRect(0, H - hb, W, hb);
    if (b.replayTag) {
      ctx.save(); ctx.globalAlpha = k * (0.75 + 0.25 * Math.sin(lt * 5));
      ctx.fillStyle = '#d6283b'; ctx.beginPath(); ctx.arc(W - 250, H - hb - 46, 11, 0, 7); ctx.fill();
      font(800, 30, 'Mono', '5px'); ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(b.replayTag, W - 228, H - hb - 44);
      ctx.restore();
    }
  }
  if (b.speedlines) drawSpeedlines(b, lt);
  if (b.flashes) {   // phone and camera flashes popping across the stands (big moments, celebrations)
    const n = typeof b.flashes === 'number' ? b.flashes : 14, slot = Math.floor(t / 0.09);
    for (let k = 0; k < 3; k++) {
      const R = rng((slot - k) * 7 + 3);
      for (let i = 0; i < n; i++) {
        const x = R() * W, y = H * (0.36 + R() * 0.24), age = (t - (slot - k) * 0.09) / 0.27;
        if (R() > 0.45 || age > 1) continue;
        const a = (1 - age) * 0.9, r = 10 + R() * 22;
        const g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.2);
        g.addColorStop(0, `rgba(255,255,255,${a})`); g.addColorStop(0.3, `rgba(255,250,235,${a * 0.5})`); g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = g; ctx.fillRect(x - r * 2.2, y - r * 2.2, r * 4.4, r * 4.4);
      }
    }
  }
  if (scene.type === 'stadium' && b.fans) drawFans(t, scene);
  if (b.transition === 'polaroid' && lt < 1.2) polaroid(lt, b.polaroidLabel);
  if (b.transition === 'vhs') vhsRewind(lt, b.vhsLabel, b.vhsDur || 1.6);
  if (b.transition === 'whip') whipPan(lt, b.whipDir);
  const blend = (key, def) => {
    const p = S.beats[i - 1], cur = b[key] != null ? b[key] : def;
    const from = p && !b.cut && p[key] != null ? p[key] : (p && !b.cut ? def : cur);
    return lerp(from, cur, ease(pr(lt, 0, 0.6)));
  };
  const lights = blend('lights', 1), focus = blend('focus', 0);
  if (lights < 1) {
    ctx.fillStyle = `rgba(4,6,10,${(1 - lights) * 0.8})`; ctx.fillRect(0, 0, W, H);
    const hz = ctx.createRadialGradient(W / 2, H * 0.52, 0, W / 2, H * 0.52, W);
    hz.addColorStop(0, `rgba(140,160,190,${(1 - lights) * 0.1})`); hz.addColorStop(1, 'rgba(140,160,190,0)');
    ctx.fillStyle = hz; ctx.fillRect(0, 0, W, H);
  }
  if (focus > 0.01) {
    bgx.clearRect(0, 0, W / Q, H / Q);
    bgx.filter = `blur(${(focus * 2.5).toFixed(2)}px)`;
    bgx.drawImage(cv, 0, 0, W / Q, H / Q);
    bgx.filter = 'none';
    ctx.save(); ctx.imageSmoothingQuality = 'high';
    ctx.globalAlpha = Math.min(1, focus * 2.5);
    ctx.drawImage(bgc, 0, 0, W, H);
    ctx.restore();
    ctx.fillStyle = `rgba(0,0,0,${(focus * 0.45).toFixed(3)})`; ctx.fillRect(0, 0, W, H);
  }
  if (b.confetti && t >= b.confettiStart) drawConfetti(t - b.confettiStart, b.confettiColors || [S.accent, '#ffffff', ...(scene.crowd || [])], 11);

  // legibility overlays
  const tc = scene.type === 'stage' ? '16,6,8' : '8,10,15';
  let g = ctx.createLinearGradient(0, 0, 0, H * 0.4);
  g.addColorStop(0, `rgba(${tc},0.92)`); g.addColorStop(0.6, `rgba(${tc},0.55)`); g.addColorStop(1, `rgba(${tc},0)`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * 0.4);
  g = ctx.createRadialGradient(W / 2, H * 0.55, W * 0.45, W / 2, H * 0.55, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  // cards
  S.hlBottom = !S.spec.captions && b.headline ? HL.y + (layoutHL(b.headline).length - 1) * HL.lh + 24 : null;
  for (const it of b.cards) {
    const ct = t - it.start;
    if (ct < 0) continue;
    if (it.obj.hideT != null && ct >= it.obj.hideT) continue;   // any card can vanish on a word (hideAt)
    const fn = CARDS[it.obj.type];
    if (it.obj.type === 'ball' || it.obj.type === 'vehicle' || (it.obj.type === 'ballpath' && it.obj.world)) continue; // drawn with the players
    const cont = next && it.obj.id && next.cards.some(n => n.obj.id === it.obj.id);
    const leaving = next && !next.cards.includes(it) && !cont;
    const ek = leaving ? pr(lt, b.dur - 0.45, 0.45) : 0;
    const outA = leaving && !fn.selfExit ? 1 - pr(lt, b.dur - 0.25, 0.25) : 1;
    const inA = fn.selfExit || it.obj._prev ? 1 : eOut(pr(ct, 0, 0.45));
    ctx.save();
    ctx.globalAlpha = (fn.noSlide ? 1 : inA) * outA;
    if (!fn.selfExit && !fn.noSlide) {
      const sc = 0.94 + 0.06 * inA, cy0 = cardY(it.obj);
      ctx.translate(W / 2, cy0 + (1 - inA) * 60); ctx.scale(sc, sc); ctx.translate(-W / 2, -cy0);
    }
    fn(it.obj, ct, W / 2 + (it.obj.shiftX || 0), cardY(it.obj), ek);
    ctx.restore();
  }

  // header
  drawBrand();
  const prevB = S.beats[i - 1];
  const kChanged = !prevB || prevB.kickerText !== b.kickerText;
  const kOut = next && next.kickerText !== b.kickerText ? pr(lt, b.dur - 0.22, 0.22) : 0;
  // beat 1 is the hook: kicker and headline are fully visible from frame 1
  drawKicker(b.kickerText, (kChanged && i > 0 ? eOut(pr(lt, 0, 0.4)) : 1) * (1 - kOut));
  const hChanged = i > 0 && prevB.headline !== b.headline;
  const hOut = next && next.headline !== b.headline ? lt - (b.dur - 0.22) : null;
  if (S.spec.captions) drawCaptions(t);   // word-by-word captions take the headline's place
  else if (b.headline) drawHeadline(b.headline, hChanged ? lt : 99, hOut != null && hOut >= 0 ? hOut : null, b.accent, i === 0 && b.hookWords ? t : null);
  if (S.outro && t >= S.outro.start) drawOutro(t - S.outro.start);

  ctx.restore();
}

// End screen: the last shot softly blurs and darkens, and a small brand card fades in.
function drawOutro(ot) {
  if (typeof toyOn === 'function' && toyOn()) return drawToyOutro(ot);
  const k = ease(pr(ot, 0, 0.6));
  bgx.clearRect(0, 0, W / Q, H / Q);
  bgx.filter = 'blur(2.5px)';
  bgx.drawImage(cv, 0, 0, W / Q, H / Q);
  bgx.filter = 'none';
  ctx.save();
  ctx.globalAlpha = k; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(bgc, 0, 0, W, H);
  ctx.globalAlpha = 1;
  ctx.fillStyle = `rgba(6,8,12,${0.62 * k})`; ctx.fillRect(0, 0, W, H);
  const a = eOut(pr(ot, 0.35, 0.5)), y = H * 0.47 + (1 - a) * 24;
  ctx.globalAlpha = a;
  if ((S.spec.brandStyle || 'shirt') === 'shirt') drawBrandShirt(W / 2, y - 86, 120);
  else {
    rrect(W / 2 - 44, y - 130, 88, 88, 22); ctx.fillStyle = S.accent; ctx.fill();
    ctx.fillStyle = '#0d1016'; ctx.beginPath(); ctx.arc(W / 2, y - 86, 20, 0, 7); ctx.fill();
    ctx.fillStyle = S.accent; ctx.beginPath(); ctx.arc(W / 2, y - 86, 7, 0, 7); ctx.fill();
  }
  font(800, 58, 'Inter', '-1px'); ctx.fillStyle = '#f4f2ec'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.fillText(S.spec.brand || 'theo6k', W / 2, y + 20);
  font(500, 22, 'Mono', '6px'); ctx.fillStyle = '#9aa1ad';
  ctx.fillText((S.spec.outroText || 'Follow for more football stories').toUpperCase(), W / 2, y + 72);
  ctx.fillStyle = S.accent; ctx.fillRect(W / 2 - 40 * a, y + 100, 80 * a, 3);
  ctx.restore();
}

window.frame = function (t, type = 'jpeg') {
  renderAt(t);
  return type === 'png' ? cv.toDataURL('image/png').split(',')[1] : cv.toDataURL('image/jpeg', 0.93).split(',')[1];
};
