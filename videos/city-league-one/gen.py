# Builds videos/city-league-one/spec.json (run from the repo root). Man City in League Two, episode 2: League One, matchdays 1-23.
# Every number comes from videos/city-league-two/research.md (episode 2 section) and data/ep2.json (seed 2027, with the user's Barnet/Wimbledon swap).
import json
RED, GOLD, GREEN, TEAL, SKY = "#ff4d5e", "#e9b949", "#2ecc71", "#3FE0C5", "#6cabdd"
CITY = {"shirt": SKY, "shorts": "#ffffff", "socks": SKY, "text": "#1c2c5b"}
WIG = {"shirt": "#1d4fb8", "shorts": "#ffffff", "socks": "#1d4fb8", "text": "#ffffff", "stripes": ["#1d4fb8", "#ffffff"]}
LEI = {"shirt": "#003090", "shorts": "#ffffff", "socks": "#003090", "text": "#fdbe11"}
HUD = {"shirt": "#0e63ad", "shorts": "#ffffff", "socks": "#0e63ad", "text": "#ffffff", "stripes": ["#0e63ad", "#ffffff"]}
BAR = {"shirt": "#f08a1d", "shorts": "#111111", "socks": "#f08a1d", "text": "#111111"}
WIM = {"shirt": "#1f3f8f", "shorts": "#1f3f8f", "socks": "#f7d117", "text": "#f7d117"}
GK = {"shirt": "#f7d117", "shorts": "#111111", "socks": "#f7d117", "text": "#111111"}
GKC = {"shirt": "#2ecc71", "shorts": "#111111", "socks": "#2ecc71", "text": "#111111"}
def small(crowd, seed): return {"type": "stadium", "ground": "small", "crowd": crowd, "seed": seed}
S_ETI = {"type": "stadium", "crowd": [SKY, "#ffffff", SKY, "#1c2c5b"], "seed": 6}
S_WIG = small(["#1d4fb8", "#ffffff", "#1d4fb8"], 22)
S_GRI = small(["#111111", "#ffffff", "#111111"], 18)
S_SIM = {"type": "stadium", "crowd": ["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], "seed": 21}
V = 'videos/city-league-one/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
HAAL = dict(kit=CITY, skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9)
FODEN = dict(kit=CITY, skin="#f0c8a8", hair="#3a2a1a", name="FODEN", num=47)
IRO = dict(kit=CITY, skin="#8a5a3c", hair="#141010", name="IROEGBUNAM")
CBADGE = {"colors": [SKY, "#1c2c5b", "#ffffff"], "text": "MCFC"}
MCI = {"name": "MCI", "color": SKY}
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
def hud(sub, **k):
    d = {"type": "simhud", "delay": 0, "sub": sub, "dur": 0, "clear": False}; d.update(k); return d
def bug(home, away, score, mn, frm=None, goalAt=None, lag=0.3, **k):
    d = {"type": "scorebug", "y": 560, "delay": 0, "home": home, "away": away, "score": score, "min": mn, "clear": False}
    if frm: d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    d.update(k); return d
def goal(word, x, z, side, kit, end, gdir, gkit, dkit, lag=-0.5, label=None, **pk):
    """Shooter in frame for the whole run-up; one defender blocking, one covering; keeper beaten."""
    b0 = [x + 0.22, 0.11, z + 0.45]
    sh = P(kit=kit, x=x, z=z, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate", runup=1.6, **pk)
    if label: sh.update(label=label, labelDelay=0.1)
    pl = [sh, P(kit=gkit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=gdir, actionAt=word, actionLag=lag + 0.45),
          P(kit=dkit, skin="#e7b593", hair="#141010", x=x + side * -1.9, z=z + 3.4, front=True, action="dive", dir=side, actionAt=word, actionLag=lag + 0.15, actionDur=0.7),
          P(kit=dkit, skin="#8a5a3c", hair="#141010", x=-end[0] * 0.8, z=47.8, front=True)]
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34},
             {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": 0.5, "slowmo": False, "points": [b0, mid(b0, end, 0.9), end]}]
    cam = {"camFrom": {"pos": [round(x + side * 3.0, 2), 2.2, z - 9], "tgt": [round(x * 0.4, 2), 1.0, 52]}, "camera": {"pos": [round(x + side * 2.4, 2), 1.9, z - 6.3], "tgt": [round(x * 0.4, 2), 1.0, 52]}, "move": 4, "moveEase": "linear", "follow": 0.5}
    return pl, cards, cam
B = []

# 1 hook: the voters' comments float up, the shirt spins from Hull to City and lands on IROEGBUNAM, SIGNED slams
B.append({"kicker": "Man City in League Two · Episode 2", "headline": "You picked him: [Iroegbunam signed].", "hookWords": True, "scene": S_ETI, "accent": TEAL, "lights": 0.7, "flashes": 10, "focus": 0.2,
  "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.4], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [{"type": "comments", "y": 1500, "delay": -0.6, "step": 0.35, "clear": False, "items": [
              {"text": "lvp_davie: Iroegbunam or Fellows · 4 likes", "x": -40, "y": 1560, "color": "#7a7f8c", "t": 0},
              {"text": "theo6k: Pick ONE. Which is it?", "x": 30, "y": 1680, "color": "#1d4fb8", "t": 0.3},
              {"text": "lvp_davie: Iroegbunam", "x": -80, "y": 1800, "color": "#7a7f8c", "t": 0.6}]},
           {"type": "shirtflip", "y": 900, "delay": -0.2, "size": 470, "from": {"color": "#f5a12d", "color2": "#111111", "name": "HULL CITY"}, "to": {"color": SKY, "color2": "#1c2c5b", "name": "IROEGBUNAM"}, "flipAt": "City signed him", "flipLag": -0.25, "clear": False},
           {"type": "stamp", "text": "SIGNED", "sub": "your vote · episode 2", "at": "Tim Iroegbunam", "lag": -0.1, "color": GREEN, "rot": -0.07, "size": 110, "y": 610}],
  "shake": [{"at": "Tim Iroegbunam", "lag": 0.0, "amount": 14}]})

