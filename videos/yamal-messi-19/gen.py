# Builds videos/yamal-messi-19/spec.json (run from the repo root). Facts: research.md (ESPN game logs in data/).
import sys
sys.path.insert(0, 'engine')
from lib import *

V, lines = start('videos/yamal-messi-19/')
BAR26 = kit("#a50044", "#004d98", "#004d98", text="#edbb00", stripes=["#a50044", "#004d98"])
BAR06 = kit("#a50044", "#004d98", "#004d98", text="#f2f2f2", stripes=["#a50044", "#004d98"])
RMA = kit("#f4f4f2", "#f4f4f2", "#f4f4f2", text="#1a1a1a")
CAMP = stadium(["#a50044", "#004d98", "#edbb00", "#a50044"], 11)
CAMP07 = stadium(["#a50044", "#004d98", "#a50044", "#f2f2f2"], 31)
S_DARK = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#4a1a2a"], 21)
YAMAL = dict(kit=BAR26, skin="#9a6a48", hair="#1a1210", name="YAMAL", num=10)
MESSI = dict(kit=BAR06, skin="#f0c8a8", hair="#5a3a22", name="MESSI", num=19)
BUG07 = lambda score, mn, frm=None, at=None, lag=0.3, **k: bug({"name": "BAR", "color": "#a50044"}, {"name": "RMA", "color": "#f4f4f2"}, score, mn, frm, at, lag, **k)
B = []

# 1 hook (stage face-off): goals per game pop over their heads, the crown drops onto Yamal
B.append({"kicker": "La Liga at 19 · Yamal v Messi", "headline": "Yamal at 19: [better than Messi]?", "hookWords": True, "scene": {"type": "stage"}, "accent": GOLD,
  "zoomFrom": 1.0, "zoom": 1.1, "flashes": 10,
  "players": [P(**YAMAL, sx=0.32, sy=1560, scale=1.0, front=True, chest=True, tag=0.83, tagLabel="goals per game", tagDelay=0.05, label="Yamal", labelDelay=0.0),
              P(**MESSI, sx=0.68, sy=1560, scale=1.0, front=True, chest=True, tag=0.54, tagLabel="goals per game", tagDelay=0.25, label="Messi", labelDelay=0.0)],
  "card": [{"type": "crown", "on": 0, "at": "better than Messi", "lag": -0.35}],
  "shake": [{"at": "better than Messi", "lag": 0.1, "amount": 14}]})

# 2 Yamal this season: a left-footed goal; 10 goals and 8 assists stack up; 12 starts out of 12
pl, cards, camk = goal("ten goals", 1.4, 40.5, 1, BAR26, [-2.8, 0.9, 52.3], 1, GK_GREEN, kit("#1f3f8f"), lag=-0.55, label="Yamal",
                       **{k: v for k, v in YAMAL.items() if k != "kit"}, foot="left")
B.append({"kicker": "La Liga 2026/27 · aged 19", "headline": "This season: [10 goals, 8 assists].", "cut": True, "transition": "whip", "scene": CAMP, "accent": GOLD, **camk,
  "players": pl,
  "card": cards + [{"type": "stack", "y": 760, "delay": 0, "items": [{"value": 10, "label": "goals", "at": "ten goals", "gold": True}, {"value": 8, "label": "assists", "at": "eight assists"}]},
                   {"type": "dots", "y": 1620, "at": "started every", "lag": -0.3, "n": 12, "step": 0.08, "label": "League starts", "caption": "12 of 12"}]})

