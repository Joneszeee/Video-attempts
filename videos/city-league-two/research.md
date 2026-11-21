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
