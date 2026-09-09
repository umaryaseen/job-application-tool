# TASK-026: Import optional versioned ESCO data

- Milestone: M5
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h plus official data acquisition; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-016](TASK-016.md)
- Decisions: [ADR-006](../adr/ADR-006.md), [ADR-010](../adr/ADR-010.md), [ADR-015](../adr/ADR-015.md)

## Objective

Import optional versioned ESCO data.

## Background

ESCO can improve cross-language normalization, but the reference-only local API should not become runtime infrastructure.

## Affected modules

normalization/esco.py; docs/data/ESCO.md; tests/test_esco_import.py. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Accept an officially acquired pinned EN/DE data snapshot, verify schema/hash/version, record attribution/reuse conditions, map optional URIs without changing internal IDs. Preserve equivalent/broader/narrower/related relations. Missing dataset leaves baseline working. Ask only if official acquisition requires applicant interaction.

## Tests required

A39: small synthetic/excerpt fixture with valid reuse; hash/version mismatch, unsupported format, typed relations, offline cache and no skill invention.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No ESCO API server, full taxonomy download from guessed URLs, automatic email disclosure, mandatory network, or treating broad concepts as direct skill proof.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/026-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
