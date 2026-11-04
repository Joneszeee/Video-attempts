// ---------- toy / clay style (one-off, opt-in) ----------
// Spec-level "style": "toy" switches the look: chunky big-head toy figures, tilt-shift miniature dioramas, warm clay
// palette, hand-drawn marker text on masking-tape strips. Scenes: {"type": "toy", "set": "pitch" | "room"}.
// Nothing here runs unless a video asks for it, so every other video renders exactly as before.

const TOY = {
  wall: ['#f3dcbc', '#d9a679'], felt: '#64b25e', felt2: '#6fbc68', chalk: '#f7f1e2', wood: '#c48a52', wood2: '#a8713f',
  ink: '#1d1c22', tape: 'rgba(246,234,200,0.94)',
};
function toyOn() { return S.spec && S.spec.style === 'toy'; }

// a polygon in world space, clipped at the near plane and projected
function toyPoly(cam, pts, fill, stroke, lw) {
  const q = clipNear(pts.map(p => toCam(cam, p)));
  if (q.length < 3) return false;
  ctx.beginPath();
  q.forEach((v, i) => { const s = proj(v); i ? ctx.lineTo(s[0], s[1]) : ctx.moveTo(s[0], s[1]); });
  ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw || 2; ctx.stroke(); }
  return true;
}
function toyLine(cam, pts, w, col) {   // a chalk line on the felt, width in metres so it shrinks with distance
  ctx.save(); ctx.strokeStyle = col || TOY.chalk; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (let i = 1; i < pts.length; i++) {
    const a = toCam(cam, pts[i - 1]), b = toCam(cam, pts[i]);
    if (a[2] < NEAR && b[2] < NEAR) continue;
    const q = clipNear([a, b]); if (q.length < 2) continue;
    const pa = proj(q[0]), pb = proj(q[1]), z = Math.max(NEAR, (q[0][2] + q[1][2]) / 2);
    ctx.lineWidth = Math.max(1, FOC * w / z); ctx.beginPath(); ctx.moveTo(pa[0], pa[1]); ctx.lineTo(pb[0], pb[1]); ctx.stroke();
  }
  ctx.restore();
}
function toyCircle(cam, cx, cz, r, a0, a1, w) { const pts = []; for (let i = 0; i <= 40; i++) { const a = lerp(a0, a1, i / 40); pts.push([cx + Math.cos(a) * r, 0.02, cz + Math.sin(a) * r]); } toyLine(cam, pts, w); }

// warm room behind the diorama: soft wall gradient and out-of-focus bokeh lights
function toyBackdrop(t, seed) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, TOY.wall[0]); g.addColorStop(1, TOY.wall[1]);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const R = rng(seed || 5);
  for (let i = 0; i < 26; i++) {
    const x = R() * W, y = R() * H * 0.55, r = 30 + R() * 90, a = 0.08 + R() * 0.12;
    const bg = ctx.createRadialGradient(x, y, 0, x, y, r); bg.addColorStop(0, `rgba(255,236,190,${a})`); bg.addColorStop(1, 'rgba(255,236,190,0)');
    ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(x + Math.sin(t * 0.3 + i) * 6, y, r, 0, 7); ctx.fill();
  }
}

function toyStands(cam, scene, t) {
  const crowd = scene.crowd || ['#d6283b', '#ffffff', '#1d1c22'], R = rng(scene.seed || 3), items = [];
  // four sloped stands: [inner edge, outer edge, along-axis], built as slopes rising away from the pitch
  const defs = [
    { a: [[40, 0, -50], [40, 0, 50], [54, 10, 50], [54, 10, -50]], side: 'x', s: 1 },
    { a: [[-40, 0, 50], [-40, 0, -50], [-54, 10, -50], [-54, 10, 50]], side: 'x', s: -1 },
    { a: [[-34, 0, 60], [34, 0, 60], [34, 10, 72], [-34, 10, 72]], side: 'z', s: 1 },
    { a: [[34, 0, -60], [-34, 0, -60], [-34, 10, -72], [34, 10, -72]], side: 'z', s: -1 },
  ];
  for (const d of defs) {
    const c = d.a.reduce((m, p) => [m[0] + p[0] / 4, m[1] + p[1] / 4, m[2] + p[2] / 4], [0, 0, 0]);
    items.push({ z: toCam(cam, c)[2], draw: () => {
      toyPoly(cam, d.a, '#e9e1d2');   // clay grey stand
      toyPoly(cam, [d.a[2], d.a[3], [d.a[3][0], -1, d.a[3][2]], [d.a[2][0], -1, d.a[2][2]]], '#d6cbb7');
      // beads of crowd on the slope
      for (let row = 0; row < 6; row++) for (let k = 0; k <= 48; k++) {
        const u = (row + 0.5) / 6, v = k / 48;
        const p0 = lerp3(d.a[0], d.a[1], v), p1 = lerp3(d.a[3], d.a[2], v), p = lerp3(p0, p1, u);
        const q = toCam(cam, [p[0], p[1] + 0.7 + 0.15 * Math.sin(t * 6 + k + row), p[2]]); if (q[2] < NEAR) continue;
        const s = proj(q), r = FOC * 0.55 / q[2]; if (r < 0.6) continue;
        const col = crowd[(k * 7 + row * 3 + Math.floor(webHash(k, row) * 9)) % crowd.length];
        const bg = ctx.createRadialGradient(s[0] - r * 0.35, s[1] - r * 0.35, r * 0.1, s[0], s[1], r);
        bg.addColorStop(0, shadeHex(col, 0.35)); bg.addColorStop(1, shadeHex(col, -0.25));
        ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(s[0], s[1], r, 0, 7); ctx.fill();
      }
    } });
  }
  return items;
}
function shadeHex(c, k) { return shade(c, k); }

