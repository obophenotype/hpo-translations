# Project Workflow - Human Phenotype Ontology Internationalization Effort

## 1. Track Design & Granularity
- **Granular Tasks:** All tracks must be broken down into highly detailed, clear, and granular tasks within `plan.md` to ensure minimal incremental updates.
- **Task Checkpointing:** Developers/agents must commit code immediately after completing each task.

## 2. Phase Verification, Review & Continuous Integration
- **Phase Completion & Review:** At the end of each phase, the `conductor-review` skill (or local equivalent validation runner) must run to scan code for standards, linting issues, and correctness.
- **Auto-Fix Application:** Found issues must be automatically resolved and applied.
- **Branch Pushing:** Upon completing a phase and applying fixes, the branch must be pushed to the remote repository.
- **Automatic Progression:** Once pushed, progression to the next phase is automatic.
- **Remote CI Verification:** After pushing to the remote repository, the developer/agent must query and check that the commit successfully passes all remote GitHub Actions/CI checks before marking the phase fully complete.

## 3. Development & Contribution Flow
- **Feature Branching:** All work must be carried out on dedicated topic or feature branches (e.g., `feature/add-czech-translation` or `fix/german-typo`). Direct commits to the default main branch are prohibited.
- **Pull Request Validation:** Merges to the main branch require a Pull Request. Every Pull Request must trigger automated CI checks validating all translation files (`pixi run qc` / `make validate-all`).

## 4. Validation & Scheduled Audits
- **Local Validation:** Contributors are expected to run validation checks locally before pushing changes.
- **Scheduled Audits:** An automated weekly pipeline executes to check the validation status of all language profiles. This ensures that changes in the underlying schemas or external dependencies do not silently break the translation database.

## 5. Release Coordination
- **Release Triggers:** Translation releases are closely aligned with official upstream HPO (Human Phenotype Ontology) releases.
- **Metadata Management:** Release assets must contain complete versioning and metadata tracing back to the corresponding HPO release version.

