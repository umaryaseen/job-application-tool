# Publication handoff: reviewed TASK-009 baseline fixes

Scope: current operating documents only. The original local merge and its
documentation follow-up are complete. Do not restart those review targets.
The publication status correction also received
[APPROVED scoped review](reviews/TASK-009-PUBLICATION-STATE.md). Check CI on
the final PR head before integration; do not restart the completed review below.

- Published base: `58f0c183e3c4ce76be5c7ea72c5f082cbd91c71d`.
- PR: [#3](https://github.com/umaryaseen/job-application-tool/pull/3), targeting
  main `0cc9119df20a2be974f8db41ed9869663493f800`.
- Local source merge: `266e5ef3`, retained on the workstation. The unpublished
  local merge/TASK-009 commits are not publication-branch ancestors; common
  main ancestry is retained.
- Code review: [APPROVED WITH FOLLOW-UP](reviews/MERGE-TASK-009-MAIN.md),
  including 147 tests passed on macOS against the recorded source tree.
- Original documentation review:
  [APPROVED](reviews/MERGE-TASK-009-MAIN-DOCS.md).
- Sanitization and source identity: [publication note](reviews/TASK-009-PUBLICATION.md).

## Completed scoped review

The following scope defined the completed review and is retained for audit.

Read AGENTS and [REVIEW_PROTOCOL](REVIEW_PROTOCOL.md). Inspect the exact
base-to-head correction and record the candidate commit/tree. Confirm:

1. Only PROGRESS, this handoff, MERGE_RECONCILIATION and the composite DOCX ADR
   reference in IMPLEMENTATION_PLAN change. Source, tests, schemas, scripts,
   dependencies, fixtures, CI and runtime/template identities remain unchanged.
2. Current documents distinguish the completed local merge, approved prior
   reviews, published sanitized snapshot and PR #3's pending main integration.
   Historical review records retain their recorded identities and limitations.
3. Local 147-test verification is not described as hosted publication CI.
   Verify the actual latest PR head, workflow result and logs separately; an
   earlier green run must not qualify changed source without review.
4. TASK-009 exact PDF/TXT content, final artifact acceptance and export remain
   pending. Appearance-only approval retains its original scope. No private
   data is read, changed, imported or approved by this correction.
5. F-02 remains a future gate: validate allowed URL schemes before a downstream
   feature makes `source_url` clickable or fetchable. TASK-010 stays metadata-only.

Check whitespace, relative links and added content for private material. A
documentation-only correction can receive scoped review without rerunning the
macOS suite locally. Record the independent verdict under `docs/reviews/`;
do not modify implementation or merge the PR as part of review.

## Next action

Check hosted CI and review for the final PR head before merging through the
normal GitHub workflow. Then resume TASK-009 with the actual current private
canonical profile and exact artifacts. The applicant alone approves document
content and final bytes. Do not replace current records with an older starter
profile, infer profile revision from artifact r0009, or treat saved postings as
application submissions. Later task and milestone dependencies remain in force.
