# Церква Христова — biblical-faith-life

![Open Bible icon](assets/icon.png)

Bible study, sermons and teaching grounded in the preserved Church of Christ v9 doctrinal framework. Includes 54 skills, 30 specialist capabilities, six shared engines, a research laboratory, sermon studio, personal biblical knowledge base, visual education studio and draft-first Church UA integration. Ukrainian is the default; English and Russian are supported. Intended for adult teachers, ministers and authors. AI output needs review and does not guarantee theological, historical or factual accuracy.

Publisher: Oleksandr Rodichev. Version: 2.1.0-claude.6. License: MIT for the publisher-provided software and documentation; quoted third-party material and trademarks retain their existing rights.

## Installation

Claude Code, from this repository's marketplace:

```
/plugin marketplace add alexjnapster/biblical-faith-life
/plugin install biblical-faith-life@biblical-faith-life
```

Or in one step: `/plugin install biblical-faith-life --marketplace alexjnapster/biblical-faith-life`.

In the Claude apps open Customize → Plugins → Add plugin → Upload plugin and choose the Claude ZIP without extracting it. Account and administrator restrictions may apply. Once a public directory listing is approved and published, install from that listing instead.

## Start using it

Ask for a Bible study, sermon, lesson or article and name the passage, audience, language and format. Ask for source verification when wording or historical claims matter. The skills work without any configuration.

## Optional local tools

The plugin declares one local stdio MCP server (`scripts/bfl_mcp.py`) with 13 tools for evidence validation, a personal library, workflow checkpoints, visual exports, Church UA drafts and a read-only word count (`bfl_count_words`) for checking a requested length. It needs Python 3.9 or later available as `python3` and a host that can launch local servers. Claude Code does and lets you set the options below. Cowork starts a local server only when every plugin option it references has a default, and it does not prompt for values. Up to 2.1.0-claude.5 two options had no default, so the publisher's Claude desktop app 5.1231 reported the server as not started (`user_config_unsupported`). From 2.1.0-claude.6 every option has a default, which is intended to let the server start in Cowork with defaults only: status, validation and offline draft preview work there, while storage tools need a workspace that currently can be set only in Claude Code. This Cowork start has not yet been observed. Chat ignores local servers; the skills then work as text-only guidance. On Windows, install Python so that a `python3` command exists. Core tools need no additional package; PDF and PowerPoint export need the pinned packages in `skills/biblical-faith-life/scripts/native-export-requirements.txt`.

All four plugin options are optional:

| Option | Purpose |
| --- | --- |
| `workspace` | An existing dedicated folder for your library, checkpoints and exports. Required only for tools that store files. It cannot be your home folder, a symbolic link or a folder inside the plugin. |
| `owner` | Label bound to libraries you create. Default `local-owner`. |
| `church_ua_origin` | HTTPS origin for Church UA drafts. Default `https://churches.tools`. |
| `church_ua_key` | Existing Church UA Agent API key, stored as a sensitive option. Needed only to submit or verify a draft. |

Call `bfl_status` to see whether the workspace is usable (and why not), which export formats are available and whether a Church UA key is configured. It never returns a credential or a path. An unset option is treated as not configured. See MCP_RUNTIME.md for exact boundaries.

## Access and data

No API key, congregation access, private library or ministry record is bundled. The server opens no listening port, runs no scheduler and performs no credential discovery: it reads only the four options above. Church UA is draft-first. Preview is offline. Submission uses only the configured origin and key, requires explicit authorization and the exact reviewed payload hash, and writes an attempt marker first so an uncertain outcome is never retried automatically. Publishing remains a separate human action in Church UA.

Library versions, checkpoints and exports stay in your workspace until you remove them; uninstalling the plugin does not erase them. Review outputs before using or sharing them.

## Verification and limits

Version 2.1.0-claude.6 passes 41 repository Python tests (31 for the MCP adapter, including real stdio subprocess sessions, plus source-preservation and link checks) and the plugin validator in Claude Code 2.1.322. A live stdio session exercised all 12 tools, including SVG, HTML, PDF and PowerPoint export. Tests use synthetic data and a mocked draft transport. Authenticated live Church UA requests remain unverified. Structural checks do not certify theology, scholarship, review independence or pastoral suitability. No claim of perfect answers or directory approval is made. See VALIDATION.md in the repository for history.

## Compact reference layout

All 54 skills are present. Each of the 12 governing documents is preserved byte-for-byte once in `skills/biblical-faith-life/references`, and skill entrypoints link to that shared library. REFERENCE_RELOCATION.json records every former location, current location, byte count and digest; SOURCE_MANIFEST.json retains the governing-source digests. No source is encrypted, hidden, downloaded dynamically or removed.

## Links

[Website](https://alexjnapster.github.io/biblical-faith-life/) · [Support](https://alexjnapster.github.io/biblical-faith-life/support.html) · [Privacy](https://alexjnapster.github.io/biblical-faith-life/privacy.html) · [Terms](https://alexjnapster.github.io/biblical-faith-life/terms.html) · [Source](https://github.com/alexjnapster/biblical-faith-life)

Contact: alexandr.rodichev@gmail.com. Published by Oleksandr Rodichev, independently of OpenAI and Anthropic. Original attribution and third-party quotation rights remain applicable.
