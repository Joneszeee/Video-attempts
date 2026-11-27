# Engine test (not a video): the `divisions` card (built for videos/city-part-6): clubs fall from the Premier League and rise from League One into the Championship.
import json, sys
sys.path.insert(0, 'engine')
from lib import *
S_SIM = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], 21)
def bd(c1, c2, c3, text, style=None): return {"colors": [c1, c2, c3], "text": text, **({"style": style} if style else {})}
SUN = bd("#d6283b", "#ffffff", "#111111", "SUN", "stripes"); MUN = bd("#d6283b", "#111111", "#f7d117", "MUN"); CRY = bd("#1b458f", "#c4122e", "#ffffff", "CRY", "stripes")
MKD = bd("#ffffff", "#111111", "#d6283b", "MKD"); STK = bd("#1b4fb5", "#ffffff", "#ffffff", "STK"); MCI = bd(SKY, "#1c2c5b", "#ffffff", "MCI")
card = {"type": "divisions", "y": 1030, "tiers": ["PREMIER LEAGUE", "CHAMPIONSHIP", "LEAGUE ONE"], "focus": 1, "note": "+ 18 clubs stay", "cols": 6, "delay": 0.0, "clear": False, "moves": [
  {"name": "Sunderland", "badge": SUN, "from": 0, "to": 1, "col": 0, "t": 1.0}, {"name": "Man United", "badge": MUN, "from": 0, "to": 1, "col": 1, "t": 1.7}, {"name": "Crystal Palace", "badge": CRY, "from": 0, "to": 1, "col": 2, "t": 2.4},
  {"name": "MK Dons", "badge": MKD, "from": 2, "to": 1, "col": 3, "t": 4.5}, {"name": "Stockport", "badge": STK, "from": 2, "to": 1, "col": 4, "t": 5.2}, {"name": "Man City", "badge": MCI, "from": 2, "to": 1, "col": 5, "t": 5.9}]}
B = [{"kicker": "test", "headline": "Down. And [up].", "duration": 9, "cut": True, "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3, "camFrom": {"pos": [-24, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [22, 14, -22], "tgt": [0, 0, 6]}, "move": 9, "players": [], "card": [card]}]
json.dump({"title": "test", "brand": "theo6k", "accent": TEAL, "voSpeed": 1.0, "beats": B}, open('videos/_test-divisions/spec.json', 'w'), indent=1)
print('ok')
