# Project Workflow - Human Phenotype Ontology Internationalization Effort

## 1. Development & Contribution Flow
- **Feature Branching:** All work must be carried out on dedicated topic or feature branches (e.g., `feature/add-czech-translation` or `fix/german-typo`). Direct commits to the default main branch are prohibited.
- **Pull Request Validation:** Merges to the main branch require a Pull Request. Every Pull Request must trigger automated CI checks validating all translation files (`pixi run qc` / `make validate-all`).

## 2. Validation & Scheduled Audits
- **Local Validation:** Contributors are expected to run validation checks locally before pushing changes.
- **Scheduled Audits:** An automated weekly pipeline executes to check the validation status of all language profiles. This ensures that changes in the underlying schemas or external dependencies do not silently break the translation database.

## 3. Release Coordination
- **Release Triggers:** Translation releases are closely aligned with official upstream HPO (Human Phenotype Ontology) releases.
- **Metadata Management:** Release assets must contain complete versioning and metadata tracing back to the corresponding HPO release version.
