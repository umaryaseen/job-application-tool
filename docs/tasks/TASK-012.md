# TASK-012: Classify priorities, negation and alternatives

- Milestone: M2
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-011](TASK-011.md)
- Decisions: [ADR-007](../adr/ADR-007.md), [ADR-011](../adr/ADR-011.md)

## Objective

Classify priorities, negation and alternatives.

## Background

Mandatory/preferred and OR/AND semantics materially change matching. Preserve ambiguity rather than force a binary label.

## Affected modules

extraction/priority.py; extraction/groups.py; domain/requirement.py; tests/test_requirement_classification.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Assign mandatory/preferred/unspecified with cue/span/rationale. Support ALL/ANY groups and negation, threshold operator/unit/scope. Preserve degree-or-equivalent and Python-or-Java correctly. Complex unsupported clauses become needs_review. Merge duplicates only with retained equivalent qualifiers/spans.

## Tests required

A18–A19: explicit EN/DE cues; “German not required”; “Python or Java”; “degree or equivalent experience”; preferred headings with explicit must inside; nested conjunction; ambiguous mixed sentence and duplicates.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No invented priority, calibrated confidence scores, LLM repair or rejecting candidates based on unknown grammar.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/012-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
