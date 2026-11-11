# Builds videos/kane-snub/spec.json (run from the repo root).
import json
GOLD, RED, BLUE = "#e9b949", "#ff4d5e", "#4da3ff"
BAY = {"shirt": "#dc052d", "shorts": "#dc052d", "socks": "#dc052d", "text": "#ffffff"}
MIA = {"shirt": "#f7b5cd", "shorts": "#1d1c22", "socks": "#f7b5cd", "text": "#1d1c22"}
S_GOLD = {"type": "stadium", "crowd": ["#c9a227", "#ffffff", "#1b2a4a", "#c9a227"], "seed": 8}
S_DARK = {"type": "stadium", "crowd": ["#2a3040", "#4da3ff", "#8a93a6", "#1b2233"], "seed": 5}
S_BAY = {"type": "stadium", "crowd": ["#dc052d", "#ffffff", "#dc052d", "#1d1c22"], "seed": 14}
S_MIA = {"type": "stadium", "crowd": ["#f7b5cd", "#1d1c22", "#f7b5cd", "#ffffff"], "seed": 22}
lines = [l.strip() for l in open('videos/kane-snub/vo.txt').read().split('<break time="0.8s" />')]
def P(**k):
    d = {"name": "", "num": None}; d.update(k); return d
def kane(**k): return P(name="Kane", num=9, kit=BAY, skin="#e9b896", hair="#8a6a45", **k)
def kane_suit(**k): return P(outfit="suit", suitColor="#1a1d26", skin="#e9b896", hair="#8a6a45", **k)
XI = [("Raya", .5, .9, "#f2c200"), ("Hakimi", .2, .68, "#1b2a4a"), ("Cubarsí", .5, .7, "#a50044"), ("N. Mendes", .8, .68, "#1b2a4a"),
      ("Vitinha", .22, .47, "#1b2a4a"), ("Rodri", .5, .49, "#6cabdd"), ("Bellingham", .78, .47, "#f4f4f2")]
FW = [("Mbappé", .32, .13, "#f4f4f2"), ("Haaland", .68, .13, "#6cabdd"), ("Yamal", .86, .27, "#a50044"), ("Messi", .14, .27, "#f7b5cd")]
def lineup(fw_at=None, **k):
    items = [{"name": n, "x": x, "y": y, "color": c} for n, x, y, c in XI]
    for n, x, y, c in FW:
        it = {"name": n, "x": x, "y": y, "color": c}
        if fw_at: it["at"] = fw_at[n]
        items.append(it)
    d = {"type": "lineup", "title": "FIFPRO World XI · 2026", "items": items, "clear": False}; d.update(k); return d
