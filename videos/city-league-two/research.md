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
