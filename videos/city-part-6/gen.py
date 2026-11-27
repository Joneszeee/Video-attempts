# Builds videos/city-part-6/spec.json (run from the repo root). Man City in League Two, Part 6: the Championship (season 4), the summer (Bowen and Moylan) and the first five matchdays.
# Every score, position, table and odds figure comes from videos/city-league-two/data/ep6.json (seed 2034, fixed before running); the five matchdays' scorers and the ratings come from squad6.json (seed 2036, fixed before running).
# The poll is the user's screenshot (26 Nov 2026); Bowen's and Moylan's real numbers are ESPN's (p6_real.json, 27 Nov 2026); the Premier League's bottom three are ESPN's real table (27 Nov 2026), used as stand-ins.
# The sim gives scores only: no scorer is named except through Haaland's count and the seed-2036 allocation (squad6.json).
import json
import sys
sys.path.insert(0, 'engine')
from lib import *

D = 'videos/city-league-two/data/'
E6 = json.load(open(D + 'ep6.json')); Q = json.load(open(D + 'squad6.json')); RW = json.load(open(D + 'p6_real.json'))['players']
C6 = json.load(open(D + 'citymodel_c6.json')); P5 = json.load(open(D + 'ep5_promotion.json')); REAL_PL = json.load(open(D + 'real_eng1_table.json'))
L6 = {g['md']: g for g in E6['log']}
# --- every number the voice says, checked against the data (a wrong number stops the build)
POLL = [("Bowen", 54), ("Cozier-Duberry", 41), ("Tanner", 5)]; assert sum(p for _, p in POLL) == 100 and POLL[0][1] == max(p for _, p in POLL); VOTES = 616
assert E6['seed'] == 2034 and E6['mds'] == 5 and Q['seed'] == 2036
assert [r[1] for r in REAL_PL if r[0] >= 18] == ['Sunderland', 'Manchester United', 'Crystal Palace'] and next(r for r in REAL_PL if r[1] == 'Manchester United')[0] == 19
assert C6['came_down'] == ['Sunderland', 'Manchester United', 'Crystal Palace'] and sorted(C6['came_up']) == sorted(P5['promoted']) == sorted(['MK Dons', 'Stockport County', 'Manchester City'])
assert len(C6['stay']) == 18
BW, MY = RW['Jarrod Bowen'], RW['Jack Moylan']
assert (BW['club'], BW['starts'], BW['goals'], BW['assists']) == ('West Ham United', 17, 7, 7) and (MY['club'], MY['starts'], MY['goals'], MY['assists']) == ('Cardiff City', 17, 10, 3)
pre = E6['pre']; pc = lambda k, key='promoted': round(100 * pre[k][key])
assert (pc('neither'), pc('both')) == (32, 55) and pc('both') - pc('neither') == 23                                                          # "fifty-five percent. Your two picks add twenty-three"
ti = lambda club: round(100 * pre['both']['clubs'][club]['title'])
assert (ti('Manchester United'), ti('Sunderland'), ti('Manchester City')) == (86, 6, 5) and ti('Manchester United') == max(ti(c) for c in pre['both']['clubs'])   # "eighty-six percent to win the league. City: five"
assert [(L6[m]['opp'], L6[m]['venue'], L6[m]['score'], L6[m]['pos'], L6[m]['pts']) for m in range(1, 6)] == [('Cardiff City', 'H', '1-0', 8, 3), ('Norwich City', 'A', '2-0', 3, 6), ('Portsmouth', 'A', '1-1', 3, 7),
                                                                                                    ('Southampton', 'H', '1-0', 3, 10), ('Birmingham City', 'H', '2-0', 2, 13)]
