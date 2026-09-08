# TASK-032: Design the smallest local review UI from observed friction

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 2–3 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-003](../adr/ADR-003.md), [ADR-012](../adr/ADR-012.md), [ADR-015](../adr/ADR-015.md)

## Objective

Design the smallest local review UI from observed friction.

## Background

A UI should address actual repeated CLI friction after the working pipeline, not precede it. This is a design-only task before UI coding.

## Affected modules

docs/experiments/UI_DECISION.md; ADR-003 amendment; future issue specs. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Measure review/edit steps on two real workflows without logging private contents. Compare static local report vs minimal local web UI. Specify only needed screens/actions and localhost/auth/origin/CSRF/path controls if a server is justified. Independent review produces bounded UI implementation issues.

## Tests required

Review walkthrough covers stale approval, pending wording, visible gaps and unapproved export. No implemented UI test claims.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No React/FastAPI scaffolding, deployment, telemetry, new application logic in frontend or full dashboard.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/032-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
