# TASK-012 independent implementation review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex, a separate agent session — `codex exec` (OpenAI Codex
  v0.160.0, model `gpt-6.1-terra`, reasoning effort `xhigh`), sandbox
  `workspace-write` limited to a throwaway detached checkout plus temporary
  directories, no network, session `01a1da7b-cb48-7e92-8e7c-a0b8c840bf3c`.
  Implementer: Claude Code (Claude Opus 5.5).
- Candidate `f41df6b83fa0d48e5cd86b5675d9d155a4446429`, tree `de22bec2`. The
  checkout's tracked files were unchanged afterwards (`git status`: only the
  untracked report and `.review-tmp/` scratch). Process exit 0.
- Harness note: the implementer's prompt placed pytest temporary data inside the
  checkout, which the private-data-root policy correctly rejects; the reviewer
  worked around it with a review-only `sitecustomize.py`. Later rounds use a
  temporary directory outside the checkout.
- The reviewer could not commit (sandbox blocks the worktree index), so the
  implementer commits the report below verbatim.

---

VERDICT: CHANGES REQUIRED

# TASK-012 independent implementation review

- Reviewer: Codex, independent review session (not the implementer)
- Date: 2026-11-14
- Implementer: Claude Code
- Base commit: `f6a3bf0560df9c3e7594cc835f13864d98c3c6c3`; tree `5e02c63af4544dd489517b056c07ff37e2313704`
- Fixture commit inspected: `2988f636`; fixture review `docs/reviews/TASK-012-FIXTURES.md` is already approved
- Candidate commit: `f41df6b83fa0d48e5cd86b5675d9d155a4446429`; tree `de22bec2e3a536965f505fa982d26e9f6d7ffd63`
- Scope: cumulative `f6a3bf0..f41df6b`, TASK-012 implementation, tests and documentation. No implementation files were modified during this review.

## Commands and results

All commands were run in the supplied detached checkout. The review read AGENTS.md, `docs/REVIEW_HANDOFF.md`, `docs/REVIEW_PROTOCOL.md`, `docs/PROGRESS.md`, TASK-012, A17–A19, ADR-007/011/021, the architecture requirement-model section, security/privacy guidance, JOB_EXTRACTION and the fixture README.

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Detached candidate checkout; only review scratch appeared later under `.review-tmp/`. |
| `git rev-parse HEAD && git rev-parse HEAD^{tree}` | 0 | Candidate and tree matched the handoff. |
| `git diff --stat f6a3bf0..f41df6b` / `git diff --name-status f6a3bf0..f41df6b` | 0 | Full cumulative diff inspected: 18 paths, including fixture commit, implementation, tests and docs; no dependency/lockfile change. |
| `git diff f6a3bf0..f41df6b -- <affected files>` | 0 | Reviewed CLI, domain models, classification, grouping, priority, spans, rules, tests and docs. |
| `.venv/bin/python -m pytest tests/test_requirement_classification.py tests/test_requirement_spans.py tests/test_ingestion.py -ra -p no:cacheprovider --basetemp=.review-tmp/pytest` | 1 | 193 collected: 24 passed, 169 failed because this sandbox places `tmp_path` inside the checkout and the intentional private-data-root policy rejects it. The failures were configuration-policy failures before behavior execution. |
| `PYTHONPATH=.review-tmp .venv/bin/python -m pytest tests/test_requirement_classification.py tests/test_requirement_spans.py tests/test_ingestion.py -ra -p no:cacheprovider --basetemp=.review-tmp/pytest-harness` | 0 | 193 passed in 13.70s. The review-only `sitecustomize.py` patched repository-root detection so synthetic pytest data could exercise the implementation without changing tracked code or accessing private data. |
| `.venv/bin/ruff check .` | 0 | All checks passed. |
| `.venv/bin/ruff format --check .` | 0 | 77 files already formatted. |
| `.venv/bin/mypy src --cache-dir .review-tmp/mypy` | 0 | No issues in 47 source files. |
| `git diff --check f6a3bf0..f41df6b` | 0 | No whitespace errors. |
| `git add docs/reviews/TASK-012.md` | 128 | The managed sandbox forbids writes to the linked worktree index (`.git/worktrees/.../index.lock`); the requested report file is present, but cannot be committed from this checkout. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/adversarial.py` | 0 | 20 semantic cases, Unicode/parity checks, 3 tamper checks, hostile/large input checks and 2 CLI error checks completed. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/probe_partial.py` | 0 | 10 alternative/unknown-operand probes; exposed silent partial conditions. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/probe_thresholds.py` | 0 | 17 threshold probes; exposed the raw out-of-range validation error and silent large-number omission. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/probe_duplicates.py` | 0 | 4 duplicate-context probes; exposed cross-heading duplicate grouping. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/probe_tamper.py` | 0 | Relabel, split, invented-span and forged-digest cases were rejected. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/probe_dense.py` | 0 | Five 199,000-byte dense cases completed in 0.17–0.41s; annotation-limit cases raised bounded `ExtractionError`, unsupported grammar remained reviewable. |
| `PYTHONPATH=src:.review-tmp .venv/bin/python .review-tmp/probe_cli999.py` | 0 | The subprocess returned exit 2 for an out-of-range duration, but emitted raw Pydantic validation details (see F-03). |
| Scope/dependency/network scans with `rg` and diff inspection | 0 | No new dependency, provider, persistence, matching, tailoring, alias/normalization, correction-version or renderer feature was added; classifier and extraction paths perform no network or posting execution. |

