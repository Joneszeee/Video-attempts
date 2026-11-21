"""Thumbnail for Part 3: Wembley under lights, Haaland in close-up for the play-off final, the score bug at 0-0, the stakes in shout text."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, stadium, P, SKY, TEAL, GOLD

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
BRA = kit("#7a1428", "#111111", "#7a1428", text="#f5b301", stripes=["#7a1428", "#f5b301"])
S_WEM = stadium([SKY, "#ffffff", "#7a1428", "#f5b301"], 41)
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": S_WEM, "accent": TEAL, "lights": 0.75, "flashes": 16, "focus": 0.15,
        "camFrom": {"pos": [0, 1.45, -3.9], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -3.9], "tgt": [0, 1.35, 10]}, "move": 0.1, "moveEase": "linear",
        "players": [P(kit=CITY, skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, x=-0.55, z=0.6, front=True, chest=True, pose="fists"),
                    P(kit=BRA, skin="#e7b593", hair="#1a1210", name="BRADFORD", num=1, x=1.25, z=2.2, front=True)],
        "card": [{"type": "shout", "text": "PART 3", "y": 300, "size": 120, "delay": -3, "rot": -0.04, "clear": False, "color": TEAL, "color2": "#2bb39c"},
                 {"type": "shout", "text": "90 MINUTES\nFROM GOING UP", "y": 560, "size": 150, "delay": -3, "rot": -0.03, "clear": False},
                 {"type": "stamp", "text": "PLAY-OFF FINAL", "sub": "Man City v Bradford · Wembley", "delay": -3, "color": GOLD, "rot": -0.06, "size": 80, "y": 1640, "clear": False}]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/city-part-3/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
