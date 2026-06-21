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
- [ ] **Task 3:** Verify that all translation processing commands run successfully under `pixi run`.

## Phase 3: Code Quality & Prose Validation Configuration
- [ ] **Task 1:** Configure `ruff` linting and formatting settings (in `pyproject.toml` or `pixi.toml`).
- [ ] **Task 2:** Set up `.vale.ini` configuration and install basic prose styles.
- [ ] **Task 3:** Verify Ruff and Vale runs on existing code and documentation.
- [ ] **Task 4:** Set up git pre-commit hook template using pixi tasks to run ruff and vale.
