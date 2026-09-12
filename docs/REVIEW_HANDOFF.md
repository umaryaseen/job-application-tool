# Handoff to an independent reviewer

Use this prompt in a **separate** coding-agent session. Review the exact
TASK-003 implementation commit below; do not approve it as the implementer.

```text
Independently review TASK-003 in this repository.

TASK-002 approved merge/base: 1874f1cc0e07ed45ca291969b67f759d94f5f328
TASK-002 implementation: 6cb81c04c139a18f571cc0f3dcc3281ee5ecf86a
TASK-003 implementation head: b4526561620f5f829fcb32477ca33d2558788f28
Branch: task/003-evidence-validation

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md,
docs/IMPLEMENTATION_PLAN.md, docs/ACCEPTANCE_CRITERIA.md,
docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md, docs/tasks/TASK-003.md,
ADR-001, ADR-011, ADR-012, relevant research sections in
SOURCE_REGISTER.md, and docs/REVIEW_PROTOCOL.md.

Inspect the complete diff from the TASK-002 approved merge to the TASK-003
head, including schema changes, tests, and staged-history safeguards. Run the
locked checks independently (`uv sync --locked`, Python 3.12, pytest, Ruff,
format, and mypy). Confirm no real applicant data, credentials, or provider
approval records are trusted as local review.

Focus on exact (id, revision) resolution; dangling, cyclic, revoked and stale
bindings; fact and variant subject/scope binding; immutable support-capture
hashes; pinned documentary/repository source identities; generated-output
rejection; exact displayed-content and revision-bound local review receipts;
and adversarial tests for unrelated IDs, wrong metrics/scopes, negation or
leadership inflation, and intervening edits. Confirm the implementation does
not claim deterministic schema/graph integrity proves the real-world truth of
arbitrary prose and does not start TASK-004 work.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-003.md report with exact reviewed commit IDs.
For each blocking finding provide a narrow reproduction, affected modules,
acceptance criteria, and regression tests. Update PROGRESS with the actual
review state. Do not modify implementation, merge, force-push, or self-approve.
```
