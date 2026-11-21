# Builds videos/city-part-3/spec.json (run from the repo root). Man City in League Two, Part 3: League One matchdays 24-46 and the play-offs.
# Every score, position and table comes from videos/city-league-two/data/ep3.json (seed 2028, fixed before running); Watts's and the keepers'
# numbers are real (ESPN, 21 Nov 2026; videos/city-league-two/research.md, episode 3). The sim gives scores only: no scorer is named except Haaland's count.
import json
import sys
sys.path.insert(0, 'engine')
from lib import *

E = json.load(open('videos/city-league-two/data/ep3.json'))
LOG = {g['md']: g for g in E['log']}
assert LOG[25]['score'] == '0-4' and LOG[35]['score'] == '2-0' and LOG[37]['score'] == '3-4' and LOG[42]['score'] == '2-4' and LOG[46]['score'] == '1-1'
assert [LOG[m]['res'] for m in range(26, 31)] == ['W'] * 5 and LOG[30]['pos'] == 5 and LOG[35]['pos'] == 3 and E['pos'] == 4 and E['haaland'] == 29

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
LEI = kit("#003090", "#ffffff", "#003090", text="#fdbe11")
GRI = kit("#111111", "#111111", "#111111", text="#ffffff", stripes=["#111111", "#ffffff"])
STO = kit("#1b4fb5", "#ffffff", "#1b4fb5", text="#ffffff")
OXF = kit("#f7d117", "#0b1f4b", "#0b1f4b", text="#0b1f4b")
CAMU = kit("#f5a12d", "#111111", "#f5a12d", text="#111111")
BRA = kit("#7a1428", "#111111", "#7a1428", text="#f5b301", stripes=["#7a1428", "#f5b301"])
GEN = kit("#c8102e", "#ffffff", "#c8102e")
HAAL = dict(skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, foot="left")
WATTS = dict(kit=CITY, skin="#e7b593", hair="#2a1a10", name="WATTS", num=5)   # the same look as his Part 2 card; the squad number is our story
MCI = {"name": "MCI", "color": SKY}
S_WEM = stadium([SKY, "#ffffff", "#7a1428", "#f5b301"], 41)
S_ETI = stadium([SKY, "#ffffff", SKY, "#1c2c5b"], 6)
S_LEI = stadium(["#003090", "#ffffff", "#003090"], 14)
S_OXF = small(["#f7d117", "#0b1f4b", "#f7d117"], 27)
S_STO = small(["#1b4fb5", "#ffffff", "#1b4fb5"], 33)
S_SIM = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], 21)
COLORS = {"Manchester City": SKY, "Oxford United": "#f7d117", "Sheffield Wednesday": "#2a5caa", "Bradford City": "#7a1428", "Stockport County": "#1b4fb5",
          "Huddersfield Town": "#0e63ad", "Plymouth Argyle": "#0f5c3a", "Reading": "#004494", "Leicester City": "#003090", "Grimsby Town": "#111111"}
ZONES = [{"from": 1, "to": 2, "color": GREEN}, {"from": 3, "to": 6, "color": TEAL}]

def rows(md, n=24):
    return [[r[0], r[1], r[2]] for r in E['snaps'][str(md)][:n]]

V, lines = start('videos/city-part-3/')
B = []

