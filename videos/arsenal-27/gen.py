# Builds videos/arsenal-27/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
ARS = {"shirt": "#ef0107", "shorts": "#ffffff", "socks": "#ef0107", "text": "#ffffff"}
BRI = {"shirt": "#ffffff", "shorts": "#0057b8", "socks": "#ffffff", "text": "#0057b8", "stripes": ["#0057b8", "#ffffff"]}
GK = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
S_EM = {"type": "stadium", "crowd": ["#ef0107", "#ffffff", "#ef0107", "#9a0006"], "seed": 5}
S_BRI = {"type": "stadium", "crowd": ["#0057b8", "#ffffff", "#0057b8", "#9fc5ee"], "seed": 18}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
lines = [l.strip() for l in open('videos/arsenal-27/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
BG = {"CHE": {"colors": ["#034694", "#ffffff", "#034694"], "text": "CFC"}, "MCI": {"colors": ["#6cabdd", "#ffffff", "#1c2c5b"], "text": "MCFC"},
      "LIV": {"colors": ["#c8102e", "#f6eb61", "#00b2a9"], "text": "LFC"}, "ARS": {"colors": ["#ef0107", "#ffffff", "#9c824a"], "text": "AFC"}}
HI = {"pos": [0, 30, -50], "tgt": [0, 0, 5]}; MID = {"pos": [0, 18, -32], "tgt": [0, 0, 8]}
def tiles(extra, **k):
    T = [dict(name="Chelsea", sub="2005/06", badge=BG["CHE"], fate="win"), dict(name="Man City", sub="2011/12", badge=BG["MCI"], fate="win"),
         dict(name="Man City", sub="2017/18", badge=BG["MCI"], fate="win"), dict(name="Liverpool", sub="2019/20", badge=BG["LIV"], fate="win"),
         dict(name="Arsenal", sub="2026/27", badge=BG["ARS"], fate="win", t=99)]
    items = [dict(t, **extra.get(i, {})) for i, t in enumerate(T)]
    d = {"type": "fates", "title": "28 points after 10 games", "items": items, "clear": False}; d.update(k); return d
B = []
# 1 hook
B.append({"kicker": "Premier League · the title race", "headline": "Arsenal: [27 points]. Only four teams had more.", "hookWords": True, "scene": S_EM, "accent": GOLD, "lights": 0.75, "flashes": 12,
  "camFrom": {"pos": [0, 1.5, 0.4], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.5, -0.8], "tgt": [0, 1.35, 10]}, "move": 7, "moveEase": "linear",
  "players": [P(kit=ARS, skin="#e7b593", hair="#3a2a1a", x=0, z=3.4, front=True, enter="walk", fromZ=4.6, walkDur=2.4, label="Arsenal · 27 pts", labelDelay=0)],
  "card": [tiles({0: {"t": 0.2}, 1: {"t": 0.5}, 2: {"t": 0.8}, 3: {"t": 1.1}}, y=1560, delay=-0.05, title="More than 27 points after 10 games"),
           {"type": "stamp", "text": "4 OF 4", "sub": "won the league", "at": "All four", "color": GOLD, "rot": -0.08, "size": 100, "y": 1800}],
  "shake": [{"at": "All four", "lag": 0.16, "amount": 14}], "punch": [{"at": "twenty-seven", "amount": 0.1, "dur": 1.2, "x": 540, "y": 1560}]})
# 2 the four champions: trophies rise on each name
def cup(i, at, lab, sub):
    return {"type": "trophies", "at": at, "lag": -0.2, "floor": 1300, "stagger": 0, "rise": 0.55, "items": [{"kind": "cup", "sx": 0.14 + i * 0.24, "h": 230, "size": 170, "label": lab, "text": sub}], "clear": False}
B.append({"kicker": "More than 27 after 10", "headline": "Four teams. [Four titles].", "cut": True, "transition": "whip", "scene": S_DARK, "accent": GOLD, "lights": 0.55, "focus": 0.25,
  "camFrom": {"pos": [-14, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [14, 22, -40], "tgt": [0, 0, 6]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [cup(0, "Chelsea", "Chelsea", "2005/06"), cup(1, "Manchester City, 2011", "Man City", "2011/12"), cup(2, "City again", "Man City", "2017/18"), cup(3, "Liverpool", "Liverpool", "2019/20"),
           {"type": "stamp", "text": "CHAMPIONS", "sub": "every one", "at": "every one", "lag": -0.3, "color": GOLD, "rot": -0.07, "size": 90, "y": 1740}],
  "punch": [{"at": "Liverpool", "lag": 0.2, "amount": 0.1, "dur": 1.6, "x": 540, "y": 1300}]})
# 3 nine wins, one defeat, seven clean sheets: a real save
B.append({"kicker": "Arsenal · 2026/27", "headline": "[9] wins. [1] loss. [7] clean sheets.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_BRI, "accent": GREEN, "hype": False,
  "camFrom": {"pos": [4.2, 2.2, 36], "tgt": [0.2, 1.2, 52]}, "camera": {"pos": [3.4, 2.0, 38.5], "tgt": [0.2, 1.2, 52]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=BRI, skin="#e7b593", hair="#3a2a1a", x=-1.0, z=41, action="kick", actionDelay=2.6, actionDur=0.8),
              P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionDelay=2.65),
              P(kit=ARS, skin="#8a5a3c", hair="#141010", x=1.4, z=45.5, front=True), P(kit=ARS, skin="#f0c8a8", hair="#5a3a22", x=-2.6, z=46.5, front=True)],
  "card": [{"type": "dots", "states": ["hit"] * 9 + ["miss"], "label": "Arsenal's first 10", "y": 760, "step": 0.22, "delay": 0.3, "clear": False},
           {"type": "ball", "delay": 0, "point": [-0.78, 0.11, 41.45], "until": 3.0},
           {"type": "ballpath", "world": True, "delay": 3.0, "dur": 0.6, "slowmo": False, "saveBy": 1, "flash": False, "points": [[-0.78, 0.11, 41.45], [0.6, 1.4, 47], [2.4, 1.3, 52.0]]},
           {"type": "big", "at": "Seven clean", "lag": -0.3, "from": 0, "value": 7, "countDur": 0.9, "label": "Clean sheets", "y": 1620, "size": 240}],
  "shake": [{"at": "Seven clean", "lag": 0.3, "amount": 10}]})
# 4 five clear, Opta 72%
B.append({"kicker": "The table", "headline": "[5 points] clear. [72%] to win it.", "cut": True, "transition": "vhs", "vhsLabel": "TABLE", "vhsDur": 0.8, "scene": S_EM, "accent": GOLD, "lights": 0.55, "focus": 0.4,
  "camFrom": HI, "camera": MID, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "table", "y": 900, "delay": 0, "scale": 1.2, "label": "Premier League · top three", "pill": "+5", "pillRow": 0,
            "rows": [{"pos": 1, "name": "Arsenal", "color": "#ef0107", "color2": "#ffffff", "pts": 27, "highlight": True}, {"pos": 2, "name": "Brighton", "color": "#0057b8", "color2": "#ffffff", "pts": 22}, {"pos": 3, "name": "Man City", "color": "#6cabdd", "pts": 21}], "clear": False},
           {"type": "big", "at": "seventy-two", "lag": -0.3, "from": 0, "value": 72, "suffix": "%", "countDur": 0.9, "label": "Opta: Arsenal title chance", "y": 1560, "size": 240, "clear": False}],
  "punch": [{"at": "Brighton", "amount": 0.1, "dur": 1.4, "x": 540, "y": 1000}, {"at": "seventy-two", "amount": 0.1, "dur": 1.4, "x": 540, "y": 1560}]})
