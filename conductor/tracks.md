# Project Tracks

This file tracks all major tracks for the project. Each track has its own detailed plan in its respective folder.

<!-- conductor-automation-index:start -->
## Automation Index

| Track | Status | Priority | Source Access | Depends On | Blocks | Parallel Group | CI | Review | Merge |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `migrate_to_pixi_20260622` | `legacy_complete` | `legacy` | `not_applicable` | `-` | `translation_agents_20260622` | `foundation` | `not_started` | `not_started` | `legacy_unverified` |
| `translation_agents_20260622` | `legacy_complete` | `legacy` | `not_applicable` | `migrate_to_pixi_20260622` | `ontology_network_20260623, language_candidate_tracks` | `foundation` | `not_started` | `not_started` | `legacy_unverified` |
| `conductor_validation_20260623` | `planned` | `P0` | `not_applicable` | `migrate_to_pixi_20260622, translation_agents_20260622` | `ontology_network_20260623, all_future_conductor_tracks` | `conductor-validation` | `not_started` | `not_started` | `not_opened` |
| `ontology_network_20260623` | `implemented` | `P0` | `mixed_network_sources` | `conductor_validation_20260623:phase_1_metadata_schema, translation_agents_20260622` | `umls_metathesaurus_integration_20260623, snomed_ct_integration_20260623, meddra_integration_20260623, icd10_integration_20260623, icd11_integration_20260623, loinc_integration_20260623, mesh_integration_20260623, orphanet_integration_20260623, omim_integration_20260623, decipher_integration_20260623, fma_integration_20260623, pato_integration_20260623, mp_integration_20260623, upheno_integration_20260623, efo_integration_20260623, do_integration_20260623, oncotree_integration_20260623, lddb_integration_20260623` | `ontology-network` | `local_passing` | `subagent_review_completed_fixes_applied` | `not_opened` |
| `umls_metathesaurus_integration_20260623` | `planned` | `P2` | `license_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `snomed_ct_integration_20260623` | `planned` | `P2` | `license_or_affiliate_release_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `meddra_integration_20260623` | `planned` | `P2` | `subscription_or_license_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `icd10_integration_20260623` | `planned` | `P2` | `public_or_national_variant_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `icd11_integration_20260623` | `planned` | `P1` | `public_api_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `loinc_integration_20260623` | `planned` | `P2` | `free_account_license_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `mesh_integration_20260623` | `planned` | `P1` | `public_download_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `orphanet_integration_20260623` | `planned` | `P1` | `public_download_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `omim_integration_20260623` | `planned` | `P2` | `api_key_or_license_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `decipher_integration_20260623` | `planned` | `P2` | `permission_or_api_terms_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `fma_integration_20260623` | `phase_0_implemented_blocked` | `P3` | `public_ontology_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `local_passing` | `subagent_review_completed_fixes_applied` | `not_opened` |
| `pato_integration_20260623` | `planned` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `mp_integration_20260623` | `planned` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `upheno_integration_20260623` | `planned` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `efo_integration_20260623` | `planned` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `do_integration_20260623` | `planned` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `oncotree_integration_20260623` | `planned` | `P1` | `open_api_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_started` | `not_started` | `not_opened` |
| `lddb_integration_20260623` | `phase_0_implemented_blocked` | `P3` | `source_authority_and_access_unknown` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `local_passing` | `subagent_review_completed_fixes_applied` | `not_opened` |
<!-- conductor-automation-index:end -->

---

## [x] Track: Migrate project environment and automation workflows from uv/Makefile to pixi and configure code quality tools (ruff and vale)
*Link: [./tracks/migrate_to_pixi_20260622/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/migrate_to_pixi_20260622/)*

---

## [x] Track: Implement translation completeness audits and automated translation using LLM coding agents
*Link: [./tracks/translation_agents_20260622/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/translation_agents_20260622/)*


---

## [ ] Track: Implement automated Conductor validation and lifecycle gates
*Link: [./tracks/conductor_validation_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/conductor_validation_20260623/)*

---

## [ ] Track: Integrate UMLS Metathesaurus into terminology and translation support
*Link: [./tracks/umls_metathesaurus_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/umls_metathesaurus_integration_20260623/)*

---

## [ ] Track: Integrate SNOMED CT into terminology and translation support
*Link: [./tracks/snomed_ct_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/snomed_ct_integration_20260623/)*

---

## [ ] Track: Integrate MedDRA into terminology and translation support
*Link: [./tracks/meddra_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/meddra_integration_20260623/)*

---

## [ ] Track: Integrate ICD-10 into terminology and translation support
*Link: [./tracks/icd10_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/icd10_integration_20260623/)*

---

## [ ] Track: Integrate ICD-11 into terminology and translation support
*Link: [./tracks/icd11_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/icd11_integration_20260623/)*

---

## [ ] Track: Integrate LOINC into terminology and translation support
*Link: [./tracks/loinc_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/loinc_integration_20260623/)*

---

## [ ] Track: Integrate MeSH into terminology and translation support
*Link: [./tracks/mesh_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/mesh_integration_20260623/)*

---

## [ ] Track: Integrate Orphanet into terminology and translation support
*Link: [./tracks/orphanet_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/orphanet_integration_20260623/)*

---

## [ ] Track: Integrate OMIM into terminology and translation support
*Link: [./tracks/omim_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/omim_integration_20260623/)*

---

## [ ] Track: Integrate DECIPHER into terminology and translation support
*Link: [./tracks/decipher_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/decipher_integration_20260623/)*

---

## [ ] Track: Integrate FMA into terminology and translation support
*Link: [./tracks/fma_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/fma_integration_20260623/)*

---

## [ ] Track: Integrate PATO into terminology and translation support
*Link: [./tracks/pato_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/pato_integration_20260623/)*

---

## [ ] Track: Integrate Mammalian Phenotype Ontology into terminology and translation support
*Link: [./tracks/mp_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/mp_integration_20260623/)*

---

## [ ] Track: Integrate uPheno into terminology and translation support
*Link: [./tracks/upheno_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/upheno_integration_20260623/)*

---

## [ ] Track: Integrate EFO into terminology and translation support
*Link: [./tracks/efo_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/efo_integration_20260623/)*

---

## [ ] Track: Integrate Disease Ontology into terminology and translation support
*Link: [./tracks/do_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/do_integration_20260623/)*

---

## [ ] Track: Integrate OncoTree into terminology and translation support
*Link: [./tracks/oncotree_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/oncotree_integration_20260623/)*

---

## [ ] Track: Integrate LDDB into terminology and translation support
*Link: [./tracks/lddb_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/lddb_integration_20260623/)*

---

## [x] Track: Define ontology network outputs for terminology triangulation, validation, and downstream artifacts
*Link: [./tracks/ontology_network_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/ontology_network_20260623/)*
