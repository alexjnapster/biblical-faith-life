"""Run the same prompts against several local plugin variants under identical model/tool conditions.

Unlike run_claude.py this records the host version and loaded plugin version from the CLI's own init event,
hashes the plugin tree, pins the model and measures length with measure_words.py. Generation is not acceptance.
"""
from pathlib import Path
import argparse, json, subprocess, datetime, hashlib, time, os, sys, shutil
sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_words import measure

ROOT = Path(__file__).resolve().parents[1]
CLAUDE = os.environ.get('CLAUDE_BIN') or shutil.which('claude') or 'claude'
TOOLS = 'Read,Skill,WebSearch,WebFetch'

def tree_sha(path):
    h = hashlib.sha256()
    for p in sorted(Path(path).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.name != '.in_use':
            h.update(str(p.relative_to(path)).encode()); h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def write_checkpoint(out):
    """Restart checkpoint rebuilt from receipts at every case boundary; generation status only, never a quality verdict."""
    rows = []
    for r in sorted(out.glob('*/*/receipt.json')):
        d = json.loads(r.read_text()); m = d.get('measured_words') or {}
        rows.append({'variant': d['variant'], 'case_id': d['case_id'], 'execution_status': d['execution_status'], 'finished_at': d['finished_at'],
                     'plugin_tree_sha256': d.get('plugin_tree_sha256'), 'full_words': m.get('full', {}).get('whitespace'), 'body_words': m.get('body', {}).get('whitespace')})
    started = sorted(str(f.parent.relative_to(out)) for f in out.glob('*/*/prompt.txt') if not (f.parent/'receipt.json').exists())
    tmp = out/'CHECKPOINT.json.tmp'
    tmp.write_text(json.dumps({'written_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'receipts': rows,
                               'started_without_receipt': started, 'note': 'execution_status=completed means an answer was generated, not that it passed review'}, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(out/'CHECKPOINT.json')

p = argparse.ArgumentParser()
p.add_argument('--variant', required=True); p.add_argument('--plugin-dir', required=True)
p.add_argument('--out', required=True); p.add_argument('--ids', nargs='+', required=True)
p.add_argument('--model', default='claude-opus-5-5'); p.add_argument('--checkpoint-only', action='store_true'); p.add_argument('--with-count-tool', action='store_true', help="enable only the plugin's own local connector and allow only its read-only bfl_count_words tool")
a = p.parse_args()
if a.checkpoint_only: write_checkpoint(Path(a.out)); sys.exit(0)
cases = {c['id']: c for f in ('cases.json', 'extended-cases.json') for c in json.loads((ROOT/'evaluation'/f).read_text())['cases']}
plugin = Path(a.plugin_dir).resolve(); plugin_sha = tree_sha(plugin)
for cid in a.ids:
    case = cases[cid]
    folder = Path(a.out)/a.variant/cid; folder.mkdir(parents=True, exist_ok=True)
    receiptpath = folder/'receipt.json'
    if receiptpath.exists() and json.loads(receiptpath.read_text()).get('execution_status') == 'completed':
        print(json.dumps({'case_id': cid, 'variant': a.variant, 'skipped': 'already completed'})); continue
    prompt = ('Activate the biblical-faith-life:' + case['skill'] + ' skill from the explicitly loaded plugin and follow its entrypoint. '
              'This is a synthetic evaluation, with read-only tools only. Do not transmit private user data, access credentials, '
              'submit drafts, or perform any external write.\n\n' + case['prompt'])
    (folder/'prompt.txt').write_text(prompt)
    mcp, allowed = {'mcpServers': {}}, TOOLS
    if a.with_count_tool:
        mcp = {'mcpServers': {'bfl': {'command': 'python3', 'args': ['-B', str(plugin/'scripts/bfl_mcp.py')], 'env': {'BFL_WORKSPACE': '', 'BFL_CHURCH_UA_KEY': ''}}}}
        allowed = TOOLS + ',mcp__bfl__bfl_count_words'
    cmd = [CLAUDE, '-p', '--plugin-dir', str(plugin), '--model', a.model, '--output-format', 'stream-json', '--verbose',
           '--no-session-persistence', '--tools', TOOLS, '--allowedTools', allowed, '--strict-mcp-config', '--mcp-config', json.dumps(mcp), '--', prompt]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(); before = time.monotonic()
    models, tools, answer, errors, status, host, loaded = set(), [], '', [], 'failed', None, None
    rawpath = folder/'private-trace.jsonl'
    try:
        with rawpath.open('w') as raw:
            os.chmod(rawpath, 0o600)
            proc = subprocess.run(cmd, cwd=plugin.parent, stdout=raw, stderr=subprocess.PIPE, text=True, timeout=900)
        for line in rawpath.read_text().splitlines():
            try: event = json.loads(line)
            except ValueError: continue
            if event.get('subtype') == 'init':
                host = event.get('claude_code_version')
                loaded = [{'version': x.get('version'), 'source': x.get('source'), 'path': x.get('path')} for x in event.get('plugins', []) if x.get('name') == 'biblical-faith-life']
                loaded_skills = sum(1 for s in event.get('skills', []) if s.startswith('biblical-faith-life:'))
            msg = event.get('message', {})
            if msg.get('model') and msg['model'] != '<synthetic>': models.add(msg['model'])
            for block in msg.get('content', []) if isinstance(msg.get('content'), list) else []:
                if block.get('type') == 'tool_use':
                    inp = block.get('input', {})
                    tools.append({k: v for k, v in {'name': block.get('name'), 'skill': inp.get('skill'), 'file_path': inp.get('file_path'),
                                  'offset': inp.get('offset'), 'limit': inp.get('limit'), 'url': inp.get('url'), 'query': inp.get('query')}.items() if v is not None})
            if event.get('type') == 'result':
                answer = event.get('result', ''); errors = event.get('errors', [])
                status = ('quota_blocked' if event.get('api_error_status') == 429 else 'failed') if event.get('is_error') else 'completed'
                if event.get('is_error'): errors = [event.get('api_error', 'provider_error'), answer]
        if proc.returncode and not errors: errors = ['CLI returned nonzero status ' + str(proc.returncode), proc.stderr[:2000]]
    except subprocess.TimeoutExpired:
        status = 'timeout'; errors = ['900-second execution limit reached; not counted as a completed answer']
    (folder/'answer.md').write_text(answer)
    receipt = {'case_id': cid, 'variant': a.variant, 'started_at': started, 'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'elapsed_seconds': round(time.monotonic()-before, 2), 'execution_status': status, 'semantic_review': 'pending',
               'model_requested': a.model, 'models_observed': sorted(models), 'host_claude_code_version': host,
               'plugin_loaded': loaded, 'plugin_skills_loaded': locals().get('loaded_skills'), 'plugin_dir': str(plugin), 'plugin_tree_sha256': plugin_sha,
               'tools_allowed': allowed, 'mcp': ('plugin connector only; only bfl_count_words allowed' if a.with_count_tool else 'disabled (strict empty config)'),
               'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(), 'tools_requested': tools,
               'answer_sha256': hashlib.sha256(answer.encode()).hexdigest(), 'measured_words': measure(answer) if answer else None,
               'errors': errors, 'network_writes_authorized': False}
    receiptpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('case_id', 'variant', 'execution_status', 'elapsed_seconds', 'models_observed', 'errors')}, ensure_ascii=False), flush=True)
    write_checkpoint(Path(a.out))
    if status != 'completed': sys.exit(2)  # circuit-breaker: no retries around quota/auth failures
