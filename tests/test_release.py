"""Cross-platform preservation and actual evidence-validator regression checks."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHAT = ROOT / 'plugins/chatgpt/biblical-faith-life'
BASE = json.loads((ROOT / 'tests/fixtures/chatgpt7-preservation.json').read_text())


class ReleaseTests(unittest.TestCase):
    def test_chatgpt_preserves_every_skill_with_only_reference_rewrites(self):
        self.assertEqual({p.parent.name for p in (CHAT/'skills').glob('*/SKILL.md')}, set(BASE['skills']))
        rewired = {Path(r['old_path']).parts[1] for r in BASE['relocations']}
        for slug, baseline in BASE['skills'].items():
            if slug in rewired:
                baseline = baseline.replace('(references/', '(../biblical-faith-life/references/').replace("All filenames in routing resolve in this skill's references directory.", 'All filenames in routing resolve in ../biblical-faith-life/references inside this plugin.')
            baseline = baseline.replace('Each skill bundles the complete unchanged original sources; no other skill installation or external app is required.', 'This plugin bundles the complete unchanged original sources once in its shared reference library; no separate plugin installation or external app is required.')
            text = (CHAT/'skills'/slug/'SKILL.md').read_text()
            # The quality upgrade appends exactly one section; everything before it must stay byte-identical.
            appended = re.search(r'\n\n\n## Verified answer production\n.*\Z', text, re.S)
            self.assertIsNotNone(appended, slug)
            self.assertIn('references/ANSWER_PRODUCTION.md)', appended.group(0), slug)  # link targets are checked below
            self.assertEqual(text[:appended.start()] + '\n', baseline, slug)

    def test_chatgpt_removed_only_identical_references(self):
        for row in BASE['relocations']:
            self.assertFalse((CHAT/row['old_path']).exists())
            self.assertEqual(hashlib.sha256((CHAT/row['canonical_path']).read_bytes()).hexdigest(), row['sha256'])

    def test_both_packages_preserve_all_governing_bytes_and_skill_links(self):
        pinned = json.loads((ROOT/'tests/fixtures/claude3-preservation.json').read_text())
        for platform in ['chatgpt', 'claude']:
            plugin = ROOT/'plugins'/platform/'biblical-faith-life'
            for row in pinned['governing_sources']:
                raw = (plugin/'skills/biblical-faith-life/references'/row['file']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            for f in (plugin/'skills').glob('*/SKILL.md'):
                for link in re.findall(r'\]\(([^)\n]+)\)', f.read_text()):
                    if ':' in link:
                        continue
                    target = (plugin/link.removeprefix('${CLAUDE_PLUGIN_ROOT}/') if link.startswith('${CLAUDE_PLUGIN_ROOT}/') else f.parent/link).resolve()
                    self.assertTrue(target.is_relative_to(plugin.resolve()), str(f)+':'+link)
                    self.assertTrue(target.is_file(), str(f)+':'+link)

    def test_review_identity_validation_in_both_local_runtimes(self):
        fixture = json.loads((ROOT/'hosted-research/audit-regression-fixtures.json').read_text())[0]['artifact']
        for platform in ['chatgpt', 'claude']:
            plugin = ROOT/'plugins'/platform/'biblical-faith-life'
            file = plugin/'skills/biblical-faith-life/scripts/bfl/engines.py'
            spec = importlib.util.spec_from_file_location('engine_'+platform, file)
            engine = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(engine)
            for reviewer in [True, 42, {}, [], '   ', ' '+fixture['author']+' ']:
                a = copy.deepcopy(fixture)
                a['review']['reviewer'] = reviewer
                a['review']['artifact_sha256'] = engine.content_hash(a)
                result = engine.validate(a, plugin/'skills/biblical-faith-life')
                self.assertNotEqual(result['status'], 'pass')
                self.assertIn('independent_review_pending', {f['code'] for f in result['findings']})


if __name__ == '__main__':
    unittest.main(verbosity=2)
