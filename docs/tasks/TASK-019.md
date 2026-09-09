# TASK-019: Harden claim, numeric and privacy adversarial validation

- Milestone: M3
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-018](TASK-018.md)
- Decisions: [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md), [ADR-015](../adr/ADR-015.md)

## Objective

Harden claim, numeric and privacy adversarial validation.

## Background

Before the complete tailoring MVP, exercise attacks that reference checks and happy-path rendering would miss. Preserve first-release checks; expand them against the integrated export path.

## Affected modules

verification/; tests/security/; tests/regression/test_claim_attacks.py; snapshots/export.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Exercise each generated candidate claim through the real plan→PDF→QA→approval→export boundary. Fix any escapes in scope/revision/typed-number handling. Ensure no logs or CI artifacts leak private payloads. Verify unknown/revoked facts and malicious JD/text inputs cannot reach export.

## Tests required

A04, A06–A08, A27, A29, A34: cross-employer numeric transplant, % vs points, spelled-out numbers, negation, leadership inflation, technology/expertise invention, stale review, export tampering and renderer exfiltration payloads.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No replacing failures with a warning, deleting negative tests, LLM “truth” scoring, broad refactor or changing root evidence without applicant review.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/019-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
