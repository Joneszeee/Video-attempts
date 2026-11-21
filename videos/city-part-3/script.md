# Man City in League Two, Part 3: script (as built)

All results come from the simulation (`videos/city-league-two/data/ep3.json`, seed 2028 fixed before running). Watts's and the keepers' numbers are
real (ESPN, 21 Nov 2026; `videos/city-league-two/research.md`, episode 3). The SIM tag stays on screen throughout. The words to record are in
`vo.txt` / `vo_elevenlabs.md` (14 lines, 160 words; about 66 s at 1.08×).

## Hook (A, approved): stakes with an open loop
"Man City were ninety minutes from the Championship."
- 0.0s: Wembley, the play-off final, MCI 0–0 BRA. Haaland's shot is already flying and the headline is readable.
- About 0.5s: the keeper dives the wrong way.
- About 1.2s: the shot **hits the post** (shake, red "OFF THE POST!") while 90 counts up and locks.
- It never says who won until line 13.

Hooks B ("93 goals… still didn't go up": gives the ending away) and C ("Your signing took City to Wembley": too close to Part 2's "You picked him") were not used.

## Script and picture
| # | Line | On screen |
|---|---|---|
| 1 | Man City were ninety minutes from the Championship. | Hook A (above). |
| 2 | Season two: League One. Twelfth at halfway, and leaking goals. So you voted… and half of you picked Kelland Watts. | "SEASON 2" flies through; 12th pops; leaky bucket (43 conceded). Cut on "So you voted": poll bars fill (Watts 50, Sowunmi 33, Seimen 17), the shirt flips CAMBRIDGE → WATTS. |
| 3 | A centre-back from Cambridge. Fifteen starts in League One, two goals. | Watts's clean slide tackle; his card with real stats (15 starts, 2 goals); SIGNED. |
| 4 | His second game: Leicester win four–nil. Welcome to League One. | **Match 1** (MD25): Leicester score their fourth past City (Watts closing down); bug LEI 4–0 MCI; stamp 0–4. |
| 5 | Then five wins in a row. Wycombe, Doncaster, Stevenage, Huddersfield, Notts County. City climb to fifth. | **Match 2** (MD26–30): the new table-climb card, City's row sliding 13th → 5th as each club is named; 5TH stamp. |
| 6 | Grimsby come to City. Haaland scores twice. Top three for the first time. | **Match 3** (MD35): Haaland's goal; bug MCI 2–0 GRI; TOP 3 stamp (best in the first half was 6th). |
| 7 | Stockport win a seven-goal thriller, four–three. Remember them. | **Match 4** (MD37): seven balls rain into a counter (3 City, 4 Stockport); bug MCI 3–4 STO; freeze and a red ring under the Stockport player. |
| 8 | Oxford, the champions, win four–two. Haaland still ends on twenty-nine. | **Match 5** (MD42): Oxford lift the trophy in confetti; bug OXF 4–2 MCI. Cut: Haaland close-up, his count races 18 → 29. |
| 9 | But here's where it hurts. The last day: level on points with second… against Cambridge. Watts's old club. | Re-hook: VHS "LAST DAY"; the table after MD45 (City 3rd on 77, level with Wednesday); LEVEL ON 77. Cut: Watts v a Cambridge player, bug MCI 0–0 CAM, HIS OLD CLUB. |
| 10 | One–one. Wednesday win. City finish fourth. | Bug 1–1; the table steps to the final standings and City's row drops 3rd → 4th; 4TH stamp ("two points off going up"). |
| 11 | Play-offs. Stockport again. Four–nil over two legs. | Split screen (home and away): 2–0, 2–0; 4–0 on aggregate. |
| 12 | Then Wembley. Bradford City, the best defence in the league. | Face-off at Wembley: Haaland v Bradford; "30 goals conceded · the fewest" tag. |
| 13 | Bradford win two–nil. City stay in League One. | Bradford's second goes in; bug BRA 2–0 MCI; freeze; STAYING DOWN. |
| 14 | Ninety-three goals, the most in the league. Not enough. Who should City sign this summer? | Goal barrage from behind the net, 93 counts up; NOT ENOUGH (74 conceded). Cut: the keeper vote (below) and a poll. |

All scores are sim scores. No scorer is named except through Haaland's count. Watts is never shown striking the ball (his footedness isn't confirmed).

## The summer vote: a keeper (user: two well-known Championship names, "pretty decent, not too good")
City still conceded the 6th-most goals, and in the model the keeper carries the biggest single share of the defence.
| Keeper | Club | Age | Starts | Clean sheets | Saves per game |
|---|---|---|---|---|---|
| José Sá | Wolves (Championship) | 33 | 15 | 4 | 2.5 |
| Gavin Bazunu | Bolton (Championship), ex-City academy | 24 | 8 | 2 | 3.6 |
| Jon McCracken | Bradford (League One), the keeper who beat City at Wembley | 26 | 13 | 9 | 1.5 |
