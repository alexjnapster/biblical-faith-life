from pathlib import Path
import importlib.util, unittest, tempfile, json, io, os, hashlib, subprocess, sys, copy

W=Path(__file__).resolve().parents[1]
P=W/'plugins/claude/biblical-faith-life'
spec=importlib.util.spec_from_file_location('bfl_public_mcp',P/'scripts/bfl_mcp.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

class MCPTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.a=M.Adapter(str(self.root),'test-owner')
    def tearDown(self):self.tmp.cleanup()
    def doc(self):return {'title':'Synthetic study','content':'A supplied synthetic evidence document about Luke fifteen.','language':'en','locator':'fixture:local'}
    def test_runtime_identity_matches_package(self):
        version=json.loads((P/'.claude-plugin/plugin.json').read_text())['version']
        self.assertEqual(self.a.call('bfl_status',{})['version'],version)
        r=self.frames([{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}}])
        self.assertEqual(r[0]['result']['serverInfo']['version'],version)
    def test_status_no_secret(self):
        a=M.Adapter(token='synthetic-private-value');r=a.call('bfl_status',{});self.assertFalse(r['church_ua_configured']);self.assertNotIn(a._token,json.dumps(r))
    def test_all_tools_have_strict_schemas_and_annotations(self):
        self.assertEqual(len(M.TOOLS),12)
        for t in M.TOOLS:
            self.assertFalse(t['inputSchema']['additionalProperties'])
            for key in ['readOnlyHint','destructiveHint','openWorldHint']:self.assertIs(type(t['annotations'][key]),bool)
            self.assertLessEqual(len(t['name']),64)
    def test_schema_rejects_unknown_and_wrong_types(self):
        for args in [{'extra':True},[],None]:
            with self.assertRaises(ValueError):self.a.call('bfl_status',args)
        with self.assertRaises(ValueError):self.a.call('bfl_library_search',{'library':'library','query':'x','limit':True})
    def test_missing_workspace(self):
        with self.assertRaises(ValueError):M.Adapter().call('bfl_library_ingest',{'library':'library','document':self.doc()})
    def test_traversal_and_absolute_paths(self):
        for name in ['../escape','x/../../escape',str(self.root/'absolute'),'']:
            with self.assertRaises(ValueError):self.a.path(name)
    def test_symlink_and_hardlink_refusal(self):
        outside=self.root/'outside';outside.mkdir();(self.root/'link').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError):self.a.path('link/file')
        f=self.root/'one';f.write_text('{}');os.link(f,self.root/'two')
        with self.assertRaises(ValueError):self.a.path('two')
    def test_library_ingest_get_search(self):
        r=self.a.call('bfl_library_ingest',{'library':'library','document':self.doc()})
        got=self.a.call('bfl_library_get',{'library':'library','doc_id':r['doc_id']});self.assertEqual(got['content'],self.doc()['content'])
        found=self.a.call('bfl_library_search',{'library':'library','query':'Luke','limit':3});self.assertEqual(len(found['matches']),1)
    def test_library_private_consent(self):
        d=dict(self.doc(),private=True,consent=False)
        with self.assertRaises(PermissionError):self.a.call('bfl_library_ingest',{'library':'private','document':d})
        d['consent']=True;self.assertTrue(self.a.call('bfl_library_ingest',{'library':'private','document':d})['created'])
    def test_library_read_is_readonly(self):
        self.a.call('bfl_library_ingest',{'library':'library','document':self.doc()});p=self.root/'library/library.sqlite3';before=p.read_bytes();mode=p.stat().st_mode
        self.a.call('bfl_library_search',{'library':'library','query':'Luke'});self.assertEqual(p.read_bytes(),before);self.assertEqual(p.stat().st_mode,mode)
    def test_library_owner_boundary(self):
        self.a.call('bfl_library_ingest',{'library':'library','document':self.doc()})
        with self.assertRaises(PermissionError):M.Adapter(str(self.root),'different-owner').call('bfl_library_search',{'library':'library','query':'Luke'})
    def test_missing_read_does_not_create_library(self):
        with self.assertRaises(ValueError):self.a.call('bfl_library_search',{'library':'absent','query':'Luke'})
        self.assertFalse((self.root/'absent').exists())
    def test_workflow_persistence_review_and_invalidation(self):
        self.a.call('bfl_workflow_start',{'workflow':'biblical-research-laboratory','checkpoint':'study.json','stages':['deep-exegesis','interpretation-review']})
        self.a.call('bfl_workflow_record',{'checkpoint':'study.json','stage':'deep-exegesis','content':'Synthetic research fixture.','actor':'author'})
        with self.assertRaises(PermissionError):self.a.call('bfl_workflow_record',{'checkpoint':'study.json','stage':'interpretation-review','content':'Synthetic review fixture.','actor':'author','review':True})
        self.a.call('bfl_workflow_record',{'checkpoint':'study.json','stage':'interpretation-review','content':'Synthetic review fixture.','actor':'reviewer','review':True})
        self.assertEqual(self.a.call('bfl_workflow_status',{'checkpoint':'study.json'})['status'],'recorded')
        self.a.call('bfl_workflow_record',{'checkpoint':'study.json','stage':'deep-exegesis','content':'Changed synthetic research.','actor':'author'})
        self.assertEqual(self.a.call('bfl_workflow_status',{'checkpoint':'study.json'})['status'],'incomplete')
    def test_visual_real_files_and_no_overwrite(self):
        s={'kind':'comparison','language':'en','title':'Synthetic visual','description':'Synthetic acceptance fixture.','items':[{'label':'A','detail':'B','source':'fixture:one','certainty':'uncertain'}]}
        r=self.a.call('bfl_visual_export',{'spec':s,'output_dir':'visuals','formats':['svg','html']});self.assertEqual(r['status'],'created')
        for f in r['files']:self.assertTrue((self.root/f['path']).is_file())
        with self.assertRaises(ValueError):self.a.call('bfl_visual_export',{'spec':s,'output_dir':'visuals'})
    def test_draft_preview_offline(self):
        r=self.a.call('bfl_draft_preview',{'kind':'article','payload':{'title':'Synthetic draft','body':'A synthetic test article.'}});self.assertEqual(r['publication'],'human review required')
    def test_draft_requires_boolean_authorization(self):
        for value in [False,'true',1]:
            with self.assertRaises((ValueError,PermissionError)):self.a.call('bfl_draft_submit',{'kind':'article','payload':{},'review_envelope':{},'authorized_draft':value})
    def test_draft_requires_passing_review_before_key_use(self):
        with self.assertRaises(ValueError):self.a.call('bfl_draft_submit',{'kind':'article','payload':{'title':'Synthetic draft'},'review_envelope':{},'authorized_draft':True})
    def test_draft_journal_prevents_duplicate_after_success(self):
        original=M.validate;M.validate=lambda *args:{'status':'pass'};calls=[]
        class FakeClient:
            def submit(self,*args,**kwargs):calls.append('POST');return {'id':'synthetic-id','kind':'article','readback_verified':False}
            def verify(self,receipt):return dict(receipt,readback_verified=True)
        self.a.origin='https://churches.tools';self.a.client=lambda:FakeClient()
        payload={'title':'Synthetic reviewed draft'};p=M.prepare('article',payload)
        args={'kind':'article','payload':payload,'review_envelope':{'church_ua_request':{'kind':'article','payload_sha256':p['payload_sha256']}},'authorized_draft':True}
        try:
            self.assertTrue(self.a.call('bfl_draft_submit',args)['readback_verified'])
            with self.assertRaises(ValueError):self.a.call('bfl_draft_submit',args)
            self.assertEqual(calls,['POST'])
        finally:M.validate=original
    def test_uncertain_draft_attempt_is_not_retried(self):
        original=M.validate;M.validate=lambda *args:{'status':'pass'};calls=[]
        class FakeClient:
            def submit(self,*args,**kwargs):calls.append('POST');raise TimeoutError()
        self.a.origin='https://churches.tools';self.a.client=lambda:FakeClient()
        payload={'title':'Synthetic ambiguous draft'};p=M.prepare('article',payload)
        args={'kind':'article','payload':payload,'review_envelope':{'church_ua_request':{'kind':'article','payload_sha256':p['payload_sha256']}},'authorized_draft':True}
        try:
            with self.assertRaises(RuntimeError):self.a.call('bfl_draft_submit',args)
            with self.assertRaises(ValueError):self.a.call('bfl_draft_submit',args)
            self.assertEqual(calls,['POST']);self.assertEqual(len(list((self.root/'.bfl/draft-attempts').glob('*.json'))),1)
        finally:M.validate=original
    def test_changed_payload_cannot_reuse_review(self):
        original=M.validate;M.validate=lambda *args:{'status':'pass'}
        try:
            with self.assertRaises(ValueError):self.a.call('bfl_draft_submit',{'kind':'article','payload':{'title':'Synthetic changed draft'},'review_envelope':{'church_ua_request':{'kind':'article','payload_sha256':'wrong'}},'authorized_draft':True})
            self.assertFalse((self.root/'.bfl').exists())
        finally:M.validate=original
    def test_unsubstituted_or_blank_options_mean_unconfigured(self):
        for raw in ['${user_config.workspace}','   ','']:
            a=M.Adapter(raw,'${user_config.owner}','${user_config.church_ua_origin}','${user_config.church_ua_key}');r=a.call('bfl_status',{})
            self.assertFalse(r['workspace_configured']);self.assertFalse(r['workspace_ready']);self.assertFalse(r['church_ua_configured']);self.assertEqual(a.owner,'local-owner')
            with self.assertRaises(ValueError):a.call('bfl_library_ingest',{'library':'library','document':self.doc()})
            with self.assertRaises(ValueError):a.client()
    def test_subprocess_placeholders_and_default_origin(self):
        frames=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'bfl_status','arguments':{}}}]
        env=dict(os.environ,CLAUDE_PLUGIN_OPTION_WORKSPACE='${user_config.workspace}',CLAUDE_PLUGIN_OPTION_OWNER='${user_config.owner}',CLAUDE_PLUGIN_OPTION_CHURCH_UA_ORIGIN='${user_config.church_ua_origin}',CLAUDE_PLUGIN_OPTION_CHURCH_UA_KEY='${user_config.church_ua_key}')
        r=subprocess.run([sys.executable,'-B',str(P/'scripts/bfl_mcp.py')],input=''.join(json.dumps(f)+'\n' for f in frames),text=True,capture_output=True,env=env,timeout=15)
        status=json.loads(json.loads(r.stdout.splitlines()[1])['result']['content'][0]['text'])
        self.assertFalse(status['workspace_configured']);self.assertFalse(status['church_ua_configured']);self.assertEqual(r.stderr,'')
    def test_status_reports_usable_and_unusable_workspace_without_paths(self):
        r=self.a.call('bfl_status',{});self.assertTrue(r['workspace_ready']);self.assertIsNone(r['workspace_problem']);self.assertTrue(r['export_formats']['svg'])
        bad=M.Adapter(str(self.root/'absent'),'test-owner').call('bfl_status',{})
        self.assertTrue(bad['workspace_configured']);self.assertFalse(bad['workspace_ready']);self.assertNotIn(str(self.root),json.dumps(bad))
    def test_search_returns_excerpt_unless_content_requested(self):
        d=dict(self.doc(),content='Luke fifteen. '+'filler '*5000);self.a.call('bfl_library_ingest',{'library':'library','document':d})
        m=self.a.call('bfl_library_search',{'library':'library','query':'Luke'})['matches'][0]
        self.assertNotIn('content',m);self.assertEqual(m['content_chars'],len(d['content']));self.assertLessEqual(len(m['excerpt']),500)
        full=self.a.call('bfl_library_search',{'library':'library','query':'Luke','include_content':True})['matches'][0];self.assertEqual(full['content'],d['content'])
    def test_missing_document_error_is_actionable(self):
        self.a.call('bfl_library_ingest',{'library':'library','document':self.doc()})
        for name,args in [('bfl_library_get',{'library':'library','doc_id':'absent'}),('bfl_library_ingest',{'library':'library','document':dict(self.doc(),doc_id='absent')})]:
            with self.assertRaisesRegex(ValueError,'No such document'):self.a.call(name,args)
    def test_receipt_schema_rejected_before_credential_or_network(self):
        for receipt in [{},{'id':'x'},{'id':'x','kind':'unknown'},{'id':7,'kind':'article'}]:
            with self.assertRaisesRegex(ValueError,'argument|Argument'):self.a.call('bfl_draft_verify',{'receipt':receipt})
    def test_failed_export_leaves_no_blocking_directory(self):
        s={'kind':'comparison','language':'en','title':'Synthetic visual','description':'Synthetic acceptance fixture.','items':[{'label':'A','detail':'B','source':'fixture:one','certainty':'uncertain'}]}
        import builtins;real=builtins.__import__
        def blocked(name,*a,**k):
            if name=='bfl.native_exports':raise ImportError(name)
            return real(name,*a,**k)
        builtins.__import__=blocked
        try:r=self.a.call('bfl_visual_export',{'spec':s,'output_dir':'native','formats':['pdf']})
        finally:builtins.__import__=real
        self.assertEqual(r['status'],'failed');self.assertFalse((self.root/'native').exists())
        self.assertEqual(self.a.call('bfl_visual_export',{'spec':s,'output_dir':'native','formats':['svg']})['status'],'created')
    def test_manifest_uses_directory_accepted_launch_and_env_names(self):
        m=json.loads((P/'.claude-plugin/plugin.json').read_text());srv=m['mcpServers']['biblical-faith-life']
        self.assertEqual(srv['args'],['${CLAUDE_PLUGIN_ROOT}/scripts/bfl_mcp.py'])
        self.assertEqual(srv['env'],{'CLAUDE_PLUGIN_OPTION_'+k.upper():'${user_config.'+k+'}' for k in m['userConfig']})
        self.assertTrue(all('default' in o for o in m['userConfig'].values()))
        source=(P/'scripts/bfl_mcp.py').read_text();self.assertNotIn('plugin.json',source)
        for name in srv['env']:self.assertIn(name,source)
    def test_subprocess_writes_no_bytecode_into_plugin(self):
        import shutil
        for d in P.rglob('__pycache__'):shutil.rmtree(d)
        env={k:v for k,v in os.environ.items() if k!='PYTHONDONTWRITEBYTECODE'}
        subprocess.run([sys.executable,str(P/'scripts/bfl_mcp.py')],input='',text=True,capture_output=True,env=env,timeout=15)
        self.assertEqual(list(P.rglob('__pycache__')),[])
    def frames(self,frames):
        source=io.BytesIO(b''.join(json.dumps(f).encode()+b'\n' for f in frames));sink=io.BytesIO();M.serve(self.a,source,sink);return [json.loads(x) for x in sink.getvalue().splitlines()]
    def test_protocol_handshake_and_tool_call(self):
        r=self.frames([{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'bfl_status','arguments':{}}}]);self.assertEqual(len(r),3);self.assertEqual(len(r[1]['result']['tools']),12);self.assertFalse(r[2]['result']['isError'])
    def test_protocol_notifications_cannot_execute_tools(self):
        r=self.frames([{'jsonrpc':'2.0','method':'tools/call','params':{'name':'bfl_library_ingest','arguments':{'library':'bad','document':self.doc()}}}]);self.assertEqual(r,[]);self.assertFalse((self.root/'bad').exists())
    def test_protocol_requires_initialize_and_unknown_method(self):
        r=self.frames([{'jsonrpc':'2.0','id':1,'method':'tools/list'},{'jsonrpc':'2.0','id':2,'method':'initialize','params':{}},{'jsonrpc':'2.0','id':3,'method':'unknown'}]);self.assertEqual(r[0]['error']['code'],-32002);self.assertEqual(r[2]['error']['code'],-32601)
    def test_protocol_bad_input_is_bounded(self):
        sink=io.BytesIO();M.serve(self.a,io.BytesIO(b'not JSON\n'),sink);self.assertEqual(json.loads(sink.getvalue())['error']['code'],-32700)
        sink=io.BytesIO();M.serve(self.a,io.BytesIO(b'x'*(M.MAX_MESSAGE+1)),sink);self.assertIn('too large',json.loads(sink.getvalue())['error']['message'])
    def test_protocol_actual_subprocess_ignores_ambient_key(self):
        frames=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'bfl_status','arguments':{}}}]
        env=dict(os.environ,CHURCH_UA_AGENT_KEY='synthetic-unused-ambient-key',CLAUDE_PLUGIN_OPTION_CHURCH_UA_KEY='',CLAUDE_PLUGIN_OPTION_WORKSPACE='')
        r=subprocess.run([sys.executable,str(P/'scripts/bfl_mcp.py')],input=''.join(json.dumps(f)+'\n' for f in frames),text=True,capture_output=True,env=env,timeout=15)
        self.assertEqual(r.returncode,0);out=[json.loads(l) for l in r.stdout.splitlines()];status=json.loads(out[1]['result']['content'][0]['text']);self.assertFalse(status['church_ua_configured']);self.assertNotIn('synthetic-unused-ambient-key',r.stdout+r.stderr)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(MCPTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    dest=W/('mcp-tests-python'+str(sys.version_info.major)+str(sys.version_info.minor)+'.json')
    dest.write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'python':sys.version.split()[0],'scope':'Declared MCP adapter tests and actual stdio subprocess; synthetic data only; no live Church UA request.'},indent=2))
    sys.exit(not result.wasSuccessful())
