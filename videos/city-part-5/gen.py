# Builds videos/city-part-5/spec.json (run from the repo root). Man City in League Two, Part 5: League One 2028/29 (season 3), matchdays 24-46, Ward-Prowse (poll) and Moylan (comment loan) join.
# Every score, position, table and odds figure comes from videos/city-league-two/data/ep4.json + ep5.json (seeds 2029 and 2031, fixed before running); the signings' ratings and simulated stats come
# from squad5.json (seed 2032, fixed before running). The poll and the comment are the user's screenshots (25 Nov 2026); the five real players' numbers are ESPN's (p5_real.json, same day).
# The sim gives scores only: no scorer is named except through Haaland's count.
import json
import sys
sys.path.insert(0, 'engine')
from lib import *

D = 'videos/city-league-two/data/'
E4 = json.load(open(D + 'ep4.json')); E5 = json.load(open(D + 'ep5.json')); Q = json.load(open(D + 'squad5.json')); RW = json.load(open(D + 'p5_real.json'))['players']
L4 = {g['md']: g for g in E4['log']}; L5 = {g['md']: g for g in E5['log']}
CREDIT = "Caiolfan_private"      # the commenter's public handle, shown as a credit (set to None to hide it)
# --- every number the voice says, checked against the data (a wrong number stops the build)
POLL = [("Ward-Prowse", 47), ("Norwood", 30), ("Phillips", 23)]; assert sum(p for _, p in POLL) == 100 and POLL[0][1] == max(p for _, p in POLL); VOTES = 785
LIKES, NEEDED = 19, 30
assert E5['seeds'] == [2029, 2031] and E5['sign'] == 'Ward-Prowse' and E5['loan']['name'] == 'Moylan' and E5['champions'] and E5['promoted'] and E5['playoffs'] is None
t23 = {r[1]: r for r in E4['table_md23']}; assert t23['Manchester City'][0] == 4 and t23['Manchester City'][2] == 38                      # "fourth at halfway"
fin = {r[1]: r for r in E5['table_final']}; city = fin['Manchester City']
assert (city[0], city[2], city[3], city[4]) == (1, 82, 97, 51) and city[3] == max(r[3] for r in E5['table_final']) and city[4] == min(r[4] for r in E5['table_final'])
assert E5['haaland'] == 35 and E4['haaland'] == 13 and L5[46]['hg_total'] == 35
tt = lambda k: round(100 * E5[k]['title'])
assert (tt('odds_without'), tt('odds_with_sign'), tt('odds_with_both')) == (57, 67, 74) and tt('odds_with_both') - tt('odds_without') == 17
R = Q['ratings']; ST = Q['stats_second_half']
assert R['Ward-Prowse']['ovr'] == 69 and R['Moylan']['ovr'] == 72 and R['Moylan']['ovr'] > R['Ward-Prowse']['ovr'] and Q['seed'] == 2032
assert ST['Ward-Prowse'] == dict(apps=23, goals=4, assists=2, cs=0, conceded=0) and ST['Moylan'] == dict(apps=23, goals=1, assists=6, cs=0, conceded=0)
assert (L5[24]['opp'], L5[24]['venue'], L5[24]['score'], L5[24]['pos']) == ('Stevenage', 'A', '1-2', 5)                                     # debut day
assert [(L5[m]['opp'], L5[m]['score']) for m in (25, 26, 27)] == [('Burnley', '5-1'), ('Wycombe Wanderers', '4-3'), ('Burton Albion', '2-0')] and L5[27]['pos'] == 1
assert min(g['pos'] for g in E4['log']) == 3 and all(L5[m]['pos'] != 1 for m in range(24, 27))                                              # top for the first time this season on matchday 27
assert (L5[34]['opp'], L5[34]['venue'], L5[34]['score'], L5[34]['haaland']) == ('Salford City', 'H', '6-0', False) and max(int(g['score'][0]) - int(g['score'][2]) for g in E5['log']) == 6
assert (L5[37]['opp'], L5[37]['score']) == ('Chesterfield', '3-4') and (L5[41]['opp'], L5[41]['score']) == ('Plymouth Argyle', '1-3')
def top2(md):
    s = E5['snaps'][str(md)]; c = next(r for r in s if r[1] == 'Manchester City'); o = max((r for r in s if r[1] != 'Manchester City'), key=lambda r: (r[2], r[3])); return c, o