# 2 who he is: a ball-winning tackle, then his road from Aston Villa to Everton to Hull to City, U19 European champion
B.append({"kicker": "The new signing", "headline": "A midfielder who [wins it back].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": TEAL, "hype": False,
  "camFrom": {"pos": [-4.2, 1.5, 1.6], "tgt": [0.6, 0.9, 6]}, "camera": {"pos": [-3.4, 1.4, 2.6], "tgt": [0.6, 0.9, 6]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=WIG, skin="#e7b593", hair="#141010", x=1.8, z=6.2, path=[[3.5, 4.2], [0.6, 6.2]], pathDur=1.6, dribble=True, action="fall", actionAt="wins the ball back", actionLag=0.1),
              P(**IRO, x=-1.2, z=5.6, path=[[-1.6, 4.4], [0.0, 6.0]], pathDur=1.4, action="slide", dir=-1, actionAt="wins the ball back", actionLag=-0.4, label="Iroegbunam", labelDelay=0.1)],
  "card": [{"type": "flytext", "text": "BALL-WINNER", "size": 170, "endScale": 0.6, "y": 1500, "at": "wins the ball back", "lag": 0.2, "color": TEAL, "clear": False}],
  "shots": [{"at": "Ex-Aston Villa", "lag": -0.15, "cut": True, "transition": "whip", "whipDir": -1, "headline": "Villa. Everton. Hull. [City].", "scene": S_ETI, "lights": 0.55, "focus": 0.35,
     "camFrom": {"pos": [20, 22, -34], "tgt": [0, 0, 6]}, "camera": {"pos": [-16, 18, -28], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
     "card": [{"type": "career", "y": 1080, "delay": 0.0, "title": "Tim Iroegbunam · 23 · midfielder", "clear": False,
               "items": [{"name": "Aston Villa", "sub": "academy", "color": "#670e36", "result": "DEBUT", "good": True, "at": "Ex-Aston Villa", "lag": -0.1},
                         {"name": "Everton", "sub": "Premier League", "color": "#003399", "result": "PL", "good": True, "at": "and Everton"},
                         {"name": "Hull City", "sub": "2026", "color": "#f5a12d", "result": "PL", "good": True, "at": "now at Hull"},
                         {"name": "Man City", "sub": "League One", "color": SKY, "result": "SIGNED", "good": True, "at": "European champion", "lag": 0.3}]},
              {"type": "stamp", "text": "U19 EURO CHAMPION", "sub": "England · 2022", "at": "European champion", "lag": -0.1, "color": GOLD, "rot": -0.06, "size": 64, "y": 1740}]}]})

