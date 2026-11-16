# Builds videos/ronaldo-146/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
POR = {"shirt": "#c8102e", "shorts": "#046a38", "socks": "#c8102e", "text": "#fdda24"}
ARG = {"shirt": "#75aadb", "shorts": "#111111", "socks": "#ffffff", "text": "#111111", "stripes": ["#75aadb", "#ffffff"]}
ENG = {"shirt": "#ffffff", "shorts": "#1c2c5b", "socks": "#ffffff", "text": "#1c2c5b"}
FRA = {"shirt": "#1c2c7a", "shorts": "#ffffff", "socks": "#c8102e", "text": "#ffffff"}
NOR = {"shirt": "#c8102e", "shorts": "#ffffff", "socks": "#1c2c7a", "text": "#ffffff"}
GK = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
S_POR = {"type": "stadium", "crowd": ["#c8102e", "#046a38", "#c8102e", "#fdda24"], "seed": 8}
S_ARG = {"type": "stadium", "crowd": ["#75aadb", "#ffffff", "#75aadb", "#fdda24"], "seed": 12}
S_ENG = {"type": "stadium", "crowd": ["#ffffff", "#c8102e", "#ffffff", "#1c2c5b"], "seed": 3}
S_FRA = {"type": "stadium", "crowd": ["#1c2c7a", "#ffffff", "#c8102e", "#1c2c7a"], "seed": 17}
S_NOR = {"type": "stadium", "crowd": ["#c8102e", "#ffffff", "#1c2c7a", "#c8102e"], "seed": 29}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
V = 'videos/ronaldo-146/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
ROW = [dict(name="Messi", value=126, done=True, note="retired"), dict(name="Kane", value=93, color="#ffffff", note="53 short"),
       dict(name="Mbappé", value=67, color="#3b5bdb", note="79 short"), dict(name="Haaland", value=66, color="#c8102e", note="80 short")]
def ladder(states, **k):
    items = []
    for i, r in enumerate(ROW):
        it = dict(r); it.update(states.get(i, {"t": 99})); items.append(it)
    d = {"type": "ladder", "max": 146, "maxLabel": "Ronaldo · 146", "items": items, "h": 820, "clear": False}; d.update(k); return d
NOW = {"t": 0, "dur": 0.01}
CLOSE = lambda x=0: dict(camFrom={"pos": [x + 1.2, 1.6, -2.6], "tgt": [x, 1.3, 10]}, camera={"pos": [x + 0.3, 1.5, -0.8], "tgt": [x, 1.3, 10]}, move=6, moveEase="linear")
B = []
# 1 hook: counter races to 146 and locks, UNBREAKABLE
B.append({"kicker": "International goals · the record", "headline": "Nobody is catching [Ronaldo's 146].", "hookWords": True, "scene": S_POR, "accent": GOLD, "lights": 0.85, "flashes": 18,
  "camFrom": {"pos": [0.9, 1.5, 0.3], "tgt": [0.9, 1.35, 10]}, "camera": {"pos": [0.9, 1.5, -0.9], "tgt": [0.9, 1.35, 10]}, "move": 8, "moveEase": "linear",
  "players": [P(kit=POR, num=7, skin="#c99b7a", hair="#141010", x=1.7, z=3.5, front=True, chest=True, action="celebrate", label="Ronaldo", labelDelay=0)],
  "card": [{"type": "big", "delay": -0.6, "from": 0, "value": 146, "countDur": 2.4, "label": "International goals", "y": 1250, "shiftX": -210, "size": 290, "clear": False},
           {"type": "stamp", "text": "UNBREAKABLE?", "sub": "nobody is close", "at": "Nobody playing", "lag": 0, "color": GOLD, "rot": -0.07, "size": 84, "y": 1740}],
  "shake": [{"t": 1.85, "amount": 14}, {"at": "Nobody playing", "lag": 0.16, "amount": 12}]})
