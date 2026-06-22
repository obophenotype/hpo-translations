# Specification - Implement translation completeness audits and automated translation using LLM coding agents

## Objective
Add deterministic repository-side tooling that measures translation completeness, exports bounded translation work items for LLM coding agents, and safely imports reviewed agent suggestions without requiring live LLM credentials in CI.

## Technical Details

### 1. Completeness Audit
- Discover language profiles from `babelon/hp-*.babelon.tsv`.
- Summarize per-language row counts, completion counts, status counts, predicate coverage, and synonym rows.
- Write a stable TSV report that can be reviewed in CI or by maintainers.

### 2. Agent Work Item Export
- Export untranslated or selected-status rows to JSONL work items.
- Include source value, HPO subject, predicate, language code, current status, and explicit output instructions.
- Keep exports bounded with optional language/status/limit selectors.

### 3. Agent Output Import
- Accept JSONL suggestions from coding agents.
- Match suggestions by language, subject, predicate, and source value.
- Default to dry-run; require an explicit apply flag before rewriting Babelon profiles.
- Only update rows currently marked `NOT_TRANSLATED` or `CANDIDATE`.

### 4. Automation Surface
- Expose audit and agent workflow commands through Pixi tasks.
- Add Just wrappers for local ergonomics while keeping Pixi canonical.
- Keep generated reports and work item files separate from source translation profiles unless explicitly committed.

### 5. Validation
- Pass `pixi run lint`.
- Verify audit and export commands on the current profiles.
- Verify apply dry-run against a small synthetic suggestion file without mutating source TSV files.
