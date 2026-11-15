# Review handoff: TASK-016 matrix fixture oracle, round 2 (before implementation)

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `deee9aa`. Branch: `task/016-evidence-matrix`.

Round 1 ([report](reviews/TASK-016-FIXTURES.md)) confirmed the row arithmetic
and returned CHANGES REQUIRED. The revision: expected rows now carry a method
code, exact fact and evidence references with revisions, and every part
(F-01); each case has an expected snapshot of literal versions, with digests
required to equal the loaded profile and replayed review (F-02); an ALL group
with a satisfied and a missing child (F-03); exposure and self-study are
checked first and stay adjacent whatever the surface, with an alias-spelled
case (F-04); review actions are keyed by quote and occurrence, and the repeated
row now differs in review state (F-05); and cases for `term_not_a_language`,
`duration_scope_unrecognized`, `threshold_scope_unclear` and `ambiguous_term`
(F-06). Review the revised `tests/fixtures/matrix/README.md` and
`matrix.json` against the same sources, recompute every expected value
independently and record round 2 in `docs/reviews/TASK-016-FIXTURES.md`
without editing the fixture.
