# TASK-001 Independent Review

Reviewer: Codex (independent reviewer)  
Date: 2026-09-12  
Base: `8939d9e8ec5af2035ca6b5a86c94ae74efedbabb`  
Implementation head reviewed: `8eca02b481a6a1f11b153cc4620d5fd85a7fd4d4`

## Verdict

**CHANGES REQUIRED**

## Findings

### F-001 — commit hook is not installed (blocking)

The repository contains `.githooks/pre-commit`, but this checkout has no `.git/hooks/pre-commit`, and no setup/configuration step installs or enables the hook. Therefore the staged private-file/secret safeguard is documentation-only for a normal commit and does not satisfy TASK-001's requirement that safeguards are actually installed.

Reproduction: `test -x .git/hooks/pre-commit` fails on the reviewed checkout; `git config --get core.hooksPath` is unset. A commit can therefore be made without invoking `scripts/check_staged.py`.

Affected files: `.githooks/pre-commit`, project setup/documentation (and/or an explicit installer).

Corrective task: Fix TASK-001 review finding F-001 only. Add a deterministic, documented installation path that configures this repository's hooks (or otherwise installs the hook), and verify it in a fresh checkout. Acceptance: `core.hooksPath` points to the repository hook directory, the hook is executable and runs on commit, and staged synthetic private paths and staged secret content are rejected while clean staged content succeeds. Retain/add tests for installation and run the full TASK-001 checks. Non-goal: no unrelated refactor.

### F-002 — explicit root bypasses root safety checks (blocking)

`safe_private_path(relative, root=...)` calls `root.resolve()` without checking that the supplied root is an existing, non-symlink directory. A symlink or non-directory explicit root is therefore accepted, contrary to the private-root symlink rejection contract.

Corrective task: validate explicit roots with the same absolute, existing-directory, non-symlink and repository-boundary checks as `private_data_root`, and add regression tests.

## Verification

Working tree was clean on branch `task/001-project-bootstrap`; `HEAD` exactly matched the supplied implementation head. Full base-to-head diff, source, tests, lockfile, dependency documentation, CI and hook configuration were inspected.

Commands run:

- `git status --short --branch` and `git rev-parse` for branch/base/head: passed; exact head matched.
- `uv sync --locked --group dev`: **not run** — `uv` is unavailable in this environment (`command not found`).
- `uv run pytest`, Ruff, Ruff format and mypy: **not run** for the same reason.
- `python3 -m pytest -q`: not run successfully; pytest is not installed.
- Hook installation check: failed as described in F-001.

The implementation code and tests were also reviewed for explicit absolute private roots, traversal and symlink rejection, ignore rules, staged-content scanning via `git show :path`, synthetic fixtures, and CI read-only permissions. No other blocking finding was identified. Rendering, schemas, model, database and application flows are correctly out of scope for TASK-001.
