# Builds videos/italy-collapse/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
ITA = {"shirt": "#0b5fc0", "shorts": "#ffffff", "socks": "#0b5fc0", "text": "#ffffff"}
BEL = {"shirt": "#c8102e", "shorts": "#c8102e", "socks": "#c8102e", "text": "#fdda24"}
BOS = {"shirt": "#1c2c7a", "shorts": "#1c2c7a", "socks": "#1c2c7a", "text": "#fdda24"}
GKI = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
GKB = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
S_BEL = {"type": "stadium", "crowd": ["#c8102e", "#fdda24", "#111111", "#c8102e"], "seed": 26}
S_ITA = {"type": "stadium", "crowd": ["#0b5fc0", "#ffffff", "#0b5fc0", "#0a8a4a"], "seed": 19}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
V = 'videos/italy-collapse/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
def bug(score, mn, frm=None, goalAt=None, lag=0.35, **k):
    d = {"type": "scorebug", "y": 520, "delay": 0, "home": {"name": "BEL", "color": "#c8102e"}, "away": {"name": "ITA", "color": "#0b5fc0"}, "score": score, "min": mn, "clear": False}
    if frm: d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    d.update(k); return d
def keeper(kit, d, word=None, lag=0.3, **k):
    kp = P(kit=kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", **k)
    if word: kp.update(action="dive", dir=d, actionAt=word, actionLag=lag)
    return kp
BG_ITA = {"colors": ["#0b5fc0", "#ffffff", "#0a8a4a"], "text": "ITA"}
B = []
# 1 hook: score flips 0-1 -> 3-1, timeline bracket
B.append({"kicker": "Belgium 4–1 Italy · Nations League", "headline": "Italy led. [11 minutes] later: 3–1 down.", "hookWords": True, "scene": S_BEL, "accent": RED, "lights": 0.75, "flashes": 12,
  "camFrom": {"pos": [0.9, 1.5, 0.3], "tgt": [0.9, 1.35, 10]}, "camera": {"pos": [0.9, 1.5, -0.9], "tgt": [0.9, 1.35, 10]}, "move": 7, "moveEase": "linear",
  "players": [P(kit=ITA, skin="#e7b593", hair="#141010", x=1.6, z=3.5, front=True, pose="think", label="Italy", labelDelay=0)],
  "card": [bug([3, 1], "11 MIN", [0, 1], "Eleven minutes", 0.5, y=640),
           {"type": "stopwatch", "y": 1300, "shiftX": -200, "delay": -0.3, "value": 11, "max": 15, "unit": "MIN", "lockAt": "Eleven minutes", "lockLag": 0.5, "label": "From 0–1 to 3–1", "r": 210, "clear": False},
           {"type": "stamp", "text": "COLLAPSE", "sub": "and it gets worse", "at": "it gets worse", "lag": -0.2, "color": RED, "rot": -0.08, "size": 96, "y": 1780}],
  "shake": [{"at": "Eleven minutes", "lag": 0.55, "amount": 18}, {"at": "it gets worse", "lag": -0.04, "amount": 12}]})
# 2 setting: top of the group
B.append({"kicker": "Brussels · Sunday 15 November 2026", "headline": "Italy arrive [top of the group].", "cut": True, "transition": "whip", "scene": S_BEL, "accent": GOLD, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 16, -30], "tgt": [0, 0, 10]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 680, "delay": 0.1, "label": "Nations League · Group A1", "groups": [{"label": "November", "value": 15, "digits": 2}], "side": {"top": "SUN", "big": "15", "bottom": "NOV"}},
           {"type": "table", "y": 1380, "at": "top of", "lag": -0.5, "scale": 1.2, "label": "Group A1 · before kick-off", "clear": False,
            "rows": [{"pos": 1, "name": "Italy", "color": "#0b5fc0", "color2": "#ffffff", "pts": "", "highlight": True}, {"pos": 2, "name": "France", "color": "#1c2c7a", "color2": "#ffffff", "pts": ""}, {"pos": 3, "name": "Belgium", "color": "#c8102e", "color2": "#111111", "pts": ""}]}]})
