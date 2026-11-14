"""Measure answer length with a real counter; never trust a model's own word-count claim.

whitespace: str.split() tokens, the owner's measurement convention.
lexical: tokens containing at least one letter or digit (drops markdown bullets, '#', '—').
body: the text before a trailing notes/sources block (a final '---' rule or a heading/bold label such as
'Джерела', 'Sources', 'Обмеження', 'Примітки'). The cut is reported so a reviewer can check it.
"""
from pathlib import Path
import json, re, sys

TRAILER = re.compile(r'^(?:-{3,}\s*$|(?:#+\s*|\*\*)?(?:Джерела|Источники|Sources|References|Обмеження|Ограничения|Limitations|Примітк|Примечани|Notes|Перевірка|Verification)\b)', re.I | re.M)

def counts(text):
    tokens = text.split()
    return {'whitespace': len(tokens), 'lexical': sum(1 for t in tokens if re.search(r'\w', t))}

def measure(text):
    cut = None
    for m in TRAILER.finditer(text):
        if m.start() > len(text) * 0.5:  # only a trailing block, never the opening half
            cut = m.start(); break
    body = text[:cut] if cut is not None else text
    return {'full': counts(text), 'body': counts(body), 'body_cut_at_char': cut,
            'body_cut_line': text[cut:].splitlines()[0][:80] if cut is not None else None}

def within(n, lo, hi):
    return lo <= n <= hi

if __name__ == '__main__':
    for path in sys.argv[1:]:
        print(json.dumps({'path': path, **measure(Path(path).read_text())}, ensure_ascii=False))
