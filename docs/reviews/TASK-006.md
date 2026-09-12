# TASK-006 Independent Review

Reviewer: Codex (independent reviewer)
Date: 2026-09-13
Base: `75b8b1f7b37ed62f51ec833e7f7e0ce50143cc10`
Implementation: `452edbe21f94a844b04d080ed7549e216c13e42f`
Documentation head: `b6c73204a052ce860eca573a8a2ca778815b9f29`

## Verdict

**CHANGES REQUIRED**

The implementation head is an exact descendant of the base. The implementation-to-documentation delta contains only `docs/PROGRESS.md` and `docs/REVIEW_HANDOFF.md`. The production adapter, CLI, tests, dependency change, and staging/isolation behavior were inspected.

### F-001 — dependency documentation contains a stale Pydantic version (blocking documentation correction)

`docs/DEPENDENCIES.md` still lists Pydantic 2.11.7 in the locked-version table while `pyproject.toml` and `uv.lock` use 2.12.5 (required by RenderCV 2.8). Correct the table and add the exact compatibility rationale/version evidence consistently. Acceptance: no conflicting locked runtime version appears in dependency documentation; dependency and schema checks remain passing.

### F-002 — two-page production path lacks independent pypdf assertion (blocking acceptance gap)

`tests/test_rendering.py::test_production_pdf_handles_long_two_page_plan_without_pruning` compares the two-page PDF only with Poppler. The pypdf comparison is present for the short and hostile cases, but the requested short and two-page production outputs must each be compared with both extractors. Add the pypdf complete-content assertion to the two-page test (and retain the existing Poppler assertion). Acceptance: a fresh two-page `jae build-cv`/adapter output passes complete normalized extraction in both Poppler and pypdf; a suffix/field mutation fails.

## Verification

`/Users/apple/.local/bin/uv sync --locked` passed; Python 3.12.14; `uv run pytest` passed **38 tests**; Ruff check and format passed; mypy passed with no issues in 23 source files. CLI help and invalid-usage checks were run (`jae --help`, `jae build-cv --help`, missing-input invocation exit 2). Production tests exercised tampered-plan rejection before staging, network-isolation fail-closed behavior, timeout/failure cleanup, hostile literal text, Unicode, and two-page Poppler output. The adapter uses macOS `sandbox-exec` around the worker, bounded timeout/output, fixed local template/font paths, and escaped Typst string insertion; pypdf remains dev-only as documented. No implementation changes were made. A fresh CLI build with serialized profile/plan/review fixtures was not separately scripted because the production test path invokes the same `build_pdf` entry point and the CLI requires generated review JSON; this is recorded as a limitation, not treated as additional acceptance.
