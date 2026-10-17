#!/usr/bin/env python3
"""Local evidence validation, library, previews and draft submission."""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from bfl.engines import validate
from bfl.knowledge import KnowledgeBase
from bfl.visuals import render
from bfl.church_ua import prepare,DraftClient
from bfl.workflows import Workflow

def save_checkpoint(path,snapshot):
    path=Path(path)
    if path.is_symlink():raise ValueError('Checkpoint target cannot be a symlink')
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,prefix='.bfl-checkpoint-',delete=False) as handle:
            temporary=Path(handle.name);json.dump(snapshot,handle,ensure_ascii=False,indent=2);handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,path)
    finally:
        if temporary is not None and temporary.exists():temporary.unlink()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('validate','visual','draft-preview'):
        p=sub.add_parser(name);p.add_argument('input')
        if name=='visual':
            p.add_argument('--output',required=True);p.add_argument('--formats',nargs='+',choices=['svg','html','pdf','pptx'],default=['svg','html']);p.add_argument('--font')
        if name=='draft-preview':p.add_argument('--kind',required=True)
    for name in ('kb-ingest','kb-search'):
        p=sub.add_parser(name);p.add_argument('--library',required=True);p.add_argument('--owner',required=True)
        if name=='kb-ingest':p.add_argument('input')
        else:p.add_argument('query')
    p=sub.add_parser('draft-submit');p.add_argument('input');p.add_argument('--kind',required=True);p.add_argument('--authorized-draft',action='store_true');p.add_argument('--origin',required=True);p.add_argument('--review-envelope',required=True)
    p=sub.add_parser('workflow-start');p.add_argument('workflow');p.add_argument('--language',default='uk');p.add_argument('--output',required=True);p.add_argument('--stages',nargs='+')
    p=sub.add_parser('workflow-record');p.add_argument('checkpoint');p.add_argument('--stage',required=True);p.add_argument('--text-file',required=True);p.add_argument('--actor',required=True);p.add_argument('--review',action='store_true')
    p=sub.add_parser('workflow-status');p.add_argument('checkpoint')
    args=parser.parse_args();refs=Path(__file__).resolve().parents[1]/'references'
    try:
        data=json.loads(Path(args.input).read_text()) if hasattr(args,'input') else None
        if args.command=='validate':
            r=validate(data,refs);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='pass' else 2
        if args.command=='visual':
            r=render(data);out=Path(args.output)
            if out.suffix:raise ValueError('Output must be a new directory')
            out.mkdir(parents=True,exist_ok=False)
            results=[]
            for ext in dict.fromkeys(args.formats):
                if ext in {'svg','html'}:
                    target=out/('visual.'+ext);target.write_text(r[ext]);results.append({'format':ext,'path':str(target.resolve())})
                else:
                    from bfl.native_exports import export
                    results.append(export(data,out/('visual.'+ext),ext,args.font))
            print(json.dumps({'output':str(out.resolve()),'sha256':r['sha256'],'files':results}))
        elif args.command=='draft-preview':print(json.dumps(prepare(args.kind,data),ensure_ascii=False,indent=2))
        elif args.command in {'kb-ingest','kb-search'}:
            kb=KnowledgeBase(args.library,args.owner)
            try:r=kb.ingest(**data) if args.command=='kb-ingest' else kb.search(args.query)
            finally:kb.close()
            print(json.dumps(r,ensure_ascii=False,indent=2))
        elif args.command=='workflow-start':
            target=Path(args.output)
            if target.exists():raise ValueError('Initial checkpoint must use a new path')
            registry=json.loads((refs/'registry.json').read_text());w=Workflow(registry,args.workflow,args.language,args.stages);save_checkpoint(target,w.snapshot());print(json.dumps(w.snapshot(),ensure_ascii=False,indent=2))
        elif args.command in {'workflow-record','workflow-status'}:
            registry=json.loads((refs/'registry.json').read_text());w=Workflow.from_snapshot(registry,json.loads(Path(args.checkpoint).read_text()))
            if args.command=='workflow-record':
                content=Path(args.text_file).read_text()
                if args.review:w.review(args.stage,content,args.actor)
                else:w.record(args.stage,content,args.actor)
                save_checkpoint(args.checkpoint,w.snapshot())
            print(json.dumps(w.snapshot(),ensure_ascii=False,indent=2))
        elif args.command=='draft-submit':
            raise PermissionError('Use the declared Biblical Faith Life MCP draft tool and secure plugin configuration in this distribution')
        return 0
    except (ValueError,KeyError,PermissionError,RuntimeError,OSError) as e:
        # Validation messages never echo source content, paths to private material, or credentials.
        print(json.dumps({'status':'blocked','error':str(e) if not isinstance(e,OSError) else type(e).__name__}),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
