# TASK-030: Add JSON Resume interchange with loss reporting

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-020](TASK-020.md)
- Decisions: [ADR-001](../adr/ADR-001.md), [ADR-010](../adr/ADR-010.md), [ADR-011](../adr/ADR-011.md)

## Objective

Add JSON Resume interchange with loss reporting.

## Background

External compatibility is valuable, but external resume schemas cannot carry all provenance and review state.

## Affected modules

profile/json_resume.py; schemas/vendor/; docs/INTERCHANGE.md; tests/test_interchange.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Pin current upstream schema revision/license. Export chosen public fields from approved canonical data with a loss report. Import to a separate unverified draft with provenance of imported file and explicit missing-evidence questions. Never overwrite approved canonical profile or import approval flags.

## Tests required

Schema conformance, missing fields, unknown extensions, lost localization/evidence report and import remains unverified; show intentional non-round-trip fields.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No JSON Resume registry publication, personal data in Git, universal lossless compatibility, npm runtime for a trivial export or making interchange the database.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/030-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
