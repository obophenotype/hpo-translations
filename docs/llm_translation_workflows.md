# LLM-assisted candidate translation workflows

These workflows generate reviewable candidate translations. They do not produce `OFFICIAL` translations.

All LLM-assisted output must use:

- `translation_status`: `CANDIDATE`
- `agent_generated`: `true`
- `translation_method`: `LLM_ASSISTED_DRAFT`
- a recorded `workflow_id`, `batch_id`, `coding_agent`, and `model`

## Workflow lanes

| Workflow | Language | Lane | Model | Coding agent | Review policy |
| --- | --- | --- | --- | --- | --- |
| `fi-bootstrap-profile` | `fi` | Missing profile bootstrap | `gpt-5` | Codex CLI | Human review required |
| `th-bootstrap-profile` | `th` | Missing profile bootstrap | `gpt-5` | Codex CLI | Human review required |
| `ar-empty-profile-bootstrap` | `ar` | Empty profile bootstrap | `gpt-5` | Codex CLI | Human review required |
| `ja-gap-fill` | `ja` | Existing profile gap fill | `gpt-5` | Codex CLI | Human review required |
| `tr-gap-fill` | `tr` | Existing profile gap fill | `gpt-5` | Codex CLI | Human review required |
| `nl-gap-fill` | `nl` | Existing profile gap fill | `gpt-5` | Codex CLI | Human review required |

## Existing profile gap-fill

Use this for `ja`, `tr`, and `nl`.

```bash
pixi run agent-export --language nl --status NOT_TRANSLATED --limit 250 --workflow-id nl-gap-fill --batch-id nl-gap-fill-001 --model gpt-5 --output tmp/nl-gap-fill-001.jsonl
```

The LLM agent should return JSONL suggestions preserving the matching keys and metadata. Import is dry-run by default:

```bash
pixi run agent-apply-dry-run --input tmp/nl-gap-fill-001.suggestions.jsonl
```

After JSONL validation and model-triangulation checks, suggestions can be applied
with the script's explicit `--apply` flag to write `CANDIDATE` rows. Human review
is still required before any row is promoted to `OFFICIAL`.

## Candidate production method

Use this method when the deliverable is an LLM-generated candidate profile for
later human review:

1. Export only currently untranslated rows with `agent-export`.
2. Generate candidate JSONL with exact `language`, `subject_id`, `predicate_id`,
   and `source_value` keys preserved from the work items.
3. Mark every generated row as:

   - `translation_status`: `CANDIDATE`
   - `agent_generated`: `true`
   - `translation_method`: `LLM_ASSISTED_DRAFT`
   - `workflow_id`, `batch_id`, `coding_agent`, `model`, and `review_policy`
     preserved from the work item

4. Run `agent-apply-dry-run` before writing anything.
5. Use at least two free or open model review lanes where practical. Do not
   overuse a single model when other reliable free models are available.
6. Apply with `--apply` only if the importer matches the expected row count and
   the model checks do not report failures.
7. Leave rows as `CANDIDATE`; do not mark LLM output as `OFFICIAL`.

## End-to-end release workflow

Use this sequence for each language. The goal is an upstream pull request with
LLM-generated `CANDIDATE` rows, not human-approved `OFFICIAL` rows.

1. Refresh the audit:

   ```bash
   pixi run audit-translations --output tmp/translation-audit.tsv
   ```

2. Export untranslated rows for the selected workflow:

   ```bash
   pixi run agent-export --language tr --status NOT_TRANSLATED --workflow-id tr-gap-fill --batch-id tr-gap-fill-001 --model gpt-5 --output tmp/tr-gap-fill-001.work.jsonl
   ```

3. Generate candidate JSONL from the work items. Preserve exact keys from the
   work item and add only the candidate translation value plus required LLM
   provenance.

4. Validate row matching before writing:

   ```bash
   pixi run agent-apply-dry-run --input tmp/tr-gap-fill-001.codex-gpt5.suggestions.jsonl
   ```