# 1 hook: the play-off final at Wembley. Haaland's shot is already flying on frame 0, beats the keeper... and hits the post. 90 races up.
H = "Man City"
pl, cards, cam = goal(H, -0.6, 40.5, -1, CITY, [-3.55, 1.25, 52.3], 1, GK_GREEN, BRA, lag=-0.5, label="Haaland", **HAAL)
pl[0]["after"] = "idle"   # it hits the post: no celebration
POST = [-3.62, 1.25, 52.25]
cards[1].update(dur=1.25, slowmo=True, flash=False, points=[cards[1]["points"][0], [-2.2, 1.6, 47.5], POST])
cards.append({"type": "ballpath", "world": True, "at": H, "lag": -0.16 + 1.25, "dur": 0.7, "slowmo": False, "flash": False, "points": [POST, [-5.2, 0.9, 49.5], [-6.8, 0.11, 46.5]]})
B.append({"kicker": "Man City in League Two · Part 3", "headline": "City: [90 minutes] from the Championship.", "hookWords": True, "scene": S_WEM, "accent": TEAL,
  "flashes": 14, "hype": False, **cam, "players": pl,
  "card": cards + [bug(MCI, {"name": "BRA", "color": "#7a1428"}, [0, 0], "FINAL"),
                   {"type": "flytext", "text": "OFF THE POST!", "size": 130, "endScale": 0.6, "y": 1330, "at": H, "lag": 1.08, "color": RED, "clear": False},
                   big(90, "ninety minutes", "minutes from the Championship", frm=0, y=1640, size=170, dur=0.9, lag=-0.35, style="accent")],
  "speedlines": [{"t": 0.0, "dur": 0.9, "amount": 0.7}],
  "shake": [{"at": H, "lag": 1.1, "amount": 18}], "punch": [{"at": H, "lag": 1.05, "amount": 0.12, "dur": 1.2}]})

# 2 recap (Part 2 in one line: 12th, leaking goals) then the vote: the poll bars fill, the shirt flips from Cambridge to WATTS
B.append({"kicker": "Season 2 · League One · halfway", "headline": "Twelfth, and [leaking goals].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": RED, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [26, 30, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 16, -24], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [hud("Season 2 · League One", counter=False),
           {"type": "leak", "y": 1160, "at": "leaking goals", "lag": -0.6, "value": 43, "dur": 1.6, "sub": "MAN CITY", "label": "conceded in 23 games", "clear": False},
           big(12, "Twelfth", "after 23 games", frm=6, y=700, size=130, dur=0.6, lag=-0.2, suffix="th", style="accent"),
           {"type": "flytext", "text": "SEASON 2", "size": 190, "delay": 0.0, "settle": False, "y": 1150, "color": TEAL, "clear": False}],
  "shots": [{"at": "So you voted", "lag": -0.15, "cut": True, "transition": "whip", "whipDir": -1, "kicker": "Your vote · the TikTok poll", "headline": "You voted: [Kelland Watts].",
     "scene": S_ETI, "accent": TEAL, "lights": 0.6, "focus": 0.3, "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]},
     "move": 4, "moveEase": "linear", "players": [],
     "card": [{"type": "shirtflip", "y": 860, "delay": 0.0, "size": 400, "from": {"color": "#f5a12d", "color2": "#111111", "name": "CAMBRIDGE"},
               "to": {"color": SKY, "color2": "#1c2c5b", "name": "WATTS"}, "flipAt": "Kelland Watts", "flipLag": -0.35, "clear": False},
              {"type": "poll", "y": 1560, "delay": 0.0, "question": "Who should City sign?", "clear": False,
               "options": [{"label": "Watts", "color": "#f5a12d", "fill": 0.5, "pct": "50%"}, {"label": "Sowunmi", "color": "#9aa1ad", "fill": 0.33, "pct": "33%"},
                           {"label": "Seimen", "color": "#2e2e33", "fill": 0.17, "pct": "17%"}]}]}]})

# 3 who he is: a clean slide tackle (contact on "centre-back"), then his real League One numbers on a drawn card
pl, cards, cam = clean_tackle("centre-back", WATTS, GEN, CITY, label="Watts")
B.append({"kicker": "January signing", "headline": "Watts: [the fans' pick].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": TEAL, **cam, "players": pl,
  "card": cards + [hud("January window · signed", counter=False),
                   {"type": "pcard", "y": 1080, "w": 400, "h": 530, "at": "Fifteen starts", "lag": -0.25, "player": dict(WATTS, kit=CAMU, name="", num=None),
                    "tag": "WATTS · CB · CAMBRIDGE", "caption": "Kelland Watts", "stats": [[15, "starts"], [2, "goals"]], "statsNote": "League One · real stats", "clear": False},
                   stamp("SIGNED", "two goals", sub="your vote · Part 3", color=GREEN, y=1560, size=90, lag=0.2)]})

