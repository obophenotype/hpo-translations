# Specification - Integrate ICD-10 into terminology and translation support

## Objective
Introduce ICD-10 as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: English, French, Spanish, Arabic, Chinese, Russian, plus many national localized variants.
- GitHub repositories:
- https://github.com/ICD-API
- Source note: Use WHO and national release/licensing rules; ICD-API GitHub is implementation support.

## Usefulness
Disease classification crosswalks and national morbidity/mortality coding context.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and human-review-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without maintainer review.