# 3 Messi at 19 (polaroid flashback): dribbles past a lunging defender into the box and scores past a wrong-way keeper; 14 goals in 26 games
#   (user: the ball vanished and he stopped running, and there was no keeper). The ball stays at his feet until the strike, then flies in.
RUN, END = 2.8, [0.9, 39.5]                                   # path time, where he shoots from
FOOT = [END[0] - 0.22, 0.11, END[1] + 0.5]                    # ball by his left foot when he stops
HIT = RUN + 0.15                                               # contact
B.append({"kicker": "La Liga 2006/07 · aged 19", "headline": "Messi at 19: [14 goals] in 26.", "cut": True, "transition": "polaroid", "polaroidLabel": "Barcelona 2006/07", "scene": CAMP07, "accent": GOLD, "hype": False, "flashes": 10,
  "camFrom": {"pos": [-5.0, 2.4, 20.0], "tgt": [1.5, 1, 40]}, "camera": {"pos": [-6.6, 2.2, 30.5], "tgt": [0, 1, 44]}, "move": 4.5, "moveEase": "linear",
  "players": [P(**MESSI, x=1.5, z=30, path=[[1.5, 30], [0.4, 34], END], pathDur=RUN, dribble=True, dribbleUntil=RUN, foot="left", label="Messi", labelDelay=0.2,
                hops=[{"t": 1.15, "dur": 0.45, "height": 0.2}], action="kick", actionDelay=round(HIT - 0.42 * 0.8, 2), actionDur=0.8, after="celebrate"),
              P(kit=kit("#1f6b3a"), skin="#e7b593", hair="#141010", x=-0.4, z=34.6, front=True, action="dive", dir=1, actionDelay=1.0, actionDur=0.7),
              P(kit=kit("#1f6b3a"), skin="#8a5a3c", hair="#141010", x=2.8, z=44.5, front=True),
              P(kit=GK_YELLOW, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=1, actionDelay=round(HIT + 0.05, 2))],
  "card": [{"type": "ball", "delay": RUN, "point": FOOT, "until": round(HIT - RUN, 2)},
           {"type": "ballpath", "world": True, "delay": HIT, "dur": 0.5, "slowmo": False, "points": [FOOT, [-1.0, 1.0, 46], [-2.7, 0.9, 52.3]]},
           big(14, "fourteen goals", "La Liga goals · 26 games", y=1620, size=170, lag=-0.3)],
  "shake": [{"t": HIT + 0.5, "amount": 12}]})

# 4 per game: tale of the tape, Yamal's bar goes gold
B.append({"kicker": "Goals per game · La Liga at 19", "headline": "Per game: [0.83] v 0.54.", "cut": True, "transition": "whip", "whipDir": -1, "scene": CAMP, "accent": GOLD, "lights": 0.6, "focus": 0.3,
  "camFrom": {"pos": [24, 22, -34], "tgt": [0, 0, 6]}, "camera": {"pos": [-22, 14, -20], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "tape", "y": 1080, "delay": 0.1, "decimals": 2, "left": {"name": "Yamal 26/27", "color": "#a50044"}, "right": {"name": "Messi 06/07", "color": "#004d98"},
            "rows": [{"label": "Goals per game", "left": 0.83, "right": 0.54, "at": "point eight three", "lag": -0.4, "floor": 0.3}],
            "caption": "La Liga, both aged 19", "captionAt": "Point five four"}]})

# 5 Messi missed three months: the calendar crosses off 13 weeks (12 Nov 2006 to 11 Feb 2007, from his game log)
B.append({"kicker": "Messi 2006/07", "headline": "Messi missed [13 weeks].", "cut": True, "transition": "whip", "scene": S_DARK, "accent": RED, "lights": 0.45, "focus": 0.25,
  "camFrom": {"pos": [0, 1.6, -3.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.2], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
  "players": [P(**MESSI, x=1.6, z=4.0, front=True, ghost=True)],
  "card": [{"type": "crossoff", "y": 1060, "delay": 0.0, "shiftX": -110, "title": "OUT", "days": 13, "cols": 5, "cell": 110, "crossAt": "missed three months", "crossLag": -0.3, "dur": 1.4, "caption": "{n} weeks"}]})

# 6 re-hook: VHS back to March 2007; a newspaper spins in on the Clásico
B.append({"kicker": "El Clásico · 10 March 2007", "headline": "March 2007: [Real Madrid] at the Camp Nou.", "cut": True, "transition": "vhs", "vhsLabel": "2007", "vhsDur": 1.0, "scene": CAMP07, "accent": RED, "lights": 0.7, "focus": 0.2,
  "camFrom": {"pos": [0, 60, -80], "tgt": [0, 0, 5]}, "camera": {"pos": [18, 28, -44], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "newspaper", "y": 1150, "at": "March 2007", "lag": -0.3, "headline": "EL CLÁSICO", "sub": "Barcelona v Real Madrid", "dateline": "Saturday 10 March 2007", "masthead": "THE MATCHDAY POST", "color": "#a50044"}]})