assert L6[1]['haaland'] and L6[1]['hgoals'] == 1 and Q['goals'][0] == {'md': 1, 'opp': 'Cardiff City', 'scorer': 'Haaland', 'assist': None}      # "Haaland scores. One-nil." (his is City's only goal)
fin = {r[1]: r for r in E6['table_md5']}; city, utd = fin['Manchester City'], fin['Manchester United']                                         # [pos, name, pts, gf, ga]
assert (city[0], city[2], city[3], city[4]) == (2, 13, 7, 1) and city[4] == min(r[4] for r in E6['table_md5'])                                 # "Thirteen points. One goal conceded" (the fewest)
assert (utd[0], utd[2], utd[3], utd[4]) == (3, 12, 18, 5) and utd[3] == max(r[3] for r in E6['table_md5'])                                     # "United have scored eighteen goals in five games"
def cs(club): return sum(1 for md in range(1, 6) for h, a, x, y in E6['results'][str(md)] if (h == club and y == 0) or (a == club and x == 0))
assert cs('Manchester City') == 4 == E6['clean_sheets'] and cs('Manchester United') == 2
assert Q['stats_five_games']['Bowen'] == dict(apps=5, goals=2, assists=2, cs=0, conceded=0)                                                      # "And Bowen: two goals, two assists"
assert ('Manchester United', 'Manchester City') in [tuple(m) for m in E6['fixtures'][6]] and E6['derby_md'] == 7                                  # "Matchday seven. Man United against Man City" (at Old Trafford)

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
MUN = kit("#d6283b", "#ffffff", "#111111", text="#ffffff")
CAR = kit("#0a4ea1", "#ffffff", "#0a4ea1", text="#ffffff")
WHU = kit("#7a263a", "#ffffff", "#7a263a", text="#1bb1e7")
HAAL = dict(skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, foot="left")
BOWEN = dict(skin="#f0c8a8", hair="#4a3324")
MCI = {"name": "MCI", "color": SKY}
def bd(c1, c2, c3, text, style=None): return {"colors": [c1, c2, c3], "text": text, **({"style": style} if style else {})}      # stylised shields in club colours, never real crests
BAD = {"SUN": bd("#d6283b", "#ffffff", "#111111", "SUN", "stripes"), "MUN": bd("#d6283b", "#111111", "#f7d117", "MUN"), "CRY": bd("#1b458f", "#c4122e", "#ffffff", "CRY", "stripes"),
       "MKD": bd("#1a1a1a", "#ffffff", "#d6283b", "MKD"), "STK": bd("#1b4fb5", "#ffffff", "#ffffff", "STK"), "MCI": bd(SKY, "#1c2c5b", "#ffffff", "MCI")}
S_DERBY = stadium([SKY, "#d6283b", "#ffffff", "#1c2c5b"], 14)
S_ETI = stadium([SKY, "#ffffff", SKY, "#1c2c5b"], 6)
S_NIGHT = stadium(["#ffffff", "#1c2c5b", SKY], 9)
S_SIM = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], 21)
S_CAR = stadium(["#0a4ea1", "#ffffff", "#0a4ea1", "#d6283b"], 33)
S_UTD = stadium(["#d6283b", "#ffffff", "#111111", "#d6283b"], 41)
COLORS = {"Manchester City": SKY, "Manchester United": "#d6283b", "Sunderland": "#d6283b", "West Bromwich Albion": "#1c3f8a", "MK Dons": "#e8e8ea", "Crystal Palace": "#1b458f", "Portsmouth": "#1d4fa8",
          "Stockport County": "#1b4fb5", "Blackburn Rovers": "#2d6cc0", "West Ham United": "#7a263a", "Birmingham City": "#1d4fa8", "Southampton": "#d71920", "Bristol City": "#d6283b"}
ZONES = [{"from": 1, "to": 2, "color": GREEN}, {"from": 3, "to": 6, "color": TEAL}]
GOLDBAR = "#e9b949"

def rows(md, n=8): return [[r[0], r[1], r[2]] for r in E6['snaps'][str(md)][:n]]
def res(md): g = L6[md]; return f"MD{md} · {g['res']} {g['score'].replace('-', '–')} {g['opp'].replace(' City', '')}"

V, lines = start('videos/city-part-6/')
B = []

