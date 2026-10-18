"""Compare the compact package against independently pinned pre-compaction bytes."""
from pathlib import Path
import hashlib
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT/'plugins/claude/biblical-faith-life'
BASE = json.loads((ROOT/'tests/fixtures/claude3-preservation.json').read_text())
REF = PLUGIN/'skills/biblical-faith-life/references'

class ReferenceLayoutTests(unittest.TestCase):
    def test_all_skill_identities_preserved(self):
        self.assertEqual({p.parent.name for p in (PLUGIN/'skills').glob('*/SKILL.md')}, set(BASE['skill_hashes']))

    def test_governing_sources_match_pre_compaction_hashes(self):
        self.assertEqual(len(BASE['governing_sources']),12)
        for row in BASE['governing_sources']:
            raw=(REF/row['file']).read_bytes()
            self.assertEqual(len(raw),row['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            raw.decode('utf-8')

    def test_every_removed_duplicate_has_identical_readable_target(self):
        rows=json.loads((PLUGIN/'REFERENCE_RELOCATION.json').read_text())['relocations']
        self.assertEqual({r['old_path'] for r in rows},set(BASE['relocated_reference_hashes']))
        for row in rows:
            self.assertEqual(row['sha256'],BASE['relocated_reference_hashes'][row['old_path']])
            target=PLUGIN/row['canonical_path']
            self.assertFalse(target.is_symlink())
            self.assertTrue(target.resolve().is_relative_to(REF.resolve()))
            raw=target.read_bytes();raw.decode('utf-8')
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(len(raw),row['bytes'])

    def test_skill_changes_are_only_declared_reference_rewrites(self):
        for slug,digest in BASE['skill_hashes'].items():
            baseline=BASE['skill_texts'][slug]
            self.assertEqual(hashlib.sha256(baseline.encode()).hexdigest(),digest,slug)
            expected=baseline
            if slug in BASE['rewired_skills']:
                expected=expected.replace('(references/','(../biblical-faith-life/references/').replace("All filenames in routing resolve in this skill's references directory.",'All filenames in routing resolve in ../biblical-faith-life/references inside this plugin.')
            if slug in BASE['rewired_skills'] or slug=='biblical-faith-life':
                expected=expected.replace('Each skill bundles the complete unchanged original sources; no other skill installation or external app is required.','This plugin bundles the complete unchanged original sources once in its shared reference library; no separate plugin installation or external app is required.')
            self.assertEqual((PLUGIN/'skills'/slug/'SKILL.md').read_text(),expected,slug)

    def test_all_declared_skill_links_resolve_inside_package(self):
        for f in (PLUGIN/'skills').glob('*/SKILL.md'):
            for link in re.findall(r'\]\(([^)\n]+)\)',f.read_text()):
                if ':' in link:continue
                target=(PLUGIN/link.removeprefix('${CLAUDE_PLUGIN_ROOT}/') if link.startswith('${CLAUDE_PLUGIN_ROOT}/') else f.parent/link).resolve()
                self.assertTrue(target.is_relative_to(PLUGIN.resolve()),str(f)+':'+link)
                self.assertTrue(target.is_file(),str(f)+':'+link)

if __name__=='__main__':unittest.main(verbosity=2)
