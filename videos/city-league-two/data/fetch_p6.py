"""Part 6: real stats (ESPN rosters, as of the run date) for the three players City signed or kept (Bowen, Moylan, Ward-Prowse) -> p6_real.json (asserted in videos/city-part-6/gen.py)."""
import json, urllib.request, datetime
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(r, timeout=40))
        except Exception as e: err = e
    return {}
B = 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2'
ids = json.load(open('ch_team_ids.json'))
WANT = {'James Ward-Prowse': 'Southampton', 'Jack Moylan': 'Cardiff City', 'Jarrod Bowen': 'West Ham United'}
out = {'asof': datetime.date.today().isoformat(), 'players': {}}
for nm, club in WANT.items():
    for a in get(f'{B}/teams/{ids[club]}/roster').get('athletes', []):
        if a.get('displayName') == nm:
            st = {}
            for cat in a.get('statistics', {}).get('splits', {}).get('categories', []):
                for s in cat.get('stats', []): st[s['name']] = s.get('value')
            out['players'][nm] = {'club': club, 'age': a.get('age'), 'pos': (a.get('position') or {}).get('abbreviation'), 'apps': st.get('appearances'), 'subIns': st.get('subIns'),
                                  'starts': (st.get('appearances') or 0) - (st.get('subIns') or 0), 'goals': st.get('totalGoals'), 'assists': st.get('goalAssists'), 'shots': st.get('totalShots'), 'sot': st.get('shotsOnTarget'), 'id': a.get('id')}
            print(nm, out['players'][nm])
json.dump(out, open('p6_real.json', 'w'), indent=1)