# 3 the team: he replaces Fapetu next to Braybrooke; the stars stay; the kids a year better
SIGN = "#9aa1ad"
XI = [{"name": "Haaland", "x": 0.5, "y": 0.12, "color": SKY}, {"name": "Foden", "x": 0.5, "y": 0.32, "color": SKY},
      {"name": "R. Lewis", "x": 0.86, "y": 0.66, "color": SKY}, {"name": "O'Reilly", "x": 0.14, "y": 0.66, "color": SKY},
      {"name": "McAidoo", "x": 0.82, "y": 0.3, "color": SKY}, {"name": "T. Samba", "x": 0.18, "y": 0.3, "color": SKY},
      {"name": "Braybrooke", "x": 0.65, "y": 0.5, "color": SIGN}, {"name": "Fitzwater", "x": 0.36, "y": 0.72, "color": SIGN},
      {"name": "Scarr", "x": 0.64, "y": 0.72, "color": SIGN}, {"name": "Hudson", "x": 0.5, "y": 0.9, "color": SIGN},
      {"name": "Iroegbunam", "x": 0.35, "y": 0.5, "color": GOLD, "at": "next to Braybrooke", "lag": -0.2}]
B.append({"kicker": "The League One XI", "headline": "Straight in. [Fapetu benched].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": GOLD, "lights": 0.55, "focus": 0.35,
  "camFrom": {"pos": [-30, 26, -40], "tgt": [0, 0, 5]}, "camera": {"pos": [24, 20, -34], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "lineup", "y": 1150, "delay": 0.0, "w": 720, "title": "City · League One XI", "clear": False, "items": XI},
           {"type": "stamp", "text": "BENCHED", "sub": "Oluwafemi Fapetu", "at": "Fapetu drops", "lag": 0.0, "color": RED, "rot": -0.07, "size": 70, "y": 1700}],
  "shots": [{"at": "Haaland, Foden", "lag": -0.2, "cut": True, "transition": "whip", "headline": "The stars stay. [Kids +1 year].", "scene": S_ETI, "lights": 0.85,
     "camFrom": {"pos": [0, 1.5, -3.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.8], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear",
     "players": [P(**HAAL, x=0, z=3.6, front=True, pose="fists", label="Haaland", labelAt="Haaland"),
                 P(**FODEN, x=-1.4, z=4.4, front=True, label="Foden", labelAt="Foden"),
                 P(kit=CITY, skin="#8a5a3c", hair="#141010", num=82, x=1.5, z=4.4, front=True, label="Lewis", labelAt="Lewis"),
                 P(kit=CITY, skin="#f0c8a8", hair="#6a4a2a", num=33, x=2.9, z=5.6, front=True, label="O'Reilly", labelAt="O'Reilly")],
     "card": [{"type": "flytext", "text": "+1 YEAR", "size": 200, "endScale": 0.65, "y": 1560, "at": "a year better", "lag": -0.2, "color": TEAL, "clear": False}]}]})

