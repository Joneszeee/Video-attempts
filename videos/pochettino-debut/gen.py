# Builds videos/pochettino-debut/spec.json (run from the repo root). Liverpool 4-0 Man United, 22 Nov 2026: Pochettino's first game as United manager.
# Every minute, score and stat below is asserted against ESPN's match feed (data/fetch.py); the expected-goals pair (4.38 v 0.63) is from the user's
# match-stats screenshot. Kits are stylised (never real crests); United wear white here because their red would clash with Liverpool's.
import json
import re
import sys
sys.path.insert(0, 'engine')
from lib import *

D = 'videos/pochettino-debut/data/'
S = json.load(open(D + 'espn_summary.json'))
SH = json.load(open(D + 'shots.json'))
RES = json.load(open(D + 'united_results.json'))
TAB = json.load(open(D + 'table.json'))

# ---- facts the script relies on: the build stops if any of them is not in the data ----
KE = S['keyEvents']
at_ = lambda m, typ: [k for k in KE if k['clock']['displayValue'] == m and k['type']['text'].startswith(typ)]
assert 'Yoro' in at_("8'", 'Red Card')[0]['text']
goals = {k['clock']['displayValue']: re.search(r'\. (.+?) \(', k['text']).group(1) for k in KE if k['type']['text'].startswith('Goal')}
assert goals == {"10'": 'Dominik Szoboszlai', "13'": 'Florian Wirtz', "66'": 'Rio Ngumoha', "82'": 'Víctor Muñoz'}, goals
assert 'free kick' in at_("10'", 'Goal')[0]['text'].lower() and 'Assisted by Rio Ngumoha' in at_("13'", 'Goal')[0]['text']
subs = [(k['clock']['displayValue'], k['text']) for k in KE if k['type']['text'] == 'Substitution']
assert ("22'", 'Substitution, Manchester United. Harry Maguire replaces Bryan Mbeumo.') in subs
assert ("45'", 'Substitution, Manchester United. Joshua Zirkzee replaces Matheus Cunha.') in subs
assert [m for m, t in subs if 'Manchester United' in t][0] == "22'"                       # his first change
assert ("72'", 'Substitution, Liverpool. Víctor Muñoz replaces Bradley Barcola.') in subs   # Muñoz came off the bench
BOX = {b['team']['displayName']: {s['name']: s['displayValue'] for s in b['statistics']} for b in S['boxscore']['teams']}
assert (BOX['Liverpool']['totalShots'], BOX['Liverpool']['shotsOnTarget'], BOX['Manchester United']['totalShots'], BOX['Manchester United']['shotsOnTarget']) == ('28', '11', '10', '3')
assert BOX['Manchester United']['saves'] == '7' and BOX['Manchester United']['redCards'] == '1' and BOX['Manchester United']['yellowCards'] == '0'   # Lammens' 7 saves; a straight red
assert sum(1 for s in SH if s['side'] == 'home') == 28 and sum(1 for s in SH if s['side'] == 'away') == 10
assert ''.join(r['res'] for r in RES) == 'LWDLDDDLLDL' and [r for r in RES if r['res'] == 'W'][-1]['date'] == '2026-08-30'   # one win in eleven, the last on 30 Aug
assert ''.join(r['res'] for r in RES[:10]) == 'LWDLDDDLLD'                                                                    # one win in ten when Carrick went (no game since 8 Nov)
assert ''.join(r['res'] for r in RES[2:]) == 'DLDDDLLDL' and len(RES[2:]) == 9                                              # nine league games without a win
U = [r for r in TAB if r['team'] == 'Manchester United'][0]
assert (U['rank'], U['pts'], U['w'], U['d'], U['l']) == (19, 8, 1, 5, 5) and [r for r in TAB if r['rank'] == 20][0]['pts'] == 7
assert 'Pochettino' in S['article']['headline'] and 'Iraola' in re.sub('<[^>]+>', '', S['article']['story'])                   # Liverpool's manager is Iraola here, not Slot
XG = (4.38, 0.63)

