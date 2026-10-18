import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {audit,artifactHash,catalogue,corpusIntegrity,sections,search,readUnit,callTool,rpc,TOOLS} from './lib/bfl-service.mjs';
const results=[];
async function test(name,fn){await fn();results.push({name,status:'passed'});}
const fixtures=JSON.parse(await fs.readFile(new URL('./audit-regression-fixtures.json',import.meta.url),'utf8'));
for(const fixture of fixtures)await test('Python comparison: '+fixture.name,async()=>{
  const result=await audit(fixture.artifact);assert.equal(result.status,fixture.expected_status);
  assert.deepEqual([...new Set(result.findings.map(f=>f.code))].sort(),fixture.expected_codes);
});
await test('All twelve original source digests match',async()=>{assert.equal(catalogue().length,12);assert((await corpusIntegrity()).every(s=>s.ok));});
await test('Unit identifiers are unique including a heading on line one',()=>{
  const listed=sections('source-1',0,60).sections;assert.equal(new Set(listed.map(s=>s.unit_id)).size,listed.length);
});
await test('Search and paginated reading return actual consistent source lines',async()=>{
  const hit=search('repentance',4).hits[0];assert(hit);let offset=0,pages=[];
  while(offset!==null){const page=await readUnit(hit.source_id,hit.unit_id,offset,3);pages.push(page);offset=page.next_offset;assert(pages.length<2000);}
  assert.equal(pages[0].start_line,pages[0].unit_start_line);assert.equal(pages.at(-1).end_line,pages.at(-1).unit_end_line);
  for(let i=1;i<pages.length;i++)assert.equal(pages[i].start_line,pages[i-1].end_line+1);
});
await test('Unknown source cannot become a file read',async()=>{await assert.rejects(()=>readUnit('../../etc/passwd','source-1:1:0'));});
await test('Invalid pagination bounds are refused',async()=>{assert.throws(()=>sections('source-1',-1));await assert.rejects(()=>readUnit('source-1','source-1:1:0',0,10000));});
await test('Audit requires a signed-in caller',async()=>{await assert.rejects(()=>callTool('bfl_audit_evidence',{artifact:fixtures[0].artifact},false));});
await test('Public source tools do not require private user data',async()=>{assert.equal((await callTool('bfl_catalogue',{},false)).sources.length,12);});
await test('Every tool has explicit boolean safety annotations',()=>{assert.equal(TOOLS.length,5);for(const t of TOOLS)for(const k of ['readOnlyHint','destructiveHint','openWorldHint'])assert.equal(typeof t.annotations[k],'boolean');});
await test('Unknown tools and unknown arguments are refused',async()=>{await assert.rejects(()=>callTool('shell_exec',{},true));await assert.rejects(()=>callTool('bfl_catalogue',{origin:'https://unrelated.example'},true));});
await test('MCP handshake, discovery and notifications',async()=>{assert.equal((await rpc({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-11-25'}})).result.serverInfo.name,'biblical-faith-life-research');assert.equal((await rpc({jsonrpc:'2.0',id:2,method:'tools/list'})).result.tools.length,5);assert.equal(await rpc({jsonrpc:'2.0',method:'notifications/initialized'}),null);});
await test('Malformed JSON-RPC and invalid IDs return protocol errors',async()=>{assert.equal((await rpc([])).error.code,-32600);assert.equal((await rpc({jsonrpc:'2.0',id:{},method:'ping'})).error.code,-32600);});
await test('Authenticated MCP calls return actual audit result',async()=>{const r=await rpc({jsonrpc:'2.0',id:3,method:'tools/call',params:{name:'bfl_audit_evidence',arguments:{artifact:fixtures[0].artifact}}},true);assert.equal(JSON.parse(r.result.content[0].text).status,'pass');});
await test('Year zero is refused as an invalid source date',async()=>{const a=structuredClone(fixtures[0].artifact);a.sources[0].accessed_at='0000-01-01';assert((await audit(a)).findings.some(f=>f.code==='source_date'));});
await test('Unpaired surrogate content cannot produce a replacement-character digest',async()=>{await assert.rejects(()=>artifactHash({content:'\ud800'}));});
await test('Hosted hash scheme and compatibility limits are explicit',async()=>{const a=structuredClone(fixtures[0].artifact);a.measurement=1e-6;const r=await audit(a);assert.equal(r.hash_scheme,'bfl-hosted-ecmascript-sorted-json-v1');assert(r.hash_compatibility.includes('floating-point'));assert(r.findings.some(f=>f.code==='stale_review'));});
const evidence={tests:results.length,failures:0,checks:results,scope:'31 paired synthetic Python/hosted audit fixtures plus public-corpus, pagination, schema, identity, Unicode, digest-compatibility and MCP protocol checks. This does not certify source authenticity or semantic quality.'};
await fs.writeFile(new URL('./test-results.json',import.meta.url),JSON.stringify(evidence,null,2));
console.log(JSON.stringify({tests:results.length,failures:0}));