assert top2(42)[0][2] == top2(42)[1][2] == 74 and top2(42)[1][1] == 'Stockport County' and top2(41)[0][2] == top2(41)[1][2] == 73 and top2(41)[1][1] == 'Stockport County'     # level on points with Stockport
assert (L5[45]['opp'], L5[45]['venue'], L5[45]['score'], L5[45]['haaland'], L5[45]['hgoals'], L5[45]['pts']) == ('Cambridge United', 'H', '3-0', True, 2, 81)
assert top2(45)[0][2] - top2(45)[1][2] == 4 and 4 > 3 and top2(44)[0][2] - top2(44)[1][2] == 4 and 4 < 6                                      # champions on matchday 45 with one game to spare
assert (RW['Jack Moylan']['starts'], RW['Jack Moylan']['goals'], RW['Jack Moylan']['assists']) == (16, 10, 3) and RW['Jack Moylan']['club'] == 'Cardiff City'
assert (RW['Jarrod Bowen']['starts'], RW['Jarrod Bowen']['goals'], RW['Jarrod Bowen']['assists']) == (16, 7, 7) and RW['Jarrod Bowen']['club'] == 'West Ham United'
assert (RW['Amario Cozier-Duberry']['starts'], RW['Amario Cozier-Duberry']['goals'], RW['Amario Cozier-Duberry']['assists']) == (11, 3, 6) and RW['Amario Cozier-Duberry']['club'] == 'Middlesbrough'
assert (RW['Ollie Tanner']['starts'], RW['Ollie Tanner']['goals'], RW['Ollie Tanner']['assists']) == (16, 3, 4) and RW['Ollie Tanner']['club'] == 'Cardiff City'
assert Q['upgrade_to_championship']['McAidoo'] == max(Q['upgrade_to_championship'].values())                                                  # right wing is the weakest slot

CITY = kit(SKY, "#ffffff", SKY, text="#1c2c5b")
STE = kit("#d6283b", "#ffffff", "#d6283b", text="#ffffff")
CAR = kit("#0a4ea1", "#ffffff", "#0a4ea1", text="#ffffff")
WHU = kit("#7a263a", "#ffffff", "#7a263a", text="#1bb1e7")
MID = kit("#e2231a", "#ffffff", "#e2231a", text="#ffffff")
CAM = kit("#f6a800", "#111111", "#f6a800", text="#111111")
SOU = kit("#d71920", "#ffffff", "#d71920", text="#ffffff", stripes=["#d71920", "#ffffff"])
SAL = kit("#d6283b", "#ffffff", "#d6283b", text="#ffffff")
HAAL = dict(skin="#f1d3bd", hair="#d9b46a", name="HAALAND", num=9, foot="left")
LOOK = {'Ward-Prowse': dict(skin="#f0c8a8", hair="#4a3324"), 'Moylan': dict(skin="#e7b593", hair="#3a2a1a")}
MCI = {"name": "MCI", "color": SKY}
BADGE = {"colors": [SKY, "#1c2c5b", "#ffffff"], "text": "MCI"}
S_ETI = stadium([SKY, "#ffffff", SKY, "#1c2c5b"], 6)
S_NIGHT = stadium(["#ffffff", "#1c2c5b", SKY], 9)
S_GOLD = stadium(["#f1c453", "#ffffff", "#1c2c5b", SKY], 12)
S_SIM = stadium(["#2a2f3a", "#3a4356", "#1c2029", "#2c5a66"], 21)
S_STE = stadium(["#d6283b", "#ffffff", "#d6283b"], 29)
S_CAR = stadium(["#0a4ea1", "#ffffff", "#0a4ea1", "#d6283b"], 33)
COLORS = {"Manchester City": SKY, "MK Dons": "#ffffff", "Luton Town": "#f78f1e", "Grimsby Town": "#cfd3da", "Leicester City": "#003090", "Stockport County": "#1b4fb5", "Reading": "#1f4fa0",
          "Stevenage": "#d6283b", "Mansfield Town": "#f2c500", "Burnley": "#6c1d45", "Wycombe Wanderers": "#2a5caa", "Preston North End": "#cfd3da"}
