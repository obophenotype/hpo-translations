# Specification - Integrate SNOMED CT into terminology and translation support

## Objective
Introduce SNOMED CT as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: English, Spanish, French, German, Dutch, Danish, Swedish, Norwegian, Estonian, Finnish, and Slovak.
- GitHub repositories:
- https://github.com/IHTSDO
- https://github.com/IHTSDO/snowstorm
- https://github.com/IHTSDO/snomed-owl-toolkit
- Source note: Use licensed SNOMED CT releases; GitHub repositories are tooling, not a substitute for release distribution rights.

## Usefulness
Clinical terminology crosswalks, post-coordination review, and clinical synonym support.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and human-review-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without maintainer review.
