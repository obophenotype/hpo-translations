# Specification - Integrate DECIPHER into terminology and translation support

## Objective
Introduce DECIPHER as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: English only.
- GitHub repositories:
- None confirmed.
- Source note: No official public GitHub repository confirmed; use DECIPHER data-access terms.

## Usefulness
Variant, CNV, and phenotype case context where licensed access permits.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and human-review-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without maintainer review.
