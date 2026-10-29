"""Music input for the generator: note-text notation, chords, auto-harmony,
accompaniment styles and MIDI import. Everything is turned into one internal song
format with absolute times in seconds:

    {"melody": [{"t", "midi", "dur"}],            # one bounce per entry
     "acc":    [{"t", "midi", "dur", "inst", "vel", "pan"}],
     "events": [{"t", "type", "vel", ...}],      # drums
     "beats":  [t, ...],                          # pulse the props dance to
     "length": seconds, "end": "chord" | "crash" | "none",
     "endChord": [midi, ...] }
"""
import json
import math
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTER = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_midi(tok):
    """'C#5' -> 73, 'E#4' -> 65, 'Bb3' -> 58, 'B#4' -> 72"""
    m = re.fullmatch(r"([A-Ga-g])([#b]*)(-?\d)", tok)
    if not m:
        raise ValueError(f"bad note '{tok}'")
    letter, acc, octv = m.groups()
    return 12 * (int(octv) + 1) + LETTER[letter.upper()] + acc.count("#") - acc.count("b")


def midi_name(m):
    return f"{SHARP_NAMES[m % 12]}{m // 12 - 1}"


# ------------------------------------------------------------------ notation
def parse_duration(d):
    """'8' eighth, '8.' dotted eighth, '8t' triplet eighth, '2..' -> length in quarter notes"""
    m = re.fullmatch(r"(\d+)(\.*)(t?)", d)
    if not m:
        raise ValueError(f"bad duration '{d}'")
    base = 4.0 / int(m.group(1))
    dots = len(m.group(2))
    q = base * (2 - 0.5 ** dots)
    if m.group(3):
        q *= 2 / 3
    return q


def parse_melody(text):
    """'E5/16 D#5 | E5 r/8 C4/16' -> [(midi or None, quarters)]. A token without a
    duration reuses the previous one. 'r' is a rest. Bar lines are ignored."""
    out, dur = [], 1.0
    for tok in text.replace("|", " ").split():
        if "/" in tok:
            p, d = tok.split("/", 1)
            dur = parse_duration(d)
        else:
            p = tok
        out.append((None if p.lower() in ("r", "rest", "-") else note_midi(p), dur))
    return out


def parse_meter(s):
    num, den = (int(x) for x in s.split("/"))
    return num * 4.0 / den, den   # bar length in quarters, beat denominator


QUAL = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11],
        "dim": [0, 3, 6], "aug": [0, 4, 8], "sus4": [0, 5, 7], "sus2": [0, 2, 7], "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9]}


def parse_chord(s):
    """'F#m7' -> (6, [0,3,7,10]); '-' or '' -> None"""
    if not s or s in ("-", "."):
        return None
    m = re.fullmatch(r"([A-G])([#b]?)(.*)", s)
    if not m or m.group(3) not in QUAL:
        raise ValueError(f"bad chord '{s}'")
    root = (LETTER[m.group(1)] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)) % 12
    return root, QUAL[m.group(3)]


# ------------------------------------------------------------------ harmony
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def detect_key(notes):
    """Krumhansl key finding on (midi, weight) pairs -> (tonic pc, is_minor)"""
    hist = [0.0] * 12
    for m, w in notes:
        hist[m % 12] += w
    best = None
    for tonic in range(12):
        for minor, prof in ((False, MAJOR_PROFILE), (True, MINOR_PROFILE)):
            rot = [prof[(i - tonic) % 12] for i in range(12)]
            ma, mb = sum(hist) / 12, sum(rot) / 12
            num = sum((a - ma) * (b - mb) for a, b in zip(hist, rot))
            den = math.sqrt(sum((a - ma) ** 2 for a in hist) * sum((b - mb) ** 2 for b in rot)) or 1
            r = num / den
            if best is None or r > best[0]:
                best = (r, tonic, minor)
    return best[1], best[2]


