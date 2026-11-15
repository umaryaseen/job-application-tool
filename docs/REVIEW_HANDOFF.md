# Review handoff: TASK-015 fixture oracle, round 2 (before implementation)

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `e88546e`. Branch: `task/015-constraints-durations`.

Round 1 ([report](reviews/TASK-015-FIXTURES.md)) confirmed every expected value
and returned CHANGES REQUIRED for coverage and rule gaps F-01..F-07. The
revision: the A22 split and the meaning of "numeric" are stated in the README
and in `docs/tasks/TASK-015.md`; as-of capping is defined as an intersection
that never moves a start, with a day-level `starts_after_as_of`; year-precision
contributors and period-less responsibility, skill (used/exposure/study) and
education facts are covered; `below_threshold_with_unknown_intervals` is
distinguished from `documented_below_threshold`; multi-fact precedence for
degree, language, credential and authorization is defined and tested; and
credential `awarded_on` is evaluated with its precision. 88 cases.

Review the revised `tests/fixtures/matching/README.md` and `constraints.json`
against the same sources, recompute every expected value independently, and
record findings and one verdict as round 2 in
`docs/reviews/TASK-015-FIXTURES.md` without editing the fixture.
