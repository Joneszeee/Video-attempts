#!/usr/bin/env python3
"""Synthesises the sound-effects track (whooshes, counter ticks, pops, crowd) from events.json.

usage: python3 sfx.py events.json out.wav
"""
import json
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(3)


def env(n, attack, release):
    a = max(1, int(attack * SR))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    e[a:] = np.exp(-np.linspace(0, 1, n - a) * (n - a) / (release * SR))
    return e


def lowpass(x, cutoff):
    # one-pole low-pass; cutoff may be an array (sweeps)
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def whoosh(dur=0.45, gain=0.5):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    sweep = np.concatenate([np.linspace(300, 4000, n // 2), np.linspace(4000, 500, n - n // 2)])
    x = lowpass(noise, sweep)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * shape * gain / (np.abs(x).max() + 1e-9)


def tick(gain=0.12):
    n = int(0.012 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 500) * gain


def pop(gain=0.3):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = np.linspace(500, 1100, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * gain


def impact(gain=0.7):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 40, n)) / SR) * np.exp(-t * 5)
    click = lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 60) * 3
    x = body + click
    return x / np.abs(x).max() * gain


def crowd(dur=4.0, gain=0.35):
    n = int(dur * SR)
    x = lowpass(rng.standard_normal(n), 1400)
    x = x - lowpass(x, 150)
    swell = env(n, 0.6, 1.6)
    return x / (np.abs(x).max() + 1e-9) * swell * gain


def bed(n, gain=0.012):
    # very quiet low rumble only; higher cutoffs read as hiss/static
    x = lowpass(lowpass(rng.standard_normal(n), 220), 220)
    return x / (np.abs(x).max() + 1e-9) * gain


def main():
    data = json.load(open(sys.argv[1]))
    n = int((data['duration'] + 0.5) * SR)
    out = np.zeros((n, 2))
    mono = bed(n)
    out[:, 0] += mono
    out[:, 1] += mono
    cache = {}
    makers = {
        'whoosh': lambda: whoosh(0.5, 0.55),
        'swish': lambda: whoosh(0.32, 0.25),
        'swipe': lambda: whoosh(0.25, 0.18),
        'tick': tick,
        'pop': pop,
        'impact': impact,
        'crowd': crowd,
    }
    for e in data['events']:
        if e['type'] not in cache:
            cache[e['type']] = makers[e['type']]()
        s = cache[e['type']]
        i = int(e['t'] * SR)
        j = min(n, i + len(s))
        if i >= n or i < 0:  # cues before frame 1 (cards already on screen in the hook) are skipped
            continue
        pan = 0.5 if e['type'] != 'tick' else 0.5 + rng.uniform(-0.15, 0.15)
        out[i:j, 0] += s[: j - i] * (1 - pan) * 2 * 0.7
        out[i:j, 1] += s[: j - i] * pan * 2 * 0.7
    peak = np.abs(out).max()
    if peak > 0.95:
        out *= 0.95 / peak
    pcm = (out * 32767).astype('<i2')
    with wave.open(sys.argv[2], 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
