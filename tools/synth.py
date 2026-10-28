#!/usr/bin/env python3
"""Synthesizes the soundtrack from build/score.json (no samples).

Every note and sound effect is placed at the exact time the score gives it, which is the
same time the picture uses for the matching bounce. Writes build/audio.wav (48 kHz stereo,
float). Loudness is normalised to -14 LUFS later, in tools/mux.mjs.
"""
import json
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
rng = np.random.default_rng(7)

score = json.load(open(os.path.join(ROOT, "build", "score.json")))
hits_path = os.path.join(ROOT, "build", "hits.json")
hits = json.load(open(hits_path))["hits"] if os.path.exists(hits_path) else []
DUR = score["duration"]
N = int(np.ceil(DUR * SR)) + SR

# three buses, one per world, each with its own room
dry = {s: np.zeros((2, N)) for s in (1, 2, 3)}
send = {s: np.zeros((2, N)) for s in (1, 2, 3)}
fx = np.zeros((2, N))   # sound effects (go to the party room unless stated)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def scene_at(t):
    secs = score["sections"]
    if t < secs[1]["firstHit"] - 0.05:
        return 1
    if t < secs[2]["firstHit"] - 0.05:
        return 2
    return 3


def place(sig, t, pan=0.0, gain=1.0, bus=None, rev=0.25):
    """Mix a mono signal into a bus at time t with constant-power panning."""
    i0 = int(round(t * SR))
    if i0 >= N:
        return
    sig = sig[: N - i0]
    a = (pan + 1) * np.pi / 4
    lr = np.array([np.cos(a), np.sin(a)])[:, None] * sig[None, :] * gain
    s = bus or scene_at(t)
    dry[s][:, i0:i0 + len(sig)] += lr
    send[s][:, i0:i0 + len(sig)] += lr * rev


def tvec(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a, d, s, r_start, r):
    """attack/decay/sustain, release beginning at r_start seconds (all in seconds)."""
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    e = np.where(t > r_start, e * np.exp(-(t - r_start) / r), e)
    return e


# --------------------------------------------------------------- filters
def fft_filter(x, fn):
    """Zero-phase filter: fn(freqs) -> gain."""
    n = len(x)
    nf = 1 << int(np.ceil(np.log2(n + 1)))
    X = np.fft.rfft(x, nf)
    f = np.fft.rfftfreq(nf, 1 / SR)
    return np.fft.irfft(X * fn(f), nf)[:n]


