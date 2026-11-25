# Research: Man City in League Two, episode 1 (season 2026/27)

Scripts and data are in `data/` (run from that folder: `parse.py` → `fit.py` → `citymodel.py` → `sim.py` / `sens.py` / `official.py`).
Raw downloads (openfootball, ESPN day files) stay out of the repo; `parse.py` and the ESPN steps in this file rebuild them.

## The premise (agreed with the user)
City drop to League Two for 2026/27. They keep Erling Haaland, their academy players in the first team and the under-21s. Everyone else goes.
With a League Two budget they sign four League Two players (keeper, two centre-backs, a holding midfielder). They take the place of the club
currently bottom of the real table (Crawley Town; **to confirm with the user**).

## The squad (ESPN rosters, 19 Nov 2026; to double-check on the club site)
- First-team academy graduates: **Phil Foden** (26), **Rico Lewis** (21), **Nico O'Reilly** (21); plus academy players registered with the first
  team: Kaden Braithwaite (18), Floyd Samba (17), Ryan McAidoo (18), Dexter Oliver, Max-Edgar Chabot (GK, 18).
- Under-21s (ESPN list, partly stale): Max Hudson, Ben Vickery, Josh Wilson-Esbrand, Leke Drake, Kian Noble, Matthew Henderson-Hall, Harrison Parker,
  Brooklyn Nfonkeu, Marlow Barrett, Dante Headley, Oluwafemi Fapetu, Finlay Gorman, Harrison Miles, Christian Dunbar-Mcdonald, Teddie Lamb, Tyrone Samba,
  Kylan Midwood and others. Wikipedia (blocked from this session) would confirm who is out on loan.
- Not academy: Bouaddi, Vitor Reis, Khusanov, Elias (signings), so they go.

## How strong is that team against League Two? (real results only)
| Benchmark | Games | Goals for–against per game (neutral venue) | Record |
|---|---|---|---|
| Premier League under-21 sides v League Two clubs (EFL Trophy 2023/24–2026/27) | 99 | 1.84–1.79 | W30 D24 L45 |
| Man City U21 v EFL clubs (League One + Two) | 12 | 1.58–2.83 | W2 D3 L7 |
| Premier League first teams v League Two clubs (FA Cup + League Cup, 2015–2026) | 104 | 2.70–0.67 | W77 D17 L10 |
| Man City first team v League Two clubs | 6 | 4.14–0.63 | W6 (8–0 Salford, 2025) |
| League Two average | 731 | 1.22–1.22 | |