function toyGoal(cam, z) {
  const s = Math.sign(z), d = 2.4;
  const post = (a, b) => toyLine(cam, [a, b], 0.28, '#fbfbf7');
  ctx.save(); ctx.globalAlpha = 0.35; toyPoly(cam, [[-3.66, 0, z], [3.66, 0, z], [3.66, 0, z + s * d], [-3.66, 0, z + s * d]], 'rgba(255,255,255,0.25)'); ctx.restore();
  for (let i = 0; i <= 8; i++) toyLine(cam, [[-3.66 + i * 0.915, 2.44, z], [-3.66 + i * 0.915, 0, z + s * d]], 0.04, 'rgba(255,255,255,0.55)');
  post([-3.66, 0, z], [-3.66, 2.44, z]); post([3.66, 0, z], [3.66, 2.44, z]); post([-3.66, 2.44, z], [3.66, 2.44, z]);
}

function drawToyPitch(cam, scene, t) {
  toyBackdrop(t, scene.seed);
  // the table the model sits on
  toyPoly(cam, [[-260, -1, -260], [260, -1, -260], [260, -1, 260], [-260, -1, 260]], TOY.wood);
  for (let x = -250; x <= 250; x += 9) toyLine(cam, [[x, -0.99, -250], [x, -0.99, 250]], 0.25, 'rgba(120,70,30,0.25)');
  const items = toyStands(cam, scene, t);
  const B = [[-38, 0, -56], [38, 0, -56], [38, 0, 56], [-38, 0, 56]];
  items.push({ z: toCam(cam, [0, 0, 0])[2] + 0.01, draw: () => {
    // board sides (wood), then the felt top with mown stripes and chalk lines
    const sides = [[B[0], B[1]], [B[1], B[2]], [B[2], B[3]], [B[3], B[0]]];
    for (const [a, b] of sides) toyPoly(cam, [a, b, [b[0], -1, b[2]], [a[0], -1, a[2]]], TOY.wood2);
    toyPoly(cam, B, TOY.felt);
    for (let z = -56, i = 0; z < 56; z += 7, i++) if (i % 2) toyPoly(cam, [[-38, 0.005, z], [38, 0.005, z], [38, 0.005, z + 7], [-38, 0.005, z + 7]], TOY.felt2);
    const L = 0.22;
    toyLine(cam, [[-34, 0.02, -52.5], [34, 0.02, -52.5], [34, 0.02, 52.5], [-34, 0.02, 52.5], [-34, 0.02, -52.5]], L);
    toyLine(cam, [[-34, 0.02, 0], [34, 0.02, 0]], L);
    toyCircle(cam, 0, 0, 9.15, 0, Math.PI * 2, L);
    for (const s of [-1, 1]) {
      const e = s * 52.5, bx = e - s * 16.5, sx = e - s * 5.5;
      toyLine(cam, [[-20.16, 0.02, e], [-20.16, 0.02, bx], [20.16, 0.02, bx], [20.16, 0.02, e]], L);
      toyLine(cam, [[-9.16, 0.02, e], [-9.16, 0.02, sx], [9.16, 0.02, sx], [9.16, 0.02, e]], L);
      toyCircle(cam, 0, e - s * 11, 9.15, s > 0 ? Math.PI + 0.93 : 0.93, s > 0 ? 2 * Math.PI - 0.93 : Math.PI - 0.93, L);
    }
  } });
  items.sort((a, b) => b.z - a.z);
  for (const it of items) it.draw();
  toyGoal(cam, 52.5); toyGoal(cam, -52.5);
}

function drawToyRoom(t, scene) {
  toyBackdrop(t, scene.seed || 8);
  // a soft window light falling across the wall, a skirting board and a wooden floor
  ctx.save(); ctx.globalAlpha = 0.18; ctx.fillStyle = '#fff6dc';
  ctx.beginPath(); ctx.moveTo(W * 0.62, 0); ctx.lineTo(W, 0); ctx.lineTo(W * 0.55, H * 0.8); ctx.lineTo(W * 0.15, H * 0.8); ctx.fill(); ctx.restore();
  const fy = H * 0.8;
  ctx.fillStyle = '#e8d5bb'; ctx.fillRect(0, fy - 26, W, 26);
  const g = ctx.createLinearGradient(0, fy, 0, H); g.addColorStop(0, '#b97a45'); g.addColorStop(1, '#8a5530');
  ctx.fillStyle = g; ctx.fillRect(0, fy, W, H - fy);
  ctx.strokeStyle = 'rgba(70,35,10,0.25)'; ctx.lineWidth = 3;
  for (let i = -6; i <= 6; i++) { ctx.beginPath(); ctx.moveTo(W / 2 + i * 40, fy); ctx.lineTo(W / 2 + i * 260, H); ctx.stroke(); }
}

