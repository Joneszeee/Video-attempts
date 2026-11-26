# Engine test (not a video): penalty (saved / scored), bundle, divot goal, cross and finish, disallowed goal (builders in engine/lib.py, built for videos/united-sporting).
import json, sys
sys.path.insert(0, 'engine')
from lib import *
SPT = kit("#0b8f4b", "#ffffff", "#0b8f4b", text="#ffffff", hoops=["#0b8f4b", "#ffffff"])
MUN = kit("#d6283b", "#ffffff", "#111111", text="#ffffff")
GKM = kit("#ff7a1a", "#111111", "#ff7a1a", text="#111111")      # Lammens
GKS = kit("#7a4de0", "#111111", "#7a4de0", text="#ffffff")      # Kaique
S = stadium(["#0b8f4b", "#ffffff", "#0b8f4b", "#111111"], 11)
B = []
def beat(title, dur, pl, cards, camk, **k):
    d = {"kicker": "test", "headline": title, "duration": dur, "cut": True, "scene": S, "accent": TEAL, "lights": 1, "flashes": 12, **camk, "players": pl, "card": cards}
    d.update(k); return d
# 0-5.6: penalty saved (word 4.0)
pl, cards, camk = penalty(4.0, SPT, GKM, outcome="saved", label="Suárez", kicker=dict(name="SUÁREZ", num=97))
B.append(beat("Penalty saved.", 5.6, pl, cards, camk))
# 5.6-11.2: penalty scored (word 4.0)
pl, cards, camk = penalty(4.0, SPT, GKM, outcome="scored", corner=-1, label="Suárez", kicker=dict(name="SUÁREZ", num=97))
B.append(beat("Penalty scored.", 5.6, pl, cards, camk))
# 11.2-15.7: bundle (word 2.6)
pl, cards, camk = bundle(2.6, SPT, GKM, label="Araújo", victim=dict(name="ARAÚJO", num=22))
B.append(beat("Keeper bundles him.", 4.5, pl, cards, camk))
# 15.7-17.7 + 17.7-21.5: divot (word 3.6; cut at 3.6 - 1.9 + 0.3 = 2.0)
pl, cards, camk, cut2 = goal_divot(3.6, MUN, GKS, SPT, foot="left", label="Bruno", shooter=dict(name="B. FERNANDES", num=8))
B.append(beat("Divot goal.", 2.0, pl, cards, camk))
B.append({"kicker": "test", "headline": "Divot goal.", "duration": 3.8, "scene": S, "accent": TEAL, "lights": 1, **cut2, "card": "same"})
# 21.5-26.9: cross (word 3.4)
pl, cards, camk = goal_cross(3.4, SPT, GKM, MUN, label="Suárez", scorer=dict(name="SUÁREZ", num=97))
B.append(beat("Cross and finish.", 5.2, pl, cards, camk))
# 26.7-31.9: disallowed (word 3.2)
pl, cards, camk = disallowed(3.2, MUN, GKS, SPT, label="Amad", scorer=dict(name="AMAD", num=16))
B.append(beat("Whistle first.", 5.0, pl, cards, camk))
# 31.7-40.2: disallowed again with the varcheck card (numeric times)
pl, cards, camk = disallowed(3.2, MUN, GKS, SPT, label="Amad", scorer=dict(name="AMAD", num=16))
vc = {"type": "varcheck", "title": "VAR · 40'", "y": 1330, "rowH": 84, "w": 940, "source": "per ESPN match report",
      "steps": [{"text": "Tielemans plays Amad in", "t": 3.6, "kind": "ball"}, {"text": "Amad shoots: onto the bar", "t": 4.3, "kind": "ball"}, {"text": "Referee blows the whistle", "t": 5.0, "kind": "whistle", "tag": "TOO EARLY", "tagColor": "#ff4d5e"}, {"text": "Amad heads in the loose ball", "t": 5.7, "kind": "goal"}],
      "verdict": {"text": "NO GOAL", "sub": "VAR can't review", "color": "#ff4d5e", "t": 6.5}}
B.append(beat("Whistle first.", 8.5, pl, cards + [vc], camk))
# 40.2-45.7: penalty scored + the tracker
pl, cards, camk = penalty(4.0, SPT, GKM, outcome="scored", corner=-1, label="Suárez", kicker=dict(name="SUÁREZ", num=97))
pt = {"type": "pentrack", "title": "PENALTIES", "y": 1560, "items": [{"who": "Suárez", "min": "30'", "state": "miss", "result": "SAVED"}, {"who": "Suárez", "min": "33'", "state": "hit", "result": "GOAL", "t": 3.9}, {"who": "Bruno", "min": "48'", "state": "empty"}]}
B.append(beat("Penalty tracker.", 5.5, pl, cards + [pt], camk))
json.dump({"title": "test", "brand": "theo6k", "accent": TEAL, "outro": False, "hookZoom": False, "beats": B}, open('videos/_test-united/spec.json', 'w'), indent=1)
t = 0.0
for b in B:
    print(round(t, 2), b['headline']); t += b['duration']
print('total', t)
