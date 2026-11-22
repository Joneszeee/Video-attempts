"""Shared building blocks for videos/<slug>/gen.py (so each video's script stays short and the same fixes apply everywhere).

    import sys; sys.path.insert(0, 'engine'); from lib import *
    V, lines = start('videos/<slug>/')
    B = []
    ... B.append({...}) using P(), goal(), bug(), hud(), stamp(), big(), clean_tackle() ...
    save(V, B, lines, 'Title', accent=TEAL)

Everything here encodes rules the user asked for (see CLAUDE.md): shooters stay on screen through the run-up, one defender blocks and one
covers, the keeper is beaten or makes a real save, tackles are clean (no fall, the ball goes to a team-mate), score bugs clear the headline.
"""
import json
import math

RED, GOLD, GREEN, TEAL, SKY = "#ff4d5e", "#e9b949", "#2ecc71", "#3FE0C5", "#6cabdd"
GK_YELLOW = {"shirt": "#f7d117", "shorts": "#111111", "socks": "#f7d117", "text": "#111111"}
GK_GREEN = {"shirt": "#2ecc71", "shorts": "#111111", "socks": "#2ecc71", "text": "#111111"}


def kit(shirt, shorts=None, socks=None, text="#ffffff", **extra):
    """kit('#a50044', '#004d98', stripes=['#a50044', '#004d98'])"""
    d = {"shirt": shirt, "shorts": shorts or shirt, "socks": socks or shirt, "text": text}
    d.update(extra)
    return d


def stadium(crowd, seed=7, **k):
    d = {"type": "stadium", "crowd": crowd, "seed": seed}
    d.update(k)
    return d


def small(crowd, seed=7, **k):
    """League Two / lower-league ground."""
    return stadium(crowd, seed, ground="small", **k)


def start(folder):
    """Returns (folder, VO lines) from videos/<slug>/vo.txt."""
    lines = [l.strip() for l in open(folder + 'vo.txt').read().split('<break time="0.8s" />')]
    return folder, lines


def save(folder, beats, lines, title, accent=TEAL, **spec):
    for b, v in zip(beats, lines):
        b["vo"] = v
    assert len(beats) == len(lines), f'{len(beats)} beats but {len(lines)} VO lines'
    out = {"title": title, "brand": "theo6k", "accent": accent, "voSpeed": 1.08, "beats": beats}
    out.update(spec)
    json.dump(out, open(folder + 'spec.json', 'w'), indent=1, ensure_ascii=False)
    print("ok", len(beats), "beats")


def P(**k):
    d = {"name": "", "num": None}
    d.update(k)
    return d


def mid(a, c, h):
    return [(a[0] + c[0]) / 2, h, (a[2] + c[2]) / 2]


def cam(pos, tgt, frm=None, frm_tgt=None, move=5, **k):
    d = {"camera": {"pos": pos, "tgt": tgt}, "camFrom": {"pos": frm or pos, "tgt": frm_tgt or tgt}, "move": move, "moveEase": "linear"}
    d.update(k)
    return d


def hud(sub, **k):
    """Simulation frame (what-if videos). counter=False for one simulated match (no 10,000-run counter; just the SIM tag, low in the corner)."""
    d = {"type": "simhud", "delay": 0, "sub": sub, "dur": 0, "clear": False}
    d.update(k)
    return d


def bug(home, away, score, mn, frm=None, goalAt=None, lag=0.3, **k):
    """TV score bug; home/away = {"name": "MCI", "color": "#6cabdd"}. It clears a two-line headline by itself."""
    d = {"type": "scorebug", "y": 560, "delay": 0, "home": home, "away": away, "score": score, "min": mn}
    if frm:
        d.update({"from": frm, "goalAt": goalAt, "goalLag": lag})
    d.update(k)
    return d


def stamp(text, at, sub=None, color=RED, y=1600, size=96, lag=-0.1, rot=-0.07, **k):
    d = {"type": "stamp", "text": text, "at": at, "lag": lag, "color": color, "rot": rot, "size": size, "y": y}
    if sub:
        d["sub"] = sub
    d.update(k)
    return d


def big(value, at, label, frm=0, y=1500, size=170, dur=0.8, lag=-0.2, **k):
    d = {"type": "big", "at": at, "lag": lag, "from": frm, "value": value, "countDur": dur, "label": label, "y": y, "size": size}
    d.update(k)
    return d


