#!/usr/bin/env python3
"""Builds a finished reel from a spec.

usage:
  python3 build.py videos/<name>/spec.json                 # preview with estimated timing + SFX
  python3 build.py videos/<name>/spec.json --vo vo.mp3     # sync beats to the voiceover and mix it in
  python3 build.py videos/<name>/spec.json --vo vo.mp3 --music track.mp3
  python3 build.py videos/<name>/spec.json --stills 1,5,9  # PNG frames only (quick look)

The voiceover should have a clear pause (~0.6s+) between beats; each beat's on-screen
change is placed just before its line starts.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VO_DELAY = 0.25  # seconds of picture before the voice starts


def run(cmd, **kw):
    print('$', ' '.join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, **kw)


def audio_duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def silences(path, noise_db=-35, min_len=0.3):
    err = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(path), '-af', f'silencedetect=noise={noise_db}dB:d={min_len}',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    return list(zip(starts, ends))


def join_clips(folder, gap=0.45, sr=48000):
    """A folder of per-line voice clips (01.mp3, 02.mp3, ...) -> one vo.wav plus exact line starts."""
    import numpy as np
    files = sorted((f for f in Path(folder).iterdir() if f.suffix.lower() in ('.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac')),
                   key=lambda f: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', f.name)])
    parts, starts, t = [], [], 0.0
    for f in files:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-af',
                              'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
                              'silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                              '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, dtype=np.float32)
        starts.append(t)
        parts += [a, np.zeros(int(gap * sr), dtype=np.float32)]
        t += len(a) / sr + gap
        print(f'  {f.name}: {len(a) / sr:.2f}s')
    out = Path(folder) / 'vo_joined.wav'
    pcm = np.concatenate(parts[:-1])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', str(out)],
                   input=pcm.tobytes(), check=True)
    Path(str(out) + '.beats.json').write_text(json.dumps({'starts': starts}))
    return out


def align(spec, vo_path):
    """Set each beat's duration so beat i starts just before VO line i."""
    n = len(spec['beats'])
    total = audio_duration(vo_path)
    side = Path(str(vo_path) + '.beats.json')  # written by engine/tts.py: exact line start times
    if side.exists():
        line_starts = json.loads(side.read_text())['starts']
        if len(line_starts) != n:
            sys.exit(f'{side} has {len(line_starts)} lines but the spec has {n} beats.')
        starts = [0.0] + [VO_DELAY + t - 0.12 for t in line_starts[1:]]
    else:
        starts = pause_starts(vo_path, total, n)
    end = VO_DELAY + total + 0.6
    for i, b in enumerate(spec['beats']):
        b['duration'] = round((starts[i + 1] if i + 1 < n else end) - starts[i], 3)
    spec['tail'] = 0.6
    print('beat starts (s):', ', '.join(f'{s:.2f}' for s in starts))


def pause_starts(vo_path, total, n):
    """Beat starts from the n-1 longest pauses in a voiceover recorded elsewhere."""
    sil = [(s, e) for s, e in silences(vo_path) if s > 0.15 and e < total - 0.15]
    if len(sil) < n - 1:
        sil = [(s, e) for s, e in silences(vo_path, -30, 0.2) if s > 0.15 and e < total - 0.15]
    if len(sil) < n - 1:
        sys.exit(f'Found only {len(sil)} pauses in the voiceover but need {n - 1} (one between each beat). '
                 'Regenerate it with a longer pause between beats, or add "timings" to the spec.')
    picked = sorted(sorted(sil, key=lambda p: p[1] - p[0], reverse=True)[: n - 1])
    return [0.0] + [VO_DELAY + e - 0.12 for _, e in picked]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--vo')
    ap.add_argument('--music')
    ap.add_argument('--mute-vo', action='store_true', help='use the voice only for timing; mix SFX only (previews)')
    ap.add_argument('--music-volume', type=float, default=0.14)
    ap.add_argument('--stills')
    ap.add_argument('--out')
    a = ap.parse_args()

    spec_path = Path(a.spec)
    spec = json.loads(spec_path.read_text())
    outdir = spec_path.parent / 'out'
    outdir.mkdir(exist_ok=True)
    if spec.get('timings'):
        for b, d in zip(spec['beats'], spec['timings']):
            b['duration'] = d
    elif a.vo:
        if Path(a.vo).is_dir():  # one clip per beat, e.g. from ElevenLabs
            a.vo = str(join_clips(a.vo))
        align(spec, a.vo)
    resolved = outdir / 'resolved.json'
    resolved.write_text(json.dumps(spec, indent=1))

    render = ['node', ROOT / 'engine' / 'render.js', resolved]
    if a.stills:
        run(render + [outdir / 'stills', '--stills', a.stills])
        return

    silent, events, sfx = outdir / 'silent.mp4', outdir / 'events.json', outdir / 'sfx.wav'
    run(render + [silent, '--events', events])
    run([sys.executable, ROOT / 'engine' / 'sfx.py', events, sfx])

    final = Path(a.out) if a.out else outdir / (spec_path.parent.name + ('' if a.vo else '_preview') + '.mp4')
    inputs = ['-i', silent, '-i', sfx]
    mix = ['[1:a]volume=0.55[s]']
    labels = ['[s]']
    if a.vo and not a.mute_vo:
        inputs += ['-i', a.vo]
        d = int(VO_DELAY * 1000)
        mix.append(f'[2:a]adelay={d}|{d},volume=1.0[v]')
        labels.append('[v]')
    if a.music:
        inputs += ['-stream_loop', '-1', '-i', a.music]
        mix.append(f'[{3 if a.vo and not a.mute_vo else 2}:a]volume={a.music_volume}[m]')
        labels.append('[m]')
    mix.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=first[a]')
    mixed = outdir / 'mix.wav'
    run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(mix), '-map', '[a]', '-ar', '48000', mixed])
    # One fixed gain to reach -14 LUFS (Instagram). Dynamic loudnorm pumped the background noise up in pauses.
    err = subprocess.run(['ffmpeg', '-i', str(mixed), '-af', 'loudnorm=I=-14:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    measured = float(json.loads(err[err.rindex('{'):err.rindex('}') + 1])['input_i'])
    gain = -14 - measured
    print(f'loudness {measured:.1f} LUFS, gain {gain:+.1f} dB')
    run(['ffmpeg', '-y', '-v', 'error', '-i', silent, '-i', mixed, '-filter_complex',
         f'[1:a]volume={gain:.2f}dB,alimiter=limit=0.89:level=false[a]', '-map', '0:v', '-map', '[a]',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', final])
    print('done ->', final)


if __name__ == '__main__':
    main()
