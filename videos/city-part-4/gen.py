# Builds videos/city-part-4/spec.json (run from the repo root). Man City in League Two, Part 4: League One 2028/29 (season 3), matchdays 1-23, McCracken in goal.
# Every score, position, table and odds figure comes from videos/city-league-two/data/ep4.json + ep4_extra.json (seed 2029, fixed before running); McCracken's and the
# midfielders' numbers are real (ESPN, 23 Nov 2026; videos/city-league-two/research.md, episode 4). The sim gives scores only: no scorer is named except Haaland's count.
import json
import sys
sys.path.insert(0, 'engine')
from lib import *

D = 'videos/city-league-two/data/'
E = json.load(open(D + 'ep4.json')); X = json.load(open(D + 'ep4_extra.json')); E3 = json.load(open(D + 'ep3.json')); MCK = json.load(open(D + 'mccracken.json'))
LOG = {g['md']: g for g in E['log']}
# --- every number the voice says, checked against the data (a wrong number stops the build)
assert (LOG[1]['opp'], LOG[1]['venue'], LOG[1]['score'], LOG[1]['pos']) == ('Stevenage', 'H', '0-1', 18)
assert (LOG[2]['opp'], LOG[2]['venue'], LOG[2]['score'], LOG[2]['hgoals'], LOG[2]['pos']) == ('Burnley', 'A', '2-1', 2, 13)
assert (LOG[8]['opp'], LOG[8]['venue'], LOG[8]['score']) == ('Luton Town', 'H', '3-4')
assert (LOG[16]['opp'], LOG[16]['venue'], LOG[16]['score']) == ('Stockport County', 'H', '3-1')
assert (LOG[21]['opp'], LOG[21]['venue'], LOG[21]['score']) == ('Derby County', 'H', '9-1')
assert (LOG[19]['opp'], LOG[19]['score']) == ('Preston North End', '4-1')
fell = [LOG[2], LOG[19], LOG[21]]; assert sum(int(g['score'][0]) for g in fell) == 15 and sum(int(g['score'][2]) for g in fell) == 3
p3 = {r[1]: r for r in E3['table_final']}; assert [r[1] for r in E3['table_final'][:4]] == ['Oxford United', 'Sheffield Wednesday', 'Bradford City', 'Manchester City']
LOG3 = {g['md']: g for g in E3['log']}; assert (LOG3[37]['opp'], LOG3[37]['venue'], LOG3[37]['score']) == ('Stockport County', 'H', '3-4')   # last year (Part 3, matchday 37): City 3-4 Stockport
tab = {r[1]: r for r in E['table_md23']}; city = tab['Manchester City']                     # [pos, name, pts, gf, ga]
assert city[0] == 4 and city[2] == 38 and city[3] == 43 and city[4] == 22 and E['table_md23'][0][1:3] == ['MK Dons', 43]
assert all(r[3] - r[4] < 21 for r in E['table_md23'] if r[1] != 'Manchester City') and min(r[4] for r in E['table_md23']) == 22 and E['city_ga_rank'] == 1
assert round(100 * E['pre']['promoted']) == 94 and round(100 * E['pre_without_mccracken']['promoted']) == 86 and round(100 * E['pre']['title']) == 75
assert round(100 * E['half_odds']['promoted']) == 88 and round(X['xpts_23']) == 46 and X['actual_by_md'][-1] == 38 and E['clean_sheets'] == 6 and E['haaland'] == 13
mc = [g for g in MCK if 'Jon McCracken' in g and g['Jon McCracken']['starter']]
assert len(mc) == 13 and sum(1 for g in mc if g['Jon McCracken']['conceded'] == 0) == 9

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
BRA = kit("#7a1428", "#111111", "#7a1428", text="#f5b301", stripes=["#7a1428", "#f5b301"])
STE = kit("#d6283b", "#ffffff", "#d6283b", text="#ffffff")
BUR = kit("#6c1d45", "#ffffff", "#6c1d45", text="#99d6ea")
LUT = kit("#f78f1e", "#0b1f4b", "#f78f1e", text="#0b1f4b")
STO = kit("#1b4fb5", "#ffffff", "#1b4fb5", text="#ffffff")
SHU = kit("#d71920", "#111111", "#d71920", text="#ffffff", stripes=["#d71920", "#ffffff"])
SOU = kit("#d71920", "#ffffff", "#d71920", text="#ffffff", stripes=["#d71920", "#ffffff"])
GEN = kit("#c8102e", "#ffffff", "#c8102e")
HAAL = dict(skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, foot="left")
MCCR = dict(skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2")               # his look is ours (a stylised player); the name and numbers are real
MCI = {"name": "MCI", "color": SKY}
S_WEM = stadium([SKY, "#ffffff", "#7a1428", "#f5b301"], 41)
S_ETI = stadium([SKY, "#ffffff", SKY, "#1c2c5b"], 6)
S_SIM = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], 21)
S_BUR = stadium(["#6c1d45", "#99d6ea", "#6c1d45"], 17)
COLORS = {"Manchester City": SKY, "MK Dons": "#ffffff", "Luton Town": "#f78f1e", "Grimsby Town": "#cfd3da", "Leicester City": "#003090", "Stockport County": "#1b4fb5"}
ZONES = [{"from": 1, "to": 2, "color": GREEN}, {"from": 3, "to": 6, "color": TEAL}]

