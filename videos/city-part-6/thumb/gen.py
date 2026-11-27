"""Thumbnail for Part 6: Haaland (City) and a red-shirted United player face to face, the claim in shout text ("CITY v UNITED IN THE CHAMPIONSHIP"), RELEGATED stamped across United (in our simulation)."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, stadium, P, SKY, TEAL, GOLD, RED

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
MUN = kit("#d6283b", "#ffffff", "#111111", text="#ffffff")
S_DERBY = stadium([SKY, "#d6283b", "#ffffff", "#1c2c5b"], 14)
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": S_DERBY, "accent": TEAL, "lights": 0.85, "flashes": 16, "focus": 0.15,
        "camFrom": {"pos": [0, 1.45, -1.75], "tgt": [0, 1.1, 10]}, "camera": {"pos": [0, 1.45, -1.75], "tgt": [0, 1.1, 10]}, "move": 0.1, "moveEase": "linear",
        "players": [P(kit=CITY, skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, x=-0.6, z=1.0, front=True, chest=True, pose="fists"),
                    P(kit=MUN, skin="#8a5a3c", hair="#141010", name="", num=7, x=0.6, z=1.0, front=True, chest=True)],
        "card": [{"type": "shout", "text": "PART 6", "y": 300, "size": 120, "delay": -3, "rot": -0.04, "clear": False, "color": TEAL, "color2": "#2bb39c"},
                 {"type": "shout", "text": "CITY v UNITED\nIN THE\nCHAMPIONSHIP", "y": 620, "size": 150, "delay": -3, "rot": -0.03, "clear": False},
                 {"type": "stamp", "text": "RELEGATED", "sub": "in our simulation", "delay": -3, "color": RED, "rot": -0.06, "size": 100, "y": 1500, "dx": 150, "clear": False}]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/city-part-6/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
