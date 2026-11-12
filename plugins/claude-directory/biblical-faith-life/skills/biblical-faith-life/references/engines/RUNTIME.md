# Local runtime usage

Use Python 3.9 or newer. The helper is `skills/biblical-faith-life/scripts/bfl_cli.py` relative to the plugin root. It uses only Python's standard library. Run it from a local executor; a chat-only host can follow the skills but cannot claim to have run these helpers. No remote server, account connection, persistent worker, or scheduler is installed by this package.

## Evidence validation

`python3 skills/biblical-faith-life/scripts/bfl_cli.py validate artifact.json`

The artifact contract is specified in CONTRACT.md. The review hash is computed with `bfl.engines.content_hash(artifact)` and covers every field except `review`. The source hash is SHA-256 of exact UTF-8 text. For a Church UA submission include `church_ua_request` with `kind` and the complete prepared `payload_sha256` before review. Changing a title, body, tags, visibility, language, or plan data invalidates that binding.

Exit 0 means internal structural checks passed; exit 2 means failed or pending checks. Record review evidence only after it actually happened. Valid source hashes do not authenticate a website, prove an excerpt supports an inference, or verify that an independent reviewer exists. Prompt text must never authorize its own publication. An actual reviewer must inspect the raw sources, conclusion, exceptions, manuscript and original request.

## Private knowledge library

`python3 skills/biblical-faith-life/scripts/bfl_cli.py kb-ingest document.json --library /authorized/private/path --owner LOCAL_OWNER`

Document JSON contains `title`, `content`, `language`, `locator`, optional `metadata`, and optional `doc_id` for a new immutable version. For private material explicitly set `private=true` and `consent=true` only after the user's real consent. The helper preserves original text, locator, metadata and content hash. Same-content imports retain distinct document identities and source metadata while returning a duplicate_of reference. Repeating the current version with the same document ID and metadata is idempotent. Restoring an older body or changing metadata creates a new immutable current version. Privacy and consent must be actual booleans. Existing library ownership and complete schema are checked before changes; an unrelated database is never adopted from its owner row alone.

`python3 skills/biblical-faith-life/scripts/bfl_cli.py kb-search "покаяння" --library /authorized/private/path --owner LOCAL_OWNER`

Retrieval matches normalized Unicode terms and ranks latest document versions by matched terms. It returns exact original excerpts and version locators. It does not perform semantic embedding search or establish the truth of a retrieved statement. The owner binding and OS permissions protect a local library; they are not authentication for a remote multi-tenant service. Keep it local. The library is not encrypted; use the OS's protected storage for sensitive material. Never ingest confidential pastoral data by default.

## Workflow records

Import `Workflow` from `bfl.workflows`, load `references/registry.json`, and create it with a registered workflow slug and language. `record(stage, content, actor)` preserves stage output and invalidates all later outputs after an edit. `review(stage, content, reviewer)` requires a reviewer distinct from authors of the underlying non-review inputs and binds every such input hash. `snapshot()` returns an immutable serializable checkpoint with stage evidence. `Workflow.from_snapshot(registry, saved)` revalidates stage order, hashes, author separation and review bindings before resuming; saved status never grants approval.

`python3 skills/biblical-faith-life/scripts/bfl_cli.py workflow-start sermon-studio --output /new/authorized/state.json`

`python3 skills/biblical-faith-life/scripts/bfl_cli.py workflow-record /authorized/state.json --stage deep-exegesis --text-file /authorized/exegesis.txt --actor AUTHOR_ID`

Use `--review` for actual review records and a distinct reviewer. `workflow-status STATE.json` revalidates a saved checkpoint. Research Laboratory may select `--stages deep-exegesis interpretation-review` when other specialists are irrelevant; it cannot omit the initial exegesis or independent final review. Checkpoint writes use atomic replacement with private temporary-file permissions. Save state only inside the user's authorized local workspace. A completed stage record proves neither that a model was invoked nor that its output was correct; retain actual execution evidence.

## Visual exports

`python3 skills/biblical-faith-life/scripts/bfl_cli.py visual visual-spec.json --output /new/output/directory`

The spec contains `kind` (`map`, `timeline`, `comparison`, `reconstruction`, `slides`), `title`, `description`, `language`, and `items`. Each item contains `label`, `detail`, `source`, and `certainty` (`text`, `historical`, `inferred`, `reconstruction`, `uncertain`). Map items need source-backed `lat`/`lon`; timeline items need numeric `start`/`end` with a stated calendar convention. A reconstruction must label uncertainty. Optional `elements` provide bounded rect/line/circle geometry in 0–100 percentage coordinates; every element needs a `source_item` index into the evidence legend. Rectangles use x/y/width/height, lines x/y/x2/y2, circles x/y/r. Dashed geometry signals reconstruction or uncertainty. Timelines render source-linked date-range bands. The map is a coordinate plot with an approximate projection and source legend, not an archaeological basemap. Other modes render source-linked teaching panels; slides export as HTML storyboards. Render and inspect before delivery. Native PDF and PowerPoint exports are available with optional dependencies pinned in `scripts/native-export-requirements.txt`. Add `--formats svg html pdf pptx` to the visual command. A Unicode TrueType font is required; supported system font paths are detected or supplied explicitly with `--font`. No package is installed automatically. Native PDF embeds the chosen font; PowerPoint keeps evidence text, data diagrams and source notes editable and requires a compatible installed font at display time. Full original labels, descriptions and sources are retained across automatically paginated pages. Diagram overviews are separate from numbered evidence pages. The helper creates files; render and inspect the actual exports before claiming visual verification. Raster artwork still requires an appropriate available host image tool, and every historical reconstruction must be labeled.

## Church UA drafts

Read [verified API notes](../church-ua-api.md) before a write. Preview without network access:

`python3 skills/biblical-faith-life/scripts/bfl_cli.py draft-preview payload.json --kind article`

After actual user authorization, configured scoped key, and a completed independent review envelope:

`python3 skills/biblical-faith-life/scripts/bfl_cli.py draft-submit payload.json --kind article --origin https://VERIFIED_APP_ORIGIN --review-envelope artifact.json --authorized-draft`

The runtime reads `CHURCH_UA_AGENT_KEY` from the process environment. Set it through the host's secret facility, never a source file. Never print the environment or token. Origin must be the actual user-verified application origin. No key is included in the candidate.

The adapter supports articles, sermon manuscripts as articles, reading plans, class/lesson shells, and devotionals. It rejects publication controls, alternate congregation IDs, global scope, unknown fields and redirects. It submits exactly once. On an uncertain response reconcile in the app before any retry. The returned receipt's ID and draft-state fields can be checked against the bounded recent listing if the key also has read scope. The listing omits full body data, so `content_readback_verified` remains false. It does not certify body equality, all translations, or database row-level security. Human review and publication remain in the app console. Do not infer publication authorization from draft authorization.