def rows(md, n=24):
    return [[r[0], r[1], r[2]] for r in E['snaps'][str(md)][:n]]

V, lines = start('videos/city-part-4/')
B = []

# 1 hook: the play-off final at Wembley again. Haaland's shot is already flying on frame 0... and the Bradford keeper holds it. The claim lands on "the keeper".
H = "Man City"
pl, cards, cam = goal(H, -0.6, 42.5, -1, CITY, [-2.0, 1.1, 52.3], -1, GK_GREEN, BRA, lag=-0.5, label="Haaland", save_it=True, **HAAL)
cam.update(camFrom={"pos": [-2.9, 1.9, 35.0], "tgt": [-0.7, 1.0, 52]}, camera={"pos": [-2.3, 1.6, 38.2], "tgt": [-0.7, 1.0, 52]}, move=3.4)   # tighter than goal()'s default: he and the keeper fill the frame
pl[0]["after"] = "idle"
pl[1].update(label="McCracken", labelDelay=0.15)
cards[1].update(dur=1.15, slowmo=True)                           # the save in slow motion: contact at about 1.0s
b = bug({"name": "BRA", "color": "#7a1428"}, MCI, [2, 0], "FINAL"); b.update(at="at Wembley", lag=-0.3)
B.append({"kicker": "Man City in League Two · Part 4", "headline": "City signed the keeper who [beat them at Wembley].", "hookWords": True, "scene": S_WEM, "accent": TEAL,
  "flashes": 14, "hype": False, **cam, "players": pl,
  "card": cards + [b, {"type": "flytext", "text": "DENIED!", "size": 150, "endScale": 0.6, "y": 1330, "at": H, "lag": 1.05, "color": RED, "clear": False},
                   {"type": "pen", "anchor": 1, "delay": 0, "clear": False, "strokes": [{"kind": "ellipse", "layer": "under", "cx": 0, "cy": 0, "rx": 0.55, "ry": 0.13, "at": "the keeper", "lag": -0.1, "dur": 0.45, "color": GOLD, "width": 9}]}],
  "speedlines": [{"t": 0.0, "dur": 0.9, "amount": 0.7}], "punch": [{"at": H, "lag": 0.95, "amount": 0.12, "dur": 1.2}], "shake": [{"at": H, "lag": 1.0, "amount": 12}]})

