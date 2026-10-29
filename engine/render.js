#!/usr/bin/env node
// Renders a reel spec to a silent MP4 (plus events.json for sound effects),
// or to PNG stills for quick checks.
//   node engine/render.js spec.json out.mp4 [--fps 30] [--events events.json]
//   node engine/render.js spec.json stills_dir --stills 0.5,3,7.2
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : def;
}

(async () => {
  const [specPath, out] = process.argv.slice(2);
  if (!specPath || !out) {
    console.error('usage: render.js spec.json out.mp4|stills_dir [--fps 30] [--events f.json] [--stills t1,t2]');
    process.exit(1);
  }
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const fps = Number(arg('--fps', spec.fps || 30));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exit(1); });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  const info = await page.evaluate(s => window.loadSpec(s), spec);
  console.log(`duration ${info.duration.toFixed(2)}s, ${info.beats.length} beats`);
  info.beats.forEach((b, i) => console.log(`  beat ${i + 1}: ${b.start.toFixed(2)}s +${b.dur.toFixed(2)}s  ${b.headline || ''}`));

  const eventsPath = arg('--events');
  if (eventsPath) fs.writeFileSync(eventsPath, JSON.stringify({ duration: info.duration, events: info.events }, null, 1));

  const stills = arg('--stills');
  if (stills) {
    fs.mkdirSync(out, { recursive: true });
    for (const t of stills.split(',').map(Number)) {
      const b64 = await page.evaluate(t => window.frame(t, 'png'), t);
      const f = path.join(out, `t${t.toFixed(2)}.png`);
      fs.writeFileSync(f, Buffer.from(b64, 'base64'));
      console.log(f);
    }
    await browser.close();
    return;
  }

  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg exited ' + c)))));
  const n = Math.round(info.duration * fps);
  const t0 = Date.now();
  for (let f = 0; f < n; f++) {
    const b64 = await page.evaluate(t => window.frame(t), f / fps);
    if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % (fps * 5) === 0) process.stdout.write(`\r  frame ${f}/${n}`);
  }
  ff.stdin.end();
  await done;
  console.log(`\r  rendered ${n} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s -> ${out}`);
  await browser.close();
})();
