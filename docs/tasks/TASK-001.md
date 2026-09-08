# TASK-001: Bootstrap the local Python project and commit safeguards

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: M0 planning review and local repository restoration. No previous implementation task.
- Decisions: [ADR-002](../adr/ADR-002.md), [ADR-003](../adr/ADR-003.md), [ADR-014](../adr/ADR-014.md), [ADR-015](../adr/ADR-015.md)

## Objective

Bootstrap the local Python project and commit safeguards.

## Background

Planning exists but there is no executable package. Establish a reproducible development environment before private data is introduced. Local Git/GitHub restoration is covered in LOCAL_SETUP.

## Affected modules

pyproject.toml; uv.lock; src/job_application_engine/cli.py; config.py; tests/test_cli.py; tests/test_repository_policy.py; .github/workflows/ci.yml; hook configuration; DEPENDENCIES.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Record OS/architecture/Python/tool versions without secrets; create a Python 3.12 package and jae help/version entry point; install and lock only immediate dev dependencies; configure Ruff, mypy and pytest; verify ignored private paths and staged secret/path safeguards; CI uses synthetic data and minimal permissions. Require explicit private data root and reject unsafe root/path escapes.

## Tests required

CLI help/usage exit behavior; private-root traversal/symlink rejection; git check-ignore assertions; safe synthetic secret detection and private-file stage refusal; locked install; lint/type checks.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No career schema or real profile, renderer, model, API, UI, scraper or database. Do not claim future features in CLI help as implemented.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/001-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
