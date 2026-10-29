# Story Gaffer format breakdown

Source: @story.gaffer (Instagram, 27 posts, 12.8K followers). Example reel: 14.2K likes, 101 comments, 180 reposts, 1,411 shares.
Bio: "Football's best stories in under a minute. Tactics, history and the odd daft moment." Lead magnet: "Take the FREE dead ball test" link.

## The concept in one line
One surprising football stat, told as a short animated story in 3–5 beats with flat vector graphics, under 60 seconds.

## Visual system (keep it identical on every video)
- **Canvas:** 9:16 vertical (1080×1920).
- **Style:** flat 2D/2.5D vector illustration. Faceless players with a skin-tone head, kit colours and name/number on the back. Stylised stadiums with a dotted crowd in club colours, floodlights and striped green pitches. No real footage and no photos, so there are no rights problems.
- **Palette:** near-black navy sky (#1a1d24-ish), pitch greens, club colours in the crowd. **One accent colour, mustard yellow/gold (#E8B84A-ish)**, used only on the key number or phrase.
- **Top-left layout:**
  1. A small logo plus the `storygaffer` wordmark in a monospace font.
  2. A tiny monospace **kicker/eyebrow** in grey caps with a leading dash: `— EL CLÁSICO · AGE V MINUTES`, `— PREMIER LEAGUE 2025/26 · RE-SCORED`, `— STATSBOMB · EVERY LA LIGA GAME 2004–2021`. It doubles as a data-source credit.
  3. A **headline** of 2 lines, about 6–8 words, in a bold geometric sans (similar to Inter/Satoshi/General Sans). White text, with the key number or word in yellow, and always ending in a full stop. Example: "Lamine Yamal will / be **19y 104d** old."
- **Data widgets:** a dark rounded card with a thin border, monospace caps labels and big numerals. Examples:
  - a split-flap counter that rolls up (00 → 19 years, 000 → 104 days),
  - a mini league table with kit icons and a yellow "+7" pill,
  - shot vs goal counters (6 / 0),
  - penalty dots (●○○○ "1 SAVED"),
  - an ECG-style line chart,
  - a giant centred number (12, 36%).
- **The widget animates in**: it fades or slides up and the numbers count or roll. That motion is the whole payoff of each beat.

## Story structure (from the Yamal reel)
| Beat | ~Time | Screen | Headline |
|---|---|---|---|
| 1. Hook/setup | 0–2s | Wide aerial shot of the stadium, crowd in club colours | "Sunday's **Clásico.**" |
| 2. The fact | 2–5s | Camera pushes down to pitch level, player walks in, counter rolls to 19y 104d | "Lamine Yamal will be **19y 104d** old." |
| 3. The turn | 5–7s | Cut to a new set-up: Ronaldo, Messi, Yamal and Mbappé lined up on a yard-line pitch | "At exactly **that age…**" |
| 4. Payoff | 7s+ | Bars or counters race to show the comparison | caption: "Yamal had **73** goal contributions. Messi had just **12**." |

Arsenal reel: "Arsenal: champions by **7 points.**" → the final table card animates in (85 vs 78, +7 pill) → "Their first title in **22 years.**" → twist (caption: "Ronaldo leads Messi by 45 goals. Remove penalties and everything changes.").

Rules that fall out of this:
- **Every beat is one sentence on screen.** Don't use subtitles or paragraphs.
- **The headline swaps on each beat, while the scene keeps moving.** It's one continuous "camera" per idea, with a hard cut only at the turn.
- **Structure each video as setup → number → "but/at that age/remove X" → payoff.** The twist is what drives comments and shares.
- **The hook is either a pattern-breaking stat or a contrarian claim in quotes.** Examples from the grid: "Haaland only scores against bad teams." / "No Barcelona player lost the ball more than Messi." / "The bookies gave Wolves a 4.5% chance at City." / "Ligue 1: 306 games. 6 free-kick goals."
- **The cover equals the first frame,** so the hook headline and visual work as the grid thumbnail.
- **Audio is "Original audio"**, probably a VO or a sound bed with SFX for whooshes, flaps and crowd. Copy that with a calm British-pundit-style VO, or music plus SFX.
- **The caption restates the payoff stat** and leaves the question open, which drives comments.

## Topic formula
Pick a stat that is (a) timely (this weekend's fixture, an award, a record chase), (b) counter-intuitive and (c) expressible as 1–2 numbers.
Formats seen: age comparison, "re-scored" alternate table, bookies' odds, StatsBomb/Understat deep cut, World Cup flashback, giant % reveal.

## Script template
```
KICKER:   — <COMPETITION> · <ANGLE OR DATA SOURCE>
BEAT 1:   <Context>. <Accent word>.                 [establishing shot]
BEAT 2:   <Subject> <verb> <ACCENT NUMBER>.          [widget animates the number]
BEAT 3:   <Twist phrase>…                            [new scene / comparison set-up]
BEAT 4:   <Payoff: X had <A>. Y had just <B>.>       [comparison widget races]
(BEAT 5): <Kicker line / question>                   [hold 1.5s, loop-friendly]
CAPTION:  <Payoff stat as a sentence>. ⚽ <question to the audience>
```

## Reference 4: the free-kick reel ("Counted goal by goal…")
- **The star graphic is a split-flap departure board** over a blurred, darkened stadium with out-of-focus fans in the foreground.
- **Rows:** player name on the left, number on the right. Inactive rows are grey; the active row is white with a glowing gold outline that slides between rows.
- **Corrections:** a red strike across the old number, then it flips to the corrected one, with a small red "-2" badge. A pill caption below explains why ("TAKE OUT THE FRIENDLIES").
- **Re-sorts:** every cell scrambles through random letters and settles into the new ranking.
- **The headline accent changes with meaning:** red for "number is wrong", gold for the answer.
- **The final shot:** a dark, hazy stadium with the floodlights low. The camera pushes slowly toward one player standing with the ball.
- **Takeaway:** depth (blur plus foreground), constant small motion, and animated corrections instead of static numbers.