// tilt-shift: blur the top and bottom of the frame so the scene reads as a miniature, then a warm grade
const toyTmp = document.createElement('canvas'); toyTmp.width = W / 2; toyTmp.height = H / 2;
const toyTx = toyTmp.getContext('2d');
function toyTiltShift(amount) {
  const a = amount == null ? 1 : amount; if (a <= 0) return;
  toyTx.globalCompositeOperation = 'source-over'; toyTx.clearRect(0, 0, W / 2, H / 2);
  toyTx.filter = `blur(${4 * a}px)`; toyTx.drawImage(cv, 0, 0, W / 2, H / 2); toyTx.filter = 'none';
  const m = toyTx.createLinearGradient(0, 0, 0, H / 2);
  m.addColorStop(0, 'rgba(0,0,0,1)'); m.addColorStop(0.3, 'rgba(0,0,0,0)'); m.addColorStop(0.72, 'rgba(0,0,0,0)'); m.addColorStop(1, 'rgba(0,0,0,1)');
  toyTx.globalCompositeOperation = 'destination-in'; toyTx.fillStyle = m; toyTx.fillRect(0, 0, W / 2, H / 2);
  toyTx.globalCompositeOperation = 'source-over';
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(toyTmp, 0, 0, W, H);
  const v = ctx.createRadialGradient(W / 2, H * 0.55, H * 0.25, W / 2, H * 0.55, H * 0.75);
  v.addColorStop(0, 'rgba(255,214,150,0)'); v.addColorStop(1, 'rgba(120,60,20,0.28)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  ctx.restore();
}

function drawToyScene(ts, b, i, lts) {
  const scene = b.sceneObj;
  if (scene.set === 'room') { S.cam = null; const z = 1 + 0.035 * lts; ctx.save(); ctx.translate(W / 2, H * 0.6); ctx.scale(z, z); ctx.translate(-W / 2, -H * 0.6); drawToyRoom(ts, scene); ctx.restore(); }
  else {
    const c = camInBeat(i, lts), cam = mkCam(c.pos, c.tgt);
    S.cam = cam;
    drawToyPitch(cam, scene, ts);
    drawPlayers(cam, ts - b.playersStart, b.playersArr);
  }
  toyTiltShift(scene.tilt);
}

// ---------- the big-head toy figure ----------
function toyCapsule(x1, y1, x2, y2, w, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineWidth = w;
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.lineWidth = w * 0.35;
  ctx.beginPath(); ctx.moveTo(x1 - w * 0.15, y1 - w * 0.1); ctx.lineTo(x2 - w * 0.15, y2 - w * 0.1); ctx.stroke();
  ctx.restore();
}
function toyBlob(x, y, r, col) {   // a lit clay sphere
  const g = ctx.createRadialGradient(x - r * 0.38, y - r * 0.42, r * 0.08, x, y, r * 1.05);
  g.addColorStop(0, shade(col, 0.3)); g.addColorStop(0.55, col); g.addColorStop(1, shade(col, -0.32));
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
}
function drawToyHair(hx, hy, r, p, front) {
  const col = p.hair || '#2a1a10', st = p.hairStyle || 'short';
  if (st === 'bald') return;
  ctx.save(); ctx.beginPath(); ctx.arc(hx, hy, r * 1.02, 0, 7); ctx.clip();
  const g = ctx.createRadialGradient(hx - r * 0.3, hy - r * 0.6, r * 0.1, hx, hy - r * 0.2, r * 1.2);
  g.addColorStop(0, shade(col, 0.28)); g.addColorStop(1, shade(col, -0.2)); ctx.fillStyle = g;
  if (!front) { ctx.beginPath(); ctx.ellipse(hx, hy - r * 0.05, r * 1.05, r * (st === 'buzz' ? 0.8 : 0.95), 0, 0, 7); ctx.fill(); }
  else {
    const drop = st === 'long' ? 0.25 : st === 'buzz' ? -0.45 : st === 'curly' ? -0.15 : -0.3;
    ctx.beginPath(); ctx.ellipse(hx, hy - r * 0.55, r * 1.1, r * 0.62, 0, Math.PI, 2 * Math.PI); ctx.lineTo(hx + r * 1.1, hy + r * drop); ctx.lineTo(hx - r * 1.1, hy + r * drop); ctx.fill();
  }
  ctx.restore();
  if (st === 'curly') for (let k = 0; k < 9; k++) { const a = Math.PI + k * Math.PI / 8; toyBlob(hx + Math.cos(a) * r * 0.92, hy + Math.sin(a) * r * 0.92, r * 0.22, col); }
  if (st === 'bun') toyBlob(hx, hy - r * 1.05, r * 0.3, col);
  if (st === 'long' && !front) { ctx.fillStyle = col; rrect(hx - r * 0.95, hy, r * 1.9, r * 0.75, r * 0.3); ctx.fill(); }
}
function toyPose(p, t, walk) {   // arms (angles from straight down, + = outwards), legs swing, body hop/rotation/squash
  const o = { aL: 0.25, aR: 0.25, legL: 0, legR: 0, hop: 0, rot: 0, sq: 0, dx: 0, lean: 0 };
  const seed = (p.x || 0) * 1.7 + (p.z || 0);
  o.sq = 0.015 * Math.sin(t * 2.4 + seed);   // breathing
  const pose = p.pose;
  if (pose === 'arms_up') { o.aL = o.aR = 2.75 + 0.08 * Math.sin(t * 7); }
  else if (pose === 'wings') { o.aL = o.aR = 1.5 + 0.06 * Math.sin(t * 6); o.rot = 0.1 * Math.sin(t * 3); }
  else if (pose === 'fists') { o.aL = o.aR = 2.4 + 0.15 * Math.sin(t * 9); }
  else if (pose === 'keeper') { o.aL = o.aR = 1.0; o.sq = -0.06; }
  else if (pose === 'shake') { o.aR = 1.2 + 0.1 * Math.sin(t * 9); }
  else if (pose === 'point') { o.aR = 2.1; }
  else if (pose === 'think') { o.aR = 2.6; }
  if (walk > 0) {
    const ph = t * 10 + seed;
    o.hop = Math.abs(Math.sin(ph)) * 0.06 * walk; o.legL = Math.sin(ph) * 0.5 * walk; o.legR = -o.legL;
    if (!pose) { o.aL = 0.35 + Math.sin(ph) * 0.6 * walk; o.aR = 0.35 - Math.sin(ph) * 0.6 * walk; }
    o.sq += -0.05 * Math.cos(ph * 2) * walk;
  }
  const d = p.actionDelay != null ? p.actionDelay : 0, act = p.action;
  const celebrate = act === 'celebrate' || (p.after === 'celebrate' && t > d + (p.actionDur || 0.9));
  if (celebrate) { const ph = t * 6 + seed; o.hop = Math.abs(Math.sin(ph)) * 0.16; o.aL = o.aR = 2.6 + 0.2 * Math.sin(ph); o.sq = -0.08 * Math.cos(ph * 2); }
  if (act === 'kick' && t >= d && t < d + (p.actionDur || 0.9)) {
    const k = (t - d) / (p.actionDur || 0.9), foot = p.foot === 'left' ? -1 : 1;
    const swing = k < 0.42 ? -1.1 * eOut(k / 0.42) : lerp(-1.1, 1.4, eOut((k - 0.42) / 0.3)) * (k > 0.85 ? 1 - (k - 0.85) / 0.15 * 0.6 : 1);
    if (foot > 0) o.legR = swing; else o.legL = swing;
    o.lean = -0.18 * Math.sin(Math.PI * k); o.aL = 0.9; o.aR = 0.9;
  }
  if (act === 'dive' && t >= d) {
    const k = eOut(Math.min(1, (t - d) / (p.actionDur || 0.9))), dir = p.dir || 1;
    o.rot = dir * 1.35 * k; o.dx = dir * 0.55 * k; o.hop = 0.25 * Math.sin(Math.PI * Math.min(1, k * 1.2)); o.aL = o.aR = 2.7;
  }
  if (act === 'slide' && t >= d) {
    const k = Math.min(1, (t - d) / (p.actionDur || 1.1)), dir = p.dir || 1;
    o.rot = -dir * 1.0 * eOut(Math.min(1, k * 2)) * (k > 0.8 ? 1 - (k - 0.8) / 0.2 : 1); o.legR = dir * 1.0; o.aL = 1.2;
  }
  if (p.hops) for (const h of p.hops) { const k = pr(t, h.t, h.dur || 0.45); if (k > 0 && k < 1) o.hop += (h.height || 0.16) * Math.sin(Math.PI * k); }
  return o;
}
function drawToyFigure(x, y, u, p, t, walk, alpha) {
  if (u < 3) return;
  // drop onto the set with a bounce when it appears
  let drop = 0, dsc = 1;
  if (p.delay != null && p.enter !== 'walk' && !p.path) { const k = pr(t, p.delay, 0.45); if (k <= 0) return; drop = (1 - eOut(k)) * u * 0.9; dsc = 0.85 + 0.15 * eBack(k); }
  if (p.ghost) alpha *= 0.4;
  const k = p.kit || {}, skin = p.skin || '#e3b38f', shirt = k.shirt || '#d6283b', shorts = k.shorts || '#ffffff', socks = k.socks || shirt, txt = k.text || '#ffffff';
  const front = !!p.front, o = toyPose(p, t, walk), suit = p.outfit === 'suit', sc = u * dsc;
  ctx.save(); ctx.globalAlpha *= alpha;
  // contact shadow stays on the ground
  ctx.fillStyle = `rgba(40,20,5,${0.35 / (1 + o.hop * 6)})`; ctx.beginPath(); ctx.ellipse(x + o.dx * sc, y, sc * 0.22, sc * 0.05, 0, 0, 7); ctx.fill();
  ctx.translate(x + o.dx * sc, y - o.hop * sc - drop); ctx.rotate(o.rot); ctx.scale(dsc * (1 - o.sq), dsc * (1 + o.sq)); ctx.rotate(o.lean);
  const s = u;
  // legs + boots
  const leg = (side, ang) => {
    const hx = side * 0.075 * s, hy = -0.22 * s, fx = hx + Math.sin(ang) * 0.2 * s * (front ? -1 : 1) * 0.6, fy = hy + Math.cos(ang) * 0.2 * s;
    toyCapsule(hx, hy, fx, fy - 0.02 * s, 0.1 * s, suit ? (p.suitColor || '#2a3140') : socks);
    toyBlob(fx, fy - 0.01 * s, 0.055 * s, suit ? '#151515' : '#1d1c22');
  };
  leg(-1, o.legL); leg(1, o.legR);
  // shorts
  ctx.fillStyle = suit ? (p.suitColor || '#2a3140') : shorts; rrect(-0.15 * s, -0.36 * s, 0.3 * s, 0.17 * s, 0.06 * s); ctx.fill();
  // arms behind the body when seen from behind are drawn after the torso anyway (they hang outside it)
  const arm = (side, ang) => {
    const sx = side * 0.17 * s, sy = -0.6 * s, a = side * ang, ex = sx + Math.sin(a) * 0.22 * s, ey = sy + Math.cos(a) * 0.22 * s;
    toyCapsule(sx, sy, ex, ey, 0.085 * s, suit ? (p.suitColor || '#2a3140') : shirt);
    toyBlob(ex, ey, 0.05 * s, skin);
  };
  // torso
  const tw = 0.37 * s, tt = -0.66 * s, th = 0.34 * s;
  ctx.save(); rrect(-tw / 2, tt, tw, th, 0.11 * s); ctx.clip();
  ctx.fillStyle = suit ? (p.suitColor || '#2a3140') : shirt; ctx.fillRect(-tw / 2, tt, tw, th);
  if (!suit && k.stripes) { ctx.fillStyle = k.stripes[1]; for (let i = 0; i < 5; i++) if (i % 2) ctx.fillRect(-tw / 2 + i * tw / 5, tt, tw / 5, th); }
  if (!suit && k.hoops) { ctx.fillStyle = k.hoops[1]; for (let i = 0; i < 5; i++) if (i % 2) ctx.fillRect(-tw / 2, tt + i * th / 5, tw, th / 5); }
  if (suit && front) { ctx.fillStyle = '#f4f4f2'; ctx.beginPath(); ctx.moveTo(-0.06 * s, tt); ctx.lineTo(0.06 * s, tt); ctx.lineTo(0, tt + 0.16 * s); ctx.fill();
    ctx.fillStyle = p.tie || '#7a1420'; ctx.fillRect(-0.012 * s, tt + 0.01 * s, 0.024 * s, 0.13 * s); }
  const sg = ctx.createLinearGradient(-tw / 2, tt, tw / 2, tt + th); sg.addColorStop(0, 'rgba(255,255,255,0.22)'); sg.addColorStop(0.5, 'rgba(255,255,255,0)'); sg.addColorStop(1, 'rgba(0,0,0,0.22)');
  ctx.fillStyle = sg; ctx.fillRect(-tw / 2, tt, tw, th);
  ctx.restore();
  if (!suit && p.num != null && (!front || p.chest)) {
    font(900, (front ? 0.11 : 0.17) * s, 'Inter'); ctx.fillStyle = txt; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(String(p.num), front ? 0.08 * s : 0, tt + th * (front ? 0.35 : 0.55));
  }
  arm(-1, o.aL); arm(1, o.aR);
  // big head
  const hr = 0.22 * s, hx = 0, hy = tt - hr * 0.82;
  toyBlob(hx - hr * 0.95, hy + hr * 0.1, hr * 0.2, skin); toyBlob(hx + hr * 0.95, hy + hr * 0.1, hr * 0.2, skin);   // ears
  toyBlob(hx, hy, hr, skin);
  if (front) {
    if (p.beard) { ctx.save(); ctx.beginPath(); ctx.arc(hx, hy, hr, 0, 7); ctx.clip(); ctx.fillStyle = p.beardColor || p.hair || '#2a1a10'; ctx.globalAlpha *= 0.92;
      ctx.beginPath(); ctx.ellipse(hx, hy + hr * 0.62, hr * 0.85, hr * 0.55, 0, 0, 7); ctx.fill(); ctx.restore(); }
    ctx.fillStyle = '#1d1c22';
    const blink = (Math.sin(t * 1.3 + (p.x || 0)) > 0.985) ? 0.15 : 1;
    ctx.beginPath(); ctx.ellipse(hx - hr * 0.33, hy + hr * 0.02, hr * 0.09, hr * 0.13 * blink, 0, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.ellipse(hx + hr * 0.33, hy + hr * 0.02, hr * 0.09, hr * 0.13 * blink, 0, 0, 7); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.8)'; ctx.beginPath(); ctx.arc(hx - hr * 0.36, hy - hr * 0.04, hr * 0.03, 0, 7); ctx.arc(hx + hr * 0.3, hy - hr * 0.04, hr * 0.03, 0, 7); ctx.fill();
    ctx.fillStyle = 'rgba(230,90,80,0.25)'; ctx.beginPath(); ctx.arc(hx - hr * 0.55, hy + hr * 0.3, hr * 0.13, 0, 7); ctx.arc(hx + hr * 0.55, hy + hr * 0.3, hr * 0.13, 0, 7); ctx.fill();
    ctx.strokeStyle = '#5a2a20'; ctx.lineWidth = Math.max(1, hr * 0.06); ctx.lineCap = 'round';
    const mood = p.mood || (o.aL > 2 ? 'joy' : 'calm');
    ctx.beginPath();
    if (mood === 'joy') { ctx.fillStyle = '#5a2a20'; ctx.arc(hx, hy + hr * 0.38, hr * 0.17, 0, Math.PI); ctx.fill(); }
    else if (mood === 'cross') { ctx.moveTo(hx - hr * 0.16, hy + hr * 0.48); ctx.quadraticCurveTo(hx, hy + hr * 0.36, hx + hr * 0.16, hy + hr * 0.48); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(hx - hr * 0.5, hy - hr * 0.22); ctx.lineTo(hx - hr * 0.18, hy - hr * 0.12); ctx.moveTo(hx + hr * 0.5, hy - hr * 0.22); ctx.lineTo(hx + hr * 0.18, hy - hr * 0.12); ctx.stroke(); }
    else { ctx.moveTo(hx - hr * 0.16, hy + hr * 0.4); ctx.quadraticCurveTo(hx, hy + hr * 0.52, hx + hr * 0.16, hy + hr * 0.4); ctx.stroke(); }
  }
  drawToyHair(hx, hy, hr, p, front);
  ctx.restore();
  // a masking-tape name label above the head
  if (p.label && t >= (p.labelDelay != null ? p.labelDelay : (p.delay || 0) + 0.3)) {
    const lk = eBack(pr(t, p.labelDelay != null ? p.labelDelay : (p.delay || 0) + 0.3, 0.3));
    toyTape(p.label, x + o.dx * u, y - u * 1.18 - o.hop * u, Math.max(34, Math.min(46, u * 0.14)), lk, (p.x || 0) * 0.02);
  }
}

// Typography for the toy style (user: "simple, minimalistic, Apple-like, modern"): Inter with tight tracking,
// frosted rounded pills instead of tape, no rotation or hand lettering.
function tf(weight, size) { font(weight, size, 'Inter', (-size * 0.025).toFixed(1) + 'px'); }
function toyPill(x, y, w, h, alpha) {   // frosted glass pill
  ctx.save(); ctx.shadowColor = 'rgba(40,20,5,0.18)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 6;
  ctx.fillStyle = `rgba(255,255,255,${alpha == null ? 0.82 : alpha})`; rrect(x, y, w, h, h / 2); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 1.5; rrect(x + 0.75, y + 0.75, w - 1.5, h - 1.5, h / 2); ctx.stroke();
  ctx.restore();
}
function toyTape(text, cx, cy, size, k, rot, col) {   // name label: a small frosted pill
  if (k <= 0) return;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k);
  tf(600, size * 0.8); const tw = ctx.measureText(text).width, h = size * 1.25, w = tw + size * 1.0;
  toyPill(-w / 2, -h / 2, w, h);
  ctx.fillStyle = col || TOY.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 0, size * 0.03);
  ctx.restore();
}

