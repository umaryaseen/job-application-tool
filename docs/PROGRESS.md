# Current implementation state

Last reconciled: 2026-11-14 against main `83497777` (merged PR #3). The
reviewed baseline fixes, sanitized publication and status correction are
integrated. Final publication CI at `b48781a` passed 147 tests and lint/types.
TASK-009 personal acceptance remains open. Accepted ADR-021 permits source-only
analysis on reviewed dependencies; TASK-011 is reviewed on
[PR #4](https://github.com/umaryaseen/job-application-tool/pull/4), not yet merged.

| Work | State | Evidence / remaining gate |
| --- | --- | --- |
| TASK-001–004 | APPROVED in prior history | Existing review records |
| TASK-005 | APPROVED WITH FOLLOW-UP | Renderer comparison remains unmeasured |
| TASK-006–008 | APPROVED in prior history | Existing renderer/QA/snapshot reviews |
| M1-FIX-001–005 and focused corrections | Approved implementations recorded locally | [Local baseline history](history/PROGRESS_LOCAL_TASK_009.md), individual review files |
| TASK-009 / M1 | Technical QA pass and applicant appearance approval recorded for baseline-r0009 | Exact PDF/TXT content, final artifact acceptance and export remain pending |
| CLEANUP-001 | Reviewed and merged into main through PR #1 | [Review](reviews/CLEANUP-001.md), merge `0d81aa1` |
| TASK-010 | Reviewed and merged into main through PR #2 | [Review](reviews/TASK-010.md), [intake guide](JOB_INTAKE.md), merge `0cc9119` |
| Local integration | MERGE COMMITTED; CODE AND DOCUMENTATION REVIEWED | [Code review](reviews/MERGE-TASK-009-MAIN.md), [documentation review](reviews/MERGE-TASK-009-MAIN-DOCS.md); local merge `266e5ef3` |
| Sanitized publication | PR #3 MERGED | [Publication note](reviews/TASK-009-PUBLICATION.md); main `83497777`, final published CI `43541161616` |
| Publication state correction | APPROVED, documentation only | [Scoped review](reviews/TASK-009-PUBLICATION-STATE.md); no runtime or approval-policy changes |
| TASK-011 | REVIEWED ON PR #4; NOT MERGED | [Implementation review](reviews/TASK-011.md), [guide](JOB_EXTRACTION.md), [ADR-021](adr/ADR-021.md); final-head CI required before integration |
| TASK-012–020 | NOT IMPLEMENTED | Later source analysis, matching and tailoring |
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

Pre-sync local progress and handoffs are archived under `history/`; their old
task gates describe their historical candidates. Published documentation uses
portable path references. The original bytes and full local commit history
remain in the retained workstation branch and external merge backup. The
unpublished TASK-009 branch and merge commits were not imported as publication
ancestors; shared main ancestry remains. Earlier baseline
iterations and failed QA remain historical. Do not replace current private
records with an older profile or infer that artifact r0009 means profile
revision 9.

## Reviewed implementation and publication

CLEANUP-001 adds supported macOS CI, stage-local Typst package resolution and
checksum-pinned public assets installed explicitly. TASK-010 adds private,
bounded UTF-8 JD intake, original bytes, faithful normalized Markdown, supplied
metadata, integrity checks, duplicate detection and immutable numbered revisions.
It does not read career facts or create application submissions or outcomes.
Independent macOS verification of the combined tree passed 147 tests with no
skips or xfails. Locked sync, Typst asset verification, Ruff, format, mypy,
installed CLI help and Git whitespace checks exited 0. The reviewer also
exercised synthetic intake and real rendering; see the [review](reviews/MERGE-TASK-009-MAIN.md)
for commands, environment and limits. This was a local run, not combined-tree CI.
Published snapshot `58f0c183` starts from main `0cc9119` and preserves the
reviewed non-documentation files. Its independent publication review and
outgoing-history audit were reported as approved before push. That does not
qualify hosted CI; inspect the latest head and check results on PR #3.

Hosted [CI 43539855170](https://github.com/umaryaseen/job-application-tool/actions/runs/43539855170)
verified published snapshot `58f0c183`: **147 passed in 80.68s**, Ruff and
format passed (68 files), and mypy passed (40 source files). The separate
reviewer fetched the actual run and job logs. This records that exact snapshot;
check the final PR head separately after the documentation-only correction.

Local ADR-017/018 retain their original meanings and template identities.
Main's conflicting decision IDs are now [ADR-019](adr/ADR-019.md) (cleanup) and
[ADR-020](adr/ADR-020.md) (draft-intake sequencing). The mapping is recorded in
[the reconciliation note](MERGE_RECONCILIATION.md); historical approvals are not
rewritten or extended. ADR-020 originally allowed independent draft intake;
ADR-021 also permits source-only TASK-011–014 implementation on reviewed
dependencies before personal acceptance. Neither releases M1/M2 or enables
career matching, tailoring or export. Later gates remain in force.

## Next action

Verify final-head CI and merge reviewed PR #4 before starting TASK-012's
source-only priority/negation/group classification. Do not repeat the completed
decision, fixture or implementation reviews. Do not start career matching or
treat draft candidates as approved requirements. Also resume
TASK-009's exact content and artifact acceptance with the applicant;
appearance-only approval retains its original scope. Before any downstream
feature makes `source_url` clickable or fetchable, that feature's implementer
must validate allowed URL schemes (F-02). TASK-010 continues to store the value
as metadata only. Personal records remain outside Git and CI. No export or
application is created.

## TASK-011 reviewed implementation

Adds bounded source segmentation and typed draft annotations tied to a verified
raw JD revision/hash. Unicode-codepoint quotes and lexical subspans round-trip;
repeated clauses have distinct IDs. Known sections retain responsibility and
benefit/context scope; explicit unknown headings reset it. Unknown/mixed clauses
stay ambiguous. All priority stays unspecified and all candidates need review.
No intake mutation, requirement approval, provider, network or dependency was added.

The [fixture review](reviews/TASK-011-FIXTURES.md) independently approved the
16 EN/16 DE literal-label corpus before it was used as the test oracle. Local
focused A17/CLI suite: **57 passed in 2.56s**. Ruff check and format passed
(73 files); mypy passed (44 source files). The independent implementation review
ran **84 extraction/intake tests**, additional adversarial/boundary probes and
the same lint/types. Hosted [CI 43544575739](https://github.com/umaryaseen/job-application-tool/actions/runs/43544575739)
on published implementation `c72d93a` passed **204 tests in 153.70s**, with
Ruff/format/mypy passing. Its actual CI checkout tree matched local `d47311e`
and published tree `54340c9a`. The [review](reviews/TASK-011.md) returned
APPROVED WITH FOLLOW-UP; the sole low finding was the stale intake-only
sentence, corrected above in this documentation closure. Final-head CI still
needs verification after that closure. No M1/M2 acceptance is claimed.
