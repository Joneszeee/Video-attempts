# Builds videos/germany-five/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
GER = {"shirt": "#f4f4f2", "shorts": "#111111", "socks": "#f4f4f2", "text": "#111111"}
NED = {"shirt": "#f36c21", "shorts": "#f36c21", "socks": "#f36c21", "text": "#111111"}
ENG = {"shirt": "#ffffff", "shorts": "#1c2c5b", "socks": "#ffffff", "text": "#1c2c5b"}
GKN = {"shirt": "#2ecc71", "shorts": "#1d1c22", "socks": "#2ecc71", "text": "#1d1c22"}
S_BER = {"type": "stadium", "crowd": ["#f4f4f2", "#111111", "#dd0000", "#ffce00"], "seed": 13}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
S_ENG = {"type": "stadium", "crowd": ["#ffffff", "#c8102e", "#ffffff", "#1c2c5b"], "seed": 3}
V = 'videos/germany-five/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def boss(tie, skin, hair, **k): return P(outfit="suit", suitColor="#1c1f28", tie=tie, skin=skin, hair=hair, front=True, **k)
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
BG_NED = {"colors": ["#f36c21", "#1c2c7a", "#ffffff"], "text": "NED"}
BG = {"GER": {"colors": ["#f4f4f2", "#111111", "#c8102e"], "text": "GER"}, "NED": BG_NED, "BEL": {"colors": ["#c8102e", "#111111", "#fdda24"], "text": "BEL"}}
def bug(score, mn, frm=None, goalAt=None, lag=0.35, **k):
    d = {"type": "scorebug", "y": 520, "delay": 0, "home": {"name": "GER", "color": "#f4f4f2"}, "away": {"name": "NED", "color": "#f36c21"}, "score": score, "min": mn, "clear": False}
    if frm: d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    d.update(k); return d
def goal(word, x, z, side, label, end, gdir, lag=-0.5, skin="#f0c8a8", hair="#3a2a1a", foot=None):
    """Shooter in frame for the whole run-up; one defender blocking, one covering; keeper beaten."""
    sx = -1 if foot == "left" else 1
    b0 = [x + sx * 0.22, 0.11, z + 0.45]
    sh = P(kit=GER, skin=skin, hair=hair, x=x, z=z, label=label, labelDelay=0.1, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate", runup=1.6)
    if foot: sh["foot"] = foot
    pl = [sh, P(kit=GKN, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=gdir, actionAt=word, actionLag=lag + 0.45),
          P(kit=NED, skin="#e7b593", hair="#141010", x=x + side * -1.9, z=z + 3.4, front=True, action="dive", dir=side, actionAt=word, actionLag=lag + 0.15, actionDur=0.7),
          P(kit=NED, skin="#8a5a3c", hair="#141010", x=-end[0] * 0.8, z=47.8, front=True)]
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34},
             {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": 0.5, "slowmo": False, "points": [b0, mid(b0, end, 0.9), end]}]
    cam = {"camFrom": {"pos": [round(x + side * 3.0, 2), 2.2, z - 9], "tgt": [round(x * 0.4, 2), 1.0, 52]}, "camera": {"pos": [round(x + side * 2.4, 2), 1.9, z - 6.3], "tgt": [round(x * 0.4, 2), 1.0, 52]}, "move": 4, "moveEase": "linear", "follow": 0.5}
    return pl, cards, cam
XAVI = dict(tie="#f36c21", skin="#d9a37c", hair="#2a1a10"); KLOPP = dict(tie="#111111", skin="#f0c8a8", hair="#c9b28a")
B = []
# 1 hook: Xavi, the Dutch shield sinking as the goals race to five, Klopp walks in
B.append({"kicker": "Germany 5–0 Netherlands · Nations League", "headline": "Xavi's first defeat: [5–0] to Klopp.", "hookWords": True, "scene": S_BER, "accent": RED, "lights": 0.75, "flashes": 16,
  "camFrom": {"pos": [0, 1.45, -0.9], "tgt": [0, 1.2, 10]}, "camera": {"pos": [0, 1.45, -1.9], "tgt": [0, 1.2, 10]}, "move": 7, "moveEase": "linear",
  "players": [boss(x=-1.0, z=3.4, label="Xavi", labelDelay=0, pose="think", **XAVI),
              boss(x=1.05, z=3.6, enter="walk", fromZ=6.5, walkDur=1.4, at="Jürgen Klopp", lag=-0.3, label="Jürgen Klopp", labelAt="Jürgen Klopp", pose="fists", **KLOPP)],
  "card": [{"type": "sinking", "y": 1560, "delay": -0.2, "badge": BG_NED, "label": "Netherlands · goals conceded", "w": 460, "h": 520, "badgeH": 220, "clear": False,
            "steps": [{"t": 0.35}, {"t": 0.85}, {"t": 1.35}, {"t": 1.85}, {"t": 2.35}]},
           {"type": "stamp", "text": "5–0", "sub": "Xavi's first defeat", "at": "Five–nil", "lag": -0.1, "color": RED, "rot": -0.08, "size": 120, "y": 640}],
  "shake": [{"t": 2.6, "amount": 14}, {"at": "Five–nil", "lag": 0.06, "amount": 18}]})
# 2 setting: Berlin, and 7-0 three days earlier
B.append({"kicker": "Berlin · Monday 16 November 2026", "headline": "Three days earlier: [7–0] winners.", "cut": True, "transition": "whip", "scene": S_BER, "accent": GOLD, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 16, -30], "tgt": [0, 0, 10]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 680, "delay": 0.1, "label": "Nations League · Group A2", "groups": [{"label": "November", "value": 16, "digits": 2}], "side": {"top": "MON", "big": "16", "bottom": "NOV"}},
           {"type": "tickets", "y": 1380, "at": "Three days", "lag": -0.1, "done": 0, "newT": 0.1, "tw": 760, "th": 270, "dx": 0, "stamp": "7–0", "clear": False,
            "tickets": [{"comp": "Nations League · 13 November", "teams": "Netherlands v Greece", "score": "7–0", "date": "3 days earlier", "color": "#f36c21"}]}]})
