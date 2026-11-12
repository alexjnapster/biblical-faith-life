"""Generate the skills-only Claude directory edition from the full Claude package.

The plugin directory accepts local MCP servers, scripts and non-document files
only from Verified organizations. This edition therefore carries the same 54
skills and the same byte-identical governing references, and nothing that
executes: no MCP server, no Python, no plugin options, no credential.

Run `python3 tools/build_directory_edition.py` to regenerate, or with `--check`
to verify that the committed edition matches what this tool would produce.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
FULL = ROOT/'plugins/claude/biblical-faith-life'
EDITION = ROOT/'plugins/claude-directory/biblical-faith-life'
TEMPLATES = ROOT/'tools/directory_edition'
ALLOWED = {'.md', '.json', '.png'}
COPIED_ROOT_FILES = ['LICENSE', 'SOURCE_MANIFEST.json', 'REFERENCE_RELOCATION.json', 'assets/icon.png']
TEMPLATE_FILES = ['README.md', 'CLAUDE_HOST.md', 'MCP_RUNTIME.md']
DESCRIPTION = ('Bible study, sermons and teaching grounded in the preserved Church of Christ v9 doctrinal framework. '
               '54 skills covering exegesis, sermons, lessons, articles, research review, pastoral care and ministry writing. '
               'Ukrainian is the default; English and Russian are supported. Intended for adult teachers, ministers and authors. '
               'Skills-only edition: it runs no code, starts no server, stores nothing and needs no configuration. '
               'AI output needs review and does not guarantee theological, historical or factual accuracy.')


def expected():
    """Return {relative path: bytes} for the whole edition."""
    files = {}
    for skill in sorted((FULL/'skills').glob('*/SKILL.md')):
        files[skill.relative_to(FULL).as_posix()] = skill.read_bytes()
    for ref in sorted((FULL/'skills/biblical-faith-life/references').rglob('*')):
        if ref.is_file():
            if ref.suffix not in ALLOWED:
                raise ValueError('Unexpected reference type: '+str(ref))
            files[ref.relative_to(FULL).as_posix()] = ref.read_bytes()
    for name in COPIED_ROOT_FILES:
        files[name] = (FULL/name).read_bytes()
    for name in TEMPLATE_FILES:
        files[name] = (TEMPLATES/name).read_bytes()
    manifest = json.loads((FULL/'.claude-plugin/plugin.json').read_text(encoding='utf-8'))
    for key in ('mcpServers', 'userConfig'):
        manifest.pop(key)
    manifest['description'] = DESCRIPTION
    files['.claude-plugin/plugin.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    return files


def actual():
    if not EDITION.is_dir():
        return {}
    return {p.relative_to(EDITION).as_posix(): p.read_bytes() for p in sorted(EDITION.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify the committed edition instead of writing it')
    args = parser.parse_args()
    want = expected()
    if args.check:
        have = actual()
        problems = sorted(set(want) ^ set(have)) + sorted(k for k in set(want) & set(have) if want[k] != have[k])
        if problems:
            print('Directory edition is out of date: '+', '.join(problems[:20]), file=sys.stderr)
            return 1
        print(json.dumps({'files': len(want), 'bytes': sum(map(len, want.values())), 'status': 'in sync'}))
        return 0
    if EDITION.exists():
        shutil.rmtree(EDITION)
    for name, data in want.items():
        target = EDITION/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({'files': len(want), 'bytes': sum(map(len, want.values())), 'status': 'written'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
