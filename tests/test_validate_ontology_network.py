import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

from scripts.build_ontology_network import build, schema_definitions
from scripts.validate_ontology_network import validate_artifacts, write_schemas

TEST_TMP = Path(os.environ.get("ONTOLOGY_NETWORK_TEST_TMP", ".cache/ontology-network-validation-tests"))


def write_json(root: Path, name: str, records: list[dict[str, object]]) -> Path:
    path = root / name
    path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return path


def registry_record(source_id: str = "mesh") -> dict[str, object]:
    return {
        "source_id": source_id,
        "source_name": "MeSH",
        "source_version": "2026",
        "license_name": "Public domain notice with terms review",
        "access_mode": "open",
        "source_access_status": "public_download_terms_review_required",
        "supported_languages": ["en", "es"],
        "authoritative_endpoint": "https://id.nlm.nih.gov/mesh/",
        "retrieval_date": "2026-06-23",
        "payload_commit_allowed": False,
        "derived_commit_allowed": True,
        "local_only": False,
        "payload_policy": "commit schemas, validation summaries, and bounded non-restricted rows only",
        "artifact_classes": ["committed", "generated", "pr_safe"],
        "provenance_id": "prov-mesh-2026",
    }


def crosswalk_record(source_id: str = "mesh") -> dict[str, object]:
    return {
        "edge_id": "edge-1",
        "hpo_id": "HP:0001250",
        "external_source_id": source_id,
        "external_id": "MESH:D009128",
        "mapping_predicate": "exactMatch",
        "mapping_source": "manual fixture",
        "mapping_basis": "curated_identifier",
        "confidence": 1.0,
        "provenance_id": "prov-crosswalk-1",
        "review_status": "needs_review",
        "candidate_only": True,
        "human_review_required": True,
    }


def conflict_record() -> dict[str, object]:
    return {
        "conflict_id": "conflict-1",
        "conflict_type": "source_disagreement",
        "severity": "medium",
        "hpo_id": "HP:0001250",
        "source_ids": ["mesh", "orphanet"],
        "evidence_ids": ["edge-1", "edge-2"],
        "resolution_status": "needs_review",
        "reviewer_action": "review divergent external labels before candidate promotion",
        "provenance_id": "prov-conflict-1",
    }


def coverage_record() -> dict[str, object]:
    return {
        "coverage_id": "coverage-1",
        "source_id": "mesh",
        "hpo_branch_id": "HP:0000118",
        "language": "en",
        "predicate": "exactMatch",
        "total_hpo_terms": 10,
        "covered_hpo_terms": 4,
        "coverage_ratio": 0.4,
        "review_status": "needs_review",
        "provenance_id": "prov-coverage-1",
    }


def review_pack_record() -> dict[str, object]:
    return {
        "pack_id": "pack-es-mesh-1",
        "language": "es",
        "scope": "MeSH-supported seizure terms",
        "hpo_ids": ["HP:0001250"],
        "source_ids": ["mesh"],
        "crosswalk_ids": ["edge-1"],
        "conflict_ids": [],
        "coverage_ids": ["coverage-1"],
        "candidate_count": 3,
        "candidate_only": True,
        "human_review_required": True,
        "promotion_policy": "manual_review_only",
        "reviewer_role": "language reviewer",
        "provenance_id": "prov-pack-1",
    }


def issue_codes(report: dict[str, object]) -> set[str]:
    issues = report["issues"]
    assert isinstance(issues, list)
    return {str(issue["code"]) for issue in issues if isinstance(issue, dict)}


