# Builds videos/bruno-whatif/spec.json (run from the repo root).
# Every number comes from videos/bruno-whatif/research.md (data/mc.py, 10,000 runs per season).
import json
RED, GOLD, GREEN, TEAL = "#ff4d5e", "#e9b949", "#2ecc71", "#3FE0C5"
MUN = {"shirt": "#da291c", "shorts": "#ffffff", "socks": "#111111", "text": "#ffffff"}
OPP = {"shirt": "#1d4fb8", "shorts": "#1d4fb8", "socks": "#1d4fb8", "text": "#ffffff"}
GK = {"shirt": "#f7d117", "shorts": "#111111", "socks": "#f7d117", "text": "#111111"}
S_OT = {"type": "stadium", "crowd": ["#da291c", "#ffffff", "#111111", "#da291c"], "seed": 7}
S_SIM = {"type": "stadium", "crowd": ["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], "seed": 21}
V = 'videos/bruno-whatif/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
BRUNO = dict(kit=MUN, skin="#d9a37c", hair="#2a1a10", name="FERNANDES", num=8)
MOUNT = dict(kit=MUN, skin="#f0c8a8", hair="#3a2a1a", name="MOUNT", num=7)
ERIK = dict(kit=MUN, skin="#f3d2b8", hair="#b89a6a", name="ERIKSEN", num=14)
def hud(sub, **k):
    d = {"type": "simhud", "delay": 0, "sub": sub, "clear": False}; d.update(k); return d
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
B = []

# 1 hook: Bruno deleted into pixels inside the simulation, then the finishing-position chart builds: 7% Champions League
B.append({"kicker": "Man United · 10,000 simulations", "headline": "No Bruno? United [miss the Champions League].", "hookWords": True, "scene": S_OT, "accent": TEAL, "lights": 0.8,
  "camFrom": {"pos": [0, 1.3, 0.9], "tgt": [0, 1.15, 10]}, "camera": {"pos": [0, 1.3, 1.35], "tgt": [0, 1.15, 10]}, "move": 4, "moveEase": "linear",
  "players": [P(**BRUNO, x=0, z=3.3, front=True, chest=True, vanishAt="Bruno Fernandes", vanishLag=0.2, vanishDur=1.8)],
  "card": [hud("Man United · without Bruno", runs=10000, dur=0, y=1700)],
  "glitch": [{"t": 0.0, "dur": 0.35, "amount": 0.6}],
  "shots": [{"at": "In ten thousand", "lag": -0.15, "cut": True, "transition": "whip", "scene": S_SIM, "lights": 0.55, "focus": 0.2,
     "camFrom": {"pos": [24, 20, -30], "tgt": [0, 0, 6]}, "camera": {"pos": [-22, 12, -18], "tgt": [0, 0, 6]}, "move": 5.5, "moveEase": "linear", "players": [],
     "card": [hud("2025/26 · without Bruno", countT=0.1, dur=2.2, y=1760),
              {"type": "simrun", "y": 1180, "delay": 0, "countT": 0.1, "title": "2025/26 · where United finish", "positions": [1, 20], "real": 3, "dur": 3.0,
               "dist": {3: 0.2, 4: 2.0, 5: 4.8, 6: 28.4, 7: 5.0, 8: 2.5, 9: 1.9, 10: 7.5, 11: 31.7, 12: 4.7, 13: 2.5, 14: 4.9, 15: 1.3, 16: 2.5, 17: 0.1},
               "zone": {"from": 1, "to": 5, "label": "UCL", "color": GREEN}, "stamp": {"text": "7%", "sub": "of 10,000 runs"}, "stampAt": "seven percent", "stampLag": -0.1, "clear": False}],
     "shake": [{"at": "seven percent", "lag": 0.0, "amount": 14}]}]})

# 2 the method: his goals and assists deleted (board strikes 17 and 31 down to 0)
B.append({"kicker": "The experiment · 2024/25 + 2025/26", "headline": "Every Bruno goal and assist: [deleted].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_OT, "accent": RED, "lights": 0.65, "focus": 0.3,
  "camFrom": {"pos": [0, 60, -80], "tgt": [0, 0, 5]}, "camera": {"pos": [16, 30, -46], "tgt": [0, 0, 5]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [hud("The rules", dur=0, y=1760),
           {"type": "board", "y": 1050, "delay": 0.1, "label": "Bruno · Premier League · 2 seasons", "cols": 9, "vcols": 3, "swapAt": "deleted", "clear": False,
            "rows": [{"name": "GOALS", "value": "0", "from": "17"}, {"name": "ASSISTS", "value": "0", "from": "31"}], "focusPath": [{"t": 0, "row": 0}, {"at": "set up", "row": 1}]},
           {"type": "stamp", "text": "DELETED", "sub": "48 goals gone", "at": "deleted", "lag": 0.5, "color": RED, "rot": -0.07, "size": 100, "y": 1450}],
  "glitch": [{"at": "deleted", "lag": 0.0, "dur": 0.4}]})

# 3 the stand-in: sub board 8 out, 7 in; Mount runs on; Eriksen card for 2024/25
B.append({"kicker": "The stand-in", "headline": "On comes [Mason Mount].", "cut": True, "transition": "whip", "scene": S_OT, "accent": GOLD, "lights": 0.85,
  "camFrom": {"pos": [-1.2, 1.5, -1.0], "tgt": [0, 1.25, 10]}, "camera": {"pos": [-0.5, 1.45, 0.4], "tgt": [0, 1.25, 10]}, "move": 7, "moveEase": "linear",
  "players": [P(**MOUNT, x=-0.85, z=3.6, front=True, enter="walk", fromZ=8, walkDur=1.8, at="Mason Mount", lag=-1.2, label="Mason Mount", labelAt="Mason Mount", pose="fists")],
  "card": [{"type": "subboard", "y": 1480, "shiftX": 200, "w": 560, "delay": 0.0, "out": {"num": 8, "name": "Bruno"}, "in": {"num": 7, "name": "Mount"}, "swapAt": "Mason Mount", "clear": False, "hideAt": "Christian Eriksen", "hideLag": -0.2},
           {"type": "pcard", "y": 1380, "w": 380, "h": 500, "side": "right", "shiftX": 220, "at": "Christian Eriksen", "lag": -0.1, "player": dict(ERIK), "tag": "Eriksen · 2024/25", "clear": False}]})

# 4 the rules: they take his penalties (Mount scores one), then 10,000 seasons are played
B.append({"kicker": "The stand-in takes his penalties", "headline": "Their own rate. [His penalties].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_OT, "accent": GOLD,
  "camFrom": {"pos": [3.0, 2.2, 32.5], "tgt": [0, 1.0, 52]}, "camera": {"pos": [2.4, 1.9, 35.2], "tgt": [0, 1.0, 52]}, "move": 4, "moveEase": "linear", "follow": 0.45,
  "players": [P(**MOUNT, x=-0.15, z=41.0, action="kick", actionAt="take his penalties", actionLag=-0.35, actionDur=0.8, after="celebrate", runup=1.6, label="Mount", labelDelay=0.1),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="take his penalties", actionLag=0.05)],
  "card": [{"type": "ball", "delay": 0, "point": [0.02, 0.11, 41.5], "untilAt": "take his penalties", "untilLag": -0.01},
           {"type": "ballpath", "world": True, "at": "take his penalties", "lag": -0.01, "dur": 0.5, "slowmo": False, "points": [[0.02, 0.11, 41.5], [-1.4, 0.9, 47], [-2.8, 0.9, 52.3]]},
           {"type": "tape", "y": 1560, "delay": 0.2, "decimals": 2, "left": {"name": "Bruno", "color": "#da291c"}, "right": {"name": "Stand-in", "color": "#cfd3da"}, "clear": False,
            "rows": [{"label": "Goals + assists per 90 · 24/25", "left": 0.46, "right": 0.16, "at": "real rate", "lag": -0.4}]}],
  "shots": [{"at": "Then we played", "lag": -0.15, "cut": True, "transition": "whip", "scene": S_SIM, "lights": 0.55, "focus": 0.3, "headline": "Then: [10,000 seasons].",
     "camFrom": {"pos": [-30, 40, -40], "tgt": [0, 0, 0]}, "camera": {"pos": [30, 26, -30], "tgt": [0, 0, 0]}, "move": 4, "moveEase": "linear", "players": [],
     "card": [hud("Simulating both seasons", countT=0.1, dur=2.6, y=1760),
              {"type": "big", "delay": 0.05, "from": 0, "value": 10000, "comma": True, "countDur": 2.4, "label": "simulations of each season", "y": 1050, "size": 230, "clear": False}],
     "glitch": [{"t": 0.05, "dur": 0.4}]}]})

# 5 2024/25 for real: 15th, 42 points, worst PL season
TBL5 = [{"pos": 13, "name": "Everton", "color": "#274488", "pts": 48}, {"pos": 14, "name": "West Ham", "color": "#7a263a", "color2": "#1bb1e7", "pts": 43},
        {"pos": 15, "name": "Man United", "color": "#da291c", "pts": 42, "highlight": True}, {"pos": 16, "name": "Wolves", "color": "#fdb913", "pts": 42},
        {"pos": 17, "name": "Tottenham", "color": "#ffffff", "color2": "#132257", "pts": 38}]
B.append({"kicker": "2024/25 · the real season", "headline": "Real United: [15th], 42 points.", "cut": True, "transition": "polaroid", "polaroidLabel": "2024/25 · real", "scene": S_OT, "accent": RED, "lights": 0.6, "focus": 0.25,
  "camFrom": {"pos": [-12, 9, -18], "tgt": [0, 1, 6]}, "camera": {"pos": [-4, 6, -12], "tgt": [0, 1, 6]}, "move": 8, "moveEase": "linear",
  "players": [P(**BRUNO, x=-1.4, z=2.0, front=True, pose="think"), P(kit=MUN, skin="#8a5a3c", hair="#141010", num=6, name="", x=1.6, z=3.2, front=True)],
  "card": [{"type": "table", "y": 980, "at": "fifteenth", "lag": -0.9, "scale": 1.15, "label": "Premier League 2024/25 · real", "clear": False, "rows": TBL5},
           {"type": "stamp", "text": "WORST EVER", "sub": "United's lowest PL points total", "at": "their worst", "lag": -0.1, "color": RED, "rot": -0.06, "size": 92, "y": 1600}],
  "shake": [{"at": "their worst", "lag": 0.05, "amount": 12}]})

# 6 2024/25 simulated: about 36 points, 17th in 3 of 4 runs, never relegated
B.append({"kicker": "2024/25 · with the stand-in", "headline": "Simulated: [17th] in 3 of 4 runs.", "cut": True, "transition": "whip", "scene": S_SIM, "accent": RED, "lights": 0.5, "focus": 0.35,
  "camFrom": {"pos": [26, 40, -50], "tgt": [0, 0, 8]}, "camera": {"pos": [-26, 16, -26], "tgt": [0, 0, 8]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [hud("2024/25 · without Bruno", countT=0.1, dur=1.8, y=1760),
           {"type": "big", "at": "thirty-six points", "lag": -0.6, "from": 42, "value": 36, "countDur": 0.8, "label": "points on average (real: 42)", "y": 640, "size": 170, "style": "accent", "clear": False},
           {"type": "simrun", "y": 1240, "at": "With the stand-in", "lag": 0.2, "countT": 0.1, "dur": 2.6, "title": "2024/25 · where United finish", "positions": [10, 20], "real": 15,
            "dist": {14: 1.5, 15: 2.0, 16: 21.4, 17: 75.1}, "zone": {"from": 18, "to": 20, "label": "Relegation", "color": "#8a2a34"}, "peakColor": RED,
            "stamp": {"text": "75%", "sub": "17th", "color": RED, "pos": 17}, "stampAt": "three out of four", "stampLag": -0.1, "stampSize": 100, "clear": False}],
  "glitch": [{"t": 0.0, "dur": 0.3, "amount": 0.7}], "shake": [{"at": "three out of four", "lag": 0.0, "amount": 12}]})

# 7 re-hook: VHS to 2025/26, Bruno threads the pass, goal; 21 assists, a Premier League record
bf = [-5.78, 0.11, 30.45]; sf = [2.2, 0.11, 39.4]; gend = [-2.6, 0.8, 52.3]
B.append({"kicker": "2025/26 · the good season", "headline": "Then Bruno broke [a record].", "cut": True, "transition": "vhs", "vhsLabel": "2025/26", "vhsDur": 1.2, "scene": S_OT, "accent": GOLD,
  "camFrom": {"pos": [-11.5, 3.0, 22.5], "tgt": [-2, 1, 37]}, "camera": {"pos": [-9.5, 2.7, 26.0], "tgt": [-0.5, 1, 41]}, "move": 6.5, "moveEase": "linear", "follow": 0.3,
  "players": [P(**BRUNO, x=-6, z=30, action="kick", actionAt="Bruno set up", actionLag=-0.35, actionDur=0.8, runup=1.2, label="Bruno", labelDelay=0.2),
              P(kit=MUN, skin="#8a5a3c", hair="#141010", num=30, x=2.0, z=39.0, action="kick", actionAt="Bruno set up", actionLag=0.62, actionDur=0.8, runup=1.4, after="celebrate"),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="Bruno set up", actionLag=1.0),
              P(kit=OPP, skin="#e7b593", hair="#141010", x=4.2, z=41.5, front=True, action="dive", dir=-1, actionAt="Bruno set up", actionLag=0.7, actionDur=0.7),
              P(kit=OPP, skin="#8a5a3c", hair="#141010", x=-3.5, z=36, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": bf, "untilAt": "Bruno set up", "untilLag": -0.01},
           {"type": "ballpath", "world": True, "at": "Bruno set up", "lag": -0.01, "dur": 0.9, "slowmo": False, "flash": False, "points": [bf, mid(bf, sf, 0.3), sf]},
           {"type": "ballpath", "world": True, "at": "Bruno set up", "lag": 0.95, "dur": 0.5, "slowmo": False, "points": [sf, mid(sf, gend, 1.0), gend]},
           {"type": "big", "at": "twenty-one goals", "lag": -0.9, "from": 0, "value": 21, "countDur": 1.0, "label": "Bruno assists · 2025/26", "y": 650, "size": 200, "clear": False},
           {"type": "stamp", "text": "RECORD", "sub": "most in a Premier League season", "at": "A Premier League record", "lag": 0.0, "color": GOLD, "rot": -0.07, "size": 96, "y": 1720}],
  "shake": [{"at": "A Premier League record", "lag": 0.05, "amount": 14}], "flashes": 12})

# 8 ghost replay: the same move with Mount, and the pass never arrives; Mount's rate about a third of Bruno's
mf = [-5.78, 0.11, 30.45]; cut_ = [1.0, 0.11, 36.2]
B.append({"kicker": "2025/26 · the simulation", "headline": "Same move. [No Bruno].", "cut": True, "scene": S_OT, "accent": RED, "lights": 0.6, "letterbox": True, "replayTag": "SIMULATION", "hype": False,
  "camFrom": {"pos": [-11.5, 3.0, 22.5], "tgt": [-2, 1, 36]}, "camera": {"pos": [-10.5, 2.8, 24.5], "tgt": [-1.5, 1, 36.5]}, "move": 4, "moveEase": "linear",
  "players": [P(**MOUNT, x=-6, z=30, action="kick", actionDelay=0.35, actionDur=0.8, label="Mount", labelDelay=0.1),
              P(kit=MUN, skin="#8a5a3c", hair="#141010", num=30, x=2.0, z=39.0, action="idle"),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready"),
              P(kit=OPP, skin="#e7b593", hair="#141010", x=1.3, z=36.6, front=True, action="dive", dir=1, actionDelay=0.85, actionDur=0.7),
              P(kit=OPP, skin="#8a5a3c", hair="#141010", x=-3.5, z=36, front=True)],
  "card": [{"type": "ball", "delay": 0, "point": mf, "until": 0.69},
           {"type": "ballpath", "world": True, "delay": 0.69, "dur": 0.75, "slowmo": False, "flash": False, "points": [mf, mid(mf, cut_, 0.25), cut_]},
           {"type": "ball", "delay": 1.44, "point": cut_},
           {"type": "tape", "y": 1430, "at": "rate", "lag": -0.2, "decimals": 2, "left": {"name": "Bruno", "color": "#da291c"}, "right": {"name": "Mount", "color": "#cfd3da"}, "clear": False,
            "rows": [{"label": "Goals + assists per 90 · 25/26", "left": 0.78, "right": 0.27, "t": 0.1}], "caption": "about a third", "captionAt": "a third"}],
  "glitch": [{"t": 0.0, "dur": 0.4}]})

# 9 split screen: real United 3rd on 71 v simulated about 53: 18 points gone
B.append({"kicker": "2025/26 · real v simulated", "headline": "[18 points] gone.", "cut": True, "transition": "whip", "scene": S_OT, "accent": RED, "flashes": 8,
  "camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.4], "tgt": [0, 1.3, 10]}, "move": 7, "moveEase": "linear",
  "players": [P(**BRUNO, x=0, z=3.4, front=True, pose="fists", label="Real", labelDelay=0.1)],
  "split": {"at": "Simulated United", "lag": -0.2, "scene": S_SIM, "lights": 0.45, "camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.6], "tgt": [0, 1.3, 10]}, "move": 7,
            "players": [P(**MOUNT, x=0, z=3.4, front=True, pose="think", label="Simulated", labelDelay=0.1)]},
  "card": [{"type": "big", "shiftX": -270, "at": "seventy-one", "lag": -0.5, "from": 0, "value": 71, "countDur": 0.8, "label": "3rd · real", "y": 1500, "size": 190, "clear": False},
           {"type": "big", "shiftX": 270, "at": "fifty-three", "lag": -0.5, "from": 71, "value": 53, "countDur": 0.8, "label": "avg · simulated", "y": 1500, "size": 190, "style": "accent", "clear": False},
           {"type": "stamp", "text": "−18", "sub": "points", "at": "Eighteen points", "lag": -0.05, "color": RED, "rot": -0.08, "size": 120, "y": 780}],
  "shake": [{"at": "Eighteen points", "lag": 0.05, "amount": 16}]})

# 10 the odds: 7 squares in 100 light up
B.append({"kicker": "2025/26 · Champions League (top 5)", "headline": "Champions League: [7 in 100].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": GREEN, "lights": 0.45, "focus": 0.45,
  "camFrom": {"pos": [0, 70, -30], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 46, -12], "tgt": [0, 0, 0]}, "move": 4.5, "moveEase": "linear", "players": [],
  "card": [hud("10,000 runs · 2025/26", dur=0, y=1780),
           {"type": "odds", "y": 1060, "delay": 0.0, "lit": 7, "litAt": "Seven simulations", "litLag": -0.1, "title": "Every 100 simulations", "label": "{n} in 100", "clear": False}],
  "glitch": [{"t": 0.0, "dur": 0.3, "amount": 0.6}]})

# 11 Bruno builds back up out of the pixels; the question
B.append({"kicker": "Your call", "headline": "Should United [let him go]?", "cut": True, "scene": S_OT, "accent": GOLD, "flashes": 10,
  "orbit": {"center": [0, 1.25, 3], "r": 5.0, "from": -26, "to": 14, "h": 1.5, "h2": 1.8, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [P(**BRUNO, x=0, z=3.2, front=True, chest=True, pose="arms_up", appearDelay=0.1, vanishDur=1.2)],
  "card": [{"type": "poll", "y": 1580, "at": "be honest", "lag": -0.4, "question": "Should United let Bruno go?", "options": [{"label": "Keep him", "color": "#da291c", "fill": 0.5}, {"label": "Let him go", "color": "#3a4356", "fill": 0.5}]}],
  "glitch": [{"t": 0.0, "dur": 0.35}]})

for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
json.dump({"title": "What if Bruno had left Man United?", "brand": "theo6k", "accent": TEAL, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
