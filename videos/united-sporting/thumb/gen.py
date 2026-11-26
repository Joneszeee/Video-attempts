"""Thumbnail for Sporting 2-2 Man United (user's pick: the score as the headline, Suarez and Bruno Fernandes face to face): the two scorers side by side in close-up, Sporting's hoops v United's red,
the search-friendly claim in shout text, the three oddities stamped under them."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, stadium, P, TEAL, GOLD, RED

SPT = kit("#0b8f4b", "#ffffff", "#0b8f4b", text="#111111", hoops=["#0b8f4b", "#ffffff"])
MUN = kit("#d6283b", "#ffffff", "#111111", text="#ffffff")
S = stadium(["#0b8f4b", "#ffffff", "#0b8f4b", "#d6283b"], 11)
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": S, "accent": TEAL, "lights": 0.85, "flashes": 16, "focus": 0.15,
        "camFrom": {"pos": [0, 1.45, -3.3], "tgt": [0, 1.6, 10]}, "camera": {"pos": [0, 1.45, -3.3], "tgt": [0, 1.6, 10]}, "move": 0.1, "moveEase": "linear",
        "players": [P(kit=SPT, skin="#c99b7a", hair="#141010", name="SUÁREZ", num=97, x=-0.66, z=0.4, front=True, chest=True, pose="fists"),
                    P(kit=MUN, skin="#f0c8a8", hair="#6a4a2a", name="FERNANDES", num=8, x=0.66, z=0.4, front=True, chest=True, pose="fists")],
        "card": [{"type": "shout", "text": "SPORTING 2–2\nMAN UNITED", "y": 470, "size": 150, "delay": -3, "rot": -0.03, "clear": False},
                 {"type": "shout", "text": "3 PENALTIES · 1 DIVOT", "y": 1745, "size": 78, "delay": -3, "rot": 0.02, "clear": False, "color": TEAL, "color2": "#2bb39c"}]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/united-sporting/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
