import argparse
import json
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

Severity = Literal["error", "warning", "info"]

CONDUCTOR_DIR = Path("conductor")
TRACKS_DIR = CONDUCTOR_DIR / "tracks"
PHASE0_HEADING = "## Phase 0: Dependency, Blocker, Source, and Automation Gates"
STALE_DELIVERY_FRAGMENTS = [
    "Use conductor-implement for each ready task",
    "Run conductor-review after every phase, apply authorized fixes",
    "Verify GitHub Actions pass on the pushed branch and PR head",
    "Verify the PR is merged upstream before marking the track complete",
]
BLOCKED_PATH_PATTERNS = [
    "api_key",
    "credential",
    "full_release",
    "licensed",
    "private",
    "raw",
    "restricted",
    "token",
]
SKIP_PATH_PARTS = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".pixi",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "tmp",
}
KNOWN_EXTERNAL_REFS = {
    "all_future_conductor_tracks",
    "language_candidate_tracks",
}
REQUIRED_METADATA_FIELDS = {
    "agent_telemetry",
    "artifact_contract",
    "blocker_owner",
    "blocks",
    "branch",
    "ci_status",
    "depends_on",
    "expected_blockers",
    "fail_fast_probe",
    "fallback_path",
    "github_checks_url",
    "human_review_handoff",
    "known_blockers",
    "last_commit",
    "merge_commit",
    "merge_owner",
    "merge_status",
    "parallel_group",
    "phase_review_status",
    "pr_url",
    "priority",
    "restricted_payload_policy",
    "source_access_status",
    "status",
    "track_id",
    "write_owner",
}
REQUIRED_POLICY_FIELDS = {
    "blocked_patterns",
    "commit_policy",
    "local_only_artifacts",
    "required_evidence",
}
REQUIRED_PROBE_FIELDS = {
    "required",
    "scope",
    "success_criteria",
}
REQUIRED_ARTIFACT_FIELDS = {
    "conditional_outputs",
    "excluded_until_policy_allows",
    "required_before_phase_1_completion",
}
PHASE0_TOPICS = {
    "blocker": ["blocker"],
    "source_access": ["source access", "source_access_status"],
    "restricted_payload": ["restricted payload", "payload policy"],
    "fail_fast": ["fail-fast", "fail fast"],
    "artifact_contract": ["artifact contract"],
    "parallelization": ["parallel", "write ownership", "write_owner"],
    "remote_delivery": ["github actions", "pr head", "merge"],
    "telemetry": ["telemetry", "model"],
}


@dataclass(frozen=True)
class Issue:
    severity: Severity
    code: str
    message: str
    path: str
    track_id: str | None = None
    remediation: str | None = None


@dataclass(frozen=True)
class Track:
    track_id: str
    path: Path
    metadata_path: Path
    plan_path: Path
    metadata: dict[str, Any]
    plan_text: str


