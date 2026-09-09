# TASK-034: Evaluate an optional independent resume parser

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-010](../adr/ADR-010.md), [ADR-013](../adr/ADR-013.md), [ADR-015](../adr/ADR-015.md)

## Objective

Evaluate an optional independent resume parser.

## Background

Two PDF extractors test document fidelity but not every resume field parser. An additional parser can provide diagnostics after license/maintenance review.

## Affected modules

docs/experiments/PARSER_DECISION.md; tests/fixtures/parser/; optional adapter only if justified. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Inspect current OpenResume or another suitable parser at a pinned version and license. Evaluate only synthetic PDFs locally; compare field-level precision/recall to approved expected maps. Record limitations and whether adoption is worth the dependency/licensing cost. Independent review before bundling/copying anything.

## Tests required

Parser field/order cases with genuine measured output; do not translate parser failures into fabricated candidate data or ATS success claims.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No copying AGPL/GPL code into presumed permissive project, commercial API upload, universal ATS emulator or assumption that subprocess separation resolves licensing.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/034-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
