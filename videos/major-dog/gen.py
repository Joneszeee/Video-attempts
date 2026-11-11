# Builds videos/major-dog/spec.json (run from the repo root).
import json
RED, GOLD, GRN = "#ff4d5e", "#e9b949", "#3fbf6a"
NH = {"shirt": "#1f7a3a", "shorts": "#1d1c22", "socks": "#1d1c22", "text": "#f1c453", "stripes": ["#1f7a3a", "#f1c453"]}
MUN = {"shirt": "#da291c", "shorts": "#ffffff", "socks": "#111111", "text": "#ffffff"}
S_OT = {"type": "stadium", "crowd": ["#da291c", "#ffffff", "#111111", "#da291c"], "seed": 7}
S_NH = {"type": "stadium", "crowd": ["#1f7a3a", "#f1c453", "#5a4a30", "#2a2418"], "seed": 3}
S_TOWN = {"type": "stadium", "crowd": ["#3a3020", "#6a5a3a", "#2a2418", "#8a7a5a"], "seed": 15}
lines = [l.strip() for l in open('videos/major-dog/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def stafford(**k): return P(kit=NH, skin="#efc9a8", hair="#3a2a1a", **k)
def davies(**k): return P(outfit="suit", suitColor="#2a2622", tie="#6a4a1e", skin="#efc9a8", hair="#8a8a8a", **k)
CAM = {"camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.2, 10]}, "camera": {"pos": [0, 1.5, -2.2], "tgt": [0, 1.2, 10]}}
B = []
# 1 hook: Major trots across Old Trafford
B.append({"kicker": "Manchester United · 1901", "headline": "United exist because a [dog got lost].", "hookWords": True, "scene": S_OT, "accent": GOLD, "flashes": 12,
  "camFrom": {"pos": [0, 2.0, -5], "tgt": [0, 1.0, 10]}, "camera": {"pos": [0, 1.7, -3.2], "tgt": [0, 1.0, 10]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "dog", "y": 1380, "delay": -1.0, "from": -260, "to": 620, "dur": 3.2, "scale": 1.5, "box": True, "sitAfter": True, "label": "Major", "clear": False},
           {"type": "stamp", "text": "LOST", "sub": "1901", "at": "got lost", "color": RED, "rot": -0.1, "size": 110, "y": 1720}],
  "shake": [{"at": "got lost", "lag": 0.16, "amount": 12}]})
# 2 1901, Newton Heath, the debt
B.append({"kicker": "1901 · Newton Heath", "headline": "£2,670 in [debt].", "cut": True, "transition": "polaroid", "polaroidLabel": "1901", "scene": S_NH, "accent": RED, "lights": 0.6, "focus": 0.45,
  "camFrom": {"pos": [0, 34, -56], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 16, -28], "tgt": [0, 0, 8]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "ledger", "y": 1130, "at": "Newton Heath", "lag": -0.4, "title": "Newton Heath F.C.", "sub": "Accounts · 1901", "step": 0.5,
            "rows": [["Wages owed", "unpaid"], ["Ground rent", "overdue"]], "total": {"label": "TOTAL DEBT", "value": 2670}, "clear": False}]})
# 3 Stafford and Major
B.append(dict({"kicker": "The captain", "headline": "Harry Stafford and [Major].", "cut": True, "transition": "whip", "scene": S_NH, "accent": GOLD, "lights": 0.9, "move": 4, "moveEase": "linear",
  "players": [stafford(x=-1.3, z=3, front=True, chest=True, label="Harry Stafford", labelAt="Harry Stafford")],
  "card": [{"type": "dog", "mode": "sit", "y": 1420, "shiftX": 210, "at": "St Bernard", "lag": -0.3, "scale": 1.25, "label": "Major", "dir": -1, "clear": False}]}, **CAM))
