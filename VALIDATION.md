# Claude package audit — November 12, 2026

Claude 2.1.0-claude.6 fixes adapter defects found by a live stdio session over all 12 tools: unset options arriving as empty values or literal `${user_config.NAME}` templates were reported as configured; search returned unbounded full text; missing records and malformed receipts gave vague errors; a failed export left a blocking empty directory. Seven regression tests were added (41 Python tests pass; 47 hosted-service and 24 public-interface checks unchanged). `claude plugin validate` in Claude Code 2.1.322 passes for the marketplace and the plugin, and the plugin installs from the repository marketplace with 54 skills and one MCP server. PDF and PowerPoint export produced real files with the pinned optional packages. Cowork starts a local server only when every plugin option it references has a default, and it does not prompt for values. Up to 2.1.0-claude.5 two options had no default, so the publisher's Claude desktop app 5.1231 reported the server as not started (`user_config_unsupported`). From 2.1.0-claude.6 every option has a default, which is intended to let the server start in Cowork with defaults only: status, validation and offline draft preview work there, while storage tools need a workspace that currently can be set only in Claude Code. This Cowork start has not yet been observed. Not observed: Claude Code launching the server (the audit environment disables plugin-launched local servers), a fresh generation run, and any live Church UA request. Skill text and the 12 governing sources are byte-identical to the pinned fixtures.

# Audit — November 10, 2026

Observed directly in the authenticated OpenAI publisher portal: public no-auth app `asdk_app_6ad5e6871a688191b100a2b201db4643`, plugin package name `biblical-faith-life-public-sources`, version **2.2.0-rc.6**, **In review**, **Not published**, MCP **Configured**. All 54 listed skills show **Checks passed**. The current portal observation supersedes older statements below that this public app was not submitted. The two other OpenAI records show authenticated app 2.2.0-rc.4 Not submitted / Configuration incomplete, and skills-only 2.1.0-rc.7 Needs attention. These records must remain distinct.

The Claude Directory management page for Oleksandr Rodichev showed **0 submissions**. A previous package validation report is not a confirmed current marketplace submission. No plugin-specific Anthropic review message was established by the targeted email investigation.

OpenAI Support case 17580361 last replied November 7 asking for Review/Submission screenshots and a private-App Connect recording. A fresh targeted mail search found no newer response. The current active review was preserved. Portal release ZIP export did not complete; browser control subsequently timed out. The exact saved public package, its owner preview and requested support recording are therefore unverified. No legal attestations were made, no active review was cancelled, and no new public submission or publication is claimed by this audit.

## Source corrections and reproducible checks

Canonical starting repository commit: `dc2e1c29ebff3b19afe3dd97f1485e460fbf2b34`. Next source candidates: ChatGPT 2.1.0-rc.8 and Claude 2.1.0-claude.5. This older source lineage is not represented as the source of the public 2.2.0-rc.6 package.

- 34 Python tests pass: local adapter, source preservation, every skill link, ChatGPT reference compaction, and invalid reviewer identities in both Python runtimes.
- 47 hosted-service tests pass, including malformed reviewer identities and whitespace-only attempts to distinguish the author from the reviewer.
- 24 public-only profile and HTTP-boundary checks pass.
- All 12 independently pinned governing-source SHA-256 hashes match in both packages; all 54 skill entrypoints remain. ChatGPT removes exactly 285 byte-identical reference copies and rewires only their links. No governing belief text was edited.
- `tools/build_release.py` builds deterministic separate ZIPs and rereads their inventory and CRCs. It performs no upload, attestation or submission.
- A read-only GitHub Actions workflow runs the same checks on future pushes and pull requests.
- The four listing URLs returned public HTTP 200 pages with the correct titles and publisher; their site, support contact, privacy coverage and terms were inspected from canonical source. Legal adequacy is not certified.

Run from repository root:

```sh
python3 -m unittest discover -s tests -v
node hosted-research/test-service.mjs
node hosted-research/test-public-service.mjs
python3 tools/build_release.py --output /tmp/bfl-release
```

The new behavior was tested locally, not in a fresh Claude/ChatGPT generation run. The hosted service code change is not deployed by building a ZIP or pushing this repository. No independent semantic quality review or live authenticated Church UA write was performed. No score or perfect-answer guarantee is asserted. The historical 102-case engineering suite referenced below is absent from this repository and was not rerun in this audit.

## Historical evidence (not current release verification)

# Validation evidence and limits

The Claude 2.1.0-claude.4 candidate contains a declared local MCP server and all 54 skills. Directory feedback on .3 reported that validation could not finish because there was too much to read. Version .4 removes 285 byte-identical reference copies and points their 19 skill entrypoints to the existing readable shared library. All 12 governing source documents retain their exact bytes. The package falls from 21,828,603 to 2,543,086 uncompressed bytes (118 files). No doctrine or unique reference document was removed.

Run `python3 tests/test_reference_layout.py` from this repository: five checks verify all skill identities, governing hashes, every relocated reference, the precise permitted skill link rewrites, and all relative skill links. The independently pinned .3 ZIP hash and preservation fixtures are outside the plugin folder. The 24 MCP adapter tests also pass against .4 on Python 3.9; run `python3 tests/test_claude_mcp.py`. These use synthetic data and mock external draft transport, not a live congregation request. The retained engineering workspace's 102-case core suite also passes against .4 with reference relocation explicitly accounted for. Earlier .3 adapter checks passed on Python 3.9 and 3.12.

Actual Claude Code runs connected the declared server through manifest userConfig, stored and retrieved synthetic documents, persisted a workflow, refused self-review, generated real SVG/HTML files and prepared an offline Church UA draft. The first run exposed two unclear input schemas. The final schema run succeeded on its first calls. The configured host reported claude-opus-5-5; this is a configured-provider test, not proof of an independently verified Anthropic network route. Seven core modules also passed the existing 102-case suite in the retained engineering workspace.

A further actual .4 host run invoked the devotional skill, read the relocated shared guidance and governing sources, called the .4 MCP status tool and wrote a 276-word Ukrainian devotional on Luke 15:1–10. The run completed successfully without permission denials. Its bounded manual review checked coherent Ukrainian prose, the passage's complaint/parables/repentance setting and explicit paraphrase rather than an invented verified quotation. This is one observed sample, not an unrestricted answer-quality claim.

OpenAI publisher identity is verified. The public skills-only draft has 54 passing skill checks, but OpenAI currently blocks new skills-only submissions. A genuine hosted research service passes 46 reproducible cases (`node hosted-research/test-service.mjs`). Eight bounded development-host cases were executed against private plugin 1.1.1/service 0.1.1, and their actual browser recording is available at https://alexjnapster.github.io/biblical-faith-life/demo.html. A new MCP-declaring public draft was accepted without the skills-only gate; all 54 skill checks pass. Its five positive and three negative review cases, all-country targeting and actual demo URL were verified in the saved portal form. Its portal-created App association differs from the existing canonical Sites App; public connection, reviewer credentials, exact saved-submission tests and owner attestations remain unresolved. It has not been submitted for review. A deployment, package validation, public GitHub repository or project installation is not official marketplace approval.

Live authenticated Church UA tests remain unverified because no existing authorized key was available. No new key was created. An output file or structural evidence-gate result does not certify semantic accuracy, sound exegesis, actual review independence, pastoral suitability, layout quality or perfect answers. Official directory legal attestations and review decisions remain separate gates.
