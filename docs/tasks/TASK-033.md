# TASK-033: Add portable backup, selective deletion and basic outcome analytics

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 4–6 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-023](TASK-023.md)
- Decisions: [ADR-002](../adr/ADR-002.md), [ADR-012](../adr/ADR-012.md), [ADR-015](../adr/ADR-015.md)

## Objective

Add portable backup, selective deletion and basic outcome analytics.

## Background

Private artifacts need recoverable backups and honest outcome counts. Implement as bounded CLI operations; split this task if it exceeds a focused day.

## Affected modules

tracking/analytics.py; snapshots/backup.py; snapshots/delete.py; cli.py; tests/test_backup_analytics.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Export private snapshot/tracker set with checksums and consistent SQLite backup; restore to new target with conflict checks. Deletion previews exact affected snapshots/events/caches and requires explicit user action. Report submitted-application denominator and response/interview counts by cohort with sample sizes; no causal claims.

## Tests required

A40: backup/restore hash identity, missing/corrupt file, FK integrity, existing-target conflict, cache deletion linkage, approved-only not counted submitted, corrected events, zero denominators.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No automatic destructive retention, guaranteed secure SSD erasure, encrypted-backup claims without implementation, ML outcome optimization or external analytics.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/033-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
