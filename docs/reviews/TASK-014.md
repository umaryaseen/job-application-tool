# TASK-014 independent implementation review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, sandbox `workspace-write` on a throwaway detached checkout of
  `18bd782` plus a dedicated temporary directory, no network, session
  `01a1dfc3-8de6-76d0-a243-5a4ad6150fc5`. Tracked files unchanged; exit 0.
- Hosted CI on `18bd782`: run `43728454796` success (the reviewer did not query it).
- The report below is verbatim.

## Round 1 report

VERDICT: CHANGES REQUIRED

# TASK-014 independent implementation review

Reviewer: Codex, independent implementation reviewer; the implementation was not authored by this reviewer
Date: 2026-11-15
Base: `01f3a403ea3a3efa045b97e35401700f4ab2de1e` (`main`)
Candidate: `18bd7824d364aa5634fac638fda485e8798a125e`
Candidate tree: `edd0c9147d24c2a353cff01160e5054ee2f34ec5`
Checkout: detached candidate; tracked files remained unchanged during review.
Scope: TASK-014, A20, ADR-007, ADR-012, the requirement-review implementation and tests, related source-bound extraction, private-path and replay behavior. All probe data was synthetic and stored under the permitted `codex-014-tmp` root. No network or private applicant data was used.
Artifacts inspected: `AGENTS.md`, `docs/REVIEW_HANDOFF.md`, `docs/REVIEW_PROTOCOL.md`, `docs/PROGRESS.md`, `docs/tasks/TASK-014.md`, A20 in `docs/ACCEPTANCE_CRITERIA.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/APPLICATION_WORKFLOW.md`, ADR-007, ADR-012, `docs/SECURITY_AND_PRIVACY.md`, `docs/JOB_EXTRACTION.md`, the complete base-to-candidate diff, changed source modules and `tests/test_requirement_review.py`.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Clean detached candidate (`HEAD (no branch)`). |
| `git rev-parse HEAD HEAD^{tree} 01f3a403ea3a3efa045b97e35401700f4ab2de1e 18bd7824d364aa5634fac638fda485e8798a125e` | 0 | Candidate, tree, base and candidate IDs matched the handoff. |
| `git diff 01f3a403ea3a3efa045b97e35401700f4ab2de1e..18bd7824d364aa5634fac638fda485e8798a125e` (complete diff inspection) | 0 | 9 paths; 1,514 insertions and 27 deletions. |
| `.venv/bin/python -m pytest tests/test_requirement_review.py tests/test_requirement_classification.py tests/test_requirement_spans.py tests/test_skill_normalization.py -ra -p no:cacheprovider --basetemp=/private/tmp/.../codex-014-tmp/pytest` | 0 | **476 passed**, 0 failed, 0 skipped. |
| `.venv/bin/python -m pytest -ra -p no:cacheprovider --basetemp=/private/tmp/.../codex-014-tmp/pytest-full` | 1 | **623 passed, 28 failed, 0 skipped** in 78.76s. Twenty-seven failures are renderer/ATS-QA or renderer-dependent tests in `tests/rendering/test_pdf_qa.py` (10), `tests/test_m1_fix.py` (2), `tests/test_m1_fix004.py` (5), `tests/test_m1_fix006.py` (1), `tests/test_m1_fix007.py` (3), and `tests/test_rendering.py` (6). The production renderer failures reach worker exit 71 because nested macOS `sandbox-exec` cannot apply in this checkout; `sandbox-exec -p '(version 1) (allow default) (deny network*)' true` independently returned 71 (`sandbox_apply: Operation not permitted`). Hosted macOS CI is the appropriate gate for those tests and was not queried. The remaining failure is `tests/test_snapshot_cli.py::test_snapshot_cli_workflow_and_negative_cases`, which fails while validating an existing synthetic profile fixture with extra fields; it is outside the TASK-014 diff. |
| `sandbox-exec -p '(version 1) (allow default) (deny network*)' true` | 71 | Nested sandbox application is not permitted in this checkout (`sandbox_apply: Operation not permitted`). |
| `.venv/bin/ruff check --no-cache .` | 0 | All checks passed. |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 87 files already formatted. |
| `.venv/bin/mypy src --cache-dir=/private/tmp/.../codex-014-tmp/mypy` | 0 | No issues in 53 source files. |
| `git diff --check 01f3a403ea3a3efa045b97e35401700f4ab2de1e..18bd7824d364aa5634fac638fda485e8798a125e` | 0 | No whitespace errors. |
| `probe_spans.py` | 0 | Wrong quote, shifted, outside-clause and out-of-range spans rejected; overlapping/misordered children, outside connectives and excessive depth rejected; CRLF, combining/astral Unicode offsets accepted; raw bytes unchanged. |
| `probe_terms.py` | 0 | A nested condition with 129 leaves was rejected with the bounded term-limit error. |
| `probe_gates.py` | 0 | Explicit correction plus accept made a structured mandatory row a hard gate; negated rows stayed `not_required`; non-requirement and marker rows did not gate unless explicitly changed/accepted under the declared operation rules. |
| `probe_replay.py` | 0 | Symlinked and unexpected revision entries were rejected; `.review-*` temporary entries were tolerated as documented interrupted-write debris; a metadata-only re-sign of a `reopen` revision was accepted (F-02). |
| `probe_missing_tail.py` | 0 | Deleting the only revision or the newest tail revision returned a valid truncated/draft view instead of failing (F-01). |
| `probe_input_cli.py` | 0 | Outside-root, symlink, duplicate-key, oversized and invalid-UTF-8 correction inputs were rejected with bounded errors; no posting text leaked. |
| `probe_combining.py` | 0 | A correction quoting a decomposed combining-mark span was accepted and replayed; raw CRLF/Unicode source remained unchanged. |
| `probe_time.py` | 0 | An aware `+02:00` reviewer timestamp was accepted and persisted rather than normalized/rejected as UTC (F-03); naive time was rejected. |
| `probe_real_cli.py` | 0 | Real CLI ingest/review/apply succeeded with exit 0; replaying the same stale correction returned exit 2 and a sanitized reload message. |

