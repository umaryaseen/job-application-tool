# TASK-015 synthetic constraint and duration oracle

`constraints.json` holds a synthetic applicant (reserved example names, no real
person) and typed constraints with literal expected results. The labels were
authored from TASK-015, A07, A22, A23, ADR-007/011 and ARCHITECTURE ("Matching
and tailoring", "Years of experience", language and authorization rules) and
the rules below, before the evaluator existed. A separate review must approve
them independently of any output.

## Format

- `base_facts`: simplified facts (`fact_id`, `kind`, `status` and the domain
  fields of that kind). The harness builds properly approved revision-1 facts
  for `approved` entries; `draft` and `revoked` entries are present but
  unapproved.
- `cases`: one typed `constraint`, optional `as_of` (default `as_of_default`),
  optional `extra_facts` and `remove_fact_ids`, and `expected`:
  `state`, `rationale`, `fact_ids` (sorted), and for durations `lower_months`,
  `upper_months` and `excluded` (fact ID → reason for candidate facts that could
  not contribute). For a `direct` language, credential, degree or authorization
  result, `fact_ids` are the facts that satisfy the constraint; for any other
  state they are all candidate facts considered (matching language, credential
  name, degree name; every authorization fact). For durations they are the
  facts that contributed at least one upper month.

## States and scope

`direct`, `explicitly_unmet`, `no_evidence`, `unknown`. No state is an
application decision.

A22 is split between two independently reviewed oracles. This one covers the
typed constraints: direct versus explicitly unmet (a CEFR level below the
requirement, an expired, in-progress or not-yet-awarded credential, an ongoing
or withdrawn degree) versus no evidence versus unknown, and that exposure,
self-study, responsibilities and other facts without their own period never
satisfy a duration. TASK-016 covers `equivalent`, `adjacent`, negative
mentions and production/depth semantics of free-text requirements.

"Numeric" means duration thresholds: the requirement model (TASK-012) extracts
only duration and CEFR thresholds. Comparing metric facts (counts, percent,
currency) is not part of TASK-015.

## Rules

1. Only approved facts are evidence. Draft and revoked facts are ignored.
2. Names compare after Unicode NFC, whitespace collapsing and `casefold()`.
   Language identity uses the TASK-013 concept of each whole surface
   (`German` and `Deutsch` are one concept); two unmatched surfaces compare as
   names. Nothing else is inferred.
3. **Language** `{language, min_level}`. No matching fact → `no_evidence` /
   `no_language_fact`. `min_level: null` (level not stated) with a matching
   fact → `unknown` / `required_level_unspecified`. A CEFR fact at or above the
   level → `direct` / `cefr_meets` (A1 < A2 < B1 < B2 < C1 < C2). Otherwise, if
   every matching fact is CEFR and below → `explicitly_unmet` / `cefr_below`;
   if any is a test score or self-description → `unknown` /
   `assessment_not_comparable`. A test score (for example IELTS) is never
   converted to CEFR, a self-description is never parsed (even "C1" or
   "Native"), and native is never C2.
4. **Credential** `{name}`. No matching fact → `no_evidence` /
   `no_credential_fact`. Each matching fact has one outcome: `status: unknown`
   → status unknown; `in_progress` → in progress; `expired` → expired;
   `awarded` → not yet awarded if `awarded_on`'s earliest possible day is
   later than `as_of`, award uncertain if `awarded_on`'s latest possible day is
   later than `as_of` (its period contains `as_of`), expired if past its
   expiry, otherwise valid. Expiry: `expires_at` converted to UTC with its date
   earlier than `as_of`, or `valid_through` whose last day (end of its year,
   month or the day) is earlier than `as_of`. Result, first that applies: any
   valid → `direct` / `credential_valid`; any status unknown → `unknown` /
   `credential_status_unknown`; any award uncertain → `unknown` /
   `award_date_precision`; any in progress → `explicitly_unmet` /
   `credential_in_progress`; any not yet awarded → `explicitly_unmet` /
   `awarded_after_as_of`; otherwise `explicitly_unmet` / `credential_expired`.
5. **Degree** `{degree_name}` against education `degree_name`. No matching fact
   → `no_evidence` / `no_degree_fact`. `ongoing` → `explicitly_unmet` /
   `degree_in_progress`; `withdrawn` → `explicitly_unmet` / `degree_withdrawn`;
   `unknown` → `unknown` / `degree_status_unknown`; `completed` without a
   completion date → `direct` / `degree_completed`; with one, its earliest
   possible day later than `as_of` → `explicitly_unmet` /
   `completed_after_as_of`, its latest possible day on or before `as_of` →
   `direct` / `degree_completed`, otherwise `unknown` / `completion_precision`.
   Several facts: the first rationale that applies in the order
   `degree_completed`, `degree_status_unknown`, `completion_precision`,
   `degree_in_progress`, `completed_after_as_of`, `degree_withdrawn`.
6. **Authorization** `{country, scope}`. Only an exact applicant-approved
   statement can support it; nothing is inferred from location, residence,
   nationality or student status, and absence is never a negative. No
   authorization fact → `unknown` / `authorization_not_recorded`. A fact with
   `status: unknown` → `unknown` / `authorization_status_unknown`. A `known`
   statement matches when its country (and scope, when the constraint states
   one) compare equal. A matching statement whose `as_of` earliest possible day
   is later than the evaluation `as_of` → `statement_after_as_of`; whose `as_of`
   latest possible day is later than the evaluation `as_of` (its period contains
   it) → `statement_date_precision`; an expired one (rule 4 expiry) →
   `authorization_expired_needs_review`; otherwise it is valid. Precedence over
   all facts: any valid matching statement → `direct` /
   `authorization_statement_matches`; else `unknown` with the first that applies
   of `statement_after_as_of`, `statement_date_precision`,
   `authorization_expired_needs_review`, `authorization_status_unknown`,
   `no_matching_authorization_statement`.
7. **Duration** `{months, scope}`, with the threshold already expressed as a
   minimum number of months (converting a TASK-012 threshold's years, months
   and operator is the caller's step and is tested separately), and scope
   `overall` (approved employment),
   `skill` (approved projects whose `technologies` contain a whole surface of
   the concept) or `role` (approved employment whose title equals the text).
   Responsibilities, skills without periods and education never contribute.
   Durations are calendar months, not FTE; part-time roles count as calendar
   time and are never scaled.
   - Month index: `year * 12 + month - 1`.
   - Start: day precision → lower = that month if the day is 1, else the next
     month; upper = that month. Month precision → lower = next month, upper =
     that month. Year precision → lower = January of the next year, upper =
     January of that year.
   - Known end: day precision → lower = that month if the day is the month's
     last day, else the previous month; upper = that month. Month precision →
     lower = previous month, upper = that month. Year precision → lower =
     December of the previous year, upper = December of that year.
   - Ongoing end is the `as_of` day (day precision). For every candidate,
     whether its end is known or ongoing, the lower set is then intersected
     with all months up to the lower end of the `as_of` day and the upper set
     with all months up to the `as_of` month. The cutoff only removes months;
     it never moves a start earlier.
   - Excluded with a reason, checked in this order: unknown start
     (`unknown_start`), unknown end (`unknown_end`), a start whose earliest
     possible day is later than the `as_of` day (`starts_after_as_of`; for a
     day-precision start this is the day itself).
   - Lower and upper results are the sizes of the unions of the month sets
     (overlap counted once, gaps excluded).
   - `lower ≥ months` → `direct` / `duration_meets`. No contributing fact and
     no uncertain exclusion (`unknown_start`, `unknown_end`) → `no_evidence` /
     `no_scoped_interval`. Otherwise `unknown`, first that applies: no
     contributing fact → `only_unknown_dates`; `lower < months ≤ upper` →
     `precision_insufficient`; `upper < months` with an uncertain exclusion →
     `below_threshold_with_unknown_intervals` (an undated interval could close
     the gap); `upper < months` → `documented_below_threshold`. A documented
     total below the threshold is not a negative, because the profile does not
     claim to be complete; duration never yields `explicitly_unmet`.
   - `starts_after_as_of` alone is not uncertainty: with no other candidate the
     result is `no_evidence` / `no_scoped_interval`.

The corpus proves these examples only.
