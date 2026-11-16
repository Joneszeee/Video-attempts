# Builds videos/poch-anfield/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
MUN = {"shirt": "#da291c", "shorts": "#ffffff", "socks": "#111111", "text": "#ffffff"}
MUA = {"shirt": "#f4f4f2", "shorts": "#111111", "socks": "#f4f4f2", "text": "#111111"}   # change kit for the Anfield scenes (kit-clash rule)
LIV = {"shirt": "#c8102e", "shorts": "#c8102e", "socks": "#c8102e", "text": "#ffffff"}
TOT = {"shirt": "#f4f4f2", "shorts": "#132257", "socks": "#f4f4f2", "text": "#132257"}
GK = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
S_ANF = {"type": "stadium", "crowd": ["#c8102e", "#ffffff", "#c8102e", "#8a0b1f"], "seed": 6}
S_OT = {"type": "stadium", "crowd": ["#da291c", "#ffffff", "#111111", "#da291c"], "seed": 7}
S_TOT = {"type": "stadium", "crowd": ["#ffffff", "#132257", "#ffffff", "#9aa3b2"], "seed": 11}
V = 'videos/poch-anfield/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def poch(tie="#7a1420", **k): return P(outfit="suit", suitColor="#1c1f28", tie=tie, skin="#e2b08c", hair="#3a3a3e", front=True, **k)
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
YEARS = [str(y) for y in range(2018, 2027)]
B = []
# 1 hook: nine years of crosses, then ANFIELD
B.append({"kicker": "Liverpool v Man United · Sunday 22 November", "headline": "No win v Liverpool in [9 years]. Next: Anfield.", "hookWords": True, "scene": S_ANF, "accent": RED, "lights": 0.7, "flashes": 14,
  "camFrom": {"pos": [-1.0, 1.5, 0.3], "tgt": [-1.0, 1.35, 10]}, "camera": {"pos": [-1.0, 1.5, -0.9], "tgt": [-1.0, 1.35, 10]}, "move": 8, "moveEase": "linear",
  "players": [poch(x=-1.6, z=3.5, enter="walk", fromZ=4.9, walkDur=2.4, label="Pochettino", labelDelay=0)],
  "card": [{"type": "tally", "y": 1240, "shiftX": 215, "delay": -0.3, "r": 62, "gap": 16, "perRow": 3, "title": "v Liverpool", "score": "{l} years · no win", "clear": False,
            "items": [{"label": y, "mark": "x", "t": 0.25 + i * 0.16} for i, y in enumerate(YEARS)]},
           {"type": "flytext", "text": "ANFIELD", "size": 230, "endScale": 0.75, "y": 1800, "at": "At Anfield", "lag": -0.1, "color": RED, "clear": False}],
  "shake": [{"t": 1.75, "amount": 12}, {"at": "At Anfield", "lag": 0.2, "amount": 16}]})
# 2 United 18th
B.append({"kicker": "Premier League · after 10 games", "headline": "United are [18th].", "cut": True, "transition": "whip", "scene": S_OT, "accent": RED, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-12, 14, -28], "tgt": [0, 0, 8]}, "camera": {"pos": [10, 22, -40], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "table", "y": 760, "delay": 0, "scale": 1.15, "label": "Premier League · bottom three", "clear": False,
            "rows": [{"pos": 18, "name": "Man United", "color": "#da291c", "pts": 8, "highlight": True}, {"pos": 19, "name": "Sunderland", "color": "#eb172b", "color2": "#ffffff", "pts": 8}, {"pos": 20, "name": "Crystal Palace", "color": "#1b458f", "color2": "#c4122e", "pts": 7}]},
           {"type": "stack", "y": 1700, "delay": 0, "size": 190, "items": [{"value": 10, "label": "Games", "at": "Ten games"}, {"value": 1, "label": "Win", "at": "one win", "color": RED}, {"value": 8, "label": "Points", "at": "eight points", "color": RED}]}]})