ZONES = [{"from": 1, "to": 2, "color": GREEN}, {"from": 3, "to": 6, "color": TEAL}]

def snap(md): return E4['snaps'][str(md)] if md <= 23 else E5['snaps'][str(md)]
def rows(md, n=6): return [[r[0], r[1], r[2]] for r in snap(md)[:n]]
def res(md): g = L5[md]; return f"MD{md} · {g['res']} {g['score'].replace('-', '–')} {g['opp'].replace(' Wanderers', '').replace(' Albion', '').replace(' City', '').replace(' United', '')}"

V, lines = start('videos/city-part-5/')
B = []

# 1 hook: the number clash (4th -> champions). Frame 0: Haaland and two team-mates in City's kit, the halfway table already on screen with City 4th, every headline word readable, speed lines, push-in.
# "fourth" pulses; on "champions" City's row slides 4th -> 1st (points tick 38 -> 82), a CHAMPIONS stamp slams, confetti, the players celebrate.
mates = [P(kit=CITY, skin="#8a5a3c", hair="#141010", x=-1.9, z=0.6, front=True, action="celebrate", actionAt="champions", actionLag=-0.1),
         P(kit=CITY, skin="#f0c8a8", hair="#3a2a1a", x=1.9, z=0.6, front=True, action="celebrate", actionAt="champions", actionLag=0.05),
         P(kit=CITY, x=0.0, z=-0.3, front=True, action="celebrate", actionAt="champions", actionLag=-0.2, label="Haaland", labelDelay=-0.4, **{k: v for k, v in HAAL.items() if k not in ('name', 'num')})]
B.append({"kicker": "Man City in League Two · Part 5", "headline": "City were [fourth]. Now [champions].", "hookWords": True, "scene": S_ETI, "accent": TEAL, "lights": 0.9, "flashes": 12, "hype": False,
  "camFrom": {"pos": [0, 1.5, -9.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.5, -6.2], "tgt": [0, 1.3, 10]}, "move": 3.4, "moveEase": "linear", "players": mates,
  "card": [{"type": "climb", "y": 1380, "delay": -1.0, "show": 6, "stepDur": 0.9, "title": "League One · matchday 23 → 46", "focus": "Manchester City", "zones": ZONES, "colors": COLORS, "clear": False,
            "steps": [{"rows": rows(23)}, {"at": "champions", "lag": -0.35, "rows": rows(46), "label": "FINAL TABLE · 82 PTS"}]},
           stamp("CHAMPIONS", "champions", sub="promoted · 82 points", color=GOLD, y=1700, size=104, lag=0.1), hud("Season 3 · League One", counter=False)],
  "confetti": True, "confettiAt": "champions", "speedlines": [{"t": 0.0, "dur": 0.9, "amount": 0.7}], "shake": [{"at": "champions", "lag": 0.0, "amount": 14}]})

# 2 the vote: the shirt flips Southampton -> City on his name; the poll bars fill (47 / 30 / 23, 785 votes)
GOLDBAR = "#e9b949"
B.append({"kicker": f"Your vote · the TikTok poll · {VOTES} votes", "headline": "You voted: [Ward-Prowse].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [26, 30, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [-24, 16, -24], "tgt": [0, 0, 6]}, "move": 5, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · January window", counter=False),
           {"type": "shirtflip", "y": 860, "delay": 0.0, "size": 400, "from": {"color": "#d71920", "color2": "#ffffff", "name": "SOUTHAMPTON"}, "to": {"color": SKY, "color2": "#1c2c5b", "name": "WARD-PROWSE"},
            "flipAt": "Ward-Prowse", "flipLag": -0.35, "clear": False},
           {"type": "poll", "y": 1560, "delay": 0.0, "question": "Who should City sign?", "clear": False,
            "options": [{"label": "Ward-Prowse", "color": GOLDBAR, "fill": 0.47, "pct": "47%"}, {"label": "Norwood", "color": "#1b4fb5", "fill": 0.30, "pct": "30%"}, {"label": "Phillips", "color": "#9a1c24", "fill": 0.23, "pct": "23%"}]}]})

