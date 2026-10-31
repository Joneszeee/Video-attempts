"""Word-synced visuals: lets a spec pin anything to the moment a phrase is spoken.

In spec.json, inside a beat:
  - card:          "at": "Gerd Müller"     -> the card starts when that phrase is said
  - pen stroke:    "at": "Sixteen"         -> the stroke draws when that word is said
  - player:        "at": "..." (enter), "tagAt": "..." (the gold number pops)
  - beat "shots":  [{"at": "Gerd Müller", ...beat fields...}, ...]
                   -> the beat is cut into several shots inside one voice line (new camera, players, cards, headline...).

Times are estimated inside each spoken line from character position (punctuation counts as a pause), using the
line's real start and end in the voiceover. Accurate to roughly a quarter of a second.
"""
import copy
import re
import subprocess

PAUSE = {',': 4, ';': 5, ':': 5, '.': 7, '?': 7, '!': 7, '—': 5, '–': 3}


def silences(path, noise_db=-35, min_len=0.15):
    err = subprocess.run(['ffmpeg', '-i', str(path), '-af', f'silencedetect=noise={noise_db}dB:d={min_len}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    e = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    return list(zip(s, e))


def line_spans(vo_path, starts, total):
    """(start, end) of speech for each line, in audio seconds. starts = line start times."""
    sil = silences(vo_path)
    spans = []
    for i, st in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else total + 0.01
        # the pause just before the next line starts marks this line's end
        cands = [s for s, e in sil if st + 0.3 < s < nxt and abs(e - nxt) < 0.35]
        end = max(cands) if cands else (nxt - 0.35 if i + 1 < len(starts) else
                                         max([s for s, e in sil if s > st + 0.3] or [total]))
        spans.append((st, max(end, st + 0.3)))
    return spans


def frac_of(text, phrase):
    low, p = text.lower(), phrase.lower()
    k = low.find(p)
    if k < 0:
        raise SystemExit(f'cue "{phrase}" not found in line: {text}')
    w = lambda ch: PAUSE.get(ch, 1)
    return sum(w(c) for c in text[:k]) / max(1, sum(w(c) for c in text))


def resolve(spec, beat_starts, speech):
    """beat_starts: timeline start of each beat. speech: timeline (start, end) of each beat's spoken line."""
    out = []
    for i, b in enumerate(spec['beats']):
        s0, s1 = speech[i]
        rel = lambda phrase: round(s0 + frac_of(b.get('vo', ''), phrase) * (s1 - s0) - beat_starts[i], 3)
        _resolve_beat(b, rel)
        for sh in b.get('shots', []):
            sh['_t'] = rel(sh['at'])
            _resolve_beat(sh, rel)
        out.extend(_split(b))
    spec['beats'] = out


def _cards(b):
    c = b.get('card')
    return [x for x in (c if isinstance(c, list) else [c]) if isinstance(x, dict)]


def _resolve_beat(b, rel):
    for c in _cards(b):
        if 'at' in c:
            c['delay'] = rel(c.pop('at'))
        base = c.get('delay', 0.3)
        for fp in c.get('focusPath') or []:
            if 'at' in fp:
                fp['t'] = round(max(0, rel(fp.pop('at')) - base), 3)
        for key in ('captionAt', 'swapAt'):
            if isinstance(c.get(key), str):
                c[key] = round(max(0, rel(c[key]) - base), 3)
        if c.get('type') == 'receipt' and isinstance(c.get('totalAt'), str):
            n = len(c.get('lines', [])) + 1
            c['step'] = round(max(0.15, (rel(c.pop('totalAt')) - base - 0.2) / n), 3)
        if c.get('type') == 'pen':
            base = c.get('delay', 0.3)
            for s in c['strokes']:
                if 'at' in s:
                    s['t'] = round(max(0, rel(s.pop('at')) - base), 3)
    for p in b.get('players') or []:
        if 'at' in p:
            p['delay'] = rel(p.pop('at'))
        if 'tagAt' in p:
            p['tagDelay'] = rel(p.pop('tagAt'))


def _shift(b, dt):
    """Make a shot's times relative to the shot's own start."""
    for c in _cards(b):
        if 'delay' in c:
            c['delay'] = round(c['delay'] - dt, 3)
    for p in b.get('players') or []:
        for k in ('delay', 'tagDelay'):
            if k in p:
                p[k] = round(p[k] - dt, 3)


def _split(b):
    shots = sorted(b.pop('shots', []), key=lambda s: s['_t'])
    if not shots:
        return [b]
    total = b['duration']
    parts, prev = [b], b
    cuts = [s['_t'] for s in shots] + [total]
    b['duration'] = round(cuts[0], 3)
    for k, sh in enumerate(shots):
        nb = {key: copy.deepcopy(v) for key, v in sh.items() if key not in ('at', '_t')}
        nb.setdefault('headline', prev.get('headline'))
        nb.setdefault('camera', prev.get('camera'))
        if prev.get('zoom') is not None:
            nb.setdefault('zoom', prev.get('zoom'))
        nb.setdefault('card', 'same' if prev.get('card') else None)
        nb['vo'] = ''
        nb['duration'] = round(cuts[k + 1] - cuts[k], 3)
        _shift(nb, sh['_t'])
        parts.append(nb)
        prev = nb
    return parts
