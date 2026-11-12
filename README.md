# Церква Христова — biblical-faith-life

![Open Bible icon](plugins/claude/biblical-faith-life/assets/icon.png)

Bible study, sermons and teaching grounded in the preserved Church of Christ v9 doctrinal framework. Includes 54 skills, 30 specialist capabilities, six shared engines, a research laboratory, sermon studio, personal biblical knowledge base, visual education studio and draft-first Church UA integration. Ukrainian is the default; English and Russian are supported. Intended for adult teachers, ministers and authors. Local library, persistent workflows and Python exports require a host with an available code executor. Church UA submission requires separately configured authorized access; installation grants no congregation access. AI output needs review and does not guarantee theological, historical or factual accuracy.

Publisher: Oleksandr Rodichev. Version: 2.1.0-claude.7. License: MIT for the publisher-provided software and documentation; quoted third-party material and trademarks retain their existing rights.

## Installation

In Claude open Customize → Plugins → Add plugin → Upload plugin and choose the Claude ZIP without extracting it. Account and administrator restrictions may apply. For Claude Code, run `/plugin marketplace add alexjnapster/biblical-faith-life`, then `/plugin install biblical-faith-life@biblical-faith-life`. Once the public listing is approved and published, install from that listing.

Claude Code one-step installation (2.1.275 or later):

`/plugin install biblical-faith-life --marketplace alexjnapster/biblical-faith-life`

## Start using it

Select the plugin in a new conversation and request a Bible study, sermon, lesson or article. Specify the passage, audience, language and requested format. Ask for source verification when wording or historical claims matter. Full local tools require Python 3.9 or later and a code-capable host; optional PDF/PowerPoint exports require the documented dependencies. Libraries and workflow files belong in your own workspace outside the installed plugin folder. Preserve those files before uninstalling or replacing a local installation.

## Access and data

No API key, congregation access, private library or ministry record is bundled. Church UA is optional and draft-first; supply only your own authorized access through the host's secure configuration and approve each actual submission. The package does not install a remote MCP service, scheduler or automatic publisher. The knowledge base stores version history locally; removing a current document does not automatically erase historical versions or backups. Review outputs before using or sharing them.

## Declared local MCP tools and credentials

Version 2.1.0-claude.4 adds 12 declared local MCP tools for the existing validation, library, workflow, visual and Church UA engines. Configure a dedicated existing workspace and stable local owner label through plugin options. The local server requires Python 3.9 or later and a supported local-execution host. Core operations need no additional package. Read MCP_RUNTIME.md for configuration, exact boundaries and optional native-export dependencies.

The optional existing Church UA key is shared explicitly through the sensitive `church_ua_key` option. It is passed only through the declared server's configuration. No ambient API key, keychain or credential-file discovery is performed. Preview is offline. Submission uses the configured origin, explicit user authorization and an exact reviewed payload hash; a durable attempt marker prevents automatic retries after uncertain outcomes. The legacy CLI's direct network path is disabled in this public distribution. No remote MCP service, new credential or public publishing tool is installed.

## Verification and limits

The current Claude .4 candidate passes 102 core tests, 24 MCP adapter tests and five source-preservation checks. It reduces repeated references while preserving all 54 skills and all original governing source bytes. An actual .4 Claude Code run read the shared sources and generated a Ukrainian devotional. Earlier Claude Desktop and ChatGPT web-host output checks are recorded separately in VALIDATION.md. Neither public marketplace approval nor authenticated live Church UA API checks is established. No claim of perfect answers or complete live integration is made.

## Links

