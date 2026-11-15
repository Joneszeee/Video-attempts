# Builds videos/england-spain/spec.json (run from the repo root).
import json, math
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
ENG = {"shirt": "#ffffff", "shorts": "#1c2c5b", "socks": "#ffffff", "text": "#1c2c5b"}
ESP = {"shirt": "#c60b1e", "shorts": "#1c2c7a", "socks": "#c60b1e", "text": "#ffc400"}
GKE = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
GKS = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
S_MAD = {"type": "stadium", "crowd": ["#c60b1e", "#ffc400", "#c60b1e", "#ffffff"], "seed": 14}
V = 'videos/england-spain/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def E(**k): return P(kit=ENG, **k)
def S(**k): return P(kit=ESP, **k)
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
def bug(score, mn, frm=None, goalAt=None, lag=0.35, red=None, **k):
    d = {"type": "scorebug", "y": 520, "delay": 0, "home": {"name": "ESP", "color": "#c60b1e"}, "away": {"name": "ENG", "color": "#ffffff"}, "score": score, "min": mn, "clear": False}
    if frm: d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    if red: d["red"] = red
    d.update(k); return d
def keeper(kit, d, word=None, lag=0.3, **k):
    kp = P(kit=kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", **k)
    if word: kp.update(action="dive", dir=d, actionAt=word, actionLag=lag)
    return kp
B = []
# 1 hook: the streak shatters
B.append({"kicker": "Spain 2–3 England · Nations League", "headline": "England end Spain's [43-game] run.", "hookWords": True, "scene": S_MAD, "accent": GOLD, "lights": 0.8, "flashes": 16,
  "camFrom": {"pos": [0.9, 1.5, 0.2], "tgt": [0.9, 1.35, 10]}, "camera": {"pos": [0.9, 1.5, -1.0], "tgt": [0.9, 1.35, 10]}, "move": 7, "moveEase": "linear",
  "players": [E(skin="#e7b593", hair="#3a2a1a", x=2.3, z=3.6, front=True, action="celebrate", label="England · 10 men", labelAt="ten men")],
  "card": [{"type": "streak", "y": 1100, "shiftX": -140, "delay": -0.9, "n": 43, "cols": 8, "cell": 88, "fill": 1.1, "title": "Spain · games unbeaten", "breakAt": "unbeaten run", "breakLag": 0.1, "broken": "OVER", "brokenLabel": "after 43 games", "clear": False},
           {"type": "stamp", "text": "10 MEN", "sub": "in Madrid", "at": "ten men", "lag": -0.1, "color": RED, "rot": -0.08, "size": 100, "dx": 240, "y": 1760}],
  "shake": [{"at": "unbeaten run", "lag": 0.15, "amount": 20}, {"at": "ten men", "lag": 0.06, "amount": 12}]})
# 2 the setting
B.append({"kicker": "Madrid · Sunday 15 November 2026", "headline": "World champions. Unbeaten since [March 2024].", "cut": True, "transition": "whip", "scene": S_MAD, "accent": GOLD, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 16, -30], "tgt": [0, 0, 10]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 700, "delay": 0.2, "label": "Nations League · Group A3", "groups": [{"label": "November", "value": 15, "digits": 2}], "side": {"top": "SUN", "big": "15", "bottom": "NOV"}},
           {"type": "trophies", "at": "world champions", "lag": -0.3, "floor": 1500, "stagger": 0, "rise": 0.55, "items": [{"kind": "worldcup", "sx": 0.5, "h": 160, "size": 210, "label": "Spain · World Cup 2026"}], "clear": False},
           {"type": "big", "at": "hadn't lost", "lag": -0.2, "from": 0, "value": 43, "countDur": 0.9, "label": "Games unbeaten · since March 2024", "y": 1740, "size": 170, "clear": False}]})