B = []
# 1 hook: split. Left: Kane with the Ballon d'Or. Right: the players' team sheet with one man missing.
B.append({"kicker": "Ballon d'Or winner · 2026", "headline": "Best in the world. [Not in the XI].", "hookWords": True, "scene": S_GOLD, "accent": RED, "flashes": 16,
  "camFrom": {"pos": [0, 1.5, -2.0], "tgt": [0, 1.45, 10]}, "camera": {"pos": [0, 1.45, -1.1], "tgt": [0, 1.45, 10]}, "move": 6, "moveEase": "linear",
  "players": [kane_suit(x=0, z=2.6, front=True, pose="arms_up")],
  "split": {"scene": S_DARK, "lights": 0.45, "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 22, -38], "tgt": [0, 0, 8]}, "players": []},
  "card": [{"type": "trophies", "delay": -1.1, "floor": 800, "stagger": 0, "items": [{"kind": "ballondor", "sx": 0.25, "h": 0, "size": 130}]},
           lineup(instant=True, delay=-1, w=480, shiftX=268, y=1130, title="Players' World XI", empty={"x": .5, "y": .3, "label": "Kane", "t": 0}),
           {"type": "stamp", "text": "BEST", "sub": "journalists", "at": "best player", "color": GOLD, "rot": -0.1, "size": 62, "dx": -270, "y": 1600},
           {"type": "stamp", "text": "LEFT OUT", "sub": "players", "at": "left him out", "color": RED, "rot": 0.08, "size": 62, "dx": 268, "y": 1600}],
  "shake": [{"at": "left him out", "lag": 0.16, "amount": 14}]})
# 2 the date, then the players' ballot box
B.append({"kicker": "Monday · 9 November 2026", "headline": "The players [vote].", "cut": True, "transition": "whip", "scene": S_DARK, "accent": BLUE, "lights": 0.8,
  "camFrom": {"pos": [0, 60, -95], "tgt": [0, 0, 0]}, "camera": {"pos": [0, 26, -44], "tgt": [0, 0, 10]}, "move": 3, "players": [],
  "card": [{"type": "flip", "y": 760, "at": "ninth", "lag": -0.3, "label": "FIFPRO World XI", "groups": [{"label": "November", "value": 9, "digits": 2}], "side": {"top": "MON", "big": "9", "bottom": "NOV"}}],
  "shots": [{"at": "FIFPRO names", "lag": -0.1, "cut": True, "transition": "whip", "whipDir": -1, "lights": 0.55, "focus": 0.5, "move": 5, "moveEase": "linear",
     "camFrom": {"pos": [0, 30, -50], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 18, -32], "tgt": [0, 0, 8]}, "players": [],
     "card": [{"type": "ballot", "y": 1250, "delay": 0, "title": "World XI", "sub": "Players' vote", "color": BLUE, "n": 26, "dur": 3.4, "w": 420},
              {"type": "flytext", "text": "THOUSANDS", "size": 150, "endScale": 0.62, "y": 760, "at": "thousands", "color": "#ffffff", "clear": False}]}]})
# 3 the front four pop onto the team sheet, then Messi's 18th
fw_at = {"Mbappé": "Mbappé", "Haaland": "Haaland", "Yamal": "Yamal", "Messi": "Lionel Messi"}
B.append({"kicker": "The front four", "headline": "Mbappé. Haaland. Yamal. [Messi].", "cut": True, "scene": S_DARK, "accent": GOLD, "lights": 0.5, "focus": 0.5,
  "camFrom": {"pos": [0, 26, -44], "tgt": [0, 0, 8]}, "camera": {"pos": [0, 20, -34], "tgt": [0, 0, 8]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [lineup(fw_at=fw_at, delay=0, y=1180, w=780)],
  "shots": [{"at": "in for a record", "lag": -0.15, "cut": True, "transition": "whip", "scene": S_MIA, "lights": 1, "focus": 0, "flashes": 16,
     "orbit": {"center": [0, 1.25, 2.4], "r": 4.2, "from": -28, "to": 12, "h": 1.3, "h2": 1.6, "dur": 3.5}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.25, 2.4]},
     "players": [P(name="Messi", num=10, kit=MIA, skin="#e9bd9a", hair="#5a3a22", x=0, z=2.4, front=True, chest=True, pose="fists", tag=18, tagLabel="World XIs", tagDelay=0.25)],
     "card": [{"type": "stamp", "text": "RECORD", "sub": "18th World XI", "at": "eighteenth", "color": GOLD, "rot": -0.08, "size": 100, "y": 1600}],
     "confetti": True, "confettiDelay": 0.3, "confettiColors": ["#f7b5cd", "#ffffff", "#e9b949"]}]})
# 4 No Harry Kane: the empty slot
B.append({"kicker": "The man missing", "headline": "One name missing: [Harry Kane].", "cut": True, "scene": S_DARK, "accent": RED, "lights": 0.45, "focus": 0.5,
  "camFrom": {"pos": [0, 22, -38], "tgt": [0, 0, 8]}, "camera": {"pos": [0, 16, -28], "tgt": [0, 0, 8]}, "move": 3, "moveEase": "linear", "players": [],
  "card": [lineup(instant=True, delay=0, y=1180, w=780, empty={"x": .5, "y": .3, "label": "Kane · 5th", "t": 0.15}),
           {"type": "stamp", "text": "LEFT OUT", "delay": 0.7, "color": RED, "rot": -0.09, "size": 110, "y": 1730}],
  "punch": [{"t": 0.15, "amount": 0.16, "dur": 1.6, "x": 540, "y": 900}], "shake": [{"t": 0.86, "amount": 16}]})