# 1 hook: "a claim that sounds wrong" (two big clubs, one league). Frame 0: Haaland (City) and a red-shirted United player face to face under the lights, both name pills already up, every headline word readable,
# speed lines and a push-in; on "Man United" (about 1.3 s) a RELEGATED stamp slams across United with a shake (the extraordinary thing before 3 s); the Championship is the headline's accent word.
B.append({"kicker": "Man City in League Two, Part 6 · a football simulation", "headline": "City v United. In the [Championship].", "hookWords": True, "scene": S_DERBY, "accent": TEAL, "lights": 0.85, "flashes": 12, "hype": False,
  "camFrom": {"pos": [0, 1.45, -2.2], "tgt": [0, 1.1, 10]}, "camera": {"pos": [0, 1.45, -1.3], "tgt": [0, 1.1, 10]}, "move": 4.8, "moveEase": "linear",
  "players": [P(kit=CITY, x=-0.62, z=1.0, front=True, chest=True, label="Man City", labelDelay=-0.45, **HAAL),
              P(kit=MUN, skin="#8a5a3c", hair="#141010", name="", num=7, x=0.62, z=1.0, front=True, chest=True, label="Man United", labelDelay=-0.25)],
  "card": [stamp("RELEGATED", "Man United", sub="in our simulation", color=RED, y=1290, size=78, dx=205, lag=-0.1), hud("Season 4 · a football simulation", counter=False)],
  "speedlines": [{"t": 0.0, "dur": 0.9, "amount": 0.7}], "shake": [{"at": "Man United", "lag": -0.1, "amount": 14}]})

# 2 the new league (a NEW card, `divisions`): the real Premier League's bottom three today fall into the Championship (red arrows), City, MK Dons and Stockport rise from League One (green arrows)
B.append({"kicker": "The new league · simulated", "headline": "Three come [down]. Three come [up].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-24, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [22, 14, -22], "tgt": [0, 0, 6]}, "move": 9.5, "moveEase": "linear", "players": [],
  "speedlines": [{"at": "bottom three", "lag": -0.4, "dur": 1.2, "amount": 0.5}], "punch": [{"at": "In our simulation", "lag": 0.5, "amount": 0.10, "dur": 1.4}, {"at": "bottom three", "lag": -0.3, "amount": 0.14, "dur": 1.5}],
  "shake": [{"at": "bottom three", "lag": 0.0, "amount": 8}],
  "card": [hud("Season 4 · simulated", counter=False),
           {"type": "divisions", "y": 1010, "w": 940, "delay": 0.0, "tiers": ["PREMIER LEAGUE · BOTTOM 3 NOW", "CHAMPIONSHIP", "LEAGUE ONE"], "focus": 1, "note": "+ 18 clubs stay", "cols": 6, "clear": False,
            "moves": [{"name": "Sunderland", "badge": BAD["SUN"], "from": 0, "to": 1, "col": 0, "at": "Sunderland", "lag": -0.15},
                      {"name": "Man United", "badge": BAD["MUN"], "from": 0, "to": 1, "col": 1, "at": "Man United", "lag": -0.15},
                      {"name": "Crystal Palace", "badge": BAD["CRY"], "from": 0, "to": 1, "col": 2, "at": "Crystal Palace", "lag": -0.15},
                      {"name": "Man City", "badge": BAD["MCI"], "from": 2, "to": 1, "col": 3, "at": "City,", "lag": -0.15},
                      {"name": "MK Dons", "badge": BAD["MKD"], "from": 2, "to": 1, "col": 4, "at": "MK Dons", "lag": -0.15},
                      {"name": "Stockport", "badge": BAD["STK"], "from": 2, "to": 1, "col": 5, "at": "Stockport", "lag": -0.15}]},
           stamp("19TH", "Man United", sub="in the real Premier League table today", color=RED, y=1560, size=96, lag=0.1, hideAt="Up from", hideLag=-0.1),
           stamp("PROMOTED", "City,", sub="City · MK Dons · Stockport", color=GREEN, y=1560, size=96, lag=-0.3)]})

