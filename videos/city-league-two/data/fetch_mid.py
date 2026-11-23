"""Part 4: January vote candidates. Every Championship midfielder's real season numbers from ESPN's roster feed -> mid_candidates.json."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(r, timeout=40))
        except Exception as e: err = e
    return {'athletes': [], 'error': str(err)}
B = 'https://site.api.espn.com/apis/site/v2/sports/soccer'
ids = json.load(open('ch_team_ids.json'))
def team(kv):
    name, tid = kv; d = get(f'{B}/eng.2/teams/{tid}/roster'); out = []
    for a in d.get('athletes', []):
        pos = a.get('position', {}).get('abbreviation')
        st = {}
        for cat in a.get('statistics', {}).get('splits', {}).get('categories', []):
            for s in cat.get('stats', []): st[s['name']] = s.get('value')
        out.append({'club': name, 'name': a.get('displayName'), 'id': a.get('id'), 'pos': pos, 'age': a.get('age'), 'stats': st})
    return out
with ThreadPoolExecutor(6) as ex: res = [p for t in ex.map(team, ids.items()) for p in t]
json.dump(res, open('ch_players.json', 'w'))
print(len(res), 'players; stat names on one:', sorted(next(p for p in res if p['stats'])['stats'])[:40])
mids = [p for p in res if p['pos'] == 'M' and (p['stats'].get('appearances') or 0) >= 10]
mids.sort(key=lambda p: -(p['stats'].get('appearances') or 0))
for p in mids: s = p['stats']; print('%-24s %-24s age %-3s apps %-3s subIns %-3s goals %-3s assists %-3s' % (p['name'], p['club'], p['age'], s.get('appearances'), s.get('subIns'), s.get('totalGoals'), s.get('goalAssists')))