PDF renderer tests were not run. They require nested macOS `sandbox-exec`, Poppler and pinned Typst assets that cannot run inside this sandbox; hosted CI is the appropriate check for that separate renderer path.

## Probe outcomes

- Preferred headings and marker scopes did not produce `mandatory`; explicit mandatory text under a preferred scope became `unspecified` with review, and marker scope ended at the next heading.
- Recognized English and German not-required forms stayed `requirement_negated`; unsupported negation stayed `unsupported` and review-required.
- Supported nested `ANY`/`ALL`, degree-or-equivalent, CEFR and integer threshold examples matched the approved oracle.
- CRLF, BOM, combining marks and emoji quotes/signals round-tripped exactly; saved `job-extract` and `job-classify` results matched direct extraction/classification and did not mutate the synthetic job files.
- Recomputed classification digests did not authorize relabelled, split or invented rows.
- Dense 200,000-byte-class inputs stayed bounded or failed with `ExtractionError`; no hostile text executed and no socket was opened.

## Findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-01 | blocking | `src/job_application_engine/extraction/groups.py:277-319`, `:512-523` | Unsupported alternatives with an unrecognized operand can yield a supported partial condition with no review. Slash detection only runs between two recognized atoms, and a comma-only/unknown-operand gap has no connective for the final safety pass. This violates the documented rule that unsupported alternatives remain review-required and are never partially kept. | Synthetic source `Requirements ⏎ Python / Rust is required.` (or `Python / QuuxDB`) returns `condition=Python`, `review_reasons=[]`. `Requirements ⏎ Python, QuuxDB is required.` does the same. Both operands are not fully represented by the extracted signals. |
| F-02 | blocking | `src/job_application_engine/extraction/groups.py:323-363` | The education shortcut can consume a later `or a related/similar field` after the equivalent branch and emit only the first two alternatives without review. The third OR is treated as a field qualifier even though it follows `equivalent experience`, contrary to the all-connectives-accounted invariant. | `Requirements ⏎ A degree or equivalent experience or a related field.` returns an `ANY` group `degree / equivalent experience`, `needs_review=false`, with the trailing alternative omitted. `... or similar field.` behaves the same. |
| F-03 | blocking | `src/job_application_engine/extraction/groups.py:366-407`; `src/job_application_engine/domain/requirement.py:132-167` | Out-of-range integer durations are not converted to a bounded review outcome. A three-digit value such as 999 reaches `Threshold(value=999)` even though the model limit is 99 and raises raw `pydantic_core.ValidationError`; a four-digit value such as 1000 is not extracted at all and can leave a bare `Python` condition with no review. The CLI returns 2 but exposes the raw validator detail. | `Requirements ⏎ 999 years of Python experience.` raises `ValidationError: value Input should be less than or equal to 99`. `Requirements ⏎ 1000 years of Python experience.` returns no threshold and no review. |
| F-04 | blocking | `src/job_application_engine/extraction/classification.py:87-126` | Duplicate grouping ignores source heading/section identity. Identical text and qualifiers under different headings are grouped as duplicates, despite the fixture README explicitly requiring that same text under different headings not be merged. | `Requirements ⏎ - Python is required. ⏎ Qualifications ⏎ - Python is required.` produces one duplicate group containing both rows (`[[0, 1]]`). The rows retain spans, but the duplicate classification is wrong and can distort later requirement counts. |

## Architecture, security and acceptance assessment

The implementation stays within TASK-012’s intended source-only boundary: output is draft, revision/hash/extraction-bound, read-only, deterministic, and does not access profiles, providers, persistence or the network. The exact candidate rows and spans are structurally checked, and the forged-digest probes confirm that deterministic reclassification rejects relabelled or invented content. Static checks and the focused suite pass when run with the review-only data-root harness.

The four blocking findings violate core A18/A19 acceptance and the handoff’s explicit safety invariants: unsupported alternatives may become hard partial conditions, a supported group may omit a visible alternative, malformed numeric input can escape as an unbounded internal validation error, and duplicate semantics do not match the independently approved fixture rules. The candidate therefore requires a narrow corrective implementation and a new independent review.