# 3 the vote: the poll bars fill (54 / 41 / 5, 616 votes) and Bowen's drawn card (real West Ham numbers) slides in on his name
B.append({"kicker": f"Your vote · the TikTok poll · {VOTES} votes", "headline": "You voted: [Bowen].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [26, 30, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 16, -24], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [hud("Season 4 · the summer", counter=False),
           {"type": "pcard", "y": 860, "w": 300, "h": 420, "shiftX": 0, "side": "left", "at": "Jarrod Bowen", "lag": -0.2, "player": dict(kit=WHU, name="", num=None, **BOWEN),
            "tag": "WEST HAM", "caption": "Jarrod Bowen", "stats": [[int(BW['goals']), "goals"], [int(BW['assists']), "assists"]], "statsNote": f"{int(BW['starts'])} starts · Championship · real stats", "clear": False},
           {"type": "poll", "y": 1450, "at": "Fifty-four", "lag": -0.9, "question": "Who should we sign next?", "clear": False,
            "options": [{"label": "Bowen", "color": "#7a263a", "fill": 0.54, "pct": "54%"}, {"label": "Cozier-Duberry", "color": "#e2231a", "fill": 0.41, "pct": "41%"}, {"label": "Tanner", "color": "#0a4ea1", "fill": 0.05, "pct": "5%"}]}]})

# 4 Moylan stays: the shirt flips Cardiff -> City on "he stays", PERMANENT slams
B.append({"kicker": "The comment vote · keep him", "headline": "Moylan [stays].", "cut": True, "transition": "whip", "scene": S_CAR, "accent": TEAL, "lights": 0.7, "focus": 0.35, "flashes": 8,
  "camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.8, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 4.2, "moveEase": "linear", "players": [],
  "card": [hud("Season 4 · the summer", counter=False),
           {"type": "shirtflip", "y": 820, "delay": 0.0, "size": 420, "from": {"color": "#0a4ea1", "color2": "#ffffff", "name": "CARDIFF"}, "to": {"color": SKY, "color2": "#1c2c5b", "name": "MOYLAN"},
            "flipAt": "So he stays", "flipLag": -0.15, "clear": False},
           stamp("PERMANENT", "a permanent deal", sub="no more loan · left wing", color=GOLD, y=1500, size=96, lag=-0.35)]})

# 5 the odds: 55 of 100 squares light; on "add twenty-three" the last 23 turn gold (what the two picks add: 32 -> 55)
B.append({"kicker": "10,000 seasons simulated · pre-season", "headline": "Promotion: [55%].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-26, 22, -38], "tgt": [0, 0, 6]}, "camera": {"pos": [24, 14, -22], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [hud("Season 4 · 10,000 runs", dur=1.6),
           {"type": "odds", "y": 1030, "cell": 60, "title": "City · chance of promotion", "lit": pc('both'), "litStep": 0.016, "litAt": "fifty-five percent", "litLag": -0.35, "label": "{n}%", "clear": False,
            "extra": {"n": pc('both') - pc('neither'), "color": GOLD, "at": "Your two picks add", "lag": 0.0, "label": "your two picks: +23"}}]})

