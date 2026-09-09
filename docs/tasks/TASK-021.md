# TASK-021: Plan cover letters from approved claims and motivation

- Milestone: M4
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-008](../adr/ADR-008.md), [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md), [ADR-013](../adr/ADR-013.md)

## Objective

Plan cover letters from approved claims and motivation.

## Background

Letters add employer and motivation claims that are not all career facts. Keep their source classes explicit.

## Affected modules

domain/letter.py; tailoring/letter.py; verification/letter.py; tests/test_cover_letter_claims.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Build letter plans using approved career variants, JD-grounded company/role details, and applicant-approved motivation/availability statements. Static greeting/closing are finite labels; unknown recipient uses neutral hiring-team greeting. Company claims bind to JD/company evidence, never invented praise. New prose requires variant review.

## Tests required

A32: unknown contact, invented motivation, wrong company/requisition, unsupported achievements, source-revision changes, salary/availability without approved data and exact plan bindings.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No web company research, invented personal enthusiasm, autonomous letters sent, or LLM requirement.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/021-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
