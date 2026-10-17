# Церква Христова — biblical-faith-life

![Open Bible icon](assets/icon.png)

Bible study, sermons and teaching grounded in the preserved Church of Christ v9 doctrinal framework. Includes 54 skills, 30 specialist capabilities, six shared engines, a research laboratory, sermon studio, personal biblical knowledge base, visual education studio and draft-first Church UA integration. Ukrainian is the default; English and Russian are supported. Intended for adult teachers, ministers and authors. Local library, persistent workflows and Python exports require a host with an available code executor. Church UA submission requires separately configured authorized access; installation grants no congregation access. AI output needs review and does not guarantee theological, historical or factual accuracy.

Publisher: Oleksandr Rodichev. Version: 2.1.0-claude.3. License: MIT for the publisher-provided software and documentation; quoted third-party material and trademarks retain their existing rights.

## Installation

In Claude open Customize → Plugins → Add plugin → Upload plugin and choose the Claude ZIP without extracting it. Account and administrator restrictions may apply. For Claude Code, register the repository marketplace, then install `biblical-faith-life@biblical-faith-life`. Once the public listing is approved and published, install from that listing.

Claude Code one-step installation (2.1.275 or later):

`/plugin install biblical-faith-life --marketplace alexjnapster/biblical-faith-life`

## Start using it

Select the plugin in a new conversation and request a Bible study, sermon, lesson or article. Specify the passage, audience, language and requested format. Ask for source verification when wording or historical claims matter. Full local tools require Python 3.9 or later and a code-capable host; optional PDF/PowerPoint exports require the documented dependencies. Libraries and workflow files belong in your own workspace outside the installed plugin folder. Preserve those files before uninstalling or replacing a local installation.

## Access and data

No API key, congregation access, private library or ministry record is bundled. Church UA is optional and draft-first; supply only your own authorized access through the host's secure configuration and approve each actual submission. The package does not install a remote MCP service, scheduler or automatic publisher. The knowledge base stores version history locally; removing a current document does not automatically erase historical versions or backups. Review outputs before using or sharing them.

## Declared local MCP tools and credentials

Version 2.1.0-claude.3 adds 12 declared local MCP tools for the existing validation, library, workflow, visual and Church UA engines. Configure a dedicated existing workspace and stable local owner label through plugin options. The local server requires Python 3.9 or later and a supported local-execution host. Core operations need no additional package. Read MCP_RUNTIME.md for configuration, exact boundaries and optional native-export dependencies.

The optional existing Church UA key is shared explicitly through the sensitive `church_ua_key` option. It is passed only through the declared server's configuration. No ambient API key, keychain or credential-file discovery is performed. Preview is offline. Submission uses the configured origin, explicit user authorization and an exact reviewed payload hash; a durable attempt marker prevents automatic retries after uncertain outcomes. The legacy CLI's direct network path is disabled in this public distribution. No remote MCP service, new credential or public publishing tool is installed.

## Verification and limits

The prior ChatGPT rc.4 and Claude .1 cores passed 102 local tests each. Claude .1 was installed in Desktop and generated actual Ukrainian/English report files through Claude Code. ChatGPT rc.4 generated an actual Ukrainian article and downloadable HTML in its web host. The .3 public candidate also adds the declared MCP adapter; its tests and host checks are recorded separately. It is not yet marketplace-approved. Authenticated live Church UA API and tenant-scope checks remain unverified because the authorized existing key was not available. No claim of perfect answers, complete live integration or platform approval is made.

## Links

[Website](https://alexjnapster.github.io/biblical-faith-life/) · [Support](https://alexjnapster.github.io/biblical-faith-life/support.html) · [Privacy](https://alexjnapster.github.io/biblical-faith-life/privacy.html) · [Terms](https://alexjnapster.github.io/biblical-faith-life/terms.html) · [Source](https://github.com/alexjnapster/biblical-faith-life)

Contact: alexandr.rodichev@gmail.com. This plugin is published by Oleksandr Rodichev, independently of OpenAI and Anthropic. All original governing reference copies are preserved. Original attribution and third-party quotation rights remain applicable.