# 3 Carrick sacked after 15 games
B.append({"kicker": "Michael Carrick", "headline": "Sacked after [15 games].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_OT, "accent": RED, "lights": 0.55,
  "camFrom": {"pos": [1.0, 1.6, -2.8], "tgt": [0, 1.25, 10]}, "camera": {"pos": [0.3, 1.5, -1.2], "tgt": [0, 1.25, 10]}, "move": 6, "moveEase": "linear",
  "players": [P(outfit="suit", suitColor="#1c1f28", tie="#1c2c5b", skin="#f0c8a8", hair="#3a2a1a", front=True, x=0, z=2.9, label="Michael Carrick", labelDelay=0.2)],
  "card": [{"type": "dots", "n": 15, "y": 1500, "label": "Games in charge", "step": 0.1, "delay": 0.2, "clear": False},
           {"type": "stamp", "text": "SACKED", "sub": "worst Premier League start", "at": "sacked", "lag": 0.1, "color": RED, "rot": -0.08, "size": 96, "y": 1790}],
  "shake": [{"at": "sacked", "lag": 0.26, "amount": 14}], "freezeAt": "worst start", "freezeLag": 0.2})
# 4 the dates: 18 Nov -> 4 days -> Anfield
B.append({"kicker": "The week", "headline": "Four days to [Anfield].", "cut": True, "transition": "whip", "scene": S_ANF, "accent": GOLD, "lights": 0.6, "focus": 0.25,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 14, -28], "tgt": [0, 0, 10]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 660, "delay": 0.1, "label": "Pochettino takes over", "groups": [{"label": "November", "value": 18, "digits": 2}], "side": {"top": "WED", "big": "18", "bottom": "NOV"}},
           {"type": "crossoff", "y": 1190, "at": "Four days", "lag": -0.4, "title": "Days to prepare", "days": 4, "cols": 4, "cell": 150, "crossT": 0.2, "dur": 1.0, "caption": "{n} days", "clear": False},
           {"type": "tickets", "y": 1690, "at": "he walks out", "lag": -0.2, "done": 1, "tw": 720, "th": 230, "dx": 0, "tickets": [{"comp": "Premier League", "teams": "Liverpool v Man United", "score": "16:30", "date": "Sun 22 Nov", "color": "#c8102e"}], "clear": False}]})
# 5 last win over Liverpool: 2017, with Tottenham
t0 = [1.22, 0.11, 41.45]; te = [-2.8, 0.7, 52.3]
B.append({"kicker": "October 2017", "headline": "His last win over Liverpool: [2017].", "cut": True, "transition": "polaroid", "polaroidLabel": "Tottenham 2017", "scene": S_TOT, "accent": GOLD, "follow": 0.5,
  "camFrom": {"pos": [4.0, 2.2, 32.0], "tgt": [0.4, 1.0, 52]}, "camera": {"pos": [3.4, 1.9, 34.7], "tgt": [0.4, 1.0, 52]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=TOT, skin="#f0c8a8", hair="#b8905a", x=1.0, z=41, action="kick", actionAt="2017", actionLag=-0.6, actionDur=0.8, after="celebrate", runup=1.6),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="2017", actionLag=-0.15),
              P(kit=LIV, skin="#e7b593", hair="#141010", x=3.0, z=44.3, front=True, action="dive", dir=-1, actionAt="2017", actionLag=-0.45, actionDur=0.7), P(kit=LIV, skin="#8a5a3c", hair="#141010", x=-2.4, z=47.6, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": t0, "untilAt": "2017", "untilLag": -0.26},
           {"type": "ballpath", "world": True, "at": "2017", "lag": -0.26, "dur": 0.5, "slowmo": False, "points": [t0, mid(t0, te, 0.9), te]},
           {"type": "big", "at": "2017", "lag": 0.2, "from": 2026, "value": 2017, "countDur": 0.9, "label": "Pochettino's last win over Liverpool", "y": 1620, "size": 230, "clear": False}]})
