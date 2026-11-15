# Review handoff: TASK-014 requirement review and correction versions

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `01f3a40a`. Branch: `task/014-requirement-review`. TASK-012 and
TASK-013 (dependencies) are merged.

Read AGENTS, PROGRESS, [the task](tasks/TASK-014.md), A20 in
ACCEPTANCE_CRITERIA, ADR-007, ADR-012, REVIEW_PROTOCOL, SECURITY_AND_PRIVACY and
the new section of [JOB_EXTRACTION](JOB_EXTRACTION.md#review-and-correct-requirements).

Focus: that every corrected span is verified against the raw JD and confined to
its clause (and connectives to their group); that a row reaches `reviewed` only
through `accept` naming exactly its review reasons and any edit returns it to
draft; that only reviewed, unnegated, structured, mandatory rows are hard gates
(ambiguous, negated or unreviewed rows never are); binding of a correction to
JD revision, record/raw digests and the exact base view; immutable exclusive
publication and concurrent writers; replay (hash chain, result digests, gaps,
foreign or temporary files, re-signed tampering, time order, changed JD text or
rules output); newer JD revisions starting unreviewed; private, bounded,
duplicate-key-free correction input; sanitized errors; no raw posting change.
Record findings and one verdict in `docs/reviews/TASK-014.md` without modifying
implementation. Implementer full suite: 664 passed, no skips (after the round-1 correction).

## Round 2 request

Round 1 ([report](reviews/TASK-014.md)) returned CHANGES REQUIRED: F-01 missing
tail undetected, F-02 re-signed last-revision metadata undetected, F-03 non-UTC
times accepted. The correction adds `RequirementReviewHead` (`head.json`):
created atomically with the review folder, advanced after each publication and
never moved backwards; replay requires it to match the revision count and last
digest, tolerating only a one-revision lag after a crash. Review times must be
UTC. Whole-folder deletion is documented as undetectable and fail-safe (no
hard gates). Review the delta from `18bd782`.