# 3 Scherhant 41'
pl, cards, cam = goal("Scherhant scores", -2.0, 41, -1, "Derry Scherhant", [2.9, 0.6, 52.3], -1, lag=-0.2)
B.append({"kicker": "41'", "headline": "Scherhant. [1–0].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_BER, "accent": GOLD, **cam, "players": pl,
  "card": cards + [bug([1, 0], "41'", [0, 0], "Scherhant scores", 0.7)]})
# 4 Wirtz 60'
pl, cards, cam = goal("makes it two", 1.2, 42, 1, "Florian Wirtz", [-2.9, 1.0, 52.3], 1, lag=-0.5, hair="#5a3a22")
B.append({"kicker": "60'", "headline": "Wirtz. [2–0].", "cut": True, "scene": S_BER, "accent": GOLD, **cam, "players": pl,
  "card": cards + [bug([2, 0], "60'", [1, 0], "makes it two", 0.4)]})
# 5 Schlotterbeck header 65', then Wirtz again 71'
c0 = [-14, 0.2, 44]; hd = [-1.2, 2.25, 46.5]; e2 = [2.8, 1.2, 52.3]
B.append({"kicker": "65' · 71'", "headline": "Schlotterbeck. Wirtz. [4–0].", "cut": True, "transition": "whip", "scene": S_BER, "accent": GOLD, "hype": False,
  "camFrom": {"pos": [6, 2.5, 39.5], "tgt": [-0.5, 1.5, 49.5]}, "camera": {"pos": [5, 2.2, 41.5], "tgt": [-0.5, 1.5, 49.5]}, "move": 5, "moveEase": "linear",
  "players": [P(kit=GER, skin="#f0c8a8", hair="#8a6a3a", x=-1.2, z=46.5, front=True, label="Schlotterbeck", labelDelay=0.1, hops=[{"at": "heads in", "lag": -0.3, "dur": 0.6, "height": 0.3}], action="idle"),
              P(kit=GKN, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=-1, actionAt="heads in", actionLag=0.05),
              P(kit=NED, skin="#e7b593", hair="#141010", x=0.7, z=47.6, front=True), P(kit=NED, skin="#8a5a3c", hair="#141010", x=-3.4, z=48.2, front=True)],
  "card": [bug([3, 0], "65'", [2, 0], "heads in", 0.4, hideAt="Then Wirtz", hideLag=0.1, y=620),
           {"type": "ballpath", "world": True, "at": "heads in", "lag": -0.9, "dur": 0.9, "slowmo": False, "flash": False, "points": [c0, mid(c0, hd, 5.5), hd]},
           {"type": "ballpath", "world": True, "at": "heads in", "lag": 0.0, "dur": 0.4, "slowmo": False, "points": [hd, mid(hd, e2, 1.9), e2]},
           dict(bug([4, 0], "71'", [3, 0], "Four", -0.1, y=620), at="Then Wirtz", lag=0.1),
           {"type": "flytext", "text": "4–0", "size": 300, "endScale": 0.7, "y": 1600, "at": "Four", "lag": -0.15, "color": GOLD, "clear": False}],
  "shake": [{"at": "heads in", "lag": 0.42, "amount": 12}, {"at": "Four", "lag": 0.05, "amount": 14}]})
