# TASK-022: Render and review one-page cover letters

- Milestone: M4
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-021](TASK-021.md)
- Decisions: [ADR-004](../adr/ADR-004.md), [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md), [ADR-013](../adr/ADR-013.md)

## Objective

Render and review one-page cover letters.

## Background

Letters should use the existing validated rendering/snapshot machinery, not a separate uncontrolled writer.

## Affected modules

rendering/letter.py; templates/letter/; ats_qa/letter.py; tests/rendering/test_letter.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Render one A4 page PDF/TXT from validated letter plan with readable standard typography; integrate checks and exact artifact review into the application snapshot. Optional/required/skipped letter status is explicit. Overflow asks for approved shorter content, not a second page.

## Tests required

A09–A14 as applicable plus A32: one-page output, Unicode, letter/CV company consistency, unapproved letter blocks letter export and preserves prior CV snapshot.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No second PDF backend, DOCX letter, auto-send, arbitrary HTML or unreviewed motivation generation.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/022-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