# 2 retired: 23 years, 234 games
B.append({"kicker": "5 November 2026", "headline": "Ronaldo [retires] from Portugal.", "cut": True, "transition": "whip", "scene": S_POR, "accent": GOLD, "lights": 0.55, "focus": 0.3,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 16, -30], "tgt": [0, 0, 10]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 680, "delay": 0.1, "label": "Retired from Portugal", "groups": [{"label": "November", "value": 5, "digits": 2}], "side": {"top": "THU", "big": "05", "bottom": "NOV"}},
           {"type": "stack", "y": 1400, "delay": 0, "size": 190, "items": [{"value": 23, "label": "Years", "at": "Twenty-three"}, {"value": 234, "label": "Games for Portugal", "at": "Two hundred"}, {"value": 146, "label": "Goals", "t": 99}]}]})
# 3 Messi 126, stopped too
B.append({"kicker": "Second all-time", "headline": "Messi: [126]. Also done.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ARG, "accent": GOLD, "lights": 0.6, **CLOSE(-1.0),
  "players": [P(kit=ARG, num=10, skin="#e8b896", hair="#4a3020", x=-1.6, z=2.9, front=True, ghost=True, label="Lionel Messi", labelAt="Lionel")],
  "card": [ladder({0: {"at": "Lionel Messi", "lag": 0.1}}, y=1180, shiftX=150, w=640, h=760, items=None)]})
B[-1]["card"][0]["items"] = [dict(ROW[0], at="Lionel Messi", lag=0.1)]
# 4 Kane 93
k0 = [-1.78, 0.11, 41.45]; ke = [2.9, 0.6, 52.3]
B.append({"kicker": "England", "headline": "Kane: [93]. Needs 53 more.", "cut": True, "transition": "whip", "scene": S_ENG, "accent": RED, "follow": 0.5,
  "camFrom": {"pos": [-6.4, 2.0, 34], "tgt": [0, 1.0, 52]}, "camera": {"pos": [-5.6, 1.8, 36.4], "tgt": [0, 1.0, 52]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=ENG, skin="#f0c8a8", hair="#b8905a", x=-2.0, z=41, label="Harry Kane · 33", labelAt="Harry Kane", action="kick", actionAt="ninety-three", actionLag=-0.6, actionDur=0.8, after="celebrate"),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="ninety-three", actionLag=-0.15),
              P(kit=FRA, skin="#e7b593", hair="#141010", x=-3.9, z=44.4, front=True, action="dive", dir=1, actionAt="ninety-three", actionLag=-0.45, actionDur=0.7), P(kit=FRA, skin="#8a5a3c", hair="#141010", x=2.4, z=47.6, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": k0, "untilAt": "ninety-three", "untilLag": -0.26},
           {"type": "ballpath", "world": True, "at": "ninety-three", "lag": -0.26, "dur": 0.5, "slowmo": False, "points": [k0, mid(k0, ke, 0.9), ke]},
           {"type": "stack", "y": 1680, "shiftX": -200, "delay": 0, "size": 170, "items": [{"value": 93, "label": "Goals for England", "at": "ninety-three", "lag": 0.2}, {"value": 53, "label": "Still needed", "at": "fifty-three", "color": RED}, {"value": 33, "label": "His age", "at": "thirty-three", "color": RED}]}]})
