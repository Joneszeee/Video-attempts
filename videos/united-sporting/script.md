# Sporting 2–2 Man United: script (Champions League, league phase matchday 5, Wednesday 25 Nov 2026)

A real match, not a sim. Every minute, score, shot count and table position comes from ESPN's feed (`data/fetch.py`; `gen.py` asserts every one of them, so a wrong number stops the build).
Every sentence about a referee decision is ESPN's own (the recap article and the play-by-play) and is said as "ESPN says" or shown with "per ESPN match report". The referee is never named ("the referee").
Nothing on screen is our verdict: the viewers decide, in the poll at the end (the one hype line, "the craziest match you'll ever see", is the user's own wording). The words to record are in `vo.txt` / `vo_elevenlabs.md` (12 lines, 174 words).
The jokes: "Not that one" (two different Luis Suárezes: the Sporting striker, and the famous one), and the divot.

## Three hooks (frame plans, virality checklist)
**A (picked, the user's idea): "Luis Suárez just scored twice against Manchester United. Not that one."** Pattern: a claim that sounds wrong, then the twist (rotated from Part 5's number clash and
Pochettino's "result first"). The user's wording was "scored 2 goals against Manchester United in the craziest football match ever": the craziest-match line is beat 2.
- 0.0s: Suárez fills the lower two-thirds of the frame in Sporting's green-and-white hoops, 97 on his chest; the gold "2 GOALS V MAN UNITED" tag is already above his head; the other Suárez stands beside him as a half
  see-through ghost in a plain pale-blue shirt, labelled THE OTHER ONE; the score bug SCP 2–2 MUN is already on screen; every headline word is readable; zoom burst and speed lines.
- 0.5s: "Luis Suárez": the first spoken word is the subject; each headline word flashes in turn (hookWords).
- 1.2–1.6s: "twice against Manchester United": the tag and the score pop.
- 3.0s: "Not that one": a red X is drawn across the ghost, the camera shakes and Suárez throws his arms up.
- Checklist: moving on frame 0 (push-in, speed lines, zoom burst); instantly recognisable (a Sporting shirt, the real 97, a score line); the biggest element (Suárez) fills 40%+ of the frame; something happens
  before 3s (the X); the subject is the first spoken word; works on mute (headline + tag + score); it is the viewer's world (Man United).
**B: "Three penalties. Two goals ruled out. One divot."** Pattern: a list of absurd numbers (curiosity). Held back: no person in the first second, so weaker for search ("Suárez", "Man United"); it is beat 2.
**C: "Man United took a point in Lisbon. The officials took the rest."** Pattern: stakes / controversy. Held back: it overclaims; ESPN reports the decisions, the viewers decide (that is the ending question).

## Script and picture
| # | Line | On screen |
|---|---|---|
| 1 | Luis Suárez just scored twice against Manchester United. Not that one. | Hook A (above). |
| 2 | The craziest match you'll ever see: three penalties, two disallowed goals, a divot, a red card. | A slow orbit round the penalty area with the players in it; the **stacked counter** 3 / 2 / 1 / 1 on each word. |
| 3 | Thirty minutes: penalty to Sporting. Suárez hits it down the middle. Lammens saves it. | **New: penalty duel.** Three-quarter view from behind the taker: he stands back, runs in, hits a weak shot down the middle (ESPN: "saved in the centre of the goal"), Lammens reaches and holds it (the ball ends in his gloves). Whistle on "penalty", SAVED stamp, the **penalty tracker** (new card) goes red on its first slot. |
| 4 | Then Lammens charges out and bundles Araújo. Second penalty. Suárez scores this one. | **New: bundle.** Araújo chases a loose ball, the keeper charges off his line and dives at his feet, both go down, yellow card; cut to penalty two: low into the left corner, the keeper dives the other way; tracker slot 2 ticks; score 1–0. |
| 5 | Forty minutes: Amad scores, but the referee had already blown. ESPN says too early, so VAR couldn't look. | **New: whistle first.** VHS rewind; the through ball, Amad's shot, the bar, the header goes in (it looks like a goal); the **VAR monitor card** (new) then lists the real order: shot hits the bar, whistle (TOO EARLY, glowing, with the sound), header, verdict NO GOAL · VAR could not review, "per ESPN match report". |
| 6 | Second half: Martínez wins a penalty. Bruno Fernandes, Sporting's old star, scores. | Penalty three from the other side; the tracker's third slot ticks; EX-SPORTING stamp; score 1–1. |
| 7 | Two minutes later, Bruno again. His shot hits a divot and flies over the keeper. | **New: the divot goal.** Bruno (left foot) from outside the box; cut to a low camera at the turf: the ball skids onto the scuffed patch (a new dust-and-ring **puff** card, the patch stays on the grass, a DIVOT pill) and kicks up over the keeper's hands. Score 1–2. |
| 8 | Eightieth minute: Lammens goes for a high ball. ESPN says Suárez nudged him. Suárez scores. Two–two. | **New: cross and finish.** The TV pen draws the cross, the keeper jumps with Suárez on him (ESPN: "nudged off balance"), he lands flat, Suárez finishes with a leap; the pen circles the contact (NUDGE · ESPN); then GOAL STANDS · after VAR review. |
| 9 | Then Sporting's keeper flaps at a corner and scores an own goal. VAR rules it out for a foul by Dorgu. Tielemans, already booked, is sent off. | Mirror camera: Dorgu leans on the keeper, who flaps it into his own net; the VAR monitor card (keeper flaps, sent to the monitor, judged: Dorgu fouled the keeper, NO GOAL); cut: Tielemans slides in from behind, the referee's second yellow, then red. |
| 10 | Sporting had eleven shots, United seven. Sporting's keeper made no saves. | The **shot timeline** (every shot on a minute track, 11 v 7, goals pinned, the red card marker), then a 0 SAVES stamp. |
| 11 | United took a point. Nineteenth, three games left. | The **table climb**: the table when United kicked off (19th, 6 points) and now (still 19th, 7 points), the play-off zone and the cut-off below it; 3 LEFT stamp (8-game league phase). |
| 12 | Pochettino's second game, still no win. Brentford on Saturday. Were the officials fair? | The **form strip**: L 0–4 Liverpool, D 2–2 Sporting, ? Brentford, NO WIN YET; then the **poll sticker** "Were the officials fair?" (Fair / Not fair, results empty: the real poll is the user's). |

## Facts checked (all asserted in `gen.py`)
- Result and venue: Sporting CP 2–2 Manchester United, Estádio José Alvalade (ESPN header, Full Time).
- 30' penalty saved, Suárez, "saved in the centre of the goal by Senne Lammens"; 31' Lammens fouls Maxi Araújo, penalty, yellow card; the recap: "charged off his line", "bundled over Maximiliano Araujo".
- 33' Suárez converts (1–0). 40' Tielemans booked. Amad's first-half leveller ruled out: "blown his whistle early meaning the VAR could not intervene" (ESPN recap).
- 47' Martínez draws the foul, 48' Bruno Fernandes converts (1–1); 50' Fernandes, left foot, from outside the box, assisted by Amad: "hit a divot just outside the six-yard box and flew over" (1–2).
- 80' Suárez (2–2), "Goal confirmed following VAR Review"; the recap: "nudged off balance by Suárez", "Calls for a foul were dismissed". 82' own goal by Kaique, "VAR Decision: No Goal"; "adjudged Dorgu to have fouled the goalkeeper".
- 90'+3 Tielemans, second yellow card (ESPN).
- Shots 11 v 7, Sporting's saves 0 (ESPN boxscore); penalties = 30' saved, 33' scored, 48' scored; goals = four.
- Table (ESPN standings; the 18 matchday-5 results reversed, then Tuesday's nine put back, to get the table at kick-off; the same sort rule reproduces ESPN's final table exactly): United started the matchday 17th on 6 points, were already 19th on 6 at kick-off (Tuesday's results), and are 19th on 7 after the draw; the league phase is 8 games, so 3 left. (An earlier draft said "dropped two places": that was wrong for this game, so the line was changed.)
- Pochettino: first game a 0–4 loss at Liverpool (22 Nov), second this 2–2; next Brentford on Saturday (ESPN recap).
- Not claimed: anything about why the decisions were made beyond ESPN's words; the referee's name; who deserved what.

## What is reconstruction (not match footage)
The goals, saves and fouls are re-enacted by drawn players, so only the facts above are claims. Not given by ESPN, so chosen by us: how Lammens held or parried the 30' penalty and what happened between it and the 31' foul; where the loose ball
Araújo chased came from; which wing the 80' cross came from and what kind of finish it was ("acrobatic" is ESPN's word); the exact shape of the own goal; the kits (Sporting's hoops and United's red are stylised, the keepers' colours are ours, the referee's shirt is yellow);
the other Suárez is a plain pale-blue ghost, not a likeness.

## What is new in the engine (reusable)
`lib.penalty`, `lib.bundle`, `lib.goal_divot`, `lib.goal_cross` (also an own goal, mirrored), `lib.disallowed`; cards `puff`, `varcheck`, `pentrack`, `sound`; sfx `whistle` and `thud`; `climb` window (`from`);
`form` "?" chip; spec `ballScale`. See CLAUDE.md.
