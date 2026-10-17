#!/usr/bin/env python3
"""Declared, bounded stdio MCP adapter for the existing Biblical Faith Life engines."""
import contextlib
import hashlib
import io
import json
import os
import sqlite3
from pathlib import Path
import sys

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN/'skills/biblical-faith-life/scripts'))
from bfl.engines import validate
from bfl.knowledge import KnowledgeBase
from bfl.visuals import render
from bfl.workflows import Workflow
from bfl.church_ua import prepare, DraftClient
from bfl_cli import save_checkpoint

REF = PLUGIN/'skills/biblical-faith-life/references'
REGISTRY = json.loads((REF/'registry.json').read_text(encoding='utf-8'))
MAX_MESSAGE = 2*1024*1024
STRING = {'type':'string','minLength':1,'maxLength':1000000}
OBJECT = {'type':'object'}
BOOL = {'type':'boolean'}

def schema(properties, required):
    return {'type':'object','properties':properties,'required':required,'additionalProperties':False}

DOCUMENT = schema({'title':STRING,'content':STRING,'language':{'type':'string','enum':['uk','en','ru']},'locator':STRING,'doc_id':STRING,'metadata':OBJECT,'private':BOOL,'consent':BOOL},['title','content','language','locator'])
VISUAL_ITEM = {'type':'object','properties':{'label':STRING,'detail':STRING,'source':STRING,'certainty':{'type':'string','enum':['text','historical','inferred','reconstruction','uncertain']},'lat':{'type':'number'},'lon':{'type':'number'},'start':{'type':'number'},'end':{'type':'number'}},'required':['label','detail','source','certainty'],'additionalProperties':False}
VISUAL = schema({'kind':{'type':'string','enum':['map','timeline','comparison','reconstruction','slides']},'language':{'type':'string','enum':['uk','en','ru']},'title':{'type':'string','minLength':1,'maxLength':180},'description':{'type':'string','minLength':1,'maxLength':2000},'items':{'type':'array','minItems':1,'maxItems':60,'items':VISUAL_ITEM},'elements':{'type':'array','maxItems':100,'items':OBJECT}},['kind','language','title','description','items'])

def tool(name, description, properties, required, readonly=False, network=False):
    return {'name':name,'description':description,'inputSchema':schema(properties,required),
            'annotations':{'title':name.replace('bfl_','').replace('_',' ').title(),
              'readOnlyHint':readonly,'destructiveHint':False,'openWorldHint':network}}

TOOLS = [
 tool('bfl_status','Show available engines and whether this plugin has an explicitly configured workspace and Church UA credential. Never returns a credential.',{},[],True),
 tool('bfl_validate','Validate a supplied evidence envelope against the six shared engine gates. Structural validation does not certify theology or scholarship.',{'envelope':OBJECT},['envelope'],True),
 tool('bfl_library_ingest','Store a supplied document and immutable provenance/version history in the configured local workspace. Put optional passage tags in document.metadata, not unknown document fields. Private records require actual boolean consent in document.',{'library':STRING,'document':DOCUMENT},['library','document']),
 tool('bfl_library_search','Search a named existing local library in the configured workspace; returns only matching stored evidence.',{'library':STRING,'query':STRING,'limit':{'type':'integer','minimum':1,'maximum':50}},['library','query'],True),
 tool('bfl_library_get','Read an actual stored document version from a named existing local library.',{'library':STRING,'doc_id':STRING,'version':{'type':'integer','minimum':1}},['library','doc_id'],True),
 tool('bfl_workflow_start','Create a new persistent research, sermon or other registered studio checkpoint. Does not generate or certify manuscripts.',{'workflow':STRING,'checkpoint':STRING,'language':{'type':'string','enum':['uk','en','ru']},'stages':{'type':'array','items':STRING}},['workflow','checkpoint']),
 tool('bfl_workflow_record','Record a supplied substantive stage or review and invalidate downstream records when inputs change. Actor labels do not establish real review independence.',{'checkpoint':STRING,'stage':STRING,'content':STRING,'actor':STRING,'review':BOOL},['checkpoint','stage','content','actor']),
 tool('bfl_workflow_status','Reopen and revalidate a saved checkpoint, including exact manuscript/review hash bindings.',{'checkpoint':STRING},['checkpoint'],True),
 tool('bfl_visual_export','Render a supplied source-linked visual specification into a new workspace directory. Set spec.kind, not spec.type. SVG/HTML are built in; PDF/PPTX need separately installed documented dependencies.',{'spec':VISUAL,'output_dir':STRING,'formats':{'type':'array','minItems':1,'maxItems':4,'items':{'type':'string','enum':['svg','html','pdf','pptx']}}},['spec','output_dir']),
 tool('bfl_draft_preview','Prepare and validate a Church UA draft payload without network access or submitting anything.',{'kind':STRING,'payload':OBJECT},['kind','payload'],True),
 tool('bfl_draft_submit','Submit exactly one explicitly authorized, reviewed Church UA draft to the configured origin using only the credential explicitly shared through plugin configuration. Persists an attempt marker before sending; never automatically retries an uncertain outcome. Requires workspace and credential configuration.',{'kind':STRING,'payload':OBJECT,'review_envelope':OBJECT,'authorized_draft':BOOL},['kind','payload','review_envelope','authorized_draft'],False,True),
 tool('bfl_draft_verify','Read back the ID and selected draft-state fields for a prior receipt using the configured Church UA access. Cannot verify the complete body through the bounded listing.',{'receipt':OBJECT},['receipt'],True,True)
]
BY_NAME = {t['name']:t for t in TOOLS}