# 2 recap (season three, 4th last year) then the vote: poll bars fill (43 / 33 / 24, 645 votes) and the shirt flips from Bradford to City
B.append({"kicker": "Season 3 · League One · again", "headline": "Season 3. League One [again].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [26, 30, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 16, -24], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · League One", counter=False),
           {"type": "flytext", "text": "SEASON 3", "size": 190, "endScale": 0.9, "delay": 0.0, "y": 1130, "color": TEAL, "clear": False},
           big(4, "League One again", "last season's finish", frm=4, y=1500, size=150, dur=0.6, lag=-0.1, suffix="th", style="accent")],
  "shots": [{"at": "You voted", "lag": -0.15, "cut": True, "transition": "whip", "whipDir": -1, "kicker": "Your vote · the TikTok poll · 645 votes", "headline": "You voted: [McCracken].",
     "scene": S_ETI, "accent": TEAL, "lights": 0.6, "focus": 0.3, "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]},
     "move": 4, "moveEase": "linear", "players": [],
     "card": [{"type": "shirtflip", "y": 860, "delay": 0.0, "size": 400, "from": {"color": "#7a1428", "color2": "#f5b301", "name": "BRADFORD"},
               "to": {"color": SKY, "color2": "#1c2c5b", "name": "MCCRACKEN"}, "flipAt": "Jon McCracken", "flipLag": -0.35, "clear": False},
              {"type": "poll", "y": 1560, "delay": 0.0, "question": "Who should City sign?", "clear": False,
               "options": [{"label": "McCracken", "color": "#7a1428", "fill": 0.43, "pct": "43%"}, {"label": "Sá", "color": "#fdb913", "fill": 0.33, "pct": "33%"},
                           {"label": "Bazunu", "color": "#1b2a6b", "fill": 0.24, "pct": "24%"}]}]}]})

# 3 who he is: a real save at City's ground (contact on "clean sheets"), and his drawn card with his real numbers
pl, cards, cam = goal("clean sheets", 0.6, 42.5, 1, GEN, [-1.8, 1.0, 52.3], -1, GK_YELLOW, CITY, lag=-0.5, save_it=True, skin="#e7b593", hair="#141010")
cam.update(camFrom={"pos": [2.9, 1.9, 35.0], "tgt": [0.7, 1.0, 52]}, camera={"pos": [2.3, 1.6, 38.2], "tgt": [0.7, 1.0, 52]}, move=3.4)
pl[0]["after"] = "idle"
pl[1].update(label="McCracken", labelDelay=0.2, **{k: v for k, v in MCCR.items() if k != "gloves"})
B.append({"kicker": "The signing", "headline": "McCracken: [the fans' pick].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": TEAL, **cam, "players": pl,
  "card": cards + [hud("Summer window", counter=False),
                   {"type": "pcard", "y": 1300, "w": 330, "h": 450, "shiftX": 290, "side": "right", "at": "Thirteen starts", "lag": -0.25, "player": dict(kit=BRA, **MCCR, name="", num=None),
                    "tag": "GK · BRADFORD", "caption": "Jon McCracken", "stats": [[13, "starts"], [9, "clean sheets"]], "statsNote": "League One · real stats", "clear": False},
                   stamp("SIGNED", "clean sheets", sub="your vote · Part 4", color=GREEN, y=1500, size=84, lag=0.15, dx=-200)]})

# 4 the league got easier: last season's top four as tiles; Oxford, Wednesday and Bradford flip to PROMOTED as they are named, City stay
def badge(c1, c2, t, style="band"): return {"colors": [c1, c2, c1], "text": t, "style": style}
B.append({"kicker": "Season 3 · the new league", "headline": "Three of the top four [went up].", "cut": True, "transition": "whip", "whipDir": -1, "scene": {"type": "stage"}, "accent": GOLD,
  "zoomFrom": 1.0, "zoom": 1.1, "lights": 0.7, "players": [],
  "card": [hud("Season 3 · League One", counter=False),
           {"type": "fates", "y": 1050, "delay": 0.0, "title": "Last season's top four", "clear": False, "items": [
             {"name": "Oxford", "sub": f"{p3['Oxford United'][2]} pts", "badge": badge("#f7d117", "#0b1f4b", "OXF"), "fate": "up", "label": "PROMOTED", "at": "Oxford", "lag": -0.1},
             {"name": "Wednesday", "sub": f"{p3['Sheffield Wednesday'][2]} pts", "badge": badge("#2a5caa", "#ffffff", "SHW", "stripes"), "fate": "up", "label": "PROMOTED", "at": "Wednesday", "lag": -0.1},
             {"name": "Bradford", "sub": f"{p3['Bradford City'][2]} pts", "badge": badge("#7a1428", "#f5b301", "BRA"), "fate": "up", "label": "PROMOTED", "at": "Bradford all", "lag": -0.1},
             {"name": "Man City", "sub": f"{p3['Manchester City'][2]} pts", "badge": badge(SKY, "#1c2c5b", "MCI"), "fate": "second", "label": "STAYED"}]},
           stamp("EASIER", "got easier", sub="three top clubs gone", color=GOLD, y=1570, size=96, lag=-0.1)]})

