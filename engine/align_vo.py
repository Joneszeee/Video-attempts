#!/usr/bin/env python3
"""Finds where each beat starts in a voiceover recorded elsewhere (e.g. one ElevenLabs file),
by aligning it against a reference read of the same script whose line starts are known
(the Kokoro preview from engine/tts.py). Uses MFCC features + dynamic time warping, then snaps
each boundary to the nearest pause. Writes <vo>.beats.json, which build.py then uses for sync.

usage: python3 engine/align_vo.py <recorded vo> <reference vo.wav (with .beats.json)>
"""
import json
import re
import subprocess
import sys

import numpy as np

SR, HOP, WIN = 16000, 320, 400  # 20 ms hop, 25 ms window


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def mfcc(x, n_mels=26, n_ceps=13):
    frames = np.lib.stride_tricks.sliding_window_view(x, WIN)[::HOP] * np.hamming(WIN)
    spec = np.abs(np.fft.rfft(frames, 512)) ** 2
    mel = lambda f: 2595 * np.log10(1 + f / 700)
    imel = lambda m: 700 * (10 ** (m / 2595) - 1)
    pts = np.floor((512 + 1) * imel(np.linspace(mel(60), mel(7600), n_mels + 2)) / SR).astype(int)
    fb = np.zeros((n_mels, spec.shape[1]))
    for i in range(n_mels):
        a, b, c = pts[i], pts[i + 1], pts[i + 2]
        fb[i, a:b] = (np.arange(a, b) - a) / max(1, b - a)
        fb[i, b:c] = (c - np.arange(b, c)) / max(1, c - b)
    logmel = np.log(spec @ fb.T + 1e-8)
    n = np.arange(n_mels)
    dct = np.cos(np.pi / n_mels * (n[None, :] + 0.5) * np.arange(n_ceps)[:, None])
    c = logmel @ dct.T
    return (c - c.mean(0)) / (c.std(0) + 1e-8)


def dtw_path(a, b):
    n, m = len(a), len(b)
    cost = np.full(m + 1, np.inf)
    cost[0] = 0
    back = np.zeros((n, m), dtype=np.int8)
    bn = (b ** 2).sum(1)
    for i in range(n):
        d = (a[i] ** 2).sum() + bn - 2 * b @ a[i]
        new = np.full(m + 1, np.inf)
        diag, up = cost[:-1], cost[1:]
        # sequential min for the "left" move
        best = np.minimum(diag, up)
        choice = np.where(diag <= up, 0, 1).astype(np.int8)
        row = np.empty(m)
        prev = np.inf
        for j in range(m):
            v = best[j]
            ch = choice[j]
            if prev < v:
                v, ch = prev, 2
            row[j] = v + d[j]
            back[i, j] = ch
            prev = row[j]
        new[1:] = row
        new[0] = np.inf
        cost = new
    # backtrack: map each reference frame i to a frame j in b
    i, j, mapping = n - 1, m - 1, {}
    while i >= 0 and j >= 0:
        mapping.setdefault(i, j)
        ch = back[i, j]
        if ch == 0:
            i, j = i - 1, j - 1
        elif ch == 1:
            i -= 1
        else:
            j -= 1
    return mapping


def pauses(path):
    err = subprocess.run(['ffmpeg', '-i', path, '-af', 'silencedetect=noise=-35dB:d=0.15', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return list(zip(map(float, re.findall(r'silence_start: ([\d.]+)', err)), map(float, re.findall(r'silence_end: ([\d.]+)', err))))


def main():
    rec, ref = sys.argv[1], sys.argv[2]
    ref_starts = json.load(open(ref + '.beats.json'))['starts']
    a, b = mfcc(load(ref)), mfcc(load(rec))
    mapping = dtw_path(a, b)
    sil = pauses(rec)
    starts = [0.0]
    for t in ref_starts[1:]:
        j = mapping[min(int(t * SR / HOP), len(a) - 1)] * HOP / SR
        near = min(sil, key=lambda p: abs(p[1] - j)) if sil else None
        s = near[1] if near and abs(near[1] - j) < 0.6 else j
        print(f'  ref {t:6.2f}s -> dtw {j:6.2f}s -> start {s:6.2f}s')
        starts.append(s)
    json.dump({'starts': starts}, open(rec + '.beats.json', 'w'))
    print('wrote', rec + '.beats.json')


if __name__ == '__main__':
    main()
