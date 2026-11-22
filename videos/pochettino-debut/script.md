# Liverpool 4–0 Man United, Pochettino's debut: script

Made the same day (22 Nov 2026), straight after the final whistle. Every minute, score and stat is asserted against ESPN's match feed in `gen.py`
(`data/fetch.py` pulls it). Words to record: `vo_elevenlabs.md` (9 lines, 134 words; about 50 s at 1.08×).

## Three hooks (virality skill), rotated away from Part 3's "stakes: 90 minutes from the Championship" and Yamal's "claim"

**A. "Pochettino's new-manager bounce at United lasted thirteen minutes: a red card, then two goals." (chosen)**
- 0.0s: Anfield under lights, Pochettino walking toward the camera (already moving), headline fully readable, the clock at 00:00 starts to race.
- 0.5s: first spoken word "Pochettino's"; the clock pills pop as it passes 8' (RED CARD · YORO), 10' (1–0), 13' (2–0).
- 1.2–2.6s: the clock locks on 13:00 in red as "thirteen minutes" is said.
- 3.0–4.3s: the red card slams in with a shake on "a red card"; the score bug flips to 2–0 on "two goals".
- Checklist: 1 ✓ moving · 2 ✓ Pochettino, Anfield, the red card · 3 ✓ he fills about 45% of the frame by 3 s · 4 ✓ a clock races and locks, the card slams · 5 ✓ claim readable from frame 0 · 6 ✓ "Pochettino's" first · 7 ✓ works on mute · 8 ✓ every United and Liverpool fan.
- Pattern: stakes with a clock; the ESPN recap itself says the new-manager bounce was "extinguished within 13 nightmare minutes".

**B. "United sacked Carrick ten days ago. This is the new manager's first game."**: conflict with a villain (Carrick performed best on the channel), but it spends the first line on context.

**C. "Was this a red card? Eight minutes in, Pochettino's debut was over."**: a debate hook; strong, but it gives the viewer the end (the question) in the first second. It became the ending instead.

## Beats
| # | Line | On screen |
|---|---|---|
| 1 | Pochettino's new-manager bounce at United lasted thirteen minutes: a red card, then two goals. | Hook A. |
| 2 | United sacked Carrick ten days ago, after one league win in ten. Pochettino's first game: Anfield. | VHS cut "12 NOV"; 10-day calendar crossing off; "1 WIN IN 10" stamp. Then Pochettino walks in at Anfield, "ANFIELD" whips across. |
| 3 | Eight minutes in, Isak is through on goal. Yoro fouls him. Straight red. | Isak dribbles, Yoro chases and slides in from behind, both go down; freeze; the red card slams; the score bug gets its red square. |
| 4 | Two minutes later, Szoboszlai's free kick: one–nil. Then Wirtz, set up by Ngumoha: two–nil. | **New free-kick scene**: a wall that jumps, the ball over it into the corner, keeper beaten. Then Wirtz's finish with Ngumoha beside him. |
| 5 | Pochettino's first change: Mbeumo off for Maguire, after twenty-two minutes. Cunha followed at half-time. | Pochettino at the touchline; the fourth official's board swaps 19→5, then 10→11. |
| 6 | Second half: Ngumoha, eighteen, makes it three. Muñoz, off the bench, makes it four. | Two goals; Ngumoha carries a gold "18" tag. |
| 7 | Liverpool had twenty-eight shots. United had ten. Lammens made seven saves. Expected goals: four point three eight to nought point six three. | **New shot-timeline card**: all 38 shots on a minute track, a playhead sweeping, goal pills, the red card marker, live counters; a "7 saves" counter; then the expected-goals spheres. |
| 8 | United haven't won a league game since the thirtieth of August. Nine without a win. Nineteenth. | **New form-strip card**: United's 11 league results as W/D/L chips, the one win ringed in gold, a bracket "9 WITHOUT A WIN", then a "19TH" stamp. |
| 9 | Was it a red card? And how long does Pochettino get? | The foul again from a drone, rewinding on VHS, with a poll: Yes, red / No, harsh. |

## Facts and where they come from
- ESPN match feed (data/espn_summary.json): score, red card 8' (Yoro, straight, no earlier yellow), goals 10' (free kick), 13' (assist Ngumoha), 66', 82', substitutions
  22' (Maguire for Mbeumo), 45' (Zirkzee for Cunha), 72' (Muñoz on), shots 28 (11 on target) v 10 (3), Lammens 7 saves, ages (Ngumoha 18), Liverpool manager Iraola.
- ESPN schedule and standings: United's results LWDLDDDLLDL (one win, 30 Aug, 5–2 v Ipswich), 19th on 8 points, Palace 20th on 7.
- Carrick sacked 12 November (Al Jazeera / The National / Sky headlines, found by search); no United league game between 8 and 22 Nov (ESPN), so "one win in ten" is right.
- Expected goals 4.38 v 0.63: from the user's match-stats screenshot (22 Nov, 18:35).
- **Not used:** the Opta "Premier League first for a manager's debut" line (one search summary of Yahoo, not confirmed anywhere else) and Pochettino's own quotes (news sites are blocked in this container).
