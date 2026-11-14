# Review handoff: TASK-012 priority, negation and alternatives

Implementer: Claude Code. Independent reviewer: a separate Codex session (or
another engineer). TASK-011 is merged (`f6a3bf05`); its reviews are complete.
The TASK-012 fixture labels are already independently
[approved](reviews/TASK-012-FIXTURES.md); do not re-derive or change them to fit
output. Review the implementation commit supplied with this handoff.

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
tests/test_requirement_spans.py tests/test_ingestion.py -ra`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run mypy src`, `git diff --check`. Also try
your own adversarial inputs. The full suite needs macOS `sandbox-exec`, Poppler
and the pinned Typst assets; inspect hosted CI for the exact published head
rather than repeating renderer tests in a sandbox that cannot nest them.
Implementer results are in PROGRESS (313 passed locally); they are not a
substitute for your checks.

Record actual commands/results, exact head/tree, findings and one verdict in
`docs/reviews/TASK-012.md` without modifying implementation. Do not merge or
approve applicant facts. TASK-009 personal acceptance and all M1/M2, matching,
tailoring and export gates remain unchanged.
