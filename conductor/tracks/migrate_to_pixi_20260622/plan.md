# Plan - Migrate project environment and automation workflows from uv/Makefile to pixi and configure code quality tools (ruff and vale)

This plan outlines the sequential steps required to migrate the development environment and configure the automated checks.

## Phase 1: Environment Setup with Pixi
- [x] **Task 1:** Initialize `pixi` configuration (`pixi.toml`) in the root directory.
- [x] **Task 2:** Add Python >=3.14 environment and add standard dependencies (`babelon`, `tsvalid`, `linkml`, `linkml-runtime`, `setuptools`).
- [x] **Task 3:** Add development dependencies (`ruff` and `vale`).
- [x] **Task 4:** Verify pixi environment installation and sync.

## Phase 2: Task & Workflow Migration
- [x] **Task 1:** Define pixi tasks in `pixi.toml` matching the `sort-all` and `clean-all` Makefile behaviors.
- [x] **Task 2:** Define validation tasks (`validate-all` and `qc` equivalent) in `pixi.toml`.
- [x] **Task 3:** Verify that all translation processing commands run successfully under `pixi run`.
- [x] **Task 4:** Configure Pixi task caching (caching inputs/outputs) for translation processing and validation tasks.

## Phase 3: Code Quality & Prose Validation Configuration
- [x] **Task 1:** Configure `ruff` linting and formatting settings (in `pyproject.toml` or `pixi.toml`).
- [x] **Task 2:** Set up `.vale.ini` configuration and install basic prose styles.
- [x] **Task 3:** Verify Ruff and Vale runs on existing code and documentation.
- [x] **Task 4:** Set up git pre-commit hook template using pixi tasks to run ruff and vale.
- [x] **Task 5:** Configure pre-commit hook framework integration managed by Pixi.

## Phase 4: CI/CD & Static Analysis Configuration
- [x] **Task 1:** Update GitHub Actions workflows (`qc.yml` and `docs.yml`) to use `prefix-dev/setup-pixi` and configure caching.
- [x] **Task 2:** Add `mypy` to dev dependencies and verify static type safety of repository scripts in strict mode (`mypy --strict`).
- [x] **Task 3:** Configure native LinkML schema validation checks in the validation pipeline.

## Phase 5: Semantic Releases & Packaging Automation
- [x] **Task 1:** Add and configure `commitizen` in `pixi.toml` and git hooks for conventional commits.
- [x] **Task 2:** Create a `pixi run package` task to automatically bundle translations into release assets (e.g. `all_translations.zip`).
- [x] **Task 3:** Implement translation diff auditing script to output summary changes on PRs.

## Phase 6: Dependabot, Diagnostics & Performance Profiling
- [x] **Task 1:** Create `.github/dependabot.yml` to automatically track and update package dependencies.
- [x] **Task 2:** Implement a `pixi run profile` task to benchmark validation execution times per translation profile.
- [x] **Task 3:** Configure GitHub Actions pipeline to comment TSV validation diagnostic warnings directly on pull requests.
