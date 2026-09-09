# TASK-018: Enforce a deterministic rendered page budget

- Milestone: M3
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-017](TASK-017.md)
- Decisions: [ADR-004](../adr/ADR-004.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md)

## Objective

Enforce a deterministic rendered page budget.

## Background

Selection must fit two readable pages and cannot rely on rough word counts alone.

## Affected modules

tailoring/page_budget.py; rendering/pdf.py integration; tests/test_page_budget.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Render/measure in a bounded loop of at most 20 iterations. Remove lowest-priority optional bullets or choose approved shorter variants deterministically; preserve role identity/dates and required sections. Record what changed and rerun claim/ATS checks on the final plan. Fail with actionable overlength report if protected content cannot fit.

## Tests required

A13, A26: overflowing profile, long German variants, ties, all-protected overflow, no tiny fonts, no page truncation, all final claims remain bound.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No knapsack solver, beam search, raw sentence truncation, disappearing chronology or silent third-page acceptance.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/018-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
