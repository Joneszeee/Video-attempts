# Builds videos/city-squad-update/spec.json (run from the repo root). Man City in League Two, squad update between Parts 4 and 5: the starting XI as collectible-style cards.
# Ratings and stats come from videos/city-league-two/data/squad.json (squad.py, seed 2030 fixed before running): the rating is 60 + 80 x the goals per game a player adds v an average League One
# player in his slot (Part 4 model); Haaland's goals are the sim's own (29 + 29 + 13), everyone else's goals and assists are shared out after the fact by the model's attack weights.
import json
import sys
sys.path.insert(0, 'engine')
from lib import *

Q = json.load(open('videos/city-league-two/data/squad.json')); R, ST = Q['ratings'], Q['stats']
# --- every number the voice says, checked against the data (a wrong number stops the build)
assert R['Haaland']['ovr'] == 91 and R['Scarr']['ovr'] == 57 and min(v['ovr'] for v in R.values()) == 57 and max(v['ovr'] for v in R.values()) == 91
assert round(sum(v['ovr'] for v in R.values()) / 11) == 69
assert ST['Scarr']['all']['cs'] == 26 and R['Watts']['ovr'] == 59 and R['Braybrooke']['ovr'] == 59 and R['Iroegbunam']['ovr'] == 71
assert R['McAidoo']['ovr'] == 61 and R['T. Samba']['ovr'] == 61 and ST['T. Samba']['all']['goals'] == 31 and ST['Foden']['all']['goals'] == 22 and ST['T. Samba']['all']['goals'] > ST['Foden']['all']['goals']
assert R['McCracken']['ovr'] == 66 and ST['McCracken']['now']['cs'] == 6 and ST['McCracken']['all'] == {k: ST['McCracken']['now'][k] for k in ST['McCracken']['all']}
assert R['Lewis']['ovr'] == 75 and R["O'Reilly"]['ovr'] == 75 and ST["O'Reilly"]['now']['goals'] == 7
assert R['Foden']['ovr'] == 82 and ST['Foden']['all']['goals'] == 22 and ST['Foden']['all']['assists'] == 20
assert ST['Haaland']['all']['goals'] == 71 and ST['Haaland']['all']['apps'] == 100 and ST['Haaland']['now']['goals'] == 13

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
BADGE = {"colors": [SKY, "#1c2c5b", "#ffffff"], "text": "MCI"}
S_WEM = stadium([SKY, "#ffffff", "#7a1428", "#f5b301"], 41)
S_ETI = stadium([SKY, "#ffffff", SKY, "#1c2c5b"], 6)
S_NIGHT = stadium(["#ffffff", "#1c2c5b", SKY], 9)
S_GOLD = stadium(["#f1c453", "#ffffff", "#1c2c5b", SKY], 12)
S_SIM = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], 21)
LOOK = {'Haaland': dict(skin="#f1d3bd", hair="#d9b46a"), 'Foden': dict(skin="#f0c8a8", hair="#3a2a1a"), 'Lewis': dict(skin="#8a5a3c", hair="#141010"),
        "O'Reilly": dict(skin="#f0c8a8", hair="#6a4a2a"), 'Iroegbunam': dict(skin="#8a5a3c", hair="#141010"), 'McCracken': dict(skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2"),
        'Watts': dict(skin="#e7b593", hair="#2a1a10"), 'Scarr': dict(skin="#e7b593", hair="#141010"), 'Braybrooke': dict(skin="#f0c8a8", hair="#6a4a2a"),
        'McAidoo': dict(skin="#e7b593", hair="#3a2a1a"), 'T. Samba': dict(skin="#8a5a3c", hair="#141010")}
SHOW = {'T. Samba': 'SAMBA'}
POSLAB = {'Iroegbunam': 'DM', 'Braybrooke': 'DM'}
rar = lambda ovr: 'elite' if ovr >= 85 else 'gold' if ovr >= 75 else 'silver' if ovr >= 65 else 'bronze'
SEED = {n: i * 5 + 1 for i, n in enumerate(R)}

def rows(nm):
    pos, a, n = R[nm]['pos'], ST[nm]['all'], ST[nm]['now']
    def cells(x):
        if pos == 'GK': return [[x['apps'], 'gp'], [x['cs'], 'cs'], [x['conceded'], 'gc']]
        if pos == 'CB': return [[x['apps'], 'gp'], [x['cs'], 'cs'], [x['goals'], 'g']]
        return [[x['apps'], 'gp'], [x['goals'], 'g'], [x['assists'], 'a']]
    out = [{"label": "This season", "cells": cells(n)}]
    if a['apps'] != n['apps']: out.append({"label": "All-time", "cells": cells(a)})
    return out

def card(nm, dx=0, scale=0.8, y=1110, entry="flip", ribbon=None, **k):
    gk = R[nm]['pos'] == 'GK'
    d = {"type": "scard", "y": y, "name": SHOW.get(nm, nm), "pos": POSLAB.get(nm, R[nm]['pos']), "ovr": R[nm]['ovr'], "rarity": rar(R[nm]['ovr']),
         "player": dict(kit=kit("#f7d117", "#111111", "#f7d117", text="#111111") if gk else CITY, name="", num=None, **LOOK[nm]), "badge": BADGE, "rows": rows(nm),
         "foot": "sim rating · sim stats", "entry": entry, "dx": dx, "scale": scale, "seed": SEED[nm], "clear": False}
    if ribbon: d["ribbon"] = ribbon
    d.update(k)
    return d

V, lines = start('videos/city-squad-update/')
B = []
SQ = lambda: hud("Squad update · simulated", counter=False)

# 1 hook: the best card (91) and the worst (57) side by side, already in place and shining on frame 0
B.append({"kicker": "Man City in League Two · Squad update", "headline": "Haaland: [91]. City's worst starter: [57].", "hookWords": True, "scene": S_WEM, "accent": TEAL, "lights": 0.8, "focus": 0.35,
  "flashes": 14, "hype": False, "camFrom": {"pos": [0, 1.6, -4.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.4], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [card('Haaland', dx=-252, scale=0.9, y=1130, entry="left", delay=-1.25, snap=True), card('Scarr', dx=252, scale=0.9, y=1130, entry="right", delay=-1.25, snap=True), SQ()],
  "speedlines": [{"t": 0.0, "dur": 0.9, "amount": 0.7}]})

# 2 the rules: 60 is an average League One player; the four card colours
LEG = [("<65", "bronze", -345, 57), ("65+", "silver", -115, 66), ("75+", "gold", 115, 75), ("85+", "elite", 345, 91)]
B.append({"kicker": "How the ratings work", "headline": "Rated by [the model].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [26, 30, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 16, -24], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [SQ(), big(60, "Sixty is", "= an average League One player", frm=40, y=700, size=200, dur=0.7, lag=-0.1, style="accent")] +
          [{"type": "scard", "mini": True, "y": 1230, "scale": 0.42, "dx": dx, "ovr": txt, "pos": name, "rarity": name, "entry": "drop", "at": "Every starter", "lag": round(0.0 + i * 0.14, 2), "clear": False, "seed": i * 3 + 2}
           for i, (txt, name, dx, _) in enumerate(LEG)]})

# 3 centre-backs: the worst (Scarr, 26 clean sheets) and Watts, your pick
B.append({"kicker": "Centre-backs", "headline": "Centre-backs: [57] and [59].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": TEAL, "lights": 0.7, "focus": 0.35,
  "camFrom": {"pos": [-1.2, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.8, 1.6, -2.0], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [SQ(), card('Scarr', dx=-235, entry="left", at="Scarr", lag=-0.1), card('Watts', dx=235, entry="right", at="Watts", lag=-0.1, ribbon="Fan pick"),
           stamp("26 CLEAN SHEETS", "twenty-six clean sheets", sub="Scarr · three seasons", color=GREEN, y=1500, size=62, lag=-0.05)]})

# 4 midfield: Braybrooke (59) drops in, Iroegbunam (71, your pick) zooms in
B.append({"kicker": "Midfield", "headline": "Midfield: [59] and [71].", "cut": True, "transition": "whip", "scene": S_NIGHT, "accent": TEAL, "lights": 0.7, "focus": 0.35,
  "camFrom": {"pos": [1.4, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [-0.8, 1.6, -2.0], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [SQ(), card('Braybrooke', dx=-235, y=1200, tilt=-0.06, entry="drop", at="Braybrooke", lag=-0.1), card('Iroegbunam', dx=235, y=1020, tilt=0.06, entry="zoom", at="Iroegbunam", lag=-0.1, ribbon="Fan pick")]})

# 5 re-hook (pattern break on the stage): the kids on the wings; Samba has more goals than Foden
B.append({"kicker": "The wingers", "headline": "The wingers: [61] each.", "cut": True, "transition": "vhs", "vhsLabel": "WAIT", "vhsDur": 0.9, "scene": {"type": "stage"}, "accent": GOLD,
  "zoomFrom": 1.0, "zoom": 1.1, "lights": 0.75, "players": [],
  "card": [SQ(), card('McAidoo', dx=-220, scale=0.8, y=1110, tilt=-0.07, entry="left", at="The kids", lag=-0.1), card('T. Samba', dx=220, scale=0.8, y=1110, tilt=0.07, entry="right", at="Samba", lag=-0.35),
           stamp("31 v 22", "more than Foden", sub="Samba v Foden · all-time goals", color=GOLD, y=1500, size=100, lag=-0.05)]})

# 6 in goal: McCracken (66, your pick), one stat row because he only has one season
B.append({"kicker": "In goal", "headline": "In goal: [McCracken], 66.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ETI, "accent": TEAL, "lights": 0.7, "focus": 0.35,
  "camFrom": {"pos": [0, 1.6, -4.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.2], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear", "players": [], "flashes": 10,
  "card": [SQ(), card('McCracken', scale=1.0, y=1140, entry="flip", at="McCracken", lag=-0.1, ribbon="Fan pick")]})

# 7 full-backs: two golds; confetti and flashes; the left-back's seven goals
B.append({"kicker": "Full-backs", "headline": "Full-backs: [75] each.", "cut": True, "transition": "whip", "scene": S_GOLD, "accent": GOLD, "lights": 0.8, "focus": 0.35,
  "camFrom": {"pos": [-1.0, 1.6, -3.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [1.0, 1.6, -2.0], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear", "players": [],
  "confetti": True, "confettiAt": "Seventy-five each", "flashes": 14,
  "card": [SQ(), card('Lewis', dx=-235, entry="left", at="Lewis", lag=-0.1), card("O'Reilly", dx=235, entry="right", at="O'Reilly", lag=-0.1),
           stamp("7 GOALS", "seven goals", sub="O'Reilly · left-back · this season", color=GOLD, y=1500, size=84, lag=-0.05)]})

# 8 Foden (82): gold, zoom entry
B.append({"kicker": "Attacking midfield", "headline": "Foden: [82].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_NIGHT, "accent": GOLD, "lights": 0.8, "focus": 0.35,
  "camFrom": {"pos": [0, 1.6, -4.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.2], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [], "flashes": 12,
  "card": [SQ(), card('Foden', scale=1.0, y=1140, entry="zoom", at="Foden", lag=-0.1)]})

# 9 Haaland (91): the elite card on the stage, rays and sparkles, 71 goals counting up
B.append({"kicker": "The star", "headline": "The star: [71 goals].", "cut": True, "transition": "whip", "scene": {"type": "stage"}, "accent": GOLD, "zoomFrom": 1.0, "zoom": 1.12, "lights": 0.8, "players": [],
  "confetti": True, "confettiAt": "Seventy-one goals",
  "card": [SQ(), card('Haaland', scale=1.0, y=1110, entry="drop", at="And Haaland", lag=-0.1),
           big(71, "Seventy-one goals", "in 100 games · 13 this season", frm=0, y=1590, size=120, dur=1.0, lag=-0.2)],
  "speedlines": [{"at": "Seventy-one goals", "dur": 1.0}], "shake": [{"at": "And Haaland", "lag": 0.3, "amount": 14}]})

# 10 the team: the XI with every rating, a red ring on midfield, and the poll
RC = {"bronze": ("#d8a070", "#2b1a0e"), "silver": ("#e4e8ee", "#1c2430"), "gold": ("#f1c453", "#3a2a06"), "elite": ("#22305f", "#f1c453")}
XY = {'Haaland': (0.5, 0.12), 'Foden': (0.5, 0.32), 'McAidoo': (0.82, 0.3), 'T. Samba': (0.18, 0.3), 'Iroegbunam': (0.35, 0.5), 'Braybrooke': (0.65, 0.5), 'Lewis': (0.86, 0.66),
      "O'Reilly": (0.14, 0.66), 'Watts': (0.36, 0.72), 'Scarr': (0.64, 0.72), 'McCracken': (0.5, 0.9)}
items = []
for nm, (x, y) in XY.items():
    col, ink = RC[rar(R[nm]['ovr'])]
    it = {"name": SHOW.get(nm, nm).title() if nm == 'T. Samba' else nm, "x": x, "y": y, "color": col, "ink": ink, "ovr": R[nm]['ovr']}
    if nm == 'Braybrooke': it["warnAt"] = "fixes midfield"
    items.append(it)
B.append({"kicker": "The team", "headline": "The team: [69].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.35,
  "camFrom": {"pos": [-30, 26, -40], "tgt": [0, 0, 5]}, "camera": {"pos": [24, 20, -34], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "lineup", "y": 910, "delay": 0.0, "w": 660, "title": "City · XI average 69", "clear": False, "instant": True, "items": items}, SQ(),
           {"type": "poll", "y": 1560, "at": "Vote in the poll", "lag": -0.2, "question": "Who should City sign?", "clear": False,
            "options": [{"label": "Phillips", "color": "#d71920", "fill": 0.34}, {"label": "Ward-Prowse", "color": "#9a1c24", "fill": 0.33}, {"label": "Norwood", "color": "#1b4fb5", "fill": 0.33}]}]})

save(V, B, lines, "Man City in League Two · Squad update", accent=TEAL)
