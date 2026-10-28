#!/usr/bin/env python3
"""The score: the single clock for picture and sound.

Writes build/score.json. Every timestamp in the video and the audio is read
from this file: the melody notes become ball bounces (one per note), the
accompaniment and sound effects become audio events, and the scene/ending
markers drive the scene changes and the final gag.

All three pieces are public domain and written here as note data.
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "score.json")

FPS = 30
WIDTH, HEIGHT = 1080, 1920
GRAVITY = 50.0  # scene units / s^2, the one gravity used everywhere

NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "E#": 5, "F": 5,
        "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def midi(name):
    """'C#5' -> 73"""
    pitch, octave = name[:-1], int(name[-1])
    return 12 * (octave + 1) + NOTE[pitch]


melody = []   # bounce events, in order
notes = []    # every audible note (melody included)
events = []   # non-note audio/visual cues
sections = []
beats = []    # strong beats, used for dancing props


def add_note(t, name_or_midi, dur, inst, vel=1.0, pan=0.0):
    m = name_or_midi if isinstance(name_or_midi, int) else midi(name_or_midi)
    notes.append({"t": round(t, 6), "midi": m, "dur": round(dur, 6), "inst": inst,
                  "vel": vel, "pan": pan})


def add_melody(t, name, dur, scene, inst, vel=1.0, tag=None):
    m = midi(name)
    melody.append({"t": round(t, 6), "midi": m, "name": name, "dur": round(dur, 6),
                   "scene": scene, "tag": tag})
    add_note(t, m, dur, inst, vel)


# ---------------------------------------------------------------- 1. Für Elise
# 3/8, unit = one sixteenth. (name, units). Pickup + bars 1-8.
FE_START = 0.62
FE_SIXTEENTH = 0.215
fur_elise = [
    ("E5", 1), ("D#5", 1),
    ("E5", 1), ("D#5", 1), ("E5", 1), ("B4", 1), ("D5", 1), ("C5", 1),
    ("A4", 3), ("C4", 1), ("E4", 1), ("A4", 1),
    ("B4", 3), ("E4", 1), ("G#4", 1), ("B4", 1),
    ("C5", 3), ("E4", 1), ("E5", 1), ("D#5", 1),
    ("E5", 1), ("D#5", 1), ("E5", 1), ("B4", 1), ("D5", 1), ("C5", 1),
    ("A4", 3), ("C4", 1), ("E4", 1), ("A4", 1),
    ("B4", 3), ("E4", 1), ("C5", 1), ("B4", 1),
    ("A4", 6),
]


def fe_time(u):
    """Sixteenth position -> seconds, with a gentle ritardando into the last bar."""
    rit_from = 2 + 6 * 6  # start of bar 7
    if u <= rit_from:
        return FE_START + u * FE_SIXTEENTH
    x = u - rit_from
    return FE_START + rit_from * FE_SIXTEENTH + FE_SIXTEENTH * (x + 0.035 * x * x)


u = 0
for name, units in fur_elise:
    t = fe_time(u)
    add_melody(t, name, fe_time(u + units) - t, 1, "piano", 0.9)
    u += units
FE_END_UNIT = u
fe_last = melody[-1]["t"]

# left hand: (bar, [notes on sixteenths 0,1,2])
fe_lh = {2: ["A2", "E3", "A3"], 3: ["E2", "E3", "G#3"], 4: ["A2", "E3", "A3"],
         6: ["A2", "E3", "A3"], 7: ["E2", "E3", "G#3"]}
for bar, ns in fe_lh.items():
    b0 = 2 + 6 * (bar - 1)
    for i, n in enumerate(ns):
        t = fe_time(b0 + i)
        add_note(t, n, fe_time(b0 + 3) - t + 0.25, "piano", 0.5, pan=-0.25)
# final A minor chord under the last A4
for n in ["A2", "E3", "A3", "C4"]:
    add_note(fe_last, n, 1.6, "piano", 0.55, pan=-0.2)
sections.append({"scene": 1, "name": "Für Elise", "start": 0.0, "firstHit": melody[0]["t"],
                 "lastHit": fe_last})

# ------------------------------------- 2. In the Hall of the Mountain King
# 4/4 in B minor, unit = one eighth, accelerating the whole way.
MK_GAP = 1.42          # the dive from the salon into the cave
MK_START = fe_last + MK_GAP
MK_FROM, MK_TO = 0.26, 0.115   # eighth-note length at the start / at the crash
phrase = [
    ("B3", 1), ("C#4", 1), ("D4", 1), ("E4", 1), ("F#4", 1), ("D4", 1), ("F#4", 2),
    ("E#4", 1), ("C#4", 1), ("E#4", 2), ("E4", 1), ("C4", 1), ("E4", 2),
    ("B3", 1), ("C#4", 1), ("D4", 1), ("E4", 1), ("F#4", 1), ("D4", 1), ("F#4", 1), ("B4", 1),
    ("A4", 1), ("F#4", 1), ("D4", 1), ("F#4", 1), ("A4", 4),
]


def up(n, octaves=1):
    return n[:-1] + str(int(n[-1]) + octaves)


mk_seq = list(phrase) + [(up(n), d) for n, d in phrase[:-1]] + [("B5", 4)]
MK_UNITS = sum(d for _, d in mk_seq) - 4  # position of the crash
MK_RATE = math.log(MK_TO / MK_FROM) / MK_UNITS


def mk_time(u):
    """Eighth position -> seconds. Eighth length shrinks exponentially (accelerando)."""
    return MK_START + MK_FROM * (math.exp(MK_RATE * u) - 1.0) / MK_RATE


u = 0
for i, (name, units) in enumerate(mk_seq):
    t = mk_time(u)
    last = i == len(mk_seq) - 1
    dur = 1.8 if last else mk_time(u + units) - t
    add_melody(t, name, dur, 2, "crash" if last else "pluck", 1.0,
               tag="crash" if last else None)
    if not last:
        add_note(t, midi(name) + 12, dur, "bell", 0.35)   # crystal shimmer on top
    u += units
mk_last = melody[-1]["t"]

# bassoon/cello on the beats: root per bar (B, F#/C#, B, F#)
roots = ["B1", "F#1", "B1", "F#1"]
for bar in range(8):
    for beat in range(4):
        uu = bar * 8 + beat * 2
        if uu >= MK_UNITS:
            break
        t = mk_time(uu)
        r = roots[bar % 4] if beat % 2 == 0 else up(roots[bar % 4])
        add_note(t, r, (mk_time(uu + 2) - t) * 0.55, "bassoon", 0.7 + 0.3 * bar / 8, pan=0.15)
        if beat == 0:
            add_note(t, roots[bar % 4], 0.3, "timpani", 0.4 + 0.5 * bar / 8)
        beats.append({"t": round(t, 6), "scene": 2})
# the crash itself: full B minor chord, cymbal, timpani
for n in ["B1", "B2", "F#3", "B3", "D4", "F#4", "B4", "D5"]:
    add_note(mk_last, n, 2.2, "brass", 0.75)
add_note(mk_last, "B1", 1.5, "timpani", 1.0)
events.append({"t": mk_last, "type": "cymbal", "vel": 1.0})
events.append({"t": mk_last, "type": "shatter", "vel": 0.9})
events.append({"t": mk_last + 0.55, "type": "troll", "vel": 0.8})
sections.append({"scene": 2, "name": "In the Hall of the Mountain King", "start": MK_START,
                 "firstHit": MK_START, "lastHit": mk_last})

# --------------------------------------------------------------- 3. Can-Can
# 2/4 in C, unit = one eighth.
CC_GAP = 1.30
CC_START = mk_last + CC_GAP
CC_EIGHTH = 0.19
can_can = [
    ("C5", 4),
    ("C5", 1), ("D5", 1), ("F5", 1), ("E5", 1),
    ("D5", 1), ("G5", 1), ("G5", 2),
    ("G5", 1), ("A5", 1), ("E5", 1), ("F5", 1),
    ("D5", 2), ("D5", 2),
    ("D5", 1), ("F5", 1), ("E5", 1), ("D5", 1),
    ("C5", 1), ("C6", 1), ("B5", 1), ("A5", 1),
    ("G5", 1), ("F5", 1), ("E5", 1), ("D5", 1),
    ("C5", 4),
    ("C5", 1), ("D5", 1), ("F5", 1), ("E5", 1),
    ("D5", 1), ("G5", 1), ("G5", 2),
    ("G5", 1), ("A5", 1), ("E5", 1), ("F5", 1),
    ("D5", 1), ("G5", 1), ("E5", 1), ("D5", 1),
    ("C5", 4),
]


def cc_time(u):
    return CC_START + u * CC_EIGHTH


u = 0
cc_first_index = len(melody)
for i, (name, units) in enumerate(can_can):
    t = cc_time(u)
    last = i == len(can_can) - 1
    add_melody(t, name, 1.4 if last else units * CC_EIGHTH, 3, "brass", 0.85,
               tag="final" if last else None)
    u += units
CC_UNITS = u
cc_last = melody[-1]["t"]

# "sol sol sol": every run of three G5s lands on the rubber duck, which squeaks
cc = melody[cc_first_index:]
for i in range(len(cc) - 2):
    if all(cc[i + k]["name"] == "G5" for k in range(3)):
        for k in range(3):
            cc[i + k]["tag"] = "duck"
            events.append({"t": cc[i + k]["t"], "type": "squeak", "vel": 0.8, "n": k})

# oom-pah accompaniment, snare backbeat, cymbal at phrase starts
harmony = ["C", "C", "G", "C", "G", "G", "C", "G", "C", "C", "G", "C", "G", "C"]
chords = {"C": (["C3", "G2"], ["E4", "G4", "C5"]), "G": (["G2", "D3"], ["D4", "F4", "B4"])}
for bar, h in enumerate(harmony):
    bass, chord = chords[h]
    for e in range(4):
        t = cc_time(bar * 4 + e)
        if bar == len(harmony) - 1 and e > 0:
            break
        beats.append({"t": round(t, 6), "scene": 3})
        if e % 2 == 0:
            add_note(t, bass[e // 2], CC_EIGHTH * 0.9, "bass", 0.8, pan=-0.1)
            events.append({"t": round(t, 6), "type": "kick", "vel": 0.8})
        else:
            for n in chord:
                add_note(t, n, CC_EIGHTH * 0.6, "chord", 0.35, pan=0.25)
            events.append({"t": round(t, 6), "type": "snare", "vel": 0.6})
        events.append({"t": round(t + CC_EIGHTH / 2, 6), "type": "hat", "vel": 0.25})
    if bar in (0, 8):
        events.append({"t": round(cc_time(bar * 4), 6), "type": "cymbal", "vel": 0.6})
# final chord
for n in ["C2", "C3", "G3", "C4", "E4", "G4", "C5"]:
    add_note(cc_last, n, 1.5, "brass", 0.7)
events.append({"t": cc_last, "type": "cymbal", "vel": 0.9})
events.append({"t": cc_last, "type": "kick", "vel": 1.0})
sections.append({"scene": 3, "name": "Can-Can", "start": CC_START, "firstHit": CC_START,
                 "lastHit": cc_last})

# dives: a whoosh as the ball drops into each new world
events.append({"t": fe_last + 0.15, "type": "whoosh", "vel": 0.6, "dur": MK_GAP})
events.append({"t": mk_last + 0.15, "type": "whoosh", "vel": 0.6, "dur": CC_GAP})

# ------------------------------------------------------------------ ending
# The ball sits on the final drum, rolls off, silence, boings back, lands, "Fin."
ending = {
    "rollStart": round(cc_last + 0.95, 6),   # starts creeping toward the edge
    "rollOff": round(cc_last + 1.95, 6),     # leaves the edge
    "boing": round(cc_last + 3.15, 6),       # hits something springy far below
    "land": round(cc_last + 4.62, 6),        # back on the drum
    "fin": round(cc_last + 5.05, 6),
}
events.append({"t": ending["rollStart"], "type": "roll", "vel": 0.5,
               "dur": ending["rollOff"] - ending["rollStart"]})
events.append({"t": ending["boing"], "type": "boing", "vel": 0.9})
events.append({"t": ending["land"], "type": "thump", "vel": 0.9})
events.append({"t": ending["fin"], "type": "fin", "vel": 0.5})
duration = round(ending["fin"] + 3.0, 6)

events.sort(key=lambda e: e["t"])
notes.sort(key=lambda n: n["t"])

score = {
    "fps": FPS, "width": WIDTH, "height": HEIGHT, "duration": duration,
    "gravity": GRAVITY, "sections": sections, "ending": ending,
    "melody": melody, "notes": notes, "events": events, "beats": beats,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(score, f, indent=1)

print(f"score: {len(melody)} bounces, {len(notes)} notes, {len(events)} events, "
      f"{duration:.2f} s ({math.ceil(duration * FPS)} frames)")
for s in sections:
    print(f"  scene {s['scene']}: {s['name']:<34} {s['firstHit']:6.2f} -> {s['lastHit']:6.2f} s")
print(f"  ending: {ending}")
