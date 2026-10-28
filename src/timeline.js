// Pure math, shared by the three.js scene (browser) and the pre-render checker (node).
// Everything here is derived from score.json and is a function of time t: no state,
// no integration across frames, so any frame can be rendered (or checked) on its own.

export const BALL_R = 0.16;
export const RING_R = 2.0;        // radius of the spiral the ball travels on
export const POLE_R = 0.3;

const TAU = Math.PI * 2;
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
export const v3 = {
  add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]],
  sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]],
  mul: (a, s) => [a[0] * s, a[1] * s, a[2] * s],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2],
  len: (a) => Math.hypot(a[0], a[1], a[2]),
  norm: (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; },
  cross: (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]],
  lerp: (a, b, s) => [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, a[2] + (b[2] - a[2]) * s],
};

// quaternions as [x, y, z, w]
export const quat = {
  axisAngle(axis, ang) { const s = Math.sin(ang / 2); return [axis[0] * s, axis[1] * s, axis[2] * s, Math.cos(ang / 2)]; },
  mul(a, b) {
    return [
      a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
      a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
      a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
      a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2],
    ];
  },
  rotate(q, v) {
    const [x, y, z, w] = q;
    const ix = w * v[0] + y * v[2] - z * v[1], iy = w * v[1] + z * v[0] - x * v[2];
    const iz = w * v[2] + x * v[1] - y * v[0], iw = -x * v[0] - y * v[1] - z * v[2];
    return [ix * w + iw * -x + iy * -z - iz * -y, iy * w + iw * -y + iz * -x - ix * -z,
      iz * w + iw * -z + ix * -y - iy * -x];
  },
  conj: (q) => [-q[0], -q[1], -q[2], q[3]],
  identity: () => [0, 0, 0, 1],
};

// --------------------------------------------------------------- object kinds
// Local frame of every object: origin at the centre of its top (the contact point),
// +Y up, +Z radially outward (toward the camera), +X along the direction of travel.
// Colliders are in that local frame and are what the checker tests the ball against.
export const KINDS = {
  whiteKey: { w: 0.36, collider: [{ shape: 'box', c: [0, -0.1, 0], h: [0.18, 0.1, 0.62] }] },
  blackKey: { w: 0.26, collider: [{ shape: 'box', c: [0, -0.13, -0.18], h: [0.13, 0.13, 0.42] }] },
  books: { w: 0.66, collider: [{ shape: 'box', c: [0, -0.24, 0], h: [0.34, 0.24, 0.44] }] },
  crystal: { w: 0.42, collider: [{ shape: 'cyl', c: [0, -0.3, 0], r: 0.21, hh: 0.3 }] },
  mushroom: {
    w: 0.76, collider: [
      { shape: 'cyl', c: [0, -0.09, 0], r: 0.38, hh: 0.09 },
      { shape: 'cyl', c: [0, -0.45, 0], r: 0.13, hh: 0.3 }],
  },
  bigCrystal: { w: 0.64, collider: [{ shape: 'cyl', c: [0, -0.5, 0], r: 0.32, hh: 0.5 }] },
  drum: { w: 0.66, collider: [{ shape: 'cyl', c: [0, -0.17, 0], r: 0.33, hh: 0.17 }] },
  jelly: { w: 0.4, collider: [{ shape: 'box', c: [0, -0.19, 0], h: [0.19, 0.19, 0.19] }] },
  duck: {
    w: 0.56, collider: [
      { shape: 'box', c: [0, -0.16, -0.02], h: [0.27, 0.16, 0.21] },
      { shape: 'sphere', c: [0, 0.05, 0.31], r: 0.14 }],
  },
  stage: { w: 1.8, collider: [{ shape: 'cyl', c: [0, -0.25, 0], r: 0.9, hh: 0.25 }] },
};

export const SCENES = {
  1: { name: 'salon', bg: [0x24 / 255, 0x1a / 255, 0x3d / 255] },
  2: { name: 'cave', bg: [0x06 / 255, 0x1a / 255, 0x1d / 255] },
  3: { name: 'party', bg: [0xb8 / 255, 0x30 / 255, 0x6e / 255] },
};

function kindFor(note, dt, scene, repeated) {
  if (scene === 1) {
    if (note.name.includes('#')) return 'blackKey';
    return dt > 0.5 ? 'books' : 'whiteKey';
  }
  if (scene === 2) {
    if (note.tag === 'crash') return 'bigCrystal';
    return dt > 0.36 ? 'mushroom' : 'crystal';
  }
  if (note.tag === 'final') return 'stage';
  if (note.tag === 'duck') return 'duck';
  if (repeated || dt > 0.3) return 'drum';
  return 'jelly';
}

