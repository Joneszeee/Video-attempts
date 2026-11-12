# Theo6k reels

This repo turns a football script into a finished 9:16 animated reel in the Story Gaffer style
(see FORMAT.md). Brand: **theo6k**, shown as a **blue shirt with yellow trim and a yellow 6** next to the name (user's choice; default
`brandStyle: "shirt"`, also on the end screen). Other styles exist (`classic`, `pill`, `ball`, `scoreboard`, `marker`; see `videos/_mock-brand`). Accent `#3FE0C5` (teal) for stadium videos, `#E9B949` (gold)
for theatre-stage videos (awards, "greatest ever", debates).

Two looks:
- **stadium**: 3D stadium with camera moves. Best for match and season stories. Demo: `videos/leicester`.
- **stage**: theatre with red curtains, gold balconies and a spotlight on each player. Best for awards, comparisons and "who's the best" stories. Demo: `videos/modric`.

## When the user asks for video ideas
Give **10 ideas: 7 from recent news and 3 evergreen** (user preference). For the 7, search widely first: this week's results, records,
awards, transfers, controversies and articles across the major leagues and international football. Pick the stories that are most video-worthy for
virality: surprise, conflict, a record, a big name, and a clear hook number. For each idea give the hook line, the story in one line, the
visuals (which tools or backlog items), and what still needs fact-checking. End with your top pick and why, and list the sources.

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
   **The user records on Eleven v4.** v4 audio tags: one emotion tag per sentence or segment (not "[proud, building]"), optional delivery tags
   such as `[slowly]` mid-line, and punctuation for pacing (… to hang, full stops for beats). ElevenLabs has no separate field for delivery notes,
   so build the notes into the text itself and keep the words identical to `vo.txt` so the sync still works.
   **Kokoro sounds flat and robotic (user feedback), so use it only for previews.** For finals, prefer ElevenLabs (v4 now): write
   `videos/<slug>/vo_elevenlabs.md` with an [emotion] tag and a delivery note per line (example: `videos/messi-91/vo_elevenlabs.md`).
   The user uploads one clip per line (`01.mp3` …), and `build.py --vo <folder>` trims and joins them and syncs exactly.
   **If they upload one single file** (ElevenLabs pauses inside lines too, so pause detection is unreliable), align it against the
   Kokoro read of the same script: `python3 engine/tts.py vo.txt out/vo.wav` (reference), then
   `python3 engine/align_vo.py <their file> out/vo.wav`. This writes `<their file>.beats.json` (MFCC + DTW, snapped to pauses),
   which `build.py --vo <their file>` uses automatically.
   **Never send the user a video with an AI voice of ours (user instruction).** They voice every script themselves in ElevenLabs.
   Deliver `vo_elevenlabs.md` plus a preview with **SFX only**: `build.py --vo out/vo.wav --mute-vo` uses the Kokoro read just for
   timing (and as the alignment reference later) and leaves it out of the mix.
4. When their voiceover arrives, run `python3 build.py videos/<slug>/spec.json --vo <voice file> --out videos/<slug>/out/<slug>_final.mp4`
   to sync the beats to the voice, mix it with the SFX (normalised to -14 LUFS for Instagram) and send the final MP4.
   **The voice must sit clearly on top (user: SFX drowned it out).** `build.py` levels the voice to -16 LUFS, puts the SFX 12 dB under it
   (`SFX_UNDER`) and ducks them further while the voice speaks. To fix only the mix without re-rendering, add `--audio-only`.

5. **With every final, give the YouTube post** (also saved as `videos/<slug>/youtube.md`): 3 title options, **each in its own code block** so it can be
   copied in one tap, a description (hook sentence, key facts, a question for comments, "Follow for more football stories in under a minute.", 3 hashtags),
   comma-separated tags **filling YouTube's 500-character tag box (aim for 490–500 by YouTube's count: each tag's length, +2 for a tag with a space, +1 per comma; user asked)**, and a pinned comment. **Also give a TikTok description and an Instagram caption** (user asked; saved as `videos/<slug>/social.md` and added to `SOCIAL.md`): TikTok = hook first, 1–2 fact sentences, the comment question, 5–7 hashtags; Instagram = hook, facts, question, "Follow @theo6k…", 10–12 hashtags. Re-check any fact that may have changed (e.g. a league table) before the final.
6. **Changes after a preview:** fix the issue everywhere in the engine (never just in one video), re-render only the changed section as a short
   clip with the user's voice when the user asks to see it first, then re-render the full final once they approve. Commit and push after each change.

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

**Virality skill** (`.claude/skills/virality/SKILL.md`, from the user; built from 262 real posts). Read it before writing any hook or script.
Football version of its rules:
- **The 8-point hook checklist applies to every video.** Frame 0 is already moving (no fade-in, no static card). It shows something instantly
  recognisable: a famous player in his real kit, the real trophy, a club's colours. The biggest element fills 40%+ of the frame and moves from frame 1.
  **Something extraordinary happens before 3s**: a shot hits the net, a number races and locks, a stamp slams, a trophy shatters, a shirt rips.
  The claim lands at about 1.2–1.6s, word by word, big and high contrast. The first spoken word comes within 0.5s and it's the subject ("Mbappé…",
  "Harry Kane…"). It works on mute. It's about the viewer's world: their club, their rivalry, their opinion.
