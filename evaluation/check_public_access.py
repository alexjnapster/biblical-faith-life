from urllib.request import Request,urlopen
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent.parent.parent/'outputs/quality-upgrade.nosync'
rows=[]
urls=['https://alexjnapster.github.io/biblical-faith-life/'+p for p in ['', 'privacy.html','terms.html','support.html','demo-public-sources.html']]
for url in urls:
 try:
  with urlopen(Request(url,headers={'User-Agent':'BFL-Quality-Verification/1.0'}),timeout=25) as r:
   b=r.read(2_000_000);rows.append({'url':url,'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'ok':r.status==200,'scope':'GET availability; video playback and legal content not certified'})
 except Exception as e:rows.append({'url':url,'ok':False,'error':str(e)[:300]})
endpoint='https://biblical-faith-life-public-sources.rodichev-fam-1261.chatgpt.site/api/public-research/mcp'
def rpc(method,params={}):
 data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
 with urlopen(Request(endpoint,data=data,headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','User-Agent':'BFL-Quality-Verification/1.0'}),timeout=25) as r:return json.load(r)
try:
 tools=rpc('tools/list')['result']['tools'];names=sorted(t['name'] for t in tools)
 rows.append({'check':'anonymous_live_tools','ok':names==['bfl_catalogue','bfl_read_unit','bfl_search_sources','bfl_sections'],'tools':names})
 cat=rpc('tools/call',{'name':'bfl_catalogue','arguments':{}})['result'];parsed=json.loads(cat['content'][0]['text'])
 rows.append({'check':'anonymous_live_catalogue','ok':len(parsed['sources'])==12,'source_count':len(parsed['sources'])})
 section=rpc('tools/call',{'name':'bfl_sections','arguments':{'source_id':'source-1'}})['result'];units=json.loads(section['content'][0]['text'])['sections']
 rows.append({'check':'live_sections','ok':bool(units)})
 page=rpc('tools/call',{'name':'bfl_read_unit','arguments':{'source_id':'source-1','unit_id':units[0]['unit_id'],'limit':2}})['result'];page=json.loads(page['content'][0]['text'])
 rows.append({'check':'live_read_unit','ok':page['complete_unit'] is False and page['next_offset']==2})
 search=rpc('tools/call',{'name':'bfl_search_sources','arguments':{'query':'покаяння','limit':2}})['result']
 rows.append({'check':'live_search','ok':search.get('isError') is False})
 denied=rpc('tools/call',{'name':'bfl_draft_submit','arguments':{}})['result']
 rows.append({'check':'live_public_write_tool_refused','ok':denied.get('isError') is True})
except Exception as e:rows.append({'check':'live_mcp','ok':False,'error':str(e)[:300]})
receipt={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':rows,'scope':'Actual anonymous HTTP requests; not the exact submitted ChatGPT App installation'}
(OUT/'public-access.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
