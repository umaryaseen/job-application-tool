# TASK-006: Implement the chosen deterministic PDF adapter

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-005](TASK-005.md)
- Decisions: [ADR-004](../adr/ADR-004.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md), [ADR-015](../adr/ADR-015.md)

## Objective

Implement the chosen deterministic PDF adapter.

## Background

A reviewed renderer choice now exists. Implement only its narrow plan-to-PDF adapter and trusted ATS template.

## Affected modules

rendering/pdf.py; templates/; cli.py; tests/test_rendering.py; DEPENDENCIES.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Accept only validated DocumentPlan; produce PDF in private staging. Pin backend/engine/fonts/template and document each dependency. Enforce A4, one column, 11 pt body, 20 mm margins, ordinary bullets/body contacts and no decorative content. Escape all source text and bound assets, paths, subprocess runtime/output. Expose baseline cv build with truthful implemented behavior.

## Tests required

A08 and a real two-page fixture smoke test: long names/URLs, German Unicode, raw Typst/HTML/template payloads, remote/file links, timeout and temp-file failure cleanup. Compare text content with plan.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No second backend, downloaded remote fonts, arbitrary custom user templates, DOCX, semantic generation or page-budget pruning.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/006-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