def goal(word, x, z, side, shooter_kit, end, keeper_dir, keeper_kit, def_kit, lag=-0.5, label=None, save_it=False, **shooter):
    """A shot on goal timed so contact lands on `word`.
    x, z: shooter's spot (z about 40-42); side: +1/-1 = which side the camera sits; end: [x, y, 52.3] where the ball ends (inside the posts);
    keeper_dir: the way he dives (send him the wrong way for a goal). save_it=True puts the ball in his gloves instead.
    Returns (players, cards, camera keys) — the shooter is on screen for the whole run-up (camera behind and to one side)."""
    b0 = [x + (-0.22 if shooter.get('foot') == 'left' else 0.22), 0.11, z + 0.45]   # ball on his stronger foot
    sh = P(kit=shooter_kit, x=x, z=z, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate", runup=1.6, **shooter)
    if label:
        sh.update(label=label, labelDelay=0.1)
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=keeper_dir)
    if not save_it:
        keeper.update(actionAt=word, actionLag=lag + 0.45)
    pl = [sh, keeper,
          P(kit=def_kit, skin="#e7b593", hair="#141010", x=x + side * -1.9, z=z + 3.4, front=True, action="dive", dir=side, actionAt=word, actionLag=lag + 0.15, actionDur=0.7),
          P(kit=def_kit, skin="#8a5a3c", hair="#141010", x=-end[0] * 0.8, z=47.8, front=True)]
    shot = {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": 0.5, "slowmo": False, "points": [b0, mid(b0, end, 0.9), end]}
    if save_it:
        shot.update(flash=False, saveBy=1)
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34}, shot]
    camk = {"camFrom": {"pos": [round(x + side * 3.0, 2), 2.2, z - 9], "tgt": [round(x * 0.4, 2), 1.0, 52]},
            "camera": {"pos": [round(x + side * 2.4, 2), 1.9, z - 6.3], "tgt": [round(x * 0.4, 2), 1.0, 52]}, "move": 4, "moveEase": "linear", "follow": 0.5}
    return pl, cards, camk


def freekick(word, x, z, shooter_kit, wall_kit, keeper_kit, end, keeper_dir, side=1, lag=-0.5, label=None, wall_n=4, jump=True, **shooter):
    """A direct free kick with contact on `word`: the shooter stands over the ball at (x, z) (z about 28-33), a wall of `wall_n` faces him 9.15 m
    away on the line to goal and jumps as he strikes, the ball goes over it and dips into `end` ([x, y, 52.3], inside the posts). keeper_dir: the
    way the keeper dives (the same way as the ball = he is beaten by pace; he starts late so the ball passes his fingertips).
    Returns (players, cards, camera keys) like goal(); the camera sits behind and to one side of the shooter (side +1/-1)."""
    b0 = [x + (-0.22 if shooter.get('foot') == 'left' else 0.22), 0.11, z + 0.45]
    sh = P(kit=shooter_kit, x=x, z=z, action="kick", actionAt=word, actionLag=lag, actionDur=0.8, after="celebrate", runup=2.0, **shooter)
    if label:
        sh.update(label=label, labelDelay=0.1)
    dx, dz = -x, 52.5 - z
    n = (dx * dx + dz * dz) ** 0.5
    ux, uz = dx / n, dz / n                           # unit vector from the ball to the middle of the goal
    cx, cz = x + 9.15 * ux, z + 9.15 * uz             # the wall stands 9.15 m away on that line
    looks = [("#e7b593", "#141010"), ("#8a5a3c", "#141010"), ("#f0c8a8", "#6a4a2a"), ("#c99b7a", "#2a1a10"), ("#e7b593", "#3a2a1a")]
    wall = []
    for i in range(wall_n):
        off = (i - (wall_n - 1) / 2) * 0.62
        sk, hr = looks[i % len(looks)]
        w = P(kit=wall_kit, skin=sk, hair=hr, x=round(cx - uz * off, 2), z=round(cz + ux * off, 2), front=True)
        if jump:
            w.update(hops=[{"at": word, "lag": lag + 0.28, "dur": 0.55, "height": 0.45}])
        wall.append(w)
    keeper = P(kit=keeper_kit, skin="#f0c8a8", hair="#3a2a1a", gloves="#f2f2f2", x=0, z=52.0, front=True, pose="keeper", before="ready", action="dive", dir=keeper_dir,
               actionAt=word, actionLag=lag + 0.62)
    ctrl = [round(b0[0] + 0.55 * (end[0] - b0[0]), 2), 4.6, round(b0[2] + 0.55 * (end[2] - b0[2]), 2)]   # high over the wall, dipping late
    shot = {"type": "ballpath", "world": True, "at": word, "lag": lag + 0.34, "dur": 1.0, "slowmo": True, "points": [b0, ctrl, end]}
    cards = [{"type": "ball", "delay": 0, "point": b0, "untilAt": word, "untilLag": lag + 0.34}, shot]
    # the camera sits well to one side and behind the shooter, so his body never hides the ball's path to the corner;
    # it looks midway (in bearing) between the shooter and the middle of the goal, so both stay in frame
    def aim(cam):
        bearing = lambda px, pz: math.atan2(cam[0] - px, pz - cam[2])
        th = (bearing(x, z) + bearing(0.0, 52.5)) / 2
        return [round(cam[0] - math.tan(th) * (47 - cam[2]), 2), 1.2, 47]
    c0 = [round(x + side * 7.0, 2), 2.3, round(z - 6.5, 2)]
    c1 = [round(x + side * 6.0, 2), 2.0, round(z - 4.0, 2)]
    camk = {"camFrom": {"pos": c0, "tgt": aim(c0)}, "camera": {"pos": c1, "tgt": aim(c1)}, "move": 4, "moveEase": "linear", "follow": 0.12}
    return [sh] + wall + [keeper], cards, camk