# 4 opening day: the Wigan win as a score bug, then Leicester win 4-3 at City (one shot, so no cut under 2 s)
B.append({"kicker": "League One · Matchdays 1–2", "headline": "Then [Leicester win 4–3].", "cut": True, "transition": "vhs", "vhsLabel": "PLAY", "vhsDur": 0.9, "scene": S_ETI, "accent": RED,
  "camFrom": {"pos": [7.5, 2.5, 35.5], "tgt": [-0.5, 1.2, 50]}, "camera": {"pos": [6.5, 2.3, 38.5], "tgt": [-0.5, 1.2, 50]}, "move": 5, "moveEase": "linear", "follow": 0.3,
  "players": [P(kit=LEI, skin="#e7b593", hair="#141010", x=-1.0, z=41, action="kick", actionAt="four–three", actionLag=-0.9, actionDur=0.8, after="celebrate", runup=1.4),
              P(kit=GKC, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="four–three", actionLag=-0.45),
              P(kit=CITY, skin="#8a5a3c", hair="#141010", x=-2.9, z=44.4, front=True, action="dive", dir=-1, actionAt="four–three", actionLag=-0.75, actionDur=0.7)],
  "card": [{"type": "ball", "delay": 0, "point": [-0.78, 0.11, 41.45], "untilAt": "four–three", "untilLag": -0.56},
           {"type": "ballpath", "world": True, "at": "four–three", "lag": -0.56, "dur": 0.5, "slowmo": False, "points": [[-0.78, 0.11, 41.45], [0.9, 0.9, 47], [2.8, 0.9, 52.3]]},
           bug({"name": "WIG", "color": "#1d4fb8"}, MCI, [1, 2], "90'", [1, 1], "win at Wigan", -0.2, hideAt="Then Leicester", hideLag=-0.1),
           dict(bug(MCI, {"name": "LEI", "color": "#003090"}, [3, 4], "89'", [3, 3], "four–three", -0.5), at="Then Leicester", lag=-0.1),
           hud("Season 2 · League One", y=1720)]})