def lowpass(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def highpass(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def bandpass(x, fc, q):
    return fft_filter(x, lambda f: 1 / (1 + (q * (f / fc - fc / np.maximum(f, 1e-3))) ** 2))


# --------------------------------------------------------------- instruments
def partials(f0, d, amps, ratios, decays, detune=0.0, phase_rand=True):
    t = tvec(d)
    out = np.zeros_like(t)
    for a, r, tau in zip(amps, ratios, decays):
        f = f0 * r
        if f > SR * 0.45 or a <= 0:
            continue
        ph = rng.uniform(0, 2 * np.pi) if phase_rand else 0
        out += a * np.sin(2 * np.pi * f * t + ph) * np.exp(-t / tau)
        if detune:
            out += a * 0.7 * np.sin(2 * np.pi * f * (1 + detune) * t + ph * 1.3) * np.exp(-t / tau)
    return out


def piano(m, dur, vel):
    f0 = mtof(m)
    d = dur + 1.6
    n = np.arange(1, 16)
    B = 0.00035
    ratios = n * np.sqrt(1 + B * n * n)
    bright = 0.6 + 0.6 * vel
    amps = (1 / n ** 1.15) * np.exp(-n * f0 / (2600 * bright))
    base = 3.2 * (262 / f0) ** 0.45
    decays = base / (1 + 0.45 * (n - 1))
    s = partials(f0, d, amps, ratios, decays, detune=0.0009)
    t = tvec(d)
    s *= np.minimum(1, t / 0.003)
    s *= np.where(t > dur, np.exp(-(t - dur) / 0.35), 1)
    k = int(0.012 * SR)
    hammer = lowpass(rng.standard_normal(k), 2500 + f0) * np.exp(-np.arange(k) / (0.003 * SR)) * 0.25
    s[:k] += hammer
    return s * vel * 0.32


def pluck(m, dur, vel):
    """pizzicato strings + a reedy bassoon underneath (the troll king's march)"""
    f0 = mtof(m)
    d = max(dur, 0.12) + 0.5
    n = np.arange(1, 14)
    amps = (1 / n) * np.exp(-n * f0 / 2400)
    decays = 0.42 * (330 / f0) ** 0.3 / (1 + 0.5 * (n - 1))
    s = partials(f0, d, amps, n.astype(float), decays, detune=0.002)
    t = tvec(d)
    s *= np.minimum(1, t / 0.002)
    s += 0.6 * bassoon(m - 12, dur * 0.8, vel, length=d)
    return s * vel * 0.34


def bassoon(m, dur, vel, length=None):
    f0 = mtof(m)
    d = length or dur + 0.2
    t = tvec(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.3)
    ph = 2 * np.pi * f0 * np.cumsum(vib) / SR
    s = np.zeros_like(t)
    for k in range(1, 14):
        if f0 * k > 9000:
            break
        form = np.exp(-((f0 * k - 500) / 380) ** 2) * 1.4 + np.exp(-((f0 * k - 1150) / 300) ** 2) * 0.7 + 0.25
        s += form / k ** 0.8 * np.sin(k * ph)
    e = env_adsr(len(t), 0.025, 0.12, 0.75, dur, 0.06)
    return s * e * vel * 0.22


def bell(m, dur, vel):
    f0 = mtof(m)
    d = 1.8
    ratios = [1, 2.0, 2.76, 4.07, 5.40, 8.93]
    amps = [1, 0.35, 0.5, 0.25, 0.2, 0.08]
    decays = [1.4, 0.9, 0.6, 0.35, 0.25, 0.12]
    s = partials(f0, d, amps, ratios, decays)
    return s * np.minimum(1, tvec(d) / 0.001) * vel * 0.22


def brass(m, dur, vel):
    f0 = mtof(m)
    d = dur + 0.35
    t = tvec(d)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.8 * t) * np.clip((t - 0.15) / 0.3, 0, 1)
    ph = 2 * np.pi * f0 * np.cumsum(vib) / SR
    # brightness opens on the attack ("blat") and settles
    cutoff = 900 + 3200 * vel * (np.exp(-t / 0.08) * 0.8 + 0.5)
    s = np.zeros_like(t)
    for k in range(1, 30):
        if f0 * k > 12000:
            break
        s += (1 / k) * np.exp(-(f0 * k) / cutoff) * np.sin(k * ph)
    e = env_adsr(len(t), 0.018, 0.15, 0.7, dur, 0.08)
    return s * e * vel * 0.3


def bass(m, dur, vel):
    f0 = mtof(m)
    d = dur + 0.25
    t = tvec(d)
    s = np.sin(2 * np.pi * f0 * t) + 0.45 * np.sin(4 * np.pi * f0 * t) + 0.2 * np.sin(6 * np.pi * f0 * t)
    return s * env_adsr(len(t), 0.006, 0.12, 0.5, dur, 0.05) * vel * 0.35


def timpani(m, dur, vel):
    f0 = mtof(m + 12)
    d = 1.4
    t = tvec(d)
    f = f0 * (1 + 0.08 * np.exp(-t / 0.05))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.55)
    s += 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * np.exp(-t / 0.3)
    k = int(0.03 * SR)
    s[:k] += lowpass(rng.standard_normal(k), 800) * np.exp(-np.arange(k) / (0.006 * SR)) * 0.6
    return s * vel * 0.45


INST = {"piano": piano, "pluck": pluck, "bell": bell, "brass": brass, "bassoon": bassoon,
        "bass": bass, "timpani": timpani, "chord": brass, "crash": brass}

# --------------------------------------------------------------- drums & effects
def kick(vel):
    t = tvec(0.45)
    f = 45 + 95 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * vel * 0.8


def snare(vel):
    t = tvec(0.3)
    noise = bandpass(rng.standard_normal(len(t)), 3000, 0.6) * np.exp(-t / 0.09)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    return (noise * 0.7 + tone * 0.5) * vel * 0.6


def hat(vel):
    t = tvec(0.08)
    return highpass(rng.standard_normal(len(t)), 7000, 3) * np.exp(-t / 0.014) * vel * 0.32


def cymbal(vel):
    t = tvec(2.6)
    x = highpass(rng.standard_normal(len(t)), 4000, 2)
    ring = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3310, 4870, 5925, 7340, 8810)) * 0.08
    return (x * 0.4 + ring) * np.exp(-t / 0.6) * np.minimum(1, t / 0.002) * vel * 0.45


