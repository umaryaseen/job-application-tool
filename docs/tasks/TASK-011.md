# TASK-011: Extract source-grounded requirement candidates

- Milestone: M2
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-010](TASK-010.md)
- Sequencing: [ADR-021](../adr/ADR-021.md) permits source-only implementation
  before personal acceptance; no milestone release or matching gate is waived.
- Decisions: [ADR-007](../adr/ADR-007.md), [ADR-013](../adr/ADR-013.md), [ADR-015](../adr/ADR-015.md)

## Objective

Extract source-grounded requirement candidates.

## Background

Requirement text needs stable quotes and offsets, even when interpretation is uncertain.

## Affected modules

domain/requirement.py; extraction/spans.py; extraction/rules.py; tests/test_requirement_spans.py. Paths are intended additions unless already present; inspect before editing.

Expose read-only `jae job-extract --job-id ID [--revision N]` for a verified
saved source. Return draft candidates as JSON without changing intake files or
creating persistent requirement review/approval records. Priority remains
unspecified in this task; classification is TASK-012.

## Acceptance criteria

Implement bounded sentence/list/section extraction for EN/DE with exact original quotes and offsets. Classify kind separately from priority. Recognize technology/education/language/years candidates without claiming all prose is resolved. Keep responsibilities, context and ambiguous spans visible. Establish at least 12 EN and 12 DE short fixtures with independently reviewed labels.

## Tests required

A17: quotation round-trip, Unicode offsets, repeated phrases, section boundaries, unsupported span, negative statements and unrelated benefit text; no fabricated requirements.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No embeddings, ESCO, LLM, mandatory/default classification shortcuts, or treating JD as career evidence.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/011-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