# 4 the bazaar: coins in the box
B.append({"kicker": "The fundraising bazaar", "headline": "A [collection box] on his collar.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_TOWN, "accent": GOLD, "lights": 0.8,
  "camFrom": {"pos": [3, 2.4, -6], "tgt": [0, 1.0, 10]}, "camera": {"pos": [-2, 2.0, -4.5], "tgt": [0, 1.0, 10]}, "move": 5, "moveEase": "linear",
  "players": [P(kit={"shirt": "#5a4a30", "shorts": "#2a2418", "socks": "#2a2418", "text": "#fff"}, skin="#efc9a8", hair="#3a2a1a", x=-4, z=7, front=True),
              P(kit={"shirt": "#6a2a2a", "shorts": "#2a2418", "socks": "#2a2418", "text": "#fff"}, skin="#d9a37c", hair="#141010", x=3.5, z=8, front=True, pose="arms_up")],
  "card": [{"type": "dog", "y": 1400, "delay": 0, "from": -260, "to": 1340, "dur": 6, "scale": 1.35, "box": True, "coins": True, "coinN": 10, "coinStep": 0.42, "clear": False}]})
# 5 need £1,000: not close
B.append({"kicker": "The target", "headline": "They needed [£1,000].", "cut": True, "scene": S_NH, "accent": RED, "lights": 0.5, "focus": 0.4,
  "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 18, -32], "tgt": [0, 0, 8]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [{"type": "big", "delay": 0, "value": 1000, "prefix": "£", "comma": True, "label": "Needed to save the club", "y": 980, "size": 250},
           {"type": "stamp", "text": "NOT ENOUGH", "at": "don't get close", "lag": -0.1, "color": RED, "rot": -0.08, "size": 100, "y": 1420}],
  "shake": [{"at": "don't get close", "lag": 0.06, "amount": 14}]})
# 6 Major disappears
B.append({"kicker": "One night", "headline": "Major [disappears].", "cut": True, "transition": "vhs", "vhsLabel": "THEN", "vhsDur": 0.8, "scene": S_TOWN, "accent": RED, "lights": 0.35,
  "camFrom": {"pos": [0, 2.0, -5], "tgt": [0, 1.0, 10]}, "camera": {"pos": [0, 1.8, -4], "tgt": [0, 1.0, 10]}, "move": 3, "moveEase": "linear", "players": [],
  "card": [{"type": "dog", "y": 1380, "delay": -0.6, "from": 420, "to": 1500, "dur": 2.6, "scale": 1.35, "box": True, "clear": False},
           {"type": "flytext", "text": "GONE", "size": 300, "endScale": 0.7, "y": 1380, "at": "disappears", "color": RED, "clear": False}]})
# 7 Davies
B.append(dict({"kicker": "The brewer", "headline": "He ends up with [J. H. Davies].", "cut": True, "transition": "whip", "scene": S_TOWN, "accent": GOLD, "lights": 0.85, "move": 5, "moveEase": "linear",
  "players": [davies(x=1.3, z=3, front=True, at="wealthy brewer", lag=-0.2, enter="walk", fromX=7, fromZ=3, walkDur=1.0, label="John Henry Davies", labelAt="John Henry")],
  "card": [{"type": "dog", "mode": "sit", "y": 1420, "shiftX": -210, "delay": 0.1, "scale": 1.25, "box": True, "label": "Major", "clear": False}]}, **CAM))
# 8 the conversation
B.append(dict({"kicker": "The conversation", "headline": "The dog, and the [debts].", "cut": True, "scene": S_NH, "accent": RED, "lights": 0.7, "move": 6, "moveEase": "linear",
  "players": [davies(x=-1.5, z=3, front=True, label="Davies", labelDelay=0.2), stafford(x=1.5, z=3, front=True, label="Stafford", labelDelay=0.4)],
  "card": [{"type": "dog", "mode": "sit", "y": 1560, "delay": 0.2, "scale": 0.95, "clear": False},
           {"type": "flytext", "text": "£2,670", "size": 190, "endScale": 0.6, "y": 760, "at": "debts", "lag": -0.3, "color": RED, "clear": False}],
  "punch": [{"at": "Stafford tells", "amount": 0.1, "dur": 1.6}]}, **CAM))
