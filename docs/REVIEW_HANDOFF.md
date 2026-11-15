# Review handoff: TASK-015 scoped constraints and experience intervals

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `e88546e`. Branch: `task/015-constraints-durations`. TASK-014 is
merged.

Read AGENTS, PROGRESS, [the task](tasks/TASK-015.md) (including its
clarifications), A07/A22/A23, ADR-007, ADR-011, ARCHITECTURE (matching,
language, authorization, years), REVIEW_PROTOCOL, SECURITY_AND_PRIVACY,
[the guide](MATCHING.md) and the [fixture review](reviews/TASK-015-FIXTURES.md).

The oracle `tests/fixtures/matching/` was reviewed before implementation
(round 2 APPROVED WITH FOLLOW-UP); follow-ups F-01..F-03 were added afterwards
in their own commit and must be checked here: authorization statement-date
precision (`statement_date_precision`, month/year cases), the months-only
duration API with `months_from_threshold`, and the as-of intersection for known
ends (non-last-day case). Focus: that the evaluator implements exactly the
README rules; no inference of language level, authorization, seniority or FTE;
duration bounds, unions, exclusions and cutoffs (including day-level starts,
extreme years and many intervals); multi-fact precedence and `fact_ids`;
expiry in UTC; validation of the profile before evaluation; and that unknown
data is never turned into a negative. Record findings and one verdict in
`docs/reviews/TASK-015.md` without modifying implementation.