# 5 re-hook
B.append({"kicker": "But here's the problem", "headline": "Sounds perfect. [But].", "cut": True, "transition": "vhs", "vhsLabel": "BUT", "vhsDur": 0.9, "scene": S_EM, "accent": RED, "lights": 0.3,
  "camFrom": {"pos": [1.2, 1.5, -2.8], "tgt": [0.4, 1.3, 10]}, "camera": {"pos": [0.5, 1.4, -0.8], "tgt": [0.4, 1.3, 10]}, "move": 3.5, "moveEase": "linear",
  "players": [P(kit=ARS, skin="#e7b593", hair="#3a2a1a", x=0.9, z=2.8, front=True, pose="think")],
  "card": [{"type": "flytext", "text": "BUT…", "size": 360, "endScale": 0.9, "y": 1450, "delay": 0.3, "color": RED, "clear": False}],
  "shake": [{"at": "problem", "amount": 14}]})
# 6 split: 2022 v 2026, both 27
B.append({"kicker": "2022 · 2026", "headline": "Same start. [27] points.", "cut": True, "transition": "whip", "scene": S_DARK, "accent": GOLD, "lights": 0.6,
  "camFrom": {"pos": [0, 1.5, -2.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.0], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=ARS, skin="#e7b593", hair="#3a2a1a", x=0, z=2.8, front=True)],
  "split": {"scene": S_EM, "lights": 0.8, "camFrom": {"pos": [0, 1.5, -2.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.0], "tgt": [0, 1.3, 10]}, "move": 5,
            "players": [P(kit=ARS, skin="#8a5a3c", hair="#141010", x=0, z=2.8, front=True)], "at": "The same"},
  "card": [{"type": "big", "at": "2022", "lag": -0.2, "from": 0, "value": 27, "countDur": 0.7, "label": "Arsenal · 2022/23", "y": 1500, "shiftX": -270, "size": 190, "clear": False},
           {"type": "big", "at": "The same", "lag": -0.1, "from": 0, "value": 27, "countDur": 0.7, "label": "Arsenal · 2026/27", "y": 1500, "shiftX": 270, "size": 190, "clear": False}]})
