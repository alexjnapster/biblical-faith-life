"""Build the public MCP edition from maintained skills and exported portal metadata."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
from build_release import ROOT


def build_public(output):
    templates = ROOT / 'tools/public_submission'
    manifest = json.loads((templates / 'plugin.json').read_text())
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        plugin = Path(temp) / 'plugin'
        shutil.copytree(ROOT / 'plugins/chatgpt/biblical-faith-life', plugin,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        for name in ['plugin.json', 'mcp.json']:
            shutil.copy2(templates / name, plugin / name)
        fallback = json.loads((plugin / '.codex-plugin/plugin.json').read_text())
        for key in ['name', 'version', 'description', 'author', 'license']:
            fallback[key] = manifest[key]
        fallback['interface'] = manifest['extensions']['com.openai']['interface']
        fallback['mcpServers'] = './.mcp.json'
        (plugin / '.codex-plugin/plugin.json').write_text(json.dumps(fallback, ensure_ascii=False, indent=2)+'\n')
        # The portable and compatibility formats describe the same existing server.
        servers = json.loads((templates / 'mcp.json').read_text())['mcpServers']
        (plugin / '.mcp.json').write_text(json.dumps({'mcpServers': {k: {'url': v['url']} for k, v in servers.items()}}, indent=2)+'\n')
        core = plugin / 'skills/biblical-faith-life'
        with (core / 'SKILL.md').open('a') as stream:
            stream.write('\n'+(templates / 'hosted-skill-appendix.md').read_text())
        shutil.copy2(templates / 'HOSTED_RESEARCH.md', core / 'references/HOSTED_RESEARCH.md')
        (plugin / 'README.md').write_text(
            '# Церква Христова — public-source edition\n\n'+
            manifest['extensions']['com.openai']['interface']['longDescription']+'\n\n'+
            'Version '+manifest['version']+'. Four anonymous, read-only source tools. '+
            'The optional local tools require a code-capable host; no credentials are bundled. '+
            'This candidate is not approval or publication. Update the existing public MCP listing; '+
            'check its active review before uploading. Website, privacy, terms and support are in the listing metadata.\n')
        skills = list((plugin / 'skills').glob('*/SKILL.md'))
        if len(skills) != 54:
            raise ValueError('Expected all 54 skills')
        for row in json.loads((plugin / 'SOURCE_MANIFEST.json').read_text()):
            if hashlib.sha256((core / 'references' / row['file']).read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Governing source changed: '+row['file'])
        path = output / ('biblical-faith-life-public-sources-'+manifest['version']+'.zip')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(plugin.rglob('*')):
                if p.is_file():
                    if p.is_symlink():
                        raise ValueError('Release symlink')
                    info = zipfile.ZipInfo(p.relative_to(plugin).as_posix(), (2026, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    z.writestr(info, p.read_bytes())
        return {'path': str(path), 'version': manifest['version'], 'skills': len(skills),
                'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_public(args.output), indent=2))
