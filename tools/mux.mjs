// Two-pass EBU R128 loudness normalisation to -14 LUFS (-1 dBTP), then mux with the video.
import fs from 'fs';
import path from 'path';
import { execFileSync, spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const NAME = process.argv[2] || 'classic';
const BUILD = path.join(ROOT, 'build', NAME);
const OUT = path.join(ROOT, 'out');
fs.mkdirSync(OUT, { recursive: true });
const audio = path.join(BUILD, 'audio.wav');
const video = path.join(BUILD, 'video.mp4');
const TARGET = 'I=-14:TP=-1:LRA=11';

const pass1 = spawnSync('ffmpeg', ['-hide_banner', '-i', audio, '-af', `loudnorm=${TARGET}:print_format=json`, '-f', 'null', '-'], { encoding: 'utf8' });
const m = JSON.parse(pass1.stderr.slice(pass1.stderr.lastIndexOf('{'), pass1.stderr.lastIndexOf('}') + 1));
const norm = path.join(BUILD, 'audio-14lufs.wav');
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', audio, '-af',
  `loudnorm=${TARGET}:measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}:linear=true,aresample=48000`,
  '-c:a', 'pcm_s16le', norm]);
const check = spawnSync('ffmpeg', ['-hide_banner', '-i', norm, '-af', 'ebur128=peak=true', '-f', 'null', '-'], { encoding: 'utf8' }).stderr;
const I = (check.match(/I:\s+(-?[\d.]+) LUFS/g) || []).pop();
const TP = (check.match(/Peak:\s+(-?[\d.]+) dBFS/g) || []).pop();
console.log(`audio loudness: ${I}, true ${TP}`);

const out = path.join(OUT, `${NAME}.mp4`);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-i', norm, '-map', '0:v', '-map', '1:a',
  '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out]);
console.log('final ->', out);
