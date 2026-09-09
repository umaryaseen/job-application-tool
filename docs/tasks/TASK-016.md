# TASK-016: Produce the evidence matrix and accept M2

- Milestone: M2
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-015](TASK-015.md)
- Decisions: [ADR-005](../adr/ADR-005.md), [ADR-006](../adr/ADR-006.md), [ADR-007](../adr/ADR-007.md), [ADR-011](../adr/ADR-011.md), [ADR-014](../adr/ADR-014.md)

## Objective

Produce the evidence matrix and accept M2.

## Background

The first useful job analysis is an inspectable matrix rather than an opaque fit score.

## Affected modules

matching/matrix.py; matching/report.py; cli.py; tests/test_match_matrix.py; docs/reviews/M2.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Combine exact/alias matches and constraint results into direct/equivalent/adjacent/no_evidence/explicitly_unmet/unknown rows. Bind fact/evidence IDs and concise method/reason codes. Report mandatory/preferred numerators/denominators with ANY/ALL semantics and N/A for empty classes. Snapshot profile/JD/requirement/alias versions. Run all implemented regressions and independent M2 review.

## Tests required

A22–A24 and M2 fixtures: missing mandatory stays visible; unrelated evidence cannot satisfy; preferred cannot hide mandatory gaps; groups count once; unknown and explicit unmet differ.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No weighted score, ATS probability, semantic model, tailored PDF or suppression of truthful low-fit applications.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/016-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
