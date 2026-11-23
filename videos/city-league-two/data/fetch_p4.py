"""Part 4 real-player data from ESPN (public JSON): McCracken's games (starts, clean sheets, goals conceded, saves) and Championship / League One
midfielders for the January vote (appearances, goals, assists, ...). Writes mccracken.json and mid_candidates.json."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(r, timeout=40))
        except Exception as e: err = e
    return {'error': str(err)}
B = 'https://site.api.espn.com/apis/site/v2/sports/soccer'
# 1) McCracken: every completed Bradford league game this season, his line in the match report
sch = get(f'{B}/eng.3/teams/387/schedule?season=2026')
games = [(e['id'], e['date'][:10]) for e in sch['events'] if e['competitions'][0]['status']['type'].get('completed')]
def game(g):
    s = get(f'{B}/eng.3/summary?event={g[0]}'); out = {'id': g[0], 'date': g[1]}
    for t in s['rosters']:
        if t['team']['displayName'] != 'Bradford City': continue
        for p in t['roster']:
            if p['athlete']['displayName'] in ('Jon McCracken', 'Cameron Dawson') and p.get('position', {}).get('abbreviation') == 'G':
                st = {x['name']: x['value'] for x in p.get('stats', [])}
                out[p['athlete']['displayName']] = {'starter': p.get('starter'), 'saves': st.get('saves'), 'conceded': st.get('goalsConceded'), 'subbedOut': p.get('subbedOut')}
    c = s['header']['competitions'][0]['competitors']; out['score'] = [(x['team']['displayName'], x['score']) for x in c]
    return out
with ThreadPoolExecutor(6) as ex: gl = sorted(ex.map(game, games), key=lambda g: g['date'])
json.dump(gl, open('mccracken.json', 'w'), indent=1)
mc = [g for g in gl if 'Jon McCracken' in g]
print('Bradford games', len(gl), '| McCracken in', len(mc), '| starts', sum(1 for g in mc if g['Jon McCracken']['starter']),
      '| clean sheets', sum(1 for g in mc if g['Jon McCracken']['conceded'] == 0 and g['Jon McCracken']['starter']), '| conceded', sum(g['Jon McCracken']['conceded'] or 0 for g in mc),
      '| saves', sum(g['Jon McCracken']['saves'] or 0 for g in mc), '| saves per start %.2f' % (sum(g['Jon McCracken']['saves'] or 0 for g in mc) / max(1, len(mc))))
for g in gl: print(g['date'], g['score'], {k: v for k, v in g.items() if k in ('Jon McCracken', 'Cameron Dawson')})
