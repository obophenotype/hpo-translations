# Specification - Integrate PATO into terminology and translation support

## Objective
Introduce PATO as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: English only.
- GitHub repositories:
- https://github.com/pato-ontology/pato
- Source note: OBO ontology repository with release files and editorial workflow.

## Usefulness
Phenotypic quality normalization and logical definition support.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and human-review-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without maintainer review.