5. Triangulate with free or open models. The default clean review lanes are:

   ```bash
   opencode run --pure --model opencode/deepseek-v4-flash-free --format json "<review prompt>"
   opencode run --pure --model opencode/mimo-v2.5-free --format json "<review prompt>"
   ```

   Use representative samples for large batches. Include obsolete terms,
   inheritance/modifier terms, anatomical terms, and any known terminology
   clusters in the sample. Do not use one model more than twice when another
   reliable free model is available.

6. Resolve conflicts before apply:

   - If both review lanes pass, apply the candidate batch.
   - If one lane passes and one lane flags notes, prefer existing terminology in
     the target language profile and keep the row `CANDIDATE`.
   - If any lane reports a likely mistranslation, revise the candidate and rerun
     dry-run plus model checks for that batch.
   - If the conflict cannot be resolved confidently, keep the safest literal
     candidate, leave it `CANDIDATE`, and document the uncertainty in the
     workflow record or PR body.
   - Never promote a generated row to `OFFICIAL`.

7. Apply the candidate batch:

   ```bash
   pixi run .pixi/envs/default/python.exe scripts/translation_audit.py apply-agent-output --input tmp/tr-gap-fill-001.codex-gpt5.suggestions.jsonl --apply
   ```

8. Repeat export, generate, validate, triangulate, and apply until the language
   audit reports `not_translated_rows: 0`.

9. Run verification:

   ```bash
   pixi run audit-translations --language tr --output tmp/tr-audit-finished.tsv
   pixi run lint
   git diff --check -- babelon/hp-tr.babelon.tsv docs/llm_translation_workflows.md translation_workflows/candidate_workflows.json
   ```

10. Commit only the intended language/workflow files. Do not sweep unrelated
    dirty Babelon files into the commit.

    ```bash
    git add babelon/hp-tr.babelon.tsv docs/llm_translation_workflows.md translation_workflows/candidate_workflows.json
    git commit -F tmp/commit-message.txt
    ```

11. Push the branch:

    ```bash
    git push -u origin <branch-name>
    ```

12. Open or update the upstream pull request:

    ```bash
    gh pr create --repo obophenotype/hpo-translations --head edithatogo:<branch-name> --base main --fill-first --body-file tmp/pr-body.md
    ```

    If a PR already exists for the branch, update it:

    ```bash
    gh pr edit <number> --repo obophenotype/hpo-translations --title <short-title> --body-file tmp/pr-body.md
    ```

13. The PR body should include:

    - language audit before and after
    - number of LLM `CANDIDATE` rows added
    - generator model and review models used
    - dry-run and lint results
    - conflict-resolution notes
    - explicit statement that human review is required before `OFFICIAL`
      promotion

## Per-language workflows

### Japanese (`ja-gap-fill`)

State: completed in upstream PR
<https://github.com/obophenotype/hpo-translations/pull/40>.

Use Japanese as the reference implementation for the full flow. It was completed
by exporting existing `NOT_TRANSLATED` rows, generating `CANDIDATE` rows with
Codex CLI / `gpt-5`, validating every row through the importer, triangulating
with free OpenCode review lanes, applying candidates, committing, pushing, and
updating the upstream PR.

Conflict resolution:

- Existing Japanese profile terminology was checked before filling remaining
  rows.
- Source labels beginning with `obsolete` were kept visibly obsolete with the
  `旧：` prefix.
- Rows stayed `CANDIDATE` even when both review lanes passed.

### Turkish (`tr-gap-fill`)

State: next recommended completeable language.

Use the existing-profile gap-fill lifecycle. Turkish has a medium backlog and
should be processed in bounded batches, starting with `batch_size: 250`.

Translate:

- Export only `NOT_TRANSLATED` rows from `babelon/hp-tr.babelon.tsv`.
- Generate candidate rows with Codex CLI / `gpt-5`.
- Preserve Turkish profile style and existing terminology when present.

