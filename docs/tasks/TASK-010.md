# TASK-010: Ingest pasted job descriptions as immutable snapshots

- Milestone: M2
- State: APPROVED implementation on PR #2; not merged. [Independent review](../reviews/TASK-010.md) covers exact published implementation `ccad19062f3050fc69c799072bb0098f13123da7`; fresh macOS CI passed 112 tests plus lint/format/types. TASK-009 and overall M2 release remain pending.
- Estimate: 2–3 h; planning range, excludes unresolved human input and review waiting
- Dependencies: reviewed TASK-001/TASK-008 and integrated CLEANUP-001; [ADR-018](../adr/ADR-018.md) permits only draft intake before TASK-009 personal acceptance. TASK-009 and the overall M2 release gate remain pending.
- Decisions: [ADR-002](../adr/ADR-002.md), [ADR-007](../adr/ADR-007.md), [ADR-012](../adr/ADR-012.md), [ADR-015](../adr/ADR-015.md)

## Objective

Ingest pasted job descriptions as immutable snapshots.

## Background

Jobs are untrusted specifications and can change. Establish source identity before extraction.

## Affected modules

ingestion/text.py; domain/job.py; cli.py; tests/test_ingestion.py; tests/fixtures/jobs/. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Read UTF-8 file/stdin bounded to 200,000 bytes; store raw bytes/text/hash and normalized text/hash privately, explicit locale or unknown, source metadata supplied by user. Deduplicate identical content and create a new revision for changed text. Maintain raw codepoint offsets for downstream quotes.

## Tests required

A16: EN/DE/Unicode newlines, duplicate and changed input, malformed UTF-8, oversize, empty input, hostile instructions remain text, no network.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

No URL retrieval, HTML scraping, job discovery, cookies, source policies or automatic company research.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/010-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