def whoosh(vel, d):
    t = tvec(d)
    x = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    # moving band-pass, done in overlapping blocks
    blk = 4096
    win = np.hanning(blk)
    for i0 in range(0, len(t) - blk, blk // 2):
        u = (i0 + blk / 2) / len(t)
        fc = 300 + 2200 * u ** 1.5
        out[i0:i0 + blk] += bandpass(x[i0:i0 + blk] * win, fc, 1.2)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * (0.4 + 0.6 * t / d)
    return out * e * vel * 0.5


def shatter(vel):
    d = 1.0
    out = np.zeros(int(d * SR))
    for k in range(26):
        t0 = abs(rng.normal(0, 0.09))
        f = rng.uniform(2200, 7500)
        p = partials(f, 0.35, [1, 0.5, 0.3], [1, 2.31, 3.9], [0.12, 0.07, 0.04]) * rng.uniform(0.3, 1)
        i0 = int(t0 * SR)
        out[i0:i0 + len(p)] += p[: len(out) - i0]
    t = tvec(d)
    out += highpass(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.06) * 0.4
    return out * vel * 0.35


def troll_grunt(vel):
    """a sleepy 'hrrmph?!' : low growl rising in pitch, through two vowel formants"""
    d = 0.7
    t = tvec(d)
    f0 = 85 + 70 * np.clip(t / 0.5, 0, 1) ** 2
    ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.03 * np.sin(2 * np.pi * 23 * t))) / SR
    src = sum(np.sin(k * ph) / k for k in range(1, 40))
    s = bandpass(src, 650, 2.5) * 1.0 + bandpass(src, 1100, 3) * 0.6 + bandpass(src, 250, 1.5) * 0.8
    e = np.minimum(1, t / 0.04) * np.exp(-np.maximum(0, t - 0.45) / 0.08)
    return s * e * vel * 0.9