## Required follow-up

- Fix F-01 by treating every separator/alternative candidate, including unknown operands and bare slash/comma forms, as accounted only when the complete clause is represented; otherwise emit `condition=null` with review.
- Fix F-02 by rejecting or reviewing any extra connective after the degree/equivalent pair instead of attaching it to the first degree term.
- Fix F-03 by detecting out-of-range/oversized numeric literals, returning a bounded `ExtractionError` or explicit review result, and keeping CLI diagnostics sanitized and bounded.
- Fix F-04 by incorporating heading/section context into duplicate equivalence or deriving duplicate groups from the extraction’s section identity; preserve each source span.

The corrective commit should rerun the focused suite, Ruff, format, mypy, diff-check and these adversarial probes before returning for independent review.

---

## Round 2 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning `xhigh`,
  sandbox `workspace-write` on a throwaway detached checkout of `fbc4c97` plus a
  dedicated temporary directory, no network, session
  `01a1da93-7347-7e43-b38f-0c2461886496`. Checkout tracked files unchanged; exit 0.
- Pytest used a temporary directory outside the checkout (no policy workaround).

The reviewer's round-2 report follows verbatim.

## Round 2

VERDICT: CHANGES REQUIRED

- Reviewer: Codex, independent implementation reviewer
- Date: 2026-11-14
- Base: `f6a3bf0560df9c3e7594cc835f13864d98c3c6c3`
- Round-1 head: `f41df6b83fa0d48e5cd86b5675d9d155a4446429`
- Candidate: `fbc4c970854e77a9b3957439da7d1a600bb0f69c`
- Candidate tree: `22baf8e8a58c58e79ef22b2bde663e06a3c20518`
- Corrective delta inspected in full: 8 paths, 678 diff lines. Working tree remained clean.

### Commands

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Clean detached checkout |
| `git rev-parse HEAD && git rev-parse HEAD^{tree}` | 0 | Candidate/tree matched handoff |
| `git diff f41df6b..fbc4c97` | 0 | Full corrective delta inspected |
| Focused pytest command from handoff | 0 | **221 passed** |
| `.venv/bin/ruff check --no-cache .` | 0 | All checks passed |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 77 files formatted |
| `.venv/bin/mypy src --cache-dir ...` | 0 | No issues in 47 source files |
| `git diff --check f41df6b..fbc4c97` | 0 | Clean |
| `shasum -a 256 tests/fixtures/requirements/classification.json` | 0 | `16b05e8f0f6f1a8d274de6b06e9eacf08fc3af47d6a802fd564537d4be5b18d1` |
| `probe_round2.py` | 0 | 49 cases, no exceptions |
| Numeric, education, connector, cue, CEFR and scope probes | 0 | 94 cases total, no raw exceptions |
| 200,000-byte dense probe | 0 | 4 bounded `ExtractionError` results; one classified in 0.547s |
| CLI sanitization probe | 0 | 4 cases; no raw Pydantic diagnostics |

PDF/renderer tests were not run, as instructed.

### Probe outcomes

- F-01 reproductions and nearby slash, pipe, ampersand, plus, comma and semicolon variants now produce `condition=null` with review.
- F-02 trailing related-field alternatives now remain review-required.
- F-03 round-1 values (`999`, `1000`, `10,000`, `3yrs`, leading zeros and decimals) produce no threshold and require review; CLI output is sanitized.
- F-04 duplicate groups now respect heading and marker scope. Same-scope duplicates still group correctly.
- Controls for `CI/CD`, `C++`, `Ideally, Python`, `Python, preferably`, and supported conjunctions passed without false review.

### Findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-05 | blocking | `src/job_application_engine/extraction/groups.py:376-482,443-456,520-565` | Unsupported or uncaptured threshold text can be omitted or interpreted without review, and malformed scopes can be emitted as valid. | `six years of Python experience.` → `condition=Python`, no threshold, no review. `1000-year Python experience.` and `3-year Python experience.` behave the same. `3 years minimum of Python experience.` → unqualified threshold with no review. `English C2 minimum.` → unqualified C2 with no review. `3 years of.` → scope `of`, no review. |
| F-06 | blocking | `src/job_application_engine/extraction/groups.py:332-373,569-581` | The education shortcut still bypasses comma/semicolon continuation checks, allowing trailing unknown operands to be dropped. | `A degree; QuuxDB is required.` → `condition=degree`, no review. `A degree or a related field; QuuxDB is required.` and `Bachelor's degree or equivalent experience; QuuxDB is required.` also return supported conditions without review. |
| F-07 | blocking | `src/job_application_engine/extraction/groups.py:575-612` | Unknown operands after a recognized term can remain a single-term condition when separated by unsupported filler or punctuation. | `Python plus QuuxDB is required.`, `Python with QuuxDB is required.`, `Python but QuuxDB is required.`, `Python: QuuxDB is required.`, and `Python, preferably; QuuxDB.` all return `condition=Python` without review. |
| F-08 | blocking | `docs/PROGRESS.md:40-52` | The corrective documentation adds applicant-specific private revision details to the tracked TASK-009 state note. This conflicts with the required sanitized note and the repository privacy policy. | The note includes applicant CV revision metadata, a payload count, and a profile degree/date defect. Replace with a generic pending-review state without applicant-specific facts. |

