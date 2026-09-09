# TASK-027: Define a frozen semantic retrieval benchmark

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-016](TASK-016.md)
- Decisions: [ADR-005](../adr/ADR-005.md), [ADR-011](../adr/ADR-011.md)

## Objective

Define a frozen semantic retrieval benchmark.

## Background

Embedding adoption needs labels and comparison criteria before choosing a model or tuning thresholds.

## Affected modules

tests/fixtures/semantic/; docs/experiments/SEMANTIC_BENCHMARK.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Create at least 40 supported EN/DE pairs and 40 negative/adjacent pairs across languages using synthetic career evidence. Have labels independently reviewed. Separate tuning/held-out split. Define exact baseline, Recall@5/precision/unsafe-promotion metrics and hardware measurement protocol. Freeze labels/hashes before 029.

## Tests required

Validate fixture schema, counts, split leakage by source fact/paraphrase family, explicit hard negatives and reproducible metric denominators. Acceptance A35 adoption threshold documented before model run.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No downloading/tuning models, selecting thresholds from held-out results, employer ATS score or claims of population-level benchmark validity.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/027-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
