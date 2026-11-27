# Man City in League Two, Part 6: script

Championship 2029/30 (season 4): the summer and the first five matchdays, a short opener (the user's choice: "just the summer and the first few games"; Moylan kept on a permanent deal; the opening kicker says
"a football simulation"). Every score, position, table and odds figure comes from `videos/city-league-two/data/ep6.json` (seed **2034**, matchdays 1–5 only, fixed before running); the five matchdays' scorers and the ratings come from
`squad6.json` (seed **2036**, fixed before running); the league line-up and every rating come from `c6model.py` (`citymodel_c6.json`); the poll is the user's screenshot (26 Nov 2026: Bowen 54%, Cozier-Duberry 41%, Tanner 5%, 616 votes);
Bowen's and Moylan's real numbers are ESPN's (`p6_real.json`, 27 Nov 2026). The SIM tag stays on screen throughout. The words to record are in `vo.txt` / `vo_elevenlabs.md` (11 lines, 128 words).

**Stand-ins (the series' convention, said on screen):** the three Premier League clubs that come down are today's real bottom three (ESPN table, 27 Nov 2026: Sunderland 18th, Manchester United 19th, Crystal Palace 20th); the Championship's real top three
(Middlesbrough, Stoke, Wolves) are the clubs that went up and its real bottom three (Preston, Burnley, Derby) are already in League One (Part 4); City, MK Dons and Stockport County come up from League One (Part 5's sim + play-offs, `ep5_promotion.json`).
So "Man United are in the Championship" is a statement about the simulation, never about the real season; the stamp on screen says "in our simulation" and the line-up beat says "19th in the real Premier League table today".

## Three hooks (frame plans, virality checklist)
**A (picked): "Man City and Man United are in the same league. The Championship."** Pattern: a claim that sounds wrong, with a big-club conflict (rotated from Part 5's number clash / result first, Part 4's irony and Part 3's stakes).
- 0.0s: Haaland (City, 9) and a red-shirted United player (7) face to face under the lights, each filling about half the height of the frame, both name pills already up ("Man City", "Man United"); every headline word is readable;
  zoom-out burst, speed lines and a slow push-in.
- 0.5s: "Man City": the first spoken word is the subject; each headline word flashes in turn (hookWords).
- 1.3–1.6s: "Man United": a **RELEGATED** stamp (sub: "in our simulation") slams across United with a shake: the extraordinary thing before 3 s.
- 3.0s+: "The Championship": the headline's accent word flashes; whip cut to the new league.
- Checklist: moving on frame 0 (push-in, burst, speed lines); instantly recognisable (City's sky blue and United's red, the real names); the biggest element fills 40%+ of the frame; something extraordinary before 3 s (the stamp); the subject is the first
  spoken word; works on mute (headline + kits + the stamp); it is the viewer's world (their club, their rivalry).
**B: "You voted Bowen in. Now City are second."** Pattern: the viewer's own vote pays off. Held back: no conflict in the first second, and it gives away the result.
**C: "Man United have scored eighteen goals in five games. In the Championship."** Pattern: a shocking number. Held back: it needs the sim explained first; it is the cliffhanger (beat 10) instead.

## Script and picture
| # | Line | On screen |
|---|---|---|
| 1 | Man City and Man United are in the same league. The Championship. | Hook A (above). |
| 2 | In our simulation, the Premier League's bottom three come down: Sunderland, Man United, Crystal Palace. Up from League One: City, MK Dons, Stockport. | **New card `divisions`**: three bands (Premier League, Championship, League One); the three shields fall into the Championship on their names (red ▼), then City, MK Dons and Stockport rise (green ▲); stamps "19TH · in the real Premier League table today" and PROMOTED; speed lines and punches. |
| 3 | You voted for the right wing: Jarrod Bowen. Fifty-four percent. | The **ballot box** (voting slips drop in on "You voted for the right wing"); Bowen's drawn card with his real West Ham numbers (7 goals, 7 assists, 17 starts) slides in on his name; the poll bars fill on "Fifty-four percent" (54 / 41 / 5, 616 votes). |
| 4 | And you said keep Moylan. So he stays: a permanent deal. | The shirt flips Cardiff → City ("MOYLAN") on "he stays"; PERMANENT stamp. |
| 5 | Promotion odds: fifty-five percent. Your two picks add twenty-three. | Odds grid: 55 squares light; the last 23 turn gold ("your two picks: +23"). 10,000 seasons: 32% with neither pick, 55% with both. |
| 6 | But Man United are the favourites: eighty-six percent to win the league. City: five. | Re-hook (VHS tear "BUT"): a giant UNITED flies across; bars: United 86, Sunderland 6, City 5 (title odds, pre-season). |
| 7 | Day one: Cardiff, Moylan's old club. Haaland scores. One–nil. | **Match 1** (MD1, home): Haaland dribbles at goal, hops the slide, finishes low past the wrong-way keeper; OLD CLUB stamp, then 1–0; bug MCI 1–0 CAR. |
| 8 | Then Norwich, two–nil. Portsmouth, one–one. Southampton, one–nil. Birmingham, two–nil. | The **climb** card: City 8th → 3rd → 3rd → 3rd → 2nd, one step per result, United on top for three of the five weeks. |
| 9 | Thirteen points. One goal conceded. And Bowen: two goals, two assists. | Bowen in City's shirt walks into frame on his name; the stacked counter: 13 points, 1 against (the fewest), 2 goals, 2 assists (sim, seed 2036). |
| 10 | Next: Old Trafford. United have scored eighteen goals in five games. | The tale of the tape, City v United after five games: points 13 v 12, goals scored 7 v 18, clean sheets 4 v 2; the two players face each other under the lights. |
| 11 | Matchday seven. Man United against Man City. Who wins? | MD 7 stamp (Old Trafford) and the poll sticker "Who wins the derby?" (City / Draw / United; results left empty: the real poll is the user's). |

## Facts checked (all asserted in `gen.py`)
- League line-up: PL bottom three today = Sunderland, Man United, Crystal Palace (ESPN, 27 Nov 2026; United 19th); promoted from League One in the sim = Man City, MK Dons, Stockport County (`ep5_promotion.json`); 18 Championship clubs stay.
- Poll: Bowen 54%, Cozier-Duberry 41%, Tanner 5% (sum 100), 616 votes (the user's closing screenshot). Real stats: Bowen (West Ham United) 17 starts, 7 goals, 7 assists; Moylan (Cardiff City) 17 starts, 10 goals, 3 assists (ESPN, 27 Nov 2026).
- Odds (10,000 seasons from the empty table, seed 7, the four versions of City's XI on the same seeds): promotion 32% with neither pick, 55% with both (+23); title odds with both: Man United 86%, Sunderland 6%, Man City 5%.
- Official run (seed 2034): MD1 City 1–0 Cardiff (H), MD2 Norwich 0–2 City, MD3 Portsmouth 1–1 City, MD4 City 1–0 Southampton, MD5 City 2–0 Birmingham; positions 8th, 3rd, 3rd, 3rd, 2nd; 13 points, 7 scored, 1 against (the fewest), 4 clean sheets,
  Haaland 3 goals (MD1, MD2, MD5). United after five: 12 points (3rd), 18 scored (the most), 5 against, 2 clean sheets: Bristol City 0–2 (W), Sheffield United 5–0, Bolton 2–5, Cardiff 5–1, Portsmouth 2–1 (their first defeat).
- Derby: matchday 7 at Old Trafford (the fixture list is `fixtures(2034)`, fixed before the run); matchday 30 is the return at the Etihad.
- Scorers (seed 2036, shared out after the fact, no score changed): Haaland, Moylan (MD2) and Bowen 2 goals (MD4, MD5) with 2 assists (both at Norwich); Ward-Prowse one goal (MD3). Only Haaland's goals and Bowen's count are named in the video.
- Not claimed: anything about United's or any other club's real season; the order of goals; minutes.

## What is reconstruction (not match footage)
Everything: the kits (United's red with black socks, Cardiff's blue) and the players are drawn figures; the goal is a re-enactment of a 1–0 win with Haaland's goal (the sim has no minutes or build-up); the shields on the line-up card are stylised, not real crests;
Man United's player is a generic red-shirted 7, not a likeness; the Championship's real clubs are stand-ins (above).

## What is new in the engine (reusable)
The `divisions` card (clubs fall or rise between division bands, red/green arrows, dashed arrival slots; test spec `videos/_test-divisions`), and the kicker label now shrinks to fit the headline's width (a long label was cut off at the edge).
