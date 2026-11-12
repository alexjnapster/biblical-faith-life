# Claude host execution — public MCP distribution

This port preserves the original governing v9 sources and capabilities. Version 2.1.0-claude.3 adds a declared local stdio MCP server for the existing engines. The Python core requires Python 3.9 or later. No external package is needed for its core operations.

## Runtime boundary

Use the declared `biblical-faith-life` MCP tools for executable library, workflow, validator, visual export and Church UA operations. Read MCP_RUNTIME.md in this plugin root for the exact tools and setup. Do not invoke the legacy CLI, shell scripts, arbitrary Python or another undeclared process to execute plugin functionality. The old CLI is retained for source compatibility; its standalone network submission path is disabled. If the declared MCP tools are unavailable, explain that limitation and provide an answer or draft without claiming runtime execution.

Skills can produce study text in the Claude hosts that support skills. The local MCP tools require a host that can launch local servers. Claude Code does and prompts for the plugin options. Cowork starts a local server only when every plugin option it references has a default, and it does not prompt for values. Up to 2.1.0-claude.5 two options had no default, so the publisher's Claude desktop app 5.1231 reported the server as not started (`user_config_unsupported`). From 2.1.0-claude.6 every option has a default, which is intended to let the server start in Cowork with defaults only: status, validation and offline draft preview work there, while storage tools need a workspace that currently can be set only in Claude Code. This Cowork start has not yet been observed. Chat hosts ignore local servers; there the skills work as text-only guidance. A web/mobile chat must not claim that local state, files or network requests were executed unless its actual connected tools did so. Do not bypass host permission controls.

## Configuration and consent

All plugin options are optional; an unset option is treated as not configured. The workspace is explicitly selected through plugin configuration. Use a dedicated existing directory outside the installation, with a stable owner label. Do not read unrelated files, search credential stores or import private records without permission. Private library ingestion requires explicit boolean consent. History and checkpoints remain in the chosen directory until removed by the user; uninstalling the plugin does not erase them.

For optional Church UA access, the user can share an existing authorized key through the plugin's sensitive `church_ua_key` option and select `church_ua_origin`. The declared MCP env maps only that selected secret to this server. Do not read an ambient CHURCH_UA_AGENT_KEY or another application's credentials, put a secret in a conversation, create a new key, or substitute a different origin through tool arguments. Preview needs no key. Submit needs actual user authorization for the reviewed full payload, and persists an attempt before making a request. An uncertain outcome must be reconciled, never automatically retried. Publishing remains a separate human action.

## Substance and review

Read COMMON, KNOWLEDGE_ROUTING and applicable complete governing units before substantive conclusions. Ukrainian is the default; honor requested language and genre. Real independent review requires a distinct author and reviewer who actually read the exact artifact; workflow actor labels alone cannot prove it. Structural checks cannot certify theology, scholarship, safety or perfect answers. Preserve all material uncertainty and measured output requirements.