# 5 the odds: 94 of 100 squares light; on "adds eight" eight of them turn gold: what McCracken adds (86 -> 94)
B.append({"kicker": "10,000 seasons simulated", "headline": "City: [94%] to go up.", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-26, 22, -38], "tgt": [0, 0, 6]}, "camera": {"pos": [24, 14, -22], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · 10,000 runs", dur=1.6),
           {"type": "odds", "y": 1030, "cell": 60, "title": "City · promotion chance", "lit": 94, "litStep": 0.016, "litAt": "ninety-four percent", "litLag": -0.35, "label": "{n}%", "clear": False,
            "extra": {"n": 8, "color": GOLD, "at": "Your keeper adds eight", "lag": 0.0, "label": "McCracken: +8"}}]})

# 6 match 1: day one at home, Stevenage win 1-0. Stevenage's goal beats the keeper; 18th
pl, cards, cam = goal("one–nil", -1.0, 41, -1, STE, [2.6, 1.0, 52.3], -1, GK_YELLOW, CITY, lag=-0.5, skin="#e7b593", hair="#141010")
pl[1].update(skin="#f0c8a8", hair="#3a2a1a")
B.append({"kicker": "Matchday 1 · at home", "headline": "Day one: [0–1] to Stevenage.", "cut": True, "transition": "vhs", "vhsLabel": "MD1", "vhsDur": 0.8, "scene": S_ETI, "accent": RED, **cam, "players": pl,
  "card": cards + [bug(MCI, {"name": "STE", "color": "#d6283b"}, [0, 1], "MD1", [0, 0], "one–nil", 0.25), hud("League One · matchday 1", counter=False),
                   stamp("0–1", "one–nil", sub=f"day one · {LOG[1]['pos']}th", y=1530, size=110, lag=0.05)],
  "shake": [{"at": "one–nil", "lag": 0.4, "amount": 12}]})

# 7 match 2: Burnley away (a club that fell from the Championship): Haaland scores twice, 2-1, first win
pl, cards, cam = goal("scores twice", -1.2, 41, -1, CITY, [2.8, 1.0, 52.3], -1, GK_GREEN, BUR, lag=-0.3, label="Haaland", **HAAL)
pl[0].update(tag=2, tagLabel="goals", tagAt="twice", tagLag=-0.1)
B.append({"kicker": "Matchday 2 · Burnley away", "headline": "Burnley away: Haaland [twice].", "cut": True, "transition": "whip", "scene": S_BUR, "accent": GOLD, **cam, "players": pl, "flashes": 12,
  "card": cards + [bug({"name": "BUR", "color": "#6c1d45"}, MCI, [1, 2], "MD2", [1, 1], "scores twice", 0.5), hud("League One · matchday 2", counter=False),
                   stamp("FIRST WIN", "Two–one", sub=f"13th", color=GREEN, y=1560, size=84, lag=0.1)]})

