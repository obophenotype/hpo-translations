# Code Styleguides - Human Phenotype Ontology Internationalization Effort

## 1. Python Style Guide
- **Formatter & Linter:** Ruff is the primary tool for formatting and linting.
- **Rulesets:** Enforce standard PEP 8 rules, pyupgrade (for Python >=3.14 syntax compatibility), isort (import sorting), and flake8-bugbear.
- **Line Length:** Configured to a maximum of 120 characters.

## 2. Prose & Documentation Style Guide
- **Vale Prose Linter:** Enforces editorial guidelines, syntax rules, and clear messaging across Markdown documentation (`README.md`, `docs/`, `conductor/`).
- **Configured checks:** Use `pixi run lint`, `pixi run qc`, and `pixi run vale-check`; do not require tools that are not configured in this repository.

## 3. Translation Profile (TSV) Formatting
- **Separators:** Must use Tab characters (`\t`) exclusively. Spaces should not be used as field delimiters.
- **Whitespace Hygiene:** No leading or trailing spaces are permitted inside cell contents.
- **Sorting:** Entries must be sorted alphabetically by term ID (e.g., `HP:XXXXXXX`) to avoid merge conflicts.
- **Schema Alignment:** Must strictly match the schema rules validated by `tsvalid`.
