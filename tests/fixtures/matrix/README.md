# TASK-016 synthetic evidence-matrix oracle

`matrix.json` holds synthetic job postings (reserved example names), reviewer
corrections, a synthetic applicant and the literal expected matrix rows and
coverage. The labels were authored from TASK-016, A22, A24, ADR-005/006/007/011,
ARCHITECTURE ("Matching and tailoring"), the reviewed TASK-012/013/014/015
behaviour and the rules below, before the matrix existed. A separate review
must approve them independently of any output.

## Format

- `profile_facts`: simplified approved facts, built by the harness as in the
  TASK-015 oracle (`tests/fixtures/matching/README.md`).
- `cases`: `source` (a job posting, ingested as revision 1), `as_of`, and
  `review`: `unreviewed` (row quotes left unreviewed; every other requirement
  row is accepted, acknowledging exactly its displayed review reasons) and
  `corrections` (per row quote, operations applied before the accept):
  `set_priority`, `set_condition` with one term `{term_kind, quote}` (the span
  of that quote inside the row), and `set_thresholds` with duration thresholds
  `{operator, value, unit, quote}` (no scope). `expected` holds `rows` (keyed
  by row quote, in source order; repeated quotes appear in order),
  `excluded` (quote → reason) and `coverage`.
- A row expectation: `state`, `reason`, `priority`, `fact_ids` (sorted) and,
  for a repeated requirement, `duplicate_of_index` (the index of the counted
  row).

## Row gating

Only rows whose role is `requirement` are matrix rows. A reviewed negated row
(`gate: not_required`) is excluded with reason `requirement_negated`; priority
markers and non-requirements are excluded with reason `not_a_requirement`.
An unreviewed row is `unknown` / `requirement_unreviewed` (its evidence is not
evaluated). A reviewed row without structure or with an uninterpreted negation
(`gate: manual_check`) is `unknown` / `manual_check_required`. Other reviewed
rows are evaluated from their condition and thresholds.

## Evaluating parts

A row's parts are its condition tree and its duration thresholds; a
language-level threshold belongs to the language term whose quote names the
same language (TASK-013 language concept, or equal normalized text).

- **Technology term.** The quote's whole-surface TASK-013 mention:
  ambiguous → `unknown` / `ambiguous_term`. Evidence facts are approved skill
  facts (by `name`) and approved projects (by any `technologies` entry), each
  compared by whole surface: same concept, or for an unmatched quote the same
  normalized text. Per evidence fact: a skill with context `used` or
  `unknown`, or a project, whose normalized surface equals the quote's →
  `direct` (`exact_match`); same concept with a different surface →
  `equivalent` (`alias_match`); a skill with context `exposure` →
  `adjacent` (`exposure_only`); `study` → `adjacent` (`self_study_only`); a
  skill or project technology whose concept has a typed TASK-013 relation with
  the quote's concept (either direction) → `adjacent` (`related_concept`). The
  term takes the best of `direct`, `equivalent`, `adjacent`, else
  `no_evidence` (`no_matching_fact`); its facts are those at that level, and
  its reason is the first applicable code in the order listed. Responsibilities,
  descriptions and skill notes never count.
- **Language term.** TASK-015 language constraint with the attached
  threshold's level (`gte`, `unqualified` → that level; `range` → the lower
  level) or no level. Its state and rationale are used, except that a `direct`
  result whose satisfying facts all name the language with a different
  normalized surface than the quote is `equivalent`. A quote that is not a
  language (TASK-015 rejects it) → `unknown` / `term_not_a_language`.
- **Education term** → `unknown` / `education_not_evaluated`.
  **Equivalent experience or qualification term** → `unknown` /
  `equivalence_requires_review`.
- **Duration threshold.** Minimum months by TASK-015 `months_from_threshold`.
  No scope → overall; a scope containing exactly one matched non-language
  TASK-013 mention (scan) → that skill; anything else → `unknown` /
  `duration_scope_unrecognized`. Otherwise the TASK-015 state and rationale.
- A language-level threshold that no language term claims → `unknown` /
  `threshold_scope_unclear`.

## Combining

ANY group, first that applies: any `direct`; any `equivalent`; any `unknown`;
any `adjacent`; any `no_evidence`; otherwise `explicitly_unmet`.
ALL group (and a row's condition with its duration parts), first that applies:
any `explicitly_unmet`; any `no_evidence`; any `adjacent`; any `unknown`; any
`equivalent`; otherwise `direct`. The row's reason is the reason of the first
part, in condition-tree order followed by duration thresholds, whose state is
the row's state. Its facts are the sorted union of every part's facts.

## Coverage

Classes are the row priorities (`mandatory`, `preferred`, `unspecified`; the
draft priority for an unreviewed row). Each row counts once; an ANY/ALL group
is one row. For a rule-observed duplicate group only the first member in source
order counts; the others name it. Per class: `total`, `met` (`direct` +
`equivalent`) and each state count; `coverage` is `"met/total"`, or `"N/A"`
when `total` is 0. Unknown rows stay in the denominator. Classes are reported
separately; there is no combined score.

The corpus proves these examples only.
