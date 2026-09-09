# TASK-015: Evaluate scoped hard requirements and experience intervals

- Milestone: M2
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-014](TASK-014.md)
- Decisions: [ADR-007](../adr/ADR-007.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md)

## Objective

Evaluate scoped hard requirements and experience intervals.

## Background

Language, credentials, authorization and years require precise handling, not cosine similarity.

## Affected modules

matching/constraints.py; matching/durations.py; tests/test_constraints.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Evaluate direct supported language/credential/numeric constraints with explicit unknown/no_evidence/unmet results. Compute duration only from scoped approved intervals with pinned as-of date and union overlap policy; preserve precision and part-time meaning. Existing authorization text is not legal inference.

## Tests required

A07, A22–A23: overlap, gaps, per-skill vs overall duration, unknown dates, in-progress degree, expired cert, IELTS vs CEFR, missing authorization and explicit unmet level.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No legal advice, career-wide→AI-years conversion, FTE assumptions, seniority inference, semantic hard-constraint satisfaction or automatic application rejection.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/015-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
