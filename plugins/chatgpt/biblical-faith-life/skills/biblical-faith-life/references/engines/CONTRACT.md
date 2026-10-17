# Shared review contract

This contract applies to the 30 capability workflows and five integrated studios. Existing simple-answer workflows remain usable without making a dossier for every question.

For substantial audited artifacts use the local `scripts/bfl_cli.py` helper and the `bfl` library. No extra network permission or hosted service is installed. Python 3.9+ standard library is sufficient.

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
