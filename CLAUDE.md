# Theo6k reels

This repo turns a football script into a finished 9:16 animated reel in the Story Gaffer style
(see FORMAT.md). Brand: **theo6k**. Accent `#3FE0C5` (teal) for stadium videos, `#E9B949` (gold)
for theatre-stage videos (awards, "greatest ever", debates).

Two looks:
- **stadium**: 3D stadium with camera moves. Best for match and season stories. Demo: `videos/leicester`.
- **stage**: theatre with red curtains, gold balconies and a spotlight on each player. Best for awards, comparisons and "who's the best" stories. Demo: `videos/modric`.

## When the user sends a script (or a story)
1. Create `videos/<slug>/spec.json` (format below) and `videos/<slug>/vo.txt`.
   - One beat per sentence or short pair of sentences in the script. A good target is around 60–70s (about 11 beats, about 130 words of VO).
     The user found a 1:46 cut dragged, so keep every beat earning its place. Let the story set the exact length.
   - Varying scenes keeps it interesting (the user didn't want one look for the whole video). Move between stadium, stage and studio as the
     story moves, using `"cut": true` and new `players` on a scene change. Example: `videos/messi-91`.
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
   **Kokoro sounds flat and robotic (user feedback), so use it only for previews.** For finals, prefer ElevenLabs v3: write
   `videos/<slug>/vo_elevenlabs.md` with an [emotion] tag and a delivery note per line (example: `videos/messi-91/vo_elevenlabs.md`).
   The user uploads one clip per line (`01.mp3` …), and `build.py --vo <folder>` trims and joins them and syncs exactly.
   **If they upload one single file** (ElevenLabs pauses inside lines too, so pause detection is unreliable), align it against the
   Kokoro read of the same script: `python3 engine/tts.py vo.txt out/vo.wav` (reference), then
   `python3 engine/align_vo.py <their file> out/vo.wav`. This writes `<their file>.beats.json` (MFCC + DTW, snapped to pauses),
   which `build.py --vo <their file>` uses automatically.
4. Run `python3 build.py videos/<slug>/spec.json --vo <voice file> --out videos/<slug>/out/<slug>_final.mp4` to sync the beats to
   the voice, mix it with the SFX (normalised to -14 LUFS for Instagram) and send the final MP4.

`vo.txt` = the beat lines separated by `<break time="0.8s" />`. For a voiceover recorded elsewhere, the sync step finds those pauses,
so there must be exactly one clear pause between beats (the build fails with a clear message otherwise;
fallback: put `"timings": [secs per beat]` in the spec).

## Hook and end screen: required on every video
**Viral hook (beat 1, first 1–3 seconds).** It decides whether people keep watching. Checklist:
- **Open on the conflict, the shock or the payoff question.** Never open on scene-setting ("Seville, December 2012…" goes in beat 2).
  Good shapes include:
  - Two numbers that clash: "Messi's record: 91. Zambia say 107."
  - A claim that sounds wrong: "Haaland only scores against bad teams."
  - A stakes question: "Was the greatest season ever a fake?"
  - A "you've been lied to" angle: "Even Messi's number is wrong."
- **The VO's first words are the hook.** No intro and no "today we're looking at".
- **Frame 1 is the thumbnail.** The engine shows beat 1's headline and cards fully from frame 1. For boards or counters, set the card's `delay`
  to about -1.1 so the values are already readable on frame 1. Motion still comes from the zoom and highlight.
- **Keep the hook to one or two lines.** It should create an open loop that the last beat pays off (end on the question or the answer).
- Write 2–3 hook options and pick the strongest before building.

**End screen.** It's automatic: about 1.8s after the last line, the final shot softly blurs and darkens and a small brand card fades in
("theo6k · follow for more football stories"). Keep it subtle and short. Optional spec keys: `"outroText"`, `"outroDur"`, `"outro": false`.

## Visual richness: required on every video
- **Every video must be visually rich.** Every beat shows its information through an animated data graphic, effect or transition
  (counters, boards, tables, rulers, trophies, ball-numbers, strikes and corrections, camera moves, depth and lighting changes).
  Never a headline over a static background.
- **The user's references are examples, not a complete list.** Reuse the techniques below freely, but also **invent new, fitting
  graphics and transitions** in the same style when a story calls for them. Build them into the engine as new card types or effects and document them here.
  Aim for each video to bring at least one fresh idea, so the channel doesn't feel repetitive.
- A new screen recording or note from the user adds to this pool of ideas. It doesn't become a rigid rule. Pick what suits each story.

## Toolbox so far (reuse, combine, extend)
- **Constant small motion:** camera moves and zooms (`move`, `zoom`), built-in sway, counting numbers, scrambling flaps.
- **Depth:** blur and darken behind a card with `focus`, and add blurred foreground fans on stadium shots with `fans`.
- **Mood lighting:** `lights` below 1 for sombre or dramatic moments.
- **Meaningful accent colour:** a per-beat `accent`, e.g. red for "wrong" or "myth", gold for the answer.
- **Animated corrections:** `board` rows with `from` (red strike, then flip).
- **Guided attention:** `focusPath` walks a highlight down a list in time with the VO.
- **Continuity:** a card with the same `id` carries across beats instead of re-entering.
- **Scene variety:** stadium, stage and studio, with crowd colours per club.
- **60fps** is the default render.

Ideas not built yet (candidates for new tools):
- A pitch map with animated shot or pass trails, or goal locations as dots.
- A transfer-fee ticker or receipt that prints line by line.
- A head-to-head "tale of the tape" with bars sliding in from both sides.
- A calendar or season heatmap of goals.
- A photo-style polaroid flashback transition for history beats.
- A newspaper headline that spins in, for archive or claim beats.
- A world map with a route line, for transfers or tournaments.
- A whip-pan or zoom-through-the-number transition between scenes.
- A slow-motion replay of a ball path with a trail.

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
    "focus": 0.5,       // 0–1: blur + darken the scene behind the cards (eases between beats)
    "lights": 0.5,      // 0–1: scene lighting; < 1 = darker, hazy, moody
    "fans": true,       // stadium: blurred foreground crowd silhouettes
    "accent": "#FF4D5E",// headline accent colour for this beat only
    "sway": 1,          // camera handheld sway amount (0 = locked off)
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
- `board`: split-flap departure board, the star graphic of the free-kick reel. `rows: [{name, value, prefix, from, strike}]`, `label`,
  `focus` (row index, gold highlight) or `focusPath: [{t, row}]` (the highlight walks in time), `caption` + `captionAt` (pill underneath),
  `swapAt` (when corrections flip), `cols`/`vcols` (name and value widths). A row with `from` shows `from` first, then a red strike,
  then flips to `value`. Give it an `id` to carry it across beats: changed cells flip, the highlight slides and nothing re-enters.
- `meter`: a vertical tube filling with balls. `value`, `max`, `markers: [{label, value}]`, `icon: {kind, label, dx}`

## Files
- `engine/engine.js`: the canvas renderer (scenes, players, cards, text, timeline, SFX cue list)
- `engine/render.js`: Playwright frame capture to ffmpeg
- `engine/sfx.py`: synthesises the whoosh/tick/pop/impact/crowd track
- `build.py`: VO alignment, render, SFX and final mux. Outputs go to `videos/<slug>/out/` (gitignored).
