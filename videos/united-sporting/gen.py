# Builds videos/united-sporting/spec.json (run from the repo root). Sporting 2-2 Manchester United, Champions League league phase, matchday 5, 25 Nov 2026 (the evening before this was made).
# Every minute, score, stat and table position comes from ESPN's feed (data/fetch.py: summary.json = key events, play-by-play commentary, boxscore, rosters and the recap article;
# shots.json = every shot; table.json + results_md5.json = the league table now and the matchday-5 results). The game is not a sim: all of this is real. The words that describe a
# referee decision are ESPN's (the recap and the commentary) and are said as "ESPN says"; the referee is never named; no opinion on screen is ours.
import json
import sys
sys.path.insert(0, 'engine')
from lib import *

D = 'videos/united-sporting/data/'
SM = json.load(open(D + 'summary.json')); SH = json.load(open(D + 'shots.json')); TB = json.load(open(D + 'table.json')); R5 = json.load(open(D + 'results_md5.json')); UR = json.load(open(D + 'united_results.json'))
comp = SM['header']['competitions'][0]
ART = ' '.join(__import__('re').sub(r'<[^>]+>', ' ', SM['article'].get('story', '')).split())
COM = [(c['time']['displayValue'], c['text']) for c in SM['commentary']]
has = lambda minute, *frags: any(m == minute and all(f in t for f in frags) for m, t in COM)
art = lambda *frags: all(f in ART for f in frags)
# --- every fact the voice or the screen states, checked against the feed (a wrong number stops the build)
assert [(c['team']['displayName'], c['score'], c['homeAway']) for c in comp['competitors']] == [('Sporting CP', '2', 'home'), ('Manchester United', '2', 'away')] and comp['status']['type']['description'] == 'Full Time'
assert has("30'", 'Penalty saved', 'Luis Suárez', 'saved in the centre of the goal by Senne Lammens')                                     # "Suárez hits it down the middle. Lammens saves it"
assert has("31'", 'Maxi Araújo draws a foul') and has("31'", 'Penalty conceded by Senne Lammens') and has("31'", 'Senne Lammens', 'yellow card')   # "Lammens charges out and bundles Araújo. Second penalty"
assert art('charged off his line', 'bundled over Maximiliano Araujo')
assert has("33'", 'Goal!', 'Luis Suárez', 'converts the penalty', 'Sporting Lisbon 1, Manchester United 0')                                  # "Suárez scores this one"
assert has("40'", 'Youri Tielemans', 'yellow card')                                                                                         # "already booked"
assert art('Amad Diallo saw a first half leveler ruled out', 'blown his whistle early', 'VAR could not intervene', 'blow his whistle just before the winger headed in the loose ball')
assert has("47'", 'Lisandro Martínez draws a foul') and has("48'", 'Goal!', 'Bruno Fernandes', 'converts the penalty')                        # "Martínez wins a penalty. Bruno Fernandes scores"
assert art('former Sporting star') and art('Fernandes kept his cool')                                                                       # "Sporting's old star"
assert has("50'", 'Goal!', 'Bruno Fernandes', 'left footed shot from outside the box', 'Assisted by Amad Diallo') and art('hit a divot just outside the six-yard box and flew over')   # "Two minutes later, Bruno again. His shot hits a divot..."
assert has("80'", 'Goal!', 'Luis Suárez', 'Sporting Lisbon 2, Manchester United 2', 'Goal confirmed following VAR Review') and art('nudged off balance by Suárez', 'high ball', 'Calls for a foul were dismissed')
assert has("82'", 'Own Goal by Kaique') and has("82'", 'Foul by Patrick Dorgu') and has("82'", 'VAR Decision: No Goal') and art('flapped at a corner', 'adjudged Dorgu to have fouled the goalkeeper')
assert has("90'+3'", 'Second yellow card to Youri Tielemans')                                                                                 # "Tielemans, already booked, is sent off"
assert art('three penalties', 'a pair of controversially ruled out goals', 'bobble-assisted', 'stoppage-time red card')                      # "three penalties, two disallowed goals, a divot, a red card"
penalties = [s for s in SH if s['penalty']]
assert [(s['min'], s['who'], s['kind']) for s in penalties] == [(30, 'Suárez', 'saved'), (33, 'Suárez', 'goal'), (48, 'Fernandes', 'goal')]   # the three penalties (the 31' foul is the second one's award)
assert [(s['min'], s['who']) for s in SH if s['kind'] == 'goal'] == [(33, 'Suárez'), (48, 'Fernandes'), (50, 'Fernandes'), (80, 'Suárez')]
box = {t['team']['displayName']: {x['name']: x['displayValue'] for x in t['statistics']} for t in SM['boxscore']['teams']}
assert (box['Sporting CP']['totalShots'], box['Manchester United']['totalShots'], box['Sporting CP']['saves']) == ('11', '7', '0')              # "eleven shots, United seven. Sporting's keeper made no saves"
assert (sum(s['side'] == 'home' for s in SH), sum(s['side'] == 'away' for s in SH)) == (11, 7) and box['Manchester United']['redCards'] == '1'
ros = {t['team']['displayName']: {p['athlete']['displayName']: p['jersey'] for p in t['roster']} for t in SM['rosters']}
assert ros['Sporting CP']['Luis Suárez'] == '97' and ros['Sporting CP']['Maxi Araújo'] == '20' and ros['Manchester United']['Bruno Fernandes'] == '8' and ros['Manchester United']['Amad Diallo'] == '16'
assert ros['Manchester United']['Youri Tielemans'] == '18' and ros['Manchester United']['Patrick Dorgu'] == '13' and ros['Sporting CP']['Sergi Altimira'] == '5'
# the league table: reverse the 18 matchday-5 results to get the table before this game (the sort rule reproduces ESPN's table, so it is the same rule)
tab = {r['team']: dict(p=r['p'], pts=r['pts'], gd=int(r['gd']), gf=int(r['gf'])) for r in TB}
pre = {k: dict(v) for k, v in tab.items()}
assert len(R5) == 18 and len({t for m in R5 for t in (m['home'], m['away'])}) == 36
for m in R5:
    for t, f, c in ((m['home'], m['hg'], m['ag']), (m['away'], m['ag'], m['hg'])):
        pre[t]['p'] -= 1; pre[t]['gf'] -= f; pre[t]['gd'] -= f - c; pre[t]['pts'] -= 3 if f > c else 1 if f == c else 0
