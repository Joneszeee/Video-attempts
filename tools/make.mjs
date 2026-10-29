// The generator: one config in, one video out.
//   node tools/make.mjs videos/my-video.json             score -> check -> synth -> render -> out/my-video.mp4
//   node tools/make.mjs videos/my-video.json --preview   same up to the audio, then a contact sheet of stills
//                                                        (build/my-video/preview.png) instead of the full render
//   options: --workers N (parallel browsers, default 3), --stills 3.2,12 (explicit preview times)
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const cfgPath = args.find((a) => a.endsWith('.json'));
if (!cfgPath) { console.log('usage: node tools/make.mjs videos/<name>.json [--preview] [--workers N] [--stills t1,t2]'); process.exit(1); }
const opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const NAME = cfg.name || path.basename(cfgPath, '.json');
const BUILD = path.join(ROOT, 'build', NAME);

const run = (label, cmd, a) => {
  console.log(`\n== ${label}`);
  const r = spawnSync(cmd, a, { stdio: 'inherit', cwd: ROOT });
  if (r.status !== 0) { console.log(`\n${label} failed (exit ${r.status}); stopping.`); process.exit(r.status || 1); }
};

run('score', 'python3', ['tools/score.py', cfgPath]);
run('check (hits on notes, no clipping, ball in frame)', 'node', ['tools/check.mjs', NAME]);
run('synth', 'python3', ['tools/synth.py', NAME]);

if (args.includes('--preview')) {
  const score = JSON.parse(fs.readFileSync(path.join(BUILD, 'score.json'), 'utf8'));
  let times = opt('stills');
  if (!times) {
    const t = [];
    for (const s of score.sections) {
      t.push(s.firstHit + 0.15, s.firstHit + (s.lastHit - s.firstHit) * 0.6);
    }
    t.push(score.ending.fin + 1.0);
    times = t.map((x) => x.toFixed(2)).join(',');
  }
  const dir = path.join(BUILD, 'stills');
  fs.rmSync(dir, { recursive: true, force: true });
  run('preview stills', 'node', ['tools/render.mjs', '--name', NAME, '--stills', times]);
  const n = times.split(',').length;
  const sheet = path.join(BUILD, 'preview.png');
  spawnSync('ffmpeg', ['-loglevel', 'error', '-y', '-pattern_type', 'glob', '-i', path.join(dir, 't*.png'),
    '-vf', `scale=270:480,tile=${Math.min(n, 7)}x${Math.ceil(n / 7)}:padding=4`, '-frames:v', '1', sheet], { stdio: 'inherit' });
  console.log(`\npreview -> ${sheet}\naudio   -> ${path.join(BUILD, 'audio.wav')}`);
} else {
  run('render + mux', 'node', ['tools/render.mjs', '--name', NAME, '--workers', opt('workers', '3')]);
  console.log(`\ndone -> ${path.join(ROOT, 'out', NAME + '.mp4')}`);
}
