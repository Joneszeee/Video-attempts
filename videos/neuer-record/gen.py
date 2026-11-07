import json
ACC = "#e8384f"
BAY = {"shirt": "#f4f4f2", "shorts": "#f4f4f2", "socks": "#f4f4f2", "text": "#c8102e"}
GK = {"shirt": "#2b3242", "shorts": "#2b3242", "socks": "#2b3242", "text": "#ffffff"}
MAI = {"shirt": "#c3002f", "shorts": "#ffffff", "socks": "#c3002f", "text": "#ffffff"}
MGK = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
SC = {"type": "stadium", "crowd": ["#c3002f", "#ffffff", "#c3002f", "#1d1c22"], "seed": 27}
lines = [l.strip() for l in open('/home/user/Video-attempts/videos/neuer-record/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
NEUER = dict(kit=GK, skin="#f0c8a8", hair="#b8925f", gloves="#ffffff")
URBIG = dict(kit=GK, skin="#f2cbb0", hair="#8a6a45", gloves="#ffffff")
def bp(at, lag, pts, dur=0.5, **k):
    d = {"type": "ballpath", "world": True, "at": at, "lag": lag, "dur": dur, "slowmo": False, "points": pts}; d.update(k); return d
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
B = []
# 1 hook
B.append({"kicker": "Bundesliga · Mainz v Bayern", "headline": "Neuer's record day went [wrong].", "hookWords": True, "scene": SC,
  "camFrom": {"pos": [0, 0.7, -1.6], "tgt": [0, 1.6, 12]}, "camera": {"pos": [0, 0.6, -2.8], "tgt": [0, 1.5, 12]}, "move": 3.5,
  "lights": 0.9, "flashes": 10, "speedlines": [{"t": 0, "dur": 1.0, "amount": 0.6}],
  "players": [P(**NEUER, x=0, z=1.6, front=True, pose="keeper", enter="walk", fromZ=3.8, walkDur=1.8, label="Manuel Neuer", labelDelay=0)],
  "card": [{"type": "flip", "y": 1530, "delay": -2.6, "label": "Age today", "groups": [{"label": "Years", "value": 40, "digits": 2}, {"label": "Days", "value": 225, "digits": 3}], "hideAt": "Forty minutes"},
           {"type": "stamp", "text": "RECORD", "sub": "Bayern's oldest", "at": "record", "color": "#e9b949", "rot": -0.12, "y": 1250, "hideAt": "Forty minutes"},
           {"type": "stamp", "text": "INJURED", "sub": "40'", "at": "limping", "color": ACC, "rot": 0.1, "y": 1420}],
  "freezeAt": "Forty minutes", "freezeLag": -0.1, "shake": [{"at": "record", "amount": 12}]})
# 2 date + Neuer in goal
B.append({"kicker": "Saturday · Mewa Arena", "headline": "7 November 2026. Neuer [starts].", "cut": True, "scene": SC,
  "camFrom": {"pos": [0, 40, -70], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 22, -40], "tgt": [0, 0, 10]}, "move": 3, "players": [],
  "card": [{"type": "flip", "y": 700, "at": "seventh", "label": "Mainz v Bayern", "groups": [{"label": "November", "value": 7, "digits": 2}], "side": {"top": "SAT", "big": "7", "bottom": "NOV"}, "hideAt": "Neuer starts"}],
  "shots": [{"at": "Neuer starts", "cut": True, "move": 3.5, "camFrom": {"pos": [0, 1.7, 44], "tgt": [0, 1.3, 52]}, "camera": {"pos": [0, 1.6, 46.8], "tgt": [0, 1.3, 52]},
     "players": [P(**NEUER, x=0, z=51.6, front=True, chest=True, pose="keeper", label="Neuer · 40 years, 225 days", labelAt="aged")]}]})
# 3 record ruler
B.append({"kicker": "The record", "headline": "Bayern's [oldest ever] in the Bundesliga.", "cut": True, "scene": SC,
  "camFrom": {"pos": [0, 1.5, -1.0], "tgt": [0, 1.2, 8]}, "camera": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.2, 8]}, "move": 4.5, "lights": 0.8, "flashes": 8,
  "players": [P(**NEUER, x=1.3, z=2.6, front=True, pose="fists", mood="joy", label="Neuer · 2026", labelAt="oldest"),
              P(kit={"shirt": "#5b6b4a", "shorts": "#1d1c22", "socks": "#5b6b4a", "text": "#ffffff"}, skin="#f0c8a8", hair="#6a5038", x=-1.3, z=3.2, front=True, pose="keeper", ghost=True, label="Dreher · 2007", labelAt="Dreher", at="Dreher", enter="fade")],
  "card": [{"type": "big", "y": 1560, "at": "oldest", "value": 225, "prefix": "40y ", "suffix": "d", "size": 150, "label": "Bayern's oldest Bundesliga player", "hideAt": "Dreher", "hideLag": -0.3},
           {"type": "tape", "y": 1600, "at": "Dreher", "lag": -0.3, "left": {"name": "Neuer · 2026", "color": "#e9b949"}, "right": {"name": "Dreher · 2007", "color": "#8a96a8"},
            "rows": [{"label": "Days past his 40th birthday", "left": 225, "right": 198, "t": 0.3, "floor": 150}]}]})
