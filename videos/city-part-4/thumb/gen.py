"""Thumbnail for Part 4: Wembley under lights, McCracken in City's goalkeeper yellow in close-up, the question in shout text, SIGNED stamped under him."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, stadium, P, SKY, TEAL, GOLD, GREEN, GK_YELLOW

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
BRA = kit("#7a1428", "#111111", "#7a1428", text="#f5b301", stripes=["#7a1428", "#f5b301"])
S_WEM = stadium([SKY, "#ffffff", "#7a1428", "#f5b301"], 41)
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": S_WEM, "accent": TEAL, "lights": 0.75, "flashes": 16, "focus": 0.15,
        "camFrom": {"pos": [0, 1.45, -3.9], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -3.9], "tgt": [0, 1.35, 10]}, "move": 0.1, "moveEase": "linear",
        "players": [P(kit=GK_YELLOW, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", name="McCRACKEN", num=1, x=0, z=0.5, front=True, chest=True, pose="fists"),
                    P(kit=BRA, skin="#e7b593", hair="#1a1210", name="", num=None, x=-1.7, z=3.0, front=True)],
        "card": [{"type": "shout", "text": "PART 4", "y": 300, "size": 120, "delay": -3, "rot": -0.04, "clear": False, "color": TEAL, "color2": "#2bb39c"},
                 {"type": "shout", "text": "THE KEEPER WHO\nBEAT CITY", "y": 560, "size": 150, "delay": -3, "rot": -0.03, "clear": False},
                 {"type": "stamp", "text": "SIGNED", "sub": "Jon McCracken · your vote", "delay": -3, "color": GREEN, "rot": -0.06, "size": 100, "y": 1640, "clear": False}]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/city-part-4/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