assert all(v['p'] == 4 for v in pre.values()) and all(v['p'] == 5 for v in tab.values())
order = lambda d: sorted(d, key=lambda t: (-d[t]['pts'], -d[t]['gd'], -d[t]['gf']))
post_rank = {t: i + 1 for i, t in enumerate(order(tab))}; pre_rank = {t: i + 1 for i, t in enumerate(order(pre))}
assert post_rank == {r['team']: r['rank'] for r in TB}                                                                                       # the rule reproduces ESPN's table exactly
MU = 'Manchester United'
def play(base, games):
    d = {k: dict(v) for k, v in base.items()}
    for m in games:
        for t, f, c in ((m['home'], m['hg'], m['ag']), (m['away'], m['ag'], m['hg'])):
            d[t]['p'] += 1; d[t]['gf'] += f; d[t]['gd'] += f - c; d[t]['pts'] += 3 if f > c else 1 if f == c else 0
    return d
kickoff = play(pre, [m for m in R5 if m['date'] == '2026-11-24'])                                                                            # the table when United kicked off: Tuesday's nine games are in
assert len([m for m in R5 if m['date'] == '2026-11-24']) == 9 and [m for m in R5 if m['home'] == 'Sporting CP'][0]['date'] == '2026-11-25'
rank_of = lambda d, t: order(d).index(t) + 1
assert (pre_rank[MU], pre[MU]['pts']) == (17, 6) and (rank_of(kickoff, MU), kickoff[MU]['pts']) == (19, 6) and (post_rank[MU], tab[MU]['pts']) == (19, 7)   # United were already 19th at kick-off (Tuesday's results): the draw kept them there
key_of = lambda d: (lambda t: (d[t]['pts'], d[t]['gd'], d[t]['gf']))
assert all(key_of(kickoff)(order(kickoff)[i]) != key_of(kickoff)(order(kickoff)[i + 1]) for i in range(14, 21))                              # no exact tie around United: the order is not a guess
assert all(key_of(tab)(order(tab)[i]) != key_of(tab)(order(tab)[i + 1]) for i in range(14, 21))
LEAGUE_GAMES = 8; assert LEAGUE_GAMES - tab[MU]['p'] == 3                                                                                    # "three games left" (the league phase is 8 games)
assert (UR[-1]['opp'], UR[-1]['score'], UR[-1]['res'], UR[-1]['venue']) == ('Sporting CP', '2-2', 'D', 'away') and (UR[-2]['opp'], UR[-2]['score'], UR[-2]['res']) == ('Liverpool', '0-4', 'L')
assert art('first win in charge', 'chastening 4-0 loss at rivals', 'Brentford on Saturday')                                                  # "Pochettino's second game, still no win. Brentford on Saturday"