# 5 two weeks earlier: the Ballon d'Or, by 28 points
B.append({"kicker": "26 October 2026 · London", "headline": "He won the [Ballon d'Or].", "cut": True, "transition": "polaroid", "polaroidLabel": "2 weeks earlier", "scene": {"type": "stage"}, "accent": GOLD, "focus": 0.35,
  "zoomFrom": 1.0, "zoom": 1.14,
  "players": [kane_suit(sx=0.5, sy=1640, scale=1.15, front=True, pose="arms_up")],
  "card": [{"type": "trophies", "delay": 0.1, "floor": 1000, "stagger": 0, "rise": 0.5, "items": [{"kind": "ballondor", "sx": 0.5, "h": 0, "size": 190}], "hideAt": "He beat", "hideLag": -0.2},
           {"type": "tape", "y": 900, "at": "He beat", "lag": -0.2, "left": {"name": "Kane", "color": "#dc052d"}, "right": {"name": "Mbappé", "color": "#f4f4f2"},
            "rows": [{"label": "Ballon d'Or points", "left": 1055, "right": 1027, "t": 0.2, "floor": 950}], "caption": "+28", "captionAt": "twenty-eight"}],
  "confetti": True, "confettiDelay": 0.2, "confettiColors": ["#e9b949", "#ffffff"]})
# 6 the twist: two ballot boxes
B.append({"kicker": "Two different votes", "headline": "Journalists v [players].", "cut": True, "transition": "vhs", "vhsLabel": "THE TWIST", "vhsDur": 0.9, "scene": S_DARK, "accent": BLUE, "lights": 0.5, "focus": 0.45,
  "camFrom": {"pos": [0, 34, -56], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 16, -28], "tgt": [0, 0, 8]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [{"type": "ballot", "y": 1200, "shiftX": -262, "at": "That award", "title": "Ballon d'Or", "sub": "Journalists", "color": GOLD, "n": 12, "dur": 2.6, "w": 400, "seed": 4, "clear": False},
           {"type": "ballot", "y": 1200, "shiftX": 262, "at": "This team", "title": "World XI", "sub": "Players", "color": BLUE, "n": 14, "dur": 2.0, "w": 400, "seed": 9, "clear": False},
           {"type": "flytext", "text": "VS", "size": 170, "endScale": 0.6, "y": 1200, "at": "This team", "lag": 0.2, "color": "#ffffff", "clear": False}]})
# 7 Kane finished fifth
B.append({"kicker": "The forwards' vote", "headline": "Kane finished [fifth].", "cut": True, "transition": "whip", "scene": S_BAY, "accent": RED, "lights": 0.6,
  "camFrom": {"pos": [0.8, 1.6, -2.8], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.1, 1.5, -0.8], "tgt": [0, 1.35, 10]}, "move": 3.5, "moveEase": "linear",
  "players": [kane(x=0, z=2.4, front=True, chest=True)],
  "card": [{"type": "big", "at": "fifth", "lag": -0.5, "from": 1, "value": 5, "countDur": 0.6, "suffix": "th", "label": "Top four make the team", "y": 1560, "style": "accent", "size": 280}],
  "freezeAt": "fifth", "freezeLag": 0.25})
