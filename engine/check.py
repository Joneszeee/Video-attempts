#!/usr/bin/env python3
"""Automatic check after a draft render (build.py --draft runs it; or run it by hand).

  python3 engine/check.py videos/<slug> [--video videos/<slug>/out/<slug>_draft.mp4]

Flags, in one report (out/check.txt) plus one contact sheet (out/check_sheet.jpg, a frame every 2 s with its time):
  - text cut off at a frame edge, and text from different owners colliding (headline v score bug, stamp v bubbles, a player's label...),
    from the engine's layout audit every 0.5 s; an issue only counts if it lasts at least 1 s (so fly-ins and transitions don't trip it);
  - shots shorter than 2 s (user rule: no hard cut under about 2 s);
  - still moments: frames 1 s apart whose mean pixel difference is under 3 (needs --video).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def audit(resolved, out):
    subprocess.run(['node', str(ROOT / 'render.js'), str(resolved), str(out), '--audit', '0.5'], check=True, capture_output=True)
    return json.loads(Path(out).read_text())


def persistent(samples, step=0.5, min_len=1.0):
    """Group identical issues over time; keep the ones that last at least min_len."""
    runs, texts = {}, {}
    for s in samples:
        seen = set()
        for i in s['issues']:
            if (i['kind'], i['owner']) in seen:
                continue
            seen.add((i['kind'], i['owner']))
            if 'outro' in i['owner']:
                continue
            key = (i['kind'], i['owner'])
            texts.setdefault(key, i['text'])
            r = runs.setdefault(key, [])
            if r and abs(r[-1][1] + step - s['t']) < 1e-6:
                r[-1][1] = s['t']
            else:
                r.append([s['t'], s['t']])
    out = []
    for (kind, owner), spans in runs.items():
        for a, b in spans:
            if b - a + step >= min_len:
                out.append((a, b, kind, owner, texts[(kind, owner)]))
    return sorted(out)


def motion(video, end):
    import numpy as np
    from PIL import Image
    tmp = Path(video).parent / '_motion'
    tmp.mkdir(exist_ok=True)
    for f in tmp.glob('*.png'):
        f.unlink()
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-vf', 'fps=2,scale=270:480', str(tmp / 'f%04d.png')], check=True)
    A = [np.asarray(Image.open(f).convert('L'), dtype=float) for f in sorted(tmp.glob('*.png'))]
    still = [(i / 2, round(float(np.abs(A[i] - A[i - 2]).mean()), 2)) for i in range(2, len(A)) if i / 2 < end and np.abs(A[i] - A[i - 2]).mean() < 3]
    return still


def sheet(video, out, every=2.0, cols=8):
    from PIL import Image, ImageDraw
    tmp = Path(video).parent / '_sheet'
    tmp.mkdir(exist_ok=True)
    for f in tmp.glob('*.png'):
        f.unlink()
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-vf', f'fps=1/{every},scale=216:384', str(tmp / 's%04d.png')], check=True)
    files = sorted(tmp.glob('*.png'))
    if not files:
        return
    w, h = 216, 384
    rows = (len(files) + cols - 1) // cols
    img = Image.new('RGB', (cols * w, rows * (h + 22)), (20, 20, 24))
    d = ImageDraw.Draw(img)
    for k, f in enumerate(files):
        x, y = (k % cols) * w, (k // cols) * (h + 22)
        img.paste(Image.open(f).convert('RGB'), (x, y + 22))
        d.text((x + 6, y + 4), f'{k * every:.0f}s', fill=(240, 240, 240))
    img.save(out, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder')
    ap.add_argument('--video')
    a = ap.parse_args()
    out = Path(a.folder) / 'out'
    res = audit(out / 'resolved.json', out / 'audit.json')
    beats, dur = res['beats'], res['duration']
    lines = []
    issues = persistent(res['samples'])
    lines.append(f'LAYOUT: {len(issues)} issue(s) lasting 1 s or more')
    for a0, b0, kind, owner, text in issues:
        lines.append(f'  {a0:5.1f}-{b0:5.1f}s  {kind:8s} {owner}: "{text}"')
    short = [(i + 1, b['start'], b['dur']) for i, b in enumerate(beats) if b['dur'] < 2.0]
    lines.append(f'SHOTS: {len(short)} shorter than 2 s')
    for i, s, d in short:
        lines.append(f'  shot {i} at {s:.1f}s lasts {d:.2f}s')
    if a.video:
        still = motion(a.video, dur - 2.4)   # the end screen is meant to be calm
        lines.append(f'MOTION: {len(still)} still moment(s)')
        for t, v in still:
            lines.append(f'  {t:5.1f}s  diff {v}')
        sheet(a.video, out / 'check_sheet.jpg')
        lines.append(f'SHEET: {out / "check_sheet.jpg"}')
    report = '\n'.join(lines)
    (out / 'check.txt').write_text(report + '\n')
    print(report)


if __name__ == '__main__':
    sys.exit(main())