[Website](https://alexjnapster.github.io/biblical-faith-life/) · [Support](https://alexjnapster.github.io/biblical-faith-life/support.html) · [Privacy](https://alexjnapster.github.io/biblical-faith-life/privacy.html) · [Terms](https://alexjnapster.github.io/biblical-faith-life/terms.html) · [Source](https://github.com/alexjnapster/biblical-faith-life)

Contact: alexandr.rodichev@gmail.com. This plugin is published by Oleksandr Rodichev, independently of OpenAI and Anthropic. All original governing source documents are preserved byte-for-byte in the shared library. Original attribution and third-party quotation rights remain applicable.

The ChatGPT source is in `plugins/chatgpt/biblical-faith-life`; the Claude source is in `plugins/claude/biblical-faith-life`.

## November 12 Claude candidate (2.1.0-claude.6)

An end-to-end audit of the Claude package found and fixed these defects in the local MCP adapter; no skill text or governing source changed:

- An unset plugin option that reached the server as an empty value or as the literal `${user_config.NAME}` template was treated as configured. `bfl_status` then reported a workspace and a Church UA credential that did not exist, and the template could become a library owner label. Such values now mean "not configured".
- `bfl_status` now reports whether the workspace is actually usable and why not, the Python version and which export formats are available, without returning a path or credential.
- `bfl_library_search` returned the full text of every match, which could exceed the message limit. It now returns a short excerpt and `content_chars`; pass `include_content` for full text.
- A missing document, and a malformed receipt passed to `bfl_draft_verify`, now produce specific errors before any credential or network use.
- A visual export that writes no file no longer leaves an empty directory that blocks a retry, and reports `failed` rather than `partial`.
- The server version is read from the manifest instead of being repeated in code. The Church UA origin falls back to `https://churches.tools` when unset.

The run passes 41 Python tests, 47 hosted-service tests and 24 public-interface checks, and the Claude Code 2.1.322 plugin and marketplace validators. Launch of the server by Claude Code with unset options was not observed in this audit; the adapter was exercised directly over stdio. Cowork starts a local server only when every plugin option it references has a default, and it does not prompt for values. Up to 2.1.0-claude.5 two options had no default, so the publisher's Claude desktop app 5.1231 reported the server as not started (`user_config_unsupported`). From 2.1.0-claude.6 every option has a default, which is intended to let the server start in Cowork with defaults only: status, validation and offline draft preview work there, while storage tools need a workspace that currently can be set only in Claude Code. This Cowork start has not yet been observed.

Version 2.1.0-claude.7 follows the directory validator's own findings on .6: the server is started without interpreter options, receives each plugin option under the accepted `CLAUDE_PLUGIN_OPTION_<KEY>` name, and no longer reads the manifest (which named the icon). 43 Python tests pass. The validator still holds the plugin for human review because it ships a local Python server and can send the optional Church UA key to the configured Church UA origin; both are disclosed above.

## Skills-only directory edition

The Claude plugin directory accepts local MCP servers and script files only from Verified organizations, and holds a plugin that can send a credential to a remote host. `plugins/claude-directory/biblical-faith-life` is therefore the edition submitted to the directory: the same 54 skills and byte-identical governing references, with no MCP server, no Python, no plugin options and no credential. Its host notes tell Claude to treat the local tools as unavailable and answer in text. It is generated by `python3 tools/build_directory_edition.py`; `--check` and `tests/test_directory_edition.py` fail if it drifts from the full edition. The full edition in `plugins/claude/biblical-faith-life` remains what this repository's own marketplace installs in Claude Code. 49 Python tests pass.

## November 10 source candidate

The next repository candidates are ChatGPT 2.1.0-rc.8 and Claude 2.1.0-claude.5. Both clarify host-aware execution and honest pending review; validators now require a nonblank text reviewer identity distinct from the author after trimming. ChatGPT also removes 285 identical reference copies, preserving all 54 skill identities and every governing source byte. Run `python3 -m unittest discover -s tests -v`, both hosted-service Node test files, and `python3 tools/build_release.py --output /tmp/bfl-release` from the repository. The current run passes 34 Python tests, 47 hosted-service tests and 24 public-interface checks. Historical 102-case results above were not independently rerun because that suite is not included in this repository.

The public OpenAI source-retrieval package is a different identity/version: 2.2.0-rc.6 is In review and Not published in the publisher portal. Its MCP configuration is Configured and all 54 skills show Checks passed. Do not replace or cancel that active submission with this skills-only source candidate. The saved 2.2.0-rc.6 bundle could not be exported in this audit, so source parity is unverified. Claude showed zero directory submissions in this account; an earlier validation report is not proof of a current directory submission.
