# TASK-014: Add requirement review and correction versions

- Milestone: M2
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-012](TASK-012.md), [TASK-013](TASK-013.md)
- Decisions: [ADR-007](../adr/ADR-007.md), [ADR-012](../adr/ADR-012.md)

## Objective

Add requirement review and correction versions.

## Background

Deterministic extraction cannot reliably interpret every job ad. Users need a precise correction path tied to original text.

## Affected modules

extraction/review.py; snapshots/requirements.py; cli.py; tests/test_requirement_review.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Display quotes, priority, groups and uncertainty. Accept explicit reviewed corrections with actor/time and JD digest. Store immutable patches/revisions; validate all resulting source spans. Unreviewed complex clauses stay visible and cannot quietly become fulfilled constraints.

## Tests required

A20: edit priority/group, invalid quote, stale JD digest, concurrent review, changed JD invalidation and replay against same source.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No visual web editor, model-generated approvals or silently altering raw posting text.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/014-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
