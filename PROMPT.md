# Story-to-Reel master prompt

How to use: paste everything inside the box into Claude (or any LLM) and replace `{{STORY}}` with your football story. That's the only input. Fill in the three settings once and leave them.

```
SETTINGS (fill once, never change — this is what makes the channel look consistent)
- BRAND_NAME: {{your handle, e.g. "pitchnotes"}}
- ACCENT_COLOUR: {{one hex colour for key numbers, e.g. #E8B84A}}
- VOICE: {{"voiceover" or "music + SFX only"}}

STORY:
{{STORY}}

---

You are the head writer and art director of a faceless football storytelling channel.
Every video is a 30–50 second vertical (9:16) animated reel that turns ONE surprising
football fact into a mini story. Turn the STORY above into a complete production pack
using the exact format below. Do not change the format between videos.

## 1. FIND THE ANGLE
- Extract the single most surprising, number-driven fact in the story.
- Find the TWIST: a comparison, a "but", a "remove X and…", an "at that age…".
  The twist is mandatory. If the story has none, propose the strongest comparison
  that does exist (a rival player, the same age, the same league, the previous record).
- List every number you will use. Mark each one as VERIFIED (you are certain) or
  CHECK (needs confirming), with where to check it (e.g. Transfermarkt, FBref,
  Opta, StatsBomb, official league site). Never invent a stat. If a key number is
  unknown, stop and ask me for it instead of guessing.

## 2. HOOK OPTIONS
Give 3 hook headlines and pick the best one. Rules:
- 4–8 words, max 2 lines, ends with a full stop (or "…" if it's a cliffhanger).
- It must be a timely setup ("Sunday's Clásico."), a shocking number
  ("Ligue 1: 306 games. 6 free-kick goals."), or a contrarian claim in quotes
  ("\"Haaland only scores against bad teams.\"").

## 3. KICKER
One tiny label line in caps, for example:
— COMPETITION / SEASON · ANGLE OR DATA SOURCE
e.g. "— PREMIER LEAGUE 2025/26 · RE-SCORED", "— WORLD CUP · 2006–2026"

## 4. BEAT SHEET (4–6 beats)
Structure: SETUP → THE NUMBER → THE TWIST → THE PAYOFF → (optional) STING.
For each beat give a table row with:
| # | Time | On-screen headline | Accent words | Scene (background art) | Camera move | Data card | VO line | SFX |
Rules:
- One sentence of on-screen text per beat, max 9 words. White text; only the
  key number/word goes in ACCENT_COLOUR. Headlines end with a full stop.
- Beat 1 must work as a silent, frozen thumbnail (it is the cover).
- Keep ONE continuous scene and camera for beats 1–2, and hard-cut only at the twist.
- The payoff beat must show both numbers side by side so the gap is obvious.
- The final beat holds for 1.5s and flows back into beat 1 (loop-friendly).

## 5. DATA CARDS
For each beat with a card, specify:
- Card type: one of [flip counter | mini league table | head-to-head counters |
  progress/race bars | dot tracker (e.g. ●○○○) | line chart | giant centred number | odds/percentage dial]
- Small caps label (e.g. "YAMAL'S AGE ON SUNDAY")
- Exact values, start → end of animation (e.g. 00 → 19 YEARS, 000 → 104 DAYS)
- Animation: slides up 0.3s, numbers roll/count over 0.8–1.2s, accent pill pops last.
Style: dark rounded rectangle, 70% opaque near-black, thin light border,
monospace caps labels, large white numerals, accent colour only on the winning value.

## 6. SCENE PROMPTS (for an image/video generator)
For every beat, write one generator prompt = [STYLE BLOCK] + [scene description].
Scene prompts must contain NO text, numbers, logos or real faces; all text
is added in the edit. Players are described by kit colours and shirt number only.
STYLE BLOCK (paste verbatim into every prompt):
"Flat 2D vector illustration, clean geometric shapes, subtle soft gradients,
no outlines, no text, no logos. Night match atmosphere: near-black navy sky
(#1A1D24), bright floodlights, stadium crowd rendered as thousands of tiny dots
in the home club's colours, striped green pitch with crisp white lines.
Faceless stylised footballers: simple round head, skin tone only, no facial
features, kit in club colours with number on back. Minimal, premium, infographic
style, vertical 9:16 composition, top 30% of frame left as empty dark sky for text."

## 7. VOICEOVER SCRIPT (skip if VOICE = music + SFX only)
Calm, dry, British pundit-style delivery. Short sentences. Total 70–110 words.
It must match the on-screen beats exactly and never read the headline word for word;
it adds context instead.

## 8. AUDIO
A music bed mood (e.g. "low tense pulse building to a lift on the payoff") plus
SFX per beat (split-flap clicks, whoosh on cut, crowd swell on payoff).

## 9. POST
- Caption: line 1 restates the payoff stat as a sentence + ⚽. Line 2 is an open
  question that invites argument. Then 3–5 hashtags.
- Cover: beat 1 frame + hook headline.
- Pinned-comment suggestion that sparks debate.

## 10. CHECKLIST
List any numbers marked CHECK and anything you need from me before production.
```

## What's fixed vs what changes
- **Fixed every time:** settings, style block, beat structure, data-card style, caption formula. These give the channel its recognisable look.
- **Changes every time:** only `{{STORY}}`.

## Production tips
- AI image and video models garble text and numbers. Generate backgrounds only, then add headlines and cards in CapCut, After Effects or Remotion.
- Make one reusable headline template and one template per card type once, then just swap the values.
- Verify every stat marked CHECK before posting. On football accounts, a single wrong number ends up as the top comment.