City's first-team level = their 6 games shrunk toward the 104-game Premier League average (3.24–0.65).
Each position in a 4-2-3-1 gets an attacking and defensive weight (striker 23% of attack, keeper 20% of defence, etc.), and each player is rated at his tier:
first-team (Haaland, Foden, Lewis, O'Reilly), under-21, or a good League Two signing (top-half League Two level, 1.31–1.13).
**Result: City with everyone fit ≈ 2.34 goals for, 1.07 against per game v an average League Two side.** Without Haaland 2.05; without both 1.89.
Haaland is available 90% of games, Foden 85%; Haaland scores 38% of City's goals when he plays (his real City share has been ~28–38%).

League Two clubs are rated from their real results (2026/27 so far at full weight, 2025/26 at half weight; Poisson model, home advantage ×1.24).
Strongest on current form: Barnet, Grimsby, Salford, Chesterfield, Walsall.

## 10,000 seasons
- **Champions in 89.7%**, top three (automatic promotion) 98.9%, promoted overall 99.4%. Average 98 points (80% between 88 and 109), 110 goals scored, 50 conceded.
- Haaland averages 38 league goals (80% between 30 and 47).
- Sensitivity (3,000 runs each): kids at City U21's own worse record → title 74%; first-teamers at the Premier League average instead → 78%;
  no League Two signings → 76%; first-teamers at City's raw 6-game level → 96%. Top three stays 94–100% in every version.

## The official season (one run, seed 2026 fixed before running)
Fixtures: a double round robin with alternating home and away (the first try had a venue bug, fixed before the season was read; same seed).
- Matchday 1: **Gillingham 2–1 City** (Haaland missed it). 18th.
- Matchday 14: **Salford 1–3 City** (Salford are the real leaders right now). City go top.
- City top for 28 of 46 matchdays. Barnet briefly lead after matchday 35.
- Matchday 42: **Grimsby go top** with four games left. Matchday 43: **City 0–4 Swindon** at home.
- Going into the final day: **City and Grimsby both on 89 points; Grimsby +45 goal difference, City +28.**
- Final day: **City 3–1 Chesterfield; Grimsby lose.** City champions on 92 points, Grimsby 89, Barnet 82 (third, automatic promotion).
- City record: W28 D8 L10, scored 85, conceded 55. **Haaland 29 goals** (missed 6 games).

## Limits (say on screen: SIMULATION)
- The model rates players by tier, not individually; under-21 players are rated from Premier League U21 sides' real EFL Trophy results.
- Club ratings come from 13–15 games this season plus last season; League Two promoted sides have less data.
- The official season is one of the 10,000: the odds say City win the league nine times in ten.

# Episode 2: League One 2027/28, matchdays 1–23

## The signing (comment vote, ignore the budget)
- Tim Iroegbunam: midfielder, Hull City (Premier League); joined Hull from Everton on 1 Sept 2026. 2026/27 so far: 1 goal (ESPN: 3 starts, 4 sub apps; FotMob: 7 apps, 289 min).
- Voters: lvp_davie's comment "Tim Iroegbunam or Tom Fellows" (4 likes) and their reply "Iroegbunam" when asked to pick one.

## Model (data/l1model.py, data/sim_l1.py)
- League One clubs rated from real results (2026/27 full weight, 2025/26 half). City, Grimsby and Barnet (promoted with them in episode 1) replace the real bottom three (Bromley, Barnsley, Peterborough, 19 Nov 2026).
- Grimsby and Barnet moved onto the League One scale with 308 real League One v League Two games (cups + EFL Trophy): League One sides win those 1.73–1.27.
- City tiers v an average League One side: first-team level from 151 Premier League v League One cup games (2.43–0.87), shrunk with City's own 8 (33–4).
  Iroegbunam at the Premier League average level. Under-21s from 102 EFL Trophy games v League One clubs (1.42–2.66); **they improve a little:
  20% of the way (log scale) toward an average League One player** (user: "kids improve a little"). The four League Two signings at a top-half League Two level.
- City with everyone fit: 2.15 for, 1.26 against per game v an average League One side.

## 10,000 seasons (full League One season)
- With Iroegbunam: champions 35.6%, top two 57.6%, play-offs 32.9%, **promoted 69.5%**, average 84 points.
- Without him (an under-21 in his place): champions 19.9%, promoted 51.0%, 79 points. **He adds about 5 points and 18 points of promotion chance.**

## The official season, matchdays 1–23 (seed 2027, fixed before running)
- Matchday 1: Wigan 1–2 City. Matchday 2: City 3–4 Leicester. Matchday 6: City 0–4 Huddersfield (no Haaland), 17th.
- Matchday 12: Grimsby 1–2 City. Matchday 13: **City 5–0 Barnet** (Haaland hat-trick). **Matchday 15: City 3–4 AFC Wimbledon**, Jayden Stockley
  hat-trick (Stockley is real and at Wimbledon: 6 goals in 14 this season, ESPN; the scorer is our story, the sim only gives the score).
- **Editorial change (user):** Barnet and Wimbledon swap places in matchdays 13 and 15 (and in the return fixtures, 36 and 38); every score stays as
  simulated, and the table and the odds are rebuilt from that (`SWAP` in data/sim_l1.py).
- Matchday 19: City 0–3 Oxford (the leaders). Matchday 20: City 5–3 Luton.
- **At the halfway point: City 12th, 32 points (W9 D5 L9), 43 scored (only Oxford, 47, scored more), 43 conceded (only Grimsby 46 and Barnet 47 conceded more).**
  Four points off the play-offs (Bradford, 6th, 36). Leaders Oxford on 45. Haaland 18 goals.
- From here (10,000 runs of the second half): promoted 38.1% (top two 19.9%, play-offs 47.8%), champions 4.3%.
- Weak spot: defence. Mid-season vote shortlist: Kelland Watts (CB, Cambridge United; PFA League Two Team of the Year 2025/26), Omar Sowunmi
  (CB, Bromley; PFA League Two Team of the Year 2025/26), Dennis Seimen (GK, VfB Stuttgart; a commenter's pick; spent 2025/26 on loan at Paderborn).

# Episode 3: League One 2027/28, matchdays 24–46 and the play-offs

## The signing (fans' vote)
- TikTok poll (6 votes, ended 21 Nov 2026): **Kelland Watts 50%**, Omar Sowunmi 33%, Dennis Seimen 17%. The user confirmed Watts.
- Kelland Watts (ESPN, 21 Nov 2026): centre-back, 27, Cambridge United (League One this season; PFA League Two Team of the Year 2025/26).
  League One 2026/27: **15 starts, 2 goals, 1 clean sheet**, 24 goals conceded in his starts, 3 yellow cards (includes Cambridge 0–3 Stockport,
  21 Nov, full time confirmed). Footedness not confirmed, so the video never shows him striking the ball.

## Model (data/l1model.py, data/sim_l1b.py)
- Watts is rated at his own club's real League One level: Cambridge United's ratings (l1ratings.json) → 1.41 for, 1.45 against per game v an average
  League One side (the League Two signing he replaces: 1.37 for, 1.61 against). He replaces one of the two League Two centre-backs from matchday 24.
- City with everyone fit: 2.15 for, 1.26 against → **2.15 for, 1.24 against** with Watts. One centre-back carries 15% of the defence in the model.
- The second half starts from episode 2's exact matchday-23 table (sim_l1b.py replays the first half and checks it matches ep2.json).

## 10,000 runs of the second half (same seed as episode 2's halfway odds, so the runs are paired)
- Without Watts (episode 2's figure, reproduced): promoted 38.1%, top two 19.9%, champions 4.3%, 74.3 points.
- **With Watts: promoted 39.2%**, top two 21.6%, champions 4.6%, 74.5 points. On the model's numbers he's worth about a point of promotion chance.

## The official run-in (seed 2028, fixed before running)
- From 12th at halfway to **4th**: 15 wins, 1 draw, 7 defeats in the second half, 46 points (only Oxford, 49, took more after Christmas).
- Defence: **31 conceded in 23** (43 in the first 23); **7 clean sheets** (2 in the first half).
- Highlights: MD25 Leicester 4–0 City; MD30 City 3–2 Notts County (Haaland 2); MD34 Leyton Orient 2–5 City (Haaland 2); MD35 City 2–0 Grimsby (Haaland 2);
  MD37 City 3–4 Stockport; MD42 Oxford 4–2 City; MD45 Mansfield 0–1 City (City 3rd going into the last day).
- **Final day (MD46): City 1–1 Cambridge United**, Watts's old club. City drop to 4th, two points behind Sheffield Wednesday (2nd, 80).
- Final table: Oxford 94 (champions), Sheffield Wednesday 80, Bradford City 79, **Man City 78**, Stockport 76, Huddersfield 72.
  City scored **93, the most in the league**, and conceded 74 (only five teams conceded more).
- **Haaland: 29 league goals** (18 at halfway; he missed 4 of the last 23 games).
- **Play-offs:** semi-final v Stockport: City 2–0 at home, 2–0 away (**4–0 on aggregate**; Stockport had beaten City 4–3 on matchday 37).
  **Final: Bradford City 2–0 Man City.** Bradford (third, the league's best defence: 30 conceded) go up. **City stay in League One.**
- The sim gives scores only. Any scorer named on screen other than Haaland's count is our story, not the model's.

## Summer vote shortlist: a goalkeeper (ESPN, 21 Nov 2026)
Why a keeper: City still conceded the 6th-most goals, and in the model the keeper carries the biggest single share of the defence (20%);
City's keeper is a League Two signing. Clean sheets and saves counted from ESPN match reports (league starts only, this season).
| Keeper | Club | Age | Starts | Clean sheets | Conceded | Saves per game |
|---|---|---|---|---|---|---|
| **Jon McCracken** | Bradford City (League One) | 26 | 13 | **9** | 9 | 1.5 |
| **Matt Young** | Huddersfield Town (League One) | 19 | 15 | 4 | 13 | 2.0 |
| **Dennis Seimen** | VfB Stuttgart (Bundesliga) | 20 | 5 | 2 | 6 | 3.8 |
Also checked: Nathan Baxter (Leyton Orient) 12 starts, 5 clean sheets, 2.8 saves per game; Joe Lumley (Sheffield Wednesday) 10 starts, 3; Liam Roberts (Mansfield) 12, 3.
McCracken is Bradford's real keeper: the club that beat City in our play-off final.

### Shortlist changed (user, 21 Nov 2026): two well-known players from the Championship, "pretty decent, not too good"
City are Man City, even in League One, so they attract names. Final three (ESPN match reports, league starts this season):
| Keeper | Club | Age | Starts | Clean sheets | Conceded | Saves per game |
|---|---|---|---|---|---|---|
| **José Sá** | Wolves (Championship) | 33 | 15 | 4 | 17 | 2.5 |
| **Gavin Bazunu** | Bolton Wanderers (Championship) | 24 | 8 | 2 | 15 | 3.6 |
| **Jon McCracken** | Bradford City (League One) | 26 | 13 | 9 | 9 | 1.5 |
- José Sá: Portugal international, years as a Premier League starter with Wolves.
- Gavin Bazunu: Republic of Ireland international; joined Man City's academy from Shamrock Rovers in 2019 and was sold to Southampton in 2022
  (so "ex-City academy"). Shares the Bolton job (Jack Bonham has also started).
- Also checked: Mads Hermansen (West Ham) 15 starts, 4 clean sheets, 1.8 saves; James Beadle (Birmingham) 14, 4, 2.7.
Matt Young and Dennis Seimen dropped from the vote.

# Episode 4: League One 2028/29 (season 3), matchdays 1–23

## What changed since Part 3 (everything is in `data/l4model.py` → `citymodel_l4.json`)
- **The league (24 clubs).** Part 3's league minus the 3 promoted (**Oxford** champions, **Sheffield Wednesday** 2nd, **Bradford** play-off winners) and the
  4 relegated (the bottom four: **Blackpool, Notts County, Wigan, Doncaster**), plus 3 down from the Championship and 4 up from League Two.
  Stand-ins (same convention as Part 2, which removed the real bottom three and added the League Two clubs): the Championship's real bottom three today,
  **Burnley, Derby County, Preston North End** (ESPN table, 23 Nov 2026); the four best-rated League Two clubs after Barnet and Grimsby (who came up in Part 1),
  **Salford City, Chesterfield, Walsall, Exeter City**.
- **Ratings for the newcomers.** League Two clubs: moved onto the League One scale exactly as Grimsby and Barnet were (`l1model.py`).
  Championship clubs: Poisson ratings fitted to the Championship's real results (749 games, 2025/26 half weight + 2026/27 full weight; `fetch_ch.py` → `espn_ch.json`),
  then moved onto the League One scale with the real **Championship v League One cup ties** (`gap_ch.py`: 227 FA Cup + League Cup games 2015–2026; an average
  Championship side scores 1.68 and concedes 1.20 against an average League One side at a neutral venue).
  On that scale **Derby +0.14, Burnley +0.06, Preston 0.00** (att + def; League One's best are Huddersfield +0.35, Stockport +0.31): the relegated clubs land mid-table to upper mid-table.
  The three that went up left a hole at the top: last year's City model in this league is already **85% to go up** (69.5% in Part 2's league).
- **McCracken** in goal (rated at Bradford's real League One level, as Watts was at Cambridge's): City's goals against drop 1.235 → **1.104** per game v an average side
  (-10.6%). The League Two keeper (Hudson) is out. He is Bradford's real keeper, the club that beat City in our play-off final.
- **The kids' second year.** Part 2's growth closed 20% of the gap to an average League One player each year; two years compounds to 36%. Growth now never lowers a
  rating (Part 2's rule also pulled the kids' goals-for 1.42 → 1.40 towards the average, a small flaw in the published first year; fixed here only). The kids play
  wide (attack weight 15% each, defence 3%), so the effect on City is small: goals for 2.153 → 2.164, against 1.243 → 1.235.
- **City's rates v an average League One side (everyone fit):** 2.164 for, **1.104 against** (Part 3: 2.153, 1.243).

## McCracken: real numbers (ESPN match reports, 23 Nov 2026; `data/mccracken.json`)
Age 26, 6'3", Scotland. **13 starts of Bradford's 14 league games, 9 clean sheets, 9 conceded, 20 saves (1.5 per game).** Cameron Dawson started the other game.
Bradford (real, 14 games): 9 clean sheets and only 10 conceded, so a top-three defence in League One.

## 10,000 seasons (`data/sim_l4.py`, seed 7 for the odds, paired runs)
| | Promoted | Champions | Top two | Average points |
|---|---|---|---|---|
| City with the League Two keeper (second-year kids) | 86.3% | 60.2% | 78.2% | 87.3 |
| **City with McCracken** | **94.5%** | **75.1%** | 89.2% | 91.4 (80% between 80 and 102) |
| (last year's City, no McCracken, first-year kids) | 84.8% | 57.8% | | 86.7 |
So **McCracken alone adds 8 points of promotion chance and 15 of title chance** in this model. For comparison Part 2 (Oxford, Wednesday, Bradford still in the league): 69.5% promoted.

## The official first half (seed 2029, fixed before running; `data/ep4.json`)
City 4th after 23 matches, **38 points (W10 D8 L5), scored 43, conceded 22 (the fewest), goal difference +21 (the best)**; **6 clean sheets**; Haaland **13 goals**
(missed 3 games, Foden 2). Leaders: MK Dons 43, Luton 42, Grimsby 39, **City 38**, Leicester 38, Stockport 38. City are **5 points off the top**.
The model expected **45.9 points** from City's first 23 fixtures (`extra4.py`, which includes the chance Haaland and Foden miss games): City are 8 below expectation.
Four of the five defeats are by a single goal (Stevenage 0–1, Reading 0–1, Chesterfield 0–1, Luton 3–4; the other is Burton 0–2).
Halfway odds (10,000 runs from the real matchday-23 table, McCracken model): **88.3% promoted, 57.1% champions, 78.6% top two, 19.1% play-offs** (League Two keeper: 81.1% / 46.6%).

**Five key matches** (the user likes five): 
1. MD1 **City 0–1 Stevenage** (home): the opening-day shock after a 94% pre-season promotion chance; 18th.
2. MD2 **Burnley 1–2 City** (away): first win, Haaland twice (Burnley: one of the three clubs that fell from the Championship).
3. MD8 **City 3–4 Luton** (home): a seven-goal thriller; Luton end the half 2nd.
4. MD16 **City 3–1 Stockport** (home): revenge for last season's 3–4 (Part 3, matchday 37).
5. MD21 **City 9–1 Derby** (home): the record win (probability of 9+ goals under the model: under 0.1%; it is what the fixed seed produced). Against the three clubs that fell City have
   scored **15 and conceded 3** (Burnley 2–1, Preston 4–1, Derby 9–1; the return games come in the second half).
Other: MD7 Barnet 0–1 City; MD22 Cambridge 1–1 City (Watts's old club again); MD23 City 1–1 Leyton Orient.

## The weak spot (`data/sens4.py`: from the matchday-23 table, upgrade one slot to an average Championship player, 6,000 runs each)
Midfield (the second holding midfielder, a League Two signing) is the biggest single gain: promotion +3.3 points, title +6.5, +1.07 league points; centre-back (League Two signing)
+3.1 / +5.4 / +0.96; each academy winger +3.1 / +4.8 / +0.88; Watts +2.0 / +3.4 / +0.58. The gaps between slots are small (within a point of promotion chance of each
other), so "midfield" is the largest gain, not a landslide.

## January vote shortlist: a midfielder (ESPN rosters and match lineups, 23 Nov 2026; league starts = appearances minus substitute appearances)
| Player | Club | Age | League starts | Goals | Assists | Note |
|---|---|---|---|---|---|---|
| **Kalvin Phillips** | Sheffield United (Championship) | 30 | 6 (11 apps) | 1 | 2 | England international, ex-Man City (2022–25); started two of the last four |
| **James Ward-Prowse** | Southampton (Championship) | 32 | 12 (14 apps) | 1 | 1 | England international, set-piece specialist; started the last four |
| **Oliver Norwood** | Stockport County (League One) | 35 | 16 (16 apps) | 2 | 3 | Northern Ireland international; started every game for the league leaders |
Real stats only; each would be rated at his club's level in Part 5 (Championship clubs on the League One scale via the cup bridge). Other midfielders checked:
Flynn Downes (Southampton, 13 starts), Ben Whiteman (Wrexham, 14), Stephen Eustáquio (Swansea), Oliver Skipp (Charlton), Kasey Palmer (Luton, League One, 3 goals + 4 assists).

## Claims to keep out unless confirmed
- Nothing about Haaland's or any player's scoring beyond the model's count (the sim gives scores and Haaland's goals only).
- Why Kalvin Phillips is at Sheffield United (ESPN's roster says he is; the lineups confirm he plays for them).

# Squad update (between Parts 4 and 5): ratings and simulated stats for the XI (`data/squad.py` → `squad.json`, seed 2030 fixed before running)

**Rating** = 60 + 80 × (goals per game he adds to City's goal difference v an average League One player in his slot), Part 4 model. Cards: bronze < 65, silver 65–74, gold 75–84, elite 85+.
| Player | Slot | Rating | This season (apps, G, A / CS, GC) | All-time (three seasons) |
|---|---|---|---|---|
| Haaland | ST | 91 | 20, 13, 3 | 100 apps, 71 G, 24 A (29 + 29 + 13, the sim's own) |
| Foden | AM | 82 | 21, 7, 3 | 96, 22, 20 |
| Lewis | RB | 75 | 23, 2, 3 | 115, 9, 9 (26 clean sheets) |
| O'Reilly | LB | 75 | 23, 7, 4 | 115, 16, 12 |
| Iroegbunam | DM | 71 | 23, 1, 3 | 69, 8, 9 (from season 2; your pick) |
| McCracken | GK | 66 | 23 apps, 6 CS, 22 GC | the same (arrived this season; your pick) |
| McAidoo | RW | 61 | 23, 2, 5 | 115, 25, 23 |
| T. Samba | LW | 61 | 23, 4, 6 | 115, 31, 26 |
| Watts | CB | 59 | 23, 1, 1 (6 CS) | 46, 3, 1 (13 CS; from matchday 24 of season 2; your pick) |
| Braybrooke | DM | 59 | 23, 4, 0 | 115, 13, 10 |
| Scarr | CB | 57 | 23, 1, 1 (6 CS) | 115, 7, 5 (26 CS) |
XI average 68.8 → **69**. The model rates players by tier, so players of the same tier and slot weight tie (Lewis and O'Reilly 75, McAidoo and Samba 61).
**Method limits (say so):** only Haaland's goals (and Haaland's and Foden's availability) are the sim's own. Every other goal and assist is allocated afterwards (the model's attack weights per slot; 67% of goals carry an assist, the real
League One share from ESPN: 318 of 477); players play every league game of their time at City; scorers can be lucky (O'Reilly's 7 goals this season is a roughly 1-in-60 outcome for a left-back; kept, as the seed was fixed first).
League games only (no play-off or cup data). Tenure: Iroegbunam from season 2, Watts from matchday 24 of season 2 (replacing Fitzwater), McCracken from season 3 (replacing Hudson), Fapetu left after season 1.

## Part 5: the second half of season 3 (25 Nov 2026; `data/sim_l5.py`, `data/p5_run.py`, `data/squad5.py`, `data/fetch_p5.py`, `data/fetch_wing.py`)
**The two votes (the user's screenshots, 25 Nov 2026).** Poll "Who should we sign next!": Ward-Prowse 47%, Norwood 30%, Phillips 23% (785 votes, ended) → Ward-Prowse (Southampton). Comment "Make them sign jack moylan from cardiff"
(19 likes; the user's reply promised "30 likes" for the deal) → Jack Moylan (Cardiff City) on a 6-month loan, left wing, replacing T. Samba. Both are rated at their real club's level on the League One scale (`data/l5model.py`).
**The official second half (seed 2031, fixed before running).** City 1st, 82 points (second half W12 D8 L3 = 44 points), 97 goals (the most), 51 against (the fewest), GD +46, Haaland 35 league goals (13 + 22), 12 clean sheets;
promoted as champions (no play-offs). Table: MK Dons 78, Stockport 77, Luton 76, Reading 74, Stevenage 74. Title mathematically clinched on matchday 45 (lead 4 > 3 points left). City first top on matchday 27
(the best in the first half was 3rd). Key matches used: 24 Stevenage (A) 1–2 (5th), 25 Burnley 5–1, 26 Wycombe (A) 4–3 (2nd), 27 Burton 2–0 (1st), 34 Salford 6–0 (Haaland out), 37 Chesterfield (A) 3–4,
41 Plymouth (A) 1–3 (level on 73 with Stockport), 45 Cambridge 3–0 (Haaland twice, 81 points). Title odds at halfway (10,000 paired runs): 57% without the signings, 67% with Ward-Prowse, 74% with both (promotion 88% → 93% → 96%).
**Ratings and simulated stats since joining (seed 2032, fixed before running).** Rating = 60 + 80 × goals per game added v an average League One player in the slot: Ward-Prowse (DM) 69, Moylan (LW) 72, Haaland 94, Foden 84,
Lewis and O'Reilly 75, Iroegbunam 72, McCracken 66, McAidoo 61, Watts 59, Scarr 58. Stats shared out after the fact (method as the squad update): Ward-Prowse 23 games, 4 goals, 2 assists; Moylan 23 games, 1 goal, 6 assists
(a lucky-looking allocation for a player with 10 goals in 16 for Cardiff; kept, the seed was fixed first).
**Real numbers (ESPN rosters, 25 Nov 2026; `data/p5_real.json`).** Moylan (Cardiff, 25): 16 starts, 10 goals, 3 assists. Ward-Prowse (Southampton, 32): 12 starts (14 apps), 1 goal, 1 assist (not shown on screen).
**The weak spot for next season (`data/squad5.py`, upgrade one slot to an average Championship player):** right wing (McAidoo, 61) has the biggest gain (+0.076 goals per game), then centre-back (Scarr +0.060, Watts +0.042);
every other slot loses. Candidates = the Championship's most productive right-sided attackers, from ESPN match reports (`data/right_wing.json`: positions RM / AM-R / RW / RF in the line-ups): Jarrod Bowen (West Ham, 16 starts, 7 goals, 7 assists),
Amario Cozier-Duberry (Middlesbrough, 11 starts, 3 goals, 6 assists), Ollie Tanner (Cardiff, 16 starts, 3 goals, 4 assists; Moylan's team-mate). **Flags:** the commenter's public handle is shown as a credit (set `CREDIT = None` in `gen.py` to hide it);
Moylan's sim stats differ from his real form; Part 6 (the Championship) is the user's call.
