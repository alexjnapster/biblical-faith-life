"""Integrity and evaluation-coverage checks; these do NOT grade generated prose."""
from pathlib import Path
import unittest, json, re, hashlib
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent
BASE=WORK/'baseline'
CANDIDATE=WORK/'workspace-candidate'
MARK='\n\n## Verified answer production\n'
EDITORIAL=(ROOT/'evaluation/EDITORIAL_RULES_CLAUDE.md').read_text()

class QualityUpgradeTests(unittest.TestCase):
    def test_exactly_three_distinct_cases_for_every_skill(self):
        cases=json.loads((ROOT/'evaluation/cases.json').read_text())['cases']
        slugs={p.parent.name for p in (BASE/'skills').glob('*/SKILL.md')}
        self.assertEqual(len(slugs),54);self.assertEqual(len(cases),162)
        self.assertEqual(len({c['id'] for c in cases}),162)
        self.assertEqual({c['skill'] for c in cases},slugs)
        for slug in slugs:
            rows=[c for c in cases if c['skill']==slug]
            self.assertEqual({r['mode'] for r in rows},{'ordinary','demanding','misleading'})
            self.assertEqual(len({r['prompt'] for r in rows}),3)
            self.assertTrue(all(r['status']=='not_run' for r in rows))

    def test_all_three_packages_have_matching_quality_rules_and_54_profiles(self):
        roots=[CANDIDATE,ROOT/'plugins/chatgpt/biblical-faith-life',ROOT/'plugins/claude/biblical-faith-life']
        workflow=(ROOT/'evaluation/QUALITY_WORKFLOW.md').read_bytes()
        profiles=json.loads((ROOT/'evaluation/skill_acceptance.json').read_text())
        for package in roots:
            actual=(package/'skills/biblical-faith-life/references/ANSWER_PRODUCTION.md').read_bytes()
            if package.name=='biblical-faith-life' and package.parent.name=='claude':
                # Claude-only editorial repair from the 31 Oct 2026 answer-quality evaluation; the rest stays shared.
                self.assertIn(EDITORIAL,actual.decode())
                actual=actual.decode().replace(EDITORIAL,'').encode()
            self.assertEqual(actual,workflow)
            skills=list((package/'skills').glob('*/SKILL.md'));self.assertEqual(len(skills),54)
            for p in skills:
                text=p.read_text();self.assertEqual(text.count(MARK),1)
                self.assertIn(profiles[p.parent.name],text)
                for link in re.findall(r'\]\(([^)\n]+)\)',text.split(MARK)[1]):
                    target=(p.parent/link).resolve()
                    self.assertTrue(target.is_relative_to(package.resolve()))
                    self.assertTrue(target.is_file())

    def test_claude_marketplace_version_matches_candidate(self):
        marketplace=json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
        manifest=json.loads((ROOT/'plugins/claude/biblical-faith-life/.claude-plugin/plugin.json').read_text())
        self.assertEqual(marketplace['plugins'][0]['version'],manifest['version'])

    def test_workspace_retains_every_file_except_explicit_changes(self):
        old={p.relative_to(BASE).as_posix():p for p in BASE.rglob('*') if p.is_file()}
        new={p.relative_to(CANDIDATE).as_posix():p for p in CANDIDATE.rglob('*') if p.is_file()}
        self.assertFalse(set(old)-set(new))
        self.assertEqual(set(new)-set(old),{'skills/biblical-faith-life/references/ANSWER_PRODUCTION.md'})
        for path,p in old.items():
            if path.endswith('/SKILL.md'):
                self.assertEqual(new[path].read_text().split(MARK)[0],p.read_text())
            elif path not in {'plugin.json','.codex-plugin/plugin.json'}:
                self.assertEqual(new[path].read_bytes(),p.read_bytes(),path)

    def test_workspace_identity_scope_prompts_and_integrations_preserved(self):
        for rel in ['plugin.json','.codex-plugin/plugin.json']:
            before=json.loads((BASE/rel).read_text());after=json.loads((CANDIDATE/rel).read_text())
            self.assertEqual(before['name'],after['name']);self.assertEqual(after['version'],'2.1.0-rc.5')
            if rel=='plugin.json':
                b=before['extensions']['com.openai']['interface'];a=after['extensions']['com.openai']['interface']
            else:b=before['interface'];a=after['interface']
            self.assertEqual(a['defaultPrompt'],b['defaultPrompt'])
            after['version']=before['version'];a['longDescription']=b['longDescription']
            self.assertEqual(after,before)

    def test_all_workspace_governing_copies_remain_byte_identical(self):
        manifest=json.loads((BASE/'SOURCE_MANIFEST.json').read_text())
        self.assertEqual(len(manifest),12)
        for row in manifest:
            copies=list(CANDIDATE.glob('skills/*/references/'+row['file']))
            self.assertGreaterEqual(len(copies),1)
            for p in copies:
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['sha256'])

    def test_rubric_cannot_turn_unreviewed_generation_into_pass(self):
        rubric=json.loads((ROOT/'evaluation/rubric.json').read_text())
        self.assertEqual(rubric['missing_review'],'pending')
        self.assertIn('fabricated_source_or_execution',rubric['critical_failures'])
        self.assertIn('Every applicable dimension >=3',rubric['pass_rule'])
        self.assertEqual(len(rubric['dimensions']),7)

if __name__=='__main__':unittest.main(verbosity=2)