def check(value, rule):
    kind=rule.get('type')
    types={'object':dict,'array':list,'string':str,'integer':int,'boolean':bool}
    if kind=='number':
        if type(value) not in (int,float):raise ValueError('Argument type does not match the tool schema')
    elif kind and type(value) is not types[kind]:raise ValueError('Argument type does not match the tool schema')
    if 'enum' in rule and value not in rule['enum']:raise ValueError('Unsupported argument value')
    if kind=='object':
        properties=rule.get('properties',{})
        if any(k not in value for k in rule.get('required',[])):raise ValueError('Required argument missing')
        if rule.get('additionalProperties') is False and set(value)-set(properties):raise ValueError('Unknown argument')
        for key,subrule in properties.items():
            if key in value:check(value[key],subrule)
    if kind=='array':
        if len(value)<rule.get('minItems',0) or len(value)>rule.get('maxItems',100):raise ValueError('Array length is out of bounds')
        for entry in value:check(entry,rule.get('items',{}))
    if kind=='string' and not rule.get('minLength',0)<=len(value)<=rule.get('maxLength',MAX_MESSAGE):raise ValueError('Text length is out of bounds')
    if kind=='integer' and not rule.get('minimum',-10**15)<=value<=rule.get('maximum',10**15):raise ValueError('Number is out of bounds')