# 3 the comment: Moylan's real numbers (ESPN) in a drawn card, and the fan's comment with the like counter stopping at 19 of 30, then 6-MONTH LOAN
M = RW['Jack Moylan']
B.append({"kicker": "The comment vote · 30 likes needed", "headline": "A comment signed [Moylan]. On loan.", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_CAR, "accent": TEAL, "lights": 0.7, "focus": 0.35, "flashes": 8,
  "camFrom": {"pos": [0, 1.6, -3.4], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0.8, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · January window", counter=False),
           {"type": "pcard", "y": 800, "w": 300, "h": 420, "shiftX": 0, "side": "left", "at": "Jack Moylan", "lag": -0.15, "player": dict(kit=CAR, name="", num=None, **LOOK['Moylan']),
            "tag": "CARDIFF CITY", "caption": "Jack Moylan", "stats": [[M['goals'], "goals"], [M['assists'], "assists"]], "statsNote": f"{M['starts']} starts · Championship · real stats", "clear": False},
           {"type": "pledge", "y": 1430, "delay": 0.0, "handle": CREDIT, "text": "Make them sign jack moylan from cardiff", "likes": LIKES, "goal": NEEDED, "title": "likes on the comment", "dur": 1.0,
            "likeAt": "It got nineteen", "likeLag": -0.25, "shortAt": "So:", "shortLag": -0.1, "result": "6-MONTH LOAN", "resultAt": "a six-month loan", "resultLag": -0.35, "clear": False}]})

# 4 the two new cards (simulated rating and stats since joining); the loan out-rates the poll winner
def card(nm, pos, dx, entry, ribbon, ribbonColor=None, **k):
    s = ST[nm]
    d = {"type": "scard", "y": 1110, "name": nm, "pos": pos, "ovr": R[nm]['ovr'], "rarity": "silver", "player": dict(kit=CITY, name="", num=None, **LOOK[nm]), "badge": BADGE,
         "rows": [{"label": "Since joining", "cells": [[s['apps'], 'gp'], [s['goals'], 'g'], [s['assists'], 'a']]}], "foot": "sim rating · sim stats", "entry": entry, "dx": dx, "scale": 0.8,
         "seed": 17 if nm == 'Moylan' else 5, "ribbon": ribbon, "clear": False}
    if ribbonColor: d["ribbonColor"] = ribbonColor
    d.update(k)
    return d
B.append({"kicker": "The new signings · simulated", "headline": "Two new faces: [69] and [72].", "cut": True, "transition": "whip", "scene": S_NIGHT, "accent": TEAL, "lights": 0.7, "focus": 0.35, "flashes": 8,
  "camFrom": {"pos": [1.2, 1.6, -3.6], "tgt": [0, 1.3, 10]}, "camera": {"pos": [-0.8, 1.6, -2.0], "tgt": [0, 1.3, 10]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · simulated", counter=False),
           card("Ward-Prowse", "DM", -235, "left", "Fan pick", at="Ward-Prowse", lag=-0.1, tilt=-0.05),
           card("Moylan", "LW", 235, "right", "Loan", ribbonColor=GOLD, at="Moylan,", lag=-0.1, tilt=0.05),
           stamp("72 v 69", "The loan beats", sub="Moylan v Ward-Prowse · sim rating", color=GOLD, y=1545, size=96, lag=0.0)]})

# 5 the odds: 74 of 100 squares light; on "add seventeen" the last 17 turn gold: what the two signings add (57 -> 74)
B.append({"kicker": "10,000 seasons simulated · halfway", "headline": "City: [74%] to win the league.", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.3,
  "camFrom": {"pos": [-26, 22, -38], "tgt": [0, 0, 6]}, "camera": {"pos": [24, 14, -22], "tgt": [0, 0, 6]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · 10,000 runs", dur=1.6),
           {"type": "odds", "y": 1030, "cell": 60, "title": "City · title chance at halfway", "lit": tt('odds_with_both'), "litStep": 0.016, "litAt": "seventy-four percent", "litLag": -0.35, "label": "{n}%", "clear": False,
            "extra": {"n": 17, "color": GOLD, "at": "Your signings add seventeen", "lag": 0.0, "label": "your signings: +17"}}]})

