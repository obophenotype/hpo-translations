import csv
import shutil
import unittest
import uuid
from pathlib import Path

from scripts.build_ontology_network import build, load_json, validate

TEST_TMP = Path(".cache/ontology-network-tests")

ADVANCED_ARTIFACTS = {
    "crosswalk_graph.json",
    "language_comparison_packs.json",
    "conflict_heatmap.json",
    "coverage_summary.json",
    "semantic_drift_report.json",
    "provenance_graph.json",
    "review_workload_report.json",
    "language_review_packs.json",
    "license_access_report.json",
    "reproducibility_capsule.json",
    "validation_report.json",
    "source_class_probes.json",
    "p3_source_governance.json",
    "validation_fixtures/registry.json",
    "validation_fixtures/crosswalk.json",
    "validation_fixtures/conflict.json",
    "validation_fixtures/coverage.json",
    "validation_fixtures/review_pack.json",
}

SOURCE_ACCESS_COLUMNS = {
    "source_id",
    "track_id",
    "ontology_name",
    "access_class",
    "license_status",
    "credential_required",
    "payload_commit_allowed",
    "pr_safe",
    "release_safe",
    "redistribution_status",
}


class OntologyNetworkTests(unittest.TestCase):
    def make_output_dir(self) -> Path:
        TEST_TMP.mkdir(parents=True, exist_ok=True)
        output_dir = TEST_TMP / f"case-{uuid.uuid4().hex}"
        output_dir.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_build_and_validate_registry_artifacts(self) -> None:
        output_dir = self.make_output_dir()
        written = build(output_dir)
        errors = validate(output_dir)
        registry = load_json(output_dir / "source_registry.json")
        samples = load_json(output_dir / "fail_fast_samples.json")

        written_rel = {path.relative_to(output_dir).as_posix() for path in written}
        self.assertGreaterEqual(len(written), 37)
        self.assertTrue(ADVANCED_ARTIFACTS.issubset(written_rel), ADVANCED_ARTIFACTS - written_rel)
        self.assertEqual(errors, [])
        self.assertEqual(registry["record_count"], 18)

        records = {record["source_id"]: record for record in registry["records"]}
        self.assertEqual(records["meddra"]["declared_language_count"], 27)
        self.assertIn("ar", records["meddra"]["language_codes"])
        self.assertEqual(records["omim"]["language_codes"], ["en"])
        self.assertEqual(records["fma"]["language_normalization_status"], "english_only")
        self.assertIn("zh", records["umls"]["language_codes"])
        self.assertNotIn("und", records["umls"]["language_codes"])
        self.assertTrue(records["umls"]["credential_required"])
        self.assertEqual(
            records["umls"]["authoritative_endpoint_status"], "authority_described_github_not_authoritative"
        )
        self.assertFalse(records["snomed_ct"]["github_repository_roles"][0]["authoritative_for_release_payload"])
        self.assertEqual(records["do"]["github_repository_roles"][0]["role"], "source_repository")

        with (output_dir / "source_access_matrix.tsv").open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            self.assertTrue(SOURCE_ACCESS_COLUMNS.issubset(set(reader.fieldnames or [])))
            rows = list(reader)
        self.assertTrue(
            any(
                row["access_class"] == "restricted"
                and row["credential_required"] == "true"
                and row["payload_commit_allowed"] == "false"
                and row["release_safe"] == "false"
                for row in rows
            )
        )

        for schema_path in (output_dir / "schemas").glob("*.schema.json"):
            schema = load_json(schema_path)
            self.assertIs(schema.get("additionalProperties"), False, schema_path.name)
        probes = load_json(output_dir / "source_class_probes.json")
        self.assertEqual(
            {row["access_class"] for row in probes["records"]},
            {"API-only", "investigation-only", "open", "restricted"},
        )
        release = load_json(output_dir / "release_readiness_manifest.json")
        self.assertTrue(release["governance_artifacts_release_ready"])
        self.assertFalse(release["source_payload_release_ready"])

        p3 = load_json(output_dir / "p3_source_governance.json")
        p3_records = {record["source_id"]: record for record in p3["records"]}
        self.assertEqual(set(p3_records), {"fma", "lddb"})
        self.assertEqual(p3_records["fma"]["go_no_go"], "governance_only_terms_review_required")
        self.assertFalse(p3_records["fma"]["source_authority_confirmed"])
        self.assertTrue(p3_records["fma"]["terms_review_required"])
        self.assertEqual(p3_records["lddb"]["go_no_go"], "no_go_authority_unknown")
        self.assertFalse(p3_records["lddb"]["source_authority_confirmed"])
        for record in p3_records.values():
            self.assertFalse(record["payload_commit_allowed"])
            self.assertFalse(record["bounded_sample_allowed"])
            self.assertFalse(record["identifier_network_allowed"])
            self.assertFalse(record["non_translation_outputs_allowed"])
            self.assertTrue(record["candidate_only"])
            self.assertTrue(record["human_review_required"])

        self.assertIsNotNone(samples["open_source_registry_record"])
        self.assertIsNotNone(samples["restricted_source_governance_record"])
        self.assertNotEqual(samples["review_pack_record"]["language"], "example")
        self.assertTrue(samples["review_pack_record"]["candidate_only"])
        self.assertTrue(samples["review_pack_record"]["human_review_required"])
        self.assertTrue(samples["crosswalk_edge"]["human_review_required"])
        self.assertIn(
            samples["open_source_registry_record"]["source_id"],
            samples["crosswalk_edge"]["external_source_id"],
        )

        fixture_registry = load_json(output_dir / "validation_fixtures" / "registry.json")
        fixture_crosswalk = load_json(output_dir / "validation_fixtures" / "crosswalk.json")
        fixture_conflict = load_json(output_dir / "validation_fixtures" / "conflict.json")
        fixture_review_pack = load_json(output_dir / "validation_fixtures" / "review_pack.json")
        self.assertIsInstance(fixture_registry, list)
        self.assertEqual(fixture_crosswalk[0]["review_status"], "needs_review")
        self.assertEqual(fixture_conflict[0]["conflict_type"], "source_disagreement")
        self.assertGreaterEqual(len(set(fixture_conflict[0]["source_ids"])), 2)
        self.assertEqual(fixture_review_pack[0]["language"], "en")
        self.assertEqual(fixture_review_pack[0]["promotion_policy"], "manual_review_only")
        self.assertTrue(fixture_review_pack[0]["human_review_required"])


if __name__ == "__main__":
    unittest.main()
