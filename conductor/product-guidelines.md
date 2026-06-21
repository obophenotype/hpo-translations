# Product Guidelines - Human Phenotype Ontology Internationalization Effort

## 1. Quality Control & Validation
- **Babelon Schema Compliance:** All translation files must strictly adhere to the Babelon TSV schema.
- **Validation Check:** Every submission or modification must successfully pass validation using `tsvalid` before it can be merged into the main repository.
- **Syntactic Validity:** Synonyms and term translations must be structurally valid and verified using `babelon convert` to prevent build failures.

## 2. Translation Metadata
- **Provenance Tracking:** Translations must specify the source and methodology of translation.
- **Classification:** Distinguish clearly between:
  - Professional manual translations
  - Crowdsourced manual translations (e.g., Crowdin community)
  - Automated machine translations

## 3. Formatting & Git Hygiene
- **Sorting Entries:** To maintain clean git diffs and prevent merge conflicts, all translation files must be regularly sorted. The `make sort-all` task should be run to organize entries systematically.
- **Whitespace Normalization:** Regular cleanup via `make clean-all` is recommended to strip trailing spaces and normalize tab-separated fields.