# ---- look ----
LIVC = "#d11317"
LIV = kit(LIVC, LIVC, LIVC, text="#ffffff")
MUN = kit("#f4f4f2", "#1a1a1a", "#f4f4f2", text="#1a1a1a")
ANF = stadium([LIVC, "#ffffff", LIVC, "#f2d36b"], 8)
OT = stadium(["#da291c", "#ffffff", "#111111", "#da291c"], 7)
HOME, AWAY = {"name": "LIV", "color": LIVC}, {"name": "MUN", "color": "#f4f4f2"}
RED_UI = "#ff4d5e"


def poch(**k):
    return P(outfit="suit", suitColor="#1c1f28", tie="#7a1420", skin="#e2b08c", hair="#3a3a3e", **k)


ISAK = dict(skin="#f0c8a8", hair="#3a2a1a", name="ISAK", num=9)
YORO = dict(skin="#8a5a3c", hair="#141010", name="YORO", num=15)
SZOB = dict(skin="#f0c8a8", hair="#5a3a22", name="SZOBOSZLAI", num=8, foot="right")
WIRTZ = dict(skin="#f0c8a8", hair="#6a4a2a", name="WIRTZ", num=7, foot="left")
NGUM = dict(skin="#8a5a3c", hair="#141010", name="NGUMOHA", num=73, foot="right")
MUNZ = dict(skin="#e7b593", hair="#2a1a10", name="MUÑOZ", num=23, foot="right")

V, lines = start('videos/pochettino-debut/')
B = []

