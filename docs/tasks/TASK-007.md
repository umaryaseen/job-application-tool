# TASK-007: Implement PDF and ATS robustness checks

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 4–6 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-006](TASK-006.md)
- Decisions: [ADR-004](../adr/ADR-004.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md), [ADR-015](../adr/ADR-015.md)

## Objective

Implement PDF and ATS robustness checks.

## Background

The first CV must pass actual extraction and layout checks; beautiful output alone is insufficient.

## Affected modules

ats_qa/pdf.py; ats_qa/report.py; tests/rendering/; tests/fixtures/rendering/. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Use real Poppler and pypdf extraction with independent expected field/sequence fixtures. Produce machine-readable QA with pass/fail/warn/not_checked and versions. Measure critical fields, all meaningful text, ordering, Unicode, A4/pages/bytes and geometry; inspect raster pages and record visual result. No fake ATS score.

## Tests required

A09–A15: wrong order fixture with same words, hidden/duplicated/missing blocks, lost date, image-only or empty text, overflow, invalid page size, accented names and exact quantitative punctuation. Explicitly separate template-policy checks from actual PDF measurements.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No employer ATS simulation, online upload, commercial parser, universal success guarantee or blind golden regeneration.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/007-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
