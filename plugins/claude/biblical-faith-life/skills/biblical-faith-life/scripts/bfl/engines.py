"""Six evidence-contract checks. These do not certify semantic correctness."""
from pathlib import Path
import hashlib
import json
import datetime
import re

LANGUAGES = {'uk', 'en', 'ru'}
ORIGINAL_LANGUAGES = {'grc', 'he', 'hbo', 'arc'}
QUOTATION_LANGUAGES = LANGUAGES | ORIGINAL_LANGUAGES
DOCTRINE_STATUSES = {'FIXED', 'CLARIFIED', 'EXPLICITLY SUPERSEDED EVIDENTIARY CLAIM',
                    'FIRM INTERPRETATION', 'HISTORICALLY OPEN', 'SCIENTIFICALLY LIMITED',
                    'PASTORALLY SENSITIVE', 'OPEN / RESEARCHED'}

def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def content_hash(artifact):
    # Review binds all material inputs, including the evidence and safety record.
    return sha(json.dumps({k:v for k,v in artifact.items() if k!='review'},ensure_ascii=False,sort_keys=True,separators=(',',':')))

def finding(engine, code, detail, severity='critical'):
    return {'engine':engine,'code':code,'detail':detail,'severity':severity}

def source_based_research(a, root):
    issues=[]; sources={}; engine='source-based-research'
    for s in a.get('sources',[]):
        if not isinstance(s,dict):
            issues.append(finding(engine,'source_shape','Source must be an object'));continue
        sid=s.get('id'); text=s.get('text')
        if not sid or sid in sources:
            issues.append(finding(engine,'source_id','Source IDs must be nonempty and unique'))
        sources[sid]=s
        for key in ('title','locator','accessed_at','text','sha256','evidence_type'):
            if not isinstance(s.get(key),str) or not s[key].strip():
                issues.append(finding(engine,'source_field','Missing source field: '+key))
        if isinstance(text,str) and sha(text)!=s.get('sha256'):
            issues.append(finding(engine,'source_hash','Source text hash mismatch'))
        if s.get('evidence_type') not in {'primary','secondary','user'}:
            issues.append(finding(engine,'source_type','Unknown source type'))
        try: datetime.datetime.fromisoformat(s.get('accessed_at','').replace('Z','+00:00'))
        except (ValueError,TypeError): issues.append(finding(engine,'source_date','Invalid source access date'))
    ids=set()
    for c in a.get('claims',[]):
        if not isinstance(c,dict):
            issues.append(finding(engine,'claim_shape','Claim must be an object'));continue
        if not c.get('id') or c.get('id') in ids: issues.append(finding(engine,'claim_id','Claim IDs must be unique'))
        ids.add(c.get('id'))
        if not isinstance(c.get('text'),str) or not c['text'].strip(): issues.append(finding(engine,'claim_text','Missing claim text'))
        if c.get('status') not in {'fact','interpretation','inference','uncertain'}: issues.append(finding(engine,'claim_status','Unclassified claim'))
        s=sources.get(c.get('source_id')); excerpt=c.get('excerpt')
        if not s or not isinstance(excerpt,str) or not excerpt.strip() or excerpt not in s.get('text',''):
            issues.append(finding(engine,'claim_grounding','Claim lacks a matching source excerpt'))
    if not a.get('sources') or not a.get('claims'): issues.append(finding(engine,'evidence_pending','Audited artifacts need source and claim records','pending'))
    return issues

def biblical_accuracy(a, root):
    issues=[]; engine='biblical-accuracy'; sources={s.get('id'):s for s in a.get('sources',[]) if isinstance(s,dict)}
    for q in a.get('quotations',[]):
        if not isinstance(q,dict):
            issues.append(finding(engine,'quotation_shape','Quotation must be an object'));continue
        s=sources.get(q.get('source_id'));text=q.get('text')
        if not s or not isinstance(text,str) or not text.strip() or text not in s.get('text',''):
            issues.append(finding(engine,'quotation_text','Quotation is not present in supplied source text'))
        for key in ('translation','reference'):
            if not isinstance(q.get(key),str) or not q[key].strip(): issues.append(finding(engine,'quotation_label','Quotation needs '+key))
        if q.get('language') not in QUOTATION_LANGUAGES: issues.append(finding(engine,'quotation_language','Unknown quotation language'))
    ex=a.get('exegesis',{})
    for key in ('context','argument','meaning','limits','application'):
        if not isinstance(ex,dict) or not isinstance(ex.get(key),str) or not ex[key].strip():
            issues.append(finding(engine,'exegesis_pending','Missing exegetical evidence: '+key,'pending'))
    return issues

def doctrinal_governance(a, root):
    issues=[];engine='doctrinal-governance';root=Path(root).resolve()
    canonical=json.loads((root/'canonical-sources.json').read_text())
    manifest={s['file']:s for s in canonical['sources']}
    for name,m in manifest.items():
        p=root/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=m['sha256']:
            issues.append(finding(engine,'doctrine_integrity','Protected source differs: '+name))
    for d in a.get('doctrine',[]):
        if not isinstance(d,dict):
            issues.append(finding(engine,'doctrine_shape','Doctrine record must be an object'));continue
        name=d.get('file');m=manifest.get(name)
        if not m or d.get('sha256')!=m['sha256']:
            issues.append(finding(engine,'doctrine_reference','Doctrine record must name an unchanged canonical source'));continue
        if d.get('status') not in DOCTRINE_STATUSES: issues.append(finding(engine,'doctrine_status','Unknown v9 status'))
        lines=(root/name).read_text().splitlines();start=d.get('start_line');end=d.get('end_line')
        if type(start)!=int or type(end)!=int or not 1<=start<=end<=len(lines):
            issues.append(finding(engine,'doctrine_span','Invalid source line span'))
    if not a.get('doctrine'): issues.append(finding(engine,'doctrine_review_pending','No governing argument units recorded','pending'))
    return issues

