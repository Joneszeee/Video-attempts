"""Part 5: the step-up vote needs right-sided attackers. Every Championship and League One game this season (ESPN match reports): who played on the right (RM / AM-R / RW / RF),
with goals and assists in those reports -> right_wing.json. Also refreshes Ward-Prowse's and Moylan's numbers."""
import json, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(r, timeout=40))
        except Exception as e: err = e
    return {}
B = 'https://site.api.espn.com/apis/site/v2/sports/soccer'
RIGHT = {'RM', 'AM-R', 'RW', 'RF'}
res = {}
for lg, idsf in (('eng.2', 'ch_team_ids.json'), ('eng.3', 'l1_team_ids.json')):
    ids = json.load(open(idsf)); ev = {}
    def sched(tid): return get(f'{B}/{lg}/teams/{tid}/schedule?season=2026').get('events', [])
    with ThreadPoolExecutor(8) as ex:
        for evs in ex.map(sched, ids.values()):
            for e in evs:
                if e['competitions'][0]['status']['type'].get('completed') and e.get('season', {}).get('slug', 'x') != 'x' or True:
                    if e['competitions'][0]['status']['type'].get('completed'): ev[e['id']] = e['date'][:10]
    def match(eid):
        out = []
        for t in get(f'{B}/{lg}/summary?event={eid}').get('rosters', []):
            for p in t['roster']:
                st = {x['name']: x['value'] for x in p.get('stats', [])}
                out.append((p['athlete']['id'], p['athlete']['displayName'], t['team']['displayName'], p.get('position', {}).get('abbreviation'), p.get('starter'), st.get('totalGoals') or 0, st.get('goalAssists') or 0))
        return out
    pl = collections.defaultdict(lambda: {'games': 0, 'right': 0, 'g': 0, 'a': 0, 'rg': 0, 'ra': 0})
    with ThreadPoolExecutor(8) as ex:
        for m in ex.map(match, list(ev)):
            for pid, nm, club, pos, starter, g, a in m:
                d = pl[(pid, nm, club)]
                if starter is not None: d['games'] += 1; d['g'] += g; d['a'] += a
                if pos in RIGHT and starter: d['right'] += 1; d['rg'] += g; d['ra'] += a
    res[lg] = [{'id': k[0], 'name': k[1], 'club': k[2], **v} for k, v in pl.items() if v['right'] >= 6]
    print(lg, len(ev), 'matches;', len(res[lg]), 'players with 6+ starts on the right')
json.dump(res, open('right_wing.json', 'w'), indent=1)
for lg in res:
    print('==', lg, '(by goals + assists in games on the right)')
    for p in sorted(res[lg], key=lambda p: -(p['rg'] + p['ra']))[:14]: print('  %-22s %-24s right-side starts %2d of %2d | G %2d A %2d (on the right: G %d A %d)' % (p['name'], p['club'], p['right'], p['games'], p['g'], p['a'], p['rg'], p['ra']))
# refresh the two signings' numbers
for nm, club, lg, tid in (('James Ward-Prowse', 'Southampton', 'eng.2', json.load(open('ch_team_ids.json'))['Southampton']), ('Jack Moylan', 'Cardiff City', 'eng.2', json.load(open('ch_team_ids.json'))['Cardiff City'])):
    for a in get(f'{B}/{lg}/teams/{tid}/roster').get('athletes', []):
        if a.get('displayName') == nm:
            st = {}
            for cat in a.get('statistics', {}).get('splits', {}).get('categories', []):
                for s in cat.get('stats', []): st[s['name']] = s.get('value')
            print('REFRESH', nm, club, 'age', a.get('age'), 'apps', st.get('appearances'), 'subIns', st.get('subIns'), 'G', st.get('totalGoals'), 'A', st.get('goalAssists'))
