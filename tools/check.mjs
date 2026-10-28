// Pre-render check: run against the same timeline the renderer uses.
//  1. every hit lands exactly on its note (position, time, direction, object at rest)
//  2. the ball never clips through anything (objects, pole, arms, props)
//  3. the ball stays in frame (except the scripted roll-off gag at the very end)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { buildTimeline, BALL_R, POLE_R, KINDS, quat, v3 } from '../src/timeline.js';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const score = JSON.parse(fs.readFileSync(path.join(ROOT, 'build/score.json'), 'utf8'));
const tl = buildTimeline(score);
const { mel, objects, props } = tl;
const errors = [];
const fail = (msg) => { if (errors.length < 40) console.log('  FAIL ' + msg); errors.push(msg); };

// ---------------------------------------------------------------- 1. hits
let worstPos = 0;
for (let i = 0; i < mel.length; i++) {
  const t = mel[i].t;
  const o = objects[tl.hitObj[i]];
  const p = tl.ballRaw(t).p;
  const want = v3.add(tl.objectPose(o, t).pos, [0, BALL_R, 0]);
  const err = v3.len(v3.sub(p, want));
  worstPos = Math.max(worstPos, err);
  if (err > 1e-6) fail(`hit ${i} (${mel[i].name} @ ${t.toFixed(3)}s): ball is ${err.toExponential(2)} off its contact point`);
  if (Math.abs(tl.dipOf(o, t)) > 1e-9) fail(`hit ${i}: object still moving at contact`);
  const before = tl.ballRaw(t - 1e-4).v[1], after = tl.ballRaw(t + 1e-4).v[1];
  if (!(before < 0)) fail(`hit ${i}: ball not descending into the hit (vy=${before.toFixed(2)})`);
  if (i < mel.length - 1 && !(after > 0)) fail(`hit ${i}: ball does not bounce up (vy=${after.toFixed(2)})`);
  // the audio is rendered from the same score: the melody note must sit at this exact time
  if (!score.notes.some((n) => n.t === mel[i].t && n.midi === mel[i].midi)) fail(`hit ${i}: no audio note at ${t}`);
}
const repeated = mel.filter((n, i) => i > 0 && n.midi === mel[i - 1].midi && n.scene === mel[i - 1].scene).length;
console.log(`hits: ${mel.length} bounces on ${objects.length} objects (${repeated} in place), worst contact error ${worstPos.toExponential(1)}`);

// ---------------------------------------------------------------- 2. clipping
function sdCollider(cl, p) {
  if (cl.shape === 'box') {
    const d = [0, 1, 2].map((k) => Math.abs(p[k] - cl.c[k]) - cl.h[k]);
    const out = Math.hypot(Math.max(d[0], 0), Math.max(d[1], 0), Math.max(d[2], 0));
    return out + Math.min(Math.max(d[0], d[1], d[2]), 0);
  }
  if (cl.shape === 'cyl') {
    const dr = Math.hypot(p[0] - cl.c[0], p[2] - cl.c[2]) - cl.r;
    const dy = Math.abs(p[1] - cl.c[1]) - cl.hh;
    return Math.hypot(Math.max(dr, 0), Math.max(dy, 0)) + Math.min(Math.max(dr, dy), 0);
  }
  return v3.len(v3.sub(p, cl.c)) - cl.r;
}
const toLocal = (p, pos, q) => quat.rotate(quat.conj(q), v3.sub(p, pos));
function segDist(p, a, b) {
  const ab = v3.sub(b, a); const s = Math.min(1, Math.max(0, v3.dot(v3.sub(p, a), ab) / v3.dot(ab, ab)));
  return v3.len(v3.sub(p, v3.add(a, v3.mul(ab, s))));
}
const TOL = 1.5e-3;
const RATE = 2000;
let minClear = Infinity, minWhat = '';
const record = (d, what, t) => {
  const clear = d - BALL_R;
  if (clear < minClear) { minClear = clear; minWhat = `${what} @ ${t.toFixed(3)}s`; }
  if (clear < -TOL) fail(`ball clips ${what} at t=${t.toFixed(3)}s by ${(-clear).toFixed(4)}`);
};
const clipFails = () => errors.filter((e) => e.includes('clips')).length;
const yTop = Math.max(...objects.map((o) => o.top[1])) + 3;
for (let k = 0; k <= score.duration * RATE; k++) {
  const t = k / RATE;
  const p = tl.ballRaw(t).p;
  if (clipFails() > 30) break;
  // pole
  if (p[1] < yTop) record(Math.hypot(p[0], p[2]) - POLE_R, 'pole', t);
  for (const o of objects) {
    const pose = tl.objectPose(o, t);
    if (Math.abs(pose.pos[1] - p[1]) > 2.5 || Math.abs(pose.pos[0] - p[0]) > 2.5 || Math.abs(pose.pos[2] - p[2]) > 2.5) continue;
    const lp = toLocal(p, pose.pos, pose.q);
    for (const cl of KINDS[o.kind].collider) record(sdCollider(cl, lp), `${o.kind}#${o.id}`, t);
  }
  for (const pr of props) {
    if (pr.type === 'arm') {
      if (Math.abs(pr.a[1] - p[1]) > 1.5) continue;
      record(segDist(p, pr.a, pr.b) - pr.r, `arm#${pr.obj}`, t);
    } else {
      if (v3.len(v3.sub(pr.pos, p)) > 2.5) continue;
      const lp = toLocal(p, pr.pos, quat.axisAngle([0, 1, 0], pr.yaw));
      for (const cl of pr.colliders) record(sdCollider(cl, lp), pr.type, t);
    }
  }
}
console.log(`clipping: sampled at ${RATE} Hz, closest approach ${minClear.toFixed(4)} (${minWhat})`);

