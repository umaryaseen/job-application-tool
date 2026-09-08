# TASK-020: Validate and release the first tailoring MVP

- Milestone: M3
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-019](TASK-019.md)
- Decisions: [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md), [ADR-013](../adr/ADR-013.md), [ADR-014](../adr/ADR-014.md), [ADR-015](../adr/ADR-015.md)

## Objective

Validate and release the first tailoring MVP.

## Background

The system must work as one vertical CLI pipeline with actual artifacts, not isolated modules.

## Affected modules

tests/integration/test_application_pipeline.py; docs/USER_GUIDE.md; docs/reviews/M3.md; PROGRESS.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Run a clean locked install and real CLI profile→baseline→paste JD→review requirements→matrix→tailor→QA→review→export. Use at least two contrasting JDs and one unsupported-claim mutation. Run all implemented tests/lint/types and inspect generated pages. Record exact commit, checks, limitations and independent verdict. Provide commands for daily use and a real applicant-reviewed tailored snapshot privately.

## Tests required

A15, A30–A31 plus all M1–M3 regressions. No model/network required. Failed claim produces nonzero exit and no exportable artifact. Review the actual diff and produced documents.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No cover letter, tracker, models, ESCO, DOCX, UI, scraping or submission. Do not label M3 complete if genuine artifact review is still pending.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/020-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