# 6 the twist: United won at Anfield last season, 2-1
u0 = [-1.78, 0.11, 42.45]; ue = [2.9, 1.0, 52.3]
B.append({"kicker": "But here's the twist", "headline": "United won at Anfield: [1–2].", "cut": True, "transition": "vhs", "vhsLabel": "TWIST", "vhsDur": 0.9, "scene": S_ANF, "accent": GREEN, "follow": 0.5,
  "camFrom": {"pos": [-5.0, 2.2, 33.0], "tgt": [-0.8, 1.0, 52]}, "camera": {"pos": [-4.4, 1.9, 35.7], "tgt": [-0.8, 1.0, 52]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=MUA, skin="#8a5a3c", hair="#141010", x=-2.0, z=42, action="kick", actionAt="Two–one", actionLag=-0.6, actionDur=0.8, after="celebrate", runup=1.6),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="Two–one", actionLag=-0.15),
              P(kit=LIV, skin="#e7b593", hair="#141010", x=-3.9, z=45.3, front=True, action="dive", dir=1, actionAt="Two–one", actionLag=-0.45, actionDur=0.7), P(kit=LIV, skin="#f0c8a8", hair="#5a3a22", x=2.4, z=48, front=True)],
  "card": [{"type": "scorebug", "y": 610, "delay": 0, "home": {"name": "LIV", "color": "#c8102e"}, "away": {"name": "MUN", "color": "#f4f4f2"}, "score": [1, 2], "from": [1, 1], "goalAt": "Two–one", "goalLag": 0.3, "min": "OCT 2025", "clear": False},
           {"type": "ball", "delay": 0, "point": u0, "untilAt": "Two–one", "untilLag": -0.26},
           {"type": "ballpath", "world": True, "at": "Two–one", "lag": -0.26, "dur": 0.5, "slowmo": False, "points": [u0, mid(u0, ue, 1.0), ue]},
           {"type": "stamp", "text": "FIRST WIN", "sub": "at Anfield since January 2016", "at": "first win", "lag": -0.1, "color": GREEN, "rot": -0.07, "size": 84, "y": 1700}]})
# 7 the curse can be broken, not usually by him
B.append({"kicker": "The curse", "headline": "It can be broken. [Not by him].", "cut": True, "scene": S_ANF, "accent": RED, "lights": 0.4,
  "camFrom": {"pos": [0.9, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.2, 1.45, -0.9], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
  "players": [poch(x=0, z=2.9, pose="think")],
  "card": [{"type": "scales", "y": 1480, "delay": 0.2, "left": {"name": "United", "value": 1, "color": "#1f8a4c", "sub": "won there"}, "right": {"name": "Pochettino", "value": 1.6, "color": "#d6283b", "sub": "9 years"}, "tilt": 0.2, "arm": 250, "clear": False}],
  "punch": [{"at": "Just not", "amount": 0.14, "dur": 1.4}]})
# 8 lose / win
B.append({"kicker": "What's at stake", "headline": "Lose: bottom three. [Win: a new era].", "cut": True, "transition": "whip", "scene": S_OT, "accent": GOLD, "lights": 0.4,
  "camFrom": {"pos": [0, 9, -22], "tgt": [0, 2, 8]}, "camera": {"pos": [0, 6, -15], "tgt": [0, 2, 8]}, "move": 7, "moveEase": "linear", "players": [],
  "split": {"scene": S_ANF, "lights": 0.95, "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.2], "tgt": [0, 1.3, 10]}, "move": 7,
            "players": [P(kit=MUA, skin="#8a5a3c", hair="#141010", x=0, z=3, front=True, action="celebrate")], "at": "Win, and", "lag": -0.2},
  "card": [{"type": "trapdoor", "y": 1100, "shiftX": -270, "delay": 0.1, "scale": 0.95, "clear": False, "items": [{"name": "Lose", "badge": {"colors": ["#da291c", "#111111", "#fbe122"], "text": "MUFC"}, "at": "bottom three", "lag": -0.4, "tag": "BOTTOM 3"}]},
           {"type": "stamp", "text": "NEW ERA", "sub": "win at Anfield", "at": "new era", "lag": -0.1, "color": GOLD, "rot": -0.07, "size": 80, "dx": 270, "y": 1640}]})
# 9 question
B.append({"kicker": "Your call", "headline": "Curse, or a [new United]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ANF, "accent": GOLD, "flashes": 12,
  "orbit": {"center": [0, 1.25, 3], "r": 5.2, "from": -28, "to": 16, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [poch(x=-1.2, z=3.2, pose="fists", label="Pochettino", labelDelay=0.2), P(kit=LIV, skin="#8a5a3c", hair="#141010", x=1.3, z=3.4, front=True, label="Liverpool", labelDelay=0.4)],
  "card": [{"type": "poll", "y": 1580, "at": "Pochettino's curse", "lag": -0.3, "question": "Liverpool v Man United?", "options": [{"label": "Liverpool win", "color": "#c8102e", "fill": 0.45}, {"label": "Draw", "color": "#5d6470", "fill": 0.25}, {"label": "United win", "color": "#b8892a", "fill": 0.35}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 9
json.dump({"title": "Pochettino's first game: Anfield", "brand": "theo6k", "accent": RED, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
