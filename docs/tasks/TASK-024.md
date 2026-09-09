# TASK-024: Add direct DOCX export

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-009](../adr/ADR-009.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md)

## Objective

Add direct DOCX export.

## Background

A real portal may request DOCX. Add one projection of the approved plan while preserving evidence and truthful layout claims.

## Affected modules

rendering/docx.py; templates/docx/; tests/rendering/test_docx.py; DEPENDENCIES.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Use python-docx with plain paragraphs/headings/bullets and body contact text. Create DOCX from the same validated plan; include it in hash-bound approval. Record the available office rendering engine and version; visually verify pagination before claiming DOCX ready.

## Tests required

A37: XML/text fields/order, Unicode, no core tables/text boxes/header-only contacts, all claims accounted for; actual office-render page inspection; changed DOCX invalidates approval.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No PDF conversion, DOCX source database, tracked personal documents or assertion that PDF pagination proves Word pagination.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/024-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