def harmonize(bars, tonic, minor):
    """Choose one chord per bar from the key's primary chords, by how well each fits the
    melody notes in that bar (duration-weighted, downbeat counts double)."""
    if minor:
        cands = [(0, QUAL["m"]), (5, QUAL["m"]), (7, QUAL[""]), (8, QUAL[""]), (3, QUAL[""])]
    else:
        cands = [(0, QUAL[""]), (5, QUAL[""]), (7, QUAL[""]), (9, QUAL["m"]), (2, QUAL["m"])]
    out, prev = [], None
    for i, bar in enumerate(bars):
        if not bar:
            out.append(prev)
            continue
        best = None
        for k, (deg, q) in enumerate(cands):
            root = (tonic + deg) % 12
            pcs = {(root + x) % 12 for x in q}
            score = 0.0
            for j, (m, w) in enumerate(bar):
                score += w * (2 if j == 0 else 1) * (1 if m % 12 in pcs else -0.6)
            score += 0.15 * (k == 0) + (0.1 if (root, tuple(q)) == prev else 0)
            if i == len(bars) - 1 and k == 0:
                score += 1.0     # cadence home
            if best is None or score > best[0]:
                best = (score, (root, tuple(q)))
        prev = best[1]
        out.append(prev)
    return [(r, list(q)) if r is not None else None for r, q in (c or (None, None) for c in out)]


def voice(root, q, low, count=None):
    """chord in root position, its root being the first one at or above `low`"""
    base = low + ((root - low) % 12)
    notes = [base + x for x in q]
    return notes[:count] if count else notes


def tone(pc, low):
    """the first midi note at or above `low` with pitch class pc"""
    return low + ((pc - low) % 12)


# ------------------------------------------------------------------ accompaniment styles
def accompany(style, bars, beat_time, bar_q, den, opts, inst, vel_base=1.0):
    """bars: list of (start_q, chord or None). beat_time(q) -> seconds.
    Returns acc notes, drum events and the dance beats."""
    acc, ev, beats = [], [], []
    name = style if isinstance(style, str) else style.get("name", "none")
    sopt = {} if isinstance(style, str) else style
    n_bars = len(bars)

    def add(q, m, dq, i, v, pan=0.0, dur_s=None):
        t = beat_time(q)
        d = dur_s if dur_s is not None else beat_time(q + dq) - t
        acc.append({"t": t, "midi": m, "dur": d, "inst": i, "vel": v * vel_base, "pan": pan})

    for bi, (q0, ch) in enumerate(bars):
        prog = bi / max(1, n_bars - 1)
        if name == "arpeggio":
            step = 0.25 if sopt.get("unit", 16) == 16 else 0.5
            count = sopt.get("notes", int(round(bar_q / step)))
            if ch:
                r, qq = ch
                pat = [tone(r, 40), tone(r + qq[2], 47), tone(r, 52), tone(r + qq[1], 55)]
                for k in range(count):
                    add(q0 + k * step, pat[k % 4 if count > 3 else k], 0, inst, 0.5, -0.25,
                        dur_s=beat_time(q0 + count * step) - beat_time(q0 + k * step) + 0.25)
            for k in range(int(round(bar_q / (4 / den)))):
                beats.append(beat_time(q0 + k * 4 / den))
        elif name == "march":
            nb = int(round(bar_q))
            for k in range(nb):
                q = q0 + k
                beats.append(beat_time(q))
                if not ch:
                    continue
                r = voice(ch[0], [0], 35)[0]
                add(q, r if k % 2 == 0 else r + 12, 0.55, "bassoon", 0.7 + 0.3 * prog, 0.15)
                if k == 0:
                    add(q, r, 0, "timpani", 0.4 + 0.5 * prog, 0.0, dur_s=0.3)
        elif name in ("oompah", "pulse"):
            n8 = int(round(bar_q * 2))
            for e in range(n8):
                q = q0 + e * 0.5
                beats.append(beat_time(q))
                if ch:
                    r, qq = ch
                    if name == "oompah":
                        if e % 2 == 0:
                            add(q, tone(r, 43) if e // 2 % 2 == 0 else tone(r + 7, 38), 0.45, "bass", 0.8, -0.1)
                        else:
                            for m in voice(r, qq[:3], 62):
                                add(q, m, 0.3, "chord", 0.35, 0.25)
                    else:
                        add(q, voice(r, [0], 36)[0] + (12 if e % 4 == 3 else 0), 0.4, "bass", 0.75, -0.1)
                        if e == 0:
                            for m in voice(r, qq[:3], 60):
                                add(q, m, min(bar_q, 2), "pad", 0.3, 0.2)
                if opts.get("drums", True):
                    if name == "oompah":
                        ev.append({"t": beat_time(q), "type": "kick" if e % 2 == 0 else "snare", "vel": 0.8 if e % 2 == 0 else 0.6})
                    else:
                        if e % 2 == 0:
                            ev.append({"t": beat_time(q), "type": "kick", "vel": 0.85})
                        if e % 4 == 2:
                            ev.append({"t": beat_time(q), "type": "snare", "vel": 0.6})
                    ev.append({"t": beat_time(q + 0.25), "type": "hat", "vel": 0.25})
            if opts.get("drums", True) and bi % 8 == 0:
                ev.append({"t": beat_time(q0), "type": "cymbal", "vel": 0.6})
        elif name == "waltz":
            nb = int(round(bar_q))
            for k in range(nb):
                q = q0 + k
                beats.append(beat_time(q))
                if not ch:
                    continue
                r, qq = ch
                if k == 0:
                    add(q, voice(r, [0], 36)[0], 0.9, "bass", 0.7, -0.1)
                else:
                    for m in voice(r, qq[:3], 57):
                        add(q, m, 0.6, inst if inst in ("piano", "musicbox", "marimba") else "chord", 0.3, 0.2)
        elif name == "pad":
            for k in range(int(round(bar_q))):
                beats.append(beat_time(q0 + k))
            if ch:
                r, qq = ch
                for m in voice(r, qq[:3], 55):
                    add(q0, m, bar_q, "pad", 0.32, 0.2, dur_s=beat_time(q0 + bar_q) - beat_time(q0) + 0.4)
                add(q0, voice(r, [0], 36)[0], bar_q, "pad", 0.4, -0.1, dur_s=beat_time(q0 + bar_q) - beat_time(q0) + 0.3)
        else:  # none
            for k in range(int(round(bar_q))):
                beats.append(beat_time(q0 + k))
    return acc, ev, beats


# ------------------------------------------------------------------ text songs
def load_library(name):
    path = os.path.join(ROOT, "songs", f"{name}.json")
    if not os.path.exists(path):
        have = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "songs")) if f.endswith(".json"))
        raise SystemExit(f"unknown song '{name}'. Library: {', '.join(have)}")
    return json.load(open(path))