// ---------- toy header: clean sans, white on the scene ----------
function drawToyHeadline(text, inT, outT, accent, wordT) {
  const size = 76; tf(700, size); const sp = ctx.measureText(' ').width, lines = [[]]; let x = 0;
  for (const tk of parseHL(text)) {
    const w = ctx.measureText(tk.w).width, gap = tk.space ? sp : 0;
    if (tk.space && x + gap + w > 900 && lines[lines.length - 1].length) { lines.push([]); x = 0; } else x += gap;
    lines[lines.length - 1].push({ ...tk, x, ww: w }); x += w;
  }
  const n = lines.reduce((m, l) => m + l.length, 0); let idx = 0;
  lines.forEach((line, li) => {
    const a = eOut(pr(inT, 0.05 + li * 0.08, 0.45)), o = outT != null ? pr(outT, 0, 0.22) : 0, y = HL.y + li * 88 + (1 - a) * 20 - o * 10;
    ctx.save(); ctx.globalAlpha = a * (1 - o); tf(700, size); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    ctx.shadowColor = 'rgba(30,15,5,0.35)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 3;
    for (const tk of line) {
      let kk = 1;
      if (wordT != null) { kk = pr(wordT, 0.2 + idx * (1.2 / Math.max(1, n)), 0.3); idx++; if (kk <= 0) continue; }
      ctx.save(); ctx.globalAlpha *= eOut(kk);
      ctx.fillStyle = tk.acc ? (accent || S.accent) : '#ffffff'; ctx.fillText(tk.w, HL.x + tk.x, y + (1 - eOut(kk)) * 18); ctx.restore();
    }
    ctx.restore();
  });
}
function drawToyKicker(text, a) {
  if (!text) return;
  ctx.save(); ctx.globalAlpha = a * 0.75; font(600, 24, 'Inter', '3px'); ctx.fillStyle = '#ffffff'; ctx.textAlign = 'left';
  ctx.fillText(text.toUpperCase(), HL.x, HL.y - 96); ctx.restore();
}
function drawToyBrand() {   // the theo6k shirt in a frosted pill
  const x = HL.x, y = 220, name = S.spec.brand || 'theo6k';
  ctx.save(); tf(700, 34); const tw = ctx.measureText(name).width;
  toyPill(x - 12, y - 50, tw + 104, 66, 0.86);
  drawBrandShirt(x + 30, y - 17, 50);
  ctx.fillStyle = TOY.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; tf(700, 34); ctx.fillText(name, x + 66, y - 4);
  ctx.restore();
}
function drawToyOutro(ot) {
  const k = ease(pr(ot, 0, 0.6));
  bgx.clearRect(0, 0, W / Q, H / Q); bgx.filter = 'blur(3px)'; bgx.drawImage(cv, 0, 0, W / Q, H / Q); bgx.filter = 'none';
  ctx.save(); ctx.globalAlpha = k; ctx.drawImage(bgc, 0, 0, W, H); ctx.globalAlpha = 1;
  ctx.fillStyle = `rgba(90,50,20,${0.35 * k})`; ctx.fillRect(0, 0, W, H);
  const a = eBack(pr(ot, 0.35, 0.5)), y = H * 0.47;
  if (a > 0) {   // a clean frosted card
    ctx.translate(W / 2, y + (1 - a) * 60); ctx.globalAlpha = Math.min(1, a);
    ctx.shadowColor = 'rgba(40,20,5,0.3)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
    ctx.fillStyle = 'rgba(255,255,255,0.88)'; rrect(-300, -170, 600, 300, 44); ctx.fill(); ctx.shadowColor = 'transparent';
    drawBrandShirt(0, -86, 96);
    tf(700, 64); ctx.fillStyle = TOY.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(S.spec.brand || 'theo6k', 0, 22);
    tf(500, 28); ctx.fillStyle = '#6b6f78'; ctx.fillText(S.spec.outroText || 'Follow for more football stories', 0, 76);
  }
  ctx.restore();
}

