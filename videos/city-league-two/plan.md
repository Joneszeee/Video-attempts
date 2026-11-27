# Series idea: what if Man City were relegated to League Two?

City drop to League Two. They keep only Erling Haaland (he stays loyal) plus their academy players in the current first team and the under-21s.
Everyone else goes. They get a League Two budget and buy real League Two players. We follow their journey, one season per episode.

## Agreed with the user (19 Nov 2026)
- **Squad:** Haaland + current first-team academy graduates + the current under-21s (underdog story). Fact-check the exact list before building.
- **Simulation:** each season run 10,000 times for the odds (title, promotion, play-offs), then one "official" season played once and followed
  like a Football Manager save (form, injuries, play-offs). Ratings scaled to League Two with real data; keep the SIMULATION HUD on screen throughout.
- **Signings:** viewers vote. The pilot's opening signings are picked realistically by us (real League Two players, League Two budget);
  each episode ends with "Who should City sign?" and the comments decide the next window.
- **Length:** pilot first (episode 1 as a standalone video), then judge performance.
  **ASK THE USER AGAIN before making Part 2** (series length: stop at promotion to the Premier League, keep going, or end it). The user asked for this reminder.

## Notes
- Every episode opens with a 3-second recap for new viewers ("Season 2: City are in League One, Haaland's on 41 goals").
- Reuse the Bruno simulation kit (simhud, simrun, odds, glitch); build a small League Two ground (low stands, terraces) and the backlog's league-table climb.
- Hook angle candidates: the 115 charges link; "Haaland in League Two"; "City's kids v League Two".

## Episode 2 signing vote (from comments)
- Tim Iroegbunam: 4 votes (leading, per the user, 19 Nov 2026)
- Tom Fellows 1, James Gibbons 1, Dennis Seimen 1, Mo Salah 1 (joke)
- Before building ep. 2: check Iroegbunam's current club and realistic fee/wages v a League One budget (could be a plot point).
- Also fix: name label sat under the LEAGUE TWO stamp in ep. 1 frame 1 (keep labels clear of stamps in the engine).

## Episode 2 decisions (user, 19 Nov 2026)
- Series length: decide episode by episode (ask again after ep. 2).
- Signing: Tim Iroegbunam (won the comment vote). Ignore the budget: no fee shown, just signed.
- Show the voters' real usernames on screen; the user will send screenshots of all the Iroegbunam votes (YouTube + TikTok). Use exactly those names.
- Squad: same as ep. 1 + Iroegbunam; the kids improve a little (typical young-player development).
- Covers League One matchdays 1–23 and stops at the January window.
- Mid-season vote: the sim shows City's weak spot, and fans pick from 3 real shortlisted players aimed at fixing it (open suggestions also welcome).
- Hook: "You picked him": a shirt flips to IROEGBUNAM over the voters' comments.

## Part 2 (videos/city-league-one) done, 19 Nov 2026
- League One matchdays 1–23; City 12th at halfway; posts all say "Part 2" (user).
- Part 3 vote (January window): Kelland Watts, Omar Sowunmi or Dennis Seimen. Count the comments before building Part 3.
- Before Part 3: ask the user again how long the series should run (they chose "decide episode by episode").
- Sound: Freesound blocks requests from the cloud environment (403); the user may upload CC0 sounds instead (kick, net, whistle, roars, groans,
  ambience, terrace chant, slide skid) for the real-SFX upgrade.
- TikTok uses a poll for the Part 3 vote (user); combine poll + YouTube/Instagram comments into one tally.

## Part 3 decisions (user, 21 Nov 2026)
- Vote result: the TikTok poll ended **Watts 50%, Sowunmi 33%, Seimen 17%** (6 votes); the user called it: **Kelland Watts signs** in January.
- Series length: still **episode by episode** (asked again before Part 3, as requested).
- Scope: **finish the season**: League One matchdays 24–46, plus the play-offs if City get there; end on a summer-window vote.
- On screen: the poll result as bars (Watts 50 / Sowunmi 33 / Seimen 17), then his shirt flip. No usernames (the poll is anonymous).
- Model: Watts rated at Cambridge United's real League One level, replacing one of the League Two centre-backs; second half played from Part 2's
  exact matchday-23 table with a new seed fixed before running (`data/sim_l1b.py`, `data/ep3.json`).