def song_from_text(spec, tempo_scale=1.0, default_style="arpeggio", inst="piano", drums=True):
    """spec: {"melody", "tempo", "tempoEnd"?, "meter"?, "pickup"?, "chords"?, "style"?,
    "ritard"?, "end"?, "transpose"?}"""
    mel = parse_melody(spec["melody"])
    tr = spec.get("transpose", 0)
    mel = [(m + tr if m is not None else None, d) for m, d in mel]
    bar_q, den = parse_meter(spec.get("meter", "4/4"))
    pickup = spec.get("pickup", 0)
    if isinstance(pickup, str):
        pickup = sum(parse_duration(x) for x in pickup.split("+"))
    total_q = sum(d for _, d in mel)
    onsets, q = [], 0.0
    for m, d in mel:
        if m is not None:
            onsets.append(q)
        q += d
    last_onset = onsets[-1]

    bpm0 = spec["tempo"] * tempo_scale
    bpm1 = spec.get("tempoEnd", spec["tempo"]) * tempo_scale
    l0, l1 = 60 / bpm0, 60 / bpm1
    rit = spec.get("ritard", 0.0)
    rit_from = max(0.0, total_q - spec.get("ritardBars", 2) * bar_q)
    rate = math.log(l1 / l0) / max(last_onset, 1e-6) if l0 != l1 else 0.0

    def beat_time(qq):
        if rate:
            base = l0 * (math.exp(rate * qq) - 1) / rate
        else:
            base = l0 * qq
        if rit and qq > rit_from:
            x = qq - rit_from
            base += l0 * rit * x * x
        return base

    melody, q = [], 0.0
    for m, d in mel:
        if m is not None:
            melody.append({"t": beat_time(q), "midi": m, "dur": beat_time(q + d) - beat_time(q)})
        q += d

    # bars: the pickup (if any) is bar 0
    starts = ([0.0] if pickup else []) + [pickup + k * bar_q for k in range(int(math.ceil((total_q - pickup) / bar_q - 1e-6)))]
    bar_notes = [[] for _ in starts]
    q = 0.0
    for m, d in mel:
        if m is not None:
            bi = max(i for i, s in enumerate(starts) if s <= q + 1e-9)
            bar_notes[bi].append((m, d))
        q += d
    if spec.get("chords"):
        names = spec["chords"].replace("|", " ").split()
        chords = [parse_chord(names[i]) if i < len(names) else None for i in range(len(starts))]
    else:
        tonic, minor = detect_key([(m, d) for m, d in mel if m is not None])
        chords = harmonize(bar_notes, tonic, minor)
        if pickup:
            chords[0] = None
    # the final bar's chord rings out under the last note: handled by "end"
    style = spec.get("style", default_style)
    bars = list(zip(starts, chords))
    last_bar_chord = next((c for c in reversed(chords) if c), None)
    acc, ev, beats = accompany(style, bars[:-1] if spec.get("end", "chord") != "none" else bars,
                               beat_time, bar_q, den, {"drums": drums}, inst)
    end_chord = []
    if last_bar_chord:
        r, qq = last_bar_chord
        end_chord = [tone(r, 33), tone(r, 45)] + voice(r, qq[:3], 52)
    return {"melody": melody, "acc": acc, "events": ev, "beats": sorted(set(round(b, 6) for b in beats)),
            "length": beat_time(total_q), "end": spec.get("end", "chord"), "endChord": end_chord}


