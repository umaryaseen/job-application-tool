# TASK-016 synthetic evidence-matrix oracle

`matrix.json` holds synthetic job postings (reserved example names), reviewer
corrections, a synthetic applicant and the literal expected matrix rows and
coverage. The labels were authored from TASK-016, A22, A24, ADR-005/006/007/011,
ARCHITECTURE ("Matching and tailoring"), the reviewed TASK-012/013/014/015
behaviour and the rules below, before the matrix existed. A separate review
must approve them independently of any output.

## Format

- `profile_facts`: simplified approved facts, built by the harness as in the
  TASK-015 oracle (`tests/fixtures/matching/README.md`); every approved fact
  cites evidence `attestation-one` revision 1. A case may add
  `profile_extra_facts`.
- `cases`: `source` (a job posting, ingested as revision 1 of job
  `synthetic-match`), `as_of`, and `review`. Review actions address a row by
  `quote` and `occurrence` (1-based among rows with that quote, in source
  order): `unreviewed` lists rows left unreviewed; every other requirement row
  is accepted, acknowledging exactly its displayed review reasons, after the
  operations in `corrections` for that row: `set_priority`; `set_condition`
  with one term `{term_kind, quote}` (the span of that quote inside the row);
  `set_thresholds` with duration thresholds `{measure: duration, operator,
  value, unit, quote}` or language-level thresholds `{measure: language_level,
  operator, level, quote}`, all without scope. All operations go into one
  correction, so the reviewed state is review revision 1 (0 if nothing is
  reviewed).
- `expected.rows` lists the matrix rows in source order. Each row has
  `quote`, `state`, `reason`, `method`, `priority`, `fact_refs` and
  `evidence_refs` (sorted `[id, revision]` pairs; evidence refs are the union
  of the cited facts' evidence), `parts` (each `{kind, quote, state, reason,
  method, fact_refs}`) and, for a counted-once repeat, `duplicate_of_index`.
  `expected.excluded` maps quotes to reasons, `expected.coverage` holds the
  class counts and `expected.snapshot` the literal version fields; the profile,
  job record, raw-text, classification and review-view digests must equal
  those of the loaded profile and replayed review.
- Methods: a technology part is `alias_lexicon`; a language or duration part
  is `constraint`; education, equivalence and unclaimed threshold parts are
  `not_evaluated`. A row's method is its single part's method, `combined` for
  several parts, and `not_evaluated` for an unreviewed or manual-check row
  (which has no parts).

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
  normalized text. Per matching surface, checked in this order: a skill with
  context `exposure` → `adjacent` (`exposure_only`) and `study` → `adjacent`
  (`self_study_only`), whether the surface is exact or an alias; otherwise (a
  skill with context `used` or `unknown`, or a project) a normalized surface
  equal to the quote's → `direct` (`exact_match`), a different surface of the
  same concept → `equivalent` (`alias_match`). A skill or project technology
  whose concept has a typed TASK-013 relation with the quote's concept (either
  direction) → `adjacent` (`related_concept`). The term takes the best of
  `direct`, `equivalent`, `adjacent`, else `no_evidence` (`no_matching_fact`);
  its facts are all facts at that level, and its reason is the first
  applicable code in the order `exact_match`, `alias_match`, `exposure_only`,
  `self_study_only`, `related_concept`. Responsibilities, descriptions and
  skill notes never count.
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