def _json_object(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(dict[str, Any], value)


def load_tracks(root: Path) -> tuple[list[Track], list[Issue]]:
    tracks_dir = root / TRACKS_DIR
    issues: list[Issue] = []
    tracks: list[Track] = []
    if not tracks_dir.exists():
        return [], [
            Issue(
                "error",
                "conductor.tracks_dir_missing",
                "Conductor tracks directory is missing.",
                str(tracks_dir),
                remediation="Create conductor/tracks or run Conductor setup before validation.",
            )
        ]

    for metadata_path in sorted(tracks_dir.glob("*/metadata.json")):
        track_path = metadata_path.parent
        try:
            metadata = _json_object(json.loads(metadata_path.read_text(encoding="utf-8")), metadata_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            issues.append(
                Issue(
                    "error",
                    "metadata.invalid_json",
                    f"Could not parse metadata JSON: {exc}",
                    str(metadata_path),
                    remediation="Fix the JSON syntax before continuing.",
                )
            )
            continue

        track_id = str(metadata.get("track_id") or track_path.name)
        plan_path = track_path / "plan.md"
        plan_text = ""
        if plan_path.exists():
            plan_text = plan_path.read_text(encoding="utf-8")
        tracks.append(
            Track(
                track_id=track_id,
                path=track_path,
                metadata_path=metadata_path,
                plan_path=plan_path,
                metadata=metadata,
                plan_text=plan_text,
            )
        )
    return tracks, issues


def _is_legacy(track: Track) -> bool:
    return track.metadata.get("status") == "legacy_complete"


def _require_object(track: Track, field: str, required: set[str], issues: list[Issue]) -> None:
    value = track.metadata.get(field)
    if not isinstance(value, dict):
        issues.append(
            Issue(
                "error",
                f"metadata.{field}.not_object",
                f"`{field}` must be an object.",
                str(track.metadata_path),
                track.track_id,
                remediation=f"Populate `{field}` with {', '.join(sorted(required))}.",
            )
        )
        return
    missing = sorted(required - set(value))
    if missing:
        issues.append(
            Issue(
                "error",
                f"metadata.{field}.missing_fields",
                f"`{field}` is missing required fields: {', '.join(missing)}.",
                str(track.metadata_path),
                track.track_id,
                remediation=f"Add {', '.join(missing)} to `{field}`.",
            )
        )


def validate_metadata(tracks: list[Track]) -> list[Issue]:
    issues: list[Issue] = []
    seen_ids: set[str] = set()
    for track in tracks:
        metadata = track.metadata
        if track.track_id in seen_ids:
            issues.append(
                Issue(
                    "error",
                    "metadata.duplicate_track_id",
                    f"Duplicate track_id `{track.track_id}`.",
                    str(track.metadata_path),
                    track.track_id,
                    remediation="Use a unique track_id and folder for each Conductor track.",
                )
            )
        seen_ids.add(track.track_id)

        missing = sorted(REQUIRED_METADATA_FIELDS - set(metadata))
        if missing:
            issues.append(
                Issue(
                    "error",
                    "metadata.missing_required_fields",
                    f"Missing required metadata fields: {', '.join(missing)}.",
                    str(track.metadata_path),
                    track.track_id,
                    remediation="Update metadata from conductor/track-template.md.",
                )
            )

        if metadata.get("track_id") != track.path.name:
            issues.append(
                Issue(
                    "error",
                    "metadata.track_id_folder_mismatch",
                    f"`track_id` does not match folder name `{track.path.name}`.",
                    str(track.metadata_path),
                    track.track_id,
                    remediation="Make metadata.track_id match the track folder name.",
                )
            )

        for field in ("depends_on", "blocks"):
            if field in metadata and not isinstance(metadata[field], list):
                issues.append(
                    Issue(
                        "error",
                        f"metadata.{field}.not_list",
                        f"`{field}` must be a list.",
                        str(track.metadata_path),
                        track.track_id,
                        remediation=f"Change `{field}` to a JSON list.",
                    )
                )

        for field in ("known_blockers", "expected_blockers", "human_review_handoff"):
            if field in metadata and not isinstance(metadata[field], list):
                issues.append(
                    Issue(
                        "error",
                        f"metadata.{field}.not_list",
                        f"`{field}` must be a list.",
                        str(track.metadata_path),
                        track.track_id,
                    )
                )

        _require_object(track, "restricted_payload_policy", REQUIRED_POLICY_FIELDS, issues)
        _require_object(track, "fail_fast_probe", REQUIRED_PROBE_FIELDS, issues)
        _require_object(track, "artifact_contract", REQUIRED_ARTIFACT_FIELDS, issues)

        if metadata.get("status") == "complete":
            complete_requirements = {
                "ci_status": "passing",
                "merge_status": "merged",
            }
            for field, expected in complete_requirements.items():
                if metadata.get(field) != expected:
                    issues.append(
                        Issue(
                            "error",
                            f"metadata.complete.{field}",
                            f"Complete track has `{field}={metadata.get(field)}` instead of `{expected}`.",
                            str(track.metadata_path),
                            track.track_id,
                            remediation=(
                                "Do not mark the track complete until review, CI, PR, and merge evidence exists."
                            ),
                        )
                    )
            for field in ("last_commit", "phase_review_status", "pr_url", "github_checks_url", "merge_commit"):
                if not metadata.get(field):
                    issues.append(
                        Issue(
                            "error",
                            f"metadata.complete.{field}_missing",
                            f"Complete track is missing `{field}` evidence.",
                            str(track.metadata_path),
                            track.track_id,
                        )
                    )
        elif metadata.get("status") == "planned" and metadata.get("phase_review_status") == "not_started":
            issues.append(
                Issue(
                    "info",
                    "metadata.lifecycle.planned_unreviewed",
                    "Track is planned and has not yet reached phase review.",
                    str(track.metadata_path),
                    track.track_id,
                )
            )

    return issues


def _heading_counts(plan_text: str) -> Counter[str]:
    headings = [line.strip() for line in plan_text.splitlines() if line.startswith("## ")]
    return Counter(headings)


def validate_plans(tracks: list[Track]) -> list[Issue]:
    issues: list[Issue] = []
    for track in tracks:
        if not track.plan_path.exists():
            issues.append(
                Issue(
                    "error",
                    "plan.missing",
                    "Track plan is missing.",
                    str(track.plan_path),
                    track.track_id,
                    remediation="Create plan.md for the track.",
                )
            )
            continue

        for heading, count in _heading_counts(track.plan_text).items():
            if count > 1:
                issues.append(
                    Issue(
                        "error",
                        "plan.duplicate_heading",
                        f"Duplicate heading `{heading}` appears {count} times.",
                        str(track.plan_path),
                        track.track_id,
                    )
                )

        stale_matches = [fragment for fragment in STALE_DELIVERY_FRAGMENTS if fragment in track.plan_text]
        if stale_matches:
            issues.append(
                Issue(
                    "error",
                    "plan.stale_delivery_fragment",
                    f"Plan contains stale delivery addendum fragment(s): {', '.join(stale_matches)}.",
                    str(track.plan_path),
                    track.track_id,
                    remediation="Replace loose delivery addenda with Phase 0 lifecycle gates.",
                )
            )

        if _is_legacy(track):
            continue

        if PHASE0_HEADING not in track.plan_text:
            issues.append(
                Issue(
                    "error",
                    "plan.phase0_missing",
                    "Active track is missing the required Phase 0 gate.",
                    str(track.plan_path),
                    track.track_id,
                    remediation=f"Add `{PHASE0_HEADING}` before implementation phases.",
                )
            )
            continue

        lower_plan = track.plan_text.lower()
        for topic, needles in PHASE0_TOPICS.items():
            if not any(needle in lower_plan for needle in needles):
                issues.append(
                    Issue(
                        "error",
                        f"plan.phase0.{topic}_missing",
                        f"Phase 0 does not mention required topic `{topic}`.",
                        str(track.plan_path),
                        track.track_id,
                        remediation="Update Phase 0 from conductor/track-template.md.",
                    )
                )
    return issues


def _base_ref(reference: object) -> str | None:
    if not isinstance(reference, str) or not reference:
        return None
    return reference.split(":", maxsplit=1)[0]


def validate_dependency_graph(tracks: list[Track]) -> list[Issue]:
    issues: list[Issue] = []
    track_ids = {track.track_id for track in tracks}
    for track in tracks:
        for field in ("depends_on", "blocks"):
            values = track.metadata.get(field, [])
            if not isinstance(values, list):
                continue
            for reference in values:
                base = _base_ref(reference)
                if base is None:
                    issues.append(
                        Issue(
                            "error",
                            f"dependency.{field}.invalid_ref",
                            f"`{field}` contains a non-string or empty reference: {reference!r}.",
                            str(track.metadata_path),
                            track.track_id,
                        )
                    )
                    continue
                if base not in track_ids and base not in KNOWN_EXTERNAL_REFS:
                    issues.append(
                        Issue(
                            "error",
                            f"dependency.{field}.unknown_ref",
                            f"`{field}` references unknown track or external marker `{base}`.",
                            str(track.metadata_path),
                            track.track_id,
                            remediation=(
                                "Add the referenced track metadata or register the marker "
                                "as an accepted external dependency."
                            ),
                        )
                    )
    return issues


def _iter_repo_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(part in SKIP_PATH_PARTS for part in relative.parts):
            continue
        if path.is_file():
            paths.append(relative)
    return paths


def validate_payload_paths(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for relative in _iter_repo_paths(root):
        normalized = relative.as_posix().lower()
        if normalized.endswith(".json") and normalized.startswith("conductor/tracks/"):
            continue
        matches = [pattern for pattern in BLOCKED_PATH_PATTERNS if pattern in normalized]
        if matches:
            issues.append(
                Issue(
                    "warning",
                    "payload.path_pattern",
                    f"Path matches restricted-payload pattern(s): {', '.join(matches)}.",
                    str(relative),
                    remediation=(
                        "Verify this file is not a raw, credentialed, private, or "
                        "restricted source payload before staging."
                    ),
                )
            )
    return issues


def validate_repo_hygiene(root: Path, run_git: bool) -> list[Issue]:
    issues: list[Issue] = []
    index_lock = root / ".git" / "index.lock"
    if index_lock.exists():
        issues.append(
            Issue(
                "error",
                "git.index_lock_present",
                ".git/index.lock exists.",
                str(index_lock),
                remediation="Resolve the stale or active git lock before committing.",
            )
        )
    if run_git and (root / ".git").exists():
        result = subprocess.run(
            ["git", "diff", "--check", "--", "conductor", ".github/workflows"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            issues.append(
                Issue(
                    "error",
                    "git.diff_check_failed",
                    output or "git diff --check failed.",
                    ".",
                    remediation="Fix whitespace and conflict-marker problems before phase completion.",
                )
            )
    return issues


def validate_remote_lifecycle(tracks: list[Track], check_remote: bool) -> list[Issue]:
    issues: list[Issue] = []
    for track in tracks:
        metadata = track.metadata
        if metadata.get("merge_status") == "merged" and (
            not metadata.get("pr_url") or not metadata.get("merge_commit")
        ):
            issues.append(
                Issue(
                    "error",
                    "remote.merged_missing_evidence",
                    "Merged track is missing PR URL or merge commit.",
                    str(track.metadata_path),
                    track.track_id,
                )
            )
        if check_remote and metadata.get("pr_url"):
            result = subprocess.run(
                ["gh", "pr", "checks", str(metadata["pr_url"])],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                output = (result.stdout + result.stderr).strip()
                issues.append(
                    Issue(
                        "warning",
                        "remote.gh_pr_checks_unavailable",
                        output or "Could not query GitHub PR checks.",
                        str(track.metadata_path),
                        track.track_id,
                        remediation=(
                            "Record GitHub authentication or network blockers in metadata if remote checks cannot run."
                        ),
                    )
                )
    return issues


def release_readiness(tracks: list[Track], issues: list[Issue]) -> dict[str, Any]:
    issue_counts = Counter(issue.severity for issue in issues)
    statuses = Counter(str(track.metadata.get("status")) for track in tracks)
    source_states = Counter(str(track.metadata.get("source_access_status")) for track in tracks)
    open_blockers = sum(len(track.metadata.get("known_blockers", [])) for track in tracks)
    return {
        "track_count": len(tracks),
        "status_counts": dict(sorted(statuses.items())),
        "source_access_counts": dict(sorted(source_states.items())),
        "issue_counts": dict(sorted(issue_counts.items())),
        "known_blocker_count": open_blockers,
        "release_ready": issue_counts["error"] == 0,
    }


def validate(root: Path, run_git: bool = True, check_remote: bool = False) -> dict[str, Any]:
    tracks, issues = load_tracks(root)
    issues.extend(validate_metadata(tracks))
    issues.extend(validate_plans(tracks))
    issues.extend(validate_dependency_graph(tracks))
    issues.extend(validate_payload_paths(root))
    issues.extend(validate_repo_hygiene(root, run_git))
    issues.extend(validate_remote_lifecycle(tracks, check_remote))
    return {
        "summary": release_readiness(tracks, issues),
        "issues": [asdict(issue) for issue in issues],
        "tracks": [
            {
                "track_id": track.track_id,
                "status": track.metadata.get("status"),
                "priority": track.metadata.get("priority"),
                "source_access_status": track.metadata.get("source_access_status"),
                "ci_status": track.metadata.get("ci_status"),
                "phase_review_status": track.metadata.get("phase_review_status"),
                "merge_status": track.metadata.get("merge_status"),
                "path": str(track.path),
            }
            for track in tracks
        ],
    }


def render_text(report: dict[str, Any]) -> str:
    summary = cast(dict[str, Any], report["summary"])
    issues = cast(list[dict[str, Any]], report["issues"])
    lines = [
        "# Conductor Validation Report",
        "",
        f"- Tracks: {summary['track_count']}",
        f"- Release ready: {str(summary['release_ready']).lower()}",
        f"- Issue counts: {json.dumps(summary['issue_counts'], sort_keys=True)}",
        f"- Status counts: {json.dumps(summary['status_counts'], sort_keys=True)}",
        f"- Source access counts: {json.dumps(summary['source_access_counts'], sort_keys=True)}",
        f"- Known blocker count: {summary['known_blocker_count']}",
        "",
        "## Issues",
    ]
    if not issues:
        lines.append("- None")
    else:
        for issue in issues:
            track = f" [{issue['track_id']}]" if issue.get("track_id") else ""
            lines.append(
                f"- {str(issue['severity']).upper()} {issue['code']}{track}: {issue['message']} ({issue['path']})"
            )
            if issue.get("remediation"):
                lines.append(f"  Remediation: {issue['remediation']}")
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], json_output: Path | None, text_output: Path | None) -> None:
    if json_output is not None:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if text_output is not None:
        text_output.parent.mkdir(parents=True, exist_ok=True)
        text_output.write_text(render_text(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Conductor track lifecycle metadata and plans.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate.")
    parser.add_argument("--json-output", type=Path, help="Optional path for machine-readable JSON report.")
    parser.add_argument("--text-output", type=Path, help="Optional path for Markdown/text report.")
    parser.add_argument("--skip-git", action="store_true", help="Skip git diff and index-lock checks.")
    parser.add_argument("--check-remote", action="store_true", help="Attempt optional GitHub CLI PR checks.")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Exit non-zero when warnings are present.")
    args = parser.parse_args()

    root = args.root.resolve()
    report = validate(root, run_git=not args.skip_git, check_remote=args.check_remote)
    write_report(report, args.json_output, args.text_output)
    print(render_text(report), end="")

    issues = cast(list[dict[str, Any]], report["issues"])
    has_errors = any(issue["severity"] == "error" for issue in issues)
    has_warnings = any(issue["severity"] == "warning" for issue in issues)
    raise SystemExit(1 if has_errors or (args.warnings_as_errors and has_warnings) else 0)


if __name__ == "__main__":
    main()
