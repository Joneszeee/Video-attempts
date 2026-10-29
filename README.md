# Ball Drop video generator

Beat-synced 3D ball-drop music videos. A glossy ball falls down a spiral tower and
bounces off one object on every melody note, through one or more worlds. Give it a song,
colours and a mood, and it builds the video in the style of `out/ball-drop.mp4`
(*Für Elise* → *Mountain King* → *Can-Can*).

It uses three.js, has no Blender and no samples, and all music is synthesized in NumPy
from note data. Output is 1080×1920 at 30 fps, with audio normalised to -14 LUFS.

## Make a video

```bash
npm install
node tools/make.mjs videos/neon-jingle.json --preview   # ~1 min: checks, audio, contact sheet of stills
node tools/make.mjs videos/neon-jingle.json             # full render -> out/neon-jingle.mp4
```

The full render takes about 1.6 s of wall time per frame with 3 parallel headless
browsers (`--workers N`), so 30–45 min for a 40 s video.

A video is one JSON file in `videos/`:

```json
{
  "title": "Neon Jingle",
  "mood": "energetic",
  "song": "jingle-bells",
  "scenes": [
    {"kit": "salon", "colors": {"background": "#0b0630", "glow": "#00e5ff"}},
    {"kit": "cave",  "colors": {"background": "#14002a", "glow": "#ff2bd6"}},
    {"kit": "party", "colors": {"background": "#00a36c", "glow": "#e6ff3a"}}
  ],
  "ball": {"color": "#f2f7ff", "stripe": "#ff2bd6"},
  "endText": "Ho ho ho."
}
```

| input | options |
|---|---|
| **song** | a library name (`songs/`: fur-elise, mountain-king, can-can, ode-to-joy, twinkle, jingle-bells, greensleeves); note text (`{"melody": "E5/16 D#5 \| E5 ...", "tempo": 70, "meter": "3/8"}`, chords optional, auto-harmonized when missing); or a MIDI file (`{"midi": "midi/x.mid", "maxSeconds": 40}`, melody = top line of the best track). One `song` is split across the scenes; or give each scene its own `song` for a medley. |
| **mood** | `playful` (the original), `dreamy`, `energetic`, `spooky`, `epic`, `chill`. Sets tempo, gravity, camera, bloom, fog, reverb, accompaniment and instruments. Fine-tune with `moodOverrides` and `tempo`. |
| **scenes** | 1–5 worlds, each a `kit` (`salon`, `cave`, `party`) with `colors` (`background`, `glow`, optional `accent`, `objects`, `pole`, `stage`, `rim`). Optional per scene: `instrument`, `style`, `drums`, `end` (`soft`/`crash`), `gap`. |
| **extras** | `ball` colours, `endText`, `jokes` (`googlyEyes`, `duck`, `troll`, `pins`, `ending`). |

Examples: `videos/classic.json` (the original), `videos/neon-jingle.json` (one song split
over three neon worlds), `videos/lullaby.json` (dreamy two-scene medley) and
`videos/midi-example.json` (from a MIDI file).

Working in Claude Code? Just describe the video ("Greensleeves, misty forest greens,
spooky"). The project skill `.claude/skills/make-video` tells Claude how to turn that into
a config, preview it and render it.

## How it works

```
videos/x.json ─► tools/score.py ─► build/x/score.json ─┬─► tools/check.mjs  (gate)
  songs/, midi/   music.py, moods.py   the single clock ├─► tools/synth.py   -> audio.wav
                                                       └─► src/ (three.js) -> tools/render.mjs -> frames
                                                            tools/mux.mjs   -> out/x.mp4 (-14 LUFS)
```

- **`tools/music.py`** handles note text, chords, key detection and auto-harmony, the
  accompaniment styles, and a minimal MIDI reader.
- **`tools/moods.py`** holds the mood presets and kit defaults, and derives the lighting
  from your colours (the kits' own colours reproduce the original look exactly).
- **`tools/score.py`** places every note and effect at an exact time: the scene splits,
  dive gaps, duck squeaks, crash and troll, and the ending gag.
- **`src/timeline.js`** is pure math shared by browser and checker. It:
  - solves the ball path backwards from the note times under one gravity;
  - makes repeated notes bounce in place;
  - makes long notes "dwell": the ball lands, rolls off the edge, and drops onto the
    next object on the next note.

  Every value is a function of `t`.
- **`tools/check.mjs`** must pass before anything renders:
  - each hit lands exactly on its note;
  - the ball never clips anything (sampled at 2 kHz);
  - the ball stays in frame.

Individual steps: `python3 tools/score.py videos/x.json`, `node tools/check.mjs x`,
`python3 tools/synth.py x`, `node tools/render.mjs --name x [--stills 3,12]`,
`node tools/mux.mjs x`.
