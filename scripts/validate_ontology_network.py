from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.build_ontology_network import schema_definitions

Severity = Literal["error", "warning", "info"]
ArtifactKind = Literal["registry", "crosswalk", "conflict", "coverage", "review_pack"]
Record = dict[str, Any]

HPO_ID_RE = re.compile(r"^HP:\d{7}$")
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ACCESS_MODES = {
    "open",
    "restricted",
    "api_only",
    "local_only",
    "documentation_only",
    "investigation_only",
}
ARTIFACT_CLASSES = {
    "committed",
    "generated",
    "local_only",
    "reviewer_only",
    "pr_safe",
    "release_safe",
}
MAPPING_PREDICATES = {
    "exactMatch",
    "closeMatch",
    "broadMatch",
    "narrowMatch",
    "relatedMatch",
    "hasDbXref",
    "sourceCurated",
}
MAPPING_BASES = {
    "curated_identifier",
    "source_xref",
    "exact_identifier",
    "lexical_exact",
    "text_similarity",
    "llm_assisted",
}
NON_DETERMINISTIC_MAPPING_BASES = {"text_similarity", "llm_assisted"}
REVIEW_STATUSES = {"unreviewed", "needs_review", "reviewed", "accepted", "rejected"}
CONFLICT_TYPES = {
    "one_to_many",
    "many_to_one",
    "source_disagreement",
    "deprecated_mapping",
    "ambiguous_mapping",
    "circular_mapping",
    "label_disagreement",
    "language_disagreement",
}
CONFLICT_SEVERITIES = {"info", "low", "medium", "high", "blocking"}
CONFLICT_RESOLUTION_STATUSES = {"open", "needs_review", "resolved", "accepted_risk", "rejected"}
PROMOTION_POLICIES = {"manual_review_only", "human_review_required", "candidate_only"}

ACCESS_MODE_ALIASES = {
    "API-only": "api_only",
    "api-only": "api_only",
    "documentation-only": "documentation_only",
    "investigation-only": "investigation_only",
    "local-only": "local_only",
    "open": "open",
    "restricted": "restricted",
}

REQUIRED_FIELDS: dict[ArtifactKind, set[str]] = {
    "registry": {
        "source_id",
        "source_name",
        "source_version",
        "license_name",
        "access_mode",
        "source_access_status",
        "supported_languages",
        "authoritative_endpoint",
        "retrieval_date",
        "payload_commit_allowed",
        "derived_commit_allowed",
        "local_only",
        "payload_policy",
        "artifact_classes",
        "provenance_id",
    },
    "crosswalk": {
        "edge_id",
        "hpo_id",
        "external_source_id",
        "external_id",
        "mapping_predicate",
        "mapping_source",
        "mapping_basis",
        "confidence",
        "provenance_id",
        "review_status",
        "candidate_only",
        "human_review_required",
    },
    "conflict": {
        "conflict_id",
        "conflict_type",
        "severity",
        "hpo_id",
        "source_ids",
        "evidence_ids",
        "resolution_status",
        "reviewer_action",
        "provenance_id",
    },
    "coverage": {
        "coverage_id",
        "source_id",
        "hpo_branch_id",
        "language",
        "predicate",
        "total_hpo_terms",
        "covered_hpo_terms",
        "coverage_ratio",
        "review_status",
        "provenance_id",
    },
    "review_pack": {
        "pack_id",
        "language",
        "scope",
        "hpo_ids",
        "source_ids",
        "crosswalk_ids",
        "conflict_ids",
        "coverage_ids",
        "candidate_count",
        "candidate_only",
        "human_review_required",
        "promotion_policy",
        "reviewer_role",
        "provenance_id",
    },
}

