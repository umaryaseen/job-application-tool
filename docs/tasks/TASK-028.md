# TASK-028: Define bounded model proposal interfaces

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-007](../adr/ADR-007.md), [ADR-008](../adr/ADR-008.md), [ADR-011](../adr/ADR-011.md), [ADR-015](../adr/ADR-015.md)

## Objective

Define bounded model proposal interfaces.

## Background

Model use should not infect deterministic core functions or grant publishing authority. Introduce contracts only for the next concrete adapter.

## Affected modules

providers/contracts.py; providers/config.py; domain/proposal.py; tests/test_provider_contracts.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Define RequirementProposer/WordingProposer request-response types, selected source-bundle digest, allowed IDs, bounded response and timeout/error codes. Default provider disabled. Model output creates review proposals only and cannot alter approval records or render/export a CV.

## Tests required

A36 using a fake provider for contract/error tests: invalid JSON/IDs, excessive output, timeout, hostile instructions, attempted approval fields and no-provider baseline. Label these as contract tests, not model-quality tests.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No provider chosen automatically, model downloads, secrets store framework, vendor-specific core fields or NLI-based factuality bypass.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/028-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
