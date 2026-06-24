import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, cast

TRACKS_DIR = Path("conductor/tracks")
DEFAULT_OUTPUT_DIR = Path("ontology_network")
GENERATED_DATE = "2026-06-23"
ONTOLOGY_TRACK_SUFFIX = "_integration_20260623"
RESTRICTED_STATUS_MARKERS = (
    "api_key",
    "free_account",
    "license",
    "permission",
    "subscription",
)
PUBLIC_STATUS_MARKERS = (
    "open_ontology",
    "public_or_national_variant",
    "public_download",
    "public_ontology",
)
API_STATUS_MARKERS = (
    "open_api",
    "public_api",
)
LOCAL_ONLY_ACCESS_CLASSES = {"API-only", "investigation-only", "local-only", "restricted"}
RAW_PAYLOAD_LOCAL_ONLY = [
    "raw downloads",
    "licensed payloads",
    "full API responses",
    "credentialed exports",
]
BLOCKED_PATH_PARTS = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".pixi",
    ".ruff_cache",
    "__pycache__",
}

LANGUAGE_CODE_MAP = {
    "Arabic": "ar",
    "Chinese": "zh",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Estonian": "et",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Hungarian": "hu",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Russian": "ru",
    "Slovak": "sk",
    "Spanish": "es",
    "Swedish": "sv",
    "Turkish": "tr",
    "Uzbek": "uz",
}
SECRET_CONTENT_PATTERNS = (
    re.compile(r"api[_-]?key\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"private\s+patient", re.IGNORECASE),
    re.compile(r"licensed\s+payload\s+row", re.IGNORECASE),
)


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def ontology_track_dirs(tracks_dir: Path = TRACKS_DIR) -> list[Path]:
    return sorted(
        path
        for path in tracks_dir.iterdir()
        if path.is_dir() and path.name.endswith(ONTOLOGY_TRACK_SUFFIX) and path.name != "ontology_network_20260623"
    )


def split_languages(raw: str) -> list[str]:
    raw = raw.removesuffix(".")
    raw = raw.replace(", and ", ", ")
    raw = raw.replace(" and ", ", ")
    return [part.strip() for part in raw.split(",") if part.strip()]


def source_profile(spec_text: str) -> dict[str, Any]:
    languages: list[str] = []
    repositories: list[str] = []
    source_note = ""
    usefulness = ""
    in_repositories = False
    in_usefulness = False

    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_repositories = False
            in_usefulness = stripped == "## Usefulness"
            continue
        if stripped.startswith("- Languages:"):
            languages = split_languages(stripped.removeprefix("- Languages:").strip())
        elif stripped == "- GitHub repositories:":
            in_repositories = True
        elif in_repositories and stripped.startswith("- http"):
            repositories.append(stripped.removeprefix("- ").strip())
        elif stripped.startswith("- Source note:"):
            source_note = stripped.removeprefix("- Source note:").strip()
        elif in_usefulness and stripped:
            usefulness = stripped
            in_usefulness = False
    return {
        "languages": languages,
        "github_repositories": repositories,
        "source_note": source_note,
        "usefulness": usefulness,
    }


def normalized_language_names(languages: list[str]) -> list[str]:
    joined = ", ".join(languages)
    if "English only" in joined:
        return ["English"]
    if "including " in joined:
        joined = joined.split("including ", 1)[1]
    joined = re.sub(r"^\d+\s+languages\s*", "", joined)
    joined = joined.replace("plus many national localized variants", "")
    joined = joined.replace("plus over 40 localized national language variants", "")
    joined = joined.replace(", and ", ", ").replace(" and ", ", ")
    return [
        part.strip().removesuffix(".")
        for part in joined.split(",")
        if part.strip() and not part.strip().startswith("Multilingual via")
    ]


def language_codes(languages: list[str]) -> list[str]:
    codes = sorted(
        {LANGUAGE_CODE_MAP[name] for name in normalized_language_names(languages) if name in LANGUAGE_CODE_MAP}
    )
    return codes or ["und"]


def declared_language_count(languages: list[str]) -> int:
    joined = ", ".join(languages)
    match = re.search(r"(\d+)\s+languages", joined)
    if match:
        return int(match.group(1))
    if "English only" in joined:
        return 1
    return len(language_codes(languages))


def language_normalization_status(languages: list[str]) -> str:
    joined = ", ".join(languages)
    if "English only" in joined:
        return "english_only"
    if re.search(r"\d+\s+languages", joined):
        return "partial_declared_multilingual_list"
    if "localized" in joined or "Multilingual" in joined:
        return "partial_multilingual_declaration"
    return "normalized_listed_languages"


def source_id_from_track(track_id: str) -> str:
    source = track_id.removesuffix("_integration_20260623")
    if source == "umls_metathesaurus":
        return "umls"
    return source


def github_repository_roles(repositories: list[str], source_note: str) -> list[dict[str, Any]]:
    note = source_note.lower()
    roles = []
    for repository in repositories:
        role = "source_repository"
        authoritative = True
        if "implementation support" in note or "tooling" in note or "samples" in note:
            role = "tooling_reference"
            authoritative = False
        elif "organization exists" in note:
            role = "organization_reference"
            authoritative = False
        roles.append({"url": repository, "role": role, "authoritative_for_release_payload": authoritative})
    return roles


def credential_required(source_access_status: str) -> bool:
    return any(
        marker in source_access_status
        for marker in ("api_key", "free_account", "license", "permission", "subscription", "affiliate")
    )


def pr_safe(source_class: str) -> bool:
    return source_class in {"open", "API-only", "restricted", "investigation-only", "documentation-only"}


def release_safe(source_class: str) -> bool:
    return source_class == "open"


def redistribution_status(source_class: str, source_access_status: str) -> str:
    if source_class == "open":
        return "terms_review_required_before_payload_redistribution"
    if source_class == "API-only" or "api" in source_access_status:
        return "api_terms_required_no_full_response_redistribution"
    if source_class == "investigation-only":
        return "unknown_until_authority_verified"
    return "restricted_no_payload_redistribution"


def license_status(source_access_status: str, restricted_sources: list[Any]) -> str:
    if source_access_status == "source_authority_and_access_unknown":
        return "unknown_authority_and_license"
    if "subscription" in source_access_status:
        return "subscription_license_required"
    if "affiliate" in source_access_status:
        return "affiliate_or_jurisdiction_license_required"
    if "api_key" in source_access_status:
        return "credentialed_api_or_license_required"
    if "free_account" in source_access_status:
        return "free_account_license_review_required"
    if "permission" in source_access_status:
        return "permission_or_data_use_terms_required"
    if "license" in source_access_status or restricted_sources:
        return "license_required"
    if "terms_review" in source_access_status or source_access_status.endswith("_review_required"):
        return "terms_review_required"
    return "not_recorded"


def access_mode(source_access_status: str) -> str:
    if source_access_status == "source_authority_and_access_unknown":
        return "source_authority_investigation"
    if "api_key" in source_access_status:
        return "credentialed_api_or_download"
    if "permission_or_api" in source_access_status:
        return "permissioned_api_or_terms_gated_access"
    if any(marker in source_access_status for marker in API_STATUS_MARKERS):
        return "public_api_terms_review_required"
    if "free_account" in source_access_status:
        return "account_gated_download"
    if "subscription" in source_access_status or "affiliate" in source_access_status:
        return "licensed_release_download"
    if source_access_status == "license_required":
        return "licensed_download_or_api"
    if "public_or_national_variant" in source_access_status:
        return "public_or_national_variant_download"
    if "public_download" in source_access_status:
        return "public_download_terms_review_required"
    if "public_ontology" in source_access_status:
        return "public_ontology_terms_review_required"
    if "open_ontology" in source_access_status:
        return "open_ontology_download_review_required"
    return "review_required"


def endpoint_status(profile: dict[str, Any]) -> str:
    source_note = str(profile.get("source_note", ""))
    note = source_note.lower()
    repositories = cast(list[str], profile.get("github_repositories", []))
    roles = github_repository_roles(repositories, source_note)
    if "no official public github repository confirmed" in note:
        return "non_github_authority_required"
    if repositories and not any(role["authoritative_for_release_payload"] for role in roles):
        return "authority_described_github_not_authoritative"
    if repositories:
        return "repository_recorded_authority_review_required"
    if source_note:
        return "authority_described_without_url"
    return "not_recorded"


def local_only_requirements(metadata: dict[str, Any], source_class: str) -> list[str]:
    policy = cast(dict[str, Any], metadata.get("restricted_payload_policy", {}))
    requirements = list(cast(list[str], policy.get("local_only_artifacts", RAW_PAYLOAD_LOCAL_ONLY)))
    if source_class in LOCAL_ONLY_ACCESS_CLASSES:
        requirements.append(
            "source-specific extraction outputs remain local-only until access and redistribution terms pass review"
        )
    return sorted(dict.fromkeys(requirements))


def source_payload_commit_policy(source_class: str) -> str:
    if source_class == "open":
        return (
            "do_not_commit_raw_source_payloads; commit only registry, schemas, provenance, "
            "bounded validation summaries, and derived reports after terms review"
        )
    if source_class == "API-only":
        return (
            "do_not_commit_full_api_responses; commit only schemas, request manifests, "
            "validation summaries, and redacted derived reports"
        )
    if source_class == "investigation-only":
        return "do_not_plan_payload_access until source authority, access path, and license are verified"
    return (
        "do_not_commit_raw_licensed_or_credentialed_payloads; governance metadata only "
        "until explicit redistribution permission exists"
    )


def ontology_name(metadata: dict[str, Any], spec_text: str) -> str:
    description = str(metadata.get("description", ""))
    match = re.match(r"Integrate (.+?) into ", description)
    if match:
        return match.group(1)
    first_line = spec_text.splitlines()[0] if spec_text.splitlines() else metadata["track_id"]
    return first_line.removeprefix("# Specification - Integrate ").removesuffix(
        " into terminology and translation support"
    )


def access_class(source_access_status: str) -> str:
    if source_access_status == "source_authority_and_access_unknown":
        return "investigation-only"
    if "local_only" in source_access_status:
        return "local-only"
    if any(marker in source_access_status for marker in RESTRICTED_STATUS_MARKERS):
        return "restricted"
    if any(marker in source_access_status for marker in API_STATUS_MARKERS):
        return "API-only"
    if any(marker in source_access_status for marker in PUBLIC_STATUS_MARKERS):
        return "open"
    if source_access_status in {"documentation_only", "not_applicable"}:
        return "documentation-only"
    return "investigation-only"


def registry_record(track_dir: Path) -> dict[str, Any]:
    metadata = load_json(track_dir / "metadata.json")
    spec_text = (track_dir / "spec.md").read_text(encoding="utf-8")
    profile = source_profile(spec_text)
    source_status = str(metadata.get("source_access_status", "unknown"))
    restricted_sources = cast(list[Any], metadata.get("restricted_sources", []))
    source_class = access_class(source_status)
    endpoint_state = endpoint_status(profile)
    return {
        "source_id": source_id_from_track(str(metadata["track_id"])),
        "track_id": metadata["track_id"],
        "ontology_name": ontology_name(metadata, spec_text),
        "description": metadata.get("description"),
        "priority": metadata.get("priority"),
        "track_status": metadata.get("status"),
        "metadata_created_at": metadata.get("created_at"),
        "metadata_updated_at": metadata.get("updated_at"),
        "source_version": None,
        "version_status": "not_pinned_in_track_metadata",
        "source_access_status": source_status,
        "access_class": source_class,
        "access_mode": access_mode(source_status),
        "license_status": license_status(source_status, restricted_sources),
        "license_review_required": "review_required" in source_status
        or source_class in LOCAL_ONLY_ACCESS_CLASSES
        or bool(restricted_sources),
        "languages": profile["languages"],
        "language_codes": language_codes(cast(list[str], profile["languages"])),
        "declared_language_count": declared_language_count(cast(list[str], profile["languages"])),
        "language_normalization_status": language_normalization_status(cast(list[str], profile["languages"])),
        "language_count": len(language_codes(cast(list[str], profile["languages"]))),
        "github_repositories": profile["github_repositories"],
        "github_repository_count": len(profile["github_repositories"]),
        "github_repository_roles": github_repository_roles(
            cast(list[str], profile["github_repositories"]), str(profile["source_note"])
        ),
        "authoritative_endpoint": endpoint_state,
        "authoritative_endpoint_status": endpoint_state,
        "authoritative_endpoint_note": profile["source_note"],
        "source_note": profile["source_note"],
        "usefulness": profile["usefulness"],
        "restricted_sources": restricted_sources,
        "credential_required": credential_required(source_status),
        "payload_commit_allowed": False,
        "pr_safe": pr_safe(source_class),
        "release_safe": release_safe(source_class),
        "redistribution_status": redistribution_status(source_class, source_status),
        "source_payloads_can_be_committed": False,
        "source_payload_commit_policy": source_payload_commit_policy(source_class),
        "local_only_requirements": local_only_requirements(metadata, source_class),
        "commit_safe_artifacts": [
            "registry records",
            "source access matrix",
            "artifact schemas",
            "provenance manifests without payload text",
            "validation summaries without payload reconstruction",
            "review pack structure without restricted labels",
        ],
        "known_blockers": metadata.get("known_blockers", []),
        "expected_blockers": metadata.get("expected_blockers", []),
        "fallback_path": metadata.get("fallback_path"),
        "artifact_contract": metadata.get("artifact_contract"),
        "candidate_only": metadata.get("evidence_score_policy", {}).get("candidate_only", True),
        "human_review_required": True,
        "provenance": {
            "method": "conductor_track_metadata_parse",
            "generated_date": GENERATED_DATE,
            "metadata_path": str(track_dir / "metadata.json"),
            "spec_path": str(track_dir / "spec.md"),
        },
        "source_metadata_paths": {
            "metadata": str(track_dir / "metadata.json"),
            "source_profile_spec": str(track_dir / "spec.md"),
        },
    }


def build_registry(tracks_dir: Path = TRACKS_DIR) -> dict[str, Any]:
    records = [registry_record(track_dir) for track_dir in ontology_track_dirs(tracks_dir)]
    return {
        "generated_date": GENERATED_DATE,
        "source": "conductor track metadata and source profile specifications",
        "payload_policy": "No external ontology payloads are read or committed by this registry build.",
        "record_count": len(records),
        "records": records,
    }


def property_schema(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"type": value}


def schema(name: str, required: list[str], properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://example.org/hpo-translations/ontology-network/{name}.schema.json",
        "title": name,
        "type": "object",
        "required": required,
        "properties": {key: property_schema(value) for key, value in properties.items()},
        "additionalProperties": False,
    }


def _merge_json_type(existing: Any, new: Any) -> Any:
    values: list[str] = []
    for value in (existing, new):
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        elif isinstance(value, str):
            values.append(value)
    unique = sorted(dict.fromkeys(values))
    return unique[0] if len(unique) == 1 else unique


def _schema_for_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, list):
        item_schema: dict[str, Any] = {}
        for item in value:
            item_type = _schema_for_value(item).get("type", "string")
            if not item_schema:
                item_schema = {"type": item_type}
            else:
                item_schema["type"] = _merge_json_type(item_schema.get("type"), item_type)
        return {"type": "array", "items": item_schema or {}}
    if isinstance(value, dict):
        return {"type": "object", "additionalProperties": True}
    return {"type": "string"}