# --- kits and looks
SPT = kit("#0b8f4b", "#ffffff", "#0b8f4b", text="#111111", hoops=["#0b8f4b", "#ffffff"])      # Sporting: green and white hoops
MUN = kit("#d6283b", "#ffffff", "#111111", text="#ffffff")                                   # United: red
GKM = kit("#ff7a1a", "#111111", "#ff7a1a", text="#111111")                                   # Lammens (a keeper colour of our own, not the real kit)
GKS = kit("#7a4de0", "#111111", "#7a4de0", text="#ffffff")                                   # Kaique
OLD = kit("#7ab2e8", "#111111", "#111111", text="#111111")                                   # "the other Suárez": a plain pale-blue shirt, no crest
SUA = dict(skin="#c99b7a", hair="#141010", name="SUÁREZ", num=97)
BRU = dict(skin="#f0c8a8", hair="#6a4a2a", name="FERNANDES", num=8)
AMA = dict(skin="#8a5a3c", hair="#141010", name="AMAD", num=16)
ARA = dict(skin="#c99b7a", hair="#141010", name="ARAÚJO", num=20)
DOR = dict(skin="#8a5a3c", hair="#141010", name="DORGU", num=13)
TIE = dict(skin="#f0c8a8", hair="#6a4a2a", name="TIELEMANS", num=18)
ALT = dict(skin="#e7b593", hair="#3a2a1a", name="ALTIMIRA", num=5)
SCP = {"name": "SCP", "color": "#0b8f4b"}
MUB = {"name": "MUN", "color": "#d6283b"}
mbug = lambda score, mn, frm=None, goalAt=None, **k: bug(SCP, MUB, score, mn, frm=frm, goalAt=goalAt, **k)
CROWD = ["#0b8f4b", "#ffffff", "#0b8f4b", "#111111"]
S_A, S_B, S_C, S_D = stadium(CROWD, 11), stadium(CROWD, 23), stadium(CROWD + ["#d6283b"], 31), stadium(CROWD, 47)
YEL = "#f7d117"
KICK = "Sporting 2–2 Man United · Champions League"

V, lines = start('videos/united-sporting/')
B = []


def tracker(*items, y=1625):
    """The penalty tracker: items are (who, minute, state, result, word or None); a word pops it, no word = already there; state 'empty' = a slot to come."""
    out = []
    for who, mn, state, result, word in items:
        it = {"who": who, "min": mn, "state": state, "result": result}
        if word:
            it.update(at=word, lag=-0.05)
        out.append(it)
    return {"type": "pentrack", "y": y, "delay": 0.0, "title": "Penalties", "items": out, "h": 340, "clear": False}


P1 = ("Suárez", "30'", "miss", "SAVED", None)
P2 = ("Suárez", "33'", "hit", "GOAL", None)
EMPTY = lambda who, mn: (who, mn, "empty", "", None)

# 1 HOOK (pattern: a claim that sounds wrong, then the twist). Frame 0: Suárez fills the frame in Sporting's hoops, the number 97 on his chest, the score is already on screen and every headline word is readable;
# the other Suárez (a ghost in a plain pale-blue shirt) stands beside him and gets crossed out on "Not that one"
B.append({"kicker": KICK, "headline": "Suárez scored [twice] vs Man United. Not [that one].", "hookWords": True, "scene": S_A, "accent": TEAL, "lights": 0.95, "flashes": 14, "hype": False,
  "camFrom": {"pos": [0, 1.4, -3.1], "tgt": [0, 2.6, 10]}, "camera": {"pos": [0, 1.4, -2.6], "tgt": [0, 2.6, 10]}, "move": 3.8, "moveEase": "linear",
  "players": [P(kit=SPT, x=0.42, z=0.0, front=True, chest=True, action="celebrate", actionAt="Not that one", actionLag=0.0, tag=2, tagLabel="goals v Man United", tagDelay=-0.45, **SUA),
              P(kit=OLD, x=-0.55, z=0.8, front=True, ghost=True, name="SUÁREZ", num=9, skin="#e7b593", hair="#141010", label="THE OTHER ONE", labelDelay=-0.3)],
  "card": [mbug([2, 2], "FT", y=1660, delay=-1.0, clear=False),
           {"type": "pen", "anchor": 1, "strokes": [{"kind": "x", "cx": 0, "cy": -0.5, "r": 0.46, "at": "Not that one", "lag": 0.0, "dur": 0.45, "color": RED, "width": 16}]}],
  "speedlines": [{"t": 0.0, "dur": 0.9, "amount": 0.7}], "shake": [{"at": "Not that one", "amount": 12}]})