SCHEMA_ARTIFACTS: dict[ArtifactKind, dict[str, Any]] = {
    "registry": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Ontology source registry record",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_FIELDS["registry"]),
        "properties": {
            "source_id": {"type": "string", "minLength": 1},
            "source_name": {"type": "string", "minLength": 1},
            "source_version": {"type": "string", "minLength": 1},
            "license_name": {"type": "string", "minLength": 1},
            "access_mode": {"type": "string", "enum": sorted(ACCESS_MODES)},
            "source_access_status": {"type": "string", "minLength": 1},
            "supported_languages": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "authoritative_endpoint": {"type": "string", "minLength": 1},
            "retrieval_date": {"type": "string", "format": "date"},
            "payload_commit_allowed": {"type": "boolean"},
            "derived_commit_allowed": {"type": "boolean"},
            "local_only": {"type": "boolean"},
            "payload_policy": {"type": "string", "minLength": 1},
            "artifact_classes": {"type": "array", "items": {"type": "string", "enum": sorted(ARTIFACT_CLASSES)}},
            "provenance_id": {"type": "string", "minLength": 1},
        },
        "x-rules": [
            "restricted and local_only sources must set payload_commit_allowed=false",
            "local_only sources must set local_only=true",
            "source_access_status must not be not_applicable",
        ],
    },
    "crosswalk": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Ontology identifier crosswalk edge",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_FIELDS["crosswalk"]),
        "properties": {
            "edge_id": {"type": "string", "minLength": 1},
            "hpo_id": {"type": "string", "pattern": HPO_ID_RE.pattern},
            "external_source_id": {"type": "string", "minLength": 1},
            "external_id": {"type": "string", "minLength": 1},
            "mapping_predicate": {"type": "string", "enum": sorted(MAPPING_PREDICATES)},
            "mapping_source": {"type": "string", "minLength": 1},
            "mapping_basis": {"type": "string", "enum": sorted(MAPPING_BASES)},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "provenance_id": {"type": "string", "minLength": 1},
            "review_status": {"type": "string", "enum": sorted(REVIEW_STATUSES)},
            "candidate_only": {"type": "boolean", "const": True},
            "human_review_required": {"type": "boolean", "const": True},
        },
        "x-rules": [
            "external_source_id should exist in the source registry when registry records are supplied",
            "text_similarity and llm_assisted mapping bases are warning-only candidate evidence",
            "duplicate edge identity is an error",
        ],
    },
    "conflict": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Ontology network conflict report row",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_FIELDS["conflict"]),
        "properties": {
            "conflict_id": {"type": "string", "minLength": 1},
            "conflict_type": {"type": "string", "enum": sorted(CONFLICT_TYPES)},
            "severity": {"type": "string", "enum": sorted(CONFLICT_SEVERITIES)},
            "hpo_id": {"type": "string", "pattern": HPO_ID_RE.pattern},
            "source_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "evidence_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "resolution_status": {"type": "string", "enum": sorted(CONFLICT_RESOLUTION_STATUSES)},
            "reviewer_action": {"type": "string", "minLength": 1},
            "provenance_id": {"type": "string", "minLength": 1},
        },
    },
    "coverage": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Ontology coverage summary row",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_FIELDS["coverage"]),
        "properties": {
            "coverage_id": {"type": "string", "minLength": 1},
            "source_id": {"type": "string", "minLength": 1},
            "hpo_branch_id": {"type": "string", "pattern": HPO_ID_RE.pattern},
            "language": {"type": "string"},
            "predicate": {"type": "string", "minLength": 1},
            "total_hpo_terms": {"type": "integer", "minimum": 0},
            "covered_hpo_terms": {"type": "integer", "minimum": 0},
            "coverage_ratio": {"type": "number", "minimum": 0, "maximum": 1},
            "review_status": {"type": "string", "enum": sorted(REVIEW_STATUSES)},
            "provenance_id": {"type": "string", "minLength": 1},
        },
        "x-rules": ["coverage_ratio must match covered_hpo_terms / total_hpo_terms"],
    },
    "review_pack": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Candidate translation review pack",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(REQUIRED_FIELDS["review_pack"]),
        "properties": {
            "pack_id": {"type": "string", "minLength": 1},
            "language": {"type": "string"},
            "scope": {"type": "string", "minLength": 1},
            "hpo_ids": {"type": "array", "items": {"type": "string", "pattern": HPO_ID_RE.pattern}, "minItems": 1},
            "source_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "crosswalk_ids": {"type": "array", "items": {"type": "string"}},
            "conflict_ids": {"type": "array", "items": {"type": "string"}},
            "coverage_ids": {"type": "array", "items": {"type": "string"}},
            "candidate_count": {"type": "integer", "minimum": 0},
            "candidate_only": {"type": "boolean", "const": True},
            "human_review_required": {"type": "boolean", "const": True},
            "promotion_policy": {"type": "string", "enum": sorted(PROMOTION_POLICIES)},
            "reviewer_role": {"type": "string", "minLength": 1},
            "provenance_id": {"type": "string", "minLength": 1},
        },
        "x-rules": [
            "review packs must remain candidate-only and human-review-required",
            "at least one crosswalk, conflict, or coverage evidence id must be present",
        ],
    },
}


@dataclass(frozen=True)
class Issue:
    severity: Severity
    code: str
    message: str
    path: str
    artifact_kind: ArtifactKind | None = None
    record_id: str | None = None
    remediation: str | None = None


@dataclass(frozen=True)
class LoadedRecords:
    kind: ArtifactKind
    path: Path
    records: list[Record]


@dataclass(frozen=True)
class ValidationContext:
    registry_source_ids: frozenset[str]


def _location(path: Path, index: int) -> str:
    return f"{path}#record={index + 1}"