- **The hook headline is fully readable on frame 0** (channel data: ~50% of viewers swipe in the first second, mostly on mute). With beat 1
  `"hookWords": true` every word is already there and each one punches up and flashes in the accent colour in turn, roughly with the voice.
  The engine also opens every video mid-move: a zoom-out burst and speed lines on frame 0 (`"hookZoom": false` in the spec turns both off).
- **The first spoken word lands within ~0.1s.** `build.py` trims the silence ElevenLabs leaves before the first word and starts the voice 0.08s in.
- **Write 3 hooks** with a 0.0 / 0.5 / 1.2 / 3.0s frame plan each, run the checklist, and pick one, naming the winning pattern.
- **Motion check before every preview:** render stills every 0.5s and compare frames 1s apart (mean pixel difference). Anything under about 3
  (out of 255) is a static moment: add a camera push, a slower count or more action there. A replay shot can start part-way through the
  action with `"timeShift": <seconds>` (shot cards marked `noShift` keep their word timing).
- **Every line is shown, never just said** (already our narration-sync rule). If two frames a second apart look the same, add motion.
- **Comment trigger:** end on a question that splits opinion (we have no DM product, so no keyword-for-a-link). Ask it in the pinned comment as well.
- **Rotate the angle** from video to video: result first, contrarian ("Mbappé can't beat a teenager"), stakes or pain ("City could be relegated"),
  something breaks (a trophy cracks, a record board shatters). Never use the same hook framing twice in a row.

**End screen.** It's automatic: about 1.8s after the last line, the final shot softly blurs and darkens and a small brand card fades in
("theo6k · follow for more football stories"). Keep it subtle and short. Optional spec keys: `"outroText"`, `"outroDur"`, `"outro": false`.

## What the channel's analytics say (Nov 2026; re-check as data comes in)
- Every Short stalls at 1–2.5k views because **only ~50% of viewers stay past the swipe** (Shorts need roughly 60–70%+ to get pushed).
  Once people stay they watch: 55–67% average viewed, even on a 1:16 video. So the work is the **first second**, not the length.
- Best: person-v-person conflict on big clubs ("Cunha won it… then Carrick sent him off": 2.5k, 67% viewed; "Mbappé has NEVER beaten Yamal").
  Controversy gets the comments ("City… guilty on 114 charges": 9). Pure stat/record stories without a villain sit around 1k.
- The hybrid Como video was the weakest (39% stayed, 42% viewed). Treat toy/hybrid as unproven; default to the normal style.
- So: pick stories with a named conflict or a "you're wrong" claim on a big club; put that conflict in the frame-0 headline in plain words;
  open mid-action (a shot already flying, a stamp slamming); add a **re-hook around the middle** ("But here's where it gets weird…") with a
  pattern break on screen (cut, freeze, VHS, flytext); end on a question that splits fans, and reply to every comment in the first hour.

## Narration-synced animation: required on every video (viewer feedback)
A viewer said a video felt like "listening instead of watching": the picture sat on one shot while the narrator talked about something
else (e.g. Ronaldo and Klose on screen while he talked about Gerd Müller). So:
- **The picture follows the words.** When the narrator names a player, number, date, club or event, something on screen reacts at that
  moment: the player appears, the number pops or flips, the highlight moves, the pen circles it, the stamp slams down. Never show something
  before it's said, and never leave something unshown while it's being talked about.
- **Pin visuals to phrases with `"at"`** (handled by `engine/cues.py`, from the real voice timing):
  `card.at`, pen `stroke.at`, player `at` (entrance) and `tagAt` (number pop), board `focusPath[].at`, `captionAt`/`swapAt` as a phrase,
  receipt `totalAt`. Use them in place of hand-tuned `delay` and `t` values.
- **Several shots per line.** A long line gets `"shots": [{"at": "phrase", ...}]` to cut or move the camera, swap players or bring in a new card
  mid-sentence. Inside a shot, plain numbers (`delay`, `actionDelay`, punch `t`) count from the shot's start. Aim for **a visible change every 2–3 seconds** at most.
  A shot also takes `"lag"` to nudge its cut earlier or later. But **no hard cut shorter than about 2 seconds** (user: the Bayern beat "switches way too quickly"). When a line packs in several facts,
  stay on one shot and layer the cards and effects onto it (pop-ins, fly-in words, rising trophies, confetti) instead of cutting away for each one.
- **Motion matches the emotion** of each line (see the [tag] in `vo_elevenlabs.md`): excited or triumphant means fast moves, pops, confetti and slams.
  Tense means a slow push-in, darker lights and a held highlight. Sombre means low `lights`, slow drift and fewer elements. Dry or deadpan means a hard cut
  and a single clean graphic.
