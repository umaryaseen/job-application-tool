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