# 6 Gruda 77': four goals in 17 minutes (timeline with the real minutes)
m = lambda x: round(x / 90, 3)
B.append({"kicker": "77'", "headline": "Four goals in [17 minutes].", "cut": True, "transition": "vhs", "vhsLabel": "5–0", "vhsDur": 0.7, "scene": S_BER, "accent": RED, "lights": 0.55, "focus": 0.25,
  "camFrom": {"pos": [-14, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [14, 24, -42], "tgt": [0, 0, 5]}, "move": 7, "moveEase": "linear", "players": [], "flashes": 12,
  "card": [bug([5, 0], "77'", [4, 0], "the fifth", 0.2, y=560),
           {"type": "timeline", "y": 1020, "delay": 0.1, "title": "Germany's five goals", "clear": False,
            "events": [{"pos": m(41), "label": "41'", "color": "#f4f4f2", "t": 0.05}, {"pos": m(60), "label": "60'", "color": "#f4f4f2", "t": 0.2}, {"pos": m(65), "label": "65'", "color": "#f4f4f2", "t": 0.35}, {"pos": m(71), "label": "71'", "color": "#f4f4f2", "t": 0.5},
                       {"pos": m(77), "label": "77' Gruda", "color": GOLD, "at": "the fifth", "lag": -0.1}],
            "bracket": {"from": m(60), "to": m(77), "label": "17 MIN", "at": "Four goals"}},
           {"type": "sinking", "y": 1620, "delay": 0.1, "badge": BG_NED, "label": "Netherlands", "w": 420, "h": 360, "badgeH": 170, "from": 4, "steps": [{"at": "the fifth", "lag": 0.1}], "clear": False}],
  "shake": [{"at": "the fifth", "lag": 0.3, "amount": 12}]})
# 7 1959: West Germany 7-0
B.append({"kicker": "Cologne · 1959", "headline": "Their heaviest defeat since [1959].", "cut": True, "transition": "polaroid", "polaroidLabel": "Cologne 1959", "scene": S_DARK, "accent": RED, "lights": 0.55, "focus": 0.25,
  "camFrom": {"pos": [8, 16, -30], "tgt": [0, 0, 8]}, "camera": {"pos": [-8, 10, -22], "tgt": [0, 0, 8]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "big", "delay": 0.2, "from": 2026, "value": 1959, "countDur": 1.2, "label": "The last time the Dutch lost by five or more", "y": 820, "size": 250, "clear": False},
           {"type": "scorebug", "y": 1300, "at": "West Germany", "lag": -0.2, "home": {"name": "FRG", "color": "#f4f4f2"}, "away": {"name": "NED", "color": "#f36c21"}, "score": [7, 0], "from": [0, 0], "goalAt": "Seven–nil", "goalLag": -0.1, "min": "1959", "clear": False},
           {"type": "big", "at": "Seven–nil", "lag": 0.3, "from": 0, "value": 67, "countDur": 0.7, "suffix": " yrs", "label": "ago", "y": 1640, "size": 190, "style": "accent", "clear": False}],
  "shake": [{"at": "Seven–nil", "lag": 0, "amount": 12}]})
