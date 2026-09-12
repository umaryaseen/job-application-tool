# Handoff to an independent reviewer

Use this prompt in a **separate** coding-agent session. Review the exact
TASK-006 implementation below; do not approve it as the implementer.

```text
Independently review TASK-006 in this repository.

TASK-005 approved implementation: 62eddb346995c8ef7ade694d45775779f5017c36
TASK-005 accepted ADR-004 amendment: 1638bec9a3c334f0491625368e1a2ab208a19ce1
TASK-005 merge/base: 75b8b1f7b37ed62f51ec833e7f7e0ce50143cc10
TASK-006 implementation head: 0b2d05464142c3bde31486b7a5fd14497089035c
Branch: task/006-pdf-adapter

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md,
docs/IMPLEMENTATION_PLAN.md, docs/ACCEPTANCE_CRITERIA.md,
docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md, docs/tasks/TASK-006.md,
docs/DEPENDENCIES.md, ADR-004, ADR-011, ADR-013, ADR-015,
docs/REVIEW_PROTOCOL.md and the relevant SOURCE_REGISTER sections. Inspect
the complete diff from the TASK-005 merge to the exact TASK-006 head,
including the trusted template, CLI boundary, lockfile and tests.

Run independently:
`/Users/apple/.local/bin/uv sync --locked`, Python 3.12, `uv run pytest`,
`uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`,
and the synthetic production renderer tests. Reproduce `jae build-cv` with
synthetic profile, DocumentPlan and local review receipt JSON. Inspect the
generated A4 PDF and raster preview and compare complete content with both
Poppler and pypdf.

Focus on the validated-plan/provenance boundary (a model or recomputed digest
alone must not authorize content), exact claims and typed formatting, private
staging and root validation, output/temp bounds and cleanup, timeout and worker
failure behavior, refusal to overwrite, literal Typst insertion, hostile
markup/file/remote references, local package/font/template pinning and the
macOS sandbox-exec `(deny network*)` process chain. Confirm missing isolation
fails closed and no Playwright fallback, arbitrary template, remote font,
DOCX, UI, matching, export workflow or TASK-007 work was added.

Confirm RenderCV 2.8, Typst 0.15.0, rendercv-fonts 0.5.1, Pydantic 2.12.5
and pypdf 6.18.1 are documented and locked, with the Pydantic upgrade
explained by RenderCV's requirement. Confirm the current-laptop macOS support
scope is explicit and no cross-platform or universal ATS claim is made.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-006.md report with exact reviewed commit IDs.
For each blocking finding provide a narrow reproduction, affected modules,
acceptance criteria and regression tests. Update PROGRESS with the actual
review state. Do not modify implementation, merge, force-push or self-approve.
```
