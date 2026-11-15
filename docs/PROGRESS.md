# Current implementation state

Last reconciled: 2026-11-15 against main `01f3a40` (merged PR #8). TASK-011,
TASK-012, M1-FIX-006, TASK-013 and M1-FIX-007 are integrated. TASK-014
(requirement review and correction versions) is implemented and awaits
independent review. TASK-009 personal acceptance remains open; its private
state is recorded in the private data root.

| Work | State | Evidence / remaining gate |
| --- | --- | --- |
| TASK-001–004 | APPROVED in prior history | Existing review records |
| TASK-005 | APPROVED WITH FOLLOW-UP | Renderer comparison remains unmeasured |
| TASK-006–008 | APPROVED in prior history | Existing renderer/QA/snapshot reviews |
| M1-FIX-001–005 and focused corrections | Approved implementations recorded locally | [Local baseline history](history/PROGRESS_LOCAL_TASK_009.md), individual review files |
| TASK-009 / M1 | baseline-r0009 has technical QA and appearance-only approval; a later private content revision awaits applicant review | See [baseline state](#preserve-the-local-baseline-result); content approval, new baseline, final artifact acceptance and export pending |
| CLEANUP-001 | Reviewed and merged into main through PR #1 | [Review](reviews/CLEANUP-001.md), merge `0d81aa1` |
| TASK-010 | Reviewed and merged into main through PR #2 | [Review](reviews/TASK-010.md), [intake guide](JOB_INTAKE.md), merge `0cc9119` |
| Local integration | MERGE COMMITTED; CODE AND DOCUMENTATION REVIEWED | [Code review](reviews/MERGE-TASK-009-MAIN.md), [documentation review](reviews/MERGE-TASK-009-MAIN-DOCS.md); local merge `266e5ef3` |
| Sanitized publication | PR #3 MERGED | [Publication note](reviews/TASK-009-PUBLICATION.md); main `83497777`, final published CI `43541161616` |
| Publication state correction | APPROVED, documentation only | [Scoped review](reviews/TASK-009-PUBLICATION-STATE.md); no runtime or approval-policy changes |
| TASK-011 | Reviewed and merged into main through PR #4 | [Implementation review](reviews/TASK-011.md), [guide](JOB_EXTRACTION.md), merge `f6a3bf0` |
| TASK-012 | Reviewed and merged into main through PR #5 | [Review](reviews/TASK-012.md) round 11 APPROVED on `07375b1`; documentation closure `065d89e` scoped review APPROVED (Codex session `01a1db73-cb5f-7501-8cc2-4e2f10a55c05`); merge `ee59069` |
| M1-FIX-006 | Reviewed and merged into main through PR #6 | [Review](reviews/M1-FIX-006.md) round 2 APPROVED on `591b339`; closure scoped review APPROVED; merge `68aa536` |
| TASK-013 | Reviewed and merged into main through PR #7 | [Review](reviews/TASK-013.md) round 2 APPROVED on `f26da14`; closure scoped review APPROVED; merge `9c1d558` |
| M1-FIX-007 | Reviewed and merged into main through PR #8 | [Task](tasks/M1-FIX-007.md); [review](reviews/M1-FIX-007.md) round 2 APPROVED WITH FOLLOW-UP on `b906a7f`; follow-ups closed; merge `01f3a40` |
| TASK-014 | IMPLEMENTED — AWAITING REVIEW | [Guide](JOB_EXTRACTION.md#review-and-correct-requirements); branch `task/014-requirement-review` |
| TASK-015–020 | NOT IMPLEMENTED | Matching and tailoring |
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

Reconciled 2026-11-15: the private records hold a later content revision, so
r0009's content is not the current candidate for content approval. The
applicant has now returned written content decisions; details stay in the
private data root. Next: reviewed M1-FIX-006, a corrected private revision with
receipts bound to those decisions, a new baseline with QA, then separate final
artifact approval. No export is authorized.

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

## M1-FIX-006 implementation (merged)

Adds optional `expected_completion_date` and `specialization` to education
facts. An expected date requires an ongoing degree without a known end, may not
precede the start, and an ongoing degree can no longer carry an actual
completion date (which would claim an award). Empty new fields are stripped
from canonical payloads, so existing digests are unchanged: a pinned legacy
digest test still passes, and the private reviewed profile validates with its
existing receipts and recompiles a plan byte-identical to the stored one.
Display: `April 2023 – Expected March 2027` and a `Specialization:` line; plan
claim text carries both values. Skill groups keep internal category IDs; only
static display headings change (AI & Machine Learning, Data Engineering &
Analytics, Backend & Databases, Frontend & Visualization, Cloud &
Infrastructure). Template identity is now
`baseline-v4-m1-fix006-expected-completion-display-headings`. The exported
profile schema gains the two optional fields; expected-heading fixtures were
updated for the intended display change, and four test helpers now display
the canonical payload rather than a raw dump. Full suite: 471 passed (macOS,
real sandboxed renderer); Ruff, format, mypy and diff checks clean.

Review round 1 on `ae6c461` returned CHANGES REQUIRED (F-01): model
invariants ran only at construction, so a `model_copy(update=...)` copy could
carry an ongoing degree with an actual completion date (or an expected date
before its start) through `validate_profile` and the review operation. Both
trusted boundaries now re-validate each fact, evidence and variant's content
invariants (status/approval neutralized, reported separately as before), and
the review operation refuses to issue a receipt for invalid content. Three
regressions fail on `ae6c461` and pass now. Full suite: 474 passed. Review
round 2 on `591b339` returned APPROVED with no unresolved findings; hosted CI
43666629755 passed on that head.

## TASK-014 implementation (awaiting review)

Adds `jae job-review` and `jae job-review-apply`. A correction is an explicit
patch (`set_priority`, `set_condition`, `set_thresholds`, `set_role`, `accept`,
`reopen`) bound to the JD revision, record and raw digests and the exact review
view it was prepared against; the reviewer ID and UTC time are recorded. Each
revision is stored once under the private job folder in a hash-linked chain
and the view is always rebuilt by replaying the chain over the re-verified
deterministic classification. Corrected spans must quote the raw JD inside
their clause. A row is reviewed only through `accept` naming its displayed
review reasons; only reviewed, unnegated, structured, mandatory rows become
hard gates. A newer JD revision starts unreviewed. Round 1 review (CHANGES
REQUIRED) added a verified head record and UTC-only times; round 2 (CHANGES
REQUIRED) led to a head committed before each revision file that embeds it (a
missing newest file is restored, never rolled back) and an OS writer lock.
Synthetic tests:
`tests/test_requirement_review.py` (A20).

Implementer verification on macOS (Python 3.12, locked environment):

| Command | Result |
| --- | --- |
| `uv run pytest tests/test_requirement_review.py` | Exit 0; 46 passed |
| `uv run pytest` | Exit 0; 666 passed, no skips |
| `uv run ruff check .` / `uv run ruff format --check .` | Exit 0; 87 files formatted |
| `uv run mypy src` | Exit 0; 53 source files |

## TASK-013 implementation (merged)

Adds a reviewed EN/DE skill-alias dictionary (`skill-aliases-v1`, rationale per
concept) and an exact matcher: longest alias wins, no overlaps, Unicode
letter/digit/combining-mark boundaries, per-character case-fold equality (no
dotted/dotless-I equivalence), case-sensitive collision-prone abbreviations,
strict C/R neighbours and distinct symbolic names. "Spark" alone is only an
ambiguous candidate; broader/related links are typed and never equivalence;
unmatched surfaces keep literal text; a TASK-012 adapter passes row polarity.
The oracle (43 scan, 25 surface, 8 relation cases) was committed first; fixture
review round 1 required a sharper contract (resolved); implementation review
round 1 found Unicode case-fold false positives and a surface-bound bypass
(fixed); round 2 on `f26da14` APPROVED. Full suite on the branch: 592 passed.

## TASK-012 implementation (merged)

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

Round 2 on `fbc4c97` returned **CHANGES REQUIRED**: uncaptured or
under-interpreted numeric text ("six years", "3-year", "3 years minimum",
"English C2 minimum", scope `of`) passed without review (F-05); the education
path and unknown operands behind filler/punctuation still left partial
conditions ("A degree; QuuxDB", "Python with QuuxDB") (F-06, F-07); and the
TASK-009 note here was too specific for a public repository (F-08). The fix
replaces case-by-case checks with a coverage rule (non-filler words outside
interpreted spans withhold the condition with `uninterpreted_text`), flags any
year/month unit word not captured exactly and unsupported operator words before
or after amounts, requires a scope to contain a word, and reduces the TASK-009
note to a generic pending state. 19 of the 20 new finding cases fail on
`fbc4c97` (the remaining one is a guard case); controls with only filler keep
their conditions.

Round 3 on `2f43f4f` confirmed F-01–F-08 fixed (126 unknown-operand variants,
no unreviewed partial condition) and returned **CHANGES REQUIRED** for F-09: an
operator word away from the number or a contradictory pair still left a
structured threshold, only flagged. Now any operator word outside an accepted
threshold span drops the clause's thresholds with `unsupported_number`, and
`uninterpreted_text` withholds thresholds as well as the condition. All six
F-09 cases fail on `2f43f4f`. Non-blocking F-10 (reasonable prose such as
"Experience building REST APIs with Python" goes to review) is the documented
conservative trade-off.

Round 4 on `b91ead6` confirmed F-01–F-10 (768 unknown-operand variants, no
unreviewed partial condition) and returned **CHANGES REQUIRED** for F-11: the
degree term spanned almost the whole clause, so coverage treated trailing text
("A degree in Computer Science with Rust experience", "A degree, QuuxML") as
interpreted. The degree term is now explicit grammar (education words, an
optional field of at most four words, an optional related-field phrase), and
coverage counts only leaf terms and connectives, never a whole group span. A
CEFR-dense clause now fails early instead of building thousands of models.
All eight F-11 cases fail on `b91ead6`.

Round 5 on `d30ecc7` confirmed F-11 and an 80-case operand matrix, and returned
**CHANGES REQUIRED** for F-12: a degree field made of filler words ("A degree
in formal language") was dropped because field parsing stopped at filler and
coverage excused those words. Field parsing now stops only at function words
and connectives, and content-bearing descriptors left the global filler list;
they are exempt only as adjacent degree modifiers or as "language" after a
recognized language. The four F-12 reproductions fail on `d30ecc7`.

Round 6 on `12221f7` confirmed F-12 (no technology-only partial condition in a
1,872-case matrix) and returned **CHANGES REQUIRED** for F-13: after the F-12
change, degree fields no longer stopped at "but/also/aber/auch", so a following
unknown operand joined the field. Every filler word now stops a field (content
descriptors are no longer filler, so F-12 stays fixed), and a field link with
no field word withholds the degree condition. Non-blocking F-14 ("Written
German" sent to review) is addressed with adjacent language modifiers.

Round 7 on `faee434` confirmed F-13/F-14 and returned **CHANGES REQUIRED** for
F-15: word lexicons stored `ß` forms ("fließend") while lookups used
`casefold()` (`ß` → `ss`), so those filler words did not end a degree field.
All lexicons are now built case-folded, guarded by an invariant test over
every word set. Non-blocking F-16 ("Native-level German", "Written and spoken
German" go to review) remains the documented conservative behaviour.

Round 8 on `f5d65ee` confirmed F-15 (all 142 filler words reviewed around an
unknown operand, none unsafe) and returned **CHANGES REQUIRED** for F-17: signs
and comparison symbols next to amounts were ignored ("−3 years" read as 3,
"English ≤C2" as unqualified C2). Adjacent signs/comparison symbols now reject
the threshold, stray comparison symbols withhold the clause's thresholds, and
scopes no longer start with a closing bracket ("(3+ years) in Python"). All
13 F-17 cases fail on `f5d65ee`.

Round 9 on `1722e32` confirmed F-01–F-17 (623-case operand matrix and all 142
filler words clean) and returned **CHANGES REQUIRED** for F-18: the explicit
symbol list missed dashes after amounts and fullwidth/small sign forms ("3
years − Python", "English C2−", "＋3 years"). Sign detection now uses Unicode
categories (Sm math symbols, Pd dashes) on both sides of amounts and CEFR
levels, with only word-joining CEFR hyphens accepted, and stray math symbols
or standalone dashes withhold thresholds. All 12 F-18 cases fail on `1722e32`.

Round 10 on `ad83f8d` confirmed F-01–F-18 (2,400 operand and 5,844 Unicode sign
cases) and returned **CHANGES REQUIRED** for F-19: the CEFR word-joining
exception accepted every Unicode dash ("C2—Niveau"), not only hyphens. It now
accepts only `-`, U+2010 and U+2011. Non-blocking F-20 ("C++ 3 years" lost its
threshold because the term's "+" counted as a sign) is fixed by ignoring signs
inside recognized terms. All six F-19 dash cases fail on `ad83f8d`.

Round 11 on `07375b1` returned **APPROVED** with no new findings (140
regression, 532 operand, 710 filler and about 1,900 Unicode sign cases clean).
Hosted CI 43628074843 on that head passed 458 tests with Ruff/format/mypy; its
checkout tree matched `bf360e66`. Remaining non-blocking, meaning-preserving
false alarms (F-10, F-14, F-16) are the documented conservative behaviour:
prose such as "Experience building REST APIs with Python" or "Written and
spoken German" goes to review rather than receiving a partial condition.

Implementer verification of the correction on macOS (Python 3.12, locked
environment, `JAE_TYPST_PACKAGE_ROOT` assets verified offline):

| Command | Result |
| --- | --- |
| `uv run pytest tests/test_requirement_classification.py tests/test_requirement_spans.py tests/test_ingestion.py` | Exit 0; 338 passed |
| `uv run pytest -ra` | Exit 0; **458 passed** in 105.80s, no skips |
| `uv run ruff check .` / `uv run ruff format --check .` | Exit 0; 77 files formatted |
| `uv run mypy src` | Exit 0; 47 source files |
| `git diff --check` | Exit 0 |

Limits: small explicit cue/term allowlists, not general EN/DE parsing; "you'll
need", postfix operators ("3 years minimum", "or more"), education OR lists
(Bachelor's or Master's), comma-only skill lists and symbol-joined alternatives
intentionally stay unsupported and need review; parenthetical qualifiers are
not interpreted.

## Next action

Independent review of TASK-014 against `docs/REVIEW_PROTOCOL.md` (M1-FIX-008 is
reviewed separately on its own branch). Then TASK-015 (match states and
experience intervals). Before any downstream feature makes `source_url`
clickable or fetchable, validate allowed URL schemes (F-02). Personal records
stay outside Git and CI; no matching, tailoring, export or application occurs.
