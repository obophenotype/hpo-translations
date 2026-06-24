# Project Workflow - Human Phenotype Ontology Internationalization Effort

## 1. Track Design, Dependencies, and Readiness
- Tracks must declare dependencies before implementation begins.
- Each track must identify upstream tracks, external data sources, credentials, licenses, generated artifacts, and blocked downstream tracks.
- Every plan must include a Phase 0 dependency, blocker, source, and automation gate before implementation phases.
- A task is ready only when its required inputs, source authority, write scope, validation command, expected artifact contract, and expected commit boundary are known.
- Parallel work is preferred when tasks have disjoint write sets and no unresolved dependency between them.

## 2. Blocker, Source Access, and Payload Gates
- Every track must maintain a blocker registry with `known_blockers`, `expected_blockers`, `blocker_owner`, `fallback_path`, and the current go/no-go decision.
- Source access must be classified before ingestion as open, restricted, API-only, local-only, documentation-only, or investigation-only.
- License, credential, source authority, supported-language, and version-pinning status must be recorded before any batch extraction.
- Restricted payloads, credentials, private data, licensed release archives, and full API responses stay outside committed artifacts unless the source terms explicitly allow redistribution.
- Local-only artifacts must be recorded in metadata or a manifest so reviewers can reproduce the workflow without accidentally committing restricted data.

## 3. Fail-Fast Probe and Artifact Contract
- Every source or automation track must run a fail-fast probe before bulk work.
- A source probe processes one authoritative record into the registry, provenance row, validation output, and comparison or crosswalk sample when applicable.
- An automation probe validates one passing fixture and at least one expected failure fixture before CI integration.
- Each track must define an artifact contract naming committed outputs, generated outputs, local-only outputs, downstream consumers, schemas, validation commands, freshness rules, and PR or release eligibility.
- Downstream tracks may start only after the prerequisite artifact contract is satisfied or an explicit blocked state is recorded.

## 4. Automated Implementation Loop
- Implementation uses `conductor-implement` or an equivalent agent workflow against one ready task at a time.
- Agents must not edit outside the declared task write scope unless the plan is first updated.
- After each task, run the narrowest relevant local validation command.
- After each completed task, commit immediately with a message that names the track and task.
- If a task produces generated artifacts, commit only intentional source artifacts and record ignored or local-only outputs in the plan.
- Record agent/model/runtime/source-version telemetry for translation, ontology, and validation tasks where the tool exposes it.

## 5. Phase Review, Fix, Push, and CI Loop
- At the end of every phase, run `conductor-review` against the phase changes, the plan, the spec, metadata, dependency graph, artifact contract, and project guidelines.
- Treat review findings as blocking work items for that phase.
- Apply fixes automatically when the project request authorizes fix application, then rerun the relevant validation and review gate.
- Commit phase review fixes separately when they are not part of the task commit that introduced the issue.
- Push the branch to the remote repository after each phase has passed local validation and review.
- After pushing, query GitHub Actions for the pushed commit and do not mark the phase complete until required checks pass or a concrete external blocker is recorded.
- Concrete remote checks should use `gh run list --branch <branch> --commit <sha>`, `gh pr checks <pr>`, or the repository checks URL recorded in metadata.

## 6. Track Completion, Pull Request, and Merge Verification
- A track is complete only after all phases are complete, `conductor-review` has passed at track scope, all required local checks pass, and the artifact contract is satisfied.
- Open or update a pull request for every track branch before requesting merge.
- The pull request must include implementation scope, dependencies, validation evidence, review status, CI status, known limitations, restricted-payload handling, and reviewer handoff notes.
- Check that GitHub Actions pass on the PR head commit before merge.
- Verify the PR is merged upstream before marking the track complete in `conductor/tracks.md` or metadata.
- Merge verification must confirm PR state is `MERGED`, record the merge commit, and verify the merge commit is reachable from the target branch.
- If merge is blocked by external review, branch protection, credentials, or remote availability, record the blocker in the plan and leave the track open.

## 7. Dependency Graph and Parallelization
- Maintain a dependency graph across tracks using `depends_on`, `blocks`, phase prerequisites, priority, parallel group, write owner, merge owner, and explicit artifact contracts.
- Start downstream tracks only when prerequisite phases have produced their committed artifacts or declared remote outputs.
- Parallelize by assigning independent tasks or tracks to separate agents with disjoint file ownership.
- Do not run concurrent agents against the same Babelon profile, plan file, shared schema, or generated artifact without an explicit merge owner.
- Review agents may run in parallel with implementation only when they inspect already committed or clearly bounded changes.

## 8. Automated Validation and Scheduled Audits
- Contributors must run local validation before pushing changes.
- Conductor validation should check metadata schema, dependency graph integrity, source access gates, restricted payload policy, artifact contracts, Phase 0 presence, review gates, CI gates, PR gates, and merge evidence.
- CI must run repository quality checks, translation validation, documentation checks, and Conductor validation after the validator command exists.
- Scheduled audits should continue to check all language profiles, ontology source metadata, workflow metadata, and restricted-payload patterns so schema or dependency changes do not silently break the project.

## 9. Advanced Outputs and Review Intelligence
- Ontology work should produce more than translation evidence: identifier networks, coverage maps, conflict reports, semantic drift alerts, provenance graphs, source-license reports, reviewer workload estimates, and release-readiness manifests.
- LLM-assisted translation evidence must remain candidate-only and human-review-required.
- Candidate review packs should expose model agreement, ontology agreement, source conflicts, coverage gaps, and license caveats without promoting candidates automatically.
- Performance records should capture model or agent used, runtime, validation command, validation result, conflict count, and unresolved blocker count so future tracks can select faster or more reliable agents.

## 10. Release Coordination
- Translation releases are aligned with official upstream HPO releases.
- Release assets must include versioning, provenance, dependency, validation, CI, review, restricted-payload, and merge metadata tracing back to source commits and HPO release versions.

## 11. Future Track Creation
- New tracks must start from conductor/track-template.md.
- New tracks must update conductor/dependencies.md when they add, remove, or change dependencies.
- New tracks must not begin implementation until dependency readiness, blocker registry, source access, branch, PR target, validation commands, artifact contracts, and parallelization boundaries are documented.
