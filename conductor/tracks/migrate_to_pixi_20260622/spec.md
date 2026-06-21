# Specification - Migrate project environment and automation workflows from uv/Makefile to pixi and configure code quality tools (ruff and vale)

## Objective
Migrate the development environment from `uv` to `pixi`, and transition automation tasks from the `Makefile` to native `pixi` tasks. Configure quality tools (`ruff` for linting/formatting and `vale` for prose checking) to set up modern quality gates for the repository.

## Technical Details

### 1. Environment & Dependency Configuration
- Initialize a `pixi.toml` configuration targeting Python >= 3.14.
- Map the existing dependencies from `pyproject.toml` (`babelon`, `tsvalid`, `linkml`, `linkml-runtime`, `setuptools`) to pixi dependencies.
- Add `ruff` and `vale` as dev-dependencies in `pixi.toml`.

### 2. Workflow Automation & Task Migration
- Convert the main Makefile targets to `pixi tasks`:
  - `make sort-all` -> `pixi run sort-all`
  - `make clean-all` -> `pixi run clean-all`
  - `make validate-all` -> `pixi run validate-all`
  - `make qc` -> `pixi run qc`
- Ensure translation processing workflows function correctly within the pixi env wrapper.

### 3. Linting and Formatting Setup
- Configure `ruff` rules in `pixi.toml` or `pyproject.toml`.
- Configure `vale` configuration (`.vale.ini`) and vocabulary/style folders to lint markdown files.

### 4. CI/CD Migration & GitHub Actions
- Replace existing actions setups with `prefix-dev/setup-pixi` in `.github/workflows/qc.yml` and `.github/workflows/docs.yml`.
- Configure caching for the `.pixi` environments to run validation tests rapidly.

### 5. Static Analysis & Type Safety
- Add `mypy` to enforce strict type checking (`mypy --strict`) on repository python scripts.
- Incorporate LinkML native schema validator checks in the verification pipeline.

### 6. Semantic Releases & Commit Guidelines
- Introduce `commitizen` inside `pixi.toml` and configure hooks to enforce Conventional Commit formats (`feat:`, `fix:`, `chore:`).
- Enable automated version bumping, changelog generation, and tag creation during the release pipeline.

### 7. Release Packaging Automation & Diff Auditing
- Define a `pixi run package` task to compile and zip translation assets (e.g. producing `all_translations.zip`).
- Automate release creation and artifact uploads using GitHub CLI (`gh release create`) on main-branch tag releases.
- Implement a translation diff auditing task to format and output easy-to-read diff summaries of translated/modified strings.

### 8. Dependabot, Diagnostics & Performance Profiling
- Create `.github/dependabot.yml` to automatically track and update package dependencies.
- Implement a `pixi run profile` task to benchmark validation execution times per translation profile.
- Configure GitHub Actions pipeline to comment TSV validation diagnostic warnings directly on pull requests.
