# TASK-017: Select evidence-backed tailored content

- Milestone: M3
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-016](TASK-016.md)
- Decisions: [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md), [ADR-014](../adr/ADR-014.md)

## Objective

Select evidence-backed tailored content.

## Background

Tailoring can first be deterministic selection and ordering of approved wording. This already changes relevance without changing facts.

## Affected modules

tailoring/selection.py; tailoring/report.py; cli.py; tests/test_tailoring_selection.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Select/reorder approved variants and skills based on reviewed requirements. Keep employer/title/date facts and chronology fixed. Select relevant projects and summary variants only when approved. Deterministic tie-breaks and inclusion/exclusion rationale; mark requirements with no supported content. Build a new plan, not mutate the profile.

## Tests required

A25: same profile/two JDs produce appropriate different selections; repeated runs identical; role chronology stable; injected unsupported variant/skill rejected; no unapproved headline or summary.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No LLM prose, generated metrics, template editing, language translation or automatic profile updates.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/017-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
