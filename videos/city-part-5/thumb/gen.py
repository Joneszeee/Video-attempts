"""Thumbnail for Part 5: Haaland in City's kit in close-up (fists up) with the two new signings behind, the claim in shout text, PROMOTED stamped under him."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, stadium, P, SKY, TEAL, GOLD, GREEN

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
S_GOLD = stadium(["#f1c453", "#ffffff", "#1c2c5b", SKY], 12)
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": S_GOLD, "accent": TEAL, "lights": 0.85, "flashes": 16, "focus": 0.15,
        "camFrom": {"pos": [0, 1.45, -4.1], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -4.1], "tgt": [0, 1.35, 10]}, "move": 0.1, "moveEase": "linear",
        "players": [P(kit=CITY, skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, x=0, z=0.5, front=True, chest=True, pose="fists"),
                    P(kit=CITY, skin="#f0c8a8", hair="#4a3324", name="", num=None, x=-2.0, z=3.4, front=True, label="Ward-Prowse", labelDelay=-3),
                    P(kit=CITY, skin="#e7b593", hair="#3a2a1a", name="", num=None, x=2.0, z=3.4, front=True, label="Moylan", labelDelay=-3)],
        "card": [{"type": "shout", "text": "PART 5", "y": 300, "size": 120, "delay": -3, "rot": -0.04, "clear": False, "color": TEAL, "color2": "#2bb39c"},
                 {"type": "shout", "text": "FROM 4TH TO\nCHAMPIONS", "y": 560, "size": 150, "delay": -3, "rot": -0.03, "clear": False},
                 {"type": "stamp", "text": "PROMOTED", "sub": "your signings · simulated", "delay": -3, "color": GREEN, "rot": -0.06, "size": 100, "y": 1640, "clear": False}]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/city-part-5/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
