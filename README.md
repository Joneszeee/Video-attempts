# Ball Drop: a beat-synced 3D music video

A glossy cream-and-red ball falls down a spiral tower and bounces off one object on every
melody note: *Für Elise* in a dusk music salon, an accelerating *In the Hall of the
Mountain King* in a crystal cave, and the *Can-Can* at a toy party. It's built with
three.js and has no Blender and no samples: all music is note data synthesized in NumPy.

1080×1920 · 30 fps · ~42 s · output: `out/ball-drop.mp4`

## Build

```bash
npm install
npm run build          # score -> check -> synth -> render (+ mux)
```

Steps on their own:

| step | command | output |
|---|---|---|
| score | `python3 tools/score.py` | `build/score.json`, the single clock |
| check | `node tools/check.mjs` | fails the build if any rule is broken; writes `build/hits.json` |
| synth | `python3 tools/synth.py` | `build/audio.wav` |
| render | `node tools/render.mjs --workers 3` | `build/video.mp4`, then `out/ball-drop.mp4` |
| mux | `node tools/mux.mjs` | two-pass loudnorm to -14 LUFS / -1 dBTP, muxed with the video |

Previews: `node tools/render.mjs --stills 3.2,12,30` writes PNGs to `build/stills/`.
You can also serve the repo root and open `index.html?t=12.3` for a still, or
`index.html?play` for real-time playback.

## How it fits together

- **`tools/score.py`** writes every note (melody, accompaniment, drums) and every
  sound-effect cue with its exact time. Picture and sound both read this file.
- **`src/timeline.js`** is pure math shared by the browser and the checker. It:
  - assigns each melody note an object. Repeated notes reuse the same object, so they
    bounce in place.
  - solves the layout backwards from the note times: the final stage is fixed at the
    bottom, and each earlier contact point is placed by stepping back through the note
    intervals. Each drop is a fraction of `g·dt²/2`, so every flight is a true parabola
    under the one gravity that takes exactly the note interval.
  - covers squash and stretch, object dip and spring-back, glow, knocked-loose objects,
    the smoothed orbit camera, and the ending gag.

  Every value is a function of `t`. There is no per-frame state, so any frame renders
  on its own.
- **`src/main.js` + `src/builders.js`** build the three.js scene: PBR clearcoat
  materials, PCF soft shadows, ACES tone mapping, bloom thresholded so only lit objects
  glow, a vignette and grain, and googly eyes that track the ball.
- **Scene changes**: the ball knocks the last object loose and dives through a dark gap
  into the next world. There are no crossfades.

## Pre-render checks (`tools/check.mjs`)

- Every hit lands exactly on its note: the ball is at the contact point at the note time
  (error 0), the object is at rest, the ball arrives moving down and leaves moving up,
  and the audio has the note at that same timestamp.
- The ball never clips anything: it is sampled at 2 kHz against every object collider,
  the pole, support arms and props (troll, pins, balloons, candles).
- The ball stays in frame: every frame is projected through the real camera. The only
  exemption is the scripted roll-off at the end, where the ball deliberately leaves.

## The jokes

- Googly eyes on books, mushrooms, jelly cubes, the duck, the troll and the bowling
  pins all follow the ball.
- A rubber duck takes every "sol sol sol" (G G G) in the Can-Can and squeaks.
- A troll sleeps under the last crystal (Zzz). The final crash wakes it, and its
  nightcap flies off.
- A chorus line of bowling pins does the can-can on the final drum.
- Ending: the ball rolls off, silence, *boing*, it lands, **Fin.**