## Part 3 (videos/city-part-3) done, 21 Nov 2026
- League One matchdays 24–46 + play-offs: City 12th → 4th, beat Stockport 4–0 on aggregate, lost the final 2–0 to Bradford at Wembley. **They stay in
  League One** (season 3 would be League One again). Haaland 29 league goals; City scored 93 (most), conceded 74.
- Next vote (summer window, a keeper): **José Sá (Wolves), Gavin Bazunu (Bolton, ex-City academy), Jon McCracken (Bradford)**. User wanted two
  well-known Championship names, "pretty decent, not too good". Count the TikTok poll + YouTube/Instagram comments before any Part 4.
- Series length: still episode by episode. Ask the user before starting Part 4.

## Keeper vote (summer window): comments seen so far (22 Nov 2026; the TikTok poll total itself is not visible to me)
Options: José Sá (Wolves), Gavin Bazunu (Bolton, ex-City academy), Jon McCracken (Bradford).
- Poll votes (shown by the "Voted" tag): Stan Cooper → McCracken; Keigan Thompson → Sá; Thatfootballfan → Sá, UNCONFIRMED (their comment "Sá as who is going to keep Bradford up?" suggests they think the vote is for Bradford; the user replied to clarify it is for who City sign; count it once they confirm).
- Comment votes: Will ("Super Jon") → McCracken; LD → "John McCracken"; Bwfcmurphy ("Gavin bazunu is sick") → Bazunu.
- Unknown: LS posted only a photo of Bradford's keeper; the "Voted" tag (if any) was hidden behind the reply bar. Not counted until seen.
- Count the poll + YouTube + Instagram comments together before any Part 4, and ask the user about the series length first.
- Rule: only count a vote when the "Voted" tag or the words are visible; never infer a vote from a photo.

## Keeper vote result and Part 4 go-ahead (user, 23 Nov 2026)
- The TikTok poll (left open 7 days by accident; 645 votes after one day): **Jon McCracken 43%, José Sá 33%, Gavin Bazunu 24%**. The user called it:
  **City sign Bradford's keeper, Jon McCracken.** The academy players keep getting better. Part 4 = **the first half of the next League One season (matchdays 1–23)**.
- Series length: still episode by episode (the go-ahead for Part 4 is the answer to the reminder).
- Decisions I made (flag if wrong): the league changes as in the real EFL (3 up, 4 down in League One; 3 down from the Championship, 4 up from League Two),
  using today's real tables as the stand-ins (see research.md, episode 4); McCracken rated at Bradford's real League One level; the seed (2029) was fixed before running.