# 6 match 1 (debut day, away): Stevenage win 2-1; their winner beats the keeper; City fall to 5th
pl, cards, cam = goal("two–one", -1.0, 41, -1, STE, [2.6, 1.0, 52.3], -1, GK_YELLOW, CITY, lag=-0.5, skin="#e7b593", hair="#141010")
pl[1].update(skin="#f0c8a8", hair="#3a2a1a")
B.append({"kicker": "Matchday 24 · away", "headline": "Debut day: [1–2] at Stevenage.", "cut": True, "transition": "vhs", "vhsLabel": "MD24", "vhsDur": 0.8, "scene": S_STE, "accent": RED, **cam, "players": pl,
  "card": cards + [bug({"name": "STE", "color": "#d6283b"}, MCI, [2, 1], "MD24", [1, 1], "two–one", 0.25), hud("League One · matchday 24", counter=False),
                   stamp("1–2", "two–one", sub=f"debut day · {L5[24]['pos']}th", y=1530, size=110, lag=0.05)],
  "shake": [{"at": "two–one", "lag": 0.4, "amount": 12}]})

# 7 three wins (5-1, 4-3, 2-0): the climb card moves City 5th -> 5th -> 2nd -> 1st, one step per match on its word; "go top" stamps it
B.append({"kicker": "Matchdays 25–27", "headline": "Three wins. City go [top].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_NIGHT, "accent": GOLD, "lights": 0.85, "flashes": 10,
  "camFrom": {"pos": [4.5, 1.2, -6.5], "tgt": [0, 1.3, 10]}, "camera": {"pos": [-3.5, 1.5, -6.5], "tgt": [0, 1.3, 10]}, "move": 6.5, "moveEase": "linear", "hype": False,
  "players": [P(kit=CITY, skin="#8a5a3c", hair="#141010", x=-1.6, z=1.0, front=True, action="celebrate", actionAt="go top", actionLag=-0.1),
              P(kit=CITY, skin="#f0c8a8", hair="#3a2a1a", x=1.6, z=1.2, front=True, action="celebrate", actionAt="go top", actionLag=0.05)],
  "card": [{"type": "climb", "y": 1330, "delay": 0.0, "show": 6, "stepDur": 0.8, "title": "League One · after matchday 24", "focus": "Manchester City", "zones": ZONES, "colors": COLORS, "clear": False,
            "steps": [{"rows": rows(24)}, {"at": "Burnley", "lag": -0.1, "rows": rows(25), "label": res(25)}, {"at": "Wycombe", "lag": -0.1, "rows": rows(26), "label": res(26)},
                      {"at": "Burton", "lag": -0.1, "rows": rows(27), "label": res(27)}]},
           stamp("TOP", "City go top", sub="first time this season", color=GOLD, y=1700, size=120, lag=0.0), hud("League One · matchdays 24–27", counter=False)]})

# 8 match 4: Salford at home, 6-0, and Haaland is out (the sim's own availability): a six-ball barrage from behind the net
END = [[-2.6, 1.0, 52.3], [2.4, 1.6, 52.3], [-0.6, 0.5, 52.3], [2.9, 0.7, 52.3], [-3.0, 1.9, 52.3], [0.8, 1.2, 52.3]]
barrage = [{"type": "ballpath", "world": True, "delay": round(0.1 + i * 0.28, 2), "dur": 0.4, "slowmo": False, "points": [[x * -0.4, 0.11, 38], [x * 0.2, 1.4, 46], [x, y, z]]} for i, (x, y, z) in enumerate(END)]
B.append({"kicker": "Matchday 34 · at home", "headline": "Salford: [6–0]. No Haaland.", "cut": True, "transition": "whip", "scene": S_ETI, "accent": TEAL, "lights": 0.85, "hype": False,
  "camFrom": {"pos": [1.5, 2.3, 60.5], "tgt": [0, 1.0, 40]}, "camera": {"pos": [0.8, 2.1, 59.2], "tgt": [0, 1.0, 40]}, "move": 3.4, "moveEase": "linear",
  "players": [P(kit=SAL, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, pose="keeper")],
  "card": barrage + [bug(MCI, {"name": "SAL", "color": "#d6283b"}, [6, 0], "MD34", [0, 0], "Six–nil", 0.1), hud("League One · matchday 34", counter=False),
                     stamp("NO HAALAND", "didn't even play", sub="out · 6–0 anyway", color=RED, y=1330, size=78, lag=0.0),
                     big(6, "Six–nil", "goals v Salford", frm=0, y=1580, size=170, dur=1.4, lag=-0.3)]})

