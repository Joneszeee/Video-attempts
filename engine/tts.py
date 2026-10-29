#!/usr/bin/env python3
"""Generates the voiceover from vo.txt with Kokoro (local, offline).

usage: python3 engine/tts.py videos/<slug>/vo.txt videos/<slug>/out/vo.wav [--voice bm_george] [--speed 1.0]

Needs `pip install kokoro-onnx soundfile` and the model files kokoro-v1.0.onnx + voices-v1.0.bin
(from github.com/thewh1teagle/kokoro-onnx releases) in $KOKORO_DIR.
"""
import argparse
import os
import re

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()


def two(n):
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t - 2] + ('-' + ONES[o] if o else '')


def year(m):
    y = int(m.group(0))
    hi, lo = divmod(y, 100)
    if lo == 0:
        return two(hi) + ' hundred'
    if 2000 <= y <= 2009:
        return 'two thousand' + (' and ' + ONES[lo] if lo else '')
    return two(hi) + (' oh ' + ONES[lo] if lo < 10 else ' ' + two(lo))


def speakable(line):
    return re.sub(r'\b(19|20)\d\d\b', year, line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vo_txt')
    ap.add_argument('out_wav')
    ap.add_argument('--voice', default='bm_george')
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--gap', type=float, default=0.8)
    a = ap.parse_args()

    d = os.environ.get('KOKORO_DIR', '.')
    tts = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    lines = [l.strip() for l in re.split(r'<break[^>]*/>', open(a.vo_txt).read()) if l.strip()]
    parts, sr = [], 24000
    for i, line in enumerate(lines):
        audio, sr = tts.create(speakable(line), voice=a.voice, speed=a.speed, lang='en-gb')
        parts.append(audio)
        if i < len(lines) - 1:
            parts.append(np.zeros(int(a.gap * sr), dtype=audio.dtype))
        print(f'beat {i + 1}: {len(audio) / sr:.2f}s  {line[:60]}')
    out = np.concatenate(parts)
    out = out / max(1e-6, np.abs(out).max()) * 0.9
    sf.write(a.out_wav, out, sr)
    print(f'{len(lines)} lines, {len(out) / sr:.1f}s -> {a.out_wav}')


if __name__ == '__main__':
    main()