The report-writing probes and temporary files are outside the checkout. No tracked file was edited.

## What was verified

The deterministic classification is recomputed from the verified raw revision before replay. Corrections bind the job ID/revision, record digest, raw digest, classification digest in stored revisions, base review revision, base view digest and resulting view digest. Exact quote/offset checks use the raw decoded source and enforce clause containment; condition children are ordered and bounded, group connectives are contained, and condition depth/term counts are capped. Combining marks, astral characters and CRLF code-point offsets round-trip. Accept requires the displayed review-reason list exactly, including order and cardinality; edits return rows to draft. Priority markers are restricted to accept/reopen. Negation and duplicate observations cannot be edited. Only a reviewed, unnegated, structured, mandatory requirement row is reported as a hard gate; explicit correction is required before an ambiguous or unstructured row can acquire that state, and negated rows remained non-gating in the probes. Exclusive hard-link publication prevents two writers from publishing the same revision number. Raw posting files were never modified by correction application.

Replay rejected ordinary edited records, re-signed records whose resulting view changed, reordered/gapped/extra entries, symlinked entries, changed raw source, and a re-signed classification digest that no longer matched current deterministic rules. Temporary `.review-*` files are intentionally ignored as interrupted-write debris, consistent with the implementation comment and handoff.

## Findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-01 | **Blocking** | `src/job_application_engine/snapshots/requirements.py:104-123,195-197` | Review replay cannot detect deletion of the only revision or a missing newest tail. `_revision_files` treats an absent/empty folder as a legitimate zero-revision history and validates only the numeric files that remain. This silently erases a previously accepted correction (or rolls the view back to an older revision), contrary to the immutable review/replay contract and the handoff requirement that missing files fail. Interior gaps are detected, but tail loss is not. | Synthetic `Requirements\n- Python is required.\n- Docker.\n`: accept `v000001.json`, unlink it, then `load_review(...)` returns `review_revision == 0` and all rows `draft`; with `v000001.json` and `v000002.json`, unlink `v000002.json` and `load_review(...)` returns revision 1 with the earlier hard gate. No exception is raised. Add a durable expected head/count (or equivalent append-only history anchor) and fail closed on a missing tail/empty history after a published review. |
| F-02 | **Medium** | `src/job_application_engine/snapshots/requirements.py:137-192`; `src/job_application_engine/extraction/review.py:87-110` | A stored revision can be edited and re-signed without replay detecting changes to audit metadata that do not affect the resulting view. The revision checksum is recomputed from the modified record, while `result_view_digest` excludes reviewer/time and the `reopen` operation leaves no reviewer in the row. This contradicts the documented claim that a re-signed record fails and weakens the reviewer/time provenance of immutable revisions. | Apply a `reopen` correction with reviewer `reviewer-a`, change the stored record’s `reviewer_id` to `reviewer-z`, recompute `revision_digest`, and load the review: it succeeds and reports `reviewer-z`. The view digest also excludes the timestamp field, so equivalent metadata-only timestamp edits are not represented in the result view. Bind the audit metadata to a durable chain anchor/manifest or otherwise make replay compare it with an independently committed identity. |
| F-03 | **Low** | `src/job_application_engine/domain/requirement_review.py:122-127` | The revision model requires an aware timestamp but does not require UTC or normalize offsets. The implementation guide says each stored correction records UTC time; direct use of `apply_correction` can persist a non-UTC offset. The CLI happens to pass `datetime.now(UTC)`, but the library boundary does not enforce the documented invariant. | `apply_correction(..., reviewed_at=datetime(2026, 11, 15, 12, tzinfo=timezone(timedelta(hours=2))))` succeeds and stores `+02:00`. Reject non-UTC offsets or normalize to UTC before hashing/storing, and retain a regression test. |

