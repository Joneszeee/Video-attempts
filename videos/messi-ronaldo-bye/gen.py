# Builds videos/messi-ronaldo-bye/spec.json (run from the repo root).
import json
SKY, RED, GOLD = "#75aadb", "#e03a4e", "#e9b949"
ARG = {"shirt": "#75aadb", "shorts": "#1d1c22", "socks": "#ffffff", "text": "#1d1c22", "stripes": ["#75aadb", "#ffffff"]}
POR = {"shirt": "#c8102e", "shorts": "#0b6b3a", "socks": "#c8102e", "text": "#f1c453"}
BEN = {"shirt": "#f2c200", "shorts": "#f2c200", "socks": "#f2c200", "text": "#0b6b3a"}
BGK = {"shirt": "#2b2f3a", "shorts": "#2b2f3a", "socks": "#2b2f3a", "text": "#ffffff"}
S_ARG = {"type": "stadium", "crowd": ["#75aadb", "#ffffff", "#75aadb", "#f6d44a"], "seed": 10}
S_POR = {"type": "stadium", "crowd": ["#c8102e", "#0b6b3a", "#c8102e", "#f1c453"], "seed": 7}
S_NEU = {"type": "stadium", "crowd": ["#3a4254", "#8a93a6", "#2a3040", "#c9ced6"], "seed": 3}
lines = [l.strip() for l in open('videos/messi-ronaldo-bye/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def messi(**k): return P(name="Messi", num=10, kit=ARG, skin="#e9bd9a", hair="#5a3a22", foot="left", **k)
def cr7(**k): return P(name="Ronaldo", num=7, kit=POR, skin="#d9a67c", hair="#1d1410", **k)
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
B = []
# 1 hook: split screen, a party on the left, a walk-off on the right
B.append({"kicker": "Two goodbyes · 2026", "headline": "Messi got a party. Ronaldo got a [row].", "hookWords": True, "scene": S_ARG, "accent": RED,
  "camFrom": {"pos": [0, 1.5, -2.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.45, -1.3], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear", "flashes": 16,
  "players": [messi(x=0, z=2.6, front=True, chest=True, pose="arms_up")],
  "split": {"scene": S_POR, "lights": 0.5, "camFrom": {"pos": [0, 1.5, -1.2], "tgt": [0, 1.2, 10]}, "camera": {"pos": [0, 1.7, -2.6], "tgt": [0, 1.2, 10]},
            "players": [cr7(x=0, z=2.6)]},
  "card": [{"type": "stamp", "text": "FAREWELL", "sub": "6 Oct 2026", "at": "farewell", "color": GOLD, "rot": -0.1, "size": 62, "dx": -270, "y": 1500},
           {"type": "stamp", "text": "FELL OUT", "sub": "5 Nov 2026", "at": "row", "color": RED, "rot": 0.09, "size": 62, "dx": 266, "y": 1500}]})
# 2 neither of them: two ghosts and a year counter racing back to 2003
B.append({"kicker": "November 2026", "headline": "First time since [2003]: neither.", "cut": True, "transition": "whip", "scene": S_NEU, "lights": 0.6, "accent": GOLD,
  "camFrom": {"pos": [0, 2.2, -5.5], "tgt": [0, 1.2, 10]}, "camera": {"pos": [0, 1.6, -2.4], "tgt": [0, 1.2, 10]}, "move": 6.5, "moveEase": "linear",
  "players": [messi(x=-1.3, z=3, front=True, chest=True, ghost=True), cr7(x=1.3, z=3, front=True, chest=True, ghost=True)],
  "card": [{"type": "big", "at": "first time", "lag": -0.3, "from": 2026, "value": 2003, "countDur": 1.6, "label": "Last break without both of them", "y": 1560, "size": 250}]})
# 3 Messi's last game
pk = [-0.22, 0.11, 41.45]; pend = [2.9, 0.6, 52.8]
B.append({"kicker": "Tuesday · Buenos Aires", "headline": "Messi's last game: [3–0].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ARG, "accent": SKY,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 24, -42], "tgt": [0, 0, 10]}, "move": 3.2, "players": [],
  "card": [{"type": "flip", "y": 760, "at": "sixth", "label": "Argentina v Benin", "groups": [{"label": "October", "value": 6, "digits": 2}], "side": {"top": "TUE", "big": "6", "bottom": "OCT"}}],
  "shots": [{"at": "Messi's last game", "lag": -0.2, "cut": True, "move": 4.5, "moveEase": "linear",
     "camFrom": {"pos": [3.2, 2.0, 33.5], "tgt": [0.4, 1.0, 52]}, "camera": {"pos": [2.4, 1.8, 35.8], "tgt": [0.4, 1.0, 52]},
     "players": [messi(x=0, z=41, action="kick", actionAt="penalty", actionLag=-0.1, actionDur=0.8, after="celebrate", label="Messi", labelDelay=0.2),
                 P(kit=BGK, skin="#6b4630", hair="#141010", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionAt="penalty", actionLag=0.3)],
     "card": [{"type": "ball", "delay": 0, "point": pk, "untilAt": "penalty", "untilLag": 0.24},
              {"type": "ballpath", "world": True, "at": "penalty", "lag": 0.24, "dur": 0.5, "slowmo": False, "points": [pk, mid(pk, pend, 1.0), pend]},
              {"type": "stack", "y": 1640, "delay": 0, "size": 150, "items": [{"value": 1, "label": "Goal · penalty", "at": "penalty", "lag": 0.6}, {"value": 2, "label": "Assists", "at": "two assists"}, {"value": 3, "label": "Argentina 3–0 Benin", "at": "three–nil", "suffix": "–0", "gold": True}]}],
     "confetti": True, "confettiAt": "three–nil", "confettiColors": ["#75aadb", "#ffffff", "#f6d44a"]}]})
# 4 126 in 208, and a World Cup: orbit celebration
B.append({"kicker": "Lionel Messi · Argentina", "headline": "126 goals. 208 games. [A World Cup].", "cut": True, "scene": S_ARG, "accent": GOLD, "flashes": 16,
  "orbit": {"center": [0, 1.25, 2.4], "r": 4.4, "from": -32, "to": 18, "h": 1.3, "h2": 1.7, "dur": 6.5}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.25, 2.4]},
  "players": [messi(x=0, z=2.4, front=True, chest=True, pose="fists")],
  "card": [{"type": "stack", "y": 1600, "delay": 0, "size": 170, "items": [{"value": 126, "label": "Goals for Argentina", "at": "hundred and twenty-six"}, {"value": 208, "label": "Games", "at": "two hundred and eight"}], "hideAt": "World Cup", "hideLag": -0.25},
           {"type": "trophies", "at": "World Cup", "lag": -0.25, "floor": 1880, "stagger": 0, "rise": 0.55, "items": [{"kind": "worldcup", "sx": 0.5, "h": 150, "size": 230, "label": "World Cup winner · 2022"}]}],
  "confetti": True, "confettiAt": "World Cup", "confettiColors": ["#75aadb", "#ffffff", "#f6d44a"]})
# 5 re-hook: nothing like that
B.append({"kicker": "Cristiano Ronaldo · Portugal", "headline": "Ronaldo's goodbye? [Nothing like it].", "cut": True, "transition": "vhs", "vhsLabel": "RONALDO", "vhsDur": 1.0, "scene": S_POR, "lights": 0.42, "accent": RED,
  "camFrom": {"pos": [0.9, 1.7, -2.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.2, 1.5, -0.4], "tgt": [0, 1.35, 10]}, "move": 4, "moveEase": "linear",
  "players": [cr7(x=0, z=2.4, front=True, chest=True)],
  "punch": [{"at": "nothing", "amount": 0.14, "dur": 1.4}], "shake": [{"at": "nothing", "amount": 12}]})
# 6 fell out with Jorge Jesus; 30-day suspension (calendar)
B.append({"kicker": "Portugal camp", "headline": "He fell out with [the coach].", "cut": True, "scene": S_POR, "lights": 0.7, "accent": RED,
  "camFrom": {"pos": [0, 1.6, -1.6], "tgt": [0, 1.25, 10]}, "camera": {"pos": [0, 1.5, -0.8], "tgt": [0, 1.25, 10]}, "move": 4, "moveEase": "linear",
  "players": [cr7(x=-1.25, z=3, front=True, chest=True, label="Ronaldo", labelDelay=0.2),
              P(outfit="suit", suitColor="#20232c", tie="#0b6b3a", skin="#e2b08c", hair="#c9c9c9", x=1.25, z=3, front=True, label="Jorge Jesus", labelAt="Jorge Jesus", at="new coach", lag=-0.2, enter="walk", fromX=7, fromZ=3, walkDur=1.0)],
  "card": [{"type": "pen", "delay": 0, "strokes": [{"kind": "x", "cx": 540, "cy": 960, "r": 70, "at": "fell out", "color": RED, "width": 14},
                                                   {"kind": "text", "text": "FELL OUT", "x": 330, "y": 1500, "size": 96, "rot": -0.05, "at": "fell out", "lag": 0.25, "color": RED}]}],
  "shots": [{"at": "A thirty-day", "lag": -0.25, "cut": True, "lights": 0.5, "focus": 0.6, "move": 3.5, "moveEase": "linear",
     "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 22, -38], "tgt": [0, 0, 8]}, "players": [],
     "card": [{"type": "crossoff", "y": 1160, "delay": 0, "title": "Suspended", "days": 30, "cols": 6, "crossT": 0.35, "dur": 1.5, "caption": "{n} days", "clear": False}]}]})
# 7 5 November, at 41: done. In a video (phone)
B.append({"kicker": "Thursday · 5 November 2026", "headline": "At 41, he's [done]. In a video.", "cut": True, "transition": "whip", "scene": S_POR, "lights": 0.6, "focus": 0.25, "accent": RED, "flashes": 10,
  "camFrom": {"pos": [0, 44, -74], "tgt": [0, 0, 6]}, "camera": {"pos": [0, 12, -24], "tgt": [0, 0, 10]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 660, "at": "fifth", "lag": -0.2, "label": "Retirement announced", "groups": [{"label": "November", "value": 5, "digits": 2}, {"label": "Age", "value": 41, "digits": 2}]},
           {"type": "phone", "y": 1400, "at": "announced", "lag": -0.3, "h": 860, "w": 490, "tag": "Video", "caption": "5 Nov 2026\nInternational retirement", "bg": ["#3a1218", "#0d0f14"],
            "player": {"name": "Ronaldo", "num": 7, "kit": POR, "skin": "#d9a67c", "hair": "#1d1410"}, "clear": False}],
  "punch": [{"at": "In a video", "amount": 0.1, "dur": 1.3, "x": 540, "y": 1400}]})
