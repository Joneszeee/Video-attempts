# Builds videos/united-omen/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
MUN = {"shirt": "#da291c", "shorts": "#ffffff", "socks": "#111111", "text": "#ffffff"}
CRY = {"shirt": "#1b458f", "shorts": "#1b458f", "socks": "#1b458f", "text": "#ffffff", "stripes": ["#c4122e", "#1b458f"]}
S_OT = {"type": "stadium", "crowd": ["#da291c", "#ffffff", "#111111", "#da291c"], "seed": 7}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
S_CRY = {"type": "stadium", "crowd": ["#1b458f", "#c4122e", "#1b458f", "#ffffff"], "seed": 15}
lines = [l.strip() for l in open('videos/united-omen/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
BG = {"NOR": {"colors": ["#fff200", "#00a650", "#00a650"], "text": "NCFC"}, "FUL": {"colors": ["#ffffff", "#111111", "#cc0000"], "text": "FFC"},
      "BUR": {"colors": ["#6c1d45", "#99d6ea", "#99d6ea"], "text": "BFC"}, "WHU": {"colors": ["#7a263a", "#1bb1e7", "#1bb1e7"], "text": "WHU"},
      "CRY": {"colors": ["#1b458f", "#c4122e"], "text": "CPFC", "style": "stripes"}, "MUN": {"colors": ["#da291c", "#111111", "#fbe122"], "text": "MUFC"}}
T = [dict(name="Norwich", sub="2019/20", badge=BG["NOR"], fate="down"), dict(name="Fulham", sub="2020/21", badge=BG["FUL"], fate="down"),
     dict(name="Burnley", sub="2021/22", badge=BG["BUR"], fate="down"), dict(name="Palace", sub="2024/25", badge=BG["CRY"], fate="up"),
     dict(name="West Ham", sub="2025/26", badge=BG["WHU"], fate="down")]
def fates(extra, **k):
    items = [dict(t, **extra.get(i, {})) for i, t in enumerate(T)]
    d = {"type": "fates", "title": "7 points after 10 games", "items": items, "clear": False}; d.update(k); return d
HI = {"pos": [0, 30, -50], "tgt": [0, 0, 5]}; MID = {"pos": [0, 18, -32], "tgt": [0, 0, 8]}
B = []
# 1 hook: tiles slam to RELEGATED around a United player
B.append({"kicker": "Premier League · the omen", "headline": "United: [one point] from a relegation start.", "hookWords": True, "scene": S_OT, "accent": RED, "lights": 0.6, "flashes": 10,
  "camFrom": {"pos": [0, 1.5, 0.4], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.5, -0.8], "tgt": [0, 1.35, 10]}, "move": 7, "moveEase": "linear",
  "players": [P(kit=MUN, skin="#e7b593", hair="#3a2a1a", x=0, z=3.4, front=True, enter="walk", fromZ=4.6, walkDur=2.4, label="Man United · 8 pts", labelDelay=0)],
  "card": [fates({0: {"t": 0.15}, 1: {"t": 0.4}, 2: {"t": 0.65}, 3: {"t": 1.15}, 4: {"t": 0.9}}, y=1560, delay=-0.05),
           {"type": "stamp", "text": "4 OF 5", "sub": "relegated", "at": "four of the last", "color": RED, "rot": -0.08, "size": 100, "y": 1800}],
  "shake": [{"at": "four of the last", "lag": 0.16, "amount": 16}], "punch": [{"at": "relegated", "amount": 0.12, "dur": 1.2, "x": 540, "y": 1560}]})
# 2 the rule
B.append({"kicker": "The stat", "headline": "[7 points] from 10 games.", "cut": True, "transition": "whip", "scene": S_DARK, "accent": GOLD, "lights": 0.55, "focus": 0.4,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": MID, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "rain", "y": 640, "at": "ten Premier", "lag": -0.4, "groups": [{"n": 10, "color": "#ffffff", "t": 0, "dur": 0.9}], "cols": 10, "cell": 90, "icon": "ball", "empty": 0, "label": "Games", "hideAt": "Here are", "hideLag": -0.1},
           {"type": "big", "at": "seven points", "lag": -0.3, "value": 7, "label": "Points", "y": 1040, "size": 260, "hideAt": "Here are", "hideLag": -0.1},
           fates({i: {"t": 99} for i in range(5)}, y=1250, at="Here are", lag=0.1, title="The last five teams")],
  "punch": [{"at": "Here are", "lag": 0.2, "amount": 0.08, "dur": 1.6, "x": 540, "y": 1150}]})