# 3 Kane penalty
b0 = [0.22, 0.11, 41.5]; end = [3.0, 0.5, 52.3]
B.append({"kicker": "45' · penalty", "headline": "Kane from the spot. [0–1].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_MAD, "accent": GOLD, "follow": 0.5,
  "camFrom": {"pos": [-3.6, 2.0, 33.5], "tgt": [0.5, 1.0, 52]}, "camera": {"pos": [-3.0, 1.8, 35.5], "tgt": [0.5, 1.0, 52]}, "move": 4, "moveEase": "linear",
  "players": [E(skin="#f0c8a8", hair="#b8905a", x=0, z=41.0, label="Harry Kane", labelDelay=0.2, action="kick", actionAt="from the spot", actionLag=-0.35, actionDur=0.8, after="celebrate", runup=2.2),
              keeper(GKS, -1, "from the spot", 0.05),
              S(skin="#e7b593", hair="#141010", x=-6, z=36.5), S(skin="#8a5a3c", hair="#141010", x=6.5, z=36.2), E(skin="#8a5a3c", hair="#141010", x=4.5, z=35.8)],
  "card": [bug([0, 1], "45'", [0, 0], "from the spot"),
           {"type": "ball", "delay": 0, "point": b0, "untilAt": "from the spot", "untilLag": -0.01},
           {"type": "ballpath", "world": True, "at": "from the spot", "lag": -0.01, "dur": 0.5, "slowmo": False, "points": [b0, mid(b0, end, 0.9), end]}]})
# 4 Konsa header, then White
c0 = [-14, 0.2, 44]; hd = [-1.2, 2.25, 46.5]; e2 = [2.8, 1.2, 52.3]; w0 = [3.22, 0.11, 40.45]; e3 = [-2.9, 0.4, 52.3]
B.append({"kicker": "53' · 57'", "headline": "Konsa. Then White. [0–3].", "cut": True, "scene": S_MAD, "accent": GOLD, "hype": False,
  "camFrom": {"pos": [6, 2.5, 39.5], "tgt": [-0.5, 1.5, 49.5]}, "camera": {"pos": [5, 2.2, 41.5], "tgt": [-0.5, 1.5, 49.5]}, "move": 4, "moveEase": "linear",
  "players": [E(skin="#8a5a3c", hair="#141010", x=-1.2, z=46.5, front=True, label="Ezri Konsa", labelAt="Ezri", hops=[{"at": "heads in", "lag": -0.3, "dur": 0.6, "height": 0.3}]),
              keeper(GKS, -1, "heads in", 0.05), S(skin="#e7b593", hair="#141010", x=0.6, z=47.4, front=True), S(skin="#f0c8a8", hair="#5a3a22", x=-3.4, z=48.2, front=True)],
  "card": [bug([0, 2], "53'", [0, 1], "heads in"),
           {"type": "ballpath", "world": True, "at": "heads in", "lag": -0.9, "dur": 0.9, "slowmo": False, "flash": False, "points": [c0, mid(c0, hd, 5.5), hd]},
           {"type": "ballpath", "world": True, "at": "heads in", "lag": 0.0, "dur": 0.4, "slowmo": False, "points": [hd, mid(hd, e2, 1.9), e2]}],
  "shake": [{"at": "heads in", "lag": 0.42, "amount": 12}],
  "shots": [{"at": "Four minutes", "lag": -0.1, "cut": True, "transition": "whip", "kicker": "57' · Bellingham → White", "follow": 0.5, "hype": True,
     "camFrom": {"pos": [6.8, 2.0, 33], "tgt": [0, 1.0, 52]}, "camera": {"pos": [6.2, 1.8, 35], "tgt": [0, 1.0, 52]}, "move": 4, "moveEase": "linear",
     "players": [E(skin="#f0c8a8", hair="#3a2a1a", x=3.0, z=40, label="Ben White", labelAt="Ben White", action="kick", actionAt="Three–nil", actionLag=-0.75, actionDur=0.8, after="celebrate"),
                 keeper(GKS, 1, "Three–nil", -0.3),
                 E(skin="#c99b7a", hair="#141010", x=-5, z=37.5, label="Bellingham", labelAt="Bellingham"),
                 S(skin="#e7b593", hair="#141010", x=4.9, z=43.2, front=True, action="dive", dir=-1, actionAt="Three–nil", actionLag=-0.6, actionDur=0.7), S(skin="#8a5a3c", hair="#141010", x=-1.8, z=47.5, front=True)],
     "card": [bug([0, 3], "57'", [0, 2], "Three–nil", 0.1),
              {"type": "ballpath", "world": True, "at": "Bellingham", "lag": 0.1, "dur": 0.7, "slowmo": False, "flash": False, "points": [[-4.6, 0.11, 37.9], [-0.8, 0.3, 39.4], w0]},
              {"type": "ball", "at": "Bellingham", "lag": 0.8, "point": w0, "untilAt": "Three–nil", "untilLag": -0.41},
              {"type": "ballpath", "world": True, "at": "Three–nil", "lag": -0.41, "dur": 0.5, "slowmo": False, "points": [w0, mid(w0, e3, 0.8), e3]}]}]})