// ---------- toy cards ----------
function toyDrift(ct, cx, cy, amt) { const z = 1 + (amt || 0.03) * ct; ctx.translate(cx, cy + Math.sin(ct * 1.3) * 8); ctx.rotate(Math.sin(ct * 0.9) * 0.006); ctx.scale(z, z); ctx.translate(-cx, -cy); }
// Whiteboard: marker lines write themselves on (lines: [{text, at|t, y (0–1), size, color, circle: {at|t, color}, underline}]).
CARDS.whiteboard = function (c, ct, cx, cy) {
  const w = c.w || 920, h = c.h || 820, a = eBack(pr(ct, 0, 0.45));
  if (a <= 0) return;
  ctx.save(); ctx.translate(cx, cy + (1 - a) * 120); ctx.rotate(c.tilt != null ? c.tilt : -0.01);
  const z = 1 + 0.02 * ct; ctx.scale(z, z);
  ctx.shadowColor = 'rgba(60,30,10,0.35)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 14;
  const fg = ctx.createLinearGradient(0, -h / 2, 0, h / 2); fg.addColorStop(0, '#e9ecef'); fg.addColorStop(1, '#b8bec6');
  ctx.fillStyle = fg; rrect(-w / 2 - 18, -h / 2 - 18, w + 36, h + 36, 22); ctx.fill(); ctx.shadowColor = 'transparent';
  const bg = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2); bg.addColorStop(0, '#ffffff'); bg.addColorStop(1, '#eef1f4');
  ctx.fillStyle = bg; rrect(-w / 2, -h / 2, w, h, 10); ctx.fill();
  ctx.fillStyle = 'rgba(160,170,180,0.08)'; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.ellipse(-w / 3 + i * 160, -h / 4 + (i % 2) * 200, 160, 50, 0.3, 0, 7); ctx.fill(); }   // old wipe marks
  ctx.fillStyle = '#c9ced4'; rrect(-w * 0.35, h / 2 + 14, w * 0.7, 26, 8); ctx.fill();   // tray and markers
  toyCapsule(-w * 0.2, h / 2 + 20, -w * 0.05, h / 2 + 20, 18, '#1d1c22'); toyCapsule(w * 0.02, h / 2 + 20, w * 0.17, h / 2 + 20, 18, '#d6283b');
  for (const L of c.lines || []) {
    const t0 = L.t || 0; if (ct < t0) continue;
    const size = L.size || 72, n = L.text.length, shown = Math.min(n, Math.floor((ct - t0) / (L.speed || 0.045)) + 1);
    tf(L.weight || 700, size); ctx.fillStyle = L.color || TOY.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const y = -h / 2 + (L.y != null ? L.y : 0.5) * h, full = ctx.measureText(L.text).width;
    ctx.textAlign = 'left'; ctx.fillText(L.text.slice(0, shown), -full / 2, y);
    const done = t0 + n * (L.speed || 0.045);
    if (L.underline && ct > done) { const k = pr(ct, done, 0.35); ctx.strokeStyle = L.underline; ctx.lineWidth = 7; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(-full / 2, y + size * 0.55); ctx.lineTo(-full / 2 + full * k, y + size * 0.55 + 6 * Math.sin(k * 3)); ctx.stroke(); }
    if (L.circle) { const t1 = L.circle.t != null ? L.circle.t : done + 0.2, k = pr(ct, t1, 0.5); if (k > 0) {
      ctx.strokeStyle = L.circle.color || '#d6283b'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath();
      for (let i = 0; i <= 60 * k; i++) { const an = -Math.PI / 2 + i / 60 * Math.PI * 2, rx = full / 2 + 44, ry = size * 0.78; ctx.lineTo(Math.cos(an) * rx, y + Math.sin(an) * ry); }
      ctx.stroke(); } }
  }
  ctx.restore();
};
CARDS.whiteboard.noSlide = true;

