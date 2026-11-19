# Builds videos/city-league-two/spec.json (run from the repo root). Episode 1: City's first League Two season.
# Every number comes from research.md (data/: 10,000-season sim + the official season, seed 2026).
import json
RED, GOLD, GREEN, TEAL, SKY = "#ff4d5e", "#e9b949", "#2ecc71", "#3FE0C5", "#6cabdd"
CITY = {"shirt": SKY, "shorts": "#ffffff", "socks": SKY, "text": "#1c2c5b"}
U21 = {"shirt": SKY, "shorts": "#1c2c5b", "socks": SKY, "text": "#1c2c5b"}
GIL = {"shirt": "#1e3c96", "shorts": "#1e3c96", "socks": "#ffffff", "text": "#ffffff"}
SAL = {"shirt": "#d6262e", "shorts": "#ffffff", "socks": "#d6262e", "text": "#ffffff"}
SWI = {"shirt": "#c8102e", "shorts": "#c8102e", "socks": "#c8102e", "text": "#ffffff"}
CHE = {"shirt": "#1f4fb4", "shorts": "#ffffff", "socks": "#1f4fb4", "text": "#ffffff"}
GRI = {"shirt": "#111111", "shorts": "#111111", "socks": "#111111", "text": "#ffffff", "stripes": ["#111111", "#ffffff"]}
FLE = {"shirt": "#c8102e", "shorts": "#ffffff", "socks": "#c8102e", "text": "#ffffff"}
L2O = {"shirt": "#c8102e", "shorts": "#ffffff", "socks": "#c8102e", "text": "#ffffff"}
GK = {"shirt": "#f7d117", "shorts": "#111111", "socks": "#f7d117", "text": "#111111"}
GKC = {"shirt": "#2ecc71", "shorts": "#111111", "socks": "#2ecc71", "text": "#111111"}
def small(crowd, seed): return {"type": "stadium", "ground": "small", "crowd": crowd, "seed": seed}
S_HOOK = small(["#6cabdd", "#ffffff", "#1c2c5b", "#6cabdd"], 4)
S_GIL = small(["#1e3c96", "#ffffff", "#1e3c96"], 9)
S_SAL = small(["#d6262e", "#ffffff", "#d6262e"], 12)
S_FLE = small(["#c8102e", "#ffffff", "#c8102e"], 15)
S_ETI = {"type": "stadium", "crowd": ["#6cabdd", "#ffffff", "#6cabdd", "#1c2c5b"], "seed": 6}
S_SIM = {"type": "stadium", "crowd": ["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], "seed": 21}
V = 'videos/city-league-two/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
HAAL = dict(kit=CITY, skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9)
FODEN = dict(kit=CITY, skin="#f0c8a8", hair="#3a2a1a", name="FODEN", num=47)
CBADGE = {"colors": [SKY, "#1c2c5b", "#ffffff"], "text": "MCFC"}
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
def hud(sub, **k):
    d = {"type": "simhud", "delay": 0, "sub": sub, "dur": 0, "clear": False}; d.update(k); return d
def bug(home, away, score, mn, frm=None, goalAt=None, lag=0.3, **k):
    d = {"type": "scorebug", "y": 560, "delay": 0, "home": home, "away": away, "score": score, "min": mn, "clear": False}
    if frm: d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    d.update(k); return d
MCI = {"name": "MCI", "color": SKY}
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
def trow(pos, name, color, pts, color2=None, hl=False, fromRow=None, frm=None, fromPos=None):
    r = {"pos": pos, "name": name, "color": color, "pts": pts}
    if fromPos is not None: r["fromPos"] = fromPos
    if color2: r["color2"] = color2
    if hl: r["highlight"] = True
    if fromRow is not None: r["fromRow"] = fromRow
    if frm is not None: r["from"] = frm
    return r
B = []

# 1 hook: the City shield drops through a trapdoor, LEAGUE TWO slams; Haaland alone in a tiny ground; the kids walk in
B.append({"kicker": "What if · Man City in League Two", "headline": "Man City: relegated to [League Two].", "hookWords": True, "scene": S_HOOK, "accent": TEAL, "lights": 0.85, "flashes": 6,
  "camFrom": {"pos": [0.75, 1.3, 1.3], "tgt": [0.5, 1.15, 10]}, "camera": {"pos": [0.6, 1.35, 0.6], "tgt": [0.45, 1.2, 10]}, "move": 6, "moveEase": "linear",
  "players": [P(**HAAL, x=0.9, z=3.4, front=True, chest=True, pose="think", label="Erling Haaland", labelAt="Erling Haaland"),
              P(kit=U21, skin="#8a5a3c", hair="#141010", num=61, x=-1.6, z=6.0, enter="walk", fromZ=10, walkDur=1.4, at="and the kids", lag=-0.4),
              P(kit=U21, skin="#f0c8a8", hair="#6a4a2a", num=75, x=-0.4, z=7.0, enter="walk", fromZ=11, walkDur=1.5, at="and the kids", lag=-0.2),
              P(kit=U21, skin="#d9a37c", hair="#141010", num=56, x=2.6, z=6.5, enter="walk", fromZ=10.5, walkDur=1.4, at="and the kids", lag=-0.3)],
  "card": [{"type": "trapdoor", "y": 1560, "shiftX": -250, "delay": -0.3, "scale": 1.05, "clear": False,
            "items": [{"name": "Man City", "badge": CBADGE, "at": "relegated", "lag": -0.25, "tag": "LEAGUE TWO", "tagColor": RED}]},
           {"type": "stamp", "text": "LEAGUE TWO", "sub": "4th tier · 2026/27", "at": "League Two", "lag": 0.0, "color": RED, "rot": -0.07, "size": 96, "y": 640}],
  "shake": [{"at": "League Two", "lag": 0.05, "amount": 16}]})

# 2 the squad: a team sheet fills (academy in sky blue, four League Two signings in grey)
SIGN = "#9aa1ad"
B.append({"kicker": "The squad", "headline": "Haaland, the academy, [four signings].", "cut": True, "transition": "whip", "scene": S_HOOK, "accent": TEAL, "lights": 0.6, "focus": 0.35,
  "camFrom": {"pos": [-30, 26, -40], "tgt": [0, 0, 5]}, "camera": {"pos": [24, 20, -34], "tgt": [0, 0, 5]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "lineup", "y": 1150, "delay": 0.0, "w": 760, "title": "City · League Two XI", "clear": False,
            "items": [{"name": "Haaland", "x": 0.5, "y": 0.12, "color": SKY, "t": 0.1},
                      {"name": "Foden", "x": 0.5, "y": 0.32, "color": SKY, "at": "Phil Foden"},
                      {"name": "R. Lewis", "x": 0.86, "y": 0.66, "color": SKY, "at": "Rico Lewis"},
                      {"name": "O'Reilly", "x": 0.14, "y": 0.66, "color": SKY, "at": "Nico O'Reilly"},
                      {"name": "McAidoo", "x": 0.82, "y": 0.3, "color": SKY, "at": "the under-twenty-ones"},
                      {"name": "T. Samba", "x": 0.18, "y": 0.3, "color": SKY, "at": "the under-twenty-ones", "lag": 0.15},
                      {"name": "Fapetu", "x": 0.35, "y": 0.5, "color": SKY, "at": "the under-twenty-ones", "lag": 0.3},
                      {"name": "Braybrooke", "x": 0.65, "y": 0.5, "color": SIGN, "at": "four League Two signings", "lag": 0.0},
                      {"name": "Fitzwater", "x": 0.36, "y": 0.72, "color": SIGN, "at": "four League Two signings", "lag": 0.15},
                      {"name": "Scarr", "x": 0.64, "y": 0.72, "color": SIGN, "at": "four League Two signings", "lag": 0.3},
                      {"name": "Hudson", "x": 0.5, "y": 0.9, "color": SIGN, "at": "four League Two signings", "lag": 0.45}]}]})

# 3 the benchmark: Premier League U21 sides v League Two clubs, real EFL Trophy results (W30 D24 L45), a kid's shot saved
B.append({"kicker": "EFL Trophy · 2023–2026 · real results", "headline": "The kids v League Two: [mostly losses].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SAL, "accent": RED, "lights": 0.7, "hype": False,
  "camFrom": {"pos": [6.5, 2.3, 39], "tgt": [-0.5, 1.2, 50]}, "camera": {"pos": [5.5, 2.1, 41], "tgt": [-0.5, 1.2, 50]}, "move": 6, "moveEase": "linear",
  "players": [P(kit=U21, skin="#8a5a3c", hair="#141010", num=56, x=-0.8, z=41.5, action="kick", actionAt="already play", actionLag=-0.3, actionDur=0.8, runup=1.4),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1),
              P(kit=L2O, skin="#e7b593", hair="#141010", x=-2.6, z=44.5, front=True), P(kit=L2O, skin="#8a5a3c", hair="#141010", x=1.8, z=47.5, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": [-0.58, 0.11, 41.95], "untilAt": "already play", "untilLag": 0.04},
           {"type": "ballpath", "world": True, "at": "already play", "lag": 0.04, "dur": 0.55, "slowmo": False, "flash": False, "saveBy": 1, "points": [[-0.58, 0.11, 41.95], [-1.2, 1.2, 47], [-1.9, 1.3, 52.0]]},
           {"type": "rain", "y": 1460, "at": "Premier League under-twenty-one", "lag": -0.2, "cols": 11, "cell": 46, "icon": "dot", "label": "games v League Two clubs", "clear": False,
            "groups": [{"n": 30, "color": GREEN, "t": 0.0, "dur": 0.7}, {"n": 24, "color": "#7d8594", "t": 0.5, "dur": 0.6}, {"n": 45, "color": RED, "at": "lose more", "lag": -0.3, "dur": 0.9}]},
           {"type": "stamp", "text": "W30 D24 L45", "sub": "Premier League U21 sides", "at": "than they win", "lag": -0.1, "color": RED, "rot": -0.05, "size": 74, "y": 700}]})

# 4 the odds: 10,000 seasons, City champions 9 times in 10
B.append({"kicker": "10,000 simulated seasons", "headline": "Add Haaland: champions [9 times in 10].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": GREEN, "lights": 0.5, "focus": 0.25,
  "camFrom": {"pos": [26, 22, -30], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 14, -18], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [hud("City · League Two 2026/27", countAt="ten thousand times", countLag=-0.5, dur=2.4),
           {"type": "simrun", "y": 1150, "at": "ten thousand times", "lag": -0.6, "dur": 2.6, "title": "Where City finish", "positions": [1, 10],
            "dist": {1: 89.7, 2: 7.4, 3: 1.8, 4: 0.6, 5: 0.3, 6: 0.1}, "zone": {"from": 1, "to": 3, "label": "Promoted", "color": GREEN}, "minLabel": 5,
            "stamp": {"text": "90%", "sub": "champions", "pos": 1}, "stampAt": "nine times in ten", "stampLag": -0.1, "stampSize": 100, "clear": False}],
  "glitch": [{"t": 0.0, "dur": 0.35}], "shake": [{"at": "nine times in ten", "lag": 0.0, "amount": 12}]})

# 5 press play: opening day at Gillingham, no Haaland, lost 2-1, 18th
pl, cards, cam = goal("Lost, two–one", 1.4, 40.5, 1, GIL, [-2.8, 0.7, 52.3], 1, GKC, CITY, lag=-0.6)
pl[0].update(skin="#e7b593", hair="#141010")
cam = {"camFrom": {"pos": [7.5, 2.5, 36.5], "tgt": [-0.5, 1.2, 50]}, "camera": {"pos": [6.5, 2.3, 39.0], "tgt": [-0.5, 1.2, 50]}, "move": 5, "moveEase": "linear", "follow": 0.3}
B.append({"kicker": "The official season · Matchday 1", "headline": "Opening day: [lost] at Gillingham.", "cut": True, "transition": "vhs", "vhsLabel": "PLAY", "vhsDur": 1.0, "scene": S_GIL, "accent": RED, **cam, "players": pl,
  "card": cards + [bug({"name": "GIL", "color": "#1e3c96"}, MCI, [2, 1], "88'", [1, 1], "Lost, two–one", 0.0),
                   hud("Season 1 · matchday 1", y=1700),
                   {"type": "stamp", "text": "NO HAALAND", "sub": "injured", "at": "without Haaland", "lag": -0.1, "color": RED, "rot": -0.06, "size": 70, "y": 1330},
                   {"type": "big", "at": "two–one", "lag": 0.5, "from": 1, "value": 18, "countDur": 0.5, "suffix": "th", "label": "in the table", "y": 1560, "size": 130, "style": "accent", "clear": False}]})

# 6 matchday 14: City win at Salford (the real leaders) and go top; one high shot, the table climbs underneath
pl, cards, cam = goal("win at Salford", -1.2, 41, -1, CITY, [2.8, 1.0, 52.3], -1, GK, SAL, lag=-0.3, label="Haaland", **{k: v for k, v in HAAL.items() if k != "kit"})
cam = {"camFrom": {"pos": [-13, 9, 30], "tgt": [0, 0.5, 46]}, "camera": {"pos": [-10, 7.5, 33], "tgt": [0, 0.5, 46]}, "move": 5, "moveEase": "linear", "follow": 0.3}
B.append({"kicker": "Matchday 14", "headline": "City win at Salford… and [go top].", "cut": True, "transition": "whip", "scene": S_SAL, "accent": GOLD, **cam, "players": pl,
  "card": cards + [bug({"name": "SAL", "color": "#d6262e"}, MCI, [1, 3], "71'", [1, 2], "win at Salford", 0.2),
                   {"type": "table", "y": 1460, "at": "the real leaders", "lag": -0.3, "moveAt": "go top", "moveLag": -0.2, "scale": 1.0, "label": "League Two · after matchday 14", "clear": False,
                    "rows": [trow(1, "Man City", SKY, 31, hl=True, fromRow=2, frm=28, fromPos=3), trow(2, "Barnet", "#f08a1d", 30, fromRow=0, frm=29, fromPos=1), trow(3, "Grimsby", "#f2f2f2", 29, "#111111", fromRow=1, frm=28, fromPos=2), trow(4, "Tranmere", "#ffffff", 28, "#1e3c96", frm=25, fromPos=6)]}]})

# 7 re-hook: with four games left Grimsby go above them (table slides the other way)
B.append({"kicker": "Matchday 42 · four games left", "headline": "Then Grimsby [go above them].", "cut": True, "transition": "vhs", "vhsLabel": "WEIRD", "vhsDur": 0.9, "scene": small(["#111111", "#ffffff", "#111111"], 18), "accent": RED, "lights": 0.45, "focus": 0.3,
  "camFrom": {"pos": [20, 14, -26], "tgt": [0, 0, 8]}, "camera": {"pos": [-14, 9, -18], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "table", "y": 1050, "delay": 0.0, "moveAt": "Grimsby go above", "moveLag": -0.1, "scale": 1.15, "label": "League Two · after matchday 42", "clear": False,
            "rows": [trow(1, "Grimsby", "#f2f2f2", 86, "#111111", fromRow=1, frm=83, fromPos=2), trow(2, "Man City", SKY, 85, hl=True, fromRow=0, frm=84, fromPos=1), trow(3, "Barnet", "#f08a1d", 81, frm=81), trow(4, "Swindon", "#c8102e", 72, frm=69)]}],
  "glitch": [{"at": "gets weird", "lag": 0.0, "dur": 0.45}]})

