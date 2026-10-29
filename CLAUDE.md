# Theo6k reels

This repo turns a football script into a finished 9:16 animated reel in the Story Gaffer style
(see FORMAT.md). Brand: **theo6k**, accent `#3FE0C5`.

## When the user sends a script (or a story)
1. Create `videos/<slug>/spec.json` (format below) and `videos/<slug>/vo.txt`.
   - One beat per sentence or short pair of sentences in the script. 4–6 beats, 25–45s total.
   - If they sent a story rather than a script, write the script first using PROMPT.md's rules.
   - Never invent stats. List anything you are not certain of and ask before rendering.
2. Render a preview with `python3 build.py videos/<slug>/spec.json --stills 1,5,9,...`, look at the stills, and fix layout problems
   (cards covering players, text overflow). Then run the full preview with `python3 build.py videos/<slug>/spec.json`.
3. Send the user the preview MP4 plus `vo.txt`. They generate the voiceover elsewhere (e.g. ElevenLabs) and upload it.
4. Run `python3 build.py videos/<slug>/spec.json --vo <upload>` to sync the beats to the voice and mix it in. Send the final MP4.

`vo.txt` = the beat lines separated by `<break time="0.8s" />`. The sync step finds those pauses,
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
    "scene": { "type": "stadium", "crowd": ["#1d4fb8", "#ffffff"], "seed": 4 }, // or {"type":"studio"}; inherited
    "camera": "aerial|high|stand|pitch|player|side" or { "pos": [x,y,z], "tgt": [x,y,z] },
    "camFrom": "...",   // starting camera for beat 1 or for a cut
    "cut": true,        // hard cut instead of a camera glide from the previous beat
    "move": 3,          // seconds for the camera move (default min(2.4, 80% of the beat))
    "players": [{ "name": "Vardy", "num": 9, "x": 0, "z": 0, "enter": "walk|fade", "fromZ": -4,
                  "pose": "arms_up", "trophy": true,
                  "kit": { "shirt": "#1b4fb5", "shorts": "#fff", "socks": "#1b4fb5", "text": "#fff" },
                  "skin": "#e7b593", "hair": "#4a3324" }],   // omitted = inherited, [] = none
    "confetti": true,
    "card": { ... } or "same"   // omitted = no card
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

## Files
- `engine/engine.js`: the canvas renderer (scenes, players, cards, text, timeline, SFX cue list)
- `engine/render.js`: Playwright frame capture to ffmpeg
- `engine/sfx.py`: synthesises the whoosh/tick/pop/impact/crowd track
- `build.py`: VO alignment, render, SFX and final mux. Outputs go to `videos/<slug>/out/` (gitignored).
