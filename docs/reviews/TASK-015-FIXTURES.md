# TASK-015 fixture oracle review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, sandbox `workspace-write` (read-only review, writes only to a
  temporary directory) on a throwaway detached checkout of `ef9d434`, no
  network, session `01a1e048-abda-7003-aa96-5dd55e76edf0`. Tracked files
  unchanged; exit 0.
- The report below is verbatim. Its findings are addressed by the next commit
  (revised rules and 23 new cases) for round 2.

## Round 1 report

VERDICT: CHANGES REQUIRED

# TASK-015 independent fixture-oracle review

- Reviewer: Codex, independent fixture reviewer; the fixture author is Claude Code.
- Date: 2026-11-15.
- Base: `e88546e57ca01a6052c24b2539ae45272e1993db`.
- Candidate: `ef9d4340489c2111647b7dd71d5588c6a21bf15a` (detached checkout; clean at review).
- Scope: `tests/fixtures/matching/README.md` and `tests/fixtures/matching/constraints.json`, with the requested handoff, task, acceptance, architecture, ADR, domain-model and normalization files read for context. No evaluator code was present. The checkout was read-only; no network or private data directory was accessed.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git rev-parse HEAD^` | 0 | `e88546e57ca01a6052c24b2539ae45272e1993db` |
| `git rev-parse HEAD` | 0 | `ef9d4340489c2111647b7dd71d5588c6a21bf15a` |
| `git status --porcelain=v1` | 0 | Empty; no tracked or untracked changes in the checkout. |
| `git diff --check HEAD^ HEAD` | 0 | No whitespace errors. |
| `git diff --name-status HEAD^ HEAD` | 0 | Handoff plus the two intended fixture files; no implementation code. |
| `python3 -m json.tool tests/fixtures/matching/constraints.json >/dev/null` | 0 | JSON parses. |
| `python3 /private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-015-fx-tmp/recompute.py` | 0 | Independent standard-library evaluator: 65 cases, 0 mismatches. The script was written for this review and did not import repository matching code. |
| Independent corpus-shape/synthetic scan (standard-library Python) | 0 | 65 unique case IDs, 25 unique base fact IDs, valid JSON; no email, URL, or person-name literals; only synthetic identifiers/labels. |
| `python3 -m pytest --version` | 1 | Pytest is unavailable in this checkout. No TASK-015 evaluator exists to run. |
| `uv --version` | 127 | `uv` is unavailable; no dependency installation was attempted. |

## Independent recomputation

The script applied the README rules directly: NFC/whitespace/casefold name comparison, concept-level German/Deutsch identity, approved-status filtering, CEFR ordering without test-score or self-description conversion, UTC expiry and valid-through boundaries, completion-date precision, authorization as-of/expiry precedence, and month-set lower/upper unions. It compared the complete expected object, including state, rationale, fact IDs, lower/upper months and exclusions, for every row.

The corpus contains 14 language, 14 credential, 9 degree, 10 authorization and 18 duration cases. All 65 expected objects agree with that independent recomputation. The state coverage is:

| Type | Cases | States present |
|---|---:|---|
| Language | 14 | direct 4; explicitly_unmet 4; unknown 5; no_evidence 1 |
| Credential | 14 | direct 6; explicitly_unmet 6; unknown 1; no_evidence 1 |
| Degree | 9 | direct 2; explicitly_unmet 4; unknown 2; no_evidence 1 |
| Authorization | 10 | direct 4; unknown 6 |
| Duration | 18 | direct 7; unknown 7; no_evidence 4 |

The duration rows recompute as follows. `lower/upper` are the sizes of independently enumerated month unions; `facts` are those with at least one upper-bound month, and `excluded` lists candidates that cannot contribute under the written rules.

| Case | State / rationale | Lower / upper | Facts | Excluded |
|---|---|---:|---|---|
| `dur-overall-5y` | direct / duration_meets | 83 / 86 | emp-a, emp-b, emp-c | emp-d: unknown_start |
| `dur-overall-7y-overlap-counted-once` | unknown / precision_insufficient | 83 / 86 | emp-a, emp-b, emp-c | emp-d: unknown_start |
| `dur-overall-8y-below` | unknown / documented_below_threshold | 83 / 86 | emp-a, emp-b, emp-c | emp-d: unknown_start |
| `dur-overall-pinned-as-of` | direct / duration_meets | 12 / 13 | emp-a | emp-b: starts_after_as_of; emp-c: starts_after_as_of; emp-d: unknown_start |
| `dur-overall-only-unknown-dates` | unknown / only_unknown_dates | 0 / 0 | — | emp-a/b/c: starts_after_as_of; emp-d: unknown_start |
| `dur-python-meets` | direct / duration_meets | 13 / 15 | proj-1, proj-3 | proj-4: unknown_start |
| `dur-python-below` | unknown / documented_below_threshold | 13 / 15 | proj-1, proj-3 | proj-4: unknown_start |
| `dur-sql-meets-unknown-end-excluded` | direct / duration_meets | 10 / 12 | proj-1 | proj-6: unknown_end |
| `dur-sql-precision` | unknown / precision_insufficient | 10 / 12 | proj-1 | proj-6: unknown_end |
| `dur-pytorch-precision` | unknown / precision_insufficient | 10 / 12 | proj-2 | — |
| `dur-deep-learning-is-not-pytorch` | no_evidence / no_scoped_interval | 0 / 0 | — | — |
| `dur-kubernetes-none` | no_evidence / no_scoped_interval | 0 / 0 | — | — |
| `dur-docker-only-unknown` | unknown / only_unknown_dates | 0 / 0 | — | proj-5: unknown_start |
| `dur-role-exact` | direct / duration_meets | 33 / 34 | emp-b | — |
| `dur-role-normalized` | direct / duration_meets | 33 / 34 | emp-b | — |
| `dur-role-senior-not-inferred` | no_evidence / no_scoped_interval | 0 / 0 | — | — |
| `dur-role-starts-after-as-of` | no_evidence / no_scoped_interval | 0 / 0 | — | emp-c: starts_after_as_of |
| `dur-part-time-is-calendar-time` | direct / duration_meets | 36 / 38 | emp-c | — |

The key union checks are consistent: overall employment intervals produce 83 lower and 86 upper months after counting the emp-a/emp-b overlap once and retaining the gap before emp-c; Python projects produce 13/15 after counting the proj-1/proj-3 overlap once; SQL and PyTorch each produce 10/12; the exact Software Engineer role produces 33/34; the ongoing Working Student interval at the default as-of date produces 36/38; and the pinned 2019-01-31 overall case produces 12/13. Draft `emp-x`, draft `lang-it`, and revoked `lang-es2` never contribute.

The language, credential, degree and authorization labels also follow the written rules: IELTS and self-descriptions remain non-comparable, `Native` is not C2, CEFR below-level cases are explicitly unmet, credential expiry and in-progress states are preserved, year-level degree completion is unknown until its latest possible date has passed, authorization is unknown when absent or expired, and the Berlin location does not authorize Germany. No row infers seniority, FTE, authorization, language level, or overlapping experience.

## Findings

| ID | Severity | Location | Finding | Suggested correction |
|---|---|---|---|---|
| F-01 | high | `docs/tasks/TASK-015.md:21-29`; `docs/ACCEPTANCE_CRITERIA.md:48`; `tests/fixtures/matching/README.md:26-29` | A22 is not represented by this oracle. There are no negative requirement/skill cases, no adjacent state, and no project-exposure-versus-production/depth case. The README explicitly defers `adjacent` to TASK-016, while the acceptance matrix assigns A22 to TASK-015 and TASK-016. The current JSON has only typed language, credential, degree, authorization and duration constraints, so an implementation could pass this oracle while violating the required match-state distinctions. | Add a linked A22 fixture slice with direct, no-evidence, explicit-negative and adjacent rows, including an approved project exposure that cannot meet a production/depth requirement; or explicitly split A22 between two independently reviewed oracles and remove any claim that this TASK-015 oracle covers the full criterion. |
| F-02 | high | `docs/tasks/TASK-015.md:21-29`; `src/job_application_engine/domain/fact.py:54-83,273-275`; all `constraint.type` values in `constraints.json` | The acceptance says “numeric constraints,” but the oracle defines only duration-month thresholds. It contains no typed metric/unit/operator/context case (for example percent versus percentage points, currency, count, or a scoped period), and no numeric unknown/unmet case outside duration. The task scope is therefore ambiguous: either MetricFact-style numeric matching is required and untested, or “numeric” must be explicitly narrowed to duration. | Add synthetic numeric cases bound to the supported domain fields, with wrong unit/scope, missing metric, explicit below-threshold and unknown states; or amend TASK-015 and this README to state that numeric means only duration thresholds and identify the deferred metric-matching task. |
| F-03 | high | `tests/fixtures/matching/README.md:85-98,108-109` | The as-of cap is underspecified and has a false-result implementation hazard. “Every lower month is capped” can be read as clamping a start bound down to the as-of cutoff. For a known interval beginning on (for example) 2026-11-20 and evaluated on 2026-11-15, that mistake creates a lower October month and can yield `direct`, although no work has occurred by the as-of day. The exclusion rule checks only whether the upper start month is after the as-of month, so it does not settle this same-month day boundary. | Define lower and upper month sets as the possible interval sets intersected with the respective as-of cutoffs; never move a start earlier when applying a cap. Add a day-precision start-after-as-of-day/same-month case and the corresponding end boundary, with expected uncertainty/no-evidence semantics. |
| F-04 | medium | `tests/fixtures/matching/README.md:78-83,85-92`; `constraints.json:4-81,103-126` | A23 requires precision and scope exclusions, but no duration contributor uses year precision, and the corpus has no ResponsibilityFact, SkillFact without a period, or EducationFact candidate to prove those exclusions. Month/day bounds, overlap, gaps, ongoing dates and unknown endpoints are covered; this important part of the stated domain contract is not. | Add synthetic year-precision start/end rows, plus duration queries containing responsibility, periodless skill and education facts. Assert they cannot contribute and that year-bound lower/upper sets preserve uncertainty. |
| F-05 | medium | `tests/fixtures/matching/README.md:101-107`; `constraints.json:1316-1337,1413-1434` | `dur-overall-8y-below` and `dur-python-below` report `unknown` but use `documented_below_threshold` while an excluded unknown-start project/employment could add arbitrary months and close the threshold gap. The state is safely not a negative, but the rationale code does not say whether uncertain exclusions were considered and could be implemented as a misleading “known below” result. | Define rationale precedence for uncertain exclusions and add a case where an unknown interval could satisfy the threshold. Prefer an explicit uncertainty rationale (or document that `documented_below_threshold` means only the supported subset) while retaining `unknown` and never emitting `explicitly_unmet`. |
| F-06 | medium | `tests/fixtures/matching/README.md:20-24,47-77`; degree/language/credential/authorization cases in `constraints.json` | The stated precedence and `fact_ids` contract are not fully exercised. There is no multi-fact degree case for direct-versus-unknown/unmet precedence, no CEFR-meets plus non-comparable language combination, and no credential/authorization mixtures involving valid, expired, unknown and mismatched candidates. Since non-direct results are supposed to retain all candidate IDs while direct results retain only satisfying IDs, these combinations are necessary to prevent silent ID loss or precedence drift. | Add multi-candidate rows for each precedence family and assert both state/rationale and exact sorted IDs. Define whether an unrelated unknown authorization fact participates in the candidate set before applying the stated precedence. |
| F-07 | medium | `src/job_application_engine/domain/fact.py:124-130`; `tests/fixtures/matching/README.md:47-55` | `CredentialValue` has an optional `awarded_on` date, but credential evaluation only checks `status` and expiry. A credential marked `awarded` with an award date after the evaluation as-of date would be labelled valid/direct under the written rule. This is inconsistent with the date-bound handling already specified for degree completion and authorization statements, and the boundary is untested. | Define future-award behavior using the date precision rules (future means not yet available; an interval containing the as-of date remains uncertain), add year/month/day boundary cases, and include the selected rationale/state in this oracle. |

## Architecture, safety and synthetic-data assessment

The positive parts are sound: approved facts are required; draft/revoked records are ignored; language assessments are typed and never converted; authorization is exact and never inferred from residence/location/nationality; role text does not upgrade seniority; part-time duration is calendar time without FTE scaling; and interval unions count overlap once while preserving gaps and unknown dates. All literals are synthetic (`synthetic-person`, `synthetic-employer`, `synthetic-project`, synthetic credential/education names); no applicant names, contacts, URLs, secrets or external source captures appear. The report does not approve an implementation or any applicant facts.

The high findings must be resolved in the fixture/rules before implementation can use this file as a complete TASK-015 oracle. After corrections, rerun the independent recomputation, JSON/invariant checks and the eventual focused evaluator; then request a fresh independent review of the new commit.

## Round 2 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, read-only review (writes only to a temporary directory) of a
  throwaway detached checkout of `5bf2123`, no network, session
  `01a1e057-05ec-7f93-871d-dacf218dca9c`. Tracked files unchanged; exit 0.
- The report below is verbatim, except that 3 header lines ending in Markdown
  hard-break spaces were turned into list items for whitespace checks.
  Follow-ups F-01..F-03 are applied in the next
  commit (authorization statement-date precision with month/year cases; the
  months-only duration API stated and a tested threshold adapter; the as-of
  intersection stated for known ends with a non-last-day boundary case) and
  are checked in the implementation review.

## Round 2 report

VERDICT: APPROVED WITH FOLLOW-UP

# TASK-015 fixture oracle review, round 2

- Reviewer: Codex independent fixture reviewer, separate from the Claude Code fixture author.
- Date: 2026-11-15.
- Commit reviewed: `5bf2123286f1729e61911730ad761bba029e3b8a` (detached checkout).
Review scope: `tests/fixtures/matching/README.md` and `tests/fixtures/matching/constraints.json`, read against `docs/REVIEW_HANDOFF.md`, `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, TASK-015, A07/A22/A23, ADR-007, ADR-011, the matching/tailoring and typed-fact sections of `docs/ARCHITECTURE.md`, `fact.py`, `common.py`, and the normalization modules. No evaluator exists in this checkout.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git status --porcelain=v1` | 0 | Clean checkout; no tracked or untracked changes. |
| `git rev-parse HEAD` | 0 | Reviewed commit is `5bf2123286f1729e61911730ad761bba029e3b8a`. |
| `git diff --check HEAD^ HEAD` | 0 | No whitespace errors. |
| `git diff --name-status HEAD^ HEAD` | 0 | Handoff/review documentation, TASK-015 clarification, README and constraints fixture only; no implementation code. |
| `python3 -m json.tool tests/fixtures/matching/constraints.json >/dev/null` | 0 | JSON parses. |
| `python3 /private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-015-fx2-tmp/recompute_round2.py` | 0 | Independent standard-library evaluator; all 88 complete expected objects matched, 0 mismatches. It did not import repository matching code. |
| `python3 /private/tmp/claude-501/-Users-apple-Desktop-webapps-job-application-engine-handoff-job-application-engine/a06068fd-ae2e-442d-9995-10755a74803d/scratchpad/codex-015-fx2-tmp/scan_round2.py` | 0 | 88 unique case IDs, 25 unique base fact IDs, sorted fact-ID assertions, valid synthetic scan, no email or URL. |
| `python3 -m pytest --version` | 1 | Pytest is unavailable (`No module named pytest`); no TASK-015 evaluator can be run. |
| `uv --version` | 127 | `uv` is unavailable; no dependency installation was attempted. |

The review read no private data directory, home directory, other worktree, or network resource. The only generated files are the two reviewer scripts and this report under the permitted temporary directory.

## Independent recomputation

The script independently applied the written rules: NFC/whitespace/casefold name matching; German/Deutsch concept identity; approved-only filtering; CEFR ordering without IELTS, native, or self-description conversion; credential UTC-expiry and valid-through boundaries; awarded-date earliest/latest precision; degree completion precision and precedence; authorization matching, as-of and expiry precedence; and per-interval lower/upper month sets intersected with the as-of cutoffs before unioning. It compared state, rationale, sorted `fact_ids`, all duration bounds, and every exclusion for every row.

The 88 cases break down as follows:

| Constraint family | Cases | Direct | Explicitly unmet | Unknown | No evidence |
|---|---:|---:|---:|---:|---:|
| Language | 15 | 5 | 4 | 5 | 1 |
| Credential | 21 | 8 | 8 | 4 | 1 |
| Degree | 12 | 3 | 5 | 3 | 1 |
| Authorization | 12 | 4 | 0 | 8 | 0 |
| Duration | 28 | 10 | 0 | 12 | 6 |

The expected duration results recomputed as follows. A dash means an empty list/map.

| Case | State / rationale | Lower/upper months | Contributing facts | Exclusions |
|---|---|---:|---|---|
| `dur-overall-5y` | direct / duration_meets | 83/86 | emp-a, emp-b, emp-c | emp-d: unknown_start |
| `dur-overall-7y-overlap-counted-once` | unknown / precision_insufficient | 83/86 | emp-a, emp-b, emp-c | emp-d: unknown_start |
| `dur-overall-8y-below` | unknown / below_threshold_with_unknown_intervals | 83/86 | emp-a, emp-b, emp-c | emp-d: unknown_start |
| `dur-overall-pinned-as-of` | direct / duration_meets | 12/13 | emp-a | emp-b: starts_after_as_of; emp-c: starts_after_as_of; emp-d: unknown_start |
| `dur-overall-only-unknown-dates` | unknown / only_unknown_dates | 0/0 | — | emp-a/b/c: starts_after_as_of; emp-d: unknown_start |
| `dur-python-meets` | direct / duration_meets | 13/15 | proj-1, proj-3 | proj-4: unknown_start |
| `dur-python-below` | unknown / below_threshold_with_unknown_intervals | 13/15 | proj-1, proj-3 | proj-4: unknown_start |
| `dur-sql-meets-unknown-end-excluded` | direct / duration_meets | 10/12 | proj-1 | proj-6: unknown_end |
| `dur-sql-precision` | unknown / precision_insufficient | 10/12 | proj-1 | proj-6: unknown_end |
| `dur-pytorch-precision` | unknown / precision_insufficient | 10/12 | proj-2 | — |
| `dur-deep-learning-is-not-pytorch` | no_evidence / no_scoped_interval | 0/0 | — | — |
| `dur-kubernetes-none` | no_evidence / no_scoped_interval | 0/0 | — | — |
| `dur-docker-only-unknown` | unknown / only_unknown_dates | 0/0 | — | proj-5: unknown_start |
| `dur-role-exact` | direct / duration_meets | 33/34 | emp-b | — |
| `dur-role-normalized` | direct / duration_meets | 33/34 | emp-b | — |
| `dur-role-senior-not-inferred` | no_evidence / no_scoped_interval | 0/0 | — | — |
| `dur-role-starts-after-as-of` | no_evidence / no_scoped_interval | 0/0 | — | emp-c: starts_after_as_of |
| `dur-part-time-is-calendar-time` | direct / duration_meets | 36/38 | emp-c | — |
| `dur-day-start-after-as-of-same-month` | no_evidence / no_scoped_interval | 0/0 | — | emp-intern: starts_after_as_of |
| `dur-day-start-before-as-of-same-month` | unknown / precision_insufficient | 0/1 | emp-trainee | — |
| `dur-known-end-after-as-of-is-cut` | direct / duration_meets | 2/3 | emp-contract | — |
| `dur-year-precision-short` | unknown / precision_insufficient | 0/24 | emp-ra | — |
| `dur-year-precision-meets` | direct / duration_meets | 36/60 | emp-le | — |
| `dur-year-precision-uncertain` | unknown / precision_insufficient | 36/60 | emp-le | — |
| `dur-python-periodless-facts-never-add-time` | direct / duration_meets | 13/15 | proj-1, proj-3 | proj-4: unknown_start |
| `dur-exposure-skill-is-not-duration` | no_evidence / no_scoped_interval | 0/0 | — | — |
| `dur-pytorch-documented-below` | unknown / documented_below_threshold | 10/12 | proj-2 | — |
| `dur-role-documented-below` | unknown / documented_below_threshold | 33/34 | emp-b | — |

The typed rows also matched exactly. In particular, the corpus exercises CEFR below/equal/above and unspecified levels; IELTS and self-description without conversion; draft/revoked filtering; credential expiry, timezone conversion, in-progress, unknown, and future award precision; degree ongoing/completed/withdrawn/unknown and multi-fact precedence; authorization scope/country, absence, location non-inference, status unknown, expiry and as-of; and direct-result versus non-direct `fact_ids` semantics.

The interval arithmetic is consistent: employment unions are 83/86 after counting emp-a/emp-b overlap once and retaining the gap before emp-c; Python projects are 13/15 after counting proj-1/proj-3 overlap once; SQL and PyTorch are 10/12; Software Engineer is 33/34; the ongoing Working Student is 36/38; year-precision contributors produce 0/24 and 36/60; and the pinned 2019-01-31 case is 12/13. No interval is summed twice, and no period-less responsibility, skill, study, exposure, or education fact adds time.

## Findings

| ID | Severity | Location | Finding | Suggested correction |
|---|---|---|---|---|
| F-01 | medium | `tests/fixtures/matching/README.md:84-96`; `src/job_application_engine/domain/common.py:30-56`; authorization cases | Authorization `as_of` precision is only defined for the case where its earliest possible day is later than the evaluation date. A month/year statement whose possible interval contains the evaluation date has no rule or fixture. This is inconsistent with the explicit interval-precision treatment for credential awards and degree completion and can let a statement become `direct` while its effective date may be later than `as_of`. | Define the containing-interval result explicitly (prefer an `unknown` precision rationale unless earliest-only semantics are deliberate), then add month and year boundary cases. |
| F-02 | medium | `tests/fixtures/matching/README.md:97-115`; `src/job_application_engine/domain/requirement.py:133-168` | The fixture constraint is `{months, scope}` only, while TASK-012's duration threshold model accepts integer `years` or `months` and operators (`gte`, `gt`, `range`, `unqualified`). No case or rule says that this oracle receives thresholds pre-normalized to months, so an implementation can pass all 28 duration rows while mishandling a `5 years` or non-default operator requirement. | Either state that the fixture API is pre-normalized to `months` and add an adapter test such as 5 years → 60 months, or extend the fixture constraint and expected semantics to carry unit/operator cases. |
| F-03 | low | `tests/fixtures/matching/README.md:112-115`; `constraints.json:dur-known-end-after-as-of-is-cut` | The expected 2/3-month result for a known interval ending 2026-11-30 evaluated on 2026-11-15 requires the as-of intersection to cap known ends as well as ongoing ends. The prose starts this rule with “Ongoing end is the as_of day” and does not explicitly say that the subsequent lower/upper intersection applies to every known-end interval. | Say directly that every candidate's lower and upper sets, including known ends, are intersected with the lower/upper as-of cutoffs; retain the current known-end case and add a known non-last-day end boundary. |

These are bounded rule/coverage follow-ups; they do not change any current expected object. The round-one findings about A22 scope, duration uncertainty rationale, year-precision contributors, period-less exclusions, multi-fact precedence, and future credential awards are addressed in this revision.

## Architecture, factuality, security and synthetic-data assessment

The rules preserve the required safety boundaries. Only approved facts contribute; draft and revoked facts are ignored. IELTS, native/self-description, residence/location/nationality, role wording, and “Working Student” do not manufacture CEFR level, authorization, seniority, or FTE. Overlapping intervals are unioned once, gaps are not bridged, and incomplete dates yield uncertainty or no evidence rather than a negative. Credential and degree states are explicit facts; duration below a documented threshold remains `unknown`, never `explicitly_unmet`.

The fixture is synthetic: subject and entity identifiers are `synthetic-*`, labels use synthetic employers/projects/credentials/schools, and the scan found no email address, URL, or personal name. No secrets, source captures, or applicant records are present.