# 8 matchday 43: Swindon win 4-0 at City; a goal barrage from behind the net, then a freeze
bar = []
for i, (x0, ex) in enumerate([(-6, -2.6), (4, 2.7), (-1.5, 1.4), (7, -2.2)]):
    s0 = [x0, 0.11, 38 + i]; e0 = [ex, 0.9 + 0.3 * (i % 2), 52.3]
    bar.append({"type": "ballpath", "world": True, "at": "and win", "lag": -1.6 + i * 0.75, "dur": 0.55, "slowmo": False, "points": [s0, mid(s0, e0, 1.6), e0]})
B.append({"kicker": "Matchday 43 · at home", "headline": "Swindon come to City: [0–4].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": RED, "hype": False, "flashes": 6,
  "camFrom": {"pos": [1.5, 2.4, 60.5], "tgt": [0, 1.0, 40]}, "camera": {"pos": [0.5, 2.1, 59.5], "tgt": [0, 1.0, 40]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=SWI, skin="#e7b593", hair="#141010", x=-3.5, z=44, action="celebrate"), P(kit=SWI, skin="#8a5a3c", hair="#141010", x=3, z=42, action="celebrate"),
              P(kit=GKC, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0.4, z=51.6, front=False, pose="keeper")],
  "card": bar + [bug(MCI, {"name": "SWI", "color": "#c8102e"}, [0, 4], "90'", [0, 0], "and win", -1.0, y=600)],
  "freezeAt": "four–nil", "freezeLag": 0.1, "shake": [{"at": "four–nil", "lag": 0.1, "amount": 14}]})

