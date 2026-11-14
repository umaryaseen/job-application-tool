# Current implementation state

Last reconciled: 2026-11-14, combining local TASK-009 head `d0f1436` with main
`0cc9119df20a2be974f8db41ed9869663493f800` (merged PR #2).
The combined code tree `2794c6af04df5beb982561c0115eadde58196500` received
independent **APPROVED WITH FOLLOW-UP** review. This documentation follow-up
is awaiting scoped independent review; the merge is not yet committed.

| Work | State | Evidence / remaining gate |
| --- | --- | --- |
| TASK-001–004 | APPROVED in prior history | Existing review records |
| TASK-005 | APPROVED WITH FOLLOW-UP | Renderer comparison remains unmeasured |
| TASK-006–008 | APPROVED in prior history | Existing renderer/QA/snapshot reviews |
| M1-FIX-001–005 and focused corrections | Approved implementations recorded locally | [Local baseline history](history/PROGRESS_LOCAL_TASK_009.md), individual review files |
| TASK-009 / M1 | Technical QA pass and applicant appearance approval recorded for baseline-r0009 | Exact PDF/TXT content, final artifact acceptance and export remain pending |
| CLEANUP-001 | Reviewed and merged into main through PR #1 | [Review](reviews/CLEANUP-001.md), merge `0d81aa1` |
| TASK-010 | Reviewed and merged into main through PR #2 | [Review](reviews/TASK-010.md), [intake guide](JOB_INTAKE.md), merge `0cc9119` |
| Current local integration | CODE APPROVED WITH FOLLOW-UP; DOCUMENTATION DELTA AWAITING REVIEW | [Independent review](reviews/MERGE-TASK-009-MAIN.md), [scoped handoff](REVIEW_HANDOFF.md) |
| TASK-011–020 | NOT IMPLEMENTED | Requirements, matching and tailoring |
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

Complete pre-sync local progress and handoffs are archived under `history/`;
their old task gates describe their historical candidates. The original bytes
remain in local HEAD and the external merge backup. Earlier baseline iterations
and failed QA remain historical. Do not replace current private records with
an older profile or infer that artifact r0009 means profile revision 9.

## Main integration

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
No dependency changes are introduced by this documentation follow-up.

Local ADR-017/018 retain their original meanings and template identities.
Main's conflicting decision IDs are now [ADR-019](adr/ADR-019.md) (cleanup) and
[ADR-020](adr/ADR-020.md) (draft-intake sequencing). The mapping is recorded in
[the reconciliation note](MERGE_RECONCILIATION.md); historical approvals are not
rewritten or extended. Only independent draft intake precedes personal
acceptance. Later task and milestone gates remain in force.

## Next action

Obtain scoped independent review of the documentation delta from the reviewed
tree before completing the merge. Resume TASK-009's exact content and artifact
acceptance with the applicant; appearance-only approval retains its original
scope. Before any downstream feature makes `source_url` clickable or fetchable,
that feature's implementer must validate allowed URL schemes (F-02). TASK-010
continues to store the value as metadata only. Personal records remain outside
Git and CI. No export or application is created.
