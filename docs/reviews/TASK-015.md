# TASK-015 independent implementation review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, sandbox `workspace-write` on a throwaway detached checkout of
  `4cc18ef` plus a dedicated temporary directory, no network, session
  `01a1e069-0e53-7f71-81f8-949961f46865`. Tracked files unchanged; exit 0.
- The report below is verbatim. F-01 is addressed by the next commit for round 2.

## Round 1 report

VERDICT: CHANGES REQUIRED

# TASK-015 independent implementation review

- Reviewer: Codex, independent implementation reviewer in a separate session from the Claude Code implementer.
- Date: 2026-11-15.
- Base: `main` `e88546e57ca01a6052c24b2539ae45272e1993db` (tree `8d4ff6c57dde99200106b52c6e04f4686368b8bf`).
- Candidate: `4cc18efa6b7686a65794afc7c3fc76a31726f40d` (tree `73dd126cca85d0b4ea491d221d83edcf29702418`).
- Review checkout: detached candidate checkout; working tree remained clean.
- Scope: full candidate diff; post-approval fixture delta `5bf2123286f1729e61911730ad761bba029e3b8a..965ca66`; `matching/constraints.py`, `matching/durations.py`, focused tests and fixtures.

## Artifacts and requirements read

Read `AGENTS.md`, `docs/REVIEW_HANDOFF.md`, `docs/REVIEW_PROTOCOL.md`, `docs/PROGRESS.md`, `docs/tasks/TASK-015.md`, `docs/ACCEPTANCE_CRITERIA.md` (A07, A22, A23), `docs/ARCHITECTURE.md` (matching, language, authorization, numeric and years sections), `docs/SECURITY_AND_PRIVACY.md`, `docs/MATCHING.md`, `docs/adr/ADR-007.md`, `docs/adr/ADR-011.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/APPLICATION_WORKFLOW.md`, `docs/reviews/TASK-015-FIXTURES.md`, and `tests/fixtures/matching/README.md`. The required A07/A22/A23 entries are in the central acceptance matrix; there are no separate `docs/acceptance/A07*` files in this checkout.

