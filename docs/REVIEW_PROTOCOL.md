# Independent implementation review protocol

## Reviewer independence

The implementer may test and self-check but cannot supply the independent verdict. Use a separate agent/session or another engineer with the full repository and specific base/head commits. If unavailable, deliver the reviewable commit and mark awaiting review. No fake second-agent role within the same implementation response.

The supervising engineer can amend the architecture under delegated authority only with an ADR trail and separate review for meaningful changes. Applicant fact/document approval remains a different human action.

## Inputs and inspection

Read AGENTS, ARCHITECTURE, IMPLEMENTATION_PLAN, ACCEPTANCE_CRITERIA, SECURITY_AND_PRIVACY, relevant task/ADRs, source sections and PROGRESS. Confirm reviewed commit IDs and inspect the full diff, affected code, lockfile changes, tests and fixtures. Check that PROGRESS describes actual state.

| Review dimension | Questions |
|---|---|
| Task scope | Are objective and all acceptance criteria met? Were non-goals respected? |
| Research/ADRs | Does behavior implement the explicit decisions? Did new evidence change an assumption without an ADR? |
| Factuality | Can unrelated evidence, stale approval, new text or cross-scope metrics pass? Are all visible candidate claims covered? |
| Correctness | Are error/unknown/negative cases represented? Are snapshots, dates, groups and numeric semantics correct? |
| Tests | Run relevant checks independently where possible. Do real renderer/model tests exist? Are expected fixtures independent from production logic? |
| Security | Secrets, PII, file paths, egress, renderer injection, CI permissions, dependency changes and deletion behavior |
| User result | Inspect actual PDF/text/QA for document milestones; synthetic success versus personal acceptance clearly distinguished |

Do not merge until the independent result covers the implementation head. If the head changes, review the new delta and rerun affected checks. Routine documentation corrections can receive a scoped review rather than a full runtime regression.

## Verdicts

- **APPROVED:** acceptance met; required tests/review completed; no unresolved blocking finding.
- **APPROVED WITH FOLLOW-UP:** safe to proceed; only bounded nonblocking findings, each with task/owner/gate. A broken provenance/export/security invariant cannot be nonblocking.
- **CHANGES REQUIRED:** incomplete acceptance, broken architecture/security, unverified required tests, or material correctness issue. Specify the smallest repair task and rerun instructions.

Record in `docs/reviews/<milestone-or-task>.md`: reviewer identity, date, base/head (or candidate tree identity for initial planning), artifacts inspected, exact commands/results, findings by severity, architecture/security/acceptance assessment, verdict, follow-up tasks and next gate. Avoid personal content or secrets in review reports.

## Narrow corrective task template

```text
Fix TASK-NNN review finding F-XX only.
Base/head reviewed: ...
Failure: exact behavior and reproducible sanitized input.
Affected modules: ...
Required change: ...
Acceptance: ...
Tests to retain/add/run: ...
Non-goals: no unrelated refactor or weakened assertions.
Update PROGRESS, make a new corrective commit, and return for independent review.
```

## Git progression

Use feature branches and normal commits. After approval, merge locally with a recorded merge commit or a reviewed PR; preserve meaningful history. No force push. GitHub PRs are preferred when authenticated; local base/head review is sufficient if remote access is unavailable. Do not open a PR containing applicant data. Keep main on the latest reviewed state.
