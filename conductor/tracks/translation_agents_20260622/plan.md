# Plan - Implement translation completeness audits and automated translation using LLM coding agents

This plan tracks the repo-side audit and agent workflow implementation.

## Phase 1: Track Setup
- [x] **Task 1:** Create Conductor track folder, metadata, specification, and plan.
- [x] **Task 2:** Mark the completed Pixi migration track as complete in `conductor/tracks.md`.
- [x] **Task 3:** Mark this translation-agent track as in progress in `conductor/tracks.md`.

## Phase 2: Completeness Audit
- [x] **Task 1:** Implement language discovery from `babelon/hp-*.babelon.tsv`.
- [x] **Task 2:** Compute per-language completeness, status, predicate, and synonym counts.
- [x] **Task 3:** Write a stable TSV audit report.

## Phase 3: Agent Work Item Export
- [x] **Task 1:** Export untranslated rows to JSONL work items.
- [x] **Task 2:** Include matching keys and explicit agent output instructions.
- [x] **Task 3:** Support language, status, output, and limit selectors.

## Phase 4: Agent Suggestion Import
- [x] **Task 1:** Implement JSONL suggestion loading and validation.
- [x] **Task 2:** Match suggestions by language, subject, predicate, and source value.
- [x] **Task 3:** Default to dry-run and require explicit apply before rewriting profiles.

## Phase 5: Automation Wiring
- [x] **Task 1:** Add Pixi tasks for audit, export, and dry-run import.
- [x] **Task 2:** Add Just wrappers for audit and agent workflow commands.
- [x] **Task 3:** Verify commands on the current workspace.

## Phase 6: Review
- [x] **Task 1:** Run `pixi run lint`.
- [x] **Task 2:** Confirm generated outputs are either intentionally tracked or cleaned.
- [x] **Task 3:** Mark track complete after verification.
