# TASK-025: Add approved German document localization

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h plus applicant language review; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md)

## Objective

Add approved German document localization.

## Background

German Unicode and JD fixtures exist, but approved German prose and document business language require their own acceptance.

## Affected modules

templates/locales/de.json; profile/variant review; rendering/locale.py; tests/test_localization.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Produce separate DE document from approved German variants of the same facts. Standard headings/dates, German numeric punctuation and locale-specific letter phrasing if M4 is available. Preserve title/degree semantics and language-level facts. Missing variants are review gaps, never automatic unverified translations.

## Tests required

A12, A14, A38: current/unknown dates, accents, metric units, meaning scope, incomplete localization and genuine German artifact review.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No inferred German proficiency, bilingual full-text CV, machine translation of finished PDF or public disclosure of private translations.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/025-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
