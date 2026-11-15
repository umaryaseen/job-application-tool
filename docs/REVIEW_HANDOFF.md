# Review handoff: TASK-015 fixture oracle (before implementation)

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `e88546e`. Branch: `task/015-constraints-durations`. TASK-014 and
M1-FIX-008 are merged.

Review only the synthetic oracle `tests/fixtures/matching/constraints.json` and
its rules `tests/fixtures/matching/README.md`, written before any evaluator
code. Check them against TASK-015, A07, A22, A23, ADR-007/011 and ARCHITECTURE
("Matching and tailoring", "Years of experience", language and authorization):
that each expected state, rationale, fact list and month bound follows from the
written rules; that the rules never infer language levels (IELTS, native,
self-description), authorization (location, residence, nationality), seniority
or FTE, never sum overlapping intervals, and treat unknown dates and missing
authorization as uncertainty; that rule gaps or ambiguities are named; and
that the data is synthetic. Record findings and one verdict in
`docs/reviews/TASK-015-FIXTURES.md` without editing the fixture.