# 9 re-hook: it got tight. The title race (City v the best of the rest, matchdays 1-42): the two defeats pin on City's line on their words, the lines meet at 74 and LEVEL slams
def pts_series(upto):
    c, r = [], []
    for md in range(1, upto + 1):
        s = snap(md); cc = next(x for x in s if x[1] == 'Manchester City'); oo = max((x for x in s if x[1] != 'Manchester City'), key=lambda x: (x[2], x[3])); c.append(cc[2]); r.append(oo[2])
    return c, r
cp, rp = pts_series(42); assert cp[36] == 66 and rp[36] == 67 and cp[40] == rp[40] == 73 and cp[41] == rp[41] == 74
B.append({"kicker": "The title race · City v the best of the rest", "headline": "Then it got [tight].", "cut": True, "transition": "vhs", "vhsLabel": "TIGHT", "vhsDur": 1.0, "scene": S_SIM, "accent": RED,
  "lights": 0.45, "focus": 0.35, "camFrom": {"pos": [-24, 26, -40], "tgt": [0, 0, 6]}, "camera": {"pos": [22, 14, -22], "tgt": [0, 0, 6]}, "move": 7, "moveEase": "linear", "players": [],
  "card": [hud("League One · after matchday 42", counter=False),
           {"type": "pace", "y": 1060, "delay": 0.0, "startT": 0.3, "dur": 3.0, "linear": True, "title": "points after each matchday", "names": {"expected": "best of the rest", "actual": "Man City"},
            "expected": rp, "actual": cp, "top": 80, "clear": False,
            "pins": [{"i": 36, "at": "Chesterfield win", "lag": -0.1, "label": "CHE 3–4", "color": RED, "dy": -52}, {"i": 40, "at": "Plymouth win", "lag": -0.1, "label": "PLY 1–3", "color": RED, "dy": -52}]},
           stamp("LEVEL", "Level on points", sub="74 – 74 · Stockport · four to play", color=GOLD, y=1580, size=120, lag=-0.1)]})

# 10 match 5: Cambridge at home, 3-0: Haaland scores twice (his "2" tag pops on "twice"), then the title: trophy, confetti, a CHAMPIONS stamp on matchday 45
pl, cards, cam = goal("scores twice", -1.2, 41, -1, CITY, [2.8, 1.0, 52.3], -1, GK_GREEN, CAM, lag=-0.3, label="Haaland", **HAAL)
pl[0].update(tag=2, tagLabel="goals", tagAt="twice", tagLag=-0.1)
B.append({"kicker": "Matchday 45 · at home", "headline": "Cambridge: Haaland [twice].", "cut": True, "transition": "whip", "scene": S_ETI, "accent": GOLD, **cam, "players": pl, "flashes": 12,
  "card": cards + [bug(MCI, {"name": "CAM", "color": "#f6a800"}, [2, 0], "MD45", [1, 0], "scores twice", 0.5), hud("League One · matchday 45", counter=False)],
  "shots": [{"at": "Three–nil", "lag": -0.15, "cut": True, "transition": "whip", "kicker": "Matchday 45 · full time", "headline": "One game to spare: [champions].", "scene": S_GOLD, "accent": GOLD, "lights": 0.9,
     "camFrom": {"pos": [0, 1.4, -7.5], "tgt": [0, 1.4, 10]}, "camera": {"pos": [0, 1.5, -5.2], "tgt": [0, 1.4, 10]}, "move": 4, "moveEase": "linear", "hype": False, "flashes": 16,
     "confetti": True, "confettiAt": "champions",
     "players": [P(kit=CITY, skin="#8a5a3c", hair="#141010", x=-1.8, z=0.4, front=True, action="celebrate", actionDelay=0.4), P(kit=CITY, skin="#f0c8a8", hair="#3a2a1a", x=1.8, z=0.5, front=True, action="celebrate", actionDelay=0.7),
                 P(kit=CITY, x=0.0, z=-0.2, front=True, pose="fists", **{k: v for k, v in HAAL.items() if k not in ('name', 'num')})],
     "card": [bug(MCI, {"name": "CAM", "color": "#f6a800"}, [3, 0], "FT", [2, 0], "Three–nil", 0.1), hud("League One · matchday 45", counter=False),
              {"type": "trophies", "at": "champions", "lag": -0.35, "floor": 1500, "stagger": 0, "rise": 0.55, "items": [{"kind": "cup", "sx": 0.5, "h": 150, "size": 200, "label": "League One · champions"}], "clear": False}]}]})