# 3 Esposito 0-1
e0 = [-1.78, 0.11, 41.45]; ee = [2.9, 0.6, 52.3]
B.append({"kicker": "Belgium 0–1 Italy", "headline": "Pio Esposito. [0–1].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_BEL, "accent": GREEN, "follow": 0.5,
  "camFrom": {"pos": [-5.0, 2.2, 32.0], "tgt": [-0.8, 1.0, 52]}, "camera": {"pos": [-4.4, 1.9, 34.7], "tgt": [-0.8, 1.0, 52]}, "move": 4, "moveEase": "linear",
  "players": [P(kit=ITA, skin="#e7b593", hair="#141010", x=-2.0, z=41, label="Pio Esposito", labelDelay=0.1, action="kick", actionAt="puts them ahead", actionLag=-0.3, actionDur=0.8, after="celebrate", runup=1.6),
              keeper(GKB, -1, "puts them ahead", 0.15),
              P(kit=BEL, skin="#8a5a3c", hair="#141010", x=-3.9, z=44.4, front=True, action="dive", dir=1, actionAt="puts them ahead", actionLag=-0.15, actionDur=0.7), P(kit=BEL, skin="#f0c8a8", hair="#5a3a22", x=2.4, z=47.6, front=True)],
  "card": [bug([0, 1], "1ST HALF", [0, 0], "puts them ahead", 0.6),
           {"type": "ball", "delay": 0, "point": e0, "untilAt": "puts them ahead", "untilLag": 0.04},
           {"type": "ballpath", "world": True, "at": "puts them ahead", "lag": 0.04, "dur": 0.5, "slowmo": False, "points": [e0, mid(e0, ee, 0.9), ee]}]})
# 4 the collapse: three goals, barrage + timeline
shots = [(-2.3, 42.0, [-2.8, 0.6, 52.3], "De Cuyper", "De Cuyper"), (0.3, 41.2, [2.9, 1.2, 52.3], "Ngoy", "Ngoy"), (2.5, 42.8, [-2.9, 1.0, 52.3], "Doku", "Doku")]
pl, cards = [], []
for i, (x, z, end, name, word) in enumerate(shots):
    b0 = [x + 0.22, 0.11, z + 0.45]
    pl.append(P(kit=BEL, skin=["#f0c8a8", "#8a5a3c", "#6a4630"][i], hair="#141010", x=x, z=z, label=name, labelAt=word, action="kick", actionAt=word, actionLag=-0.2, actionDur=0.8, after="celebrate", runup=False))
    cards += [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": 0.14}, {"type": "ballpath", "world": True, "at": word, "lag": 0.14, "dur": 0.45, "slowmo": False, "points": [b0, mid(b0, end, 1.0), end]}]
pl += [keeper(GKI, 1, "De Cuyper", 0.2), P(kit=ITA, skin="#e7b593", hair="#141010", x=-1.0, z=47.2, front=True), P(kit=ITA, skin="#c99b7a", hair="#3a2a1a", x=3.7, z=47.8, front=True)]
B.append({"kicker": "The collapse", "headline": "Three goals in [11 minutes].", "cut": True, "transition": "vhs", "vhsLabel": "THEN", "vhsDur": 0.7, "scene": S_BEL, "accent": RED, "hype": False,
  "camFrom": {"pos": [-1.2, 3.4, 29.5], "tgt": [0, 1.2, 50]}, "camera": {"pos": [0.8, 3.0, 32.0], "tgt": [0, 1.2, 50]}, "move": 6, "moveEase": "linear", "players": pl,
  "card": cards + [bug([3, 1], "11 MIN", [0, 1], "De Cuyper", 0.6),
                   {"type": "timeline", "y": 1560, "delay": 0.1, "title": "Belgium v Italy · not to scale", "clear": False,
                    "events": [{"pos": 0.22, "label": "Esposito", "color": "#0b5fc0", "t": 0.05}, {"pos": 0.48, "label": "De Cuyper", "color": "#c8102e", "at": "De Cuyper", "lag": 0.3}, {"pos": 0.62, "label": "Ngoy", "color": "#c8102e", "at": "Ngoy", "lag": 0.3}, {"pos": 0.76, "label": "Doku", "color": "#c8102e", "at": "Doku", "lag": 0.3}],
                    "bracket": {"from": 0.48, "to": 0.76, "label": "11 MIN", "at": "Three goals"}}],
  "shake": [{"at": "De Cuyper", "lag": 0.6, "amount": 10}, {"at": "Ngoy", "lag": 0.6, "amount": 10}, {"at": "Doku", "lag": 0.6, "amount": 14}]})
# 5 Moreira 4-1, first to third, out
B.append({"kicker": "Full time", "headline": "4–1. From first to [third]. Out.", "cut": True, "transition": "whip", "scene": S_BEL, "accent": RED, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-14, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [14, 24, -42], "tgt": [0, 0, 5]}, "move": 7, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [bug([4, 1], "FT", [3, 1], "a fourth", 0.1, y=650),
           {"type": "table", "y": 1080, "delay": 0.2, "scale": 1.2, "label": "Group A1 · final", "moveAt": "from first", "clear": False,
            "rows": [{"pos": 1, "fromPos": 2, "fromRow": 1, "name": "France", "color": "#1c2c7a", "color2": "#ffffff", "pts": ""}, {"pos": 2, "fromPos": 3, "fromRow": 2, "name": "Belgium", "color": "#c8102e", "color2": "#111111", "pts": ""},
                     {"pos": 3, "fromPos": 1, "fromRow": 0, "name": "Italy", "color": "#0b5fc0", "color2": "#ffffff", "pts": "", "highlight": True}]},
           {"type": "trapdoor", "y": 1620, "at": "they're out", "lag": -0.7, "scale": 0.9, "clear": False, "items": [{"name": "Italy", "badge": BG_ITA, "at": "they're out", "lag": -0.1, "tag": "OUT"}]}],
  "shake": [{"at": "they're out", "lag": 0, "amount": 14}]})