def multilingual_scripture(a, root):
    issues=[];engine='multilingual-scripture'
    if a.get('language') not in LANGUAGES: issues.append(finding(engine,'language','Language must be uk, en, or ru'))
    for q in a.get('quotations',[]):
        if not isinstance(q,dict): continue
        if q.get('language') in ORIGINAL_LANGUAGES:
            if q.get('text_kind')!='original' or not isinstance(q.get('edition_name'),str) or not q['edition_name'].strip():
                issues.append(finding(engine,'original_edition','Original-language quotation needs text_kind=original and a full edition_name'))
        label=q.get('translation','')
        if label in {'CUV','НПУ'}:
            expected={'CUV':'Сучасний український переклад','НПУ':'Новий переклад українською'}[label]
            if q.get('edition_name')!=expected or q.get('language')!='uk':
                issues.append(finding(engine,'translation_identity','Verify full Ukrainian edition name for '+label))
    return issues

def pastoral_safety(a, root):
    issues=[];engine='pastoral-safety';s=a.get('safety',{})
    if not isinstance(s,dict): return [finding(engine,'safety_shape','Safety record must be an object')]
    if s.get('risk') not in {'none','concern','crisis','unknown'}: issues.append(finding(engine,'risk','Risk must be recorded'))
    for key in ('private_data','consent_to_store','human_reviewed'):
        if type(s.get(key))!=bool: issues.append(finding(engine,'safety_field','Boolean required: '+key))
    if s.get('private_data') and not s.get('consent_to_store'): issues.append(finding(engine,'private_consent','Do not persist private data without consent'))
    if not isinstance(s.get('actions'),list) or any(not isinstance(v,str) for v in s.get('actions',[])):
        issues.append(finding(engine,'safety_actions','Actions must be a string array'))
    if s.get('risk') in {'concern','crisis','unknown'}:
        if s.get('human_reviewed') is not True: issues.append(finding(engine,'safety_review_pending','Risk requires actual human review','pending'))
        if not s.get('actions'): issues.append(finding(engine,'safety_action_pending','Risk requires concrete safety steps','pending'))
    return issues

def independent_quality_assurance(a, root):
    issues=[];engine='independent-quality-assurance';r=a.get('review',{})
    if not isinstance(r,dict): return [finding(engine,'review_shape','Review must be an object')]
    if not r.get('reviewer') or r.get('reviewer')==a.get('author'): issues.append(finding(engine,'independent_review_pending','Reviewer must differ from author','pending'))
    if r.get('semantic_reviewed') is not True: issues.append(finding(engine,'semantic_review_pending','Independent semantic review has not been attested','pending'))
    if r.get('artifact_sha256')!=content_hash(a): issues.append(finding(engine,'stale_review','Review does not match current artifact'))
    if not isinstance(r.get('findings'),list): issues.append(finding(engine,'review_findings','Findings must be an array'))
    for f in r.get('findings',[]) if isinstance(r.get('findings'),list) else []:
        if not isinstance(f,dict) or f.get('severity') not in {'critical','high','medium','low'} or type(f.get('resolved'))!=bool:
            issues.append(finding(engine,'review_finding_shape','Invalid finding'));continue
        if f['severity'] in {'critical','high'} and not f['resolved']: issues.append(finding(engine,'unresolved_finding','Unresolved consequential review finding'))
    if not a.get('requirements'): issues.append(finding(engine,'requirements_pending','Original request has no recorded acceptance evidence','pending'))
    for req in a.get('requirements',[]):
        if not isinstance(req,dict) or any(not isinstance(req.get(k),str) or not req[k].strip() for k in ('id','expected','evidence')):
            issues.append(finding(engine,'requirement_evidence','Each requirement needs expected behavior and evidence'))
    return issues

ENGINES=(biblical_accuracy,doctrinal_governance,source_based_research,multilingual_scripture,pastoral_safety,independent_quality_assurance)

def validate(a, root):
    issues=[]
    if not isinstance(a,dict): return {'status':'fail','findings':[finding('contract','shape','Artifact must be an object')]}
    for key in ('id','author','content'):
        if not isinstance(a.get(key),str) or not a[key].strip(): issues.append(finding('contract','required','Missing '+key))
    if type(a.get('schema_version'))!=int or a.get('schema_version')!=1: issues.append(finding('contract','version','schema_version must equal integer 1'))
    for key in ('sources','claims','quotations','doctrine','requirements'):
        if not isinstance(a.get(key),list): issues.append(finding('contract','array',key+' must be an array'))
    if issues: return {'status':'fail','findings':issues,'scope':'structural evidence checks only'}
    for engine in ENGINES:
        try: issues.extend(engine(a,root))
        except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:
            issues.append(finding(engine.__name__,'invalid_record','Unable to validate malformed or unavailable records: '+type(e).__name__))
    status='fail' if any(f['severity'] in {'critical','high'} for f in issues) else 'pending' if issues else 'pass'
    return {'status':status,'findings':issues,'scope':'structural evidence checks only; source authenticity and semantic truth require actual review'}