# 8 photo finish: 27.6 v 28.4
B.append({"kicker": "Share of the vote", "headline": "27.6% v [28.4%].", "cut": True,
  "scene": {"type": "booth", "crowd": ["#dc052d", "#6cabdd", "#ffffff"], "seed": 9, "screenLeft": ["KANE", "5TH"], "screenRight": ["HAALAND", "4TH"]}, "accent": GOLD,
  "players": [P(kit={"shirt": "#2b2f3a", "shorts": "#2b2f3a", "socks": "#2b2f3a", "text": "#ffffff"}, skin="#e2b08c", hair="#3a2a1a", headset=True, sx=0.5, scale=0.75, front=True, pose="think")],
  "card": [{"type": "photofinish", "y": 800, "delay": 0, "title": "Forwards · share of the players' vote", "dur": 3.2, "floor": 26.8, "gap": "0.8%", "gapAt": "twenty-eight point four", "gapLag": 0.9,
            "rows": [{"name": "Harry Kane · 5th", "value": 27.6, "color": "#dc052d"}, {"name": "Erling Haaland · 4th", "value": 28.4, "color": "#6cabdd"}], "clear": False}]})
# 9 missed out by less than one percent
B.append({"kicker": "The gap", "headline": "Less than [one percent].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_BAY, "accent": RED, "lights": 0.4,
  "camFrom": {"pos": [-1.0, 1.7, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [-0.2, 1.5, -1.2], "tgt": [0, 1.35, 10]}, "move": 3, "moveEase": "linear",
  "players": [kane(x=0, z=2.4, front=True, chest=True)],
  "card": [{"type": "flytext", "text": "0.8%", "size": 330, "endScale": 0.8, "y": 1560, "at": "less than", "lag": -0.2, "color": RED, "clear": False}],
  "shake": [{"at": "less than", "lag": 0.25, "amount": 18}], "speedlines": [{"at": "less than", "lag": -0.2, "dur": 0.9, "amount": 0.6}]})
# 10 first ever
B.append({"kicker": "History", "headline": "It had [never] happened.", "cut": True, "scene": S_GOLD, "accent": GOLD, "lights": 0.6, "focus": 0.35,
  "camFrom": {"pos": [0, 40, -66], "tgt": [0, 0, 5]}, "camera": {"pos": [0, 14, -26], "tgt": [0, 0, 10]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "newspaper", "delay": 0.1, "y": 1120, "masthead": "THE FOOTBALL ECHO", "dateline": "Tuesday 10 November 2026",
            "headline": "BALLON D'OR WINNER\nLEFT OUT OF WORLD XI", "sub": "A first in the award's history", "color": "#2a2116", "spin": 1.4, "scale": 0.92},
           {"type": "stamp", "text": "FIRST EVER", "at": "Until now", "color": RED, "rot": -0.1, "size": 110, "y": 1660}]})
# 11 who got it right? scales + poll
B.append({"kicker": "Your call", "headline": "Who got it [right]?", "cut": True, "transition": "whip", "scene": S_BAY, "accent": GOLD, "flashes": 12,
  "orbit": {"center": [0, 1.25, 2.6], "r": 4.6, "from": -26, "to": 18, "h": 1.4, "h2": 1.8, "dur": 6}, "camera": {"pos": [0, 1.6, -2], "tgt": [0, 1.25, 2.6]},
  "players": [kane(x=0, z=2.6, front=True, chest=True, pose="fists")],
  "card": [{"type": "stamp", "text": "BEST", "sub": "journalists", "delay": 0.3, "color": GOLD, "rot": -0.1, "size": 58, "dx": -300, "y": 1290},
           {"type": "stamp", "text": "5TH", "sub": "players", "delay": 0.8, "color": BLUE, "rot": 0.08, "size": 58, "dx": 300, "y": 1290},
           {"type": "poll", "y": 1600, "at": "the journalists", "lag": -0.3, "question": "Who got it right?", "options": [{"label": "Journalists", "color": "#e9b949", "fill": 0.5}, {"label": "Players", "color": "#4da3ff", "fill": 0.5}]}]})
for b, v in zip(B, lines): b["vo"] = v
assert len(B) == len(lines) == 11
json.dump({"title": "Kane left out of the World XI", "brand": "theo6k", "accent": GOLD, "voSpeed": 1.08, "beats": B}, open('videos/kane-snub/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
