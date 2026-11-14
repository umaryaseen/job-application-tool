# TASK-009 / main merge — independent review

Verdict: **APPROVED WITH FOLLOW-UP**
Reviewer: Claude Code (Opus 5.5), separate review session; not the implementer.
Date: 2026-11-13. Scope: the merge candidate only. This review does not approve
applicant facts, private CV content, final artifacts or export.

## Candidate identity

| Item | Value |
| --- | --- |
| Branch | `task/009-personal-baseline` (merge in progress, uncommitted) |
| Parent 1 (local HEAD) | `d0f1436d20fb8cc959feca3e9d355856f17c76ff` |
| Parent 2 (MERGE_HEAD, main) | `0cc9119df20a2be974f8db41ed9869663493f800` |
| Merge base | `3c562fe1c3de0239a129fad10804abd375c1d38e` |
| Staged candidate tree (`git write-tree`) | `2794c6af04df5beb982561c0115eadde58196500` |

Index state: no unmerged entries, no unstaged tracked changes and no untracked
files before this review file was written. The tree was re-recorded after all
checks and is unchanged. This file is untracked and is not part of that tree.

## Inspection

I classified every path changed on either side against both parents:

- **Equal to local HEAD:** all local-only paths, including `schemas/profile.schema.json`,
  `verification/{support,document}.py`, `rendering/{presentation,text}.py`,
  `rendering/templates/baseline.yaml`, `snapshots/{store,export}.py`, `ats_qa/*`,
  `domain/fact.py`, `profile/*`, the M1 fixtures and the `test_m1_fix*` suites.
  The local ADR-017, ADR-018 and `reviews/ADR-018.md` conflicts resolved to the exact local bytes.
- **Equal to main:** CI workflow, `check_staged.py`, `setup_typst_packages.py`,
  `rendering/packages.py`, `domain/job.py`, `ingestion/*`, the JD fixtures,
  `test_ingestion.py`, `test_typst_packages.py` and `test_repository_policy.py`.
- **True merges (`cli.py`, `rendering/pdf.py`, `tests/test_rendering.py`):** I checked
  line by line that (candidate − main) equals (local − base) and that
  (candidate − local) equals (main − base). All three are an exact union. Nothing
  from either side was dropped or added.
  - `pdf.py`: keeps the local `EvidenceKey`/`present_plan` imports and
    `TEMPLATE_VERSION = "baseline-v3-presentation-m1-fix005-hyphen-compounds"`.
    It adds main's import, `prepare_typst_packages` staged into the private
    directory, `package_path`/`package_cache_path` pointing there, and the worker
    exit code 29 with its bounded diagnostic. Code 29 does not collide with the
    local worker codes 20–28. The network-deny sandbox profile is unchanged.
  - `cli.py`: local build/snapshot support-capture forwarding is intact; main's
    `job-ingest` and `job-show` commands are added.
- **Main documents edited only for renumbering:** main's ADR-017 and ADR-018 became
  ADR-019 and ADR-020. The only changes are the header, an alias note and one
  review link (`reviews/ADR-020.md`). All targeted references were updated.
  Every remaining `ADR-017`/`ADR-018` reference outside `history/` refers to the
  local meaning. The ADR index lists all four with the correct statuses.
  `pyproject.toml` and `uv.lock` are identical on both parents and in the candidate.
- PROGRESS and MERGE_RECONCILIATION match the local record: baseline-r0009
  technical QA passed and the applicant approved its appearance only. PDF/TXT
  content, final artifact approval and export are still pending.
  CLEANUP-001 and TASK-010 are correctly attributed to PR #1 and PR #2.

## Commands and results

Host: macOS 13.6.9 x86_64, Python 3.12.14, uv 0.12.13, Poppler 25.08.0, `/usr/bin/sandbox-exec`.
`JAE_TYPST_PACKAGE_ROOT=$HOME/Library/Caches/jae/typst-packages`.