- January vote (Part 5): **a midfielder** (the model's weakest slot): Kalvin Phillips (Sheffield United), James Ward-Prowse (Southampton), Oliver Norwood (Stockport).
  Count the TikTok poll + YouTube/Instagram comments before building Part 5, and ask about the series length first.

## Part 4 (videos/city-part-4) built, 23 Nov 2026
- League One 2028/29, matchdays 1–23, McCracken in goal: City **4th at halfway** (38 pts, W10 D8 L5), **best defence (22 conceded) and best goal difference (+21)**, Haaland 13, 5 points off the top (MK Dons 43);
  the model expected 46 points. Pre-season odds with McCracken 94% promoted / 75% champions (86% / 60% without him); halfway 88% / 57%.
- Five key matches: Stevenage 0–1 (day one), Burnley 1–2 (Haaland twice), Luton 3–4 (seven goals), Stockport 3–1 (revenge for last year's 3–4), Derby 9–1.
- Preview (SFX only) and the ElevenLabs script were sent; the user's voice (P5.mp3, one file) was aligned and the **final was built and sent on 23 Nov 2026** (62.9 s, -14 LUFS, check clean);
  thumbnail and posts (`videos/city-part-4/thumbnail.jpg`, `youtube.md`, `social.md`; `posts.py` passes) were given with it.
- January vote (open): a midfielder: Kalvin Phillips (Sheffield United), James Ward-Prowse (Southampton), Oliver Norwood (Stockport). **Ask the user about the series length before Part 5**
  (the second half of season 3 + play-offs; replay the first half exactly from seed 2029, then fix a new seed).

## Squad update video (between Parts 4 and 5), 23 Nov 2026
- User idea (with the January poll still open for ~18 h): "go through the team with FIFA-style cards, show their rating and their stats since the beginning of the simulation and this season". Built as `videos/city-squad-update`
  (ratings from the model, stats allocated with a fixed seed; see research.md, "Squad update"). The ending was changed at the user's request: no poll on this video, it sends viewers to Part 4's poll. Preview, ElevenLabs script, thumbnail and posts delivered; the user's voice (Squad_.mp3) arrived on 24 Nov 2026 and the final (58.8 s) was built and sent.

## Part 5 (second half of season 3): seed fixed before running (24 Nov 2026)
- Second-half seed **2031** (Part 4's first half 2029, the squad stats 2030), written here before anything is run. `data/sim_l5.py` replays the first half and asserts the matchday-23 table against `ep4.json`,
  then plays matchdays 24–46 and the play-offs with the January signings: the poll winner in the second holding-midfield slot and the comment-vote loan player (6 months = the whole second half),
  each rated at his real club's level (`data/l5model.py`). Waiting for the user's poll result and the loan player's name.

## Part 5: what was run (25 Nov 2026)
- The poll ended: Ward-Prowse 47%, Norwood 30%, Phillips 23% (785 votes) → **Ward-Prowse** (Southampton) signs. The comment vote: "Make them sign Jack Moylan from Cardiff" reached 19 of the 30 likes, so **Moylan** (Cardiff City)
  comes on a **6-month loan** (left wing, replacing T. Samba). `data/p5_run.py` ran the second half with seed 2031 (fixed above, before running): City 1st, 82 points, 97 goals, 51 against, Haaland 35 league goals, promoted as champions
  (title clinched at matchday 45). Series length: decided episode by episode (user's answer, 25 Nov 2026); the ending lets the result decide: City went up, so the step-up vote is for the Championship (right wing is the weakest slot).
- Squad cards for the two signings: simulated stats since joining (matchdays 24–46) are shared out after the fact by `data/squad5.py` with seed **2032**, written here before running it.

## Part 5 addendum: who else went up (25 Nov 2026, after a viewer's comment)
- A viewer asked "who else went up?" Part 5 did not say. The official run (seed 2031) only played the play-offs when City were in 3rd–6th, so with City champions the other promotion places were never decided:
  MK Dons (2nd, 78 points) go up automatically; the third place goes to the play-offs among 3rd–6th (Stockport 77, Luton 76, Reading 74, Stevenage 74).
- The play-offs among those four are played now with seed **2033**, written here before anything is run (`data/p5_promotion.py`: same two-leg semi-finals (3rd v 6th, 4th v 5th) and one-match final as `sim_l5.py`).
  The bottom four (Huddersfield, Walsall, Exeter, Wimbledon) go down. This result is now part of the series (it feeds Part 6's league membership).
- **Standing rule (user, 25 Nov 2026): a season-ending episode always says and shows who else went up (and who went down)**, the play-off winner included, so every season sim must play the play-offs for the other clubs too.
- **Result (seed 2033):** semi-finals Stockport 4–2 Stevenage on aggregate (2–1 home, 2–1 away) and Reading 4–2 Luton (Luton 1–0 at home, Reading 4–1 at home); final Stockport 2–1 Reading.
  **Promoted: Manchester City (champions, 82), MK Dons (2nd, 78, automatic) and Stockport County (play-off winners).** Relegated: Huddersfield Town (21st), Walsall (22nd), Exeter City (23rd), Wimbledon (24th). `data/ep5_promotion.json`.

## Part 5 comments and the right-wing poll (26 Nov 2026, 10 h after posting)
- TikTok: 2,414 views, 101 likes, 30 comments. The right-wing poll (Bowen / Cozier-Duberry / Tanner) was open with 14 h left: 354 votes, Cozier-Duberry 42%, Tanner 6% (Bowen's bar was cut off in the screenshot, so about 52% if there
  are only three options; **ask for the closing screenshot**).
- Comments worth acting on: "keep moylan" (a vote to keep him), "tyler dibling" (a write-in: ESPN has him at **Everton, Premier League**, age 20, 4 appearances (3 as a sub), 0 goals and 0 assists, so he is not in the Championship / League One
  pool the candidates come from), "what game is this" (new viewers think it is a video game: for Part 6 consider a "football simulation" tag in the opening kicker; not applied yet, ask the user).

## Right-wing poll closed (26 Nov 2026, the user's closing screenshot)
- "Who should we sign next!": **Bowen 54%, Cozier-Duberry 41%, Tanner 5%, 616 votes, poll ended** (TikTok, about a day after Part 5). **Jarrod Bowen (West Ham United) signs for the Championship season (Part 6).**
  Real numbers to refresh before use (ESPN, last fetched 25 Nov 2026, `right_wing.json` / `p5_real.json`): 17 starts, 7 goals, 7 assists.
- Still open for Part 6: whether City keep Moylan (his six-month loan ends with the season; the comments said "keep moylan"), how much of season 4 the episode covers (the user decides episode by episode), and the
  "football simulation" tag for the opening kicker (new viewers ask "what game is this").

## Part 6 (season 4, Championship 2029/30: the summer and the first five matchdays): decisions and seeds, fixed before running (27 Nov 2026)
- User's answers: **just the summer and the first few games** (a short opener: Bowen arrives, the new league, then a cliffhanger); **Moylan is kept on a permanent deal** (left wing; Samba stays on the bench); the opening kicker says
  **"a football simulation"** (new viewers keep asking "what game is this").
- The league (stand-ins are today's real tables, Part 4's convention; `data/c6model.py` -> `citymodel_c6.json`): the real Championship positions 4-21 stay (Birmingham, West Brom, Southampton, QPR, Swansea, Sheffield United, Portsmouth, Norwich, Blackburn,
  West Ham, Wrexham, Charlton, Bristol City, Cardiff, Millwall, Bolton, Watford, Lincoln); the real top three (Middlesbrough, Stoke, Wolves) are the clubs that went up to the Premier League; the real bottom three (Preston, Burnley, Derby) are already in League One (Part 4);
  **the real Premier League bottom three today come down: Sunderland, Manchester United (19th), Crystal Palace**; Man City, MK Dons and Stockport County come up from League One (Part 5 + the play-offs, seed 2033). 18 + 3 + 3 = 24.
  Ratings: Championship clubs from the Championship's real results (as in Part 4); the three relegated clubs from the Premier League's real results (`fetch_pl.py`, `espn_pl.json`, this season 1.0 / last season 0.5) moved onto the Championship scale with the 295 real
  Premier League v Championship cup ties (`gap_pl.py`); MK Dons and Stockport from their League One ratings with Part 4's Championship v League One bridge. City's own PL-level tier comes from City's 19 real cup ties v Championship clubs blended with the PL average (the same blend as l1model.py).
- City's XI = Part 5's second half with the fans' picks: **Jarrod Bowen on the right wing (West Ham's Championship level)** and **Jack Moylan on the left (Cardiff's Championship level, permanent)**, Ward-Prowse at Southampton's level; the kids' third year of growth (0.20 compounds to 0.488).
  Real numbers (ESPN, 27 Nov 2026, `p6_real.json`): Bowen age 29, 17 starts, 7 goals, 7 assists; Moylan 17 starts, 10 goals, 3 assists; Ward-Prowse 15 apps, 1 goal, 1 assist.
- Odds: 10,000 seasons from the empty table, four versions of the XI on the same seeds (neither fan pick / Moylan only / Bowen only / both), seed 7 as in Part 4. Promotion = top two or the play-off winner (3rd-6th).
- **Official run: seed 2034** (the fixture list is `fixtures(2034)`: the club order is shuffled with 2034 + 1 = 2035, as sim_l4.py does), **matchdays 1-5 only**, played once (N = 5 fixed before looking at any result). Haaland and Foden are available 90% / 85% of games, Haaland takes 38% of City's goals when he plays (as in every season).
- **Scorers: seed 2036** (written here before running; 2035 is already the fixture shuffle): each City goal in the five games goes to a slot in proportion to the model's attack weights (Haaland's own goals are the sim's), 67% of goals carry an assist, exactly as `squad5.py` did it; no score changes. Fix the names only after this is run.


## Part 6: what was run (27 Nov 2026)
- `data/sim_c6.py` (odds: 10,000 seasons from the empty table, seed 7, four versions of City's XI on the same seeds; official run seed **2034**, matchdays 1-5 only) wrote `ep6.json`. **Odds before a ball is kicked:** promotion 32% with neither fan pick, 39% Moylan only, 47% Bowen only,
  **55% with both** (+23); title 1% / 2% / 3% / 5%. Title odds with both: **Man United 86%**, Sunderland 6%, Man City 5%, Crystal Palace 2%; promotion: United 99%, Sunderland 58%, City 55%, Palace 37%, Southampton 24%, West Ham 15%.
- **Official run, matchdays 1-5:** City 1-0 Cardiff (H), Norwich 0-2 City, Portsmouth 1-1 City, City 1-0 Southampton, City 2-0 Birmingham: **W W D W W, 13 points, 7 scored, 1 against (the fewest), 4 clean sheets, 2nd** (8th, 3rd, 3rd, 3rd, 2nd after each matchday), Haaland 3 goals.
  After five games: West Brom 1st (13, GD +12), City 2nd (13, +6), **Man United 3rd (12, 18 scored the most, 5 against; W W W W L, their first defeat at Portsmouth)**, Sunderland 4th (10). Odds after five games: promotion 68% (title 8%, automatic places 52%).
- **Next fixture (the cliffhanger): matchday 7 at Old Trafford, Man United v Man City** (matchday 6 is QPR v City); the return is matchday 30 at the Etihad. Matchdays 6 onwards have not been run; seed 2034 continues from the same stream when they are.
- **Scorers, seed 2036** (`data/squad6.py`, run once): Haaland 3 (MD1, MD2, MD5), Bowen 2 (MD4 Southampton, MD5 Birmingham) with 2 assists (both goals at Norwich), Moylan 1 (MD2 Norwich), Ward-Prowse 1 (MD3 Portsmouth); Foden 1 assist, O'Reilly 1 assist.
  Ratings on the Championship scale (60 = an average Championship player in the slot): Haaland 87, Foden 79, Lewis 76, O'Reilly 76, Bowen 72, Iroegbunam 71, Ward-Prowse 65, Moylan 65, McCracken 63, Watts 55, Scarr 54. **Weakest slots: the centre-backs** (an average Premier League player would add
  +0.18 / +0.16 goals a game of goal difference at CB2 / CB1, then Moylan's wing +0.13): the next vote (Part 7) would be a centre-back.
- Built `videos/city-part-6` (11 beats, about 62 s; the new `divisions` card shows who came down and who went up). Man United's relegation is the series' stand-in rule (today's real bottom three) and is said so on screen. **Ask the user the length of Part 7 before building it.**
