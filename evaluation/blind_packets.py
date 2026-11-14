"""Build blinded review packets: same prompt, variants shuffled to X/Y/Z, key written separately."""
from pathlib import Path
import argparse, json, random, hashlib

p = argparse.ArgumentParser()
p.add_argument('--out', required=True); p.add_argument('--packets', required=True)
p.add_argument('--cases', nargs='+', required=True); p.add_argument('--variants', nargs='+', required=True)
p.add_argument('--seed', default='20261031')
a = p.parse_args()
out, dest = Path(a.out), Path(a.packets); dest.mkdir(parents=True, exist_ok=True)
key = {}
for cid in a.cases:
    present = [v for v in a.variants if (out/v/cid/'receipt.json').exists()
               and json.loads((out/v/cid/'receipt.json').read_text())['execution_status'] == 'completed']
    rng = random.Random(a.seed + cid); rng.shuffle(present)
    labels = dict(zip('XYZW', present)); key[cid] = labels
    prompt = (out/present[0]/cid/'prompt.txt').read_text()
    parts = [f'# Case {cid}\n\n## Prompt (identical for every answer)\n\n{prompt}\n']
    for label, v in labels.items():
        r = json.loads((out/v/cid/'receipt.json').read_text()); m = r['measured_words']
        parts.append(f"\n## Answer {label}\n\nMeasured words (script): whole reply {m['full']['whitespace']}, body before trailing notes {m['body']['whitespace']}.\n"
                     f"answer sha256 {r['answer_sha256']}\n\n<answer label=\"{label}\">\n{(out/v/cid/'answer.md').read_text()}\n</answer>\n")
    (dest/f'{cid}.md').write_text(''.join(parts))
(dest.parent/(dest.name + '-KEY.json')).write_text(json.dumps(key, indent=2) + '\n')
print(json.dumps({c: list(k) for c, k in key.items()}))
