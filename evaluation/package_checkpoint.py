from pathlib import Path
import json,hashlib,datetime,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent
OUT=WORK.parent.parent/'outputs/quality-upgrade.nosync'
OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
packages={
 'workspace-2.1.0-rc.5-candidate.zip':WORK/'workspace-candidate',
 'claude-2.1.0-claude.5-candidate.zip':ROOT/'plugins/claude/biblical-faith-life'
}
receipts=[]
for name,folder in packages.items():
    path=OUT/name
    files=sorted(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(folder).as_posix())
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
        assert sum(n.endswith('/SKILL.md') for n in z.namelist())==54
        for p in files:assert z.read(p.relative_to(folder).as_posix())==p.read_bytes()
    receipts.append({'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'files':len(files),'skill_count':54,'archive_roundtrip':'passed','publication_status':'local_unreleased_candidate'})
rollback=OUT/'workspace-2.1.0-rc.4-rollback.tar.gz'
manifest=json.loads((WORK/'baseline/SOURCE_MANIFEST.json').read_text())
for row in manifest:
    for package in packages.values():
        p=package/'skills/biblical-faith-life/references'/row['file']
        assert sha(p)==row['sha256']
checkpoint={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'candidate_prepared_native_evaluation_blocked','source_baseline_commit':'dc2e1c29ebff3b19afe3dd97f1485e460fbf2b34','workspace_plugin_id':'Plugin_b1c6103546e081918ec49ae254fa4b20','workspace_current_release_id':'pluginrel_6ad37bff8ba88191852ad75559b57a90','workspace_current_version':'2.1.0-rc.4','workspace_scope':'WORKSPACE','workspace_audience':'LISTED within the same workspace','rollback':{'path':str(rollback),'sha256':sha(rollback)},'candidates':receipts,'preserved_governing_sources':manifest,'deterministic_results':{'python':{'passed':43,'failed':0},'protected_service':{'passed':46,'failed':0},'public_boundary':{'passed':24,'failed':0},'claude_strict_validation':'passed'},'actual_live_network_checks':json.loads((OUT/'public-access.json').read_text()),'case_counts_per_host':{'core':162,'language_transfer':12,'repeatability':8,'total':182},'claude_answer_generation':{'completed':0,'quota_blocked':1,'not_attempted':181,'semantic_review_passed':0,'provider_reported_reset':'October 30 at 16:00 Europe/Kiev'},'chatgpt_answer_generation':{'completed':0,'not_attempted':182,'exact_public_app_installation':'unverified'},'production_changes':{'workspace_plugin_updated':False,'public_submission_changed':False,'claude_submission_changed':False,'remote_source_pushed':False,'site_deployed':False},'remaining':['Execute and substantively review native answer cases on actual supported hosts','Repair failures and rerun affected plus held-out cases','Verify actual file exports and layout','Obtain targeted human specialist review where needed','Apply verified shared improvements to existing workspace identity with guarded release and readback','Handle public/Claude source updates through their own release processes without disrupting active review unknowingly'],'historical_evidence_note':'Earlier 49 Claude samples and 14 editorial revisions were reported in prior work. Their original local audit directory is unavailable at its former path, so they are not counted as current candidate evidence.'}
(OUT/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(ROOT/'evaluation/README.md',OUT/'quality-upgrade-report.md')
print(json.dumps({'packages':[{'name':Path(r['path']).name,'bytes':r['bytes'],'files':r['files']} for r in receipts],'checkpoint':str(OUT/'checkpoint.json')},indent=2))
