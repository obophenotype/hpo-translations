# Product Guide - Human Phenotype Ontology Internationalization Effort

## Vision and Purpose
The Human Phenotype Ontology Internationalization Effort (HPOIE) coordinates translation efforts surrounding the Human Phenotype Ontology (HPO). The goal is to eliminate language barriers in phenotyping and ontology curation, facilitating cross-border clinical research and diagnostics for rare diseases.

## Target Audience
- **Downstream Consumers:** Clinical geneticists, researchers, and developers consuming downstream HPO-linked tools and databases (e.g., Monarch Initiative, national registries).
- **Contributors:** Translation contributors and language working group leads managing translation workflows on Crowdin or Google Sheets.
- **Ontology Curators:** Ontology curators integrating internationalized labels directly back into the core Human Phenotype Ontology repository.

## Key Features & Requirements
1. **Fostering Collaboration:** Providing structured environments and toolings for language translation groups.
2. **Translation Standardization:** Utilizing Babelon TSV and XLIFF (Crowdin) formats to capture rich translation metadata (distinguishing manual vs. automated translations).
3. **Release Coordination:** Syncing language profile updates with periodic HPO releases.
4. **Validation and Quality Control:** Automating checks (using `tsvalid` and `babelon`) to guarantee syntax and semantics of translations.
