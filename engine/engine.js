'use strict';
// Theo6k reel engine: draws every frame of a 9:16 football story reel on a canvas.
// The page exposes window.loadSpec(spec), window.getInfo() and window.frame(t).

const W = 1080, H = 1920, FOC = 1150, CY = H * 0.56, NEAR = 0.6;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
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
    // goal frame and net
    const gz = e + 1.8 * s;
    path3(cam, [[-3.66, 0, e], [-3.66, 2.44, e], [3.66, 2.44, e], [3.66, 0, e]], 0.16, '#ffffff');
    const net = 'rgba(255,255,255,0.35)';
    path3(cam, [[-3.66, 2.44, e], [-3.66, 2.0, gz], [-3.66, 0, gz]], 0.05, net);
    path3(cam, [[3.66, 2.44, e], [3.66, 2.0, gz], [3.66, 0, gz]], 0.05, net);
    path3(cam, [[-3.66, 2.0, gz], [3.66, 2.0, gz]], 0.05, net);
    for (let x = -3; x <= 3; x += 1.2) path3(cam, [[x, 2.44, e], [x, 2.0, gz], [x, 0, gz]], 0.03, net);
  }
}

function drawStadium(cam, t, world) {
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

function drawPlayer(x, y, u, p, t, walk, alpha) {
  const k = p.kit || {};
  const shirt = k.shirt || '#c8102e', shorts = k.shorts || '#ffffff', socks = k.socks || shirt;
  const txt = k.text || '#ffffff', skin = p.skin || '#c68a63', hair = p.hair || '#1b1410';
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
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
    ctx.rotate(armsUp ? side * 0.25 + Math.PI : side * 0.12);
    ctx.fillStyle = k.sleeves || shirt; rrect(-u * 0.04, 0, u * 0.08, u * 0.1, u * 0.02); ctx.fill();
    ctx.fillStyle = skin; rrect(-u * 0.03, u * 0.09, u * 0.06, u * 0.2, u * 0.03); ctx.fill();
    ctx.restore();
  }
  ctx.fillStyle = shirt;
  ctx.beginPath();
  ctx.moveTo(-u * 0.16, -u * 0.82); ctx.lineTo(u * 0.16, -u * 0.82);
  ctx.lineTo(u * 0.135, -u * 0.53); ctx.lineTo(-u * 0.135, -u * 0.53); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(-u * 0.135, -u * 0.56, u * 0.27, u * 0.03);
  if (u > 50) {
    ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    if (p.name) { font(700, Math.max(6, u * 0.034), 'Mono', `${u * 0.004}px`); ctx.fillText(p.name.toUpperCase(), 0, -u * 0.745); }
    if (p.num != null) { font(800, u * 0.12, 'Inter', '0px'); ctx.fillText(String(p.num), 0, -u * 0.6); }
  }
  ctx.fillStyle = skin; ctx.fillRect(-u * 0.025, -u * 0.87, u * 0.05, u * 0.06);
  ctx.beginPath(); ctx.arc(0, -u * 0.91, u * 0.062, 0, 7); ctx.fill();
  ctx.fillStyle = hair; ctx.beginPath(); ctx.arc(0, -u * 0.918, u * 0.06, Math.PI * 0.92, Math.PI * 2.08); ctx.fill();
  if (armsUp && p.trophy) drawTrophy(0, -u * 1.2, u);
  ctx.restore();
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
  list.sort((a, b) => b.q[2] - a.q[2]);
  for (const o of list) {
    const s = proj(o.q);
    const alpha = o.p.enter === 'fade' ? eOut(pr(lt, o.p.delay || 0, 0.5)) : 1;
    drawPlayer(s[0], s[1], FOC * 1.85 / o.q[2], o.p, lt, o.walk, alpha);
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
    if (x + gap + w > HL.maxW && lines[lines.length - 1].length) { lines.push([]); x = 0; }
    else x += gap;
    lines[lines.length - 1].push({ ...tk, x });
    x += w;
  }
  return lines;
}
function drawHeadline(text, inT, outT) {
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
      ctx.fillStyle = tk.acc ? S.accent : '#f4f2ec';
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
    const n = c.items.length, colW = 280, bw = colW * n + 60, bh = 330;
    cardBox(cx, cy, bw, bh, c.label);
    c.items.forEach((it, i) => {
      const x = cx - (colW * n) / 2 + colW * (i + 0.5);
      const v = countVal(it, ct, 0.35 + i * 0.3, 1.2);
      font(800, 140, 'Inter', '-3px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
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
    document.fonts.load('500 24px Mono'), document.fonts.load('700 24px Mono')]);
  let t = 0, prev = null;
  S.beats = spec.beats.map((b, i) => {
    const B = { ...b };
    B.dur = b.duration || Math.max(2.4, wordsOf(b.vo) / 2.7 + 0.7);
    if (i === spec.beats.length - 1) B.dur += spec.tail != null ? spec.tail : 0.8;
    B.start = t; t += B.dur;
    B.sceneObj = b.scene || (prev ? prev.sceneObj : { type: 'stadium' });
    B.world = B.sceneObj.type === 'stadium' ? buildWorld(B.sceneObj) : null;
    if (b.players === undefined && prev) { B.playersArr = prev.playersArr; B.playersStart = prev.playersStart; }
    else { B.playersArr = b.players || []; B.playersStart = B.start; }
    B.kickerText = b.kicker !== undefined ? b.kicker : (prev ? prev.kickerText : '');
    if (b.card === 'same' && prev) { B.cardObj = prev.cardObj; B.cardStart = prev.cardStart; }
    else { B.cardObj = b.card || null; B.cardStart = B.start + (b.card && b.card.delay != null ? b.card.delay : 0.3); }
    if (b.confetti) { B.confettiStart = prev && prev.confetti ? prev.confettiStart : B.start; }
    prev = B;
    return B;
  });
  S.dur = t;
  S.events = [];
  S.beats.forEach((b, i) => {
    if (i > 0 && (b.cut || b.headline !== S.beats[i - 1].headline)) S.events.push({ t: Math.max(0, b.start - 0.12), type: b.cut ? 'whoosh' : 'swish' });
    if (b.cardObj && (i === 0 || b.cardObj !== S.beats[i - 1].cardObj)) {
      for (const e of cardEvents(b.cardObj)) S.events.push({ t: b.cardStart + e.t, type: e.type });
    }
    if (b.confetti && !(i > 0 && S.beats[i - 1].confetti)) S.events.push({ t: b.start, type: 'crowd' });
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
function renderAt(t) {
  const i = beatIdx(t), b = S.beats[i], lt = t - b.start, next = S.beats[i + 1];
  const scene = b.sceneObj;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  const c = camInBeat(i, lt), cam = mkCam(c.pos, c.tgt);
  if (scene.type === 'studio') drawStudio(t, scene);
  else {
    drawSky(scene);
    drawPitch(cam, scene);
    drawStadium(cam, t, b.world);
  }
  if (scene.type !== 'studio') drawPlayers(cam, t - b.playersStart, b.playersArr);
  if (b.confetti) drawConfetti(t - b.confettiStart, b.confettiColors || [S.accent, '#ffffff', ...(scene.crowd || [])], 11);

  // legibility overlays
  let g = ctx.createLinearGradient(0, 0, 0, H * 0.4);
  g.addColorStop(0, 'rgba(8,10,15,0.92)'); g.addColorStop(0.6, 'rgba(8,10,15,0.55)'); g.addColorStop(1, 'rgba(8,10,15,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * 0.4);
  g = ctx.createRadialGradient(W / 2, H * 0.55, W * 0.45, W / 2, H * 0.55, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

  // card
  if (b.cardObj) {
    const ct = t - b.cardStart;
    if (ct >= 0) {
      const leaving = !next || next.cardObj !== b.cardObj;
      const outA = leaving && next ? 1 - pr(lt, b.dur - 0.25, 0.25) : 1;
      const a = eOut(pr(ct, 0, 0.45)) * outA;
      ctx.save();
      ctx.globalAlpha = a;
      ctx.translate(0, (1 - eOut(pr(ct, 0, 0.45))) * 70);
      CARDS[b.cardObj.type](b.cardObj, ct, W / 2, cardY(b.cardObj));
      ctx.restore();
    }
  }

  // header
  drawBrand();
  const prevB = S.beats[i - 1];
  const kChanged = !prevB || prevB.kickerText !== b.kickerText;
  const kOut = next && next.kickerText !== b.kickerText ? pr(lt, b.dur - 0.22, 0.22) : 0;
  drawKicker(b.kickerText, (kChanged ? eOut(pr(lt, 0, 0.4)) : 1) * (1 - kOut));
  const hChanged = !prevB || prevB.headline !== b.headline;
  const hOut = next && next.headline !== b.headline ? lt - (b.dur - 0.22) : null;
  if (b.headline) drawHeadline(b.headline, hChanged ? lt : 99, hOut != null && hOut >= 0 ? hOut : null);

  ctx.restore();
}

window.frame = function (t, type = 'jpeg') {
  renderAt(t);
  return type === 'png' ? cv.toDataURL('image/png').split(',')[1] : cv.toDataURL('image/jpeg', 0.93).split(',')[1];
};
