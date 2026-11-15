# TASK-016 fixture oracle review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, read-only review (writes only to a temporary directory) of a
  throwaway detached checkout of `0017e3f`, no network, session
  `01a1e0cf-9aa1-7f40-9bb3-ec301ce6ec02`. Tracked files unchanged; exit 0.
- The report below is verbatim. Findings F-01..F-06 are addressed by the next
  commit (revised rules and two new cases) for round 2.

## Round 1 report

VERDICT: CHANGES REQUIRED

# TASK-016 fixture oracle review

Reviewer: Codex, independent fixture-review session (fixture author: Claude Code)
Date: 2026-11-15
Commit reviewed: `0017e3f98e61f2da7aff003a50964b4aba93a597`
Scope: read-only review of `tests/fixtures/matrix/README.md` and `matrix.json` before matrix implementation. No tracked files were modified; all runtime data was written below the permitted private temporary root.

## Commands and results

- `git status --short --branch && git rev-parse HEAD` — exit 0; detached checkout clean at the stated commit.
- `.venv/bin/python -m pytest tests/test_requirement_review.py tests/test_skill_normalization.py tests/test_constraints.py` — exit 0; 305 passed.
- `.venv/bin/ruff check .` — exit 0.
- `.venv/bin/ruff format --check .` — exit 0; 92 files already formatted.
- `.venv/bin/mypy src` — exit 0; 56 source files.
- Private API replay script `review_matrix_api.py` — exit 0; all three postings were ingested as revision 1, loaded with `load_review`, corrected/accepted with `apply_correction`, and reloaded successfully.
- Private independent recomputation script `recompute_matrix.py` — exit 0; all row, exclusion and coverage comparisons available in the fixture were equal.
- `.venv/bin/python -m pytest` — exit 1; 817 passed, 30 failed. Failures were in rendering/snapshot/QA tests (worker exit 71, unavailable renderer tools and stale rendering expectations); this commit changes no such code or fixtures, and no matrix fixture test exists yet.

## Independent recomputation

The review chain produced the expected reviewed/draft gates. The separate evaluator used the written README rules, TASK-013 normalization/relations and TASK-015 constraints; it did not use a matrix implementation.

| Case | Rows | Excluded | Mandatory coverage | Preferred coverage | Unspecified coverage | Comparison |
|---|---:|---:|---:|---:|---:|---|
| `main-matrix` | 16 | 2 | `4/10` | `0/3` | `1/2` | exact row/exclusion/coverage equality |
| `empty-classes-are-not-applicable` | 1 | 0 | `1/1` | `N/A` | `N/A` | exact equality |
| `nothing-reviewed-stays-visible-and-unknown` | 2 | 1 | `0/1` | `0/1` | `N/A` | exact equality |

For `main-matrix`, the recomputed row state sequence in source order was `direct, direct, adjacent, explicitly_unmet, equivalent, no_evidence, no_evidence, equivalent, unknown, unknown, unknown, direct, direct, adjacent, adjacent, unknown`; the repeated `Python or Java` row points to counted row index 0. Exclusions were `German is not required.` → `requirement_negated` and `Nice to have` → `not_a_requirement`. Unknown rows remained in denominators, and empty classes remained `N/A`.

Specific negative/constraint checks also matched the written rules:

- `PostgreSQL` and profile `Postgres` normalize to the same reviewed alias concept and produce `equivalent` / `alias_match`.
- `Amazon EC2` has the typed `broader → aws` relation and produces `adjacent` / `related_concept`; it does not satisfy AWS.
- `German`/`Deutsch` share the language concept. TASK-015 returns `cefr_below` for German B2 (`explicitly_unmet`) and `cefr_meets` for Deutsch B1, which the matrix correctly reports as `equivalent` because the satisfying fact uses a different surface.
- The Python duration is scoped to the project and the five-year threshold to overall employment; overlapping employment intervals are unioned once and both return `direct` / `duration_meets`.
- Kubernetes study and Docker exposure remain `adjacent`; Java in the approved responsibility fact does not satisfy the Java requirement; the approved React fact is not evaluated while its row is unreviewed. Thus adjacent, self-study, exposure and responsibility evidence cannot raise coverage.
- The B2 language gap is `explicitly_unmet`, while unreviewed React/Terraform and unevaluated education remain `unknown`; mandatory gaps remain visible and preferred rows do not affect mandatory coverage.

