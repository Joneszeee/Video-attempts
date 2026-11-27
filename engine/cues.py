"""Word-synced visuals: lets a spec pin anything to the moment a phrase is spoken.

In spec.json, inside a beat:
  - card:          "at": "Gerd Müller"     -> the card starts when that phrase is said
  - pen stroke:    "at": "Sixteen"         -> the stroke draws when that word is said
  - player:        "at": "..." (enter), "tagAt": "..." (the gold number pops)
  - beat "shots":  [{"at": "Gerd Müller", ...beat fields...}, ...]
                   -> the beat is cut into several shots inside one voice line (new camera, players, cards, headline...).

Times are estimated inside each spoken line from character position (punctuation counts as a pause), using the
line's real start and end in the voiceover. Sentence breaks inside a line (. ? ! … ; :) are pinned to the real pauses
the voice leaves there, so a cue on the second or third sentence lands on its word, not half a second early.
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
        if cands:
            end = max(cands)
        elif i + 1 < len(starts):
            end = nxt - 0.35
        else:   # the last line ends at the trailing silence; when the file has none (a reference read that stops on its last word) it ends with the file,
                # not at the last pause inside the line (that cut the last line's second sentence short and made a 0.6 s shot)
            trail = [s for s, e in sil if s > st + 0.3 and e >= total - 0.4]
            end = max(trail) if trail else total - 0.05
        spans.append((st, max(end, st + 0.3)))
    return spans


BREAK = re.compile(r'[.?!…;:]+(?=\s)')


def _w(ch):
    return PAUSE.get(ch, 1)


def timer(text, s0, s1, pauses=()):
    """Returns f(char index) -> spoken time in a line spoken from s0 to s1. Time is shared out by text weight, except that each
    sentence break is pinned to the real pause nearest to where it would fall (pauses = (start, end) silences inside the line)."""
    cum = [0]
    for c in text:
        cum.append(cum[-1] + _w(c))
    T = max(1, cum[-1])
    pins = [(0, s0)]
    pz = sorted((a, e) for a, e in pauses if s0 + 0.15 < a and e < s1 - 0.1)
    tol = 0.3 + 0.2 * (s1 - s0)
    for m in BREAK.finditer(text):
        k0, k1 = m.start(), m.end() + 1                  # the mark ... the next word
        if k1 >= len(text):
            continue
        est = s0 + cum[k0] / T * (s1 - s0)
        cand = [(abs(a - est), a, e) for a, e in pz if a > pins[-1][1] + 0.05 and abs(a - est) < tol]
        if cand:
            _, a, e = min(cand)
            pins += [(cum[k0], a), (cum[k1], e)]
            pz = [x for x in pz if x[0] > e]
    pins.append((T, max(s1, pins[-1][1] + 0.05)))

    def f(k):
        x = cum[max(0, min(k, len(text)))]
        for (x0, t0), (x1, t1) in zip(pins, pins[1:]):
            if x <= x1:
                return t0 + (x - x0) / max(1e-9, x1 - x0) * (t1 - t0)
        return pins[-1][1]
    return f


def index_of(text, phrase):
    k = text.lower().find(phrase.lower())
    if k < 0:
        raise SystemExit(f'cue "{phrase}" not found in line: {text}')
    return k


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
    for i, b in enumerate(spec['beats']):
        text = b.get('vo', '')
        if not text:
            continue
        s0, s1 = speech[i][:2]
        at = timer(text, s0, s1, speech[i][2] if len(speech[i]) > 2 else ())
        keys = {k.lower() for k in b.get('keys', [])}
        g += 1
        n_in = 0
        for m in re.finditer(r'\S+', text):
            word = m.group(0)
            core = re.sub(r"[^\w'’\-]", '', word).lower()
            t = at(m.start())
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
        s0, s1 = speech[i][:2]
        text = b.get('vo', '')
        at = timer(text, s0, s1, speech[i][2] if len(speech[i]) > 2 else ())
        rel = lambda phrase, at=at, text=text, i=i: round(at(index_of(text, phrase)) - beat_starts[i], 3)
        _resolve_beat(b, rel)
        for sh in b.get('shots', []):
            # inside a shot, phrases resolve relative to the shot's start, and plain numbers already are
            sh['_t'] = t0 = round(rel(sh['at']) + sh.pop('lag', 0), 3)   # 'lag' nudges the cut (keep cuts >= ~2s)
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
            for lst in (c.get('moves') or [], c.get('cam') or [], c.get('tags') or []):
                for m in lst:
                    if 'at' in m:
                        m['t'] = round(max(0, rel(m.pop('at')) + m.pop('lag', 0) - base), 3)
            for pl in c.get('players') or []:
                if 'nameAt' in pl:
                    pl['nameT'] = round(max(0, rel(pl.pop('nameAt')) - base), 3)
        if c.get('type') == 'lineup' and isinstance(c.get('empty'), dict) and 'at' in c['empty']:
            c['empty']['t'] = round(max(0, rel(c['empty'].pop('at')) + c['empty'].pop('lag', 0) - base), 3)
        if c.get('type') == 'odds' and isinstance(c.get('extra'), dict) and 'at' in c['extra']:
            c['extra']['t'] = round(max(0, rel(c['extra'].pop('at')) + c['extra'].pop('lag', 0) - base), 3)
        if c.get('type') == 'photofinish' and isinstance(c.get('gapAt'), str):
            c['gapT'] = round(max(0, rel(c.pop('gapAt')) + c.pop('gapLag', 0) - base), 3)
        if c.get('type') in ('whiteboard', 'toytable', 'toyresults', 'toydoors', 'ruler', 'lineup', 'career', 'fates', 'trapdoor', 'divisions', 'ladder', 'timeline', 'sinking', 'crown', 'seesaw', 'climb'):
            for lst in (c.get('lines') or [], c.get('zones') or [], c.get('moves') or [], c.get('items') or [], c.get('doors') or [], c.get('markers') or [], c.get('events') or [], c.get('steps') or [], [c['bracket']] if isinstance(c.get('bracket'), dict) else []):
                for it in lst:
                    if 'at' in it:
                        it['t'] = round(max(0, rel(it.pop('at')) + it.pop('lag', 0) - base), 3)
                    if isinstance(it.get('warnAt'), str):
                        it['warnT'] = round(max(0, rel(it.pop('warnAt')) - base), 3)
                    if isinstance(it.get('shut'), str):
                        it['shut'] = round(max(0, rel(it['shut']) - base), 3)
                    if isinstance(it.get('circle'), dict) and 'at' in it['circle']:
                        it['circle']['t'] = round(max(0, rel(it['circle'].pop('at')) - base), 3)
            if isinstance(c.get('teamAt'), str):
                c['teamAt'] = round(max(0, rel(c['teamAt']) - base), 3)
        if c.get('type') == 'form':
            for key, out in (('winAt', 'winT'), ('bracketAt', 'bracketT'), ('nextAt', 'nextT')):
                if isinstance(c.get(key), str):
                    c[out] = round(max(0, rel(c.pop(key)) + c.pop(key[:-2] + 'Lag', 0) - base), 3)
        if c.get('type') == 'crossoff' and isinstance(c.get('crossAt'), str):
            c['crossT'] = round(max(0, rel(c.pop('crossAt')) + c.pop('crossLag', 0) - base), 3)
        if c.get('type') == 'gauge' and isinstance(c.get('settleAt'), str):
            c['settleT'] = round(max(0, rel(c.pop('settleAt')) + c.pop('settleLag', 0) - base), 3)
        if c.get('type') == 'shirtflip' and isinstance(c.get('flipAt'), str):
            c['flipT'] = round(max(0, rel(c.pop('flipAt')) + c.pop('flipLag', 0) - base), 3)
        if c.get('type') == 'drawpot' and isinstance(c.get('pickAt'), str):
            c['pickT'] = round(max(0, rel(c.pop('pickAt')) + c.pop('pickLag', 0) - base), 3)
        if c.get('type') == 'streak' and isinstance(c.get('breakAt'), str):
            c['breakT'] = round(max(0, rel(c.pop('breakAt')) + c.pop('breakLag', 0) - base), 3)
        if c.get('type') == 'scorebug' and isinstance(c.get('goalAt'), str):
            c['goalT'] = round(max(0, rel(c.pop('goalAt')) + c.pop('goalLag', 0) - base), 3)
        if c.get('type') == 'stopwatch' and isinstance(c.get('lockAt'), str):
            c['lockT'] = round(max(0.4, rel(c.pop('lockAt')) + c.pop('lockLag', 0) - base), 3)
        for typ, key, out in (('simrun', 'stampAt', 'stampT'), ('simrun', 'countAt', 'countT'), ('simhud', 'countAt', 'countT'), ('odds', 'litAt', 'litT'), ('pace', 'gapAt', 'gapT'), ('subboard', 'swapAt', 'swapT'),
                                ('pledge', 'likeAt', 'likeT'), ('pledge', 'shortAt', 'shortT'), ('pledge', 'resultAt', 'resultT')):
            if c.get('type') == typ and isinstance(c.get(key), str):
                c[out] = round(max(0, rel(c.pop(key)) + c.pop(key[:-2] + 'Lag', 0) - base), 3)
        if c.get('type') == 'pentrack':
            for it in c.get('items') or []:
                if 'at' in it:
                    it['t'] = round(max(0, rel(it.pop('at')) + it.pop('lag', 0) - base), 3)
        if c.get('type') == 'varcheck':
            for st in c.get('steps') or []:
                if 'at' in st:
                    st['t'] = round(max(0, rel(st.pop('at')) + st.pop('lag', 0) - base), 3)
            vd = c.get('verdict')
            if isinstance(vd, dict) and 'at' in vd:
                vd['t'] = round(max(0, rel(vd.pop('at')) + vd.pop('lag', 0) - base), 3)
        if c.get('type') == 'pace':
            for pin in c.get('pins') or []:
                if 'at' in pin:
                    pin['t'] = round(max(0, rel(pin.pop('at')) + pin.pop('lag', 0) - base), 3)
        if c.get('type') == 'coin' and isinstance(c.get('landAt'), str):
            c['landT'] = round(max(0, rel(c.pop('landAt')) + c.pop('landLag', 0) - base), 3)
        if c.get('type') == 'table' and isinstance(c.get('moveAt'), str):
            c['moveT'] = round(max(0, rel(c.pop('moveAt')) + c.pop('moveLag', 0) - base), 3)
        if c.get('type') in ('xg', 'swing', 'tally'):
            for it in c.get('items') or c.get('rows') or []:
                if 'at' in it:
                    it['t'] = round(max(0, rel(it.pop('at')) + it.pop('lag', 0) - base), 3)
        if c.get('type') in ('shelf', 'tape'):
            for it in c.get('items') or c.get('rows') or []:
                if 'at' in it:
                    it['t'] = round(max(0, rel(it.pop('at')) + it.pop('lag', 0) - base), 3)
            for key, out in (('emptyAt', 'emptyT'), ('captionAt', 'captionT')):
                if isinstance(c.get(key), str):
                    c[out] = round(max(0, rel(c.pop(key)) - base), 3)
        if c.get('type') in ('tally', 'chalk', 'tickets') and isinstance(c.get('newAt'), str):
            c['newT'] = round(max(0, rel(c.pop('newAt')) + c.pop('newLag', 0) - base), 3)
        if c.get('type') == 'ball' and isinstance(c.get('untilAt'), str):
            c['until'] = round(max(0, rel(c.pop('untilAt')) + c.pop('untilLag', 0) - base), 3)
        if c.get('type') == 'photo' and isinstance(c.get('ripAt'), str):
            c['ripT'] = round(max(0, rel(c.pop('ripAt')) + c.pop('ripLag', 0) - base), 3)
        if isinstance(c.get('hideAt'), str):
            c['hideT'] = round(max(0, rel(c.pop('hideAt')) + c.pop('hideLag', 0) - base), 3)
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
            p['delay'] = round(rel(p.pop('at')) + p.pop('lag', 0), 3)
        if 'swapAt' in p:
            p['swapDelay'] = round(rel(p.pop('swapAt')) + p.pop('swapLag', 0), 3)
        if 'labelAt' in p:
            p['labelDelay'] = rel(p.pop('labelAt'))
        if 'labelUntilAt' in p:
            p['labelUntil'] = round(rel(p.pop('labelUntilAt')) + p.pop('labelUntilLag', 0), 3)
        if 'tagAt' in p:
            p['tagDelay'] = rel(p.pop('tagAt'))
        for h in p.get('hops') or []:  # a jump on a word (e.g. a header)
            if 'at' in h:
                h['t'] = round(rel(h.pop('at')) + h.pop('lag', 0), 3)
        if 'actionAt' in p:  # e.g. the kick starts so the strike lands on the word: use "lag" to shift
            p['actionDelay'] = round(rel(p.pop('actionAt')) + p.pop('actionLag', 0), 3)
        for a in p.get('actions') or []:  # several actions on one player (a keeper's lunges, dive and get-up): each can start on a word
            if 'at' in a:
                a['delay'] = round(rel(a.pop('at')) + a.pop('lag', 0), 3)
        if 'turnAt' in p:  # he turns to face the camera on a word (a scorer wheeling away)
            p['frontT'] = round(rel(p.pop('turnAt')) + p.pop('turnLag', 0) - p.get('delay', 0), 3)
        for key, out in (('vanishAt', 'vanishDelay'), ('appearAt', 'appearDelay')):  # the player breaks into pixels / builds back up on a word
            if key in p:
                p[out] = round(rel(p.pop(key)) + p.pop(key[:-2] + 'Lag', 0), 3)
    if isinstance(b.get('split'), dict):
        sp = b['split']
        if isinstance(sp.get('at'), str):
            sp['t'] = round(rel(sp.pop('at')) + sp.pop('lag', 0), 3)
        for p in sp.get('players') or []:
            if 'at' in p:
                p['delay'] = round(rel(p.pop('at')) + p.pop('lag', 0), 3)
            if 'labelAt' in p:
                p['labelDelay'] = rel(p.pop('labelAt'))
            if 'actionAt' in p:
                p['actionDelay'] = round(rel(p.pop('actionAt')) + p.pop('actionLag', 0), 3)
    if isinstance(b.get('confettiAt'), str):
        b['confettiDelay'] = round(rel(b.pop('confettiAt')), 3)
    if isinstance(b.get('freezeAt'), str):
        b['freeze'] = round(rel(b.pop('freezeAt')) + b.pop('freezeLag', 0), 3)
    ct = b.get('camTrack')
    if isinstance(ct, dict) and isinstance(ct.get('to'), dict) and 'at' in ct['to']:  # the chase camera swings to its second framing on a word
        ct['to']['t'] = round(rel(ct['to'].pop('at')) + ct['to'].pop('lag', 0), 3)
    for key in ('punch', 'shake', 'speedlines', 'glitch'):
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
        if sh.get('keepTimes'):   # a replay shot keeps its own action timeline (with timeShift), so don't shift it
            nb.pop('keepTimes', None)
        if 'accent' in prev and 'accent' not in sh and 'headline' not in sh:  # same headline keeps its accent
            nb['accent'] = prev['accent']
        parts.append(nb)
        prev = nb
    return parts