// Toy league table: 36 slats in three coloured zones; a clay team block sits at its position and can slide (moves: [{to, at|t}]).
// zones: [{from, to, label, color, at|t}], team: {name, pts, color}, pos.
CARDS.toytable = function (c, ct, cx, cy) {
  const w = c.w || 760, h = c.h || 1180, n = c.n || 36, a = eBack(pr(ct, 0, 0.45));
  if (a <= 0) return;
  ctx.save(); toyDrift(ct, cx, cy); ctx.translate(cx + (c.dx || -60), cy + (1 - a) * 140); ctx.rotate(-0.012);
  ctx.shadowColor = 'rgba(60,30,10,0.35)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 14;
  ctx.fillStyle = '#b07a45'; rrect(-w / 2 - 20, -h / 2 - 20, w + 40, h + 40, 24); ctx.fill(); ctx.shadowColor = 'transparent';
  ctx.fillStyle = '#f3e9d6'; rrect(-w / 2, -h / 2, w, h, 12); ctx.fill();
  const rh = (h - 40) / n, top = -h / 2 + 20, zones = c.zones || [];
  const rowY = r => top + (r - 0.5) * rh;
  zones.forEach(z => { ctx.fillStyle = z.color; ctx.fillRect(-w / 2 + 10, top + (z.from - 1) * rh, w - 20, (z.to - z.from + 1) * rh); });
  for (let r = 1; r <= n; r++) {
    const y = rowY(r);
    tf(600, rh * 0.5); ctx.fillStyle = 'rgba(40,30,20,0.5)'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle'; ctx.fillText(String(r), -w / 2 + 52, y + 1);
    ctx.fillStyle = 'rgba(255,255,255,0.55)'; rrect(-w / 2 + 64, y - rh * 0.34, w * 0.5, rh * 0.68, rh * 0.34); ctx.fill();
  }
  // zone labels on the right, appearing on their words
  zones.forEach(z => { const k = eBack(pr(ct, z.t || 0, 0.35)); if (k <= 0 || !z.label) return;
    const y0 = top + (z.from - 1) * rh + 6, y1 = top + z.to * rh - 6, x = w * 0.18;
    ctx.save(); ctx.globalAlpha *= Math.min(1, k); ctx.strokeStyle = TOY.ink; ctx.lineWidth = 5; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x + 18, y0); ctx.lineTo(x + 18, y1); ctx.lineTo(x, y1); ctx.stroke();
    String(z.label).split('\n').forEach((l, i, arr) => { tf(700, 32); ctx.fillStyle = TOY.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillText(l, x + 34, (y0 + y1) / 2 + (i - (arr.length - 1) / 2) * 38); });
    ctx.restore(); });
  // the team block
  if (c.team) {
    let pos = c.pos, from = c.pos, tk = 1;
    for (const m of c.moves || []) { if (ct >= (m.t || 0)) { from = pos; pos = m.to; tk = pr(ct, m.t || 0, 0.9); } }
    const r = lerp(from, pos, eBack(tk)), y = rowY(r), bw = w * 0.62, bh = rh * 1.5, bx = -w / 2 + 40;
    const k2 = eBack(pr(ct, c.teamAt != null ? c.teamAt : 0.3, 0.45));
    if (k2 > 0) {
      ctx.save(); ctx.translate(bx + bw / 2, y); ctx.scale(k2, k2);
      ctx.shadowColor = 'rgba(60,20,10,0.4)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 6;
      const g = ctx.createLinearGradient(0, -bh / 2, 0, bh / 2); g.addColorStop(0, shade(c.team.color || '#d6283b', 0.25)); g.addColorStop(1, shade(c.team.color || '#d6283b', -0.25));
      ctx.shadowColor = `rgba(255,80,80,${0.35 + 0.25 * Math.sin(ct * 4)})`; ctx.shadowBlur = 26;
      ctx.fillStyle = g; rrect(-bw / 2, -bh / 2, bw, bh, bh / 2); ctx.fill(); ctx.shadowColor = 'transparent';
      ctx.fillStyle = 'rgba(255,255,255,0.3)'; rrect(-bw / 2 + 12, -bh / 2 + 5, bw - 24, bh * 0.28, bh * 0.14); ctx.fill();
      font(900, bh * 0.5, 'Inter'); ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(c.team.name, -bw / 2 + 24, 2);
      if (c.team.pts != null) { ctx.textAlign = 'right'; ctx.fillText(c.team.pts + ' pts', bw / 2 - 24, 2); }
      ctx.restore();
    }
  }
  if (c.title) { tf(700, 40); ctx.fillStyle = TOY.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(c.title, 0, -h / 2 - 34); }
  ctx.restore();
};
CARDS.toytable.noSlide = true;