# 8 146: the men's record, built from footballs
B.append({"kicker": "Cristiano Ronaldo · Portugal", "headline": "[146] goals. The men's record.", "cut": True, "scene": S_POR, "lights": 0.85, "accent": GOLD, "flashes": 12,
  "camFrom": {"pos": [0, 1.9, -5.2], "tgt": [0, 1.9, 10]}, "camera": {"pos": [0, 1.7, -3.2], "tgt": [0, 1.9, 10]}, "move": 5, "moveEase": "linear",
  "players": [cr7(x=0, z=3.4, front=True, chest=True, pose="arms_up")],
  "card": [{"type": "ballnumber", "text": "146", "y": 760, "size": 330, "at": "hundred and forty-six", "lag": -0.5, "label": "{n} goals for Portugal", "count": 146},
           {"type": "stamp", "text": "RECORD", "sub": "men's international football", "at": "The most", "color": GOLD, "rot": -0.08, "size": 90, "y": 1640}]})
# 9 23 years v 21 years: timeline
B.append({"kicker": "Two careers", "headline": "23 years. [21 years].", "cut": True, "scene": S_NEU, "lights": 0.8, "accent": SKY,
  "camFrom": {"pos": [0.8, 1.6, -3.0], "tgt": [0, 1.2, 10]}, "camera": {"pos": [-0.6, 1.5, -2.0], "tgt": [0, 1.2, 10]}, "move": 5, "moveEase": "linear",
  "players": [cr7(x=-1.3, z=3, front=True, chest=True, tag=23, tagLabel="Years", tagAt="Twenty-three", label="2003–2026", labelAt="Twenty-three"),
              messi(x=1.3, z=3, front=True, chest=True, tag=21, tagLabel="Years", tagAt="Twenty-one", label="2005–2026", labelAt="Twenty-one")],
  "card": [{"type": "tape", "y": 1620, "delay": 0, "left": {"name": "Ronaldo", "color": "#c8102e"}, "right": {"name": "Messi", "color": SKY},
            "rows": [{"label": "Years of international football", "left": 23, "right": 21, "at": "Twenty-one", "floor": 15}]}]})
