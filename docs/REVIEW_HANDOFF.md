# Handoff to an independent reviewer

Use this prompt in a **separate** coding-agent session. Review the exact
TASK-005 implementation commit below; do not approve it as the implementer.

```text
Independently review TASK-005 in this repository.

TASK-004 approved merge/base: 82deb141f84c59d86da78f68f06c4e35dfc339c0
TASK-005 implementation head: dcc30ea05e7d51adbd384fe700c57cf459922fd1
Branch: task/005-renderer-experiment

Resolve the full implementation hash and inspect the complete diff from the
TASK-004 approved merge to that exact head. Read AGENTS.md,
docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md, docs/IMPLEMENTATION_PLAN.md,
docs/ACCEPTANCE_CRITERIA.md, docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md,
docs/tasks/TASK-005.md, ADR-004, ADR-013, ADR-015, relevant research sections
in SOURCE_REGISTER.md, and docs/REVIEW_PROTOCOL.md.

Run the locked baseline checks and the isolated experiment independently:
`/Users/apple/.local/bin/uv sync --locked`, Python 3.12, pytest, Ruff,
format, mypy, `uv sync --project experiments/renderer --locked`, and the
reproduction commands in experiments/renderer/README.md. Inspect the
synthetic PDFs and every raster page under the ignored artifacts path when
reproducing. Confirm the report distinguishes the blocked Playwright Chromium
runtime on macOS 13 from a successful browser result.

Focus on identical validated DocumentPlans for RenderCV/Typst and HTML/CSS;
A4 dimensions, page counts, extraction/order, Unicode, wrapping and visual
inspection; exact pinned dependencies, local font/license recording; hostile
markup and sentinel handling; sandboxed/network-denied rendering; HTML
escaping and request aborts; and the one-page synthetic letter. Confirm no
real applicant data, credentials, authenticated browser profile, remote
resource, production renderer, UI, matching, export workflow, or TASK-006
work was introduced. Confirm the candidate text boundary prevents arbitrary
Typst/HTML markup and that limitations are recorded honestly.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-005.md report with exact reviewed commit IDs and
measured results. For each blocking finding provide a narrow reproduction,
affected modules, acceptance criteria, and regression tests. Update PROGRESS
with the actual review state. Do not modify implementation, merge,
force-push, or self-approve.
```