// A chunky clay number/word that drops in and squashes on landing (text, size, color, label).
CARDS.claynum = function (c, ct, cx, cy) {
  const k = pr(ct, 0, 0.5); if (k <= 0) return;
  const fall = 1 - eOut(Math.min(1, k * 1.6)), land = pr(ct, 0.31, 0.35), sq = land > 0 && land < 1 ? Math.sin(Math.PI * land) * 0.22 * (1 - land) : 0;
  const size = c.size || 260, col = c.color || '#d6283b', depth = Math.max(8, size * 0.07);
  ctx.save(); ctx.translate(cx, cy - fall * 900); ctx.scale(1 + sq, 1 - sq * 1.2); ctx.rotate(c.rot != null ? c.rot : -0.04);
  font(900, size, 'Inter', '-4px'); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = 'rgba(60,25,10,0.3)'; ctx.fillText(c.text, depth * 0.8, depth * 1.6);
  for (let d = depth; d > 0; d -= 2) { ctx.fillStyle = shade(col, -0.35 - 0.1 * d / depth); ctx.fillText(c.text, 0, d); }
  const g = ctx.createLinearGradient(0, -size * 0.8, 0, 0); g.addColorStop(0, shade(col, 0.3)); g.addColorStop(1, col);
  ctx.fillStyle = g; ctx.fillText(c.text, 0, 0);
  ctx.globalAlpha *= 0.35; ctx.fillStyle = '#fff'; ctx.fillText(c.text, -size * 0.012, -size * 0.012); ctx.globalAlpha /= 0.35;
  ctx.fillStyle = g; ctx.fillText(c.text, 0, 0);
  ctx.restore();
  if (c.label) toyTape(c.label, cx, cy + (c.labelDy || 70), 40, eBack(pr(ct, 0.55, 0.3)), 0.02);
};
CARDS.claynum.noSlide = true;

