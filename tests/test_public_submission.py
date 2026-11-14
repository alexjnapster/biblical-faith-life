"""Verify the complete public MCP candidate, not only its metadata overlay."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
ROOT = Path(__file__).resolve().parents[1]

class PublicSubmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        out = Path(cls.temp.name)
        subprocess.run([sys.executable, str(ROOT/'tools/build_public_submission.py'), '--output', str(out)], check=True, capture_output=True)
        with zipfile.ZipFile(next(out.glob('*.zip'))) as z:
            if z.testzip() is not None: raise ValueError('Corrupt release')
            z.extractall(out/'extracted')
        cls.plugin = out/'extracted'
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_metadata_and_review_materials(self):
        m=json.loads((self.plugin/'plugin.json').read_text()); o=m['extensions']['com.openai']; i=o['interface']
        self.assertEqual(m['name'],'biblical-faith-life-public-sources')
        self.assertLessEqual(len(i['displayName']),30); self.assertLessEqual(len(i['shortDescription']),30)
        self.assertLessEqual(len(i['longDescription']),4000)
        self.assertEqual(len(i['defaultPrompt']),3)
        self.assertEqual(len(set(i['defaultPrompt'])),3)
        for p in i['defaultPrompt']: self.assertLessEqual(len(p),128)
        self.assertEqual(len(o['review']['test_cases']['positive']),5)
        self.assertEqual(len(o['review']['test_cases']['negative']),3)
        for field in ['websiteURL','supportURL','privacyPolicyURL','termsOfServiceURL']:
            self.assertTrue(i[field].startswith('https://'))
        self.assertTrue(o['review']['demo_recording_url'].startswith('https://'))
        fallback=json.loads((self.plugin/'.codex-plugin/plugin.json').read_text())
        self.assertEqual(fallback['interface'], i); self.assertEqual(fallback['version'],m['version'])
    def test_public_server_binding_and_source_integrity(self):
        servers=json.loads((self.plugin/'mcp.json').read_text())['mcpServers']
        self.assertEqual(len(servers),1)
        server=next(iter(servers.values()))
        self.assertNotIn('extensions',server)  # portable 1.0.0 permits no server extensions; existing portal connection is no-auth
        self.assertTrue(server['url'].endswith('/api/public-research/mcp'))
        self.assertNotIn('headers',server)
        for row in json.loads((self.plugin/'SOURCE_MANIFEST.json').read_text()):
            self.assertEqual(hashlib.sha256((self.plugin/'skills/biblical-faith-life/references'/row['file']).read_bytes()).hexdigest(),row['sha256'])
    def test_all_skills_and_local_links(self):
        skills=list((self.plugin/'skills').glob('*/SKILL.md')); self.assertEqual(len(skills),54)
        for f in skills:
            for link in re.findall(r'\]\(([^)\n]+)\)',f.read_text()):
                if ':' in link: continue
                target=(f.parent/link).resolve()
                self.assertTrue(target.is_relative_to(self.plugin.resolve()))
                self.assertTrue(target.is_file(),str(f)+': '+link)
        core=(self.plugin/'skills/biblical-faith-life/SKILL.md').read_text()
        self.assertIn('Hosted research tools',core)
    def test_invalid_reviewer_cannot_pass(self):
        core=self.plugin/'skills/biblical-faith-life'
        spec=importlib.util.spec_from_file_location('submitted_engine',core/'scripts/bfl/engines.py')
        engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
        fixture=json.loads((ROOT/'hosted-research/audit-regression-fixtures.json').read_text())[0]['artifact']
        for reviewer in [True, 42, {}, [], '   ', ' '+fixture['author']+' ']:
            a=json.loads(json.dumps(fixture));a['review']['reviewer']=reviewer
            a['review']['artifact_sha256']=engine.content_hash(a)
            result=engine.validate(a,core)
            self.assertNotEqual(result['status'],'pass')
            self.assertIn('independent_review_pending',{f['code'] for f in result['findings']})
if __name__=='__main__': unittest.main()