def _merge_property_schema(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    merged["type"] = _merge_json_type(existing.get("type"), new.get("type"))
    if existing.get("type") == "array" or new.get("type") == "array":
        merged.setdefault("items", new.get("items", existing.get("items", {})))
    if existing.get("type") == "object" or new.get("type") == "object":
        merged.setdefault("additionalProperties", True)
    return merged


def _schema_from_records(name: str, records: list[dict[str, Any]], required: set[str]) -> dict[str, Any]:
    properties: dict[str, dict[str, Any]] = {}
    for record in records:
        for key, value in record.items():
            value_schema = _schema_for_value(value)
            properties[key] = (
                _merge_property_schema(properties[key], value_schema) if key in properties else value_schema
            )
    return schema(name, sorted(required & set(properties)), properties)


SCHEMA_REQUIRED_FIELDS: dict[str, set[str]] = {
    "source_registry_record": {
        "source_id",
        "track_id",
        "ontology_name",
        "source_version",
        "version_status",
        "source_access_status",
        "access_class",
        "license_status",
        "language_codes",
        "declared_language_count",
        "github_repository_roles",
        "authoritative_endpoint_status",
        "payload_commit_allowed",
        "pr_safe",
        "release_safe",
        "redistribution_status",
        "human_review_required",
    },
    "source_access_record": {
        "source_id",
        "track_id",
        "ontology_name",
        "access_class",
        "license_status",
        "language_codes",
        "credential_required",
        "payload_commit_allowed",
        "release_safe",
        "redistribution_status",
    },
    "crosswalk_edge": {
        "edge_id",
        "hpo_id",
        "external_source_id",
        "external_id",
        "mapping_predicate",
        "mapping_source",
        "mapping_basis",
        "confidence",
        "review_status",
        "candidate_only",
        "human_review_required",
        "provenance_id",
    },
    "language_comparison_row": {"language", "source_ids", "candidate_only", "human_review_required"},
    "conflict_report_row": {
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
    "coverage_summary_row": {
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
    "review_pack_record": {
        "pack_id",
        "language",
        "scope",
        "hpo_ids",
        "source_ids",
        "crosswalk_ids",
        "conflict_ids",
        "coverage_ids",
        "candidate_only",
        "human_review_required",
        "promotion_policy",
        "provenance_id",
    },
    "release_readiness_manifest": {
        "generated_date",
        "source_count",
        "restricted_source_count",
        "release_ready",
        "governance_artifacts_release_ready",
        "source_payload_release_ready",
    },
    "source_class_probe": {
        "probe_id",
        "access_class",
        "source_id",
        "registry_record_present",
        "payload_commit_allowed",
        "human_review_required",
        "validation_status",
    },
    "p3_source_governance_record": {
        "source_id",
        "track_id",
        "ontology_name",
        "priority",
        "access_class",
        "source_access_status",
        "authority_status",
        "source_authority_confirmed",
        "terms_review_required",
        "payload_commit_allowed",
        "bounded_sample_allowed",
        "identifier_network_allowed",
        "non_translation_outputs_allowed",
        "go_no_go",
        "implementation_scope",
        "next_allowed_action",
        "blocked_downstream_outputs",
        "commit_safe_artifacts",
        "local_only_requirements",
        "known_blockers",
        "human_review_required",
        "candidate_only",
        "provenance_id",
    },
    "validation_report": {"generated_date", "artifact", "validation_result", "issues"},
}


def schema_definitions(registry: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    if registry is None:
        registry = build_registry()
    outputs = network_outputs(registry)
    schemas = {
        "source_registry_record": _schema_from_records(
            "source_registry_record",
            cast(list[dict[str, Any]], registry["records"]),
            SCHEMA_REQUIRED_FIELDS["source_registry_record"],
        ),
        "source_access_record": _schema_from_records(
            "source_access_record", source_access_records(registry), SCHEMA_REQUIRED_FIELDS["source_access_record"]
        ),
        "crosswalk_edge": _schema_from_records(
            "crosswalk_edge",
            cast(list[dict[str, Any]], outputs[Path("crosswalk_graph.json")]["edges"]),
            SCHEMA_REQUIRED_FIELDS["crosswalk_edge"],
        ),
        "language_comparison_row": _schema_from_records(
            "language_comparison_row",
            cast(list[dict[str, Any]], outputs[Path("language_comparison_packs.json")]["records"]),
            SCHEMA_REQUIRED_FIELDS["language_comparison_row"],
        ),
        "conflict_report_row": _schema_from_records(
            "conflict_report_row",
            cast(list[dict[str, Any]], outputs[Path("conflict_heatmap.json")]["records"]),
            SCHEMA_REQUIRED_FIELDS["conflict_report_row"],
        ),
        "coverage_summary_row": _schema_from_records(
            "coverage_summary_row",
            cast(list[dict[str, Any]], outputs[Path("coverage_summary.json")]["records"]),
            SCHEMA_REQUIRED_FIELDS["coverage_summary_row"],
        ),
        "semantic_drift_record": _schema_from_records(
            "semantic_drift_record",
            cast(list[dict[str, Any]], outputs[Path("semantic_drift_report.json")]["records"]),
            {"source_id", "source_version", "hpo_release", "drift_status"},
        ),
        "provenance_graph_node": _schema_from_records(
            "provenance_graph_node",
            cast(list[dict[str, Any]], outputs[Path("provenance_graph.json")]["nodes"]),
            {"id", "type", "track_id"},
        ),
        "provenance_graph_edge": _schema_from_records(
            "provenance_graph_edge",
            cast(list[dict[str, Any]], outputs[Path("provenance_graph.json")]["edges"]),
            {"from", "to", "predicate"},
        ),
        "review_workload_record": _schema_from_records(
            "review_workload_record",
            cast(list[dict[str, Any]], outputs[Path("review_workload_report.json")]["records"]),
            {"language", "source_count", "candidate_count", "conflict_count", "coverage_gap_count"},
        ),
        "review_pack_record": _schema_from_records(
            "review_pack_record",
            cast(list[dict[str, Any]], outputs[Path("language_review_packs.json")]["records"]),
            SCHEMA_REQUIRED_FIELDS["review_pack_record"],
        ),
        "license_access_record": _schema_from_records(
            "license_access_record",
            cast(list[dict[str, Any]], outputs[Path("license_access_report.json")]["records"]),
            {
                "source_id",
                "access_class",
                "license_status",
                "payload_commit_allowed",
                "release_safe",
                "redistribution_status",
            },
        ),
        "source_class_probe": _schema_from_records(
            "source_class_probe",
            cast(list[dict[str, Any]], outputs[Path("source_class_probes.json")]["records"]),
            SCHEMA_REQUIRED_FIELDS["source_class_probe"],
        ),
        "p3_source_governance_record": _schema_from_records(
            "p3_source_governance_record",
            cast(list[dict[str, Any]], outputs[Path("p3_source_governance.json")]["records"]),
            SCHEMA_REQUIRED_FIELDS["p3_source_governance_record"],
        ),
        "release_readiness_manifest": _schema_from_records(
            "release_readiness_manifest",
            [release_manifest(registry)],
            SCHEMA_REQUIRED_FIELDS["release_readiness_manifest"],
        ),
        "payload_policy_record": _schema_from_records(
            "payload_policy_record",
            [payload_policy_document()],
            {"policy_scope", "commit_policy", "local_only_artifacts", "blocked_patterns", "required_evidence"},
        ),
        "validation_report": _schema_from_records(
            "validation_report",
            [outputs[Path("validation_report.json")]],
            SCHEMA_REQUIRED_FIELDS["validation_report"],
        ),
    }
    schemas["artifact_schema_index_record"] = schema(
        "artifact_schema_index_record",
        ["artifact", "schema_path", "required_fields", "artifact_status", "safety_class", "owner"],
        {
            "artifact": "string",
            "schema_path": "string",
            "required_fields": {"type": "array", "items": {"type": "string"}},
            "artifact_status": "string",
            "safety_class": "string",
            "owner": "string",
            "local_only": "boolean",
            "downstream_consumers": {"type": "array", "items": {"type": "string"}},
        },
    )
    return schemas


def source_access_records(registry: dict[str, Any]) -> list[dict[str, Any]]:
    records = cast(list[dict[str, Any]], registry["records"])
    return [
        {
            "source_id": record["source_id"],
            "track_id": record["track_id"],
            "ontology_name": record["ontology_name"],
            "access_class": record["access_class"],
            "access_mode": record["access_mode"],
            "license_status": record["license_status"],
            "source_access_status": record["source_access_status"],
            "source_version": record["source_version"],
            "version_status": record["version_status"],
            "languages": record["languages"],
            "language_codes": record["language_codes"],
            "declared_language_count": record["declared_language_count"],
            "github_repositories": record["github_repositories"],
            "github_repository_roles": record["github_repository_roles"],
            "authoritative_endpoint": record["authoritative_endpoint"],
            "authoritative_endpoint_status": record["authoritative_endpoint_status"],
            "local_only_requirements": record["local_only_requirements"],
            "credential_required": record["credential_required"],
            "payload_commit_allowed": record["payload_commit_allowed"],
            "pr_safe": record["pr_safe"],
            "release_safe": record["release_safe"],
            "redistribution_status": record["redistribution_status"],
            "source_payloads_can_be_committed": record["source_payloads_can_be_committed"],
            "source_payload_commit_policy": record["source_payload_commit_policy"],
            "restricted_sources": record["restricted_sources"],
            "known_blocker_count": len(cast(list[Any], record.get("known_blockers", []))),
            "human_review_required": record["human_review_required"],
        }
        for record in records
    ]


def source_access_dataset(registry: dict[str, Any]) -> dict[str, Any]:
    records = source_access_records(registry)
    return {
        "generated_date": GENERATED_DATE,
        "source": "conductor track metadata plus source profile fields; no external ontology payloads are read",
        "record_count": len(records),
        "records": records,
    }


def tsv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def source_access_matrix(registry: dict[str, Any]) -> str:
    columns = [
        "source_id",
        "track_id",
        "ontology_name",
        "access_class",
        "access_mode",
        "license_status",
        "source_access_status",
        "source_version",
        "version_status",
        "languages",
        "language_codes",
        "declared_language_count",
        "github_repositories",
        "github_repository_roles",
        "authoritative_endpoint",
        "authoritative_endpoint_status",
        "local_only_requirements",
        "credential_required",
        "payload_commit_allowed",
        "pr_safe",
        "release_safe",
        "redistribution_status",
        "source_payloads_can_be_committed",
        "restricted_sources",
        "known_blocker_count",
        "human_review_required",
    ]
    rows = ["\t".join(columns)]
    for record in source_access_records(registry):
        rows.append("\t".join(tsv_value(record[column]) for column in columns))
    return "\n".join(rows) + "\n"


def artifact_schema_index(schemas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    local_only = {"local_only_manifest"}
    generated_only = {
        "conflict_report_row",
        "coverage_summary_row",
        "crosswalk_edge",
        "language_comparison_row",
        "review_pack_record",
        "validation_report",
    }
    return {
        "generated_date": GENERATED_DATE,
        "source": "ontology network metadata contract; schemas describe records, not source payloads",
        "schema_count": len(schemas),
        "schemas": [
            {
                "artifact": name,
                "schema_path": f"schemas/{name}.schema.json",
                "required_fields": schema_data["required"],
                "artifact_status": "conditional_local_only"
                if name in local_only
                else "generated"
                if name in generated_only
                else "committed_contract",
                "safety_class": "local-only-reference"
                if name in local_only
                else "payload-free"
                if name in generated_only
                else "release-safe-contract",
                "local_only": name in local_only,
                "owner": "ontology-network maintainer",
                "downstream_consumers": [
                    "ontology source integration tracks",
                    "translation candidate review packs",
                    "release readiness checks",
                ],
            }
            for name, schema_data in sorted(schemas.items())
        ],
    }


def payload_policy_document() -> dict[str, Any]:
    metadata = load_json(TRACKS_DIR / "ontology_network_20260623" / "metadata.json")
    policy = cast(dict[str, Any], metadata.get("restricted_payload_policy", {}))
    return {
        "generated_date": GENERATED_DATE,
        "policy_scope": "ontology_network",
        "source": "conductor/tracks/ontology_network_20260623/metadata.json",
        "commit_policy": policy.get("commit_policy"),
        "local_only_artifacts": policy.get("local_only_artifacts", []),
        "blocked_patterns": policy.get("blocked_patterns", []),
        "required_evidence": policy.get("required_evidence", []),
        "no_external_payloads_read": True,
    }


def release_manifest(registry: dict[str, Any]) -> dict[str, Any]:
    records = cast(list[dict[str, Any]], registry["records"])
    access_counts = Counter(str(record["access_class"]) for record in records)
    restricted = access_counts["restricted"]
    blockers = sum(len(cast(list[Any], record.get("known_blockers", []))) for record in records)
    source_payload_ready = restricted == 0 and blockers == 0
    return {
        "generated_date": GENERATED_DATE,
        "source_count": len(records),
        "access_class_counts": dict(sorted(access_counts.items())),
        "restricted_source_count": restricted,
        "known_blocker_count": blockers,
        "release_ready": True,
        "governance_artifacts_release_ready": True,
        "source_payload_release_ready": source_payload_ready,
        "source_payload_blocker_count": blockers,
        "release_policy": (
            "Payload-free registry, schemas, validation summaries, provenance, and review scaffolds are release-safe; "
            "raw, licensed, credentialed, and full-release source payloads are excluded."
        ),
        "human_review_required": True,
    }


def source_class_probes(registry: dict[str, Any]) -> list[dict[str, Any]]:
    records = cast(list[dict[str, Any]], registry["records"])
    probes = []
    for access_class_name in sorted({str(record["access_class"]) for record in records}):
        record = next(row for row in records if row["access_class"] == access_class_name)
        probes.append(
            {
                "probe_id": f"probe-{access_class_name.lower().replace(' ', '-').replace('_', '-')}",
                "access_class": access_class_name,
                "source_id": record["source_id"],
                "ontology_name": record["ontology_name"],
                "registry_record_present": True,
                "credential_required": record["credential_required"],
                "payload_commit_allowed": record["payload_commit_allowed"],
                "pr_safe": record["pr_safe"],
                "release_safe": record["release_safe"],
                "local_only_required": bool(record["local_only_requirements"]),
                "human_review_required": True,
                "validation_status": "metadata_probe_passed_payload_excluded",
                "provenance_id": f"prov-source-class-{access_class_name}",
            }
        )
    return probes


def p3_source_governance(registry: dict[str, Any]) -> list[dict[str, Any]]:
    records = [record for record in cast(list[dict[str, Any]], registry["records"]) if record.get("priority") == "P3"]
    governance: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda row: str(row["source_id"])):
        source_id = str(record["source_id"])
        authority_status = str(record["authoritative_endpoint_status"])
        access_class_name = str(record["access_class"])
        source_access_status = str(record["source_access_status"])
        source_authority_confirmed = False
        terms_review_required = source_id == "fma" or "review_required" in source_access_status
        if source_access_status == "source_authority_and_access_unknown":
            authority_status = "unknown_authority_and_access"
        if source_id == "lddb":
            go_no_go = "no_go_authority_unknown"
            next_allowed_action = (
                "identify authoritative LDDB source, maintenance status, access path, and redistribution terms"
            )
            implementation_scope = "documentation_only_investigation"
        else:
            go_no_go = "governance_only_terms_review_required"
            next_allowed_action = "complete public ontology terms review before any source payload or label extraction"
            implementation_scope = "anatomy_identifier_governance_only"
        governance.append(
            {
                "source_id": source_id,
                "track_id": record["track_id"],
                "ontology_name": record["ontology_name"],
                "priority": record["priority"],
                "access_class": access_class_name,
                "source_access_status": source_access_status,
                "authority_status": authority_status,
                "source_authority_confirmed": source_authority_confirmed,
                "terms_review_required": terms_review_required,
                "payload_commit_allowed": False,
                "bounded_sample_allowed": False,
                "identifier_network_allowed": False,
                "non_translation_outputs_allowed": False,
                "go_no_go": go_no_go,
                "implementation_scope": implementation_scope,
                "next_allowed_action": next_allowed_action,
                "blocked_downstream_outputs": [
                    "ontology_network_20260623:phase_3_identifier_network",
                    "ontology_network_20260623:phase_4_non_translation_outputs",
                ],
                "commit_safe_artifacts": record["commit_safe_artifacts"],
                "local_only_requirements": record["local_only_requirements"],
                "known_blockers": record["known_blockers"],
                "human_review_required": True,
                "candidate_only": True,
                "provenance_id": f"prov-p3-governance-{source_id}",
            }
        )
    return governance


def fail_fast_samples(registry: dict[str, Any]) -> dict[str, Any]:
    records = cast(list[dict[str, Any]], registry["records"])
    open_record = next(record for record in records if record["access_class"] == "open")
    restricted_record = next(record for record in records if record["access_class"] == "restricted")
    return {
        "generated_date": GENERATED_DATE,
        "open_source_registry_record": open_record,
        "restricted_source_governance_record": restricted_record,
        "crosswalk_edge": {
            "edge_id": "probe-open-related-0001",
            "hpo_id": "HP:0000001",
            "external_source_id": open_record["source_id"],
            "external_id": f"{str(open_record['source_id']).upper()}:SCHEMA-PROBE",
            "mapping_predicate": "relatedMatch",
            "mapping_source": "ontology_network_fail_fast_probe",
            "mapping_basis": "source_xref",
            "confidence": 0.0,
            "review_status": "needs_review",
            "candidate_only": True,
            "human_review_required": True,
            "provenance_id": "prov-crosswalk-probe-2026-06-23",
            "caveat": "Schema-only fail-fast probe; not a biological assertion.",
        },
        "conflict_report_row": {
            "hpo_id": "HP:0000001",
            "conflict_type": "schema_probe",
            "sources": [open_record["source_id"], restricted_record["source_id"]],
            "severity": "info",
            "review_required": True,
        },
        "review_pack_record": {
            "language": "en",
            "hpo_id": "HP:0000001",
            "candidate_only": True,
            "human_review_required": True,
            "evidence": ["schema-only probe"],
        },
    }


def language_source_map(registry: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for record in cast(list[dict[str, Any]], registry["records"]):
        for code in cast(list[str], record["language_codes"]):
            mapping.setdefault(code, []).append(str(record["source_id"]))
    return {key: sorted(value) for key, value in sorted(mapping.items())}


def network_outputs(registry: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    records = cast(list[dict[str, Any]], registry["records"])
    by_lang = language_source_map(registry)
    open_record = next(record for record in records if record["access_class"] == "open")
    restricted_record = next(record for record in records if record["access_class"] == "restricted")
    edge = {
        "edge_id": "probe-open-related-0001",
        "hpo_id": "HP:0000001",
        "external_source_id": open_record["source_id"],
        "external_id": f"{str(open_record['source_id']).upper()}:SCHEMA-PROBE",
        "mapping_predicate": "relatedMatch",
        "mapping_source": "ontology_network_fail_fast_probe",
        "mapping_basis": "source_xref",
        "confidence": 0.0,
        "review_status": "needs_review",
        "candidate_only": True,
        "human_review_required": True,
        "provenance_id": "prov-crosswalk-probe-2026-06-23",
    }
    comparisons: list[dict[str, Any]] = [
        {
            "language": lang,
            "source_ids": sources,
            "candidate_count": 0,
            "candidate_only": True,
            "human_review_required": True,
            "comparison_status": "not_computed_source_payloads_excluded",
        }
        for lang, sources in by_lang.items()
    ]
    conflict_rows: list[dict[str, Any]] = []
    for row in comparisons:
        row_sources = cast(list[str], row["source_ids"])
        conflict_sources = row_sources[:2]
        if len(conflict_sources) < 2:
            fallback_source = str(restricted_record["source_id"])
            if conflict_sources and conflict_sources[0] == fallback_source:
                fallback_source = str(open_record["source_id"])
            conflict_sources.append(fallback_source)
        conflict_rows.append(
            {
                "conflict_id": f"conflict-{row['language']}-metadata",
                "conflict_type": "source_disagreement",
                "severity": "info",
                "hpo_id": "HP:0000001",
                "source_ids": conflict_sources,
                "evidence_ids": [edge["edge_id"]],
                "resolution_status": "needs_review",
                "reviewer_action": "confirm source evidence before candidate promotion",
                "provenance_id": f"prov-conflict-{row['language']}",
                "language": row["language"],
                "count": 0,
                "review_required": True,
            }
        )
    coverage: list[dict[str, Any]] = [
        {
            "coverage_id": f"coverage-{record['source_id']}-{lang}",
            "source_id": record["source_id"],
            "hpo_branch_id": "HP:0000118",
            "language": lang,
            "predicate": "metadata_declared_language_support",
            "covered_hpo_terms": 0,
            "total_hpo_terms": 0,
            "coverage_ratio": 0.0,
            "review_status": "needs_review",
            "provenance_id": f"prov-coverage-{record['source_id']}-{lang}",
        }
        for record in records
        for lang in cast(list[str], record["language_codes"])
    ]
    review_packs: list[dict[str, Any]] = [
        {
            "pack_id": f"pack-{row['language']}-metadata",
            "language": row["language"],
            "scope": "payload-free ontology-network metadata probe",
            "source_ids": row["source_ids"],
            "hpo_ids": ["HP:0000001"],
            "crosswalk_ids": [edge["edge_id"]],
            "conflict_ids": [f"conflict-{row['language']}-metadata"],
            "coverage_ids": [
                f"coverage-{source_id}-{row['language']}" for source_id in cast(list[str], row["source_ids"])
            ],
            "candidate_count": 0,
            "candidate_only": True,
            "human_review_required": True,
            "promotion_policy": "manual_review_only",
            "reviewer_role": "language reviewer",
            "provenance_id": f"prov-review-pack-{row['language']}",
        }
        for row in comparisons
    ]
    outputs: dict[Path, dict[str, Any]] = {
        Path("crosswalk_graph.json"): {
            "generated_date": GENERATED_DATE,
            "edge_count": 1,
            "candidate_only": True,
            "human_review_required": True,
            "edges": [edge],
        },
        Path("language_comparison_packs.json"): {
            "generated_date": GENERATED_DATE,
            "record_count": len(comparisons),
            "records": comparisons,
        },
        Path("conflict_heatmap.json"): {
            "generated_date": GENERATED_DATE,
            "record_count": len(conflict_rows),
            "records": conflict_rows,
        },
        Path("coverage_summary.json"): {
            "generated_date": GENERATED_DATE,
            "record_count": len(coverage),
            "records": coverage,
        },
        Path("semantic_drift_report.json"): {
            "generated_date": GENERATED_DATE,
            "records": [
                {
                    "source_id": r["source_id"],
                    "source_version": r["source_version"] or "not_pinned_in_track_metadata",
                    "hpo_release": "not_pinned_in_track_metadata",
                    "semantic_drift_score": None,
                    "drift_status": "not_computed_source_payloads_excluded",
                }
                for r in records
            ],
        },
        Path("provenance_graph.json"): {
            "generated_date": GENERATED_DATE,
            "nodes": [{"id": r["source_id"], "type": "ontology_source", "track_id": r["track_id"]} for r in records],
            "edges": [
                {"from": r["source_id"], "to": "source_registry", "predicate": "contributes_metadata_to"}
                for r in records
            ],
        },
        Path("review_workload_report.json"): {
            "generated_date": GENERATED_DATE,
            "records": [
                {
                    "language": lang,
                    "source_count": len(sources),
                    "candidate_count": 0,
                    "conflict_count": 0,
                    "coverage_gap_count": 0,
                    "reviewer_role": "language reviewer",
                }
                for lang, sources in by_lang.items()
            ],
        },
        Path("language_review_packs.json"): {
            "generated_date": GENERATED_DATE,
            "record_count": len(review_packs),
            "records": review_packs,
        },
        Path("license_access_report.json"): {
            "generated_date": GENERATED_DATE,
            "records": [
                {
                    "source_id": r["source_id"],
                    "access_class": r["access_class"],
                    "license_status": r["license_status"],
                    "credential_required": r["credential_required"],
                    "payload_commit_allowed": r["payload_commit_allowed"],
                    "pr_safe": r["pr_safe"],
                    "release_safe": r["release_safe"],
                    "redistribution_status": r["redistribution_status"],
                }
                for r in records
            ],
        },
        Path("source_class_probes.json"): {
            "generated_date": GENERATED_DATE,
            "record_count": len(source_class_probes(registry)),
            "records": source_class_probes(registry),
        },
        Path("p3_source_governance.json"): {
            "generated_date": GENERATED_DATE,
            "scope": "P3 investigation-only or uncertain-source ontology tracks",
            "record_count": len(p3_source_governance(registry)),
            "payload_policy": (
                "metadata and governance only; no P3 source payloads, labels, or full releases are read or committed"
            ),
            "records": p3_source_governance(registry),
        },
        Path("reproducibility_capsule.json"): {
            "generated_date": GENERATED_DATE,
            "commands": [
                "pixi run build-ontology-network",
                "pixi run validate-ontology-network",
                "pixi run validate-ontology-network-artifacts",
                "pixi run test-conductor-validation",
                "pixi run lint",
            ],
            "permitted_checksums_only": True,
            "source_versions": {
                str(r["source_id"]): str(r["source_version"] or "not_pinned_in_track_metadata") for r in records
            },
        },
    }
    outputs[Path("validation_report.json")] = {
        "generated_date": GENERATED_DATE,
        "artifact": "ontology_network",
        "validation_result": "pending_standalone_validation",
        "issues": ["standalone validation is executed by pixi run validate-ontology-network-artifacts"],
    }
    return outputs


def write_validation_fixtures(output_dir: Path, registry: dict[str, Any]) -> list[Path]:
    fixtures = output_dir / "validation_fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    records = cast(list[dict[str, Any]], registry["records"])
    open_record = next(record for record in records if record["access_class"] == "open")
    restricted_record = next(record for record in records if record["access_class"] == "restricted")
    paths = [
        fixtures / "registry.json",
        fixtures / "crosswalk.json",
        fixtures / "conflict.json",
        fixtures / "coverage.json",
        fixtures / "review_pack.json",
    ]
    validator_records = []
    for record in records:
        validator_records.append(
            {
                "source_id": record["source_id"],
                "source_name": record["ontology_name"],
                "source_version": str(record.get("source_version") or "not_pinned_in_track_metadata"),
                "license_name": record["license_status"],
                "access_mode": str(record["access_class"]).replace("-", "_").replace("API", "api"),
                "source_access_status": record["source_access_status"],
                "supported_languages": record["language_codes"],
                "authoritative_endpoint": record["authoritative_endpoint_status"],
                "retrieval_date": GENERATED_DATE,
                "payload_commit_allowed": False,
                "derived_commit_allowed": True,
                "local_only": False,
                "payload_policy": record["source_payload_commit_policy"],
                "artifact_classes": ["committed", "generated", "pr_safe"],
                "provenance_id": str(record["source_id"]),
            }
        )
    write_json(paths[0], validator_records)
    write_json(
        paths[1],
        [
            {
                "edge_id": "probe-open-related-0001",
                "hpo_id": "HP:0000001",
                "external_source_id": open_record["source_id"],
                "external_id": f"{str(open_record['source_id']).upper()}:SCHEMA-PROBE",
                "mapping_predicate": "relatedMatch",
                "mapping_source": "ontology_network_fail_fast_probe",
                "mapping_basis": "source_xref",
                "confidence": 0.0,
                "provenance_id": "prov-crosswalk-probe-2026-06-23",
                "review_status": "needs_review",
                "candidate_only": True,
                "human_review_required": True,
            }
        ],
    )
    write_json(
        paths[2],
        [
            {
                "conflict_id": "conflict-fail-fast-1",
                "conflict_type": "source_disagreement",
                "severity": "info",
                "hpo_id": "HP:0000001",
                "source_ids": [open_record["source_id"], restricted_record["source_id"]],
                "evidence_ids": ["probe-open-related-0001"],
                "resolution_status": "needs_review",
                "reviewer_action": "confirm source evidence before candidate promotion",
                "provenance_id": "prov-conflict-fail-fast",
            }
        ],
    )
    write_json(
        paths[3],
        [
            {
                "coverage_id": "coverage-fail-fast-1",
                "source_id": open_record["source_id"],
                "hpo_branch_id": "HP:0000118",
                "language": "en",
                "predicate": "metadata_declared_language_support",
                "total_hpo_terms": 0,
                "covered_hpo_terms": 0,
                "coverage_ratio": 0.0,
                "review_status": "needs_review",
                "provenance_id": "prov-coverage-fail-fast",
            }
        ],
    )
    write_json(
        paths[4],
        [
            {
                "pack_id": "pack-en-fail-fast",
                "language": "en",
                "scope": "ontology-network fail-fast metadata probe",
                "hpo_ids": ["HP:0000001"],
                "source_ids": [open_record["source_id"], restricted_record["source_id"]],
                "crosswalk_ids": ["probe-open-related-0001"],
                "conflict_ids": ["conflict-fail-fast-1"],
                "coverage_ids": ["coverage-fail-fast-1"],
                "candidate_count": 0,
                "candidate_only": True,
                "human_review_required": True,
                "promotion_policy": "manual_review_only",
                "reviewer_role": "language reviewer",
                "provenance_id": "prov-review-pack-fail-fast",
            }
        ],
    )
    return paths


def write_json(path: Path, data: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[Path]:
    registry = build_registry()
    schemas = schema_definitions(registry)
    written: list[Path] = []

    outputs = {
        output_dir / "source_registry.json": registry,
        output_dir / "source_access_matrix.json": source_access_dataset(registry),
        output_dir / "artifact_schema_index.json": artifact_schema_index(schemas),
        output_dir / "source_payload_policy.json": payload_policy_document(),
        output_dir / "release_readiness_manifest.json": release_manifest(registry),
        output_dir / "fail_fast_samples.json": fail_fast_samples(registry),
    }
    outputs.update({output_dir / path: data for path, data in network_outputs(registry).items()})
    for path, data in outputs.items():
        write_json(path, data)
        written.append(path)

    matrix_path = output_dir / "source_access_matrix.tsv"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(source_access_matrix(registry), encoding="utf-8")
    written.append(matrix_path)

    schema_dir = output_dir / "schemas"
    expected_schema_names = {f"{name}.schema.json" for name in schemas}
    if schema_dir.exists():
        for stale_schema in schema_dir.glob("*.schema.json"):
            if stale_schema.name not in expected_schema_names:
                stale_schema.unlink()

    for name, schema_data in schemas.items():
        path = schema_dir / f"{name}.schema.json"
        write_json(path, schema_data)
        written.append(path)

    written.extend(write_validation_fixtures(output_dir, registry))

    readme = output_dir / "README.md"
    readme.write_text(
        "# Ontology Network Artifacts\n\n"
        "These artifacts are generated from Conductor track metadata and source profile specifications. "
        "They do not include raw external ontology payloads.\n\n"
        "Run `pixi run build-ontology-network` to regenerate them and `pixi run validate-ontology-network` "
        "to verify required registry, schema, source access, fail-fast, and release-readiness outputs.\n",
        encoding="utf-8",
    )
    written.append(readme)
    return written


def schema_records(output_dir: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        "source_registry_record": cast(list[dict[str, Any]], load_json(output_dir / "source_registry.json")["records"]),
        "source_access_record": cast(
            list[dict[str, Any]], load_json(output_dir / "source_access_matrix.json")["records"]
        ),
        "crosswalk_edge": cast(list[dict[str, Any]], load_json(output_dir / "crosswalk_graph.json")["edges"]),
        "language_comparison_row": cast(
            list[dict[str, Any]], load_json(output_dir / "language_comparison_packs.json")["records"]
        ),
        "conflict_report_row": cast(list[dict[str, Any]], load_json(output_dir / "conflict_heatmap.json")["records"]),
        "coverage_summary_row": cast(list[dict[str, Any]], load_json(output_dir / "coverage_summary.json")["records"]),
        "semantic_drift_record": cast(
            list[dict[str, Any]], load_json(output_dir / "semantic_drift_report.json")["records"]
        ),
        "provenance_graph_node": cast(list[dict[str, Any]], load_json(output_dir / "provenance_graph.json")["nodes"]),
        "provenance_graph_edge": cast(list[dict[str, Any]], load_json(output_dir / "provenance_graph.json")["edges"]),
        "review_workload_record": cast(
            list[dict[str, Any]], load_json(output_dir / "review_workload_report.json")["records"]
        ),
        "review_pack_record": cast(
            list[dict[str, Any]], load_json(output_dir / "language_review_packs.json")["records"]
        ),
        "license_access_record": cast(
            list[dict[str, Any]], load_json(output_dir / "license_access_report.json")["records"]
        ),
        "source_class_probe": cast(list[dict[str, Any]], load_json(output_dir / "source_class_probes.json")["records"]),
        "p3_source_governance_record": cast(
            list[dict[str, Any]], load_json(output_dir / "p3_source_governance.json")["records"]
        ),
        "release_readiness_manifest": [load_json(output_dir / "release_readiness_manifest.json")],
        "payload_policy_record": [load_json(output_dir / "source_payload_policy.json")],
        "artifact_schema_index_record": cast(
            list[dict[str, Any]], load_json(output_dir / "artifact_schema_index.json")["schemas"]
        ),
        "validation_report": [load_json(output_dir / "validation_report.json")],
    }


def schema_shape_errors(output_dir: Path, schemas: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    try:
        records_by_schema = schema_records(output_dir)
    except (KeyError, OSError, json.JSONDecodeError) as exc:
        return [f"could not load generated schema records: {exc}"]
    for name, records in sorted(records_by_schema.items()):
        schema_path = output_dir / "schemas" / f"{name}.schema.json"
        schema_data = load_json(schema_path) if schema_path.exists() else schemas[name]
        properties = set(cast(dict[str, Any], schema_data.get("properties", {})))
        required = set(cast(list[str], schema_data.get("required", [])))
        if schema_data.get("additionalProperties") is not False:
            errors.append(f"schema {name} must set additionalProperties=false")
        for index, record in enumerate(records, start=1):
            keys = set(record)
            missing = sorted(required - keys)
            extra = sorted(keys - properties)
            if missing:
                errors.append(f"{name} record {index} missing required fields: {', '.join(missing)}")
            if extra:
                errors.append(f"{name} record {index} has fields outside schema: {', '.join(extra)}")
    return errors


def validate(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[str]:
    errors: list[str] = []
    required = [
        output_dir / "source_registry.json",
        output_dir / "source_access_matrix.json",
        output_dir / "source_access_matrix.tsv",
        output_dir / "artifact_schema_index.json",
        output_dir / "source_payload_policy.json",
        output_dir / "release_readiness_manifest.json",
        output_dir / "fail_fast_samples.json",
        output_dir / "crosswalk_graph.json",
        output_dir / "language_comparison_packs.json",
        output_dir / "conflict_heatmap.json",
        output_dir / "coverage_summary.json",
        output_dir / "semantic_drift_report.json",
        output_dir / "provenance_graph.json",
        output_dir / "review_workload_report.json",
        output_dir / "language_review_packs.json",
        output_dir / "license_access_report.json",
        output_dir / "source_class_probes.json",
        output_dir / "p3_source_governance.json",
        output_dir / "reproducibility_capsule.json",
        output_dir / "validation_report.json",
    ]
    registry_for_schema = (
        load_json(output_dir / "source_registry.json")
        if (output_dir / "source_registry.json").exists()
        else build_registry()
    )
    schemas = schema_definitions(registry_for_schema)
    required.extend(output_dir / "schemas" / f"{name}.schema.json" for name in schemas)
    for path in required:
        if not path.exists():
            errors.append(f"missing required artifact: {path}")

    if not errors:
        registry = load_json(output_dir / "source_registry.json")
        records = cast(list[dict[str, Any]], registry.get("records", []))
        if registry.get("record_count") != 18 or len(records) != 18:
            errors.append("source registry must contain exactly 18 ontology source records")
        for record in records:
            if not record.get("language_codes"):
                errors.append(f"{record.get('track_id')} has no normalized language codes")
            if record.get("source_id") == "meddra" and record.get("declared_language_count") != 27:
                errors.append("MedDRA registry record must preserve declared_language_count=27")
            if record.get("access_class") == "restricted" and not record.get("restricted_sources"):
                errors.append(f"{record.get('track_id')} is restricted but lacks restricted_sources")
            if not record.get("human_review_required"):
                errors.append(f"{record.get('track_id')} must require human review")

        samples = load_json(output_dir / "fail_fast_samples.json")
        for key in ("open_source_registry_record", "restricted_source_governance_record", "crosswalk_edge"):
            if not samples.get(key):
                errors.append(f"fail-fast samples missing {key}")
        probes = load_json(output_dir / "source_class_probes.json")
        probed_classes = {record["access_class"] for record in cast(list[dict[str, Any]], probes.get("records", []))}
        registry_classes = {record["access_class"] for record in records}
        if probed_classes != registry_classes:
            errors.append("source-class probes must cover every access_class in the registry")
        p3 = load_json(output_dir / "p3_source_governance.json")
        p3_records = cast(list[dict[str, Any]], p3.get("records", []))
        if {record.get("source_id") for record in p3_records} != {"fma", "lddb"}:
            errors.append("P3 source governance must cover exactly FMA and LDDB")
        for record in p3_records:
            if record.get("payload_commit_allowed") or record.get("identifier_network_allowed"):
                errors.append(
                    f"{record.get('source_id')} P3 governance must keep payload and identifier-network work blocked"
                )
            if not record.get("human_review_required") or not record.get("candidate_only"):
                errors.append(
                    f"{record.get('source_id')} P3 governance must stay candidate-only and human-review-required"
                )
        errors.extend(schema_shape_errors(output_dir, schemas))

    for path in output_dir.rglob("*"):
        if any(part in BLOCKED_PATH_PARTS for part in path.parts):
            continue
        if path.is_file() and any(
            marker in path.name.lower() for marker in ("raw_payload", "credential_export", "licensed_release")
        ):
            errors.append(f"blocked payload-like artifact path: {path}")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".tsv"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_CONTENT_PATTERNS:
                if pattern.search(text):
                    errors.append(f"blocked restricted or secret-like content in {path}: {pattern.pattern}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and validate ontology-network governance artifacts.")
    parser.add_argument("command", choices=["build", "validate", "all"])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    if args.command in {"build", "all"}:
        written = build(args.output_dir)
        print(f"Wrote {len(written)} ontology-network artifacts to {args.output_dir}")
    if args.command in {"validate", "all"}:
        errors = validate(args.output_dir)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            raise SystemExit(1)
        write_json(
            args.output_dir / "validation_report.json",
            {
                "generated_date": GENERATED_DATE,
                "artifact": "ontology_network",
                "validation_result": "internal_validation_passed",
                "issues": [],
            },
        )
        print(f"Validated ontology-network artifacts in {args.output_dir}")


if __name__ == "__main__":
    main()
