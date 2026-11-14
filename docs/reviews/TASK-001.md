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

## Re-review (corrective head)

Date: 2026-09-12  
Reviewed implementation head: `a1e7d43c2fd387c2f5b048a42ac59b69758b4aaa` (documentation correction atop implementation `cf60afb3d650418be3eef678994961ffc0fbe92c`)  
Ancestry verified: `8939d9e` → `8eca02b` → `cfaeaf1` → `cf60afb` → `a1e7d43`. Working tree was clean.

F-001 disposition: **addressed in code**, with idempotent installer, conflict preservation, and real Git invocation tests.

F-002 disposition: **addressed in code**, with shared explicit-root validation and regression tests.

Required verification commands were attempted independently but remain an unresolved gate: `uv sync --locked`, `uv run python --version`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src` all could not execute because `uv` is not installed (`zsh: command not found: uv`). Therefore the verdict remains **CHANGES REQUIRED** until these checks run successfully in Python 3.12/uv.

## Independent verification gate (resolved)

Date: 2026-09-12
Reviewer: independent reviewer (separate session, laptop checkout)

### Environment

- Working directory: `<repository>` (matches the restored laptop checkout named in `LOCAL_SETUP.md`; not a remote/container environment).
- OS: Darwin 22.6.0 (macOS 13.6.x), architecture `x86_64` (`Umars-MBP`).
- `git status --short --branch`: `## task/001-project-bootstrap`, clean working tree. `HEAD` = `b2fce650ad2dfec53a38051f46423eee31c09d42`, matching the supplied "latest review documentation" commit.

### Ancestry and diff scope

`git diff --name-status a1e7d43c2fd387c2f5b048a42ac59b69758b4aaa HEAD` touches only `docs/PROGRESS.md` and `docs/reviews/TASK-001.md`. No source, test, hook, CI, dependency, or lockfile paths changed between the reviewed implementation head and the current `HEAD`. `git merge-base --is-ancestor a1e7d43 HEAD` confirms linear ancestry. No additional implementation review was required.

### Tooling resolution

`command -v uv` failed in the review shell (`uv` not on `PATH`), matching the prior reviewer's blocker. Inspection of standard install locations found a working executable at `uv` (version `0.12.13 (0ebbd9274 2026-09-10 x86_64-apple-darwin)`, the same version the implementer recorded in `PROGRESS.md`). No provisioning, application-code, dependency, or lockfile change was needed; the absolute path was used directly for every command below. Root cause is a missing `PATH` entry in this interactive shell, not an absent installation.

### Commands run (absolute `uv` path), exact output

- `uv sync --locked` → `Resolved 12 packages in 36ms` / `Checked 11 packages in 8ms`, exit 0. Lockfile satisfied without regeneration.
- `uv run python --version` → `Python 3.12.14`, exit 0.
- `uv run pytest -v` → `10 passed` in 2.71s, exit 0. Collected: `tests/test_cli.py` (6 tests), `tests/test_repository_policy.py` (4 tests).
- `uv run ruff check .` → `All checks passed!`, exit 0.
- `uv run ruff format --check .` → `7 files already formatted`, exit 0.
- `uv run mypy src` → `Success: no issues found in 3 source files`, exit 0.

Additional sanity checks matching `PROGRESS.md` claims: `uv run jae --version` → `jae 0.1.0` (exit 0); with `JAE_DATA_DIR` unset, `uv run jae config-check` → `jae: JAE_DATA_DIR is required and must point outside the repository` (exit 2). In this actual checkout, `git config --local --get core.hooksPath` → `.githooks`, confirming the hook installer was applied here as claimed (no `.git/hooks/pre-commit` exists, which is expected since `core.hooksPath` redirects to `.githooks`).

### Test coverage inspection (F-001 / F-002)

- `tests/test_repository_policy.py::test_git_hook_installation_and_invocation` builds a fresh temporary Git repository, copies `.githooks/` and `scripts/check_staged.py` into it, runs `scripts/install_hooks.sh` twice (idempotency), asserts `core.hooksPath` is `.githooks`, then performs **real `git commit` invocations**: a safe commit succeeds; a commit with staged synthetic credential-like content (`github_pat_...`) is rejected via the real hook path with `credential-like content staged` on stderr; a commit with a staged private path (`local-data/profile.txt`) is rejected with `private path staged` on stderr. This exercises actual hook activation end-to-end, not just a direct call to `check()`.
- `tests/test_repository_policy.py::test_hook_setup_preserves_conflicting_local_configuration` pre-sets a conflicting `core.hooksPath=custom-hooks`, runs the installer, asserts nonzero exit, an stderr message naming `custom-hooks`, and that the original setting is left untouched — matching F-001's conflict-preservation requirement.
- `src/job_application_engine/config.py::_validate_private_root` is now called for both the implicit `JAE_DATA_DIR` root and any explicit `root` argument to `safe_private_path`, applying identical absolute/existing-directory/non-symlink/repository-boundary checks.
- `tests/test_cli.py::test_safe_private_path_validates_explicit_root` regression-tests the explicit-root path directly: valid root accepted; a symlink root rejected (`match="symlink"`); a file (non-directory) root rejected (`match="existing directory"`); the repository root itself rejected (`match="outside"`). Combined with `test_safe_private_path_rejects_escape_and_symlink` (traversal and in-root symlink escape), this closes F-002 for both default and explicit roots.

### Assessment

- Task scope: acceptance criteria for TASK-001 (package bootstrap, `jae` entry point, private-root/path safeguards, staged-secret/path safeguard, locked install, lint/type checks, CI) remain met; non-goals respected (no career schema, renderer, model, API, UI, scraper, or database code present).
- F-001 and F-002 are fixed in code (unchanged since `cf60afb`, already reviewed) and are now also independently verified by execution, not just static inspection.
- Security: no secrets or personal data observed in the diff, test fixtures use synthetic values and reserved/invalid domains, hook and CLI checks were exercised against real Git operations.
- The previously unresolved gate — actual execution of `uv sync --locked`, `uv run python --version`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src` — is now closed with passing results recorded above.

## Verdict (updated)

**APPROVED**

No blocking or nonblocking findings remain open. F-001 and F-002 are addressed in code and verified by independent execution of the full required check set at implementation head `a1e7d43c2fd387c2f5b048a42ac59b69758b4aaa` (documentation-only commits `a1e7d43` → `b2fce65` on top). Next gate: proceed to TASK-002 under a fresh branch and independent review cycle.