class ValidateOntologyNetworkTests(unittest.TestCase):
    def make_root(self) -> Path:
        TEST_TMP.mkdir(parents=True, exist_ok=True)
        root = TEST_TMP / f"case-{uuid.uuid4().hex}"
        root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_valid_network_artifacts_pass(self) -> None:
        root = self.make_root()
        registry = write_json(root, "registry.json", [registry_record(), registry_record("orphanet")])
        crosswalk = write_json(root, "crosswalk.json", [crosswalk_record()])
        conflict = write_json(root, "conflict.json", [conflict_record()])
        coverage = write_json(root, "coverage.json", [coverage_record()])
        review_pack = write_json(root, "review_pack.json", [review_pack_record()])

        report = validate_artifacts(
            {
                "registry": [registry],
                "crosswalk": [crosswalk],
                "conflict": [conflict],
                "coverage": [coverage],
                "review_pack": [review_pack],
            }
        )

        self.assertEqual(issue_codes(report), set())
        summary = report["summary"]
        assert isinstance(summary, dict)
        self.assertTrue(summary["release_ready"])

    def test_generated_primary_artifacts_pass_standalone_validation(self) -> None:
        root = self.make_root()
        build(root)

        report = validate_artifacts(
            {
                "registry": [root / "source_registry.json"],
                "crosswalk": [root / "crosswalk_graph.json"],
                "conflict": [root / "conflict_heatmap.json"],
                "coverage": [root / "coverage_summary.json"],
                "review_pack": [root / "language_review_packs.json"],
            }
        )

        self.assertEqual(issue_codes(report), set())
        summary = report["summary"]
        assert isinstance(summary, dict)
        self.assertTrue(summary["release_ready"])
        self.assertEqual(summary["registry_source_count"], 18)

    def test_registry_blocks_restricted_payload_commit(self) -> None:
        root = self.make_root()
        bad_registry = registry_record()
        bad_registry["access_mode"] = "restricted"
        bad_registry["payload_commit_allowed"] = True
        registry = write_json(root, "registry.json", [bad_registry])

        report = validate_artifacts(
            {"registry": [registry], "crosswalk": [], "conflict": [], "coverage": [], "review_pack": []}
        )

        self.assertIn("registry.payload_commit_allowed.restricted_source", issue_codes(report))

    def test_crosswalk_requires_registered_source_and_candidate_guardrails(self) -> None:
        root = self.make_root()
        registry = write_json(root, "registry.json", [registry_record()])
        bad_crosswalk = crosswalk_record("missing-source")
        bad_crosswalk["candidate_only"] = False
        bad_crosswalk["human_review_required"] = False
        crosswalk = write_json(root, "crosswalk.json", [bad_crosswalk])

        report = validate_artifacts(
            {"registry": [registry], "crosswalk": [crosswalk], "conflict": [], "coverage": [], "review_pack": []}
        )

        codes = issue_codes(report)
        self.assertIn("crosswalk.source_id.unknown", codes)
        self.assertIn("crosswalk.candidate_only.required", codes)
        self.assertIn("crosswalk.human_review_required.required", codes)

    def test_crosswalk_warns_on_nondeterministic_mapping_basis(self) -> None:
        root = self.make_root()
        crosswalk_row = crosswalk_record()
        crosswalk_row["mapping_basis"] = "text_similarity"
        crosswalk = write_json(root, "crosswalk.json", [crosswalk_row])

        report = validate_artifacts(
            {"registry": [], "crosswalk": [crosswalk], "conflict": [], "coverage": [], "review_pack": []}
        )

        self.assertIn("crosswalk.mapping_basis.nondeterministic", issue_codes(report))
        summary = report["summary"]
        assert isinstance(summary, dict)
        self.assertTrue(summary["release_ready"])

    def test_coverage_ratio_must_match_counts(self) -> None:
        root = self.make_root()
        coverage_row = coverage_record()
        coverage_row["coverage_ratio"] = 0.9
        coverage = write_json(root, "coverage.json", [coverage_row])

        report = validate_artifacts(
            {"registry": [], "crosswalk": [], "conflict": [], "coverage": [coverage], "review_pack": []}
        )

        self.assertIn("coverage.coverage_ratio.mismatch", issue_codes(report))

    def test_review_pack_requires_human_review_and_evidence_links(self) -> None:
        root = self.make_root()
        review_pack_row = review_pack_record()
        review_pack_row["human_review_required"] = False
        review_pack_row["crosswalk_ids"] = []
        review_pack_row["coverage_ids"] = []
        review_pack = write_json(root, "review_pack.json", [review_pack_row])

        report = validate_artifacts(
            {"registry": [], "crosswalk": [], "conflict": [], "coverage": [], "review_pack": [review_pack]}
        )

        codes = issue_codes(report)
        self.assertIn("review_pack.human_review_required.required", codes)
        self.assertIn("review_pack.evidence_links.missing", codes)

    def test_schema_output_writes_generated_record_contracts(self) -> None:
        root = self.make_root()
        schema_dir = root / "schemas"
        write_schemas(schema_dir)

        expected = {f"{name}.schema.json" for name in schema_definitions()}
        self.assertEqual({path.name for path in schema_dir.iterdir()}, expected)
        registry_schema = json.loads((schema_dir / "source_registry_record.schema.json").read_text(encoding="utf-8"))
        self.assertIn("ontology_name", registry_schema["properties"])
        self.assertIn("language_codes", registry_schema["properties"])
        self.assertIs(registry_schema["additionalProperties"], False)

    def test_cli_writes_reports_and_exits_zero_for_valid_artifacts(self) -> None:
        root = self.make_root()
        registry = write_json(root, "registry.json", [registry_record()])
        json_report = root / "report.json"
        text_report = root / "report.md"

        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_ontology_network.py",
                "--registry",
                str(registry),
                "--json-output",
                str(json_report),
                "--text-output",
                str(text_report),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json_report.exists())
        self.assertIn("Ontology Network Validation Report", text_report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