# 11 the season in numbers: Haaland close-up and the stacked counter (82 points, 97 goals the most, 51 against the fewest, Haaland 35)
B.append({"kicker": "The season in numbers", "headline": "Champions: [82 points].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_NIGHT, "accent": GOLD, "lights": 0.8, "flashes": 10,
  "camFrom": {"pos": [0, 1.45, -4.6], "tgt": [0, 1.35, 10]}, "camera": {"pos": [0, 1.45, -3.4], "tgt": [0, 1.35, 10]}, "move": 5.5, "moveEase": "linear",
  "players": [P(kit=CITY, x=-0.55, z=0, front=True, chest=True, **HAAL)],
  "card": [hud("League One · the final table", counter=False),
           {"type": "stack", "y": 1480, "dx": 250, "size": 130, "clear": False, "items": [
              {"value": 82, "label": "points", "at": "Eighty-two points", "lag": -0.1},
              {"value": 97, "label": "goals · the most", "at": "Ninety-seven goals", "lag": -0.1},
              {"value": 51, "label": "against · the fewest", "at": "Fifty-one against", "lag": -0.1},
              {"value": 35, "label": "Haaland · league goals", "at": "thirty-five", "lag": -0.25, "gold": True}]}]})

# 12 promoted, and the next vote: the weak spot (right wing) is an empty slot on the team sheet; three real Championship right-sided attackers and a poll
RC = {"bronze": ("#d8a070", "#2b1a0e"), "silver": ("#e4e8ee", "#1c2430"), "gold": ("#f1c453", "#3a2a06"), "elite": ("#22305f", "#f1c453")}
rar = lambda ovr: 'elite' if ovr >= 85 else 'gold' if ovr >= 75 else 'silver' if ovr >= 65 else 'bronze'
XY = {'Haaland': (0.5, 0.12), 'Foden': (0.5, 0.32), 'Moylan': (0.18, 0.3), 'Iroegbunam': (0.35, 0.5), 'Ward-Prowse': (0.65, 0.5), 'Lewis': (0.86, 0.66), "O'Reilly": (0.14, 0.66),
      'Watts': (0.36, 0.72), 'Scarr': (0.64, 0.72), 'McCracken': (0.5, 0.9)}
items = []
for nm, (x, y) in XY.items():
    col, ink = RC[rar(R[nm]['ovr'])]
    items.append({"name": nm, "x": x, "y": y, "color": col, "ink": ink, "ovr": R[nm]['ovr']})
def cand(name, tag, kt, sx, word, lag, stats, skin, hair):
    return {"type": "pcard", "y": 1000, "w": 290, "h": 400, "shiftX": sx, "side": "left" if sx < 0 else "right", "at": word, "lag": lag,
            "player": dict(kit=kt, skin=skin, hair=hair, name=""), "tag": tag, "caption": name, "stats": stats, "statsNote": "Championship · real stats", "clear": False}