# 5 the turn: Yamal runs through, Anderson brings him down
B.append({"kicker": "63' · the turn", "headline": "Then it [all changes].", "cut": True, "transition": "vhs", "vhsLabel": "63'", "vhsDur": 0.8, "scene": S_MAD, "accent": RED, "lights": 0.7, "hype": False,
  "camFrom": {"pos": [-4.5, 2.3, 25.5], "tgt": [1.6, 1.0, 36]}, "camera": {"pos": [-3.6, 1.9, 29.5], "tgt": [1.2, 1.0, 38]}, "move": 7, "moveEase": "linear",
  "players": [S(skin="#b98a66", hair="#141010", foot="left", dribble=True, x=2.2, z=32.6, path=[[2.2, 32.6], [1.2, 35.5], [0.4, 38.6]], pathDur=1.7, at="Lamine Yamal", lag=-0.2, label="Lamine Yamal", labelAt="Lamine Yamal",
                action="fall", actionAt="brings him down", actionLag=0.05),
              E(skin="#f0c8a8", hair="#6a4a2a", x=5.5, z=36, path=[[5.5, 36], [3.2, 37.8], [0.9, 38.9]], pathDur=1.3, at="Elliot Anderson", lag=0.1, label="Elliot Anderson", labelAt="Elliot Anderson",
                action="slide", dir=1, actionAt="brings him down", actionLag=-0.35, actionDur=1.1),
              E(skin="#8a5a3c", hair="#141010", x=3.4, z=32.2, front=True, label="Quansah", labelAt="Quansah", pose="think"),
              keeper(GKE, 1)],
  "card": [bug([0, 3], "63'"),
           {"type": "pen", "delay": 0, "anchor": 2, "strokes": [{"kind": "ellipse", "at": "loses the ball", "dur": 0.4, "cx": 0, "cy": 0, "rx": 0.6, "ry": 0.2, "color": RED, "width": 9, "layer": "under"}]},
           {"type": "flytext", "text": "FOUL", "size": 280, "endScale": 0.7, "y": 1600, "at": "brings him down", "lag": 0.25, "color": RED, "clear": False}],
  "shake": [{"at": "brings him down", "lag": 0.2, "amount": 18}], "punch": [{"at": "Lamine Yamal", "amount": 0.3, "dur": 5, "anchor": 0}], "freezeAt": "brings him down", "freezeLag": 0.75})
