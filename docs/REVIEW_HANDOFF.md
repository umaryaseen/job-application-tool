# Independent review handoff

Fill in the exact task/base/head. Prior TASK-008 review is complete in [its review record](reviews/TASK-008.md); do not restart it from a stale prompt.

```text
Independently review TASK_ID.
Repository / branch: ...
Base: ...
Implementation head: ...
Any documentation-only head: ...

Read AGENTS, PROGRESS, task acceptance, affected design/ADRs and REVIEW_PROTOCOL.
Inspect the full diff and implementation. Verify exact candidate commit/tree.

Re-run relevant tests and inspect actual evidence. Production PDF/QA requires
supported macOS isolation and Poppler. A Linux domain run is not complete
rendering verification. Inspect full CI evidence for platform-specific changes.

Check scope, correctness, meaningful regression coverage, source/approval
integrity and private-data exclusions. Do not modify implementation while
supplying the independent verdict.

Record APPROVED, APPROVED WITH FOLLOW-UP or CHANGES REQUIRED, exact reviewed
heads, commands/results, concrete findings and the next gate in docs/reviews.
Do not merge or impersonate applicant approval of facts or application files.
```
