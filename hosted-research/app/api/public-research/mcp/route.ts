// A separate public-document API, not the protected Sites /mcp connection.
export { publicPost as POST } from '../../../../lib/bfl-public-service.mjs';
export const dynamic = 'force-dynamic';
export async function GET() {
  return new Response('Use the public, read-only MCP POST endpoint.', {
    status: 405, headers: { Allow: 'POST' },
  });
}
