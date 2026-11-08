# Builds videos/city-seven/spec.json (run from the repo root).
import json
ACC = "#6cabdd"
CITY = {"shirt": "#6cabdd", "shorts": "#ffffff", "socks": "#6cabdd", "text": "#1c2c5b"}
CGK = {"shirt": "#2b2f3a", "shorts": "#2b2f3a", "socks": "#2b2f3a", "text": "#f1c453"}
VILLA = {"shirt": "#670e36", "shorts": "#ffffff", "socks": "#670e36", "text": "#95bfe5"}
BRI = {"shirt": "#0057b8", "shorts": "#0057b8", "socks": "#ffffff", "text": "#ffffff", "stripes": ["#0057b8", "#ffffff"]}
FOR = {"shirt": "#dd0000", "shorts": "#ffffff", "socks": "#dd0000", "text": "#ffffff"}
FGK = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
ARS = {"shirt": "#ef0107", "shorts": "#ffffff", "socks": "#ef0107", "text": "#ffffff"}
SWFC = {"shirt": "#1f4e9c", "shorts": "#ffffff", "socks": "#1f4e9c", "text": "#ffffff", "stripes": ["#1f4e9c", "#ffffff"]}
S_CITY = {"type": "stadium", "crowd": ["#6cabdd", "#6cabdd", "#ffffff", "#1c2c5b"], "seed": 19}
S_VILLA = {"type": "stadium", "crowd": ["#670e36", "#95bfe5", "#670e36", "#f2c200"], "seed": 31}
S_FOR = {"type": "stadium", "crowd": ["#dd0000", "#ffffff", "#dd0000", "#1d1c22"], "seed": 41}
S_OLD = {"type": "stadium", "crowd": ["#1f4e9c", "#ffffff", "#8a7a5a", "#3a3020"], "seed": 4}
lines = [l.strip() for l in open('videos/city-seven/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
DONNA = dict(kit=CGK, skin="#e7b593", hair="#2a1a10", gloves="#f2f2f2")
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
def goal(word, x, z, kit, skin, hair, label, end, gk, gdir, side=1, lag=-0.1, labelAt=None, h=1.0, dur=0.5, extra=None, foot=None):
    """A shooter at (x, z) striking on `word` into the +z goal past a diving keeper; camera behind and to one side."""
    b0 = [x + 0.22, 0.11, z + 0.45]
    sh = P(kit=kit, skin=skin, hair=hair, x=x, z=z, label=label, labelAt=labelAt or word, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate")
    if foot: sh["foot"] = foot; b0[0] = x - 0.22
    kp = P(**gk, x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=gdir, actionAt=word, actionLag=lag + 0.45)
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34},
             {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": dur, "slowmo": False, "points": [b0, mid(b0, end, h), end]}]
    cam = {"camFrom": {"pos": [x + side * 3.0, 2.0, z - 6.5], "tgt": [x * 0.4, 1.0, 52]}, "camera": {"pos": [x + side * 2.4, 1.8, z - 4.8], "tgt": [x * 0.4, 1.0, 52]}}
    return [sh, kp] + (extra or []), cards, cam
B = []
# 1 hook
B.append({"kicker": "Premier League · 2026/27", "headline": "122 years. Nobody did [this].", "hookWords": True, "scene": S_CITY,
  "camFrom": {"pos": [0, 1.4, -2.6], "tgt": [0, 1.3, 12]}, "camera": {"pos": [0, 1.3, -1.3], "tgt": [0, 1.2, 12]}, "move": 6, "moveEase": "linear",
  "lights": 1, "flashes": 14, "speedlines": [{"t": 0, "dur": 1.0, "amount": 0.6}],
  "players": [P(kit=CITY, skin="#e7b593", hair="#3a2a1a", x=0, z=2.2, front=True, chest=True, pose="arms_up")],
  "card": [{"type": "big", "delay": -0.9, "countDur": 3.0, "from": 0, "value": 122, "suffix": " yrs", "label": "Since it last happened · 1904", "y": 1660, "hideAt": "Seven wins", "hideLag": -0.2},
           {"type": "tally", "at": "Seven wins", "lag": -0.25, "y": 1560, "r": 46, "gap": 14, "perRow": 5, "title": "Man City · first 10 games", "score": "{w} W · {l} L",
            "items": [{"mark": "check", "at": "Seven wins", "lag": -0.25 + 0.11 * i} for i in range(7)] + [{"mark": "x", "at": "three", "lag": 0.32 * i} for i in range(3)]}],
  "shake": [{"at": "three", "lag": 0.32 * i, "amount": 16} for i in range(3)], "freezeAt": "defeats", "freezeLag": 0.3})
# 2 1904
B.append({"kicker": "The only other time", "headline": "Sheffield Wednesday, [1904].", "accent": "#e9b949", "cut": True, "scene": S_OLD,
  "transition": "polaroid", "polaroidLabel": "1904", "lights": 0.85,
  "camFrom": {"pos": [0, 1.5, -4.5], "tgt": [0, 1.2, 12]}, "camera": {"pos": [0, 1.4, -3.2], "tgt": [0, 1.2, 12]}, "move": 4,
  "players": [P(kit=SWFC, skin="#efc9a8", hair="#5a4030", x=-1.5, z=2.8, front=True, pose="arms_up"),
              P(kit=SWFC, skin="#e7b593", hair="#2a1a10", x=0.1, z=2.2, front=True, chest=True),
              P(kit=SWFC, skin="#efc9a8", hair="#8a6a45", x=1.6, z=2.9, front=True)],
  "card": [{"type": "newspaper", "at": "Sheffield Wednesday", "lag": -0.3, "y": 1500, "masthead": "THE FOOTBALL ECHO", "dateline": "Season 1904–05",
            "headline": "SEVEN WINS…\nTHEN THREE DEFEATS", "sub": "Wednesday's perfect start is over", "color": "#2a2116", "spin": 1.4, "scale": 0.8}]})
# 3 Maresca's perfect start
B.append({"kicker": "August to October", "headline": "Seven games. [Seven wins].", "cut": True, "scene": S_CITY,
  "camFrom": {"pos": [-1.0, 1.5, -2.6], "tgt": [0.2, 1.3, 10]}, "camera": {"pos": [-0.4, 1.5, -1.6], "tgt": [0.2, 1.3, 10]}, "move": 4,
  "players": [P(outfit="suit", suitColor="#1c2233", tie="#6cabdd", skin="#e7b593", hair="#2a1a10", x=0.3, z=2.0, front=True, pose="fists", label="Enzo Maresca", labelAt="Maresca")],
  "confetti": True, "confettiAt": "Seven wins", "confettiColors": ["#6cabdd", "#ffffff", "#1c2c5b"],
  "card": [{"type": "rain", "y": 1560, "at": "Seven games", "groups": [{"n": 7, "color": "#6cabdd", "at": "Seven wins", "dur": 0.8}], "cols": 7, "cell": 96, "icon": "ball", "empty": 0, "label": "Wins"}]})
# 4 Villa
pl, cards, cam = goal("Jackson", -1.2, 40, VILLA, "#5a3a28", "#141010", "Nicolas Jackson", [2.8, 0.6, 52.8], DONNA, -1, side=-1)
pl[0].update(tag=2, tagLabel="Goals", tagAt="twice")
B.append(dict({"kicker": "24 October · Villa Park", "headline": "Jackson twice. [Villa 2–1].", "accent": "#ff4d5e", "cut": True, "scene": S_VILLA, "move": 5, "moveEase": "linear",
  "players": pl, "card": cards + [{"type": "tickets", "y": 1560, "delay": 0, "tickets": [{"comp": "Premier League", "teams": "Villa v City", "score": "2–1", "date": "24 Oct 2026", "color": "#670e36"}],
     "done": 0, "newAt": "Villa win", "stamp": "LOST", "dx": 0}],
  "shake": [{"at": "Villa win", "lag": 0.6, "amount": 12}]}, **cam))
# 5 Brighton
pl, cards, cam = goal("Ayari", 1.4, 41, BRI, "#c99a6e", "#1d1410", "Yasin Ayari", [-2.7, 0.5, 52.8], DONNA, 1, side=1)
B.append(dict({"kicker": "31 October · Etihad", "headline": "Brighton win at the [Etihad].", "accent": "#ff4d5e", "cut": True, "scene": S_CITY, "move": 5, "moveEase": "linear",
  "players": pl, "card": cards + [{"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 0, "to": 11, "dur": 1.6, "events": [{"min": 11, "text": "11' Ayari · 0–1"}]},
                                  {"type": "flytext", "text": "0–1", "size": 260, "endScale": 0.7, "y": 1600, "at": "One–nil", "lag": -0.1, "color": "#ff4d5e"}]}, **cam))
# 6 Forest away
B.append({"kicker": "Saturday · City Ground", "headline": "Nottingham Forest [away].", "accent": "#ff4d5e", "cut": True, "scene": S_FOR, "lights": 0.75,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 26, -44], "tgt": [0, 0, 10]}, "move": 4.5, "players": [],
  "card": [{"type": "flip", "y": 760, "at": "seventh", "label": "Forest v City", "groups": [{"label": "November", "value": 7, "digits": 2}], "side": {"top": "SAT", "big": "7", "bottom": "NOV"}}]})
# 7 Cunha steals and scores
cun = [-2.0, 0.11, 34.0]; cend = [-2.9, 0.3, 52.8]
B.append({"kicker": "6 minutes", "headline": "Cunha [steals it] and scores.", "accent": "#ff4d5e", "cut": True, "scene": S_FOR, "lights": 0.9,
  "camFrom": {"pos": [2.8, 2.3, 24.5], "tgt": [-1.5, 0.9, 36]}, "camera": {"pos": [2.0, 2.0, 26.5], "tgt": [-1.8, 0.9, 40]}, "move": 4.5, "moveEase": "linear",
  "players": [P(kit=CITY, skin="#f0c8a8", hair="#3a2a1a", x=-1.0, z=30, label="Gvardiol", labelAt="Gvardiol", path=[[-0.4, 28.5], [-1.6, 32.6]], pathDur=1.2, at="Six"),
              P(kit=FOR, skin="#6b4630", hair="#141010", x=-3.0, z=34.6, label="Jair Cunha", labelAt="Jair", path=[[-3.2, 34.8], [-2.2, 33.8], [-1.9, 34.0]], pathDur=0.7, at="takes", lag=-0.3,
                action="kick", actionAt="scores", actionLag=-0.55, actionDur=0.8, after="celebrate", hops=[]),
              P(**DONNA, x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="scores", actionLag=-0.05)],
  "card": [{"type": "ball", "at": "Six", "point": [-1.35, 0.11, 32.9], "untilAt": "scores", "untilLag": -0.21},
           {"type": "ballpath", "world": True, "at": "scores", "lag": -0.21, "dur": 0.75, "slowmo": False, "points": [[-1.35, 0.11, 32.9], [-2.2, 0.6, 43], cend]},
           {"type": "pen", "delay": 0, "anchor": 0, "strokes": [{"kind": "ellipse", "cx": 0, "cy": 0, "rx": 0.5, "ry": 0.16, "at": "takes the ball", "color": "#ffd23f", "layer": "under"},
                                                             {"kind": "text", "text": "LOST IT", "x": 640, "y": 1060, "size": 64, "rot": -0.08, "at": "off Gvardiol", "color": "#ffd23f"}]},
           {"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 0, "to": 6, "dur": 1.0, "events": [{"min": 6, "text": "6' Cunha · 1–0"}]}]})
# 8 Delap, City's old striker
pl, cards, cam = goal("makes it two", 0.9, 40.5, FOR, "#f0c8a8", "#4a3324", "Liam Delap", [-2.6, 1.6, 52.8], DONNA, 1, side=1, labelAt="Delap", h=2.2)
B.append(dict({"kicker": "18 minutes", "headline": "Delap. [Ex-City].", "accent": "#ff4d5e", "cut": True, "scene": S_FOR, "move": 4.5, "moveEase": "linear",
  "players": pl, "card": cards + [{"type": "pcard", "at": "Liam Delap", "y": 1300, "shiftX": 280, "w": 320, "h": 430, "side": "right", "tag": "Delap · ex-City", "color": ACC,
     "player": {"name": "Delap", "kit": CITY, "skin": "#f0c8a8", "hair": "#4a3324"}, "hideAt": "makes it two", "hideLag": 0.4}]}, **cam))
# 9 Cherki, then Delap on the counter
dl = [3.8, 0.11, 37.0]
B.append({"kicker": "Second half", "headline": "Then Delap [again]. 3–1.", "accent": "#ff4d5e", "cut": True, "scene": S_FOR,
  "camFrom": {"pos": [9, 3.2, 22], "tgt": [1.5, 0.9, 40]}, "camera": {"pos": [7.5, 2.4, 29], "tgt": [0.8, 1.0, 48]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=FOR, skin="#f0c8a8", hair="#4a3324", x=5.5, z=26, label="Delap", labelAt="Delap again", path=[[6.5, 24], [3.6, 36.6]], pathDur=2.0, at="Delap again", lag=-0.4, dribble=True,
                action="kick", actionAt="Three–one", actionLag=-0.85, actionDur=0.8, after="celebrate"),
              P(kit=CITY, skin="#c99a6e", hair="#141010", x=1.0, z=31, path=[[0.6, 27], [2.2, 35]], pathDur=2.2, at="Delap again", lag=-0.2),
              P(**DONNA, x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="Three–one", actionLag=-0.3)],
  "card": [{"type": "ballpath", "world": True, "at": "Three–one", "lag": -0.51, "dur": 0.55, "slowmo": False, "points": [dl, [3.2, 1.6, 45], [2.9, 2.0, 52.8]]},
           {"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 46, "to": 73, "dur": 2.8, "events": [{"min": 52, "text": "52' Cherki · 2–1"}, {"min": 73, "text": "73' Delap · 3–1"}]},
           {"type": "tickets", "y": 1430, "at": "Cherki", "tickets": [{"comp": "Premier League", "teams": "Villa v City", "score": "2–1", "date": "24 Oct 2026", "color": "#670e36"},
              {"comp": "Premier League", "teams": "City v Brighton", "score": "0–1", "date": "31 Oct 2026", "color": "#0057b8"},
              {"comp": "Premier League", "teams": "Forest v City", "score": "3–1", "date": "7 Nov 2026", "color": "#dd0000"}],
            "done": 2, "newAt": "Three–one", "newLag": 0.2, "stamp": "LOST", "dx": 0, "count": "{n} in a row"}]})
# 10 table
B.append({"kicker": "The table", "headline": "Arsenal [six points] clear.", "accent": "#ef0107", "cut": True, "scene": S_CITY, "focus": 0.6, "lights": 0.7,
  "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 20, -34], "tgt": [0, 0, 8]}, "move": 4, "players": [], "card": [{"type": "table", "y": 1050, "delay": 0, "scale": 1.3, "moveAt": "Arsenal go", "label": "Premier League · top",
     "rows": [{"pos": 1, "fromPos": 2, "fromRow": 1, "name": "Arsenal", "color": "#ef0107", "color2": "#ffffff", "pts": 27, "highlight": True},
              {"pos": 2, "fromPos": 1, "fromRow": 0, "name": "Man City", "color": "#6cabdd", "pts": 21}], "pill": "+6", "pillRow": 0}]})
# 11 your call
B.append({"kicker": "Your call", "headline": "Blip, or [over]?", "cut": True, "scene": S_CITY, "lights": 0.6,
  "orbit": {"center": [0, 1.2, 3], "r": 5, "from": -25, "to": 20, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.2, 3]},
  "players": [P(kit=CITY, skin="#e7b593", hair="#3a2a1a", x=-1.3, z=3.2, front=True, label="City · 21 pts", labelDelay=0.2),
              P(kit=ARS, skin="#c99a6e", hair="#141010", x=1.3, z=3.2, front=True, pose="arms_up", label="Arsenal · 27 pts", labelDelay=0.5)],
  "card": [{"type": "poll", "y": 1560, "at": "So be honest", "question": "City's title race?", "options": [{"label": "Just a blip", "color": ACC, "fill": 0.5}, {"label": "It's over", "color": "#ef0107", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v; b.setdefault("accent", ACC)
assert len(B) == len(lines) == 11
spec = {"title": "Man City: won 7, lost 3", "brand": "theo6k", "accent": ACC, "voSpeed": 1.08, "beats": B}
json.dump(spec, open('videos/city-seven/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
