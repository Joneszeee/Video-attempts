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


NUMBER_WORDS = set('one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen '
                   'nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion first second third '
                   'half minus'.split())
STOP = set('the a an and but so or if on in at of for to by with from as is was are were be been it its this that these those '
           'what when where who why how there they their them he his she her we our you your i my me take every reports opta\'s '
           'for context until tell'.split())


def caption_words(spec, beat_starts, speech):
    """Each spoken word with its timeline time, phrase group and whether it is a key word (names, numbers, beat 'keys')."""
    names = set()
    for b in spec['beats']:
        toks = b.get('vo', '').split()
        for j, w in enumerate(toks):
            core = re.sub(r"[^\w'’\-]", '', w)
            if j > 0 and core[:1].isupper() and not re.search(r'[.?!:]$', toks[j - 1]) and core.lower() not in STOP:
                names.add(core.lower())
    out, g = [], 0
    w = lambda ch: PAUSE.get(ch, 1)
    for i, b in enumerate(spec['beats']):
        text = b.get('vo', '')
        if not text:
            continue
        s0, s1 = speech[i]
        total = max(1, sum(w(c) for c in text))
        keys = {k.lower() for k in b.get('keys', [])}
        g += 1
        n_in = 0
        for m in re.finditer(r'\S+', text):
            word = m.group(0)
            core = re.sub(r"[^\w'’\-]", '', word).lower()
            t = s0 + sum(w(c) for c in text[:m.start()]) / total * (s1 - s0)
            key = (bool(re.search(r'\d', word)) or core in keys or core in names or core.split('-')[0] in NUMBER_WORDS
                   or core.endswith('ty') and core in NUMBER_WORDS)
            if core in ('one', 'first', 'second', 'half', 'minus') and core not in keys:
                key = False
            if n_in >= (spec.get('captionMax') or 5):
                g += 1
                n_in = 0
            out.append({'w': word, 't': round(t, 3), 'g': g, 'key': key})
            n_in += 1
            if re.search(r'[,.;:?!—]$', word):
                g += 1
                n_in = 0
    return out


def resolve(spec, beat_starts, speech):
    """beat_starts: timeline start of each beat. speech: timeline (start, end) of each beat's spoken line."""
    if spec.get('captions'):
        spec['captionWords'] = caption_words(spec, beat_starts, speech)
    out = []
    for i, b in enumerate(spec['beats']):
        s0, s1 = speech[i]
        rel = lambda phrase: round(s0 + frac_of(b.get('vo', ''), phrase) * (s1 - s0) - beat_starts[i], 3)
        _resolve_beat(b, rel)
        for sh in b.get('shots', []):
            # inside a shot, phrases resolve relative to the shot's start, and plain numbers already are
            sh['_t'] = t0 = rel(sh['at'])
            _resolve_beat(sh, lambda phrase, t0=t0: round(rel(phrase) - t0, 3))
        out.extend(_split(b))
    spec['beats'] = out


def _cards(b):
    c = b.get('card')
    return [x for x in (c if isinstance(c, list) else [c]) if isinstance(x, dict)]


def _resolve_beat(b, rel):
    for c in _cards(b):
        if 'at' in c:
            c['delay'] = round(rel(c.pop('at')) + c.pop('lag', 0), 3)
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
        if c.get('type') == 'rain':
            for g in c['groups']:
                if 'at' in g:
                    g['t'] = round(max(0, rel(g.pop('at')) - base), 3)
            if isinstance(c.get('emptyAt'), str):
                c['emptyT'] = round(max(0, rel(c.pop('emptyAt')) - base), 3)
        if c.get('type') == 'tactic':
            for lst in (c.get('moves') or [], c.get('cam') or []):
                for m in lst:
                    if 'at' in m:
                        m['t'] = round(max(0, rel(m.pop('at')) + m.pop('lag', 0) - base), 3)
            for pl in c.get('players') or []:
                if 'nameAt' in pl:
                    pl['nameT'] = round(max(0, rel(pl.pop('nameAt')) - base), 3)
        if c.get('type') in ('shelf', 'tape'):
            for it in c.get('items') or c.get('rows') or []:
                if 'at' in it:
                    it['t'] = round(max(0, rel(it.pop('at')) + it.pop('lag', 0) - base), 3)
            for key, out in (('emptyAt', 'emptyT'), ('captionAt', 'captionT')):
                if isinstance(c.get(key), str):
                    c[out] = round(max(0, rel(c.pop(key)) - base), 3)
        if c.get('type') == 'stack':
            for it in c['items']:
                if 'at' in it:
                    it['t'] = round(max(0, rel(it.pop('at')) - base), 3)
        if c.get('type') == 'shotmap':
            for sh in c['shots']:
                if 'at' in sh:
                    sh['t'] = round(max(0, rel(sh.pop('at')) - base), 3)
            if isinstance(c.get('blockedAt'), str):
                c['blockedT'] = round(max(0, rel(c.pop('blockedAt')) - base), 3)
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
        if 'actionAt' in p:  # e.g. the kick starts so the strike lands on the word: use "lag" to shift
            p['actionDelay'] = round(rel(p.pop('actionAt')) + p.pop('actionLag', 0), 3)
    if isinstance(b.get('confettiAt'), str):
        b['confettiDelay'] = round(rel(b.pop('confettiAt')), 3)
    if isinstance(b.get('freezeAt'), str):
        b['freeze'] = round(rel(b.pop('freezeAt')) + b.pop('freezeLag', 0), 3)
    for key in ('punch', 'shake', 'speedlines'):
        for fx in b.get(key) or []:
            if 'at' in fx:
                fx['t'] = round(rel(fx.pop('at')) + fx.pop('lag', 0), 3)


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
        if 'accent' in prev and 'accent' not in sh and 'headline' not in sh:  # same headline keeps its accent
            nb['accent'] = prev['accent']
        parts.append(nb)
        prev = nb
    return parts