- **Voice speed:** the user's ElevenLabs narrator reads slightly too slowly. Set `"voSpeed": 1.08` in every spec; `build.py` speeds up the
  uploaded voice (pitch unchanged) before syncing. The user doesn't need to change ElevenLabs settings.

## Animate, don't slideshow (user direction)
The user wants videos that look like a cartoon match, not numbers on a grey background. Show the story happening:
- **Players act.** Give players an `action`: `"kick"` (run-up, plant, wind-up, strike, follow-through; contact at 42% of `actionDur`),
  `"dive"` (keeper; `"dir": 1|-1`, `"before": "ready"`), `"celebrate"` and `"run"` (loops), plus `"idle"`. Use `actionDelay`, or `actionAt` + `actionLag`
  to land the strike on a word, and `"after": "celebrate"` for what follows. A player walking in (`enter: "walk"`) runs with arms pumping.
- **The camera reacts.** Use beat `"punch": [{"at": "...", "amount": 0.3, "dur": 1.5, "anchor": 0}]` for a quick zoom on the moment of action,
  and `"shake": [{"at": "...", "amount": 20}]` on impacts.
- **The ball is real.** A `ball` card (`point`, `until`) rests on the pitch, and `ballpath` with `world: true` is the shot. Both are depth-sorted
  with the players, so they pass behind or in front correctly. A goal (`flash` on) bulges the net where it hits and makes the crowd jump.
- **Real saves (user: the keeper "doesn't actually save shots"):** give the `ballpath` `"saveBy": <keeper index>` and `"flash": false`. The ball then
  ends in the keeper's gloves at the moment of contact, worked out from his dive pose, and stays held as he falls. Time his `actionDelay` so contact
  (about 45% through the dive) matches the ball's arrival, and film it from in front of the goal, never from behind the net.
- **Run cycle:** rigged players with `action: "run"` (or walking in) use an athletic run: knee drive, bob, and, seen from behind, the arms swinging
  **in front of the body** (only the back arm shows at his side). The user found the old one goofy and wanted the arms in front.
- **Running for real (user: Messi "keeps running on the spot"):** give a player `"path": [[x,z], ...]` + `"pathDur"` and he runs along it at a steady pace,
  with the ball following his heading when he's dribbling. Keep the camera slower than him (or still) so he visibly covers ground. To beat a defender,
  put a `front` defender beside the path with a short `dive` (lunge) timed just before Messi reaches him. Example: `videos/_test-save`.
- **Slide tackle:** `action: "slide"` (with `dir: 1` when he slides right-to-left on screen, `-1` the other way) on a player moving along a short `path`
  across the runner's line: drop, lean back, leading leg out, skid. The runner jumps it with `"hops": [{"t", "dur", "height"}]`. Example: `videos/_test-save`.
