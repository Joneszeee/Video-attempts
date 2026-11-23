# Man City in League Two: squad update (between Parts 4 and 5), script

A walkout of City's starting XI as collectible-style cards: a rating, this season's stats (23 games) and all-time stats (three simulated seasons). The words to record are in
`vo.txt` / `vo_elevenlabs.md` (10 lines, 122 words; about 50 s at 1.08×).

## How the numbers are made (say it in the description; `videos/city-league-two/data/squad.py`)
- **Rating** = 60 + 80 × the goals per game a player adds to City's goal difference compared with an average League One player in his slot (the Part 4 model). 60 = average, each point = 0.0125 goals a game.
  Cards: bronze under 65, silver 65–74, gold 75–84, elite 85+. XI average 69.
- **Stats**: the sim recorded City's scores, Haaland's and Foden's availability and Haaland's goals (29, 29 and 13: 71 in 100 games). The rest are **shared out after the fact with a seed fixed before running
  (2030), without changing any score**: every other City goal goes to a scorer in proportion to the model's attack weight for his slot, 67% of goals carry an assist (the real League One share, 318 of 477),
  assisted by the same weights. Players play every league game of their time at City (the model has no other absences). Clean sheets and goals conceded come straight from the scores. League games only.
- Players' time at City: Iroegbunam from season 2, Watts from matchday 24 of season 2, McCracken from season 3 (all-time rows count only that time).

## Three hooks (frame plans, virality checklist)
**A (picked): "Haaland: ninety-one. City's worst starter: fifty-seven."** Pattern: two numbers that clash (and an open loop: who is the 57?).
- 0.0s: Haaland's elite card (91) on the left and a bronze card (57) on the right, already in place and shining; the stadium behind pushes in; speed lines. Every headline word is on screen.
- 0.5s: a light sweep runs across both cards; crowd flashes.
- 1.2s: the claim lands: "[91]" and "[57]" flash in the headline.
- 3.0s: cut to the rules ("60 = an average League One player"); the 57 is revealed as Scarr on line 3.
- Checklist: moving on frame 0, a famous player on a card, two big cards fill the frame, the numbers race and lock, the first word is the subject, works on mute, the viewer's world (their team, their picks).
**B: "A teenager on City's wing has more goals than Foden."** Pattern: a claim that sounds wrong. Held back: it rests on a sim artefact (115 games v 96) and gives away the surprise of line 5.
**C: "Rating Man City's whole team after three simulated seasons."** Pattern: plain list. Held back: no conflict or open loop.

## Script and picture
| # | Line | On screen |
|---|---|---|
| 1 | Haaland: ninety-one. City's worst starter: fifty-seven. | Hook A: the two cards side by side (elite 91, bronze 57), shine sweep. |
| 2 | Every starter in City's team, rated by the model. Sixty is an average League One player. | "60" slams in with "= an average League One player"; four small cards (bronze, silver, gold, elite) drop in with their ranges. |
| 3 | Centre-backs. Scarr: fifty-seven, the worst. But twenty-six clean sheets. Watts: fifty-nine, your pick. | Scarr (bronze) and Watts (bronze, FAN PICK) fly in from the sides. |
| 4 | Midfield. Braybrooke: fifty-nine. Iroegbunam: seventy-one, another of your picks. | Braybrooke (bronze) drops in, Iroegbunam (silver, FAN PICK) zooms in. |
| 5 | The kids on the wings: sixty-one each. Samba has thirty-one goals… more than Foden. | VHS pattern break on the stage; McAidoo and Samba (bronze); a "31 v 22" stamp on "more than Foden". |
| 6 | In goal: McCracken. Sixty-six. Six clean sheets since you signed him. | McCracken (silver, FAN PICK), one stat row (his only season). |
| 7 | Full-backs: Lewis and O'Reilly. Seventy-five each. O'Reilly has seven goals this season. | Two gold cards, confetti and flashes; a "7 goals" tag on O'Reilly. |
| 8 | Foden: eighty-two. Twenty-two goals, twenty assists. | Foden (gold), zoom entry. |
| 9 | And Haaland. Seventy-one goals in a hundred games. Thirteen this season. | Haaland (elite) on the stage: rays, sparkles, shake; "71" counts up. |
| 10 | The team: sixty-nine. Whose rating is wrong? And who fixes midfield? Vote in the poll. | The XI on a pitch with every rating, a pulsing "?" in midfield; the poll (Phillips, Ward-Prowse, Norwood). |
