# Specification - Define ontology network outputs for terminology triangulation, validation, and downstream artifacts

## Objective
Create an ontology-network layer that uses external biomedical terminologies and ontologies to support HPO translation triangulation while also producing reusable alignment, provenance, validation, and review artifacts.

## Ontology Network Scope
- UMLS
- SNOMED CT
- MedDRA
- ICD-10
- ICD-11
- LOINC
- MeSH
- OMIM
- Orphanet
- DECIPHER
- FMA
- PATO
- MP
- uPheno
- EFO
- DO
- OncoTree
- LDDB

## Primary Translation Use
The network should support multilingual candidate review by comparing HPO labels, synonyms, definitions, and candidate translations against licensed or open external terminology labels in matching languages.

## Additional Outputs
- Ontology source registry with version, license, access, and redistribution metadata.
- Identifier crosswalk graph between HPO entities and external ontology identifiers.
- Multilingual label and synonym comparison tables.
- Conflict reports for divergent labels, ambiguous mappings, and source disagreement.
- Provenance manifests for every generated artifact and every external source used.
- Candidate translation review packs grouped by language, ontology source, and confidence signal.
- Terminology coverage dashboards showing which HPO areas are supported by each source.
- Validation fixtures for import dry-run workflows and regression tests.
- License and access matrix separating open, restricted, API-only, and local-only sources.
- Release packages that exclude restricted payloads but include manifests, scripts, and reproducible instructions.

## Requirements
- Do not commit restricted ontology payloads.
- Treat external labels as evidence, not automatic approved translations.
- Preserve language tags, source identifiers, source versions, retrieval dates, and method provenance.
- Keep LLM-assisted output marked candidate-only and human-review-required.
- Prefer deterministic identifier mappings over text-only similarity when available.
- Emit reviewable deltas rather than silently overwriting HPO translation files.

## Non-Goals
- No redistribution of restricted content unless licensing explicitly permits it.
- No automatic promotion from network-supported candidate to approved translation.