The corrective code remains source-only, deterministic, revision-bound, dependency-neutral and bounded on dense inputs. The fixture oracle is byte-identical. F-05–F-08 remain unresolved correctness/privacy defects, so the candidate requires another narrow corrective commit and independent re-review.

---

## Round 3 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning `xhigh`,
  sandbox `workspace-write` on a throwaway detached checkout of `2f43f4f` plus a
  dedicated temporary directory, no network, session
  `01a1daac-aee9-7e32-a0a1-569cf6a223aa`. Checkout tracked files unchanged; exit 0.

The reviewer's round-3 report follows verbatim, except that five header lines ending in
Markdown hard-break spaces were turned into list items for whitespace checks.

## Round 3

- Reviewer: Codex, independent implementation reviewer
- Date: 2026-11-14
- Base: `f6a3bf0560df9c3e7594cc835f13864d98c3c6c3`
- Corrective base: `fbc4c970854e77a9b3957439da7d1a600bb0f69c`
- Candidate: `2f43f4f2aa370f4e8b1c20ea358d01aab5fa3ba7`
Candidate tree: `4d59b1a5fcf27b5ab0ce1060d254dfe60df9ef60`

VERDICT: CHANGES REQUIRED

### Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Clean detached checkout |
| `git rev-parse HEAD && git rev-parse HEAD^{tree}` | 0 | Candidate/tree matched handoff |
| Full corrective `git diff fbc4c97..2f43f4f` | 0 | 7 paths, 481 patch lines, 271 additions/35 deletions; fully inspected |
| Focused pytest command | 0 | 249 passed, no skips |
| `.venv/bin/ruff check --no-cache .` | 0 | No violations |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 77 files formatted |
| `.venv/bin/mypy src --cache-dir ...` | 0 | 47 source files, no issues |
| `git diff --check fbc4c97..2f43f4f` | 0 | Clean |
| `sha256sum ...classification.json` | 127 | Utility unavailable |
| `shasum -a 256 ...classification.json` | 0 | Expected digest `16b05e8f...5b18d1` |
| Final `git status --short --branch` | 0 | Clean; no tracked files modified |

PDF renderer tests were not run, as instructed.

### Probe outcomes

- Round-1 F-01/F-02/F-03/F-04 reproductions passed: unsupported alternatives remained `condition=null` with review; malformed durations produced no threshold; duplicate groups respected heading/marker scope.
- `probe_semantics.py`: 74 cases, zero exceptions.
- Unknown-operand matrix: 126 variants, zero unreviewed partial conditions.
- Filler matrix: 14 generic descriptor words; none hid a named operand.
- Education probes: 32 cases, zero exceptions.
- Dense probes: exact 200,000-byte inputs completed in 0.18–0.36s or raised bounded `ExtractionError`.
- CLI probe: one reviewed out-of-range result and four sanitized exit-2 failures; no traceback, Pydantic diagnostics or private paths.
- `docs/PROGRESS.md` now has a generic TASK-009 pending note.

### Findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-09 | blocking | `src/job_application_engine/extraction/groups.py:420-426,465-472,671-687` | Unsupported threshold operators appearing after the scoped phrase, or outside the operator lexicon, can leave a structured `unqualified` threshold. Coverage adds review but does not remove the invalid threshold, contradicting the documented rule that unsupported operators create no threshold. | `3 years of Python experience minimum.` → threshold `unqualified`, value `3`, scope `Python experience minimum`, `condition=null`, review only `uninterpreted_text`. `English B2 level minimum.` similarly emits an unqualified B2 threshold. `About at least 3 years of Python experience.` emits `gte=3` despite contradictory unsupported text. |
| F-10 | non-blocking | `src/job_application_engine/extraction/groups.py:532-539` | The conservative coverage rule flags reasonable prose such as `Experience building REST APIs with Python.` as `uninterpreted_text`, withholding the condition for review. This is documented and does not create a partial condition. | Result is `condition=null`, `needs_review=true`; intended false alarm, with no hidden named operand. |

F-01–F-08 are otherwise fixed, and the implementation remains deterministic, local, revision-bound, dependency-neutral and bounded. F-09 must be corrected and independently re-reviewed before approval.