# ------------------------------------------------------------------ MIDI
def read_midi(path):
    """Minimal Standard MIDI File reader -> (notes [(t_sec, dur_sec, midi, vel, track, chan)], beats)"""
    data = open(path, "rb").read()
    if data[:4] != b"MThd":
        raise SystemExit(f"{path}: not a MIDI file")
    _, fmt, ntrk, div = struct.unpack(">IHHH", data[4:14])
    if div & 0x8000:
        raise SystemExit("SMPTE-timed MIDI files are not supported")
    pos, tracks = 14, []
    for _ in range(ntrk):
        while data[pos:pos + 4] != b"MTrk":
            pos += 8 + struct.unpack(">I", data[pos + 4:pos + 8])[0]
        ln = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        tracks.append(data[pos + 8:pos + 8 + ln])
        pos += 8 + ln
    tempos = [(0, 500000)]
    raw = []   # (tick, kind, a, b, track, chan)
    ts_num, ts_den = 4, 4
    for ti, tr in enumerate(tracks):
        p, tick, status = 0, 0, 0
        while p < len(tr):
            v = 0
            while True:
                c = tr[p]; p += 1
                v = (v << 7) | (c & 0x7F)
                if not c & 0x80:
                    break
            tick += v
            c = tr[p]
            if c & 0x80:
                status = c; p += 1
            if status == 0xFF:
                typ = tr[p]; p += 1
                ln = 0
                while True:
                    c = tr[p]; p += 1
                    ln = (ln << 7) | (c & 0x7F)
                    if not c & 0x80:
                        break
                body = tr[p:p + ln]; p += ln
                if typ == 0x51:
                    tempos.append((tick, int.from_bytes(body, "big")))
                elif typ == 0x58 and tick == 0:
                    ts_num, ts_den = body[0], 2 ** body[1]
            elif status in (0xF0, 0xF7):
                ln = 0
                while True:
                    c = tr[p]; p += 1
                    ln = (ln << 7) | (c & 0x7F)
                    if not c & 0x80:
                        break
                p += ln
            else:
                hi, ch = status & 0xF0, status & 0x0F
                a = tr[p]; p += 1
                b = 0
                if hi not in (0xC0, 0xD0):
                    b = tr[p]; p += 1
                if hi == 0x90 and b > 0:
                    raw.append((tick, "on", a, b, ti, ch))
                elif hi == 0x80 or (hi == 0x90 and b == 0):
                    raw.append((tick, "off", a, 0, ti, ch))
    tempos.sort()

    def sec(tick):
        s, last_t, last_us = 0.0, 0, 500000
        for tt, us in tempos:
            if tt >= tick:
                break
            s += (tt - last_t) * last_us / div / 1e6
            last_t, last_us = tt, us
        return s + (tick - last_t) * last_us / div / 1e6

    raw.sort(key=lambda e: (e[0], e[1] == "on"))
    open_, notes = {}, []
    for tick, kind, m, v, ti, ch in raw:
        key = (m, ti, ch)
        if kind == "on":
            open_.setdefault(key, []).append((tick, v))
        elif open_.get(key):
            t0, vel = open_[key].pop(0)
            notes.append((sec(t0), sec(tick) - sec(t0), m, vel, ti, ch))
    notes.sort()
    last_tick = max((e[0] for e in raw), default=0)
    beat_ticks = div * 4 / ts_den
    beats = [sec(int(k * beat_ticks)) for k in range(int(last_tick / beat_ticks) + 1)]
    return notes, beats


