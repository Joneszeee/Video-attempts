"""Thumbnail: Pochettino close-up at Anfield, the red card slamming in, '13 MINUTES' in shout text, the score underneath."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import stadium, P, TEAL

ANF = stadium(["#d11317", "#ffffff", "#d11317", "#f2d36b"], 8)
poch = P(outfit="suit", suitColor="#1c1f28", tie="#7a1420", skin="#e2b08c", hair="#3a3a3e", x=-0.45, z=2.0, front=True)
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": ANF, "accent": TEAL, "lights": 0.8, "flashes": 16, "focus": 0.1,
        "camFrom": {"pos": [0, 1.5, -0.8], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -0.8], "tgt": [0, 1.3, 10]}, "move": 0.1, "moveEase": "linear",
        "players": [poch],
        "card": [{"type": "redcard", "delay": -3, "dx": 300, "y": 1420},
                 {"type": "shout", "text": "POCHETTINO'S DEBUT", "y": 330, "size": 100, "delay": -3, "rot": -0.04, "clear": False, "color": "#ffffff", "color2": "#d9dde6"},
                 {"type": "shout", "text": "13 MINUTES", "y": 600, "size": 230, "delay": -3, "rot": -0.03, "clear": False},
                 {"type": "stamp", "text": "LIVERPOOL 4–0 UNITED", "sub": "Anfield · 22 Nov 2026", "delay": -3, "color": "#ff4d5e", "rot": -0.05, "size": 72, "y": 1680, "clear": False}]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/pochettino-debut/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
