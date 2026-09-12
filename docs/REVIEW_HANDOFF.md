# Handoff to an independent reviewer

Use this prompt in a **separate** coding-agent session. Review the exact
TASK-006 implementation below; do not approve it as the implementer.

```text
Independently review TASK-006 in this repository.

TASK-005 approved implementation: 62eddb346995c8ef7ade694d45775779f5017c36
TASK-005 accepted ADR-004 amendment: 1638bec9a3c334f0491625368e1a2ab208a19ce1
TASK-005 merge/base: 75b8b1f7b37ed62f51ec833e7f7e0ce50143cc10
TASK-006 implementation head: 452edbe21f94a844b04d080ed7549e216c13e42f
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

## TASK-006 corrective re-review

Use this prompt in a separate coding-agent session to review only the two
corrections below. Preserve the original `docs/reviews/TASK-006.md` finding.

```text
Independently re-review the TASK-006 corrections in this repository.

Original reviewed implementation: 452edbe21f94a844b04d080ed7549e216c13e42f
Original review: 2feccf0032268ed3918310f5865e4fb63f60fa39
Correction commit: 8f8181fd88925c1bc33e6800576c938f3f9857e1
Branch: task/006-pdf-adapter

Read AGENTS.md, docs/reviews/TASK-006.md, docs/tasks/TASK-006.md,
docs/DEPENDENCIES.md, docs/PROGRESS.md and the complete correction diff.
Confirm no dependency or lockfile changed and no unrelated implementation was
introduced.

F-001: verify the current dependency register names Pydantic 2.12.5, while the
historical TASK-002 Pydantic 2.11.7 row is explicitly marked superseded. Verify
the installed RenderCV 2.8 metadata constraint `pydantic[email]>=2.12.5` and
the locked project graph. Confirm historical records remain intact.

F-002: inspect and run
`tests/test_rendering.py::test_production_pdf_handles_long_two_page_plan_without_pruning`.
Confirm the same freshly generated two-page PDF is independently extracted by
Poppler and pypdf, and both are compared with the same expected plan using the
existing narrow normalization. Confirm the page-count assertion remains and
the existing complete-content negative controls reject suffix loss,
qualification changes, duplication, reordering and unexpected content. Do not
accept a prefix check, one extractor as the other's oracle, fallback behavior,
or broadened normalization.

Run `/Users/apple/.local/bin/uv sync --locked`, Python 3.12, full pytest, Ruff,
format and mypy. Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED
in docs/reviews/TASK-006-correction.md with exact commit IDs and update
PROGRESS. Do not modify implementation, merge, push or self-approve.
```
