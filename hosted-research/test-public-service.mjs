import assert from 'node:assert/strict';
import { publicRpc, publicPost } from './lib/bfl-public-service.mjs';
import { rpc, catalogue } from './lib/bfl-service.mjs';
let passed = 0;
const check = (value, message) => { assert.ok(value, message); passed++; };
const msg = (name, args = {}) => ({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } });
const list = await publicRpc({ jsonrpc: '2.0', id: 1, method: 'tools/list' });
assert.deepEqual(list.result.tools.map(t => t.name).sort(), ['bfl_catalogue', 'bfl_read_unit', 'bfl_search_sources', 'bfl_sections']); passed++;
check(list.result.tools.every(t => t.annotations.readOnlyHint === true && t.annotations.destructiveHint === false && t.annotations.openWorldHint === false), 'Public operations are read-only and bounded');
check(list.result.tools.every(t => t.securitySchemes[0].type === 'noauth'), 'No private account is requested');
const init = await publicRpc({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26' } });
check(init.result.serverInfo.name === 'biblical-faith-life-public-sources' && init.result.instructions.includes('Do not send manuscripts'), 'Public scope is explicit');
const cat = JSON.parse((await publicRpc(msg('bfl_catalogue'))).result.content[0].text);
assert.deepEqual(cat.sources, catalogue()); passed++;
check(cat.sources.length === 12, 'All twelve public documents, no extra collection');
const sections = JSON.parse((await publicRpc(msg('bfl_sections', { source_id: 'source-1' }))).result.content[0].text);
const unit = sections.sections[0];
const page = JSON.parse((await publicRpc(msg('bfl_read_unit', { source_id: 'source-1', unit_id: unit.unit_id, limit: 2 }))).result.content[0].text);
check(page.end_line - page.start_line === 1 && page.complete_unit === false && page.next_offset === 2, 'Bounded page and honest completeness');
check((await publicRpc(msg('bfl_search_sources', { query: 'покаяння', limit: 2 }))).result.isError === false, 'Public source search works');
for (const name of ['bfl_audit_evidence', 'bfl_draft_submit', 'bfl_library_get', 'bfl_workflow_start', '__proto__']) {
  const response = await publicRpc(msg(name, { artifact: { private_record: 'SYNTHETIC-DO-NOT-ECHO' }, authenticated: true }));
  check(response.result.isError === true && !JSON.stringify(response).includes('SYNTHETIC-DO-NOT-ECHO'), `No protected forwarding or argument echo: ${name}`);
}
check((await rpc(msg('bfl_audit_evidence', { artifact: {} }), false)).result.isError === true, 'Original audit still rejects an unauthenticated caller');
for (const args of [{ source_id: '../secret' }, { source_id: 'source-1', extra: true }, { source_id: 'source-1', limit: 999999 }]) {
  check((await publicRpc(msg('bfl_sections', args))).result.isError === true, 'Source traversal, unknown arguments and overlong pages rejected');
}
const endpoint = 'https://example.invalid/api/public-research/mcp';
const post = (body, headers = { 'content-type': 'application/json' }) => publicPost(new Request(endpoint, { method: 'POST', headers, body }));
check((await post(JSON.stringify(msg('bfl_catalogue')))).status === 200, 'Anonymous HTTP catalogue works');
check((await post('{')).status === 400, 'Malformed JSON rejected');
check((await post(new Uint8Array([0xff]))).status === 400, 'Invalid UTF-8 rejected');
check((await post('{}', { 'content-type': 'text/plain' })).status === 415, 'Incorrect content type rejected');
check((await post(' '.repeat(32769))).status === 413, 'Stream byte bound enforced');
check((await post('{}', { 'content-type': 'application/json', 'content-length': '-1' })).status === 413, 'Invalid declared length rejected');
check((await post(JSON.stringify({ jsonrpc: '2.0', method: 'tools/call', params: { name: 'bfl_audit_evidence' } }))).status === 202, 'Notifications do not execute protected actions');
console.log(JSON.stringify({ passed, scope: 'Public-only profile and HTTP boundary; original protected endpoint unchanged' }));
