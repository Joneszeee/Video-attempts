# Man City in League Two, Part 5: script

League One 2028/29 (season 3), matchdays 24–46, with the January signings: the poll winner **James Ward-Prowse** (47% of 785 votes) and **Jack Moylan** on a six-month loan (the fan comment got
19 of the 30 likes it needed, so a loan, not a permanent deal). Every score, position, table and odds figure comes from `videos/city-league-two/data/ep5.json` (seed 2031, fixed before running;
the first half replays Part 4's seed 2029 and asserts the matchday-23 table); the signings' ratings and simulated stats come from `squad5.json` (seed 2032, fixed before running); the poll and the
comment are the user's screenshots (25 Nov 2026); Moylan's and the three right-wing candidates' numbers are real (ESPN, 25 Nov 2026, `p5_real.json`). The SIM tag stays on screen throughout.
The words to record are in `vo.txt` / `vo_elevenlabs.md` (13 lines).

## Three hooks (frame plans, virality checklist)
**A (picked): "Man City were fourth at halfway. Now they're champions."** Pattern: number clash and result first (4th → champions; rotated from Part 3's stakes and Part 4's irony).
- 0.0s: Haaland and two team-mates in City's kit, filling the middle of the frame, camera pushing in; the halfway table is already on screen with City 4th on 38; every headline word is readable; zoom burst and speed lines.
- 0.5s: "fourth": the City row glows gold on the table.
- 1.2–2.6s: "champions": City's row slides 4th → 1st (▲3, points tick 38 → 82), a CHAMPIONS stamp slams, confetti, the three players celebrate.
- 3.0s: whip cut to the poll (47% for Ward-Prowse).
- Checklist: moving on frame 0 (push-in, zoom burst, speed lines, a table that is about to move); a famous player in City's kit with his name; the players and the table fill the frame; something extraordinary before 3s (the climb, the stamp, the confetti);
  the subject is the first spoken word ("Man City"); works on mute; it is the viewer's world (their club). **Not** "your vote won it": the model only says the signings add 17 points of title odds, so that claim stays in beat 5.
**B: "Your vote just won Man City the league."** Pattern: the viewer's own vote pays off. Held back: it overclaims (the sim ran one season; the odds only rose from 57% to 74%) and the first image has no conflict.
**C: "Man City were five points off the top. Then you voted."** Pattern: open loop (what did the vote do?). Held back: weaker frame 0 (a table, no player) and "five points off" was Part 4's close.

## Script and picture
| # | Line | On screen |
|---|---|---|
| 1 | Man City were fourth at halfway. Now they're champions. | Hook A (above). |
| 2 | You voted, and forty-seven percent picked Ward-Prowse. | Poll bars (Ward-Prowse 47, Norwood 30, Phillips 23; 785 votes); the shirt flips Southampton → City on his name. |
| 3 | A comment wanted Jack Moylan. Thirty likes needed. It got nineteen. So: a six-month loan. | His drawn card with real numbers (Cardiff: 10 goals, 3 assists, 17 starts) and the new **pledge** card: the real comment, a heart counter that stops at 19 of 30, "11 SHORT", then a 6-MONTH LOAN stamp. |
| 4 | Ratings: Ward-Prowse, sixty-nine. Moylan, seventy-two. The loan beats your pick. | Two squad cards (silver, "FAN PICK" and "LOAN" ribbons), simulated stats since joining; "72 v 69". |
| 5 | Title odds at halfway: seventy-four percent. Your signings add seventeen. | Odds grid: 74 squares light, the last 17 turn gold ("your signings: +17"). 57% → 74% (Ward-Prowse alone: 67%). |
| 6 | Debut day. Stevenage win two–one. City fall to fifth. | **Match 1** (MD24, away): Stevenage's winner beats the keeper; bug STE 2–1 MCI; 5TH. |
| 7 | Then three wins. Burnley, five–one. Wycombe, four–three. Burton, two–nil. City go top. | **Matches 2–4** (MD25–27): the climb card moves City 5th → 5th → 2nd → 1st, one step per match; TOP stamp (first time this season: the best in the first half was 3rd). |
| 8 | Salford. Six–nil. Haaland didn't even play. | **Match 5** (MD34, home): six-ball barrage from behind the net; "NO HAALAND" (the sim's own availability); the biggest win of the half. |
| 9 | Then it got tight. Chesterfield win four–three. Plymouth win three–one. Level on points with Stockport. | VHS re-hook "TIGHT": the pace chart, City v the best of the rest for matchdays 1–42; the two defeats pin on their words; both lines meet at 74; LEVEL stamp. |
| 10 | Then Cambridge. Haaland scores twice. Three–nil. One game to spare, and City are champions. | **Match 6** (MD45, home): Haaland's goal and "2" tag, bug MCI 2–0 CAM; cut to the trophy, confetti, bug 3–0. Title clinched on MD45 (lead 4 > 3 points left). |
| 11 | Eighty-two points. Ninety-seven goals, the most. Fifty-one against, the fewest. And Haaland: thirty-five. | Haaland close-up; stacked counter 82 / 97 / 51 / 35. |
| 12 | City are going up. The weak spot: right wing. Who should City sign? | The team sheet with the sim ratings and an empty "RIGHT WING" slot (the model's biggest upgrade gain: McAidoo, 61), PROMOTED stamp; then three real Championship right-sided attackers (Bowen, Cozier-Duberry, Tanner) and a poll. |
| 13 | And Moylan's loan is nearly up. Keep him? | His card and a six-month calendar crossing off; KEEP HIM? stamp. |

All scores are sim scores. No scorer is named except through Haaland's count (his goals are the sim's own). The signings' stats are shared out after the fact with a fixed seed (Moylan: 1 goal, 6 assists
in 23 games; Ward-Prowse: 4 goals, 2 assists), so they can differ from the real players' form (Moylan has 10 goals in 17 starts for Cardiff). The commenter's public handle is shown as a credit
(`CREDIT` in `gen.py`; set it to `None` to hide it).