# 7 Madrid ahead three times, Messi level three times: a seesaw of goals, popping in match order (5', 11', 13', 28', 73')
B.append({"kicker": "Barcelona v Real Madrid · 2007", "headline": "Madrid lead [three times].", "cut": True, "transition": "whip", "scene": CAMP07, "accent": RED, "lights": 0.6,
  "camFrom": {"pos": [0, 3.0, -9.0], "tgt": [0, 0.5, 4.0]}, "camera": {"pos": [0, 2.7, -5.8], "tgt": [0, 0.3, 4.0]}, "move": 4.5, "moveEase": "linear",
  "punch": [{"at": "equalises three times", "lag": 0.1, "amount": 0.12, "dur": 1.6}],
  "players": [P(**MESSI, x=-1.0, z=3.6, front=True, label="Messi", labelDelay=0.1), P(kit=RMA, skin="#f0c8a8", hair="#8a6a3a", x=1.2, z=3.8, front=True, pose="fists", label="Real Madrid", labelDelay=0.1)],
  "card": [{"type": "seesaw", "y": 1460, "rowH": 104, "delay": 0.0, "title": "Barcelona v Real Madrid · 10 March 2007", "clear": False,
            "left": {"name": "Real Madrid", "color": "#f4f4f2", "text": "#111111"}, "right": {"name": "Messi", "color": GOLD, "text": "#111111"},
            "items": [{"side": "left", "min": "5'", "who": "Van Nistelrooy", "score": "0–1", "at": "Madrid go ahead", "lag": -0.20},
                      {"side": "right", "min": "11'", "who": "Messi", "score": "1–1", "at": "Madrid go ahead", "lag": 0.52},
                      {"side": "left", "min": "13'", "who": "Van Nistelrooy", "score": "1–2", "at": "Madrid go ahead", "lag": 1.24},
                      {"side": "right", "min": "28'", "who": "Messi", "score": "2–2", "at": "Madrid go ahead", "lag": 1.96},
                      {"side": "left", "min": "73'", "who": "Sergio Ramos", "score": "2–3", "at": "Madrid go ahead", "lag": 2.68}]}]})

# 8 the 91st minute: Messi's equaliser, 3-3, a hat-trick at 19
pl, cards, camk = goal("ninety-first minute", -1.2, 41, -1, BAR06, [2.8, 1.0, 52.3], -1, GK_YELLOW, RMA, lag=-0.3, label="Messi",
                       **{k: v for k, v in MESSI.items() if k != "kit"}, foot="left")
B.append({"kicker": "90+1' · Camp Nou", "headline": "91st minute: [hat-trick] at 19.", "cut": True, "transition": "whip", "whipDir": -1, "scene": CAMP07, "accent": GOLD, **camk,
  "players": pl, "flashes": 16, "confetti": True, "confettiAt": "A hat-trick",
  "card": cards + [BUG07([3, 3], "90+1'", [2, 3], "ninety-first minute", 0.2), big(3, "A hat-trick", "Messi goals · 3–3", y=1600, size=180)]})

# 9 Yamal's Clásico, October 2026: Mbappé's winner, 1-2; freeze; Yamal 0 goals 0 assists
pl, cards, camk = goal("Mbappé scored twice", 1.0, 41, 1, RMA, [-2.8, 0.8, 52.3], 1, GK_YELLOW, BAR26, lag=-0.5, label="Mbappé", skin="#8a5a3c", hair="#141010")
B.append({"kicker": "El Clásico · 25 October 2026", "headline": "Yamal's Clásico: [lost 2–1].", "cut": True, "transition": "whip", "scene": CAMP, "accent": RED, **camk,
  "players": pl,
  "card": cards + [bug({"name": "BAR", "color": "#a50044"}, {"name": "RMA", "color": "#f4f4f2"}, [1, 2], "87'", [1, 1], "Mbappé scored twice", 0.2),
                   stamp("0 GOALS · 0 ASSISTS", "No goal", "Yamal v Real Madrid", y=1620, size=64)],
  "freezeAt": "No goal", "freezeLag": -0.2})

# 10 back to the stage: the crown leaves Yamal for Messi, then hovers between them; the vote
B.append({"kicker": "Your call", "headline": "Numbers or [the moment]?", "cut": True, "transition": "whip", "scene": {"type": "stage"}, "accent": GOLD, "zoomFrom": 1.08, "zoom": 1.0, "flashes": 8,
  "players": [P(**YAMAL, sx=0.3, sy=1400, scale=0.85, front=True, label="Yamal · the numbers", labelAt="Yamal has the numbers"),
              P(**MESSI, sx=0.7, sy=1400, scale=0.85, front=True, label="Messi · the moment", labelAt="Messi had the moment")],
  "card": [{"type": "crown", "on": 0, "delay": -3, "items": [{"to": 1, "at": "Messi had the moment", "lag": -0.2}, {"to": "both", "at": "Who was better", "lag": -0.3}]},
           {"type": "poll", "y": 1660, "at": "Who was better", "lag": -0.4, "question": "Who was better at 19?", "options": [{"label": "Yamal", "color": "#a50044", "fill": 0.5}, {"label": "Messi", "color": "#004d98", "fill": 0.5}]}]})

save(V, B, lines, "Yamal v Messi at 19", accent=GOLD)
