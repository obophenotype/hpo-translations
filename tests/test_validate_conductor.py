import json
import os
import shutil
import unittest
import uuid
from pathlib import Path

from scripts.validate_conductor import validate

TEST_TMP = Path(os.environ.get("CONDUCTOR_TEST_TMP", ".cache/conductor-validation-tests"))


def write_track(
    root: Path,
    track_id: str,
    metadata_updates: dict[str, object] | None = None,
    plan_text: str | None = None,
) -> None:
    track_dir = root / "conductor" / "tracks" / track_id
    track_dir.mkdir(parents=True, exist_ok=True)
    metadata: dict[str, object] = {
        "track_id": track_id,
        "type": "feature",
        "status": "planned",
        "created_at": "2026-06-23T00:00:00Z",
        "updated_at": "2026-06-23T00:00:00Z",
        "description": "Test track",
        "depends_on": [],
        "blocks": [],
        "branch": f"codex/{track_id}",
        "pr_url": None,
        "ci_status": "not_started",
        "merge_status": "not_opened",
        "last_commit": None,
        "phase_review_status": "not_started",
        "github_checks_url": None,
        "merge_commit": None,
        "parallel_group": "test",
        "priority": "P0",
        "known_blockers": [],
        "expected_blockers": [],
        "blocker_owner": "test",
        "fallback_path": "test fallback",
        "source_access_status": "not_applicable",
        "restricted_payload_policy": {
            "commit_policy": "metadata only",
            "local_only_artifacts": [],
            "blocked_patterns": ["raw"],
            "required_evidence": [],
        },
        "fail_fast_probe": {
            "required": True,
            "scope": "one passing fixture",
            "success_criteria": ["validator reports expected result"],
        },
        "artifact_contract": {
            "required_before_phase_1_completion": ["human_report"],
            "conditional_outputs": ["json_report"],
            "excluded_until_policy_allows": ["raw_payload"],
        },
        "write_owner": "test",
        "merge_owner": "test",
        "automation_readiness": "phase_0_required",
        "evidence_score_policy": {
            "candidate_only": True,
            "signals": [],
            "promotion_rule": "none",
        },
        "agent_telemetry": {
            "record_required": True,
            "fields": ["agent", "model"],
        },
        "human_review_handoff": [],
    }
    if metadata_updates:
        metadata.update(metadata_updates)
    (track_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    plan = (
        plan_text
        or """# Plan - Test track

## Phase 0: Dependency, Blocker, Source, and Automation Gates
- [ ] **Task 1:** Record blocker registry and owner.
- [ ] **Task 2:** Record source access and source_access_status.
- [ ] **Task 3:** Define restricted payload policy.
- [ ] **Task 4:** Run fail-fast probe.
- [ ] **Task 5:** Define artifact contract.
- [ ] **Task 6:** Declare parallel write ownership and write_owner.
- [ ] **Task 7:** Verify GitHub Actions, PR head, and merge gates.
- [ ] **Task 8:** Capture telemetry and model evidence.

## Phase 1: Implementation
- [ ] **Task 1:** Implement.
"""
    )
    (track_dir / "plan.md").write_text(plan, encoding="utf-8")
    (track_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")


def issue_codes(report: dict[str, object]) -> set[str]:
    issues = report["issues"]
    assert isinstance(issues, list)
    return {str(issue["code"]) for issue in issues if isinstance(issue, dict)}


class ValidateConductorTests(unittest.TestCase):
    def make_root(self) -> Path:
        TEST_TMP.mkdir(parents=True, exist_ok=True)
        root = TEST_TMP / f"case-{uuid.uuid4().hex}"
        root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_passing_track_has_no_errors(self) -> None:
        root = self.make_root()
        write_track(root, "passing_track")
        report = validate(root, run_git=False)
        issues = report["issues"]
        assert isinstance(issues, list)
        errors = [issue for issue in issues if isinstance(issue, dict) and issue["severity"] == "error"]
        self.assertEqual(errors, [])

    def test_missing_metadata_field_fails(self) -> None:
        root = self.make_root()
        write_track(root, "missing_metadata")
        metadata_path = root / "conductor" / "tracks" / "missing_metadata" / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        del metadata["artifact_contract"]
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        report = validate(root, run_git=False)
        self.assertIn("metadata.missing_required_fields", issue_codes(report))

    def test_missing_phase0_fails(self) -> None:
        root = self.make_root()
        write_track(root, "missing_phase0", plan_text="# Plan\n\n## Phase 1: Implementation\n")
        report = validate(root, run_git=False)
        self.assertIn("plan.phase0_missing", issue_codes(report))

    def test_stale_delivery_fragment_fails(self) -> None:
        root = self.make_root()
        write_track(
            root,
            "stale_fragment",
            plan_text="# Plan\n\n## Phase 1: Implementation\n- [ ] Use conductor-implement for each ready task\n",
        )
        report = validate(root, run_git=False)
        self.assertIn("plan.stale_delivery_fragment", issue_codes(report))

    def test_unknown_dependency_fails(self) -> None:
        root = self.make_root()
        write_track(root, "bad_dependency", {"depends_on": ["missing_track"]})
        report = validate(root, run_git=False)
        self.assertIn("dependency.depends_on.unknown_ref", issue_codes(report))

    def test_restricted_payload_path_warns(self) -> None:
        root = self.make_root()
        write_track(root, "payload_path")
        raw_dir = root / "exports"
        raw_dir.mkdir()
        (raw_dir / "raw_payload.tsv").write_text("source\tvalue\n", encoding="utf-8")
        report = validate(root, run_git=False)
        self.assertIn("payload.path_pattern", issue_codes(report))


if __name__ == "__main__":
    unittest.main()