# 6 penalty + red
p0 = [-0.22, 0.11, 41.5]; pe = [-3.0, 0.4, 52.3]
B.append({"kicker": "63' · 65'", "headline": "Penalty [and] a red card.", "cut": True, "scene": S_MAD, "accent": RED, "lights": 0.75, "follow": 0.4,
  "camFrom": {"pos": [3.6, 2.0, 33.5], "tgt": [-0.5, 1.0, 52]}, "camera": {"pos": [3.0, 1.8, 35.5], "tgt": [-0.5, 1.0, 52]}, "move": 5, "moveEase": "linear",
  "players": [S(skin="#e7b593", hair="#3a2a1a", foot="left", x=0, z=41.0, label="Oyarzabal", labelAt="Oyarzabal", action="kick", actionAt="Oyarzabal scores", actionLag=0.15, actionDur=0.8, after="celebrate", runup=2.2),
              keeper(GKE, 1, "Oyarzabal scores", 0.55), E(skin="#f0c8a8", hair="#6a4a2a", x=-6.5, z=37, label="Anderson · off", labelAt="red card")],
  "card": [bug([1, 3], "65'", [0, 3], "Oyarzabal scores", 0.95, red="away"),
           {"type": "flytext", "text": "PENALTY", "size": 200, "endScale": 0.7, "y": 760, "delay": 0.05, "color": GOLD, "clear": False, "hideAt": "Oyarzabal", "hideLag": -0.1},
           {"type": "redcard", "at": "straight red", "lag": -0.3, "dx": -230, "y": 1500, "label": "63' Anderson", "hideAt": "Oyarzabal", "hideLag": 0.1},
           {"type": "ball", "delay": 0, "point": p0, "untilAt": "Oyarzabal scores", "untilLag": 0.49},
           {"type": "ballpath", "world": True, "at": "Oyarzabal scores", "lag": 0.49, "dur": 0.5, "slowmo": False, "points": [p0, mid(p0, pe, 0.8), pe]}]})
# 7 Tuchel: why both?
B.append({"kicker": "After the game", "headline": "Tuchel: why [both]?", "cut": True, "transition": "whip", "scene": {"type": "booth", "crowd": ["#c60b1e", "#ffc400", "#c60b1e", "#ffffff"], "screenLeft": ["ESP 2–3 ENG", "FT"], "screenRight": ["63'", "RED + PEN"]}, "accent": GOLD,
  "players": [P(outfit="suit", suitColor="#1c1f28", tie="#1c2c5b", skin="#e2b08c", hair="#5a4a3a", sx=0.5, scale=1, label="Thomas Tuchel", labelDelay=0.2)],
  "card": [{"type": "scales", "y": 1500, "at": "why it had", "lag": -0.2, "left": {"name": "Penalty", "value": 1, "color": GOLD, "text": "PEN"}, "right": {"name": "Red card", "value": 1.25, "color": "#d6283b", "text": "RED"}, "tilt": 0.15, "clear": False}]})
# 8 Williams 3-2, 23 shots
n0 = [-2.22, 0.11, 43.45]; ne = [2.9, 0.5, 52.3]
B.append({"kicker": "75' · Spain pour forward", "headline": "Williams. [2–3].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_MAD, "accent": RED, "follow": 0.5,
  "camFrom": {"pos": [-7, 2.0, 35], "tgt": [0, 1.0, 52]}, "camera": {"pos": [-6.2, 1.8, 37.5], "tgt": [0, 1.0, 52]}, "move": 4, "moveEase": "linear",
  "players": [S(skin="#6a4630", hair="#141010", x=-2.0, z=43, label="Nico Williams", labelAt="Nico", action="kick", actionAt="three–two", actionLag=-0.75, actionDur=0.8, after="celebrate"),
              keeper(GKE, -1, "three–two", -0.3),
              S(skin="#b98a66", hair="#141010", x=9, z=41, label="Yamal", labelAt="Nico"),
              E(skin="#e7b593", hair="#3a2a1a", x=-3.9, z=46, front=True, action="dive", dir=1, actionAt="three–two", actionLag=-0.6, actionDur=0.7), E(skin="#8a5a3c", hair="#141010", x=2.6, z=48, front=True)],
  "card": [bug([2, 3], "75'", [1, 3], "three–two", 0.1, red="away"),
           {"type": "ballpath", "world": True, "at": "Nico", "lag": -0.1, "dur": 0.8, "slowmo": False, "flash": False, "points": [[8.6, 0.11, 41.4], [3, 2.2, 43], n0]},
           {"type": "ball", "at": "Nico", "lag": 0.7, "point": n0, "untilAt": "three–two", "untilLag": -0.41},
           {"type": "ballpath", "world": True, "at": "three–two", "lag": -0.41, "dur": 0.5, "slowmo": False, "points": [n0, mid(n0, ne, 0.9), ne]}],
  "shots": [{"at": "Spain finish", "lag": -0.1, "cut": True, "kicker": "Spain's shots", "camFrom": {"pos": [0, 46, 22], "tgt": [0, 0, 46]}, "camera": {"pos": [0, 40, 26], "tgt": [0, 0, 46]}, "move": 4, "moveEase": "linear", "players": [], "lights": 0.7,
     "card": [bug([2, 3], "90'", red="away"),
              {"type": "shotmap", "delay": 0.1, "scale": 2.2, "step": 0.06, "color": "#ffc400", "shots": [{"x": x, "z": z} for x, z in [(-8, 36), (4, 34), (-2, 40), (9, 39), (-11, 43), (1, 44), (6, 45), (-5, 46), (12, 41), (-1, 37), (3, 47), (-7, 41), (8, 35), (0, 42), (-3, 33), (5, 40), (-9, 47), (10, 46), (2, 36), (-6, 38), (7, 43), (-12, 39), (0, 48)]]},
              {"type": "big", "at": "twenty-three", "lag": -0.3, "from": 0, "value": 23, "countDur": 0.8, "label": "Spain shots · England 9", "y": 1640, "size": 220, "clear": False}]}]})