# 4 match 1: his second game, Leicester away: Leicester score their fourth past City's keeper (Watts the defender closing down), 4-0
pl, cards, cam = goal("four–nil", -1.0, 41, -1, LEI, [2.6, 1.0, 52.3], -1, GK_GREEN, CITY, lag=-0.5, skin="#e7b593", hair="#141010")
pl[2].update(WATTS, label="Watts", labelDelay=0.2)
B.append({"kicker": "Matchday 25 · Leicester away", "headline": "His second game: [0–4].", "cut": True, "transition": "vhs", "vhsLabel": "MD25", "vhsDur": 0.8, "scene": S_LEI, "accent": RED, **cam, "players": pl,
  "card": cards + [bug({"name": "LEI", "color": "#003090"}, MCI, [4, 0], "81'", [3, 0], "four–nil", 0.25), hud("League One · matchday 25", counter=False),
                   stamp("0–4", "Welcome to League One", sub="welcome to League One", y=1530, size=110, lag=-0.05)],
  "shake": [{"at": "four–nil", "lag": 0.4, "amount": 12}]})

# 5 match 2: five wins in a row; the new table-climb card: City's row slides 13th -> 5th, one step per club named
steps = [{"rows": rows(25, 13), "label": "MD25 · L 0–4 Leicester"}]
for md, word in zip(range(26, 31), ["Wycombe", "Doncaster", "Stevenage", "Huddersfield", "Notts County"]):
    g = LOG[md]
    steps.append({"at": word, "lag": -0.15, "rows": rows(md, 13), "label": f"MD{md} · W {g['score'].replace('-', '–')} {word}"})
B.append({"kicker": "Matchdays 26–30", "headline": "Five wins. [Fifth].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": GREEN, "lights": 0.5, "focus": 0.35,
  "camFrom": {"pos": [-30, 34, -50], "tgt": [0, 0, 6]}, "camera": {"pos": [28, 18, -26], "tgt": [0, 0, 6]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "climb", "y": 1150, "delay": 0.0, "title": "League One · 2027/28", "focus": "Manchester City", "show": 13, "steps": steps, "zones": ZONES, "colors": COLORS, "clear": False},
           stamp("5TH", "climb to fifth", sub="from 13th in five games", color=GREEN, y=1760, size=72, lag=-0.1)]})

# 6 match 3: Grimsby at City; Haaland's second; top three for the first time (best in the first half: 6th)
pl, cards, cam = goal("scores twice", -1.2, 41, -1, CITY, [2.8, 1.0, 52.3], -1, GK_YELLOW, GRI, lag=-0.3, label="Haaland", **HAAL)
B.append({"kicker": "Matchday 35 · at home", "headline": "Haaland twice: [top three].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": GOLD, **cam, "players": pl, "flashes": 12,
  "card": cards + [bug(MCI, {"name": "GRI", "color": "#f2f2f2"}, [2, 0], "77'", [1, 0], "scores twice", 0.25), hud("League One · matchday 35", counter=False),
                   stamp("TOP 3", "Top three", sub="for the first time in League One", color=GOLD, y=1530, size=100)]})

