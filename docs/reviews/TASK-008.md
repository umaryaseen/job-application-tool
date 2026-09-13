# TASK-008 Independent Review

Reviewer: Codex (independent reviewer)
Date: 2026-09-13
Base: `a83324f9afcef143ef264c554c5d4e7764d1e8bd`
Initial implementation: `d53276b8357846774e5147bd13448af23b73cc5d`
Corrected implementation: `c0c25f81baca6bf34822aea58a56340000c15ce6`
Documentation head: `ff66a8617a9e9884efdff44023570e7c3081ba40`

## Verdict

**CHANGES REQUIRED**

The corrected implementation is an exact ancestor of the documentation head, and the tail after `c0c25f8` is documentation-only (`docs/PROGRESS.md`, `docs/REVIEW_HANDOFF.md`). Snapshot integrity, atomic staging/owned cleanup, exact hashes, current eligibility/expiry checks, approval separation, and the corrective staged-byte recheck were inspected. The implementation is otherwise in scope.

### F-001 — required CLI workflow not independently exercised (blocking)

The requested real workflow requires `snapshot-build`, `snapshot-approve`, and `snapshot-export` through the implemented CLI. `tests/reproduce_task008.py` invokes `build_snapshot`, `approve_snapshot`, and `export_snapshot` APIs directly and does not invoke the CLI. No CLI snapshot workflow test was found. API success therefore does not verify CLI argument/path wiring or exit behavior.

Corrective task: execute the three commands in a fresh external synthetic `JAE_DATA_DIR`, or add focused CLI integration coverage using the existing synthetic inputs. Acceptance: each command succeeds with expected private paths and exits nonzero for stale/missing approval; output bytes and manifest hashes match the API workflow. Retain all existing integrity tests; do not alter implementation scope.

## Independent verification

- Commit identities, ancestry, clean state, and documentation-only tail: passed.
- `/Users/apple/.local/bin/uv sync --locked`: passed; Python 3.12.14.
- Persistent full `uv run pytest -q`: exit 0, **80 passed** (run completed in approximately 76 seconds).
- `/Users/apple/.local/bin/uv run python tests/reproduce_task008.py`: exit 0; synthetic API workflow produced matching manifest/approval digests and exact export bytes.
- Ruff check and format: passed (55 files formatted); mypy: passed, no issues in 35 source files.
- Schema/provenance/QA regressions and A28–A29 tamper/interruption/eligibility tests were included in the 80-test suite and passed.

TASK-009 was not started. Review documentation and PROGRESS were the only changes committed.

## Corrective CLI re-review

Date: 2026-09-13. Corrected implementation `045b1e598b5e47bd73b3838442d466fa50e40286`; documentation head `bd7c8185816d8cb4af6ce881948aa1bb81d38dba`; previous review `e7f1c8d`. Ancestry and clean state were verified; the tail is documentation-only.

F-001 is **resolved**. `cli._reviews` parses JSON through the duplicate-key rejecting loader, then validates receipts with Pydantic, including timezone-aware ISO datetimes; malformed and naive timestamps fail. Unknown fields, wrong types and nested duplicate keys remain rejected. Imported approval records are data only and cannot bypass local validation.

Independent `uv run pytest tests/test_snapshot_cli.py -q` passed (1 test), exercising the installed `jae` entry point, external private root, real build/approve/export commands, exact bytes, failed pre-approval/escape/existing/tampered cases and unrelated-file preservation. Full `uv run pytest -q` completed with **81 passed**. Locked sync, Python 3.12.14, Ruff check/format and mypy passed. No implementation or lockfile changes were made.

**Final verdict: APPROVED.** TASK-009 was not started.
