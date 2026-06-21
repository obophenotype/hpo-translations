# Technology Stack - Human Phenotype Ontology Internationalization Effort

## Core Language & Runtime
- **Python >= 3.14:** Utilizing the latest Python features, runtime improvements, and performance enhancements.

## Package & Environment Management
- **Pixi:** A modern, lightning-fast package manager and workflow tool based on Conda/Rattler ecosystem, replacing `uv` for cross-platform dependency resolution, task running, and environment consistency.

## Data Processing & Ontology Modeling
- **Babelon (>= 0.3.6):** Parses translation assets (e.g., Crowdin XLIFF files) to Babelon TSV and handles OWL conversions.
- **LinkML & LinkML-Runtime (>= 1.10):** Semantic modeling language used to structure translation metadata and validation templates.
- **TSValid (>= 0.0.5):** Validates TSV structure and alignment with schema definitions.

## Quality Assurance & Formatting (Bleeding Edge)
- **Ruff:** An extremely fast Python linter and formatter written in Rust, replacing traditional tools like flake8, black, and isort.
- **Pixi Tasks:** Used to define tasks (e.g., `pixi run qc`, `pixi run sort-all`, `pixi run update`) for automated validation and quality gates, reducing reliance on legacy Makefiles.
- **Pre-commit / Git Hooks:** Integrated via Pixi task runner to automate linting, formatting, and validation prior to committing code.
