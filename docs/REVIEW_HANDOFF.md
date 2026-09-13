# Handoff to an independent reviewer

Use this prompt in a separate coding-agent session. Review the exact
TASK-007 implementation commit below; do not approve it as the implementer.

```text
Independently review TASK-007 in this repository.

TASK-006 approved merge/base: d04d4dfe247958c175e66df5ab64f228d206246a
TASK-007 implementation: 72daba1beb691e81f068825ae032c36a43da367e
Branch: task/007-pdf-ats-qa

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md,
docs/IMPLEMENTATION_PLAN.md, docs/ACCEPTANCE_CRITERIA.md,
docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md, docs/tasks/TASK-007.md,
ADR-004, ADR-011, ADR-013, ADR-015, relevant research sections in
SOURCE_REGISTER.md, and docs/REVIEW_PROTOCOL.md.

Inspect the complete diff from the TASK-006 approved merge to the exact
TASK-007 head, including expected JSON fixtures, the bounded pypdf worker,
Poppler subprocesses, machine-readable report contract and tests. Run:

  /Users/apple/.local/bin/uv sync --locked
  /Users/apple/.local/bin/uv run python --version
  /Users/apple/.local/bin/uv run pytest
  /Users/apple/.local/bin/uv run ruff check .
  /Users/apple/.local/bin/uv run ruff format --check .
  /Users/apple/.local/bin/uv run mypy src
  /Users/apple/.local/bin/uv run python tests/rendering/reproduce_task007.py

Inspect both generated reports and every raster page under the ignored
artifacts/qa/task-007-<UTC>/ directory. Confirm report checks include
check_id, pass/fail/warn/not_checked, measured and expected/threshold values,
tool/version, exact PDF SHA-256 and bounded diagnostics. Confirm independent
Poppler and pypdf complete ordered text expectations; correct section, entry
and critical-field scopes; standard headings; Unicode and quantitative
punctuation; actual page count, A4 media/crop/rotation, file size and
geometry; and raster generation separate from attributed visual review.

Exercise the real synthetic negative PDFs for wrong order with the same words,
hidden/nonpainting text, clipping, duplicate/missing/suffix/qualification/date/
numeric/unexpected content, image-only/empty content, overflow and invalid
page dimensions. Confirm failures come from actual PDF bytes and that missing
tools or failed subprocesses are not passes. Confirm empty token denominators
are null and overall mandatory not_checked results cannot pass.

Check the narrow normalization is exactly the reviewed TASK-005 policy and
preserves numbers, units, punctuation, negation and qualifiers. Confirm the
pypdf subprocess is bounded and network-denied, reports do not contain full
candidate text, and visibility checks state their explicit limits. Confirm
there is no universal hidden-text detector claim, employer ATS score, OCR,
commercial parser, online upload, second renderer, final approval/export
workflow, or TASK-008 work. Confirm pypdf's unchanged 6.18.1 pin is accurately
recorded as a TASK-007 runtime QA dependency while historical TASK-002 records
remain intact.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-007.md report with exact reviewed commit IDs and
measured results. For every blocking finding provide a narrow reproduction,
affected modules, acceptance criteria and regression tests. Update PROGRESS
with the actual review state. Do not modify implementation, merge, force-push,
or self-approve.
```
