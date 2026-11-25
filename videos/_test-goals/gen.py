# Engine test (not a video): the new keeper rig, seen from the front and from behind the net.
import json, sys
sys.path.insert(0, 'engine')
from lib import *
GK = kit("#f7d117", "#111111", "#f7d117", text="#111111")
S = stadium([SKY, "#ffffff", SKY, "#1c2c5b"], 6)
keeper = lambda **k: P(kit=GK, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", pose="keeper", **k)
B = []
CITY = kit(SKY, '#ffffff', SKY, text='#1c2c5b')
OPP = kit('#d6283b', '#ffffff', '#d6283b', text='#ffffff')
GKY = kit('#f7d117', '#111111', '#f7d117', text='#111111')
GKG = kit('#2ecc71', '#111111', '#2ecc71', text='#111111')
KEEP = []
# 1: front view, 7 s: ready + shuffle (0-1.5), lunge right (1.6), lunge left (2.6), dive right (3.6, holds), get up (5.2)
KEEP.append({"kicker": "test", "headline": "Keeper from the front.", "duration": 7.0, "scene": S, "accent": TEAL, "hype": False, "lights": 1,
          "camFrom": {"pos": [0, 1.3, 41], "tgt": [0, 0.9, 52]}, "camera": {"pos": [0, 1.3, 41], "tgt": [0, 0.9, 52]}, "move": 0.1,
          "players": [keeper(x=0, z=52, front=True, actions=[{"action": "lunge", "dir": 1, "delay": 1.6}, {"action": "lunge", "dir": -1, "delay": 2.6}, {"action": "dive", "dir": 1, "delay": 3.6}, {"action": "getup", "dir": 1, "delay": 5.2}])],
          "card": []})
# 2: from behind the net, a barrage-style set of reactions
KEEP.append({"kicker": "test", "headline": "Keeper from behind.", "duration": 7.0, "cut": True, "scene": S, "accent": TEAL, "hype": False, "lights": 1,
          "camFrom": {"pos": [0, 1.6, 60.0], "tgt": [0, 1.0, 40]}, "camera": {"pos": [0, 1.6, 60.0], "tgt": [0, 1.0, 40]}, "move": 0.1,
          "players": [keeper(x=0, z=52, actions=[{"action": "lunge", "dir": 1, "delay": 1.6}, {"action": "lunge", "dir": -1, "delay": 2.6}, {"action": "dive", "dir": -1, "delay": 3.6}, {"action": "getup", "dir": -1, "delay": 5.2}])],
          "card": []})
pl, cards, cam, cut2 = goal_dribble(4.4, CITY, GKY, OPP, foot="left", label="Haaland", scorer=dict(name="HAALAND", num=9))
B.append({"kicker": "test", "headline": "Dribble and finish.", "duration": 4.4, "cut": True, "scene": S, "accent": TEAL, "lights": 1, "flashes": 12, **cam, "players": pl, "card": cards})
B.append({"kicker": "test", "headline": "Dribble and finish.", "duration": 2.6, "scene": S, "accent": TEAL, "lights": 1, **{k: v for k, v in cut2.items() if k != "transition"}, "card": "same"})
pl, cards, cam, cut2 = goal_curler(4.6, OPP, GKY, CITY, foot="right", label="Scorer")
B.append({"kicker": "test", "headline": "Long-range curler.", "duration": 4.6, "cut": True, "scene": S, "accent": TEAL, "lights": 1, "flashes": 12, **cam, "players": pl, "card": cards})
B.append({"kicker": "test", "headline": "Long-range curler.", "duration": 2.6, "scene": S, "accent": TEAL, "lights": 1, **{k: v for k, v in cut2.items() if k != "transition"}, "card": "same"})
json.dump({"title": "test", "brand": "theo6k", "accent": TEAL, "outro": False, "hookZoom": False, "beats": B}, open('videos/_test-goals/spec.json', 'w'), indent=1)
print('ok')
