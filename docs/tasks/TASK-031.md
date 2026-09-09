# TASK-031: Implement one explicitly selected model adapter

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h plus provider choice; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-028](TASK-028.md)
- Decisions: [ADR-008](../adr/ADR-008.md), [ADR-011](../adr/ADR-011.md), [ADR-015](../adr/ADR-015.md)

## Objective

Implement one explicitly selected model adapter.

## Background

Choose local or cloud only when user preference/hardware/data boundary are known. The deterministic system remains useful without it.

## Affected modules

providers/selected_adapter.py; docs/MODEL_SETUP.md; tests/test_model_adapter.py; DEPENDENCIES.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Implement exactly one provider through 028 contracts. Record concrete model/config/revision or available version, timeout/size/retry budgets, minimal disclosure and credential source. Cloud requires applicant opt-in and current provider terms review; local requires explicit verified download. Store exact proposals privately; human review is the only path to approved variants.

## Tests required

A36 contract and real adapter smoke tests with sanitized input; unexpected egress, invalid outputs, invented IDs, outage and credential/log redaction; no auto-approval.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No second provider, silent local→cloud fallback, model browser/filesystem tools, real applicant upload without opt-in or rewriting approved facts.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/031-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
