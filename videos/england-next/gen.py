# Builds videos/england-next/spec.json (run from the repo root).
import json
RED, GOLD, GREEN = "#ff4d5e", "#e9b949", "#2ecc71"
ENG = {"shirt": "#ffffff", "shorts": "#1c2c5b", "socks": "#ffffff", "text": "#1c2c5b"}
BEL = {"shirt": "#c8102e", "shorts": "#c8102e", "socks": "#c8102e", "text": "#fdda24"}
ITA = {"shirt": "#0b5fc0", "shorts": "#ffffff", "socks": "#0b5fc0", "text": "#ffffff"}
GKI = {"shirt": "#f2c200", "shorts": "#1d1c22", "socks": "#f2c200", "text": "#1d1c22"}
S_WEM = {"type": "stadium", "crowd": ["#ffffff", "#c8102e", "#ffffff", "#1c2c5b"], "seed": 3}
S_BEL = {"type": "stadium", "crowd": ["#c8102e", "#fdda24", "#111111", "#c8102e"], "seed": 26}
S_DARK = {"type": "stadium", "crowd": ["#2a2f3a", "#444b5a", "#1c2029", "#3a4050"], "seed": 21}
V = 'videos/england-next/'
lines = [l.strip() for l in open(V + 'vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def E(**k): return P(kit=ENG, **k)
def mid(a, c, h): return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]
BALLS = [{"text": "BEL", "color": "#c8102e", "color2": "#111111"}, {"text": "GER", "color": "#f4f4f2", "color2": "#111111", "text2": "#fff"}, {"text": "NED", "color": "#f36c21", "color2": "#1c2c7a"},
         {"text": "POR", "color": "#c8102e", "color2": "#046a38"}, {"text": "GRE", "color": "#0d5eaf", "color2": "#ffffff"}, {"text": "?", "color": "#e9b949", "color2": "#8a6a1a"}]
BG = {"ESP": {"colors": ["#c60b1e", "#ffc400", "#ffc400"], "text": "ESP"}, "FRA": {"colors": ["#1c2c7a", "#ffffff", "#c8102e"], "text": "FRA"}, "BEL": {"colors": ["#c8102e", "#111111", "#fdda24"], "text": "BEL"},
      "GER": {"colors": ["#f4f4f2", "#111111", "#c8102e"], "text": "GER"}, "NED": {"colors": ["#f36c21", "#1c2c7a", "#ffffff"], "text": "NED"}, "POR": {"colors": ["#c8102e", "#046a38", "#fdda24"], "text": "POR"}}
def tiles(states, **k):
    T = [("Spain", "ESP"), ("France", "FRA"), ("Belgium", "BEL"), ("Ger / Ned", "GER"), ("Portugal", "POR")]
    items = []
    for i, (n, b) in enumerate(T):
        it = dict(name=n, sub="", badge=BG[b]); it.update(states.get(i, {"t": 99})); items.append(it)
    d = {"type": "fates", "title": "England's quarter-final draw", "items": items, "clear": False}; d.update(k); return d
NO = lambda **k: {"fate": "down", "label": "CAN'T", **k}; YES = lambda **k: {"fate": "up", "label": "POSSIBLE", **k}
HI = {"pos": [0, 30, -50], "tgt": [0, 0, 5]}; MID = {"pos": [0, 16, -30], "tgt": [0, 0, 8]}
B = []
# 1 hook: the draw pot, one ball rises with "?"
B.append({"kicker": "England · Nations League", "headline": "England top the group. [Who's next]?", "hookWords": True, "scene": S_WEM, "accent": GOLD, "lights": 0.8, "flashes": 16,
  "camFrom": {"pos": [-0.9, 1.5, 0.2], "tgt": [-0.9, 1.35, 10]}, "camera": {"pos": [-0.9, 1.5, -1.0], "tgt": [-0.9, 1.35, 10]}, "move": 7, "moveEase": "linear",
  "players": [E(skin="#e7b593", hair="#3a2a1a", x=-1.75, z=3.6, front=True, action="celebrate", label="England", labelDelay=0)],
  "card": [{"type": "drawpot", "y": 1330, "shiftX": 210, "delay": -0.5, "r": 270, "balls": BALLS, "pick": 5, "pickText": "?", "pickAt": "Now comes", "pickLag": 0.1, "pickLabel": "Quarter-final opponent", "title": "The draw", "clear": False},
           {"type": "stamp", "text": "TOP", "sub": "Group A3", "at": "topped the group", "lag": -0.1, "color": GOLD, "rot": -0.08, "size": 110, "dx": -270, "y": 1760}],
  "shake": [{"at": "topped the group", "lag": 0.06, "amount": 12}, {"at": "Now comes", "lag": 0.55, "amount": 10}]})
# 2 the campaign: 5 wins, 19 goals, one defeat
B.append({"kicker": "The group stage", "headline": "[5] wins. [19] goals. One defeat.", "cut": True, "transition": "whip", "scene": S_WEM, "accent": GOLD, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [-12, 14, -28], "tgt": [0, 0, 8]}, "camera": {"pos": [10, 22, -40], "tgt": [0, 0, 6]}, "move": 8, "moveEase": "linear", "players": [],
  "card": [{"type": "dots", "states": ["hit", "miss", "hit", "hit", "hit", "hit"], "label": "England · six group games", "y": 780, "step": 0.14, "delay": 0.1, "clear": False},
           {"type": "rain", "y": 1250, "at": "Nineteen", "lag": -0.4, "groups": [{"n": 19, "color": "#ffffff", "t": 0, "dur": 1.0}], "cols": 10, "cell": 86, "icon": "ball", "empty": 0, "label": "Goals", "clear": False, "hideAt": "The only", "hideLag": 0.2},
           {"type": "tickets", "y": 1250, "at": "The only", "lag": 0.3, "done": 0, "newT": 0.1, "tw": 760, "th": 280, "tickets": [{"comp": "Nations League", "teams": "England v Spain", "score": "2–3", "date": "Wembley · Sept 2026", "color": "#c60b1e"}], "stamp": "LOST", "clear": False}]})
