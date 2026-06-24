# Specification - Integrate LOINC into terminology and translation support

## Objective
Introduce LOINC as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: English, French, German, Italian, Spanish, Chinese, Korean, Dutch, Portuguese, Russian, and Turkish.
- GitHub repositories:
- https://github.com/loinc
- https://github.com/loinc/comp-loinc
- Source note: Use official LOINC releases and terms of use; CompLOINC provides ontology build support.

## Usefulness
Laboratory and clinical observation terminology alignment.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and human-review-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without maintainer review.