# 4 Kimmich goal
kim = [0.6, 0.11, 31.5]; kend = [2.9, 2.1, 52.8]
B.append({"kicker": "14 minutes", "headline": "Kane finds [Kimmich].", "cut": True, "scene": SC,
  "camFrom": {"pos": [-1.5, 4.2, 18.5], "tgt": [0.0, 0.8, 44]}, "camera": {"pos": [-1.0, 3.5, 21.5], "tgt": [0.3, 0.8, 45]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=BAY, skin="#f0c8a8", hair="#a07850", x=-5, z=36, label="Kane", labelAt="Kane", action="kick", actionAt="Kane", actionLag=-0.1, actionDur=0.8),
              P(kit=BAY, skin="#f0c8a8", hair="#4a3324", x=0.35, z=31.0, label="Kimmich", labelAt="Kimmich", action="kick", actionAt="Kimmich", actionLag=0.15, actionDur=0.8, after="celebrate"),
              P(kit=MAI, skin="#d9a37c", hair="#1d1410", x=2.6, z=36, front=True),
              P(kit=MGK, skin="#f0c8a8", hair="#5a3a20", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="Kimmich", actionLag=0.55)],
  "card": [{"type": "ball", "delay": 0, "point": [-4.72, 0.11, 36.45], "untilAt": "Kane", "untilLag": 0.24},
           bp("Kane", 0.24, [[-4.72, 0.11, 36.45], [-3.0, 0.3, 33.6], kim], 0.55),
           {"type": "ball", "at": "Kane", "lag": 0.79, "point": kim, "untilAt": "Kimmich", "untilLag": 0.49},
           bp("Kimmich", 0.49, [kim, mid(kim, kend, 3.4), kend], 0.75),
           {"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 0, "to": 14, "dur": 1.2, "events": [{"min": 14, "text": "14' Kimmich · 0–1"}]}],
  "punch": [{"at": "Kimmich", "lag": 0.6, "amount": 0.2, "dur": 1.2, "anchor": 1}]})
# 5 free kick
fk = [-15, 0.11, 34]; tah = [-1.2, 2.3, 46.2]
B.append({"kicker": "40 minutes", "headline": "Amiri. Free kick. Tah [flicks it].", "cut": True, "scene": SC, "lights": 0.7,
  "camFrom": {"pos": [-24, 8.0, 22], "tgt": [-2, 0.6, 46]}, "camera": {"pos": [-21, 6.5, 26], "tgt": [-1.5, 0.8, 47.5]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=MAI, skin="#c99a6e", hair="#1d1410", x=-15.4, z=33.4, label="Amiri", labelAt="Amiri", action="kick", actionAt="swings", actionLag=-0.1, actionDur=0.8, foot="left"),
              P(kit=BAY, skin="#6b4630", hair="#141010", x=-1.2, z=46.0, label="Tah", labelAt="Tah", hops=[{"at": "flicks", "lag": -0.25, "dur": 0.5, "height": 0.35}]),
              P(kit=MAI, skin="#e8c39e", hair="#141010", x=3.6, z=48.6, label="Lee", labelAt="Tah"),
              P(kit=BAY, skin="#f0c8a8", hair="#3a2a1a", x=2.4, z=47.8), P(kit=MAI, skin="#f0c8a8", hair="#7a5a3a", x=-3.0, z=47.0), P(kit=BAY, skin="#d9a37c", hair="#141010", x=-4.0, z=45.6),
              P(**NEUER, x=0.4, z=51.6, front=True, pose="keeper")],
  "card": [{"type": "ball", "delay": 0, "point": fk, "untilAt": "swings", "untilLag": 0.24},
           bp("swings", 0.24, [fk, [-8, 6.5, 44], tah], 1.1),
           bp("flicks", 0.0, [tah, [1.5, 3.2, 48.5], [3.6, 0.6, 49.6]], 0.9, flash=False),
           {"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 14, "to": 40, "dur": 1.2, "events": [{"min": 40, "text": "40' free kick"}]}]})
# 6 the miss (slow-mo)
B.append({"kicker": "The flap", "headline": "Missed it [by a mile].", "accent": ACC, "cut": True, "scene": SC, "lights": 0.8,
  "camFrom": {"pos": [-6.5, 1.9, 43.5], "tgt": [1.5, 1.5, 50]}, "camera": {"pos": [-5.5, 1.8, 45], "tgt": [1.7, 1.5, 50]}, "move": 4, "moveEase": "linear",
  "players": [P(**NEUER, x=0.4, z=51.6, front=True, pose="keeper", path=[[0.4, 51.6], [1.0, 48.9]], pathDur=0.8, at="flying", action="dive", dir=1, actionAt="flying", actionLag=0.55, actionDur=0.9),
              P(kit=MAI, skin="#e8c39e", hair="#141010", x=3.6, z=49.8, front=True)],
  "card": [bp("flying", 0.5, [[-1.2, 2.3, 46.2], [1.0, 4.2, 48.0], [3.1, 0.5, 49.2]], 1.5, flash=False, slowmo=True),
           {"type": "pen", "delay": 0, "strokes": [{"kind": "text", "text": "A MILE", "x": 560, "y": 860, "size": 80, "rot": -6, "at": "mile", "color": ACC}]}],
  "punch": [{"at": "misses", "amount": 0.18, "dur": 1.4, "anchor": 0}]})
# 7 Lee scores
lee = [3.4, 0.2, 49.75]; lend = [2.4, 0.3, 52.8]
B.append({"kicker": "40 minutes", "headline": "Lee scores. [1–1]?", "cut": True, "scene": SC,
  "camFrom": {"pos": [5.5, 1.8, 40.5], "tgt": [1.5, 1.0, 51]}, "camera": {"pos": [4.6, 1.7, 42.5], "tgt": [1.6, 1.0, 51]}, "move": 4,
  "players": [P(kit=MAI, skin="#e8c39e", hair="#141010", x=3.6, z=49.4, label="Lee Jae-sung", labelAt="Lee", action="kick", actionAt="scores", actionLag=-0.45, actionDur=0.7, after="celebrate"),
              P(**NEUER, x=0.9, z=49.2, front=True, pose="hurt", mood="cross"),
              P(kit=MAI, skin="#f0c8a8", hair="#7a5a3a", x=-2.0, z=47.0, front=True, action="celebrate", actionAt="level")],
  "card": [{"type": "ball", "delay": 0, "point": lee, "untilAt": "scores", "untilLag": -0.15},
           bp("scores", -0.15, [lee, mid(lee, lend, 0.5), lend], 0.35),
           {"type": "claynum", "text": "1–1", "size": 220, "y": 1600, "at": "level", "color": "#ffffff", "label": "40' · Lee", "labelDy": 80, "clear": False}]})
# 8 injury + Urbig
B.append({"kicker": "Injury", "headline": "Neuer [can't go on].", "accent": ACC, "cut": True, "scene": SC, "lights": 0.6,
  "camFrom": {"pos": [2.0, 1.4, 45.5], "tgt": [0.9, 0.5, 49.2]}, "camera": {"pos": [1.6, 1.2, 46.5], "tgt": [0.9, 0.5, 49.2]}, "move": 3.5,
  "players": [P(**NEUER, x=0.9, z=49.2, front=True, pose="hurt", mood="cross", label="Right foot", labelAt="right foot")],
  "card": [{"type": "pen", "delay": 0, "anchor": 0, "strokes": [{"kind": "ellipse", "cx": 0.12, "cy": -0.05, "rx": 0.32, "ry": 0.12, "at": "right foot", "color": ACC, "layer": "under"}], "hideAt": "On comes", "hideLag": -0.1}],
  "shots": [{"at": "On comes", "lag": -0.1, "cut": True, "lights": 0.9, "move": 3, "camFrom": {"pos": [-1, 1.6, -3.5], "tgt": [0, 1.2, 6]}, "camera": {"pos": [-0.6, 1.5, -2.4], "tgt": [0, 1.2, 6]},
     "players": [P(**URBIG, x=0, z=2.2, front=True, enter="walk", fromX=-6, fromZ=2.2, walkDur=1.4, label="Jonas Urbig", labelAt="Urbig", pose="keeper")]}]})
# 9 VAR
B.append({"kicker": "VAR check", "headline": "Lee was [offside].", "accent": "#3fa0ff", "cut": True, "scene": SC,
  "camFrom": {"pos": [-11, 5.5, 44.5], "tgt": [2.5, 0.6, 49.4]}, "camera": {"pos": [-8.5, 4.2, 45.5], "tgt": [2.5, 0.6, 49.4]}, "move": 5, "moveEase": "linear", "lights": 0.85,
  "players": [P(kit=MAI, skin="#e8c39e", hair="#141010", x=4.6, z=49.5, label="Lee", labelAt="offside"),
              P(kit=BAY, skin="#f0c8a8", hair="#3a2a1a", x=-0.6, z=48.9, label="Last defender", labelAt="VAR"),
              P(kit=MAI, skin="#f0c8a8", hair="#7a5a3a", x=-3.0, z=46.5), P(kit=BAY, skin="#6b4630", hair="#141010", x=-1.2, z=46.0),
              ],
  "card": [{"type": "varlines", "at": "VAR", "def": 48.9, "att": 49.5, "x0": -20, "x1": 30, "dur": 0.7, "y": 640, "clear": False},
           {"type": "stamp", "text": "NO GOAL", "sub": "HT · 0–1", "at": "No goal", "color": "#3fa0ff", "rot": -0.1, "y": 1660}]})
# 10 Karl, Tietz, 2-1
kar = [-1.0, 0.11, 40.5]; karend = [-2.9, 0.5, 52.8]
B.append({"kicker": "Second half", "headline": "Bayern win [2–1].", "cut": True, "scene": SC,
  "camFrom": {"pos": [2.8, 2.0, 32.5], "tgt": [-0.8, 1.0, 51]}, "camera": {"pos": [2.0, 1.9, 35.0], "tgt": [-0.8, 1.0, 51]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=BAY, skin="#e2b08c", hair="#1d1410", x=-1.25, z=40.0, label="Karl", labelAt="Karl", action="kick", actionAt="Karl", actionLag=-0.1, actionDur=0.8, after="celebrate"),
              P(kit=MGK, skin="#f0c8a8", hair="#5a3a20", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="Karl", actionLag=0.4)],
  "card": [{"type": "ball", "delay": 0, "point": kar, "untilAt": "Karl", "untilLag": 0.24},
           bp("Karl", 0.24, [kar, mid(kar, karend, 1.0), karend], 0.5),
           {"type": "clock", "y": 700, "scale": 0.75, "delay": 0, "from": 45, "to": 93, "dur": 3.2, "events": [{"min": 57, "text": "57' Karl · 0–2"}, {"min": 93, "text": "90+3' Tietz · 1–2"}]},
           {"type": "claynum", "text": "1–2", "size": 230, "y": 1650, "at": "Bayern win", "color": ACC, "label": "Mainz v Bayern", "labelDy": 84, "clear": False}]})
# 11 face-off + poll
B.append({"kicker": "Your call", "headline": "Neuer or [Urbig]?", "cut": True, "scene": SC, "lights": 0.7,
  "orbit": {"center": [0, 1.2, 3], "r": 5, "from": -25, "to": 20, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.2, 3]}, "flashes": 8,
  "players": [P(**NEUER, x=-1.3, z=3.2, front=True, pose="keeper", label="Neuer · 40", labelDelay=0),
              P(**URBIG, x=1.3, z=3.2, front=True, pose="keeper", label="Urbig", labelAt="Urbig")],
  "card": [{"type": "toyresults", "y": 1640, "delay": 0, "hideAt": "So is it", "items": [{"score": "✓", "team": "record", "win": True, "at": "record"}, {"score": "✗", "team": "howler", "win": False, "at": "howler"}, {"score": "+", "team": "injury", "win": False, "at": "injury"}]},
           {"type": "poll", "y": 1560, "at": "So is it", "question": "Who starts next?", "options": [{"label": "Urbig, for good", "color": ACC, "fill": 0.5}, {"label": "Neuer, always", "color": "#9aa1ad", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v; b.setdefault("accent", ACC)
assert len(B) == len(lines) == 11
spec = {"title": "Neuer's record day", "brand": "theo6k", "accent": ACC, "style": "hybrid", "voSpeed": 1.08, "beats": B}
json.dump(spec, open('/home/user/Video-attempts/videos/neuer-record/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