# 6 three World Cups missed
B.append({"kicker": "The bigger picture", "headline": "Three World Cups [missed].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ITA, "accent": RED, "lights": 0.4,
  "camFrom": {"pos": [-0.3, 1.6, -3.0], "tgt": [-0.9, 1.3, 10]}, "camera": {"pos": [-0.8, 1.45, -0.9], "tgt": [-0.9, 1.3, 10]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=ITA, skin="#e7b593", hair="#141010", x=-1.9, z=2.9, front=True, pose="think")],
  "card": [{"type": "tally", "y": 1300, "shiftX": 200, "at": "missed three", "lag": -0.5, "r": 70, "gap": 20, "perRow": 3, "title": "World Cups", "score": "{l} in a row", "clear": False,
            "items": [{"label": "2018", "mark": "x", "t": 0.2}, {"label": "2022", "mark": "x", "t": 0.55}, {"label": "2026", "mark": "x", "t": 0.9}]}],
  "shake": [{"at": "missed three", "lag": 0.5, "amount": 12}]})
# 7 Bosnia play-off; Mancini back
B.append({"kicker": "March 2026 · play-off", "headline": "Lost to Bosnia on [penalties].", "cut": True, "transition": "polaroid", "polaroidLabel": "March 2026", "scene": S_DARK, "accent": RED, "hype": False,
  "camFrom": {"pos": [2.4, 2.1, 33.5], "tgt": [0, 1.2, 52]}, "camera": {"pos": [1.9, 1.9, 35.5], "tgt": [0, 1.2, 52]}, "move": 3.5, "moveEase": "linear",
  "players": [P(kit=ITA, skin="#e7b593", hair="#141010", x=-0.2, z=41.0, action="kick", actionDelay=0.5, actionDur=0.8, runup=2),
              P(kit=GKB, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1)],
  "card": [{"type": "ball", "delay": 0, "point": [0.02, 0.11, 41.5], "until": 0.84},
           {"type": "ballpath", "world": True, "delay": 0.84, "dur": 0.55, "slowmo": False, "saveBy": 1, "flash": False, "points": [[0.02, 0.11, 41.5], [1.2, 1.2, 47], [2.3, 1.2, 52.0]]},
           {"type": "stamp", "text": "PENALTIES", "sub": "Bosnia 4–1 on pens", "at": "on penalties", "lag": -0.1, "color": RED, "rot": -0.07, "size": 84, "y": 1640}],
  "shots": [{"at": "Roberto Mancini", "lag": -0.1, "cut": True, "transition": "whip", "kicker": "July 2026", "headline": "Mancini returns to [fix it].", "scene": S_ITA, "accent": GOLD, "lights": 0.7,
     "camFrom": {"pos": [1.2, 1.6, -2.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.3, 1.5, -0.8], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
     "players": [P(outfit="suit", suitColor="#1c2a4a", tie="#0b5fc0", skin="#e2b08c", hair="#c9ced6", front=True, x=0, z=2.9, enter="walk", fromZ=4.4, walkDur=1.6, label="Roberto Mancini", labelDelay=0.2)],
     "card": [{"type": "flytext", "text": "FIX IT", "size": 220, "endScale": 0.7, "y": 1620, "at": "to fix it", "lag": -0.2, "color": GOLD, "clear": False}]}]})
# 8 four months later, still falling
B.append({"kicker": "Four months later", "headline": "Italy are [still falling].", "cut": True, "scene": S_DARK, "accent": RED, "lights": 0.4, "focus": 0.3,
  "camFrom": {"pos": [8, 16, -30], "tgt": [0, 0, 8]}, "camera": {"pos": [-8, 10, -22], "tgt": [0, 0, 8]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [{"type": "crossoff", "y": 950, "delay": 0.1, "title": "Months of Mancini", "days": 4, "cols": 4, "cell": 150, "crossT": 0.2, "dur": 1.0, "caption": "{n} months", "clear": False},
           {"type": "trapdoor", "y": 1560, "delay": 0.1, "scale": 1.0, "clear": False, "items": [{"name": "Italy", "badge": BG_ITA, "at": "still falling", "lag": -0.2, "tag": "STILL FALLING"}]}],
  "shake": [{"at": "still falling", "lag": -0.1, "amount": 14}]})
# 9 four World Cups, none since 2006
B.append({"kicker": "Italy · World Cups", "headline": "Four won. [None since 2006].", "cut": True, "transition": "whip", "scene": S_ITA, "accent": GOLD, "lights": 0.55, "focus": 0.25,
  "camFrom": {"pos": [0, 20, -36], "tgt": [0, 2, 6]}, "camera": {"pos": [0, 9, -20], "tgt": [0, 2, 8]}, "move": 5, "moveEase": "linear", "players": [], "flashes": 10,
  "card": [{"type": "shelf", "y": 1050, "delay": 0.1, "title": "Italy's World Cups", "slots": 4, "clear": False,
            "items": [{"kind": "worldcup", "label": "1934", "t": 0.2}, {"kind": "worldcup", "label": "1938", "t": 0.45}, {"kind": "worldcup", "label": "1982", "t": 0.7}, {"kind": "worldcup", "label": "2006", "t": 0.95}]},
           {"type": "big", "at": "None since", "lag": -0.2, "from": 0, "value": 20, "countDur": 0.8, "suffix": " yrs", "label": "Since Italy last won it", "y": 1700, "size": 190, "style": "accent", "clear": False}]})
# 10 question
B.append({"kicker": "Your call", "headline": "The [worst] Italy team ever?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_ITA, "accent": RED, "lights": 0.6,
  "orbit": {"center": [0, 1.25, 3], "r": 5.2, "from": -28, "to": 16, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [P(kit=ITA, skin="#e7b593", hair="#141010", x=0, z=3.3, front=True, pose="think")],
  "card": [{"type": "poll", "y": 1580, "at": "worst Italy", "lag": -0.5, "question": "Worst Italy team of all time?", "options": [{"label": "Yes", "color": "#d6283b", "fill": 0.5}, {"label": "No, it's been worse", "color": "#0b5fc0", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "Italy's 11-minute collapse", "brand": "theo6k", "accent": RED, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