def song_from_midi(spec, tempo_scale=1.0, inst="piano"):
    """spec: {"midi": path, "track"?: n, "channel"?: n, "start"?: s, "maxSeconds"?: s,
    "transpose"?: n}. The melody is the top line ("skyline") of the chosen track; the
    rest of the (non-drum) notes become the accompaniment."""
    path = spec["midi"] if os.path.isabs(spec["midi"]) else os.path.join(ROOT, spec["midi"])
    notes, beats = read_midi(path)
    notes = [n for n in notes if n[5] != 9]      # drop GM drums
    if not notes:
        raise SystemExit("MIDI file has no pitched notes")
    t0 = spec.get("start", notes[0][0])
    t1 = t0 + spec.get("maxSeconds", 30)
    notes = [n for n in notes if t0 <= n[0] < t1]
    tracks = sorted({(n[4], n[5]) for n in notes})
    if "track" in spec:
        mel_src = [n for n in notes if n[4] == spec["track"] and n[5] == spec.get("channel", n[5])]
    else:
        # the melody track: high average pitch, plenty of notes, mostly one note at a time
        def rank(tc):
            ns = [n for n in notes if (n[4], n[5]) == tc]
            onsets = {round(n[0], 2) for n in ns}
            mono = len(onsets) / len(ns)
            return sum(n[2] for n in ns) / len(ns) + 6 * mono + min(len(ns), 80) / 10
        best = max(tracks, key=rank)
        mel_src = [n for n in notes if (n[4], n[5]) == best]
    # skyline: highest note per onset, then drop notes too close to bounce on
    by_on = {}
    for n in mel_src:
        k = round(n[0], 3)
        if k not in by_on or n[2] > by_on[k][2]:
            by_on[k] = n
    sky = [by_on[k] for k in sorted(by_on)]
    min_dt = 0.1
    melody, used = [], set()
    for n in sky:
        if melody and n[0] - melody[-1]["t"] - t0 < min_dt:
            continue
        melody.append({"t": n[0] - t0, "midi": n[2] + spec.get("transpose", 0), "dur": n[1]})
        used.add(id(n))
    acc = [{"t": n[0] - t0, "midi": n[2] + spec.get("transpose", 0), "dur": n[1],
            "inst": inst, "vel": 0.35 + 0.4 * n[3] / 127, "pan": -0.2}
           for n in notes if id(n) not in used]
    sc = 1 / tempo_scale
    for x in melody + acc:
        x["t"] *= sc
        x["dur"] *= sc
    bts = [(b - t0) * sc for b in beats if t0 <= b < t1]
    length = max(n["t"] + n["dur"] for n in melody)
    return {"melody": melody, "acc": acc, "events": [], "beats": bts, "length": length,
            "end": spec.get("end", "chord"), "endChord": []}


def load_song(spec, tempo_scale, default_style, inst, drums):
    """A song reference from a config: {"library": name, ...overrides} | {"melody": ...} | {"midi": ...}"""
    if isinstance(spec, str):
        spec = {"library": spec}
    if "library" in spec:
        base = load_library(spec["library"])
        base.update({k: v for k, v in spec.items() if k != "library"})
        spec = base
    song = song_from_midi(spec, tempo_scale, inst) if "midi" in spec else song_from_text(spec, tempo_scale, default_style, inst, drums)
    song["title"] = spec.get("title")
    return song