The candidate adds the deterministic typed evaluator, calendar-month interval union, 93-case synthetic oracle and focused tests. The fixture follow-up delta adds authorization month/year precision cases and the known-end as-of-cutoff case, and states the months-only duration API and threshold adapter.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Detached candidate checkout, clean before and after review; no tracked files changed. |
| `git diff --stat e88546e57ca01a6052c24b2539ae45272e1993db..4cc18efa6b7686a65794afc7c3fc76a31726f40d` | 0 | 11 files; 3,985 insertions and 27 deletions. |
| `git diff 5bf2123286f1729e61911730ad761bba029e3b8a..965ca66 -- tests/fixtures/matching` | 0 | README and fixture follow-up delta; 158 added/removed lines. |
| `.venv/bin/python -m pytest tests/test_constraints.py -ra -p no:cacheprovider --basetemp=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-015-impl-tmp/pytest` | 0 | **115 passed**, 0 failed, 0 skipped. The 93 oracle cases and focused adversarial/validation tests passed. |
| `PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -m pytest -ra -p no:cacheprovider --basetemp=/private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-015-impl-tmp/pytest-full` | 1 | **811 passed, 29 failed, 0 skipped**. All failures are pre-existing renderer/QA tests that require nested macOS `sandbox-exec`/host renderer tools in this environment; the matching tests pass. Hosted CI is the required environment for those checks. Failed test identifiers: `tests/rendering/test_pdf_qa.py::test_real_production_pdf_complete_content_and_geometry[False]`, `[True]`, `test_actual_negative_pdf_fails_for_intended_reason[wrong_scope-check_ids9]`, `test_actual_negative_pdf_fails_for_intended_reason[hidden-check_ids13]`, `test_adversarial_control_is_valid_and_empty_denominators_are_null`, `test_missing_tool_is_not_a_pass[pdftotext]`, `[pdftoppm]`, `[pypdf]`, `test_visual_observation_is_explicit_and_hash_bound`, `test_qa_module_command_records_unchecked_visuals`; `tests/test_m1_fix.py::test_m1_real_pdf_qa_and_snapshot_export_preserve_claims`, `test_m1_cli_build_forwards_required_support_captures`; `tests/test_m1_fix004.py::test_real_no_project_pdf_has_no_project_heading_or_extra_page`, `test_real_over_capacity_pdf_preserves_content_without_shrinking`, `test_exact_review_long_contact_url_fails_before_publication`, `test_fitting_contact_url_is_complete_in_both_extractors`, `test_over_width_contact_url_fails_with_bounded_diagnostic`; `tests/test_m1_fix006.py::test_real_pdf_extracts_expected_completion_specialization_and_headings`; `tests/test_m1_fix007.py::test_over_width_trailing_slash_token_fails_before_publication`, `test_real_pdf_keeps_slash_compounds_complete_in_both_extractors`, `test_unbreakable_slash_compound_fails_before_publication`; `tests/test_m1_fix008.py::test_over_width_linkedin_url_fails_before_publication`, `test_real_pdf_compact_groups_and_linkedin_extract_exactly`; `tests/test_rendering.py::test_production_pdf_preserves_complete_unicode_content_with_two_extractors`, `test_production_pdf_keeps_hostile_text_literal_and_does_not_read_sentinel`, `test_production_pdf_handles_long_two_page_plan_without_pruning`, `test_production_pdf_preserves_url_and_hyphenation_sensitive_words`, `test_literal_hyphen_compounds_are_complete_in_summary_and_project_body`, `test_unbreakable_hyphenated_compound_fails_before_publication`. |
| `.venv/bin/ruff check --no-cache .` | 0 | All checks passed. |
| `.venv/bin/ruff format --no-cache --check .` | 0 | 92 files already formatted. |
| `.venv/bin/mypy src --cache-dir /private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-015-impl-tmp/mypy` | 0 | No issues in 56 source files. |
| `git diff --check e88546e57ca01a6052c24b2539ae45272e1993db..4cc18efa6b7686a65794afc7c3fc76a31726f40d` | 0 | No whitespace errors. |

The only generated files were reviewer probes, pytest basetemp, mypy cache and this report under the permitted `codex-015-impl-tmp` directory. No network, home directory, other worktree or private data root was read.

## Independent probes

I wrote a separate standard-library reference implementation for the README interval rules and compared it with the production functions/evaluator. It did not call production interval arithmetic to compute expected values.

- 5,000 randomized date/precision/known-end/ongoing/unknown-end interval sets matched lower and upper union bounds, exclusions, contributor IDs and as-of cutoffs.
- 300 randomized approved employment profiles matched the evaluator's overall-duration bounds, contributor IDs, exclusions and state semantics.
- 250 randomized language cases, 250 credential cases, 250 degree cases and 250 authorization cases matched independently calculated state, rationale and sorted `fact_ids`, including mixed multi-fact precedence and date precision.
- Boundary probes covered day-1 and non-day-1 starts, last-day and non-last-day ends, leap February, ongoing ends, same-month precision, month/year starts after as-of, known ends after as-of, year precision, extreme years 1/9999, and 5,000 intervals. No discrepancy was found.
- The fixture oracle's overlap/gap union, role and skill scope, periodless facts, exposure/self-study exclusion, unknown dates, future awards, statement month/year precision and known-end as-of follow-up cases all passed the focused suite.
- Explicit probes confirmed UTC expiry conversion at offsets including `+14:00` and `-12:00`/`-23:59`; NFC, whitespace collapsing, `casefold()` behavior for `ß`, `İ` and combining marks; strict extra-key/type/bound rejection; `datetime` rejection for `as_of`; draft/revoked exclusion; and rejection of an invalid `model_copy` profile before evaluation.
- No path inferred IELTS/native/self-described language level, authorization from location/residence/nationality/student status, seniority from a title, or FTE from part-time facts. Missing authorization and duration evidence stayed `unknown`/`no_evidence`, never `explicitly_unmet`.