# 5 Mbappé 67
B.append({"kicker": "France", "headline": "Mbappé: [67]. Not halfway.", "cut": True, "scene": S_FRA, "accent": RED, "lights": 0.55, "focus": 0.3,
  "camFrom": {"pos": [-12, 22, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [10, 12, -24], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [ladder({0: NOW, 1: NOW, 2: {"at": "sixty-seven", "lag": -0.5}}, y=1050)],
  "punch": [{"at": "halfway", "amount": 0.1, "dur": 1.2, "x": 640, "y": 1050}]})
# 6 Haaland 66, a goal a game
h0 = [1.22, 0.11, 42.45]; he = [-2.9, 1.0, 52.3]
B.append({"kicker": "Norway", "headline": "Haaland: [66]. A goal a game.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_NOR, "accent": GOLD, "follow": 0.5,
  "camFrom": {"pos": [5.6, 2.0, 35], "tgt": [0, 1.0, 52]}, "camera": {"pos": [5.0, 1.8, 37.4], "tgt": [0, 1.0, 52]}, "move": 4, "moveEase": "linear",
  "players": [P(kit=NOR, skin="#f0c8a8", hair="#e8d28a", foot="left", x=1.0, z=42, label="Erling Haaland · 26", labelDelay=0.2, action="kick", actionAt="sixty-six", actionLag=-0.6, actionDur=0.8, after="celebrate"),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="sixty-six", actionLag=-0.15),
              P(kit=ENG, skin="#e7b593", hair="#141010", x=3.0, z=45.2, front=True, action="dive", dir=-1, actionAt="sixty-six", actionLag=-0.45, actionDur=0.7), P(kit=ENG, skin="#8a5a3c", hair="#141010", x=-2.4, z=48, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": h0, "untilAt": "sixty-six", "untilLag": -0.26},
           {"type": "ballpath", "world": True, "at": "sixty-six", "lag": -0.26, "dur": 0.5, "slowmo": False, "points": [h0, mid(h0, he, 1.0), he]},
           {"type": "big", "at": "sixty-six", "lag": 0.2, "from": 0, "value": 66, "countDur": 0.7, "label": "Goals for Norway · more than one a game", "y": 1620, "size": 230, "clear": False}]})
# 7 re-hook: even then, 80 more, ~8 years
B.append({"kicker": "The maths", "headline": "[80] more goals. About 8 years.", "cut": True, "transition": "vhs", "vhsLabel": "BUT", "vhsDur": 0.8, "scene": S_DARK, "accent": RED, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [12, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [-12, 22, -40], "tgt": [0, 0, 5]}, "move": 7, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [ladder({0: NOW, 1: NOW, 2: NOW, 3: {"at": "eighty more", "lag": -0.6}}, y=930, h=760),
           {"type": "crossoff", "y": 1600, "at": "around eight", "lag": -0.5, "title": "Years of internationals", "days": 8, "cols": 8, "cell": 96, "crossT": 0.3, "dur": 1.2, "caption": "about {n} years · an estimate", "clear": False}]})
# 8 six World Cups
B.append({"kicker": "Only Ronaldo", "headline": "Scored at [six] World Cups.", "cut": True, "transition": "whip", "scene": S_POR, "accent": GOLD, "lights": 0.6, "focus": 0.25,
  "camFrom": {"pos": [0, 20, -36], "tgt": [0, 2, 6]}, "camera": {"pos": [0, 9, -20], "tgt": [0, 2, 8]}, "move": 6, "moveEase": "linear", "players": [], "flashes": 14,
  "card": [{"type": "tally", "at": "six different", "lag": -0.5, "y": 880, "r": 62, "gap": 18, "perRow": 6, "title": "World Cups Ronaldo scored at", "mark": "check", "n": 6, "done": 0,
            "items": [{"label": y, "t": 0.15 + i * 0.2} for i, y in enumerate(["2006", "2010", "2014", "2018", "2022", "2026"])], "score": "{w} World Cups", "clear": False},
           {"type": "trophies", "at": "Nobody else", "lag": -0.3, "floor": 1760, "stagger": 0, "rise": 0.55, "items": [{"kind": "boot", "sx": 0.5, "h": 160, "size": 300, "label": "First to score at six"}], "clear": False}]})
# 9 the question
B.append({"kicker": "Your call", "headline": "Will anyone catch [146]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_POR, "accent": GOLD, "flashes": 12,
  "orbit": {"center": [0, 1.25, 3], "r": 5.4, "from": -28, "to": 16, "h": 1.5, "h2": 1.9, "dur": 7}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [P(kit=ENG, skin="#f0c8a8", hair="#b8905a", x=-1.7, z=3.3, front=True, label="Kane", labelAt="Kane"), P(kit=FRA, skin="#8a5a3c", hair="#141010", x=0, z=3.6, front=True, label="Mbappé", labelAt="Mbappé"),
              P(kit=NOR, skin="#f0c8a8", hair="#e8d28a", x=1.7, z=3.3, front=True, label="Haaland", labelAt="Haaland")],
  "card": [{"type": "poll", "y": 1560, "at": "Kane", "lag": -0.4, "question": "Who catches Ronaldo's 146?", "options": [{"label": "Kane", "color": "#1c2c5b", "fill": 0.3}, {"label": "Mbappé", "color": "#3b5bdb", "fill": 0.3}, {"label": "Haaland", "color": "#c8102e", "fill": 0.3}, {"label": "Nobody", "color": "#b8892a", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 9
json.dump({"title": "Nobody is catching Ronaldo's 146", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