# 6 re-hook (a pattern break: VHS tear, a giant UNITED flies across): the favourites. Title odds before a ball is kicked: United 86, Sunderland 6, City 5
B.append({"kicker": "The title race · pre-season", "headline": "But the favourites are [United].", "cut": True, "transition": "vhs", "vhsLabel": "BUT", "vhsDur": 1.0, "scene": S_UTD, "accent": RED, "lights": 0.55, "focus": 0.35,
  "camFrom": {"pos": [-4.0, 2.4, 20.0], "tgt": [0, 1.2, 40]}, "camera": {"pos": [5.0, 3.0, 22.0], "tgt": [0, 1.2, 40]}, "move": 6, "moveEase": "linear", "players": [], "hype": False,
  "card": [hud("Season 4 · 10,000 runs", counter=False),
           {"type": "flytext", "text": "UNITED", "size": 300, "endScale": 0.42, "y": 640, "at": "Man United", "lag": -0.35, "color": "#ff4d5e", "clear": False},
           {"type": "bars", "y": 1180, "label": "chance to win the league", "at": "eighty-six", "lag": -1.2, "max": 100, "clear": False,
            "rows": [{"name": "United", "value": ti('Manchester United'), "suffix": "%", "color": "#d6283b"}, {"name": "Sunderland", "value": ti('Sunderland'), "suffix": "%", "color": "#9aa1ad"},
                     {"name": "City", "value": ti('Manchester City'), "suffix": "%", "color": SKY}]}]})

# 7 match 1 (matchday 1, home): Cardiff, Moylan's old club. Haaland dribbles at goal, hops the slide, finishes low past the wrong-way keeper (the sim's only City goal, and it is his)
pl, cards, cam, _ = goal_dribble("scores", CITY, GK_GREEN, CAR, mate_kit=CITY, foot="left", label="Haaland", cut=False, scorer=dict(name="HAALAND", num=9, skin=HAAL["skin"], hair=HAAL["hair"]))
B.append({"kicker": "Matchday 1 · at home", "headline": "Day one: [1–0] v Cardiff.", "cut": True, "transition": "whip", "scene": S_ETI, "accent": TEAL, **cam, "players": pl,
  "card": cards + [bug(MCI, {"name": "CAR", "color": "#0a4ea1"}, [1, 0], "MD1", [0, 0], "scores", 0.25), hud("Championship · matchday 1", counter=False),
                   stamp("OLD CLUB", "Moylan's old club", sub="Cardiff City", color="#4aa3ff", y=1520, size=84, lag=-0.1, hideAt="Haaland scores", hideLag=-0.3),
                   stamp("1–0", "One–nil", sub="Haaland · day one", color=GREEN, y=1520, size=110, lag=-0.1)]})

# 8 matchdays 2-5: the table climb. Each result pops on its word and City's row slides 8th -> 3rd -> 3rd -> 3rd -> 2nd (United are on top for three of the five weeks)
B.append({"kicker": "Matchdays 2–5", "headline": "Then four more. City climb to [second].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_NIGHT, "accent": GOLD, "lights": 0.8, "fans": True, "flashes": 10,
  "camFrom": {"pos": [9.0, 1.6, 22.0], "tgt": [0, 1.2, 40]}, "camera": {"pos": [-7.0, 2.2, 24.0], "tgt": [0, 1.2, 40]}, "move": 6.5, "moveEase": "linear", "hype": False, "players": [],
  "card": [{"type": "climb", "y": 1110, "w": 900, "rowH": 70, "delay": 0.0, "show": 8, "stepDur": 0.8, "title": "Championship · the top eight", "focus": "Manchester City", "zones": ZONES, "colors": COLORS, "clear": False,
            "steps": [{"rows": rows(1), "label": res(1)}, {"at": "Norwich", "lag": -0.1, "rows": rows(2), "label": res(2)}, {"at": "Portsmouth", "lag": -0.1, "rows": rows(3), "label": res(3)},
                      {"at": "Southampton", "lag": -0.1, "rows": rows(4), "label": res(4)}, {"at": "Birmingham", "lag": -0.1, "rows": rows(5), "label": res(5)}]},
           hud("Championship · matchdays 1–5", counter=False)]})