## Findings

| ID | Severity | File | Finding | Reproduction |
|---|---|---|---|---|
| F-01 | high | `src/job_application_engine/matching/constraints.py:175-178,202-208` | `_language_key()` accepts every `normalize_surface()` concept without checking that the concept is a reviewed language concept, and it collapses `status="ambiguous"` surfaces into the ordinary literal-name path. TASK-013 marks ambiguous aliases as candidates, not exact concepts; the review requirement is that ambiguous aliases must not count. A false language match can therefore become `direct` and satisfy a hard language requirement. | With an approved synthetic `LanguageFact(language="Spark", assessment=CEFR C2)` and constraint `{"type":"language","language":"Spark","min_level":"B2"}`, the candidate returns `direct / cefr_meets / ["lang-spark"]`. `normalize_surface("Spark")` is `status="ambiguous"`, so this must not count as a concept-backed language match. The same code also treats technology aliases as language identity: an approved language fact `"Amazon Web Services"` satisfies a `"AWS"` language constraint. Keep arbitrary genuinely unmatched names comparable by NFC/whitespace/casefold, but reject ambiguous surfaces and restrict concept identity to `Concept.kind == "language"`; add both regressions. |

## Architecture, security and acceptance assessment

The implementation otherwise follows the reviewed contract: approved facts are validated through the existing support graph before evaluation; draft/revoked records are ignored; fact references retain exact revisions; typed language/credential/degree/authorization precedence is deterministic; credential expiry is evaluated in UTC; authorization is exact and never inferred; duration intervals are conservative calendar-month lower/upper unions with overlap counted once, gaps excluded, unknown precision disclosed and no FTE scaling. `months_from_threshold()` implements the reviewed TASK-012 operator/unit conversion and rejects unsupported/out-of-range thresholds. Constraints use strict Pydantic models with forbidden extra keys and bounded fields.

The matching code is offline and in-memory, adds no dependency or subprocess/network path, and the synthetic fixture contains reserved/example identifiers only. No secrets, personal data, external captures or private paths entered the repository or review report. The renderer failures are environment limitations outside TASK-015 and are explicitly recorded above; they are not claimed as passes.

A07 and the typed TASK-015 slice of A22 are covered by the passing language/credential/degree/authorization cases; the reviewed clarification correctly leaves free-text negative/adjacent/production-depth semantics to TASK-016. A23's interval and scope rules pass the oracle and independent probes. F-01 is a correctness failure in the requested TASK-013 identity boundary, so the candidate is not ready for approval.

## Required corrective task and next gate

Fix TASK-015 review finding F-01 only.

- Base/head reviewed: `e88546e57ca01a6052c24b2539ae45272e1993db` → `4cc18efa6b7686a65794afc7c3fc76a31726f40d`.
- Failure: ambiguous `Spark` and non-language aliases can satisfy a language constraint as `direct`.
- Affected module: `src/job_application_engine/matching/constraints.py` (and the reviewed concept lookup/normalization adapter as needed).
- Required change: keep NFC/whitespace/casefold matching for genuinely unmatched language names; do not treat ambiguous TASK-013 aliases as matches; use only reviewed language concepts for concept identity. Preserve skill behavior and all existing state/precedence/fact-ID rules.
- Acceptance: sanitized regressions for ambiguous `Spark` and non-language `AWS`/`Amazon Web Services` return `no_evidence` (or literal-name behavior only where both surfaces are genuinely unmatched), while `German`/`Deutsch` remains one language concept; focused oracle and independent randomized probes remain green.
- Tests to retain/add/run: focused TASK-015 suite, full suite in hosted macOS CI, Ruff, format, mypy and diff checks; rerun the independent ambiguity and concept-kind probes.
- Non-goals: no matcher redesign, no TASK-016 semantic matching, no weakening of alias or profile validation.
