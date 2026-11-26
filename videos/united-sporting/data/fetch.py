"""Sporting CP 2-2 Manchester United (UEFA Champions League league phase, matchday 5, Wed 25 Nov 2026, Estadio Jose Alvalade): pulls everything the video uses from ESPN's public JSON
into data/*.json (run from this folder); gen.py asserts every minute, score and stat against these files.
  summary.json         the match feed (key events, play-by-play, box score, rosters, recap article, standings)
  shots.json           every shot with its minute, from the play-by-play (penalties included)
  united_results.json  United's results this season in all competitions, in date order (league, Champions League, cups)
  table.json           the Champions League league-phase table after matchday 5
  results_md5.json     the 18 matchday-5 results (24-25 Nov), for the table before the matchday
Event 401915373 in uefa.champions (Sporting CP id 2250, Manchester United id 360)."""
import json, re, urllib.request
B = 'https://site.api.espn.com/apis/site/v2/sports/soccer'
EV = '401915373'
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(r, timeout=40))
        except Exception as e: err = e
    raise SystemExit('fetch failed: ' + str(err))
s = get(f'{B}/uefa.champions/summary?event={EV}'); json.dump(s, open('summary.json', 'w'), indent=1, ensure_ascii=False)
shots, seen = [], set()
for x in s['commentary']:
    txt = x['text']
    if not re.match(r'^(Attempt (saved|missed|blocked)|Goal!|Penalty saved)', txt): continue
    key = (x['time']['value'], txt)
    if key in seen: continue
    seen.add(key)
    team = re.search(r'\(([^)]+)\)', txt).group(1)
    who = re.search(r'(?:Goal![^.]*\.\s*|Penalty saved\.\s*)?([^.(]+?) \(' + re.escape(team) + r'\)', txt)
    kind = 'goal' if txt.startswith('Goal!') else 'saved' if txt.startswith(('Attempt saved', 'Penalty saved')) else 'missed' if txt.startswith('Attempt missed') else 'blocked'
    m = re.match(r"(\d+)'(?:\+(\d+)')?", x['time']['displayValue']); minute = int(m.group(1)) + (int(m.group(2)) if m.group(2) else 0)
    shots.append({'min': minute, 'side': 'home' if team == 'Sporting Lisbon' else 'away', 'kind': kind, 'who': who.group(1).strip().split()[-1] if who else '?', 'team': team, 'penalty': txt.startswith('Penalty saved') or 'penalty' in txt.lower()})
json.dump(shots, open('shots.json', 'w'), indent=1, ensure_ascii=False)
rows = []
for lg in ('eng.1', 'uefa.champions', 'eng.league_cup', 'eng.fa'):
    sched = get(f'{B}/{lg}/teams/360/schedule?season=2026')
    for e in sched.get('events', []):
        c = e['competitions'][0]
        if c['status']['type']['name'] != 'STATUS_FULL_TIME': continue
        me = [t for t in c['competitors'] if t['team']['id'] == '360'][0]; op = [t for t in c['competitors'] if t['team']['id'] != '360'][0]
        sc = lambda t: int(float((t.get('score') or {}).get('value', 0) if isinstance(t.get('score'), dict) else t.get('score', 0)))
        a, b = sc(me), sc(op)
        rows.append({'date': e['date'][:10], 'comp': lg, 'opp': op['team']['displayName'], 'abbr': op['team']['abbreviation'], 'venue': me['homeAway'], 'score': f'{a}-{b}', 'res': 'W' if a > b else 'D' if a == b else 'L'})
rows.sort(key=lambda r: r['date']); json.dump(rows, open('united_results.json', 'w'), indent=1)
st = get('https://site.api.espn.com/apis/v2/sports/soccer/uefa.champions/standings')
tab = []
for e in st['children'][0]['standings']['entries']:
    g = lambda k: next((x.get('displayValue') for x in e['stats'] if x['name'] == k), None)
    tab.append({'rank': int(g('rank')), 'team': e['team']['displayName'], 'p': int(g('gamesPlayed')), 'w': int(g('wins')), 'd': int(g('ties')), 'l': int(g('losses')), 'pts': int(g('points')), 'gd': g('pointDifferential'),
                'gf': g('pointsFor'), 'ga': g('pointsAgainst')})
tab.sort(key=lambda r: r['rank']); json.dump(tab, open('table.json', 'w'), indent=1)
md5 = []
for d in ('20261124', '20261125'):
    for e in get(f'{B}/uefa.champions/scoreboard?dates={d}').get('events', []):
        c = e['competitions'][0]; t = c['competitors']
        h = [x for x in t if x['homeAway'] == 'home'][0]; a = [x for x in t if x['homeAway'] == 'away'][0]
        md5.append({'date': e['date'][:10], 'home': h['team']['displayName'], 'away': a['team']['displayName'], 'hg': int(h['score']), 'ag': int(a['score'])})
json.dump(md5, open('results_md5.json', 'w'), indent=1)
print('shots', len(shots), '| Sporting', sum(1 for x in shots if x['side'] == 'home'), 'United', sum(1 for x in shots if x['side'] == 'away'), '| United results', len(rows), '| table rows', len(tab), '| md5 results', len(md5))
