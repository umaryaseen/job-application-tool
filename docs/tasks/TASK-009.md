# TASK-009: Curate and accept the first genuine baseline CV

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 2–4 h plus applicant review; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-008](TASK-008.md)
- Decisions: [ADR-011](../adr/ADR-011.md), [ADR-012](../adr/ADR-012.md), [ADR-013](../adr/ADR-013.md), [ADR-014](../adr/ADR-014.md), [ADR-015](../adr/ADR-015.md)

## Objective

Curate and accept the first genuine baseline CV.

## Background

Synthetic fixtures cannot satisfy the user’s first major milestone. A real profile must be manually sourced and reviewed. This task requires applicant input that is not in the three research reports.

## Affected modules

docs/PROFILE_CURATION.md; private JAE_DATA_DIR only; docs/reviews/M1.md; PROGRESS.md. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Use the curation checklist to collect current contact/history/education/skills/languages and approved bullets. Record attestation/evidence IDs, resolve unknowns and keep personal files outside Git. Generate a genuine EN baseline, run all M1 tests, inspect actual PDF pages and extracted text, then record applicant approval of exact bytes. Commit only sanitized process/review outcome.

## Tests required

A30 plus all implemented M1 regressions, lint/types and independent implementation review. Do not put private hashes/details into public test artifacts; local review can refer to an opaque private snapshot ID.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No importing chat memory as approved data, invented months/metrics/authorization, JD matching, cosmetic third-page workaround or M1 completion based only on synthetic data. If applicant data is missing, leave M1 awaiting applicant input.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/009-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
