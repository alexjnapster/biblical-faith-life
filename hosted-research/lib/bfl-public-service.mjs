// Deliberately public, read-only corpus interface. Never forwards an audit,
// identity, credential, private library, filesystem path, URL or write action.
import { rpc } from './bfl-service.mjs';

export const PUBLIC_VERSION = '0.1.1';
const PUBLIC_TOOLS = new Set(['bfl_catalogue', 'bfl_sections', 'bfl_search_sources', 'bfl_read_unit']);
const MAX_BYTES = 32 * 1024;
export async function publicRpc(message) {
  const request = message?.method === 'tools/call' && !PUBLIC_TOOLS.has(message?.params?.name)
    ? { ...message, params: { name: '__unsupported_public_operation__', arguments: {} } }
    : message;
  // Authentication is never inferred from headers or supplied arguments.
  const result = await rpc(request, false);
  if (result?.result?.tools) {
    result.result.tools = result.result.tools.filter(tool => PUBLIC_TOOLS.has(tool.name))
      .map(tool => ({ ...tool, securitySchemes: [{ type: 'noauth' }] }));
  }
  if (message?.method === 'initialize' && result?.result?.serverInfo) {
    result.result.serverInfo = { name: 'biblical-faith-life-public-sources', version: PUBLIC_VERSION };
    result.result.instructions = 'Read-only access to twelve already-public publisher-supplied governing documents. This fixed corpus is not live academic search, private user data or a Bible translation service. Search locates evidence; read complete relevant argument units before concluding. No accounts, manuscript audits, private-library operations or publishing are available here. Do not send manuscripts or personal records. The existing signed-in audit service is separate and remains protected.';
  }
  return result;
}

const json = (body, options = {}) => Response.json(body, { ...options, headers: { 'cache-control': 'no-store', ...options.headers } });
export async function publicPost(request) {
  const origin = request.headers.get('origin');
  if (origin !== null && origin !== new URL(request.url).origin) {
    return json({ error: 'Origin is not allowed' }, { status: 403 });
  }
  const protocol = request.headers.get('mcp-protocol-version');
  if (protocol !== null && !['2025-03-26', '2025-06-18', '2025-11-25'].includes(protocol)) {
    return json({ error: 'Unsupported MCP protocol version' }, { status: 400 });
  }
  const type = (request.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
  if (type !== 'application/json') return json({ error: 'Use application/json' }, { status: 415 });
  const length = request.headers.get('content-length');
  if (length !== null && (!/^\d+$/.test(length) || Number(length) > MAX_BYTES)) {
    return json({ error: 'Request too large or invalid length' }, { status: 413 });
  }
  const reader = request.body?.getReader();
  if (!reader) return json({ error: 'A JSON-RPC body is required' }, { status: 400 });
  const chunks = []; let size = 0;
  try {
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > MAX_BYTES) {
      await reader.cancel();
      return json({ error: 'Request too large' }, { status: 413 });
    }
    chunks.push(value);
  }
  } catch {
    return json({ error: 'Unable to read request body' }, { status: 400 });
  } finally {
    reader.releaseLock();
  }
  const body = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
  let message;
  try { message = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(body)); }
  catch { return json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Invalid UTF-8 JSON' } }, { status: 400 }); }
  const result = await publicRpc(message);
  if (result === null) return new Response(null, { status: 202, headers: { 'cache-control': 'no-store' } });
  return json(result, { headers: { 'cache-control': 'no-store' } });
}