# 7 match 4: Stockport win a seven-goal thriller at City, 3-4; seven balls rain into the counter; "remember them" freezes on their celebration
B.append({"kicker": "Matchday 37 · at home", "headline": "Stockport win [4–3].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": RED, "lights": 0.6,
  "camFrom": {"pos": [0.6, 1.6, -4.4], "tgt": [0, 1.2, 10]}, "camera": {"pos": [0.2, 1.55, -2.8], "tgt": [0, 1.2, 10]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=STO, skin="#e7b593", hair="#141010", x=-0.9, z=2.6, front=True, action="celebrate", actionDelay=0.1, label="Stockport", labelDelay=0.2),
              P(kit=CITY, skin="#8a5a3c", hair="#141010", x=1.4, z=4.2, front=True)],
  "card": [bug(MCI, {"name": "STO", "color": "#1b4fb5"}, [3, 4], "FT"), hud("League One · matchday 37", counter=False),
           {"type": "rain", "y": 1400, "delay": 0.0, "cols": 7, "cell": 104, "icon": "ball", "label": "goals in one game", "clear": False,
            "groups": [{"n": 3, "color": SKY, "at": "seven-goal", "lag": -0.3, "dur": 0.6}, {"n": 4, "color": "#1b4fb5", "at": "four–three", "lag": -0.4, "dur": 0.7}]},
           {"type": "pen", "anchor": 0, "delay": 0, "clear": False, "strokes": [{"kind": "ellipse", "layer": "under", "cx": 0, "cy": 0, "rx": 0.55, "ry": 0.13, "at": "Remember them", "lag": -0.15, "dur": 0.45, "color": RED, "width": 9}]}],
  "freezeAt": "Remember them", "freezeLag": -0.05})

# 8 match 5: Oxford, the champions, win 4-2 (trophy and confetti at their place); then Haaland's count locks on 29
B.append({"kicker": "Matchday 42 · Oxford away", "headline": "The champions: [Oxford 4–2].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_OXF, "accent": RED, "lights": 0.85,
  "camFrom": {"pos": [0.8, 1.5, -4.0], "tgt": [0, 1.4, 10]}, "camera": {"pos": [0.3, 1.5, -2.6], "tgt": [0, 1.4, 10]}, "move": 4, "moveEase": "linear", "confetti": True, "confettiAt": "the champions",
  "players": [P(kit=OXF, skin="#f0c8a8", hair="#6a4a2a", x=0, z=3.0, front=True, pose="arms_up", trophy=True, label="Oxford · champions", labelAt="the champions")],
  "card": [bug({"name": "OXF", "color": "#f7d117"}, MCI, [4, 2], "FT"), hud("League One · matchday 42", counter=False)],
  "shots": [{"at": "Haaland still", "lag": -0.2, "cut": True, "transition": "whip", "headline": "Haaland: [29 league goals].", "scene": S_ETI, "accent": GOLD, "lights": 0.8, "flashes": 10,
     "camFrom": {"pos": [0, 1.45, -4.6], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -3.6], "tgt": [0, 1.35, 10]}, "move": 3, "moveEase": "linear",
     "players": [P(kit=CITY, **{k: v for k, v in HAAL.items() if k != "foot"}, x=0, z=0, front=True, chest=True, pose="fists")],
     "card": [big(29, "twenty-nine", "League One goals this season", frm=18, y=1640, size=170, dur=0.9, lag=-0.5)]}]})

