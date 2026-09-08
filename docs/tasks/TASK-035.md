# TASK-035: Specify a permitted application-page handoff boundary

- Milestone: LATER
- State at planning handoff: NOT STARTED
- Estimate: 2–3 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-023](TASK-023.md)
- Decisions: [ADR-012](../adr/ADR-012.md), [ADR-015](../adr/ADR-015.md), [ADR-016](../adr/ADR-016.md)

## Objective

Specify a permitted application-page handoff boundary.

## Background

Only after reliable generation/tracking should a specific source integration be considered. This task produces a policy and task spec, not an application bot.

## Affected modules

docs/SOURCE_POLICIES.md; ADR-016 amendment; future adapter issue. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Identify one user-requested source, refresh its actual permitted operations, record permission basis/date and default-deny policy. Define input approved snapshot ID, manual screening answers and final approval checks. Keep generation independent; create one bounded implementation issue only if explicitly authorized.

## Tests required

Policy table review for expired/unknown permission, stale approval, unsupported screening answer, source mismatch and no automated final submit in design.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No scraping, credentials/cookies, account interaction, CAPTCHA bypass, mass applications, contacting recruiters or implementing browser automation in this task.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/035-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
