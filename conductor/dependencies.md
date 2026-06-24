# Conductor Dependency Graph and Remote Delivery Gates

## Core Dependency Graph
- migrate_to_pixi_20260622 has no project-track prerequisite and provides the Pixi, lint, validation, and CI task foundation.
- conductor_validation_20260623 depends on migrate_to_pixi_20260622 and translation_agents_20260622 and provides machine validation for track metadata, dependency graph state, source gates, artifact contracts, review gates, CI gates, and merge gates.
- translation_agents_20260622 depends on migrate_to_pixi_20260622 and provides audit, export, import, and LLM candidate workflow tooling.
- ontology_network_20260623 depends on translation_agents_20260622 and conductor_validation_20260623 Phase 1 for registry schema, metadata validation, governance rules, crosswalk graph contracts, provenance, validation, review-pack, and release surfaces.
- Each ontology integration track depends on ontology_network_20260623 Phase 1 for registry schema and governance rules before source-specific implementation begins.
- Language profile candidate tracks depend on translation_agents_20260622 and may depend on ontology_network_20260623 when ontology triangulation evidence is required before upstream submission.

## Readiness States
- `planned`: track exists but Phase 0 gates are incomplete.
- `ready`: blocker registry, source access, restricted payload policy, fail-fast probe, artifact contract, write owner, validation command, and branch/PR target are documented.
- `in_progress`: at least one ready task is being implemented.
- `blocked`: implementation cannot continue because a named blocker lacks owner, permission, source access, CI availability, or reviewer decision.
- `complete`: implementation, local validation, conductor-review, push, GitHub Actions, PR, merge verification, and downstream handoff are complete.
- `legacy_complete`: completed before the current lifecycle contract and retained as an upstream dependency with legacy verification notes.

## Blocker Registry Requirements
Every active track must record:
- Known blockers: concrete issues already present, such as missing source credentials, unclear license, private data, or CI failure.
- Expected blockers: likely risks, such as schema drift, large payloads, source rate limits, mapping ambiguity, and reviewer capacity.
- Owner: person, agent, or track responsible for resolving or escalating the blocker.
- Fallback path: what can still be delivered if the blocker persists, such as metadata-only registry, documentation-only source, or local-only validation.
- Go/no-go decision: whether source ingestion, generated artifacts, PR opening, or merge may proceed.

## Source Access Gates
- Classify every source as open, restricted, API-only, local-only, documentation-only, or investigation-only before extraction.
- Record license status, credential needs, authoritative endpoint or repository, source version, supported languages, and rate or download limits.
- Distinguish source metadata that can be committed from source payloads that must remain local-only.
- For UMLS, SNOMED CT, MedDRA, OMIM, DECIPHER, LOINC, and national ICD variants, default to restricted or license-review mode until proven otherwise.
- For uncertain sources such as LDDB, keep the track investigation-only until authority, maintenance status, and access terms are verified.

## Restricted Payload Policy
- Commit only metadata, schemas, bounded non-restricted samples, validation summaries, review-pack structure, and derived reports allowed by source terms.
- Never commit credentials, API keys, private data, full licensed releases, raw restricted payloads, or generated artifacts that reconstruct restricted source text.
- Maintain a local-only manifest for any raw, licensed, credentialed, private, or full-release source touched during implementation.
- Require redaction or exclusion proof before phase push when a track used restricted or licensed inputs.
- CI should eventually fail on blocked filename patterns and missing local-only manifests for restricted tracks.

## Fail-Fast Probe Contract
- Run one bounded end-to-end probe before batch work for each source or validator feature.
- Source probes must produce a registry row, provenance row, validation output, and comparison or crosswalk sample when applicable.
- Automation probes must include one passing fixture and at least one expected failure fixture.
- Probe failure updates the blocker registry and prevents bulk extraction, PR-safe artifact generation, or downstream phase completion.

## Artifact Contracts
Each track must define committed, generated, local-only, reviewer-only, PR-safe, and release-safe outputs. Common ontology-network artifacts include:
- Source registry records with license, access, language, version, repository, and endpoint fields.
- Crosswalk edges keyed by HPO id, external id, mapping predicate, mapping source, confidence, and caveats.
- Multilingual comparison packs for HPO labels, HPO synonyms, source labels, source synonyms, and LLM candidates.
- Conflict reports for ambiguous, circular, deprecated, one-to-many, many-to-one, and language-specific disagreements.
- Coverage summaries by HPO branch, source, language, predicate, and review status.
- Provenance manifests, validation fixtures, local-only manifests, and human review handoff packs.

## Parallelization Groups
- `foundation`: environment, package, and shared workflow tracks. These must finish before dependent automation.
- `conductor-validation`: schema and lifecycle validation. It can run beside source-governance planning but blocks completion claims.
- `ontology-network`: shared registry, crosswalk, provenance, conflict, coverage, and release contracts. It owns shared schema merges.
- `ontology-source-governance`: individual ontology tracks. These can run in parallel after the shared registry contract exists, but only with disjoint source manifests and one merge owner per shared artifact.
- `language-profile-candidates`: LLM candidate profiles. These can run in parallel by language, but only one agent may edit a given Babelon profile at a time.
- `review-only`: review agents. These can run in parallel against committed or bounded phase output.

## Remote Delivery Contract
- Commit after every completed task.
- Run conductor-review after every phase and at full-track scope.
- Apply authorized review fixes before pushing the phase.
- Push to the remote repository after every phase.
- Check GitHub Actions for the pushed commit and PR head.
- Verify the PR is merged before marking the track complete.
- Record external blockers instead of marking completion early.
- Record PR URL, checks URL, last commit, review status, merge status, and merge commit in metadata.

## Filesystem and Repo Hygiene Gate
- Run `git diff --check` before phase push.
- Validate every `metadata.json` as JSON.
- Check for stale delivery addendum fragments, missing Phase 0 sections, and missing required metadata fields.
- Check for restricted-payload filename patterns before staging.
- On Windows and OneDrive-backed worktrees, verify no `.git/index.lock` remains and record permission blockers rather than forcing destructive cleanup.

## Additional Advanced Improvements
- Add schema-enforced Conductor validation and wire it to CI only after local fixtures pass.
- Add semantic drift reports comparing ontology release changes against the HPO release used for translation candidates.
- Add evidence scoring that separates curated mappings, exact identifiers, preferred labels, synonyms, multilingual agreement, LLM agreement, and conflicts.
- Add provenance graph exports so maintainers can trace every candidate, crosswalk, conflict, and coverage count to source release, model run, and commit.
- Add conflict heatmaps and reviewer workload estimates to prioritize human review where ontology and LLM signals disagree.
- Add reproducibility capsules with commands, source versions, permitted checksums, local-only manifests, and validation outputs.
- Add agent performance telemetry across Codex, opencode, agy, cline, mimo, local LLMs, and Hugging Face models where available, while avoiding repeated use of the same model beyond the defined triangulation cap.
- Add release-readiness scoring that fails tracks with missing source governance, blocked payload policy, stale validation, unmerged PRs, or absent human-review handoff.