# 9 the numbers: Bowen in City's shirt on the left (he walks into frame on his name), the stacked counter on the right: 13 points, 1 against (the fewest), his 2 goals and 2 assists (seed 2036)
B.append({"kicker": "After five games · simulated", "headline": "Five games: [13 points].", "cut": True, "transition": "whip", "scene": S_NIGHT, "accent": GOLD, "lights": 0.8, "flashes": 10,
  "camFrom": {"pos": [0, 1.45, -4.6], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -3.4], "tgt": [0, 1.35, 10]}, "move": 5.0, "moveEase": "linear",
  "players": [P(kit=CITY, x=-0.55, z=0, front=True, chest=True, name="BOWEN", num=20, label="Bowen", at="And Bowen", lag=-0.3, enter="fade", **BOWEN)],
  "card": [hud("Championship · after matchday 5", counter=False),
           {"type": "stack", "y": 1480, "dx": 250, "size": 130, "clear": False, "items": [
              {"value": city[2], "label": "points", "at": "Thirteen points", "lag": -0.1},
              {"value": city[4], "label": "against · the fewest", "at": "One goal conceded", "lag": -0.1},
              {"value": 2, "label": "Bowen · sim goals", "at": "two goals", "lag": -0.2},
              {"value": 2, "label": "Bowen · sim assists", "at": "two assists", "lag": -0.25, "gold": True}]}]})

# 10 the cliffhanger: City v United after five games (the tale of the tape: points 13 v 12, goals 7 v 18, clean sheets 4 v 2); the two players face each other under the Old Trafford lights
B.append({"kicker": "Next: Old Trafford", "headline": "United: [18 goals] in five.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_UTD, "accent": RED, "lights": 0.7, "flashes": 12,
  "camFrom": {"pos": [0, 2.2, -3.8], "tgt": [0, -2.4, 10]}, "camera": {"pos": [0, 2.2, -3.4], "tgt": [0, -2.4, 10]}, "move": 5.0, "moveEase": "linear", "hype": False,
  "players": [P(kit=CITY, x=-0.62, z=1.0, front=True, chest=True, label="Man City", labelDelay=0.1, **HAAL),
              P(kit=MUN, skin="#8a5a3c", hair="#141010", name="", num=7, x=0.62, z=1.0, front=True, chest=True, label="Man United", labelDelay=0.2)],
  "card": [hud("Championship · after matchday 5", counter=False),
           {"type": "tape", "y": 1450, "w": 900, "rowH": 118, "left": {"name": "MAN CITY", "color": SKY}, "right": {"name": "MAN UNITED", "color": "#d6283b"}, "clear": False,
            "rows": [{"label": "points", "left": city[2], "right": utd[2], "at": "Old Trafford", "lag": -0.1},
                     {"label": "goals scored", "left": city[3], "right": utd[3], "at": "eighteen goals", "lag": -0.2},
                     {"label": "clean sheets", "left": cs('Manchester City'), "right": cs('Manchester United'), "at": "in five games", "lag": 0.1}]}]})

# 11 the question: matchday seven, United v City, with the poll (results left empty: the real poll is the user's)
B.append({"kicker": "Matchday 7 · Old Trafford", "headline": "United v City. Who [wins]?", "cut": True, "transition": "whip", "scene": S_UTD, "accent": GOLD, "lights": 0.6, "flashes": 14,
  "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 0.6, 10]}, "camera": {"pos": [0, 1.5, -1.7], "tgt": [0, 0.6, 10]}, "move": 4.6, "moveEase": "linear", "hype": False,
  "players": [P(kit=CITY, x=-0.62, z=1.0, front=True, chest=True, **HAAL), P(kit=MUN, skin="#8a5a3c", hair="#141010", name="", num=7, x=0.62, z=1.0, front=True, chest=True)],
  "card": [stamp("MD 7", "Matchday seven", sub="Man United v Man City · Old Trafford", color=GOLD, y=690, size=100, lag=-0.1),
           {"type": "poll", "y": 1560, "at": "Who wins", "lag": -0.6, "question": "Who wins the derby?", "clear": False,
            "options": [{"label": "City", "color": SKY, "fill": 0.34}, {"label": "Draw", "color": "#9aa1ad", "fill": 0.33}, {"label": "United", "color": "#d6283b", "fill": 0.33}]}]})

save(V, B, lines, "Man City in League Two · Part 6", accent=TEAL)