The renderer failures are environmental limitations of this checkout, not TASK-014 findings. The full-suite snapshot CLI fixture failure is likewise outside the changed modules; it prevents claiming a green full suite here but does not exercise requirement review behavior.

## Required next gate

Fix F-01 and F-02, add regression tests for missing-tail/empty-history and metadata-only re-sign tampering, then rerun the focused suite, full suite in hosted renderer-capable CI, Ruff, format, mypy, diff check and the adversarial probes. Fix F-03 in the same narrow correction or record it as an explicit documented follow-up if the project intentionally treats the direct library API as offset-normalizing input. Return the corrected commit for independent review; this report does not approve the candidate.

## Round 2 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, sandbox `workspace-write` on a throwaway detached checkout of
  `5d034b9` plus a dedicated temporary directory, no network, session
  `01a1dfe2-1c85-7aa0-a182-70ddfc7d04c4`. Tracked files unchanged; exit 0.
- Hosted CI on `5d034b9`: run `43731564313` success (the reviewer did not query it).
- The report below is verbatim. F-04 and F-05 are addressed by the next commit
  for round 3.

## Round 2 report

VERDICT: CHANGES REQUIRED

# TASK-014 independent implementation review — round 2

- Reviewer: Codex, independent implementation reviewer in a separate session; implementation authored by Claude Code.
- Date: 2026-11-15
- Base: `18bd7824d364aa5634fac638fda485e8798a125e`; tree `edd0c9147d24c2a353cff01160e5054ee2f34ec5`
- Candidate: `5d034b9607648900dbb114596651e0dd8793f905`; tree `1dbc9f6e80983c989979c14a6bb661fd0eb729f3`
- Checkout: supplied detached checkout; tracked files remained unchanged during review.
- Scope: cumulative base-to-candidate TASK-014 delta, A20, ADR-007/012, review handoff, replay/head protocol, tests and related documentation. Synthetic data only; no network or private applicant data.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Clean detached candidate. |
| `git rev-parse HEAD HEAD^{tree} 18bd7824d364aa5634fac638fda485e8798a125e 18bd7824d364aa5634fac638fda485e8798a125e^{tree}` | 0 | IDs matched the supplied candidate and base. |
| `git diff --stat 18bd7824d364aa5634fac638fda485e8798a125e..5d034b9607648900dbb114596651e0dd8793f905` and `git diff --name-status ...` | 0 | 7 paths; 347 insertions and 29 deletions. Complete changed-file diff inspected; no dependency or lockfile change. |
| `.venv/bin/python -m pytest tests/test_requirement_review.py tests/test_requirement_classification.py -ra -p no:cacheprovider --basetemp=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-014-r2-tmp/pytest` | 0 | 298 passed, 0 failed, 0 skipped (44 review tests and 254 classification tests). |
| `PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -m pytest -ra -p no:cacheprovider --basetemp=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-014-r2-tmp/pytest-full` | 1 | 637 passed, 27 failed, 0 skipped. The 27 failures were renderer/ATS-QA tests: 10 in `tests/rendering/test_pdf_qa.py`, 2 in `tests/test_m1_fix.py`, 5 in `tests/test_m1_fix004.py`, 1 in `tests/test_m1_fix006.py`, 3 in `tests/test_m1_fix007.py`, and 6 in `tests/test_rendering.py`. Renderer workers and QA measurement subprocesses fail with nested `sandbox-exec` exit 71 in this checkout. |
| `sandbox-exec -p '(version 1) (allow default) (deny network*)' true` | 71 | `sandbox_apply: Operation not permitted`; confirms the renderer limitation. |
| `.venv/bin/python -m pytest tests/rendering/test_pdf_qa.py -ra -p no:cacheprovider --basetemp=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-014-r2-tmp/pytest-pdfqa` | 1 | 24 passed, 10 failed; failures report unavailable Poppler verification or measurement exit 71 from the same nested sandbox limitation. |
| `.venv/bin/ruff check --no-cache .` | 0 | All checks passed. |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 87 files already formatted. |
| `.venv/bin/mypy src --cache-dir=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-014-r2-tmp/mypy` | 0 | No issues in 53 source files. |
| `git diff --check 18bd7824d364aa5634fac638fda485e8798a125e..5d034b9607648900dbb114596651e0dd8793f905` | 0 | No whitespace errors. |
| `probe_crash_clean.py` | 0 | Crash after folder stage -> revision 0 draft; after link -> revision 1 replay; before head advance -> revision 1 replay; two unacknowledged links -> hard replay failure. |
| `probe_integrity_clean.py` | 0 | Head ahead, revision symlink, revision oversize and head oversize were rejected. Focused tests also rejected missing head, edited/re-signed head metadata and renamed head. |
| `probe_utc_clean.py` | 0 | Naive and non-UTC offset timestamps were rejected at the apply and stored-record model boundaries. |
| `probe_connective.py` | 0 | A corrected condition with a raw-mismatching connective span was rejected; corrected child/group spans remained source-bound. |
| `probe_lag_tail.py` | 0 | Valid crash-lag state had head 1 and files 1/2; deleting v2 was accepted as review revision 1. |
| `probe_lag_reopen.py` | 0 | A lagged v2 `reopen` removed a gate, but deleting v2 replayed revision 1 and restored the stale Python hard gate. |
| `probe_race_only.py` | 0 | Controlled concurrent writers left files v1/v2 with final head revision 1 after it had reached 2; writer B succeeded and slow writer A failed after publication with “stored requirement review does not reproduce its result.” |