def _record_id(record: Record, fallback: str) -> str:
    for field in ("source_id", "edge_id", "conflict_id", "coverage_id", "pack_id"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return fallback


def _missing_required(kind: ArtifactKind, record: Record, path: Path, index: int) -> list[Issue]:
    missing = sorted(field for field in REQUIRED_FIELDS[kind] if field not in record)
    if not missing:
        return []
    return [
        Issue(
            "error",
            f"{kind}.missing_required_fields",
            f"Missing required fields: {', '.join(missing)}.",
            _location(path, index),
            kind,
            _record_id(record, f"record-{index + 1}"),
            remediation=f"Add {', '.join(missing)} to the {kind} record.",
        )
    ]


def _string(record: Record, field: str) -> str | None:
    value = record.get(field)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _issue_empty_string(kind: ArtifactKind, record: Record, path: Path, index: int, field: str) -> Issue | None:
    if field not in record:
        return None
    if _string(record, field) is not None:
        return None
    return Issue(
        "error",
        f"{kind}.{field}.empty",
        f"`{field}` must be a non-empty string.",
        _location(path, index),
        kind,
        _record_id(record, f"record-{index + 1}"),
    )


def _split_scalar_list(value: str) -> list[str]:
    for delimiter in ("|", ";", ","):
        if delimiter in value:
            return [part.strip() for part in value.split(delimiter) if part.strip()]
    return [value.strip()] if value.strip() else []


def _list(record: Record, field: str) -> list[Any] | None:
    value = record.get(field)
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return _split_scalar_list(value)
    return None


def _bool(record: Record, field: str) -> bool | None:
    value = record.get(field)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None


def _int(record: Record, field: str) -> int | None:
    value = record.get(field)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def _float(record: Record, field: str) -> float | None:
    value = record.get(field)
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _date_string(value: str) -> bool:
    if not DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _language(value: str) -> bool:
    return value in {"und", "zxx"} or LANGUAGE_RE.match(value) is not None


def _enum_issue(
    kind: ArtifactKind,
    record: Record,
    path: Path,
    index: int,
    field: str,
    allowed: set[str],
) -> Issue | None:
    value = _string(record, field)
    if value is None or value in allowed:
        return None
    return Issue(
        "error",
        f"{kind}.{field}.invalid",
        f"`{field}` must be one of {', '.join(sorted(allowed))}; got `{value}`.",
        _location(path, index),
        kind,
        _record_id(record, f"record-{index + 1}"),
    )


def _list_issue(
    kind: ArtifactKind,
    record: Record,
    path: Path,
    index: int,
    field: str,
    *,
    min_items: int = 0,
) -> Issue | None:
    value = _list(record, field)
    if value is not None and len(value) >= min_items and all(isinstance(item, str) and item.strip() for item in value):
        return None
    requirement = "a list"
    if min_items > 0:
        requirement = f"a list with at least {min_items} item(s)"
    return Issue(
        "error",
        f"{kind}.{field}.invalid_list",
        f"`{field}` must be {requirement}.",
        _location(path, index),
        kind,
        _record_id(record, f"record-{index + 1}"),
    )


def _bool_issue(kind: ArtifactKind, record: Record, path: Path, index: int, field: str) -> Issue | None:
    if _bool(record, field) is not None:
        return None
    return Issue(
        "error",
        f"{kind}.{field}.invalid_bool",
        f"`{field}` must be a boolean.",
        _location(path, index),
        kind,
        _record_id(record, f"record-{index + 1}"),
    )


def _hpo_issue(kind: ArtifactKind, record: Record, path: Path, index: int, field: str) -> Issue | None:
    value = _string(record, field)
    if value is None or HPO_ID_RE.match(value):
        return None
    return Issue(
        "error",
        f"{kind}.{field}.invalid_hpo_id",
        f"`{field}` must be an HPO identifier like HP:0000001.",
        _location(path, index),
        kind,
        _record_id(record, f"record-{index + 1}"),
    )


def _unknown_source_issue(
    kind: ArtifactKind,
    source_id: str,
    record: Record,
    path: Path,
    index: int,
    context: ValidationContext,
) -> Issue | None:
    if not context.registry_source_ids or source_id in context.registry_source_ids:
        return None
    return Issue(
        "error",
        f"{kind}.source_id.unknown",
        f"Source `{source_id}` is not present in supplied registry records.",
        _location(path, index),
        kind,
        _record_id(record, f"record-{index + 1}"),
        remediation="Add the source registry record or fix the artifact source id.",
    )


def _normalise_access_mode(value: Any) -> str:
    text = str(value or "").strip()
    return ACCESS_MODE_ALIASES.get(text, text.replace("-", "_").replace("API", "api"))


def _normalise_registry_record(record: Record, generated_date: str) -> Record:
    if "source_name" in record and "supported_languages" in record:
        normalised = dict(record)
        normalised["access_mode"] = _normalise_access_mode(normalised.get("access_mode"))
        normalised["source_version"] = str(normalised.get("source_version") or "not_pinned_in_artifact")
        return normalised
    access_class = str(record.get("access_class") or record.get("access_mode") or "")
    artifact_classes = ["committed", "generated", "pr_safe"]
    if record.get("release_safe") is True:
        artifact_classes.append("release_safe")
    return {
        "source_id": record.get("source_id"),
        "source_name": record.get("ontology_name") or record.get("source_name"),
        "source_version": str(record.get("source_version") or record.get("version_status") or "not_pinned_in_artifact"),
        "license_name": record.get("license_status") or record.get("license_name") or "terms_review_required",
        "access_mode": _normalise_access_mode(access_class),
        "source_access_status": record.get("source_access_status") or "not_recorded",
        "supported_languages": record.get("language_codes") or record.get("supported_languages") or ["und"],
        "authoritative_endpoint": record.get("authoritative_endpoint_status")
        or record.get("authoritative_endpoint")
        or "not_recorded",
        "retrieval_date": generated_date,
        "payload_commit_allowed": bool(record.get("payload_commit_allowed", False)),
        "derived_commit_allowed": True,
        "local_only": access_class == "local-only",
        "payload_policy": record.get("source_payload_commit_policy")
        or record.get("payload_policy")
        or "payload-free metadata only",
        "artifact_classes": artifact_classes,
        "provenance_id": record.get("source_id") or record.get("provenance_id") or "unknown-source",
    }


def _normalise_record(kind: ArtifactKind, record: Record, generated_date: str) -> Record:
    if kind == "registry":
        return _normalise_registry_record(record, generated_date)
    return record


def _json_records_from_value(kind: ArtifactKind, value: Any) -> tuple[list[Any], str]:
    if isinstance(value, list):
        return value, "not_recorded"
    if not isinstance(value, dict):
        raise ValueError("JSON artifact must contain an object or list of objects")
    generated_date = str(value.get("generated_date") or "not_recorded")
    if kind == "crosswalk" and isinstance(value.get("edges"), list):
        return cast(list[Any], value["edges"]), generated_date
    if isinstance(value.get("records"), list):
        return cast(list[Any], value["records"]), generated_date
    return [value], generated_date


def load_records(kind: ArtifactKind, path: Path) -> tuple[LoadedRecords | None, list[Issue]]:
    if not path.exists():
        return None, [
            Issue(
                "error",
                f"{kind}.path_missing",
                "Artifact path does not exist.",
                str(path),
                kind,
                remediation="Pass an existing JSON, JSONL, CSV, or TSV artifact path.",
            )
        ]

    generated_date = "not_recorded"
    try:
        suffix = path.suffix.lower()
        if suffix == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
            records, generated_date = _json_records_from_value(kind, value)
        elif suffix in {".jsonl", ".ndjson"}:
            records = []
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {line_number} is not a JSON object")
                records.append(value)
        elif suffix in {".csv", ".tsv"}:
            delimiter = "\t" if suffix == ".tsv" else ","
            with path.open(encoding="utf-8", newline="") as handle:
                records = [dict(row) for row in csv.DictReader(handle, delimiter=delimiter)]
        else:
            raise ValueError("unsupported artifact extension; use .json, .jsonl, .ndjson, .csv, or .tsv")
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        return None, [
            Issue(
                "error",
                f"{kind}.parse_failed",
                f"Could not parse artifact: {exc}",
                str(path),
                kind,
                remediation="Fix the artifact syntax before schema validation.",
            )
        ]

    invalid = [
        Issue(
            "error",
            f"{kind}.record.not_object",
            "Each artifact record must be an object.",
            _location(path, index),
            kind,
        )
        for index, record in enumerate(records)
        if not isinstance(record, dict)
    ]
    if invalid:
        return None, invalid
    normalised_records = [_normalise_record(kind, cast(Record, record), generated_date) for record in records]
    return LoadedRecords(kind, path, normalised_records), []


def validate_registry(loaded: LoadedRecords) -> tuple[list[Issue], frozenset[str]]:
    issues: list[Issue] = []
    source_ids: set[str] = set()
    seen_ids: set[str] = set()
    for index, record in enumerate(loaded.records):
        issues.extend(_missing_required("registry", record, loaded.path, index))
        for field in (
            "source_id",
            "source_name",
            "source_version",
            "license_name",
            "source_access_status",
            "authoritative_endpoint",
            "payload_policy",
            "provenance_id",
        ):
            issue = _issue_empty_string("registry", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)

        source_id = _string(record, "source_id")
        if source_id is not None:
            source_ids.add(source_id)
            if source_id in seen_ids:
                issues.append(
                    Issue(
                        "error",
                        "registry.source_id.duplicate",
                        f"Duplicate source_id `{source_id}`.",
                        _location(loaded.path, index),
                        "registry",
                        source_id,
                    )
                )
            seen_ids.add(source_id)

        access_issue = _enum_issue("registry", record, loaded.path, index, "access_mode", ACCESS_MODES)
        if access_issue is not None:
            issues.append(access_issue)
        for field in ("payload_commit_allowed", "derived_commit_allowed", "local_only"):
            issue = _bool_issue("registry", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)

        for field, min_items in (("supported_languages", 1), ("artifact_classes", 1)):
            issue = _list_issue("registry", record, loaded.path, index, field, min_items=min_items)
            if issue is not None:
                issues.append(issue)

        languages = _list(record, "supported_languages") or []
        for language in languages:
            if isinstance(language, str) and not _language(language):
                issues.append(
                    Issue(
                        "error",
                        "registry.supported_languages.invalid_language",
                        f"Unsupported language tag `{language}`.",
                        _location(loaded.path, index),
                        "registry",
                        _record_id(record, f"record-{index + 1}"),
                    )
                )

        artifact_classes = _list(record, "artifact_classes") or []
        invalid_classes = sorted(
            item for item in artifact_classes if isinstance(item, str) and item not in ARTIFACT_CLASSES
        )
        if invalid_classes:
            issues.append(
                Issue(
                    "error",
                    "registry.artifact_classes.invalid",
                    f"Unknown artifact class(es): {', '.join(invalid_classes)}.",
                    _location(loaded.path, index),
                    "registry",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        retrieval_date = _string(record, "retrieval_date")
        if retrieval_date is not None and not _date_string(retrieval_date):
            issues.append(
                Issue(
                    "error",
                    "registry.retrieval_date.invalid_date",
                    "`retrieval_date` must be YYYY-MM-DD.",
                    _location(loaded.path, index),
                    "registry",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        source_access_status = _string(record, "source_access_status")
        if source_access_status == "not_applicable":
            issues.append(
                Issue(
                    "error",
                    "registry.source_access_status.not_applicable",
                    "Source registry rows must record a concrete source access status.",
                    _location(loaded.path, index),
                    "registry",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        access_mode = _string(record, "access_mode")
        payload_commit_allowed = _bool(record, "payload_commit_allowed")
        local_only = _bool(record, "local_only")
        if access_mode in {"restricted", "local_only"} and payload_commit_allowed is True:
            issues.append(
                Issue(
                    "error",
                    "registry.payload_commit_allowed.restricted_source",
                    "`payload_commit_allowed` must be false for restricted or local-only sources.",
                    _location(loaded.path, index),
                    "registry",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if access_mode == "local_only" and local_only is not True:
            issues.append(
                Issue(
                    "error",
                    "registry.local_only.inconsistent",
                    "`local_only` must be true when access_mode is local_only.",
                    _location(loaded.path, index),
                    "registry",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
    return issues, frozenset(source_ids)


def validate_crosswalk(loaded: LoadedRecords, context: ValidationContext) -> list[Issue]:
    issues: list[Issue] = []
    seen_edges: set[tuple[str, str, str, str, str]] = set()
    for index, record in enumerate(loaded.records):
        issues.extend(_missing_required("crosswalk", record, loaded.path, index))
        for field in ("edge_id", "external_source_id", "external_id", "mapping_source", "provenance_id"):
            issue = _issue_empty_string("crosswalk", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)

        for field, allowed in (
            ("mapping_predicate", MAPPING_PREDICATES),
            ("mapping_basis", MAPPING_BASES),
            ("review_status", REVIEW_STATUSES),
        ):
            issue = _enum_issue("crosswalk", record, loaded.path, index, field, allowed)
            if issue is not None:
                issues.append(issue)

        hpo_issue = _hpo_issue("crosswalk", record, loaded.path, index, "hpo_id")
        if hpo_issue is not None:
            issues.append(hpo_issue)

        source_id = _string(record, "external_source_id")
        if source_id is not None:
            issue = _unknown_source_issue("crosswalk", source_id, record, loaded.path, index, context)
            if issue is not None:
                issues.append(issue)

        confidence = _float(record, "confidence")
        if confidence is None or not 0 <= confidence <= 1:
            issues.append(
                Issue(
                    "error",
                    "crosswalk.confidence.invalid",
                    "`confidence` must be a number between 0 and 1.",
                    _location(loaded.path, index),
                    "crosswalk",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        for field in ("candidate_only", "human_review_required"):
            issue = _bool_issue("crosswalk", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)
        if _bool(record, "candidate_only") is not True:
            issues.append(
                Issue(
                    "error",
                    "crosswalk.candidate_only.required",
                    "Crosswalk evidence must remain candidate-only.",
                    _location(loaded.path, index),
                    "crosswalk",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if _bool(record, "human_review_required") is not True:
            issues.append(
                Issue(
                    "error",
                    "crosswalk.human_review_required.required",
                    "Crosswalk evidence must require human review before promotion.",
                    _location(loaded.path, index),
                    "crosswalk",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        mapping_basis = _string(record, "mapping_basis")
        if mapping_basis in NON_DETERMINISTIC_MAPPING_BASES:
            issues.append(
                Issue(
                    "warning",
                    "crosswalk.mapping_basis.nondeterministic",
                    f"`{mapping_basis}` mappings are candidate evidence and require deterministic follow-up.",
                    _location(loaded.path, index),
                    "crosswalk",
                    _record_id(record, f"record-{index + 1}"),
                    remediation=(
                        "Prefer curated identifiers, source xrefs, or exact identifiers for release-safe crosswalks."
                    ),
                )
            )

        edge_key_values = (
            _string(record, "hpo_id"),
            _string(record, "external_source_id"),
            _string(record, "external_id"),
            _string(record, "mapping_predicate"),
            _string(record, "mapping_source"),
        )
        if all(value is not None for value in edge_key_values):
            edge_key = cast(tuple[str, str, str, str, str], edge_key_values)
            if edge_key in seen_edges:
                issues.append(
                    Issue(
                        "error",
                        "crosswalk.edge.duplicate",
                        "Duplicate crosswalk edge identity.",
                        _location(loaded.path, index),
                        "crosswalk",
                        _record_id(record, f"record-{index + 1}"),
                    )
                )
            seen_edges.add(edge_key)
    return issues


def validate_conflict(loaded: LoadedRecords, context: ValidationContext) -> list[Issue]:
    issues: list[Issue] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(loaded.records):
        issues.extend(_missing_required("conflict", record, loaded.path, index))
        for field in ("conflict_id", "reviewer_action", "provenance_id"):
            issue = _issue_empty_string("conflict", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)

        for field, allowed in (
            ("conflict_type", CONFLICT_TYPES),
            ("severity", CONFLICT_SEVERITIES),
            ("resolution_status", CONFLICT_RESOLUTION_STATUSES),
        ):
            issue = _enum_issue("conflict", record, loaded.path, index, field, allowed)
            if issue is not None:
                issues.append(issue)

        hpo_issue = _hpo_issue("conflict", record, loaded.path, index, "hpo_id")
        if hpo_issue is not None:
            issues.append(hpo_issue)

        conflict_id = _string(record, "conflict_id")
        if conflict_id is not None:
            if conflict_id in seen_ids:
                issues.append(
                    Issue(
                        "error",
                        "conflict.conflict_id.duplicate",
                        f"Duplicate conflict_id `{conflict_id}`.",
                        _location(loaded.path, index),
                        "conflict",
                        conflict_id,
                    )
                )
            seen_ids.add(conflict_id)

        for field in ("source_ids", "evidence_ids"):
            issue = _list_issue("conflict", record, loaded.path, index, field, min_items=1)
            if issue is not None:
                issues.append(issue)

        source_ids = _list(record, "source_ids") or []
        for source_id in source_ids:
            if isinstance(source_id, str):
                issue = _unknown_source_issue("conflict", source_id, record, loaded.path, index, context)
                if issue is not None:
                    issues.append(issue)

        conflict_type = _string(record, "conflict_type")
        if conflict_type in {"one_to_many", "many_to_one", "source_disagreement", "label_disagreement"}:
            unique_sources = {source_id for source_id in source_ids if isinstance(source_id, str) and source_id}
            if len(unique_sources) < 2:
                issues.append(
                    Issue(
                        "error",
                        "conflict.source_ids.too_few_for_conflict_type",
                        f"`{conflict_type}` conflicts require at least two source_ids.",
                        _location(loaded.path, index),
                        "conflict",
                        _record_id(record, f"record-{index + 1}"),
                    )
                )
    return issues


def validate_coverage(loaded: LoadedRecords, context: ValidationContext) -> list[Issue]:
    issues: list[Issue] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(loaded.records):
        issues.extend(_missing_required("coverage", record, loaded.path, index))
        for field in ("coverage_id", "source_id", "language", "predicate", "provenance_id"):
            issue = _issue_empty_string("coverage", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)

        coverage_id = _string(record, "coverage_id")
        if coverage_id is not None:
            if coverage_id in seen_ids:
                issues.append(
                    Issue(
                        "error",
                        "coverage.coverage_id.duplicate",
                        f"Duplicate coverage_id `{coverage_id}`.",
                        _location(loaded.path, index),
                        "coverage",
                        coverage_id,
                    )
                )
            seen_ids.add(coverage_id)

        hpo_issue = _hpo_issue("coverage", record, loaded.path, index, "hpo_branch_id")
        if hpo_issue is not None:
            issues.append(hpo_issue)

        language = _string(record, "language")
        if language is not None and not _language(language):
            issues.append(
                Issue(
                    "error",
                    "coverage.language.invalid",
                    f"Unsupported language tag `{language}`.",
                    _location(loaded.path, index),
                    "coverage",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        source_id = _string(record, "source_id")
        if source_id is not None:
            issue = _unknown_source_issue("coverage", source_id, record, loaded.path, index, context)
            if issue is not None:
                issues.append(issue)

        review_issue = _enum_issue("coverage", record, loaded.path, index, "review_status", REVIEW_STATUSES)
        if review_issue is not None:
            issues.append(review_issue)

        total = _int(record, "total_hpo_terms")
        covered = _int(record, "covered_hpo_terms")
        ratio = _float(record, "coverage_ratio")
        if total is None or total < 0:
            issues.append(
                Issue(
                    "error",
                    "coverage.total_hpo_terms.invalid",
                    "`total_hpo_terms` must be a non-negative integer.",
                    _location(loaded.path, index),
                    "coverage",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if covered is None or covered < 0:
            issues.append(
                Issue(
                    "error",
                    "coverage.covered_hpo_terms.invalid",
                    "`covered_hpo_terms` must be a non-negative integer.",
                    _location(loaded.path, index),
                    "coverage",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if total is not None and covered is not None and covered > total:
            issues.append(
                Issue(
                    "error",
                    "coverage.covered_hpo_terms.exceeds_total",
                    "`covered_hpo_terms` cannot exceed `total_hpo_terms`.",
                    _location(loaded.path, index),
                    "coverage",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if ratio is None or not 0 <= ratio <= 1:
            issues.append(
                Issue(
                    "error",
                    "coverage.coverage_ratio.invalid",
                    "`coverage_ratio` must be a number between 0 and 1.",
                    _location(loaded.path, index),
                    "coverage",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if total is not None and covered is not None and ratio is not None and total >= 0 and covered <= total:
            expected_ratio = 0.0 if total == 0 else covered / total
            if abs(ratio - expected_ratio) > 0.0001:
                issues.append(
                    Issue(
                        "error",
                        "coverage.coverage_ratio.mismatch",
                        "`coverage_ratio` must equal covered_hpo_terms / total_hpo_terms.",
                        _location(loaded.path, index),
                        "coverage",
                        _record_id(record, f"record-{index + 1}"),
                    )
                )
    return issues


def validate_review_pack(loaded: LoadedRecords, context: ValidationContext) -> list[Issue]:
    issues: list[Issue] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(loaded.records):
        issues.extend(_missing_required("review_pack", record, loaded.path, index))
        for field in ("pack_id", "language", "scope", "reviewer_role", "provenance_id"):
            issue = _issue_empty_string("review_pack", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)

        pack_id = _string(record, "pack_id")
        if pack_id is not None:
            if pack_id in seen_ids:
                issues.append(
                    Issue(
                        "error",
                        "review_pack.pack_id.duplicate",
                        f"Duplicate pack_id `{pack_id}`.",
                        _location(loaded.path, index),
                        "review_pack",
                        pack_id,
                    )
                )
            seen_ids.add(pack_id)

        language = _string(record, "language")
        if language is not None and not _language(language):
            issues.append(
                Issue(
                    "error",
                    "review_pack.language.invalid",
                    f"Unsupported language tag `{language}`.",
                    _location(loaded.path, index),
                    "review_pack",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        for field, min_items in (
            ("hpo_ids", 1),
            ("source_ids", 1),
            ("crosswalk_ids", 0),
            ("conflict_ids", 0),
            ("coverage_ids", 0),
        ):
            issue = _list_issue("review_pack", record, loaded.path, index, field, min_items=min_items)
            if issue is not None:
                issues.append(issue)

        hpo_ids = _list(record, "hpo_ids") or []
        for hpo_id in hpo_ids:
            if isinstance(hpo_id, str) and not HPO_ID_RE.match(hpo_id):
                issues.append(
                    Issue(
                        "error",
                        "review_pack.hpo_ids.invalid_hpo_id",
                        f"`{hpo_id}` is not a valid HPO identifier.",
                        _location(loaded.path, index),
                        "review_pack",
                        _record_id(record, f"record-{index + 1}"),
                    )
                )

        source_ids = _list(record, "source_ids") or []
        for source_id in source_ids:
            if isinstance(source_id, str):
                issue = _unknown_source_issue("review_pack", source_id, record, loaded.path, index, context)
                if issue is not None:
                    issues.append(issue)

        candidate_count = _int(record, "candidate_count")
        if candidate_count is None or candidate_count < 0:
            issues.append(
                Issue(
                    "error",
                    "review_pack.candidate_count.invalid",
                    "`candidate_count` must be a non-negative integer.",
                    _location(loaded.path, index),
                    "review_pack",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        for field in ("candidate_only", "human_review_required"):
            issue = _bool_issue("review_pack", record, loaded.path, index, field)
            if issue is not None:
                issues.append(issue)
        if _bool(record, "candidate_only") is not True:
            issues.append(
                Issue(
                    "error",
                    "review_pack.candidate_only.required",
                    "Review packs must remain candidate-only.",
                    _location(loaded.path, index),
                    "review_pack",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
        if _bool(record, "human_review_required") is not True:
            issues.append(
                Issue(
                    "error",
                    "review_pack.human_review_required.required",
                    "Review packs must require human review.",
                    _location(loaded.path, index),
                    "review_pack",
                    _record_id(record, f"record-{index + 1}"),
                )
            )

        promotion_issue = _enum_issue("review_pack", record, loaded.path, index, "promotion_policy", PROMOTION_POLICIES)
        if promotion_issue is not None:
            issues.append(promotion_issue)

        crosswalk_ids = _list(record, "crosswalk_ids") or []
        conflict_ids = _list(record, "conflict_ids") or []
        coverage_ids = _list(record, "coverage_ids") or []
        if not crosswalk_ids and not conflict_ids and not coverage_ids:
            issues.append(
                Issue(
                    "error",
                    "review_pack.evidence_links.missing",
                    "Review packs must link at least one crosswalk, conflict, or coverage evidence id.",
                    _location(loaded.path, index),
                    "review_pack",
                    _record_id(record, f"record-{index + 1}"),
                )
            )
    return issues


def validate_artifacts(artifact_paths: dict[ArtifactKind, list[Path]]) -> dict[str, Any]:
    issues: list[Issue] = []
    loaded_by_kind: dict[ArtifactKind, list[LoadedRecords]] = {kind: [] for kind in REQUIRED_FIELDS}
    for kind, paths in artifact_paths.items():
        for path in paths:
            loaded, load_issues = load_records(kind, path)
            issues.extend(load_issues)
            if loaded is not None:
                loaded_by_kind[kind].append(loaded)

    registry_source_ids: set[str] = set()
    for loaded in loaded_by_kind["registry"]:
        registry_issues, source_ids = validate_registry(loaded)
        issues.extend(registry_issues)
        registry_source_ids.update(source_ids)

    context = ValidationContext(frozenset(registry_source_ids))
    for loaded in loaded_by_kind["crosswalk"]:
        issues.extend(validate_crosswalk(loaded, context))
    for loaded in loaded_by_kind["conflict"]:
        issues.extend(validate_conflict(loaded, context))
    for loaded in loaded_by_kind["coverage"]:
        issues.extend(validate_coverage(loaded, context))
    for loaded in loaded_by_kind["review_pack"]:
        issues.extend(validate_review_pack(loaded, context))

    return {
        "summary": summarize(loaded_by_kind, issues, registry_source_ids),
        "issues": [asdict(issue) for issue in issues],
        "artifacts": [
            {"kind": loaded.kind, "path": str(loaded.path), "record_count": len(loaded.records)}
            for loaded_group in loaded_by_kind.values()
            for loaded in loaded_group
        ],
    }


def summarize(
    loaded_by_kind: dict[ArtifactKind, list[LoadedRecords]],
    issues: list[Issue],
    registry_source_ids: set[str],
) -> dict[str, Any]:
    issue_counts = Counter(issue.severity for issue in issues)
    artifact_counts = {
        kind: sum(len(loaded.records) for loaded in loaded_group)
        for kind, loaded_group in sorted(loaded_by_kind.items())
    }
    return {
        "artifact_record_counts": artifact_counts,
        "registry_source_count": len(registry_source_ids),
        "issue_counts": dict(sorted(issue_counts.items())),
        "release_ready": issue_counts["error"] == 0,
    }


def render_text(report: dict[str, Any]) -> str:
    summary = cast(dict[str, Any], report["summary"])
    issues = cast(list[dict[str, Any]], report["issues"])
    artifacts = cast(list[dict[str, Any]], report["artifacts"])
    lines = [
        "# Ontology Network Validation Report",
        "",
        f"- Release ready: {str(summary['release_ready']).lower()}",
        f"- Issue counts: {json.dumps(summary['issue_counts'], sort_keys=True)}",
        f"- Artifact record counts: {json.dumps(summary['artifact_record_counts'], sort_keys=True)}",
        f"- Registry source count: {summary['registry_source_count']}",
        "",
        "## Artifacts",
    ]
    if not artifacts:
        lines.append("- None")
    else:
        for artifact in artifacts:
            lines.append(f"- {artifact['kind']}: {artifact['record_count']} record(s) from {artifact['path']}")

    lines.extend(["", "## Issues"])
    if not issues:
        lines.append("- None")
    else:
        for issue in issues:
            record = f" [{issue['record_id']}]" if issue.get("record_id") else ""
            kind = f" {issue['artifact_kind']}" if issue.get("artifact_kind") else ""
            lines.append(
                f"- {str(issue['severity']).upper()} {issue['code']}{kind}{record}: "
                f"{issue['message']} ({issue['path']})"
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


def write_schemas(schema_output: Path) -> None:
    schema_output.mkdir(parents=True, exist_ok=True)
    schemas = schema_definitions()
    expected = {f"{name}.schema.json" for name in schemas}
    for stale_schema in schema_output.glob("*.schema.json"):
        if stale_schema.name not in expected:
            stale_schema.unlink()
    for name, schema in sorted(schemas.items()):
        (schema_output / f"{name}.schema.json").write_text(
            json.dumps(schema, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _append_path(values: list[Path] | None) -> list[Path]:
    return values or []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate ontology-network registry, crosswalk, conflict, coverage, and review-pack artifacts."
    )
    parser.add_argument("--registry", action="append", type=Path, help="Source registry JSON/JSONL/CSV/TSV artifact.")
    parser.add_argument(
        "--crosswalk", action="append", type=Path, help="Identifier crosswalk JSON/JSONL/CSV/TSV artifact."
    )
    parser.add_argument("--conflict", action="append", type=Path, help="Conflict report JSON/JSONL/CSV/TSV artifact.")
    parser.add_argument("--coverage", action="append", type=Path, help="Coverage summary JSON/JSONL/CSV/TSV artifact.")
    parser.add_argument("--review-pack", action="append", type=Path, help="Review-pack JSON/JSONL/CSV/TSV artifact.")
    parser.add_argument("--schema-output", type=Path, help="Optional directory to write JSON Schema-style contracts.")
    parser.add_argument("--json-output", type=Path, help="Optional path for machine-readable JSON validation report.")
    parser.add_argument("--text-output", type=Path, help="Optional path for Markdown/text validation report.")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Exit non-zero when warnings are present.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    artifact_paths: dict[ArtifactKind, list[Path]] = {
        "registry": _append_path(args.registry),
        "crosswalk": _append_path(args.crosswalk),
        "conflict": _append_path(args.conflict),
        "coverage": _append_path(args.coverage),
        "review_pack": _append_path(args.review_pack),
    }
    if args.schema_output is not None:
        write_schemas(args.schema_output)

    report = validate_artifacts(artifact_paths)
    write_report(report, args.json_output, args.text_output)
    print(render_text(report), end="")

    issues = cast(list[dict[str, Any]], report["issues"])
    has_errors = any(issue["severity"] == "error" for issue in issues)
    has_warnings = any(issue["severity"] == "warning" for issue in issues)
    raise SystemExit(1 if has_errors or (args.warnings_as_errors and has_warnings) else 0)


if __name__ == "__main__":
    main()