def foul_from_behind(word, victim_kit, fouler_kit, victim=None, fouler=None, lag=0.0, lead=3.6, victim_label=None, fouler_label=None):
    """A clean-through player is brought down by a defender who chases him and slides in from behind, with contact on `word` (the engine's slide + fall).
    Both start running `lead` seconds before the word (a negative start = already mid-run on frame 0), so the contact always lands on the word.
    victim / fouler = extra P() kwargs (skin, hair, name, num, foot...). Returns (players, cards, camera keys): a side-on camera 6 m away that tracks
    the run (about 3.4 s). The loose ball keeps rolling after contact (a ballpath that is not a goal)."""
    v = dict(victim or {})
    f = dict(fouler or {})
    pv = P(kit=victim_kit, dribble=True, dribbleUntil=round(lead - 0.05, 2), x=0.2, z=17.5, path=[[0.2, 17.5], [0.5, 26.0], [0.9, 33.5], [1.2, 38.8]], pathDur=round(lead + 0.25, 2),
           at=word, lag=-lead + lag, action="fall", actionAt=word, actionLag=0.1 + lag, **v)
    pf = P(kit=fouler_kit, x=-2.4, z=11.0, path=[[-2.4, 11.0], [-1.7, 21.5], [-0.8, 30.0], [0.5, 36.0]], pathDur=round(lead - 0.1, 2),
           at=word, lag=-lead + lag, action="slide", dir=1, actionAt=word, actionLag=-0.5 + lag, actionDur=1.1, **f)
    if victim_label:
        pv.update(label=victim_label, labelDelay=round(lead - 1.2, 2))
    if fouler_label:
        pf.update(label=fouler_label, labelDelay=round(lead - 0.4, 2))
    cards = [{"type": "ballpath", "world": True, "at": word, "lag": 0.15 + lag, "dur": 0.9, "slowmo": True, "flash": False, "points": [[1.3, 0.11, 39.0], [2.4, 0.2, 41.5], [3.6, 0.11, 43.8]]}]
    camk = {"camFrom": {"pos": [7.0, 1.6, 19.5], "tgt": [0.6, 1.0, 23.0]}, "camera": {"pos": [6.2, 1.6, 34.5], "tgt": [1.2, 1.0, 38.0]}, "move": 3.4, "moveEase": "linear", "hype": False}
    return [pv, pf], cards, camk


def clean_tackle(word, tackler, runner_kit, mate_kit, label=None):
    """A clean slide tackle with contact on `word` (user: no foul, the ball never vanishes): the runner dribbles across, the tackler jogs
    in and slides, the ball is poked into a team-mate's stride, the runner hurdles the leg and keeps going. tackler = P(...) kwargs (kit, skin...).
    Returns (players, cards, camera keys); filmed side-on from 8-10 m."""
    t = dict(tackler)
    t.update(x=-4.5, z=2.2, path=[[-4.5, 2.2], [-1.6, 4.4], [0.5, 6.1]], pathDur=2.4, at=word, lag=-2.1, action="slide", dir=-1, actionAt=word, actionLag=-0.4)
    if label:
        t.update(label=label, labelAt=word)
    pl = [P(kit=runner_kit, skin="#e7b593", hair="#141010", x=4.5, z=8.5, path=[[4.5, 8.5], [0.8, 6.6], [-2.2, 6.4]], pathDur=1.5, at=word, lag=-0.87,
            dribble=True, dribbleUntil=0.87, hops=[{"at": word, "lag": -0.08, "dur": 0.5, "height": 0.3}]),
          P(**t),
          P(kit=mate_kit, skin="#f0c8a8", hair="#6a4a2a", num=4, x=4.0, z=2.8, path=[[4.0, 2.8], [2.4, 4.3], [0.6, 8.0]], pathDur=1.5, at=word, lag=0.05, dribble=True, dribbleFrom=0.55)]
    cards = [{"type": "ballpath", "world": True, "at": word, "lag": 0.0, "dur": 0.6, "slowmo": False, "flash": False, "points": [[0.27, 0.11, 6.32], [1.3, 0.16, 5.6], [2.09, 0.11, 4.93]]}]
    camk = {"camFrom": {"pos": [-6.0, 1.7, -1.6], "tgt": [0.6, 0.8, 6.2]}, "camera": {"pos": [-4.9, 1.6, -0.3], "tgt": [0.8, 0.8, 6.4]}, "move": 5, "moveEase": "linear",
            "punch": [{"at": word, "lag": -0.05, "amount": 0.14, "dur": 1.3, "x": 480, "y": 1060}], "hype": False}
    return pl, cards, camk


def tags_count(tags):
    """YouTube's tag-box count: each tag's length, +2 for a tag with a space, +1 per comma (aim for 490-500)."""
    return sum(len(t) + (2 if ' ' in t else 0) for t in tags) + len(tags) - 1