# 3 the table
B.append({"kicker": "Group A3 · final table", "headline": "Level on [15]. Top on goal difference.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_DARK, "accent": GOLD, "lights": 0.55, "focus": 0.3,
  "camFrom": {"pos": [-14, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [14, 26, -44], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [], "focus": 0.15, "flashes": 10,
  "punch": [{"t": 0.2, "amount": 0.12, "dur": 2.4, "x": 540, "y": 900}],
  "card": [{"type": "table", "y": 900, "delay": 0, "scale": 1.25, "label": "Nations League · Group A3", "pill": "+13", "pillRow": 0, "clear": False,
            "rows": [{"pos": 1, "name": "England", "color": "#ffffff", "color2": "#1c2c5b", "pts": 15, "highlight": True}, {"pos": 2, "name": "Spain", "color": "#c60b1e", "color2": "#ffc400", "pts": 15}, {"pos": 3, "name": "Croatia", "color": "#ffffff", "color2": "#c8102e", "pts": 6}, {"pos": 4, "name": "Czechia", "color": "#c8102e", "color2": "#1c2c7a", "pts": 0}]},
           {"type": "tape", "y": 1560, "at": "goal difference", "lag": -0.5, "left": {"name": "England", "color": "#ffffff"}, "right": {"name": "Spain", "color": "#c60b1e"}, "rows": [{"label": "Goal difference", "left": 13, "right": 8}], "clear": False}]})
# 4 the prize: seeded, second leg at home
B.append({"kicker": "The prize", "headline": "Seeded. [Second leg at home].", "cut": True, "transition": "whip", "scene": S_WEM, "accent": GOLD, "flashes": 14,
  "camFrom": {"pos": [0, 0.9, -2.8], "tgt": [0, 1.5, 4]}, "camera": {"pos": [0, 1.2, -0.4], "tgt": [0, 1.4, 4]}, "move": 5, "moveEase": "linear",
  "players": [E(skin="#8a5a3c", hair="#141010", x=0, z=4, front=True, enter="walk", fromZ=9, walkDur=3, pose="wings")],
  "card": [{"type": "flytext", "text": "SEEDED", "size": 240, "endScale": 0.7, "y": 1500, "at": "seeded", "lag": -0.2, "color": GOLD, "clear": False},
           {"type": "stamp", "text": "2ND LEG", "sub": "at home", "at": "second leg", "lag": -0.1, "color": "#ffffff", "rot": -0.07, "size": 90, "y": 1740}],
  "shake": [{"at": "second leg", "lag": 0.06, "amount": 10}]})
# 5 can't draw Spain or France
B.append({"kicker": "The draw rules", "headline": "Not Spain. [Not France].", "cut": True, "transition": "vhs", "vhsLabel": "THE DRAW", "vhsDur": 0.8, "scene": S_DARK, "accent": RED, "lights": 0.5, "focus": 0.25,
  "camFrom": {"pos": [-14, 24, -42], "tgt": [0, 0, 5]}, "camera": {"pos": [12, 12, -24], "tgt": [0, 0, 8]}, "move": 6, "moveEase": "linear", "players": [], "flashes": 8,
  "card": [tiles({0: NO(at="Spain", lag=0.1), 1: NO(at="France", lag=0.1)}, y=1000, delay=0), {"type": "stamp", "text": "BLOCKED", "sub": "same group · both group winners", "at": "France", "lag": 0.7, "color": RED, "rot": -0.07, "size": 100, "y": 1560}],
  "punch": [{"at": "Spain", "lag": 0.5, "amount": 0.12, "dur": 1.2, "x": 200, "y": 1000}, {"at": "France", "lag": 0.5, "amount": 0.12, "dur": 1.2, "x": 380, "y": 1000}]})
# 6 Belgium: four past Italy (barrage)
shots = [(-3.6, 41.5, [-2.8, 0.6, 52.3]), (1.4, 40.6, [2.9, 1.2, 52.3]), (-1.2, 43.2, [2.6, 0.4, 52.3]), (3.8, 42.4, [-2.9, 1.4, 52.3])]
pl, cards = [], []
for i, (x, z, end) in enumerate(shots):
    t0 = 0.5 + i * 0.75; b0 = [x + 0.22, 0.11, z + 0.45]
    pl.append(P(kit=BEL, skin=["#e7b593", "#8a5a3c", "#f0c8a8", "#6a4630"][i], hair="#141010", x=x, z=z, action="kick", actionDelay=round(t0 - 0.34, 2), actionDur=0.8, after="celebrate", runup=False))
    cards += [{"type": "ball", "delay": 0, "point": b0, "until": round(t0, 2)}, {"type": "ballpath", "world": True, "delay": round(t0, 2), "dur": 0.45, "slowmo": False, "points": [b0, mid(b0, end, 1.0), end]}]
pl += [P(kit=GKI, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionDelay=0.55),
       P(kit=ITA, skin="#e7b593", hair="#141010", x=-3.5, z=46.5, front=True), P(kit=ITA, skin="#c99b7a", hair="#3a2a1a", x=1.6, z=47.3, front=True)]
B.append({"kicker": "Belgium 4–1 Italy", "headline": "Belgium: [four] past Italy.", "cut": True, "transition": "whip", "scene": S_BEL, "accent": RED, "hype": False,
  "camFrom": {"pos": [-1.5, 3.2, 31.5], "tgt": [0, 1.2, 50]}, "camera": {"pos": [1.0, 2.7, 34.5], "tgt": [0, 1.2, 50]}, "move": 4.5, "moveEase": "linear", "players": pl,
  "card": cards + [{"type": "scorebug", "y": 520, "delay": 0, "home": {"name": "BEL", "color": "#c8102e"}, "away": {"name": "ITA", "color": "#0b5fc0"}, "score": [4, 1], "min": "FT", "clear": False},
                   {"type": "big", "delay": 0.4, "from": 0, "value": 4, "countDur": 3.4, "label": "Belgium goals v Italy", "y": 1650, "size": 230, "style": "accent", "clear": False}],
  "shake": [{"t": 0.95, "amount": 9}, {"t": 1.7, "amount": 9}, {"t": 2.45, "amount": 9}, {"t": 3.2, "amount": 12}]})
# 7 or the other runners-up
B.append({"kicker": "The other pots", "headline": "Germany? [Netherlands]? Portugal?", "cut": True, "scene": S_DARK, "accent": GOLD, "lights": 0.55, "focus": 0.25,
  "camFrom": {"pos": [12, 12, -24], "tgt": [0, 0, 8]}, "camera": {"pos": [-12, 22, -40], "tgt": [0, 0, 5]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [tiles({0: NO(), 1: NO(), 2: YES(), 3: YES(at="Germany", lag=-0.1, label="RUNNER-UP"), 4: YES(at="Portugal", lag=-0.1, label="RUNNER-UP")}, y=760, delay=0),
           {"type": "drawpot", "y": 1500, "delay": 0.2, "r": 250, "balls": BALLS[:5], "title": "Possible opponents", "clear": False}]})
# 8 dates
B.append({"kicker": "The dates", "headline": "Draw: [Friday 20 November].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_WEM, "accent": GOLD, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 16, -30], "tgt": [0, 0, 10]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "flip", "y": 700, "at": "Friday", "lag": -0.3, "label": "Quarter-final draw", "groups": [{"label": "November", "value": 20, "digits": 2}], "side": {"top": "FRI", "big": "20", "bottom": "NOV"}},
           {"type": "tickets", "y": 1200, "at": "The ties", "lag": 0, "done": 1, "tw": 720, "th": 250, "dx": 0, "tickets": [{"comp": "Quarter-final · 1st leg", "teams": "? v England", "score": "AWAY", "date": "25–27 March 2027", "color": "#1c2c5b"}], "clear": False},
           {"type": "tickets", "y": 1520, "at": "two legs", "lag": -0.3, "done": 1, "tw": 720, "th": 250, "dx": 0, "tickets": [{"comp": "Quarter-final · 2nd leg", "teams": "England v ?", "score": "HOME", "date": "28–30 March 2027", "color": "#c8102e"}], "clear": False}]})
# 9 never won it
B.append({"kicker": "The finals", "headline": "A trophy England have [never won].", "cut": True, "transition": "whip", "scene": S_WEM, "accent": GOLD, "lights": 0.5, "flashes": 16,
  "camFrom": {"pos": [0, 20, -36], "tgt": [0, 2, 6]}, "camera": {"pos": [0, 9, -20], "tgt": [0, 2, 8]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "career", "title": "England's road", "y": 1000, "w": 900, "rowH": 190, "clear": False, "items": [{"name": "Group A3", "sub": "Top", "color": "#1c2c5b", "result": "Won", "good": True},
             {"name": "Quarter-final", "sub": "March 2027", "color": "#1c2c5b", "result": "Two legs", "at": "Win that", "good": True}, {"name": "Finals", "sub": "Semi-final and final", "color": "#b8892a", "result": "Never won", "at": "the finals"}]},
           {"type": "trophies", "at": "never won", "lag": -0.4, "floor": 1860, "stagger": 0, "rise": 0.55, "items": [{"kind": "cup", "sx": 0.5, "h": 110, "size": 190, "label": "Nations League"}], "clear": False}]})
# 10 the question
B.append({"kicker": "Your call", "headline": "Who do you [want]?", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_WEM, "accent": GOLD, "flashes": 12,
  "orbit": {"center": [0, 1.25, 3], "r": 5.2, "from": -28, "to": 16, "h": 1.5, "h2": 1.9, "dur": 6}, "camera": {"pos": [0, 1.7, -2], "tgt": [0, 1.25, 3]},
  "players": [E(skin="#e7b593", hair="#3a2a1a", x=0, z=3.4, front=True, pose="fists")],
  "card": [{"type": "poll", "y": 1560, "at": "Belgium", "lag": -0.5, "question": "England's quarter-final?", "options": [{"label": "Belgium", "color": "#c8102e", "fill": 0.4}, {"label": "Germany", "color": "#5d6470", "fill": 0.4}, {"label": "Netherlands", "color": "#f36c21", "fill": 0.4}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 10
json.dump({"title": "England top the group: what next?", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open(V + 'spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
