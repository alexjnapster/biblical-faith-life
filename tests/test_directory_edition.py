"""The skills-only directory edition must stay generated, inert and complete."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FULL = ROOT/'plugins/claude/biblical-faith-life'
EDITION = ROOT/'plugins/claude-directory/biblical-faith-life'
spec = importlib.util.spec_from_file_location('build_directory_edition', ROOT/'tools/build_directory_edition.py')
BUILD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BUILD)


class DirectoryEditionTests(unittest.TestCase):
    def test_committed_edition_matches_generator(self):
        self.assertEqual(BUILD.actual(), BUILD.expected())

    def test_contains_only_inert_document_types(self):
        for path in EDITION.rglob('*'):
            if path.is_file():
                self.assertFalse(path.is_symlink())
                self.assertTrue(path.suffix in {'.md', '.json', '.png'} or path.name == 'LICENSE', str(path))
                self.assertLess(path.stat().st_size, 5*1024*1024)
                if path.suffix != '.png':
                    self.assertLess(path.stat().st_size, 256*1024, str(path))
                    self.assertFalse(path.read_bytes().startswith(b'#!'))
        self.assertEqual(list(EDITION.rglob('scripts')), [])

    def test_manifest_declares_nothing_executable_or_configurable(self):
        manifest = json.loads((EDITION/'.claude-plugin/plugin.json').read_text())
        full = json.loads((FULL/'.claude-plugin/plugin.json').read_text())
        for key in ('mcpServers', 'userConfig', 'hooks', 'lspServers', 'commands', 'agents'):
            self.assertNotIn(key, manifest)
        self.assertEqual(manifest['name'], full['name'])
        self.assertEqual(manifest['version'], full['version'])
        self.assertTrue((EDITION/manifest['icon']).is_file())

    def test_all_skills_and_governing_sources_are_byte_identical(self):
        skills = sorted(p.parent.name for p in (EDITION/'skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 54)
        for slug in skills:
            self.assertEqual((EDITION/'skills'/slug/'SKILL.md').read_bytes(), (FULL/'skills'/slug/'SKILL.md').read_bytes())
        for row in json.loads((EDITION/'SOURCE_MANIFEST.json').read_text()):
            raw = (EDITION/'skills/biblical-faith-life/references'/row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])

    def test_every_skill_link_resolves_inside_the_edition(self):
        for f in (EDITION/'skills').glob('*/SKILL.md'):
            for link in re.findall(r'\]\(([^)\n]+)\)', f.read_text()):
                if ':' in link:
                    continue
                target = (EDITION/link.removeprefix('${CLAUDE_PLUGIN_ROOT}/') if link.startswith('${CLAUDE_PLUGIN_ROOT}/') else f.parent/link).resolve()
                self.assertTrue(target.is_relative_to(EDITION.resolve()), str(f)+':'+link)
                self.assertTrue(target.is_file(), str(f)+':'+link)

    def test_edition_docs_do_not_promise_tools_or_ask_for_credentials(self):
        readme = (EDITION/'README.md').read_text()
        self.assertGreater(len(readme.split()), 40)
        self.assertIn('runs no code', readme)
        host = (EDITION/'CLAUDE_HOST.md').read_text()
        self.assertIn('No `biblical-faith-life` MCP tools exist in this edition', host)
        for name in ('README.md', 'CLAUDE_HOST.md', 'MCP_RUNTIME.md'):
            self.assertNotIn('church_ua_key', (EDITION/name).read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
