"""Run actual local Claude plugin subjects; save no hidden thinking in public receipts."""
from pathlib import Path
import argparse, json, subprocess, datetime, hashlib, time, os, shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent.parent.parent/'outputs/quality-upgrade.nosync/claude-candidate'
p=argparse.ArgumentParser();p.add_argument('--ids',nargs='*');p.add_argument('--limit',type=int);p.add_argument('--suite',choices=['core','extended','all'],default='core');a=p.parse_args()
cases=[]
for filename in (['cases.json','extended-cases.json'] if a.suite=='all' else ['extended-cases.json' if a.suite=='extended' else 'cases.json']):
    cases.extend(json.loads((ROOT/'evaluation'/filename).read_text())['cases'])
if a.ids:cases=[c for c in cases if c['id'] in a.ids]
if a.limit:cases=cases[:a.limit]
OUT.mkdir(parents=True,exist_ok=True)
plugin=ROOT/'plugins/claude/biblical-faith-life'
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
for case in cases:
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    folder=OUT/case['id'];folder.mkdir(exist_ok=True)
    receiptpath=folder/'receipt.json'
    if receiptpath.exists():
        prior=json.loads(receiptpath.read_text())
        if prior.get('execution_status')=='completed':continue
    prompt='Activate the biblical-faith-life:'+case['skill']+' skill from the explicitly loaded plugin and follow its entrypoint. This is a synthetic evaluation, with read-only tools only. Do not transmit private user data, access credentials, submit drafts, or perform any external write.\n\n'+case['prompt']
    (folder/'prompt.txt').write_text(prompt)
    cmd=[os.environ.get('CLAUDE_BIN') or shutil.which('claude') or 'claude','-p','--plugin-dir',str(plugin),'--output-format','stream-json','--verbose','--no-session-persistence','--tools','Read,Skill,WebSearch,WebFetch','--allowedTools','Read,Skill,WebSearch,WebFetch','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--',prompt]
    before=time.monotonic();models=set();tools=[];answer='';errors=[];status='failed'
    rawpath=folder/'private-trace.jsonl'
    try:
        with rawpath.open('w') as raw:
            os.chmod(rawpath,0o600)
            proc=subprocess.run(cmd,cwd=ROOT.parent,stdout=raw,stderr=subprocess.PIPE,text=True,timeout=420)
        for line in rawpath.read_text().splitlines():
            try:event=json.loads(line)
            except ValueError:continue
            msg=event.get('message',{})
            if msg.get('model') and msg['model']!='<synthetic>':models.add(msg['model'])
            for block in msg.get('content',[]) if isinstance(msg.get('content'),list) else []:
                if block.get('type')=='tool_use':
                    inp=block.get('input',{})
                    tools.append({'name':block.get('name'),'skill':inp.get('skill'),'file_path':inp.get('file_path'),'offset':inp.get('offset'),'limit':inp.get('limit')})
            if event.get('type')=='result':
                answer=event.get('result','');errors=event.get('errors',[])
                status=('quota_blocked' if event.get('api_error_status')==429 else 'failed') if event.get('is_error') else 'completed'
                if event.get('is_error'):errors=[event.get('api_error','provider_error'),answer]
        if proc.returncode and not errors:errors=['CLI returned nonzero status '+str(proc.returncode), proc.stderr[:2000]]
    except subprocess.TimeoutExpired:
        status='timeout';errors=['420-second execution limit reached; not counted as a completed answer']
    (folder/'answer.md').write_text(answer)
    receipt={'case_id':case['id'],'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':round(time.monotonic()-before,2),'execution_status':status,'semantic_review':'pending','models_observed':sorted(models),'host':'Claude Code 2.1.303; local --plugin-dir candidate, not directory installation','plugin_version':'2.1.0-claude.5','prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'tools_requested':tools,'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'errors':errors,'network_writes_authorized':False,'file_export_checks':'not_run'}
    receiptpath.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['case_id','execution_status','elapsed_seconds','models_observed','errors']},ensure_ascii=False),flush=True)
    if status!='completed':break # circuit-breaker: no retries around quota/auth failures