# 9 Trafford saves
s0 = [-1.5, 0.11, 43.45]
B.append({"kicker": "James Trafford", "headline": "Trafford [keeps them out].", "cut": True, "transition": "whip", "scene": S_MAD, "accent": GREEN, "hype": False,
  "camFrom": {"pos": [4.4, 2.2, 37], "tgt": [0.2, 1.2, 52]}, "camera": {"pos": [3.2, 1.9, 41], "tgt": [0.2, 1.2, 52]}, "move": 3.6, "moveEase": "linear",
  "players": [S(skin="#e7b593", hair="#3a2a1a", x=-1.7, z=43, action="kick", actionDelay=0.3, actionDur=0.8),
              P(kit=GKE, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, label="James Trafford", labelDelay=0.2),
              E(skin="#8a5a3c", hair="#141010", x=1.6, z=46.5, front=True), E(skin="#f0c8a8", hair="#5a3a22", x=-3.2, z=47.2, front=True)],
  "card": [bug([2, 3], "90+'", red="away"),
           {"type": "ball", "delay": 0, "point": s0, "until": 0.64},
           {"type": "ballpath", "world": True, "delay": 0.64, "dur": 0.55, "slowmo": False, "saveBy": 1, "flash": False, "points": [s0, [0.4, 1.4, 48], [2.3, 1.3, 52.0]]}],
  "confetti": True, "confettiAt": "England win", "flashes": 16,
  "shake": [{"t": 1.2, "amount": 10}]})
B[-1]["card"] += [{"type": "stamp", "text": "ENGLAND WIN", "sub": "top of Group A3", "at": "England win", "lag": -0.1, "color": GOLD, "rot": -0.06, "size": 84, "y": 1680}]
B[-1]["players"][2]["after"] = "celebrate"; B[-1]["players"][3]["after"] = "celebrate"
# 10 the question
B.append({"kicker": "Your call", "headline": "Penalty and red: [fair or harsh]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_MAD, "accent": GOLD, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-8, 14, -28], "tgt": [0, 0, 8]}, "camera": {"pos": [8, 20, -36], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "redcard", "delay": 0.1, "dx": 250, "y": 1100},
           {"type": "flytext", "text": "PENALTY +", "size": 150, "endScale": 0.7, "y": 780, "shiftX": -170, "delay": 0.1, "color": GOLD, "clear": False},
           {"type": "poll", "y": 1620, "at": "Fair", "lag": -0.4, "question": "Penalty and a red card?", "options": [{"label": "Fair", "color": "#c60b1e", "fill": 0.5}, {"label": "Too harsh", "color": "#1c2c5b", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "Spain 2-3 England", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
