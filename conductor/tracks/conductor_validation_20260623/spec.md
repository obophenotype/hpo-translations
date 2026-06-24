# Spec - Implement automated Conductor validation and lifecycle gates

## Objective
Create an automated validation track that turns the Conductor lifecycle rules into machine-checkable gates for all current and future tracks.

## Scope
- Validate `metadata.json` files for required lifecycle, blocker, source access, payload policy, artifact contract, automation, telemetry, and merge fields.
- Validate track plans for Phase 0 gates, stale delivery fragments, review gates, validation gates, CI gates, and merge gates.
- Validate dependency graph references across `depends_on`, `blocks`, `parallel_group`, priority, write owner, and merge owner.
- Validate restricted-source tracks have source access status, restricted payload policy, local-only manifest requirements, and blocked-payload patterns.
- Emit a human-readable report, machine-readable JSON report, and CI-ready summary.

## Out of Scope
- Reading, downloading, or committing licensed ontology payloads.
- Deciding legal license interpretation beyond recording required review status and blocking unsafe payload handling.
- Replacing human translation review.

## Acceptance Criteria
- The validator can identify missing required metadata fields across all tracks.
- The validator can fail on missing Phase 0 gates, stale delivery addendum fragments, and unresolved restricted-source policy.
- The validator emits per-track remediation steps suitable for conductor-implement or conductor-review follow-up.
- CI integration is added only after local fixtures prove passing and failing cases behave deterministically.
