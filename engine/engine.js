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
  const to = camPreset(b.camera);
  const from = (i === 0 || b.cut) ? camPreset(b.camFrom || b.camera) : camEnd(i - 1);
  const md = b.move != null ? b.move : Math.min(2.4, b.dur * 0.8);
  const k = ease(pr(lt, 0, md));
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
const P0 = { rot: 0, px: 0, hy: 0, lean: 0, L: [-0.06, 0], R: [0.06, 0], AL: [-0.16, 0.25], AR: [0.16, 0.25] };
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
  if (name === 'run') {
    const ph = t / 0.5 * Math.PI * 2, s = Math.sin(ph);
    return { ...P0, L: [-0.08 + 0.05 * s, Math.max(0, s) * 0.9], R: [0.08 + 0.05 * s, Math.max(0, -s) * 0.9],
      AL: [-0.3, 1.1 + 0.5 * s], AR: [0.3, 1.1 - 0.5 * s], hy: -0.025 * Math.abs(s), lean: 0.03 * s };
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
      if (p.dir === -1) { ps.rot = -ps.rot; ps.px = -ps.px; [ps.AL, ps.AR] = [[-ps.AR[0], ps.AR[1]], [-ps.AL[0], ps.AL[1]]]; [ps.L, ps.R] = [[-ps.R[0], ps.R[1]], [-ps.L[0], ps.L[1]]]; }
      return ps;
    };
    if (t >= d && t < d + dur) return act((t - d) / dur);
    if (t >= d + dur) return p.after ? loopPose(p.after, t - d - dur) : act(1);
    if (walking) return loopPose('run', t);
    return loopPose(p.before || 'idle', t);
  }
  if (walking) return loopPose('run', t);
  return loopPose(p.action || 'idle', t);
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
  ctx.fillStyle = c.shirt;
  ctx.beginPath(); ctx.moveTo(-u * 0.16, -u * 0.32); ctx.lineTo(u * 0.16, -u * 0.32); ctx.lineTo(u * 0.135, -u * 0.03); ctx.lineTo(-u * 0.135, -u * 0.03); ctx.closePath(); ctx.fill();
  if (c.k.stripes || c.k.checks) {
    ctx.save(); ctx.clip();
    const sq = u * 0.045;
    if (c.k.stripes) for (let i = -4; i <= 4; i++) { ctx.fillStyle = c.k.stripes[(i + 8) % 2]; ctx.fillRect(i * sq - sq / 2, -u * 0.33, sq, u * 0.31); }
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
  for (const [side, arm] of [[-1, ps.AL], [1, ps.AR]]) {
    const [a, e] = arm, sx = side * u * 0.15, sy = -u * 0.3;
    const [ex, ey] = limb(sx, sy, a, u * 0.14, u * 0.07, c.k.sleeves || c.shirt);
    const [hx, hy] = limb(ex, ey, a + side * e, u * 0.15, u * 0.06, c.skin);
    if (p.gloves) { ctx.fillStyle = p.gloves; ctx.beginPath(); ctx.arc(hx, hy, u * 0.045, 0, 7); ctx.fill(); }
  }
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
  if (p.action || p.rig) {
    const ps = poseFor(p, t, walk > 0);
    const lift = Math.max(0, -ps.hy) * 3;
    ctx.fillStyle = `rgba(0,0,0,${0.3 / (1 + lift)})`;
    ctx.beginPath(); ctx.ellipse(ps.px * u + Math.sin(ps.rot) * u * 0.3, 0, u * (0.17 + Math.abs(Math.sin(ps.rot)) * 0.3), u * 0.035, 0, 0, 7); ctx.fill();
    rigBody(u, p, t, walk > 0, { k, skin, hair, shirt, shorts, socks, txt });
    if (p.tag != null) drawTag(u, p, t);
    ctx.restore();
    return;
  }
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.beginPath(); ctx.ellipse(0, 0, u * 0.17, u * 0.035, 0, 0, 7); ctx.fill();
  const sw = Math.sin(t * 9) * walk, legW = u * 0.075, gap = u * 0.05;
  for (const side of [-1, 1]) {
    const lift = Math.max(0, side * sw) * u * 0.05, lx = side * gap;
    ctx.fillStyle = skin; ctx.fillRect(lx - legW / 2, -u * 0.47 - lift, legW, u * 0.2);
    ctx.fillStyle = socks; rrect(lx - legW / 2, -u * 0.28 - lift, legW, u * 0.25, legW * 0.3); ctx.fill();
    ctx.fillStyle = '#15171c'; rrect(lx - legW * 0.6, -u * 0.04 - lift, legW * 1.2, u * 0.045, legW * 0.3); ctx.fill();
  }
  ctx.fillStyle = shorts; rrect(-u * 0.135, -u * 0.56, u * 0.27, u * 0.15, u * 0.02); ctx.fill();
  const armsUp = p.pose === 'arms_up';
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.translate(side * u * 0.15, -u * 0.8);
    ctx.rotate(armsUp ? side * 0.25 + Math.PI : p.pose === 'keeper' ? side * 0.95 : side * 0.12);
    ctx.fillStyle = k.sleeves || shirt; rrect(-u * 0.04, 0, u * 0.08, u * 0.1, u * 0.02); ctx.fill();
    ctx.fillStyle = skin; rrect(-u * 0.03, u * 0.09, u * 0.06, u * 0.2, u * 0.03); ctx.fill();
    if (p.gloves) { ctx.fillStyle = p.gloves; ctx.beginPath(); ctx.arc(0, u * 0.3, u * 0.042, 0, 7); ctx.fill(); }
    ctx.restore();
  }
  ctx.fillStyle = shirt;
  ctx.beginPath();
  ctx.moveTo(-u * 0.16, -u * 0.82); ctx.lineTo(u * 0.16, -u * 0.82);
  ctx.lineTo(u * 0.135, -u * 0.53); ctx.lineTo(-u * 0.135, -u * 0.53); ctx.closePath(); ctx.fill();
  if (k.stripes || k.checks) {
    ctx.save();
    ctx.clip();
    const sq = u * 0.045;
    if (k.stripes) {
      for (let i = -4; i <= 4; i++) { ctx.fillStyle = k.stripes[(i + 8) % 2]; ctx.fillRect(i * sq - sq / 2, -u * 0.83, sq, u * 0.31); }
    } else {
      for (let r = 0; r < 8; r++) for (let c = -4; c <= 4; c++) {
        ctx.fillStyle = k.checks[(r + c + 16) % 2]; ctx.fillRect(c * sq - sq / 2, -u * 0.83 + r * sq, sq, sq);
      }
    }
    ctx.restore();
  }
  ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(-u * 0.135, -u * 0.56, u * 0.27, u * 0.03);
  if (u > 50 && p.front) {
    ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.num != null) { font(800, u * 0.07, 'Inter', '0px'); ctx.fillText(String(p.num), u * 0.06, -u * 0.7); }
  } else if (u > 50) {
    ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.name) { font(700, Math.max(6, u * 0.034), 'Mono', `${u * 0.004}px`); ctx.fillText(p.name.toUpperCase(), 0, -u * 0.745); }
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
  for (const p of players) {
    let x = p.x || 0, z = p.z || 0, walk = 0;
    if (p.enter === 'walk') {
      const k = pr(lt, p.delay || 0, p.walkDur || 1.8);
      x = lerp(p.fromX != null ? p.fromX : x, x, eOut(k));
      z = lerp(p.fromZ != null ? p.fromZ : z - 6, z, eOut(k));
      walk = k < 1 ? 1 - k * 0.6 : 0;
    }
    const q = toCam(cam, [x, 0, z]);
    if (q[2] < NEAR + 0.5) continue;
    list.push({ p, q, walk });
  }
  for (const o of list) {
    const s = proj(o.q);
    S.anchors[players.indexOf(o.p)] = { x: s[0], y: s[1], u: FOC * 1.85 / o.q[2] };
  }
  // balls in the world (resting ball, shots) are drawn in depth order with the players, so they pass behind or in front correctly
  for (const it of S.cur ? S.cur.cards : []) {
    const c = it.obj, ct = S.t - it.start;
    if (ct < 0 || !(c.type === 'ball' || (c.type === 'ballpath' && c.world))) continue;
    if (c.type === 'ball' && c.until != null && ct >= c.until) continue;
    if (c.type === 'ballpath' && ct >= (c.dur || 1.6) && c.flash === false) continue;
    const q = toCam(cam, c.type === 'ball' ? c.point : ballWorld(c, ct));
    if (q[2] < NEAR) continue;
    list.push({ q, ball: c, ct });
  }
  list.sort((a, b) => b.q[2] - a.q[2]);
  drawUnderPens();
  for (const o of list) {
    if (o.ball) { ctx.save(); CARDS[o.ball.type](o.ball, o.ct, W / 2, 0, 0); ctx.restore(); continue; }
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
function drawHeadline(text, inT, outT, accent) {
  const lines = layoutHL(text);
  font(700, HL.size, 'Inter', '-1.5px');
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((line, li) => {
    const a = eOut(pr(inT, 0.05 + li * 0.08, 0.45));
    const o = outT != null ? pr(outT, 0, 0.22) : 0;
    ctx.save();
    ctx.globalAlpha = a * (1 - o);
    const y = HL.y + li * HL.lh + (1 - a) * 30 - o * 14;
    for (const tk of line) {
      ctx.fillStyle = tk.acc ? (accent || S.accent) : '#f4f2ec';
      ctx.fillText(tk.w, HL.x + tk.x, y);
    }
    ctx.restore();
  });
}
function drawKicker(text, a) {
  if (!text) return;
  ctx.save();
  ctx.globalAlpha = a;
  font(500, 23, 'Mono', '5px');
  ctx.fillStyle = '#8b919c'; ctx.textAlign = 'left';
  ctx.fillText('— ' + text.toUpperCase(), HL.x, HL.y - 92);
  ctx.restore();
}
function drawBrand() {
  const x = HL.x, y = 220;
  rrect(x, y - 30, 40, 40, 10); ctx.fillStyle = S.accent; ctx.fill();
  ctx.fillStyle = '#0d1016';
  ctx.beginPath(); ctx.arc(x + 20, y - 10, 9, 0, 7); ctx.fill();
  ctx.fillStyle = S.accent;
  ctx.beginPath(); ctx.arc(x + 20, y - 10, 3.2, 0, 7); ctx.fill();
  font(700, 26, 'Mono', '1px');
  ctx.fillStyle = '#d6dae1'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  ctx.fillText(S.spec.brand || 'theo6k', x + 54, y);
}

// ---------- cards ----------
const GOLD = ['#fff4c9', '#f1c453', '#b77d16'];
function cardY(c) {
  if (c.y != null) return c.y;
  return { top: 0.4, mid: 0.47, center: 0.55, low: 0.8 }[c.pos || 'mid'] * H;
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
    const rows = c.rows, rh = 78, bw = 780, bh = 110 + rows.length * rh;
    cardBox(cx, cy, bw, bh, c.label);
    const top = cy - bh / 2 + 82;
    rows.forEach((r, i) => {
      const a = eOut(pr(ct, 0.25 + i * 0.12, 0.4));
      ctx.save(); ctx.globalAlpha *= a;
      const y = top + i * rh + rh / 2 + (1 - a) * 20, x0 = cx - bw / 2 + 50;
      font(500, 26, 'Mono', '0px'); ctx.fillStyle = '#6f7684'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillText(String(r.pos), x0, y);
      drawShirtIcon(x0 + 70, y, 46, r.color || '#888', r.color2);
      font(700, 30, 'Mono', '3px'); ctx.fillStyle = '#eef0f3';
      ctx.fillText(r.name.toUpperCase(), x0 + 115, y);
      const v = countVal({ value: r.pts, from: r.from || 0 }, ct, 0.5, 1.3);
      font(800, 52, 'Inter', '0px'); ctx.textAlign = 'right';
      ctx.fillStyle = r.highlight ? S.accent : '#eef0f3';
      ctx.fillText(String(Math.round(v)), cx + bw / 2 - 50, y + 2);
      ctx.restore();
    });
    if (c.pill) {
      const k = pr(ct, 1.9, 0.35), s = k > 0 ? eBack(k) : 0;
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
      const k = eOut(pr(ct, 0.8 + i * 0.5, 0.4));
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
      const k = eOut(pr(ct, 0.2 + i * 0.5, 0.9));
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
    if (it.obj.type !== 'pen' || !it.obj.strokes.some(s => s.layer === 'under')) continue;
    const ct = S.t - it.start;
    if (ct < 0) continue;
    ctx.save();
    it.obj._under = true; CARDS.pen(it.obj, ct); it.obj._under = false;
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

// Newspaper front page that spins in (archive / reaction beats). Masthead is fictional: never imitate a real paper.
CARDS.newspaper = function (c, ct, cx, cy) {
  const k = eOut(pr(ct, 0, 0.9));
  if (k <= 0) return;
  const w = c.w || 760, h = c.h || 980;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(lerp(-Math.PI * 4, c.tilt != null ? c.tilt : -0.05, k));
  ctx.scale(lerp(0.05, 1, k), lerp(0.05, 1, k));
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
  ctx.font = `900 ${c.size || 300}px Inter`; ctx.fillStyle = c.color || '#16130e'; ctx.fillText(c.headline || '', 0, -h / 2 + 170 + (c.size || 300) * 0.82);
  ctx.fillStyle = '#16130e'; ctx.font = `700 54px ${serif}`;
  const subY = -h / 2 + 200 + (c.size || 300) * 0.82 + 40;
  String(c.sub || '').split('\n').forEach((l, i) => ctx.fillText(l, 0, subY + i * 60));
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
  if (k0 >= 1 && c.flash === false && c.hide !== false) return;
  let P = c.points, r0 = c.r || 18, r1 = c.rEnd || 8;
  if (c.world) {
    const q = c.points.map(p => toCam(S.cam, p));
    if (q.some(v => v[2] < NEAR)) return;
    P = q.map(proj);
    r0 = Math.max(4, FOC * 0.11 / q[0][2]); r1 = Math.max(3, FOC * 0.11 / q[2][2]);
  }
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
    case 'table': ticks(0.5, 1.1); if (c.pill) ev.push({ t: 1.9, type: 'pop' }); break;
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
    case 'newspaper': ev.push({ t: 0, type: 'whoosh' }, { t: 0.9, type: 'impact' }); break;
    case 'ballpath': ev.push({ t: 0, type: 'swish' }); if (c.flash !== false) ev.push({ t: c.dur || 1.6, type: 'crowd' }); else ev.push({ t: c.dur || 1.6, type: 'pop' }); break;
    case 'receipt': { const n = (c.lines || []).length + (c.total ? 1 : 0) + 1; for (let i = 0; i < n; i++) for (let t = 0.2 + i * (c.step || 0.45); t < 0.2 + i * (c.step || 0.45) + 0.25; t += 0.03) ev.push({ t, type: 'tick' }); break; }
    case 'stamp': ev.push({ t: 0.16, type: 'impact' }); break;
    case 'pen': c.strokes.forEach(s => ev.push({ t: s.t || 0, type: 'swipe' })); break;
    case 'balls': for (let i = 0; i < c.n; i++) ev.push({ t: 0.3 + i * (c.step || 0.12), type: 'pop' }); break;
    case 'ruler': (c.markers || []).forEach((m, i) => ev.push({ t: 0.8 + i * 0.5, type: 'pop' })); if (c.bracket) ev.push({ t: 0.8 + (c.markers || []).length * 0.5, type: 'swipe' }); break;
    case 'trophies': c.items.forEach((it, i) => ev.push({ t: 0.9 + i * 0.5, type: 'impact' })); break;
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
    if (b.players === undefined && prev) { B.playersArr = prev.playersArr; B.playersStart = prev.playersStart; }
    else { B.playersArr = b.players || []; B.playersStart = B.start; }
    B.kickerText = b.kicker !== undefined ? b.kicker : (prev ? prev.kickerText : '');
    B.cards = [];
    for (const c of b.card == null ? [] : Array.isArray(b.card) ? b.card : [b.card]) {
      if (c === 'same') { if (prev) B.cards.push(...prev.cards); }
      else {
        const pb = prev && c.id && prev.cards.find(x => x.obj.id === c.id);
        if (pb) c._prev = pb.obj;
        // beat 1 is the hook: its cards are already in on frame 1 (the frame people see while scrolling)
        const delay = c.delay != null ? c.delay : (i === 0 ? -0.45 : 0.3);
        B.cards.push({ obj: c, start: pb ? B.start : B.start + delay });
      }
    }
    if (b.confetti) { B.confettiStart = prev && prev.confetti ? prev.confettiStart : B.start; }
    prev = B;
    return B;
  });
  // short, subtle end screen after the last beat
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
    if (b.confetti && !(i > 0 && S.beats[i - 1].confetti)) S.events.push({ t: b.start, type: 'crowd' });
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
    for (const p of b.playersArr || []) if (p.action === 'kick' && p.actionDelay != null && b.playersStart === b.start) S.events.push({ t: b.start + p.actionDelay + 0.42 * (p.actionDur || 1), type: 'pop' });
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
function cameraFX(b, lt) {
  let s = 1, cx = W / 2, cy = H * 0.58, dx = 0, dy = 0;
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
function renderAt(t) {
  const i = beatIdx(t), b = S.beats[i], lt = t - b.start, next = S.beats[i + 1];
  const scene = b.sceneObj;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  S.anchors = []; S.cam = null; S.cur = b; S.t = t;
  if (scene.type === 'stage') drawStage(t, b, stageCamAt(i, lt), t - b.playersStart);
  else if (scene.type === 'booth') drawBooth(t, b, t - b.playersStart);
  else if (scene.type === 'studio') drawStudio(t, scene);
  else {
    const c = camInBeat(i, lt), cam = mkCam(c.pos, c.tgt);
    S.cam = cam;
    drawSky(scene);
    drawPitch(cam, scene);
    drawStadium(cam, t, b.world);
    drawGoals(cam);
    drawPlayers(cam, t - b.playersStart, b.playersArr);
  }
  if (b.punch || b.shake) cameraFX(b, lt);
  if (scene.type === 'stadium' && b.fans) drawFans(t, scene);
  if (b.transition === 'polaroid' && lt < 1.2) polaroid(lt, b.polaroidLabel);
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
  if (b.confetti) drawConfetti(t - b.confettiStart, b.confettiColors || [S.accent, '#ffffff', ...(scene.crowd || [])], 11);

  // legibility overlays
  const tc = scene.type === 'stage' ? '16,6,8' : '8,10,15';
  let g = ctx.createLinearGradient(0, 0, 0, H * 0.4);
  g.addColorStop(0, `rgba(${tc},0.92)`); g.addColorStop(0.6, `rgba(${tc},0.55)`); g.addColorStop(1, `rgba(${tc},0)`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * 0.4);
  g = ctx.createRadialGradient(W / 2, H * 0.55, W * 0.45, W / 2, H * 0.55, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  // cards
  for (const it of b.cards) {
    const ct = t - it.start;
    if (ct < 0) continue;
    const fn = CARDS[it.obj.type];
    if (it.obj.type === 'ball' || (it.obj.type === 'ballpath' && it.obj.world)) continue; // drawn with the players
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
  if (b.headline) drawHeadline(b.headline, hChanged ? lt : 99, hOut != null && hOut >= 0 ? hOut : null, b.accent);
  if (S.outro && t >= S.outro.start) drawOutro(t - S.outro.start);

  ctx.restore();
}

// End screen: the last shot softly blurs and darkens, and a small brand card fades in.
function drawOutro(ot) {
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
  rrect(W / 2 - 44, y - 130, 88, 88, 22); ctx.fillStyle = S.accent; ctx.fill();
  ctx.fillStyle = '#0d1016'; ctx.beginPath(); ctx.arc(W / 2, y - 86, 20, 0, 7); ctx.fill();
  ctx.fillStyle = S.accent; ctx.beginPath(); ctx.arc(W / 2, y - 86, 7, 0, 7); ctx.fill();
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
