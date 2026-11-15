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
  words (stopping at any filler word, connective or punctuation; content
  descriptors are not filler, so "formal language" stays in the field; a link
  with no field word is withheld for review), optionally
  "or a related field" directly after. The field is taken literally, so words
  appended to it without any separator count as part of the field name; any
  other text after the term is outside it. If any OR/AND in the clause is outside that
  grammar — or a `/`, `|`, `&`, `+` outside a recognized term, or a comma or
  semicolon joining the terms to further unrecognized text ("Python, QuuxDB")
  — the condition is `null` and the row needs review: an OR is never split or
  partially kept. Coverage rule: every word outside the interpreted spans
  (leaf terms, connectives, cues, negation, thresholds) must be on a small EN/DE filler
  list (experience, with, strong, Kenntnisse, sehr gute, …; compared
  case-folded, so `ß` and `ss` match). Content-bearing
  descriptors (technical, formal, academic, university, language, written, …)
  are exempt only as modifiers directly before a degree, as spoken/written/
  native-style modifiers directly before a recognized language, or as
  "language" directly after one ("Written German", "German language skills").
  Any other word
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
  clause's thresholds. Signs are not operators: any Unicode math symbol
  (category Sm, e.g. + < > = ~ ± ≤ ≥ ≈ − and fullwidth forms) or dash (Pd) on
  either side of an amount or CEFR level rejects the threshold ("−3 years",
  "3 years − Python", "English C2−", "＋3 years"); only a true hyphen (`-`,
  U+2010, U+2011) joining a CEFR level to a word ("C1-Niveau") and ranges
  inside the amount are accepted, and a sign inside a recognized term
  ("C++ 3 years") does not count.
  Elsewhere in the clause, a math symbol outside a recognized term or a
  standalone dash withholds its thresholds; hyphens inside words ("hands-on")
  do not.
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

## Normalize skill mentions

TASK-013 adds a library (no CLI yet) that maps explicit technology, field and
language mentions to internal concept IDs using a small reviewed dictionary
(`normalization/dictionary.py`, version `skill-aliases-v1`). Each concept has
EN/DE aliases and a recorded rationale. Matching is exact: the longest alias
wins, mentions never overlap, and word aliases need letter/digit/combining-mark
boundaries. Collision-prone abbreviations (C, R, ML, DL, JS, NLP, AI, KI, AWS,
GCP, LLM/LLMs, k8s, React) are case-sensitive; C and R need strict neighbours,
so "R&D", "C-level" and "Objective-C" yield nothing. Symbolic names (C++, C#,
.NET, ASP.NET, Node.js, CI/CD) keep their distinctions. "Spark" alone is only an
`ambiguous` candidate. Go, TS, Rust, Swift and Objective-C are deliberately not
aliases.

Broader/related links (SageMaker → AWS, PyTorch → deep learning, Azure
Pipelines → Azure DevOps) are typed relations, never equivalence. A whole
surface (for example a skill name) matches only when one alias covers it; any
other surface stays `unmatched` with its literal text. Polarity and context
come from the caller: `normalize_classification` annotates TASK-012 condition
terms and marks terms in requirement-negated rows as negated. Nothing records
possession, approval or a career fact. Matching evidence against requirements
is TASK-015.

## Review and correct requirements

TASK-014 adds explicit, versioned corrections on top of the deterministic
draft. Show the current review state of a saved job:

```bash
uv run jae job-review --job-id example-ai-role
uv run jae job-review --job-id example-ai-role --revision 1
```

The JSON lists every row with its literal quote, priority, ALL/ANY condition,
thresholds, negation, draft `review_reasons`, `edited_fields`, `review_state`
and `gate`, plus the rules' duplicate groups, `latest_job_revision`,
`superseded` and `hard_gate_ids`. Its `view` carries the identity a correction
must quote: `job_revision`, `job_record_digest`, `raw_sha256`,
`review_revision` and `view_digest`.

A correction is a JSON file inside `$JAE_DATA_DIR`:

```json
{
  "job_id": "example-ai-role",
  "job_revision": 1,
  "job_record_digest": "<view.job_record_digest>",
  "raw_sha256": "<view.raw_sha256>",
  "base_review_revision": 0,
  "base_view_digest": "<view.view_digest>",
  "operations": [
    {"op": "set_priority", "candidate_id": "req-…", "priority": "mandatory"},
    {"op": "accept", "candidate_id": "req-…", "acknowledged_reasons": []}
  ]
}
```

```bash
uv run jae job-review-apply --correction corrections/example.json --reviewer-id reviewer-a
```

Operations apply in order: `set_priority`, `set_condition` (a full ALL/ANY tree
or `null`), `set_thresholds`, `set_role` (`requirement` or `non_requirement`),
`accept` and `reopen`. Every corrected span must quote the raw JD exactly and
lie inside its row's clause (connectives inside their group); the posting text
is never changed. Priority-marker rows can only be accepted or reopened. Any
edit returns a row to `draft`; only `accept`, naming exactly the row's displayed
`review_reasons`, makes it `reviewed`.

Gates: only a reviewed, unnegated, mandatory row with a condition or threshold
is a `hard_gate`. Unreviewed rows stay `unreviewed`; reviewed rows that are
negated (`not_required`), carry an uninterpreted negation or no structure
(`manual_check`), or are preferred/unspecified never exclude an application.

Each correction is stored once as
`jobs/<job_id>/requirement-reviews/r<job revision>/v<n>.json`, recording the
reviewer, UTC time (other offsets are refused), JD record and raw digests,
classification digest, base revision and view digests, the operations and the
resulting view digest. Writers are serialized by an OS file lock (released if
the process dies). Each correction first commits `head.json`, which embeds the
newest revision, then writes that revision's file. Loading re-verifies the JD,
rebuilds the classification and replays the chain; a gap, a missing head, files
beyond the head, a newest file that differs from the head, a foreign file, an
edited or re-signed record, changed JD text or changed rules output fails with
exit 2. A missing newest file (a crash between the two writes, or a deletion)
is taken from the head instead of rolling the review back, and the next
correction writes it out again. A correction whose stored revision or head
would exceed the size limits that loading enforces is refused before anything
is written. Deleting the entire review folder cannot be
detected; the job then shows its unreviewed draft, which never yields a hard
gate. Hashes detect accidental or partial changes, not a deliberate rewrite by
the local account owner (ADR-012). A correction must name the review state it
was prepared against, so two reviewers cannot both extend the same state, and a
newer JD revision starts unreviewed while older reviews remain historical and
read-only. Limits: negation and duplicate groups are rule observations that
cannot be edited (a wrongly negated row simply never gates; it can be set to
`non_requirement`), and there is no editor or model-proposed correction.
