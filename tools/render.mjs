// Renders the video with headless Chromium (Playwright) and pipes frames into ffmpeg.
//   node tools/render.mjs                      full render -> build/video.mp4, then mux -> out/ball-drop.mp4
//   node tools/render.mjs --stills 3.2,12,30   preview stills -> build/stills/
//   node tools/render.mjs --workers 3          split the frame range across browsers
//   node tools/render.mjs --from 100 --to 200  render a frame range only (no mux)
import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn, execFileSync } from 'child_process';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const BUILD = path.join(ROOT, 'build');
const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : def; };
const score = JSON.parse(fs.readFileSync(path.join(BUILD, 'score.json'), 'utf8'));
const FPS = score.fps, TOTAL = Math.ceil(score.duration * FPS);

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff' };
function serve() {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      if (p === '/') p = '/index.html';
      const f = path.join(ROOT, path.normalize(p));
      if (!f.startsWith(ROOT)) { res.writeHead(403); res.end(); return; }
      fs.readFile(f, (e, d) => {
        if (e) { res.writeHead(404); res.end(); return; }
        res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
        res.end(d);
      });
    }).listen(0, () => resolve(srv));
  });
}

async function openPage(port) {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: score.width, height: score.height }, deviceScaleFactor: 1 });
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.log('  [page]', m.text().slice(0, 300)); });
  page.on('pageerror', (e) => console.log('  [page error]', e.message));
  await page.goto(`http://localhost:${port}/index.html`);
  await page.waitForFunction('window.ready === true', null, { timeout: 180000 });
  return { browser, page };
}

const frame = async (page, t) => {
  await page.evaluate((tt) => window.renderFrame(tt), t);
  return page.screenshot({ type: 'png', omitBackground: false });
};

async function renderRange(port, from, to, outFile, label) {
  const { browser, page } = await openPage(port);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = from; f < to; f++) {
    const png = await frame(page, f / FPS);
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once('drain', r));
    const done = f - from + 1;
    if (done % 25 === 0 || f === to - 1) {
      const per = (Date.now() - t0) / done / 1000;
      console.log(`${label} frame ${f + 1}/${to}  ${per.toFixed(2)} s/frame  eta ${((to - f - 1) * per / 60).toFixed(1)} min`);
    }
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await browser.close();
}

const srv = await serve();
const port = srv.address().port;
fs.mkdirSync(BUILD, { recursive: true });

if (opt('stills')) {
  const dir = path.join(BUILD, 'stills');
  fs.mkdirSync(dir, { recursive: true });
  const { browser, page } = await openPage(port);
  for (const s of opt('stills').split(',')) {
    const t = parseFloat(s);
    const t0 = Date.now();
    const png = await frame(page, t);
    const f = path.join(dir, `t${t.toFixed(2).padStart(6, '0')}.png`);
    fs.writeFileSync(f, png);
    console.log(`still ${f}  (${Date.now() - t0} ms)`);
  }
  await browser.close();
  srv.close();
  process.exit(0);
}

const from = parseInt(opt('from', '0'), 10), to = Math.min(TOTAL, parseInt(opt('to', String(TOTAL)), 10));
const workers = parseInt(opt('workers', '2'), 10);
const chunk = Math.ceil((to - from) / workers);
const parts = [];
const jobs = [];
for (let w = 0; w < workers; w++) {
  const a = from + w * chunk, b = Math.min(to, a + chunk);
  if (a >= b) break;
  const out = path.join(BUILD, `part${w}.mp4`);
  parts.push(out);
  jobs.push(renderRange(port, a, b, out, `[w${w}]`));
}
await Promise.all(jobs);
srv.close();
const list = path.join(BUILD, 'parts.txt');
fs.writeFileSync(list, parts.map((p) => `file '${p}'`).join('\n'));
const video = path.join(BUILD, 'video.mp4');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]);
console.log('video ->', video);

if (from === 0 && to === TOTAL && !args.includes('--no-mux')) {
  const audio = path.join(BUILD, 'audio.wav');
  if (!fs.existsSync(audio)) { console.log('no build/audio.wav yet: run `npm run synth`, then `node tools/mux.mjs`'); process.exit(0); }
  execFileSync('node', [path.join(ROOT, 'tools/mux.mjs')], { stdio: 'inherit' });
}
