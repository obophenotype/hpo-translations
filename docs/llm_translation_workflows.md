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
