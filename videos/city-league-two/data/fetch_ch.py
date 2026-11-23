"""Part 4: Championship league results (2025/26 + 2026/27 to date) from ESPN's public scoreboard (one request per day), to rate the clubs
that come down. Output: espn_ch.json = [[date, home, away, home_goals, away_goals], ...] (same shape as espn_games.json)."""
import json, urllib.request, datetime, collections
from concurrent.futures import ThreadPoolExecutor
def get(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(r, timeout=40))
        except Exception: pass
    return {'events': []}
d0, d1 = datetime.date(2025, 8, 1), datetime.date.today()
days = [d0 + datetime.timedelta(days=i) for i in range((d1 - d0).days + 1)]
def day(d):
    out = []
    for ev in get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2/scoreboard?dates={d:%Y%m%d}').get('events', []):
        c = ev['competitions'][0]
        if not c['status']['type'].get('completed'): continue
        h = next(t for t in c['competitors'] if t['homeAway'] == 'home'); a = next(t for t in c['competitors'] if t['homeAway'] == 'away')
        out.append((ev['id'], [ev['date'][:10], h['team']['displayName'], a['team']['displayName'], int(h['score']), int(a['score'])]))
    return out
with ThreadPoolExecutor(8) as ex: res = list(ex.map(day, days))
rows = {i: r for lst in res for i, r in lst}
out = sorted(rows.values())
json.dump(out, open('espn_ch.json', 'w'))
print(len(out), 'games', out[0], out[-1])
print(sorted(collections.Counter(r[0][:7] for r in out).items()))