# 7 248 days
B.append({"kicker": "2022/23", "headline": "[248] days on top.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_EM, "accent": GOLD, "lights": 0.5, "focus": 0.45,
  "camFrom": HI, "camera": {"pos": [0, 14, -28], "tgt": [0, 0, 8]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "rain", "y": 980, "at": "two hundred", "lag": -0.6, "groups": [{"n": 248, "color": GOLD, "t": 0, "dur": 2.6}], "cols": 20, "cell": 46, "icon": "dot", "label": "Days top of the table", "clear": False},
           {"type": "stamp", "text": "NO TITLE", "sub": "most ever without winning it", "at": "didn't win", "lag": -0.3, "color": RED, "rot": -0.07, "size": 100, "y": 1640}],
  "shake": [{"at": "didn't win", "lag": 0.2, "amount": 14}]})
# 8 second
B.append({"kicker": "2022/23", "headline": "Second. [5 points] behind.", "cut": True, "transition": "whip", "scene": S_DARK, "accent": RED, "lights": 0.4, "focus": 0.35,
  "camFrom": {"pos": [10, 16, -30], "tgt": [0, 0, 8]}, "camera": {"pos": [-8, 9, -20], "tgt": [0, 0, 8]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [{"type": "trapdoor", "y": 1250, "scale": 1.2, "delay": 0, "clear": False, "items": [{"name": "Arsenal · 2022/23", "badge": BG["ARS"], "at": "finished second", "lag": 0.3, "tag": "2ND PLACE", "tagColor": "#6b7280"}]},
           {"type": "big", "at": "Five points", "lag": -0.2, "from": 0, "value": 5, "countDur": 0.6, "label": "points behind Man City", "y": 1700, "size": 200, "clear": False}],
  "shake": [{"at": "finished second", "lag": 0.4, "amount": 14}]})
# 9 never decided after 10
B.append({"kicker": "The season", "headline": "10 games down. [28] to go.", "cut": True, "transition": "vhs", "vhsLabel": "REWIND", "vhsDur": 0.8, "scene": S_EM, "accent": GOLD, "lights": 0.55, "focus": 0.4,
  "camFrom": {"pos": [-10, 20, -34], "tgt": [0, 0, 8]}, "camera": {"pos": [10, 12, -22], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "dots", "n": 38, "filled": 10, "cols": 10, "y": 900, "label": "Premier League season: 38 games", "caption": "28 still to play", "delay": 0.2, "clear": False}],
  "punch": [{"at": "better than anyone", "amount": 0.1, "dur": 1.4, "x": 540, "y": 900}]})
# 10 ending: ballot
B.append({"kicker": "Your call", "headline": "Champions, or [2023 again]?", "cut": True, "transition": "whip", "scene": S_EM, "accent": GOLD, "flashes": 12,
  "orbit": {"center": [0, 1.25, 3], "r": 5, "from": -25, "to": 18, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [P(kit=ARS, skin="#e7b593", hair="#3a2a1a", x=0, z=3.4, front=True, pose="fists", label="Arsenal fans?", labelDelay=0.2)],
  "card": [{"type": "ballot", "y": 1580, "at": "champions", "lag": -0.3, "title": "Champions", "sub": "Arsenal", "color": GOLD, "n": 14, "dur": 2.4, "w": 300, "shiftX": -190},
           {"type": "ballot", "y": 1580, "at": "twenty twenty-three", "lag": -0.2, "title": "2023 again", "sub": "Collapse", "color": RED, "n": 14, "dur": 2.0, "w": 300, "shiftX": 190, "seed": 7}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "Arsenal's 27 points", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open('videos/arsenal-27/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