# 8 match 3: Luton at home, a seven-goal thriller, Luton win 4-3: their winner goes in; seven footballs build a 7
pl, cards, cam = goal("four–three", 1.2, 41, 1, LUT, [-2.7, 1.0, 52.3], 1, GK_YELLOW, CITY, lag=-0.5, skin="#e7b593", hair="#141010")
B.append({"kicker": "Matchday 8 · at home", "headline": "Seven goals. [Luton win 4–3].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": RED, **cam, "players": pl,
  "card": cards + [bug(MCI, {"name": "LUT", "color": "#f78f1e"}, [3, 4], "MD8", [3, 3], "four–three", 0.25), hud("League One · matchday 8", counter=False),
                   {"type": "ballnumber", "text": "7", "size": 380, "y": 1430, "at": "Seven goals", "lag": -0.15, "label": "goals in one game", "clear": False}],
  "shake": [{"at": "four–three", "lag": 0.4, "amount": 12}]})

# 9 match 4: Stockport at home, 3-1: last year's ticket (3-4, LOST) is already there; this year's flies in, stamped REVENGE
B.append({"kicker": "Matchday 16 · at home", "headline": "Stockport again: [revenge]. 3–1.", "cut": True, "transition": "vhs", "vhsLabel": "MD16", "vhsDur": 0.8, "scene": S_ETI, "accent": GREEN, "lights": 0.8,
  "camFrom": {"pos": [0.5, 1.55, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.2, 1.5, -2.2], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=STO, skin="#e7b593", hair="#141010", x=-1.1, z=3.2, front=True, label="Stockport", labelDelay=0.2),
              P(kit=CITY, skin="#8a5a3c", hair="#141010", x=1.2, z=3.4, front=True, action="celebrate", actionAt="Three–one", actionLag=0.0, label="City", labelDelay=0.3)],
  "card": [bug(MCI, {"name": "STO", "color": "#1b4fb5"}, [3, 1], "FT"), hud("League One · matchday 16", counter=False),
           {"type": "tickets", "y": 1380, "dx": 0, "done": 1, "tw": 740, "th": 190, "stampDx": 120, "clear": False, "tickets": [
              {"comp": "Last season · matchday 37", "teams": "City v Stockport", "score": "3–4", "date": "2027/28", "color": "#1b4fb5", "stamp": "LOST", "stampColor": "#d6283b"}]},
           {"type": "tickets", "y": 1595, "dx": 0, "done": 0, "newAt": "Three–one", "newLag": -0.2, "tw": 740, "th": 190, "stampDx": 120, "clear": False, "tickets": [
              {"comp": "This season · matchday 16", "teams": "City v Stockport", "score": "3–1", "date": "2028/29", "color": SKY, "stamp": "WON", "stampColor": "#1f9d55"}]}]})

# 10 match 5: Derby at home, 9-1. A nine-ball barrage from behind the net; then 15 balls rain in (2 + 4 + 9): the goals against the three clubs that fell
END = [[-2.6, 1.0, 52.3], [2.4, 1.6, 52.3], [-0.6, 0.5, 52.3], [2.9, 0.7, 52.3], [-3.0, 1.9, 52.3], [0.8, 1.2, 52.3], [-1.6, 0.6, 52.3], [1.8, 2.0, 52.3], [0.0, 1.0, 52.3]]
barrage = [{"type": "ballpath", "world": True, "delay": round(0.1 + i * 0.2, 2), "dur": 0.4, "slowmo": False, "points": [[x * -0.4, 0.11, 38], [x * 0.2, 1.4, 46], [x, y, z]]}
           for i, (x, y, z) in enumerate(END)]
