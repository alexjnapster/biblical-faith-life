import { getChatGPTUser } from '../chatgpt-auth';
import { rpc } from '../../lib/bfl-service.mjs';

export const dynamic = 'force-dynamic';
const MAX_BYTES = 512 * 1024;
export async function POST(request: Request) {
  const type = request.headers.get('content-type') || '';
  if (!type.includes('application/json')) return Response.json({ error: 'Use application/json' }, { status: 415 });
  const declared = Number(request.headers.get('content-length') || '0');
  if (!Number.isFinite(declared) || declared > MAX_BYTES) return Response.json({ error: 'Request too large' }, { status: 413 });
  const reader = request.body?.getReader();
  if (!reader) return Response.json({ error: 'A JSON-RPC body is required' }, { status: 400 });
  const chunks: Uint8Array[] = []; let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > MAX_BYTES) { await reader.cancel(); return Response.json({ error: 'Request too large' }, { status: 413 }); }
    chunks.push(value);
  }
  const body = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
  let message;
  try { message = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(body)); }
  catch { return Response.json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Invalid UTF-8 JSON' } }, { status: 400 }); }
  const user = await getChatGPTUser();
  if (message?.method === 'tools/call' && message?.params?.name === 'bfl_audit_evidence' && !user) {
    return Response.json({ error: 'Sign in with ChatGPT before sending a manuscript envelope' }, { status: 401 });
  }
  const result = await rpc(message, Boolean(user));
  if (result === null) return new Response(null, { status: 202 });
  return Response.json(result, { headers: { 'cache-control': 'no-store' } });
}
export async function GET() {
  return new Response('Use the stateless MCP POST endpoint.', { status: 405, headers: { Allow: 'POST' } });
}
