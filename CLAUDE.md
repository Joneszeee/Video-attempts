# Theo6k reels

This repo turns a football script into a finished 9:16 animated reel in the Story Gaffer style
(see FORMAT.md). Brand: **theo6k**. Accent `#3FE0C5` (teal) for stadium videos, `#E9B949` (gold)
for theatre-stage videos (awards, "greatest ever", debates).

Two looks:
- **stadium**: 3D stadium with camera moves. Best for match and season stories. Demo: `videos/leicester`.
- **stage**: theatre with red curtains, gold balconies and a spotlight on each player. Best for awards, comparisons and "who's the best" stories. Demo: `videos/modric`.

## When the user sends a script (or a story)
1. Create `videos/<slug>/spec.json` (format below) and `videos/<slug>/vo.txt`.
   - One beat per sentence or short pair of sentences in the script. Aim for **60–70s: about 11 beats, about 130 words of VO**.
     Longer drags: the user found 1:46 boring. Every beat must add a new fact or twist. Merge explainer beats and keep lines short.
   - **Change scenes through the video.** Don't use one look for the whole thing. Move between stadium (crowd colours per club),
     stage and studio as the story moves (a different club or era means a new stadium, a debate means the stage). Put `"cut": true` on every scene change
     and give the new scene its own `players`. Example: `videos/messi-91`.
   - If they sent a story rather than a script, write the script first using PROMPT.md's rules.
   - Never invent stats. List anything you are not certain of and ask before rendering.
2. Render a preview with `python3 build.py videos/<slug>/spec.json --stills 1,5,9,...`, look at the stills, and fix layout problems
   (cards covering players, text overflow). Then run the full preview with `python3 build.py videos/<slug>/spec.json`.
3. Voiceover: either the user uploads their own (e.g. ElevenLabs, best quality), or generate it here with Kokoro
   (local, free; default voice `bm_george`, British male):
   ```
   pip install kokoro-onnx soundfile        # once per session; the user approved this
   # model files (about 350 MB) from github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into $KOKORO_DIR:
   #   kokoro-v1.0.onnx, voices-v1.0.bin
   python3 engine/tts.py videos/<slug>/vo.txt videos/<slug>/out/vo.wav
   ```
   `tts.py` turns years into words, fixes names via its `PRONOUNCE` table (add any name the voice gets wrong), puts a short gap
   between beats (`--gap 0.45`) and writes `vo.wav.beats.json` with exact line starts, which `build.py` uses for the sync.
   Other voices: `--voice bm_fable|am_michael|am_fenrir`, or blends like `bm_george:0.7+bm_fable:0.3`.
4. Run `python3 build.py videos/<slug>/spec.json --vo <voice file> --out videos/<slug>/out/<slug>_final.mp4` to sync the beats to
   the voice, mix it with the SFX (normalised to -14 LUFS for Instagram) and send the final MP4.

`vo.txt` = the beat lines separated by `<break time="0.8s" />`. For a voiceover recorded elsewhere, the sync step finds those pauses,
so there must be exactly one clear pause between beats (the build fails with a clear message otherwise;
fallback: put `"timings": [secs per beat]` in the spec).

## spec.json
```jsonc
{
  "brand": "theo6k", "accent": "#3FE0C5",
  "beats": [{
    "kicker": "Premier League 2015/16 · The odds",   // small caps label; inherited by later beats until changed
    "headline": "August 2015. Leicester at [5000-1].", // [brackets] = accent colour; <= ~9 words, ends with a full stop
    "vo": "Spoken line for this beat",                // drives estimated timing before the real VO exists
    "scene": { "type": "stadium", "crowd": ["#1d4fb8", "#ffffff"], "seed": 4 }, // or {"type":"stage"} / {"type":"studio"}; inherited
    "zoom": 1.1, "zoomFrom": 1.0,                     // stage only: camera push-in (instead of "camera")
    "camera": "aerial|high|stand|pitch|player|side" or { "pos": [x,y,z], "tgt": [x,y,z] },
    "camFrom": "...",   // starting camera for beat 1 or for a cut
    "cut": true,        // hard cut instead of a camera glide from the previous beat
    "move": 3,          // seconds for the camera move (default min(2.4, 80% of the beat))
    "players": [{ "name": "Vardy", "num": 9, "x": 0, "z": 0, "enter": "walk|fade", "fromZ": -4,
                  "pose": "arms_up", "trophy": true,
                  "sx": 0.5, "sy": 1610, "scale": 1,          // stage placement (fraction of width, feet y px)
                  "ghost": true,                               // translucent "past player"
                  "tag": 61, "tagLabel": "Goals", "tagDelay": 0.4, // gold number above the head
                  "kit": { "shirt": "#1b4fb5", "shorts": "#fff", "socks": "#1b4fb5", "text": "#fff",
                           "stripes": ["#a50044", "#004d98"] /* or "checks": [c1, c2] */ },
                  "skin": "#e7b593", "hair": "#4a3324" }],   // omitted = inherited, [] = none
    "confetti": true,
    "card": { ... } or "same" or [ "same", { ... } ]   // omitted = no card; arrays stack cards
  }]
}
```
World units are metres. The pitch is 68×105 and centred on the origin, the camera looks toward +z, and players face away from the camera.
Use the `player` camera for one hero player at (0,0). Cards then go at `"pos": "low"` so they sit below the player's feet.

Card types (`pos`: top | mid | center | low, or `y` in px):
- `big`: `value`, `prefix`/`suffix`/`decimals`/`comma`, `label`, `size`, `style: "accent"` (default is gold)
- `flip`: `groups: [{label, value, digits}]`, optional `side: {top, big, bottom}` (date box), `label`
- `table`: `rows: [{pos, name, color, color2, pts, highlight}]`, `pill: "+7"`, `label`
- `dots`: `n` (+`filled`) or `states: ["hit","miss",...]`, `label`, `caption`, `step`
- `vs`: `items: [{label, value, accent}]`, `label`
- `bars`: `rows: [{name, value, accent, color}]`, `max`, `label`
- `orb`: percent fill ball (Ballon d'Or style), `value`, `label`
- `ballnumber`: a number built from footballs that fly in, then scatter on exit. `text`, `size`, `label` (with `{n}` counting to `count`)
- `balls`: a row of ball icons popping in. `n`, `label`
- `ruler`: an age or year line. `min`, `max`, `step`, `left`/`right` end labels,
  `markers: [{value, label, accent, side: "above"|"below", len}]`, `bracket: {from, to, label, y}`, `style: "dots"` for a dotted timeline
- `trophies`: pedestals rising from the floor. `items: [{kind: cup|worldcup|ball|boot, sx, h, size, label, text}]`, `floor`.
  Use `h: 0` for a floating prop (e.g. a gold ball above a player's head)
- `meter`: a vertical tube filling with balls. `value`, `max`, `markers: [{label, value}]`, `icon: {kind, label, dx}`

## Files
- `engine/engine.js`: the canvas renderer (scenes, players, cards, text, timeline, SFX cue list)
- `engine/render.js`: Playwright frame capture to ffmpeg
- `engine/sfx.py`: synthesises the whoosh/tick/pop/impact/crowd track
- `build.py`: VO alignment, render, SFX and final mux. Outputs go to `videos/<slug>/out/` (gitignored).
