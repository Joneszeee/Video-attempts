# Man City in League Two, Part 3: script for approval

All results come from the simulation (`videos/city-league-two/data/ep3.json`, seed 2028 fixed before running). Watts's numbers are his real
League One stats (ESPN, 21 Nov 2026). The SIM tag stays on screen throughout.

## Three hooks (rotating away from Part 2's "You picked him")

**A. Stakes with an open loop: "Man City were ninety minutes from the Championship."** (recommended)
- 0.0s: Wembley-style final under lights. A City shot is already flying at goal, the score bug reads PLAY-OFF FINAL 0–0, and the match clock is racing. The headline is fully readable.
- 0.1s: first word: "Man City…"
- 1.2s: the shot **hits the post** (shake, crowd gasp), and "90 MINUTES" locks on the clock as "Championship" is said.
- 3.0s: whip-pan to the recap.
- Checklist: 1 ✓ moving on frame 0 · 2 ✓ City kit, Haaland, a Wembley final · 3 ✓ the shot fills the frame · 4 ✓ hits the post · 5 ✓ claim at ~1.3s · 6 ✓ "Man City" first · 7 ✓ works on mute · 8 ✓ the viewers' own vote and club.
- Pattern: **stakes and an open loop**. It doesn't say whether they won, and the last minute of the video pays it off.

**B. Clashing numbers: "Ninety-three goals. The most in League One. And City still didn't go up."**
- 0.0s: goal barrage from behind the net, the counter racing.
- 1.3s: it locks on 93.
- 2.4s: a red NOT PROMOTED stamp.
- Strong, but it gives the ending away in the first 3 seconds.

**C. Your signing: "Your signing took Man City to Wembley."**
- The WATTS shirt flips over the poll bars.
- Too close to Part 2's "You picked him" hook (the rotate-the-angle rule).

## Script (12 lines, about 135 words, about 62s with the voice at 1.08×)

| # | Line | On screen |
|---|---|---|
| 1 | Man City were ninety minutes from the Championship. | Hook A: Wembley final, shot off the post, the clock locks on 90. |
| 2 | Season two: League One. Twelfth at halfway, and leaking goals. | Recap: a leaky bucket pours out 43; a table row sits at 12th; SIM HUD. |
| 3 | So you voted. Half of you picked Kelland Watts. | Poll bars race: Watts 50, Sowunmi 33, Seimen 17. A tap on Watts. |
| 4 | A centre-back from Cambridge. Fifteen starts in League One, two goals. | Shirt flip CAMBRIDGE → WATTS; drawn player card with his real stats. |
| 5 | With him, City win fifteen of their last twenty-three. Seven clean sheets. | **New: the league-table climb.** City's row slides up the table week by week (12 → 4) while the wins tick. Clean-sheet gloves pop. |
| 6 | Haaland finishes on twenty-nine. | Haaland strike in the small ground; the counter races 18 → 29. |
| 7 | But here's where it hurts. The last day, against Cambridge. Watts's old club. | Re-hook: VHS cut. Score bug MCI v CAM, final day; Watts glances at his old shirt (stage beat or a drawn card). |
| 8 | One–one. City finish fourth, two points off going up. | Freeze on the equaliser; the table row drops 3 → 4; a "2 PTS" gap chip. |
| 9 | Play-offs. Stockport beaten four–nil over two legs. | Two-leg chips (2–0, 2–0) pop on a split screen; aggregate 4–0. |
| 10 | Then Wembley. Bradford City, the best defence in the league. | Face-off under lights: City v Bradford (claret and amber); "30 conceded" tag. |
| 11 | Bradford win two–nil. City stay in League One. | The final from hook A plays on: Bradford score; red stamp STAYING DOWN; a newspaper spin. |
| 12 | Ninety-three goals, the most in the league. Not enough. Who should City sign this summer? | Goal barrage counter 93, then the vote: three drawn player cards and a poll (shortlist below). |

Facts to note:
- The 1–1 v Cambridge, the 4–0 against Stockport and the 2–0 final are sim scores, so no scorers are named except Haaland's count.
- Bradford had the league's best defence (30 conceded) in our simulated season. The line says "in the league", which is true within the sim.

## Still to decide
1. **The summer vote shortlist.** City still conceded the 6th-most goals. The model gives the goalkeeper the biggest single share of the defence
   (20%), and City's keeper is a League Two signing. Suggestion: three real keepers, Dennis Seimen (17% last time) plus the two League One
   keepers with the best clean-sheet records this season (researched from ESPN before building).
2. **Hook A** (recommended), B or C.

## As built (user approved hook A and asked for the five key matches, 21 Nov 2026)
Script v2 is `vo.txt` (14 lines, 160 words). The five matches, all from ep3.json:
1. MD25 Leicester 4–0 City (Watts's second game; City 13th).
2. MD26–30 five straight wins (Wycombe 4–2, Doncaster 4–2, Stevenage 2–1, Huddersfield 2–1, Notts County 3–2): 13th → 5th (the new `climb` card).
3. MD35 City 2–0 Grimsby, Haaland twice: top three for the first time in League One (best in the first half: 6th).
4. MD37 City 3–4 Stockport: the seven-goal thriller ("Remember them": they meet again in the play-offs).
5. MD42 Oxford 4–2 City (the champions); Haaland ends on 29.
Then the last day (level on 77 with Wednesday in 2nd; 1–1 v Cambridge; 4th), the play-offs (4–0 v Stockport; Bradford 2–0 at Wembley) and the keeper vote
(McCracken, Young, Seimen: real stats in research.md).