# 10 272 together: sky-blue and red balls rain in
B.append({"kicker": "Between them", "headline": "Together: [272] goals.", "cut": True, "scene": S_NEU, "lights": 0.5, "focus": 0.5, "accent": GOLD,
  "camFrom": {"pos": [0, 34, -56], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 24, -40], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "rain", "y": 1000, "delay": 0, "cols": 16, "cell": 56, "icon": "ball", "label": "International goals", "clear": False,
            "groups": [{"n": 126, "color": SKY, "t": 0, "dur": 1.1}, {"n": 146, "color": RED, "t": 1.2, "dur": 1.3}]}],
  "punch": [{"at": "international goals", "amount": 0.12, "dur": 1.6, "x": 540, "y": 1100}], "shake": [{"at": "international goals", "lag": 0.5, "amount": 14}], "flashes": 12})
# 11 final answer: split screen again, with a poll
B.append({"kicker": "Your call", "headline": "Final answer: [Messi or Ronaldo]?", "cut": True, "scene": S_ARG, "accent": GOLD, "flashes": 12,
  "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.45, -1.4], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear",
  "players": [messi(x=0, z=2.6, front=True, chest=True, pose="fists")],
  "split": {"scene": S_POR, "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.45, -1.4], "tgt": [0, 1.3, 10]},
            "players": [cr7(x=0, z=2.6, front=True, chest=True, pose="arms_up")], "at": "who was", "lag": -0.6},
  "card": [{"type": "poll", "y": 1580, "at": "Messi or Ronaldo", "lag": -0.6, "question": "Better international?", "options": [{"label": "Messi", "color": SKY, "fill": 0.5}, {"label": "Ronaldo", "color": "#c8102e", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
spec = {"title": "Messi and Ronaldo say goodbye", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}
json.dump(spec, open('videos/messi-ronaldo-bye/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
