"""Draft-only adapter for the inspected application API. No database access."""
import datetime
import json
import urllib.request
import urllib.error
import urllib.parse
from .engines import sha

ENDPOINTS={'article':('articles','articles','article'),'sermon':('articles','articles','article'),
 'reading-plan':('reading-plans','plans','plan'),'lesson':('classes','classes','class'),
 'class':('classes','classes','class'),'devotional':('devotionals','devotionals','devotional')}
FIELDS={'articles':{'title','summary','body','language','type','visibility','tags'},
 'reading-plans':{'title','days','description','tags','plan_data'},
 'classes':{'title','description','language','days_count','starts_on','tags'},
 'devotionals':{'title','body','scripture_reference','publish_date'}}

def jslen(s):return len(s.encode('utf-16-le'))//2

def prepare(kind,data):
    if kind not in ENDPOINTS or not isinstance(data,dict):raise ValueError('Unsupported content kind or payload')
    endpoint,scope,result=ENDPOINTS[kind]
    if set(data)-FIELDS[endpoint]:raise ValueError('Unknown, publication, or scope-control field rejected')
    p=dict(data)
    maxima={'title':300 if endpoint=='articles' else 200,'summary':2000,'body':200000 if endpoint=='articles' else 20000,'description':5000,'scripture_reference':200}
    for field,maximum in maxima.items():
        if field in p:
            if not isinstance(p[field],str):raise ValueError(field+' must be text')
            p[field]=p[field].strip()
            if jslen(p[field])>maximum:raise ValueError(field+' exceeds contract limit')
    if not isinstance(p.get('title'),str) or jslen(p['title'])<3:raise ValueError('Title needs at least 3 characters')
    if endpoint=='devotionals' and (not isinstance(p.get('body'),str) or jslen(p['body'])<20):raise ValueError('Devotional body needs at least 20 characters')
    for field,maximum in [('days',365),('days_count',366)]:
        if field in p and (type(p[field])!=int or not 1<=p[field]<=maximum):raise ValueError(field+' is out of range')
    if endpoint=='reading-plans' and 'days' not in p:raise ValueError('Reading plans need days')
    if 'plan_data' in p and not isinstance(p['plan_data'],dict):raise ValueError('plan_data must be an object')
    if 'tags' in p and (not isinstance(p['tags'],list) or len(p['tags'])>20 or any(not isinstance(t,str) for t in p['tags'])):raise ValueError('Invalid tags')
    for field in ('publish_date','starts_on'):
        if field in p:
            try:
                if not isinstance(p[field],str) or len(p[field])!=10:raise ValueError()
                datetime.date.fromisoformat(p[field])
            except (ValueError,TypeError):raise ValueError(field+' must be a valid YYYY-MM-DD')
    if endpoint in {'articles','classes'}:
        p.setdefault('language','uk')
        if p['language'] not in {'uk','en','ru'}:raise ValueError('Unsupported language')
    if endpoint=='articles':
        p.setdefault('visibility','private');p.setdefault('type','article')
        if p['visibility'] not in {'private','approved_members','members','public'}:raise ValueError('Invalid visibility')
        if p['type'] not in {'article','news','blog','study'}:raise ValueError('Invalid article type')
    encoded=json.dumps(p,ensure_ascii=False,separators=(',',':')).encode()
    if len(encoded)>256*1024:raise ValueError('Request exceeds 256 KiB')
    return {'kind':kind,'endpoint':endpoint,'required_scope':scope+':write','result_key':result,'payload':p,'payload_sha256':sha(encoded.decode()),'publication':'human review required','limitations':['Class API creates a shell; detailed lessons remain local'] if kind in {'lesson','class'} else []}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def transport(method,url,headers,payload):
    req=urllib.request.Request(url,data=payload,headers=headers,method=method)
    try:
        with urllib.request.build_opener(NoRedirect).open(req,timeout=20) as response:
            raw=response.read(1024*1024+1)
            if len(raw)>1024*1024:raise ValueError('Response too large')
            return response.status,json.loads(raw.decode())
    except urllib.error.HTTPError as e:return e.code,{'ok':False,'error':'http_error'}

