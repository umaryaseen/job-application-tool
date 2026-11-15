# TASK-013 independent implementation review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, sandbox `workspace-write` on a throwaway detached checkout of
  `a56309a` plus a dedicated temporary directory, no network, session
  `01a1dd03-4724-7153-93b2-54a24f59bb71`. Tracked files unchanged; exit 0.
- The report below is verbatim.

---

VERDICT: CHANGES REQUIRED

# TASK-013 independent implementation review

- Reviewer: Codex, independent implementation reviewer; the implementation was not authored by this reviewer
- Date: 2026-11-15
- Base: `ee590699b49077a1cd61161caa679f104b99b659` (tree `1d7387c7dd2aa5fb11ae63d2d6ee19f9ab9d24f7`)
- Candidate: `a56309ac2a3f6414e06d784214066bdcf077f42f` (tree `c8d03a67a66a8f7aa6285dd845c31351cb166a57`)
- Fixture amendment reviewed in the candidate: `cd9493f97d7bf266731ae7ebc7fbcaa1e4880918`
- Scope: TASK-013 implementation, amended normalization oracle, TASK-012 adapter, relevant documentation and static checks

## Artifacts inspected

`AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `docs/PROGRESS.md`, `docs/tasks/TASK-013.md`, A21 in `docs/ACCEPTANCE_CRITERIA.md`, ADR-005/006/007, the normalization sections of `docs/ARCHITECTURE.md`, `docs/JOB_EXTRACTION.md`, `tests/fixtures/normalization/README.md`, `docs/reviews/TASK-013-FIXTURES.md`, and the full base-to-candidate diff.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Detached candidate clean before the review report was created. |
| `git diff --stat ee590699b49077a1cd61161caa679f104b99b659..a56309ac2a3f6414e06d784214066bdcf077f42f` and `git diff --name-status ee590699b49077a1cd61161caa679f104b99b659..a56309ac2a3f6414e06d784214066bdcf077f42f` | 0 | 10 changed paths: normalization package, tests/oracle, and task documentation; no dependency or CLI file. |
| Independent fixture structure probe using `python` and `json` | 0 | 43 scan cases, 25 surface cases, 8 relation rows; 0 quote/order/status invariant errors. |
| `.venv/bin/python -m pytest tests/test_skill_normalization.py tests/test_requirement_classification.py -ra -p no:cacheprovider --basetemp=.../codex-013-impl-tmp/pytest` (first run, prescribed parent absent) | 1 | 135 passed, 242 setup errors because pytest could not create the absent basetemp directory. No test assertion failed. |
| `mkdir -p .../codex-013-impl-tmp/pytest` followed by the same prescribed pytest command | 0 | **377 passed** in 37.96s. |
| `.venv/bin/ruff check --no-cache .` | 0 | All checks passed. |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 81 files already formatted. |
| `.venv/bin/mypy src --cache-dir .../codex-013-impl-tmp/mypy` | 0 | No issues found in 50 source files. |
| `git diff --check ee590699..a56309ac` | 0 | No whitespace errors. |
| Independent Unicode, overlap, surface, relation, adapter, bound and performance probe | 0 | Found the two Part B findings below. The matcher accepted a 200,000-character input and rejected 200,001 characters; dense mention input raised the 4,096-mention limit; tested 200,000-character no-match inputs completed below one second after matcher initialization. |
| Renderer tests | not run | Nested `sandbox-exec` is required in this environment; renderer coverage is hosted-CI work and was not claimed here. |

## Part A — amended fixture re-review

F-01 is resolved. The README now defines surfaces as trimmed whole-string alias matches, with scan semantics explicitly excluded. Therefore `Python 3` and `Deep Learning — applied object detection` are correctly `unmatched`, while `  Kubernetes ` is correctly trimmed and `matched`.

F-02 is resolved. The README identifies the reviewed alias inventory in `normalization/dictionary.py` and explicitly excludes Go, TS, Rust, Swift and Objective-C. The empty result for `Go-to-market` follows that contract; it does not depend on an unstated alias set.

F-03 is resolved. The README defines `from` as the subject, makes a `broader` edge point from the narrower subject to the broader `to` concept, and prohibits relation traversal as alias equivalence. The AWS/SageMaker, .NET/ASP.NET, Azure, and learning relation rows follow that orientation.

F-04 is resolved. The README now defines Unicode alphanumeric boundaries, combining marks in category M as attached to the preceding letter, and underscore, punctuation, symbols and whitespace as boundaries. The added combining-mark and underscore cases are consistent with those rules.

All unchanged and amended labels follow the amended contract: scan mentions are literal, source-ordered, non-overlapping explicit aliases; whole surfaces are either one complete alias or unmatched with trimmed literal text; ambiguous Spark remains a candidate; relation rows remain typed and non-equivalent; and no label asserts possession. Part A has no unresolved finding.

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| — | — | `tests/fixtures/normalization/README.md`, `tests/fixtures/normalization/aliases.json` | No unresolved fixture-label finding. F-01–F-04 are closed, and all 43 scan, 25 surface and 8 relation labels comply with the amended rules. | Independent JSON quote/order/status probe: exit 0, 0 structural errors; manual rule audit of every label. |

## Part B — implementation findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-05 | high | `src/job_application_engine/normalization/aliases.py:89-95` | Word and symbol aliases use Python `re.IGNORECASE`, whose extra Unicode caseless matches are not Unicode `casefold()` equivalence. This creates false positive skill mentions for dotted and dotless-I variants. The reviewed exact matcher must not normalize text that is not case-fold equivalent to the alias. | `find_mentions("GİT")` returns `quote="GİT", concept_id="git", status="matched"`; `find_mentions("GıT")` does the same. Yet `"GİT".casefold() == "git".casefold()` and `"GıT".casefold() == "git".casefold()` are both false. The same class affects aliases containing `I` such as Linux, JavaScript, CI/CD and the field aliases. |
| F-06 | medium | `src/job_application_engine/normalization/aliases.py:31,168-184` | `normalize_surface` enforces `MAX_TEXT` only on the trimmed value passed to `find_mentions`, so an arbitrarily oversized raw surface consisting of an alias plus trailing whitespace is accepted. This bypasses the normalizer's stated 200,000-character bound at a public entry point. | `normalize_surface("Python" + " " * 200001)` returns a matched Python mention with span `[0, 6)` even though the raw input length is 200,007; it should reject the oversized input before trimming. |

## Architecture, security and acceptance assessment

The dictionary is versioned, explicit and rationale-backed. Longest valid aliases win, mentions do not overlap, symbolic names remain distinct, unmatched surfaces retain their trimmed literal text, and typed relations are not traversed. The TASK-012 adapter preserves source offsets and maps `none`, `requirement_negated` and `unsupported` to positive, negated and unknown mention polarity without adding possession, approval or career facts. The focused A21 and classification tests pass.

The candidate stays within scope: no CLI command, ESCO service, model, dependency, subprocess, network access, profile access, approval state or applicant data was added. The Unicode caseless false positive is a correctness and trust-boundary issue for exact normalization. The surface-bound bypass is bounded in practical TASK-012 use by source-span validation, but remains an exposed API limit failure and needs a narrow fix.

## Required follow-up and next gate

Fix F-05 with explicit Unicode case-fold-aware matching that does not use `re.IGNORECASE`'s dotted/dotless-I extras; retain literal spans and add negative tests for `GİT` and `GıT`, plus coverage for the relevant `ß` case-fold behavior if a reviewed alias uses it. Fix F-06 by checking the raw surface length before trimming and add an over-boundary regression case. Rerun the focused pytest command, Ruff check/format, mypy, diff check, and the Unicode/200,000-character probes on the corrective head. The corrective commit requires another independent review before approval.

---

## Round 2 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning `xhigh`,
  sandbox `workspace-write` on a throwaway detached checkout of `f26da14` plus a
  dedicated temporary directory, no network, session
  `01a1dd1d-9637-7830-9fb4-9cfbb7dd7061`. Tracked files unchanged; exit 0.

The reviewer's round-2 report follows verbatim.

## Round 2

- Reviewer: Codex, independent implementation reviewer; implementation not authored by reviewer
- Date: 2026-11-15
- Base: `ee590699b49077a1cd61161caa679f104b99b659` (tree `1d7387c7dd2aa5fb11ae63d2d6ee19f9ab9d24f7`)
- Candidate: `f26da14bc265d7ccf56290c6777aa8cb54857605` (tree `9bd41db5d082342799817b2babf2cbc41c8488e6`)
- Fixture amendment: `cd9493f97d7bf266731ae7ebc7fbcaa1e4880918`
- Scope: TASK-013 corrective re-review, fixture contract/cases, normalization matcher, TASK-012 adapter, architecture/security/scope compliance

VERDICT: APPROVED

### Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Detached checkout clean |
| Full corrective diff `git diff a56309a..f26da14bc265d7ccf56290c6777aa8cb54857605` | 0 | 264 lines, 5 paths inspected |
| Full base-to-head diff `git diff ee590699b49077a1cd61161caa679f104b99b659..f26da14bc265d7ccf56290c6777aa8cb54857605` | 0 | 2,042 lines, 11 paths inspected |
| Independent fixture-contract probe | 0 | 43 scan, 25 surface, 8 relation cases; 0 errors |
| `.venv/bin/python -m pytest tests/test_skill_normalization.py tests/test_requirement_classification.py -ra -p no:cacheprovider --basetemp=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-013-r2-tmp/pytest` | 0 | 388 passed |
| `.venv/bin/ruff check --no-cache .` | 0 | All checks passed |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 81 files formatted |
| `.venv/bin/mypy src --cache-dir /private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-013-r2-tmp/mypy` | 0 | 50 source files passed |
| `git diff --check ee59069..f26da14bc265d7ccf56290c6777aa8cb54857605` | 0 | No whitespace errors |
| Unicode, overlap, surface, relation, bound and performance probe | 0 | All assertions passed; 200,000-character no-match input completed in 0.007 s after matcher warm-up; first-call probe completed in 0.877 s |
| Cross-concept alias-collision probe | 0 | 3 collision dictionaries rejected |
| TASK-012 adapter offset/polarity probe | 0 | 5 rows, 5 normalized terms, 0 assertion errors |
| Renderer tests | Not run | Nested `sandbox-exec` required; hosted CI covers renderer tests |

### Part A — fixture re-review

The amended README resolves F-01 through F-04. The independent contract probe checked every amended and unchanged label against the README rules, without using the production matcher, and found no discrepancies.

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-01 | blocking — closed | `tests/fixtures/normalization/README.md`, `aliases.json` | Surface semantics now explicitly trim whitespace, require one whole-alias match, and exclude scan semantics. | `Python 3` and compound `Deep Learning — applied object detection` are correctly unmatched; padded `Kubernetes` is correctly matched. |
| F-02 | high — closed | `tests/fixtures/normalization/README.md`, `aliases.json` | The reviewed inventory is named and explicitly excludes Go, TS, Rust, Swift and Objective-C. | `Go-to-market` correctly has no mention. |
| F-03 | high — closed | `tests/fixtures/normalization/README.md`, `aliases.json` | Relation orientation and non-traversal are explicit. | All 8 relation rows match typed dictionary relations; no relation is treated as equivalence. |
| F-04 | medium — closed | `tests/fixtures/normalization/README.md`, `aliases.json` | Unicode alphanumeric boundaries, combining marks, underscores and punctuation are defined. | Independent scan/surface audit: 0 errors across all 68 expected mentions and 25 surfaces. |
| — | — | — | No unresolved fixture-label finding. | All 43 scan, 25 surface and 8 relation labels comply. |

### Part B — implementation findings

F-05 is fixed by explicit per-character Unicode `casefold()` matching and rejection of aliases with multi-character folds. Dotted/dotless-I false positives are rejected while valid equivalents such as `GIT`, long-s `ſQL`, and Kelvin-sign `Kubernetes` match.

F-06 is fixed by checking raw surface length before trimming. Oversized alias-plus-whitespace input now raises `NormalizationError`.

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-05 | high — closed | `src/job_application_engine/normalization/aliases.py` | `re.IGNORECASE` false positives removed; exact Unicode case-fold semantics enforced. | `GİT`, `GıT`, `JAVASCRİPT`, and `PYTHONİ` produce no mentions; multi-character-fold alias validation rejects `Straße`. |
| F-06 | medium — closed | `src/job_application_engine/normalization/aliases.py` | Raw `normalize_surface` input is bounded before trimming. | `normalize_surface("Python" + " " * 200001)` raises `NormalizationError`. |
| — | — | — | No new implementation finding. | Unicode, boundary, longest-match/backtracking, ambiguity, relation, polarity, adapter, bound and performance probes passed. |

The candidate remains within TASK-013 scope: no CLI change, dependency, model, network access, profile access, possession or approval logic was added. Exact aliases remain distinct from typed broader/related relations, unmatched surfaces retain literal text, and TASK-012 offsets and negation polarity are preserved.
