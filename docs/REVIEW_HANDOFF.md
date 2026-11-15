# Review handoff: TASK-016 matrix fixture oracle (before implementation)

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `deee9aa`. Branch: `task/016-evidence-matrix`. TASK-012 to TASK-015
are merged.

Review only the synthetic oracle `tests/fixtures/matrix/matrix.json` and its
rules `tests/fixtures/matrix/README.md`, written before any matrix code. Check
them against TASK-016, A22, A24, ADR-005/006/007/011, ARCHITECTURE ("Matching
and tailoring"), the merged TASK-012 classifier, TASK-013 aliases and relations,
TASK-014 review gates and TASK-015 constraints (run them to confirm the draft
structures the cases depend on): that every expected row state, reason,
priority, fact list, duplicate link, exclusion and coverage count follows from
the written rules; that unrelated, adjacent, exposure, self-study and
responsibility evidence never satisfies a requirement; that unknown and
explicitly unmet stay distinct; that mandatory gaps stay visible and preferred
results cannot hide them; that groups and duplicates count once and empty
classes are N/A; and that rule gaps or ambiguities are named. Record findings
and one verdict in `docs/reviews/TASK-016-FIXTURES.md` without editing the
fixture.
