# Handoff to an independent reviewer

Use this prompt in a separate coding-agent session. Review the exact
TASK-008 implementation commit below; do not approve it as the implementer.

```text
Independently review TASK-008 in this repository.

TASK-007 approved merge/base: a83324f9afcef143ef264c554c5d4e7764d1e8bd
TASK-008 implementation: d53276b8357846774e5147bd13448af23b73cc5d
Branch: task/008-snapshots-export

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md,
docs/IMPLEMENTATION_PLAN.md, docs/ACCEPTANCE_CRITERIA.md,
docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md, docs/tasks/TASK-008.md,
ADR-002, ADR-011, ADR-012, ADR-015, relevant research sections in
SOURCE_REGISTER.md, and docs/REVIEW_PROTOCOL.md.

Inspect the complete diff from the TASK-007 approved merge to the exact
TASK-008 head. Run the locked checks independently:

  /Users/apple/.local/bin/uv sync --locked
  /Users/apple/.local/bin/uv run python --version
  /Users/apple/.local/bin/uv run pytest -vv --durations=0 --junitxml=artifacts/verification/task-008/review-junit.xml
  /Users/apple/.local/bin/uv run ruff check .
  /Users/apple/.local/bin/uv run ruff format --check .
  /Users/apple/.local/bin/uv run mypy src
  /Users/apple/.local/bin/uv run python tests/reproduce_task008.py

Focus on atomic same-filesystem staging and publication, owner-marked staging
cleanup, no-overwrite IDs, complete source slice/capture/review/plan/PDF/TXT/QA
/config/tool files, manifest hashes without self-reference, restore verification,
and rejection of modified PDF/TXT/plan/manifest/capture bytes. Confirm failed or
interrupted builds never publish ready snapshots and historical snapshots remain.

Confirm final approval is a distinct explicit local-human record bound to exact
manifest/PDF/TXT digests, reviewer and timezone-aware time. Confirm export
revalidates the current trusted profile, exact fact/variant revisions and local
reviews, support capture hashes/status/availability, current profile and plan
digests, mandatory QA and attributed visual review, and explicit expiry using
current time rather than a backdated plan as-of. Check corrected, superseded,
revoked, deleted and unavailable support; an external-original deletion with
an intact capture must remain usable. Exercise concurrent profile-loader
revision conflicts and unauthorized/missing approvals.

Run or inspect the synthetic A28–A29 tests for all of those mutations. Confirm
export copies only the verified approved PDF/TXT bytes, refuses an existing
destination, does not mutate snapshots, and has no SQLite, signing, browser,
identity-document, history-deletion or TASK-009 work. Confirm no dependency or
lockfile change was introduced and no applicant data or credentials are present.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-008.md report with exact reviewed commit IDs and
measured results. For each blocking finding provide a narrow reproduction,
affected modules, acceptance criteria and regression tests. Update PROGRESS
with the actual review state. Do not modify implementation, merge, force-push,
or self-approve.
```
