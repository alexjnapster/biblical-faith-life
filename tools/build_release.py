"""Build reproducible source candidates; this never uploads or submits them."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build(platform, output):
    plugin = ROOT/'plugins'/platform/'biblical-faith-life'
    manifest = plugin/('plugin.json' if platform == 'chatgpt' else '.claude-plugin/plugin.json')
    version = json.loads(manifest.read_text())['version']
    files = sorted(p for p in plugin.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and p.name != '.DS_Store')
    assert len(list((plugin/'skills').glob('*/SKILL.md'))) == 54
    for row in json.loads((plugin/'SOURCE_MANIFEST.json').read_text()):
        assert hashlib.sha256((plugin/'skills/biblical-faith-life/references'/row['file']).read_bytes()).hexdigest() == row['sha256']
    for p in files:
        if p.is_symlink() or p.name == '.env' or p.suffix in {'.sqlite3', '.zip'}:
            raise ValueError('Unexpected release file: '+str(p))
    if platform == 'chatgpt':
        assert not (plugin/'.app.json').exists()
        for p in [plugin/'plugin.json', plugin/'.codex-plugin/plugin.json']:
            m = json.loads(p.read_text())
            assert not m.get('apps') and not m.get('extensions', {}).get('com.openai', {}).get('apps')
    output.mkdir(parents=True, exist_ok=True)
    path = output/f'biblical-faith-life-{platform}-{version}.zip'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(plugin).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, p.read_bytes())
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.endswith('/SKILL.md')]) == 54
    return {'file': path.name, 'version': version, 'files': len(files), 'uncompressed_bytes': sum(p.stat().st_size for p in files), 'zip_bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'status': 'repository candidate; not uploaded, submitted or approved'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to((ROOT/'plugins').resolve()):
        parser.error('Output must be outside plugin source directories')
    report = [build(p, args.output) for p in ['chatgpt', 'claude']]
    (args.output/'release-inventory.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
