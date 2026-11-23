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
- Preview (SFX only) and the ElevenLabs script were sent; the thumbnail and posts are ready (`videos/city-part-4/thumbnail.jpg`, `youtube.md`, `social.md`; `posts.py` passes). Waiting for the user's voice.
- January vote (open): a midfielder: Kalvin Phillips (Sheffield United), James Ward-Prowse (Southampton), Oliver Norwood (Stockport). **Ask the user about the series length before Part 5**
  (the second half of season 3 + play-offs; replay the first half exactly from seed 2029, then fix a new seed).