def verify_state(endpoint,entity,readback=False):
    expected={'articles':{'status':'draft','is_global':False,'approval_status':'pending'},
     'classes':{'is_published':False,'is_global':False},
     'reading-plans':{'is_global':False,'approval_status':'pending'},
     'devotionals':{'status':'draft'}}[endpoint]
    if endpoint=='reading-plans' and readback:expected=dict(expected,is_published=False)
    for field,value in expected.items():
        if field not in entity or type(entity[field])!=type(value) or entity[field]!=value:raise RuntimeError('Response lacks verified draft state or violates draft-only scope')
    if entity.get('is_published',False) is not False or entity.get('is_global',False) is not False:raise RuntimeError('Response violates draft-only scope')

class DraftClient:
    def __init__(self,origin,token,transport_fn=transport):
        u=urllib.parse.urlsplit(origin)
        if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/'):raise ValueError('Configure an HTTPS origin without credentials, path, query, or fragment')
        if not isinstance(token,str) or not token.startswith('cc_live_') or any(c.isspace() for c in token):raise ValueError('A Church UA Agent API key is required')
        self.origin=origin.rstrip('/');self._token=token;self._send=transport_fn
    def __repr__(self):return 'DraftClient(origin='+repr(self.origin)+', token=<redacted>)'
    def submit(self,kind,data,authorized=False):
        if authorized is not True:raise PermissionError('Actual user authorization for draft submission is required')
        prepared=prepare(kind,data);body=json.dumps(prepared['payload'],ensure_ascii=False,separators=(',',':')).encode()
        try:code,r=self._send('POST',self.origin+'/api/public/v1/content/'+prepared['endpoint'],{'Authorization':'Bearer '+self._token,'Content-Type':'application/json'},body)
        except Exception:raise RuntimeError('Submission outcome unknown; reconcile before retrying') from None
        if code!=201 or not isinstance(r,dict) or r.get('ok') is not True:raise RuntimeError('Draft request not verified (HTTP '+str(code)+'); reconcile before retrying')
        entity=r.get(prepared['result_key'],{})
        if not isinstance(entity,dict) or not isinstance(entity.get('id'),str) or not entity['id']:raise RuntimeError('Missing draft ID; reconcile before retrying')
        if r.get('status')!='draft_pending_review':raise RuntimeError('Response violates draft-only contract; stop for human review')
        verify_state(prepared['endpoint'],entity)
        return {'id':entity['id'],'kind':kind,'status':'draft_pending_review','payload_sha256':prepared['payload_sha256'],'readback_verified':False,'content_readback_verified':False}
    def verify(self,receipt):
        endpoint,scope,result=ENDPOINTS[receipt['kind']];plural={'article':'articles','plan':'plans','class':'classes','devotional':'devotionals'}[result]
        try:code,r=self._send('GET',self.origin+'/api/public/v1/content/'+endpoint,{'Authorization':'Bearer '+self._token},None)
        except Exception:raise RuntimeError('Draft read-back unavailable') from None
        if code!=200 or not isinstance(r,dict) or r.get('ok') is not True:raise RuntimeError('Draft read-back requires a valid read scope')
        items=r.get(plural,[])
        if not isinstance(items,list):raise RuntimeError('Invalid read-back contract')
        matches=[x for x in items if isinstance(x,dict) and x.get('id')==receipt['id']]
        if len(matches)!=1:raise RuntimeError('Draft ID absent from bounded recent listing; inspect console before retrying')
        verify_state(endpoint,matches[0],readback=True)
        return dict(receipt,readback_verified=True,content_readback_verified=False,verification_scope='ID and selected draft-state fields only; full body unavailable in recent listing')