| Command | Exit | Result |
| --- | --- | --- |
| `uv sync --locked --group dev` | 0 | 35 packages checked |
| `./scripts/install_hooks.sh` | 0 | hooks enabled (idempotent) |
| `uv run python scripts/setup_typst_packages.py --destination "$JAE_TYPST_PACKAGE_ROOT"` | 0 | Assets were already installed, so I used the verify-only mode: same checksum check, no network. `--download` would skip files that already match their checksums. |
| `uv run ruff check .` | 0 | All checks passed |
| `uv run ruff format --check .` | 0 | 68 files already formatted |
| `uv run mypy src` | 0 | no issues in 40 source files |
| `uv run pytest -ra` | 0 | **147 passed**, 0 skipped/xfail, 65 s |
| `uv run jae --help` | 0 | lists `config-check`, `job-ingest`, `job-show`, `build-cv`, `snapshot-build`, `snapshot-approve`, `snapshot-export` |
| `git diff --check`; `git diff --cached --check HEAD`; `… MERGE_HEAD` | 0 | clean |
| Relative Markdown link scan (110 tracked `.md` files) | — | 0 broken, including the archived `history/` files |

Additional evidence:

- **Real renderer:** with `JAE_TYPST_PACKAGE_ROOT` unset,
  `test_real_production_pdf_complete_content_and_geometry` fails with the bounded
  "offline Typst packages missing or changed" `PdfRenderError`. So the
  147-pass run included real Typst rendering, and missing assets fail closed.
- **CLI intake exercised by hand** against a throwaway synthetic `JAE_DATA_DIR`
  (deleted afterwards), using only the repository's synthetic JD fixtures:
  - file ingest created r1; repeating it reported `duplicate: true`;
  - stdin with an explicit `--job-id` and changed text created r2;
  - `job-show` returned the revision record;
  - invalid UTF-8 and a 3 MB input were rejected (exit 2);
  - a missing file gave the generic unavailable error (exit 2);
  - a path-traversal job ID was rejected (exit 2);
  - appending to a stored `job_description.md` made `job-show` fail with a checksum mismatch (exit 2).

## Findings

None are blocking.

- **F-01 (Low, docs):** [REVIEW_HANDOFF.md](../REVIEW_HANDOFF.md) line 27 names
  `baseline-v2-presentation-adr018` as the identity to preserve. The current
  local identity, preserved in the candidate, is
  `baseline-v3-presentation-m1-fix005-hyphen-compounds`. Runtime behavior is
  correct; only the handoff wording is stale. Fix it in the documentation delta
  that records this verification.
- **F-02 (Info, existing, not caused by this merge):** `JobMetadata.source_url`
  accepts any string, including `javascript:` schemes. This matches TASK-010's
  documented behavior (metadata only, never fetched) and main's reviewed bytes.
  Owner/gate: any later task that renders or links the URL (letters, tracker,
  DOCX: TASK-021–024) must validate or escape the scheme first.
- **F-03 (Info, existing local):** the ADR index lists ADR-017 as
  "PROPOSED — INDEPENDENT REVIEW REQUIRED", but ADR-017 itself says
  "PROPOSED — IMPLEMENTATION CLEARED BY INDEPENDENT REVIEW". This was inherited
  unchanged from local HEAD. Align it in a later documentation correction.

## Assessment and next gate

- Architecture/ADRs: local decision identities, reviews and template identity
  are preserved. The renumbering of main's decisions changes no policy and
  transfers no approval.
- Security/privacy:
  - runtime network denial is intact, and Typst packages are now staged in a
    private per-build directory;
  - I found no personal data, secrets or private paths in the staged diff;
  - no private profile was read and no CV was regenerated.
- Limitations:
  - this is a local macOS run, not CI on the combined tree;
  - I did not inspect the personal baseline-r0009 artifacts (out of scope).

Next gate:

1. The implementer records this verification and fixes F-01 in a
   documentation-only delta.
2. That delta gets a scoped review.
3. Then complete the merge commit. Push only on explicit user instruction.
4. TASK-009 content and final artifact acceptance remain the user's decision.
