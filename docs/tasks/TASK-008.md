# TASK-008: Create immutable snapshots and hash-bound approval/export

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 4–6 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-007](TASK-007.md)
- Decisions: [ADR-002](../adr/ADR-002.md), [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md), [ADR-015](../adr/ADR-015.md)

## Objective

Create immutable snapshots and hash-bound approval/export.

## Background

Generated files must remain tied to the reviewed content and sources. Introduce the first application version without needing a tracker database.

## Affected modules

snapshots/store.py; snapshots/manifest.py; snapshots/review.py; snapshots/export.py; cli.py; tests/test_snapshots.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Atomically publish complete private snapshots with source slice, evidence/variant approvals, plan, PDF/TXT, QA and version hashes. Preserve stored bytes and reject overwrite. Record final human approval separately against manifest/PDF/TXT digests. Export rechecks hashes, source revocation and approval. Failed builds never become ready artifacts.

## Tests required

A28–A29: interruption, existing ID, temp cleanup, modified PDF/plan, changed fact/template, stale review, revoked evidence, concurrent revision conflict and unauthorized export; restore/read manifest verifies all file hashes.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No SQLite, signing infrastructure, browser submit, mutable approved Boolean, copying raw identity documents, or deleting application history.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/008-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
