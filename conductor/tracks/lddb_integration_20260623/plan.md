# Plan - Integrate LDDB into terminology and translation support

This plan introduces LDDB into the project where it can improve terminology alignment, multilingual review, or validation.

## Implementation Result
Phase 0 governance is implemented as investigation-only no-go. LDDB does not proceed to source retrieval, identifier-network contribution, translation use, or non-translation outputs until source authority, maintenance status, access path, and redistribution terms are verified.

## Phase 0: Dependency, Blocker, Source, and Automation Gates
- [x] **Task 1:** Populate the blocker registry in metadata before implementation.
  - Record `known_blockers`, `expected_blockers`, `blocker_owner`, `fallback_path`, and a go/no-go decision for source ingestion.
  - Do not begin batch extraction while license, credential, source authority, or payload-commit status is unresolved.
- [x] **Task 2:** Complete the source access gate.
  - Record `source_access_status`, authoritative endpoint or repository, version-pinning strategy, credential requirements, cache location, and rate-limit or download constraints.
  - Classify the source as open, restricted, API-only, local-only, documentation-only, or investigation-only.
- [x] **Task 3:** Apply the restricted payload policy.
  - Define the commit allowlist and denylist for this source before touching payloads.
  - Add a local-only manifest for any raw, licensed, private, credentialed, or full-release payload.
  - Prove generated review artifacts do not contain prohibited source text, credentials, or redistributable payload fragments.
- [x] **Task 4:** Run a fail-fast probe before bulk work.
  - Process one authoritative source record end to end into a registry row, provenance row, validation result, and comparison or crosswalk sample when applicable.
  - Stop and update the blocker registry if schema, license, source authority, or mapping semantics fail on the probe.
- [x] **Task 5:** Define the track artifact contract.
  - Name each committed artifact, local-only artifact, generated report, validation fixture, and downstream consumer.
  - Include expected schema, owner, validation command, freshness rule, and whether the artifact can appear in an upstream PR.
- [x] **Task 6:** Set priority, write ownership, and parallelization boundaries.
  - Record `priority`, `parallel_group`, `write_owner`, and `merge_owner`.
  - Parallel work is allowed only when agents have disjoint source manifests, plans, generated artifacts, and Babelon profile write scopes.
- [x] **Task 7:** Define task automation and remote delivery gates.
  - For each ready task, run the implementation workflow, validate locally, commit after completion, run conductor-review after each phase, apply authorized fixes, push after each phase, verify GitHub Actions on the pushed commit and PR head, and verify PR merge before marking complete.
- [x] **Task 8:** Start performance, evidence, and model telemetry.
  - Record coding agent, model, task id, source version, runtime, validation result, conflict count, and unresolved blockers.
  - Mark any LLM-assisted candidate output as candidate-only and human-review-required in the handoff pack.

## Phase 1: Source Governance
- [ ] **Task 1:** Confirm authoritative release source, license, and redistribution constraints.
- [ ] **Task 2:** Record supported languages and source-version metadata.
- [ ] **Task 3:** List relevant GitHub repositories:
  - None confirmed; document authoritative non-GitHub source instead.

## Phase 2: Data Access and Normalization
- [ ] **Task 1:** Define source retrieval path without committing restricted payloads.
- [ ] **Task 2:** Normalize identifiers, preferred labels, synonyms, language tags, and provenance fields.
- [ ] **Task 3:** Produce a bounded sample artifact for maintainer review.

## Phase 3: HPO Translation Use
- [ ] **Task 1:** Identify where LDDB helps: crosswalks, synonym review, multilingual label comparison, or domain validation.
- [ ] **Task 2:** Add deterministic matching rules and conflict reporting.
- [ ] **Task 3:** Ensure LLM-assisted outputs remain candidate-only and human-review-required.

## Phase 4: Validation and Review
- [ ] **Task 1:** Validate schema, provenance, and license metadata.
- [ ] **Task 2:** Run translation-audit and import dry-run checks against sample outputs.
- [ ] **Task 3:** Document limitations, excluded payloads, and review decisions.

## Phase 0 Validation Evidence
- Generated governance record: `ontology_network/p3_source_governance.json` entry for `lddb_integration_20260623`.
- Payload status: no raw, licensed, credentialed, private, full-release, label, synonym, or API-response payload is read or committed.
- Downstream status: Phase 3 identifier-network and Phase 4 non-translation outputs remain blocked until source authority and terms review pass.
