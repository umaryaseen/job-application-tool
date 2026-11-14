# Inspect draft requirements in a saved job

TASK-011 adds local, deterministic source annotations. Save the vacancy first
using [job intake](JOB_INTAKE.md), then run:

```bash
uv run jae job-extract --job-id example-ai-role
uv run jae job-extract --job-id example-ai-role --revision 1
```

The command verifies the saved revision and prints JSON. It does not change job
files, save an analysis revision or create requirement approvals. No applicant
profile, model service or network request is used. Missing/tampered input or
analysis limits produce exit 2 without a partial result.

## Reading the result

Each candidate has a literal source quote, half-open `[start,end)` Unicode
codepoint offsets, section reference, draft kind and lexical surface hints.
Offsets refer to `job_description.raw.txt`, including original CRLF, combining
characters and BOM positions. They are not UTF-8 byte or grapheme offsets.
Normalization in the separate Markdown file does not change the quote source.

The result binds the job ID/revision, record digest, raw hash, supplied locale
and rules version. Candidate IDs distinguish repeated occurrences and change
when the job record changes. The analysis digest is deterministic for the same
record and rules. Structural validation checks exact quotes, IDs, placement and
checksums; it does not certify the meaning of the posting.

Every candidate stays `draft`, `needs_review: true`, and
`priority: unspecified`. This includes text containing required/preferred cues
or negation. Priority/negation/alternatives interpretation belongs to TASK-012;
source-bound review/correction versions belong to TASK-014. A kind such as
`language` marks a lexical candidate, not a positive mandatory condition.

Recognized responsibility sections produce `responsibility` candidates.
Benefits and company-context sections produce `context`, even when they mention
technologies or languages. Other clauses can be technology, education, language,
experience or ambiguous. Multiple different hint kinds stay ambiguous. Unknown
explicit headings reset context; unknown prose is retained rather than discarded.
An OR clause stays one clause; hints are not separate requirements or groups.

## Bounds and limits

The existing intake limit is 200,000 UTF-8 bytes. Analysis permits at most
2,048 structural spans (headings plus clauses) and 4,096 lexical hints in total.
Exceeding either fails the entire analysis; it never silently truncates a job.
Blank lines, bullet markers and recognized heading structure guide splitting;
soft-wrapped prose and common EN/DE abbreviations are preserved.

Section cues and technology/language/education surface hints use a small
explicit allowlist. They are not a canonical skill ontology, language detector,
general NLP parser or numeric-constraint interpreter. Unknown technologies and
complex grammar can remain ambiguous. An independently reviewed 16 EN/16 DE
synthetic corpus and adversarial span/CLI tests cover the stated examples, not
general language accuracy.

[ADR-021](adr/ADR-021.md) permits this source-only implementation while personal
CV acceptance is open. Full M1/M2 release, career matching, tailoring and export
retain their gates. Employer text never becomes career evidence. Stored source
URLs remain metadata; later link/fetch features must validate allowed schemes.

## Classify priority, negation and alternatives

TASK-012 interprets the same candidates with a second deterministic layer:

```bash
uv run jae job-classify --job-id example-ai-role
uv run jae job-classify --job-id example-ai-role --revision 1
```

The command re-verifies the saved revision, rebuilds the TASK-011 extraction
and prints JSON bound to its job record, raw hash and `extraction_digest`. It is
read-only like `job-extract` and uses no profile, model, network or new
dependency. Oversized annotation counts fail with exit 2 instead of truncating.

Each candidate row keeps its literal quote and adds:

- `role`: `requirement`, `priority_marker` (a standalone line such as
  `Nice to have` that scopes later lines) or `non_requirement`
  (responsibility/benefit/company-context text, never prioritized).
- `priority` (`mandatory`, `preferred`, `unspecified`) with a fixed `basis`
  code and every `cues` span used. Only explicit EN/DE cue words decide
  priority. General headings such as Requirements or Ihr Profil supply none;
  headings or marker lines containing a cue apply only to clauses without
  their own cue. Disagreement between clause and heading, or mandatory plus
  preferred/not-required cues in one clause, yields `unspecified` and review.
  A preferred section never becomes mandatory.
- `negation`: `requirement_negated` for recognized forms such as
  "German not required", "kein Muss" or "Keine Deutschkenntnisse erforderlich"
  (the condition then names what is *not* required); any other negation word
  is `unsupported` and needs review.
- `condition`: a literal term or `any`/`all` tree. Supported grammar is
  recognized technology/language terms joined by commas and one consistent
  conjunction (or/oder/and/or/und/oder → `any`; and/und/sowie → `all`),
  explicit either…or / both…and / sowohl…als auch / parentheses for nesting,
  and `<degree> or equivalent experience/qualification` (oder vergleichbare …)
  as one `any` group. A degree term is explicit grammar only: consecutive
  education words, optionally `in/of/der/des/im` plus a field of at most four
  words (stopping at filler words, connectives or punctuation), optionally
  "or a related field" directly after. The field is taken literally, so words
  appended to it without any separator count as part of the field name; any
  other text after the term is outside it. If any OR/AND in the clause is outside that
  grammar — or a `/`, `|`, `&`, `+` outside a recognized term, or a comma or
  semicolon joining the terms to further unrecognized text ("Python, QuuxDB")
  — the condition is `null` and the row needs review: an OR is never split or
  partially kept. Coverage rule: every word outside the interpreted spans
  (leaf terms, connectives, cues, negation, thresholds) must be on a small EN/DE filler
  list (experience, with, strong, Kenntnisse, sehr gute, …). Any other word
  could be an unrecognized operand ("Python with QuuxDB"), so the condition is
  withheld with `uninterpreted_text`, and the clause's thresholds are withheld
  too, since unplaced words may qualify them. This deliberately sends many real
  clauses ("Experience building REST APIs with Python") to review rather than
  risk a partial condition.
- `thresholds`: integer year/month durations up to 99 (`gte`, `gt`, `range`,
  `unqualified`) and CEFR levels with operator, unit and literal scope. A scope
  ends at the next cue, negation or numeric amount; without a condition the
  literal scope is the threshold's interpretation. Vague, decimal, leading-zero,
  larger or otherwise uncaptured amounts ("1000 years", "3yrs", "six years",
  "3-year") and unsupported operator words (up to, about, maximum, "3 years
  minimum", "or more", etwa, bis zu) create no threshold and need review. Any
  operator word elsewhere in the clause outside an accepted threshold ("3 years
  of Python experience minimum", "About at least 3 years") withholds all of the
  clause's thresholds.
- `review_reasons` / `needs_review`: why a person must look at the row.
  `review_state` stays `draft` for every row.

`duplicates` groups repeated requirements only within one heading/marker scope
and only when the case-folded quote and every qualifier are identical; the same
text under different headings is not merged. Every member keeps its own span.

Structural validation rejects relabelled, split or invented content even when
checksums are recomputed: each label must equal the deterministic rule output
for the exact source. That proves reproducibility, not that the posting was
understood. An independently reviewed 30 EN / 29 DE synthetic oracle covers the
documented grammar only. Requirement correction/review versions are TASK-014;
nothing here approves a requirement, matches a career fact or authorizes export.
