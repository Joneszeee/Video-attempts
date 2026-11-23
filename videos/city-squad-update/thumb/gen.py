"""Thumbnail for the squad update: the best card (Haaland 91) and the worst (Scarr 57) side by side under Wembley's lights, the numbers in shout text."""
import json
import sys
sys.path.insert(0, 'engine')
from lib import kit, stadium, SKY, TEAL, GOLD

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
S_WEM = stadium([SKY, "#ffffff", "#7a1428", "#f5b301"], 41)
Q = json.load(open('videos/city-league-two/data/squad.json')); R, ST = Q['ratings'], Q['stats']
assert R['Haaland']['ovr'] == 91 and R['Scarr']['ovr'] == 57
def card(nm, name, pos, rar, look, dx, entry, cells_now, cells_all):
    return {"type": "scard", "y": 1180, "name": name, "pos": pos, "ovr": R[nm]['ovr'], "rarity": rar, "player": dict(kit=CITY, name="", num=None, **look),
            "badge": {"colors": [SKY, "#1c2c5b", "#ffffff"], "text": "MCI"}, "rows": [{"label": "This season", "cells": cells_now}, {"label": "All-time", "cells": cells_all}],
            "foot": "sim rating · sim stats", "entry": entry, "dx": dx, "scale": 0.92, "snap": True, "delay": -4, "clear": False, "seed": 3 if nm == 'Haaland' else 8}
h, s = ST['Haaland'], ST['Scarr']
beat = {"kicker": "", "headline": "", "vo": "Thumbnail.", "scene": S_WEM, "accent": TEAL, "lights": 0.75, "flashes": 16, "focus": 0.2,
        "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "move": 0.1, "moveEase": "linear", "players": [],
        "card": [{"type": "shout", "text": "SQUAD UPDATE", "y": 290, "size": 110, "delay": -3, "rot": -0.04, "clear": False, "color": TEAL, "color2": "#2bb39c"},
                 {"type": "shout", "text": "HAALAND: 91\nWORST STARTER: 57", "y": 560, "size": 150, "delay": -3, "rot": -0.03, "clear": False},
                 card('Haaland', "HAALAND", "ST", "elite", dict(skin="#f1d3bd", hair="#d9b46a"), -255, "left",
                      [[h['now']['apps'], 'gp'], [h['now']['goals'], 'g'], [h['now']['assists'], 'a']], [[h['all']['apps'], 'gp'], [h['all']['goals'], 'g'], [h['all']['assists'], 'a']]),
                 card('Scarr', "SCARR", "CB", "bronze", dict(skin="#e7b593", hair="#141010"), 255, "right",
                      [[s['now']['apps'], 'gp'], [s['now']['cs'], 'cs'], [s['now']['goals'], 'g']], [[s['all']['apps'], 'gp'], [s['all']['cs'], 'cs'], [s['all']['goals'], 'g']])]}
json.dump({"brand": "theo6k", "accent": TEAL, "outro": False, "tail": 0, "hookZoom": False, "timings": [3], "beats": [beat]}, open('videos/city-squad-update/thumb/spec.json', 'w'), indent=1, ensure_ascii=False)
print("ok")
