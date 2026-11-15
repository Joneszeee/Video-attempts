# Builds videos/fastest-sackings/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
FOR = {"shirt": "#dd0000", "shorts": "#ffffff", "socks": "#dd0000", "text": "#ffffff"}
CHE = {"shirt": "#034694", "shorts": "#034694", "socks": "#ffffff", "text": "#ffffff"}
GK = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
S_FOR = {"type": "stadium", "crowd": ["#dd0000", "#ffffff", "#dd0000", "#8a0000"], "seed": 9}
S_CRY = {"type": "stadium", "crowd": ["#1b458f", "#c4122e", "#1b458f", "#ffffff"], "seed": 15}
S_FUL = {"type": "stadium", "crowd": ["#ffffff", "#111111", "#ffffff", "#cc0000"], "seed": 23}
S_CHA = {"type": "stadium", "crowd": ["#d4021d", "#ffffff", "#d4021d", "#111111"], "seed": 31}
S_LEE = {"type": "stadium", "crowd": ["#ffffff", "#1d428a", "#ffcd00", "#ffffff"], "seed": 40}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
V = 'videos/fastest-sackings/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def boss(tie, skin="#e2b08c", hair="#8a8a8e", **k): return P(outfit="suit", suitColor="#1c1f28", tie=tie, skin=skin, hair=hair, front=True, **k)
BG = {"LEE": {"colors": ["#ffffff", "#1d428a", "#ffcd00"], "text": "LUFC"}}
def rank(n, name, sub, at="Number", **k):
    d = {"type": "rank", "n": n, "name": name, "sub": sub, "y": 560, "at": at, "lag": -0.15, "clear": False}; d.update(k); return d
CLOSE = lambda x=0: dict(camFrom={"pos": [x + 1.2, 1.6, -2.6], "tgt": [x, 1.3, 10]}, camera={"pos": [x + 0.3, 1.5, -0.8], "tgt": [x, 1.3, 10]}, move=6, moveEase="linear")
B = []
# 1 hook: stopwatch races to 20 and locks, SACKED stamp
B.append({"kicker": "Premier League · shortest reigns", "headline": "Sacked in [under 20 minutes].", "hookWords": True, "scene": S_FOR, "accent": RED, "lights": 0.7, "flashes": 12,
  "camFrom": {"pos": [-1.4, 1.5, 0.3], "tgt": [-0.9, 1.35, 10]}, "camera": {"pos": [-1.1, 1.5, -0.9], "tgt": [-0.9, 1.35, 10]}, "move": 8, "moveEase": "linear",
  "players": [boss("#7a1420", x=-1.9, z=3.4, enter="walk", fromZ=4.8, walkDur=2.4, label="Ange Postecoglou", labelDelay=0)],
  "card": [{"type": "stopwatch", "y": 1330, "shiftX": 200, "delay": -0.25, "value": 20, "max": 60, "unit": "MIN", "prefix": "<", "lockAt": "twenty minutes", "lockLag": 0.3, "label": "After the final whistle", "r": 210, "clear": False},
           {"type": "stamp", "text": "SACKED", "sub": "39 days", "at": "final whistle", "lag": 0.2, "color": RED, "rot": -0.09, "size": 110, "dx": 200, "y": 1750},
           {"type": "flytext", "text": "NOT THE SHORTEST", "size": 120, "endScale": 0.8, "y": 700, "at": "isn't even", "color": GOLD, "clear": False}],
  "shake": [{"at": "twenty minutes", "lag": 0.35, "amount": 16}, {"at": "final whistle", "lag": 0.36, "amount": 12}]})
# 2 de Boer
B.append({"kicker": "Crystal Palace · 2017", "headline": "77 days. [Zero goals].", "cut": True, "transition": "whip", "scene": S_CRY, "accent": RED, "lights": 0.75, **CLOSE(0.9),
  "players": [boss("#1b458f", hair="#c9b28a", x=1.5, z=2.9, pose="think", label="Frank de Boer", labelAt="Frank")],
  "card": [rank(5, "Frank de Boer", "Crystal Palace"),
           {"type": "stack", "y": 1300, "shiftX": -240, "delay": 0, "size": 150, "items": [{"value": 77, "label": "Days", "at": "Seventy-seven"}, {"value": 4, "label": "League games", "at": "Four league"}, {"value": 0, "label": "Points", "at": "Zero points", "color": RED}, {"value": 0, "label": "Goals", "at": "Zero goals", "color": RED}]}],
  "shake": [{"at": "Zero goals", "lag": 0.2, "amount": 12}]})