B.append({"kicker": "Matchday 21 · at home", "headline": "Derby: [9–1].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": TEAL, "lights": 0.85,
  "camFrom": {"pos": [1.5, 2.3, 60.5], "tgt": [0, 1.0, 40]}, "camera": {"pos": [0.8, 2.1, 59.2], "tgt": [0, 1.0, 40]}, "move": 3, "moveEase": "linear", "hype": False,
  "players": [P(kit=GK_GREEN, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, pose="keeper")],
  "card": barrage + [bug(MCI, {"name": "DER", "color": "#cfd3da"}, [9, 1], "MD21", [0, 0], "Nine–one", 0.15), hud("League One · matchday 21", counter=False),
                     big(9, "Then Derby", "goals v Derby", frm=0, y=1560, size=170, dur=1.6, lag=-0.3)],
  "shots": [{"at": "Fifteen goals", "lag": 0.15, "cut": True, "transition": "whip", "kicker": "The three clubs that fell from the Championship", "headline": "15 goals v the clubs that [fell].", "scene": S_SIM, "accent": TEAL,
     "lights": 0.5, "focus": 0.3, "camFrom": {"pos": [24, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-22, 14, -22], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
     "card": [{"type": "rain", "y": 1260, "delay": 0.0, "cols": 5, "cell": 110, "icon": "ball", "label": "goals v Burnley, Preston and Derby", "clear": False,
               "groups": [{"n": 2, "color": SKY, "at": "Fifteen goals", "lag": -0.1, "dur": 0.5}, {"n": 4, "color": SKY, "at": "against the three", "lag": 0.0, "dur": 0.6}, {"n": 9, "color": SKY, "at": "that fell", "lag": -0.2, "dur": 0.9}]},
              hud("League One · matchdays 2, 19, 21", counter=False)]}]})

# 11 re-hook: the model expected 46 points, City have 38. The pace chart draws both lines; the five matches are pinned on City's line
PIN = {1: ("STE", RED), 2: ("BUR", GREEN), 8: ("LUT", RED), 16: ("STO", GREEN), 21: ("DER", GREEN)}
B.append({"kicker": "Halfway · the model v the table", "headline": "Expected 46. [Actual 38].", "cut": True, "transition": "vhs", "vhsLabel": "HALFWAY", "vhsDur": 1.0, "scene": S_SIM, "accent": GOLD,
  "lights": 0.45, "focus": 0.35, "camFrom": {"pos": [-24, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [22, 14, -22], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [hud("League One · after matchday 23", counter=False),
           {"type": "pace", "y": 1090, "at": "The model expected", "lag": -0.25, "startT": 0.3, "dur": 2.6, "title": "City's points after each matchday", "names": {"expected": "model expected", "actual": "actual"},
            "expected": X['xpts_by_md'], "actual": X['actual_by_md'], "pins": [{"i": md - 1, "label": lab, "color": col, **({"dy": -50} if md == 2 else {})} for md, (lab, col) in PIN.items()],
            "gapAt": "thirty-eight", "gapLag": 0.0, "gapLabel": "−8", "clear": False}]})

# 12 the best defence (22 conceded), the best goal difference (+21), only fourth: McCracken close-up, the stacked counter
B.append({"kicker": "Halfway · 23 games", "headline": "The best defence. [And fourth].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": TEAL, "lights": 0.8, "flashes": 10,
  "camFrom": {"pos": [0, 1.45, -4.6], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -3.4], "tgt": [0, 1.35, 10]}, "move": 5.5, "moveEase": "linear",
  "players": [P(kit=GK_YELLOW, name="McCRACKEN", num=1, x=-0.55, z=0, front=True, chest=True, **MCCR)],
  "card": [hud("League One · after matchday 23", counter=False),
           {"type": "stack", "y": 1480, "dx": 250, "size": 140, "clear": False, "items": [
              {"value": 22, "label": "goals conceded · the fewest", "at": "The best defence", "lag": -0.1},
              {"value": 21, "prefix": "+", "label": "goal difference · the best", "at": "The best goal difference", "lag": -0.1, "gold": True},
              {"value": 4, "suffix": "th", "countDur": 0.01, "label": "in the table", "at": "Only fourth", "lag": -0.1, "color": "#ff4d5e"}]}]})

# 13 halfway: the table (MK Dons 43, City 4th on 38), five points off the top, and the odds: still 88%
B.append({"kicker": "Halfway · the table", "headline": "[5 points] off the top.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": GOLD, "lights": 0.45, "focus": 0.35,
  "camFrom": {"pos": [22, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 14, -22], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "climb", "y": 960, "delay": 0.0, "title": "League One · after matchday 23", "focus": "Manchester City", "show": 6, "zones": ZONES, "colors": COLORS, "clear": False,
            "steps": [{"rows": rows(23, 6), "label": f"MD23 · D {LOG[23]['score'].replace('-', '–')} {LOG[23]['opp'].replace(' Town', '')}"}]},
           big(88, "eighty-eight percent", "to go up · halfway odds", frm=57, y=1560, size=170, dur=1.0, lag=-0.5, suffix="%", style="accent"),
           stamp("5 POINTS OFF", "Five points", sub="MK Dons lead on 43", color=GOLD, y=1330, size=72, lag=-0.1)]})

# 14 the January vote: the model's weak spot is midfield (an empty slot pulses on the team sheet); three real midfielders and a poll
SIGN = "#9aa1ad"
XI = [{"name": "Haaland", "x": 0.5, "y": 0.12, "color": SKY}, {"name": "Foden", "x": 0.5, "y": 0.32, "color": SKY},
      {"name": "R. Lewis", "x": 0.86, "y": 0.66, "color": SKY}, {"name": "O'Reilly", "x": 0.14, "y": 0.66, "color": SKY},
      {"name": "McAidoo", "x": 0.82, "y": 0.3, "color": SKY}, {"name": "T. Samba", "x": 0.18, "y": 0.3, "color": SKY},
      {"name": "Iroegbunam", "x": 0.35, "y": 0.5, "color": GOLD}, {"name": "Watts", "x": 0.36, "y": 0.72, "color": GOLD},
      {"name": "Scarr", "x": 0.64, "y": 0.72, "color": SIGN}, {"name": "McCracken", "x": 0.5, "y": 0.9, "color": GOLD}]
def cand(name, tag, kt, sx, word, stats, note, skin, hair):
    return {"type": "pcard", "y": 1000, "w": 290, "h": 400, "shiftX": sx, "side": "left" if sx < 0 else "right", "at": word, "lag": -0.1,
            "player": dict(kit=kt, skin=skin, hair=hair, name=""), "tag": tag, "caption": name, "stats": stats, "statsNote": note, "clear": False}
B.append({"kicker": "The weak spot", "headline": "The weak spot: [midfield].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.35,
  "camFrom": {"pos": [-30, 26, -40], "tgt": [0, 0, 5]}, "camera": {"pos": [24, 20, -34], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "lineup", "y": 1150, "delay": 0.0, "w": 720, "title": "City · the XI", "clear": False, "instant": True, "items": XI,
            "empty": {"x": 0.65, "y": 0.5, "label": "MIDFIELD", "at": "midfield", "lag": -0.15}}, hud("League One · January window", counter=False)],
  "shots": [{"at": "Who should City", "lag": 0.32, "cut": True, "transition": "whip", "kicker": "Your vote · January window", "headline": "January: [which midfielder]?", "scene": S_ETI, "accent": TEAL,
     "lights": 0.6, "focus": 0.3, "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [], "hype": False,
     "card": [cand("Kalvin Phillips", "SHEFFIELD UTD", SHU, -335, "Who should City", [[6, "starts"], ["1+2", "G + A"]], "ex-Man City", "#8a5a3c", "#141010"),
              cand("James Ward-Prowse", "SOUTHAMPTON", SOU, 0, "sign in January", [[12, "starts"], ["1+1", "G + A"]], "Championship", "#f0c8a8", "#4a3324"),
              cand("Oliver Norwood", "STOCKPORT", STO, 335, "in January", [[16, "starts"], ["2+3", "G + A"]], "League One", "#e7b593", "#2a1a10"),
              {"type": "poll", "y": 1640, "at": "Who should City", "lag": 0.4, "question": "Who should City sign?", "clear": False,
               "options": [{"label": "Phillips", "color": "#d71920", "fill": 0.34}, {"label": "Ward-Prowse", "color": "#9a1c24", "fill": 0.33}, {"label": "Norwood", "color": "#1b4fb5", "fill": 0.33}]}]}]})

save(V, B, lines, "Man City in League Two · Part 4", accent=TEAL)