// ---------------------------------------------------------------- 3. framing
const W = score.width, H = score.height;
let worstX = 0, worstY = 0, worstT = 0, exempt = 0;
const frames = Math.ceil(score.duration * score.fps);
for (let f = 0; f < frames; f++) {
  const t = f / score.fps;
  if (tl.exemptFrame(t)) { exempt++; continue; }
  const cam = tl.camera(t);
  const b = tl.ball(t).p;
  const fwd = v3.norm(v3.sub(cam.target, cam.pos));
  const right = v3.norm(v3.cross(fwd, [0, 1, 0]));
  const up = v3.cross(right, fwd);
  const d = v3.sub(b, cam.pos);
  const z = v3.dot(d, fwd);
  const th = Math.tan((cam.fov * Math.PI / 180) / 2);
  const ny = v3.dot(d, up) / (z * th);
  const nx = v3.dot(d, right) / (z * th * (W / H));
  const rr = BALL_R / (z * th);   // ball radius in NDC (vertical)
  const ex = Math.abs(nx) + rr * (H / W), ey = Math.abs(ny) + rr;
  if (ex > worstX) worstX = ex;
  if (ey > worstY) { worstY = ey; worstT = t; }
  if (z <= 0.5 || ex > 0.92 || ey > 0.92) fail(`ball leaves the safe frame at frame ${f} (t=${t.toFixed(2)}s): ndc x=${nx.toFixed(2)} y=${ny.toFixed(2)}`);
}
console.log(`framing: ${frames} frames, ball edge reaches |x|<=${worstX.toFixed(2)} |y|<=${worstY.toFixed(2)} (worst at ${worstT.toFixed(2)}s), ${exempt} frames exempt (roll-off gag)`);

// export what the synth needs to know about each hit (object kind, impact speed and
// where on screen it happens, for stereo placement)
const hits = mel.map((n, i) => {
  const cam = tl.camera(n.t);
  const b = tl.contact[i];
  const fwd = v3.norm(v3.sub(cam.target, cam.pos));
  const right = v3.norm(v3.cross(fwd, [0, 1, 0]));
  const d = v3.sub(b, cam.pos);
  const x = v3.dot(d, right) / (v3.dot(d, fwd) * Math.tan(cam.fov * Math.PI / 360) * (W / H));
  return { t: n.t, kind: objects[tl.hitObj[i]].kind, speed: +v3.len(tl.impact[i]).toFixed(3), x: +x.toFixed(3) };
});
fs.writeFileSync(path.join(ROOT, 'build/hits.json'), JSON.stringify({ hits, land: tl.ending.land }, null, 1));

// ------------------------------------------------------------------ summary
const s = tl.sceneRange;
console.log(`tower: salon ${s[1].top.toFixed(1)}..${s[1].bottom.toFixed(1)}, cave ${s[2].top.toFixed(1)}..${s[2].bottom.toFixed(1)}, party ${s[3].top.toFixed(1)}..${s[3].bottom.toFixed(1)}`);
if (errors.length) {
  console.log(`\nCHECK FAILED: ${errors.length} problem(s)`);
  process.exit(1);
}
console.log('\nCHECK PASSED');
