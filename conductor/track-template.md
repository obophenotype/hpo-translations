# Conductor Track Template

Use this template when creating or revising tracks. Replace bracketed placeholders before implementation begins.

## Metadata Requirements
- `track_id`: stable folder name.
- `status`: planned, in_progress, blocked, complete, or legacy_complete.
- `depends_on`: prerequisite tracks, phases, source artifacts, credentials, or remote resources.
- `blocks`: downstream tracks, phases, or releases waiting on this work.
- `branch`: expected git branch.
- `pr_url`: pull request URL once opened.
- `ci_status`: not_started, pending, passing, failing, or blocked.
- `merge_status`: not_opened, open, merged, blocked, or legacy_unverified.
- `last_commit`, `phase_review_status`, `github_checks_url`, `merge_commit`: lifecycle evidence.
- `known_blockers`, `expected_blockers`, `blocker_owner`, `fallback_path`: blocker registry.
- `source_access_status`: open, restricted, API-only, local-only, documentation-only, investigation-only, not_applicable, or a source-specific review state such as license_required.
- `restricted_payload_policy`: commit allowlist, denylist, local-only artifacts, blocked patterns, and proof required before commit.
- `fail_fast_probe`: smallest source or automation probe that must pass before batch work.
- `artifact_contract`: committed, generated, local-only, reviewer-only, PR-safe, and release-safe outputs with schemas and validation commands.
- `priority`, `parallel_group`, `write_owner`, `merge_owner`: scheduling and concurrency controls.
- `automation_readiness`, `evidence_score_policy`, `agent_telemetry`, `human_review_handoff`: automation and review intelligence.

## Required Plan Sections

### Phase 0: Dependency, Blocker, Source, and Automation Gates
- [ ] **Task 1:** Populate the blocker registry and assign owners.
- [ ] **Task 2:** Complete source access, license, credential, source-authority, language, and version-pinning checks.
- [ ] **Task 3:** Define restricted payload policy, local-only manifest requirements, and commit allowlist/denylist.
- [ ] **Task 4:** Run the fail-fast probe before any bulk implementation.
- [ ] **Task 5:** Define the artifact contract and downstream consumers.
- [ ] **Task 6:** Declare priority, write owner, merge owner, and parallelization boundaries.
- [ ] **Task 7:** Define validation commands, commit boundaries, branch name, remote, PR target, CI gate, and merge gate.
- [ ] **Task 8:** Start telemetry for agent, model, runtime, validation, conflicts, and unresolved blockers.

### Implementation Phases
- [ ] **Task 1:** Implement the smallest ready unit of work.
- [ ] **Task 2:** Run local validation for the changed scope.
- [ ] **Task 3:** Commit immediately with the track and task identifier.
- [ ] **Task 4:** Update metadata and the artifact contract when the task changes dependencies, outputs, or blockers.

### Phase Review Gate
- [ ] **Task 1:** Run `conductor-review` for the phase.
- [ ] **Task 2:** Apply review fixes automatically when authorized by project policy.
- [ ] **Task 3:** Rerun validation, commit fixes, push the branch, and verify GitHub Actions for the pushed commit.
- [ ] **Task 4:** Record review outcome, CI URL, unresolved blockers, and any local-only artifact changes.

### Track Completion Gate
- [ ] **Task 1:** Run `conductor-review` for the full track.
- [ ] **Task 2:** Open or update the PR with validation, review, dependency, payload-policy, telemetry, and CI evidence.
- [ ] **Task 3:** Verify GitHub Actions pass and the PR is merged before marking the track complete.
- [ ] **Task 4:** Record merge commit, release eligibility, and downstream handoff state.

## Recommended Advanced Features
- Evidence scoring that separates curated mappings, label agreement, synonym agreement, multilingual agreement, LLM agreement, and source conflicts.
- Semantic drift detection between source releases and HPO release versions.
- Conflict heatmaps for one-to-many, many-to-one, deprecated, circular, and language-specific disagreements.
- Reproducibility capsules containing commands, source versions, checksums when allowed, local-only manifests, and validation outputs.
- Reviewer workload estimation and active-learning queues ordered by impact, disagreement, and source coverage.
- Agent telemetry comparing coding agent, model, runtime, validation reliability, and conflict-resolution performance.
