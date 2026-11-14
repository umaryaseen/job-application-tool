# Review handoff: TASK-012 priority, negation and alternatives

Implementer: Claude Code. Independent reviewer: a separate Codex session (or
another engineer). TASK-011 is merged (`f6a3bf05`); its reviews are complete.
The TASK-012 fixture labels are already independently
[approved](reviews/TASK-012-FIXTURES.md); do not re-derive or change them to fit
output. Review the implementation commit supplied with this handoff.

## Round 8: corrective re-review

Round 7 on `faee434` returned CHANGES REQUIRED for F-15 (F-16 non-blocking).
Re-review `faee434..<candidate>`: all word sets are now case-folded at
construction, with an invariant test. Confirm F-01–F-14 stay as recorded.
Append a "Round 8" section.

## Round 7 (completed)

Round 6 on `12221f7` returned CHANGES REQUIRED for F-13 (F-14 non-blocking).
Re-review `12221f7..<candidate>`: every filler word and connective now ends a
degree field, a dangling field link withholds the degree condition, and
spoken/written/native-style words directly before a recognized language are
covered modifiers. Confirm F-01–F-12 stay as recorded. Append a "Round 7"
section.

## Round 6 (completed)

Round 5 on `d30ecc7` returned CHANGES REQUIRED for F-12 only. Re-review
`d30ecc7..<candidate>`: degree fields stop only at function words/connectives;
content descriptors are no longer global filler and are exempt only as
adjacent degree modifiers or "language" after a recognized language. Probe
whether any remaining FILLER word can form a meaningful operand on its own, and
confirm F-01–F-11 stay as recorded. Append a "Round 6" section.

## Round 5 (completed)

Round 4 on `b91ead6` returned CHANGES REQUIRED for F-11 only. Re-review
`b91ead6..<candidate>`: explicit degree-term grammar, leaf-only coverage and
the early CEFR bound. Confirm F-01–F-10 stay as recorded. The literal field
rule (up to four words, words appended without a separator join the field) is
documented; judge whether it is acceptable. Append a "Round 5" section.

## Round 4 (completed)

Round 3 on `2f43f4f` returned CHANGES REQUIRED for F-09 only (F-10
non-blocking). Re-review `2f43f4f..<candidate>`: stray/contradictory operator
words now withhold all thresholds, and `uninterpreted_text` withholds
thresholds with the condition. Confirm F-01–F-08 stay fixed. Append a
"Round 4" section; do not rewrite earlier rounds.

## Round 3 (completed)

Round 2 on `fbc4c97` returned CHANGES REQUIRED (F-05–F-08). Re-review
`fbc4c97..<candidate>`: the coverage rule (`uninterpreted_text`, filler list),
unit-word and unsupported-operator detection, the scope-word requirement and
the sanitized PROGRESS note. Probe for remaining partial conditions and for
filler-list entries that could themselves hide an operand. Append a "Round 3"
section; do not rewrite earlier rounds.

## Round 2 (completed)

Round 1 on `f41df6b` returned CHANGES REQUIRED (F-01–F-04; see
[the review](reviews/TASK-012.md)). Re-review the corrective delta
`f41df6b..<candidate>`: verify each finding is fixed for its reproduction and
for nearby variants, that the generalized symbol/comma/semicolon,
duration-bound, scope-stop and duplicate-scope rules do not hide other
partial conditions, that controls (CI/CD, "Ideally, Python", supported lists)
still work, that the fixture oracle is byte-identical, and that the
documentation tail (PROGRESS incl. the sanitized TASK-009 state note, guide,
CODEX_HANDOFF harness note) is faithful. Append a "Round 2" section to
`docs/reviews/TASK-012.md` content in your report; do not rewrite round 1.

Base: main `f6a3bf0560df9c3e7594cc835f13864d98c3c6c3`.
Branch: `task/012-requirement-semantics`. Fixture commit `2988f63` precedes the
implementation commit; inspect both with `git diff f6a3bf0..<candidate>`.

## Read first

AGENTS, PROGRESS, TASK-012, A18/A19 (and A17 for spans), ADR-007/011/021, the
"Pasted jobs and requirement model" section of ARCHITECTURE, SECURITY_AND_PRIVACY,
REVIEW_PROTOCOL, JOB_EXTRACTION and the fixture README.

## Review focus

- Labels: explicit EN/DE cue lexicon; general headings carry no priority; cue
  headings and marker lines scope later clauses; clause/heading and mixed-cue
  conflicts stay unspecified with review; a preferred scope never yields
  mandatory; recognized not-required forms versus unsupported negation.
- Groups: ANY/ALL parser (consistent conjunction, either/both/sowohl…als auch,
  parentheses, depth/term bounds), degree-or-equivalent and related-field
  handling, and the rule that any unaccounted OR/AND nulls the condition (never
  split or partially kept). Look for inputs where an OR still yields a partial
  or mandatory single-term condition.
- Thresholds: integer durations and CEFR operators/units/literal scopes,
  vague/decimal/contradictory forms rejected to review.
- Integrity: every span verified against the raw source and inside its clause
  or referenced heading/marker; rows aligned with extraction candidates; binding
  to job revision/raw hash/extraction digest; `validate_classification`
  rejects relabelled, split or invented content even with recomputed digests.
- Bounds and security: adversarial 200,000-byte inputs stay sub-second or fail
  with a bounded `ExtractionError`; read-only `jae job-classify`; sanitized CLI
  errors; no network, execution of posting text, profile access, persistence,
  provider or new dependency. The `load_saved_source` refactor must leave
  TASK-011 `job-extract` behaviour and tests unchanged.
- Scope: no aliases/normalization (TASK-013), no correction versions (TASK-014),
  no matching, tailoring or approval; documentation matches actual behaviour.

## Verification

Runtime: `uv run pytest tests/test_requirement_classification.py
tests/test_requirement_spans.py tests/test_ingestion.py -ra` (in a sandbox, call
`.venv/bin/python -m pytest` with `--basetemp` outside the checkout; data inside
the repository is rejected by design), `uv run ruff check .`,
`uv run ruff format --check .`, `uv run mypy src`, `git diff --check`. Also try
your own adversarial inputs. The full suite needs macOS `sandbox-exec`, Poppler
and the pinned Typst assets; inspect hosted CI for the exact published head
rather than repeating renderer tests in a sandbox that cannot nest them.
Implementer results are in PROGRESS (417 passed locally); they are not a
substitute for your checks.

Record actual commands/results, exact head/tree, findings and one verdict in
`docs/reviews/TASK-012.md` without modifying implementation. Do not merge or
approve applicant facts. TASK-009 personal acceptance and all M1/M2, matching,
tailoring and export gates remain unchanged.