Triangulate:

- Review each applied batch with `opencode/deepseek-v4-flash-free`.
- Use `opencode/mimo-v2.5-free` as the second clean review lane.
- For larger batches, use representative samples that include inheritance,
  modifier, anatomical, obsolete, and long compound terms.

Resolve conflicts:

- If one model flags wording but the translation matches existing Turkish
  profile style, keep the candidate and document the note.
- If both models flag a likely error, revise before apply.
- If uncertainty remains, keep the row `CANDIDATE` and mention the issue in the
  PR body.

Commit and PR:

- Commit `babelon/hp-tr.babelon.tsv` plus workflow documentation updates only.
- Push the branch and update or open the upstream PR with Turkish audit counts
  and model evidence.

### Dutch (`nl-gap-fill`)

State: largest existing-profile backlog.

Use the same existing-profile lifecycle after Turkish. Dutch has a larger backlog,
so use smaller reviewable chunks when model review or terminology conflict grows
too broad.

Translate:

- Export only `NOT_TRANSLATED` rows from `babelon/hp-nl.babelon.tsv`.
- Generate candidate rows with Codex CLI / `gpt-5`.
- Preserve Dutch profile terminology already present in the file.

Triangulate:

- Use the two clean OpenCode free lanes by default.
- Add extra spot checks for definition-heavy or long compound batches.
- Do not ask free models to emit full 18k-row judgments; use importer validation
  for full row coverage and stratified model samples for quality checks.

Resolve conflicts:

- Split large disagreement clusters into smaller batches.
- Prefer established Dutch HPO terminology where it exists locally.
- Keep unresolved rows as `CANDIDATE`; do not mark anything `OFFICIAL`.

Commit and PR:

- Commit `babelon/hp-nl.babelon.tsv` plus workflow documentation updates only.
- Push and update or open the upstream PR with Dutch audit counts and model
  evidence.

### Arabic (`ar-empty-profile-bootstrap`)

State: profile exists but contains no rows.

Arabic is not a normal gap-fill workflow because there are no source rows to
export. Treat it as bootstrap work.

Translate:

- First create or derive a canonical source-row inventory that matches the
  Babelon schema.
- Generate Arabic candidate rows from that inventory only.
- Preserve right-to-left text correctly and keep all rows `CANDIDATE`.

Triangulate:

- Use the default OpenCode free review lanes where they return usable Arabic
  review output.
- Add a right-to-left formatting check before applying.
- If a translation-specific Hugging Face or other free Arabic-capable model is
  available, use it as an additional baseline lane.

Resolve conflicts:

- Do not invent source rows from docs alone.
- If model outputs disagree on Arabic terminology, keep the more literal HPO
  label candidate and document the uncertainty for human review.

Commit and PR:

- Commit Arabic profile files plus source-inventory/workflow documentation.
- The PR body must state that this is bootstrap candidate output, not a gap-fill
  from an existing populated profile.

### Finnish (`fi-bootstrap-profile`)

State: documented language without a Babelon profile.

Finnish requires profile bootstrap before candidate generation.

Translate:

- Create a canonical Finnish Babelon source-row inventory first.
- Generate `CANDIDATE` rows from the inventory with Codex CLI / `gpt-5`.
- Preserve exact HPO IDs, predicates, and source labels.

Triangulate:

- Use the default OpenCode free lanes for sample review.
- Add extra samples for compound clinical labels and morphology terms.
- If a Finnish-capable free translation model is available, use it as a baseline
  comparison, not as an `OFFICIAL` source.

Resolve conflicts:

- Do not apply rows until schema validation and importer dry-run pass.
- If Finnish terminology is uncertain, keep literal candidates and document the
  uncertainty in the PR body.

Commit and PR:

- Commit the new Finnish profile files and workflow documentation together.
- The PR body must identify it as bootstrap `CANDIDATE` output requiring human
  review.