# 9 the deal
B.append({"kicker": "The deal", "headline": "Davies keeps Major. The club gets [his money].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_NH, "accent": GRN, "lights": 0.5, "focus": 0.45,
  "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 16, -28], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "receipt", "y": 1100, "delay": 0, "title": "THE DEAL", "sub": "Stafford ⇄ Davies", "step": 0.6,
            "lines": [["Major", "→ Davies"], ["Investment", "→ the club", True]], "total": ["CLUB", "SAVED"], "clear": False},
           {"type": "stamp", "text": "DEAL", "at": "puts his money", "lag": 0.3, "color": GRN, "rot": -0.1, "size": 120, "y": 1640}]})
# 10 Manchester United, champions
B.append({"kicker": "1902", "headline": "Newton Heath become [Manchester United].", "cut": True, "scene": S_OT, "accent": RED, "lights": 0.8, "focus": 0.3, "flashes": 12,
  "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 20, -34], "tgt": [0, 0, 8]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [{"type": "shirtflip", "y": 1080, "delay": 0, "flipAt": "become", "flipLag": -0.2, "from": {"color": "#1f7a3a", "color2": "#f1c453", "name": "Newton Heath"}, "to": {"color": "#da291c", "color2": "#ffffff", "name": "Manchester United"}, "clear": False}],
  "shots": [{"at": "Six years later", "lag": -0.1, "cut": True, "transition": "whip", "focus": 0, "lights": 1, "flashes": 16,
     "orbit": {"center": [0, 1.25, 2.6], "r": 4.4, "from": -26, "to": 14, "h": 1.3, "h2": 1.7, "dur": 3.5}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.25, 2.6]},
     "players": [P(kit=MUN, skin="#efc9a8", hair="#3a2a1a", x=0, z=2.6, front=True, pose="arms_up", trophy=True)],
     "card": [{"type": "stamp", "text": "CHAMPIONS", "sub": "1908 · first league title", "at": "champions", "lag": -0.3, "color": GOLD, "rot": -0.07, "size": 96, "y": 1640}],
     "confetti": True, "confettiDelay": 0.2, "confettiColors": ["#da291c", "#ffffff", "#f1c453"]}]})
# 11 poll
B.append({"kicker": "Your call", "headline": "Busby, Fergie… or a [St Bernard]?", "cut": True, "transition": "whip", "scene": S_OT, "accent": GOLD, "flashes": 10,
  "camFrom": {"pos": [0, 2.0, -5], "tgt": [0, 1.0, 10]}, "camera": {"pos": [0, 1.8, -3.6], "tgt": [0, 1.0, 10]}, "move": 8, "moveEase": "linear", "players": [],
  "punch": [{"at": "St Bernard", "amount": 0.12, "dur": 1.8, "x": 540, "y": 1100}, {"t": 5.6, "amount": 0.08, "dur": 1.6, "x": 540, "y": 1300}], "confetti": True, "confettiAt": "St Bernard", "confettiColors": ["#da291c", "#ffffff", "#e9b949"],
  "card": [{"type": "dog", "mode": "sit", "y": 1130, "delay": 0, "scale": 1.3, "box": True, "label": "Major", "clear": False},
           {"type": "poll", "y": 1570, "at": "Busby", "lag": -0.4, "question": "United's most important figure?", "options": [{"label": "Busby", "color": "#da291c", "fill": 0.34}, {"label": "Fergie", "color": "#9aa1ad", "fill": 0.34}, {"label": "Major the dog", "color": "#e9b949", "fill": 0.34}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
json.dump({"title": "The dog that saved Manchester United", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open('videos/major-dog/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