# 3 Meulensteen: calendar
B.append({"kicker": "Fulham · 2013/14", "headline": "[75] days.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_FUL, "accent": RED, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [-12, 14, -28], "tgt": [0, 0, 8]}, "camera": {"pos": [10, 20, -36], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [rank(4, "René Meulensteen", "Fulham"),
           {"type": "crossoff", "y": 1230, "delay": 0.35, "title": "Fulham · days in charge", "days": 75, "cols": 15, "cell": 60, "crossAt": "Seventy-five", "crossLag": -0.5, "dur": 1.3, "caption": "{n} days", "clear": False}]})
# 4 Les Reed: polaroid flashback
B.append({"kicker": "Charlton · 2006", "headline": "[40] days.", "cut": True, "transition": "polaroid", "polaroidLabel": "Charlton 2006", "scene": S_CHA, "accent": RED, "lights": 0.7, **CLOSE(-0.9),
  "players": [boss("#d4021d", hair="#6a6a6e", x=-1.5, z=2.9, label="Les Reed", labelAt="Les Reed")],
  "card": [rank(3, "Les Reed", "Charlton"),
           {"type": "big", "at": "Forty", "lag": -0.35, "from": 0, "value": 40, "countDur": 0.7, "label": "Days in charge", "y": 1350, "shiftX": 240, "size": 250, "style": "accent", "clear": False}]})
# 5 Postecoglou: 39 days, 8 games, no wins
B.append({"kicker": "Nottingham Forest · 2025", "headline": "39 days. [No wins].", "cut": True, "transition": "whip", "scene": S_FOR, "accent": RED, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [0, 28, -48], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 13, -26], "tgt": [0, 0, 8]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [rank(2, "Ange Postecoglou", "Nottingham Forest"),
           {"type": "big", "at": "Thirty-nine", "lag": -0.35, "from": 0, "value": 39, "countDur": 0.7, "label": "Days in charge", "y": 980, "size": 250, "style": "accent", "clear": False},
           {"type": "dots", "states": ["miss"] * 8, "label": "8 games · all competitions", "caption": "0 wins", "y": 1480, "step": 0.16, "at": "Eight games", "lag": -0.3, "clear": False}],
  "shake": [{"at": "No wins", "lag": 0.15, "amount": 12}], "punch": [{"t": 0.1, "amount": 0.14, "dur": 2.4, "x": 540, "y": 700}], "flashes": 12})
# 6 Chelsea 3-0: a goal, then the stopwatch
b0 = [1.42, 0.11, 39.45]; end = [-2.6, 0.9, 52.3]
B.append({"kicker": "18 October 2025", "headline": "Forest 0–3 Chelsea. [Gone].", "cut": True, "scene": S_FOR, "accent": RED, "follow": 0.5,
  "camFrom": {"pos": [4.6, 2.0, 32.5], "tgt": [0.3, 1.0, 52]}, "camera": {"pos": [4.0, 1.8, 34.2], "tgt": [0.3, 1.0, 52]}, "move": 3, "moveEase": "linear",
  "players": [P(kit=CHE, skin="#8a5a3c", hair="#141010", x=1.2, z=39, action="kick", actionAt="three–nil", actionLag=-0.5, actionDur=0.8, after="celebrate"),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="three–nil", actionLag=-0.05),
              P(kit=FOR, skin="#e7b593", hair="#3a2a1a", x=2.6, z=42.8, front=True, action="dive", dir=1, actionAt="three–nil", actionLag=-0.35, actionDur=0.7),
              P(kit=FOR, skin="#8a5a3c", hair="#141010", x=-3.4, z=48, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": b0, "untilAt": "three–nil", "untilLag": -0.16},
           {"type": "ballpath", "world": True, "at": "three–nil", "lag": -0.16, "dur": 0.5, "slowmo": False, "points": [b0, [(b0[0] + end[0]) / 2, 1.1, (b0[2] + end[2]) / 2], end]},
           {"type": "flytext", "text": "0–3", "size": 300, "endScale": 0.7, "y": 620, "at": "three–nil", "lag": 0.3, "color": RED, "clear": False, "hideAt": "Within", "hideLag": -0.1},
           {"type": "stopwatch", "y": 1250, "at": "Within", "lag": -0.2, "value": 20, "max": 60, "unit": "MIN", "prefix": "<", "lockAt": "twenty minutes", "lockLag": 0.25, "r": 200, "clear": False},
           {"type": "stamp", "text": "GONE", "sub": "club statement", "at": "he was gone", "lag": 0.1, "color": RED, "rot": -0.08, "size": 110, "y": 1700}],
  "freezeAt": "he was gone", "freezeLag": 0.2})
