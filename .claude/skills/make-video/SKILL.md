---
name: make-video
description: Turn a request like "song X, these colours, this mood" into a beat-synced 3D ball-drop music video in this repo's style. Use whenever the user asks for a new video, a variation of one, or gives a song, colours, mood or vibe to build from.
---

# Make a ball-drop video from a request

The user describes a video in plain words (a song, colours, a mood or vibe, maybe jokes
or an end title). Your job is to translate that into a config at `videos/<name>.json`,
preview it, show them, then render it. The style is fixed: a glossy ball drops down a
spiral tower, bouncing once per melody note, through one or more worlds.

## 1. Pick the song

| They give you | Put in the config |
|---|---|
| A song in the library (`ls songs/`) | `"song": "can-can"` |
| A public-domain tune not in the library | Write it in note text (below), or add `songs/<id>.json` so it can be reused |
| A `.mid` file | Save it under `midi/` and use `"song": {"midi": "midi/x.mid", "maxSeconds": 40}` |

**Copyright:** only write melodies out as note data if they are public domain or the user
owns them. For a copyrighted pop song, ask for a MIDI file they have the rights to, or
suggest a public-domain alternative with the same vibe. Don't transcribe it from memory.

Note-text format (also the format of `songs/*.json`):

```json
{"melody": "E5/16 D#5 | E5 D#5 E5 B4 D5 C5 | A4/8 r/16 C4 E4 A4", "tempo": 70, "meter": "3/8",
 "pickup": "16+16", "chords": "- - Am E", "style": "arpeggio", "end": "chord"}
```

- **Notes:** `NOTE/DUR`. Durations are `1 2 4 8 16 32`, plus `.` for dotted and `t` for triplet.
  A note with no duration reuses the previous one. `r` is a rest, and `|` is just for reading.
- **Tempo:** `tempo` is quarter-note bpm. `tempoEnd` makes an accelerando, `ritard` slows
  the last bars, and `transpose` shifts by semitones.
- **Chords:** one per bar (the pickup counts as bar 0), `-` for no chord. Leave `chords`
  out and they are auto-harmonized from the detected key.
- **`style`** is the accompaniment: `arpeggio`, `march`, `oompah`, `pulse`, `waltz`, `pad` or `none`.
- **`end`** is `chord`, `crash` (knocks the scene's last object loose with a cymbal crash,
  and wakes the troll) or `none`.
- One bounce per melody note, so pick a melody that is mostly single notes. Notes closer
  together than 0.1 s are heard but not bounced on.

## 2. Map the vibe to settings

**Moods** (in `tools/moods.py`) set tempo, gravity/floatiness, camera, bloom, fog, reverb,
the default accompaniment and the default instruments:

- `playful`: the original video
- `dreamy`: slow, floaty, soft glow, lots of reverb, pads and music box
- `energetic`: faster, heavier gravity, synth lead, driving pulse with drums
- `spooky`: dark, foggy, heavy vignette, march, music box
- `epic`: wide camera, big reverb, brass march
- `chill`: slow, gentle marimba and pads

Any value can be overridden with `"moodOverrides": {"bloom": [0.5, 0.5, 1.6], "fog": [8, 30]}`.
`"tempo": 1.1` scales the speed on top of the mood.

**Kits** are the worlds: `salon` (piano keys, book stacks, candles, wooden pole), `cave`
(hex crystals, mushrooms, rock pole, troll) and `party` (jelly cubes, drums, balloons,
candy-striped pole, final stage with bowling pins). The final scene always ends on the
big stage drum, whatever its kit. Use 1–5 scenes; 3 is the classic length.

**Colours** are per scene. Turn the user's words into hex values:

```json
"colors": {"background": "#0b0630", "glow": "#00e5ff", "accent": "#c0c8ff",
           "objects": ["#ff2bd6", "#00e5ff"], "pole": "#ff2bd6", "stage": "#d81f4a", "rim": "#..."}
```

- **`background`** is the world colour.
- **`glow`** is the lit-object, light and particle colour.
- **`accent`** is the metal trim.
- **`objects`** colours the cubes, drums, books, mushroom caps and balloons.
- **`pole`** is the wood colour (salon), the rock colour (cave) or the stripe colour (party).

Only `background` and `glow` are needed; everything else is derived. Dark backgrounds
read best in salon/cave, and saturated mid-tones work in party.

**Other fields:**

- `"ball": {"color", "stripe"}`
- `"endText": "Fin."` (any short text)
- `"jokes": {"googlyEyes", "duck", "troll", "pins", "ending"}`: each is `true`/`false`.
  `duck` can also be a pitch letter (`"G"`) to limit the rubber duck to runs of that
  note; it takes at most 2 runs of three repeated notes.

Per scene you can also set `title`, `instrument` (`piano pluck brass bell musicbox
marimba lead`), `style`, `drums`, `end`, and `gap` (seconds for the dive into it).

One top-level `"song"` with several scenes splits the song at natural breaths. A `song`
per scene plays them as a medley, like the original.

## 3. Build it

```bash
node tools/make.mjs videos/<name>.json --preview   # score + check + synth + stills, about 1 min
```

- Look at `build/<name>/preview.png` yourself, and send it to the user with a one-line
  summary of the choices you made (song split, mood, colours). Offer to adjust before the
  long render.
- If the **checker fails**, it prints what and when. The usual fixes:
  - framing or clipping in a dense fast passage: a slightly lower `tempo` or `moodOverrides.drop`.
  - a huge empty tower: lower `moodOverrides.maxDrop` or `dwell`.
  - a far-off-screen ending: the gravity is extreme; bring `gravity` back toward 50.
- Never skip or weaken a check.

Then do the full render, about 1.6 s of wall time per frame with 3 workers, so 30–45 min
for a 40 s video. Run it in the background:

```bash
node tools/make.mjs videos/<name>.json --workers 3      # -> out/<name>.mp4
```

Afterwards, spot-check a few frames from the MP4 and send the video to the user. Commit
the config (and any new song or MIDI file). Commit the MP4 only if the user wants it in
the repo; GitHub rejects files over 100 MB.

## Example: "Jingle Bells but neon and hyped, end with Ho ho ho"

```json
{"title": "Neon Jingle", "mood": "energetic", "song": "jingle-bells",
 "scenes": [{"kit": "salon", "colors": {"background": "#0b0630", "glow": "#00e5ff"}},
            {"kit": "cave",  "colors": {"background": "#14002a", "glow": "#ff2bd6"}},
            {"kit": "party", "colors": {"background": "#00a36c", "glow": "#e6ff3a"}}],
 "ball": {"color": "#f2f7ff", "stripe": "#ff2bd6"}, "endText": "Ho ho ho."}
```
