#!/usr/bin/env python3
"""Check a video's YouTube post and TikTok / Instagram captions against the platform rules in CLAUDE.md (step 5).

  python3 engine/posts.py videos/<slug>

Reads videos/<slug>/youtube.md and social.md and prints every rule each one breaks (exit code 1 if any).
Rules researched Nov 2026; re-check them when a platform changes its limits:
  - YouTube: 3 title options, each <= 60 characters with the hook and the searchable subject in the first 40 (the feed cuts long titles),
    no hashtags in the title; description opens with the hook and the subject's name; exactly 3 hashtags at the end (YouTube shows up to
    3 above the title); tags fill 490-500 by YouTube's count (user rule) and lead with names and common misspellings (YouTube: tags mostly
    help with misspellings); a pinned comment that asks a question.
  - TikTok: 3-5 hashtags (more dilutes); the caption opens with the searchable phrase; about 100-300 characters before the hashtags.
  - Instagram: at most 5 hashtags (Instagram's cap since Dec 2025: more are blocked); hook + keywords in the first 125 characters (shown
    before "more"); a question; a send/share prompt (DM shares are Instagram's strongest reach signal); "Follow @theo6k".
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import tags_count


def blocks(text, head):
    m = re.search(r'## ' + head + r'.*?\n(.*?)(?=\n## |\Z)', text, re.S)
    return re.findall(r'```\n(.*?)\n```', m.group(1), re.S) if m else []


def section(text, head):
    m = re.search(r'## ' + head + r'.*?\n(.*?)(?=\n## |\Z)', text, re.S)
    return m.group(1).strip() if m else ''


def hashtags(s):
    return re.findall(r'(?<![\w&])#\w+', s)


def check(folder):
    f = Path(folder)
    bad = []
    yt = (f / 'youtube.md').read_text() if (f / 'youtube.md').exists() else ''
    so = (f / 'social.md').read_text() if (f / 'social.md').exists() else ''
    if not yt:
        bad.append('youtube.md missing')
    else:
        titles = blocks(yt, 'Title')
        if len(titles) != 3:
            bad.append(f'YouTube: {len(titles)} title options (want 3, each in its own code block)')
        for t in titles:
            if len(t) > 60:
                bad.append(f'YouTube title over 60 characters ({len(t)}): {t}')
            if hashtags(t):
                bad.append(f'YouTube title has a hashtag (put #Shorts in the description): {t}')
        desc = '\n'.join(blocks(yt, 'Description')) or section(yt, 'Description')
        tags_desc = hashtags(desc)
        if len(tags_desc) != 3:
            bad.append(f'YouTube description has {len(tags_desc)} hashtags (want exactly 3; YouTube shows up to 3 above the title)')
        if 'Follow for more football stories in under a minute.' not in desc:
            bad.append('YouTube description is missing "Follow for more football stories in under a minute."')
        if '?' not in desc:
            bad.append('YouTube description has no question for the comments')
        tag_text = (blocks(yt, 'Tags') or [section(yt, 'Tags').split('\n')[0]])[0]
        tags = [t.strip() for t in tag_text.split(',') if t.strip()]
        n = tags_count(tags)
        if not 490 <= n <= 500:
            bad.append(f'YouTube tags count {n} by YouTube\'s rules (want 490-500)')
        pin = '\n'.join(blocks(yt, 'Pinned comment')) or section(yt, 'Pinned comment')
        if '?' not in pin:
            bad.append('YouTube pinned comment asks no question')
    if not so:
        bad.append('social.md missing')
    else:
        tk = '\n'.join(blocks(so, 'TikTok'))
        h = hashtags(tk)
        if not 3 <= len(h) <= 5:
            bad.append(f'TikTok caption has {len(h)} hashtags (want 3-5)')
        body = re.sub(r'(?<![\w&])#\w+', '', tk).strip()
        if not 100 <= len(body) <= 300:
            bad.append(f'TikTok caption is {len(body)} characters before the hashtags (aim for 100-300)')
        if '?' not in tk:
            bad.append('TikTok caption asks no question')
        ig = '\n'.join(blocks(so, 'Instagram'))
        h = hashtags(ig)
        if len(h) > 5:
            bad.append(f'Instagram caption has {len(h)} hashtags (Instagram allows 5 at most since Dec 2025)')
        if len(h) < 3:
            bad.append(f'Instagram caption has {len(h)} hashtags (use 3-5)')
        if len(ig) > 2200:
            bad.append(f'Instagram caption is {len(ig)} characters (limit 2,200)')
        if '?' not in ig:
            bad.append('Instagram caption asks no question')
        if not re.search(r'\b(send|share|tag)\b', ig, re.I):
            bad.append('Instagram caption has no send/share prompt (DM shares are the strongest reach signal)')
        if 'Follow @theo6k' not in ig:
            bad.append('Instagram caption is missing "Follow @theo6k"')
    for b in bad:
        print('  -', b)
    print('POSTS:', 'all rules met' if not bad else f'{len(bad)} problem(s)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(check(sys.argv[1]))