### Thai (`th-bootstrap-profile`)

State: documented language without a Babelon profile.

Thai also requires profile bootstrap before candidate generation.

Translate:

- Create a canonical Thai Babelon source-row inventory first.
- Generate `CANDIDATE` rows from that inventory with Codex CLI / `gpt-5`.
- Preserve exact HPO IDs, predicates, and source labels.

Triangulate:

- Use the default OpenCode free lanes where they return usable Thai review
  output.
- Add formatting checks for Thai text and punctuation.
- Use additional free Thai-capable models if available, but do not overuse one
  model more than twice when alternatives work.

Resolve conflicts:

- Do not synthesize rows from docs alone.
- If reviewers disagree, keep the safest literal candidate and document the
  issue for human review.

Commit and PR:

- Commit the new Thai profile files and workflow documentation together.
- The PR body must identify it as bootstrap `CANDIDATE` output requiring human
  review.

## Japanese completion record

Japanese (`ja-gap-fill`) was completed as an LLM-assisted candidate profile.

Final audit:

| Metric | Value |
| --- | ---: |
| Total rows | 17,868 |
| Complete rows | 17,868 |
| Official rows | 17,649 |
| Candidate rows | 219 |
| Not translated rows | 0 |
| Completion percent | 100.0 |

Generation metadata:

| Field | Value |
| --- | --- |
| `workflow_id` | `ja-gap-fill` |
| `coding_agent` | `Codex CLI` |
| `model` | `gpt-5` |
| `translation_method` | `LLM_ASSISTED_DRAFT` |
| `translation_status` | `CANDIDATE` |
| `review_policy` | `human-review-required` |

Model triangulation used:

| Tool | Model | Outcome |
| --- | --- | --- |
| OpenCode | `opencode/deepseek-v4-flash-free` | Passed pilot, batch 002, and representative final-sample checks |
| OpenCode | `opencode/mimo-v2.5-free` | Passed batch 002 and representative final-sample checks |
| OpenCode | `opencode/nemotron-3-ultra-free` | Returned all-pass review on the pilot, but the wrapper used tools and did not behave as a clean JSON-only verifier |
| Mimo | `openrouter/openai/gpt-oss-20b:free` | Confirmed pilot terms were largely correct, including `遺伝形式`, but the wrapper later hit context-overflow looping |
| Hugging Face | `Helsinki-NLP/opus-mt-en-jap` identified | Available as a possible baseline translation lane; not used to apply Japanese rows |

Tool or model issues encountered:

- Direct Mimo Xiaomi models were not used for production because the account
  returned insufficient balance.
- Cline with `openai/gpt-5` reached provider/model resolution but was blocked by
  insufficient Cline Credits.
- Agy print mode exited without useful output and was not treated as evidence.
- OpenCode direct NVIDIA `riva-translate-4b-instruct-v1_1` returned a 404
  through the configured provider route.
- Groq free routes failed with token-per-minute/context limits under OpenCode.
- Local Ollama `lfm:2.5b` failed to allocate the CPU buffer and was not used.

Issue-resolution choices:

- Obsolete labels were kept visibly obsolete using the `旧：` prefix where the
  source label began with `obsolete`, rather than silently dropping obsolete
  status.
- Existing Japanese terminology and style in `babelon/hp-ja.babelon.tsv` were
  checked before generating remaining candidate rows.
- Full 204-row importer dry-run was used before applying the remaining Japanese
  set.
- A representative 20-item final sample covered obsolete terms, inheritance,
  onset, severity/modifier terms, and head/neck anatomy terms. Both clean free
  review lanes passed that sample with no failures.

## Missing or empty profile bootstrap

Use this for `fi`, `th`, and `ar`.

These workflows require a canonical source-row inventory before work items can be exported. Do not synthesize a full profile from docs alone. Once the source inventory exists, generate candidate rows in bounded batches and mark every LLM-assisted value as `CANDIDATE`.
