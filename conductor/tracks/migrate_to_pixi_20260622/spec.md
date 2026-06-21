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
