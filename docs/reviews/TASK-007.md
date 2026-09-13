# TASK-007 Independent Review

Reviewer: Codex (independent reviewer)
Date: 2026-09-13
Base: `d04d4dfe247958c175e66df5ab64f228d206246a`
Initial implementation: `72daba1beb691e81f068825ae032c36a43da367e`
Corrected implementation reviewed: `4437ff51c79cb93e3bd458dcfc910538dd045361`
Documentation head inspected: `5bcb43fe2087fc0ee0577312689e6f850e025746`

## Verdict

**CHANGES REQUIRED**

The complete base-to-corrected diff and scoped-field correction were inspected. The documentation delta from corrected implementation to `5bcb43f` is documentation-only (`docs/PROGRESS.md`, `docs/REVIEW_HANDOFF.md`). Scoped field checks now include employer/role/section in field identity and adversarial PDFs report the intended field-scope check failures. Report aggregation fails on mandatory failures and keeps absent visual review `not_checked`; hash-mismatched visual receipts are rejected and recording observation preserves automated failures. QA artifacts bind extraction, geometry and rasters to a PDF hash.

The implementation is otherwise aligned with the stated TASK-007 boundaries and synthetic fixtures.

## Blocking gate

The required full test suite did not complete within the available execution window: repeated independent runs progressed through the rendering tests but remained running, so no successful full-suite exit code can be recorded. This is an unresolved review gate under REVIEW_PROTOCOL. The focused collection was verified (56 tests), and Ruff check/format and mypy passed, but partial progress is not a pass.

Corrective task: rerun the full suite in a Python 3.12 locked environment to a completed exit code, preserving all assertions; record the exact result and ensure schema/provenance/rendering regressions pass. No implementation change is otherwise requested by this review.

## Verification

- Commit identities, ancestry and clean working-tree state: passed.
- `/Users/apple/.local/bin/uv sync --locked`: passed; Python 3.12.14.
- Full-suite `uv run pytest`: attempted independently but did not complete before the review window; no pass claim.
- `uv run pytest --collect-only -q`: passed; 56 tests collected.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: passed (48 files already formatted).
- `uv run mypy src`: passed with no issues in 30 source files.
- Raster/visual review and report semantics were inspected in implementation and fixture code; no visual acceptance is claimed without the completed suite.

TASK-008 was not started. Review documentation and progress were the only changes committed.
