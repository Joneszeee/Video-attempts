#!/usr/bin/env python3
"""Pulls everything the video uses from ESPN's public JSON (run from the repo root; the video's gen.py asserts on these files).
  data/espn_summary.json   the match feed (key events, play-by-play, box score, rosters, recap article)
  data/shots.json          every shot with its minute, from the play-by-play (Liverpool 28, United 10: matches ESPN's own totals)
  data/united_results.json United's league results this season, in date order
  data/table.json          the league table after the game
Liverpool v Man United, 22 Nov 2026, event 401878755."""
import json
import re
import subprocess
from pathlib import Path

OUT = Path('videos/pochettino-debut/data')
EVENT = '401878755'


def get(u):
    return json.loads(subprocess.run(['curl', '-s', u], capture_output=True, text=True).stdout)


summary = get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/summary?event={EVENT}')
(OUT / 'espn_summary.json').write_text(json.dumps(summary))

shots, seen = [], set()
for x in summary['commentary']:
    txt = x['text']
    if not re.match(r'^(Attempt (saved|missed|blocked)|Goal!)', txt):
        continue
    key = (x['time']['value'], txt)
    if key in seen:
        continue
    seen.add(key)
    team = re.search(r'\(([^)]+)\)', txt).group(1)
    who = re.search(r'(?:Goal![^.]*\.\s*)?([^.(]+?) \(' + re.escape(team) + r'\)', txt)
    kind = 'goal' if txt.startswith('Goal!') else 'saved' if txt.startswith('Attempt saved') else 'missed' if txt.startswith('Attempt missed') else 'blocked'
    m = re.match(r"(\d+)'(?:\+(\d+)')?", x['time']['displayValue'])
    minute = int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0)
    shots.append({'min': minute, 'side': 'home' if team == 'Liverpool' else 'away', 'kind': kind, 'who': who.group(1).strip().split()[-1] if who else '?', 'team': team})
(OUT / 'shots.json').write_text(json.dumps(shots, indent=1, ensure_ascii=False))

rows = []
sched = get('https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/teams/360/schedule?season=2026')
for e in sched.get('events', []):
    c = e['competitions'][0]
    if c['status']['type']['name'] != 'STATUS_FULL_TIME':
        continue
    me = [t for t in c['competitors'] if t['team']['id'] == '360'][0]
    op = [t for t in c['competitors'] if t['team']['id'] != '360'][0]
    sc = lambda t: int(float((t.get('score') or {}).get('value', 0) if isinstance(t.get('score'), dict) else t.get('score', 0)))
    a, b = sc(me), sc(op)
    rows.append({'date': e['date'][:10], 'opp': op['team']['displayName'], 'abbr': op['team']['abbreviation'], 'venue': me['homeAway'], 'score': f'{a}-{b}', 'res': 'W' if a > b else 'D' if a == b else 'L'})
rows.sort(key=lambda r: r['date'])
(OUT / 'united_results.json').write_text(json.dumps(rows, indent=1))

st = get('https://site.api.espn.com/apis/v2/sports/soccer/eng.1/standings')
tab = []
for e in st['children'][0]['standings']['entries']:
    g = lambda k: next((s.get('displayValue') for s in e['stats'] if s['name'] == k), None)
    tab.append({'rank': int(g('rank')), 'team': e['team']['displayName'], 'p': int(g('gamesPlayed')), 'w': int(g('wins')), 'd': int(g('ties')), 'l': int(g('losses')), 'pts': int(g('points')), 'gd': g('pointDifferential')})
tab.sort(key=lambda r: r['rank'])
(OUT / 'table.json').write_text(json.dumps(tab, indent=1))
print('ok:', len(shots), 'shots,', len(rows), 'United results,', len(tab), 'table rows')
