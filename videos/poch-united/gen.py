# Builds videos/poch-united/spec.json (run from the repo root).
import json
RED, GOLD, BLUE = "#ff4d5e", "#e9b949", "#4da3ff"
MUN = {"shirt": "#da291c", "shorts": "#ffffff", "socks": "#111111", "text": "#ffffff"}
TOT = {"shirt": "#f4f4f2", "shorts": "#132257", "socks": "#f4f4f2", "text": "#132257"}
OPP = {"shirt": "#6cabdd", "shorts": "#ffffff", "socks": "#6cabdd", "text": "#1c2c5b"}
GK = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
S_OT = {"type": "stadium", "crowd": ["#da291c", "#ffffff", "#111111", "#da291c"], "seed": 7}
S_USA = {"type": "stadium", "crowd": ["#0a2a66", "#ffffff", "#c8102e", "#0a2a66"], "seed": 12}
S_TOT = {"type": "stadium", "crowd": ["#ffffff", "#132257", "#ffffff", "#9aa3b2"], "seed": 11}
S_PAR = {"type": "stadium", "crowd": ["#0a2a66", "#c8102e", "#0a2a66", "#ffffff"], "seed": 30}
lines = [l.strip() for l in open('videos/poch-united/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def poch(tie="#7a1420", **k): return P(outfit="suit", suitColor="#1c1f28", tie=tie, skin="#e2b08c", hair="#3a3a3e", **k)
STOPS = [dict(name="Tottenham", sub="2014–2019", color="#132257", result="UCL final · no trophy"),
         dict(name="PSG", sub="2021–2022", color="#0a2a66", result="League title · sacked"),
         dict(name="Chelsea", sub="2023–2024", color="#034694", result="6th · gone in a year"),
         dict(name="USA", sub="2024–", color="#c8102e", result="Lost 4–1 · last 16")]
def career(done, at, **k):
    items = []
    for i, s in enumerate(STOPS):
        it = dict(s)
        if i in at: it["at"] = at[i]
        elif i >= done: it["t"] = 99
        items.append(it)
    d = {"type": "career", "title": "Pochettino's last four jobs", "items": items, "y": 1130, "w": 960, "rowH": 235, "clear": False}; d.update(k); return d
B = []
# 1 hook
B.append({"kicker": "Manchester United · manager search", "headline": "United's saviour? [Zero trophies] in England.", "hookWords": True, "scene": S_OT, "accent": RED, "lights": 0.8, "flashes": 14,
  "camFrom": {"pos": [0, 1.5, 0.2], "tgt": [0, 1.4, 10]}, "camera": {"pos": [0, 1.5, -0.6], "tgt": [0, 1.4, 10]}, "move": 7, "moveEase": "linear",
  "players": [poch(x=0, z=3.2, front=True, enter="walk", fromZ=4.4, walkDur=2.6, label="Mauricio Pochettino", labelDelay=0)],
  "card": [{"type": "stamp", "text": "18TH", "sub": "Man United", "delay": 0.25, "color": RED, "rot": -0.1, "size": 86, "dx": -250, "y": 1640},
           {"type": "stamp", "text": "0", "sub": "trophies in England", "at": "never won", "color": GOLD, "rot": 0.08, "size": 120, "dx": 260, "y": 1640}],
  "shake": [{"at": "never won", "lag": 0.16, "amount": 14}]})
# 2 talks
B.append({"kicker": "Wednesday · 11 November 2026", "headline": "United open [talks].", "cut": True, "transition": "whip", "scene": S_OT, "accent": RED, "lights": 0.6, "focus": 0.35,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 16, -30], "tgt": [0, 0, 10]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 680, "at": "eleventh", "lag": -0.3, "label": "The reports", "groups": [{"label": "November", "value": 11, "digits": 2}], "side": {"top": "WED", "big": "11", "bottom": "NOV"}},
           {"type": "newspaper", "at": "Reports say", "lag": -0.2, "y": 1330, "masthead": "THE MATCHDAY POST", "dateline": "Wednesday 11 November 2026",
            "headline": "UNITED OPEN TALKS\nWITH POCHETTINO", "sub": "Carrick's future in doubt", "color": "#2a2116", "spin": 1.4, "scale": 0.8, "clear": False}]})