bw, cd, tn = RW['Jarrod Bowen'], RW['Amario Cozier-Duberry'], RW['Ollie Tanner']
B.append({"kicker": "Next season · the Championship", "headline": "Going up. The weak spot: [right wing].", "cut": True, "transition": "whip", "scene": S_SIM, "accent": TEAL, "lights": 0.5, "focus": 0.35,
  "camFrom": {"pos": [-30, 26, -40], "tgt": [0, 0, 5]}, "camera": {"pos": [24, 20, -34], "tgt": [0, 0, 5]}, "move": 6, "moveEase": "linear", "players": [],
  "card": [{"type": "lineup", "y": 1120, "delay": 0.0, "w": 640, "title": "City · the XI · sim ratings", "clear": False, "instant": True, "items": items,
            "empty": {"x": 0.82, "y": 0.3, "label": "RIGHT WING", "at": "right wing", "lag": -0.15}},
           stamp("PROMOTED", "going up", sub="to the Championship", color=GREEN, y=1690, size=96, lag=-0.1), hud("Season 3 · the Championship next", counter=False)],
  "shots": [{"at": "Who should City", "lag": 0.32, "cut": True, "transition": "whip", "kicker": "Your vote · the right wing", "headline": "Who should City [sign]?", "scene": S_ETI, "accent": TEAL,
     "lights": 0.6, "focus": 0.3, "camFrom": {"pos": [0, 1.6, -3.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -1.8], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [], "hype": False,
     "card": [cand("Jarrod Bowen", "WEST HAM", WHU, -335, "Who should City", -0.1, [[bw['starts'], "starts"], [f"{bw['goals']:.0f}+{bw['assists']:.0f}", "G + A"]], "#f0c8a8", "#4a3324"),
              cand("Cozier-Duberry", "MIDDLESBROUGH", MID, 0, "Who should City", 0.2, [[cd['starts'], "starts"], [f"{cd['goals']:.0f}+{cd['assists']:.0f}", "G + A"]], "#8a5a3c", "#141010"),
              cand("Ollie Tanner", "CARDIFF", CAR, 335, "Who should City", 0.5, [[tn['starts'], "starts"], [f"{tn['goals']:.0f}+{tn['assists']:.0f}", "G + A"]], "#f0c8a8", "#6a4a2a"),
              {"type": "poll", "y": 1640, "at": "Who should City", "lag": 0.4, "question": "Who should City sign?", "clear": False,
               "options": [{"label": "Bowen", "color": "#7a263a", "fill": 0.34}, {"label": "Cozier-Duberry", "color": "#e2231a", "fill": 0.33}, {"label": "Tanner", "color": "#0a4ea1", "fill": 0.33}]}]}]})

# 13 the cliffhanger: Moylan's six-month loan is nearly up (a six-month calendar crosses off), "keep him?"
B.append({"kicker": "The loan", "headline": "Moylan's loan is [nearly up].", "cut": True, "transition": "whip", "whipDir": -1, "scene": S_CAR, "accent": GOLD, "lights": 0.7, "focus": 0.3, "flashes": 10,
  "camFrom": {"pos": [0, 1.6, -4.0], "tgt": [0, 1.3, 10]}, "camera": {"pos": [0, 1.6, -2.2], "tgt": [0, 1.3, 10]}, "move": 4, "moveEase": "linear", "players": [],
  "card": [hud("Season 3 · simulated", counter=False),
           card("Moylan", "LW", -250, "zoom", "Loan", ribbonColor=GOLD, at="Moylan's", lag=-0.1, tilt=-0.04, snap=True),
           {"type": "crossoff", "y": 1050, "dx": 245, "delay": 0.2, "title": "THE LOAN", "days": 6, "cols": 3, "cell": 104, "crossAt": "nearly up", "crossLag": -0.2, "dur": 1.5, "caption": "{n} of 6 months", "clear": False},
           stamp("KEEP HIM?", "Keep him", sub="comment yes or no", color=GOLD, y=1560, size=120, lag=-0.1)]})

save(V, B, lines, "Man City in League Two · Part 5", accent=TEAL)
