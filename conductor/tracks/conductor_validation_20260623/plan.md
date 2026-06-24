# Plan - Implement automated Conductor validation and lifecycle gates

This plan adds repository-local validation for the Conductor track lifecycle so dependency, blocker, source access, payload, review, CI, PR, and merge claims are mechanically checked.

## Phase 0: Dependency, Blocker, Source, and Automation Gates
- [ ] **Task 1:** Define the validation contract before writing validator code.
  - Required checks include metadata schema, dependency graph integrity, Phase 0 presence, source access status, restricted payload policy, artifact contract, review gate, CI gate, PR gate, merge gate, and no stale delivery addenda.
- [ ] **Task 2:** Define the validator's own source and payload boundaries.
  - The validator may read Conductor metadata, plans, specs, git status, and CI metadata; it must not read or commit licensed ontology payloads.
- [ ] **Task 3:** Define fail-fast fixtures.
  - Include one passing track, one missing metadata field, one unresolved restricted source, one missing review gate, and one stale plan fragment fixture.
- [ ] **Task 4:** Define output artifacts.
  - Emit a human-readable report, a JSON report, a CI summary, and a per-track remediation list.
- [ ] **Task 5:** Define remote automation gates.
  - Validator checks should run locally first, then in GitHub Actions after the command is stable; CI must fail on schema drift, missing source governance, or restricted-payload leakage patterns.

## Phase 1: Metadata Schema Validation
- [ ] **Task 1:** Define required metadata fields for legacy, planned, in-progress, blocked, and complete tracks.
- [ ] **Task 2:** Validate `depends_on`, `blocks`, `priority`, `parallel_group`, `write_owner`, `merge_owner`, `source_access_status`, `restricted_payload_policy`, `fail_fast_probe`, and `artifact_contract`.
- [ ] **Task 3:** Emit per-track remediation output for missing, inconsistent, or stale lifecycle fields.

## Phase 2: Plan and Dependency Validation
- [ ] **Task 1:** Validate every active plan has Phase 0 dependency, blocker, source, payload, fail-fast, artifact, parallelization, telemetry, and remote delivery gates.
- [ ] **Task 2:** Detect stale delivery addendum fragments, duplicate headings, missing phase gates, and completion claims without validation evidence.
- [ ] **Task 3:** Validate dependency graph references and flag downstream tracks whose prerequisites are not ready.

## Phase 3: Restricted Payload and Repo Hygiene Validation
- [ ] **Task 1:** Add blocked filename and path-pattern checks for restricted, raw, licensed, private, credentialed, or full-release payloads.
- [ ] **Task 2:** Require local-only manifest evidence when restricted-source tracks touch local payloads.
- [ ] **Task 3:** Run `git diff --check`, JSON validation, and stale-lock checks as part of the local validation report.

## Phase 4: CI, PR, and Merge Lifecycle Validation
- [ ] **Task 1:** Add optional GitHub CLI checks for branch, PR URL, PR-head checks, CI URL, merge status, and merge commit reachability.
- [ ] **Task 2:** Keep remote checks non-destructive and report authentication or permission blockers explicitly.
- [ ] **Task 3:** Wire the validator into GitHub Actions after local fixtures pass and the command is stable.

## Phase 5: Review Automation and Advanced Reporting
- [ ] **Task 1:** Add conductor-review prompts or report sections for automated fix application after each phase.
- [ ] **Task 2:** Add summaries for blocker age, source access state, payload risk, artifact readiness, conflict count, and agent/model telemetry.
- [ ] **Task 3:** Add release-readiness scoring for tracks that combines validation, review, CI, PR, merge, source-governance, and human-review handoff state.