class Adapter:
    def __init__(self, workspace='', owner='local-owner', origin='', token=''):
        self.workspace=workspace;self.owner=owner;self.origin=origin;self._token=token

    def root(self):
        if not self.workspace:raise ValueError('Configure this plugin workspace before using local storage or sending a draft')
        original=Path(self.workspace)
        if not original.is_absolute():raise ValueError('The configured workspace must be an absolute existing directory')
        if any(p.is_symlink() for p in (original,*original.parents)):raise ValueError('The configured workspace cannot traverse symbolic links')
        root=original.resolve(strict=True)
        if not root.is_dir() or root==Path(root.anchor) or root==Path.home() or root==PLUGIN or PLUGIN in root.parents:raise ValueError('Choose a dedicated workspace outside the installed plugin')
        return root

    def path(self, relative, existing=False):
        root=self.root();relative=Path(relative)
        if relative.is_absolute() or not relative.parts or any(p in {'.','..'} for p in relative.parts):raise ValueError('Use a contained workspace-relative path')
        target=root/relative
        for p in (target,*target.parents):
            if p==root:break
            if p.is_symlink():raise ValueError('Workspace paths cannot traverse symbolic links')
        resolved=target.resolve()
        if root not in resolved.parents or resolved==PLUGIN or PLUGIN in resolved.parents:raise ValueError('Path is outside the allowed workspace')
        if target.exists() and target.is_file() and target.stat().st_nlink>1:raise ValueError('Hard-linked files cannot be used')
        if existing and not target.exists():raise ValueError('Requested workspace item does not exist')
        return target

    def read_json(self, relative):
        p=self.path(relative,True)
        if not p.is_file() or p.stat().st_size>MAX_MESSAGE:raise ValueError('Checkpoint is not a bounded regular file')
        return json.loads(p.read_text(encoding='utf-8'))

    def client(self):
        if not self.origin or not self._token:raise ValueError('Configure your own Church UA origin and an existing authorized key through the plugin secure configuration')
        return DraftClient(self.origin,self._token)

    def library(self, relative, existing=False):
        path=self.path(relative,existing)
        if existing and not (path/'library.sqlite3').is_file():raise ValueError('Requested library does not exist')
        if existing:
            database=self.path(str(Path(relative)/'library.sqlite3'),True)
            kb=object.__new__(KnowledgeBase);kb.path=database;kb.owner=self.owner
            kb.db=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
            try:
                if kb.db.execute("SELECT value FROM meta WHERE key='owner'").fetchone()!=(self.owner,):raise PermissionError('Library belongs to another configured owner')
                if kb.db.execute("SELECT value FROM meta WHERE key='library_kind'").fetchone()!=('biblical-faith-life',):raise ValueError('Existing database is not a biblical library')
            except Exception:
                kb.close();raise
            return kb
        return KnowledgeBase(path,self.owner)

    def call(self,name,args):
        if name not in BY_NAME:raise ValueError('Unknown tool')
        check(args,BY_NAME[name]['inputSchema'])
        if name=='bfl_status':return {'server':'biblical-faith-life','version':'2.1.0-claude.3','skills':54,'engines':6,'workflows':5,'workspace_configured':bool(self.workspace),'church_ua_configured':bool(self.origin and self._token),'network_used':False}
        if name=='bfl_validate':return validate(args['envelope'],REF)
        if name=='bfl_draft_preview':return prepare(args['kind'],args['payload'])
        if name.startswith('bfl_library_'):
            kb=self.library(args['library'],name!='bfl_library_ingest')
            try:
                if name=='bfl_library_ingest':return kb.ingest(**args['document'])
                if name=='bfl_library_search':return {'matches':kb.search(args['query'],args.get('limit',10))}
                return kb.get(args['doc_id'],args.get('version'))
            finally:kb.close()
        if name=='bfl_workflow_start':
            p=self.path(args['checkpoint'])
            if p.exists():raise ValueError('A new checkpoint path is required')
            w=Workflow(REGISTRY,args['workflow'],args.get('language','uk'),args.get('stages'));save_checkpoint(p,w.snapshot());return w.snapshot()
        if name in {'bfl_workflow_record','bfl_workflow_status'}:
            w=Workflow.from_snapshot(REGISTRY,self.read_json(args['checkpoint']))
            if name=='bfl_workflow_record':
                if args.get('review',False):w.review(args['stage'],args['content'],args['actor'])
                else:w.record(args['stage'],args['content'],args['actor'])
                save_checkpoint(self.path(args['checkpoint']),w.snapshot())
            return w.snapshot()
        if name=='bfl_visual_export':
            rendered=render(args['spec']);p=self.path(args['output_dir'])
            if p.exists():raise ValueError('Visual export requires a new directory')
            p.mkdir(parents=True,mode=0o700);files=[];errors=[]
            for ext in dict.fromkeys(args.get('formats',['svg','html'])):
                try:
                    target=p/('visual.'+ext)
                    if ext in {'svg','html'}:target.write_text(rendered[ext],encoding='utf-8')
                    else:
                        from bfl.native_exports import export
                        export(args['spec'],target,ext,None)
                    files.append({'format':ext,'path':str(target.relative_to(self.root()))})
                except ImportError:errors.append({'format':ext,'error':'Install the documented optional native-export dependencies before requesting this format'})
                except (ValueError,OSError):errors.append({'format':ext,'error':'Native export failed; inspect the source specification and documented font/dependency requirements'})
            return {'status':'partial' if errors else 'created','files':files,'errors':errors,'sha256':rendered['sha256']}
        if name=='bfl_draft_verify':return self.client().verify(args['receipt'])
        if name=='bfl_draft_submit':
            if args['authorized_draft'] is not True:raise PermissionError('Actual user authorization for this draft is required')
            p=prepare(args['kind'],args['payload']);envelope=args['review_envelope']
            report=validate(envelope,REF)
            if report['status']!='pass':raise ValueError('The review envelope has failed or pending gates')
            if envelope.get('church_ua_request')!={'kind':args['kind'],'payload_sha256':p['payload_sha256']}:raise ValueError('The full request differs from the reviewed payload')
            client=self.client()
            digest=hashlib.sha256((self.origin+'|'+args['kind']+'|'+p['payload_sha256']).encode()).hexdigest()
            marker=self.path('.bfl/draft-attempts/'+digest+'.json');marker.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            try:
                with marker.open('x',encoding='utf-8') as f:
                    os.chmod(marker,0o600);json.dump({'status':'attempt_recorded','payload_sha256':p['payload_sha256']},f);f.flush();os.fsync(f.fileno())
            except FileExistsError:raise ValueError('An attempt for this exact draft already exists. Reconcile it in Church UA before any retry') from None
            # Persist before sending: a process or transport failure must not silently permit a duplicate POST.
            try:receipt=client.submit(args['kind'],args['payload'],authorized=True)
            except Exception:raise RuntimeError('Draft outcome requires reconciliation. Do not retry; the attempt marker is retained') from None
            save_checkpoint(marker,dict(receipt,status='created_pending_readback'))
            try:receipt=client.verify(receipt)
            except RuntimeError:return dict(receipt,readback_pending=True,do_not_resubmit=True)
            save_checkpoint(marker,receipt);return receipt
        raise ValueError('Unknown tool')

