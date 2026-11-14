# TASK-009 and main reconciliation

Date: 2026-11-13; publication state reconciled 2026-11-14. The code received
**APPROVED WITH FOLLOW-UP** review and the documentation follow-up received
**APPROVED** review. Local merge `266e5ef3` is committed. Sanitized snapshot
`58f0c183` is published in [PR #3](https://github.com/umaryaseen/job-application-tool/pull/3),
which is not yet merged into main. See [current progress](PROGRESS.md) for the
remaining publication gates; the merge procedure below is historical.

The report identifies local head `d0f1436` and incoming main `0cc9119`. Git
reported seven conflicted paths. The original branch and incoming commits are
retained; the helper performs no reset, rebase, staging, commit or push.

| Existing decision identity | Identity in combined branch | Treatment |
| --- | --- | --- |
| Local ADR-017: typed responsibility/project claims | ADR-017 | Original bytes and existing references retained |
| Local ADR-018: applicant-facing presentation | ADR-018 | Original bytes, review and runtime identities retained |
| Main ADR-017: cleanup, operating docs and CI | ADR-019 | Decision text retained; new ID and explicit alias note |
| Main ADR-018: independent draft JD intake | ADR-020 | Decision/review retained; new ID and explicit alias note |

Historical main commits and PR #1/#2 still use their original ADR identifiers.
Read those identifiers in the context of that commit. The new names remove
ambiguity in the combined checkout; they do not change architectural policy or
transfer approvals to new code. Local proposed/architecture-review statuses are
preserved without inventing later acceptance. Existing implementation reviews
remain separate records.

The active progress/handoff documents are reconciled and shortened. The local
versions are archived with relative Markdown links adjusted for their new
directory and portable paths in the publication snapshot. Original exact bytes
remain in the retained local branch and external merge backup. The original
remote versions remain in the historical main commits. The backup contains
only affected repository files and merge metadata, not the external personal
data directory. The publication branch starts at main `0cc9119`; it does not
contain the unpublished local commits as ancestors.

The PDF import conflict keeps EvidenceKey and present_plan as well as
PackageAssetsError and prepare_typst_packages. All local PDF behavior remains;
main's package preparation, stage-local package/cache paths and bounded missing-
asset diagnostic are retained. Local template/build constants are unchanged.

The helper verifies the seven unmerged index identities reported by the user,
their unresolved working contents and the incoming merge head. It refuses
unexpected manual edits, changed auto-merged targets, occupied new paths and
symlinked target paths. Dry-run is the default. Apply makes an external backup
before writes and leaves Git staging and merge completion to local verification
and review. It does not read profiles, create approvals, export CVs, install
dependencies or send network requests.

Validation performed on the helper is separate from product verification.
Independent review of staged tree `2794c6af04df5beb982561c0115eadde58196500`
reported 147 tests passed on macOS, no skips or xfails; locked sync, Typst
asset verification, Ruff, format, mypy, CLI help and Git whitespace checks
exited 0. The [review](reviews/MERGE-TASK-009-MAIN.md) records the commands,
synthetic intake and renderer checks, findings and limitations. It is a local
run, not combined-tree CI, and does not approve personal CV content or final
artifacts. Those gates and export remain pending.

F-01 and F-03 were addressed and independently approved in the
[documentation follow-up](reviews/MERGE-TASK-009-MAIN-DOCS.md). F-02 remains a
future gate: the implementer of the first
downstream feature that makes `source_url` clickable or fetchable must validate
allowed URL schemes before doing so. TASK-010 remains metadata-only; its
behavior is unchanged. No dependency changes are part of this follow-up.