// Results tiles: frosted tiles that drop in one by one (items: [{score, team, win, at|t}]), 2 columns.
CARDS.toyresults = function (c, ct, cx, cy) {
  ctx.save(); toyDrift(ct, cx, cy, 0.035);
  const items = c.items || [], cols = 2, tw = 420, th = 230, gap = 34, rows = Math.ceil(items.length / cols);
  items.forEach((it, i) => {
    const k = pr(ct, it.t != null ? it.t : i * 0.5, 0.5); if (k <= 0) return;
    const col = i % cols, row = Math.floor(i / cols), x = cx + (col - (cols - 1) / 2) * (tw + gap), y = cy + (row - (rows - 1) / 2) * (th + gap);
    const fall = 1 - eOut(Math.min(1, k * 1.5)), land = pr(k, 0.62, 0.38), sq = land > 0 && land < 1 ? Math.sin(Math.PI * land) * 0.08 : 0;
    ctx.save(); ctx.translate(x, y - fall * 700); ctx.scale(1 + sq, 1 - sq); ctx.rotate((col ? 1 : -1) * 0.015);
    ctx.shadowColor = 'rgba(40,20,5,0.28)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 12;
    ctx.fillStyle = 'rgba(255,255,255,0.9)'; rrect(-tw / 2, -th / 2, tw, th, 36); ctx.fill(); ctx.shadowColor = 'transparent';
    tf(800, 92); ctx.fillStyle = TOY.ink; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillText(it.score, -tw / 2 + 40, 18);
    tf(600, 34); ctx.fillStyle = '#6b6f78'; ctx.fillText(it.team, -tw / 2 + 42, 74);
    const ok = it.win, chip = ok ? '#34c759' : '#ff3b30';   // iOS green / red
    toyBlob(tw / 2 - 64, -th / 2 + 64, 34, chip);
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath();
    const bx = tw / 2 - 64, by = -th / 2 + 64;
    if (ok) { ctx.moveTo(bx - 14, by + 1); ctx.lineTo(bx - 3, by + 12); ctx.lineTo(bx + 15, by - 11); } else { ctx.moveTo(bx - 11, by - 11); ctx.lineTo(bx + 11, by + 11); ctx.moveTo(bx + 11, by - 11); ctx.lineTo(bx - 11, by + 11); }
    ctx.stroke(); ctx.restore();
  });
  ctx.restore();
};
CARDS.toyresults.noSlide = true;

// Three clay archways (doors: [{label, sub, color, at|t, shut}]): each pops up on its word; a shut door gets a red bar across.
CARDS.toydoors = function (c, ct, cx, cy) {
  ctx.save(); toyDrift(ct, cx, cy, 0.035);
  const doors = c.doors || [], dw = 290, dh = 470, gap = 30;
  doors.forEach((d, i) => {
    const k = eBack(pr(ct, d.t || 0, 0.5)); if (k <= 0) return;
    const x = cx + (i - (doors.length - 1) / 2) * (dw + gap);
    ctx.save(); ctx.translate(x, cy + dh / 2); ctx.scale(1, k); ctx.translate(0, -dh / 2);
    const g = ctx.createLinearGradient(-dw / 2, 0, dw / 2, 0); g.addColorStop(0, shade(d.color, 0.25)); g.addColorStop(1, shade(d.color, -0.2));
    ctx.shadowColor = 'rgba(40,20,5,0.3)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 12;
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-dw / 2, dh / 2); ctx.lineTo(-dw / 2, -dh / 2 + dw / 2); ctx.arc(0, -dh / 2 + dw / 2, dw / 2, Math.PI, 0); ctx.lineTo(dw / 2, dh / 2); ctx.closePath(); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = 'rgba(30,15,5,0.55)'; ctx.beginPath(); const iw = dw * 0.62; ctx.moveTo(-iw / 2, dh / 2); ctx.lineTo(-iw / 2, -dh / 2 + dw / 2 + 30); ctx.arc(0, -dh / 2 + dw / 2 + 30, iw / 2, Math.PI, 0); ctx.lineTo(iw / 2, dh / 2); ctx.closePath(); ctx.fill();
    tf(800, 54); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(d.label, 0, -dh / 2 + 92);
    if (d.sub) { tf(600, 30); ctx.fillStyle = 'rgba(255,255,255,0.92)'; ctx.fillText(d.sub, 0, dh / 2 + 52); }
    if (d.shut != null) { const sk = eOut(pr(ct, d.shut, 0.35)); if (sk > 0) { ctx.save(); ctx.rotate(-0.18); ctx.fillStyle = '#ff3b30'; rrect(-dw * 0.62 * sk, -24, dw * 1.24 * sk, 48, 24); ctx.fill();
      tf(800, 30); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; if (sk > 0.9) ctx.fillText('OUT', 0, 2); ctx.restore(); } }
    ctx.restore();
  });
  ctx.restore();
};
CARDS.toydoors.noSlide = true;