# 1 hook: Pochettino walks in, the clock races to 13' (events pop as it passes them), the red card slams, the score flips to 2-0
B.append({"kicker": "Liverpool 4–0 Man United · Pochettino's debut", "headline": "Pochettino's bounce lasted [13 minutes].", "hookWords": True, "scene": ANF, "accent": RED_UI, "lights": 0.85, "flashes": 14, "focus": 0.1,
  "camFrom": {"pos": [0, 1.5, -1.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -0.4], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear",
  "players": [poch(x=-0.35, z=2.0, front=True, enter="walk", fromZ=2.7, walkDur=2.4, label="Pochettino", labelDelay=0.1)],
  "card": [bug(HOME, AWAY, [2, 0], "", [0, 0], "two goals", -0.1),
           {"type": "redcard", "at": "a red card", "lag": -0.15, "dx": 250, "y": 1190, "label": "8' Yoro"},
           {"type": "clock", "y": 1610, "shiftX": 150, "scale": 0.9, "at": "thirteen minutes", "lag": -2.7, "from": 0, "to": 13, "dur": 2.5, "phase": "ANFIELD", "endColor": RED_UI, "clear": False,
            "events": [{"min": 8, "text": "8'  RED CARD · YORO"}, {"min": 10, "text": "10'  1–0 · SZOBOSZLAI"}, {"min": 13, "text": "13'  2–0 · WIRTZ"}]}],
  "shake": [{"at": "a red card", "lag": 0.1, "amount": 16}]})

# 2 why it matters: ten days since Carrick was sacked (one win in ten), then Anfield with Pochettino walking in
B.append({"kicker": "Man United · 12 November", "headline": "Carrick sacked. [Ten days] later: Anfield.", "cut": True, "transition": "vhs", "vhsLabel": "12 NOV", "vhsDur": 0.8, "scene": OT, "accent": RED_UI, "lights": 0.55, "focus": 0.3, "fans": True,
  "camFrom": {"pos": [0, 1.6, -3.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [{"type": "crossoff", "y": 880, "delay": 0.0, "title": "Since the sacking", "days": 10, "cols": 5, "cell": 96, "crossAt": "ten days ago", "crossLag": -0.1, "dur": 2.4, "color": "#d6283b", "caption": "{n} days", "clear": False},
           stamp("1 WIN IN 10", "one league win", sub="the record when Carrick went", y=1380, size=88, lag=-0.15, clear=False)],
  "shots": [{"at": "Pochettino's first game", "lag": -0.25, "cut": True, "transition": "whip", "headline": "Pochettino's first game: [Anfield].", "kicker": "22 November · Anfield", "scene": ANF, "accent": RED_UI, "lights": 0.8, "flashes": 12,
             "camFrom": {"pos": [0, 1.5, -2.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -1.0], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
             "players": [poch(x=0, z=2.6, front=True, enter="walk", fromZ=9.5, walkDur=3.2, label="Pochettino", labelDelay=0.2)],
             "card": [{"type": "flytext", "text": "ANFIELD", "size": 230, "settle": False, "dur": 1.3, "y": 1480, "at": "Anfield", "lag": -0.5, "color": RED_UI, "clear": False}]}]})

# 3 the foul: Isak clean through, Yoro slides in from behind, freeze, the red card slams, the score bug gets its red square
FOUL = "Yoro fouls him"
pl, cards, cam = foul_from_behind(FOUL, LIV, MUN, victim=dict(ISAK), fouler=dict(YORO), victim_label="Isak", fouler_label="Yoro")
B.append({"kicker": "8' · Anfield", "headline": "Eight minutes in: [straight red].", "cut": True, "transition": "whip", "scene": ANF, "accent": RED_UI, "lights": 0.85, "flashes": 10, **cam, "players": pl,
  "card": cards + [dict(bug(HOME, AWAY, [0, 0], "8'"), hideAt="Straight red", hideLag=-0.2),
                   dict(bug(HOME, AWAY, [0, 0], "8'", red="away"), at="Straight red", lag=-0.2),
                   {"type": "flytext", "text": "FOUL", "size": 260, "endScale": 0.7, "y": 1600, "at": FOUL, "lag": 0.25, "color": RED_UI, "clear": False, "hideAt": "Straight red", "hideLag": -0.3},
                   {"type": "redcard", "at": "Straight red", "lag": -0.1, "dx": -240, "y": 1470, "label": "8' Yoro"}],
  "shake": [{"at": FOUL, "lag": 0.2, "amount": 14}], "freezeAt": "Straight red", "freezeLag": -0.25})

# 4 the free kick (a wall that jumps, the ball over it into the corner), then Wirtz from Ngumoha's pass
FK = "one–nil"
pl, cards, cam = freekick(FK, 6.0, 33.5, LIV, MUN, GK_GREEN, [-3.2, 0.4, 52.3], -1, side=1, lag=-1.15, label="Szoboszlai", **SZOB)
pl2, cards2, cam2 = goal("two–nil", 1.4, 45.2, -1, LIV, [0.5, 1.7, 52.3], -1, GK_GREEN, MUN, lag=-0.45, label="Wirtz", **WIRTZ)
pl2.append(P(kit=LIV, **dict(NGUM, foot=None), x=-3.2, z=48.2, label="Ngumoha", labelAt="set up by Ngumoha"))
B.append({"kicker": "10' · free kick", "headline": "Two minutes later: [1–0].", "cut": True, "transition": "whip", "whipDir": -1, "scene": ANF, "accent": RED_UI, "lights": 0.9, "flashes": 14, **cam, "players": pl,
  "card": cards + [bug(HOME, AWAY, [1, 0], "10'", [0, 0], FK, 0.1)],
  "shots": [{"at": "Then Wirtz", "lag": -0.3, "cut": True, "transition": "whip", "headline": "13': Wirtz makes it [2–0].", "scene": ANF, "accent": RED_UI, **cam2, "players": pl2, "flashes": 12,
             "card": cards2 + [bug(HOME, AWAY, [2, 0], "13'", [1, 0], "two–nil", 0.1)]}]})

# 5 Pochettino's first change (a scoreboard swap), and the second at half-time
B.append({"kicker": "22' · Pochettino's first change", "headline": "First change: [Mbeumo off].", "cut": True, "transition": "whip", "scene": ANF, "accent": RED_UI, "lights": 0.7, "focus": 0.3,
  "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.7], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
  "players": [poch(x=-1.5, z=3.4, front=True, pose="think", label="Pochettino", labelDelay=0.2)],
  "card": [bug(HOME, AWAY, [2, 0], "22'"),
           {"type": "subboard", "y": 1230, "shiftX": 150, "w": 600, "at": "Mbeumo off", "lag": -0.2, "out": {"num": 19, "name": "Mbeumo"}, "in": {"num": 5, "name": "Maguire"}, "swapAt": "Maguire", "hideAt": "Cunha followed", "hideLag": -0.25}],
  "shots": [{"at": "Cunha followed", "lag": -0.35, "cut": True, "transition": "whip", "headline": "Cunha off at [half-time].", "kicker": "Half-time · 2–0", "scene": ANF, "accent": RED_UI, "lights": 0.7, "focus": 0.3,
             "camFrom": {"pos": [0.6, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.2, 1.6, -1.7], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear",
             "players": [poch(x=1.5, z=3.4, front=True, pose="think", label="Pochettino", labelDelay=0.2)],
             "card": [bug(HOME, AWAY, [2, 0], "HT"),
                      {"type": "subboard", "y": 1230, "shiftX": -150, "w": 600, "delay": 0.0, "out": {"num": 10, "name": "Cunha"}, "in": {"num": 11, "name": "Zirkzee"}, "swapAt": "half-time", "swapLag": -0.1}]}]})

# 6 the second-half goals: Ngumoha (18) makes it three, substitute Muñoz makes it four
pl, cards, cam = goal("makes it three", -1.5, 40.5, -1, LIV, [0.2, 0.8, 52.3], 1, GK_GREEN, MUN, lag=-0.45, label="Ngumoha", tag=18, tagLabel="years old", tagDelay=0.3, **NGUM)
pl2, cards2, cam2 = goal("makes it four", 1.6, 41.5, 1, LIV, [3.0, 2.0, 52.3], -1, GK_GREEN, MUN, lag=-0.45, label="Muñoz · sub", **MUNZ)
B.append({"kicker": "66' · second half", "headline": "Ngumoha, 18: [3–0].", "cut": True, "transition": "whip", "scene": ANF, "accent": RED_UI, **cam, "players": pl, "flashes": 12,
  "card": cards + [bug(HOME, AWAY, [3, 0], "66'", [2, 0], "makes it three", 0.1)],
  "shots": [{"at": "Muñoz, off", "lag": -0.2, "cut": True, "transition": "whip", "whipDir": -1, "headline": "82': Muñoz off the bench, [4–0].", "scene": ANF, "accent": RED_UI, **cam2, "players": pl2, "flashes": 14,
             "card": cards2 + [bug(HOME, AWAY, [4, 0], "82'", [3, 0], "makes it four", 0.1)]}]})

# 7 the numbers: every shot on a minute track (new card), Lammens' saves, then expected goals
B.append({"kicker": "Liverpool 4–0 Man United · the numbers", "headline": "Shots: [28 to 10].", "cut": True, "transition": "whip", "scene": ANF, "accent": RED_UI, "flashes": 14, "lights": 0.75, "focus": 0.4, "punch": [{"at": "Lammens", "lag": -0.1, "amount": 0.1, "dur": 1.4}], "camFrom": {"pos": [0, 34, 8], "tgt": [0, 0, 30]}, "camera": {"pos": [0, 24, 14], "tgt": [0, 0, 30]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "shotline", "y": 1130, "w": 960, "title": "Every shot, by minute", "at": "Liverpool had", "lag": -0.1, "dur": 3.3, "total": 94, "ht": 45.5, "home": {"name": "Liverpool", "color": "#ff4d4d"}, "away": {"name": "United", "color": "#f4f4f2"},
            "shots": SH, "events": [{"min": 8, "side": "away", "kind": "red", "label": "RED CARD · YORO 8'"}], "clear": False},
           big(7, "Lammens", "saves by Lammens", y=1640, size=150, dur=0.7, lag=-0.1)],
  "shots": [{"at": "Expected goals", "lag": -0.35, "cut": True, "transition": "whip", "headline": "Expected goals: [4.38 to 0.63].", "scene": ANF, "accent": RED_UI, "flashes": 14, "lights": 0.75, "focus": 0.45, "camFrom": {"pos": [-8, 30, 10], "tgt": [0, 0, 30]}, "camera": {"pos": [8, 20, 14], "tgt": [0, 0, 30]}, "move": 5, "moveEase": "linear", "players": [],
             "punch": [{"at": "four point three eight", "amount": 0.12, "dur": 1.5}],
             "card": [{"type": "xg", "y": 1130, "title": "Expected goals", "max": 4.38, "gap": 460, "dur": 1.3, "clear": False,
                       "items": [{"label": "Liverpool", "value": XG[0], "color": LIVC, "at": "four point three eight", "lag": -0.2}, {"label": "United", "value": XG[1], "color": "#d9dde6", "at": "nought point six three", "lag": -0.2}]}]}]})

# 8 the record: United's season as a form strip (the new card), then 19th
B.append({"kicker": "Man United · Premier League 2026/27", "headline": "One win in [eleven].", "cut": True, "transition": "whip", "whipDir": -1, "scene": OT, "accent": RED_UI, "lights": 0.6, "focus": 0.3, "fans": True, "flashes": 12,
  "camFrom": {"pos": [0, 1.6, -4.2], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.6], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear", "players": [],
  "punch": [{"at": "Nine without a win", "lag": -0.2, "amount": 0.1, "dur": 1.8}, {"at": "Nineteenth", "lag": -0.1, "amount": 0.16, "dur": 1.6}], "shake": [{"at": "Nineteenth", "lag": 0.05, "amount": 14}],
  "card": [{"type": "form", "y": 980, "delay": 0.0, "title": "Man United · the league run", "results": ''.join(r['res'] for r in RES), "opps": [('MCI' if r['abbr'] == 'MNC' else r['abbr']) for r in RES],
            "winAt": "thirtieth of August", "winLag": -0.2, "winLabel": "LAST WIN · 30 AUG", "bracket": {"from": 2, "to": 10, "label": "9 WITHOUT A WIN"}, "bracketAt": "Nine without a win", "bracketLag": -0.3, "clear": False},
           stamp("19TH", "Nineteenth", sub="a point above bottom club Palace", y=1560, size=128, lag=-0.1)]})

# 9 the question: the foul again from a drone, rewinding on VHS, with a poll
pl, cards, cam = foul_from_behind("red card", LIV, MUN, victim=dict(ISAK), fouler=dict(YORO), victim_label="Isak", fouler_label="Yoro")
cam = {"camFrom": {"pos": [13.0, 9.0, 19.0], "tgt": [0.6, 0.5, 30.0]}, "camera": {"pos": [-5.0, 4.6, 28.0], "tgt": [1.0, 0.8, 37.5]}, "move": 4.4, "moveEase": "linear", "hype": False}
B.append({"kicker": "Your call", "headline": "Was it a [red card]?", "cut": True, "transition": "vhs", "vhsLabel": "AGAIN", "vhsDur": 0.9, "letterbox": True, "replayTag": "REPLAY", "scene": ANF, "accent": RED_UI, "lights": 0.9, **cam, "players": pl,
  "card": cards + [bug(HOME, AWAY, [0, 0], "8'"),
                   {"type": "poll", "y": 1600, "at": "how long", "lag": -0.5, "question": "Was it a red card?", "clear": False,
                    "options": [{"label": "Yes, red", "color": "#d6283b", "fill": 0.5}, {"label": "No, harsh", "color": "#9aa1ad", "fill": 0.5}]}]})

save(V, B, lines, "Liverpool 4–0 Man United: Pochettino's debut", accent=TEAL)
