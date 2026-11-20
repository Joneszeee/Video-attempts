"""Thumbnail: the stage face-off from the hook. Yamal and Messi at 19, goals per game over their heads, the crown on Yamal, the claim in shout text."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, GOLD, P

BAR26 = kit("#a50044", "#004d98", "#004d98", text="#edbb00", stripes=["#a50044", "#004d98"])
BAR06 = kit("#a50044", "#004d98", "#004d98", text="#f2f2f2", stripes=["#a50044", "#004d98"])
YAMAL = dict(kit=BAR26, skin="#9a6a48", hair="#1a1210", name="YAMAL", num=10)
MESSI = dict(kit=BAR06, skin="#f0c8a8", hair="#5a3a22", name="MESSI", num=19)

beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": {"type": "stage"}, "accent": GOLD, "zoomFrom": 1.04, "zoom": 1.04, "flashes": 12,
        "players": [P(**YAMAL, sx=0.3, sy=1750, scale=1.08, front=True, chest=True, tag=0.83, tagLabel="goals per game", tagDelay=-3, label="Yamal · 19", labelDelay=-3),
                    P(**MESSI, sx=0.7, sy=1750, scale=1.08, front=True, chest=True, tag=0.54, tagLabel="goals per game", tagDelay=-3, label="Messi · 19", labelDelay=-3)],
        "card": [{"type": "crown", "on": 0, "delay": -3},
                 {"type": "shout", "text": "YAMAL AT 19", "y": 340, "size": 120, "delay": -3, "rot": -0.04, "clear": False, "color": "#ffffff", "color2": "#d9dde6"},
                 {"type": "shout", "text": "BETTER THAN\nMESSI?", "y": 590, "size": 165, "delay": -3, "rot": -0.03, "clear": False}]}
json.dump({"brand": "theo6k", "accent": GOLD, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]},
          open('videos/yamal-messi-19/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
