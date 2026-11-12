# Shared review contract

This contract applies to the 30 capability workflows and five integrated studios. Existing simple-answer workflows remain usable without making a dossier for every question.

For substantial audited artifacts, first inspect the tools actually available in the host. In Claude use the declared local MCP tools when connected; otherwise use `skills/biblical-faith-life/scripts/bfl_cli.py` relative to the plugin root with Python 3.9+ standard library. A text-only host can still produce useful text and source notes: disclose the specific checks it cannot run, retain pending review, and never invent tool execution or a reviewer. No extra network permission or hosted service is installed.

## Work proportionate to the request

Reuse passages and argument units already read in this conversation while their identity and completeness remain known. Load the relevant complete units and amendments, then expand only when the argument requires it; do not load the entire source library for each response. Choose one primary workflow. Invoke additional specialists only for a concrete unresolved question. Simple questions need no artifact envelope.

For substantial work, identify the requested outcome, evidence and important constraints; explain the conclusion through the text's actual reasoning, address the strongest relevant alternative and distinguish fact from interpretation. Verify consequential claims before polishing. Ask only for missing facts that change the result, continuing independent work meanwhile. Keep internal review records separate from the finished sermon, lesson or article unless requested.

When independent semantic review is required, use a genuinely separate reviewer available under the host's delegation rules. A different name on the same author's self-review does not establish independence. If a reviewer is unavailable, provide the useful draft with review pending. Never loop until an automatic score passes or claim that structural validation proves semantic quality.

Required artifact envelope: schema_version=1, id, language (uk/en/ru), author, content, sources, claims, quotations, doctrine, safety, requirements, and review. Source records contain id, title, locator, accessed_at, text, sha256, and evidence_type (primary/secondary/user). Claim records contain id, text, status (fact/interpretation/inference/uncertain), source_id, and excerpt. Quotation records contain text, source_id, translation, language, and reference. Doctrine records contain file, sha256, start_line, end_line, and status from the preserved v9 status vocabulary. Safety records contain risk (none/concern/crisis/unknown), private_data, consent_to_store, actions, and human_reviewed. Requirements contain id, expected, and evidence; objective constraints must be checked by appropriate tools. Review contains reviewer, artifact_sha256, findings with severity and resolved, and semantic_reviewed=true only after an actual independent review.

Never fill review fields with fabricated attestations just to pass a validator. The helper reports structural findings, pending review gates, and limits of what was checked. A pass means the submitted records are internally consistent. It does not mean a manuscript is doctrinally correct, a citation is authentic, or a person is safe.

The artifact's response language remains `uk`, `en`, or `ru`. Quotations may also use original-language codes `grc` (Ancient Greek), `he` or `hbo` (Hebrew/Biblical Hebrew), and `arc` (Aramaic). For those quotations set `text_kind` to `original`, provide a nonempty full `edition_name`, and use the existing `translation` field for the edition's short label, such as `SBLGNT` or `WLC`. This field name is retained for compatibility; an original edition is not a translation. Exact source-text matching still applies. These labels identify the submitted source and do not certify a transcription, vocalization, manuscript reading or translation. If ordered corpus tokens are normalized into a readable quotation, record that extraction and the pinned original corpus hash in the source record; never label a back-translation as original text.

Read engines relevant to the task:

- [biblical-accuracy](biblical-accuracy.md)
- [doctrinal-governance](doctrinal-governance.md)
- [source-based-research](source-based-research.md)
- [multilingual-scripture](multilingual-scripture.md)
- [pastoral-safety](pastoral-safety.md)
- [independent-quality-assurance](independent-quality-assurance.md)

Read [runtime usage](RUNTIME.md) for commands and local data controls.
