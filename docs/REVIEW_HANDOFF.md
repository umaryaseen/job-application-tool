# Handoff to an independent reviewer

Use this in a **separate** coding-agent session after an implementation task has committed. Fill the task and commit IDs from Git, not memory.

```text
Independently review TASK-001 in this repository.
Base commit: 8939d9e8ec5af2035ca6b5a86c94ae74efedbabb
Implementation head: run `git rev-parse HEAD` in this checkout and review that exact commit.

Read AGENTS.md, docs/ARCHITECTURE.md, docs/IMPLEMENTATION_PLAN.md,
docs/ACCEPTANCE_CRITERIA.md, docs/SECURITY_AND_PRIVACY.md,
docs/PROGRESS.md, docs/tasks/TASK-001.md, relevant ADRs and research
sections identified in docs/SOURCE_REGISTER.md.

Follow docs/REVIEW_PROTOCOL.md. Inspect the full diff, code, tests,
dependencies, actual outputs and security boundaries. Run the relevant
checks independently. Do not trust an implementer's test summary alone.
Do not rewrite implementation while claiming to be its independent reviewer.

Pay particular attention to real-but-unrelated evidence IDs, scope and
numeric changes, stale approvals, unknown dates/languages/authorization,
renderer injection and private data in staged files/CI.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a
sanitized docs/reviews/TASK-001.md report with exact reviewed commit IDs.
For each blocking finding provide a narrowly scoped corrective task with
reproduction, affected modules, acceptance and tests. Update PROGRESS
with the actual review state. Do not merge or force-push.
```
