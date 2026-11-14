# Answer-quality evaluation and repair: «Церква Христова» Claude plugin, 31 October 2026

**Scope:** the private Claude plugin `biblical-faith-life`, 54 skills and one local connector with 12 tools. This work is separate from the Church UA app.
**Result in one line:** the repaired local candidate `2.1.0-claude.6` passed independent blind review on 12 of 13 actual outputs. The installed `2.1.0-claude.5` passed 1 of 10 and the old `2.1.0-claude.4` baseline 2 of 7, on the same prompts. These are small-sample results for 8 of 54 skills. They do not establish same-or-better quality across all tasks.

Evidence root (outside the repo): `outputs/quality-upgrade.nosync/compare-20261031/`. Paths below are relative to it unless absolute.

## 1. Variants and conditions

| Variant label | What it is | Tree / version evidence |
|---|---|---|
| `baseline-claude.4` | Plugin at public baseline commit `dc2e1c2` (`2.1.0-claude.4`), extracted with `git archive` | CLI init event: version `2.1.0-claude.4`, 54 skills |
| `candidate-claude.5-installed` | The installed archive `church-of-christ-claude-install.zip` (owner's private local copy) (sha256 `f99f4b62…9c46`, never modified), unzipped into a copy | Identical to repo `1d3f48c` except the shortened manifest description. Identical to Desktop's synced copy except `.in_use`. |
| `candidate-claude.5-owner-run` | The owner's two existing runs (bible-commentary, sermon) on the repo `.5` source, imported unchanged (answer sha256 verified) | Original receipts kept. Their host label was hardcoded. |
| `repaired-claude.6` (iter 1) | Repair round 1 | Tree sha in each receipt |
| `repaired-claude.6-iter2` | Repair round 2 = repo commit after `cdf639f` (see §4) | Tree sha in each receipt |

Identical for every run:
- model `claude-opus-5-5`, requested with `--model` and observed in every trace;
- Claude Code 2.1.316;
- tools `Read,Skill,WebSearch,WebFetch`, MCP disabled (strict empty config), no code execution;
- the same prompt bytes (prompt sha in the receipts);
- `--plugin-dir` isolation. Init events show that only the inline copy loads: the synced Desktop copy is shadowed, 54 plugin skills, version from the directory. `--safe-mode` was rejected because it drops plugin skills.

Runner: `evaluation/run_compare.py`. Lengths: `evaluation/measure_words.py`, whitespace tokens, the owner's convention. It reproduces the owner's 1002 and 875 exactly. Heuristic defect flags: `evaluation/editorial_markers.py` (pointers only, not verdicts).

## 2. Structural validation (actual)

All copies (baseline, installed, repaired, repaired-iter2):
- `claude plugin validate --strict` passed;
- 12 of 12 governing sources match the checkpoint sha256 and byte counts;
- 54 skills each.

A local stdio `initialize`, `tools/list` and `bfl_status` call returned 12 tools in every copy (`work/.../plugin-eval-20261031/evidence/stdio-*.jsonl`). A harmless `bfl_status` call through this session's live Desktop connector also worked. Repo unit tests: 44 of 44 pass, including a new status-version test.

**Finding: stale runtime identifier.** `bfl_status` and `serverInfo` report `2.1.0-claude.4` in the installed `.5` package, confirmed both in the live Desktop connector and over local stdio. Cause: two hardcoded strings in `scripts/bfl_mcp.py`. Fixed in the candidate, which now reads the manifest version and reports `2.1.0-claude.6`. The installed `.5` is unchanged and still reports `.4`.

## 3. Owner's new evidence (bible-commentary__ordinary, `.5`)

Confirmed with the counter:
- 1002 words in the whole reply, 875 in the body, against 650–850 requested; the answer claimed «750–800». Length acceptance: **FAIL**.
- It also has an unrequested «Чого текст навчає і чого не навчає» section, a closing «Обмеження та перевірка» block, a missing-tool remark, and a Watchtower-mirror source (`wol.pr418.com`) for the ¾-denarius claim.

Reviewer A independently gave the same verdict, FAIL.

Root causes found in the plugin text:
1. The sermon workflow says «що він доводить і чого не доводить».
2. `COMMON.md` asks for «what follows and what does not».
3. No real counting tool is available, so models estimated, overshot and reported the estimate.

Items 1 and 2 are in hash-locked, preserved owner instruction files.

## 4. Repairs (repo commits `cdf639f` and the follow-up commit)

Unchanged, byte for byte: the 12 governing sources, `COMMON.md`, `ROLE_WORKFLOWS.md`, `KNOWLEDGE_ROUTING.md` and every original skill body. Tests pin all of them. No conviction was rewritten. Repairs are only in the unlocked layer:

- **`ANSWER_PRODUCTION.md` → new "Editorial release rules"** (Claude package only; copy in `evaluation/EDITORIAL_RULES_CLAUDE.md`):
  - A requested length covers the whole reply. Plan for the lower half and never state an estimated count.
  - No unrequested "does not teach/prove" sections and no invented objections. Older "proves / does not prove" wording describes reasoning; its result is stated positively, and every doctrinal conclusion must still appear.
  - No process talk, no closing verification or limitations paragraph, no mention of missing tools. A limitation goes in a clause at the claim it affects.
  - Cite only original publishers or recognized reference works, no mirrors.
  - Do not present a reconstruction as narrated fact.
- **All 54 skill addenda** (after the `## Verified answer production` marker) carry a one-sentence pointer to those rules.
- **Iteration 2** tightened the no-process-talk rule after iteration 1 still produced a trailing missing-tool note.
- `bfl_mcp.py` version fix, plus a regression test.
- Manifest and marketplace bumped to **`2.1.0-claude.6`** (local, unreleased) so the repaired candidate can't be confused with the installed `.5`.
- `tests/test_quality_upgrade.py` now allows exactly this Claude-only editorial section as a checked delta. The ChatGPT and workspace packages are untouched.

## 5. Per-case evidence and verdicts

Verdicts come from three independent blind Opus reviewers (`reviews/review-A.md`, `review-B.md`, `review-C.md`). Answers were shuffled to X/Y/Z per case; keys are in `blind-round*-KEY.json`, opened only after each review was complete. Each reviewer spot-checked Bible wording (Огієнко, Synodal, ESV/NIV), Greek, Metzger and SBLGNT data, Hodge, IOCDF and the crisis lines online.

"Whole" = every word of the reply, "Body" = text before a trailing notes block. Every answer is at `<variant>/<case>/answer.md`, with the prompt at `prompt.txt` and the receipt (version, model, tools, hashes) beside it. Full rows: `per-case-measurements.json`.

### Representative comparison (same prompts, three variants)

| Case (skill) | Range | baseline .4 whole/body → verdict | candidate .5 whole/body → verdict | repaired .6 whole/body → verdict |
|---|---|---|---|---|
| deep-exegesis__ordinary (UA exegesis, Eph 2:1–10) | 650–850 | 953/883 → FAIL | 919/780 → FAIL | 801/801 → **PASS, best** |
| deep-exegesis__language_ru (RU transfer) | 650–850 | 838/785 → FAIL (narrow) | 927/864 → FAIL | 776/776 → **PASS, best** |
| master-sermon-writer__ordinary (sustained sermon, Luke 15) | 750–950 | 972/886 → FAIL | 934/872 → FAIL | 900/841 → **PASS, best** |
| christian-article__ordinary (article, Luke 15) | 650–850 | 839/754 → PASS | 886/828 → FAIL | 773/737 → **PASS, best** (opening process line) |
| textual-criticism__ordinary (Mark 16 manuscripts) | none | 1171/1115 → FAIL (narrow) | 1726/1577 → FAIL (narrow) | 1368/1290 → **PASS, best** (has «Обмеження» block) |
| pastoral-care__ordinary (intrusive thoughts) | none | 833/733 → PASS | 839/750 → **PASS, best** | 722/685 → PASS |

### Affected cases (owner evidence)

| Case | Range | candidate .5 (owner run) | repaired iter 1 | repaired iter 2 |
|---|---|---|---|---|
| bible-commentary__ordinary | 650–850 | 1002/875 → FAIL | 841/766 → PASS (narrow; missing-tool note) | **754/754 → PASS, best** |
| sermon__ordinary (Acts 2:36–41) | 750–950 | 1040/970 → FAIL | **889/889 → PASS, best** | not rerun |

Baseline bible-commentary__ordinary: 843/750 → FAIL (narrow; «Що випливає з тексту, а що ні», process notes).

### Held-out cases (never used for tuning)

| Case | Range | candidate .5 | repaired iter 2 |
|---|---|---|---|
| bible-commentary__demanding | 650–850 | 949/872 → FAIL | **734/734 → PASS, best** |
| christian-article__demanding | 650–850 | 779/747 → FAIL (process outro, staged objection) | **695/695 → PASS, best** |
| pastoral-counseling-assistant__ordinary | none | not run | 610/610 → PASS |
| textual-criticism__language_en (EN transfer) | none | not run | 1256/1223 → **FAIL (narrow)**: opens «Next I'm writing up… the passages the plugin relies on»; «In this framework» |

**Tallies (reviewer verdicts):** baseline 2 of 7, candidate .5 1 of 10, repaired 12 of 13 (iteration 1: 8 of 8; iteration 2: 4 of 5).
**Whole-reply length on prompts with a range:** baseline 3 of 5, candidate 2 of 7, repaired 9 of 9.
**Model word-count claims:** every count stated in a baseline or candidate answer that could be checked was wrong (e.g. «близько 780», measured 886; «≈800», measured 949). No repaired answer stated a count.

**Doctrinal fidelity:** all reviewers found every variant broadly faithful, with no doctrinal failure. In repaired outputs the defensive "not merit" rubrics became positive statements: baptism for forgiveness argued from Acts 2:38, 22:16, Col 2:12 and Rom 6, presented as the response of faith; continued faithfulness; cessation handled as apostolic confirmation. Repairs removed framing, not convictions.

## 6. Bible-commentary repair status

**Repaired, with evidence.** A new actual output (`repaired-claude.6-iter2/bible-commentary__ordinary/answer.md`, answer sha256 `9ea1580e…bfe927`, 754 words in the whole reply) passed blind independent review as the best of four. The held-out demanding variant also passed (734 words). One residual minor defect noted by the reviewer: two phrases in quotation marks («Хто з вас…?», «доки не знайде») are not Ogienko's wording.

## 7. Open issues (not repaired; not claimed)

1. **Process openings are reduced but not eliminated.** Iteration 1 article: «Перевірив цитати… пишу статтю за настановами навички». Iteration 2 English textual criticism: «Next I'm writing up…», plus naming "the plugin"/"framework", which `COMMON.md` already forbids. This looks like host-level narration leaking into the final message. Instructions alone may not close it.
2. **Quotation discipline, all variants:** paraphrases placed inside quotation marks without a translation label, against an existing `COMMON.md` rule.
3. **Crisis-line accuracy is unresolved.** Reviewer B found a Kyiv Post report (4 Oct 2025) that Lifeline Ukraine 7333 was suspended from 1 Oct 2025. Reviewer C found it listed as active. 112 and 103 are correct. The repaired pastoral-care output cites 7333. Owner or human verification is needed before relying on it.
4. **Textual-criticism specifics:** an A. T. Robertson attribution for the Vaticanus blank column is unconfirmed (Wikipedia credits Skeat). The answer admits unconfirmed sigla while the prompt asks for verified evidence. The `.5` candidate misdescribes Metzger on Codex Bobiensis (k).
5. **Coverage:** 30 generated outputs across 8 of 54 skills, one sample per case, no repeatability runs. 152+ of the 182 suite cases remain unrun and are **not passed**.
6. **Conditions differ from Desktop:** MCP was disabled and no code tool was available. Desktop has the local connector. Results with the connector enabled are not measured.
7. **The installed Desktop copy is still `.5`,** with the defects above and the `.4` status string. The repaired `.6` exists only locally (repo plus the copy). Installing it is the owner's decision.
8. **The ChatGPT and workspace packages did not receive this repair** (they have their own release processes).
9. **Reviewer strictness differed** (B treated a single trailing note as a defect, A as a failure). Verdicts are reported as given, not re-scored.

## 8. Listing and publication status (dated receipts only)

- **Local/private installation:** `claude plugin list` (31 Oct 2026) shows `biblical-faith-life@synced`, version `2.1.0-claude.5`, status loaded, in the host's synced-plugin folder. The live connector answers `bfl_status`.
- **Workspace-listed availability, submitted review, approval, global publication (Claude):** no receipt was examined in this session. Unknown. No publisher dashboard was accessed.
- **ChatGPT workspace plugin:** the earlier 25 Oct checkpoint receipt records `2.1.0-rc.4` as "LISTED within the same workspace". It was not re-verified today.
- **Nothing was pushed, submitted, published or attested in this work.** No credentials were configured and no settings were changed.

## 9. Model and role assignments (actual)

- Judgement, repairs and synthesis: Claude Opus 5.5 (this session).
- Subject runs: `claude-opus-5-5` for every variant.
- Independent blind reviews A, B and C: three separate Opus subagents, given only the brief, the packets and the preserved sources.
- No Sonnet was used.

## 10. Repair rounds 3–7 (31 Oct 2026, later): final candidate and blind review

Commits:
- `945441c` (iter 3): no opening narration, quotation marks only for exact wording, help lines only when verified.
- `266777f` (iter 4): per-section length budgets; no "Below is…" introductions.
- `0e44947` (iter 5): the first-line rule holds right after tool use; English plans for the lower third of the range.
- `31db43b` (iter 6): read-only `bfl_count_words` connector tool (13 tools) and runner `--with-count-tool`. Instruction-only length control had not converged for English: 1060, 901, 859 and 919 against 650–850.
- `cf6bfc5` (iter 7): quotations copied from retrieved text and checked word for word; local paths removed from evaluation files.

The final candidate is the iteration-7 tree. Iterations 6 and 7 ran with the plugin's own connector enabled and only the counter allowed, which is closer to Desktop than earlier rounds. The model called the counter in 11 of 12 runs.

Blind reviews D, E and F (`reviews/review-D.md`, `review-E.md`, `review-F.md`; keys in `blind-round3-KEY.json` and `blind-round4-KEY.json`). "Whole" = every word of the reply.

| Case | installed .5 | repaired iter 6 | repaired iter 7 |
|---|---|---|---|
| deep-exegesis EN (650–850) | 1154 → FAIL | 849 → **PASS, best**; repeat 790 → PASS | – |
| deep-exegesis UA (650–850) | 919 → FAIL | 679 → PASS (minor: «хрищенні») | – |
| bible-commentary UA (650–850) | 1002 → FAIL | 682 → FAIL (narrow): «праведних» misquotes Ogienko «праведників» | 740 → PASS; repeat 711 → **PASS, best** (every quotation exact) |
| master-sermon-writer UA (750–950) | 934 → FAIL (status opening; «праведники» misquote) | – | 812 → **PASS, best** (every quotation exact) |
| master-sermon-writer demanding (750–950) | 847 → FAIL (status opening; «не випливає» section) | 772 → **PASS, best** | – |
| pastoral-care UA | 839 → FAIL (process talk) | 743 → **PASS, best** (only 112/103) | – |
| christian-article misleading, held out (650–850) | – | 701 → PASS (minor: trailing «Примітка») | – |
| textual-criticism EN | – | 1365 → PASS | – |
| pastoral-care EN | – | 606 → PASS | – |

Iteration 6 passed 8 of 9 reviewed answers; iteration 7 passed 3 of 3; the installed `.5` passed 0 of 6 in these rounds. Every ranged repaired answer from iterations 6 and 7 is within its range.

Open items from §7, with their status:
1. **Process openings: repaired.** No final-round answer opens with narration. Evidence: reviews D, E and F.
2. **Loose quotation marks: repaired at iteration 7.** Every quoted string in 3 of 3 iteration-7 answers matched Ogienko word for word (review F). One remaining minor in a single answer: a lemma («притча») placed in quotation marks.
3. **Crisis line: repaired.** Final-round pastoral replies name only 112/103/911 (review E). Whether Lifeline 7333 is currently operating was not established, so the plugin no longer names it.
4. **English length: repaired with the counter.** 849 and 790 (review D). Without the connector, as in the earlier runs, English length is not controlled. A host without the connector would see the earlier behaviour.

Still open, not repaired:
- the minor spelling «хрищення» (two answers);
- coverage of 8 of 54 skills, mostly one sample per case;
- about 150 suite cases unrun and not passed;
- the ChatGPT and workspace packages are unrepaired;
- the installed Desktop copy is still `.5`.