# 8 three teams on 11
B.append({"kicker": "And here's the strange part", "headline": "Three teams. [11 points] each.", "cut": True, "transition": "vhs", "vhsLabel": "BUT", "vhsDur": 0.8, "scene": S_BER, "accent": GOLD, "lights": 0.55, "focus": 0.2,
  "camFrom": {"pos": [14, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [-14, 24, -42], "tgt": [0, 0, 5]}, "move": 9, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [{"type": "table", "y": 900, "at": "Germany, the", "lag": -0.4, "scale": 1.25, "label": "Group A2 · final table", "clear": False,
            "rows": [{"pos": 1, "name": "Germany", "color": "#f4f4f2", "color2": "#111111", "pts": 11, "highlight": True}, {"pos": 2, "name": "Netherlands", "color": "#f36c21", "pts": 11}, {"pos": 3, "name": "Greece", "color": "#0d5eaf", "color2": "#ffffff", "pts": 11}]},
           {"type": "stamp", "text": "TOP", "sub": "Germany · on head-to-head", "at": "Germany top", "lag": -0.1, "color": GOLD, "rot": -0.07, "size": 90, "y": 1380},
           {"type": "stamp", "text": "THROUGH", "sub": "the Netherlands · second", "at": "still go through", "lag": -0.2, "color": "#f36c21", "rot": 0.05, "size": 84, "y": 1660}],
  "punch": [{"at": "eleven points", "amount": 0.1, "dur": 1.4, "x": 800, "y": 900}]})
# 9 England angle
def tiles(states, **k):
    T = [("Germany", "GER"), ("Netherlands", "NED"), ("Belgium", "BEL")]
    items = [dict(name=n, sub="", badge=BG[b], **states.get(i, {"t": 99})) for i, (n, b) in enumerate(T)]
    d = {"type": "fates", "title": "England's quarter-final draw · Friday", "items": items, "clear": False}; d.update(k); return d
B.append({"kicker": "What it means for England", "headline": "Not Germany. [Maybe the Dutch].", "cut": True, "transition": "whip", "scene": S_ENG, "accent": GOLD, "lights": 0.8,
  "camFrom": {"pos": [0, 1.5, -2.6], "tgt": [0, 1.2, 10]}, "camera": {"pos": [0, 1.5, -1.3], "tgt": [0, 1.2, 10]}, "move": 6, "moveEase": "linear",
  "players": [P(kit=ENG, skin="#e7b593", hair="#3a2a1a", x=0, z=3.2, front=True, pose="think", label="England", labelDelay=0.1)],
  "card": [tiles({0: {"fate": "down", "label": "CAN'T", "at": "can't face", "lag": -0.2}, 1: {"fate": "up", "label": "POSSIBLE", "at": "the Netherlands can", "lag": -0.2}, 2: {"fate": "up", "label": "POSSIBLE", "at": "the Netherlands can", "lag": 0.3}}, y=1600, delay=0)]})
# 10 question
B.append({"kicker": "Your call", "headline": "Klopp's Germany: [the team to beat]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_BER, "accent": GOLD, "flashes": 14, "confetti": True,
  "orbit": {"center": [0, 1.25, 3], "r": 5.2, "from": -28, "to": 16, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [boss(x=0, z=3.2, pose="fists", label="Jürgen Klopp", labelDelay=0.2, **KLOPP), P(kit=GER, skin="#f0c8a8", hair="#5a3a22", x=-1.9, z=4.2, front=True, action="celebrate"), P(kit=GER, skin="#8a5a3c", hair="#141010", x=1.9, z=4.2, front=True, action="celebrate")],
  "card": [{"type": "poll", "y": 1600, "at": "team to beat", "lag": -0.6, "question": "Is Germany the team to beat?", "options": [{"label": "Yes", "color": "#b8892a", "fill": 0.5}, {"label": "No, still Spain", "color": "#c60b1e", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "Germany 5-0 Netherlands", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
