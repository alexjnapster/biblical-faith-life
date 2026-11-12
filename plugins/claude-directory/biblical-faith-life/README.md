# Церква Христова — biblical-faith-life (directory edition)

![Open Bible icon](assets/icon.png)

Bible study, sermons and teaching grounded in the preserved Church of Christ v9 doctrinal framework. This edition contains 54 skills covering exegesis, sermons, lessons, articles, research review, pastoral care and ministry writing. Ukrainian is the default; English and Russian are supported. Intended for adult teachers, ministers and authors. AI output needs review and does not guarantee theological, historical or factual accuracy.

Publisher: Oleksandr Rodichev. License: MIT for the publisher-provided software and documentation; quoted third-party material and trademarks retain their existing rights.

## What this edition is

This is the skills-only edition published to the Claude plugin directory. It contains Markdown skills, the shared reference library and an icon, and nothing else:

- It runs no code and starts no MCP server.
- It has no plugin options and asks for no credential.
- It stores nothing and sends nothing anywhere. Your prompts and Claude's answers are handled only by the Claude product you use.
- It works the same in Claude Code, Cowork and the Claude apps.

## Start using it

Ask for a Bible study, sermon, lesson or article and name the passage, audience, language and format. Three prompts to try:

- «Підготуй проповідь на 25 хвилин за Луки 15:11–32 для дорослої громади українською.»
- "Write a Sunday school lesson for ages 8–10 on Psalm 23 with two activities and review questions."
- "Review this interpretation of Romans 6:1–4 for contextual and logical soundness, and list what the text cannot establish."

Ask for source verification when wording or historical claims matter. Some skills describe optional local tools (a personal library, workflow checkpoints, visual exports, Church UA drafts). Those tools are not part of this edition; the skills then give a text answer or draft and say that nothing was executed.

## Full edition with local tools

The same skills plus a local Python MCP server with 12 tools are published from the source repository for Claude Code:

```
/plugin marketplace add alexjnapster/biblical-faith-life
/plugin install biblical-faith-life@biblical-faith-life
```

Install one edition, not both: they share the plugin name.

## Reference layout

All 54 skills are present. Each of the 12 governing documents is preserved byte-for-byte once in `skills/biblical-faith-life/references`, and skill entrypoints link to that shared library. REFERENCE_RELOCATION.json and SOURCE_MANIFEST.json record locations, byte counts and digests. No source is encrypted, hidden, downloaded dynamically or removed. This folder is generated from the full edition by `tools/build_directory_edition.py` in the source repository, and a test fails if the two drift apart.

## Sensitive topics

The pastoral-care and counseling skills offer biblical and pastoral support. They are not medical, psychological or legal services. For abuse, self-harm or other emergencies, contact local emergency services and qualified professionals.

## Links

[Website](https://alexjnapster.github.io/biblical-faith-life/) · [Support](https://alexjnapster.github.io/biblical-faith-life/support.html) · [Privacy](https://alexjnapster.github.io/biblical-faith-life/privacy.html) · [Terms](https://alexjnapster.github.io/biblical-faith-life/terms.html) · [Source](https://github.com/alexjnapster/biblical-faith-life)

Contact: alexandr.rodichev@gmail.com. Published by Oleksandr Rodichev, independently of OpenAI and Anthropic.