The first focused-test invocation was accidentally overlapped with a second invocation using the same pytest base directory and ended with one temporary-directory setup error (297 passed); the single, clean invocation above is authoritative.

## Probes and assessment

The round-1 F-01/F-02/F-03 cases pass in the ordinary acknowledged state: deleting an acknowledged newest or only revision, deleting or editing the head, re-signing the last revision metadata, and naive/offset review times are rejected. A one-revision head lag is accepted and a next correction catches it up; a second unacknowledged publication fails closed. Static foreign entries, symlinks, oversize JSON, head-ahead state, duplicate correction keys, stale digests, changed source, invalid spans, and raw posting immutability were also exercised. Whole-review-folder deletion returns an all-draft view with no hard gates, as documented. The source-bound condition, role/acceptance, negation and hard-gate tests pass.

Two blocking integrity defects remain.

## Findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-04 | blocking | `src/job_application_engine/snapshots/requirements.py:247-255` | The one-revision crash-lag exception makes tail deletion indistinguishable from a valid shorter history. When head revision `n-1` points to its digest and files `v1..vn` exist, deleting `vn` leaves count `n-1` and the exact head digest expected by `_history`; replay accepts the rollback. The same occurs for the only revision when a crash leaves head 0 and v1, then v1 is deleted. This contradicts the documented “missing tail ... fails” guarantee and can restore a stale hard gate: in the probe, v1 accepted “Python is required.”, lagged v2 reopened it (zero gates), deleting v2 replayed v1 and returned the Python hard gate. | `probe_lag_tail.py`: before deletion, head=1, files v1/v2, replay revision=2; after unlinking v2, `load_review` returns revision 1. `probe_lag_reopen.py`: after unlinking lagged v2, `hard_gates` contains “Python is required.”. |
| F-05 | blocking | `src/job_application_engine/snapshots/requirements.py:303-314` | `_write_head` reads the current head, checks `current.review_revision >= target`, then later uses unconditional `os.replace`. Two writers can both read head 0; writer B publishes v2 and replaces head with 2, then slow writer A replaces it with stale head 1. The head moves backwards, violating the explicit monotonic-head requirement. A’s publication remains on disk but its post-publication verification fails because replay now includes B’s newer view, leaving a confusing failed writer and a deliberately lagging head. | `probe_race_only.py` pauses A after its head-1 read, lets B publish and acknowledge v2, then resumes A. Output: files `head.json,v000001.json,v000002.json`, final head revision 1, replay revision 2, writer B succeeds, writer A raises `ReviewError: stored requirement review does not reproduce its result`. |

The head, hash chain, replay, source binding, UTC validation, privacy path checks and hard-gate derivation otherwise match the reviewed requirements. The full-suite renderer failures are environmental in this checkout and require hosted renderer-capable CI; they do not exercise TASK-014 behavior.

## Required next gate

Fix F-04 with a durable, independent publication anchor or equivalent protocol that both preserves the allowed one-revision crash recovery and detects deletion of the newest/only revision from a lagged state. Fix F-05 by serializing or compare-and-swapping head advancement so a stale writer cannot replace a higher head. Add regression tests for both races and lagged-tail/only-file deletion, then rerun the focused suite, full hosted suite, Ruff, format, mypy, diff check and these probes. This review remains changes required until those invariants are demonstrated.
