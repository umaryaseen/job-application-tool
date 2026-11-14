# Current implementation state

Last reconciled: 2026-11-14 against main `f6a3bf05` (merged PR #4). TASK-011
draft source candidates are integrated; final PR #4 CI 43545596860 passed 204
tests with lint/types and its checkout tree matched the reviewed tree. TASK-009
personal acceptance remains open. Accepted ADR-021 permits source-only analysis
on reviewed dependencies; TASK-012 is on draft
[PR #5](https://github.com/umaryaseen/job-application-tool/pull/5): round-1
review found four blocking defects, now corrected and awaiting re-review.

| Work | State | Evidence / remaining gate |
| --- | --- | --- |
| TASK-001–004 | APPROVED in prior history | Existing review records |
| TASK-005 | APPROVED WITH FOLLOW-UP | Renderer comparison remains unmeasured |
| TASK-006–008 | APPROVED in prior history | Existing renderer/QA/snapshot reviews |
| M1-FIX-001–005 and focused corrections | Approved implementations recorded locally | [Local baseline history](history/PROGRESS_LOCAL_TASK_009.md), individual review files |
| TASK-009 / M1 | baseline-r0009 has technical QA and appearance-only approval; a later applicant-supplied private content revision awaits applicant review | See [baseline state](#preserve-the-local-baseline-result); content approval, new baseline, final artifact acceptance and export pending |
| CLEANUP-001 | Reviewed and merged into main through PR #1 | [Review](reviews/CLEANUP-001.md), merge `0d81aa1` |
| TASK-010 | Reviewed and merged into main through PR #2 | [Review](reviews/TASK-010.md), [intake guide](JOB_INTAKE.md), merge `0cc9119` |
| Local integration | MERGE COMMITTED; CODE AND DOCUMENTATION REVIEWED | [Code review](reviews/MERGE-TASK-009-MAIN.md), [documentation review](reviews/MERGE-TASK-009-MAIN-DOCS.md); local merge `266e5ef3` |
| Sanitized publication | PR #3 MERGED | [Publication note](reviews/TASK-009-PUBLICATION.md); main `83497777`, final published CI `43541161616` |
| Publication state correction | APPROVED, documentation only | [Scoped review](reviews/TASK-009-PUBLICATION-STATE.md); no runtime or approval-policy changes |
| TASK-011 | Reviewed and merged into main through PR #4 | [Implementation review](reviews/TASK-011.md), [guide](JOB_EXTRACTION.md), merge `f6a3bf0` |
| TASK-012 | CORRECTED — AWAITING RE-REVIEW | [Fixture review](reviews/TASK-012-FIXTURES.md) APPROVED; [implementation review](reviews/TASK-012.md) round 1 CHANGES REQUIRED (F-01–F-04), corrections pending re-review, see [handoff](REVIEW_HANDOFF.md) |
| TASK-013–020 | NOT IMPLEMENTED | Skill aliases, review versions, matching and tailoring |
| TASK-021–024 | NOT IMPLEMENTED | Letters, tracker and DOCX |
| Interview preparation and skill-demand analysis | PLANNED | [Requested workflow](APPLICATION_WORKFLOW.md) |

## Preserve the local baseline result

Local merge `35309ea` integrated approved M1-FIX-005. The preserved local
record reports a fresh baseline-r0009 with passing independent Poppler/pypdf
content, identity, scope, contact/URL, Unicode, punctuation, A4, geometry,
pagination and file checks. Both raster pages received technical inspection.
The applicant approved the appearance/layout of the exact PDF only.
That is not PDF/TXT content approval, final artifact approval or permission to
export. Those gates remain pending. This reconciliation does not read, replace,
approve or regenerate private profiles, receipts, plans or artifacts.

Reconciled 2026-11-14 from the private records (no content copied here): after
that appearance approval the applicant supplied revised CV text, and a pending
private content revision with 42 changed payloads was drafted against the
reviewed profile. It supersedes r0009's content for review purposes, so r0009
should not receive content approval if the revision is accepted. A private
old-to-new review packet now exists under the data root's `reviews/`. Preparing
it exposed a drafting defect: one ongoing degree carries a completion date in
addition to its expected date, which would imply an award; it must be corrected
in a new draft before approval. Remaining order: applicant answers (wording,
skill-heading representation, omissions) → corrected draft → M1-FIX-006 typed
expected-completion field with independent review → receipts through the
existing exact-payload review → new baseline and QA → separate final byte
approval → export.

Pre-sync local progress and handoffs are archived under `history/`; their old
task gates describe their historical candidates. Published documentation uses
portable path references. The original bytes and full local commit history
remain in the retained workstation branch and external merge backup. The
unpublished TASK-009 branch and merge commits were not imported as publication
ancestors; shared main ancestry remains. Earlier baseline iterations and failed
QA remain historical. Do not replace current private records with an older
profile or infer that artifact r0009 means profile revision 9.

## Integrated history in brief

CLEANUP-001 added supported macOS CI, stage-local Typst package resolution and
checksum-pinned public assets. TASK-010 added private bounded UTF-8 JD intake
with original bytes, faithful Markdown, metadata, integrity checks, duplicates
and immutable revisions. PR #3 published the reviewed baseline fixes as a
sanitized snapshot (CI `43539855170`, 147 passed). Local ADR-017/018 keep their
meanings; main's cleanup and intake decisions are [ADR-019](adr/ADR-019.md) and
[ADR-020](adr/ADR-020.md) per [the reconciliation note](MERGE_RECONCILIATION.md).
TASK-011 added read-only `jae job-extract`: exact raw Unicode-codepoint quotes,
section scope and lexical hints, all draft with unspecified priority, verified
by an independently reviewed 16 EN/16 DE oracle and hosted CI. Detailed
evidence lives in each linked review.

## TASK-012 implementation (corrected, awaiting re-review)

Adds read-only `jae job-classify`: a deterministic layer over the unchanged
TASK-011 candidates. Explicit EN/DE cues give mandatory/preferred/unspecified
with cue spans and a fixed basis code; general headings carry no priority;
cue headings and standalone marker lines (`Nice to have`, `Von Vorteil`) scope
later clauses; clause/heading or mixed-cue conflicts stay unspecified and need
review, so a preferred section never becomes mandatory. Recognized
"not required"/"kein Muss" forms are `requirement_negated`; other negation is
`unsupported`. Supported ANY/ALL trees cover term lists with one consistent
conjunction, either/both/sowohl…als auch/parentheses nesting and
degree-or-equivalent; any other OR/AND makes the condition `null` with review,
so no OR is split or partially kept. Integer durations and CEFR levels record
operator/unit/literal scope. Duplicates merge only with identical qualifiers.
Validation requires each label to equal the rule output for the exact source,
so recomputed checksums cannot authorize relabelled content. Output stays
draft; no persistence, profile access, provider, network or dependency.

The 30 EN / 29 DE oracle (`2988f63`) was committed before any classifier code
and approved by an independent Codex review with no discrepancies. An
adversarial probe found quadratic behaviour and a raw validation error on dense
200,000-byte clauses; both were fixed before commit (logarithmic span cover,
windowed prefix searches, explicit 4,096/16,384 annotation limits failing with
exit 2). Dense maximum-size clauses now finish in under 0.5 s.

Candidate `f41df6b` passed 313 tests locally and in hosted CI 43605582149.
Independent Codex review round 1 returned **CHANGES REQUIRED**: a slash or comma
to an unrecognized term kept a partial condition (F-01); a "related field" after
the equivalent branch was swallowed (F-02); 999/1000-year amounts raised a raw
validation error or vanished (F-03); duplicates merged across headings (F-04).
The corrective commit accounts for `/ | & +` outside terms and comma/semicolon
list continuation, consumes field alternatives only before the equivalent
branch, bounds durations (≤99, no leading zeros, uncaptured amounts such as
"1000 years"/"3yrs" go to review and end scopes), scopes duplicates by
heading/marker and converts any model-validation gap into `ExtractionError`.
The oracle is unchanged. All 18 finding-specific regression cases fail on
`f41df6b` and pass now; the reviewer's own probe scripts reproduce the fixes.

Implementer verification of the correction on macOS (Python 3.12, locked
environment, `JAE_TYPST_PACKAGE_ROOT` assets verified offline):

| Command | Result |
| --- | --- |
| `uv run pytest tests/test_requirement_classification.py tests/test_requirement_spans.py tests/test_ingestion.py` | Exit 0; 221 passed |
| `uv run pytest -ra` | Exit 0; **341 passed** in 102.66s, no skips |
| `uv run ruff check .` / `uv run ruff format --check .` | Exit 0; 77 files formatted |
| `uv run mypy src` | Exit 0; 47 source files |
| `git diff --check` | Exit 0 |

Limits: small explicit cue/term allowlists, not general EN/DE parsing; "you'll
need", postfix operators ("3 years minimum", "or more"), education OR lists
(Bachelor's or Master's), comma-only skill lists and symbol-joined alternatives
intentionally stay unsupported and need review; parenthetical qualifiers are
not interpreted. Re-review of the corrective delta and final-head hosted CI are
pending.

## Next action

Obtain the independent re-review of the TASK-012 corrective delta, verify
final-head hosted CI, then mark PR #5 ready and merge. Then TASK-013
(reviewed skill aliases, separate from lexical extraction) and TASK-014
(source-bound correction/review versions). Separately, TASK-009 waits on the
applicant's answers to the private content-revision packet; appearance-only
approval keeps its scope. Before any downstream feature makes `source_url`
clickable or fetchable, validate allowed URL schemes (F-02). Personal records
stay outside Git and CI; no matching, tailoring, export or application occurs.