# 5 matchday 6: Huddersfield win 4-0 at City; the City shield sinks one notch per goal; 17th
B.append({"kicker": "Matchday 6 · at home", "headline": "Huddersfield: [4–0]. City 17th.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": RED, "lights": 0.45, "focus": 0.3,
  "camFrom": {"pos": [14, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [-14, 9, -18], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [bug(MCI, {"name": "HUD", "color": "#0e63ad"}, [0, 4], "90'", None, None, y=600),
           {"type": "sinking", "y": 1180, "delay": 0.0, "badge": CBADGE, "label": "City · goals conceded", "w": 460, "h": 480, "badgeH": 200, "clear": False,
            "steps": [{"at": "Huddersfield", "lag": -0.2}, {"at": "Huddersfield", "lag": 0.3}, {"at": "win four–nil", "lag": -0.2}, {"at": "win four–nil", "lag": 0.3}]},
           {"type": "big", "at": "seventeenth", "lag": -0.4, "from": 6, "value": 17, "countDur": 0.5, "suffix": "th", "label": "in League One", "y": 1640, "size": 140, "style": "accent", "clear": False}]})

# 6 a win at Grimsby, then Haaland's hat-trick against Barnet, 5-0
pl, cards, cam = goal("hat-trick", -1.2, 41, -1, CITY, [2.8, 1.0, 52.3], -1, GK, BAR, lag=-0.3, label="Haaland", **{k: v for k, v in HAAL.items() if k != "kit"})
pl[0]["after"] = "celebrate"
B.append({"kicker": "Matchdays 12–13", "headline": "Haaland hat-trick: [5–0] Barnet.", "cut": True, "transition": "whip", "scene": S_ETI, "accent": GOLD, **cam, "players": pl, "flashes": 12,
  "card": cards + [bug({"name": "GRI", "color": "#f2f2f2"}, MCI, [1, 2], "FT", None, None, y=560, hideAt="hat-trick", hideLag=-0.6),
                   dict(bug(MCI, {"name": "BAR", "color": "#f08a1d"}, [5, 0], "84'", [4, 0], "hat-trick", 0.25, y=560), at="hat-trick", lag=-0.6),
                   {"type": "big", "y": 1600, "at": "hat-trick", "lag": 0.2, "from": 0, "value": 3, "countDur": 0.6, "label": "Haaland goals", "size": 170, "clear": False}]})

# 7 re-hook: Wimbledon at City; Stockley's hat-trick, the winner a screamer from distance; freeze, 3-4
st0 = [-6.5, 0.11, 27.5]; top = [-3.1, 2.25, 52.3]
B.append({"kicker": "Matchday 15 · at home", "headline": "Stockley hat-trick. [City 3–4].", "cut": True, "transition": "vhs", "vhsLabel": "PROBLEM", "vhsDur": 0.9, "scene": S_ETI, "accent": RED, "hype": False, "flashes": 8,
  "camFrom": {"pos": [-13, 2.6, 22], "tgt": [-2, 1.2, 40]}, "camera": {"pos": [-12, 2.4, 25], "tgt": [-2, 1.4, 44]}, "move": 6, "moveEase": "linear",
  "players": [P(kit=WIM, skin="#e7b593", hair="#1a1210", name="STOCKLEY", num=9, x=-6.7, z=27.0, action="kick", actionAt="a screamer", actionLag=-0.55, actionDur=0.8, after="celebrate", runup=2.0, label="Jayden Stockley", labelAt="Jayden Stockley"),
              P(kit=CITY, skin="#8a5a3c", hair="#141010", x=-5.2, z=30.2, front=True, action="dive", dir=-1, actionAt="a screamer", actionLag=-0.3, actionDur=0.7),
              P(kit=GKC, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="a screamer", actionLag=0.25)],
  "card": [{"type": "ball", "delay": 0, "point": [-6.48, 0.11, 27.45], "untilAt": "a screamer", "untilLag": -0.21},
           {"type": "ballpath", "world": True, "at": "a screamer", "lag": -0.21, "dur": 1.3, "slowmo": True, "points": [st0, mid(st0, top, 6.5), top]},
           bug(MCI, {"name": "WIM", "color": "#1f3f8f"}, [3, 4], "88'", [3, 3], "a screamer", 1.1),
           {"type": "big", "y": 1600, "at": "scores a hat-trick", "lag": 0.0, "from": 0, "value": 3, "countDur": 0.6, "label": "Stockley goals", "size": 170, "style": "accent", "clear": False, "hideAt": "Four–three", "hideLag": -0.3},
           {"type": "stamp", "text": "3–4", "sub": "the winner: a screamer", "at": "Four–three", "lag": -0.05, "color": RED, "rot": -0.07, "size": 120, "y": 900}],
  "speedlines": [{"at": "a screamer", "lag": -0.2, "dur": 1.0, "amount": 0.6}],
  "freezeAt": "Four–three", "freezeLag": -0.1, "shake": [{"at": "Four–three", "lag": -0.05, "amount": 16}]})

# 8 halfway: 12th; goals for 43 (2nd), against 43 (22nd)
B.append({"kicker": "Halfway · matchday 23", "headline": "Twelfth. Scores lots. [Leaks lots].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": RED, "lights": 0.5, "focus": 0.35,
  "camFrom": {"pos": [0, 46, -60], "tgt": [0, 0, 6]}, "camera": {"pos": [-20, 22, -34], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "board", "y": 1060, "delay": 0.0, "label": "City after 23 games · 12th", "cols": 12, "vcols": 3, "clear": False,
            "rows": [{"name": "POINTS", "value": "32"}, {"name": "SCORED  2ND", "value": "43"}, {"name": "CONCEDED 22ND", "value": "43"}],
            "focusPath": [{"t": 0, "row": 0}, {"at": "Only one team", "row": 1}, {"at": "Only two", "row": 2}]},
           {"type": "stamp", "text": "LEAKY", "sub": "only Grimsby and Barnet let in more", "at": "let in more", "lag": 0.1, "color": RED, "rot": -0.06, "size": 90, "y": 1560}]})

# 9 the odds now: 70% in the summer, 38% at halfway (finishing chart re-runs)
B.append({"kicker": "10,000 runs of the second half", "headline": "Promotion: 70% → [38%].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": RED, "lights": 0.45, "focus": 0.3,
  "camFrom": {"pos": [24, 20, -30], "tgt": [0, 0, 6]}, "camera": {"pos": [-22, 12, -18], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [hud("League One · second half", countAt="going up", countLag=-0.3, dur=2.0),
           {"type": "big", "at": "Seventy percent", "lag": -0.2, "from": 70, "value": 38, "suffix": "%", "countDur": 1.4, "label": "chance of promotion", "y": 640, "size": 150, "style": "accent", "clear": False},
           {"type": "simrun", "y": 1200, "at": "going up", "lag": -0.3, "dur": 2.2, "title": "Where City finish", "positions": [1, 16], "real": 12, "realLabel": "NOW",
            "dist": {1: 4.3, 2: 15.5, 3: 15.2, 4: 12.8, 5: 10.8, 6: 9.0, 7: 7.5, 8: 6.3, 9: 4.9, 10: 3.8, 11: 3.1, 12: 2.3, 13: 1.5, 14: 1.2, 15: 0.8, 16: 0.5},
            "zone": {"from": 1, "to": 6, "label": "Up or play-offs", "color": GREEN}, "minLabel": 9, "clear": False}],
  "glitch": [{"t": 0.0, "dur": 0.3, "amount": 0.6}]})

# 10 the window opens: January days crossing off, NEED: A DEFENDER
B.append({"kicker": "January transfer window", "headline": "The window's open. [Defender needed].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": GOLD, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.2], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [{"type": "crossoff", "y": 1050, "delay": 0.0, "title": "JANUARY", "days": 31, "cols": 7, "cell": 96, "crossT": 0.4, "dur": 3.0, "color": SKY, "caption": "window open", "clear": False},
           {"type": "stamp", "text": "NEED: DEFENDER", "sub": "22nd for goals conceded", "at": "City need a defender", "lag": -0.1, "color": RED, "rot": -0.06, "size": 70, "y": 1700}]})

# 11 the vote: three real candidates, then the poll
def cand(name, tag, kit, sx, word, gk=False):
    pl = dict(kit=kit, skin="#e7b593", hair="#2a1a10", name="")
    if gk: pl.update(gloves="#f2f2f2")
    return {"type": "pcard", "y": 980, "w": 300, "h": 420, "shiftX": sx, "side": "left" if sx < 0 else "right", "at": word, "lag": -0.1, "player": pl, "tag": tag, "caption": name, "clear": False}
CAM = {"shirt": "#f5a12d", "shorts": "#111111", "socks": "#f5a12d", "text": "#111111"}
BRO = {"shirt": "#ffffff", "shorts": "#111111", "socks": "#ffffff", "text": "#111111"}
VFB = {"shirt": "#2e2e33", "shorts": "#2e2e33", "socks": "#2e2e33", "text": "#ffffff"}
B.append({"kicker": "Your vote · episode 3", "headline": "Who should City [sign]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": TEAL, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [cand("Kelland Watts", "CB · Cambridge", CAM, -350, "Kelland Watts"), cand("Omar Sowunmi", "CB · Bromley", BRO, 0, "Omar Sowunmi"), cand("Dennis Seimen", "GK · Stuttgart", VFB, 350, "Dennis Seimen", gk=True),
           {"type": "poll", "y": 1600, "at": "You pick", "lag": -0.6, "question": "Who should City sign?", "options": [{"label": "Watts", "color": "#f5a12d", "fill": 0.34}, {"label": "Sowunmi", "color": "#9aa1ad", "fill": 0.33}, {"label": "Seimen", "color": "#2e2e33", "fill": 0.33}]}]})

for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
json.dump({"title": "Man City in League Two · Episode 2", "brand": "theo6k", "accent": TEAL, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
