# TASK-023: Add SQLite application tracking and accept M4

- Milestone: M4
- State at planning handoff: NOT STARTED
- Estimate: 4–6 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-022](TASK-022.md)
- Decisions: [ADR-002](../adr/ADR-002.md), [ADR-012](../adr/ADR-012.md), [ADR-014](../adr/ADR-014.md), [ADR-016](../adr/ADR-016.md)

## Objective

Add SQLite application tracking and accept M4.

## Background

Tracking needs transactions and immutable links but no database server. An approved document is not evidence an application was submitted.

## Affected modules

tracking/db.py; tracking/migrations/; tracking/events.py; tracking/queries.py; cli.py; tests/test_tracking.py; docs/reviews/M4.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Initialize schema version/FKs and migrations using sqlite3. Record application/company/job references, immutable snapshot ID and append-only dated status events. Permit manual submitted/rejected/interview/offer updates with dates/notes and provenance; derive current status. Correct events by new events, not rewriting history. Run M4 review and inherited regression suite.

## Tests required

A33: FK failures, migration from previous fixture, transaction rollback, duplicate events/idempotency, corrected event, approval≠submission, link to exact CV/letter version.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No Postgres/ORM, calendar/email sync, recruiter scraping, scheduling, analytics dashboard or browser submissions.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/023-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