# 9 final day: level on 89, Grimsby far ahead on goal difference (tale of the tape)
B.append({"kicker": "Matchday 46 · final day", "headline": "Level on [89 points].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": GOLD, "lights": 0.5,
  "camFrom": {"pos": [0, 1.5, -2.8], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.6], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear",
  "players": [P(**HAAL, x=-1.0, z=3.4, front=True, pose="think"), P(kit=GRI, skin="#e7b593", hair="#141010", x=1.2, z=3.6, front=True, pose="think")],
  "card": [{"type": "tape", "y": 1450, "at": "Level on", "lag": -0.3, "left": {"name": "Man City", "color": SKY}, "right": {"name": "Grimsby", "color": "#e8e8ea"}, "clear": False,
            "rows": [{"label": "Points", "left": 89, "right": 89, "t": 0.1}, {"label": "Goal difference", "left": 28, "right": 45, "at": "goal difference", "lag": -0.4, "floor": 0}]}],
  "punch": [{"at": "way ahead", "amount": 0.08, "dur": 1.6}]})

# 10 the finale: split screen, both scores update; then champions with the trophy and Haaland's 29
B.append({"kicker": "Final day", "headline": "City 3–1. Grimsby [lose 6–1].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": GOLD, "flashes": 10,
  "camFrom": {"pos": [0, 1.6, -3.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.4], "tgt": [0, 1.3, 10]}, "move": 5,
  "players": [P(**HAAL, x=0, z=3.4, front=True, pose="fists", label="City v Chesterfield", labelDelay=0.1)],
  "split": {"scene": S_FLE, "lights": 0.6, "camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.6], "tgt": [0, 1.3, 10]}, "move": 5,
            "players": [P(kit=GRI, skin="#e7b593", hair="#141010", x=0, z=3.4, front=True, pose="think", label="Fleetwood v Grimsby", labelDelay=0.1)]},
  "card": [bug(MCI, {"name": "CHE", "color": "#1f4fb4"}, [3, 1], "FT", [1, 1], "three–one", -0.3, y=1420, shiftX=-200),
           bug({"name": "FLE", "color": "#c8102e"}, {"name": "GRI", "color": "#f2f2f2"}, [6, 1], "FT", [2, 1], "six–one", -0.3, y=1640, shiftX=200)],
  "shots": [{"at": "Champions", "lag": -0.15, "cut": True, "transition": "whip", "headline": "League Two [champions].", "scene": S_ETI, "split": None, "confetti": True, "flashes": 16,
     "orbit": {"center": [0, 1.25, 3], "r": 5.0, "from": -24, "to": 16, "h": 1.5, "h2": 1.8, "dur": 5}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
     "players": [P(**HAAL, x=0, z=3.2, front=True, chest=True, pose="arms_up", trophy=True),
                 P(**FODEN, x=-1.9, z=4.2, front=True, action="celebrate"), P(kit=CITY, skin="#8a5a3c", hair="#141010", num=82, x=1.9, z=4.2, front=True, action="celebrate")],
     "card": [{"type": "big", "at": "by three points", "lag": -0.3, "from": 89, "value": 92, "countDur": 0.6, "label": "points · 3 clear", "y": 1480, "size": 150, "clear": False},
              {"type": "stamp", "text": "29 GOALS", "sub": "Haaland · 40 games", "at": "by three points", "lag": 0.5, "color": GOLD, "rot": -0.06, "size": 80, "y": 1730}]}]})

# 11 the vote: the title celebration carries on (no cut) and the poll pops up
B.append({"kicker": "Next: League One", "headline": "City can sign [one player].", "accent": TEAL, "confetti": True, "flashes": 10,
  "orbit": {"center": [0, 1.25, 3], "r": 5.0, "from": 16, "to": 40, "h": 1.8, "h2": 2.0, "dur": 6},
  "card": [{"type": "poll", "y": 1600, "at": "Who should", "lag": -0.8, "question": "Who should City sign?", "options": [{"label": "A striker", "color": SKY, "fill": 0.34}, {"label": "A centre-back", "color": "#1c2c5b", "fill": 0.33}, {"label": "A keeper", "color": "#3a4356", "fill": 0.33}]}]})

for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
json.dump({"title": "Man City in League Two · Episode 1", "brand": "theo6k", "accent": TEAL, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
