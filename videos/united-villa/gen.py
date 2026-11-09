# Builds videos/united-villa/spec.json (run from the repo root).
import json, math
ACC = "#ff4d5e"
MUN = {"shirt": "#da291c", "shorts": "#ffffff", "socks": "#111111", "text": "#ffffff"}
MGK = {"shirt": "#2fae6b", "shorts": "#1d1c22", "socks": "#2fae6b", "text": "#ffffff"}
AVL = {"shirt": "#95bfe5", "shorts": "#670e36", "socks": "#95bfe5", "text": "#670e36"}   # Villa in light blue (away-style) to avoid a red v claret clash
VGK = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
S_OT = {"type": "stadium", "crowd": ["#da291c", "#ffffff", "#111111", "#da291c"], "seed": 7}
lines = [l.strip() for l in open('videos/united-villa/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
LAM = dict(kit=MGK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2")
VKEEP = dict(kit=VGK, skin="#e7b593", hair="#2a1a10", gloves="#f2f2f2")
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
def defenders(b0, end, kit, word, lag=-0.1, skins=(("#e7b593", "#3a2a1a"), ("#8a5a3c", "#141010"))):
    dx, dz = end[0] - b0[0], end[2] - b0[2]; L = math.hypot(dx, dz); nx, nz = -dz / L, dx / L
    a = [b0[0] + dx * 0.28 + nx * 1.5, b0[2] + dz * 0.28 + nz * 1.5]
    c = [b0[0] + dx * 0.72 - nx * 2.2, b0[2] + dz * 0.72 - nz * 2.2]
    return [P(kit=kit, skin=skins[0][0], hair=skins[0][1], x=round(a[0], 2), z=round(a[1], 2), front=True, action="dive", dir=1 if nx > 0 else -1, actionAt=word, actionLag=lag + 0.15, actionDur=0.7),
            P(kit=kit, skin=skins[1][0], hair=skins[1][1], x=round(c[0], 2), z=round(c[1], 2), front=True, action="run", path=[[round(c[0] - nx * 0.6, 2), round(c[1] - 1.0, 2)], [round(c[0], 2), round(c[1], 2)]], pathDur=1.2, at=word, lag=lag - 0.5)]
def shot(word, x, z, kit, skin, hair, label, end, h=1.0, dur=0.5, lag=-0.1, labelAt=None, defKit=None, foot=None, runup=True):
    b0 = [x + (-0.22 if foot == "left" else 0.22), 0.11, z + 0.45]
    sh = P(kit=kit, skin=skin, hair=hair, x=x, z=z, label=label, labelAt=labelAt or word, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate")
    if foot: sh["foot"] = foot
    if not runup: sh["runup"] = False
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34},
             {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": dur, "slowmo": False, "points": [b0, mid(b0, end, h), end]}]
    return [sh] + (defenders(b0, end, defKit, word, lag) if defKit else []), cards
def keeper(gk, word, d, lag):
    return P(**gk, x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=d, actionAt=word, actionLag=lag)
B = []
# 1 hook: Dorgu's header already flying on frame 0
head = [0.9, 2.25, 47.3]; hend = [-2.6, 1.5, 52.8]
B.append({"kicker": "Premier League · Old Trafford", "headline": "United came back. Still in the [drop zone].", "hookWords": True, "scene": S_OT,
  "camFrom": {"pos": [6.5, 2.2, 41.5], "tgt": [-0.6, 1.6, 50.5]}, "camera": {"pos": [5.0, 1.9, 43.5], "tgt": [-0.8, 1.5, 51]}, "move": 5, "moveEase": "linear", "lights": 1, "flashes": 16,
  "players": [P(kit=MUN, skin="#8a5a3c", hair="#141010", x=0.9, z=47.0, label="Dorgu", labelDelay=0.1, hops=[{"t": -0.35, "dur": 0.7, "height": 0.6}], action="celebrate", actionDelay=0.9),
              P(kit=AVL, skin="#e7b593", hair="#3a2a1a", x=1.9, z=47.8, front=True, hops=[{"t": -0.3, "dur": 0.6, "height": 0.4}]),
              P(**VKEEP, x=0.2, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionDelay=-0.25, actionDur=0.9)],
  "card": [{"type": "ballpath", "world": True, "delay": -0.4, "dur": 0.7, "slowmo": False, "points": [head, mid(head, hend, 2.4), hend], "noShift": True},
           {"type": "flytext", "text": "4–4", "size": 300, "endScale": 0.7, "y": 1450, "delay": 0.45, "color": "#ffffff", "clear": False, "hideAt": "relegation", "hideLag": -0.3},
           {"type": "stamp", "text": "18TH", "sub": "relegation zone", "at": "relegation", "lag": -0.2, "color": ACC, "rot": -0.12, "y": 1460}],
  "confetti": True, "confettiDelay": 0.3, "confettiColors": ["#da291c", "#ffffff", "#111111"],
  "freezeAt": "relegation zone", "freezeLag": -0.1})
# 2 date
B.append({"kicker": "Sunday · Old Trafford", "headline": "Aston Villa at [Old Trafford].", "cut": True, "scene": S_OT,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 24, -42], "tgt": [0, 0, 10]}, "move": 4, "players": [],
  "card": [{"type": "flip", "y": 760, "at": "eighth", "label": "Man United v Aston Villa", "groups": [{"label": "November", "value": 8, "digits": 2}], "side": {"top": "SUN", "big": "8", "bottom": "NOV"}}]})
# 3 two Lammens errors inside four minutes
p1, c1 = shot("Alysson", -2.2, 44.5, AVL, "#c99a6e", "#141010", "Alysson", [-1.0, 0.4, 52.8], runup=False)
p2, c2 = shot("Jackson", 1.8, 43.5, AVL, "#5a3a28", "#141010", "Nicolas Jackson", [2.9, 0.6, 52.8], runup=False)
B.append({"kicker": "Inside 4 minutes", "headline": "Two [Lammens] mistakes. 0–2.", "cut": True, "scene": S_OT, "lights": 0.85,
  "camFrom": {"pos": [-5.0, 2.4, 37], "tgt": [0, 1.0, 51]}, "camera": {"pos": [-4.0, 2.1, 39], "tgt": [0.2, 1.0, 51]}, "move": 6, "moveEase": "linear",
  "players": [P(**LAM, x=0, z=51.0, front=True, pose="keeper", label="Lammens", labelAt="Lammens"), p1[0], p2[0],
              P(kit=MUN, skin="#e7b593", hair="#3a2a1a", x=-3.8, z=47, front=True), P(kit=MUN, skin="#8a5a3c", hair="#141010", x=3.6, z=46.5, front=True)],
  "card": c1 + c2 + [{"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 0, "to": 4, "dur": 2.4, "events": [{"min": 1, "text": "1' Alysson · 0–1"}, {"min": 4, "text": "4' Jackson · 0–2"}]},
           {"type": "pen", "delay": 0, "anchor": 0, "strokes": [{"kind": "ellipse", "cx": 0, "cy": 0, "rx": 0.5, "ry": 0.16, "at": "mistakes", "color": "#ffd23f", "layer": "under"},
                                                             {"kind": "text", "text": "ERROR x2", "x": 560, "y": 1100, "size": 66, "rot": -0.08, "at": "Lammens", "color": "#ffd23f"}]}]})
# 4 Bruno pen, Tielemans: 2-2
pb, cb = shot("penalty", 0.1, 40.9, MUN, "#e7b593", "#3a2a1a", "Bruno Fernandes", [2.9, 0.5, 52.8], labelAt="Bruno")
pb[0]["num"] = None
B.append({"kicker": "16 minutes · first half", "headline": "Bruno. Then [Tielemans]. 2–2.", "cut": True, "scene": S_OT,
  "camFrom": {"pos": [-3.2, 2.0, 33.5], "tgt": [0.6, 1.0, 52]}, "camera": {"pos": [-2.4, 1.8, 35.5], "tgt": [0.6, 1.0, 52]}, "move": 3, "moveEase": "linear",
  "players": pb + [keeper(VKEEP, "penalty", -1, 0.25)],
  "card": cb + [{"type": "stack", "y": 1640, "delay": 0, "size": 150, "items": [{"value": 1, "label": "16' Bruno · pen", "at": "penalty", "prefix": "", "suffix": "–2"}]}],
  "shots": [{"at": "Tielemans", "lag": -0.35, "cut": True, "move": 3.5, "moveEase": "linear",
     "camFrom": {"pos": [5.5, 2.3, 30], "tgt": [0.5, 1.0, 51]}, "camera": {"pos": [4.5, 2.0, 32.5], "tgt": [0.3, 1.0, 51]},
     "players": shot("old club", 2.2, 36.5, MUN, "#f0c8a8", "#c9a46a", "Tielemans · ex-Villa", [-2.8, 1.8, 52.8], h=2.6, dur=0.65, labelAt="Tielemans", defKit=AVL)[0] + [keeper(VKEEP, "old club", 1, 0.35)],
     "card": shot("old club", 2.2, 36.5, MUN, "#f0c8a8", "#c9a46a", "", [-2.8, 1.8, 52.8], h=2.6, dur=0.65)[1]
             + [{"type": "flytext", "text": "2–2", "size": 280, "endScale": 0.7, "y": 1560, "at": "Two–two", "lag": -0.1, "color": "#ffffff", "clear": False}]}]})
# 5 Villa 4-2: dark analytics board
B.append({"kicker": "After the break", "headline": "McGinn. Goretzka. [4–2 Villa].", "cut": True, "scene": S_OT, "punch": [{"at": "punishes", "amount": 0.1, "dur": 1.6}, {"at": "Four–two", "amount": 0.14, "dur": 1.4}], "camFrom": "stand", "camera": "stand", "lights": 0.4, "focus": 0.75, "players": [],
  "card": {"type": "tactic", "theme": "dark", "y": 1180, "delay": 0, "note": False, "home": "#95bfe5", "away": "#da291c", "awayText": "#ffffff", "r": 34, "showBall": False,
    "players": [{"n": "GK", "x": 0.5, "y": 0.05, "team": "away", "name": "Lammens", "label": "left"}, {"n": "", "x": 0.4, "y": 0.2, "team": "away", "name": "Yoro", "nameAt": "Yoro"},
                {"n": 7, "x": 0.5, "y": 0.22, "team": "home", "name": "McGinn", "nameAt": "McGinn"}, {"n": 8, "x": 0.62, "y": 0.3, "team": "home", "name": "Goretzka", "nameAt": "Goretzka", "ring": "#95bfe5"}],
    "moves": [{"from": 2, "to": [0.6, 0.0], "at": "McGinn scores", "dur": 0.5, "kind": "shot", "ball": False, "color": "#95bfe5"},
              {"from": 3, "to": [0.42, 0.0], "at": "punishes", "dur": 0.5, "kind": "shot", "ball": False, "color": "#95bfe5"}],
    "tags": [{"at": "McGinn", "x": 0.72, "y": 0.12, "text": "48' pen · 2–3", "color": "#670e36"},
             {"at": "Yoro mistake", "x": 0.25, "y": 0.3, "text": "YORO ERROR", "color": "#da291c"},
             {"at": "Four–two", "x": 0.5, "y": 0.62, "text": "MUN 2–4 AVL", "color": "#670e36"}]}})
# 6 Zirkzee 92'
pz, cz = shot("Zirkzee", -1.0, 41, MUN, "#e7b593", "#5a3a20", "Zirkzee", [2.8, 0.6, 52.8], defKit=AVL)
B.append({"kicker": "92 minutes", "headline": "[Zirkzee]. 4–3.", "cut": True, "scene": S_OT, "lights": 0.8,
  "camFrom": {"pos": [-4.0, 2.2, 32], "tgt": [0, 1.0, 51]}, "camera": {"pos": [-3.0, 2.0, 34.5], "tgt": [0.2, 1.0, 51]}, "move": 4, "moveEase": "linear",
  "players": pz + [keeper(VKEEP, "Zirkzee", -1, 0.35)],
  "card": cz + [{"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 88, "to": 92, "dur": 1.2, "phase": "STOPPAGE TIME", "events": [{"min": 92, "text": "92' Zirkzee · 3–4"}]}]})
# 7 Dorgu header, drone replay
h0 = [0.9, 2.25, 47.3]
B.append({"kicker": "Deep into stoppage time", "headline": "Dorgu. [4–4].", "cut": True, "scene": S_OT, "letterbox": True, "replayTag": "REPLAY", "follow": 0.4,
  "camFrom": {"pos": [-9, 7, 39], "tgt": [0, 0.8, 49]}, "camera": {"pos": [6.5, 3.6, 42], "tgt": [-0.4, 1.0, 50]}, "move": 5,
  "players": [P(kit=MUN, skin="#8a5a3c", hair="#141010", x=0.9, z=47.0, label="Dorgu", labelAt="Dorgu", hops=[{"at": "heads", "lag": -0.35, "dur": 0.7, "height": 0.6}], action="celebrate", actionAt="heads", actionLag=0.6),
              P(kit=AVL, skin="#e7b593", hair="#3a2a1a", x=1.9, z=47.8, front=True, hops=[{"at": "heads", "lag": -0.3, "dur": 0.6, "height": 0.4}]),
              P(kit=AVL, skin="#8a5a3c", hair="#141010", x=-1.8, z=48.5, front=True),
              P(**VKEEP, x=0.2, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="heads", actionLag=-0.1, actionDur=0.9),
              P(kit=MUN, skin="#f0c8a8", hair="#3a2a1a", x=-6, z=30, path=[[-8, 26], [-2.5, 44]], pathDur=1.6, at="Dorgu", action="run")],
  "card": [{"type": "ballpath", "world": True, "at": "heads", "lag": 0.0, "dur": 0.7, "slowmo": False, "points": [h0, mid(h0, hend, 2.4), hend]},
           {"type": "flytext", "text": "4–4", "size": 320, "endScale": 0.75, "y": 1500, "at": "Four–four", "lag": -0.1, "color": "#ffffff", "clear": False}],
  "confetti": True, "confettiAt": "Four–four", "confettiColors": ["#da291c", "#ffffff", "#111111"]})
# 8 re-hook: 18th, lowest since 1986/87
B.append({"kicker": "The table", "headline": "18th. Lowest since [1986].", "cut": True, "transition": "vhs", "vhsLabel": "1986", "vhsDur": 1.4,
  "scene": S_OT, "lights": 0.45, "focus": 0.35,
  "camFrom": {"pos": [1.2, 2.6, -6.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [-0.3, 1.8, -1.6], "tgt": [0, 1.25, 10]}, "move": 6, "moveEase": "linear", "punch": [{"at": "eighteenth", "amount": 0.12, "dur": 1.6}],
  "players": [P(kit=MUN, skin="#e7b593", hair="#3a2a1a", x=0, z=2.2, front=True, label="Man United · 18th", labelAt="eighteenth")],
  "card": [{"type": "big", "at": "eighteenth", "value": 18, "suffix": "th", "label": "Lowest after 10 games since 1986/87", "y": 1560, "style": "accent", "size": 260}]})
# 9 Keane tears into Carrick
B.append({"kicker": "After the whistle", "headline": "Keane tore into [Carrick].", "cut": True,
  "scene": {"type": "booth", "crowd": ["#da291c", "#ffffff", "#111111"], "seed": 9, "screenLeft": ["KEANE", "ON CARRICK"], "screenRight": ["MUN", "18TH"]},
  "players": [P(outfit="suit", suitColor="#1b1d24", tie="#3a3f4b", skin="#e7b593", hair="#4a4038", headset=True, sx=0.5, scale=0.75, front=True, pose="point", mood="cross", label="Roy Keane", labelAt="Roy Keane")],
  "card": [{"type": "newspaper", "at": "Roy Keane", "lag": -0.2, "y": 1480, "masthead": "THE MATCHDAY POST", "dateline": "Monday 9 November 2026",
            "headline": "KEANE TEARS\nINTO CARRICK", "sub": "United 18th after 4–4 draw", "color": "#2a2116", "spin": 1.4, "scale": 0.8}]})
# 10 resign?
B.append({"kicker": "Michael Carrick", "headline": "Resign? He [expects to stay].", "cut": True, "scene": S_OT, "lights": 0.75,
  "camFrom": {"pos": [-0.8, 1.5, -2.8], "tgt": [0.1, 1.3, 10]}, "camera": {"pos": [-0.3, 1.5, -1.8], "tgt": [0.1, 1.3, 10]}, "move": 4, "moveEase": "linear",
  "players": [P(outfit="suit", suitColor="#1c1f28", tie="#7a1420", skin="#efc9a8", hair="#4a3324", x=0.2, z=2.0, front=True, label="Michael Carrick", labelDelay=0.2)],
  "card": [{"type": "stamp", "text": "RESIGN?", "sub": "asked on Sky", "at": "resign", "color": ACC, "rot": 0.1, "y": 1500, "hideAt": "expects", "hideLag": -0.2},
           {"type": "stamp", "text": "STAYING", "sub": "he says", "at": "expects to stay", "color": "#ffffff", "rot": -0.1, "y": 1500}]})
# 11 your call
B.append({"kicker": "Your call", "headline": "Carrick: [stay or go]?", "cut": True, "scene": S_OT, "lights": 0.6,
  "orbit": {"center": [0, 1.2, 3], "r": 5, "from": -25, "to": 20, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.2, 3]}, "flashes": 8,
  "players": [P(outfit="suit", suitColor="#1c1f28", tie="#7a1420", skin="#efc9a8", hair="#4a3324", x=-1.2, z=3.2, front=True, label="Carrick", labelDelay=0.2),
              P(kit=MUN, skin="#8a5a3c", hair="#141010", x=1.3, z=3.4, front=True, pose="arms_up", label="United · 18th", labelDelay=0.5)],
  "card": [{"type": "poll", "y": 1560, "at": "So be honest", "question": "Should Carrick stay?", "options": [{"label": "Give him time", "color": "#da291c", "fill": 0.5}, {"label": "Time to go", "color": "#9aa1ad", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v; b.setdefault("accent", ACC)
assert len(B) == len(lines) == 11
spec = {"title": "Man United 4–4 Aston Villa", "brand": "theo6k", "accent": ACC, "voSpeed": 1.08, "beats": B}
json.dump(spec, open('videos/united-villa/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
