# Specification - Integrate ICD-11 into terminology and translation support

## Objective
Introduce ICD-11 as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: Arabic, Chinese, Czech, English, French, Portuguese, Russian, Spanish, Turkish, and Uzbek.
- GitHub repositories:
- https://github.com/ICD-API
- Source note: Use WHO ICD API, browser, and licensing as authority; GitHub repositories are implementation support.

## Usefulness
Digital-first disease classification, multilingual terminology comparison, and ICD-11 foundation alignment.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and human-review-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without maintainer review.