# 2 the craziest match: an orbit around the penalty area (everyone is in it), the stacked counter on the words: 3 penalties, 2 goals ruled out, 1 divot, 1 red card
box_players = [P(kit=SPT, skin="#c99b7a", hair="#141010", x=-3.6, z=44.5, front=True, action="idle"), P(kit=MUN, skin="#f0c8a8", hair="#6a4a2a", x=2.8, z=45.4, front=True, action="idle"),
               P(kit=SPT, skin="#e7b593", hair="#3a2a1a", x=5.4, z=42.0, front=True, action="idle"), P(kit=MUN, skin="#8a5a3c", hair="#141010", x=-6.0, z=41.2, front=True, action="idle"),
               P(kit=GKM, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper"), P(kit=SPT, skin="#f0c8a8", hair="#6a4a2a", x=0.6, z=39.0, front=True, action="idle")]
B.append({"kicker": "The craziest match", "headline": "[3] penalties. [2] goals ruled out.", "cut": True, "transition": "whip", "scene": S_B, "accent": TEAL, "lights": 0.8, "focus": 0.25, "flashes": 10, "hype": False,
  "orbit": {"center": [0, 1.2, 44.5], "r": 17, "from": -60, "to": 60, "h": 11, "h2": 6, "dur": 6.0}, "players": box_players,
  "card": [mbug([2, 2], "FT"), {"type": "ball", "point": [0, 0.11, 41.5], "delay": 0},
           {"type": "stack", "y": 1400, "size": 170, "delay": 0, "items": [{"value": 3, "label": "penalties", "at": "three penalties"}, {"value": 2, "label": "goals ruled out", "at": "two disallowed"},
                                                                           {"value": 1, "label": "divot", "at": "a divot"}, {"value": 1, "label": "red card", "at": "red card"}]}]})

# 3 penalty one: Suárez hits it at the keeper's chest, Lammens stops it and holds it (the engine's saveBy puts the ball in his gloves); the tracker's first slot goes red on "saves"
pl, cards, camk = penalty("saves", SPT, GKM, outcome="saved", save="lunge", save_dir=1, lag=-0.15, label="Suárez", kicker=SUA, keeper_label="Lammens", keeper_label_at="Lammens")
B.append({"kicker": KICK, "headline": "30': [penalty] to Sporting.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_A, "accent": TEAL, "lights": 0.95, **camk, "players": pl,
  "card": cards + [mbug([0, 0], "30'"), {"type": "sound", "name": "whistle", "at": "penalty", "lag": -0.1},
                   tracker(("Suárez", "30'", "miss", "SAVED", "saves"), EMPTY("Suárez", "33'"), EMPTY("Bruno", "48'")),
                   stamp("SAVED", "saves", sub="Lammens", color=GOLD, y=800, size=104, lag=-0.05)]})

# 4 the keeper charges out and bundles Araújo (yellow card), then penalty two: Suárez scores low into the left corner (the keeper goes the other way)
pl, cards, camk = bundle("bundles", SPT, GKM, lag=0.0, label="Araújo", victim=ARA, keeper_label="Lammens", keeper_label_at="Lammens")
pl2, cards2, camk2 = penalty("scores", SPT, GKM, outcome="scored", corner=-1, lag=-0.05, label="Suárez", kicker=SUA)
B.append({"kicker": KICK, "headline": "Lammens [bundles] him. Penalty [two].", "cut": True, "transition": "whip", "scene": S_B, "accent": TEAL, "lights": 0.95, **camk, "players": pl,
  "card": cards + [mbug([0, 0], "31'"), {"type": "sound", "name": "whistle", "at": "bundles", "lag": 0.15}, {"type": "redcard", "color": YEL, "at": "bundles", "lag": 0.25, "label": "31' Lammens", "dx": 260, "y": 1450}],
  "shots": [{"at": "Second penalty", "lag": 0.1, "cut": True, "transition": "whip", "headline": "33': Suárez [scores]. 1–0.", "scene": S_A, **camk2, "players": pl2,
             "card": cards2 + [mbug([1, 0], "33'", frm=[0, 0], goalAt="scores", lag=0.2), tracker(P1, ("Suárez", "33'", "hit", "GOAL", "scores"), EMPTY("Bruno", "48'")),
                               {"type": "sound", "name": "whistle", "at": "Second penalty", "lag": -0.1}]}]})

# 5 whistle too early: Amad's shot hits the bar and he heads in the rebound; it looks like a goal. The VAR monitor card then shows the real order and the tag TOO EARLY (ESPN's words), then the verdict
pl, cards, camk = disallowed("scores", MUN, GKS, SPT, lag=0.0, label="Amad", scorer=AMA, whistle=False)
B.append({"kicker": KICK, "headline": "40': Amad scores. [Whistle] first.", "cut": True, "transition": "vhs", "vhsLabel": "REWIND", "vhsDur": 1.2, "scene": S_C, "accent": RED, "lights": 0.85, **camk, "players": pl,
  "card": cards + [mbug([1, 0], "40'"),
                   {"type": "varcheck", "title": "VAR · 40'", "y": 1330, "w": 940, "rowH": 84, "verdictH": 200, "source": "per ESPN match report", "at": "referee", "lag": 0.1, "clear": False,
                    "steps": [{"text": "Amad's shot hits the bar", "at": "referee", "lag": 0.35, "kind": "ball"},
                              {"text": "Referee blows his whistle", "at": "already blown", "lag": -0.1, "kind": "whistle", "tag": "TOO EARLY", "tagColor": RED},
                              {"text": "Amad heads in the rebound", "at": "ESPN", "lag": 0.0, "kind": "goal"}],
                    "verdict": {"text": "NO GOAL", "sub": "VAR could not review", "color": RED, "at": "VAR", "lag": 0.05, "size": 112}}]})

# 6 penalty three: Martínez wins it, Bruno (Sporting's old star) scores low into the left corner; the tracker's third slot ticks on "scores"
pl, cards, camk = penalty("scores", MUN, GKS, outcome="scored", corner=-1, foot="right", side=1, lag=-0.05, label="Bruno", kicker=BRU)
B.append({"kicker": KICK, "headline": "48': [Bruno] scores. 1–1.", "cut": True, "transition": "whip", "scene": S_D, "accent": TEAL, "lights": 0.95, **camk, "players": pl,
  "card": cards + [mbug([1, 1], "48'", frm=[1, 0], goalAt="scores", lag=0.2), {"type": "sound", "name": "whistle", "at": "Martínez", "lag": 0.5},
                   tracker(P1, P2, ("Bruno", "48'", "hit", "GOAL", "scores")), stamp("EX-SPORTING", "old star", sub="Bruno Fernandes", color=GOLD, y=770, size=88, lag=0.0)]})

# 7 the divot goal: the shot from outside the box, the cut to the low camera at the turf (the scuffed patch and the DIVOT pill), the ball kicks up over the keeper
pl, cards, camk, cut2 = goal_divot("keeper", MUN, GKS, SPT, foot="left", lag=-0.1, label="Bruno", shooter=BRU, t1=0.95, t2=1.0, cut_lag=0.3)
cut2.update({"headline": "50': a [divot]. 1–2.", "card": "same"})
B.append({"kicker": KICK, "headline": "50': Bruno [again].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_A, "accent": TEAL, "lights": 0.95, **camk, "players": pl,
  "card": cards + [mbug([1, 2], "50'", frm=[1, 1], goalAt="keeper", lag=0.3)], "shots": [cut2]})

# 8 cross and finish: the high ball, the keeper goes for it, Suárez nudges him (ESPN's word), he flaps and the striker finishes; the pen marks the nudge, then GOAL STANDS (VAR review confirmed it)
pl, cards, camk = goal_cross("scores", SPT, GKM, MUN, lag=-0.05, label="Suárez", scorer=SUA, keeper_label="Lammens", keeper_label_at="Lammens")
B.append({"kicker": KICK, "headline": "80': [Suárez] again. 2–2.", "cut": True, "transition": "whip", "scene": S_B, "accent": TEAL, "lights": 0.95, **camk, "players": pl,
  "card": cards + [mbug([2, 2], "80'", frm=[1, 2], goalAt="scores", lag=0.2),
                   {"type": "pen", "anchor": 1, "strokes": [{"kind": "ellipse", "cx": 0.28, "cy": -0.62, "rx": 0.34, "ry": 0.24, "at": "nudged", "lag": 0.0, "dur": 0.5, "color": GOLD, "width": 8},
                                                           {"kind": "text", "text": "NUDGE · ESPN", "x": 0.95, "y": -1.38, "size": 0.2, "at": "nudged", "lag": 0.25, "dur": 0.6, "color": GOLD, "rot": -0.08}]},
                   {"type": "pen", "strokes": [{"kind": "arrow", "points": [[110, 760], [280, 690], [400, 880]], "at": "high ball", "lag": -0.2, "dur": 0.7, "color": GOLD, "width": 7, "dashed": True},
                                               {"kind": "text", "text": "CROSS", "x": 120, "y": 690, "size": 56, "at": "high ball", "lag": -0.1, "dur": 0.5, "color": GOLD, "rot": -0.08}]},
                   stamp("GOAL STANDS", "scores", sub="after VAR review", color=GREEN, y=1480, size=92, lag=0.45)]})

# 9 own goal ruled out, then the red card: shot 1 the keeper flaps at the corner, Dorgu leaning on him, the ball drops in; the monitor card follows on the words; shot 2 Tielemans's tackle and the red card
pl, cards, camk = goal_cross("scores", MUN, GKS, SPT, own_goal=True, mirror=True, lag=-0.05, label="Dorgu", scorer=DOR)
pl3, cards3, camk3 = foul_from_behind("booked", SPT, MUN, victim=ALT, fouler=TIE, lag=0.0, lead=3.6, victim_label="Altimira", fouler_label="Tielemans")
camk3.update(camFrom={"pos": [7.2, 1.6, 30.0], "tgt": [1.0, 1.0, 35.5]}, camera={"pos": [6.4, 1.6, 34.0], "tgt": [1.2, 1.0, 38.0]}, move=2.6)
B.append({"kicker": KICK, "headline": "82': own goal. [VAR] says no.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_C, "accent": RED, "lights": 0.85, **camk, "players": pl,
  "card": cards + [mbug([2, 2], "82'"),
                   {"type": "varcheck", "title": "VAR · 82'", "y": 1330, "w": 940, "rowH": 84, "verdictH": 200, "source": "per ESPN match report", "at": "VAR", "lag": -0.1, "clear": False,
                    "steps": [{"text": "Keeper flaps: own goal", "at": "VAR", "lag": 0.1, "kind": "ball"},
                              {"text": "Referee sent to the monitor", "at": "rules", "lag": 0.0, "kind": "var"},
                              {"text": "Judged: Dorgu fouled the keeper", "at": "foul", "lag": 0.0, "kind": "foul"}],
                    "verdict": {"text": "NO GOAL", "sub": "own goal ruled out", "color": RED, "at": "foul", "lag": 0.4, "size": 112}}],
  "shots": [{"at": "Tielemans", "lag": 0.2, "cut": True, "transition": "whip", "headline": "90'+3: Tielemans [sent off].", "scene": S_D, "accent": RED, "lights": 0.8, **camk3, "players": pl3,
             "card": cards3 + [mbug([2, 2], "90'+3", red="away"), {"type": "redcard", "at": "sent off", "lag": -0.2, "label": "90'+3 Tielemans · 2nd yellow", "dx": -200, "y": 1450}]}]})

# 10 the shot timeline: every shot of the match (11 v 7), the red card marker, then Sporting's keeper: 0 saves
B.append({"kicker": "The match in numbers", "headline": "[11] shots to [7].", "cut": True, "transition": "whip", "scene": S_B, "accent": TEAL, "lights": 0.7, "focus": 0.45, "flashes": 8, "hype": False,
  "orbit": {"center": [0, 1.0, 40.0], "r": 40, "from": 70, "to": 20, "h": 26, "h2": 20, "dur": 5.0}, "players": [],
  "card": [{"type": "shotline", "y": 1010, "delay": 0.0, "w": 940, "h": 640, "title": "Every shot · ESPN", "home": {"name": "SPORTING", "color": "#0b8f4b"}, "away": {"name": "UNITED", "color": "#d6283b"},
            "shots": [{"min": s['min'], "side": s['side'], "kind": s['kind'], "who": s['who']} for s in SH], "events": [{"min": 93, "side": "away", "kind": "red", "label": "TIELEMANS"}],
            "total": 96, "ht": 45, "dur": 2.6, "startT": 0.3, "clear": False},
           stamp("0 SAVES", "no saves", sub="Sporting's keeper", color=GOLD, y=1560, size=100, lag=-0.1)]})

# 11 the table: United 17th -> 19th (the climb card, going down), three games left
ZONES = [{"from": 9, "to": 24, "color": "#e9b949"}, {"from": 25, "to": 36, "color": RED}]
COLORS = {"Manchester United": "#d6283b", "Sporting CP": "#0b8f4b", "VfB Stuttgart": "#e30613", "Atlético Madrid": "#cb3524", "Bodo/Glimt": "#f7d117", "LASK Linz": "#cccccc", "FC Porto": "#1b4fb5", "RB Leipzig": "#dd0741",
          "Villarreal": "#f9e000", "Galatasaray": "#f9a01b", "Fenerbahce": "#fcd116", "Bayern Munich": "#dc052d", "Club Brugge": "#1b4fb5", "Internazionale": "#0068a8", "Aston Villa": "#7b003c", "Real Betis": "#00954c",
          "Napoli": "#1e8dd2", "Lille": "#dc2a2a", "Lens": "#f7d117", "Feyenoord Rotterdam": "#e2231a", "PSV Eindhoven": "#e2231a", "AS Roma": "#8e1f2f", "Como": "#1b4fb5", "Viking FK": "#1b4fb5"}
rowsOf = lambda d, lo, hi: [[i + 1, t, d[t]['pts']] for i, t in enumerate(order(d)) if lo <= i + 1 <= hi]
B.append({"kicker": "Champions League table", "headline": "United: [19th]. Three games left.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_A, "accent": RED, "lights": 0.7, "focus": 0.5, "flashes": 8, "hype": False,
  "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "climb", "y": 1110, "delay": 0.0, "w": 900, "rowH": 62, "show": 9, "from": 17, "stepDur": 0.8, "title": "League phase · matchday 5", "focus": MU, "zones": ZONES, "colors": COLORS, "clear": False,
            "steps": [{"rows": rowsOf(kickoff, 17, 25)}, {"at": "point", "lag": -0.1, "rows": rowsOf(tab, 17, 25), "label": "D 2–2 Sporting"}]},
           stamp("3 LEFT", "three games left", sub="8-game league phase", color=RED, y=1630, size=96, lag=-0.1)]})