// --------------------------------------------------------------- the timeline
export function buildTimeline(score) {
  const g = score.gravity;
  const G = [0, -g, 0];
  const mel = score.melody;
  const N = mel.length;
  const ending = score.ending;
  const sceneOf = (i) => mel[i].scene;

  // 1. which object does each note land on? Repeated notes bounce in place.
  const objects = [];
  const hitObj = [];
  for (let i = 0; i < N; i++) {
    const prev = i > 0 ? mel[i - 1] : null;
    const same = prev && prev.midi === mel[i].midi && prev.scene === mel[i].scene;
    if (same) {
      hitObj.push(hitObj[i - 1]);
      objects[hitObj[i]].hits.push(i);
      objects[hitObj[i]].repeated = true;
      continue;
    }
    hitObj.push(objects.length);
    objects.push({ id: objects.length, scene: mel[i].scene, hits: [i], repeated: false });
  }
  // interval after each note (to the next bounce). The last note is the final landing.
  const dtAfter = (i) => (i < N - 1 ? mel[i + 1].t - mel[i].t : 1.0);
  for (const o of objects) {
    const first = o.hits[0];
    const dt = dtAfter(o.hits[o.hits.length - 1]);
    const n = mel[first];
    o.kind = kindFor(n, dt, o.scene, o.repeated);
    o.note = n;
    o.midi = n.midi;
    o.lastInScene = (first === N - 1) || (mel[o.hits[o.hits.length - 1] + 1] || {}).scene !== o.scene;
    o.knocked = o.lastInScene && o.scene < 3;
  }

  // 2. Solve the layout backwards from the note times. The final landing point is fixed
  // (the stage at the bottom of the tower, y = 0); every earlier contact point is placed by
  // stepping back through the note intervals: the vertical drop between two hits is a fixed
  // fraction of what one gravity allows in that interval (g dt^2 / 2), so every flight time
  // is exactly the note interval and every arc is a true parabola under the same g.
  const topPos = new Array(objects.length);
  const theta = new Array(objects.length);
  const contact = new Array(N);
  const last = hitObj[N - 1];
  theta[last] = 0.0;
  topPos[last] = [RING_R, 0, 0];
  for (let i = N - 2; i >= 0; i--) {
    const a = hitObj[i], b = hitObj[i + 1];
    if (a === b) continue;           // same object, already placed
    const dt = mel[i + 1].t - mel[i].t;
    const dive = mel[i].scene !== mel[i + 1].scene;
    const wa = KINDS[objects[a].kind].w, wb = KINDS[objects[b].kind].w;
    let k, sep;
    if (dive) {
      k = 0.62; sep = 1.5;
    } else {
      k = dt > 0.42 ? 0.42 : dt > 0.25 ? 0.36 : 0.3;
      sep = Math.max((wa + wb) / 2 + 0.16, Math.min(dt * 2.3, 1.25));
    }
    const drop = k * g * dt * dt / 2;
    const dTheta = 2 * Math.asin(sep / (2 * RING_R));
    theta[a] = theta[b] + dTheta;    // travel goes toward decreasing theta
    topPos[a] = [RING_R * Math.cos(theta[a]), topPos[b][1] + drop, RING_R * Math.sin(theta[a])];
  }
  objects.forEach((o, i) => {
    o.theta = theta[i];
    o.top = topPos[i];
    // basis: X along travel (-tangent), Y up, Z radial outward
    const c = Math.cos(o.theta), s = Math.sin(o.theta);
    o.ex = [s, 0, -c];
    o.ey = [0, 1, 0];
    o.ez = [c, 0, s];
    o.yaw = Math.PI / 2 - o.theta;   // three.js rotation.y that maps local axes to the basis
  });
  for (let i = 0; i < N; i++) contact[i] = v3.add(objects[hitObj[i]].top, [0, BALL_R, 0]);

  // 3. ballistic segments between hits: p(t) = p0 + v0 (t - t0) + G (t - t0)^2 / 2
  const segs = [];
  const pushSeg = (t0, t1, p0, v0, kind, extra = {}) => segs.push({ t0, t1, p0, v0, kind, ...extra });
  // intro: hangs, then is released from rest and falls onto the first key
  const t0 = mel[0].t;
  const tRel = Math.max(0.1, t0 - 0.36);
  const pStart = v3.add(contact[0], [0, g * (t0 - tRel) ** 2 / 2, 0]);
  pushSeg(-1, tRel, pStart, [0, 0, 0], 'hold');
  pushSeg(tRel, t0, pStart, [0, 0, 0], 'fly');
  const impact = new Array(N);
  for (let i = 0; i < N - 1; i++) {
    const dt = mel[i + 1].t - mel[i].t;
    const d = v3.sub(contact[i + 1], contact[i]);
    const v0 = v3.sub(v3.mul(d, 1 / dt), v3.mul(G, dt / 2));
    pushSeg(mel[i].t, mel[i + 1].t, contact[i], v0, 'fly', { hit: i });
  }
  // ending: dead landing, sit, roll to the edge, fall, boing back up, land, Fin.
  const tF = mel[N - 1].t;
  const prevSeg = segs[segs.length - 1];
  const arriveV = v3.add(prevSeg.v0, v3.mul(G, tF - prevSeg.t0));
  let dir = v3.norm([arriveV[0], 0, arriveV[2]]);
  const stage = objects[last];
  const stageR = KINDS.stage.collider[0].r;
  const rollDist = stageR + 0.12;
  const tRoll = ending.rollStart, tOff = ending.rollOff, tBoing = ending.boing, tLand = ending.land;
  pushSeg(tF, tRoll, contact[N - 1], [0, 0, 0], 'hold', { on: last });
  const rollA = 2 * rollDist / ((tOff - tRoll) ** 2);
  pushSeg(tRoll, tOff, contact[N - 1], [0, 0, 0], 'roll', { dir, acc: rollA, on: last });
  const pEdge = v3.add(contact[N - 1], v3.mul(dir, rollDist));
  const vEdge = v3.mul(dir, rollA * (tOff - tRoll));
  pushSeg(tOff, tBoing, pEdge, vEdge, 'fly');
  const fall = tBoing - tOff;
  const pBoing = v3.add(v3.add(pEdge, v3.mul(vEdge, fall)), v3.mul(G, fall * fall / 2));
  const tr = tLand - tBoing;
  const vBoing = v3.sub(v3.mul(v3.sub(contact[N - 1], pBoing), 1 / tr), v3.mul(G, tr / 2));
  pushSeg(tBoing, tLand, pBoing, vBoing, 'fly', { boing: true });
  pushSeg(tLand, 1e9, contact[N - 1], [0, 0, 0], 'hold', { on: last });

  // impact speeds (for squash and dip amounts)
  for (let i = 0; i < N; i++) {
    const s = segs.find((q) => q.kind === 'fly' && Math.abs(q.t1 - mel[i].t) < 1e-9);
    const v = s ? v3.add(s.v0, v3.mul(G, s.t1 - s.t0)) : [0, -5, 0];
    impact[i] = v;
  }
  const landV = v3.add(vBoing, v3.mul(G, tr));

  // spin: each flight rolls about (up x horizontal velocity); orientation is the product
  // of all previous segments' rotations, precomputed per segment start
  let q = quat.identity();
  for (const s of segs) {
    s.q0 = q;
    let axis = [0, 0, 1], w = 0;
    if (s.kind === 'fly' || s.kind === 'roll') {
      const vh = s.kind === 'roll' ? s.dir : [s.v0[0], 0, s.v0[2]];
      const sp = Math.hypot(vh[0], vh[2]);
      if (sp > 1e-6) {
        axis = v3.norm(v3.cross([0, 1, 0], vh));
        w = s.kind === 'roll' ? 1 : sp / BALL_R * 0.55;
      }
    }
    s.axis = axis; s.w = w;
    const dur = Math.min(s.t1, 1e3) - s.t0;
    q = quat.mul(quat.axisAngle(axis, s.kind === 'roll' ? (rollDist / BALL_R) : w * dur), q);
  }

  const segAt = (t) => {
    let lo = 0, hi = segs.length - 1;
    while (lo < hi) { const m = (lo + hi + 1) >> 1; if (segs[m].t0 <= t) lo = m; else hi = m - 1; }
    return segs[lo];
  };
  function ballRaw(t) {
    const s = segAt(t);
    const u = Math.max(0, t - Math.max(s.t0, -1));
    // resting on an object: ride its dip and spring-back
    const ride = s.on !== undefined ? [0, dipOf(objects[s.on], t), 0] : [0, 0, 0];
    if (s.kind === 'hold') return { p: v3.add(s.p0, ride), v: [0, 0, 0], s };
    if (s.kind === 'roll') {
      const d = 0.5 * s.acc * u * u;
      return { p: v3.add(v3.add(s.p0, v3.mul(s.dir, d)), ride), v: v3.mul(s.dir, s.acc * u), s, d };
    }
    return { p: v3.add(v3.add(s.p0, v3.mul(s.v0, u)), v3.mul(G, u * u / 2)), v: v3.add(s.v0, v3.mul(G, u)), s };
  }

  // hits of every kind, used for squash/dip: melody hits + the final landing
  const allHits = mel.map((n, i) => ({ t: n.t, obj: hitObj[i], speed: v3.len(impact[i]), i }));
  allHits.push({ t: tLand, obj: last, speed: v3.len(landV), i: -1, land: true });
  const hitTimes = allHits.map((h) => h.t);
  const nearestHit = (t) => {
    let lo = 0, hi = hitTimes.length - 1;
    while (lo < hi) { const m = (lo + hi) >> 1; if (hitTimes[m] < t) lo = m + 1; else hi = m; }
    const c = [lo - 1, lo].filter((x) => x >= 0 && x < hitTimes.length);
    return c.reduce((b, x) => (Math.abs(hitTimes[x] - t) < Math.abs(hitTimes[b] - t) ? x : b), c[0]);
  };

  function ball(t) {
    const { p, v, s, d } = ballRaw(t);
    // orientation
    let rot;
    if (s.kind === 'roll') rot = quat.mul(quat.axisAngle(s.axis, d / BALL_R), s.q0);
    else rot = quat.mul(quat.axisAngle(s.axis, s.w * Math.max(0, t - Math.max(s.t0, -1))), s.q0);
    // squash on contact (bottom stays pinned), stretch along velocity in flight
    const h = allHits[nearestHit(t)];
    const dtH = t - h.t;
    const amp = clamp(0.05 + 0.0065 * h.speed, 0.05, h.land ? 0.34 : 0.3);
    const sq = dtH < 0 ? amp * Math.exp(-((dtH / 0.012) ** 2))
      : amp * Math.exp(-((dtH / 0.055) ** 2)) * Math.cos(Math.min(dtH * 40, Math.PI * 1.5)) ** 1;
    const speed = v3.len(v);
    const near = 1 - Math.exp(-((dtH / 0.06) ** 2));
    const st = clamp(speed * 0.0045, 0, 0.16) * near;
    let axis = [0, 1, 0], scale = 1, offset = [0, 0, 0];
    if (Math.abs(sq) > st) {
      scale = 1 - sq;
      offset = [0, -BALL_R * sq, 0];
    } else if (st > 1e-4) {
      axis = v3.norm(v);
      scale = 1 + st;
    }
    return { p: v3.add(p, offset), center: p, v, rot, axis, scale };
  }

  // 4. objects: dip & spring back, glow, knocked-loose flight
  const DIP_T = 0.3;
  for (const o of objects) {
    o.hitTimes = o.hits.map((i) => mel[i].t);
    if (o.id === last) o.hitTimes = [...o.hitTimes, tLand];
    o.hitSpeed = o.hits.map((i) => v3.len(impact[i]));
    if (o.id === last) o.hitSpeed.push(v3.len(landV));
    o.dipT = o.hitTimes.map((t, j) => Math.min(DIP_T, j + 1 < o.hitTimes.length ? 0.85 * (o.hitTimes[j + 1] - t) : DIP_T));
    o.tKnock = o.knocked ? o.hitTimes[o.hitTimes.length - 1] : Infinity;
    if (o.knocked) {
      // knocked off its support: pushed down and outward (away from the ball's next
      // arc), tumbling. It shares the ball's gravity, so their separation is linear.
      o.knockV = v3.add(v3.add(v3.mul(o.ez, 1.0), v3.mul(o.ex, -1.1)), [0, -3.0, 0]);
      o.knockW = { axis: v3.norm(v3.add(o.ex, v3.mul(o.ez, 0.4))), w: -5.5 };
    }
  }
  function dipOf(o, t) {
    let y = 0;
    for (let j = 0; j < o.hitTimes.length; j++) {
      const u = (t - o.hitTimes[j]) / o.dipT[j];
      if (u <= 0 || u >= 1) continue;
      const A = clamp(0.012 * o.hitSpeed[j], 0.025, 0.11);
      y -= A * Math.sin(1.5 * Math.PI * u) * (1 - u);
    }
    return y;
  }
  function glowOf(o, t) {
    let e = 0;
    for (const th of o.hitTimes) if (t >= th) e = Math.max(e, Math.exp(-(t - th) / 0.45));
    return e;
  }
  // world transform of an object at time t: {pos, q} where q rotates local -> world
  const baseQ = (o) => quat.axisAngle([0, 1, 0], o.yaw);
  function objectPose(o, t) {
    const q0 = baseQ(o);
    if (t <= o.tKnock) return { pos: v3.add(o.top, [0, dipOf(o, t), 0]), q: q0 };
    const u = t - o.tKnock;
    const pos = v3.add(v3.add(o.top, v3.mul(o.knockV, u)), v3.mul(G, u * u / 2));
    return { pos, q: quat.mul(quat.axisAngle(o.knockW.axis, o.knockW.w * u), q0) };
  }

  // 5. scene heights, for the backdrop and fog
  const sceneRange = {};
  for (const o of objects) {
    const r = sceneRange[o.scene] || (sceneRange[o.scene] = { top: -Infinity, bottom: Infinity });
    r.top = Math.max(r.top, o.top[1]);
    r.bottom = Math.min(r.bottom, o.top[1]);
  }
  // boundary between worlds = midway down each dive
  const boundaries = [];
  for (let s = 1; s < 3; s++) boundaries.push((sceneRange[s].bottom + sceneRange[s + 1].top) / 2);
  const sceneAtY = (y) => (y > boundaries[0] ? 1 : y > boundaries[1] ? 2 : 3);

  // 6. camera: orbits the tower at the ball's angle and follows it. Smoothed with a
  // symmetric Gaussian over precomputed tables, so it is still a pure function of t.
  const RATE = 240;
  const T_END = score.duration + 1;
  const nS = Math.ceil((T_END + 2) * RATE);
  const angRaw = new Float64Array(nS), yRaw = new Float64Array(nS);
  let prevAng = null;
  for (let k = 0; k < nS; k++) {
    const t = k / RATE - 1;
    const tt = Math.min(t, tF);             // after the final landing the camera settles
    const p = ballRaw(tt).p;
    let a = Math.atan2(p[2], p[0]);
    if (prevAng !== null) { while (a - prevAng > Math.PI) a -= TAU; while (a - prevAng < -Math.PI) a += TAU; }
    prevAng = a;
    angRaw[k] = a;
    yRaw[k] = p[1];
  }
  const gauss = (src, sigmaSec) => {
    const sg = sigmaSec * RATE, R = Math.ceil(sg * 3);
    const w = []; let sum = 0;
    for (let j = -R; j <= R; j++) { const x = Math.exp(-0.5 * (j / sg) ** 2); w.push(x); sum += x; }
    const out = new Float64Array(src.length);
    for (let k = 0; k < src.length; k++) {
      let acc = 0;
      for (let j = -R; j <= R; j++) acc += w[j + R] * src[clamp(k + j, 0, src.length - 1)];
      out[k] = acc / sum;
    }
    return out;
  };
  const angS = gauss(angRaw, 0.55);
  const yS = gauss(yRaw, 0.14);
  const ySlow = gauss(yRaw, 0.5);
  const sample = (arr, t) => {
    const x = (t + 1) * RATE; const k = clamp(Math.floor(x), 0, arr.length - 2); const f = clamp(x - k, 0, 1);
    return arr[k] * (1 - f) + arr[k + 1] * f;
  };
  function camera(t) {
    // orbit slightly ahead of the ball (travel runs toward decreasing angle) and look back
    // at it, so the spiral it is about to drop down is in view
    const endK = smooth((t - tF) / 2.5);
    const angB = sample(angS, t);
    const ang = angB - 0.5 + 0.3 * endK;
    // follow tightly in fast vertical motion, loosely otherwise
    const yb = sample(yS, t), yl = sample(ySlow, t);
    // never let the smoothed height drift more than ~1.3 units from the ball itself
    const yBall = ballRaw(Math.min(t, tF)).p[1];
    const m = 1.3;
    const y = yBall + m * Math.tanh((yb * 0.75 + yl * 0.25 - yBall) / m);
    const push = smooth((t - ending.fin + 1.2) / 3.0);
    const dist = 6.2 - 0.8 * push;
    const height = 1.35 - 0.3 * endK;
    const pos = [Math.cos(ang) * dist, y + height, Math.sin(ang) * dist];
    const tr = RING_R * (0.8 + 0.1 * endK);
    const target = [Math.cos(angB) * tr, y - 0.3 + 0.5 * endK, Math.sin(angB) * tr];
    return { pos, target, fov: 50 - 2 * push };
  }

  // 7. props that are not bounced on. Shared with the checker so it can prove the ball
  // never passes through any of them.
  const local = (o, x, y, z) => v3.add(o.top, v3.add(v3.add(v3.mul(o.ex, x), v3.mul(o.ey, y)), v3.mul(o.ez, z)));
  const props = [];
  const armDepth = { whiteKey: 0.12, blackKey: 0.16, books: 0.3, crystal: 0.45, mushroom: 0.6, bigCrystal: 0.8, drum: 0.24, jelly: 0.25, duck: 0.2, stage: 0.35 };
  const innerEdge = { whiteKey: 0.62, blackKey: 0.6, books: 0.44, crystal: 0.21, mushroom: 0.13, bigCrystal: 0.32, drum: 0.33, jelly: 0.19, duck: 0.22, stage: 0.9 };
  for (const o of objects) {
    const y = o.top[1] - armDepth[o.kind];
    const r0 = POLE_R - 0.02, r1 = RING_R - innerEdge[o.kind] + 0.03;
    if (r1 <= r0) continue;
    const c = Math.cos(o.theta), s = Math.sin(o.theta);
    props.push({ type: 'arm', scene: o.scene, obj: o.id, a: [c * r0, y, s * r0], b: [c * r1, y, s * r1], r: o.kind === 'stage' ? 0.09 : 0.035 });
  }
  // the troll naps on a ledge beside the crystal that the final crash knocks loose
  const crashObj = objects.find((o) => o.kind === 'bigCrystal');
  if (crashObj) {
    const p = local(crashObj, -0.75, -1.7, -1.4);
    props.push({ type: 'troll', scene: 2, pos: p, yaw: crashObj.yaw, tWake: crashObj.tKnock,
      colliders: [{ shape: 'sphere', c: [0, 0.3, 0], r: 0.36 }, { shape: 'box', c: [0, -0.08, 0], h: [0.6, 0.08, 0.45] }] });
  }
  // a chorus line of bowling pins on the back half of the final stage
  for (let k = 0; k < 5; k++) {
    const x = -0.56 + k * 0.28;
    props.push({ type: 'pin', scene: 3, idx: k, pos: local(stage, x, 0, -0.52), yaw: stage.yaw,
      colliders: [{ shape: 'cyl', c: [0, 0.22, 0], r: 0.085, hh: 0.22 }] });
  }
  // balloons bobbing outside the ring, candles floating in the salon
  objects.forEach((o, i) => {
    if (o.scene === 3 && i % 5 === 2 && o.kind !== 'stage') {
      props.push({ type: 'balloon', scene: 3, idx: i, pos: local(o, 0.35, 1.25 + (i % 3) * 0.3, 1.25), yaw: o.yaw,
        colliders: [{ shape: 'sphere', c: [0, 0, 0], r: 0.3 }] });
    }
    if (o.scene === 1 && i % 6 === 3) {
      props.push({ type: 'candle', scene: 1, idx: i, pos: local(o, 0.2, 0.9 + (i % 2) * 0.4, 1.15), yaw: o.yaw,
        colliders: [{ shape: 'cyl', c: [0, -0.2, 0], r: 0.09, hh: 0.24 }] });
    }
  });

  return {
    props, local,
    score, g, objects, hitObj, contact, segs, ball, ballRaw, objectPose, dipOf, glowOf, camera,
    sceneRange, boundaries, sceneAtY, impact, allHits, stage, dir, tF, ending, mel,
    exemptFrame: (t) => t > tOff - 0.05 && t < tLand - 0.25,
  };
}

// colour of the backdrop at world height y: each world has its own colour; the dive
// between two worlds passes through a dark band (a physical gap, not a crossfade)
export function backdropAt(tl, y) {
  const [b1, b2] = tl.boundaries;
  const c = (s) => SCENES[s].bg;
  const mix = (a, b, f) => [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
  const band = (y, b, upper, lower) => {
    const d = y - b;
    const dark = [0.02, 0.015, 0.03];
    if (d > 3) return null;
    if (d < -3) return null;
    if (d > 0) return mix(dark, upper, smooth(d / 3));
    return mix(dark, lower, smooth(-d / 3));
  };
  if (y > b1 - 3 && y < b1 + 3) return band(y, b1, c(1), c(2));
  if (y > b2 - 3 && y < b2 + 3) return band(y, b2, c(2), c(3));
  return c(y > b1 ? 1 : y > b2 ? 2 : 3);
}