All data is explicitly synthetic (`synthetic-person`, `synthetic-project`, `synthetic-employer`, reserved fixture text) and contains no applicant material or network input.

## Findings

| ID | Severity | Location | Finding | Suggested correction |
|---|---|---|---|---|
| F-01 | High / acceptance-blocking | `tests/fixtures/matrix/README.md:20-25`; expected rows in `matrix.json` | Expected rows contain only `state`, `reason`, `priority`, `fact_ids` and duplicate index. They do not assert evidence IDs/revisions or a separate concise matching method, although TASK-016 explicitly requires fact/evidence bindings and method/reason codes. The simplified profile facts also hide the `attestation-one` evidence binding that the TASK-015 harness creates. | Extend each expected row (where applicable) with exact fact refs and evidence refs/revisions (or digests/scope) and a method code, and make the harness assert those bindings; keep empty refs explicit for gaps/unknowns. |
| F-02 | High / acceptance-blocking | `tests/fixtures/matrix/README.md:14-22`; all three case objects | The oracle has `as_of` and raw source text but no expected snapshot/version identity. It cannot catch omission or staleness of the profile revision/digest, JD revision/raw and record digests, requirement classification/review revision/view digest, or the TASK-013 alias dictionary version required by TASK-016. | Add a per-case expected snapshot containing the profile, JD, requirement/review and alias versions/digests, computed independently from the loaded private state and compared by the future matrix test. |
| F-03 | High / acceptance-blocking | `tests/fixtures/matrix/README.md:74-82`; all sources in `matrix.json` | The rules specify ALL precedence, but no fixture contains a structured `ConditionGroup(node="all")`. The Python/Java and degree alternatives exercise ANY; condition-plus-duration is not an ALL condition tree. A matrix implementation could therefore get ALL state precedence, fact union or denominator counting wrong while every fixture passes. | Add at least one reviewed ALL case with both a satisfying and a missing/unknown child, and assert row state, first reason, fact union and one-row coverage. Include a mandatory case so a missing child remains visible. |
| F-04 | Medium | `tests/fixtures/matrix/README.md:47-53` | Context precedence is ambiguous: “same concept with a different surface → equivalent” appears before the exposure/study rules. If applied literally, an exposure/study alias could become `equivalent` and count as met. Current rows use exact spellings only (`Kubernetes`, `Docker`), so they do not prove the alias negative. | State that exposure/study context is checked first and is always `adjacent`, regardless of exact or alias surface; add an alias-spelled exposure/study negative case. |
| F-05 | Medium | `tests/fixtures/matrix/README.md:17-24`; duplicate rows at `matrix.json:181-189` and `272-280` | Corrections and `unreviewed` entries are keyed only by quote. Repeated quotes are allowed in the same case, but a quote key cannot select one occurrence if their review state or correction differs. The current duplicate happens to be identical, masking this ambiguity. | Key review actions and expectations by candidate ID/source span or an explicit occurrence index; retain quote as a display assertion. |
| F-06 | Medium / coverage gap | `tests/fixtures/matrix/README.md:58-72`; no corresponding expected rows | The oracle defines but never exercises `term_not_a_language`, `duration_scope_unrecognized`, `threshold_scope_unclear` or a corrected ambiguous technology term (`ambiguous_term`). Those are important matrix unknown paths at the TASK-013/TASK-015 boundary, and the only manual-check row is an unstructured classifier output. | Add small reviewed cases for a non-language language correction, a multi-mention duration scope, an orphan language threshold and an ambiguous technology term, with `unknown` reasons and denominator assertions. |

The arithmetic and current expected states are sound for the three examples, but the omissions above prevent this fixture from serving as a complete TASK-016/A22/A24 oracle or from guarding the required provenance/version contract. Independent review should be repeated after these fixture corrections and before matrix implementation is accepted.