def squeak(vel, n):
    """rubber duck squeak: a fast upward pitch bend with a nasal formant"""
    d = 0.22
    t = tvec(d)
    base = [1350, 1450, 1250][n % 3]
    f = base * (1 + 0.35 * np.sin(np.pi * np.clip(t / 0.16, 0, 1))) * (1 + 0.02 * np.sin(2 * np.pi * 38 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    s = bandpass(s, 2400, 1.0) + 0.3 * s
    e = np.minimum(1, t / 0.008) * np.exp(-np.maximum(0, t - 0.13) / 0.03)
    return s * e * vel * 0.45


def boing(vel):
    d = 1.2
    t = tvec(d)
    f = 160 * (1 + 0.6 * np.exp(-t / 0.5) * np.sin(2 * np.pi * 16 * t)) * (1 + 0.6 * np.clip(t / 0.9, 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    return s * np.minimum(1, t / 0.004) * np.exp(-t / 0.42) * vel * 0.6


def thump(vel):
    t = tvec(0.5)
    f = 55 + 70 * np.exp(-t / 0.03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    k = int(0.01 * SR)
    s[:k] += lowpass(rng.standard_normal(k), 1500) * 0.3
    return s * vel * 0.8


def roll(vel, d):
    t = tvec(d)
    x = lowpass(rng.standard_normal(len(t)), 300, 2)
    rate = 4 + 18 * (t / d) ** 2
    am = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    return x * am * np.minimum(1, t / d * 2.5) * vel * 0.9


def fin_chime(vel):
    """a little celesta arpeggio for the title card"""
    out = np.zeros(int(2.6 * SR))
    for k, m in enumerate([72, 76, 79, 84, 88]):
        p = bell(m, 1.0, 0.8) * (1 - 0.1 * k)
        i0 = int(k * 0.07 * SR)
        out[i0:i0 + len(p)] += p[: len(out) - i0]
    return out * vel * 1.4


def hit_transient(kind, speed):
    """the sound of the ball touching the object, under the note"""
    v = min(1.0, 0.25 + speed / 40)
    t = tvec(0.25)
    if kind in ("whiteKey", "blackKey", "books"):
        s = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.012) * 0.5
        if kind == "books":
            s += np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.04) * 0.6
        return s * v * 0.35
    if kind in ("crystal", "bigCrystal"):
        return partials(rng.uniform(5200, 6800), 0.25, [1, 0.4], [1, 2.4], [0.05, 0.03]) * v * 0.18
    if kind == "mushroom":
        f = 260 * (1 - 0.4 * np.clip(t / 0.08, 0, 1))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.05) * v * 0.35
    if kind == "jelly":
        f = 420 * (1 + 0.25 * np.sin(2 * np.pi * 28 * t) * np.exp(-t / 0.06)) * (1 - 0.35 * np.clip(t / 0.12, 0, 1))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) * v * 0.3
    if kind in ("drum", "stage"):
        return (np.sin(2 * np.pi * np.cumsum(110 + 90 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.09)
                + bandpass(rng.standard_normal(len(t)), 1800, 0.8) * np.exp(-t / 0.03) * 0.4) * v * 0.5
    return np.zeros(1)


# --------------------------------------------------------------- render
melody_pan = {round(h["t"], 6): max(-0.6, min(0.6, h["x"] * 0.6)) for h in hits}
melody_t = {round(n["t"], 6) for n in score["melody"]}
for nt in score["notes"]:
    fn = INST[nt["inst"]]
    sig = fn(nt["midi"], nt["dur"], nt["vel"])
    key = round(nt["t"], 6)
    pan = nt.get("pan", 0.0)
    is_mel = key in melody_t and nt["inst"] in ("piano", "pluck", "brass", "crash") and any(
        m["midi"] == nt["midi"] and round(m["t"], 6) == key for m in score["melody"])
    if is_mel:
        pan = melody_pan.get(key, 0.0)
    rev = {1: 0.28, 2: 0.42, 3: 0.18}[scene_at(nt["t"])]
    place(sig, nt["t"], pan=pan, gain=1.15 if is_mel else 1.0, rev=rev)

for h in hits:
    place(hit_transient(h["kind"], h["speed"]), h["t"], pan=max(-0.6, min(0.6, h["x"] * 0.6)), rev=0.1)

for ev in score["events"]:
    t, v, ty = ev["t"], ev["vel"], ev["type"]
    if ty == "kick":
        place(kick(v), t, 0.0, rev=0.05)
    elif ty == "snare":
        place(snare(v), t, 0.1, rev=0.15)
    elif ty == "hat":
        place(hat(v), t, 0.3, rev=0.05)
    elif ty == "cymbal":
        place(cymbal(v), t, -0.25, rev=0.3)
    elif ty == "whoosh":
        place(whoosh(v, ev["dur"]), t, 0.0, rev=0.4)
    elif ty == "shatter":
        place(shatter(v), t, 0.2, rev=0.5, bus=2)
    elif ty == "troll":
        place(troll_grunt(v), t, 0.35, rev=0.45, bus=2)
    elif ty == "squeak":
        place(squeak(v, ev.get("n", 0)), t, 0.15, rev=0.15)
    elif ty == "boing":
        place(boing(v), t, 0.2, rev=0.25, bus=3)
    elif ty == "thump":
        place(thump(v), t, 0.0, rev=0.2, bus=3)
    elif ty == "roll":
        place(roll(v, ev["dur"]), t, 0.25, rev=0.1, bus=3)
    elif ty == "fin":
        place(fin_chime(v), t, 0.0, rev=0.5, bus=3)


def room(rt60, predelay, damp, size_hz):
    """synthetic stereo impulse response: decorrelated noise, high frequencies die faster"""
    d = rt60 * 1.2
    t = tvec(d)
    ir = np.zeros((2, len(t)))
    bands = [(80, 400), (400, 1500), (1500, 5000), (5000, 20000)]
    for ch in range(2):
        x = rng.standard_normal(len(t))
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(len(t), 1 / SR)
        y = np.zeros(len(t))
        for lo, hi in bands:
            mid = (lo + hi) / 2
            b = np.fft.irfft(X * ((f >= lo) & (f < hi)), len(t))
            r = rt60 / (1 + damp * mid / 4000)
            y += b * np.exp(-6.91 * t / r)
        # early reflections
        for k in range(8):
            dt = predelay + rng.uniform(0.005, size_hz)
            y[int(dt * SR)] += rng.uniform(0.2, 0.5) * (1 if rng.random() > 0.5 else -1)
        y[: int(predelay * SR)] = 0
        ir[ch] = y
    return ir / np.sqrt(np.sum(ir ** 2) / 2) * 0.5


def convolve(x, ir):
    n = x.shape[1] + ir.shape[1]
    nf = 1 << int(np.ceil(np.log2(n)))
    out = np.zeros((2, x.shape[1]))
    for ch in range(2):
        out[ch] = np.fft.irfft(np.fft.rfft(x[ch], nf) * np.fft.rfft(ir[ch], nf), nf)[: x.shape[1]]
    return out


rooms = {1: room(1.6, 0.018, 1.0, 0.04), 2: room(3.2, 0.035, 0.6, 0.09), 3: room(1.1, 0.012, 1.4, 0.03)}
mix = np.zeros((2, N))
for s in (1, 2, 3):
    mix += dry[s] + convolve(send[s], rooms[s])
mix += fx
# clear out sub-sonic rumble
for ch in range(2):
    mix[ch] = highpass(mix[ch], 32, 4)

# gentle bus glue: soft-knee saturation only on the peaks
peak = np.max(np.abs(mix))
mix = mix / peak * 0.9
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
mix = mix[:, : int(DUR * SR)]
# fade the very last frames to digital silence
fade = int(0.4 * SR)
mix[:, -fade:] *= np.linspace(1, 0, fade)[None, :]

out = os.path.join(ROOT, "build", "audio.wav")
pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"audio -> {out}  ({mix.shape[1] / SR:.2f} s, {len(score['notes'])} notes, {len(score['events'])} effects)")