# 3 USA contract, $10m
B.append({"kicker": "The obstacle", "headline": "USA coach until [2030].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_USA, "accent": BLUE,
  "camFrom": {"pos": [-1.6, 1.5, -1.4], "tgt": [-0.6, 1.35, 10]}, "camera": {"pos": [-1.2, 1.5, -0.4], "tgt": [-0.6, 1.35, 10]}, "move": 3, "moveEase": "linear",
  "players": [poch(tie="#0a2a66", x=-1.1, z=2.6, front=True, label="USA head coach", labelDelay=0.2)],
  "card": [{"type": "big", "at": "2030", "lag": -0.4, "from": 2026, "value": 2030, "countDur": 0.7, "label": "Contract runs until", "y": 1560, "shiftX": 150, "size": 200}],
  "shots": [{"at": "Getting him out", "lag": -0.15, "cut": True, "lights": 0.5, "focus": 0.55, "move": 4, "moveEase": "linear",
     "camFrom": {"pos": [0, 44, -72], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 12, -24], "tgt": [0, 0, 10]}, "focus": 0.3, "players": [],
     "card": [{"type": "receipt", "y": 1150, "delay": 0, "title": "RELEASE CLAUSE", "sub": "U.S. Soccer → Man United", "step": 0.45,
               "lines": [["Contract", "to 2030"], ["Exit clause", "≈ $10m", True], ["Staff", "extra"]], "total": ["TO PAY", "≈ $10m+"], "clear": False}],
     "punch": [{"at": "ten million", "amount": 0.12, "dur": 1.4, "x": 540, "y": 1250}]}]})
# 4 worth it?
B.append({"kicker": "The record", "headline": "So is he [worth it]?", "cut": True, "transition": "vhs", "vhsLabel": "HIS RECORD", "vhsDur": 0.9, "scene": S_OT, "accent": GOLD, "lights": 0.45,
  "camFrom": {"pos": [0.9, 1.6, -2.4], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0.2, 1.5, -0.6], "tgt": [0, 1.35, 10]}, "move": 3, "moveEase": "linear",
  "players": [poch(x=0, z=2.6, front=True, pose="think")],
  "card": [{"type": "flytext", "text": "WORTH IT?", "size": 200, "endScale": 0.62, "y": 1560, "delay": 0.2, "color": GOLD, "clear": False}],
  "punch": [{"at": "Look", "amount": 0.14, "dur": 1.2}]})
# 5 Tottenham
B.append({"kicker": "Stop 1 · Tottenham", "headline": "A final. [No trophy].", "cut": True, "transition": "whip", "scene": S_TOT, "accent": RED, "lights": 0.5, "focus": 0.5,
  "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 22, -38], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [],
  "punch": [{"at": "Champions League", "amount": 0.1, "dur": 1.4, "x": 540, "y": 850}],
  "card": [career(0, {0: "At Tottenham"}), {"type": "stamp", "text": "NO TROPHY", "at": "But no trophy", "color": RED, "rot": -0.08, "size": 96, "y": 1730}]})
# 6 PSG, Chelsea
B.append({"kicker": "Stops 2 and 3", "headline": "PSG: sacked. Chelsea: [one season].", "cut": True, "scene": S_PAR, "accent": RED, "lights": 0.5, "focus": 0.5,
  "camFrom": {"pos": [0, 22, -38], "tgt": [0, 0, 8]}, "camera": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [career(1, {1: "At PSG", 2: "At Chelsea"})], "punch": [{"at": "the sack", "amount": 0.08, "dur": 1.0, "x": 540, "y": 1000}, {"at": "gone", "amount": 0.08, "dur": 1.0, "x": 540, "y": 1200}]})
# 7 USA 4-1
B.append({"kicker": "Stop 4 · World Cup 2026", "headline": "USA 1–4 [Belgium].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_USA, "accent": RED, "lights": 0.6,
  "camFrom": {"pos": [0.8, 1.6, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.2, 1.5, -1.0], "tgt": [0, 1.3, 10]}, "move": 4.5, "moveEase": "linear",
  "players": [poch(tie="#0a2a66", x=0, z=2.6, front=True)],
  "card": [{"type": "flytext", "text": "1–4", "size": 330, "endScale": 0.8, "y": 1540, "at": "four–one", "lag": -0.2, "color": RED, "clear": False},
           {"type": "stamp", "text": "OUT", "sub": "last 16 · at home", "at": "home World Cup", "lag": -0.2, "color": "#ffffff", "rot": -0.09, "size": 80, "y": 1790}],
  "freezeAt": "home World Cup", "freezeLag": 0.3})
