# Handoff to an independent reviewer

Use this prompt in a **separate** coding-agent session. Review the exact
TASK-004 implementation commit below; do not approve it as the implementer.

```text
Independently review TASK-004 in this repository.

TASK-003 approved merge/base: faacbc5323d44d0ca7350356347b60dfb62984d0
TASK-003 implementation: b4526561620f5f829fcb32477ca33d2558788f28
TASK-004 implementation head: d8427071d7cdaf145dcd9a5dc6c3a2fae43d5814
Branch: task/004-baseline-document

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md,
docs/IMPLEMENTATION_PLAN.md, docs/ACCEPTANCE_CRITERIA.md,
docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md, docs/tasks/TASK-004.md,
ADR-003, ADR-011, ADR-013, relevant research sections in
SOURCE_REGISTER.md, and docs/REVIEW_PROTOCOL.md.

Inspect the complete diff from the TASK-003 approved merge to the TASK-004
head, including the typed plan, text boundary, fixtures, and tests. Run the
locked checks independently (`uv sync --locked`, Python 3.12, pytest, Ruff,
format, and mypy), and inspect the generated synthetic UTF-8 example at
`tests/fixtures/documents/baseline.txt`.

Focus on ordered allowlisted sections; exact fact/variant revisions and
support bindings for every visible candidate claim; contacts, headline,
employment dates, degrees and skills; pinned profile digest and as-of date;
chronology and deterministic ties; date precision and unknown versus ongoing
ends; optional-section omission; UTF-8 output; stale profile and altered plan
rejection; and resistance to arbitrary headline/skill text or caller-supplied
approval flags. Confirm TASK-003 provenance validation is reused and no PDF,
renderer backend, automatic rewriting, matching, pagination, export workflow,
or TASK-005 work was introduced.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-004.md report with exact reviewed commit IDs.
For each blocking finding provide a narrow reproduction, affected modules,
acceptance criteria, and regression tests. Update PROGRESS with the actual
review state. Do not modify implementation, merge, force-push, or self-approve.
```
