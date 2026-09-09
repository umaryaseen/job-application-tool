# TASK-013: Normalize skills with a reviewed alias dictionary

- Milestone: M2
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-012](TASK-012.md)
- Decisions: [ADR-005](../adr/ADR-005.md), [ADR-006](../adr/ADR-006.md), [ADR-007](../adr/ADR-007.md), [ADR-011](../adr/ADR-011.md)

## Objective

Normalize skills with a reviewed alias dictionary.

## Background

Exact terms need normalization but adjacent technologies must not become equivalent.

## Affected modules

normalization/aliases.py; tests/fixtures/aliases.json; tests/test_skill_normalization.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Create small versioned EN/DE internal concept/alias mapping with provenance of mapping decisions. Preserve exact technology distinctions and directional/context restrictions. Retain unmatched surface text. Support positive/negative/context skill mentions without inferring possession.

## Tests required

A21: C/C++/C#/R boundaries, .NET, Java vs JavaScript, abbreviation expansion, EN/DE equivalent terms, deep learning vs PyTorch, AWS vs SageMaker.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No ESCO service/download, spaCy/KeyBERT dependency for trivial rules, automatic broad-concept synonyms or candidate skill invention.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/013-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