def serve(adapter,source=None,sink=None):
    source=source or sys.stdin.buffer;sink=sink or sys.stdout.buffer;initialized=False
    def write(message):
        raw=json.dumps(message,ensure_ascii=True,allow_nan=False,separators=(',',':')).encode('utf-8')
        if len(raw)>MAX_MESSAGE:raw=json.dumps({'jsonrpc':'2.0','id':message.get('id'),'error':{'code':-32603,'message':'Response exceeds the supported MCP message size'}}).encode()
        sink.write(raw+b'\n');sink.flush()
    while True:
        raw=source.readline(MAX_MESSAGE+1)
        if not raw:break
        if len(raw)>MAX_MESSAGE:
            write({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'MCP message is too large'}});break
        try:request=json.loads(raw.decode('utf-8'),parse_constant=lambda _:(_ for _ in ()).throw(ValueError()))
        except (ValueError,UnicodeDecodeError,RecursionError):
            write({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid UTF-8 JSON message'}});continue
        if not isinstance(request,dict) or request.get('jsonrpc')!='2.0' or not isinstance(request.get('method'),str):
            write({'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Invalid JSON-RPC request'}});continue
        # Notifications cannot execute side-effecting tools or create responses.
        if 'id' not in request:continue
        rid=request['id'];method=request['method'];params=request.get('params',{})
        if type(rid) not in (int,str) or not isinstance(params,dict):
            write({'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Invalid request ID or parameters'}});continue
        response={'jsonrpc':'2.0','id':rid}
        if method=='initialize':
            requested=params.get('protocolVersion');version=requested if isinstance(requested,str) and requested in {'2024-11-05','2025-03-26','2025-06-18','2025-11-25'} else '2025-11-25'
            response['result']={'protocolVersion':version,'capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'biblical-faith-life','version':'2.1.0-claude.3'}};initialized=True
        elif method=='ping':response['result']={}
        elif not initialized:response['error']={'code':-32002,'message':'Initialize the MCP session before calling tools'}
        elif method=='tools/list':response['result']={'tools':TOOLS}
        elif method=='tools/call':
            try:
                with contextlib.redirect_stdout(io.StringIO()):value=adapter.call(params.get('name'),params.get('arguments',{}))
                response['result']={'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,allow_nan=False)}],'isError':False}
            except (ValueError,PermissionError,RuntimeError,KeyError,TypeError) as error:
                message=str(error) if not isinstance(error,(KeyError,TypeError)) else 'Invalid tool arguments or missing record'
                # Do not return credentials even if a lower layer were to include one in an error.
                if adapter._token:message=message.replace(adapter._token,'<redacted>')
                response['result']={'content':[{'type':'text','text':message}],'isError':True}
            except Exception:
                response['result']={'content':[{'type':'text','text':'Operation failed; check workspace access, input format and optional dependencies. No automatic retry was performed.'}],'isError':True}
        else:response['error']={'code':-32601,'message':'Method not found'}
        write(response)

if __name__=='__main__':
    # These exact variables are set only by the declared MCP server env bindings.
    # No ambient provider, shell-profile, keychain or credential-file lookup is used.
    serve(Adapter(os.environ.get('BFL_WORKSPACE',''),os.environ.get('BFL_OWNER','local-owner'),os.environ.get('BFL_CHURCH_UA_ORIGIN',''),os.environ.get('BFL_CHURCH_UA_KEY','')))