# 8 re-hook: the leak
B.append({"kicker": "United's real problem", "headline": "[19] conceded in 10 games.", "cut": True, "transition": "vhs", "vhsLabel": "BUT", "vhsDur": 0.8, "scene": S_OT, "accent": RED, "lights": 0.5, "focus": 0.45,
  "camFrom": {"pos": [0, 34, -56], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 16, -28], "tgt": [0, 0, 8]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "leak", "y": 1010, "at": "United's biggest", "lag": -0.2, "value": 19, "dur": 3.0, "sub": "Man United", "label": "Goals conceded · 10 league games", "clear": False}],
  "shake": [{"at": "ten league games", "lag": 0.3, "amount": 12}]})
# 9 Spurs' best defence: a real save
B.append({"kicker": "Tottenham · 2016/17", "headline": "The league's [best defence].", "cut": True, "transition": "whip", "scene": S_TOT, "accent": GOLD,
  "camFrom": {"pos": [4.2, 2.2, 36], "tgt": [0.2, 1.2, 52]}, "camera": {"pos": [3.4, 2.0, 38.5], "tgt": [0.2, 1.2, 52]}, "move": 4, "moveEase": "linear", "hype": False,
  "players": [P(kit=OPP, skin="#e7b593", hair="#3a2a1a", x=-1.0, z=41, action="kick", actionDelay=0.35, actionDur=0.8),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1),
              P(kit=TOT, skin="#8a5a3c", hair="#141010", x=1.4, z=45.5, front=True), P(kit=TOT, skin="#f0c8a8", hair="#5a3a22", x=-2.6, z=46.5, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": [-0.78, 0.11, 41.45], "until": 0.69},
           {"type": "ballpath", "world": True, "delay": 0.69, "dur": 0.6, "slowmo": False, "saveBy": 1, "flash": False, "points": [[-0.78, 0.11, 41.45], [0.6, 1.4, 47], [2.4, 1.3, 52.0]]},
           {"type": "big", "at": "best defence", "lag": -0.5, "from": 60, "value": 26, "countDur": 0.8, "label": "Goals conceded all season · fewest in the league", "y": 1580, "size": 230}]})
# 10 verdict gauge
B.append({"kicker": "The verdict", "headline": "Stops the bleeding. [No trophies].", "cut": True, "scene": S_OT, "accent": GOLD, "lights": 0.5, "focus": 0.45,
  "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 18, -32], "tgt": [0, 0, 8]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "gauge", "y": 1300, "r": 430, "delay": 0, "title": "Would Pochettino fix United?", "value": 0.5, "settleAt": "stops the bleeding", "settleLag": -0.5, "verdict": "STEADIES THE SHIP",
            "zones": [{"label": "Flop", "color": "#d6283b"}, {"label": "Steadies", "color": "#f1c453"}, {"label": "Trophies", "color": "#2ecc71"}], "clear": False},
           {"type": "stamp", "text": "NO TROPHIES", "sub": "history says", "at": "doesn't bring", "color": RED, "rot": -0.07, "size": 84, "y": 1700}],
  "punch": [{"at": "history", "amount": 0.1, "dur": 1.6, "x": 540, "y": 1300}, {"t": 0.3, "amount": 0.06, "dur": 1.4, "x": 540, "y": 1200}]})
# 11 poll
B.append({"kicker": "Your call", "headline": "Pochettino at United: [yes or no]?", "cut": True, "transition": "whip", "scene": S_OT, "accent": GOLD, "flashes": 12,
  "orbit": {"center": [0, 1.25, 3], "r": 5, "from": -25, "to": 18, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [poch(x=-1.2, z=3.2, front=True, pose="fists", label="Pochettino", labelDelay=0.2), P(kit=MUN, skin="#8a5a3c", hair="#141010", x=1.3, z=3.4, front=True, label="United · 18th", labelDelay=0.5)],
  "card": [{"type": "poll", "y": 1580, "at": "yes or no", "lag": -0.6, "question": "Pochettino at United?", "options": [{"label": "Yes, hire him", "color": "#da291c", "fill": 0.5}, {"label": "No thanks", "color": "#9aa1ad", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
json.dump({"title": "Pochettino to Man United?", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open('videos/poch-united/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
