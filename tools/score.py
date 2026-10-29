#!/usr/bin/env python3
"""The score: the single clock for picture and sound.

    python3 tools/score.py videos/classic.json      -> build/classic/score.json

Reads a video config (songs, colours, mood, jokes) and writes the score: every melody
note becomes one ball bounce, the accompaniment and effects become audio events, and
the scene / ending markers drive the scene changes and the final gag. Every timestamp
in the video and the audio is read from this file.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from music import load_song, midi_name, detect_key, voice, tone  # noqa: E402
from moods import MOODS, KITS, KIT_ORDER, scene_look, scene_colors, bokeh_for, mote_for  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRST_HIT = 0.62       # the ball is released just before this and lands on the first note
MIN_DT = 0.1           # notes closer together than this are played but not bounced on
MAX_SCENES = 5
MAX_DUCKS = 2           # a joke is funnier twice than ten times

MEL_VEL = {"piano": 0.9, "pluck": 1.0, "brass": 0.85, "musicbox": 0.9, "bell": 0.8, "marimba": 0.95, "lead": 0.8}


def load_config(path):
    cfg = json.load(open(path))
    cfg.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    return cfg


def resolve_mood(cfg):
    name = cfg.get("mood", "playful")
    if name not in MOODS:
        raise SystemExit(f"unknown mood '{name}'. Moods: {', '.join(MOODS)}")
    m = json.loads(json.dumps(MOODS[name]))
    m.update(cfg.get("moodOverrides", {}))
    m["name"] = name
    m["tempo"] *= cfg.get("tempo", 1.0)
    return m


def split_song(song, parts):
    """Split one song into `parts` scenes at the longest notes nearest equal divisions."""
    mel = song["melody"]
    if parts <= 1:
        return [song]
    gaps = [(mel[i + 1]["t"] - mel[i]["t"], i) for i in range(len(mel) - 1)]
    total = mel[-1]["t"] - mel[0]["t"]
    cuts = []
    span = total / parts
    edge = max(2, len(mel) // (parts * 3))
    for k in range(1, parts):
        target = mel[0]["t"] + total * k / parts
        # prefer a long note (a natural breath) close to the even split point
        cands = [(g - 2.0 * abs(mel[i]["t"] - target) / span, i) for g, i in gaps
                 if edge <= i < len(mel) - edge and i not in cuts]
        if cands:
            cuts.append(max(cands)[1])
    cuts = sorted(set(cuts))
    bounds = [-1] + cuts + [len(mel) - 1]
    out = []
    for a, b in zip(bounds, bounds[1:]):
        t0 = mel[a + 1]["t"]
        t1 = mel[b + 1]["t"] if b + 1 < len(mel) else song["length"] + 10
        part = {"melody": [dict(x, t=x["t"] - t0) for x in mel[a + 1:b + 1]],
                "acc": [dict(x, t=x["t"] - t0) for x in song["acc"] if t0 - 1e-6 <= x["t"] < t1 - 1e-6],
                "events": [dict(x, t=x["t"] - t0) for x in song["events"] if t0 - 1e-6 <= x["t"] < t1 - 1e-6],
                "beats": [x - t0 for x in song["beats"] if t0 - 1e-6 <= x < t1 - 1e-6],
                "length": min(t1, song["length"]) - t0,
                "end": song["end"] if b == len(mel) - 1 else "soft",
                "endChord": song["endChord"] if b == len(mel) - 1 else [],
                "natGap": (mel[b + 1]["t"] - mel[b]["t"]) if b + 1 < len(mel) else None}
        part["title"] = song.get("title")
        out.append(part)
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cfg = load_config(sys.argv[1])
    name = cfg["name"]
    out_dir = os.path.join(ROOT, "build", name)
    os.makedirs(out_dir, exist_ok=True)
    mood = resolve_mood(cfg)
    fmt = {"width": 1080, "height": 1920, "fps": 30}
    fmt.update(cfg.get("format", {}))
    jokes = {"googlyEyes": True, "duck": True, "troll": True, "pins": True, "ending": True}
    jokes.update(cfg.get("jokes", {}))

    scenes_cfg = cfg.get("scenes") or [{}] * (3 if cfg.get("song") else 1)
    if not 1 <= len(scenes_cfg) <= MAX_SCENES:
        raise SystemExit(f"between 1 and {MAX_SCENES} scenes, please")
    scenes = []
    for i, sc in enumerate(scenes_cfg):
        kit = sc.get("kit", KIT_ORDER[i % 3])
        if kit not in KITS:
            raise SystemExit(f"unknown kit '{kit}'. Kits: {', '.join(KITS)}")
        scenes.append({"kit": kit, "cfg": sc})

    # ---------------------------------------------------------------- songs
    def inst_for(s):
        return s["cfg"].get("instrument") or mood["instruments"].get(s["kit"]) or KITS[s["kit"]]["instrument"]

    def style_for(s, song_spec):
        return (s["cfg"].get("style") or mood["styles"].get(s["kit"])
                or (song_spec.get("style") if isinstance(song_spec, dict) and "library" not in song_spec else None))

    from music import load_library
    def resolved_style(s, spec):
        st = style_for(s, spec)
        if st:
            return st
        if isinstance(spec, str):
            spec = {"library": spec}
        if "library" in spec:
            return load_library(spec["library"]).get("style") or KITS[s["kit"]]["style"]
        return spec.get("style") or KITS[s["kit"]]["style"]

    def drums_for(s):
        return s["cfg"].get("drums", s["kit"] == "party" or mood["name"] == "energetic")

    def song_for(s, spec):
        spec = {"library": spec} if isinstance(spec, str) else dict(spec)
        spec["style"] = resolved_style(s, spec)
        return load_song(spec, mood["tempo"], spec["style"], inst_for(s), drums_for(s))

    if cfg.get("song") and not any(s["cfg"].get("song") for s in scenes):
        whole = song_for(scenes[-1], cfg["song"])
        parts = split_song(whole, len(scenes))
        if len(parts) < len(scenes):
            scenes = scenes[:len(parts)]
        for s, p in zip(scenes, parts):
            s["song"] = p
    else:
        for i, s in enumerate(scenes):
            spec = s["cfg"].get("song") or cfg.get("song")
            if not spec:
                raise SystemExit(f"scene {i + 1} has no song")
            s["song"] = song_for(s, spec)

    # ---------------------------------------------------------------- transitions
    n = len(scenes)
    for i, s in enumerate(scenes):
        if i == n - 1:
            s["end"] = "final"
        else:
            s["end"] = s["cfg"].get("end") or ("crash" if s["song"]["end"] == "crash" else
                                               "crash" if (i == n - 2 and not any(x["song"]["end"] == "crash" for x in scenes[:-1])) else "soft")
    troll_scene = None
    if jokes["troll"]:
        crashes = [i for i, s in enumerate(scenes) if s["end"] == "crash"]
        if crashes:
            troll_scene = crashes[-1]

    # ---------------------------------------------------------------- assemble
    melody, notes, events, beats, sections = [], [], [], [], []
    dropped = 0
    t_last = None
    for i, s in enumerate(scenes):
        song = s["song"]
        mel = song["melody"]
        if not mel:
            raise SystemExit(f"scene {i + 1}: song has no melody notes")
        if i == 0:
            offset = FIRST_HIT - mel[0]["t"]
        else:
            gap = s["cfg"].get("gap") or max(mood["diveGap"], scenes[i - 1]["song"].get("natGap") or 0)
            offset = t_last + gap - mel[0]["t"]
        inst = inst_for(s)
        vel = MEL_VEL.get(inst, 0.9)
        # one bounce per note: too-close notes are still heard, just not bounced on
        kept = []
        for nt in mel:
            if kept and nt["t"] - kept[-1]["t"] < MIN_DT:
                dropped += 1
                notes.append({"t": round(nt["t"] + offset, 6), "midi": nt["midi"], "dur": nt["dur"], "inst": inst, "vel": vel * 0.8, "pan": 0})
                continue
            kept.append(nt)
        key_tonic, key_minor = detect_key([(x["midi"], x["dur"]) for x in kept])
        first_idx = len(melody)
        for j, nt in enumerate(kept):
            t = round(nt["t"] + offset, 6)
            last = j == len(kept) - 1
            tag = None
            dur = nt["dur"]
            mi = inst
            if last and s["end"] == "crash":
                tag, dur, mi = "crash", 1.8, "brass"
            elif last and s["end"] == "final":
                tag, dur = "final", max(dur, 1.4)
            melody.append({"t": t, "midi": nt["midi"], "name": midi_name(nt["midi"]), "dur": round(dur, 6), "scene": i + 1, "tag": tag})
            notes.append({"t": t, "midi": nt["midi"], "dur": round(dur, 6), "inst": mi, "vel": vel if tag != "crash" else 1.0, "pan": 0})
            if s["kit"] == "cave" and tag != "crash":
                notes.append({"t": t, "midi": nt["midi"] + 12, "dur": round(dur, 6), "inst": "bell", "vel": 0.35, "pan": 0})
        for a in song["acc"]:
            notes.append(dict(a, t=round(a["t"] + offset, 6)))
        for e in song["events"]:
            events.append(dict(e, t=round(e["t"] + offset, 6)))
        for b in song["beats"]:
            if b + offset <= kept[-1]["t"] + offset + 1e-6:
                beats.append({"t": round(b + offset, 6), "scene": i + 1})
        t_end = melody[-1]["t"]
        sc_mel = melody[first_idx:]

        # rubber duck: runs of three (or more) identical notes ("sol sol sol")
        if jokes["duck"]:
            want = jokes["duck"]
            for j in range(len(sc_mel) - 2):
                if sum(1 for e in events if e["type"] == "squeak") >= 3 * MAX_DUCKS:
                    break
                run = sc_mel[j:j + 3]
                if all(x["midi"] == run[0]["midi"] for x in run) and not any(x["tag"] for x in run) \
                        and (want is True or run[0]["name"].rstrip("-0123456789") == want):
                    for k, x in enumerate(run):
                        x["tag"] = "duck"
                        events.append({"t": x["t"], "type": "squeak", "vel": 0.8, "n": k})

        # how the scene ends
        if s["end"] == "crash":
            last_m = sc_mel[-1]["midi"]
            root = last_m % 12
            q = [0, 3, 7] if key_minor else [0, 4, 7]
            for m in [tone(root, 35), tone(root, 47)] + voice(root, q, 54) + [voice(root, q, 66)[0], voice(root, q, 66)[1]]:
                notes.append({"t": t_end, "midi": m, "dur": 2.2, "inst": "brass", "vel": 0.75, "pan": 0})
            notes.append({"t": t_end, "midi": tone(root, 35), "dur": 1.5, "inst": "timpani", "vel": 1.0, "pan": 0})
            events.append({"t": t_end, "type": "cymbal", "vel": 1.0})
            events.append({"t": t_end, "type": "shatter", "vel": 0.9})
            if i == troll_scene:
                events.append({"t": round(t_end + 0.55, 6), "type": "troll", "vel": 0.8})
        elif song.get("endChord"):
            big = s["end"] == "final" and mood["finalHit"] == "big"
            ch_inst = "brass" if (big and inst == "brass") else ("pad" if inst in ("bell", "musicbox", "marimba") else inst if inst in ("piano", "brass") else "piano")
            for m in song["endChord"]:
                notes.append({"t": t_end, "midi": m, "dur": 1.6, "inst": ch_inst, "vel": 0.6 if big else 0.5, "pan": -0.1})
            if big:
                events.append({"t": t_end, "type": "cymbal", "vel": 0.9})
                events.append({"t": t_end, "type": "kick", "vel": 1.0})
        sections.append({"scene": i + 1, "kit": s["kit"], "name": s["cfg"].get("title") or s["song"].get("title") or s["kit"],
                         "start": 0.0 if i == 0 else round(sc_mel[0]["t"], 6), "firstHit": sc_mel[0]["t"], "lastHit": t_end})
        if i < n - 1:
            nxt_gap = scenes[i + 1]["cfg"].get("gap") or max(mood["diveGap"], song.get("natGap") or 0)
            events.append({"t": round(t_end + 0.15, 6), "type": "whoosh", "vel": 0.6, "dur": nxt_gap})
        t_last = t_end

    # ---------------------------------------------------------------- ending
    tf = melody[-1]["t"]
    end_text = cfg.get("endText", "Fin.")
    if jokes["ending"]:
        # fall and return times scale with gravity so the gag has the same shape at any g
        k = math.sqrt(50.0 / mood["gravity"])
        roll_off = tf + 1.95
        boing = roll_off + 1.2 * k
        land = boing + 1.47 * k
        ending = {"rollStart": round(tf + 0.95, 6), "rollOff": round(roll_off, 6), "boing": round(boing, 6),
                  "land": round(land, 6), "fin": round(land + 0.43, 6)}
        events.append({"t": ending["rollStart"], "type": "roll", "vel": 0.5, "dur": ending["rollOff"] - ending["rollStart"]})
        events.append({"t": ending["boing"], "type": "boing", "vel": 0.9})
        events.append({"t": ending["land"], "type": "thump", "vel": 0.9})
    else:
        ending = {"fin": round(tf + 1.3, 6)}
    if end_text:
        events.append({"t": ending["fin"], "type": "fin", "vel": 0.5})
    duration = round(ending["fin"] + 3.0, 6)

    # ---------------------------------------------------------------- scenes' look
    out_scenes = []
    for s in scenes:
        user_colors = s["cfg"].get("colors", {})
        if isinstance(user_colors, str):
            user_colors = {"background": user_colors}
        colors = scene_colors(s["kit"], user_colors)
        out_scenes.append({"kit": s["kit"], "colors": colors, "look": scene_look(s["kit"], user_colors, mood),
                           "bokeh": bokeh_for(s["kit"], user_colors), "mote": mote_for(s["kit"], user_colors),
                           "particles": KITS[s["kit"]]["particles"]})

    events.sort(key=lambda e: e["t"])
    notes.sort(key=lambda x: x["t"])
    ball = {"color": "#f4e7cb", "stripe": "#c21f2c"}
    ball.update(cfg.get("ball", {}))
    score = {
        "name": name, "title": cfg.get("title", name), **fmt, "duration": duration,
        "gravity": mood["gravity"], "mood": mood, "scenes": out_scenes, "sections": sections,
        "ending": ending, "endText": end_text, "jokes": jokes, "trollScene": None if troll_scene is None else troll_scene + 1,
        "ball": ball, "melody": melody, "notes": notes, "events": events, "beats": beats,
    }
    with open(os.path.join(out_dir, "score.json"), "w") as f:
        json.dump(score, f, indent=1)

    print(f"score [{name}]: {len(melody)} bounces, {len(notes)} notes, {len(events)} events, "
          f"{duration:.2f} s ({math.ceil(duration * fmt['fps'])} frames), mood {mood['name']}")
    for sec in sections:
        print(f"  scene {sec['scene']} ({sec['kit']}): {sec['name']:<34} {sec['firstHit']:6.2f} -> {sec['lastHit']:6.2f} s")
    if dropped:
        print(f"  note: {dropped} melody notes were closer than {MIN_DT}s and are heard but not bounced on")
    if duration > 90:
        print(f"  warning: {duration:.0f} s is long; consider maxSeconds / a shorter song (render time ~{duration * 30 * 5 / 3 / 60:.0f} min)")


if __name__ == "__main__":
    main()