# 3 trapdoor: Norwich, Fulham
B.append({"kicker": "2019 · 2020", "headline": "Norwich. Fulham. [Gone].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_DARK, "accent": RED, "lights": 0.55, "focus": 0.2, "fans": True,
  "camFrom": {"pos": [16, 16, -34], "tgt": [0, 0, 8]}, "camera": {"pos": [-16, 8, -18], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "trapdoor", "y": 1300, "scale": 1.35, "delay": 0, "clear": False, "items": [{"name": "Norwich · 2019/20", "badge": BG["NOR"], "at": "Norwich", "lag": 1.25}, {"name": "Fulham · 2020/21", "badge": BG["FUL"], "at": "Fulham", "lag": 1.25}]}],
  "shake": [{"at": "Norwich", "lag": 1.3, "amount": 14}, {"at": "Fulham", "lag": 1.3, "amount": 14}], "punch": [{"t": 0.2, "amount": 0.14, "dur": 2.6, "x": 380, "y": 1200}, {"at": "Fulham", "amount": 0.14, "dur": 2.6, "x": 700, "y": 1200}]})
# 4 fates board: Burnley, West Ham
B.append({"kicker": "2021 · 2025", "headline": "Burnley. West Ham. [Gone].", "cut": True, "scene": S_DARK, "accent": RED, "lights": 0.6, "focus": 0.2, "flashes": 10,
  "camFrom": {"pos": [-14, 26, -44], "tgt": [0, 0, 5]}, "camera": {"pos": [12, 12, -24], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [fates({2: {"at": "Burnley", "lag": 0.75}, 3: {"t": 99}, 4: {"at": "West Ham", "lag": 0.75}}, y=950, delay=0, count="relegated")],
  "punch": [{"t": 0, "amount": 0.1, "dur": 1.6, "x": 540, "y": 950}, {"at": "Burnley", "lag": 1.2, "amount": 0.14, "dur": 1.4, "x": 540, "y": 950}, {"at": "West Ham", "lag": 1.2, "amount": 0.12, "dur": 1.0, "x": 900, "y": 950}]})
# 5 Palace survive
B.append({"kicker": "2024/25 · the exception", "headline": "Only [Palace] stayed up.", "cut": True, "transition": "whip", "scene": S_CRY, "accent": GREEN, "confetti": True, "confettiAt": "stayed up", "flashes": 14,
  "orbit": {"center": [0, 1.2, 3], "r": 5.2, "from": -30, "to": 20, "h": 1.4, "h2": 1.9, "dur": 5}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.2, 3]},
  "players": [P(kit=CRY, skin="#8a5a3c", hair="#141010", x=0, z=3, front=True, action="celebrate", pose="fists")],
  "card": [{"type": "trapdoor", "y": 1620, "delay": 0, "clear": False, "items": [{"name": "Crystal Palace · 2024/25", "badge": BG["CRY"], "stay": True, "at": "stayed up", "lag": -0.1}]}]})
# 6 United now
B.append({"kicker": "Man United · 2026/27", "headline": "United: [18th].", "cut": True, "transition": "vhs", "vhsLabel": "NOW", "vhsDur": 0.8, "scene": S_OT, "accent": RED, "lights": 0.5,
  "camFrom": {"pos": [1.4, 1.7, -3.0], "tgt": [0.6, 1.3, 10]}, "camera": {"pos": [0.9, 1.5, -0.6], "tgt": [0.6, 1.3, 10]}, "move": 6, "moveEase": "linear",
  "players": [P(kit=MUN, skin="#e7b593", hair="#3a2a1a", x=1.3, z=2.8, front=True, pose="think")],
  "card": [{"type": "stack", "y": 1150, "shiftX": -230, "delay": 0, "size": 150, "items": [{"value": 10, "label": "Games", "at": "Ten games"}, {"value": 1, "label": "Win", "at": "One win"}, {"value": 8, "label": "Points", "at": "Eight points", "color": RED}]},
           {"type": "table", "y": 1700, "at": "Eighteenth", "lag": -0.5, "label": "Premier League · bottom three", "clear": False,
            "rows": [{"pos": 18, "name": "Man United", "color": "#da291c", "pts": 8, "highlight": True}, {"pos": 19, "name": "Sunderland", "color": "#eb172b", "color2": "#ffffff", "pts": 8}, {"pos": 20, "name": "Crystal Palace", "color": "#1b458f", "color2": "#c4122e", "pts": 7}]}],
  "shake": [{"at": "Eighteenth", "amount": 12}]})
