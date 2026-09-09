# TASK-029: Benchmark and optionally enable local semantic retrieval

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-027](TASK-027.md)
- Decisions: [ADR-005](../adr/ADR-005.md), [ADR-006](../adr/ADR-006.md), [ADR-011](../adr/ADR-011.md), [ADR-015](../adr/ADR-015.md)

## Objective

Benchmark and optionally enable local semantic retrieval.

## Background

The frozen benchmark exists. Measure whether a real local multilingual encoder improves retrieval on the actual laptop.

## Affected modules

providers/embeddings.py; matching/semantic.py; docs/experiments/SEMANTIC_RESULTS.md; ADR-005; tests/test_semantic_integration.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Pin model revision/checksums/license; explicit setup download then offline runtime. Encode bounded fact/requirement chunks with tokenizer limits and no silent truncation; cache by text/model/config/profile revision. Run real held-out evaluation and report CPU/memory. Suggestions stay adjacent/unconfirmed unless explicit fact support is reviewed. Independent reviewer decides adoption.

## Tests required

A35 with actual weights, EN/DE pairs, hard negatives, revision/cache invalidation, missing model fallback and truncation rejection. Record metrics whether or not adoption bar passes.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No vector database, whole-document cosine fit score, cloud embeddings without new opt-in, LLM-proven skill claims or mock-only quality evidence.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/029-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
