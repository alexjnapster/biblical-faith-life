# Inspected Church UA Agent API

Local source inspection, 2026-10-16. Repository remote: `git@github.com:alexjnapster/uachurches-19c86aba.git`. Observed HEAD: `4974258abebeb47f57df01e888226752f886d45a`. A local checkout and its contract do not prove that the production deployment has the same version.

Owning sources: `src/lib/api/v1-content.server.ts`, `src/routes/api/public/v1/content/{articles,reading-plans,classes,devotionals}.ts`, `src/lib/api/api-key.server.ts`, and `docs/api/AGENT_API.md`.

All endpoints use `/api/public/v1/content/` and a Bearer `cc_live_...` Agent API key. POST needs the resource's write scope; GET needs its read scope. The server verifies the key, scope, rate limit, body size and congregation. Caller-selected global scope is supported only for super-admin-owned keys by the application; this candidate adapter intentionally does not expose that operation. It never touches the database or changes policies.

| Kind | Endpoint | Scope prefix | Actual behavior |
|---|---|---|---|
| Article; sermon manuscript | articles | articles | Creates article plus first translation; forced draft and pending review |
| Reading plan | reading-plans | plans | Creates unpublished plan, pending review, structured `plan_data` |
| Class; lesson shell | classes | classes | Creates unpublished class shell; lesson bodies completed in app |
| Devotional | devotionals | devotionals | Creates draft; key must have a creator for authorship |

Articles accept title (3–300), summary (up to 2000), body (up to 200000), language uk/en/ru, type article/news/blog/study, visibility public/approved_members/members/private, and up to 20 tags. Adapter default visibility is private. Reading plans require title (3–200) and days (1–365); description up to 5000, tags and object `plan_data` are optional. Classes accept title (3–200), description (up to 5000), language, days_count (1–366), starts_on and tags. Devotionals require title (3–200), body (20–20000); scripture_reference up to 200 and publish_date are optional. String bounds follow JavaScript UTF-16 length; total JSON body cap is 256 KiB.

Successful POST: HTTP 201 with `ok=true`, `status=draft_pending_review`, and `article`, `plan`, `class`, or `devotional` containing the created ID. The adapter verifies the exact draft fields returned for that endpoint; it never defaults a missing status to safe.

GET returns a recent list of at most 20 for the key's congregation. Articles list status, approval_status and is_global; plans list is_published, approval_status and is_global; classes list is_published and is_global; devotionals list status. These are state checks, not full-content readbacks. Endpoint responses do not expose a full revision API or a multi-translation write contract. The candidate preserves local version history; it does not claim remote revision-history or lesson-body integration.

401/403/409/422/429/500/503 and transport ambiguity stop submission without automatic retry. No publication endpoint is implemented. A live scoped test key and deployed-contract verification are required before production draft integration can be certified. Do not put a key in this file, the archive, screenshots, or test logs.
