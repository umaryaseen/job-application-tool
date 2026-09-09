# TASK-002: Define strict profile and typed fact schemas

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-001](TASK-001.md)
- Decisions: [ADR-001](../adr/ADR-001.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md)

## Objective

Define strict profile and typed fact schemas.

## Background

The report example schema lacks mandatory evidence and allows ambiguous date/metric values. Define enforceable domain contracts before importing any personal record.

## Affected modules

domain/profile.py; domain/fact.py; domain/evidence.py; domain/variant.py; schemas/; tests/fixtures/profiles/; tests/test_profile_schema.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Implement versioned strict bounded models with stable IDs/revisions and typed contacts, employment, education, skills, languages, authorization, metrics and date states. Time-limited facts preserve explicit expires_at or valid_through plus timezone. Evidence is mandatory for facts; include support-binding and approval records, immutable support capture hashes and kind-specific pinned source identities. Export JSON Schema from the models. Create compact/two-page clearly synthetic fixtures and invalid examples.

## Tests required

A01, A05, A07: missing/unknown fields; wrong types and coercion; bad/unknown dates; degree status, credential expiry, CEFR/test-score separation; decimal units; duplicate-key input rejection at loader; schema export drift.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No semantic inference, imported real CV, graph approval shortcuts, renderer or JSON Resume adapter. This task checks types; graph acceptance belongs to 003.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/002-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
