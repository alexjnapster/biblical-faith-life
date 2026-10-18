# Hosted research implementation and regression evidence

The deployed service exposes five read-only MCP operations: a fixed 12-document catalogue, unit index, source search, paginated source reading and six structural evidence checks. Source hashes are verified by the test suite. These are publisher-supplied governing sources, not independent historical or scientific evidence.

Run `node hosted-research/test-service.mjs` from the repository root with Node 22 or later. The 46 cases include 31 bounded Python/JavaScript comparison fixtures, corpus integrity, pagination, strict argument bounds, JSON-RPC notifications, explicit safety annotations and refusal of an unauthenticated manuscript audit. Results are written beside the test script. They do not prove semantic accuracy, real human review or live congregation integration.

The HTTP route uses the existing Sites-provided `getChatGPTUser` helper and managed OAuth request identity. This directory is an inspectable implementation snapshot, not a standalone hosting or authentication replacement. No credentials, user account records, private ministry data or database are included. The audit checks a supplied envelope transiently. The core does not fetch external URLs, run commands, read arbitrary paths or publish church content.

The digest scheme is bfl-hosted-ecmascript-sorted-json-v1. JavaScript serialization can differ from the older Python digest for some floating-point numbers and object-key orderings; do not treat the two schemes as universally identical. The included fixtures test only their declared bounded cases.

Live demonstration: https://alexjnapster.github.io/biblical-faith-life/demo.html

Official public marketplace publication remains pending. A deployed service or public source repository is not marketplace approval.
