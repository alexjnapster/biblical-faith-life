# Quality upgrade checkpoint — 25 October 2026

These are local, unsubmitted candidates. The workspace baseline is the actual account release `Plugin_b1c6103546e081918ec49ae254fa4b20`, version `2.1.0-rc.4`, release `pluginrel_6ad37bff8ba88191852ad75559b57a90`. Its complete rollback archive is retained outside the repository. The public repository baseline is commit `dc2e1c29ebff3b19afe3dd97f1485e460fbf2b34`.

The workspace candidate is `../workspace-candidate` at `2.1.0-rc.5`. Local GitHub-source candidates are ChatGPT `2.1.0-rc.8` and Claude `2.1.0-claude.5`. The GitHub ChatGPT source is not the exact submitted public-sources `2.2.0-rc.6` package. No claim of synchronization with that submitted package is made. No remote push, account update, directory cancellation, resubmission or deployment was performed in this checkpoint.

All 54 skill entrypoints receive a link to the same production workflow and a skill-specific acceptance paragraph. General skill acceptance criteria are separate from case-specific expected results, to avoid embedding test answers or fixed figures in normal instructions. The original instruction bodies and all governing source bytes are preserved. The workspace metadata's outdated 20-skill count is corrected to 54; original prompts, identity and integrations are retained. The production workflow improves source retrieval, substantive revision, genre fidelity, proportionate explanation, verifiable objective checks, actual separate-review evidence and export inspection. These are instructions, not a host-enforced guarantee of compliance.

`cases.json` specifies 162 core cases: one ordinary, demanding and misleading task per skill. `extended-cases.json` adds 12 paired output-language cases and eight repeats of consequential cases. The core cases are Ukrainian. Paired language cases test the same English-worded task with English/Russian output instructions; they do not establish native-language prompt robustness. No sample is marked passed simply for existing. `rubric.json` gives seven dimensions, critical failure gates and evidence requirements. `assess_review.py` validates review records and exact content binding; it does not authenticate a reviewer or establish factual truth. There is no overall 100-point score.

## Reproduce locally

Use Python 3.12 or newer for the developer evaluation scripts. The unchanged plugin runtime still supports Python 3.9. From this repository:

- `python3 -m unittest discover -s tests -v` — requires sibling `baseline` and `workspace-candidate` directories reconstructed from the retained rollback archive and `build_candidates.py`.
- `node hosted-research/test-service.mjs` — protected source-service regression cases.
- `node hosted-research/test-public-service.mjs` — public-profile and HTTP-boundary cases.
- `claude plugin validate plugins/claude/biblical-faith-life --strict` — package validation.
- `python3 evaluation/check_public_access.py` — actual anonymous network checks, clearly separate from official host installation tests.
- `python3 evaluation/run_claude.py --ids textual-criticism__ordinary trauma-informed-ministry__ordinary visual-bible-educator__ordinary visual-education-studio__ordinary youth-teaching__ordinary` — actual Claude subject tests, only after quota is available. No provider override, quota evasion or new key is used. This starts with the five historically unfinished skills but produces new candidate samples, not replacements for inaccessible old samples.

The runner stops after a failed/quota-blocked case, preserves completed cases, retains private traces with mode 0600 and writes sanitized receipts. It uses read-only model tools, disables MCP for this prose-only suite and does not claim to test exports, authorized Church UA writes or declared MCP functionality. Adapter tests exercise the latter separately with synthetic inputs. All new model answers require substantive review and source checks before release. Use only sanitized artifacts for any public evidence; do not publish private traces.

## Actual checks and blockers

43 Python checks passed, including 24 declared-MCP adapter checks, five existing layout/source-preservation checks, seven new candidate/coverage checks and seven review-record regression checks. Protected service: 46 passed. Public boundary: 24 passed. Claude strict validation passed. These cover implementation and preservation, not answer quality.

Actual anonymous GETs returned 200 for homepage, privacy, terms, support and the public-source demo page. Actual public MCP POST calls with an identified client succeeded for tool discovery, catalogue, sections, source reading and search; a public write-tool request was refused. An earlier request with Python's default client identification received 403; that observation is retained. No root cause for that differential has been established. Do not infer universal reviewer reachability or video playback from these checks.

Claude's actual first subject request returned HTTP 429, `usage_limit_reached`, with no generated answer or real model response. The provider reported a weekly reset at October 30, 16:00 Europe/Kiev. The runner stopped. None of the 182 candidate cases has completed generation or semantic evaluation. The exact public ChatGPT App's native tests, fresh workspace host tests, actual export checks, human specialist review and live authenticated Church UA validation remain pending. The installed .4 and active marketplace reviews remain unchanged.