# 7 twist
B.append({"kicker": "But here's the twist", "headline": "The record holder: [never sacked].", "cut": True, "transition": "vhs", "vhsLabel": "TWIST", "vhsDur": 0.9, "scene": S_DARK, "accent": GOLD, "lights": 0.35,
  "camFrom": {"pos": [0.8, 1.5, -3.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.2, 1.45, -1.0], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear",
  "players": [boss("#1d428a", hair="#9a9a9e", x=0, z=2.9, ghost=True)],
  "card": [{"type": "flytext", "text": "NEVER SACKED", "size": 150, "endScale": 0.85, "y": 1560, "at": "never actually", "lag": -0.1, "color": GOLD, "clear": False},
           {"type": "big", "delay": 0.3, "value": 1, "prefix": "#", "label": "Shortest reign ever · ?", "y": 760, "size": 200, "hideAt": "never actually", "hideLag": -0.2}],
  "punch": [{"t": 0.2, "amount": 0.12, "dur": 2.0, "x": 540, "y": 760}, {"at": "never actually", "amount": 0.14, "dur": 1.6}], "flashes": 10})
# 8 Allardyce at Leeds: 4 games, relegated (trapdoor)
B.append({"kicker": "Leeds United · May 2023", "headline": "Four games. [Relegated].", "cut": True, "transition": "whip", "scene": S_LEE, "accent": RED, "lights": 0.7, **CLOSE(-0.9),
  "players": [boss("#1d428a", hair="#9a9a9e", x=-1.5, z=2.9, label="Sam Allardyce", labelAt="Sam")],
  "card": [rank(1, "Sam Allardyce", "Leeds United", gold=True),
           {"type": "dots", "n": 4, "label": "Games left", "y": 1000, "shiftX": 240, "step": 0.2, "at": "four games", "lag": -0.3, "clear": False, "hideAt": "Leeds went", "hideLag": -0.3},
           {"type": "trapdoor", "y": 1400, "shiftX": 240, "scale": 1.05, "at": "2023", "lag": 0.1, "clear": False, "items": [{"name": "Leeds · 2022/23", "badge": BG["LEE"], "at": "went down", "lag": -0.1}]}],
  "shake": [{"at": "went down", "lag": 0.05, "amount": 14}]})
# 9 contract ran out: 30 days
B.append({"kicker": "The record", "headline": "[30 days]. Contract expired.", "cut": True, "scene": S_LEE, "accent": GOLD, "lights": 0.5, "focus": 0.4,
  "camFrom": {"pos": [8, 18, -32], "tgt": [0, 0, 8]}, "camera": {"pos": [-8, 12, -24], "tgt": [0, 0, 8]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "letter", "y": 1150, "delay": 0, "date": "CONTRACT · ends 2 June 2023", "write": 2.0, "w": 560, "h": 700, "clear": False},
           {"type": "stamp", "text": "EXPIRED", "sub": "not sacked", "at": "ran out", "lag": -0.1, "color": GOLD, "rot": -0.1, "size": 110, "y": 1180},
           {"type": "big", "at": "shortest reign", "lag": -0.4, "from": 0, "value": 30, "countDur": 0.8, "suffix": " days", "label": "The shortest reign in Premier League history", "y": 1720, "size": 190, "clear": False}],
  "shake": [{"at": "ran out", "lag": 0.06, "amount": 14}], "confetti": False})
# 10 ending: split + poll
B.append({"kicker": "Your call", "headline": "Who had it [worse]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_FOR, "accent": GOLD, "lights": 0.7,
  "camFrom": {"pos": [0, 1.5, -2.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.1], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear",
  "players": [boss("#7a1420", x=0, z=2.9, label="Postecoglou · 39 days", labelDelay=0.2)],
  "split": {"scene": S_CRY, "lights": 0.7, "camFrom": {"pos": [0, 1.5, -2.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.1], "tgt": [0, 1.3, 10]}, "move": 6,
            "players": [boss("#1b458f", hair="#c9b28a", x=0, z=2.9, label="De Boer · 0 goals", labelDelay=0.2)], "at": "or de Boer", "lag": -0.2},
  "card": [{"type": "poll", "y": 1620, "at": "who never", "lag": -0.2, "question": "Who had it worse?", "options": [{"label": "Postecoglou", "color": "#dd0000", "fill": 0.5}, {"label": "De Boer", "color": "#1b458f", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "Fastest sackings in Premier League history", "brand": "theo6k", "accent": RED, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