# 7 re-hook: 88 teams
B.append({"kicker": "But here's the hope", "headline": "88 teams. [37 stayed up].", "cut": True, "transition": "whip", "scene": S_DARK, "accent": GREEN, "lights": 0.65, "focus": 0.2,
  "camFrom": {"pos": [-14, 10, -22], "tgt": [0, 0, 8]}, "camera": {"pos": [14, 30, -48], "tgt": [0, 0, 5]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "flytext", "text": "BUT…", "size": 260, "settle": False, "y": 900, "delay": 0, "color": GREEN, "clear": False},
           {"type": "rain", "y": 1100, "at": "Eighty-eight", "lag": -0.3, "cols": 11, "cell": 78, "icon": "dot", "label": "Stayed up", "clear": False,
            "groups": [{"n": 51, "color": "#d6283b", "t": 0, "dur": 1.6}, {"n": 37, "color": GREEN, "at": "Thirty-seven", "lag": -0.4, "dur": 1.0}]}],
  "punch": [{"at": "after ten", "amount": 0.1, "dur": 2.2, "x": 540, "y": 1200}, {"at": "Thirty-seven", "amount": 0.12, "dur": 1.4, "x": 540, "y": 1300}]})
# 8 coin flip
B.append({"kicker": "The odds", "headline": "[42%] survive.", "cut": True, "scene": S_OT, "accent": GOLD, "lights": 0.45, "focus": 0.5,
  "camFrom": {"pos": [-8, 12, -26], "tgt": [0, 0, 8]}, "camera": {"pos": [6, 16, -30], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "coin", "y": 1200, "delay": 0, "text": "42%", "sub": "stayed up", "label": "Almost a coin flip", "landAt": "forty-two", "landLag": 0.25, "clear": False}],
  "shake": [{"at": "forty-two", "lag": 0.3, "amount": 14}]})
# 9 never relegated
B.append({"kicker": "Premier League · since 1992", "headline": "United: [never] relegated.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_OT, "accent": GOLD, "flashes": 16,
  "camFrom": {"pos": [0, 0.9, -2.6], "tgt": [0, 1.5, 4]}, "camera": {"pos": [0, 1.2, -0.4], "tgt": [0, 1.4, 4]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=MUN, skin="#8a5a3c", hair="#141010", x=0, z=4, front=True, enter="walk", fromZ=9, walkDur=3, pose="wings")],
  "card": [{"type": "flytext", "text": "NEVER", "size": 300, "endScale": 0.7, "y": 1500, "at": "never", "lag": -0.2, "color": GOLD, "clear": False},
           {"type": "vs", "y": 1740, "at": "never", "lag": 0.3, "items": [{"label": "PL seasons", "value": 35}, {"label": "Relegations", "value": 0, "accent": True}]}]})
# 10 the question
B.append({"kicker": "Your call", "headline": "Are United in a [relegation fight]?", "cut": True, "scene": S_OT, "accent": RED, "lights": 0.8,
  "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.45, -1.2], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear",
  "players": [P(kit=MUN, skin="#e7b593", hair="#3a2a1a", x=0, z=2.8, front=True, pose="think")],
  "split": {"scene": S_DARK, "lights": 0.4, "camFrom": {"pos": [0, 10, -24], "tgt": [0, 2, 8]}, "camera": {"pos": [0, 6, -16], "tgt": [0, 2, 8]}, "move": 6, "players": []},
  "card": [{"type": "trapdoor", "y": 1050, "shiftX": 270, "dx": 270, "delay": 0.2, "clear": False, "items": [{"name": "United?", "badge": BG["MUN"], "t": 99}]},
           {"type": "poll", "y": 1600, "at": "really", "lag": -0.6, "question": "United in a relegation fight?", "options": [{"label": "Yes, real danger", "color": "#da291c", "fill": 0.5}, {"label": "No chance", "color": "#9aa1ad", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "United and the seven-point omen", "brand": "theo6k", "accent": RED, "voSpeed": 1.08, "beats": B}, open('videos/united-omen/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