# 9 re-hook: the last day. The table before it (City level on 77 with second), then Cambridge, Watts's old club
B.append({"kicker": "Before the last day", "headline": "Last day: [level with second].", "cut": True, "transition": "vhs", "vhsLabel": "LAST DAY", "vhsDur": 1.0, "scene": S_SIM, "accent": GOLD,
  "lights": 0.45, "focus": 0.35, "camFrom": {"pos": [24, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-22, 14, -22], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "climb", "y": 1030, "delay": 0.0, "title": "League One · after matchday 45", "focus": "Manchester City", "show": 6, "zones": ZONES, "colors": COLORS, "clear": False,
            "steps": [{"rows": rows(45, 6), "label": "MD45 · W 1–0 Mansfield"}]},
           stamp("LEVEL ON 77", "level on points", sub="with Sheffield Wednesday, 2nd", color=GOLD, y=1500, size=80)],
  "shots": [{"at": "against Cambridge", "lag": -0.6, "cut": True, "transition": "whip", "headline": "v Cambridge: [his old club].", "scene": S_ETI, "accent": "#f5a12d", "lights": 0.7, "focus": 0,
     "camFrom": {"pos": [0, 1.6, -4.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
     "players": [P(**WATTS, x=-1.0, z=2.6, front=True, label="Watts", labelDelay=0.1), P(kit=CAMU, skin="#f0c8a8", hair="#3a2a1a", x=1.1, z=2.8, front=True, label="Cambridge", labelDelay=0.3)],
     "card": [bug(MCI, {"name": "CAM", "color": "#f5a12d"}, [0, 0], "MD46"), stamp("HIS OLD CLUB", "old club", sub="Cambridge United", color="#f5a12d", y=1660, size=72)]}]})

# 10 1-1; Wednesday win; City drop to 4th, two points off the top two (the climb card steps MD45 -> MD46)
B.append({"kicker": "Matchday 46 · full time", "headline": "1–1. City [finish fourth].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": RED, "lights": 0.4, "focus": 0.35,
  "camFrom": {"pos": [-22, 14, -22], "tgt": [0, 0, 6]}, "camera": {"pos": [-30, 30, -46], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [bug(MCI, {"name": "CAM", "color": "#f5a12d"}, [1, 1], "FT"),
           {"type": "climb", "y": 1060, "delay": 0.0, "title": "League One · final table", "focus": "Manchester City", "show": 6, "zones": ZONES, "colors": COLORS, "clear": False, "labelColor": "#5b6270",
            "steps": [{"rows": rows(45, 6), "label": "before the last day"}, {"at": "Wednesday win", "lag": -0.1, "rows": rows(46, 6), "label": "MD46 · D 1–1 Cambridge"}]},
           stamp("4TH", "finish fourth", sub="two points off going up", y=1560, size=96)]})

# 11 play-offs: Stockport again, 2-0 at home and 2-0 away (split screen), 4-0 on aggregate
B.append({"kicker": "Play-off semi-final", "headline": "Stockport again: [4–0].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": GREEN, "lights": 0.8,
  "camFrom": {"pos": [0, 1.5, -2.8], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.6], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
  "players": [P(kit=CITY, skin="#8a5a3c", hair="#141010", num=10, x=0, z=2.6, front=True, pose="fists")],
  "split": {"scene": S_STO, "at": "Stockport again", "lag": 0.1, "lights": 0.8, "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.5], "tgt": [0, 1.3, 10]},
            "players": [P(kit=CITY, **{k: v for k, v in HAAL.items() if k != "foot"}, x=0, z=2.6, front=True, pose="wings")]},
  "card": [stamp("2–0", "Play-offs", sub="home leg", color=GREEN, y=1380, size=100, lag=0.5, dx=-270),
           stamp("2–0", "Stockport again", sub="away leg", color=GREEN, y=1380, size=100, lag=0.5, dx=270),
           stamp("4–0", "two legs", sub="on aggregate · to Wembley", color=GOLD, y=1700, size=110, lag=-0.2)]})

# 12 Wembley: face-off with Bradford, the league's best defence (30 conceded)
B.append({"kicker": "Play-off final · Wembley", "headline": "Bradford: [the best defence].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_WEM, "accent": "#f5b301", "lights": 0.55, "flashes": 12,
  "camFrom": {"pos": [0, 1.55, -5.0], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.5, -3.4], "tgt": [0, 1.35, 10]}, "move": 4.5, "moveEase": "linear",
  "players": [P(kit=CITY, **{k: v for k, v in HAAL.items() if k != "foot"}, x=-1.05, z=1.0, front=True, chest=True, label="Man City", labelAt="Then Wembley"),
              P(kit=BRA, skin="#e7b593", hair="#1a1210", name="BRADFORD", num=1, x=1.05, z=1.0, front=True, chest=True, label="Bradford City", labelAt="Bradford City",
                tag=30, tagLabel="goals conceded · the fewest", tagAt="the best defence", tagLag=-0.2)]})

# 13 the final: Bradford's second goes in; freeze; City stay in League One
pl, cards, cam = goal("two–nil", 1.2, 41, 1, BRA, [-2.7, 1.0, 52.3], 1, GK_GREEN, CITY, lag=-0.5, skin="#8a5a3c", hair="#141010")
B.append({"kicker": "Play-off final · Wembley", "headline": "Bradford 2–0. [City stay down].", "cut": True, "transition": "whip", "scene": S_WEM, "accent": RED, **cam, "players": pl,
  "card": cards + [bug({"name": "BRA", "color": "#7a1428"}, MCI, [2, 0], "84'", [1, 0], "two–nil", 0.25),
                   stamp("STAYING DOWN", "City stay", sub="League One again next season", y=1640, size=84)],
  "freezeAt": "City stay", "freezeLag": -0.1})

# 14 93 goals, the most in the league: a goal barrage from behind the net; "not enough"; then the summer vote: three real keepers
END = [[-2.6, 1.0, 52.3], [2.4, 1.6, 52.3], [-0.6, 0.5, 52.3], [2.9, 0.7, 52.3]]
barrage = [{"type": "ballpath", "world": True, "delay": round(0.25 + i * 0.7, 2), "dur": 0.45, "slowmo": False, "points": [[x * -0.4, 0.11, 38], [x * 0.2, 1.4, 46], [x, y, z]]}
           for i, (x, y, z) in enumerate(END)]
def keeper(name, tag, kt, sx, word, stats, note):
    return {"type": "pcard", "y": 1000, "w": 300, "h": 400, "shiftX": sx, "side": "left" if sx < 0 else "right", "at": word, "lag": -0.1,
            "player": dict(kit=kt, skin="#e7b593", hair="#2a1a10", name="", gloves="#f2f2f2"), "tag": tag, "caption": name, "stats": stats, "statsNote": note, "clear": False}
HUDK = kit("#0e63ad", "#ffffff", "#0e63ad", stripes=["#0e63ad", "#ffffff"])
VFB = kit("#2e2e33", "#2e2e33", "#2e2e33")
B.append({"kicker": "Season 2 · the verdict", "headline": "93 goals. [Not enough].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": RED, "lights": 0.8,
  "camFrom": {"pos": [1.5, 2.3, 60.5], "tgt": [0, 1.0, 40]}, "camera": {"pos": [0.8, 2.1, 59.2], "tgt": [0, 1.0, 40]}, "move": 3, "moveEase": "linear", "hype": False,
  "players": [P(kit=GK_GREEN, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, pose="keeper")],
  "card": barrage + [big(93, "Ninety-three goals", "league goals · the most in League One", frm=60, y=1560, size=170, dur=1.1, lag=-0.2),
                     stamp("NOT ENOUGH", "Not enough", sub="74 conceded", y=1760, size=80, lag=-0.05)],
  "shots": [{"at": "Who should City", "lag": -0.2, "cut": True, "transition": "whip", "kicker": "Your vote · summer window", "headline": "Summer: [which keeper]?", "scene": S_ETI, "accent": TEAL,
     "lights": 0.6, "focus": 0.3, "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [], "hype": False,
     "card": [keeper("Jon McCracken", "GK · Bradford", BRA, -350, "Who should City", [[9, "clean sheets"], ["1.5", "saves/game"]], "13 starts · League One"),
              keeper("Matt Young", "GK · Huddersfield", HUDK, 0, "sign this summer", [[4, "clean sheets"], ["2.0", "saves/game"]], "15 starts · age 19"),
              keeper("Dennis Seimen", "GK · Stuttgart", VFB, 350, "this summer", [[2, "clean sheets"], ["3.8", "saves/game"]], "5 starts · Bundesliga · 20"),
              {"type": "poll", "y": 1640, "at": "Who should City", "lag": 0.4, "question": "Who should City sign?", "clear": False,
               "options": [{"label": "McCracken", "color": "#7a1428", "fill": 0.34}, {"label": "Young", "color": "#0e63ad", "fill": 0.33}, {"label": "Seimen", "color": "#2e2e33", "fill": 0.33}]}]}]})

save(V, B, lines, "Man City in League Two · Part 3", accent=TEAL)
