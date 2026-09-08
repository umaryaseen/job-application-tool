# TASK-003: Enforce evidence graph and reviewed wording bindings

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 4–6 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-002](TASK-002.md)
- Decisions: [ADR-001](../adr/ADR-001.md), [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md)

## Objective

Enforce evidence graph and reviewed wording bindings.

## Background

Valid reference IDs alone permit unrelated or embellished claims. Build the approval and support graph checks before a document can use facts.

## Affected modules

profile/load.py; profile/validation.py; profile/review.py; verification/support.py; tests/test_provenance.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Resolve unique exact fact/evidence revisions, approved support scopes and text variants. Reject dangling/cyclic/revoked/stale bindings. Add an explicit human review operation that records exact displayed fact/variant digests; do not trust imported approved=true or provider-written approval. User attestations are identified as such. Approval edits use revision checks.

## Tests required

A02, A04, A06: unrelated real ID; same metric wrong subject; stale evidence revisions; modified wording; generated output used as source; negation/leadership variant mismatch; approval CLI records exact payload and cannot silently approve changed content.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No arbitrary prose entailment classifier or LLM truth judge. Do not reject honest user attestations merely because no certificate exists.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/003-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