# 12 Pochettino's second game, still no win (the form strip), Brentford next, and the question (the poll sticker: the real result is the user's to add)
B.append({"kicker": "Pochettino · Man United", "headline": "Were the [officials] fair?", "cut": True, "transition": "whip", "scene": S_C, "accent": GOLD, "lights": 0.7, "focus": 0.4, "flashes": 8, "hype": False,
  "camFrom": {"pos": [0, 1.7, -3.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.7, -2.0], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=kit("#1b2a41", "#1b2a41", "#111111", text="#ffffff"), outfit="suit", tie="#d6283b", suitColor="#1b2a41", skin="#e7b593", hair="#3a2a1a", name="", x=0, z=2.0, front=True)],
  "card": [{"type": "form", "y": 760, "delay": 0.0, "w": 720, "h": 330, "title": "Pochettino · his games in charge", "results": "LD?", "opps": ["LIV · 0–4", "SPORTING · 2–2", "BRENTFORD · SAT"], "step": 0.5, "startT": 0.3,
            "bracket": {"from": 0, "to": 1, "label": "NO WIN YET"}, "bracketAt": "still no win", "bracketLag": 0.0, "clear": False},
           {"type": "poll", "y": 1420, "at": "Were the officials", "lag": -0.2, "question": "Were the officials fair?", "clear": False,
            "options": [{"label": "Fair", "color": GREEN, "fill": 0.001, "pct": "?"}, {"label": "Not fair", "color": RED, "fill": 0.001, "pct": "?"}]}]})

save(V, B, lines, "Sporting 2–2 Man United", accent=TEAL, hookZoom=True, ballScale=1.8)
