# TASK-004: Compile the baseline document plan and text

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-003](TASK-003.md)
- Decisions: [ADR-003](../adr/ADR-003.md), [ADR-011](../adr/ADR-011.md), [ADR-013](../adr/ADR-013.md)

## Objective

Compile the baseline document plan and text.

## Background

All visible text must have an authorized origin before renderer selection. Compile a small typed plan independent of PDF APIs.

## Affected modules

domain/document.py; rendering/text.py; profile/baseline.py; verification/document.py; tests/test_document_plan.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Compile approved variants and typed fields into ordered standard sections. Bind contacts, professional label, employment dates, degrees and skills to claim nodes; static labels are allowlisted. Generate UTF-8 CV text from the same plan. Preserve chronology and date precision; require profile digest and as-of date. Reject arbitrary text/evidence pairs at publishing boundary.

## Tests required

A03, A05, A07: coverage of every visible candidate claim; chronology ties; optional section omission; no unknown→Present; plan text mutation fails; no unsupported headline or skill injection. Expected text defined independently of production traversal.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No PDF backend, auto-summary rewriting, matching, page optimization or invented default personal data.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/004-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