- **Smooth moves:** actions now blend in over 0.12s and into their `after` loop over 0.2s, so nothing snaps. When tracking a runner,
  use beat `"moveEase": "linear"` so the camera keeps a constant pace with him (easing makes him look like he's running on the spot).
- **Drone replay (user idea):** copy the action beat, add `"cut": true`, `"letterbox": true`, `"replayTag": "REPLAY"` and a high sweeping camera
  (`camFrom` high and wide to one side, `camera` lower on the other side, `move` = beat length). The same action plays again from above with cinema bars.
  A runner can finish with a shot: `action: "kick"` timed to the end of his `path`, a `ball` at his feet until contact, then the `ballpath` past a wrong-way keeper.
- **Always put a keeper in the goal** a player is running or shooting towards (`front`, `before: "ready"`).
- **Shots are full of life (user: "more excited and more animated"). Built in as the engine's automatic hype pass:** every goal-bound world
  `ballpath` in a stadium beat automatically gets a run-up (the kicker runs ~3m into the strike; `runup: false` / `runup` metres / `runupDur`
  per player), a punch-in zoom and speed lines at contact, a camera that swings after the ball and creeps toward the net (beat `follow`,
  default 0.6, lower it when the shooter is close to the camera), a shake when it hits the net and phone flashes in the stands.
  Turn off with beat or spec `"hype": false`. Saves (`saveBy`) and `flash: false` shots are left alone.
- **Defenders in every goal clip (user):** put one or two defenders around every shot unless the story says there were none: one closing
  the shooter down and lunging (`dive`, short `actionDur`) as he strikes, one covering near goal. Keep them beside the ball's line, never on it
  (helper `defenders()` in `videos/city-seven/gen.py`).
- **Saves are auto-timed:** with `saveBy`, the engine sets the keeper's `actionDelay` so the catch lands at full stretch (70% of the dive) and he falls holding it.
- **Strong foot:** `"foot": "left"` mirrors the kick and keeps the dribbled ball on his left (Messi is left-footed; check this for every named player).
- **Dribbling:** a player with `"dribble": true` runs with the ball at his feet, pushed ahead on every other stride and depth-sorted with the players.
  Use it whenever a player runs in a scene (the user asked for it).
- **Shots must read correctly.** A goal must clearly beat the keeper (send him the wrong way, or past his fingertips); a save puts the ball into
  his gloves (`flash: false`). The ball must never pass "through" a player.
- **Prefer scenes over plain graphics.** Show events happening in the stadium, booth or another place, and use cards to support the action rather than replace it.
  Avoid beats that are only a graphic on the grey studio background.
- Example: `videos/_test-action` (strike, punch-in, wrong-way dive, net bulge, crowd jump, celebration).

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
- **Commentary booth scene:** `{"type": "booth", "crowd": [...], "screenLeft": ["BRA 0–2 GER", "23'"], "screenRight": [...]}`. Blurred stadium through the
  window, desk, monitors, ON AIR light. Players stand behind the desk (`sx`, `scale`, `"headset": true`). Good for pundits, managers, reactions.
- **Goalkeeper:** a player with `"front": true, "pose": "keeper", "gloves": "#fff"` (faces the camera, arms out).
- **Use the theatre stage sparingly** (user: it felt overused). Prefer stadiums, booth and studio; at most 1–2 stage beats per video.
- **TV analysis pen** (`pen` card): circles, arrows and handwritten notes that draw themselves over the original players. Example: `videos/klose-16`.
- **60fps** is the default render.

Built so far from the idea list (reuse them):
- **Polaroid flashback:** set `"transition": "polaroid", "polaroidLabel": "Germany 2006"` on a beat. The scene starts as a sepia instant photo and grows to full frame.
- **Newspaper spin-in:** the `newspaper` card. `headline`, `sub` ("\n" for lines), `dateline`, `color`, `masthead`. Keep the masthead **fictional**.
  `spin` (seconds, default 1.4; the user found 0.9 too quick), `turns`, `scale`. Give it time on screen: bring it in early and keep it
  across a shot with the same `id` (any non-board card with the same `id` simply stays as it was).
- **Slow-motion ball path:** the `ballpath` card. `points` (3: start, control, end), `dur`, `r`/`rEnd`. The ball slows near the end, leaves a trail and the net flashes.

- **Literal metaphors (from the reference creator, see FORMAT.md Reference 5):** when the script uses an image ("parks the bus", "minnows",
  "sham sponsor"), show it literally in the stadium. Example: `videos/city-114` beat 3, where a SPONSOR van drives on and gets stamped SHAM.
- **Vehicle:** the `vehicle` card. `kind: bus|van`, `from`/`to` pitch points `[x,0,z]`, `dur`, `color`, `stripe`, `label`, `labelColor`, `length`.
  It drives in with speed lines and spinning wheels, brakes with a small rock, and is depth-sorted with the players.
- **Rain-in counter:** the `rain` card. `groups: [{n, color, at|t, dur}]` rain into a grid (`cols`, `cell`) while a big counter below counts what has
  landed. `icon: ball|doc|dot`, `empty` (outlined slots) + `emptyAt` + `emptyLabel` (pulse a missing one), `label`, `suffix`.
- **Fly-through word:** the `flytext` card. A giant word whips across with a motion trail and settles (`endScale`, `dir: -1|1`, `color`, `size`),
  or `settle: false` to pass straight through, or `mode: "through"` to zoom past the camera (a transition).
- **Speed lines:** beat `"speedlines": [{"at": "...", "dur": 1.2}]`: radial streaks for a hero intro or a big moment.
- **Freeze frame:** beat or shot `"freezeAt": "guilty"` (+ `freezeLag`). The frozen frame slowly pushes in (5%/s) so it never reads as static. The scene stops, the colour drains to grey and there's a white flash with an impact, while cards
  (a stamp, a number) keep animating on top. Good for "and then it all stopped" turns.
- **Suit for ceremonies:** a player with `"outfit": "suit"` (+ `suitColor`) wears a dinner suit with a white shirt and bow tie, and no number. Add `"tie": "#7a1420"` for a regular business suit with a long tie (managers on the touchline; user: Carrick in a regular suit, not a tuxedo). Use it for award nights,
  managers and presidents. Combine with `front: true` on the stage. Example: `videos/kane-ballon` beats 1 and 9.
- **Cinematic celebration** (user loved it, so use it for big goal or celebration moments; example: `videos/kane-ballon` beat 8): a low-angle tracking shot as the player runs at the camera (`front`, `enter: "walk"`
  with `fromZ` behind him, `pose: "wings"` = aeroplane arms), then a cut to a circling camera (`"orbit": {center, r, from, to, h, h2, dur}` in degrees,
  0 = in front) with `pose: "fists"`, confetti, a light `punch`, and `"flashes": 16` (phone and camera flashes popping in the stands).
- **Hero close-up:** a player with `"front": true, "chest": true` shows name and big number on the chest. Use a camera about 4m in front at chest height.

- **Trophy-cabinet shelf:** the `shelf` card. A lit glass cabinet: `items: [{kind: ball|cup|worldcup|boot, label, sub, at}]` drop onto the shelf with a spotlight
  as each one is named. `slots` (total; extras stay as dashed empty slots), `title`, `instant: true` (already full, for a follow-up beat),
  `emptyAt` + `emptyLabel` (a red "?" pulses in the next empty slot: "25 years of nothing"). Example: `videos/kane-ballon` beats 4 and 5.
  Each item can carry `badge: {colors: [c1, c2, c3], text: "LFC", style: band|stripes|diamond}`: a club shield that pops in above it.
  **Badges are stylised shields in club colours with initials, never real crests** (trademarks). `drawBadge()` can be reused anywhere.
- **Knockout tally** (idea list's penalty dots, built): the `tally` card. `n` circles with `labels` ("EURO\n2024"), `done` already filled, the next fills with a slam at
  `newAt`; `mark: x|check`, `title`, `score` ("defeats: {n}"). Repeat it each beat with `done` one higher to build a run of results. Example: `videos/yamal-mbappe`.
  A resting `ball` can now vanish on a word with `untilAt` (+ `untilLag`), so the kick and the shot both sync to the voice.
- **Chalkboard tally:** the `chalk` card. A wooden-framed blackboard; tally marks (gates of five) scratch in one by one (`step` seconds apart from `start`,
  or `done` + `newAt`), `title` and `score` in chalk handwriting. User liked it.
- **Matchday tickets** (idea list, built): the `tickets` card. A fanned stack of paper tickets `[{comp, teams, score, date, color}]`, each stamped (`stamp: "LOST"`)
  as it lands (`done` + `newAt`), or all at once; `count` caption underneath. User liked it.
- **Face-off:** two `front` players side by side under low lights with a giant `vs` number card between them (e.g. 6–0). User liked it.
- **Match clock** (idea list, built): the `clock` card races `from` → `to` minutes over `dur` with a `phase` pill ("EXTRA TIME") and `events: [{min, text}]` popping above.
- **VHS rewind** (idea list, built): beat `"transition": "vhs", "vhsLabel": "AGAIN", "vhsDur": 2`: tearing, colour split, scanlines and a blinking ◀◀ label.
- **Goal barrage:** several `ballpath`s from a camera behind the net (camera at z≈59 looking back up the pitch), one every ~0.75s, each bulging the net.
- **Aerial goal map:** `shotmap` from a very high camera with `scale: 4.5`; per-shot `color` for each team, `goal: true` in gold for a named player's goals.
- **Variety rule (user):** across a video, no two consecutive beats may share the same layout or graphic. Each game or fact gets its own scene idea
  (barrage, clock, aerial map, rewind, celebration, chalkboard...). Repeating a "standing players + graphic" frame beat after beat reads as samey.
- **Ripping photo:** the `photo` card. A polaroid that spins in (`scene: "bath"` draws a young player over a baby in a tub, `player` = his look, `caption`),
  then rips in half with an impact at `ripAt` (the halves fly apart). Use it for "something breaks" hooks. Example: `videos/messi-last`.
- **Goodbye letter:** the `letter` card. A sheet with a `date` whose handwriting lines write themselves over `write` seconds. The lines are illegible
  scribbles, so we never put words in a real person's mouth.
- **Any card can vanish on a word** with `hideAt` (+ `hideLag`).
- **Cards clear the headline automatically** (user: the date and points cards overlapped a two-line headline). The engine measures each card's real top
  edge and pushes it down to leave a gap under the headline. Opt out per card with `"clear": false`. Still give stat cards time to be read:
  bring a comparison in on the line *before* its payoff word (e.g. the points tape on "The final day", not on "level on points").
- **Red card:** the `redcard` card. A referee's arm swings up from the bottom holding a glowing red card, with a shake (`dx` = sideways offset, default 180;
  `label` sits above the card, e.g. "55' Barton"). Put the sent-off player on the other side of the frame. Example: `videos/aguero-9320` beat 4.
- **Shout text (viral thumbnail style):** the `shout` card. Heavy slanted caps, yellow gradient, fat black outline, white glow, tilted, pops in with a shake.
  `text` ("\n" for lines, each auto-fitted to `w`, default 1000), `size` (max), `color`/`color2`, `stroke`, `rot`, `skew`, `glow`. Use it on thumbnails
  ("AGÜEROOOO!!!", `videos/aguero-9320/thumb`) or for a big shouted moment in a video.
- **Pass web:** the `passweb` card (stadium). The ball pings from player to player on the real pitch, each pass leaving a glowing line on the grass
  (drawn under the players), with a pop per pass. `nodes: [[x, z], ...]` (put the players there), `pass` (s per pass), `trail`, `color`, `seed`, `passFor`;
  the counter (`from`, `to`, `dur`, `label`, `y`) races and goes gold, or `counter: false` for lines only. Example: `videos/spurs-759` (hook, 10 v 10 web, City 902).
- **Pass web "play" mode** (user: make it a real move, not a ball pinging around): `passweb` with `"play": true`. A forward-biased build-up that recycles
  to the back, each receiver carries the ball a few metres (`carry`, `carryFrac`), bent pass lines draw behind the ball with arrowheads (last `trail` only),
  carries dotted, the shape pushes up (`push`, `pushMax`), numbered discs in bird's-eye (`numbers`), and in 3D the nearest defender slides into a tackle
  now and then (`tackleEvery`, `tackles: false` to turn off). Slower `pass` (0.6–1.0s) reads as tactical.
- **Pre-match handshake line:** players with `"pose": "shake"` (+ `shakeSide`): home team in a line on halfway, away team walking along it on a `path`.
- **Dark analytics board** (from the user's thefinalthird.pro reference, `videos/united-roma`): the `tactic` card with `"theme": "dark"`. Numbered discs on a dark
  olive half pitch, `kind: "shot"` moves become dashed red lines with an arrowhead (`ball: false` to hide the ball), player `ring` highlights an unmarked man,
  `tags: [{at, x, y, text, color}]` pop event labels ("LOST IT", "11' · 0–1"), `showBall: false`, `awayText`. Boards and newspapers now slowly push in by themselves.
- **Board geometry (user: shot lines must end in the goal, a penalty is taken from the spot):** on the `tactic` board aim shots at
  `"to": "goal-left" | "goal" | "goal-right"` (inside the posts, never a hand-picked `[x, y]`), and a penalty starts `"from": "spot"` (drawn on the board)
  with the taker's disc just behind it (about x 0.47, y 0.17). Goal line y≈0.03, box edge y≈0.22, goal mouth x 0.44–0.56. Keep tags in open grass, off the lines and discs.
- **Split screen** (built for `videos/messi-ronaldo-bye`): beat `"split": {scene, players, camera, camFrom, move, lights, at}`. The beat's own scene
  fills the left half and `split` the right, each with its own stadium, crowd colours, camera and lighting, divided by a glowing diagonal. Each half is
  centred on its camera's target, so put each subject at x=0. `at` slides the right half in on a word. Great for contrasts and "X or Y?" endings; cards
  sit on top (`dx` ±270 puts a stamp in one half).
- **Whip-pan transition** (backlog item, built): beat `"transition": "whip"` (+ `"whipDir": -1`): the new scene whips in sideways with a motion smear.
- **Cross-off calendar** (backlog item, built): the `crossoff` card. A wall-calendar month whose days get crossed off in red one by one:
  `title`, `days`, `cols`, `crossAt`|`crossT`, `dur`, `caption` ("{n} days"). For bans, suspensions, waits. (`calendar` is the older tear-off date card.)
- **Phone video** (built): the `phone` card. A smartphone slides up showing a video post with the player drawn inside, a blinking record dot, a running timer,
  a progress bar and hearts floating up: `player`, `caption` ("\n" for lines; a plain fact, never invented words), `tag`, `w`, `h`, `bg`. For announcements made online.
- **Name labels in the normal style:** a player with `label` (+ `labelAt`/`labelDelay`) gets a white name pill above his head (above the gold `tag` if he has one).
- **Tinted rain balls:** a `rain` group's `color` now tints its footballs, so two teams' goals can rain into one counter.
- **Team sheet** (backlog formation item, built for `videos/kane-snub`): the `lineup` card. A pitch card where players pop into formation:
  `items: [{name, x, y, color, at}]` (x, y 0–1, attack at the top; an item with `at` pops on its word with a gold ring), `title`, `w`, `instant: true`
  (all there at once), `empty: {x, y, label, at|t}` = a pulsing red dashed "?" slot for the man left out.
- **Ballot box** (built): the `ballot` card. Voting slips fly in and drop through the slot while the box bounces: `title`, `sub`, `color`, `n`, `dur`, `w`,
  `shiftX` (two side by side for "who voted for what").
- **Photo finish** (built): the `photofinish` card. Two bars race to a chequered line while the numbers count; the loser stops short and a red badge
  calls out the gap: `rows: [{name, value, color}]`, `floor` (exaggerates a small gap), `dur`, `gap: "0.8%"`, `gapAt`, `suffix`, `decimals`.
- **Faster switches (user):** cut or whip-pan about every 2–3s (never under 2s), and give long lines a second shot. Alternate transition types.
- **Career path** (built for `videos/poch-united`): the `career` card. A road of club stops; a gold marker travels to each stop on its word and a
  result chip pops beside it (red, or green with `good: true`): `title`, `items: [{name, sub, color, result, good, at}]` (no `at` = already reached,
  `t: 99` = not yet). Repeat it across beats with more stops reached for a manager's or player's CV.
- **Leaky bucket** (built): the `leak` card. Footballs pour out of holes in a club-coloured bucket while a red counter races: `value`, `dur`, `sub`
  (name on the bucket), `label`, `color`. For goals conceded.
- **Verdict gauge** (built): the `gauge` card. A half-dial with labelled `zones: [{label, color}]`; the needle swings wildly then settles at `value` (0–1)
  on `settleAt`, and a `verdict` plate pops. For "the verdict" beats in opinion videos; back the verdict with facts shown earlier.
- **Dog** (built for `videos/major-dog`): the `dog` card, a big St Bernard side on. `mode: "trot"` runs `from` → `to` (px) over `dur` (add `sitAfter`),
  `mode: "sit"` sits and wags; `box: true` = collection box on his collar, `coins: true` (+ `coinN`, `coinStep`) drops coins into it; `scale`, `label`, `dir`.
- **Debt ledger** (built): the `ledger` card. An old paper page: `rows: [[label, value]]` write themselves in ink, then `total: {label, value}` counts up in
  red and gets underlined. For debts, fines and old money stories.
- **Shirt flip** (backlog shirt morph, built): the `shirtflip` card. A big shirt spins and comes back as another kit with the name changing underneath:
  `from`/`to: {color, color2, name}`, `flipAt`. For renamed clubs, transfers and rebrands.
- **History stories:** check the club's own site and at least one other source; drop quotes and details only one retelling has; say "the story goes"
  for parts that are legend.
- **xG spheres:** the `xg` card. Glossy spheres sized by expected goals with the value counting above: `items: [{label, value, from, color, at}]`, `max`, `title`.
- **Half-time swing:** the `swing` card. Rows `[{label, from, to, at, decimals, good}]`: 1st-half number on the left, an arrow draws, the 2nd-half number counts and glows
  green (`good`) or red. Great for "what changed" tactics stories.
- **Drawn player card** (backlog item, built): the `pcard` card. A gold-framed trading card with the player drawn chest-up and a tag strip ("MALEN · 17' PEN");
  `player`, `tag`, `side`, `shiftX`, `w`, `h`. We never use real photos in the video.
- **Yellow card:** the `redcard` card with `"color": "#f7d117"` (then `hideAt` and a red one for a second yellow).
- **Kit clash check:** when two teams' kits are close (United red v Roma maroon), use the away kit they actually wore (Roma played in black).
- **Hooped kits:** `kit.hoops: [c1, c2]` gives horizontal bands (QPR, Celtic).
- **Headers:** `hops` take `at`/`lag` like everything else and now work on any player (no `action` needed). For a header, time the cross `ballpath`
  to end on the word, a hop peaking there and the header `ballpath` starting from the head. Film it side-on or 3/4 so the ball isn't hidden by the scorer.
- **Shots must be visible:** never film a goal straight from behind the shooter along the ball's line (the body hides the ball). Offset the camera a few metres sideways.
- **Booth push-in:** the booth scene now slowly zooms 1 → 1.15 over each beat (linear, so it never stalls) (`zoomFrom`/`zoom` override), so it's never static.
- **Scales:** the `scales` card. A golden balance with two name plates (`left`/`right: {name, value, color, text}`); the beam wobbles and settles toward the
  bigger value (`tilt` exaggerates a small gap, `arm` sets the width). Good for "did X deserve it over Y" endings. Example: `videos/kane-ballon` beat 10.
- **Poll sticker** (`poll`: `question`, `options: [{label, color, fill, pct}]`, tapping finger) and **comment bubbles** (`comments`: `items: [{text, x, y, color}]`,
  float up like a live chat) are comment-bait endings. Bubbles are example opinions we wrote, never presented as real viewer comments. Mock-ups: `videos/_mock-ending`.
- **Tale of the tape:** the `tape` card. Two names (`left`/`right: {name, color}`), and for each of `rows: [{label, left, right, at, floor}]` bars slide out
  from the middle while the numbers count; the bigger side turns gold. `caption` + `captionAt` adds a pill underneath. Use `floor` to exaggerate small gaps.

From statbolthq (FORMAT.md Reference 6; demo `videos/_test-statbolt`). Tips, not rules: mix them with the Story Gaffer look.
- **Word-by-word captions:** spec-level `"captions": true` swaps the headline for live captions of the VO, word by word from the real voice
  timing, showing the current phrase only (`captionMax` words, default 5). Names and numbers get a blue selection box automatically;
  add `"keys": ["word", ...]` on a beat to box more. Options: `captionY`, `captionSize`, `captionBox` (colour). Frame 1 shows the opening
  phrase whole, so it still works as a thumbnail. Best for fast play-by-play or breakdown videos; keep headlines for stat-led videos.
  Alternate between the two so the channel doesn't feel samey.
- **Tactics board:** the `tactic` card. A whiteboard half pitch "drawn from match reports". `players: [{n, x, y, team: home|away, name, label: "left", nameAt}]`
  (x, y are 0–1 on the board, goal at the top), `home`/`away` colours, `ball` (starting player index), `moves: [{from, to, at, dur, kind: pass|run|shot, curve}]`
  (from and to are player indexes or `[x, y]`; marker lines draw with the ball, X at each pass start, names appear as players get involved),
  `cam: [{at, s, x, y}]` to zoom and follow the move (each move starts on its word), `note`. It's clipped below the captions. This is the backlog's pitch map, built.
- **Stacked counter:** the `stack` card. `items: [{value, label, at, color, gold, prefix, suffix, decimals}]`. Each new stat counts up big and pushes the older ones up, smaller and dimmer.
- **Shot map on the pitch:** the `shotmap` card (stadium). `shots: [{x, z, blocked, goal, at}]` in metres, `step`, `blockedAt` (blocked shots turn red with an X), `color`.
  Use a high camera looking down at the box.

**Idea backlog: don't forget it (user asked).** Every video should use at least one backlog item, or invent a new one, and build it into the engine:
- A calendar or season heatmap of goals.
- A world map with a route line, for transfers or tournaments.
- A whip-pan or zoom-through-the-number transition between scenes.
- A dive-into-a-screen transition: the next scene starts on a tablet or phone lying on a stadium seat, and the camera flies into it (statbolthq).
- A drawn player card (polaroid with a caption line) that slides in beside a graphic when a player is named.
- A shirt-number morph: one shirt number flips into another (for heirs to a number, e.g. 7s and 10s).
- Formation chalk-lines: a 4-4-2 drawn on the pitch that rearranges into a new shape.
- A stopwatch or speed-gun readout for fastest goals or sprints.
- A league-table climb: a club's row sliding up the table week by week.

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
    "confetti": true,   // + "confettiAt": "phrase" to start it on a word
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
- `trophies`: pedestals rising from the floor. `items: [{kind: cup|worldcup|ball|ballondor|boot, sx, h, size, label, text}]`, `floor`.
  `ballondor` is the realistic trophy (seamed gold ball on a tapered gold pedestal); use it for any Ballon d'Or, and plain `ball` for a generic gold ball.
  Use `h: 0` for a floating prop (e.g. a gold ball above a player's head)
  `stagger` (seconds between items, default 0.5) and `rise` (default 0.9): use `stagger: 0, rise: 0.55` when a line ends soon after the trophies are named.
- `board`: split-flap departure board, the star graphic of the free-kick reel. `rows: [{name, value, prefix, from, strike}]`, `label`,
  `focus` (row index, gold highlight) or `focusPath: [{t, row}]` (the highlight walks in time), `caption` + `captionAt` (pill underneath),
  `swapAt` (when corrections flip), `cols`/`vcols` (name and value widths). A row with `from` shows `from` first, then a red strike,
  then flips to `value`. Give it an `id` to carry it across beats: changed cells flip, the highlight slides and nothing re-enters.
- `pen`: TV-analysis marker drawn live over the shot (the user liked this look). `strokes: [{kind: ellipse|arrow|line|x|text, t, dur, color, width, ...}]`
  in screen px. Ellipse: `cx, cy, rx, ry`. Arrow and line: `points` (3 points make a curve). X: `cx, cy, r`. Text: `text, x, y, size, rot` (Permanent Marker font).
  `dashed: true` gives a run line. With the `player` camera the hero stands at x≈540 with feet at y≈1325 and head at y≈860.
- `pen` with `"anchor": 0` pins the strokes to a player (index in `players`). Coordinates are then in player-heights from the feet
  (`cx: 0, cy: 0` = feet, `cy: -1` = top of head, `rx: 0.36` ≈ shoulder width). Use this so marks follow the player and always fit.
- `pen` strokes with `"layer": "under"` are drawn on the pitch **behind players and cards** (user wants circles and rings under the player's
  feet or behind his body, not on top of him). Use `under` for rings and circles around players. Text, arrows and Xs stay on top.
- `ballpath` with `"world": true` takes points in pitch metres `[x, y, z]` (stadium scenes) and projects them through the live camera.
  `flash: false` = saved or not a goal (the ball disappears at the end); `slowmo: false` gives constant speed. Chain several for save → rebound → goal.
- `receipt`: a thermal receipt that prints line by line (money stories). `title`, `sub`, `lines: [[label, value, accent?]]`, `total: [label, value]`, `step`.
- `stamp`: a rubber stamp that slams down with a shake ("GUILTY", "APPEALED"). `text`, `sub`, `rot`, `size`, `color`, `dx`.
  Stamps are solid and clean on a dark backing plate (the sub line gets its own dark pill). **Never add grunge/ink-speckle textures to any graphic**
  (user: the speckled stamps looked "mouldy", you couldn't read them). Never use `destination-out` on the main canvas either: it erases the frame
  behind the card and shows up as black holes.
- `vs` also takes `size` (number size) and `colW` (column width) so wide values like "80/80" don't collide.
- `meter`: a vertical tube filling with balls. `value`, `max`, `markers: [{label, value}]`, `icon: {kind, label, dx}`

## Files
- `engine/engine.js`: the canvas renderer (scenes, players, cards, text, timeline, SFX cue list)
- `engine/render.js`: Playwright frame capture to ffmpeg
- `engine/sfx.py`: synthesises the whoosh/tick/pop/impact/crowd track
- `build.py`: VO alignment, render, SFX and final mux. Outputs go to `videos/<slug>/out/` (gitignored).
